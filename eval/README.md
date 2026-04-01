# Evaluation Assets

This folder contains seed datasets and a lightweight runner for evaluating the SUBIT-T encoder.

Files:
- `gold.jsonl`: clearer, higher-confidence examples
- `challenge.jsonl`: noisier or more ambiguous examples
- `runner.py`: computes simple accuracy metrics against one of the datasets

Each record may include:
- `id`
- `domain`
- `text`
- `paraphrases`
- `expected_current_state`
- `expected_operator`
- `expected_next_state`
- `expected_axis`
- `confidence`
- `tags`
- `notes`

Run:

```powershell
python eval\runner.py
python eval\runner.py --dataset eval\challenge.jsonl
```
