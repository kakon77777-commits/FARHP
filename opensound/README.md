# FARHP Open Sound — Reference MVP v0.1

This directory contains the small, deterministic, auditable reference MVP for FARHP Open Sound. It extends the existing FARHP repository without replacing FARHP-Core v0.3.

## Canonical scope

```text
Observation
→ Region / applicability
→ deterministic routing
→ FARHP / noise / transient modules
→ model-only reconstruction
→ residual
→ evidence / benchmark
→ commit / abstain / branch / reopen
```

FARHP remains the harmonic-relative-phase specialist. A valid Open Sound observation does not require a class label, an F0 estimate, or a FARHP representation.

## Explicit semantic states

- availability: `available / missing / not_applicable`
- inference: `resolved / unknown / abstain`
- applicability: `applicable / weakly_applicable / not_applicable / abstain`

These states must not collapse into an ambiguous `null`.

## Reference MVP contents

### P0 — Contract closure

- reconciled FARHP trajectory / transform / G-domain semantics;
- canonical Open Sound schemas and dataclasses;
- semantic validators;
- FARHP legacy adapter;
- minimal reusable contract fixtures.

### P1 — Deterministic runtime

- seed Region and Method registries;
- deterministic router;
- FARHP, basic noise, basic transient, and residual modules;
- circular / toroidal geometry support;
- model-only vs witness reconstruction separation;
- invariant engine;
- explicit branches;
- checkpoint / rollback replay;
- fail-closed module error handling;
- runtime ledger.

### P2 — Research harness

- versioned benchmark registry;
- deterministic fixture generator;
- metric registry;
- hidden-label execution;
- L2 synthetic evidence ledger;
- claim registry with counter-evidence;
- replay bundles;
- Research CI reference matrix.

## Validation

From repository root:

```bash
python -m pip install -e farhp/core
python -m unittest discover -s farhp/core/tests -v
PYTHONPATH=opensound/src python -m unittest discover -s opensound/tests -v
```

On PowerShell, set `PYTHONPATH` before the second command instead of using the POSIX inline assignment.

## Evidence boundary

The reference MVP evidence ceiling is **L2**. It provides contract, runtime, controlled synthetic reconstruction, routing, abstention, replay, and regression evidence. It does **not** establish natural-sound truth, human perceptual validation, production readiness, or external replication.

## FARHP boundary

- FARHP-Y is the observed output-waveform domain.
- FARHP-G is an estimate produced by explicitly declared inverse filtering and is not physiological ground truth.
- FARHP is not forced onto noise-only, transient-only, unsupported, or conflicting-source observations.

## Current branch

Reference implementation work is isolated on:

```text
integration/open-sound-mvp-v0.1
```

The branch is intentionally not merged into `main` by this handoff.
