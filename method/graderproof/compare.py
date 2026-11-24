"""Before/after comparison: did the fix kill the exploit without honest regression?"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .models import EpisodeResult, Thresholds


def _means(results: list[EpisodeResult]) -> dict[tuple[str, str], float]:
    buckets: dict[tuple[str, str], list[float]] = defaultdict(list)
    for result in results:
        if not result.error:
            buckets[(result.task, result.arm)].append(result.reward)
    return {key: sum(values) / len(values) for key, values in buckets.items()}


def compare(
    before: list[EpisodeResult],
    after: list[EpisodeResult],
    thresholds: Thresholds = Thresholds(),
) -> dict[str, Any]:
    """Status: fixed | regression | not_fixed | not_reproduced."""
    old = _means(before)
    new = _means(after)
    tasks = sorted({task for task, _ in old} | {task for task, _ in new})
    rows: list[dict[str, Any]] = []
    breaches: list[str] = []

    for task in tasks:
        row = {
            "task": task,
            "exploit_before": old.get((task, "exploit")),
            "exploit_after": new.get((task, "exploit")),
            "gold_before": old.get((task, "gold")),
            "gold_after": new.get((task, "gold")),
            "noop_before": old.get((task, "noop")),
            "noop_after": new.get((task, "noop")),
        }
        rows.append(row)

        if row["exploit_before"] is None or row["exploit_before"] <= thresholds.exploit_max:
            breaches.append(f"{task}: before exploit not > 0")
        if row["gold_before"] is None or row["gold_before"] < thresholds.gold_min:
            breaches.append(f"{task}: before gold < 1")
        if row["noop_before"] is not None and row["noop_before"] > thresholds.noop_max:
            breaches.append(f"{task}: before noop > 0")

        if row["exploit_after"] is None:
            breaches.append(f"{task}: no after exploit")
        elif row["exploit_after"] > thresholds.exploit_max:
            breaches.append(f"{task}: exploit after {row['exploit_after']:.3f} > 0")
        if row["gold_after"] is None:
            breaches.append(f"{task}: no after gold")
        elif row["gold_after"] < thresholds.gold_min:
            breaches.append(f"{task}: gold after {row['gold_after']:.3f} < 1")
        if row["noop_after"] is not None and row["noop_after"] > thresholds.noop_max:
            breaches.append(f"{task}: noop after {row['noop_after']:.3f} > 0")

    if any("gold after" in b or "noop after" in b for b in breaches):
        status = "regression"
    elif any("exploit after" in b or "no after exploit" in b for b in breaches):
        status = "not_fixed"
    elif breaches:
        status = "not_reproduced"
    else:
        status = "fixed"

    return {
        "status": status,
        "breaches": breaches,
        "tasks": rows,
        "n_before": len(before),
        "n_after": len(after),
    }
