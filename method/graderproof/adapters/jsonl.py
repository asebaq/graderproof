"""Replay adapter over saved arms-style JSONL. No environment or model needed."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from ..models import EpisodeResult


def _as_int(value: Any, default: int) -> int:
    try:
        return default if value is None else int(value)
    except (TypeError, ValueError):
        return default


class ReplayAdapter:
    """Replays recorded episodes. Useful for re-scoring real evidence offline."""

    name = "replay"

    def __init__(self, path: str | Path, grader_version: str = "recorded"):
        self.path = Path(path)
        self.grader_version = grader_version
        self._rows = [
            json.loads(line) for line in self.path.read_text().splitlines() if line.strip()
        ]
        self._by_key: dict[tuple[str, str], list[dict]] = defaultdict(list)
        for row in self._rows:
            self._by_key[(str(row.get("task", "")), str(row.get("arm", "")))].append(row)
        self._cursor: dict[tuple[str, str], int] = defaultdict(int)

    def tasks(self) -> list[str]:
        return sorted({str(row.get("task", "")) for row in self._rows})

    def load(self) -> list[EpisodeResult]:
        return [self._to_result(row, index) for index, row in enumerate(self._rows)]

    def run(self, task: str, arm: str, rep: int, seed: int) -> EpisodeResult:
        key = (task, arm)
        rows = self._by_key.get(key, [])
        index = self._cursor[key]
        if index >= len(rows):
            return EpisodeResult(
                task=task,
                arm=arm,
                rep=rep,
                seed=seed,
                reward=0.0,
                error=f"missing recorded row for {task}/{arm}",
            )
        self._cursor[key] += 1
        return self._to_result(rows[index], rep, seed)

    def _to_result(self, row: dict, default_rep: int = 0, default_seed: int = 0) -> EpisodeResult:
        known = {
            "task",
            "arm",
            "rep",
            "seed",
            "reward",
            "final_reward",
            "intended",
            "n_actions",
            "terminated",
            "truncated",
            "steps",
            "error",
        }
        meta = {key: value for key, value in row.items() if key not in known}
        meta.setdefault("grader_version", self.grader_version)
        meta.setdefault("source", str(self.path))
        reward = row.get("final_reward", row.get("reward", 0.0))
        return EpisodeResult(
            task=str(row.get("task", "")),
            arm=str(row.get("arm", "")),
            rep=_as_int(row.get("rep"), default_rep),
            seed=_as_int(row.get("seed"), default_seed),
            reward=float(reward) if reward is not None else 0.0,
            intended=row.get("intended"),
            n_actions=_as_int(row.get("n_actions"), 0),
            terminated=bool(row.get("terminated", False)),
            truncated=bool(row.get("truncated", False)),
            steps=row.get("steps") or [],
            error=row.get("error"),
            meta=meta,
        )
