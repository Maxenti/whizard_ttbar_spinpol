# Framework test report

**Package:** `whizard_ttbar_spinpol_qis_framework_v1`  
**Date:** 2026-07-13  
**Input bundle:** `whizard_qis_framework_input_20260713T192235Z.tar.gz`

## Input/environment audit

The supplied bundle was used as the integration source of truth. It contained the current WHIZARD production repository, accepted production manifests and validation products, normalization records, and eight merged 200-event LHE fixtures.

Detected lxplus/Key4HEP capabilities included WHIZARD 3.1.5, PYTHIA8 8.315, HepMC3 3.3.1, ROOT 6.38, FastJet 3.5, Python 3.13, NumPy, SciPy, Pandas, Uproot, Awkward, Vector, pyhepmc, and PyArrow.

## Automated checks completed in the build container

### Python tests

```text
25 passed
```

Coverage includes:

- four-vector boosts and invariants;
- spin-basis orthonormality and handedness;
- LHE parsing and ancestry for all eight supplied sample configurations;
- density-matrix coefficient round trips;
- physical projection and bounded physical fitting;
- Bell singlet, product, maximally mixed, and Werner-style state checks;
- concurrence, negativity, CHSH, entropy, and purity;
- bootstrap reproducibility;
- parametric detector-response determinism;
- unfolding closure for an identity response;
- longitudinal and transverse beam-density contracts;
- cross-section-weighted helicity mixtures;
- optimized correlation bases;
- polynomial EFT reweighting.

### Python packaging

A PEP 517 wheel was built successfully:

```text
whizard_ttbar_qis-1.0.0-py3-none-any.whl
```

### CMake

The project configured and built successfully with the external shower component disabled:

```text
cmake -S . -B <build> -DQIS_BUILD_SHOWER=OFF
cmake --build <build>
```

This validates the CMake project structure independently of external PYTHIA8/HepMC3 availability.

### Shell and Python syntax

- Every shell script under `scripts/` passed `bash -n`.
- Every Python module under `qis_ttbar/`, `scripts/qis/`, `scripts/showering/`, and `scripts/production/` passed compilation.

### WHIZARD template validation

Both template matrices passed static generation validation:

```text
8 spin-correlated ISR templates
8 isotropic-control ISR templates
```


### Release-manifest audit

The release-manifest builder was exercised against all eight supplied LHE fixtures in strict mode. It produced eight rows with existing-file status, byte size, and 64-character SHA-256 digests.

### End-to-end Python smoke workflow

Using all eight supplied LHE fixtures:

- generated eight 25-event QIS CSV ntuples;
- performed inclusive tomography with bootstrap covariance and physical fitting;
- ran Level B detector smearing and dilepton reconstruction;
- ran Level C CP and optimized-basis summaries;
- passed all 11 synthetic framework validation checks.

```text
E2E PASS ntuples=8 tomography_events=25 checks=11
```

## C++ PYTHIA8/HepMC3 status

The C++ shower source was audited against the current PYTHIA8/HepMC3 interface and corrected to use `HepMC3::Pythia8ToHepMC3`. The generic build container does not mount the supplied CERN CVMFS/Key4HEP C++ stack, so the external-library executable was not linked or run here.

A complete lxplus acceptance test is included:

```bash
source setup_lxplus.sh
./scripts/qis/validate_lxplus_install.sh
```

That script:

1. configures and builds the C++ executable against the active Key4HEP stack;
2. showers a small LHE fixture;
3. verifies HepMC3 event counts and metadata;
4. reruns the mathematical QIS validation.

The lxplus acceptance test is the remaining environment-specific gate before full PYTHIA8 production submission.

## Implementation size

Final framework source content:

```text
Python implementation:  3,330 lines
C++ implementation:        378 lines
Python tests:                201 lines
QIS documentation:           858 lines
```

The package also retains the validated WHIZARD production workflow and the eight small LHE regression fixtures.

## Known external-input boundaries

The software interfaces are implemented, but several physics products necessarily require external inputs:

- a real detector/full-simulation response for detector-specific Level B claims;
- direct WHIZARD generation for coherent transverse polarization;
- supplied EFT matrix-element coefficients or event weights;
- supplied NLO/differential correction maps;
- machine-specific luminosity spectra and beam backgrounds;
- dedicated off-shell/resummed samples for threshold precision.

The framework validates and propagates these inputs without silently inventing them.
