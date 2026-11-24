# Graderproof method

Adapter-based audit framework for RL-environment graders. The package is `graderproof`; repo-level context is in `../README.md`.

## Run

From `method/`:

```bash
cd method
uv run --extra dev pytest          # 37 tests
uv run python -m graderproof --help  # CLI: run, compare, verify
uv run python scripts/gate.py --help  # batch gate: score
```

From the repo root:

```bash
uv run --project method --extra dev pytest method/tests
uv run --project method python -m graderproof --help
```

## Layout

| Path | Holds |
|---|---|
| `graderproof/` | package: adapter protocol, audit runner, evidence store, metrics, verdicts, CLI |
| `graderproof/adapters/` | `toy` (self-contained) and `jsonl` (replay) adapters |
| `tests/` | unit tests; no model or environment required |
| `scripts/gate.py` | standalone CI gate; computes the scorecard and exits 1 on breach |

## Notes

- The core framework uses only the standard library. `pytest` is the only dev dependency.
- `scripts/gate.py` imports the package; run it via `uv run` or after installing. The package itself is installable with `uv pip install -e method` or `pip install -e method`.

## License

`graderproof`, `scripts/gate.py`, and `tests/` are MIT (see `LICENSE`). Audit reports, findings, scorecard operation, and the "Graderproof Audited" mark remain proprietary.
