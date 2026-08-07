from __future__ import annotations

import numpy as np


def wrap_phase(angle: np.ndarray | float) -> np.ndarray | float:
    """Wrap angle(s) to [-pi, pi)."""
    wrapped = (np.asarray(angle) + np.pi) % (2.0 * np.pi) - np.pi
    if np.isscalar(angle):
        return float(wrapped)
    return wrapped


def circular_distance(a: np.ndarray | float, b: np.ndarray | float) -> np.ndarray | float:
    """Geodesic distance on S^1."""
    return np.abs(wrap_phase(np.asarray(a) - np.asarray(b)))


def torus_distance(
    a: np.ndarray,
    b: np.ndarray,
    *,
    weights: np.ndarray | None = None,
    mask: np.ndarray | None = None,
    squared: bool = False,
) -> float:
    """Weighted distance on a product of circles.

    The default uses mean squared geodesic distance followed by a square root.
    Missing coordinates are excluded by ``mask``.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.shape != b.shape:
        raise ValueError(f"shape mismatch: {a.shape} != {b.shape}")
    w = np.ones_like(a) if weights is None else np.asarray(weights, dtype=float)
    m = np.ones_like(a) if mask is None else np.asarray(mask, dtype=float)
    if w.shape != a.shape or m.shape != a.shape:
        raise ValueError("weights and mask must match phase shape")
    effective = np.clip(w, 0.0, None) * (m > 0)
    denom = float(np.sum(effective))
    if denom <= 0:
        return float("nan")
    d2 = np.square(circular_distance(a, b))
    value = float(np.sum(effective * d2) / denom)
    return value if squared else float(np.sqrt(value))


def circular_mean(angles: np.ndarray, weights: np.ndarray | None = None, axis: int = 0) -> np.ndarray:
    angles = np.asarray(angles, dtype=float)
    if weights is None:
        weights = np.ones_like(angles)
    weights = np.asarray(weights, dtype=float)
    if weights.shape != angles.shape:
        weights = np.broadcast_to(weights, angles.shape)
    z = np.sum(weights * np.exp(1j * angles), axis=axis)
    return np.angle(z)


def rms(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    return float(np.sqrt(np.mean(np.square(x))))


def normalize_audio(x: np.ndarray, peak: float = 0.95) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    maximum = float(np.max(np.abs(x))) if x.size else 0.0
    if maximum <= 0:
        return x.copy()
    return x * (peak / maximum)
