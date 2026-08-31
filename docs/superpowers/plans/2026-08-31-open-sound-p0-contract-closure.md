# Open Sound P0 Contract Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the FARHP/Open Sound P0 contract blockers without rewriting FARHP-Core v0.3: reconcile existing FARHP specs, add semantic validation, define the minimal Open Sound canonical contract, and provide a FARHP adapter.

**Architecture:** Keep `farhp/core` as the existing FARHP reference implementation and add P0 validation there for legacy spec parity. Add a separate root `opensound/` Python reference package for universal observation/evidence contracts, so FARHP remains an optional specialist module rather than becoming the universal object. Duplicate FARHP spec trees remain byte-equivalent after reconciliation.

**Tech Stack:** Python 3.10+, unittest, PyYAML, jsonschema Draft 2020-12.

**Spec:** `FARHP_Open_Sound_Series_Synthesis_and_Canonical_Engineering_Handoff_v0.1.md` / WP-01 canonical contract as supplied in the project handoff.

## Global Constraints

- Do not rewrite FARHP-Core v0.3.
- Preserve FARHP-Y / FARHP-G distinction; G requires declared inverse filtering and is never physiological ground truth.
- `unknown`, `missing`, `not_applicable`, and `abstain` remain distinct.
- Model-only reconstruction may not reference preserved raw residual.
- Synthetic/engineering evidence ceiling is L2.
- Keep `farhp/specs/` and `farhp/core/spec/` semantically and byte-wise aligned for the six canonical spec files.
- Use `https://unboundedaxiom.org/spec/farhp/...` for reconciled FARHP schema IDs.
- No WebLab/UI/deployment changes.

---

### Task 1: Add RED contract tests and CI

**Files:**
- Create: `.github/workflows/open-sound-p0.yml`
- Create: `farhp/core/tests/test_spec_contracts.py`
- Create: `opensound/tests/test_contracts.py`

**Interfaces:**
- Consumes: existing FARHP YAML/JSON schemas.
- Produces: executable P0 acceptance tests for parity, namespace, semantic statuses, evidence ceiling, lineage, and FARHP adapter behavior.

- [ ] Write tests that assert Trajectory YAML required fields match JSON Schema required fields.
- [ ] Assert Trajectory/Transform schema `$id` values use the FARHP unboundedaxiom namespace.
- [ ] Assert Transform YAML declares the report object actually validated by the JSON Schema and includes metadata.
- [ ] Assert FARHP YAML explicitly requires `inverse_filter` for domain G.
- [ ] Assert duplicate FARHP spec trees are byte-identical.
- [ ] Add Open Sound tests for status/value consistency, model-only residual prohibition, evidence-level/type consistency, lineage cycles, and G-domain adapter behavior.
- [ ] Run CI and confirm RED failures are caused by the missing P0 behavior.

### Task 2: Reconcile FARHP specs

**Files:**
- Modify: `farhp/specs/FARHP_Spec_v0.1.yaml`
- Modify: `farhp/specs/FARHP_Trajectory_Spec_v0.2.yaml`
- Modify: `farhp/specs/FARHP_Trajectory_Spec_v0.2.schema.json`
- Modify: `farhp/specs/FARHP_Transform_Spec_v0.3.yaml`
- Modify: `farhp/specs/FARHP_Transform_Spec_v0.3.schema.json`
- Mirror same content under: `farhp/core/spec/`

**Interfaces:**
- Produces: one canonical meaning per spec pair and consistent namespace.

- [ ] Add `method`, `method_version`, and `metadata` to Trajectory YAML required top-level fields.
- [ ] Change Trajectory `$id` to `https://unboundedaxiom.org/spec/farhp/trajectory/0.2/schema.json`.
- [ ] Clarify Transform YAML as a transform specification plus a canonical `transform_report` object; require report metadata.
- [ ] Change Transform `$id` to `https://unboundedaxiom.org/spec/farhp/transform/0.3/report.schema.json`.
- [ ] Add explicit FARHP YAML G-domain requirement for `inverse_filter`.
- [ ] Mirror the six canonical files into `farhp/core/spec/` exactly.

### Task 3: Add FARHP semantic validators

**Files:**
- Modify: `farhp/core/src/farhp/schema.py`
- Modify: `farhp/core/tests/test_spec_contracts.py`

**Interfaces:**
- Produces: `validate_trajectory_semantics(obj) -> list[str]`, `validate_farhp_semantics(obj) -> list[str]`, and `validate_transform_report_semantics(obj) -> list[str]`.

- [ ] Test unequal trajectory array lengths fail semantic validation.
- [ ] Test G-domain without inverse filter fails semantic validation.
- [ ] Test transform report metadata/status contract.
- [ ] Implement only the minimal semantic checks required by those tests.

### Task 4: Add Open Sound P0 common contract package

**Files:**
- Create: `opensound/pyproject.toml`
- Create: `opensound/src/opensound/__init__.py`
- Create: `opensound/src/opensound/contracts.py`
- Create: `opensound/src/opensound/validation.py`
- Create: `opensound/src/opensound/farhp_adapter.py`
- Create: `opensound/tests/test_contracts.py`

**Interfaces:**
- Produces: explicit value states, minimal Observation/Analysis/Hypothesis/Reconstruction/Residual/Evidence/Revision/Manifest dataclasses, semantic validation helpers, and FARHP spec-object adapter.

- [ ] Add RED tests for explicit status/value semantics.
- [ ] Implement enums/dataclasses with JSON-safe `to_dict()` output.
- [ ] Add evidence level/type ceiling validation: synthetic evidence cannot claim L4–L7; human evidence requires L5+.
- [ ] Add reconstruction validation prohibiting raw residual use in `model_only`.
- [ ] Add revision-lineage cycle detection.
- [ ] Add FARHP adapter that preserves existing FARHP spec objects and requires inverse filtering for G.

### Task 5: Close P0 documentation and regression evidence

**Files:**
- Create: `opensound/README.md`
- Create: `opensound/docs/P0_STATUS.md`

**Interfaces:**
- Produces: P0 usage boundaries, exact validation commands, and evidence ceiling.

- [ ] Run FARHP core full unittest suite.
- [ ] Run Open Sound P0 unittest suite.
- [ ] Confirm duplicate spec parity tests pass.
- [ ] Record exact branch/head, tests, limitations, and `P0 = COMPLETE` only if all gates pass.
- [ ] Do not begin P1 in this change.
