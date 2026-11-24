"""Markdown and JSON reports for audits and comparisons."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Verdict


def _fmt(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def render_audit(verdict: Verdict, manifest: list[dict] | None = None) -> str:
    metrics = verdict.metrics
    lines = [
        f"# Graderproof audit — {verdict.phase}",
        "",
        f"**Status:** {verdict.status}",
        "",
    ]
    if verdict.breaches:
        lines.append("**Breaches**")
        lines.extend(f"- {breach}" for breach in verdict.breaches)
        lines.append("")
    lines.extend(["| arm | n | mean reward | reach |", "|---|---:|---:|---:|"])
    for arm, stats in metrics.get("by_arm", {}).items():
        lines.append(f"| {arm} | {stats['n']} | {_fmt(stats['mean_reward'])} | {_fmt(stats['reach'])} |")
    lines.append("")
    lines.extend(["| metric | value |", "|---|---:|"])
    for key in (
        "n",
        "valid_n",
        "errors",
        "tasks",
        "coverage",
        "exploit_mean",
        "gold_mean",
        "noop_mean",
        "unearned_credit_rate",
        "unearned_n",
    ):
        if key in metrics:
            lines.append(f"| {key} | {_fmt(metrics[key])} |")
    if manifest is not None:
        lines.extend(["", f"Evidence entries: {len(manifest)}"])
    return "\n".join(lines) + "\n"


def write_audit(outdir: str | Path, verdict: Verdict, manifest: list[dict] | None = None) -> dict[str, str]:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    markdown = out / "audit.md"
    payload = out / "audit.json"
    markdown.write_text(render_audit(verdict, manifest))
    payload.write_text(
        json.dumps(
            {"verdict": verdict.to_dict(), "manifest_entries": len(manifest or [])},
            indent=2,
            sort_keys=True,
        )
    )
    return {"markdown": str(markdown), "json": str(payload)}


def render_compare(comparison: dict[str, Any]) -> str:
    lines = [
        "# Graderproof before/after",
        "",
        f"**Status:** {comparison['status']}",
        "",
    ]
    if comparison["breaches"]:
        lines.append("**Breaches**")
        lines.extend(f"- {breach}" for breach in comparison["breaches"])
        lines.append("")
    lines.extend(
        [
            "| task | exploit before | exploit after | gold before | gold after | noop before | noop after |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in comparison["tasks"]:
        lines.append(
            "| {task} | {exploit_before} | {exploit_after} | {gold_before} | {gold_after} | {noop_before} | {noop_after} |".format(
                **{key: _fmt(value) for key, value in row.items()}
            )
        )
    return "\n".join(lines) + "\n"


def write_compare(outdir: str | Path, comparison: dict[str, Any]) -> dict[str, str]:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    markdown = out / "compare.md"
    payload = out / "compare.json"
    markdown.write_text(render_compare(comparison))
    payload.write_text(json.dumps(comparison, indent=2, sort_keys=True))
    return {"markdown": str(markdown), "json": str(payload)}
