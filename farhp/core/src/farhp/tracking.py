from __future__ import annotations

from dataclasses import dataclass
from math import log

import numpy as np
from scipy.signal import medfilt

from .analyzer import AnalysisConfig, analyze_frame
from .model import FARHPFrame, FARHPTrajectory
from .utils import wrap_phase


@dataclass(slots=True)
class TrackingConfig:
    frame_length_sec: float = 0.080
    hop_length_sec: float = 0.010
    f0_min_hz: float = 70.0
    f0_max_hz: float = 350.0
    yin_threshold: float = 0.18
    max_candidates: int = 6
    transition_weight: float = 7.5
    octave_jump_penalty: float = 4.0
    voiced_unvoiced_switch_cost: float = 2.2
    unvoiced_bias: float = 0.18
    median_filter_frames: int = 5
    k_max: int = 32
    amplitude_floor_db: float = -48.0
    window: str = "hann"


@dataclass(slots=True)
class F0CandidateSet:
    frequencies_hz: np.ndarray
    confidence: np.ndarray
    periodicity: float
    energy_rms: float


def _yin_cmnd(
    frame: np.ndarray,
    sample_rate_hz: int,
    f0_min_hz: float,
    f0_max_hz: float,
) -> tuple[np.ndarray, int, int]:
    x = np.asarray(frame, dtype=float)
    x = x - np.mean(x)
    max_tau = min(int(sample_rate_hz / f0_min_hz), x.size // 2)
    min_tau = max(2, int(sample_rate_hz / f0_max_hz))
    if max_tau <= min_tau + 2:
        raise ValueError("frame is too short for the requested F0 range")
    difference = np.zeros(max_tau + 1, dtype=float)
    for tau in range(1, max_tau + 1):
        delta = x[:-tau] - x[tau:]
        difference[tau] = float(np.dot(delta, delta))
    cmnd = np.ones_like(difference)
    cumulative = 0.0
    for tau in range(1, max_tau + 1):
        cumulative += difference[tau]
        cmnd[tau] = difference[tau] * tau / cumulative if cumulative > 0 else 1.0
    return cmnd, min_tau, max_tau


def estimate_f0_candidates(
    frame: np.ndarray,
    sample_rate_hz: int,
    *,
    f0_min_hz: float,
    f0_max_hz: float,
    max_candidates: int = 6,
) -> F0CandidateSet:
    x = np.asarray(frame, dtype=float)
    energy = float(np.sqrt(np.mean(np.square(x))))
    cmnd, min_tau, max_tau = _yin_cmnd(x, sample_rate_hz, f0_min_hz, f0_max_hz)
    minima = [
        tau
        for tau in range(min_tau + 1, max_tau)
        if cmnd[tau] <= cmnd[tau - 1] and cmnd[tau] <= cmnd[tau + 1]
    ]
    if not minima:
        minima = [int(min_tau + np.argmin(cmnd[min_tau : max_tau + 1]))]
    minima = sorted(minima, key=lambda tau: float(cmnd[tau]))[: max(1, max_candidates)]
    refined: list[float] = []
    confidences: list[float] = []
    for tau in minima:
        tau_refined = float(tau)
        if 1 <= tau < max_tau:
            y0, y1, y2 = cmnd[tau - 1 : tau + 2]
            denom = y0 - 2.0 * y1 + y2
            if abs(denom) > 1e-12:
                tau_refined += float(0.5 * (y0 - y2) / denom)
        refined.append(float(sample_rate_hz / tau_refined))
        confidences.append(float(np.clip(1.0 - cmnd[tau], 0.0, 1.0)))
    order = np.argsort(refined)
    freq = np.asarray(refined, dtype=float)[order]
    conf = np.asarray(confidences, dtype=float)[order]
    periodicity = float(np.max(conf)) if conf.size else 0.0
    return F0CandidateSet(freq, conf, periodicity, energy)


def _transition_cost(
    prev_f0: float | None,
    next_f0: float | None,
    config: TrackingConfig,
) -> float:
    if prev_f0 is None and next_f0 is None:
        return 0.0
    if prev_f0 is None or next_f0 is None:
        return config.voiced_unvoiced_switch_cost
    interval = abs(log(next_f0 / prev_f0, 2.0))
    cost = config.transition_weight * interval
    if interval > 0.5:
        cost += config.octave_jump_penalty * (interval - 0.5)
    return float(cost)


def track_f0_viterbi(
    frames: list[np.ndarray],
    sample_rate_hz: int,
    *,
    config: TrackingConfig | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[F0CandidateSet]]:
    config = config or TrackingConfig()
    candidate_sets = [
        estimate_f0_candidates(
            frame,
            sample_rate_hz,
            f0_min_hz=config.f0_min_hz,
            f0_max_hz=config.f0_max_hz,
            max_candidates=config.max_candidates,
        )
        for frame in frames
    ]
    if not candidate_sets:
        return np.zeros(0), np.zeros(0, dtype=bool), np.zeros(0), []
    max_energy = max((c.energy_rms for c in candidate_sets), default=1.0)
    states: list[list[float | None]] = []
    emissions: list[np.ndarray] = []
    for candidates in candidate_sets:
        local_states: list[float | None] = [None] + [float(v) for v in candidates.frequencies_hz]
        states.append(local_states)
        energy_ratio = candidates.energy_rms / max(max_energy, 1e-12)
        periodicity = candidates.periodicity
        uv_probability = np.clip(
            (1.0 - periodicity) * 0.78 + (1.0 - energy_ratio) * 0.22 + config.unvoiced_bias,
            1e-5,
            0.99999,
        )
        local_emission = [-np.log(uv_probability)]
        for confidence in candidates.confidence:
            probability = np.clip(confidence * (0.35 + 0.65 * energy_ratio), 1e-5, 0.99999)
            local_emission.append(float(-np.log(probability)))
        emissions.append(np.asarray(local_emission, dtype=float))

    costs: list[np.ndarray] = [emissions[0].copy()]
    backpointers: list[np.ndarray] = [np.full(len(states[0]), -1, dtype=int)]
    for t in range(1, len(states)):
        current = np.full(len(states[t]), np.inf, dtype=float)
        back = np.full(len(states[t]), -1, dtype=int)
        for j, next_state in enumerate(states[t]):
            options = np.asarray(
                [
                    costs[t - 1][i] + _transition_cost(prev_state, next_state, config)
                    for i, prev_state in enumerate(states[t - 1])
                ],
                dtype=float,
            )
            best = int(np.argmin(options))
            current[j] = emissions[t][j] + options[best]
            back[j] = best
        costs.append(current)
        backpointers.append(back)

    path = np.zeros(len(states), dtype=int)
    path[-1] = int(np.argmin(costs[-1]))
    for t in range(len(states) - 1, 0, -1):
        path[t - 1] = backpointers[t][path[t]]

    raw_f0 = np.full(len(states), np.nan, dtype=float)
    confidence = np.zeros(len(states), dtype=float)
    voiced = np.zeros(len(states), dtype=bool)
    for t, state_index in enumerate(path):
        state = states[t][state_index]
        if state is not None:
            raw_f0[t] = state
            voiced[t] = True
            confidence[t] = float(candidate_sets[t].confidence[state_index - 1])
        else:
            confidence[t] = float(1.0 - candidate_sets[t].periodicity)

    smoothed = raw_f0.copy()
    voiced_indices = np.flatnonzero(voiced)
    if voiced_indices.size and config.median_filter_frames >= 3:
        kernel = int(config.median_filter_frames)
        if kernel % 2 == 0:
            kernel += 1
        contiguous = np.interp(np.arange(len(raw_f0)), voiced_indices, raw_f0[voiced_indices])
        filtered = medfilt(contiguous, kernel_size=kernel)
        smoothed[voiced] = filtered[voiced]
    return smoothed, voiced, confidence, candidate_sets


def _unwrap_nearest(observed: float, reference: float) -> float:
    return float(reference + wrap_phase(observed - reference))


def analyze_trajectory(
    waveform: np.ndarray,
    sample_rate_hz: int,
    *,
    config: TrackingConfig | None = None,
) -> FARHPTrajectory:
    config = config or TrackingConfig()
    x = np.asarray(waveform, dtype=float)
    frame_n = int(round(config.frame_length_sec * sample_rate_hz))
    hop_n = int(round(config.hop_length_sec * sample_rate_hz))
    if x.ndim != 1 or x.size < frame_n:
        raise ValueError("waveform must be one-dimensional and at least one frame long")
    starts = list(range(0, x.size - frame_n + 1, hop_n))
    raw_frames = [x[start : start + frame_n] for start in starts]
    tracked_f0, voiced, track_confidence, candidate_sets = track_f0_viterbi(
        raw_frames, sample_rate_hz, config=config
    )
    analysis_config = AnalysisConfig(
        f0_min_hz=config.f0_min_hz,
        f0_max_hz=config.f0_max_hz,
        yin_threshold=config.yin_threshold,
        k_max=config.k_max,
        amplitude_floor_db=config.amplitude_floor_db,
        window=config.window,
    )
    analyzed: list[FARHPFrame | None] = []
    for index, (start, frame_wave) in enumerate(zip(starts, raw_frames, strict=True)):
        if not voiced[index] or not np.isfinite(tracked_f0[index]):
            analyzed.append(None)
            continue
        frame = analyze_frame(
            frame_wave,
            sample_rate_hz,
            frame_time_sec=(start + frame_n / 2) / sample_rate_hz,
            f0_hz=float(tracked_f0[index]),
            config=analysis_config,
        )
        frame.f0_confidence = float(track_confidence[index])
        frame.confidence = [float(v * track_confidence[index]) for v in frame.confidence]
        frame.metadata.update(
            {
                "frame_start_sample": int(start),
                "frame_start_sec": float(start / sample_rate_hz),
                "candidate_count": int(candidate_sets[index].frequencies_hz.size),
                "track_periodicity": float(candidate_sets[index].periodicity),
                "track_energy_rms": float(candidate_sets[index].energy_rms),
            }
        )
        analyzed.append(frame)

    frame_count = len(analyzed)
    k_max = config.k_max
    anchor_unwrapped = np.full(frame_count, np.nan, dtype=float)
    anchor_residual = np.full(frame_count, np.nan, dtype=float)
    farhp_unwrapped = np.full((frame_count, k_max), np.nan, dtype=float)
    phase_velocity = np.full((frame_count, k_max), np.nan, dtype=float)
    previous_voiced: int | None = None
    for t, frame in enumerate(analyzed):
        if frame is None:
            previous_voiced = None
            continue
        k_here = len(frame.farhp_rad)
        observed_psi = np.asarray(frame.farhp_rad, dtype=float)
        mask = np.asarray(frame.mask, dtype=bool)
        if previous_voiced is None:
            anchor_unwrapped[t] = frame.anchor_phase_rad
            farhp_unwrapped[t, :k_here][mask] = observed_psi[mask]
        else:
            previous = analyzed[previous_voiced]
            assert previous is not None
            delta_t = (starts[t] - starts[previous_voiced]) / sample_rate_hz
            predicted_anchor = anchor_unwrapped[previous_voiced] + 2.0 * np.pi * 0.5 * (
                previous.f0_hz + frame.f0_hz
            ) * delta_t
            anchor_unwrapped[t] = _unwrap_nearest(frame.anchor_phase_rad, predicted_anchor)
            anchor_residual[t] = float(wrap_phase(frame.anchor_phase_rad - predicted_anchor))
            previous_values = farhp_unwrapped[previous_voiced]
            for index in range(k_here):
                if not mask[index]:
                    continue
                if np.isfinite(previous_values[index]):
                    farhp_unwrapped[t, index] = _unwrap_nearest(observed_psi[index], previous_values[index])
                    phase_velocity[t, index] = (
                        farhp_unwrapped[t, index] - previous_values[index]
                    ) / max(delta_t, 1e-12)
                else:
                    farhp_unwrapped[t, index] = observed_psi[index]
        frame.metadata["anchor_phase_unwrapped_rad"] = float(anchor_unwrapped[t])
        if np.isfinite(anchor_residual[t]):
            frame.metadata["anchor_prediction_residual_rad"] = float(anchor_residual[t])
        previous_voiced = t

    times = np.asarray([(start + frame_n / 2) / sample_rate_hz for start in starts], dtype=float)
    return FARHPTrajectory(
        sample_rate_hz=int(sample_rate_hz),
        frame_length_sec=float(config.frame_length_sec),
        hop_length_sec=float(config.hop_length_sec),
        frame_times_sec=[float(v) for v in times],
        f0_hz=[float(v) if np.isfinite(v) else None for v in tracked_f0],
        voiced=[bool(v) for v in voiced],
        track_confidence=[float(v) for v in track_confidence],
        frames=analyzed,
        anchor_unwrapped_rad=[float(v) if np.isfinite(v) else None for v in anchor_unwrapped],
        anchor_residual_rad=[float(v) if np.isfinite(v) else None for v in anchor_residual],
        farhp_unwrapped_rad=[
            [float(v) if np.isfinite(v) else None for v in row] for row in farhp_unwrapped
        ],
        phase_velocity_rad_per_sec=[
            [float(v) if np.isfinite(v) else None for v in row] for row in phase_velocity
        ],
        method="farhp_viterbi_trajectory",
        method_version="0.2",
        metadata={
            "frame_count": frame_count,
            "k_max": k_max,
            "f0_tracker": "multi-candidate YIN + Viterbi + median smoothing",
            "phase_tracker": "nearest-branch anchor prediction and torus-coordinate unwrapping",
        },
    )
