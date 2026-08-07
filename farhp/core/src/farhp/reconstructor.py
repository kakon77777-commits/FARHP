from __future__ import annotations

import numpy as np

from .model import FARHPFrame, FARHPTrajectory
from .synth import harmonic_synthesize
from .utils import normalize_audio


def reconstruct_frame(
    frame: FARHPFrame,
    *,
    duration_sec: float | None = None,
    normalize: bool = False,
    use_mask: bool = True,
) -> np.ndarray:
    duration = frame.frame_length_sec if duration_sec is None else float(duration_sec)
    amplitudes = np.asarray(frame.amplitudes, dtype=float)
    if use_mask:
        amplitudes = amplitudes * np.asarray(frame.mask, dtype=float)
    return harmonic_synthesize(
        f0_hz=frame.f0_hz,
        sample_rate_hz=frame.sample_rate_hz,
        duration_sec=duration,
        amplitudes=amplitudes,
        farhp_rad=frame.farhp_rad,
        anchor_phase_rad=frame.anchor_phase_rad,
        normalize=normalize,
    )


def overlap_add_reconstruct(
    frames: list[FARHPFrame | None],
    *,
    hop_length_sec: float,
    normalize: bool = True,
) -> np.ndarray:
    present = [frame for frame in frames if frame is not None]
    if not present:
        return np.zeros(0, dtype=float)
    fs = present[0].sample_rate_hz
    hop = int(round(hop_length_sec * fs))
    frame_n = int(round(present[0].frame_length_sec * fs))
    output_n = hop * (len(frames) - 1) + frame_n
    output = np.zeros(output_n, dtype=float)
    weight = np.zeros(output_n, dtype=float)
    window = np.sqrt(np.hanning(frame_n))
    for i, model in enumerate(frames):
        if model is None:
            continue
        if model.sample_rate_hz != fs:
            raise ValueError("all frames must share sample rate")
        y = reconstruct_frame(model, duration_sec=frame_n / fs, normalize=False)
        start = i * hop
        output[start : start + frame_n] += y[:frame_n] * window
        weight[start : start + frame_n] += np.square(window)
    # At the outer edges a Hann-derived window approaches zero. Dividing by
    # those tiny weights creates artificial boundary spikes, so unsupported
    # edge samples remain zero instead of being numerically amplified.
    threshold = max(float(np.max(weight)) * 1e-3, 1e-10)
    valid = weight > threshold
    output[valid] /= weight[valid]
    output[~valid] = 0.0
    return normalize_audio(output) if normalize else output


def reconstruct_trajectory(
    trajectory: FARHPTrajectory,
    *,
    normalize: bool = True,
) -> np.ndarray:
    return overlap_add_reconstruct(
        trajectory.frames,
        hop_length_sec=trajectory.hop_length_sec,
        normalize=normalize,
    )
