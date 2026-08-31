from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

from farhp import schema as schema_module


ROOT = Path(__file__).resolve().parents[1]
CORE_SPEC = ROOT / "spec"
PUBLIC_SPEC = ROOT.parent / "specs"
CANONICAL_FILES = (
    "FARHP_Spec_v0.1.schema.json",
    "FARHP_Spec_v0.1.yaml",
    "FARHP_Trajectory_Spec_v0.2.schema.json",
    "FARHP_Trajectory_Spec_v0.2.yaml",
    "FARHP_Transform_Spec_v0.3.schema.json",
    "FARHP_Transform_Spec_v0.3.yaml",
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


class TestFARHPSpecContracts(unittest.TestCase):
    def test_trajectory_required_fields_match_yaml_and_schema(self) -> None:
        semantic = load_yaml(PUBLIC_SPEC / "FARHP_Trajectory_Spec_v0.2.yaml")
        schema = load_json(PUBLIC_SPEC / "FARHP_Trajectory_Spec_v0.2.schema.json")
        self.assertEqual(set(semantic["required_top_level_fields"]), set(schema["required"]))

    def test_reconciled_schema_ids_use_unboundedaxiom_namespace(self) -> None:
        trajectory = load_json(PUBLIC_SPEC / "FARHP_Trajectory_Spec_v0.2.schema.json")
        transform = load_json(PUBLIC_SPEC / "FARHP_Transform_Spec_v0.3.schema.json")
        self.assertEqual(
            trajectory["$id"],
            "https://unboundedaxiom.org/spec/farhp/trajectory/0.2/schema.json",
        )
        self.assertEqual(
            transform["$id"],
            "https://unboundedaxiom.org/spec/farhp/transform/0.3/report.schema.json",
        )

    def test_transform_yaml_declares_the_report_contract_validated_by_schema(self) -> None:
        semantic = load_yaml(PUBLIC_SPEC / "FARHP_Transform_Spec_v0.3.yaml")
        schema = load_json(PUBLIC_SPEC / "FARHP_Transform_Spec_v0.3.schema.json")
        report = semantic["report"]
        self.assertEqual(report["object_type"], "transform_report")
        self.assertEqual(set(report["fields"]), set(schema["required"]))

    def test_g_domain_explicitly_requires_inverse_filter_in_yaml(self) -> None:
        semantic = load_yaml(PUBLIC_SPEC / "FARHP_Spec_v0.1.yaml")
        self.assertIn("inverse_filter", semantic["domain_rules"]["G"]["required_fields"])

    def test_duplicate_spec_trees_are_byte_identical(self) -> None:
        for name in CANONICAL_FILES:
            self.assertEqual(
                (PUBLIC_SPEC / name).read_bytes(),
                (CORE_SPEC / name).read_bytes(),
                name,
            )

    def test_trajectory_semantic_validator_rejects_mismatched_lengths(self) -> None:
        obj = {
            "frame_times_sec": [0.0, 0.01],
            "f0_hz": [120.0],
            "voiced": [True, True],
            "track_confidence": [1.0, 1.0],
            "frames": [None, None],
            "anchor_unwrapped_rad": [0.0, 0.1],
            "anchor_residual_rad": [0.0, 0.0],
            "farhp_unwrapped_rad": [[], []],
            "phase_velocity_rad_per_sec": [[], []],
        }
        errors = schema_module.validate_trajectory_semantics(obj)
        self.assertTrue(any("length" in error for error in errors))

    def test_farhp_semantic_validator_rejects_g_without_inverse_filter(self) -> None:
        errors = schema_module.validate_farhp_semantics({"domain": "G"})
        self.assertTrue(any("inverse_filter" in error for error in errors))

    def test_transform_report_semantic_validator_requires_metadata(self) -> None:
        report = {
            "operation": "condition:zero",
            "strength": 1.0,
            "changed_coordinates": 1,
            "mean_geodesic_shift_rad": 0.2,
            "max_geodesic_shift_rad": 0.4,
        }
        errors = schema_module.validate_transform_report_semantics(report)
        self.assertTrue(any("metadata" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
