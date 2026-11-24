"""Audit orchestrator: tasks x arms x repetitions, with evidence and verdicts."""

from __future__ import annotations

from typing import Iterable, Sequence

from .adapter import Adapter
from .evidence import EvidenceStore
from .metrics import audit_metrics
from .models import EpisodeResult, Thresholds, Verdict
from .verdict import audit_verdict


class AuditRunner:
    def __init__(
        self,
        adapter: Adapter,
        *,
        store: EvidenceStore | None = None,
        run_id: str | None = None,
    ):
        self.adapter = adapter
        self.store = store
        self.run_id = run_id

    def run(
        self,
        tasks: Sequence[str] | None = None,
        arms: Iterable[str] = ("noop", "gold", "exploit"),
        reps: int = 2,
    ) -> list[EpisodeResult]:
        """Run every task/arm/repetition. Adapter exceptions become error episodes."""
        if reps < 1:
            raise ValueError("reps must be >= 1")
        arms = tuple(arms)
        tasks = tuple(tasks) if tasks is not None else tuple(self.adapter.tasks())
        results: list[EpisodeResult] = []
        for task_index, task in enumerate(tasks):
            for arm_index, arm in enumerate(arms):
                for rep in range(reps):
                    seed = task_index * 10_000 + arm_index * 100 + rep
                    try:
                        episode = self.adapter.run(task, arm, rep, seed)
                    except Exception as exc:  # adapter failure is evidence, not a crash
                        episode = EpisodeResult(
                            task=task,
                            arm=arm,
                            rep=rep,
                            seed=seed,
                            reward=0.0,
                            error=f"{type(exc).__name__}: {exc}",
                        )
                    if self.store is not None:
                        self.store.record(episode, run_id=self.run_id)
                    results.append(episode)
        return results

    def audit(
        self,
        tasks: Sequence[str] | None = None,
        arms: Iterable[str] = ("noop", "gold", "exploit"),
        reps: int = 2,
        phase: str = "baseline",
        thresholds: Thresholds = Thresholds(),
    ) -> tuple[Verdict, list[EpisodeResult]]:
        arms = tuple(arms)
        results = self.run(tasks=tasks, arms=arms, reps=reps)
        metrics = audit_metrics(results, required_arms=arms)
        return audit_verdict(metrics, phase, thresholds), results
