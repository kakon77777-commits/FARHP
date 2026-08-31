from __future__ import annotations

import json
import unittest
from pathlib import Path

import numpy as np
from jsonschema import Draft202012Validator
from farhp.synth import synthetic_vowel

from opensound.invariants import InvariantEngine
from opensound.registry import RegionRegistry
from opensound.runtime import SignalObservation, WorldSolveEngine
from opensound.validation import (
    validate_referential_integrity,
    validate_residual_semantics,
    validate_unique_identity,
)


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = ROOT / "schemas"


class ExplodingFARHP:
    def analyze(self, waveform, sample_rate_hz):
        raise RuntimeError("synthetic module failure")

    def synthesize(self, frame, sample_count):
        raise AssertionError("synthesize must not run after analysis failure")


class TestOpenSoundMVPClosure(unittest.TestCase):
    def setUp(self) -> None:
        self.fs = 16000
        self.engine = WorldSolveEngine.reference()

    def harmonic_observation(self, name: str = "closure") -> SignalObservation:
        waveform, _, _ = synthetic_vowel(duration_sec=0.08, sample_rate_hz=self.fs, k_max=10)
        return SignalObservation(f"obs-{name}", waveform, self.fs)

    def test_observation_schema_requires_provenance(self) -> None:
        schema = json.loads((SCHEMA_ROOT / "OpenSound_Observation_v0.1.schema.json").read_text(encoding="utf-8"))
        invalid = {
            "object_type": "observation",
            "schema_version": "opensound-observation-0.1",
            "observation_id": "obs-no-provenance",
            "created_at": "2026-08-31T00:00:00+08:00",
            "created_by": "test",
            "native_assets": [],
            "region_refs": [],
            "analysis_attempt_refs": [],
            "hypothesis_refs": [],
            "reconstruction_refs": [],
            "residual_refs": [],
            "evidence_refs": [],
            "revision_refs": [],
        }
        errors = list(Draft202012Validator(schema).iter_errors(invalid))
        self.assertTrue(any("provenance" in error.message for error in errors))

    def test_candidate_region_is_not_established(self) -> None:
        registry = RegionRegistry.seed()
        self.assertEqual(registry.get("unknown-mechanical").status, "provisional")
        self.assertFalse(registry.is_established("unknown-mechanical"))

    def test_duplicate_identity_with_different_content_is_rejected(self) -> None:
        records = [
            {"id": "same-id", "value": 1},
            {"id": "same-id", "value": 2},
        ]
        errors = validate_unique_identity(records, id_key="id")
        self.assertTrue(any("different content" in error for error in errors))

    def test_broken_references_are_rejected(self) -> None:
        objects = {"obs-1": {"id": "obs-1"}}
        errors = validate_referential_integrity(["obs-1", "missing-id"], objects)
        self.assertTrue(any("missing-id" in error for error in errors))

    def test_residual_cannot_be_silently_declared_noise_without_evidence(self) -> None:
        errors = validate_residual_semantics({"residual_id": "res-1", "type": "noise", "evidence_refs": []})
        self.assertTrue(any("noise" in error for error in errors))

    def test_farhp_only_invariant_detects_nonphase_drift(self) -> None:
        engine = InvariantEngine()
        before = {
            "f0_hz": 120.0,
            "amplitudes": [1.0, 0.5],
            "farhp_rad": [0.0, 0.2],
            "noise_energy": 0.1,
            "transient_energy": 0.2,
        }
        good = dict(before, farhp_rad=[0.0, 1.0])
        bad = dict(good, f0_hz=121.0)
        self.assertTrue(engine.validate("farhp_only", before, good).passed)
        self.assertFalse(engine.validate("farhp_only", before, bad).passed)

    def test_noise_only_and_transient_only_invariants_are_available(self) -> None:
        engine = InvariantEngine()
        base = {
            "f0_hz": 120.0,
            "amplitudes": [1.0, 0.5],
            "farhp_rad": [0.0, 0.2],
            "noise_energy": 0.1,
            "transient_energy": 0.2,
        }
        noise_change = dict(base, noise_energy=0.3)
        transient_change = dict(base, transient_energy=0.5)
        self.assertTrue(engine.validate("noise_only", base, noise_change).passed)
        self.assertTrue(engine.validate("transient_only", base, transient_change).passed)

    def test_world_solve_checkpoint_and_rollback_replay_same_result(self) -> None:
        obs = self.harmonic_observation("rollback")
        result = self.engine.solve(obs)
        checkpoint = self.engine.create_checkpoint(result)
        restored = self.engine.rollback(obs, checkpoint)
        self.assertEqual(result.status, restored.status)
        self.assertEqual(result.routing.to_dict(), restored.routing.to_dict())
        np.testing.assert_allclose(result.model_reconstruction, restored.model_reconstruction, atol=0.0)

    def test_two_source_branch_contains_explicit_branch_metadata(self) -> None:
        n = int(0.08 * self.fs)
        t = np.arange(n, dtype=float) / self.fs
        waveform = np.sin(2 * np.pi * 120 * t) + 0.9 * np.sin(2 * np.pi * 190 * t + 0.2)
        obs = SignalObservation("obs-branch", waveform, self.fs, {"f0_candidates_hz": [120.0, 190.0]})
        result = self.engine.solve(obs)
        self.assertEqual(result.status, "branched")
        self.assertGreaterEqual(len(result.branches), 2)
        self.assertEqual({branch["f0_hz"] for branch in result.branches}, {120.0, 190.0})

    def test_runtime_ledger_records_route_residual_and_terminal_state(self) -> None:
        result = self.engine.solve(self.harmonic_observation("ledger"))
        event_types = [event["event_type"] for event in result.ledger_events]
        self.assertIn("route", event_types)
        self.assertIn("reconstruct", event_types)
        self.assertIn("residual", event_types)
        self.assertIn(result.status, {"committed", "abstained", "branched", "failed"})
        self.assertEqual(event_types[-1], result.status)

    def test_runtime_module_exception_fails_closed_and_preserves_residual(self) -> None:
        obs = self.harmonic_observation("fail-closed")
        self.engine.farhp = ExplodingFARHP()
        result = self.engine.solve(obs)
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.components, {})
        np.testing.assert_allclose(result.residual, obs.waveform, atol=0.0)
        self.assertTrue(any(event["event_type"] == "module_fail" for event in result.ledger_events))


if __name__ == "__main__":
    unittest.main()
