"""Built-in adapters: toy (self-test) and replay (saved evidence)."""

from .jsonl import ReplayAdapter
from .toy import ToyAdapter

__all__ = ["ReplayAdapter", "ToyAdapter"]
