from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.io import wavfile

from .model import FARHPFrame, FARHPTrajectory
from .utils import normalize_audio


def read_wav(path: str | Path) -> tuple[int, np.ndarray]:
    sample_rate, data = wavfile.read(path)
    x = np.asarray(data)
    if x.ndim == 2:
        x = np.mean(x.astype(float), axis=1)
    if np.issubdtype(x.dtype, np.integer):
        scale = max(abs(np.iinfo(x.dtype).min), np.iinfo(x.dtype).max)
        x = x.astype(float) / scale
    else:
        x = x.astype(float)
    return int(sample_rate), x


def write_wav(path: str | Path, sample_rate_hz: int, waveform: np.ndarray) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    y = normalize_audio(np.asarray(waveform, dtype=float), peak=0.95)
    wavfile.write(path, sample_rate_hz, np.int16(np.clip(y, -1.0, 1.0) * 32767))


def save_json(path: str | Path, obj: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_frame(path: str | Path, frame: FARHPFrame) -> None:
    save_json(path, frame.to_spec_object())


def load_frame(path: str | Path) -> FARHPFrame:
    return FARHPFrame.from_spec_object(load_json(path))


def save_trajectory(path: str | Path, trajectory: FARHPTrajectory) -> None:
    save_json(path, trajectory.to_dict())


def load_trajectory(path: str | Path) -> FARHPTrajectory:
    return FARHPTrajectory.from_dict(load_json(path))
