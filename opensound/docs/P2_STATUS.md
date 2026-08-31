# Open Sound MVP v0.1 — P2 Research Harness Status

**Status:** COMPLETE  
**Branch:** `integration/open-sound-mvp-v0.1`  
**Base:** `main@9c3c12be7aefe7fd7f905a5cb021ff65d2a01687`  
**Evidence ceiling:** L2.

## Implemented

- versioned seed Benchmark Registry;
- deterministic fixture generator for H, H+N, H+T, H+N+T, noise-only, transient-only, unsupported, and artifact stress cases;
- stable fixture identities from family/config/seed identity;
- Metric Registry with waveform NRMSE, F0 error, FARHP circular error, false-certainty / false-activation references, residual structure, and reopening gain;
- hidden-label mode stripping private/class/source/filename/directory/text-description hints before runtime;
- L2 synthetic Evidence Ledger;
- Claim Registry retaining support and counter-evidence;
- replay bundles and deterministic replay;
- Research CI reference matrix;
- controlled L2 residual reopening reference experiment preserving old residual and emitting `RESIDUAL_REOPENING` evidence.

## Epistemic gates

- correct abstention on unsupported cases is benchmark success;
- unsupported cases preserve residual and request domain expansion;
- artifact stress cannot become high-confidence FARHP truth;
- synthetic evidence cannot exceed L2;
- negative/counter-evidence is retained;
- hidden-label metadata hints are not runtime inputs.

## TDD evidence

- RED: run `33369719607` kept P0/P1 green and failed because the P2 benchmark module did not yet exist.
- GREEN: run `33369919046` → FARHP **29/29**, Open Sound **30/30**, combined **59/59 PASS**.
- Final acceptance RED: run `33370721048` exposed the missing full hidden-label strip and reopening API along with two runtime acceptance gaps.
- Final acceptance GREEN: run `33376344538` → FARHP **29/29**, Open Sound **45/45**, combined **74/74 PASS**.

## Boundary

P2 does not execute natural-recording validation, real human studies, external replication, production benchmark governance, or SOTA neural/source-separation benchmarking.
