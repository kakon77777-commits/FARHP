from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .utils import circular_distance, wrap_phase


@dataclass(slots=True)
class CircularScalarQuantizer:
    levels: int = 16

    def __post_init__(self) -> None:
        if self.levels < 2:
            raise ValueError("levels must be at least 2")

    @property
    def step_rad(self) -> float:
        return 2.0 * np.pi / self.levels

    @property
    def worst_case_error_rad(self) -> float:
        return np.pi / self.levels

    def encode(self, angles: np.ndarray) -> np.ndarray:
        angle = np.asarray(angles, dtype=float)
        unwrapped = np.mod(angle, 2.0 * np.pi)
        return np.mod(np.rint(unwrapped / self.step_rad).astype(int), self.levels)

    def decode(self, indices: np.ndarray) -> np.ndarray:
        q = np.asarray(indices, dtype=int)
        if np.any((q < 0) | (q >= self.levels)):
            raise ValueError("quantizer indices out of range")
        return wrap_phase(q * self.step_rad)

    def error(self, angles: np.ndarray) -> np.ndarray:
        return circular_distance(angles, self.decode(self.encode(angles)))
