from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Literal

import numpy as np

from .model import FARHPFrame, FARHPTrajectory
from .utils import circular_distance, wrap_phase

PhaseCondition = Literal["identity", "zero", "alternating", "random_static", "random_smooth"]


@dataclass(slots=True)
class PhaseTransformReport:
    operation: str
    strength: float
    changed_coordinates: int
    mean_geodesic_shift_rad: float
    max_geodesic_shift_rad: float
    metadata: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "operation": self.operation,
            "strength": self.strength,
            "changed_coordinates": self.changed_coordinates,
            "mean_geodesic_shift_rad": self.mean_geodesic_shift_rad,
            "max_geodesic_shift_rad": self.max_geodesic_shift_rad,
            "metadata": self.metadata,
        }


def geodesic_interpolate(
    source: np.ndarray | float,
    target: np.ndarray | float,
    alpha: np.ndarray | float,
) -> np.ndarray | float:
    """Shortest-path interpolation on one or more copies of S^1."""
    a = np.asarray(source, dtype=float)
    b = np.asarray(target, dtype=float)
    value = wrap_phase(a + np.asarray(alpha, dtype=float) * wrap_phase(b - a))
    if np.isscalar(source) and np.isscalar(target) and np.isscalar(alpha):
        return float(value)
    return np.asarray(value, dtype=float)


def _refresh_frame_phase(frame: FARHPFrame, phase: np.ndarray, operation: str) -> None:
    phase = np.asarray(phase, dtype=float).copy()
    if phase.shape != (len(frame.harmonic_indices),):
        raise ValueError("phase vector must match frame harmonics")
    phase[0] = 0.0
    phase = np.asarray(wrap_phase(phase), dtype=float)
    phase[0] = 0.0
    frame.farhp_rad = [float(v) for v in phase]
    absolute = [
        float(wrap_phase(k * frame.anchor_phase_rad + phase[index]))
        for index, k in enumerate(frame.harmonic_indices)
    ]
    frame.absolute_phases_rad = absolute
    frame.method_version = "0.3"
    frame.metadata = dict(frame.metadata)
    frame.metadata["phase_transform"] = operation


def _trajectory_phase_matrix(trajectory: FARHPTrajectory) -> tuple[np.ndarray, np.ndarray]:
    k_max = int(trajectory.metadata.get("k_max", 0))
    if k_max <= 0:
        k_max = max((len(frame.farhp_rad) for frame in trajectory.frames if frame is not None), default=0)
    phase = np.full((trajectory.frame_count, k_max), np.nan, dtype=float)
    mask = np.zeros((trajectory.frame_count, k_max), dtype=bool)
    for t, frame in enumerate(trajectory.frames):
        if frame is None:
            continue
        size = min(k_max, len(frame.farhp_rad))
        phase[t, :size] = np.asarray(frame.farhp_rad[:size], dtype=float)
        mask[t, :size] = np.asarray(frame.mask[:size], dtype=bool)
        if size:
            phase[t, 0] = 0.0
            mask[t, 0] = True
    return phase, mask


def _rebuild_unwrapped_and_velocity(trajectory: FARHPTrajectory) -> None:
    phase, mask = _trajectory_phase_matrix(trajectory)
    unwrapped = np.full_like(phase, np.nan)
    velocity = np.full_like(phase, np.nan)
    previous: int | None = None
    for t, frame in enumerate(trajectory.frames):
        if frame is None:
            previous = None
            continue
        valid = mask[t]
        if previous is None:
            unwrapped[t, valid] = phase[t, valid]
        else:
            dt = trajectory.frame_times_sec[t] - trajectory.frame_times_sec[previous]
            for k in np.flatnonzero(valid):
                if np.isfinite(unwrapped[previous, k]):
                    unwrapped[t, k] = unwrapped[previous, k] + wrap_phase(
                        phase[t, k] - unwrapped[previous, k]
                    )
                    velocity[t, k] = (unwrapped[t, k] - unwrapped[previous, k]) / max(dt, 1e-12)
                else:
                    unwrapped[t, k] = phase[t, k]
        previous = t
    trajectory.farhp_unwrapped_rad = [
        [float(v) if np.isfinite(v) else None for v in row] for row in unwrapped
    ]
    trajectory.phase_velocity_rad_per_sec = [
        [float(v) if np.isfinite(v) else None for v in row] for row in velocity
    ]


def _condition_target(
    trajectory: FARHPTrajectory,
    condition: PhaseCondition,
    *,
    seed: int,
) -> np.ndarray:
    source, mask = _trajectory_phase_matrix(trajectory)
    target = source.copy()
    if condition == "identity":
        return target
    if condition == "zero":
        target[mask] = 0.0
        return target
    k_max = source.shape[1]
    harmonics = np.arange(1, k_max + 1, dtype=float)
    if condition == "alternating":
        template = wrap_phase((harmonics % 2.0) * np.pi * 0.72 + 0.11 * harmonics)
        template[0] = 0.0
        target[mask] = np.broadcast_to(template, source.shape)[mask]
        return target
    rng = np.random.default_rng(seed)
    if condition == "random_static":
        template = rng.uniform(-np.pi, np.pi, size=k_max)
        template[0] = 0.0
        target[mask] = np.broadcast_to(template, source.shape)[mask]
        return target
    if condition == "random_smooth":
        controls = max(4, int(np.ceil(trajectory.frame_count / 20)))
        control_x = np.linspace(0.0, 1.0, controls)
        query_x = np.linspace(0.0, 1.0, trajectory.frame_count)
        random_steps = rng.normal(scale=0.65, size=(controls, k_max))
        random_steps[:, 0] = 0.0
        random_unwrapped = np.cumsum(random_steps, axis=0)
        smooth = np.empty((trajectory.frame_count, k_max), dtype=float)
        for k in range(k_max):
            smooth[:, k] = np.interp(query_x, control_x, random_unwrapped[:, k])
        target[mask] = np.asarray(wrap_phase(smooth), dtype=float)[mask]
        return target
    raise ValueError(f"unknown phase condition: {condition}")


def apply_phase_condition(
    trajectory: FARHPTrajectory,
    condition: PhaseCondition,
    *,
    strength: float = 1.0,
    seed: int = 7,
) -> tuple[FARHPTrajectory, PhaseTransformReport]:
    if not 0.0 <= strength <= 1.0:
        raise ValueError("strength must be in [0, 1]")
    result = deepcopy(trajectory)
    source, mask = _trajectory_phase_matrix(result)
    target = _condition_target(result, condition, seed=seed)
    transformed = np.asarray(geodesic_interpolate(source, target, strength), dtype=float)
    distances: list[float] = []
    for t, frame in enumerate(result.frames):
        if frame is None:
            continue
        size = len(frame.farhp_rad)
        local = transformed[t, :size]
        local_mask = np.asarray(frame.mask, dtype=bool)
        old = np.asarray(frame.farhp_rad, dtype=float)
        local[~local_mask] = old[~local_mask]
        local[0] = 0.0
        distances.extend(np.asarray(circular_distance(old[local_mask], local[local_mask])).tolist())
        _refresh_frame_phase(frame, local, f"condition:{condition}")
    _rebuild_unwrapped_and_velocity(result)
    result.method_version = "0.3"
    result.metadata = dict(result.metadata)
    result.metadata["phase_transform"] = {
        "operation": "condition",
        "condition": condition,
        "strength": float(strength),
        "seed": int(seed),
    }
    d = np.asarray(distances, dtype=float)
    report = PhaseTransformReport(
        operation=f"condition:{condition}",
        strength=float(strength),
        changed_coordinates=int(np.sum(d > 1e-12)),
        mean_geodesic_shift_rad=float(np.mean(d)) if d.size else 0.0,
        max_geodesic_shift_rad=float(np.max(d)) if d.size else 0.0,
        metadata={"seed": int(seed)},
    )
    return result, report


def _resample_style_phase(style: FARHPTrajectory, frame_count: int, k_max: int) -> np.ndarray:
    phase, mask = _trajectory_phase_matrix(style)
    result = np.full((frame_count, k_max), np.nan, dtype=float)
    if frame_count <= 0:
        return result
    target_x = np.linspace(0.0, 1.0, frame_count)
    source_x = np.linspace(0.0, 1.0, style.frame_count)
    for k in range(min(k_max, phase.shape[1])):
        valid = np.flatnonzero(mask[:, k] & np.isfinite(phase[:, k]))
        if valid.size == 0:
            continue
        if valid.size == 1:
            result[:, k] = phase[valid[0], k]
            continue
        unwrapped = np.unwrap(phase[valid, k])
        result[:, k] = wrap_phase(np.interp(target_x, source_x[valid], unwrapped))
    if k_max:
        result[:, 0] = 0.0
    return result


def transfer_phase_style(
    content: FARHPTrajectory,
    style: FARHPTrajectory,
    *,
    strength: float = 1.0,
) -> tuple[FARHPTrajectory, PhaseTransformReport]:
    """Transfer only FARHP coordinates while preserving content F0/amplitudes/anchor."""
    if not 0.0 <= strength <= 1.0:
        raise ValueError("strength must be in [0, 1]")
    result = deepcopy(content)
    source, mask = _trajectory_phase_matrix(result)
    target = _resample_style_phase(style, result.frame_count, source.shape[1])
    available = mask & np.isfinite(target)
    transformed = source.copy()
    transformed[available] = geodesic_interpolate(source[available], target[available], strength)
    distances: list[float] = []
    for t, frame in enumerate(result.frames):
        if frame is None:
            continue
        size = len(frame.farhp_rad)
        local = transformed[t, :size]
        old = np.asarray(frame.farhp_rad, dtype=float)
        valid = np.asarray(frame.mask, dtype=bool) & np.isfinite(local)
        local[~valid] = old[~valid]
        local[0] = 0.0
        distances.extend(np.asarray(circular_distance(old[valid], local[valid])).tolist())
        _refresh_frame_phase(frame, local, "style_transfer")
    _rebuild_unwrapped_and_velocity(result)
    result.method_version = "0.3"
    result.metadata = dict(result.metadata)
    result.metadata["phase_transform"] = {
        "operation": "style_transfer",
        "strength": float(strength),
        "style_frame_count": int(style.frame_count),
        "preserved": ["f0", "harmonic_amplitudes", "anchor_phase", "duration", "voicing"],
    }
    d = np.asarray(distances, dtype=float)
    report = PhaseTransformReport(
        operation="style_transfer",
        strength=float(strength),
        changed_coordinates=int(np.sum(d > 1e-12)),
        mean_geodesic_shift_rad=float(np.mean(d)) if d.size else 0.0,
        max_geodesic_shift_rad=float(np.max(d)) if d.size else 0.0,
        metadata={"style_frame_count": int(style.frame_count)},
    )
    return result, report
