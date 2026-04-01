# SUBIT-T Canon

Generated from `subit_t/canon.py`.

```text
State = WHO x WHAT x WHEN = 4 x 4 x 4 = 64
```

The canonical state table is organized by axis values:

## WHO

- `THEY`: system-directed
- `YOU`: other-directed
- `ME`: self-directed
- `WE`: co-directed

## WHAT

- `PRESERVE`: hold and record
- `REDUCE`: analyze and narrow
- `EXPAND`: generate and open
- `TRANSFORM`: execute and change form

## WHEN

- `RELEASE`: latent or resting
- `INTEGRATE`: closing and synthesis
- `INITIATE`: opening impulse
- `SUSTAIN`: active peak

## Reference states

| State | WHO | WHAT | WHEN |
|------|-----|------|------|
| `CORE` | THEY | PRESERVE | RELEASE |
| `SCAN` | YOU | REDUCE | SUSTAIN |
| `PRIME` | ME | EXPAND | INITIATE |
| `SYNC` | WE | TRANSFORM | SUSTAIN |

## Useful trajectories

| Start | Operator | Result |
|-------|----------|--------|
| `DRIVER` | `WHO_SHIFT` | `SYNC` |
| `PRIME` | `WHAT_SHIFT` | `LAUNCHER` |
| `DRAFTER` | `WHEN_SHIFT` | `SEED` |
| `SYNC` | `INV` | `PRIME` |

For the full canonical mapping, the source of truth is [subit_t/canon.py](C:\Users\sciga\subit-t\subit_t\canon.py).
