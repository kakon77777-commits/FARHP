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


@dataclass(frozen=True, slots=True)
class DomainExpansionRequest:
    observation_ref: str
    status: str = "open"
    triggers: tuple[str, ...] = ()
    candidate_regions: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CouplingPort:
    source_module: str
    target_module: str
    quantity: str
    mandatory: bool = False


@dataclass(slots=True)
class CouplingGraph:
    ports: list[CouplingPort] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class WorldCheckpoint:
    observation_id: str
    replay_token: str
    status: str
    routing_snapshot: dict[str, Any]


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
    branches: list[dict[str, Any]] = field(default_factory=list)
    ledger_events: list[dict[str, Any]] = field(default_factory=list)
    failure: dict[str, Any] | None = None
    domain_expansion_request: DomainExpansionRequest | None = None
    coupling_graph: CouplingGraph = field(default_factory=CouplingGraph)

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

    @staticmethod
    def _event(events: list[dict[str, Any]], event_type: str, **payload: Any) -> None:
        events.append({"sequence": len(events), "event_type": event_type, **payload})

    def _token(self, observation: SignalObservation) -> str:
        metadata = json.dumps(observation.metadata, sort_keys=True, separators=(",", ":"), default=str)
        digest = sha256()
        digest.update(observation.observation_id.encode("utf-8"))
        digest.update(str(observation.sample_rate_hz).encode("ascii"))
        digest.update(observation.waveform.tobytes())
        digest.update(metadata.encode("utf-8"))
        return digest.hexdigest()

    def _terminal_result(
        self,
        observation: SignalObservation,
        routing: RoutingDecision,
        token: str,
        events: list[dict[str, Any]],
        *,
        status: str,
        components: dict[str, np.ndarray] | None = None,
        farhp_frame: Any | None = None,
        model_reconstruction: np.ndarray | None = None,
        residual: np.ndarray | None = None,
        domain_expansion_requested: bool = False,
        domain_expansion_request: DomainExpansionRequest | None = None,
        branches: list[dict[str, Any]] | None = None,
        failure: dict[str, Any] | None = None,
        coupling_graph: CouplingGraph | None = None,
    ) -> WorldSolveResult:
        x = np.asarray(observation.waveform, dtype=float)
        model = np.zeros_like(x) if model_reconstruction is None else np.asarray(model_reconstruction, dtype=float)
        res = x - model if residual is None else np.asarray(residual, dtype=float)
        witness = model + res
        if not any(event["event_type"] == "residual" for event in events):
            self._event(events, "residual", mean_square_energy=float(np.mean(np.square(res))))
        self._event(events, status)
        return WorldSolveResult(
            observation_id=observation.observation_id,
            status=status,
            routing=routing,
            components=components or {},
            farhp_frame=farhp_frame,
            model_reconstruction=model,
            residual=res,
            witness_reconstruction=witness,
            residual_descriptors=self.residual_analyzer.describe(res),
            domain_expansion_requested=domain_expansion_requested,
            replay_token=token,
            branches=branches or [],
            ledger_events=events,
            failure=failure,
            domain_expansion_request=domain_expansion_request,
            coupling_graph=coupling_graph or CouplingGraph(),
        )

    @staticmethod
    def _coupling_graph(routing: RoutingDecision) -> CouplingGraph:
        graph = CouplingGraph()
        selected = set(routing.selected_methods)
        if {"transient-detector", "farhp"}.issubset(selected):
            graph.ports.append(
                CouplingPort(
                    source_module="transient-detector",
                    target_module="farhp",
                    quantity="transient_cleaned_waveform",
                    mandatory=False,
                )
            )
        return graph

    def solve(self, observation: SignalObservation) -> WorldSolveResult:
        events: list[dict[str, Any]] = []
        routing, _features = self.router.route(observation)
        self._event(events, "route", routing=routing.to_dict())
        x = np.asarray(observation.waveform, dtype=float)
        token = self._token(observation)
        coupling_graph = self._coupling_graph(routing)

        if observation.metadata.get("unsupported_component"):
            request = DomainExpansionRequest(
                observation_ref=observation.observation_id,
                status="open",
                triggers=("unsupported_component",),
                candidate_regions=tuple(routing.region_refs),
            )
            self._event(events, "domain_expansion_request", triggers=list(request.triggers))
            return self._terminal_result(
                observation,
                routing,
                token,
                events,
                status="abstained",
                residual=x.copy(),
                domain_expansion_requested=True,
                domain_expansion_request=request,
                coupling_graph=coupling_graph,
            )

        if routing.method_states.get("farhp") == "abstain":
            candidates = observation.metadata.get("f0_candidates_hz") or []
            branches = [
                {"branch_id": f"branch-f0-{index}", "hypothesis": "single_harmonic_candidate", "f0_hz": float(value)}
                for index, value in enumerate(candidates)
            ]
            self._event(events, "branch", count=len(branches))
            return self._terminal_result(
                observation,
                routing,
                token,
                events,
                status="branched",
                residual=x.copy(),
                branches=branches,
                coupling_graph=coupling_graph,
            )

        components: dict[str, np.ndarray] = {}

        # The transient solver runs before FARHP when both are selected.  Its
        # reconstructed event component is subtracted and the cleaned waveform
        # is explicitly transferred through a coupling port to FARHP.
        transient = np.zeros_like(x)
        farhp_input = x.copy()
        if "transient-detector" in routing.selected_methods:
            self._event(events, "module_start", module="transient-detector")
            try:
                transient = self.transient.analyze_and_reconstruct(x)
                if np.any(np.abs(transient) > 0):
                    components["transient"] = transient
                self._event(events, "module_finish", module="transient-detector")
                if "farhp" in routing.selected_methods:
                    farhp_input = x - transient
                    self._event(
                        events,
                        "port_exchange",
                        source_module="transient-detector",
                        target_module="farhp",
                        quantity="transient_cleaned_waveform",
                    )
            except Exception as exc:
                self._event(events, "module_fail", module="transient-detector", error_type=type(exc).__name__, message=str(exc))
                return self._terminal_result(
                    observation,
                    routing,
                    token,
                    events,
                    status="failed",
                    residual=x.copy(),
                    failure={"module": "transient-detector", "error_type": type(exc).__name__, "message": str(exc)},
                    coupling_graph=coupling_graph,
                )

        farhp_frame = None
        harmonic = np.zeros_like(x)
        if "farhp" in routing.selected_methods:
            self._event(events, "module_start", module="farhp")
            try:
                farhp_frame = self.farhp.analyze(farhp_input, observation.sample_rate_hz)
                if farhp_frame.applicability_grade > 0:
                    harmonic = self.farhp.synthesize(farhp_frame, x.size)
                    components["harmonic"] = harmonic
                    self._event(events, "module_finish", module="farhp")
                else:
                    farhp_frame = None
                    routing.method_states["farhp"] = "not_applicable"
                    routing.selected_methods = [m for m in routing.selected_methods if m != "farhp"]
                    self._event(events, "module_abstain", module="farhp", reason="applicability_grade_zero")
            except (ValueError, FloatingPointError) as exc:
                farhp_frame = None
                routing.method_states["farhp"] = "abstain"
                routing.selected_methods = [m for m in routing.selected_methods if m != "farhp"]
                self._event(events, "module_abstain", module="farhp", reason=type(exc).__name__)
            except Exception as exc:
                self._event(events, "module_fail", module="farhp", error_type=type(exc).__name__, message=str(exc))
                return self._terminal_result(
                    observation,
                    routing,
                    token,
                    events,
                    status="failed",
                    residual=x.copy(),
                    failure={"module": "farhp", "error_type": type(exc).__name__, "message": str(exc)},
                    coupling_graph=coupling_graph,
                )

        after_modeled_structure = x - transient - harmonic
        noise = np.zeros_like(x)
        if "noise-estimator" in routing.selected_methods:
            self._event(events, "module_start", module="noise-estimator")
            try:
                noise_estimate = self.noise.analyze_and_reconstruct(after_modeled_structure, key=token)
                noise = noise_estimate.reconstruction
                components["noise"] = noise
                self._event(events, "module_finish", module="noise-estimator")
            except Exception as exc:
                self._event(events, "module_fail", module="noise-estimator", error_type=type(exc).__name__, message=str(exc))
                return self._terminal_result(
                    observation,
                    routing,
                    token,
                    events,
                    status="failed",
                    residual=x.copy(),
                    failure={"module": "noise-estimator", "error_type": type(exc).__name__, "message": str(exc)},
                    coupling_graph=coupling_graph,
                )

        model = harmonic + transient + noise
        self._event(events, "reconstruct", component_count=len(components))
        residual = x - model
        self._event(events, "residual", mean_square_energy=float(np.mean(np.square(residual))))
        status = "committed" if components else "abstained"
        return self._terminal_result(
            observation,
            routing,
            token,
            events,
            status=status,
            components=components,
            farhp_frame=farhp_frame,
            model_reconstruction=model,
            residual=residual,
            domain_expansion_requested=routing.domain_expansion_requested,
            coupling_graph=coupling_graph,
        )

    def create_checkpoint(self, result: WorldSolveResult) -> WorldCheckpoint:
        return WorldCheckpoint(
            observation_id=result.observation_id,
            replay_token=result.replay_token,
            status=result.status,
            routing_snapshot=result.routing.to_dict(),
        )

    def rollback(self, observation: SignalObservation, checkpoint: WorldCheckpoint) -> WorldSolveResult:
        if checkpoint.observation_id != observation.observation_id:
            raise ValueError("checkpoint belongs to a different observation")
        result = self.replay(observation, checkpoint.replay_token)
        if result.status != checkpoint.status or result.routing.to_dict() != checkpoint.routing_snapshot:
            raise ValueError("rollback replay does not match checkpoint state")
        return result

    def replay(self, observation: SignalObservation, replay_token: str) -> WorldSolveResult:
        expected = self._token(observation)
        if replay_token != expected:
            raise ValueError("replay token does not match observation/config identity")
        return self.solve(observation)
