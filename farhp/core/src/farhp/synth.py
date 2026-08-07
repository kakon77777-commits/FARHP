from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from .utils import normalize_audio, wrap_phase

VOWEL_FORMANTS: dict[str, tuple[tuple[float, float, float], ...]] = {
    # Approximate neutral adult formant templates for synthetic demonstrations only.
    "a": ((730.0, 100.0, 1.00), (1090.0, 140.0, 0.75), (2440.0, 180.0, 0.45)),
    "i": ((270.0, 80.0, 1.00), (2290.0, 120.0, 0.80), (3010.0, 160.0, 0.35)),
    "u": ((300.0, 90.0, 1.00), (870.0, 110.0, 0.75), (2240.0, 170.0, 0.35)),
    "e": ((530.0, 90.0, 1.00), (1840.0, 130.0, 0.75), (2480.0, 170.0, 0.40)),
    "o": ((570.0, 100.0, 1.00), (840.0, 120.0, 0.80), (2410.0, 180.0, 0.35)),
}


def harmonic_synthesize(
    *,
    f0_hz: float,
    sample_rate_hz: int,
    duration_sec: float,
    amplitudes: Sequence[float],
    farhp_rad: Sequence[float] | None = None,
    anchor_phase_rad: float = 0.0,
    time_offset_sec: float = 0.0,
    normalize: bool = False,
) -> np.ndarray:
    """Synthesize a harmonic signal from amplitudes and FARHP coordinates.

    ``farhp_rad`` may contain K values including the zero coordinate for k=1,
    or K-1 values for harmonics 2..K.
    """
    if f0_hz <= 0 or sample_rate_hz <= 0 or duration_sec <= 0:
        raise ValueError("f0_hz, sample_rate_hz and duration_sec must be positive")
    amplitudes = np.asarray(amplitudes, dtype=float)
    if amplitudes.ndim != 1 or amplitudes.size == 0:
        raise ValueError("amplitudes must be a non-empty 1-D sequence")
    k_max = amplitudes.size
    if farhp_rad is None:
        psi = np.zeros(k_max, dtype=float)
    else:
        supplied = np.asarray(farhp_rad, dtype=float)
        if supplied.size == k_max - 1:
            psi = np.concatenate(([0.0], supplied))
        elif supplied.size == k_max:
            psi = supplied.copy()
            psi[0] = 0.0
        else:
            raise ValueError("farhp_rad must have length K or K-1")
    n = np.arange(int(round(duration_sec * sample_rate_hz)), dtype=float)
    t = n / sample_rate_hz + float(time_offset_sec)
    y = np.zeros_like(t)
    for idx, amp in enumerate(amplitudes, start=1):
        if idx * f0_hz >= sample_rate_hz / 2:
            break
        phase = idx * anchor_phase_rad + psi[idx - 1]
        y += amp * np.cos(2.0 * np.pi * idx * f0_hz * t + phase)
    return normalize_audio(y) if normalize else y


def _formant_envelope(freqs: np.ndarray, formants: tuple[tuple[float, float, float], ...]) -> np.ndarray:
    envelope = np.full_like(freqs, 0.02, dtype=float)
    for center, bandwidth, gain in formants:
        sigma = max(bandwidth / 2.355, 1.0)
        envelope += gain * np.exp(-0.5 * np.square((freqs - center) / sigma))
    return envelope


def synthetic_vowel(
    vowel: str = "a",
    *,
    f0_hz: float = 125.0,
    sample_rate_hz: int = 16000,
    duration_sec: float = 0.8,
    k_max: int = 32,
    anchor_phase_rad: float = 0.35,
    phase_style: str = "curved",
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Create a deterministic harmonic vowel-like signal for regression tests.

    Returns waveform, amplitudes, and FARHP vector including k=1.
    This is not a physiological speech synthesizer.
    """
    key = vowel.lower()
    if key not in VOWEL_FORMANTS:
        raise ValueError(f"unsupported vowel {vowel!r}; choose from {sorted(VOWEL_FORMANTS)}")
    nyquist_k = int((sample_rate_hz / 2 - 1) // f0_hz)
    k_max = max(1, min(int(k_max), nyquist_k))
    k = np.arange(1, k_max + 1, dtype=float)
    freqs = k * f0_hz
    envelope = _formant_envelope(freqs, VOWEL_FORMANTS[key])
    amplitudes = envelope / np.power(k, 0.85)
    amplitudes /= np.max(amplitudes)
    if phase_style == "aligned":
        psi = np.zeros(k_max)
    elif phase_style == "curved":
        psi = wrap_phase(0.32 * np.sqrt(k) + 0.075 * np.square(k) / k_max)
        psi[0] = 0.0
    elif phase_style == "alternating":
        psi = wrap_phase((k % 2) * np.pi * 0.72 + 0.11 * k)
        psi[0] = 0.0
    else:
        raise ValueError("phase_style must be aligned, curved, or alternating")
    waveform = harmonic_synthesize(
        f0_hz=f0_hz,
        sample_rate_hz=sample_rate_hz,
        duration_sec=duration_sec,
        amplitudes=amplitudes,
        farhp_rad=psi,
        anchor_phase_rad=anchor_phase_rad,
        normalize=True,
    )
    # A short fade avoids file-edge clicks without altering the central analysis frame.
    fade_n = min(int(0.02 * sample_rate_hz), waveform.size // 4)
    if fade_n > 1:
        fade = np.linspace(0.0, 1.0, fade_n)
        waveform[:fade_n] *= fade
        waveform[-fade_n:] *= fade[::-1]
    return waveform, amplitudes, psi


def dynamic_synthetic_vowel(
    vowel: str = "a",
    *,
    f0_start_hz: float = 110.0,
    f0_end_hz: float = 165.0,
    vibrato_depth_hz: float = 2.0,
    vibrato_rate_hz: float = 4.7,
    sample_rate_hz: int = 16000,
    duration_sec: float = 1.2,
    k_max: int = 24,
    phase_modulation_depth_rad: float = 0.22,
    breath_noise: float = 0.003,
    seed: int = 7,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate a deterministic nonstationary vowel-like signal.

    Returns waveform, sample-wise F0, and sample-wise FARHP matrix.  It is a
    regression fixture for tracking algorithms, not a physiological speech model.
    """
    key = vowel.lower()
    if key not in VOWEL_FORMANTS:
        raise ValueError(f"unsupported vowel {vowel!r}; choose from {sorted(VOWEL_FORMANTS)}")
    if duration_sec <= 0 or sample_rate_hz <= 0:
        raise ValueError("duration_sec and sample_rate_hz must be positive")
    n_samples = int(round(duration_sec * sample_rate_hz))
    t = np.arange(n_samples, dtype=float) / sample_rate_hz
    progress = np.clip(t / duration_sec, 0.0, 1.0)
    smooth = progress * progress * (3.0 - 2.0 * progress)
    f0 = f0_start_hz + (f0_end_hz - f0_start_hz) * smooth
    f0 += vibrato_depth_hz * np.sin(2.0 * np.pi * vibrato_rate_hz * t)
    phase1 = 2.0 * np.pi * np.cumsum(f0) / sample_rate_hz

    nyquist_k = int((sample_rate_hz / 2 - 1) // max(float(np.max(f0)), 1.0))
    k_max = max(1, min(int(k_max), nyquist_k))
    harmonics = np.arange(1, k_max + 1, dtype=float)
    psi_base = wrap_phase(0.28 * np.sqrt(harmonics) + 0.055 * np.square(harmonics) / k_max)
    psi_base[0] = 0.0
    modulation_rate = 1.35
    modulation_shape = np.sin(2.0 * np.pi * modulation_rate * t[:, None] + 0.17 * harmonics[None, :])
    psi = psi_base[None, :] + phase_modulation_depth_rad * modulation_shape / np.sqrt(harmonics[None, :])
    psi[:, 0] = 0.0

    freqs = f0[:, None] * harmonics[None, :]
    amplitude = np.full_like(freqs, 0.02, dtype=float)
    for center, bandwidth, gain in VOWEL_FORMANTS[key]:
        sigma = max(bandwidth / 2.355, 1.0)
        amplitude += gain * np.exp(-0.5 * np.square((freqs - center) / sigma))
    amplitude /= np.power(harmonics[None, :], 0.85)
    amplitude /= max(float(np.max(amplitude)), 1e-12)
    amplitude *= (0.88 + 0.12 * np.sin(2.0 * np.pi * 1.1 * t))[:, None]

    y = np.sum(amplitude * np.cos(harmonics[None, :] * phase1[:, None] + psi), axis=1)
    if breath_noise > 0:
        rng = np.random.default_rng(seed)
        y += breath_noise * rng.standard_normal(n_samples)
    fade_n = min(int(0.025 * sample_rate_hz), n_samples // 4)
    if fade_n > 1:
        fade = np.linspace(0.0, 1.0, fade_n)
        y[:fade_n] *= fade
        y[-fade_n:] *= fade[::-1]
    y = normalize_audio(y)
    return y, f0, psi
