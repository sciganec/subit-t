# Changelog

## [0.4.0] - 2026-04-02

### Deterministic Parity
- Reached 97.3% (Current-State) and 99.7% (Operator Selection) accuracy on synthetic benchmarks
- Refactored `_detect_intents` and `_apply_adjustments` into shared functions to ensure parity between encoder and test generator
- Implemented boundary-aware regex tokenization to eliminate classification noise
- Purged temporary large synthetic datasets to reduce repository weight
- Added `eval/v7_sample.jsonl` (1,000 cases) as the new gold benchmark suite
- Unified `_determine_operator` routing logic to handle multi-intent instructions
- Synchronized React webapp ([subit.js](file:///c:/Users/sciga/subit-t/webapp/src/lib/subit.js)) with the v0.4.0 deterministic core


## [0.3.1] - 2026-04-01

### Runtime and packaging
- Added explicit runtime dependency on `requests`
- Included `integrations` in the packaged distribution
- Synced runtime web user-agent strings to the current package version

### Assistant workflows
- Added assistant profiles for `general`, `review`, `research`, `incident`, `planner`, and `coding`
- Extended `subit chat` and `subit ollama` with `--assistant`
- Kept web-assisted flows resilient: web lookup failures now fall back to local-only responses

### Encoder and evaluation
- Expanded `eval/gold.jsonl` and `eval/challenge.jsonl`
- Added optional model-assisted encoder hints through local Ollama
- Exposed assisted-eval CLI flags in `eval/runner.py`
- Brought current seed datasets to full accuracy and paraphrase consistency

### Quality
- Added smoke tests for runtime, prompts, and integrations
- Hardened Ollama payload validation and assistant runtime behavior

## [0.3.0] - 2026-03-31

### Breaking changes
- Core algebra moved to v3 cyclic routing.
- `Op` now uses `WHO_SHIFT`, `WHAT_SHIFT`, `WHEN_SHIFT`, `INV`.
- Old v2 operators `INIT`, `EXPAND`, `MERGE`, `ACT` are removed from the active model.
- `TransitionResult.idempotent` is always `False` under v3.

### v3 algebra
- `WHO_SHIFT`: `THEY -> YOU -> ME -> WE -> THEY`
- `WHAT_SHIFT`: `PRESERVE -> REDUCE -> EXPAND -> TRANSFORM -> PRESERVE`
- `WHEN_SHIFT`: `RELEASE -> INTEGRATE -> INITIATE -> SUSTAIN -> RELEASE`
- `INV`: global rollback by `-1` on all three axes

### Properties
- `State ~= Z4 x Z4 x Z4`
- 64 states, 4 operators, closed transition system
- zero idempotent transitions
- four forward steps on one axis return to the start
- rollback is deterministic, for example `SYNC -> INV -> PRIME`

### Repository updates
- Core, encoder, router, CLI, integrations and examples updated to v3
- Prompt building and public API aligned around `WHAT`
- README and docs refreshed to match the active model

---

## [0.2.0] - 2026-03-31

### Breaking changes
- `WHERE` was reframed as `WHAT`
- `State.where` became a compatibility alias for `state.what`
- `WHEN` semantics moved from seasons to cycle phases

### Compatibility
- Old names such as `EAST/SOUTH/WEST/NORTH` and `SPRING/SUMMER/AUTUMN/WINTER` still resolve in `State.from_dims(...)`

---

## [0.1.0] - 2026-03-30

### Initial release
- 64-state routing model
- v2 set-to-target operators
- encoder, router, injector and guards
