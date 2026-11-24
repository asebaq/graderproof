#!/usr/bin/env python3
"""Graderproof batch gate — embeddable CI check for RL-environment grader robustness.

Implements the scorecard in SCORECARD.md. Client-free; drop into a
builder's CI so every new task batch must pass before shipping.

Usage:
  gate.py score --results RUN/results.jsonl [--rescore mod:func] [--controls arms.jsonl] [--out DIR]

Metrics:
  M2 unearned_credit_rate  (needs --rescore plugin: intended reward per rollout)
  M1 exploit_reachability_after / M5 honest_regression / M6 isolation_noop (need --controls)
  descriptive: mean_reward, full_solve_rate, zero_rate, truncation_rate

Exit code 0 = pass, 1 = mark-threshold breach, 2 = usage/IO error.
"""
import argparse
import importlib
import json
import os
import sys

from graderproof.metrics import control_metrics, rollout_metrics
from graderproof.verdict import gate_breaches


def load_rows(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_rescore(spec):
    mod, func = spec.split(":")
    sys.path.insert(0, os.path.dirname(os.path.abspath(mod)) if os.path.sep in mod else os.getcwd())
    m = importlib.import_module(os.path.basename(mod).replace(".py", "") if os.path.sep in mod else mod)
    return getattr(m, func)


def score_rollouts(rows, rescore):
    return rollout_metrics(rows, rescore)


def score_controls(path):
    """arms-style jsonl with .arm in {noop,gold,exploit} and .final_reward; optional .patched."""
    return control_metrics(load_rows(path))


def evaluate(roll, ctrl, require_controls=False):
    return gate_breaches(roll, ctrl, require_controls=require_controls)


def emit(outdir, roll, ctrl, breaches):
    os.makedirs(outdir, exist_ok=True)
    card = {"rollouts": roll, "controls": ctrl, "breaches": breaches, "pass": not breaches}
    with open(os.path.join(outdir, "scorecard.json"), "w") as f:
        json.dump(card, f, indent=2)
    lines = ["# Grader gate scorecard", "", "| metric | value |", "|---|---|"]
    for k, v in roll.items():
        lines.append(f"| {k} | {v:.4f} |" if isinstance(v, float) else f"| {k} | {v} |")
    for k, v in ctrl.items():
        lines.append(f"| {k} | {v:.4f} |")
    lines += ["", "**PASS**" if not breaches else "**BREACH:** " + "; ".join(breaches)]
    with open(os.path.join(outdir, "scorecard.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    return card


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("score")
    s.add_argument("--results", required=True)
    s.add_argument("--rescore")
    s.add_argument("--controls")
    s.add_argument("--out", default="gate_out")
    a = ap.parse_args(argv)

    rows = load_rows(a.results)
    rescore = load_rescore(a.rescore) if a.rescore else None
    roll = score_rollouts(rows, rescore)
    ctrl = score_controls(a.controls) if a.controls else {}
    breaches = evaluate(roll, ctrl, require_controls=bool(a.controls))
    card = emit(a.out, roll, ctrl, breaches)
    print(json.dumps(card, indent=2))
    return 1 if breaches else 0


if __name__ == "__main__":
    sys.exit(main())
