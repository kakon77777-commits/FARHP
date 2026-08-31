from __future__ import annotations

import importlib
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = ROOT / "schemas"
PRIMARY_SCHEMAS = (
    "OpenSound_Observation_v0.1.schema.json",
    "OpenSound_AnalysisAttempt_v0.1.schema.json",
    "OpenSound_Hypothesis_v0.1.schema.json",
    "OpenSound_Reconstruction_v0.1.schema.json",
    "OpenSound_Residual_v0.1.schema.json",
    "OpenSound_Evidence_v0.1.schema.json",
    "OpenSound_Revision_v0.1.schema.json",
    "OpenSound_Manifest_v0.1.schema.json",
)


class TestOpenSoundContracts(unittest.TestCase):
    def contracts(self):
        return importlib.import_module("opensound.contracts")

    def validation(self):
        return importlib.import_module("opensound.validation")

    def adapter(self):
        return importlib.import_module("opensound.farhp_adapter")

    def test_primary_schemas_exist_and_are_valid_draft_2020_12(self) -> None:
        for name in PRIMARY_SCHEMAS:
            path = SCHEMA_ROOT / name
            self.assertTrue(path.exists(), name)
            schema = json.loads(path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
            self.assertTrue(schema["$id"].startswith("https://unboundedaxiom.org/spec/opensound/0.1/"))

    def test_not_applicable_value_cannot_carry_numeric_value(self) -> None:
        c = self.contracts()
        v = self.validation()
        record = c.ValueRecord(
            availability=c.AvailabilityState.NOT_APPLICABLE,
            inference=c.InferenceState.RESOLVED,
            value=0.0,
            reason="broadband_noise_component",
        )
        errors = v.validate_value_record(record)
        self.assertTrue(any("not_applicable" in error for error in errors))

    def test_abstain_value_cannot_carry_estimate(self) -> None:
        c = self.contracts()
        v = self.validation()
        record = c.ValueRecord(
            availability=c.AvailabilityState.AVAILABLE,
            inference=c.InferenceState.ABSTAIN,
            value=220.0,
            reason="competing_fundamentals",
        )
        errors = v.validate_value_record(record)
        self.assertTrue(any("abstain" in error for error in errors))

    def test_model_only_reconstruction_cannot_use_preserved_residual(self) -> None:
        c = self.contracts()
        v = self.validation()
        record = c.ReconstructionRecord(
            reconstruction_id="rec-001",
            reconstruction_type="model_only",
            uses_preserved_residual=True,
            residual_ref="res-001",
        )
        errors = v.validate_reconstruction_record(record)
        self.assertTrue(any("model_only" in error for error in errors))

    def test_synthetic_evidence_cannot_claim_natural_or_human_level(self) -> None:
        c = self.contracts()
        v = self.validation()
        errors = v.validate_evidence_level(c.EvidenceType.SYNTHETIC_RECONSTRUCTION, c.EvidenceLevel.L5)
        self.assertTrue(any("L2" in error for error in errors))

    def test_human_pilot_requires_l5_or_higher(self) -> None:
        c = self.contracts()
        v = self.validation()
        errors = v.validate_evidence_level(c.EvidenceType.HUMAN_PILOT, c.EvidenceLevel.L4)
        self.assertTrue(any("L5" in error for error in errors))

    def test_revision_lineage_cycle_is_rejected(self) -> None:
        c = self.contracts()
        v = self.validation()
        revisions = [
            c.RevisionRecord("rev-a", "hyp-a", "rev-b", "status_change"),
            c.RevisionRecord("rev-b", "hyp-a", "rev-a", "status_change"),
        ]
        errors = v.validate_revision_lineage(revisions)
        self.assertTrue(any("cycle" in error for error in errors))

    def test_farhp_g_adapter_requires_inverse_filter(self) -> None:
        a = self.adapter()
        obj = {
            "farhp_version": "0.1",
            "domain": "G",
            "analysis": {"method": "x", "method_version": "1"},
            "phase": {"representation": "not_applicable", "harmonic_indices": [], "mask": [], "confidence": []},
            "anchor": {"type": "fundamental", "confidence": 0.5},
            "polarity_policy": "preserve",
        }
        with self.assertRaises(ValueError):
            a.adapt_farhp_spec_object(obj)

    def test_minimal_unknown_observation_serializes_without_label_or_f0(self) -> None:
        c = self.contracts()
        obs = c.ObservationEnvelope(observation_id="obs-001", created_by="test")
        payload = obs.to_dict()
        self.assertNotIn("class_label", payload)
        self.assertNotIn("f0_hz", payload)
        self.assertEqual(payload["observation_id"], "obs-001")


if __name__ == "__main__":
    unittest.main()
