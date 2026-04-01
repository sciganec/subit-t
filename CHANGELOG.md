# Changelog

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
