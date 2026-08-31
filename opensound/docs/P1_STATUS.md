# Open Sound MVP v0.1 — P1 Deterministic Runtime Status

**Status:** COMPLETE  
**Branch:** `integration/open-sound-mvp-v0.1`  
**Base:** `main@9c3c12be7aefe7fd7f905a5cb021ff65d2a01687`  
**Evidence ceiling:** L2 controlled reference behavior.

## Implemented

- seed Region Registry and Method Registry;
- deterministic signal characterization and routing;
- FARHP runtime adapter using existing FARHP-Core;
- basic deterministic noise and transient modules;
- residual structure analyzer;
- circular / toroidal geometry helpers;
- additive H+N+T model-only reference reconstruction;
- witness reconstruction separated from model-only reconstruction;
- residual preservation;
- explicit `DomainExpansionRequest` for unsupported observations;
- explicit transient-detector → FARHP `transient_cleaned_waveform` coupling port and `port_exchange` ledger event;
- two-source conflict branches with explicit metadata rather than fake single-FARHP certainty;
- executable `farhp_only`, `noise_only`, and `transient_only` invariants;
- checkpoint / rollback through deterministic replay;
- fail-closed module exceptions with residual preservation;
- runtime event ledger and deterministic replay identity.

## Required reference behavior

- pure harmonic → FARHP applicable / committed;
- noise-only → FARHP not applicable;
- transient-only → FARHP not applicable or abstain;
- H+N+T → harmonic + noise + transient components with model-only residual;
- unsupported → abstain + preserved residual + explicit expansion request;
- competing F0 candidates → branch, no fake single-FARHP frame.

## TDD evidence

- RED: run `33369359165` kept P0 green and failed because P1 runtime modules did not yet exist.
- GREEN: run `33369621144` → FARHP **29/29**, Open Sound **20/20**, combined **49/49 PASS**.
- Runtime closure: run `33370340138` → combined **70/70 PASS** after invariant/ledger/rollback/fail-closed gates.
- Final acceptance RED: run `33370721048` exposed four missing acceptance semantics without regressing prior behavior.
- Final acceptance GREEN: run `33376344538` → FARHP **29/29**, Open Sound **45/45**, combined **74/74 PASS**.

## Boundary

This remains a small deterministic reference runtime. It is not complete source separation, natural validation, a production audio engine, or a universal learned router.
