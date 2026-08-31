from __future__ import annotations

import unittest

import numpy as np

from farhp.synth import harmonic_synthesize, synthetic_vowel

from opensound.geometry import circular_interpolate
from opensound.registry import MethodRegistry, RegionRegistry
from opensound.runtime import SignalObservation, WorldSolveEngine


class TestOpenSoundP1Runtime(unittest.TestCase):
    def setUp(self) -> None:
        self.fs = 16000
        self.n = int(0.08 * self.fs)
        self.t = np.arange(self.n, dtype=float) / self.fs
        self.engine = WorldSolveEngine.reference()

    def observation(self, waveform: np.ndarray, **metadata) -> SignalObservation:
        return SignalObservation(
            observation_id=f"obs-{metadata.pop('name', 'test')}",
            waveform=np.asarray(waveform, dtype=float),
            sample_rate_hz=self.fs,
            metadata=metadata,
        )

    def test_seed_registries_cover_reference_regions_and_methods(self) -> None:
        regions = RegionRegistry.seed().ids()
        methods = MethodRegistry.seed().ids()
        self.assertIn("human-auditory", regions)
        self.assertIn("unknown-mechanical", regions)
        self.assertIn("farhp", methods)
        self.assertIn("noise-estimator", methods)
        self.assertIn("transient-detector", methods)
        self.assertIn("residual-structure-analyzer", methods)

    def test_circular_interpolation_crosses_pi_boundary(self) -> None:
        a = np.deg2rad(170.0)
        b = np.deg2rad(-170.0)
        midpoint = circular_interpolate(a, b, 0.5)
        self.assertLess(abs(abs(midpoint) - np.pi), 1e-10)

    def test_pure_harmonic_routes_to_farhp_and_commits(self) -> None:
        x, _, _ = synthetic_vowel(duration_sec=0.08, sample_rate_hz=self.fs, k_max=12)
        result = self.engine.solve(self.observation(x, name="harmonic"))
        self.assertEqual(result.status, "committed")
        self.assertIn("farhp", result.routing.selected_methods)
        self.assertIn("harmonic", result.components)
        self.assertIsNotNone(result.farhp_frame)
        self.assertLess(result.residual_energy_ratio, 0.55)

    def test_noise_only_marks_farhp_not_applicable(self) -> None:
        rng = np.random.default_rng(11)
        x = 0.2 * rng.standard_normal(self.n)
        result = self.engine.solve(self.observation(x, name="noise"))
        self.assertEqual(result.routing.method_states["farhp"], "not_applicable")
        self.assertNotIn("farhp", result.routing.selected_methods)
        self.assertIn("noise", result.components)
        self.assertIsNone(result.farhp_frame)

    def test_transient_only_does_not_force_farhp(self) -> None:
        x = np.zeros(self.n)
        x[self.n // 2] = 1.0
        x[self.n // 2 + 1] = -0.65
        result = self.engine.solve(self.observation(x, name="transient"))
        self.assertIn(result.routing.method_states["farhp"], {"not_applicable", "abstain"})
        self.assertIn("transient", result.components)
        self.assertIsNone(result.farhp_frame)

    def test_layered_harmonic_noise_transient_reconstruction_is_model_only(self) -> None:
        harmonic = harmonic_synthesize(
            f0_hz=140.0,
            sample_rate_hz=self.fs,
            duration_sec=0.08,
            amplitudes=[1.0, 0.45, 0.2, 0.1],
            farhp_rad=[0.0, 0.5, -0.8, 1.1],
            normalize=False,
        )
        rng = np.random.default_rng(7)
        noise = 0.025 * rng.standard_normal(self.n)
        transient = np.zeros(self.n)
        transient[700:704] = np.array([0.25, -0.2, 0.1, -0.05])
        x = harmonic + noise + transient
        result = self.engine.solve(self.observation(x, name="hnt"))
        self.assertIn("harmonic", result.components)
        self.assertIn("noise", result.components)
        self.assertIn("transient", result.components)
        self.assertFalse(result.model_reconstruction_uses_preserved_residual)
        np.testing.assert_allclose(result.witness_reconstruction, x, atol=1e-12)
        self.assertGreaterEqual(result.residual_energy_ratio, 0.0)

    def test_unsupported_component_abstains_preserves_residual_and_requests_expansion(self) -> None:
        x = np.sign(np.sin(2.0 * np.pi * 37.0 * self.t)) * 0.3
        result = self.engine.solve(
            self.observation(x, name="unsupported", unsupported_component=True)
        )
        self.assertEqual(result.status, "abstained")
        self.assertTrue(result.domain_expansion_requested)
        np.testing.assert_allclose(result.residual, x, atol=0.0)
        self.assertEqual(result.components, {})

    def test_two_source_conflict_does_not_emit_fake_single_farhp(self) -> None:
        x1 = np.sin(2.0 * np.pi * 120.0 * self.t)
        x2 = 0.9 * np.sin(2.0 * np.pi * 190.0 * self.t + 0.4)
        result = self.engine.solve(
            self.observation(x1 + x2, name="two-source", f0_candidates_hz=[120.0, 190.0])
        )
        self.assertEqual(result.routing.method_states["farhp"], "abstain")
        self.assertIsNone(result.farhp_frame)
        self.assertIn(result.status, {"abstained", "branched"})

    def test_reference_world_solve_replay_is_deterministic(self) -> None:
        x, _, _ = synthetic_vowel(duration_sec=0.08, sample_rate_hz=self.fs, k_max=10)
        obs = self.observation(x, name="replay")
        first = self.engine.solve(obs)
        second = self.engine.replay(obs, first.replay_token)
        self.assertEqual(first.status, second.status)
        self.assertEqual(first.routing.to_dict(), second.routing.to_dict())
        np.testing.assert_allclose(first.model_reconstruction, second.model_reconstruction, atol=0.0)
        np.testing.assert_allclose(first.residual, second.residual, atol=0.0)


if __name__ == "__main__":
    unittest.main()
