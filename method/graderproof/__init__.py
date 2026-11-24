"""Graderproof: an audit framework for RL-environment graders.

The framework is adapter-based: an Adapter runs a task/arm and returns an
EpisodeResult. The framework adds replication, content-addressed evidence,
metrics, verdicts, and before/after comparison. No model or environment is
required to test the framework itself; see adapters/toy.py.
"""

from .models import EpisodeResult, Thresholds, Verdict
from .audit import AuditRunner
from .evidence import EvidenceStore
from .compare import compare

__all__ = [
    "EpisodeResult",
    "Thresholds",
    "Verdict",
    "AuditRunner",
    "EvidenceStore",
    "compare",
]
