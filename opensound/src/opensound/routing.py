from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass(slots=True)
class SignalFeatures:
    rms: float
    periodicity: float
    spectral_flatness: float
    transient_score: float


@dataclass(slots=True)
class RoutingDecision:
    selected_methods: list[str] = field(default_factory=list)
    method_states: dict[str, str] = field(default_factory=dict)
    region_refs: list[str] = field(default_factory=list)
    reasons: dict[str, list[str]] = field(default_factory=dict)
    domain_expansion_requested: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "selected_methods": list(self.selected_methods),
            "method_states": dict(self.method_states),
            "region_refs": list(self.region_refs),
            "reasons": {key: list(value) for key, value in self.reasons.items()},
            "domain_expansion_requested": bool(self.domain_expansion_requested),
        }


def characterize_signal(waveform: np.ndarray, sample_rate_hz: int) -> SignalFeatures:
    x = np.asarray(waveform, dtype=float)
    if x.ndim != 1 or x.size < 16:
        raise ValueError("waveform must be a one-dimensional signal with at least 16 samples")
    centered = x - float(np.mean(x))
    rms = float(np.sqrt(np.mean(np.square(centered))))
    eps = 1e-12
    min_tau = max(2, int(sample_rate_hz / 350.0))
    max_tau = min(int(sample_rate_hz / 70.0), x.size // 2)
    periodicity = 0.0
    if rms > eps and max_tau > min_tau:
        energy = float(np.dot(centered, centered)) + eps
        values = [float(np.dot(centered[:-tau], centered[tau:]) / energy) for tau in range(min_tau, max_tau + 1)]
        periodicity = float(np.clip(max(values, default=0.0), 0.0, 1.0))
    spectrum = np.abs(np.fft.rfft(centered)) ** 2
    positive = spectrum[1:] + eps
    spectral_flatness = float(np.exp(np.mean(np.log(positive))) / np.mean(positive)) if positive.size else 0.0
    diff = np.abs(np.diff(centered))
    median_diff = float(np.median(diff)) + eps if diff.size else eps
    transient_score = float(np.max(diff) / median_diff) if diff.size else 0.0
    return SignalFeatures(rms, periodicity, spectral_flatness, transient_score)


class DeterministicRouter:
    def route(self, observation) -> tuple[RoutingDecision, SignalFeatures]:
        features = characterize_signal(observation.waveform, observation.sample_rate_hz)
        metadata = observation.metadata
        decision = RoutingDecision(
            method_states={
                "periodicity-estimator": "applicable",
                "farhp": "not_applicable",
                "noise-estimator": "not_applicable",
                "transient-detector": "not_applicable",
                "residual-structure-analyzer": "applicable",
            },
            region_refs=["human-auditory", "atmospheric-acoustic"],
        )
        if metadata.get("unsupported_component"):
            decision.region_refs = ["unknown-mechanical"]
            decision.domain_expansion_requested = True
            decision.reasons["farhp"] = ["unsupported_component"]
            return decision, features
        candidates = metadata.get("f0_candidates_hz")
        if isinstance(candidates, (list, tuple)) and len(candidates) > 1:
            decision.method_states["farhp"] = "abstain"
            decision.reasons["farhp"] = ["competing_fundamentals"]
            return decision, features
        artifact_suspected = bool(metadata.get("artifact_suspected"))
        if features.periodicity >= 0.48:
            if artifact_suspected:
                state = "weakly_applicable"
                decision.reasons["farhp"] = ["artifact_suspected", f"periodicity={features.periodicity:.4f}"]
            else:
                state = "applicable" if features.periodicity >= 0.68 else "weakly_applicable"
                decision.reasons["farhp"] = [f"periodicity={features.periodicity:.4f}"]
            decision.method_states["farhp"] = state
            decision.selected_methods.append("farhp")
        else:
            decision.reasons["farhp"] = [f"insufficient_periodicity={features.periodicity:.4f}"]
        if features.spectral_flatness >= 0.001 or features.periodicity < 0.48 or artifact_suspected:
            decision.method_states["noise-estimator"] = "applicable"
            decision.selected_methods.append("noise-estimator")
        if features.transient_score >= 3.0 or artifact_suspected:
            decision.method_states["transient-detector"] = "applicable"
            decision.selected_methods.append("transient-detector")
        decision.selected_methods.append("residual-structure-analyzer")
        return decision, features
