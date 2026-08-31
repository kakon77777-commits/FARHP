from __future__ import annotations

from .contracts import (
    AvailabilityState,
    EvidenceLevel,
    EvidenceType,
    InferenceState,
    ReconstructionRecord,
    RevisionRecord,
    ValueRecord,
)


def validate_value_record(record: ValueRecord) -> list[str]:
    errors: list[str] = []
    if record.availability == AvailabilityState.NOT_APPLICABLE and record.value is not None:
        errors.append("not_applicable value must not carry a numeric or semantic value")
    if record.availability == AvailabilityState.MISSING and record.value is not None:
        errors.append("missing value must not carry a value")
    if record.inference == InferenceState.ABSTAIN and record.value is not None:
        errors.append("abstain inference must not carry an estimate")
    if record.inference in {InferenceState.UNKNOWN, InferenceState.ABSTAIN} and not record.reason:
        errors.append(f"{record.inference.value} inference requires a reason")
    return errors


def validate_reconstruction_record(record: ReconstructionRecord) -> list[str]:
    errors: list[str] = []
    if record.reconstruction_type == "model_only" and (
        record.uses_preserved_residual or record.residual_ref is not None
    ):
        errors.append("model_only reconstruction cannot use preserved raw residual")
    if record.reconstruction_type == "witness" and record.uses_preserved_residual and not record.residual_ref:
        errors.append("witness reconstruction using preserved residual requires residual_ref")
    return errors


def _level_number(level: EvidenceLevel) -> int:
    return int(level.value[1:])


def validate_evidence_level(evidence_type: EvidenceType, level: EvidenceLevel) -> list[str]:
    n = _level_number(level)
    if evidence_type in {EvidenceType.SCHEMA, EvidenceType.UNIT_TEST} and n > 1:
        return [f"{evidence_type.value} evidence ceiling is L1"]
    if evidence_type in {
        EvidenceType.SYNTHETIC_RECONSTRUCTION,
        EvidenceType.ABLATION,
        EvidenceType.INVARIANT,
        EvidenceType.RESIDUAL_REOPENING,
    } and n > 2:
        return [f"{evidence_type.value} evidence ceiling is L2"]
    if evidence_type == EvidenceType.SIMULATED_STUDY and n > 3:
        return ["simulated_study evidence ceiling is L3"]
    if evidence_type == EvidenceType.NATURAL_RECORDING and n != 4:
        return ["natural_recording evidence must be L4"]
    if evidence_type == EvidenceType.HUMAN_PILOT and n < 5:
        return ["human_pilot evidence requires L5 or higher"]
    if evidence_type == EvidenceType.CONFIRMATORY_STUDY and n < 6:
        return ["confirmatory_study evidence requires L6 or higher"]
    if evidence_type == EvidenceType.EXTERNAL_REPLICATION and n != 7:
        return ["external_replication evidence must be L7"]
    return []


def validate_revision_lineage(revisions: list[RevisionRecord]) -> list[str]:
    previous = {revision.revision_id: revision.previous_version_ref for revision in revisions}
    for start in previous:
        seen: set[str] = set()
        current: str | None = start
        while current is not None and current in previous:
            if current in seen:
                return [f"revision lineage cycle detected at {current}"]
            seen.add(current)
            current = previous[current]
    return []
