import unittest

from graderproof.adapters.toy import ToyAdapter
from graderproof.audit import AuditRunner


class AuditToyTest(unittest.TestCase):
    def test_broken_baseline_finds_exploit(self):
        verdict, results = AuditRunner(ToyAdapter("broken")).audit(phase="baseline", reps=2)
        self.assertEqual(verdict.status, "finding")
        self.assertEqual(len(results), 18)
        self.assertEqual(verdict.metrics["exploit_mean"], 1.0)
        self.assertEqual(verdict.metrics["gold_mean"], 1.0)
        self.assertEqual(verdict.metrics["noop_mean"], 0.0)
        self.assertAlmostEqual(verdict.metrics["unearned_credit_rate"], 0.5)

    def test_fixed_baseline_no_finding(self):
        verdict, _ = AuditRunner(ToyAdapter("fixed")).audit(phase="baseline", reps=1)
        self.assertEqual(verdict.status, "no_finding")

    def test_fixed_gate_passes(self):
        verdict, _ = AuditRunner(ToyAdapter("fixed")).audit(phase="fixed", reps=1)
        self.assertEqual(verdict.status, "pass")

    def test_broken_gate_breaches(self):
        verdict, _ = AuditRunner(ToyAdapter("broken")).audit(phase="fixed", reps=1)
        self.assertEqual(verdict.status, "breach")
        self.assertEqual(verdict.exit_code(), 1)

    def test_adapter_error_is_evidence(self):
        class Boom(ToyAdapter):
            def run(self, *args, **kwargs):
                raise RuntimeError("boom")

        verdict, results = AuditRunner(Boom("broken")).audit(phase="baseline", reps=1)
        self.assertEqual(verdict.status, "invalid_controls")
        self.assertEqual(len(results), 9)
        self.assertTrue(all(result.error for result in results))

    def test_evidence_roundtrip(self):
        import tempfile

        from graderproof.evidence import EvidenceStore

        with tempfile.TemporaryDirectory() as tmp:
            store = EvidenceStore(tmp)
            verdict, results = AuditRunner(ToyAdapter("broken"), store=store).audit(
                phase="baseline", reps=1
            )
            self.assertEqual(verdict.status, "finding")
            self.assertEqual(len(store.read_manifest()), len(results))
            self.assertEqual(store.verify(), [])


if __name__ == "__main__":
    unittest.main()
