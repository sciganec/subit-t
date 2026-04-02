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


def evaluate(records: list[dict], *, model_assisted: bool, model: str, timeout: int) -> dict:
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

    for record in records:
        totals["examples"] += 1
        scored = score_record(record["text"], record, model_assisted=model_assisted, model=model, timeout=timeout)
        totals["current_state_correct"] += int(scored["matches_current_state"])
        totals["operator_correct"] += int(scored["matches_operator"])
        totals["next_state_correct"] += int(scored["matches_next_state"])
        totals["axis_correct"] += int(scored["matches_axis"])

        if not all(
            [
                scored["matches_current_state"],
                scored["matches_operator"],
                scored["matches_next_state"],
                scored["matches_axis"],
            ]
        ):
            failures.append(
                {
                    "id": record["id"],
                    "text": record["text"],
                    "expected": {
                        "current_state": record["expected_current_state"],
                        "operator": record["expected_operator"],
                        "next_state": record["expected_next_state"],
                        "axis": record["expected_axis"],
                    },
                    "predicted": {
                        "current_state": scored["current_state"],
                        "operator": scored["operator"],
                        "next_state": scored["next_state"],
                        "axis": scored["axis"],
                    },
                }
            )

        paraphrases = record.get("paraphrases", [])
        if paraphrases:
            totals["paraphrase_examples"] += 1
            base_operator = scored["operator"]
            if all(
                encode(text, model_assisted=model_assisted, model=model, timeout=timeout).operator.value == base_operator
                for text in paraphrases
            ):
                totals["paraphrase_operator_consistent"] += 1

    examples = max(totals["examples"], 1)
    paraphrase_examples = max(totals["paraphrase_examples"], 1)
    return {
        "totals": totals,
        "metrics": {
            "current_state_accuracy": totals["current_state_correct"] / examples,
            "operator_accuracy": totals["operator_correct"] / examples,
            "next_state_accuracy": totals["next_state_correct"] / examples,
            "axis_accuracy": totals["axis_correct"] / examples,
            "paraphrase_operator_consistency": totals["paraphrase_operator_consistent"] / paraphrase_examples
            if totals["paraphrase_examples"]
            else None,
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
    if report["metrics"]["paraphrase_operator_consistency"] is not None:
        print(f"Paraphrase consistency: {report['metrics']['paraphrase_operator_consistency']:.1%}")

    if report["failures"]:
        print("\nSample failures:")
        for failure in report["failures"][: args.show_failures]:
            print(f"- {failure['id']}")
            print(f"  Text:      {failure['text']}")
            print(f"  Expected:  {failure['expected']}")
            print(f"  Predicted: {failure['predicted']}")


if __name__ == "__main__":
    main()
