from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import Any

import numpy as np

from .modules import BasicNoiseModule, BasicTransientModule, FARHPRuntimeAdapter, ResidualStructureAnalyzer
from .registry import MethodRegistry, RegionRegistry
from .routing import DeterministicRouter, RoutingDecision


@dataclass(slots=True)
class SignalObservation:
    observation_id: str
    waveform: np.ndarray
    sample_rate_hz: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.waveform = np.asarray(self.waveform, dtype=float)
        if self.waveform.ndim != 1 or self.waveform.size < 16:
            raise ValueError("waveform must be one-dimensional with at least 16 samples")
        if self.sample_rate_hz <= 0:
            raise ValueError("sample_rate_hz must be positive")


@dataclass(slots=True)
class WorldSolveResult:
    observation_id: str
    status: str
    routing: RoutingDecision
    components: dict[str, np.ndarray]
    farhp_frame: Any | None
    model_reconstruction: np.ndarray
    residual: np.ndarray
    witness_reconstruction: np.ndarray
    residual_descriptors: dict[str, float]
    domain_expansion_requested: bool
    replay_token: str
    model_reconstruction_uses_preserved_residual: bool = False

    @property
    def residual_energy_ratio(self) -> float:
        denom = float(np.mean(np.square(self.witness_reconstruction))) + 1e-12
        return float(np.mean(np.square(self.residual)) / denom)

    def checkpoint(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "status": self.status,
            "routing": self.routing.to_dict(),
            "replay_token": self.replay_token,
        }


class WorldSolveEngine:
    def __init__(self) -> None:
        self.regions = RegionRegistry.seed()
        self.methods = MethodRegistry.seed()
        self.router = DeterministicRouter()
        self.farhp = FARHPRuntimeAdapter()
        self.noise = BasicNoiseModule()
        self.transient = BasicTransientModule()
        self.residual_analyzer = ResidualStructureAnalyzer()

    @classmethod
    def reference(cls) -> "WorldSolveEngine":
        return cls()

    def _token(self, observation: SignalObservation) -> str:
        metadata = json.dumps(observation.metadata, sort_keys=True, separators=(",", ":"), default=str)
        digest = sha256()
        digest.update(observation.observation_id.encode("utf-8"))
        digest.update(str(observation.sample_rate_hz).encode("ascii"))
        digest.update(observation.waveform.tobytes())
        digest.update(metadata.encode("utf-8"))
        return digest.hexdigest()

    def solve(self, observation: SignalObservation) -> WorldSolveResult:
        routing, _features = self.router.route(observation)
        x = np.asarray(observation.waveform, dtype=float)
        token = self._token(observation)

        if observation.metadata.get("unsupported_component"):
            residual = x.copy()
            return WorldSolveResult(
                observation_id=observation.observation_id,
                status="abstained",
                routing=routing,
                components={},
                farhp_frame=None,
                model_reconstruction=np.zeros_like(x),
                residual=residual,
                witness_reconstruction=x.copy(),
                residual_descriptors=self.residual_analyzer.describe(residual),
                domain_expansion_requested=True,
                replay_token=token,
            )

        if routing.method_states.get("farhp") == "abstain":
            residual = x.copy()
            return WorldSolveResult(
                observation_id=observation.observation_id,
                status="branched",
                routing=routing,
                components={},
                farhp_frame=None,
                model_reconstruction=np.zeros_like(x),
                residual=residual,
                witness_reconstruction=x.copy(),
                residual_descriptors=self.residual_analyzer.describe(residual),
                domain_expansion_requested=False,
                replay_token=token,
            )

        components: dict[str, np.ndarray] = {}
        farhp_frame = None
        harmonic = np.zeros_like(x)
        if "farhp" in routing.selected_methods:
            try:
                farhp_frame = self.farhp.analyze(x, observation.sample_rate_hz)
                if farhp_frame.applicability_grade > 0:
                    harmonic = self.farhp.synthesize(farhp_frame, x.size)
                    components["harmonic"] = harmonic
                else:
                    farhp_frame = None
                    routing.method_states["farhp"] = "not_applicable"
                    routing.selected_methods = [m for m in routing.selected_methods if m != "farhp"]
            except (ValueError, FloatingPointError):
                farhp_frame = None
                routing.method_states["farhp"] = "abstain"
                routing.selected_methods = [m for m in routing.selected_methods if m != "farhp"]

        after_harmonic = x - harmonic
        transient = np.zeros_like(x)
        if "transient-detector" in routing.selected_methods:
            transient = self.transient.analyze_and_reconstruct(after_harmonic)
            if np.any(np.abs(transient) > 0):
                components["transient"] = transient

        after_transient = after_harmonic - transient
        noise = np.zeros_like(x)
        if "noise-estimator" in routing.selected_methods:
            noise_estimate = self.noise.analyze_and_reconstruct(after_transient, key=token)
            noise = noise_estimate.reconstruction
            components["noise"] = noise

        model = harmonic + transient + noise
        residual = x - model
        witness = model + residual
        status = "committed" if components else "abstained"
        return WorldSolveResult(
            observation_id=observation.observation_id,
            status=status,
            routing=routing,
            components=components,
            farhp_frame=farhp_frame,
            model_reconstruction=model,
            residual=residual,
            witness_reconstruction=witness,
            residual_descriptors=self.residual_analyzer.describe(residual),
            domain_expansion_requested=routing.domain_expansion_requested,
            replay_token=token,
        )

    def replay(self, observation: SignalObservation, replay_token: str) -> WorldSolveResult:
        expected = self._token(observation)
        if replay_token != expected:
            raise ValueError("replay token does not match observation/config identity")
        return self.solve(observation)
