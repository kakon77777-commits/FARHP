from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


_TRAJECTORY_TIME_FIELDS = (
    "frame_times_sec",
    "f0_hz",
    "voiced",
    "track_confidence",
    "frames",
    "anchor_unwrapped_rad",
    "anchor_residual_rad",
    "farhp_unwrapped_rad",
    "phase_velocity_rad_per_sec",
)
_TRANSFORM_REPORT_FIELDS = (
    "operation",
    "strength",
    "changed_coordinates",
    "mean_geodesic_shift_rad",
    "max_geodesic_shift_rad",
    "metadata",
)


def validate_farhp_semantics(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if obj.get("domain") == "G" and not isinstance(obj.get("inverse_filter"), dict):
        errors.append("<root>: domain G requires an inverse_filter object")
    phase = obj.get("phase")
    if isinstance(phase, dict):
        lengths = {
            key: len(phase[key])
            for key in ("harmonic_indices", "mask", "confidence")
            if isinstance(phase.get(key), list)
        }
        if len(set(lengths.values())) > 1:
            errors.append(f"phase: harmonic vector length mismatch: {lengths}")
    return errors


def validate_trajectory_semantics(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(obj.get("frame_times_sec"), list):
        return ["frame_times_sec: required for trajectory semantic validation"]
    expected = len(obj["frame_times_sec"])
    lengths: dict[str, int] = {}
    for key in _TRAJECTORY_TIME_FIELDS:
        value = obj.get(key)
        if isinstance(value, list):
            lengths[key] = len(value)
        else:
            errors.append(f"{key}: required time-indexed array")
    bad = {key: length for key, length in lengths.items() if length != expected}
    if bad:
        errors.append(f"<root>: trajectory field length mismatch: T={expected}, {bad}")
    return errors


def validate_transform_report_semantics(obj: dict[str, Any]) -> list[str]:
    return [f"{key}: required transform report field" for key in _TRANSFORM_REPORT_FIELDS if key not in obj]


def validate_spec_object(obj: dict[str, Any], schema_path: str | Path) -> list[str]:
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(obj), key=lambda error: list(error.path))
    messages = [f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors]
    schema_id = str(schema.get("$id", ""))
    if schema_id.endswith("/spec/farhp/0.1/schema.json"):
        messages.extend(validate_farhp_semantics(obj))
    elif "/farhp/trajectory/0.2/" in schema_id:
        messages.extend(validate_trajectory_semantics(obj))
    elif "/farhp/transform/0.3/" in schema_id:
        messages.extend(validate_transform_report_semantics(obj))
    return messages
