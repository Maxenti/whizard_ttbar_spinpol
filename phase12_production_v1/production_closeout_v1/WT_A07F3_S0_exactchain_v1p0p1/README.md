# Phase 12 production closeout

## Final status

```
PHASE12_PRODUCTION=PASS
RECIPE=WT_A07F3_S0_exactchain_v1p0p1
NOMINAL_QED_POLICY=G0_H0
PRODUCTION_EVENTS=1000000
```

This directory is the authoritative closeout record for the qualified
365 GeV LR100 WT-restricted full-six-fermion WHIZARD+PYTHIA production.

## Authoritative production

```
/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/full6f_365gev_ee_ttbar_spinpol_v1/phase12_production_v1/20260821T162202Z_WT_A07F3_S0_1M_40x25k_v1p0p1
```

## Physics recipe

```
/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/phase12_production_v1/recipe_freeze/WT_A07F3_S0_exactchain_v1p0p1
```

## Canonical future PYTHIA worker

```
/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/phase12_production_v1/phase12b_exactchain_v1/worker_revisions/frozen_exact_worker_v1p0p1_string_join
```

The corrected v1p0p1 string-join worker supersedes the original worker
implementation for future production. This does not invalidate the existing
1M sample.

## Contents

- `PRODUCTION_LOCK.json` — machine-readable physics/software lock.
- `FUTURE_PRODUCTION_CONTRACT.md` — rules for reuse.
- `SOURCE_POINTERS.tsv` — authoritative source locations.
- `manifests/` — complete hard-LHE and final-HepMC SHA256 manifests.
- `validation/` — final production and QED validation evidence.
- `reference/` — small authoritative cards/scripts/numerical QED products.
- `provenance/` — closeout repository/environment state.
- `tools/` — integrity revalidation utility.

## Important version distinction

The production was qualified using WHIZARD 3.1.8.

A later interactive Key4HEP environment may resolve WHIZARD 3.1.5 or another
version. That later environment is not the production provenance.

Future exact-recipe production must use the qualified frozen environment/
software combination or undergo an explicit software-version requalification.

## Data immutability

The large EOS production files are not duplicated here.

Their exact content is frozen through SHA256 manifests.

The separate EOS reproduction capsule contains the closeout records plus the
frozen recipe and canonical corrected shower worker.
