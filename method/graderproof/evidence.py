"""Content-addressed evidence store: every episode is hashed and logged."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import EpisodeResult


def canonical(payload: dict[str, Any]) -> str:
    """Deterministic JSON: sorted keys, no whitespace, ASCII escapes."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


class EvidenceStore:
    """Episodes are files named by SHA-256; the manifest records each run."""

    def __init__(self, root: str | Path, create: bool = True):
        self.root = Path(root)
        self.episodes = self.root / "episodes"
        self.manifest_path = self.root / "manifest.jsonl"
        if create:
            self.episodes.mkdir(parents=True, exist_ok=True)
            self.manifest_path.touch(exist_ok=True)
        self._seen: set[str] = set()
        if self.manifest_path.exists():
            self._seen = {entry["sha256"] for entry in self.read_manifest()}

    def record(self, result: EpisodeResult, run_id: str | None = None) -> str:
        text = canonical(result.to_dict())
        digest = hashlib.sha256(text.encode()).hexdigest()
        path = self.episodes / f"{digest}.json"
        if not path.exists():
            path.write_text(text)
        if digest not in self._seen:
            entry = {
                "sha256": digest,
                "task": result.task,
                "arm": result.arm,
                "rep": result.rep,
                "seed": result.seed,
                "reward": result.reward,
                "error": result.error,
                "run_id": run_id,
                "recorded_at": datetime.now(timezone.utc).isoformat(),
            }
            with self.manifest_path.open("a") as handle:
                handle.write(json.dumps(entry, sort_keys=True) + "\n")
            self._seen.add(digest)
        return digest

    def read_manifest(self) -> list[dict[str, Any]]:
        if not self.manifest_path.exists():
            return []
        return [json.loads(line) for line in self.manifest_path.read_text().splitlines() if line.strip()]

    def verify(self) -> list[str]:
        """Re-hash every manifest entry. Returns human-readable issues."""
        if not self.manifest_path.exists():
            return [f"missing manifest: {self.manifest_path}"]
        issues: list[str] = []
        for entry in self.read_manifest():
            digest = entry.get("sha256", "")
            path = self.episodes / f"{digest}.json"
            if not path.exists():
                issues.append(f"missing episode file: {digest}")
                continue
            try:
                payload = json.loads(path.read_text())
            except json.JSONDecodeError as exc:
                issues.append(f"unreadable episode {digest}: {exc}")
                continue
            actual = hashlib.sha256(canonical(payload).encode()).hexdigest()
            if actual != digest:
                issues.append(f"hash mismatch: {digest} != {actual}")
        return issues
