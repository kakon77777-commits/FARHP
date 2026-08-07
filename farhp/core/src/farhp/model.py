from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

import numpy as np


@dataclass(slots=True)
class FARHPFrame:
    sample_rate_hz: int
    frame_time_sec: float
    frame_length_sec: float
    f0_hz: float
    f0_confidence: float
    applicability_grade: int
    harmonic_indices: list[int]
    amplitudes: list[float]
    absolute_phases_rad: list[float]
    farhp_rad: list[float]
    mask: list[int]
    confidence: list[float]
    anchor_phase_rad: float
    domain: str = "Y"
    method: str = "farhp_projection"
    method_version: str = "0.2"
    polarity_policy: str = "preserve"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        k = len(self.harmonic_indices)
        expected = {
            "amplitudes": len(self.amplitudes),
            "absolute_phases_rad": len(self.absolute_phases_rad),
            "farhp_rad": len(self.farhp_rad),
            "mask": len(self.mask),
            "confidence": len(self.confidence),
        }
        if any(v != k for v in expected.values()):
            raise ValueError(f"inconsistent harmonic vector lengths: K={k}, {expected}")
        if not self.harmonic_indices or self.harmonic_indices[0] != 1:
            raise ValueError("harmonic_indices must start at 1")
        if self.domain not in {"Y", "G"}:
            raise ValueError("domain must be Y or G")
        if not 0 <= self.applicability_grade <= 4:
            raise ValueError("applicability_grade must be in [0, 4]")

    @property
    def k_max(self) -> int:
        return self.harmonic_indices[-1]

    def phase_vector(self) -> np.ndarray:
        return np.asarray(self.farhp_rad[1:], dtype=float)

    def phase_mask(self) -> np.ndarray:
        return np.asarray(self.mask[1:], dtype=int)

    def to_spec_object(self) -> dict[str, Any]:
        phase_indices = self.harmonic_indices[1:]
        phase_values = self.farhp_rad[1:]
        phase_mask = self.mask[1:]
        phase_conf = self.confidence[1:]
        return {
            "farhp_version": "0.1",
            "domain": self.domain,
            "anchor": {
                "type": "fundamental",
                "harmonic_index": 1,
                "confidence": float(self.f0_confidence),
                "phase_rad": float(self.anchor_phase_rad),
            },
            "analysis": {
                "method": self.method,
                "method_version": self.method_version,
                "sample_rate_hz": int(self.sample_rate_hz),
                "frame_time_sec": float(self.frame_time_sec),
                "frame_length_sec": float(self.frame_length_sec),
                "f0_hz": float(self.f0_hz),
                "f0_confidence": float(self.f0_confidence),
                "applicability_grade": int(self.applicability_grade),
            },
            "phase": {
                "representation": "angle_rad",
                "harmonic_indices": [int(k) for k in phase_indices],
                "values": [float(x) for x in phase_values],
                "mask": [int(x) for x in phase_mask],
                "confidence": [float(x) for x in phase_conf],
            },
            "harmonics": {
                "indices": [int(k) for k in self.harmonic_indices],
                "amplitude": [float(x) for x in self.amplitudes],
                "absolute_phase_rad": [float(x) for x in self.absolute_phases_rad],
            },
            "polarity_policy": self.polarity_policy,
            "provenance": dict(self.metadata),
        }

    @classmethod
    def from_spec_object(cls, obj: dict[str, Any]) -> "FARHPFrame":
        phase = obj["phase"]
        harmonics = obj.get("harmonics")
        if harmonics is None:
            raise ValueError("reference reconstructor requires top-level harmonics extension")
        indices = [int(k) for k in harmonics["indices"]]
        farhp = [0.0] + [float(v) for v in phase.get("values", [])]
        mask = [1] + [int(v) for v in phase["mask"]]
        confidence = [float(obj["anchor"]["confidence"])] + [float(v) for v in phase["confidence"]]
        absolute = [float(v) for v in harmonics.get("absolute_phase_rad", [0.0] * len(indices))]
        anchor_phase = float(obj["anchor"].get("phase_rad", absolute[0] if absolute else 0.0))
        analysis = obj["analysis"]
        return cls(
            sample_rate_hz=int(analysis["sample_rate_hz"]),
            frame_time_sec=float(analysis["frame_time_sec"]),
            frame_length_sec=float(analysis.get("frame_length_sec", 0.04)),
            f0_hz=float(analysis["f0_hz"]),
            f0_confidence=float(analysis["f0_confidence"]),
            applicability_grade=int(analysis["applicability_grade"]),
            harmonic_indices=indices,
            amplitudes=[float(v) for v in harmonics["amplitude"]],
            absolute_phases_rad=absolute,
            farhp_rad=farhp,
            mask=mask,
            confidence=confidence,
            anchor_phase_rad=anchor_phase,
            domain=str(obj["domain"]),
            method=str(analysis["method"]),
            method_version=str(analysis["method_version"]),
            polarity_policy=str(obj["polarity_policy"]),
            metadata=dict(obj.get("provenance", {})),
        )

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class FARHPTrajectory:
    sample_rate_hz: int
    frame_length_sec: float
    hop_length_sec: float
    frame_times_sec: list[float]
    f0_hz: list[float | None]
    voiced: list[bool]
    track_confidence: list[float]
    frames: list[FARHPFrame | None]
    anchor_unwrapped_rad: list[float | None]
    anchor_residual_rad: list[float | None]
    farhp_unwrapped_rad: list[list[float | None]]
    phase_velocity_rad_per_sec: list[list[float | None]]
    method: str = "farhp_viterbi_trajectory"
    method_version: str = "0.2"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        length = len(self.frame_times_sec)
        fields = {
            "f0_hz": len(self.f0_hz),
            "voiced": len(self.voiced),
            "track_confidence": len(self.track_confidence),
            "frames": len(self.frames),
            "anchor_unwrapped_rad": len(self.anchor_unwrapped_rad),
            "anchor_residual_rad": len(self.anchor_residual_rad),
            "farhp_unwrapped_rad": len(self.farhp_unwrapped_rad),
            "phase_velocity_rad_per_sec": len(self.phase_velocity_rad_per_sec),
        }
        if any(value != length for value in fields.values()):
            raise ValueError(f"trajectory field lengths disagree: T={length}, {fields}")

    @property
    def frame_count(self) -> int:
        return len(self.frames)

    @property
    def voiced_ratio(self) -> float:
        return float(np.mean(self.voiced)) if self.voiced else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "farhp_trajectory_version": "0.2",
            "sample_rate_hz": self.sample_rate_hz,
            "frame_length_sec": self.frame_length_sec,
            "hop_length_sec": self.hop_length_sec,
            "frame_times_sec": self.frame_times_sec,
            "f0_hz": self.f0_hz,
            "voiced": self.voiced,
            "track_confidence": self.track_confidence,
            "frames": [frame.to_spec_object() if frame is not None else None for frame in self.frames],
            "anchor_unwrapped_rad": self.anchor_unwrapped_rad,
            "anchor_residual_rad": self.anchor_residual_rad,
            "farhp_unwrapped_rad": self.farhp_unwrapped_rad,
            "phase_velocity_rad_per_sec": self.phase_velocity_rad_per_sec,
            "method": self.method,
            "method_version": self.method_version,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, obj: dict[str, Any]) -> "FARHPTrajectory":
        return cls(
            sample_rate_hz=int(obj["sample_rate_hz"]),
            frame_length_sec=float(obj["frame_length_sec"]),
            hop_length_sec=float(obj["hop_length_sec"]),
            frame_times_sec=[float(v) for v in obj["frame_times_sec"]],
            f0_hz=[None if v is None else float(v) for v in obj["f0_hz"]],
            voiced=[bool(v) for v in obj["voiced"]],
            track_confidence=[float(v) for v in obj["track_confidence"]],
            frames=[FARHPFrame.from_spec_object(v) if v is not None else None for v in obj["frames"]],
            anchor_unwrapped_rad=[None if v is None else float(v) for v in obj["anchor_unwrapped_rad"]],
            anchor_residual_rad=[None if v is None else float(v) for v in obj["anchor_residual_rad"]],
            farhp_unwrapped_rad=[
                [None if v is None else float(v) for v in row] for row in obj["farhp_unwrapped_rad"]
            ],
            phase_velocity_rad_per_sec=[
                [None if v is None else float(v) for v in row]
                for row in obj["phase_velocity_rad_per_sec"]
            ],
            method=str(obj.get("method", "farhp_viterbi_trajectory")),
            method_version=str(obj.get("method_version", "0.2")),
            metadata=dict(obj.get("metadata", {})),
        )
