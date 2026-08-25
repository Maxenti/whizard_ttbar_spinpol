# Frozen Phase-12 production recipe capsule

Recipe:

    WT_A07F3_S0_exactchain_v1p0p1

Purpose:

This directory is the Git-resident executable/source capsule for the
qualified 365 GeV LR100 WT-restricted full-six-fermion WHIZARD+PYTHIA
production recipe.

It is deliberately separate from the formal production closeout so that the
already-frozen closeout checksum set is not modified.

Contents:

- qualified_recipe/
    Exact qualified Phase-12 physics-recipe snapshot.

- canonical_shower_worker/
    Canonical corrected worker for future PYTHIA production:
    frozen_exact_worker_v1p0p1_string_join.

- environment/
    Qualified WHIZARD 3.1.8 environment setup, when available.

Production contract:

- WHIZARD 3.1.8
- LO WT-restricted full-six-fermion hard process
- sqrt(s) = 365 GeV
- LR100
- qualified frozen S0 integration grid
- VAMP2 / rng_stream
- one MPI rank per generation job
- independent generation seeds
- canonical history-preserving preparation chain
- PYTHIA 8.315
- HepMC3 3.3.1
- WHIZARD ISR retained
- PYTHIA ISR off
- PYTHIA FSR on
- MPI off
- top decay in PYTHIA off
- TimeShower:QEDshowerByL = on
- TimeShower:QEDshowerByQ = on
- TimeShower:QEDshowerByGamma = off nominally
- HadronLevel:QED = off nominally

The large Phase-12 production files remain on EOS and are frozen by the
formal production-closeout SHA256 manifests.

Do not edit files in this capsule in place. A physics/software change that
requires modification must receive a new recipe identifier and appropriate
qualification.
