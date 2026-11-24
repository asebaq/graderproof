import unittest

from graderproof.verdict import audit_verdict, gate_breaches


def base_metrics(**overrides):
    metrics = {
        "n": 1,
        "valid_n": 1,
        "errors": 0,
        "missing_arms": [],
        "coverage": 1.0,
        "gold_mean": 1.0,
        "noop_mean": 0.0,
        "exploit_mean": 0.0,
        "unearned_credit_rate": 0.0,
    }
    metrics.update(overrides)
    return metrics


class VerdictTest(unittest.TestCase):
    def test_baseline_finding(self):
        verdict = audit_verdict(base_metrics(exploit_mean=1.0), "baseline")
        self.assertEqual(verdict.status, "finding")
        self.assertTrue(verdict.ok())
        self.assertEqual(verdict.exit_code(), 0)

    def test_baseline_no_finding(self):
        verdict = audit_verdict(base_metrics(), "baseline")
        self.assertEqual(verdict.status, "no_finding")
        self.assertEqual(verdict.exit_code(), 0)

    def test_fixed_pass(self):
        verdict = audit_verdict(base_metrics(), "fixed")
        self.assertEqual(verdict.status, "pass")
        self.assertEqual(verdict.exit_code(), 0)

    def test_fixed_breach(self):
        verdict = audit_verdict(base_metrics(exploit_mean=1.0), "fixed")
        self.assertEqual(verdict.status, "breach")
        self.assertEqual(verdict.exit_code(), 1)

    def test_fixed_unearned_breach(self):
        verdict = audit_verdict(base_metrics(unearned_credit_rate=0.1), "fixed")
        self.assertEqual(verdict.status, "breach")

    def test_invalid_controls(self):
        for overrides in (
            {"gold_mean": 0.5},
            {"noop_mean": 0.5},
            {"missing_arms": ["t1:exploit"]},
            {"errors": 1},
            {"n": 0},
        ):
            verdict = audit_verdict(base_metrics(**overrides), "baseline")
            self.assertEqual(verdict.status, "invalid_controls", overrides)
            self.assertEqual(verdict.exit_code(), 3)

    def test_unknown_phase(self):
        with self.assertRaises(ValueError):
            audit_verdict(base_metrics(), "nope")

    def test_gate_breaches(self):
        breaches = gate_breaches(
            {"unearned_credit_rate": 0.1},
            {"M1_exploit_after": 1.0, "M5_gold_rate": 0.5, "M6_noop_rate": 0.1},
        )
        self.assertEqual(len(breaches), 4)

    def test_gate_requires_controls(self):
        breaches = gate_breaches({}, {}, require_controls=True)
        self.assertEqual(len(breaches), 1)
        self.assertIn("no control arms", breaches[0])


if __name__ == "__main__":
    unittest.main()
