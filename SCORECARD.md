# Grader robustness scorecard + the "Graderproof Audited" mark

> The barrier/standard play. A public, reproducible scorecard for RL-environment graders, plus a mark builders can display and buyers can require. The moat is not the audit technique (copyable) but being the **reference standard** everyone measures against. Public leaderboard uses only public/open environments; client engagements stay private.

## Why this is the barrier
- A named, public benchmark becomes the procurement reference: buyers ask "is it Graderproof-audited?" and builders integrate the gate to claim it. That creates switching costs (the gate lives in their CI) and a brand/default-name effect.
- It compounds: every public env scored adds a row; every client gate install adds embedding. Neither is copyable by just re-deriving the technique.
- It requires public sanction to publish scores; private client findings are never published without permission (see disclosure policy).

## Metrics (each computed by the gate, `method/scripts/gate.py`)

| ID | Metric | Definition | Mark threshold |
|---|---|---|---|
| M1 | exploit_reachability_after | success rate of known exploits **after** fix | **0.0** |
| M2 | unearned_credit_rate | share of model reward not justified by the grader's documented intent (re-scored end-states) | **≤ 0.02** |
| M3a | judge_false_positive | LLM-judge: rate wrong answers scored correct | ≤ 0.02 |
| M3b | judge_false_negative | LLM-judge: rate correct answers scored wrong | ≤ 0.05 |
| M3c | gate_intact_control | preservation gate returns "none" on a meaning-intact control | must pass |
| M4 | calibration_tails | fraction of tasks confirmed 0% or 100% for the target policy (≥8 rollouts) | reported; 0%-tasks flagged |
| M5 | honest_regression | gold pass-rate after fix vs before | **no decrease** |
| M6 | isolation_noop | no-op scores 0; fresh reset isolates episodes | must pass |

- M1/M5/M6 come from the control battery (noop / gold / known-exploit, before & after fix, ≥2 reps).
- M2 comes from model rollouts + an env-specific "intended reward" re-score plugin.
- M3 applies only to LLM-judge graders; deterministic graders report M3 = n/a.
- M4 requires ≥8 rollouts on the tail tasks; a 1-rollout screen is labelled a screen, not a rate.

## The mark
- **"Graderproof Audited — <env> <version> <date>"** is awarded when M1=0, M2≤0.02, M3 (if applicable) within thresholds, M5 no regression, M6 pass. M4 is published but not a pass/fail gate (difficulty is a design choice, not a defect).
- The mark is version- and date-scoped; re-audit required after a grader change, model upgrade, or new task batch.
- Displaying the mark without a passing scorecard, or on an un-audited version, is a misuse we publicly correct.

## Public leaderboard schema (open environments only)
```json
{
  "env": "owner/name", "version": "...", "audited_at": "YYYY-MM-DD",
  "grader_type": "deterministic | llm-judge | hybrid",
  "M1_after": 0.0, "M2": 0.0, "M3a": null, "M3b": null, "M3c": null,
  "M4_zero_frac": 0.23, "M4_full_frac": 0.06,
  "M5_regression": false, "M6_pass": true,
  "mark": true, "report": "<link or 'private'>", "gate_version": "..."
}
```
- Seed rows are added after coordinated disclosure; no environment is named without permission.
- Leaderboard is append-only; historical rows retained so regressions are visible.

## How the gate embeds (the switching cost)
- `method/scripts/gate.py score --results <run> --rescore <plugin> --thresholds SCORECARD.md` emits `scorecard.json` + `scorecard.md` and **exits non-zero on any mark-threshold breach**.
- Builders drop it into CI as a batch gate: every new task batch must pass before shipping. Once embedded, replacing it means re-wiring CI and re-earning the mark — the switching cost.
- The gate is client-free and open; the *mark* and the *leaderboard* are what we operate. Open gate + operated standard = adoption without giving away the moat.

## Limits / honesty
- Thresholds are our proposal, not industry consensus; publish them and invite comment.
- M2 depends on a correct "intended reward" plugin per env; a wrong plugin gives a wrong M2. Plugins are reviewed and versioned.
- Public scores only for open envs or with written permission; never leak client findings.
