from __future__ import annotations

import unittest

import numpy as np

from opensound.benchmark import BenchmarkRegistry, FixtureGenerator, MetricRegistry
from opensound.research import ClaimRegistry, EvidenceLedger, ResearchCI, ResearchHarness


class TestOpenSoundP2ResearchHarness(unittest.TestCase):
    def setUp(self) -> None:
        self.generator = FixtureGenerator.reference(sample_rate_hz=16000, duration_sec=0.08)
        self.harness = ResearchHarness.reference(self.generator)

    def test_seed_benchmark_registry_has_required_reference_matrix(self) -> None:
        ids = BenchmarkRegistry.seed().ids()
        for benchmark_id in {
            "bench-h",
            "bench-hn",
            "bench-ht",
            "bench-hnt",
            "bench-noise",
            "bench-transient",
            "bench-unsupported",
            "bench-artifact",
        }:
            self.assertIn(benchmark_id, ids)

    def test_fixture_generation_is_replayable_from_family_and_seed(self) -> None:
        first = self.generator.generate("H+N+T", seed=71)
        second = self.generator.generate("H+N+T", seed=71)
        self.assertEqual(first.fixture_id, second.fixture_id)
        self.assertEqual(first.ground_truth, second.ground_truth)
        np.testing.assert_allclose(first.waveform, second.waveform, atol=0.0)

    def test_metric_registry_defines_required_reference_metrics(self) -> None:
        ids = MetricRegistry.seed().ids()
        for metric_id in {
            "waveform_nrmse",
            "f0_error_hz",
            "farhp_circular_error_rad",
            "false_certainty_rate",
            "false_activation_rate",
            "residual_structure",
            "reopening_gain",
        }:
            self.assertIn(metric_id, ids)

    def test_hidden_label_run_does_not_pass_private_label_to_runtime(self) -> None:
        fixture = self.generator.generate("H", seed=5, private_label="known-harmonic-A")
        run = self.harness.run_fixture(fixture, hidden_label=True)
        self.assertEqual(fixture.ground_truth["private_label"], "known-harmonic-A")
        self.assertNotIn("private_label", run.runtime_observation_metadata)
        self.assertFalse(run.metadata_leak_detected)

    def test_every_completed_synthetic_run_emits_l2_or_lower_evidence(self) -> None:
        run = self.harness.run_benchmark("bench-hnt", seed=11)
        self.assertEqual(run.status, "completed")
        self.assertGreaterEqual(len(run.evidence_records), 1)
        self.assertTrue(all(int(record.evidence_level.value[1:]) <= 2 for record in run.evidence_records))

    def test_unsupported_benchmark_counts_correct_abstention_as_success(self) -> None:
        run = self.harness.run_benchmark("bench-unsupported", seed=13)
        self.assertEqual(run.world_result.status, "abstained")
        self.assertTrue(run.world_result.domain_expansion_requested)
        self.assertTrue(run.passed)
        self.assertEqual(run.metrics["false_certainty_rate"], 0.0)

    def test_artifact_benchmark_never_claims_farhp_as_high_confidence_truth(self) -> None:
        run = self.harness.run_benchmark("bench-artifact", seed=17)
        self.assertIn(run.world_result.routing.method_states["farhp"], {"not_applicable", "abstain", "weakly_applicable"})
        self.assertEqual(run.metrics["false_certainty_rate"], 0.0)

    def test_evidence_and_claim_registries_preserve_counter_evidence(self) -> None:
        ledger = EvidenceLedger()
        claims = ClaimRegistry()
        claim = claims.register("claim-reference-hnt", required_level="L2")
        support = ledger.record_synthetic("ev-support", direction="support")
        counter = ledger.record_synthetic("ev-counter", direction="counter")
        claims.attach_evidence(claim.claim_id, support)
        claims.attach_evidence(claim.claim_id, counter)
        stored = claims.get(claim.claim_id)
        self.assertIn("ev-support", stored.evidence_refs)
        self.assertIn("ev-counter", stored.counter_evidence_refs)
        self.assertEqual(stored.status, "disputed")

    def test_replay_bundle_reruns_to_identical_metrics_and_status(self) -> None:
        run = self.harness.run_benchmark("bench-h", seed=23)
        bundle = self.harness.export_replay_bundle(run)
        replayed = self.harness.replay(bundle)
        self.assertEqual(run.world_result.status, replayed.world_result.status)
        self.assertEqual(run.metrics, replayed.metrics)
        self.assertEqual(run.benchmark_id, replayed.benchmark_id)

    def test_reference_research_ci_matrix_passes(self) -> None:
        report = ResearchCI(self.harness).run_reference_matrix(seed=101)
        self.assertTrue(report.all_pass)
        self.assertEqual(set(report.results), BenchmarkRegistry.seed().ids())


if __name__ == "__main__":
    unittest.main()
