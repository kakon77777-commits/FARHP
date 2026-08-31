# FARHP Open Sound — P0 Contract Layer

This directory contains the P0 canonical contract layer for FARHP Open Sound. It does **not** replace FARHP-Core v0.3 and it does not claim general sound reconstruction yet.

## P0 scope

- explicit `available / missing / not_applicable` availability states;
- explicit `resolved / unknown / abstain` inference states;
- canonical Observation, AnalysisAttempt, Hypothesis, Reconstruction, Residual, Evidence, Revision and Manifest schemas;
- FARHP legacy-object adapter;
- FARHP spec parity and semantic validators;
- evidence ceilings that keep engineering/synthetic evidence at L0–L2.

## Core invariant

```text
Observation != Interpretation
```

A valid Open Sound observation does not require a class label, an F0 estimate, or a FARHP representation.

## Validation

From repository root, CI runs:

```bash
python -m pip install -e farhp/core
python -m unittest discover -s farhp/core/tests -v
PYTHONPATH=opensound/src python -m unittest discover -s opensound/tests -v
```

On PowerShell, set `PYTHONPATH` before the second command instead of using the POSIX inline assignment.

## Evidence boundary

P0 is contract and reference-engineering work only. The current evidence ceiling is L2; P0 itself primarily establishes L0/L1 contract evidence. It is not natural-sound, human-perception, production, or external-replication validation.

## FARHP boundary

FARHP remains the harmonic-relative-phase specialist. FARHP-Y is the output-waveform observation domain. FARHP-G remains an estimate produced by explicitly declared inverse filtering and is not physiological ground truth.
