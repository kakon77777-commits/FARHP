# Open Sound MVP v0.1 — P2 Research Harness Status

**Branch:** `integration/open-sound-mvp-v0.1`  
**Base:** `main@9c3c12be7aefe7fd7f905a5cb021ff65d2a01687`  
**Primary P2 implementation commit:** `a017cee129af10f61808ee38995ceec32ce5b172`  
**Evidence ceiling:** L2  

## Status

`P2 = COMPLETE` for the reference MVP scope.

## Implemented

- versioned seed Benchmark Registry;
- deterministic fixture generator;
- reference cases: H, H+N, H+T, H+N+T, noise-only, transient-only, unsupported, artifact stress;
- stable fixture identities from generator/version/config/seed identity;
- Metric Registry;
- waveform NRMSE;
- F0 error;
- FARHP circular error;
- false-certainty rate;
- false-activation rate;
- residual structure metric;
- reopening-gain metric slot;
- hidden-label metadata isolation;
- L2 synthetic Evidence Ledger;
- Claim Registry with support and counter-evidence preservation;
- replay bundle and deterministic replay;
- Research CI reference matrix.

## Epistemic gates

- correct abstention on unsupported observations is benchmark success;
- unsupported observations preserve residual and request domain expansion;
- artifact-stress cases may not be reported as high-confidence FARHP truth;
- every synthetic run emits evidence at L2 or lower;
- counter-evidence is retained and can place a claim in `disputed` state;
- hidden private labels are withheld from runtime metadata.

## Validation evidence

P2 GREEN run `33369919046` passed:

- FARHP: 29/29 PASS;
- Open Sound: 30/30 PASS;
- combined: 59/59 PASS.

The later MVP-closure run `33370340138` preserved the complete P2 suite and added the final negative/runtime gates.

## Not implemented / not claimed

- natural-data acquisition harness beyond architecture;
- real human-study execution;
- external replication execution;
- large source-separation benchmark;
- SOTA neural benchmark suite;
- production-grade benchmark governance service.
