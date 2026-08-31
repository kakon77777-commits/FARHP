from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any, Callable

import numpy as np

from farhp.synth import harmonic_synthesize

from .geometry import circular_distance


@dataclass(frozen=True, slots=True)
class BenchmarkCase:
    benchmark_id: str
    fixture_family: str
    expected_behavior: str


class BenchmarkRegistry:
    def __init__(self, cases: list[BenchmarkCase] | None = None) -> None:
        self._cases = {case.benchmark_id: case for case in (cases or [])}

    @classmethod
    def seed(cls) -> "BenchmarkRegistry":
        return cls([
            BenchmarkCase("bench-h", "H", "farhp_committed"),
            BenchmarkCase("bench-hn", "H+N", "layered_committed"),
            BenchmarkCase("bench-ht", "H+T", "layered_committed"),
            BenchmarkCase("bench-hnt", "H+N+T", "layered_committed"),
            BenchmarkCase("bench-noise", "N", "farhp_not_applicable"),
            BenchmarkCase("bench-transient", "T", "farhp_not_applicable"),
            BenchmarkCase("bench-unsupported", "U", "abstain_and_expand"),
            BenchmarkCase("bench-artifact", "ARTIFACT", "no_high_confidence_farhp"),
        ])

    def ids(self) -> set[str]:
        return set(self._cases)

    def get(self, benchmark_id: str) -> BenchmarkCase:
        return self._cases[benchmark_id]


@dataclass(slots=True)
class FixtureArtifact:
    fixture_id: str
    family: str
    waveform: np.ndarray
    sample_rate_hz: int
    ground_truth: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)
    seed: int = 0


class FixtureGenerator:
    def __init__(self, *, sample_rate_hz: int = 16000, duration_sec: float = 0.08) -> None:
        self.sample_rate_hz = int(sample_rate_hz)
        self.duration_sec = float(duration_sec)

    @classmethod
    def reference(cls, **kwargs) -> "FixtureGenerator":
        return cls(**kwargs)

    def _harmonic(self) -> tuple[np.ndarray, dict[str, Any]]:
        f0 = 140.0
        amplitudes = np.asarray([1.0, 0.45, 0.2, 0.1], dtype=float)
        farhp = np.asarray([0.0, 0.5, -0.8, 1.1], dtype=float)
        waveform = harmonic_synthesize(
            f0_hz=f0,
            sample_rate_hz=self.sample_rate_hz,
            duration_sec=self.duration_sec,
            amplitudes=amplitudes,
            farhp_rad=farhp,
            normalize=False,
        )
        truth = {
            "f0_hz": f0,
            "amplitudes": amplitudes.tolist(),
            "farhp_rad": farhp.tolist(),
        }
        return waveform, truth

    def generate(self, family: str, *, seed: int, private_label: str | None = None) -> FixtureArtifact:
        family = family.upper()
        rng = np.random.default_rng(seed)
        n = int(round(self.duration_sec * self.sample_rate_hz))
        t = np.arange(n, dtype=float) / self.sample_rate_hz
        harmonic, harmonic_truth = self._harmonic()
        noise = 0.025 * rng.standard_normal(n)
        transient = np.zeros(n, dtype=float)
        start = min(max(n // 2 + 60, 4), n - 5)
        transient[start : start + 4] = np.asarray([0.28, -0.22, 0.12, -0.06])
        metadata: dict[str, Any] = {}
        truth: dict[str, Any] = {"family": family}

        if family == "H":
            waveform = harmonic.copy()
            truth.update(harmonic_truth)
        elif family == "N":
            waveform = 0.2 * rng.standard_normal(n)
            truth["component"] = "noise"
        elif family == "T":
            waveform = np.zeros(n, dtype=float)
            waveform[n // 2] = 1.0
            waveform[n // 2 + 1] = -0.65
            truth["component"] = "transient"
        elif family == "H+N":
            waveform = harmonic + noise
            truth.update(harmonic_truth)
            truth["noise_rms"] = float(np.sqrt(np.mean(np.square(noise))))
        elif family == "H+T":
            waveform = harmonic + transient
            truth.update(harmonic_truth)
            truth["transient_onset_sample"] = int(start)
        elif family == "H+N+T":
            waveform = harmonic + noise + transient
            truth.update(harmonic_truth)
            truth["noise_rms"] = float(np.sqrt(np.mean(np.square(noise))))
            truth["transient_onset_sample"] = int(start)
        elif family == "U":
            waveform = np.sign(np.sin(2.0 * np.pi * 37.0 * t)) * 0.3
            metadata["unsupported_component"] = True
            truth["component"] = "deliberately_unsupported"
        elif family == "ARTIFACT":
            waveform = np.clip(1.8 * harmonic, -0.35, 0.35)
            metadata["artifact_suspected"] = True
            truth["artifact"] = "hard_clipping"
        else:
            raise ValueError(f"unsupported fixture family {family!r}")

        if private_label is not None:
            truth["private_label"] = private_label
        identity_payload = f"opensound-fixture-v0.1|{family}|{seed}|{self.sample_rate_hz}|{self.duration_sec}"
        fixture_id = "fixture-" + sha256(identity_payload.encode("utf-8")).hexdigest()[:20]
        return FixtureArtifact(fixture_id, family, np.asarray(waveform, dtype=float), self.sample_rate_hz, truth, metadata, int(seed))


@dataclass(frozen=True, slots=True)
class MetricRecord:
    metric_id: str
    direction: str


class MetricRegistry:
    def __init__(self, records: list[MetricRecord] | None = None) -> None:
        self._records = {record.metric_id: record for record in (records or [])}

    @classmethod
    def seed(cls) -> "MetricRegistry":
        return cls([
            MetricRecord("waveform_nrmse", "lower_is_better"),
            MetricRecord("f0_error_hz", "lower_is_better"),
            MetricRecord("farhp_circular_error_rad", "lower_is_better"),
            MetricRecord("false_certainty_rate", "lower_is_better"),
            MetricRecord("false_activation_rate", "lower_is_better"),
            MetricRecord("residual_structure", "lower_is_better"),
            MetricRecord("reopening_gain", "higher_is_better"),
        ])

    def ids(self) -> set[str]:
        return set(self._records)


def waveform_nrmse(reference: np.ndarray, estimate: np.ndarray) -> float:
    x = np.asarray(reference, dtype=float)
    y = np.asarray(estimate, dtype=float)
    return float(np.linalg.norm(x - y) / (np.linalg.norm(x) + 1e-12))


def farhp_circular_error(reference: list[float], estimate: list[float]) -> float:
    ref = np.asarray(reference, dtype=float)
    est = np.asarray(estimate, dtype=float)
    n = min(ref.size, est.size)
    if n <= 1:
        return 0.0
    return float(np.mean(circular_distance(ref[1:n], est[1:n])))
