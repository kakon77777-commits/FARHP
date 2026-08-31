from __future__ import annotations

import numpy as np


def wrap_angle(value):
    array = np.asarray(value, dtype=float)
    wrapped = (array + np.pi) % (2.0 * np.pi) - np.pi
    if np.isscalar(value):
        return float(wrapped)
    return wrapped


def circular_distance(a, b):
    return np.abs(wrap_angle(np.asarray(a, dtype=float) - np.asarray(b, dtype=float)))


def circular_interpolate(source, target, alpha):
    a = np.asarray(source, dtype=float)
    b = np.asarray(target, dtype=float)
    value = wrap_angle(a + np.asarray(alpha, dtype=float) * wrap_angle(b - a))
    if np.isscalar(source) and np.isscalar(target) and np.isscalar(alpha):
        return float(value)
    return np.asarray(value, dtype=float)
