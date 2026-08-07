from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .utils import wrap_phase


@dataclass(slots=True)
class TorusCodebook:
    centers_rad: np.ndarray
    id: str = "farhp-torus-reference"
    version: str = "0.1"

    def __post_init__(self) -> None:
        self.centers_rad = wrap_phase(np.asarray(self.centers_rad, dtype=float))
        if self.centers_rad.ndim != 2 or self.centers_rad.shape[0] < 1:
            raise ValueError("centers_rad must be [n_codes, dimensions]")

    @property
    def n_codes(self) -> int:
        return int(self.centers_rad.shape[0])

    @property
    def dimensions(self) -> int:
        return int(self.centers_rad.shape[1])

    def distances(
        self,
        x: np.ndarray,
        *,
        mask: np.ndarray | None = None,
        weights: np.ndarray | None = None,
    ) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        one = x.ndim == 1
        if one:
            x = x[None, :]
        if x.ndim != 2 or x.shape[1] != self.dimensions:
            raise ValueError("x must have shape [N, dimensions]")
        m = np.ones_like(x) if mask is None else np.asarray(mask, dtype=float)
        w = np.ones(self.dimensions) if weights is None else np.asarray(weights, dtype=float)
        if m.shape != x.shape or w.shape != (self.dimensions,):
            raise ValueError("mask or weights shape mismatch")
        delta = wrap_phase(x[:, None, :] - self.centers_rad[None, :, :])
        effective = m[:, None, :] * np.clip(w[None, None, :], 0.0, None)
        denom = np.sum(effective, axis=2)
        d2 = np.sum(effective * np.square(delta), axis=2) / np.maximum(denom, 1e-12)
        d = np.sqrt(d2)
        invalid_rows = np.asarray(denom[:, 0] <= 0)
        d[invalid_rows, :] = np.inf
        return d[0] if one else d

    def encode(self, x: np.ndarray, **kwargs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        d = self.distances(x, **kwargs)
        if d.ndim == 1:
            idx = int(np.argmin(d))
            return np.asarray(idx), np.asarray(d[idx])
        idx = np.argmin(d, axis=1)
        return idx, d[np.arange(d.shape[0]), idx]

    def decode(self, indices: np.ndarray) -> np.ndarray:
        idx = np.asarray(indices, dtype=int)
        if np.any((idx < 0) | (idx >= self.n_codes)):
            raise ValueError("codebook index out of range")
        return self.centers_rad[idx]

    @classmethod
    def fit(
        cls,
        x: np.ndarray,
        n_codes: int,
        *,
        mask: np.ndarray | None = None,
        weights: np.ndarray | None = None,
        iterations: int = 40,
        seed: int = 0,
        id: str = "farhp-torus-reference",
        version: str = "0.1",
    ) -> "TorusCodebook":
        x = wrap_phase(np.asarray(x, dtype=float))
        if x.ndim != 2 or x.shape[0] < n_codes or n_codes < 1:
            raise ValueError("x must be [N,D] with N >= n_codes >= 1")
        n, d = x.shape
        m = np.ones_like(x) if mask is None else np.asarray(mask, dtype=float)
        w = np.ones(d) if weights is None else np.asarray(weights, dtype=float)
        if m.shape != x.shape or w.shape != (d,):
            raise ValueError("mask or weights shape mismatch")
        rng = np.random.default_rng(seed)
        centers = x[rng.choice(n, n_codes, replace=False)].copy()
        model = cls(centers, id=id, version=version)
        for _ in range(iterations):
            labels, dist = model.encode(x, mask=m, weights=w)
            changed = False
            new_centers = model.centers_rad.copy()
            for c in range(n_codes):
                members = labels == c
                if not np.any(members):
                    farthest = int(np.argmax(dist))
                    new_centers[c] = x[farthest]
                    changed = True
                    continue
                angles = x[members]
                member_mask = m[members]
                z = np.sum(member_mask * np.exp(1j * angles), axis=0)
                usable = np.sum(member_mask, axis=0) > 0
                update = new_centers[c].copy()
                update[usable] = np.angle(z[usable])
                if np.max(np.abs(wrap_phase(update - new_centers[c]))) > 1e-7:
                    changed = True
                new_centers[c] = update
            model.centers_rad = wrap_phase(new_centers)
            if not changed:
                break
        return model

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "version": self.version,
            "kind": "joint_torus",
            "n_codes": self.n_codes,
            "dimensions": self.dimensions,
            "centers_rad": self.centers_rad.tolist(),
        }
