# QA gate pattern — clean-room method note

A gate that rejects bad batches before expensive downstream work. This is a pattern, not a port: no employer code, prompts, thresholds, customer names, or internal reviewer data. It is generic production-QA practice applied to RL graders.

## Why a gate, not a scorecard

A scorecard tells you how bad a batch is. A gate stops it. The gate is the product surface that embeds in CI; the scorecard is the evidence that it works. The pattern below is how the gate is designed, independent of any one environment.

## Stages

1. **Intake.** Validate the batch manifest: schema, required metadata, version pin, reference availability. Fail closed on missing fields.
2. **Hard checks.** Deterministic, cheap, fail closed. For grader QA: no-op scores above zero, gold below full, a known exploit still reachable, isolation failure, reference mismatch. A hard failure blocks the batch.
3. **Soft checks.** Probabilistic or expensive; warn, do not block. Calibration tails, judge false negatives, low honest pass rate, cost/latency drift. A soft warning is recorded and reviewed; it does not silently pass.
4. **Shadow mode.** Run a new check on existing rollouts first. Compare its decisions to human labels. Promote to hard/soft only after precision and recall are reviewed. Never enforce an uncalibrated check on a live batch.
5. **Rejection record.** Every failure carries: code, measured value, threshold, guidance, evidence link. One reason per failure. No opaque score. The client must be able to act on the rejection without asking what it meant.
6. **Regression fixtures.** A fixed battery of known-good, known-bad, and edge cases. Run it on every change to the gate. Fixtures are synthetic or public; no customer data.
7. **Human review.** Final sign-off. A reviewer can override with a reason; overrides are logged and feed back into threshold calibration. The gate is not the final authority on a judgment call.
8. **Observability.** Pass rate, false-positive and false-negative rate, time-to-fix, escape rate. Alert on drift. A gate with no telemetry is a guess.

## Mapping to grader QA

| Pattern stage | Grader QA implementation |
|---|---|
| Intake | Environment manifest: image digest, task count, grader version, reference availability |
| Hard checks | M1 exploit reachable, M6 no-op > 0, M5 gold regression, isolation failure |
| Soft checks | Calibration tails, judge false negatives, honest pass rate below the learning band |
| Shadow mode | Run the new check on the last batch's rollouts before blocking the next batch |
| Rejection record | Finding ID, measured reward delta, threshold, fix guidance, evidence hash |
| Regression fixtures | No-op, gold, known exploit, fresh reset; rerun on every grader change |
| Human review | Client engineer signs off on the patch and the after-fix rerun |
| Observability | Per-batch pass rate, false positives, time-to-fix, escapes |

## Rules

- Thresholds are versioned and calibrated on reviewer outcomes, not invented.
- Hard checks must be deterministic and cheap; soft checks may be probabilistic.
- A gate that cannot explain a rejection is not a gate.
- Shadow before enforce.
- No customer data in fixtures; synthesize or use public environments.
- A gate is not a pivot to data QA. The buyer remains the RL environment builder; the gate is how the audit stays fixed.

## What this note is not

It is not a copy of any employer's pipeline, code, thresholds, prompts, or customer data. It is a generic design note for the Graderproof batch gate.
