from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from farhp.experiment import create_blind_listening_pack
from farhp.synth import dynamic_synthetic_vowel
from farhp.tracking import TrackingConfig, analyze_trajectory
from farhp.transform import apply_phase_condition, geodesic_interpolate, transfer_phase_style
from farhp.utils import circular_distance


class TestPhaseTransform(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fs = 16000
        wave, _, _ = dynamic_synthetic_vowel(
            "a", f0_start_hz=110.0, f0_end_hz=150.0, sample_rate_hz=cls.fs,
            duration_sec=0.65, k_max=14, breath_noise=0.0,
        )
        config = TrackingConfig(
            frame_length_sec=0.080, hop_length_sec=0.010,
            f0_min_hz=80.0, f0_max_hz=210.0, k_max=14,
        )
        cls.content = analyze_trajectory(wave, cls.fs, config=config)
        cls.style, _ = apply_phase_condition(cls.content, "alternating")

    def test_geodesic_interpolation_crosses_pi_not_zero(self) -> None:
        a = np.deg2rad(170.0)
        b = np.deg2rad(-170.0)
        midpoint = float(geodesic_interpolate(a, b, 0.5))
        self.assertLess(abs(abs(midpoint) - np.pi), 1e-10)

    def test_zero_condition_preserves_nonphase_parameters(self) -> None:
        zero, report = apply_phase_condition(self.content, "zero")
        self.assertGreater(report.changed_coordinates, 0)
        for original, transformed in zip(self.content.frames, zero.frames, strict=True):
            if original is None:
                self.assertIsNone(transformed)
                continue
            assert transformed is not None
            self.assertEqual(original.f0_hz, transformed.f0_hz)
            np.testing.assert_allclose(original.amplitudes, transformed.amplitudes)
            self.assertEqual(original.anchor_phase_rad, transformed.anchor_phase_rad)
            phase = np.asarray(transformed.farhp_rad)
            mask = np.asarray(transformed.mask, dtype=bool)
            self.assertLess(float(np.max(np.abs(phase[mask]))), 1e-12)

    def test_random_condition_is_reproducible(self) -> None:
        first, _ = apply_phase_condition(self.content, "random_smooth", seed=19)
        second, _ = apply_phase_condition(self.content, "random_smooth", seed=19)
        third, _ = apply_phase_condition(self.content, "random_smooth", seed=20)
        a = np.asarray(first.frames[5].farhp_rad)
        b = np.asarray(second.frames[5].farhp_rad)
        c = np.asarray(third.frames[5].farhp_rad)
        np.testing.assert_allclose(a, b)
        self.assertGreater(float(np.max(circular_distance(a[1:], c[1:]))), 1e-3)

    def test_style_transfer_strength_endpoints(self) -> None:
        unchanged, _ = transfer_phase_style(self.content, self.style, strength=0.0)
        transferred, report = transfer_phase_style(self.content, self.style, strength=1.0)
        self.assertGreater(report.mean_geodesic_shift_rad, 0.1)
        for base, same, styled in zip(self.content.frames, unchanged.frames, transferred.frames, strict=True):
            if base is None:
                continue
            assert same is not None and styled is not None
            np.testing.assert_allclose(base.farhp_rad, same.farhp_rad, atol=1e-12)
            np.testing.assert_allclose(base.amplitudes, styled.amplitudes, atol=0)
            self.assertEqual(base.f0_hz, styled.f0_hz)

    def test_half_morph_is_geodesic_midpoint(self) -> None:
        half, _ = transfer_phase_style(self.content, self.style, strength=0.5)
        for base, target, middle in zip(self.content.frames, self.style.frames, half.frames, strict=True):
            if base is None or target is None or middle is None:
                continue
            a = np.asarray(base.farhp_rad[1:8])
            b = np.asarray(target.farhp_rad[1:8])
            m = np.asarray(middle.farhp_rad[1:8])
            total = np.asarray(circular_distance(a, b))
            left = np.asarray(circular_distance(a, m))
            np.testing.assert_allclose(left, total * 0.5, atol=1e-8)
            break

    def test_transform_report_schema(self) -> None:
        from jsonschema import Draft202012Validator
        import json
        transformed, report = apply_phase_condition(self.content, "zero")
        schema_path = Path(__file__).resolve().parents[1] / "spec" / "FARHP_Transform_Spec_v0.3.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        errors = list(Draft202012Validator(schema).iter_errors(report.to_dict()))
        self.assertEqual(errors, [])

    def test_overlap_add_does_not_create_edge_spikes(self) -> None:
        from farhp.reconstructor import reconstruct_trajectory
        from farhp.experiment import crest_factor
        waveform = reconstruct_trajectory(self.content, normalize=False)
        self.assertLess(crest_factor(waveform), 20.0)

    def test_blind_pack_contains_public_and_secret_manifests(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = create_blind_listening_pack(self.content, self.style, directory, seed=33)
            root = Path(directory)
            self.assertTrue((root / "public_manifest.json").exists())
            self.assertTrue((root / "secret_key.json").exists())
            self.assertTrue((root / "rating_template.json").exists())
            self.assertEqual(len(report["mapping"]), 7)
            self.assertEqual(len(list((root / "audio").glob("*.wav"))), 7)
            public_text = (root / "public_manifest.json").read_text(encoding="utf-8")
            self.assertNotIn('"condition"', public_text)


if __name__ == "__main__":
    unittest.main()
