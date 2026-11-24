import json
import tempfile
import unittest
from pathlib import Path

from graderproof.adapters.jsonl import ReplayAdapter


class ReplayTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "rows.jsonl"
        rows = [
            {"task": "t1", "arm": "noop", "rep": 1, "final_reward": 0.0},
            {"task": "t1", "arm": "gold", "rep": 1, "final_reward": 1.0},
            {"task": "t1", "arm": "exploit", "rep": 1, "final_reward": 1.0},
        ]
        self.path.write_text("\n".join(json.dumps(row) for row in rows))

    def tearDown(self):
        self.tmp.cleanup()

    def test_load(self):
        loaded = ReplayAdapter(self.path).load()
        self.assertEqual(len(loaded), 3)
        self.assertEqual({result.arm for result in loaded}, {"noop", "gold", "exploit"})

    def test_run_cursor(self):
        adapter = ReplayAdapter(self.path)
        first = adapter.run("t1", "gold", 1, 0)
        self.assertEqual(first.reward, 1.0)
        second = adapter.run("t1", "gold", 2, 0)
        self.assertTrue(second.error)

    def test_missing_row(self):
        adapter = ReplayAdapter(self.path)
        result = adapter.run("t1", "exploit", 1, 0)
        self.assertEqual(result.reward, 1.0)
        missing = adapter.run("t1", "noop", 1, 0)
        self.assertEqual(missing.reward, 0.0)

    def test_meta(self):
        adapter = ReplayAdapter(self.path, grader_version="fixed")
        result = adapter.run("t1", "gold", 1, 0)
        self.assertEqual(result.meta["grader_version"], "fixed")
        self.assertEqual(result.meta["source"], str(self.path))


if __name__ == "__main__":
    unittest.main()
