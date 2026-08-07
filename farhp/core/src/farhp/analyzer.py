from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.signal import get_window

from .model import FARHPFrame
from .utils import wrap_phase


@dataclass(slots=True)
class AnalysisConfig:
    f0_min_hz: float = 70.0
    f0_max_hz: float = 350.0
    yin_threshold: float = 0.12
    k_max: int = 32
    amplitude_floor_db: float = -48.0
    window: str = "hann"
    remove_mean: bool = True


def estimate_f0_yin(
    frame: np.ndarray,
    sample_rate_hz: int,
    *,
    f0_min_hz: float = 70.0,
    f0_max_hz: float = 350.0,
    threshold: float = 0.12,
) -> tuple[float, float]:
    """Small, dependency-light YIN-style F0 estimator for one frame.

    It implements the squared difference and cumulative mean normalized
    difference, followed by a first-threshold/local-minimum rule.
    """
    x = np.asarray(frame, dtype=float)
    if x.ndim != 1 or x.size < 8:
        raise ValueError("frame must be a one-dimensional signal with at least 8 samples")
    x = x - np.mean(x)
    max_tau = min(int(sample_rate_hz / f0_min_hz), x.size // 2)
    min_tau = max(2, int(sample_rate_hz / f0_max_hz))
    if max_tau <= min_tau + 2:
        raise ValueError("frame is too short for requested F0 range")
    difference = np.zeros(max_tau + 1, dtype=float)
    for tau in range(1, max_tau + 1):
        delta = x[:-tau] - x[tau:]
        difference[tau] = float(np.dot(delta, delta))
    cmnd = np.ones_like(difference)
    cumulative = 0.0
    for tau in range(1, max_tau + 1):
        cumulative += difference[tau]
        cmnd[tau] = difference[tau] * tau / cumulative if cumulative > 0 else 1.0
    # Collect local minima, then prefer the earliest candidate close to the
    # best normalized-difference value. This suppresses early formant-driven
    # dips while avoiding an automatic preference for a later integer multiple.
    candidates = [
        tau
        for tau in range(min_tau + 1, max_tau)
        if cmnd[tau] <= cmnd[tau - 1] and cmnd[tau] <= cmnd[tau + 1]
    ]
    if not candidates:
        tau_hat = int(min_tau + np.argmin(cmnd[min_tau : max_tau + 1]))
    else:
        best_value = min(float(cmnd[tau]) for tau in candidates)
        tolerance = max(0.015, 0.15 * best_value)
        near_best = [tau for tau in candidates if cmnd[tau] <= best_value + tolerance]
        thresholded = [tau for tau in near_best if cmnd[tau] < threshold]
        tau_hat = min(thresholded or near_best)
    refined = float(tau_hat)
    if 1 <= tau_hat < max_tau:
        y0, y1, y2 = cmnd[tau_hat - 1 : tau_hat + 2]
        denom = y0 - 2.0 * y1 + y2
        if abs(denom) > 1e-12:
            refined += float(0.5 * (y0 - y2) / denom)
    f0 = sample_rate_hz / refined
    confidence = float(np.clip(1.0 - cmnd[tau_hat], 0.0, 1.0))
    return float(f0), confidence


def _window_values(name: str, n: int) -> np.ndarray:
    if name in {"rect", "boxcar", "none"}:
        return np.ones(n, dtype=float)
    return get_window(name, n, fftbins=False).astype(float)


def analyze_frame(
    frame: np.ndarray,
    sample_rate_hz: int,
    *,
    frame_time_sec: float = 0.0,
    f0_hz: float | None = None,
    config: AnalysisConfig | None = None,
) -> FARHPFrame:
    config = config or AnalysisConfig()
    x = np.asarray(frame, dtype=float)
    if x.ndim != 1 or x.size < 16:
        raise ValueError("frame must be a one-dimensional signal with at least 16 samples")
    if config.remove_mean:
        x = x - np.mean(x)
    if f0_hz is None:
        f0_hz, f0_confidence = estimate_f0_yin(
            x,
            sample_rate_hz,
            f0_min_hz=config.f0_min_hz,
            f0_max_hz=config.f0_max_hz,
            threshold=config.yin_threshold,
        )
    else:
        if f0_hz <= 0:
            raise ValueError("f0_hz must be positive")
        f0_confidence = 1.0
    max_by_nyquist = int((sample_rate_hz / 2 - 1.0) // f0_hz)
    k_max = max(1, min(config.k_max, max_by_nyquist))
    window = _window_values(config.window, x.size)
    weighted = x * window
    n = np.arange(x.size, dtype=float)
    norm = float(np.sum(window))
    coefficients: list[complex] = []
    for k in range(1, k_max + 1):
        oscillator = np.exp(-1j * 2.0 * np.pi * k * f0_hz * n / sample_rate_hz)
        coefficient = (2.0 / norm) * np.dot(weighted, oscillator)
        coefficients.append(complex(coefficient))
    c = np.asarray(coefficients, dtype=complex)
    amplitudes = np.abs(c)
    phases = np.angle(c)
    anchor = float(phases[0])
    harmonic_indices = np.arange(1, k_max + 1)
    farhp = wrap_phase(phases - harmonic_indices * anchor)
    farhp[0] = 0.0
    peak = max(float(np.max(amplitudes)), 1e-12)
    relative_db = 20.0 * np.log10(np.maximum(amplitudes, 1e-12) / peak)
    amplitude_conf = np.clip((relative_db - config.amplitude_floor_db) / (-config.amplitude_floor_db), 0.0, 1.0)
    confidence = np.clip(amplitude_conf * f0_confidence, 0.0, 1.0)
    mask = (relative_db >= config.amplitude_floor_db).astype(int)
    mask[0] = 1
    confidence[0] = f0_confidence
    valid_ratio = float(np.mean(mask))
    if f0_confidence >= 0.90 and valid_ratio >= 0.75:
        grade = 4
    elif f0_confidence >= 0.75 and valid_ratio >= 0.55:
        grade = 3
    elif f0_confidence >= 0.55 and valid_ratio >= 0.35:
        grade = 2
    elif f0_confidence >= 0.30 and valid_ratio >= 0.20:
        grade = 1
    else:
        grade = 0
    return FARHPFrame(
        sample_rate_hz=int(sample_rate_hz),
        frame_time_sec=float(frame_time_sec),
        frame_length_sec=float(x.size / sample_rate_hz),
        f0_hz=float(f0_hz),
        f0_confidence=float(f0_confidence),
        applicability_grade=grade,
        harmonic_indices=[int(v) for v in harmonic_indices],
        amplitudes=[float(v) for v in amplitudes],
        absolute_phases_rad=[float(v) for v in phases],
        farhp_rad=[float(v) for v in farhp],
        mask=[int(v) for v in mask],
        confidence=[float(v) for v in confidence],
        anchor_phase_rad=anchor,
        metadata={"window": config.window, "amplitude_floor_db": config.amplitude_floor_db},
    )


def analyze_waveform(
    waveform: np.ndarray,
    sample_rate_hz: int,
    *,
    frame_length_sec: float = 0.080,
    hop_length_sec: float = 0.020,
    config: AnalysisConfig | None = None,
) -> list[FARHPFrame]:
    x = np.asarray(waveform, dtype=float)
    frame_n = int(round(frame_length_sec * sample_rate_hz))
    hop_n = int(round(hop_length_sec * sample_rate_hz))
    if frame_n < 16 or hop_n < 1:
        raise ValueError("invalid frame or hop length")
    frames: list[FARHPFrame] = []
    for start in range(0, max(x.size - frame_n + 1, 0), hop_n):
        center_time = (start + frame_n / 2) / sample_rate_hz
        frames.append(
            analyze_frame(
                x[start : start + frame_n],
                sample_rate_hz,
                frame_time_sec=center_time,
                config=config,
            )
        )
    return frames
