import tempfile
import unittest
from pathlib import Path

from graderproof.evidence import EvidenceStore, canonical
from graderproof.models import EpisodeResult


class EvidenceTest(unittest.TestCase):
    def test_canonical(self):
        self.assertEqual(canonical({"b": 1, "a": 2}), '{"a":2,"b":1}')

    def test_record_dedupe_verify(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = EvidenceStore(tmp)
            episode = EpisodeResult("t1", "gold", 1, 0, 1.0)
            first = store.record(episode)
            second = store.record(episode)
            self.assertEqual(first, second)
            self.assertEqual(len(store.read_manifest()), 1)
            self.assertEqual(store.verify(), [])

            store.record(EpisodeResult("t1", "noop", 1, 0, 0.0))
            self.assertEqual(len(store.read_manifest()), 2)
            self.assertEqual(store.verify(), [])

    def test_tamper_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = EvidenceStore(tmp)
            digest = store.record(EpisodeResult("t1", "exploit", 1, 0, 1.0))
            path = Path(tmp) / "episodes" / f"{digest}.json"
            path.write_text(path.read_text().replace("1.0", "0.0"))
            issues = store.verify()
            self.assertTrue(issues)
            self.assertIn("hash mismatch", issues[0])

    def test_missing_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            issues = EvidenceStore(tmp, create=False).verify()
            self.assertTrue(issues)
            self.assertIn("missing manifest", issues[0])


if __name__ == "__main__":
    unittest.main()
