from __future__ import annotations

import unittest

import numpy as np

from farhp.analyzer import AnalysisConfig, analyze_frame, estimate_f0_yin
from farhp.codebook import TorusCodebook
from farhp.quantizer import CircularScalarQuantizer
from farhp.reconstructor import reconstruct_frame
from farhp.synth import harmonic_synthesize, synthetic_vowel
from farhp.utils import circular_distance, rms, torus_distance, wrap_phase


class TestFARHPCore(unittest.TestCase):
    def test_wrap_and_circular_distance(self) -> None:
        self.assertAlmostEqual(float(circular_distance(-np.pi + 0.01, np.pi - 0.01)), 0.02, places=9)
        self.assertAlmostEqual(float(wrap_phase(3 * np.pi)), -np.pi, places=9)

    def test_scalar_quantizer_bound(self) -> None:
        rng = np.random.default_rng(3)
        x = rng.uniform(-np.pi, np.pi, 10000)
        q = CircularScalarQuantizer(16)
        self.assertLessEqual(float(np.max(q.error(x))), q.worst_case_error_rad + 1e-12)

    def test_f0_estimation_on_synthetic_vowel(self) -> None:
        fs = 16000
        target = 125.0
        x, _, _ = synthetic_vowel("a", f0_hz=target, sample_rate_hz=fs, duration_sec=0.4, k_max=24)
        frame = x[int(0.16 * fs) : int(0.24 * fs)]
        f0, confidence = estimate_f0_yin(frame, fs)
        self.assertLess(abs(f0 - target), 0.8)
        self.assertGreater(confidence, 0.85)

    def test_time_shift_invariance_exact_harmonics(self) -> None:
        fs = 16000
        f0 = 125.0
        duration = 0.08  # exactly 10 periods
        k = 12
        amp = 1.0 / np.arange(1, k + 1)
        psi = wrap_phase(0.17 * np.square(np.arange(1, k + 1)))
        psi[0] = 0.0
        a = harmonic_synthesize(
            f0_hz=f0,
            sample_rate_hz=fs,
            duration_sec=duration,
            amplitudes=amp,
            farhp_rad=psi,
            anchor_phase_rad=0.4,
            time_offset_sec=0.0,
        )
        b = harmonic_synthesize(
            f0_hz=f0,
            sample_rate_hz=fs,
            duration_sec=duration,
            amplitudes=amp,
            farhp_rad=psi,
            anchor_phase_rad=0.4,
            time_offset_sec=17 / fs,
        )
        cfg = AnalysisConfig(k_max=k, window="rect", remove_mean=False, amplitude_floor_db=-80)
        fa = analyze_frame(a, fs, f0_hz=f0, config=cfg)
        fb = analyze_frame(b, fs, f0_hz=f0, config=cfg)
        d = torus_distance(fa.phase_vector(), fb.phase_vector())
        self.assertLess(d, 1e-9)

    def test_harmonic_round_trip(self) -> None:
        fs = 16000
        f0 = 125.0
        duration = 0.08
        k = 10
        amp = np.linspace(1.0, 0.1, k)
        psi = wrap_phase(np.linspace(0.0, 2.2, k))
        psi[0] = 0.0
        x = harmonic_synthesize(
            f0_hz=f0,
            sample_rate_hz=fs,
            duration_sec=duration,
            amplitudes=amp,
            farhp_rad=psi,
            anchor_phase_rad=-0.31,
        )
        frame = analyze_frame(
            x,
            fs,
            f0_hz=f0,
            config=AnalysisConfig(k_max=k, window="rect", remove_mean=False, amplitude_floor_db=-80),
        )
        y = reconstruct_frame(frame, normalize=False, use_mask=False)
        self.assertLess(rms(x - y), 1e-10)

    def test_torus_codebook(self) -> None:
        rng = np.random.default_rng(8)
        cluster_a = wrap_phase(rng.normal(0.2, 0.05, size=(40, 3)))
        cluster_b = wrap_phase(rng.normal(-2.6, 0.05, size=(40, 3)))
        x = np.vstack([cluster_a, cluster_b])
        model = TorusCodebook.fit(x, 2, seed=2)
        idx, distance = model.encode(x)
        self.assertEqual(len(np.unique(idx)), 2)
        self.assertLess(float(np.mean(distance)), 0.15)


if __name__ == "__main__":
    unittest.main()
