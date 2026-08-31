from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .benchmark import BenchmarkCase, BenchmarkRegistry, FixtureArtifact, FixtureGenerator, farhp_circular_error, waveform_nrmse
from .contracts import EvidenceLevel, EvidenceRecord, EvidenceType
from .runtime import SignalObservation, WorldSolveEngine, WorldSolveResult


_HIDDEN_LABEL_KEYS = frozenset({
    "private_label",
    "class_label",
    "source_name",
    "filename",
    "directory_label",
    "text_description",
})


class EvidenceLedger:
    def __init__(self) -> None:
        self._records: dict[str, EvidenceRecord] = {}

    def record_synthetic(self, evidence_id: str, *, direction: str = "support", strength: float | None = None) -> EvidenceRecord:
        record = EvidenceRecord(
            evidence_id=evidence_id,
            evidence_type=EvidenceType.SYNTHETIC_RECONSTRUCTION,
            evidence_level=EvidenceLevel.L2,
            direction=direction,
            strength=strength,
        )
        self._records[evidence_id] = record
        return record

    def record_reopening(self, evidence_id: str, *, strength: float | None = None) -> EvidenceRecord:
        record = EvidenceRecord(
            evidence_id=evidence_id,
            evidence_type=EvidenceType.RESIDUAL_REOPENING,
            evidence_level=EvidenceLevel.L2,
            direction="support",
            strength=strength,
        )
        self._records[evidence_id] = record
        return record

    def get(self, evidence_id: str) -> EvidenceRecord:
        return self._records[evidence_id]


@dataclass(slots=True)
class ClaimRecord:
    claim_id: str
    required_level: str
    status: str = "open"
    evidence_refs: list[str] = field(default_factory=list)
    counter_evidence_refs: list[str] = field(default_factory=list)


class ClaimRegistry:
    def __init__(self) -> None:
        self._claims: dict[str, ClaimRecord] = {}

    def register(self, claim_id: str, *, required_level: str) -> ClaimRecord:
        record = ClaimRecord(claim_id, required_level)
        self._claims[claim_id] = record
        return record

    def attach_evidence(self, claim_id: str, evidence: EvidenceRecord) -> None:
        claim = self._claims[claim_id]
        if evidence.direction == "counter":
            if evidence.evidence_id not in claim.counter_evidence_refs:
                claim.counter_evidence_refs.append(evidence.evidence_id)
        else:
            if evidence.evidence_id not in claim.evidence_refs:
                claim.evidence_refs.append(evidence.evidence_id)
        if claim.evidence_refs and claim.counter_evidence_refs:
            claim.status = "disputed"
        elif claim.evidence_refs:
            claim.status = "supported"

    def get(self, claim_id: str) -> ClaimRecord:
        return self._claims[claim_id]


@dataclass(slots=True)
class ResearchRun:
    run_id: str
    benchmark_id: str
    seed: int
    fixture_id: str
    status: str
    passed: bool
    world_result: WorldSolveResult
    metrics: dict[str, float]
    evidence_records: list[EvidenceRecord]
    runtime_observation_metadata: dict[str, Any]
    metadata_leak_detected: bool


@dataclass(slots=True)
class ReopeningResult:
    observation_id: str
    old_residual: np.ndarray
    new_residual: np.ndarray
    reopening_gain: float
    evidence_record: EvidenceRecord


@dataclass(slots=True)
class ResearchCIReport:
    results: dict[str, bool]

    @property
    def all_pass(self) -> bool:
        return all(self.results.values())


class ResearchHarness:
    def __init__(self, generator: FixtureGenerator | None = None) -> None:
        self.generator = generator or FixtureGenerator.reference()
        self.benchmarks = BenchmarkRegistry.seed()
        self.engine = WorldSolveEngine.reference()
        self.evidence = EvidenceLedger()
        self.claims = ClaimRegistry()

    @classmethod
    def reference(cls, generator: FixtureGenerator | None = None) -> "ResearchHarness":
        return cls(generator)

    def run_benchmark(self, benchmark_id: str, *, seed: int) -> ResearchRun:
        case = self.benchmarks.get(benchmark_id)
        fixture = self.generator.generate(case.fixture_family, seed=seed)
        return self.run_fixture(fixture, hidden_label=False, benchmark=case)

    def run_fixture(self, fixture: FixtureArtifact, *, hidden_label: bool, benchmark: BenchmarkCase | None = None) -> ResearchRun:
        runtime_metadata = dict(fixture.metadata)
        # Private labels are never runtime inputs.  Hidden-label mode additionally
        # strips common filename/source/class/text hints so the analysis has to
        # operate on the observation rather than metadata leakage.
        runtime_metadata.pop("private_label", None)
        if hidden_label:
            for key in _HIDDEN_LABEL_KEYS:
                runtime_metadata.pop(key, None)
        metadata_leak = bool(_HIDDEN_LABEL_KEYS.intersection(runtime_metadata)) if hidden_label else "private_label" in runtime_metadata

        observation = SignalObservation(
            observation_id=fixture.fixture_id,
            waveform=fixture.waveform,
            sample_rate_hz=fixture.sample_rate_hz,
            metadata=runtime_metadata,
        )
        world = self.engine.solve(observation)
        metrics = self._metrics(fixture, world, benchmark)
        benchmark_id = benchmark.benchmark_id if benchmark is not None else "adhoc-hidden-label"
        passed = self._passes(benchmark, fixture, world, metrics) if benchmark is not None else not metadata_leak
        evidence = self.evidence.record_synthetic(
            f"ev-{benchmark_id}-{fixture.seed}",
            direction="support" if passed else "counter",
            strength=max(0.0, min(1.0, 1.0 - metrics["waveform_nrmse"])),
        )
        return ResearchRun(
            run_id=f"run-{benchmark_id}-{fixture.seed}",
            benchmark_id=benchmark_id,
            seed=fixture.seed,
            fixture_id=fixture.fixture_id,
            status="completed",
            passed=passed,
            world_result=world,
            metrics=metrics,
            evidence_records=[evidence],
            runtime_observation_metadata=runtime_metadata,
            metadata_leak_detected=metadata_leak,
        )

    def reopen_with_reference_solver(self, initial: ResearchRun) -> ReopeningResult:
        """Reopen an unresolved synthetic residual with an explicit oracle fixture solver.

        This is a controlled L2 lineage/reopening reference, not a general sound
        solver.  The reference solver deliberately models the preserved residual
        exactly so the benchmark can test identity/evidence/reopen semantics.
        """
        old_residual = np.asarray(initial.world_result.residual, dtype=float).copy()
        old_norm = float(np.linalg.norm(old_residual))
        if old_norm <= 0.0:
            raise ValueError("reopening reference requires a non-zero preserved residual")
        new_residual = np.zeros_like(old_residual)
        new_norm = float(np.linalg.norm(new_residual))
        gain = old_norm - new_norm
        evidence = self.evidence.record_reopening(
            f"ev-reopen-{initial.run_id}",
            strength=1.0 if gain > 0.0 else 0.0,
        )
        return ReopeningResult(
            observation_id=initial.world_result.observation_id,
            old_residual=old_residual,
            new_residual=new_residual,
            reopening_gain=gain,
            evidence_record=evidence,
        )

    def _metrics(self, fixture: FixtureArtifact, world: WorldSolveResult, benchmark: BenchmarkCase | None) -> dict[str, float]:
        metrics: dict[str, float] = {
            "waveform_nrmse": waveform_nrmse(fixture.waveform, world.model_reconstruction),
            "residual_structure": float(world.residual_descriptors.get("mean_square_energy", 0.0)),
            "reopening_gain": 0.0,
        }
        truth_f0 = fixture.ground_truth.get("f0_hz")
        metrics["f0_error_hz"] = (
            abs(float(world.farhp_frame.f0_hz) - float(truth_f0))
            if truth_f0 is not None and world.farhp_frame is not None
            else 0.0
        )
        truth_farhp = fixture.ground_truth.get("farhp_rad")
        metrics["farhp_circular_error_rad"] = (
            farhp_circular_error(truth_farhp, list(world.farhp_frame.farhp_rad))
            if truth_farhp is not None and world.farhp_frame is not None
            else 0.0
        )
        farhp_state = world.routing.method_states.get("farhp", "not_applicable")
        expect_no_high = benchmark is not None and benchmark.expected_behavior in {
            "farhp_not_applicable",
            "abstain_and_expand",
            "no_high_confidence_farhp",
        }
        metrics["false_certainty_rate"] = 1.0 if expect_no_high and farhp_state == "applicable" else 0.0
        metrics["false_activation_rate"] = 1.0 if benchmark is not None and benchmark.expected_behavior == "farhp_not_applicable" and "farhp" in world.routing.selected_methods else 0.0
        return metrics

    def _passes(self, case: BenchmarkCase, fixture: FixtureArtifact, world: WorldSolveResult, metrics: dict[str, float]) -> bool:
        behavior = case.expected_behavior
        if behavior == "farhp_committed":
            return world.status == "committed" and "farhp" in world.routing.selected_methods and world.farhp_frame is not None
        if behavior == "layered_committed":
            required = {"harmonic"}
            if "N" in fixture.family:
                required.add("noise")
            if "T" in fixture.family:
                required.add("transient")
            return world.status == "committed" and required.issubset(world.components)
        if behavior == "farhp_not_applicable":
            return world.routing.method_states.get("farhp") in {"not_applicable", "abstain"} and metrics["false_activation_rate"] == 0.0
        if behavior == "abstain_and_expand":
            return world.status == "abstained" and world.domain_expansion_requested and metrics["false_certainty_rate"] == 0.0
        if behavior == "no_high_confidence_farhp":
            return world.routing.method_states.get("farhp") in {"not_applicable", "abstain", "weakly_applicable"} and metrics["false_certainty_rate"] == 0.0
        return False

    def export_replay_bundle(self, run: ResearchRun) -> dict[str, Any]:
        return {
            "bundle_version": "opensound-replay-0.1",
            "benchmark_id": run.benchmark_id,
            "seed": run.seed,
            "fixture_id": run.fixture_id,
            "metrics": dict(run.metrics),
            "world_status": run.world_result.status,
        }

    def replay(self, bundle: dict[str, Any]) -> ResearchRun:
        if bundle.get("bundle_version") != "opensound-replay-0.1":
            raise ValueError("unsupported replay bundle version")
        run = self.run_benchmark(str(bundle["benchmark_id"]), seed=int(bundle["seed"]))
        if run.fixture_id != bundle.get("fixture_id"):
            raise ValueError("fixture identity mismatch during replay")
        return run


class ResearchCI:
    def __init__(self, harness: ResearchHarness) -> None:
        self.harness = harness

    def run_reference_matrix(self, *, seed: int) -> ResearchCIReport:
        results: dict[str, bool] = {}
        for index, benchmark_id in enumerate(sorted(self.harness.benchmarks.ids())):
            run = self.harness.run_benchmark(benchmark_id, seed=seed + index)
            results[benchmark_id] = bool(run.passed)
        return ResearchCIReport(results)
