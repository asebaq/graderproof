# Synthetic proof — broken vs fixed grader

The `toy` adapter is synthetic and shipped in `method/graderproof/adapters/toy.py`. No client data. It exists so the framework can be tested without a model or an environment.

## Broken grader

```bash
uv run python -m graderproof run --toy broken --reps 2 \
  --arms noop gold exploit --out /tmp/toy-broken
```

**Status:** finding

| arm | n | mean reward | reach |
|---|---:|---:|---:|
| exploit | 6 | 1.0000 | 1.0000 |
| gold | 6 | 1.0000 | 1.0000 |
| noop | 6 | 0.0000 | 0.0000 |

| metric | value |
|---|---:|
| n | 18 |
| valid_n | 18 |
| errors | 0 |
| tasks | 3 |
| coverage | 1.0000 |
| exploit_mean | 1.0000 |
| gold_mean | 1.0000 |
| noop_mean | 0.0000 |
| unearned_credit_rate | 0.5000 |
| unearned_n | 18 |

## Fixed grader

```bash
uv run python -m graderproof run --toy fixed --reps 2 \
  --arms noop gold exploit --out /tmp/toy-fixed
```

**Status:** no_finding

| arm | n | mean reward | reach |
|---|---:|---:|---:|
| exploit | 6 | 0.0000 | 0.0000 |
| gold | 6 | 1.0000 | 1.0000 |
| noop | 6 | 0.0000 | 0.0000 |

| metric | value |
|---|---:|
| n | 18 |
| valid_n | 18 |
| errors | 0 |
| tasks | 3 |
| coverage | 1.0000 |
| exploit_mean | 0.0000 |
| gold_mean | 1.0000 |
| noop_mean | 0.0000 |
| unearned_credit_rate | 0.0000 |
| unearned_n | 18 |

## What this shows

The framework separates a broken grader from a fixed one with three controls: no-op (must score 0), gold (must score full), and a known exploit. The broken run has `exploit_mean = 1.0` and `unearned_credit_rate = 0.5`; the fixed run has `exploit_mean = 0.0` and `unearned_credit_rate = 0.0`, with gold still at 1.0. No model is needed for this check.
