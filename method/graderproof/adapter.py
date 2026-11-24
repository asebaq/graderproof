"""The only integration point for a new environment."""

from __future__ import annotations

from typing import Protocol, Sequence

from .models import EpisodeResult


class Adapter(Protocol):
    """Runs one task/arm and returns the episode.

    Implementations own the environment, the policy, and the grader. The framework
    owns replication, evidence, metrics, and verdicts. An adapter may be a real
    environment, a replay of saved episodes, or a toy.
    """

    name: str

    def tasks(self) -> Sequence[str]:
        ...

    def run(self, task: str, arm: str, rep: int, seed: int) -> EpisodeResult:
        ...
