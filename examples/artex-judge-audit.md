# Case study: the benchmark judge of ARTEX

ARTEX is an open-source penetration-testing agent with about 23,000 GitHub stars. It scores its own agent with a benchmark in which an LLM judge matches the agent's findings against eight known vulnerabilities in OWASP Juice Shop. Its roadmap plans to adopt changes to the agent when benchmark results improve, so a judge that can be gamed would steer that process.

The findings and the fix are public in [issue #619](https://github.com/BaaRai/ARTEX/issues/619) and [pull request #636](https://github.com/BaaRai/ARTEX/pull/636) of the ARTEX repository. The re-run below was done by the auditor after the fix was merged.

## What was audited

The judge code, unchanged, at commit `e5c7bfc`. Only the model transport was swapped. Judge model: `claude-haiku-5-5`, 12 runs per finding set. ARTEX's own judge self-test passed 3 of 3 before any run.

No ARTEX task was run. The finding sets were fed straight to the judge.

## What was found

| Finding set | Should score (of 8) | Scored |
|---|---:|---:|
| One correct finding per vulnerability (control) | 8 | 8.00 |
| One finding that names all eight | at most 1 | 8.00 |
| 36 findings saying "possible bug, not verified, no request sent" | 0 | 5.83 |
| Findings a model wrote from memory, never seeing the target or the answer key | 0 | 5.42 |

A second judge model, `claude-sonnet-5-5`, gave 8.00, 6.00 and 4.33 on the last three rows in 3 to 4 runs each.

Two causes were in the code. One finding could be credited against several vulnerabilities, and a finding counted as detected even when its proof check failed.

## What happened next

- Reported as issue #619 on 2026-11-27, with a suggested patch.
- Fixed by the maintainer in pull request #636, merged 13 hours later. The finding sets from the report were added to the project's test suite.

## Re-run on the fixed code

Same sets, same judge model, 12 runs per set, at commit `5f5ec32`. ARTEX's self-test passed 3 of 3 and its test suite passed.

| Finding set | Before | After |
|---|---:|---:|
| Control | 8.00 | 8.00 |
| One finding naming all eight | 8.00 | 1.00 |
| 36 unverified findings, as reported | 5.83 | 0.00 |
| The same 36, reworded | 6.00 | 0.00 |
| Written from memory | 5.42 | 3.00 |

- Both reported holes are closed, and honest findings keep full credit.
- The fix is not tied to the report's wording. The new judge prompt quotes phrases from the reported set, so the 36 findings were reworded to avoid them, and they still score zero.
- Findings written from memory still earn credit. The judge reads a description of an exploit and cannot tell whether it was run. The maintainer tracks that separately.

## Not tested

- A real ARTEX run, ARTEX's documented judge models, and the judge's temperature-0 setting.
- The project's flag-based benchmark mode.
- The second judge model after the fix, and more than one rewording.
