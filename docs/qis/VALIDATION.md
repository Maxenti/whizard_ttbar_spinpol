# Validation strategy

## Mathematical unit tests

The test suite includes:

- four-vector invariance and boost closure;
- basis orthonormality and handedness;
- product states;
- Bell singlet and triplet states;
- maximally mixed state;
- Werner states;
- density-matrix round trips;
- concurrence, negativity, entropy, CHSH, steering, and state-distance checks;
- bootstrap reproducibility;
- unfolding and EFT coefficient closure.

## Event-format tests

Eight supplied 200-event LHE fixtures cover all beam, polarization, and charge/flavour combinations. Tests parse every sample, verify ancestry, and construct event-level spin observables.

## End-to-end smoke test

The package validation builds a compact ntuple, performs tomography and physical projection, executes Level B smearing/reconstruction, computes Level C summaries, and writes machine-readable validation results.

## lxplus acceptance

The PYTHIA8/HepMC3 executable must additionally be compiled and run in the supplied Key4HEP environment because those C++ libraries are not assumed to exist in a generic build container. The commands are:

```bash
source setup_lxplus.sh
./scripts/qis/build_qis.sh
build/qis_lhe_to_hepmc3 --help
```

Then shower 100 events from one fixture or production sample and run `scripts/showering/validate_showering.py --strict`.
