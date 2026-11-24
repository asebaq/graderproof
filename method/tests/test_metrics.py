import unittest

from graderproof.metrics import audit_metrics, control_metrics, mean, rollout_metrics, unearned_credit_rate
from graderproof.models import EpisodeResult


class MetricsTest(unittest.TestCase):
    def test_mean(self):
        self.assertEqual(mean([1.0, 2.0, 3.0]), 2.0)
        self.assertEqual(mean([]), 0.0)

    def test_unearned(self):
        self.assertAlmostEqual(unearned_credit_rate([1.0, 0.0], [0.0, 0.0]), 1.0)
        self.assertAlmostEqual(unearned_credit_rate([1.0, 1.0], [1.0, 0.0]), 0.5)
        self.assertEqual(unearned_credit_rate([0.0], [0.0]), 0.0)

    def test_rollout_metrics(self):
        rows = [{"reward": 1.0}, {"reward": 0.0}, {"reward": 0.5, "is_truncated": True}]
        metrics = rollout_metrics(rows)
        self.assertEqual(metrics["n"], 3)
        self.assertAlmostEqual(metrics["mean_reward"], 0.5)
        self.assertAlmostEqual(metrics["full_solve_rate"], 1 / 3)
        self.assertAlmostEqual(metrics["zero_rate"], 1 / 3)
        self.assertAlmostEqual(metrics["truncation_rate"], 1 / 3)
        self.assertNotIn("unearned_credit_rate", metrics)

    def test_rollout_rescore(self):
        rows = [{"reward": 1.0}, {"reward": 0.0}]
        metrics = rollout_metrics(rows, lambda row: 0.0)
        self.assertAlmostEqual(metrics["unearned_credit_rate"], 1.0)
        self.assertAlmostEqual(metrics["rollouts_with_unearned"], 0.5)

    def test_control_metrics_prefers_patched(self):
        rows = [
            {"arm": "exploit", "final_reward": 0.0, "patched": True},
            {"arm": "exploit", "final_reward": 1.0, "patched": False},
            {"arm": "gold", "final_reward": 1.0},
            {"arm": "noop", "final_reward": 0.0},
        ]
        metrics = control_metrics(rows)
        self.assertEqual(metrics["M1_exploit_after"], 0.0)
        self.assertEqual(metrics["M5_gold_rate"], 1.0)
        self.assertEqual(metrics["M6_noop_rate"], 0.0)

    def test_control_metrics_without_patched(self):
        rows = [
            {"arm": "exploit", "final_reward": 1.0},
            {"arm": "gold", "final_reward": 1.0},
        ]
        metrics = control_metrics(rows)
        self.assertEqual(metrics["M1_exploit_after"], 1.0)

    def test_audit_metrics(self):
        results = [
            EpisodeResult("t1", "noop", 1, 0, 0.0),
            EpisodeResult("t1", "gold", 1, 0, 1.0),
            EpisodeResult("t1", "exploit", 1, 0, 1.0),
            EpisodeResult("t2", "noop", 1, 0, 0.0),
            EpisodeResult("t2", "gold", 1, 0, 1.0),
            EpisodeResult("t2", "exploit", 1, 0, 0.0),
        ]
        metrics = audit_metrics(results)
        self.assertEqual(metrics["n"], 6)
        self.assertEqual(metrics["tasks"], 2)
        self.assertEqual(metrics["coverage"], 1.0)
        self.assertEqual(metrics["missing_arms"], [])
        self.assertAlmostEqual(metrics["exploit_mean"], 0.5)
        self.assertAlmostEqual(metrics["exploit_reach"], 0.5)
        self.assertAlmostEqual(metrics["gold_mean"], 1.0)
        self.assertAlmostEqual(metrics["noop_mean"], 0.0)
        self.assertAlmostEqual(metrics["unearned_credit_rate"], 1 / 3)
        self.assertEqual(metrics["unearned_n"], 6)

    def test_audit_missing_arm(self):
        results = [
            EpisodeResult("t1", "noop", 1, 0, 0.0),
            EpisodeResult("t1", "gold", 1, 0, 1.0),
            EpisodeResult("t1", "exploit", 1, 0, 1.0),
            EpisodeResult("t2", "noop", 1, 0, 0.0),
            EpisodeResult("t2", "gold", 1, 0, 1.0),
        ]
        metrics = audit_metrics(results)
        self.assertEqual(metrics["missing_arms"], ["t2:exploit"])
        self.assertEqual(metrics["coverage"], 0.5)

    def test_audit_errors(self):
        results = [
            EpisodeResult("t1", "noop", 1, 0, 0.0),
            EpisodeResult("t1", "gold", 1, 0, 0.0, error="boom"),
        ]
        metrics = audit_metrics(results)
        self.assertEqual(metrics["valid_n"], 1)
        self.assertEqual(metrics["errors"], 1)


if __name__ == "__main__":
    unittest.main()
