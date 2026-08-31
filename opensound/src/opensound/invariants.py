from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .geometry import circular_distance


@dataclass(frozen=True, slots=True)
class InvariantResult:
    invariant_id: str
    passed: bool
    violations: tuple[str, ...]


class InvariantEngine:
    _PRESERVE = {
        "farhp_only": ("f0_hz", "amplitudes", "noise_energy", "transient_energy"),
        "noise_only": ("f0_hz", "amplitudes", "farhp_rad", "transient_energy"),
        "transient_only": ("f0_hz", "amplitudes", "farhp_rad", "noise_energy"),
    }

    def validate(
        self,
        invariant_id: str,
        before: dict[str, Any],
        after: dict[str, Any],
        *,
        tolerance: float = 1e-9,
    ) -> InvariantResult:
        if invariant_id not in self._PRESERVE:
            raise ValueError(f"unknown invariant {invariant_id!r}")
        violations: list[str] = []
        for key in self._PRESERVE[invariant_id]:
            if key not in before or key not in after:
                violations.append(f"{key}: missing invariant quantity")
                continue
            if not self._equivalent(key, before[key], after[key], tolerance):
                violations.append(f"{key}: changed beyond tolerance")
        return InvariantResult(invariant_id, not violations, tuple(violations))

    @staticmethod
    def _equivalent(key: str, left: Any, right: Any, tolerance: float) -> bool:
        a = np.asarray(left, dtype=float)
        b = np.asarray(right, dtype=float)
        if a.shape != b.shape:
            return False
        if key == "farhp_rad":
            return bool(np.all(circular_distance(a, b) <= tolerance))
        return bool(np.allclose(a, b, rtol=0.0, atol=tolerance))
