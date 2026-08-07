from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np
from jsonschema import Draft202012Validator

from farhp.io import load_json

from farhp.io import load_trajectory, save_trajectory
from farhp.reconstructor import reconstruct_trajectory
from farhp.synth import dynamic_synthetic_vowel
from farhp.tracking import TrackingConfig, analyze_trajectory


class TestFARHPTrajectory(unittest.TestCase):
    def setUp(self) -> None:
        self.fs = 16000
        self.waveform, self.true_f0, _ = dynamic_synthetic_vowel(
            "a",
            f0_start_hz=112.0,
            f0_end_hz=158.0,
            sample_rate_hz=self.fs,
            duration_sec=1.0,
            k_max=18,
            breath_noise=0.001,
        )
        self.config = TrackingConfig(
            frame_length_sec=0.080,
            hop_length_sec=0.010,
            f0_min_hz=80.0,
            f0_max_hz=220.0,
            k_max=18,
        )

    def test_dynamic_f0_tracking(self) -> None:
        trajectory = analyze_trajectory(self.waveform, self.fs, config=self.config)
        estimated = np.asarray(
            [np.nan if value is None else value for value in trajectory.f0_hz], dtype=float
        )
        indices = np.clip(
            np.rint(np.asarray(trajectory.frame_times_sec) * self.fs).astype(int),
            0,
            self.true_f0.size - 1,
        )
        reference = self.true_f0[indices]
        valid = np.isfinite(estimated)
        self.assertGreater(float(np.mean(valid)), 0.95)
        self.assertLess(float(np.mean(np.abs(estimated[valid] - reference[valid]))), 1.5)

    def test_anchor_tracking_is_locally_continuous(self) -> None:
        trajectory = analyze_trajectory(self.waveform, self.fs, config=self.config)
        residual = np.asarray(
            [np.nan if value is None else abs(value) for value in trajectory.anchor_residual_rad],
            dtype=float,
        )
        self.assertLess(float(np.nanmedian(residual)), 0.35)
        self.assertLess(float(np.nanpercentile(residual, 95)), 1.2)

    def test_trajectory_serialization_and_reconstruction(self) -> None:
        trajectory = analyze_trajectory(self.waveform, self.fs, config=self.config)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trajectory.json"
            save_trajectory(path, trajectory)
            restored = load_trajectory(path)
        self.assertEqual(restored.frame_count, trajectory.frame_count)
        self.assertAlmostEqual(restored.voiced_ratio, trajectory.voiced_ratio, places=12)
        reconstruction = reconstruct_trajectory(restored, normalize=False)
        self.assertGreater(reconstruction.size, 0)
        self.assertTrue(np.all(np.isfinite(reconstruction)))

    def test_unvoiced_gap_resets_phase_track(self) -> None:
        first = self.waveform[: int(0.45 * self.fs)]
        gap = np.zeros(int(0.18 * self.fs), dtype=float)
        joined = np.concatenate([first, gap, first])
        trajectory = analyze_trajectory(joined, self.fs, config=self.config)
        times = np.asarray(trajectory.frame_times_sec)
        voiced = np.asarray(trajectory.voiced)
        inside_gap = (times > 0.47) & (times < 0.60)
        self.assertEqual(int(np.sum(voiced[inside_gap])), 0)
        restart_candidates = np.flatnonzero(voiced & (times > 0.60))
        self.assertGreater(restart_candidates.size, 0)
        restart = int(restart_candidates[0])
        self.assertIsNone(trajectory.anchor_residual_rad[restart])

    def test_trajectory_schema(self) -> None:
        trajectory = analyze_trajectory(self.waveform, self.fs, config=self.config)
        schema_path = Path(__file__).resolve().parents[1] / "spec" / "FARHP_Trajectory_Spec_v0.2.schema.json"
        schema = load_json(schema_path)
        errors = list(Draft202012Validator(schema).iter_errors(trajectory.to_dict()))
        self.assertEqual(errors, [])

    def test_farhp_unwrapped_tracks_without_boundary_spikes(self) -> None:
        trajectory = analyze_trajectory(self.waveform, self.fs, config=self.config)
        phase = np.asarray(
            [
                [np.nan if value is None else value for value in row]
                for row in trajectory.farhp_unwrapped_rad
            ],
            dtype=float,
        )
        # Ignore the anchor coordinate k=1 and low-confidence high harmonics.
        delta = np.diff(phase[:, 1:8], axis=0)
        finite = np.isfinite(delta)
        self.assertGreater(int(np.sum(finite)), 100)
        self.assertLess(float(np.nanpercentile(np.abs(delta), 95)), 1.5)


if __name__ == "__main__":
    unittest.main()
