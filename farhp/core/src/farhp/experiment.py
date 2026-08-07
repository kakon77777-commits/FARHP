from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.signal import stft

from .io import save_json, save_trajectory, write_wav
from .model import FARHPTrajectory
from .reconstructor import reconstruct_trajectory
from .transform import apply_phase_condition, transfer_phase_style
from .utils import rms


def crest_factor(waveform: np.ndarray) -> float:
    x = np.asarray(waveform, dtype=float)
    value = rms(x)
    return float(np.max(np.abs(x)) / max(value, 1e-12)) if x.size else 0.0


def log_spectral_distance(reference: np.ndarray, candidate: np.ndarray, sample_rate_hz: int) -> float:
    length = min(len(reference), len(candidate))
    if length == 0:
        return float("nan")
    _, _, zr = stft(reference[:length], fs=sample_rate_hz, nperseg=512, noverlap=384)
    _, _, zc = stft(candidate[:length], fs=sample_rate_hz, nperseg=512, noverlap=384)
    mr = 20.0 * np.log10(np.maximum(np.abs(zr), 1e-8))
    mc = 20.0 * np.log10(np.maximum(np.abs(zc), 1e-8))
    return float(np.sqrt(np.mean(np.square(mr - mc))))


def waveform_metrics(reference: np.ndarray, candidate: np.ndarray, sample_rate_hz: int) -> dict[str, float]:
    length = min(len(reference), len(candidate))
    if length == 0:
        return {"rms": 0.0, "crest_factor": 0.0, "correlation": 0.0, "log_spectral_distance_db": float("nan")}
    a = np.asarray(reference[:length], dtype=float)
    b = np.asarray(candidate[:length], dtype=float)
    correlation = float(np.corrcoef(a, b)[0, 1]) if np.std(a) > 0 and np.std(b) > 0 else 0.0
    return {
        "rms": rms(b),
        "crest_factor": crest_factor(b),
        "correlation_to_identity": correlation,
        "log_spectral_distance_db": log_spectral_distance(a, b, sample_rate_hz),
    }


def _token(seed: int, index: int) -> str:
    digest = hashlib.sha256(f"{seed}:{index}".encode("utf-8")).hexdigest()[:10]
    return f"sample_{digest}"


def create_blind_listening_pack(
    content: FARHPTrajectory,
    style: FARHPTrajectory,
    output_dir: str | Path,
    *,
    seed: int = 20260726,
) -> dict[str, Any]:
    out = Path(output_dir)
    audio_dir = out / "audio"
    trajectory_dir = out / "trajectories"
    audio_dir.mkdir(parents=True, exist_ok=True)
    trajectory_dir.mkdir(parents=True, exist_ok=True)

    conditions: list[tuple[str, FARHPTrajectory, dict[str, object]]] = []
    identity, r0 = apply_phase_condition(content, "identity")
    zero, r1 = apply_phase_condition(content, "zero")
    alternating, r2 = apply_phase_condition(content, "alternating")
    random_static, r3 = apply_phase_condition(content, "random_static", seed=seed)
    random_smooth, r4 = apply_phase_condition(content, "random_smooth", seed=seed + 1)
    morph, r5 = transfer_phase_style(content, style, strength=0.5)
    transferred, r6 = transfer_phase_style(content, style, strength=1.0)
    conditions.extend(
        [
            ("identity", identity, r0.to_dict()),
            ("zero", zero, r1.to_dict()),
            ("alternating", alternating, r2.to_dict()),
            ("random_static", random_static, r3.to_dict()),
            ("random_smooth", random_smooth, r4.to_dict()),
            ("style_morph_050", morph, r5.to_dict()),
            ("style_transfer_100", transferred, r6.to_dict()),
        ]
    )
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(conditions))
    identity_wave = reconstruct_trajectory(identity, normalize=False)
    public_samples: list[dict[str, object]] = []
    secret_samples: list[dict[str, object]] = []
    metrics: dict[str, dict[str, float]] = {}
    for public_index, condition_index in enumerate(order):
        condition, trajectory, transform_report = conditions[int(condition_index)]
        token = _token(seed, public_index)
        wav_name = f"{token}.wav"
        json_name = f"{token}.json"
        wave = reconstruct_trajectory(trajectory, normalize=False)
        write_wav(audio_dir / wav_name, trajectory.sample_rate_hz, wave)
        save_trajectory(trajectory_dir / json_name, trajectory)
        public_samples.append({"trial": public_index + 1, "audio": f"audio/{wav_name}"})
        secret_samples.append(
            {
                "trial": public_index + 1,
                "audio": f"audio/{wav_name}",
                "trajectory": f"trajectories/{json_name}",
                "condition": condition,
                "transform_report": transform_report,
            }
        )
        metrics[condition] = waveform_metrics(identity_wave, wave, trajectory.sample_rate_hz)

    public_manifest = {
        "experiment": "FARHP blind phase-only listening pack v0.3",
        "instructions": [
            "Use headphones at a comfortable fixed volume.",
            "Do not inspect the secret key before rating.",
            "Rate difference, naturalness, sharpness, breathiness, and preference independently.",
            "All samples preserve the content trajectory's F0 and harmonic amplitudes; only FARHP coordinates differ.",
        ],
        "rating_scale": {"minimum": 1, "maximum": 7},
        "fields": ["difference", "naturalness", "sharpness", "breathiness", "preference"],
        "samples": public_samples,
    }
    secret_manifest = {
        "experiment": public_manifest["experiment"],
        "seed": seed,
        "mapping": secret_samples,
        "objective_metrics": metrics,
        "warning": "Synthetic harmonic regression material; not a natural-speech perceptual validation.",
    }
    rating_template = {
        "listener_id": "",
        "device": "",
        "samples": [
            {"trial": sample["trial"], "difference": None, "naturalness": None, "sharpness": None, "breathiness": None, "preference": None, "notes": ""}
            for sample in public_samples
        ],
    }
    save_json(out / "public_manifest.json", public_manifest)
    save_json(out / "secret_key.json", secret_manifest)
    save_json(out / "rating_template.json", rating_template)
    (out / "README.md").write_text(
        "# FARHP v0.3 盲聽包\n\n"
        "先開啟 `public_manifest.json`，依 trial 順序聆聽並填寫 `rating_template.json`。"
        "完成評分前不要開啟 `secret_key.json`。所有樣本只改變 FARHP 相位座標，"
        "保留內容軌跡的基頻、諧波振幅、時長與有聲狀態。此包是合成材料方法測試，"
        "不是自然語音知覺結論。\n",
        encoding="utf-8",
    )
    return secret_manifest
