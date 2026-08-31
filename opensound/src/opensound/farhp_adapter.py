from __future__ import annotations

from typing import Any
from uuid import uuid4

from .contracts import AnalysisAttempt


def adapt_farhp_spec_object(obj: dict[str, Any]) -> AnalysisAttempt:
    domain = obj.get("domain")
    if domain == "G" and not isinstance(obj.get("inverse_filter"), dict):
        raise ValueError("FARHP domain G requires declared inverse_filter provenance")
    analysis = obj.get("analysis")
    if not isinstance(analysis, dict):
        raise ValueError("FARHP object requires analysis metadata")
    phase = obj.get("phase") if isinstance(obj.get("phase"), dict) else {}
    grade = analysis.get("applicability_grade")
    status = "completed"
    if phase.get("representation") == "not_applicable" or grade == 0:
        status = "not_applicable"
    return AnalysisAttempt(
        analysis_id=f"ana-farhp-{uuid4().hex}",
        method_id=str(analysis.get("method", "farhp")),
        method_version=str(analysis.get("method_version", obj.get("farhp_version", "0.1"))),
        status=status,
        outputs={"farhp": obj},
        provenance=dict(obj.get("provenance", {})),
    )
