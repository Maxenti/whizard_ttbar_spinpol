# Architecture

## Design goals

1. Preserve the accepted WHIZARD production as immutable source data.
2. Keep generation, showering, tomography, detector response, and research extensions separable.
3. Make all sign conventions, basis definitions, normalization choices, and random seeds explicit.
4. Support local smoke tests and scalable HTCondor campaigns with the same executables.
5. Make the full density matrix and covariance the central interface between analysis levels.

## Data flow

```text
WHIZARD final LHE
  -> C++ PYTHIA8 shower
  -> HepMC3 + metadata
  -> Python event extraction
  -> ROOT/Parquet/CSV QIS ntuple
  -> angular-moment estimator
  -> raw rho and covariance
  -> physical rho projection/fit
  -> QIS measures and plots
  -> Level B response/reconstruction/unfolding
  -> Level C EFT/CP/polarization/multi-energy studies
```

## Package layers

### `qis_ttbar.io`

Manifest readers, streaming LHE parser, optional HepMC3 reader, and table serialization. I/O modules do not define spin conventions.

### `qis_ttbar.physics`

Ancestry identification, Lorentz transformations, frame construction, spin axes, and event-level observables. This layer converts event records into convention-controlled analyzer directions.

### `qis_ttbar.tomography`

Moment estimators, density-matrix construction, bootstrap covariance, physical projection, binning, and diagnostics.

### `qis_ttbar.qis`

Functions of a density matrix: entropies, purity, concurrence, negativity, PPT, CHSH, steering, Fisher information, and magic diagnostics.

### `qis_ttbar.level_b`

Detector smearing, acceptance, reconstruction, response matrices, unfolding, and systematic ensembles. The default detector model is parametric and replaceable.

### `qis_ttbar.level_c`

Polarization mixtures, coherent-transverse-polarization contracts, EFT polynomial weights, CP observables, optimized bases, NLO weights, multi-energy combination, and state metrics.

### C++ shower executable

`qis_lhe_to_hepmc3` reads one LHE file, applies controlled PYTHIA8 settings, preserves the WHIZARD hard decay chain, writes HepMC3 through a partial file followed by atomic rename, and records a JSON run summary.

## Configuration contracts

YAML files contain campaign paths and physics choices. CSV production tables define WHIZARD sample matrices. PYTHIA command files hold shower settings. No analysis module should infer a collider scenario from a sample name when the same information is available in a manifest.

## Extensibility

External detector or theory integrations should implement adapters that return the existing table or weight contracts. New observables should consume `rho`, `B+`, `B-`, `C`, and covariance rather than duplicating event parsing.
