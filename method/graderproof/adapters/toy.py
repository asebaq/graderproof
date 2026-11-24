"""In-memory toy environment: broken grader vs fixed grader, no Docker or model."""

from __future__ import annotations

from ..models import EpisodeResult


class ToyAdapter:
    """A deterministic stand-in for a real environment.

    broken: the exploit scores 1.0 without doing the task.
    fixed: the exploit scores 0.0; the reference solution still scores 1.0.
    """

    name = "toy"

    def __init__(self, mode: str = "broken", tasks: tuple[str, ...] = ("toy-1", "toy-2", "toy-3")):
        if mode not in ("broken", "fixed"):
            raise ValueError("mode must be 'broken' or 'fixed'")
        self.mode = mode
        self._tasks = tasks

    def tasks(self) -> tuple[str, ...]:
        return self._tasks

    def run(self, task: str, arm: str, rep: int, seed: int) -> EpisodeResult:
        if arm == "noop":
            reward = 0.0
        elif arm == "gold":
            reward = 1.0
        elif arm == "exploit":
            reward = 1.0 if self.mode == "broken" else 0.0
        elif arm == "exploit_no_tamper":
            reward = 0.0
        else:
            raise ValueError(f"unknown arm: {arm}")
        return EpisodeResult(
            task=task,
            arm=arm,
            rep=rep,
            seed=seed,
            reward=reward,
            meta={"mode": self.mode, "adapter": self.name},
        )
