# Graderproof

**Adversarial audits for RL-environment graders.** We try to beat the grader, then patch it and prove the exploit no longer works.

RL environments train agents inside simulated workplaces — fake email, accounting, CRM, legal ops. If the grader is weak, the agent learns to game the check instead of doing the job. Graderproof finds those shortcuts, patches the grader, and re-runs the proof.

## What is here

| Path | Holds |
|---|---|
| `method/` | Adapter-based audit framework, MIT: evidence store, metrics, verdicts, CLI, tests, batch gate |
| `SCORECARD.md` | Public robustness scorecard and the "Graderproof Audited" criteria |
| `QA-GATE-PATTERN.md` | Clean-room design note for the batch gate |
| `examples/toy-audit.md` | Reproducible synthetic proof: broken grader → exploit 1.0; fixed → 0.0 |

## Quickstart

```bash
git clone https://github.com/asebaq/graderproof
cd graderproof/method
uv run --extra dev pytest
uv run python -m graderproof run --toy broken --reps 2 --arms noop gold exploit --out /tmp/toy-broken
uv run python -m graderproof run --toy fixed --reps 2 --arms noop gold exploit --out /tmp/toy-fixed
```

The first run reports a finding; the second reports no finding. See `examples/toy-audit.md`.

## Free audit

We audit one environment free for 3 days. You get the exploits whether or not you hire us. Open an issue with the environment repo or image and the grader code.

## Disclosure

Coordinated, not surprise-public: notify the maintainer, offer the patch, default 90-day window, sanitize before publishing. See `DISCLOSURE.md`. Client findings stay private unless the client gives written permission.

## Scope

This repository publishes the method and a synthetic proof. It does not contain client artifacts or private findings. Real case studies are published only after coordinated disclosure.

## License

`method/` is MIT. Docs, findings, scorecard operation, and the "Graderproof Audited" mark are proprietary. See `LICENSE` and `NOTICE`.

## Contact

GitHub: `@asebaq`. Open an issue for a free audit.
