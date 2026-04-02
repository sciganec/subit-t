"""Lightweight evaluation runner for SUBIT-T encoder datasets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from subit_t import encode


EVAL_DIR = Path(__file__).resolve().parent


def load_records(path: Path) -> list[dict]:
    records = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def score_record(text: str, record: dict, *, model_assisted: bool, model: str, timeout: int) -> dict:
    result = encode(text, model_assisted=model_assisted, model=model, timeout=timeout)
    return {
        "current_state": result.current_state.name,
        "operator": result.operator.value,
        "next_state": result.target_state.name,
        "axis": result.axis_diff,
        "model_assisted": result.model_assisted,
        "matches_current_state": result.current_state.name == record["expected_current_state"],
        "matches_operator": result.operator.value == record["expected_operator"],
        "matches_next_state": result.target_state.name == record["expected_next_state"],
        "matches_axis": result.axis_diff == record["expected_axis"],
    }


from concurrent.futures import ProcessPoolExecutor, as_completed
import sys
from functools import partial

def _task_wrapper(record, model_assisted, model, timeout):
    return score_record(record["text"], record, model_assisted=model_assisted, model=model, timeout=timeout)

def evaluate(records: list[dict], *, model_assisted: bool, model: str, timeout: int, workers: int = 4) -> dict:
    totals = {
        "examples": 0,
        "current_state_correct": 0,
        "operator_correct": 0,
        "next_state_correct": 0,
        "axis_correct": 0,
        "paraphrase_examples": 0,
        "paraphrase_operator_consistent": 0,
    }
    failures = []

    print(f"Starting evaluation of {len(records)} examples across {workers} workers...")

    # Use partial to fix arguments for the top-level wrapper
    task = partial(_task_wrapper, model_assisted=model_assisted, model=model, timeout=timeout)

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(task, r): r for r in records}
        
        for i, future in enumerate(as_completed(futures)):
            record = futures[future]
            scored = future.result()
            
            totals["examples"] += 1
            totals["current_state_correct"] += int(scored["matches_current_state"])
            totals["operator_correct"] += int(scored["matches_operator"])
            totals["next_state_correct"] += int(scored["matches_next_state"])
            totals["axis_correct"] += int(scored["matches_axis"])

            if not all([scored["matches_current_state"], scored["matches_operator"], scored["matches_next_state"], scored["matches_axis"]]):
                if len(failures) < 100: # Cap failures to prevent memory blooming
                    failures.append({
                        "id": record["id"],
                        "text": record["text"],
                        "expected": {
                            "current_state": record["expected_current_state"],
                            "operator": record["expected_operator"],
                            "next_state": record["expected_next_state"],
                            "axis": record["expected_axis"],
                        },
                        "predicted": scored,
                    })

            if i > 0 and i % 500 == 0:
                sys.stdout.write(f"\rProgress: {i}/{len(records)} ({i/len(records):.1%})")
                sys.stdout.flush()

    print(f"\rProgress: {len(records)}/{len(records)} (100.0%)")

    examples = max(totals["examples"], 1)
    return {
        "totals": totals,
        "metrics": {
            "current_state_accuracy": totals["current_state_correct"] / examples,
            "operator_accuracy": totals["operator_correct"] / examples,
            "next_state_accuracy": totals["next_state_correct"] / examples,
            "axis_accuracy": totals["axis_correct"] / examples,
        },
        "failures": failures,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run SUBIT-T encoder evaluation on a JSONL dataset.")
    parser.add_argument("--dataset", default="eval/gold.jsonl", help="Path to a JSONL dataset.")
    parser.add_argument("--show-failures", type=int, default=10, help="Number of failures to print.")
    parser.add_argument("--model-assisted", action="store_true", help="Use the optional model-assisted encoder layer.")
    parser.add_argument("--encoder-model", default="llama3.2", help="Ollama model used for model-assisted encoding.")
    parser.add_argument("--encoder-timeout", type=int, default=20, help="Timeout for model-assisted encoding requests.")
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    if not dataset_path.is_absolute():
        dataset_path = (EVAL_DIR.parent / dataset_path).resolve()
    records = load_records(dataset_path)
    report = evaluate(records, model_assisted=args.model_assisted, model=args.encoder_model, timeout=args.encoder_timeout)

    print(f"Dataset: {dataset_path}")
    print(f"Model-assisted: {'on' if args.model_assisted else 'off'}")
    print(f"Examples: {report['totals']['examples']}")
    print(f"Current-state accuracy: {report['metrics']['current_state_accuracy']:.1%}")
    print(f"Operator accuracy:      {report['metrics']['operator_accuracy']:.1%}")
    print(f"Next-state accuracy:    {report['metrics']['next_state_accuracy']:.1%}")
    print(f"Axis accuracy:          {report['metrics']['axis_accuracy']:.1%}")

    if report["failures"]:
        print("\nSample failures:")
        for failure in report["failures"][: args.show_failures]:
            print(f"- {failure['id']}")
            print(f"  Text:      {failure['text']}")
            print(f"  Expected:  {failure['expected']}")
            print(f"  Predicted: {failure['predicted']}")


if __name__ == "__main__":
    main()
