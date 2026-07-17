# PYTHIA8 and HepMC3 configuration

## Purpose

The C++ executable showers accepted WHIZARD LHE files without replacing the WHIZARD top-spin decay chain.

## Default settings

`configs/pythia/level_a.cmnd` establishes:

- external LHE input;
- PYTHIA initial-state shower off because incoming-lepton ISR is already supplied by WHIZARD;
- final-state shower on;
- MPI off for lepton-collider hard events;
- hadronization on;
- unstable hadron decays on;
- process-level resonance decays off;
- top decay disabled in PYTHIA;
- QED final-state radiation configurable;
- event consistency checks on.

## Provenance

Every HepMC3 event receives event attributes for campaign, sample, shard, event index, shower seed, and decay/ISR provenance. Every job writes a JSON summary containing versions, input/output paths, event counts, weights, and generator cross-section metadata.

## Reproducibility

Seeds must be unique by `(campaign, sample, shard)`. Condor submission scripts generate deterministic seed assignments and reject collisions. Output is written to a partial path and renamed only after successful completion.

## Required validation

For each showered sample, validate:

- requested and written event counts;
- finite event weights and momenta;
- top decay ancestry retained;
- no duplicate top or W decay;
- expected stable charged leptons and neutrinos;
- color flow on `b` and `bbar` accepted by PYTHIA;
- PYTHIA initial-state shower disabled;
- metadata and checksums present.

## Systematic variants

Use separate named campaigns for FSR, hadronization, hadron-decay, QED-FSR, tune, and color-reconnection variations. Do not overwrite the nominal shower output.
