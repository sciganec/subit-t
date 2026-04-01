# SUBIT-T Operators

SUBIT-T v3 has four cyclic operators.

## WHO_SHIFT

Moves WHO forward by one step:

```text
THEY -> YOU -> ME -> WE -> THEY
```

Example:

```python
State.from_name("DRIVER").apply(Op.WHO_SHIFT).result.name  # SYNC
```

## WHAT_SHIFT

Moves WHAT forward by one step:

```text
PRESERVE -> REDUCE -> EXPAND -> TRANSFORM -> PRESERVE
```

Example:

```python
State.from_name("PRIME").apply(Op.WHAT_SHIFT).result.name  # LAUNCHER
```

## WHEN_SHIFT

Moves WHEN forward by one step:

```text
RELEASE -> INTEGRATE -> INITIATE -> SUSTAIN -> RELEASE
```

Example:

```python
State.from_name("DRAFTER").apply(Op.WHEN_SHIFT).result.name  # SEED
```

## INV

Moves all three axes backward by one step at once.

Example:

```python
State.from_name("SYNC").apply(Op.INV).result.name  # PRIME
```

## Properties

- Every operator changes the state
- Four repeated forward shifts on the same axis return to the starting state
- `INV` is the rollback operator for recovery and backtracking
- Operators are composable, so trajectories can be reasoned about step by step
