"""Command line: python -m graderproof.cli run|compare|verify."""

from __future__ import annotations

import argparse
import json
import sys

from .adapters.jsonl import ReplayAdapter
from .adapters.toy import ToyAdapter
from .audit import AuditRunner
from .compare import compare
from .evidence import EvidenceStore
from .report import write_audit, write_compare


def _adapter(args):
    if args.toy:
        return ToyAdapter(args.toy)
    if args.replay:
        return ReplayAdapter(args.replay, grader_version=args.phase)
    raise SystemExit("choose --toy broken|fixed or --replay PATH")


def cmd_run(args) -> int:
    adapter = _adapter(args)
    store = EvidenceStore(args.evidence) if args.evidence else None
    runner = AuditRunner(adapter, store=store, run_id=args.run_id)
    verdict, _ = runner.audit(
        tasks=args.tasks,
        arms=tuple(args.arms),
        reps=args.reps,
        phase=args.phase,
    )
    paths = write_audit(args.out, verdict, store.read_manifest() if store else None)
    print(
        json.dumps(
            {
                "status": verdict.status,
                "phase": verdict.phase,
                "breaches": verdict.breaches,
                "metrics": verdict.metrics,
                "report": paths,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return verdict.exit_code()


def cmd_compare(args) -> int:
    before = ReplayAdapter(args.before).load()
    after = ReplayAdapter(args.after).load()
    comparison = compare(before, after)
    paths = write_compare(args.out, comparison)
    print(
        json.dumps(
            {
                "status": comparison["status"],
                "breaches": comparison["breaches"],
                "report": paths,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if comparison["status"] == "fixed" else 1


def cmd_verify(args) -> int:
    issues = EvidenceStore(args.evidence, create=False).verify()
    print(json.dumps({"issues": issues}, indent=2))
    return 0 if not issues else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="graderproof")
    sub = parser.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="run an audit against an adapter")
    run.add_argument("--toy", choices=("broken", "fixed"))
    run.add_argument("--replay", help="JSONL of saved arms results")
    run.add_argument("--phase", choices=("baseline", "fixed"), default="baseline")
    run.add_argument("--reps", type=int, default=2)
    run.add_argument("--arms", nargs="+", default=["noop", "gold", "exploit"])
    run.add_argument("--tasks", nargs="*")
    run.add_argument("--evidence", help="directory for the evidence store")
    run.add_argument("--run-id")
    run.add_argument("--out", default="audit_out")
    run.set_defaults(func=cmd_run)

    cmp_parser = sub.add_parser("compare", help="compare before and after evidence")
    cmp_parser.add_argument("--before", required=True)
    cmp_parser.add_argument("--after", required=True)
    cmp_parser.add_argument("--out", default="compare_out")
    cmp_parser.set_defaults(func=cmd_compare)

    verify = sub.add_parser("verify", help="verify an evidence store")
    verify.add_argument("--evidence", required=True)
    verify.set_defaults(func=cmd_verify)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
