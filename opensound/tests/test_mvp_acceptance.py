from __future__ import annotations

import unittest

import numpy as np

from farhp.synth import harmonic_synthesize

from opensound.benchmark import FixtureGenerator
from opensound.contracts import EvidenceLevel, EvidenceType
from opensound.research import ResearchHarness
from opensound.runtime import SignalObservation, WorldSolveEngine


class TestOpenSoundMVPAcceptance(unittest.TestCase):
    def setUp(self) -> None:
        self.fs = 16000
        self.generator = FixtureGenerator.reference(sample_rate_hz=self.fs, duration_sec=0.08)
        self.harness = ResearchHarness.reference(self.generator)

    def test_hidden_label_mode_strips_common_metadata_hints(self) -> None:
        fixture = self.generator.generate("H", seed=303, private_label="secret-class")
        fixture.metadata.update({
            "class_label": "secret-class",
            "source_name": "secret-source",
            "filename": "secret-class.wav",
            "directory_label": "secret-folder",
            "text_description": "obvious answer hint",
        })
        run = self.harness.run_fixture(fixture, hidden_label=True)
        forbidden = {"private_label", "class_label", "source_name", "filename", "directory_label", "text_description"}
        self.assertTrue(forbidden.isdisjoint(run.runtime_observation_metadata))
        self.assertFalse(run.metadata_leak_detected)

    def test_unsupported_world_solve_emits_explicit_domain_expansion_request(self) -> None:
        fixture = self.generator.generate("U", seed=307)
        obs = SignalObservation(fixture.fixture_id, fixture.waveform, fixture.sample_rate_hz, fixture.metadata)
        result = WorldSolveEngine.reference().solve(obs)
        self.assertTrue(result.domain_expansion_requested)
        self.assertIsNotNone(result.domain_expansion_request)
        self.assertEqual(result.domain_expansion_request.observation_ref, fixture.fixture_id)
        self.assertEqual(result.domain_expansion_request.status, "open")
        self.assertIn("unsupported_component", result.domain_expansion_request.triggers)

    def test_harmonic_transient_world_solve_has_explicit_coupling_port_and_exchange(self) -> None:
        n = int(0.08 * self.fs)
        harmonic = harmonic_synthesize(
            f0_hz=140.0,
            sample_rate_hz=self.fs,
            duration_sec=0.08,
            amplitudes=[1.0, 0.45, 0.2, 0.1],
            farhp_rad=[0.0, 0.5, -0.8, 1.1],
            normalize=False,
        )
        transient = np.zeros(n, dtype=float)
        transient[700:704] = np.asarray([0.30, -0.22, 0.13, -0.07])
        result = WorldSolveEngine.reference().solve(SignalObservation("obs-coupling", harmonic + transient, self.fs))
        ports = {(port.source_module, port.target_module, port.quantity) for port in result.coupling_graph.ports}
        self.assertIn(("transient-detector", "farhp", "transient_cleaned_waveform"), ports)
        self.assertTrue(any(event["event_type"] == "port_exchange" for event in result.ledger_events))

    def test_unsupported_residual_can_be_reopened_by_new_reference_solver(self) -> None:
        initial = self.harness.run_benchmark("bench-unsupported", seed=311)
        reopened = self.harness.reopen_with_reference_solver(initial)
        self.assertEqual(reopened.observation_id, initial.world_result.observation_id)
        self.assertGreater(reopened.reopening_gain, 0.0)
        self.assertGreater(np.linalg.norm(reopened.old_residual), 0.0)
        self.assertEqual(float(np.linalg.norm(reopened.new_residual)), 0.0)
        self.assertEqual(reopened.evidence_record.evidence_type, EvidenceType.RESIDUAL_REOPENING)
        self.assertEqual(reopened.evidence_record.evidence_level, EvidenceLevel.L2)


if __name__ == "__main__":
    unittest.main()
