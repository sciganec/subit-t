"""
SUBIT-T Canon — 64 archetypal states.

State = WHO × WHAT × WHEN
Each dimension has 4 values encoded as 2-bit integers.
Total: 4³ = 64 states, represented as 6-bit integers (0–63).

Ontological basis:
  WHO  = orientation of attention  (where is the agent directed?)
  WHAT = operation on information  (what does the agent do with uncertainty?)
  WHEN = phase of cognitive cycle  (where in the rhythm of action?)

Bit layout:
  [ b5 b4 | b3 b2 | b1 b0 ]
    WHO     WHAT    WHEN

Backward compatibility:
  WHAT values map to old WHERE names (same bits, new semantics):
    EXPAND    = EAST  (10)
    TRANSFORM = SOUTH (11)
    REDUCE    = WEST  (01)
    PRESERVE  = NORTH (00)

  WHEN values map to old WHEN names (same bits, new semantics):
    INITIATE  = SPRING (10)
    SUSTAIN   = SUMMER (11)
    INTEGRATE = AUTUMN (01)
    RELEASE   = WINTER (00)
"""

# ── WHO — Orientation of attention ───────────────────────────────────────────

WHO = {"ME": 0b10, "WE": 0b11, "YOU": 0b01, "THEY": 0b00}
WHO_I = {v: k for k, v in WHO.items()}

WHO_LABEL = {
    "ME":   "self-directed",    # autonomous action, internal process
    "WE":   "co-directed",      # shared construction, coordination
    "YOU":  "other-directed",   # response to external input
    "THEY": "system-directed",  # meta-level, external observation
}

WHO_DESCRIPTION = {
    "ME":   "Agent acts autonomously, from its own initiative and internal state.",
    "WE":   "Agent acts as part of a collective, coordinating with others.",
    "YOU":  "Agent responds to and is directed by an external input or agent.",
    "THEY": "Agent observes and acts at the system level, detached from direct action.",
}

# ── WHAT — Operation on information ──────────────────────────────────────────
# What does the agent do with uncertainty / information space?

WHAT = {
    "EXPAND":    0b10,  # (was EAST)
    "TRANSFORM": 0b11,  # (was SOUTH)
    "REDUCE":    0b01,  # (was WEST)
    "PRESERVE":  0b00,  # (was NORTH)
}
WHAT_I = {v: k for k, v in WHAT.items()}

WHAT_LABEL = {
    "EXPAND":    "expand",     # increase possibility space
    "TRANSFORM": "transform",  # change form without changing quantity
    "REDUCE":    "reduce",     # narrow possibility space
    "PRESERVE":  "preserve",   # fix without change
}

WHAT_DESCRIPTION = {
    "EXPAND":    "Increases the space of possibilities. Generation, divergence, ideation.",
    "TRANSFORM": "Changes form while preserving quantity. Execution, implementation, conversion.",
    "REDUCE":    "Narrows the space of possibilities. Analysis, convergence, critique.",
    "PRESERVE":  "Fixes state without transformation. Memory, storage, observation.",
}

# Backward compatibility aliases
WHERE = {
    "EAST":  0b10,
    "SOUTH": 0b11,
    "WEST":  0b01,
    "NORTH": 0b00,
}
WHERE_I = {v: k for k, v in WHERE.items()}
WHERE_LABEL = {
    "EAST":  "expand",
    "SOUTH": "transform",
    "WEST":  "reduce",
    "NORTH": "preserve",
}

# Mapping between old and new names
WHAT_TO_WHERE = {"EXPAND": "EAST", "TRANSFORM": "SOUTH", "REDUCE": "WEST", "PRESERVE": "NORTH"}
WHERE_TO_WHAT = {"EAST": "EXPAND", "SOUTH": "TRANSFORM", "WEST": "REDUCE", "NORTH": "PRESERVE"}

# ── WHEN — Phase of cognitive cycle ──────────────────────────────────────────
# Where is the agent in the rhythm of action?

WHEN = {
    "INITIATE":  0b10,  # (was SPRING)
    "SUSTAIN":   0b11,  # (was SUMMER)
    "INTEGRATE": 0b01,  # (was AUTUMN)
    "RELEASE":   0b00,  # (was WINTER)
}
WHEN_I = {v: k for k, v in WHEN.items()}

WHEN_LABEL = {
    "INITIATE":  "initiate",   # open new cycle
    "SUSTAIN":   "sustain",    # maintain active process
    "INTEGRATE": "integrate",  # synthesize results
    "RELEASE":   "release",    # complete cycle, ready for next
}

WHEN_DESCRIPTION = {
    "INITIATE":  "Opening a new cycle. First impulse, maximum uncertainty, fresh start.",
    "SUSTAIN":   "Maintaining active process. Peak activity, full capacity, flow state.",
    "INTEGRATE": "Integrating results. Synthesis, closing, convergence of outputs.",
    "RELEASE":   "Completing the cycle. Idle, ready, latent potential for next cycle.",
}

# Backward compatibility aliases
WHEN_OLD = {
    "SPRING": 0b10,
    "SUMMER": 0b11,
    "AUTUMN": 0b01,
    "WINTER": 0b00,
}
WHEN_OLD_I = {v: k for k, v in WHEN_OLD.items()}
WHEN_OLD_LABEL = {
    "SPRING": "initiate",
    "SUMMER": "sustain",
    "AUTUMN": "integrate",
    "WINTER": "release",
}

WHEN_TO_OLD = {"INITIATE": "SPRING", "SUSTAIN": "SUMMER", "INTEGRATE": "AUTUMN", "RELEASE": "WINTER"}
OLD_TO_WHEN = {"SPRING": "INITIATE", "SUMMER": "SUSTAIN", "AUTUMN": "INTEGRATE", "WINTER": "RELEASE"}


# ── Internal bit builder ──────────────────────────────────────────────────────

def _make_bits(who: str, what: str, when: str) -> int:
    """
    Build 6-bit state integer.
    Accepts both new names (EXPAND/TRANSFORM/REDUCE/PRESERVE, INITIATE/SUSTAIN/INTEGRATE/RELEASE)
    and old names (EAST/SOUTH/WEST/NORTH, SPRING/SUMMER/AUTUMN/WINTER) for backward compatibility.
    """
    # Normalize WHAT (accept old WHERE names)
    what_bits = WHAT.get(what) if what in WHAT else WHERE.get(what)
    if what_bits is None:
        raise KeyError(f"Unknown WHAT/WHERE value: '{what}'")

    # Normalize WHEN (accept old season names)
    when_bits = WHEN.get(when) if when in WHEN else WHEN_OLD.get(when)
    if when_bits is None:
        raise KeyError(f"Unknown WHEN value: '{when}'")

    return (WHO[who] << 4) | (what_bits << 2) | when_bits


# ── Canon entries ─────────────────────────────────────────────────────────────
# Format: (WHO, WHAT, WHEN, name)
# WHAT uses new semantic names; old WHERE names in comments for reference

_ENTRIES = [
    # ME · EXPAND (was EAST) — self-directed expansion
    ("ME", "EXPAND", "INITIATE",  "PRIME"),      # autonomous genesis
    ("ME", "EXPAND", "SUSTAIN",   "AUTHOR"),      # autonomous peak generation
    ("ME", "EXPAND", "INTEGRATE", "DRAFTER"),     # autonomous closing generation
    ("ME", "EXPAND", "RELEASE",   "SEED"),        # autonomous latent generation

    # ME · TRANSFORM (was SOUTH) — self-directed transformation
    ("ME", "TRANSFORM", "INITIATE",  "LAUNCHER"), # autonomous execution start
    ("ME", "TRANSFORM", "SUSTAIN",   "DRIVER"),   # autonomous peak execution
    ("ME", "TRANSFORM", "INTEGRATE", "CLOSER"),   # autonomous closing execution
    ("ME", "TRANSFORM", "RELEASE",   "ENGINE"),   # autonomous latent execution

    # ME · REDUCE (was WEST) — self-directed reduction
    ("ME", "REDUCE", "INITIATE",  "PROBE"),       # autonomous analysis start
    ("ME", "REDUCE", "SUSTAIN",   "AUDITOR"),     # autonomous peak analysis
    ("ME", "REDUCE", "INTEGRATE", "REFINER"),     # autonomous closing analysis
    ("ME", "REDUCE", "RELEASE",   "WATCHER"),     # autonomous latent analysis

    # ME · PRESERVE (was NORTH) — self-directed preservation
    ("ME", "PRESERVE", "INITIATE",  "LOGGER"),    # autonomous storage start
    ("ME", "PRESERVE", "SUSTAIN",   "ARCHIVIST"), # autonomous peak storage
    ("ME", "PRESERVE", "INTEGRATE", "INDEXER"),   # autonomous closing storage
    ("ME", "PRESERVE", "RELEASE",   "HERMIT"),    # autonomous latent storage

    # WE · EXPAND (was EAST) — co-directed expansion
    ("WE", "EXPAND", "INITIATE",  "SPARK"),       # collective ideation start
    ("WE", "EXPAND", "SUSTAIN",   "CHORUS"),      # collective peak generation
    ("WE", "EXPAND", "INTEGRATE", "MERGE"),       # collective synthesis
    ("WE", "EXPAND", "RELEASE",   "POOL"),        # collective latent generation

    # WE · TRANSFORM (was SOUTH) — co-directed transformation
    ("WE", "TRANSFORM", "INITIATE",  "DEPLOY"),   # collective execution start
    ("WE", "TRANSFORM", "SUSTAIN",   "SYNC"),     # collective peak execution
    ("WE", "TRANSFORM", "INTEGRATE", "COMMIT"),   # collective closing execution
    ("WE", "TRANSFORM", "RELEASE",   "STANDBY"),  # collective latent execution

    # WE · REDUCE (was WEST) — co-directed reduction
    ("WE", "REDUCE", "INITIATE",  "COUNCIL"),     # collective analysis start
    ("WE", "REDUCE", "SUSTAIN",   "TRIBUNAL"),    # collective peak analysis
    ("WE", "REDUCE", "INTEGRATE", "VERDICT"),     # collective closing analysis
    ("WE", "REDUCE", "RELEASE",   "QUORUM"),      # collective latent analysis

    # WE · PRESERVE (was NORTH) — co-directed preservation
    ("WE", "PRESERVE", "INITIATE",  "LEDGER"),    # collective storage start
    ("WE", "PRESERVE", "SUSTAIN",   "REGISTRY"),  # collective peak storage
    ("WE", "PRESERVE", "INTEGRATE", "DIGEST"),    # collective closing storage
    ("WE", "PRESERVE", "RELEASE",   "ORIGIN"),    # collective root memory

    # YOU · EXPAND (was EAST) — other-directed expansion
    ("YOU", "EXPAND", "INITIATE",  "RESPONDER"),  # reactive generation start
    ("YOU", "EXPAND", "SUSTAIN",   "ADAPTER"),    # reactive peak generation
    ("YOU", "EXPAND", "INTEGRATE", "ECHO"),       # reactive closing generation
    ("YOU", "EXPAND", "RELEASE",   "BUFFER"),     # reactive latent generation

    # YOU · TRANSFORM (was SOUTH) — other-directed transformation
    ("YOU", "TRANSFORM", "INITIATE",  "HANDLER"), # reactive execution start
    ("YOU", "TRANSFORM", "SUSTAIN",   "EXECUTOR"),# reactive peak execution
    ("YOU", "TRANSFORM", "INTEGRATE", "RESOLVER"),# reactive closing execution
    ("YOU", "TRANSFORM", "RELEASE",   "QUEUE"),   # reactive latent execution

    # YOU · REDUCE (was WEST) — other-directed reduction
    ("YOU", "REDUCE", "INITIATE",  "INTAKE"),     # reactive analysis start
    ("YOU", "REDUCE", "SUSTAIN",   "SCAN"),       # reactive peak analysis
    ("YOU", "REDUCE", "INTEGRATE", "FILTER"),     # reactive closing analysis
    ("YOU", "REDUCE", "RELEASE",   "LISTENER"),   # reactive latent analysis

    # YOU · PRESERVE (was NORTH) — other-directed preservation
    ("YOU", "PRESERVE", "INITIATE",  "INTAKE_LOG"),# reactive storage start
    ("YOU", "PRESERVE", "SUSTAIN",   "CACHE"),    # reactive peak storage
    ("YOU", "PRESERVE", "INTEGRATE", "SNAPSHOT"), # reactive closing storage
    ("YOU", "PRESERVE", "RELEASE",   "VOID"),     # reactive null state

    # THEY · EXPAND (was EAST) — system-directed expansion
    ("THEY", "EXPAND", "INITIATE",  "GHOST"),     # system-level impulse
    ("THEY", "EXPAND", "SUSTAIN",   "ORACLE"),    # system-level generation peak
    ("THEY", "EXPAND", "INTEGRATE", "SIGNAL"),    # system-level closing signal
    ("THEY", "EXPAND", "RELEASE",   "SHADOW"),    # system-level latent generation

    # THEY · TRANSFORM (was SOUTH) — system-directed transformation
    ("THEY", "TRANSFORM", "INITIATE",  "TRIGGER"),# system-level activation
    ("THEY", "TRANSFORM", "SUSTAIN",   "FORCE"),  # system-level peak action
    ("THEY", "TRANSFORM", "INTEGRATE", "SWEEP"),  # system-level cleanup
    ("THEY", "TRANSFORM", "RELEASE",   "DAEMON"), # system-level background process

    # THEY · REDUCE (was WEST) — system-directed reduction
    ("THEY", "REDUCE", "INITIATE",  "INSPECTOR"), # system-level scan start
    ("THEY", "REDUCE", "SUSTAIN",   "MONITOR"),   # system-level peak observation
    ("THEY", "REDUCE", "INTEGRATE", "VALIDATOR"), # system-level validation
    ("THEY", "REDUCE", "RELEASE",   "SENTINEL"),  # system-level passive watch

    # THEY · PRESERVE (was NORTH) — system-directed preservation
    ("THEY", "PRESERVE", "INITIATE",  "IMPRINT"), # system-level context capture
    ("THEY", "PRESERVE", "SUSTAIN",   "LEDGER_SYS"),# system-level peak storage
    ("THEY", "PRESERVE", "INTEGRATE", "FOSSIL"),  # system-level immutable record
    ("THEY", "PRESERVE", "RELEASE",   "CORE"),    # ground state — absolute source
]


# ── Public dicts ──────────────────────────────────────────────────────────────

# bits → (who, what, when, name)
CANON: dict[int, tuple[str, str, str, str]] = {
    _make_bits(w, wh, wn): (w, wh, wn, name)
    for w, wh, wn, name in _ENTRIES
}

# name → bits
BY_NAME: dict[str, int] = {
    name: _make_bits(w, wh, wn)
    for w, wh, wn, name in _ENTRIES
}


STATE_TYPE: dict[str, str] = {
    "CORE": "core",
    "PRIME": "core",
    "SYNC": "core",
    "SCAN": "core",
    "DRIVER": "core",
    "COUNCIL": "core",
    "EXECUTOR": "core",
    "MONITOR": "core",
    "DAEMON": "core",
    "SENTINEL": "core",
}

for _, _, _, _state_name in _ENTRIES:
    STATE_TYPE.setdefault(_state_name, "transient")


STATE_WEIGHT: dict[str, float] = {
    state_name: (1.0 if STATE_TYPE[state_name] == "core" else 0.7)
    for _, _, _, state_name in _ENTRIES
}
