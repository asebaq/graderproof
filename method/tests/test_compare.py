import unittest

from graderproof.compare import compare
from graderproof.models import EpisodeResult


def episodes(exploit, gold=1.0, noop=0.0, task="t1"):
    return [
        EpisodeResult(task, "noop", 1, 0, noop),
        EpisodeResult(task, "gold", 1, 0, gold),
        EpisodeResult(task, "exploit", 1, 0, exploit),
    ]


class CompareTest(unittest.TestCase):
    def test_fixed(self):
        result = compare(episodes(1.0), episodes(0.0))
        self.assertEqual(result["status"], "fixed")
        self.assertEqual(result["breaches"], [])

    def test_not_fixed(self):
        result = compare(episodes(1.0), episodes(1.0))
        self.assertEqual(result["status"], "not_fixed")

    def test_regression(self):
        result = compare(episodes(1.0), episodes(0.0, gold=0.5))
        self.assertEqual(result["status"], "regression")

    def test_not_reproduced(self):
        result = compare(episodes(0.0), episodes(0.0))
        self.assertEqual(result["status"], "not_reproduced")

    def test_missing_after_exploit(self):
        after = [
            EpisodeResult("t1", "noop", 1, 0, 0.0),
            EpisodeResult("t1", "gold", 1, 0, 1.0),
        ]
        result = compare(episodes(1.0), after)
        self.assertEqual(result["status"], "not_fixed")
        self.assertTrue(any("no after exploit" in breach for breach in result["breaches"]))


if __name__ == "__main__":
    unittest.main()
