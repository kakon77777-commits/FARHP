from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

import numpy as np

from farhp.analyzer import AnalysisConfig, analyze_frame
from farhp.reconstructor import reconstruct_frame


@dataclass(slots=True)
class NoiseEstimate:
    reconstruction: np.ndarray
    spectral_flatness: float


class FARHPRuntimeAdapter:
    def analyze(self, waveform: np.ndarray, sample_rate_hz: int):
        config = AnalysisConfig(k_max=16)
        return analyze_frame(np.asarray(waveform, dtype=float), sample_rate_hz, config=config)

    def synthesize(self, frame, sample_count: int) -> np.ndarray:
        y = reconstruct_frame(frame, duration_sec=sample_count / frame.sample_rate_hz, normalize=False)
        return np.asarray(y[:sample_count], dtype=float)


class BasicTransientModule:
    def analyze_and_reconstruct(self, waveform: np.ndarray) -> np.ndarray:
        x = np.asarray(waveform, dtype=float)
        if x.size == 0:
            return x.copy()
        width = min(9, max(3, x.size // 32 * 2 + 1))
        if width % 2 == 0:
            width += 1
        kernel = np.ones(width, dtype=float) / width
        baseline = np.convolve(x, kernel, mode="same")
        detail = x - baseline
        mad = float(np.median(np.abs(detail - np.median(detail)))) + 1e-12
        threshold = max(6.0 * 1.4826 * mad, 0.08 * float(np.max(np.abs(x))))
        mask = np.abs(detail) >= threshold
        result = np.zeros_like(x)
        result[mask] = detail[mask]
        return result


class BasicNoiseModule:
    def analyze_and_reconstruct(self, waveform: np.ndarray, *, key: str) -> NoiseEstimate:
        x = np.asarray(waveform, dtype=float)
        if x.size == 0:
            return NoiseEstimate(x.copy(), 0.0)
        spectrum = np.fft.rfft(x)
        magnitude = np.abs(spectrum)
        if magnitude.size > 3:
            kernel = np.ones(7, dtype=float) / 7.0
            smooth = np.convolve(magnitude, kernel, mode="same")
        else:
            smooth = magnitude
        seed = int.from_bytes(sha256(key.encode("utf-8")).digest()[:8], "big")
        rng = np.random.default_rng(seed)
        phase = rng.uniform(-np.pi, np.pi, size=smooth.size)
        phase[0] = 0.0
        if x.size % 2 == 0 and phase.size:
            phase[-1] = 0.0
        modeled = np.fft.irfft(smooth * np.exp(1j * phase), n=x.size)
        source_rms = float(np.sqrt(np.mean(np.square(x))))
        model_rms = float(np.sqrt(np.mean(np.square(modeled))))
        if model_rms > 1e-12:
            modeled *= min(source_rms / model_rms, 1.0)
        power = magnitude[1:] ** 2 + 1e-12
        flatness = float(np.exp(np.mean(np.log(power))) / np.mean(power)) if power.size else 0.0
        return NoiseEstimate(np.asarray(modeled, dtype=float), flatness)


class ResidualStructureAnalyzer:
    def describe(self, residual: np.ndarray) -> dict[str, float]:
        x = np.asarray(residual, dtype=float)
        energy = float(np.mean(np.square(x))) if x.size else 0.0
        diff = np.diff(x)
        transient = float(np.max(np.abs(diff))) if diff.size else 0.0
        return {"mean_square_energy": energy, "peak_difference": transient}
