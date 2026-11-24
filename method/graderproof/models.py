"""Core data types for the Graderproof audit framework."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

# Control arms and the reward the grader's own contract says each should earn.
# An exploit arm earns a reward without doing the task, so its intended reward is 0.
INTENDED_BY_ARM: dict[str, float] = {
    "noop": 0.0,
    "gold": 1.0,
    "exploit": 0.0,
    "exploit_no_tamper": 0.0,
}


@dataclass
class EpisodeResult:
    """One task/arm/repetition. `intended` is the honest reward; None means unknown."""

    task: str
    arm: str
    rep: int
    seed: int
    reward: float
    intended: float | None = None
    n_actions: int = 0
    terminated: bool = False
    truncated: bool = False
    error: str | None = None
    steps: list[dict[str, Any]] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.intended is None and self.arm in INTENDED_BY_ARM:
            self.intended = INTENDED_BY_ARM[self.arm]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> "EpisodeResult":
        known = set(cls.__dataclass_fields__)
        return cls(**{k: v for k, v in row.items() if k in known})


@dataclass(frozen=True)
class Thresholds:
    """Breach rules. Defaults are the gate's mark thresholds."""

    exploit_max: float = 0.0
    noop_max: float = 0.0
    gold_min: float = 1.0
    unearned_max: float = 0.02
    require_arms: tuple[str, ...] = ("noop", "gold", "exploit")


@dataclass
class Verdict:
    """Outcome of an audit or gate run. Exit codes: 0 pass/finding, 1 breach, 3 invalid controls."""

    phase: str
    status: str
    breaches: list[str]
    metrics: dict[str, Any]

    def ok(self) -> bool:
        return self.status in ("pass", "finding", "no_finding")

    def exit_code(self) -> int:
        if self.status == "invalid_controls":
            return 3
        if self.status == "breach":
            return 1
        return 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "status": self.status,
            "breaches": self.breaches,
            "metrics": self.metrics,
        }
