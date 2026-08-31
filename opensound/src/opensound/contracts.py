from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _serialize(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {f.name: _serialize(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, dict):
        return {str(k): _serialize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize(v) for v in value]
    return value


class AvailabilityState(str, Enum):
    AVAILABLE = "available"
    MISSING = "missing"
    NOT_APPLICABLE = "not_applicable"


class InferenceState(str, Enum):
    RESOLVED = "resolved"
    UNKNOWN = "unknown"
    ABSTAIN = "abstain"


class ApplicabilityState(str, Enum):
    APPLICABLE = "applicable"
    WEAKLY_APPLICABLE = "weakly_applicable"
    NOT_APPLICABLE = "not_applicable"
    ABSTAIN = "abstain"


class EvidenceLevel(str, Enum):
    L0 = "L0"
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"
    L5 = "L5"
    L6 = "L6"
    L7 = "L7"


class EvidenceType(str, Enum):
    SCHEMA = "schema"
    UNIT_TEST = "unit_test"
    SYNTHETIC_RECONSTRUCTION = "synthetic_reconstruction"
    SIMULATED_STUDY = "simulated_study"
    NATURAL_RECORDING = "natural_recording"
    HUMAN_PILOT = "human_pilot"
    CONFIRMATORY_STUDY = "confirmatory_study"
    EXTERNAL_REPLICATION = "external_replication"
    ABLATION = "ablation"
    INVARIANT = "invariant"
    RESIDUAL_REOPENING = "residual_reopening"


@dataclass(slots=True)
class ValueRecord:
    availability: AvailabilityState
    inference: InferenceState
    value: Any = None
    unit: str | None = None
    reason: str | None = None
    confidence: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(slots=True)
class ObservationEnvelope:
    observation_id: str
    created_by: str
    schema_version: str = "opensound-observation-0.1"
    created_at: str = field(default_factory=_now)
    native_assets: list[dict[str, Any]] = field(default_factory=list)
    region_refs: list[dict[str, Any]] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)
    analysis_attempt_refs: list[str] = field(default_factory=list)
    hypothesis_refs: list[str] = field(default_factory=list)
    reconstruction_refs: list[str] = field(default_factory=list)
    residual_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    revision_refs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = _serialize(self)
        payload["object_type"] = "observation"
        return payload


@dataclass(slots=True)
class AnalysisAttempt:
    analysis_id: str
    method_id: str
    method_version: str
    status: str
    outputs: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)
    schema_version: str = "opensound-analysis-0.1"

    def to_dict(self) -> dict[str, Any]:
        payload = _serialize(self)
        payload["object_type"] = "analysis_attempt"
        return payload


@dataclass(slots=True)
class HypothesisRecord:
    hypothesis_id: str
    observation_ref: str
    status: str = "open"
    model_components: list[dict[str, Any]] = field(default_factory=list)
    evidence_level: EvidenceLevel = EvidenceLevel.L0
    schema_version: str = "opensound-hypothesis-0.1"

    def to_dict(self) -> dict[str, Any]:
        payload = _serialize(self)
        payload["object_type"] = "hypothesis"
        return payload


@dataclass(slots=True)
class ReconstructionRecord:
    reconstruction_id: str
    reconstruction_type: str
    uses_preserved_residual: bool = False
    residual_ref: str | None = None
    components: list[dict[str, Any]] = field(default_factory=list)
    schema_version: str = "opensound-reconstruction-0.1"

    def to_dict(self) -> dict[str, Any]:
        payload = _serialize(self)
        payload["object_type"] = "reconstruction"
        return payload


@dataclass(slots=True)
class ResidualRecord:
    residual_id: str
    observation_ref: str
    reconstruction_ref: str
    status: str = "unresolved"
    parent_residual_ref: str | None = None
    schema_version: str = "opensound-residual-0.1"

    def to_dict(self) -> dict[str, Any]:
        payload = _serialize(self)
        payload["object_type"] = "residual"
        return payload


@dataclass(slots=True)
class EvidenceRecord:
    evidence_id: str
    evidence_type: EvidenceType
    evidence_level: EvidenceLevel
    direction: str = "neutral"
    strength: float | None = None
    schema_version: str = "opensound-evidence-0.1"

    def to_dict(self) -> dict[str, Any]:
        payload = _serialize(self)
        payload["object_type"] = "evidence"
        return payload


@dataclass(slots=True)
class RevisionRecord:
    revision_id: str
    target_ref: str
    previous_version_ref: str | None
    change_type: str
    schema_version: str = "opensound-revision-0.1"
    created_at: str = field(default_factory=_now)

    def to_dict(self) -> dict[str, Any]:
        payload = _serialize(self)
        payload["object_type"] = "revision"
        return payload


@dataclass(slots=True)
class ArtifactManifest:
    artifact_id: str
    observation_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    revision_refs: list[str] = field(default_factory=list)
    manifest_version: str = "opensound-manifest-0.1"

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)
