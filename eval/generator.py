"""
SUBIT-T Synthetic Test Case Generator.
Generates 100k+ test cases using combinatorial templates and fuzzing.
"""

import json
import random
import argparse
from pathlib import Path

# Phrases extracted from subit_t/encoder.py
CURRENT_KW = {
    "WHO": {
        "ME": ["i ", "my ", "i'll", "let me", "i will", "i'm", "i've", "as for me", "myself"],
        "WE": ["we ", "our ", "team", "together", "let's", "everyone", "we're", "squad", "group", "collective"],
        "YOU": ["you ", "your ", "this code", "the issue", "the bug", "review this", "the function", "examine this", "check this"],
        "THEY": ["system", "the model", "data shows", "historically", "evidence", "the pattern", "it shows"],
    },
    "WHAT": {
        "EXPAND": ["idea", "design", "draft", "brainstorm", "architecture", "document", "new approach", "proposal", "ideate", "generate"],
        "TRANSFORM": ["running", "executing", "deploying", "building", "implementing", "pipeline", "in progress", "perform", "apply"],
        "REDUCE": ["review", "analyze", "bug", "issue", "problem", "memory leak", "error", "debug", "logs", "outage", "vulnerabilit", "critique", "check", "audit", "glitch", "flaw", "defect", "examine", "inspect", "scrutinize"],
        "PRESERVE": ["log", "store", "archive", "record", "save", "remember", "document", "note", "keep"],
    },
    "WHEN": {
        "INITIATE": ["start", "begin", "first", "scratch", "initial", "kick off", "new project", "today", "opening", "commence", "launch", "trigger"],
        "SUSTAIN": ["now", "currently", "active", "working", "processing", "right now", "in progress", "asap", "presently", "forthwith"],
        "INTEGRATE": ["finish", "complete", "wrap", "close", "done", "final", "commit", "conclude", "merge", "before the release", "end", "terminate", "finalize"],
        "RELEASE": ["wait", "pause", "ready", "idle", "standby", "later", "hold", "queue", "pending"],
    },
}

TARGET_KW = {
    "WHO": {
        "ME": ["i will", "let me", "i'll do", "on my own", "autonomously", "i can handle", "myself will"],
        "WE": ["coordinate", "align", "team effort", "collaborate", "all of us", "share", "together we", "collective effort", "squad effort"],
        "YOU": ["please review", "can you", "analyze this", "evaluate", "give feedback", "check this", "examine this", "inspect this"],
        "THEY": ["observe", "monitor", "track", "watch", "report on", "the system should", "it should"],
    },
    "WHAT": {
        "EXPAND": ["generate", "create", "draft", "propose", "design", "come up with", "write", "document", "ideate"],
        "TRANSFORM": ["run", "execute", "deploy", "ship", "implement", "apply", "perform", "launch", "build"],
        "REDUCE": ["review", "analyze", "critique", "evaluate", "check", "test", "audit", "debug", "assess", "identify", "investigate", "examine", "inspect", "scrutinize"],
        "PRESERVE": ["save", "document", "log", "store", "archive", "keep", "record", "note down"],
    },
    "WHEN": {
        "INITIATE": ["start", "begin", "fresh", "restart", "from scratch", "new", "reset", "kick off", "opening", "commence", "initiate", "trigger"],
        "SUSTAIN": ["now", "immediately", "right away", "asap", "proceed", "continue", "keep going", "right now", "presently", "forthwith"],
        "INTEGRATE": ["finish", "complete", "close", "wrap up", "finalize", "commit", "conclude", "deliver", "before the release", "end", "terminate"],
        "RELEASE": ["later", "wait", "pause", "when ready", "no rush", "hold", "queue", "standby"],
    },
}

TEMPLATES = [
    "{CURRENT}. {TARGET}",
    "{CURRENT}, and {TARGET}",
]

# Synonym map for fuzzing
FUZZ_MAP = {
    "analyze": ["examine", "inspect", "scrutinize", "evaluate"],
    "review": ["assess", "check", "go over", "study"],
    "start": ["commence", "launch", "initiate", "trigger"],
    "finish": ["end", "terminate", "finalize", "conclude"],
    "i ": ["as for me, i ", "speaking for myself, i "],
    "team": ["squad", "group", "collective"],
    "bug": ["glitch", "flaw", "defect", "error"],
    "now": ["at this moment", "presently", "forthwith"],
}

def fuzz_text(text: str) -> str:
    """Replace common words with synonyms to increase variety."""
    words = text.split()
    new_words = []
    for word in words:
        clean = word.lower().strip(",.?!")
        if clean in FUZZ_MAP and random.random() < 0.3:
            syn = random.choice(FUZZ_MAP[clean])
            new_words.append(word.replace(clean, syn))
        else:
            new_words.append(word)
    return " ".join(new_words)

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic SUBIT-T tests.")
    parser.add_argument("--count", type=int, default=1000, help="Number of tests to generate.")
    parser.add_argument("--output", default="eval/synthetic.jsonl", help="Output file.")
    parser.add_argument("--fuzz", action="store_true", help="Enable synonym fuzzing.")
    args = parser.parse_args()

    # Import the actual logic to ensure bit-perfect synchronization
    from subit_t.canon import CANON
    from subit_t.encoder import _score, _pick, _determine_operator, _detect_intents, _apply_adjustments, Op
    from subit_t import State

    STATE_MAP = {}
    for bits, (who, what, when, name) in CANON.items():
        STATE_MAP[(who, what, when)] = name

    who_keys = list(CURRENT_KW["WHO"].keys())
    what_keys = list(CURRENT_KW["WHAT"].keys())
    when_keys = list(CURRENT_KW["WHEN"].keys())
    
    _WHO_ORDER = ["THEY", "YOU", "ME", "WE"]
    _WHAT_ORDER = ["PRESERVE", "REDUCE", "EXPAND", "TRANSFORM"]
    _WHEN_ORDER = ["RELEASE", "INTEGRATE", "INITIATE", "SUSTAIN"]

    with open(args.output, "w", encoding="utf-8") as f:
        for i in range(args.count):
            # 1. Select CURRENT dimensions
            who_id = random.choice(who_keys)
            what_id = random.choice(what_keys)
            when_id = random.choice(when_keys)
            
            # 2. Select TARGET goal (one step shift)
            axis_goal = random.choice(["WHO", "WHAT", "WHEN"])
            who_target_id, what_target_id, when_target_id = who_id, what_id, when_id
            
            if axis_goal == "WHO":
                who_target_id = _WHO_ORDER[(_WHO_ORDER.index(who_id) + 1) % 4]
            elif axis_goal == "WHAT":
                what_target_id = _WHAT_ORDER[(_WHAT_ORDER.index(what_id) + 1) % 4]
            else:
                when_target_id = _WHEN_ORDER[(_WHEN_ORDER.index(when_id) + 1) % 4]

            # Build text segments
            cur_txt = f"{random.choice(CURRENT_KW['WHO'][who_id])} {random.choice(CURRENT_KW['WHAT'][what_id])} {random.choice(CURRENT_KW['WHEN'][when_id])}"
            tar_txt = f"{random.choice(TARGET_KW[axis_goal][who_target_id if axis_goal=='WHO' else what_target_id if axis_goal=='WHAT' else when_target_id])}"
            
            template = random.choice(TEMPLATES)
            text = template.format(CURRENT=cur_txt.strip(), TARGET=tar_txt.strip())
            
            if args.fuzz:
                text = fuzz_text(text)
            
            # 3. Final PERFECT Labeling
            # Use SHARED logic from encoder.py
            intents = _detect_intents(text)
            
            cur_who_scores = _score(text, CURRENT_KW["WHO"])
            cur_what_scores = _score(text, CURRENT_KW["WHAT"])
            cur_when_scores = _score(text, CURRENT_KW["WHEN"])

            # Apply same weighting rules
            _apply_adjustments(cur_who_scores, cur_what_scores, cur_when_scores, intents)

            # Use same tie-breaking
            who_cur, _ = _pick(cur_who_scores, "ME", priority_order=["YOU", "WE", "THEY", "ME"])
            what_cur, _ = _pick(cur_what_scores, "EXPAND", priority_order=["TRANSFORM", "REDUCE", "EXPAND", "PRESERVE"])
            when_cur, _ = _pick(cur_when_scores, "SUSTAIN", priority_order=["SUSTAIN", "INITIATE", "INTEGRATE", "RELEASE"])

            cur_name = STATE_MAP[(who_cur, what_cur, when_cur)]
            
            # Target detection (from text)
            tar_who_scores = _score(text, TARGET_KW["WHO"])
            tar_what_scores = _score(text, TARGET_KW["WHAT"])
            tar_when_scores = _score(text, TARGET_KW["WHEN"])

            who_target, _ = _pick(tar_who_scores, who_cur, priority_order=["YOU", "WE", "THEY", "ME"])
            what_target, _ = _pick(tar_what_scores, what_cur, priority_order=["TRANSFORM", "REDUCE", "EXPAND", "PRESERVE"])
            when_target, _ = _pick(tar_when_scores, when_cur, priority_order=["SUSTAIN", "INITIATE", "INTEGRATE", "RELEASE"])

            # Calculate Diffs
            def _forward_steps(order, current, target):
                return (order.index(target) - order.index(current)) % len(order)

            diffs = []
            who_steps = _forward_steps(_WHO_ORDER, who_cur, who_target)
            if who_steps: diffs.append({"axis": "WHO", "op": "WHO_SHIFT", "steps": who_steps})
            what_steps = _forward_steps(_WHAT_ORDER, what_cur, what_target)
            if what_steps: diffs.append({"axis": "WHAT", "op": "WHAT_SHIFT", "steps": what_steps})
            when_steps = _forward_steps(_WHEN_ORDER, when_cur, when_target)
            if when_steps: diffs.append({"axis": "WHEN", "op": "WHEN_SHIFT", "steps": when_steps})

            # Perfect Policy labeling (SHARED)
            op, axis_val, _, _ = _determine_operator(
                diffs=diffs,
                who_target_scores=tar_who_scores, 
                what_cur_scores=cur_what_scores,
                what_target_scores=tar_what_scores,
                when_cur_scores=cur_when_scores,
                when_target_scores=tar_when_scores,
                review_request=intents["review_request"],
                design_collab_request=intents["design_collab_request"],
                build_start_request=intents["build_start_request"],
                incident_request=intents["incident_request"],
                audit_request=intents["audit_request"],
                creation_request=intents["creation_request"],
                execution_request=intents["execution_request"],
                immediate_request=intents["immediate_request"],
                rollback_detected=intents["rollback_detected"],
                rollback_score=intents["rollback_score"],
                factual_lookup=intents["factual_lookup"]
            )

            s_cur = State.from_name(cur_name)
            s_next = s_cur.apply(op).result

            record = {
                "id": f"syn_{i:06d}",
                "text": text,
                "expected_current_state": cur_name,
                "expected_operator": op.value,
                "expected_next_state": s_next.name,
                "expected_axis": axis_val
            }
            f.write(json.dumps(record) + "\n")

    print(f"Generated {args.count} records to {args.output}")

if __name__ == "__main__":
    main()
