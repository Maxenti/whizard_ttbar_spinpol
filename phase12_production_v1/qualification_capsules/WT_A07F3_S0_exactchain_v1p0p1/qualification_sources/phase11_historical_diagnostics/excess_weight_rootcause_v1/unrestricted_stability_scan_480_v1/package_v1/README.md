# Phase 11 unrestricted integration-stability scan — 480-node DAG

## Purpose

This package runs a predeclared stability scan of the known-problematic unrestricted
365 GeV LR100 full6f process

`e- e+ -> b bbar e+ nue mu- numubar`

using WHIZARD 3.1.8, VAMP2, `rng_stream`, simple VAMP balancing, MPI=1, OMP=1.

The scan deliberately separates adaptive-grid construction from final fixed-grid /
envelope estimation.

## Design

- 15 adaptive prescriptions A00..A14
- 8 predetermined adaptive seeds S0..S7
- 120 adaptive parent jobs
- 3 fixed descendants F0..F2 per parent
- 360 fixed child jobs
- 480 DAG nodes total

A child runs only after its exact parent succeeds.

### Fixed descendants

- F0 = `3:200000:""`
- F1 = `1:600000:""`
- F2 = `1:2000000:""`

F0 and F1 have the same total fixed-call budget but different iteration segmentation.
All three siblings use the same predetermined fixed-stage seed for a given Sx.

## Important reuse contract

Each adaptive parent saves exactly:

- `proc_epmum.i1.phs`
- `proc_epmum.m1.vg2`

into `integration_artifacts.tar.gz`.

Each fixed child restores that parent workspace and requests:

`<stored adaptive schedule>,<fixed suffix>`

VAMP2 must reuse the stored prefix and calculate only the missing fixed iterations.
The fixed worker fails if its log contains `VAMP2: Initialize new grids` or lacks
`VAMP2: Using grids and results from file`.

## Seed policy

S0/S1/S2 preserve the established Phase-11 adaptive seeds. S3..S7 are frozen in
`config/seeds.tsv`. Fixed-stage seeds are a separate deterministic namespace and
are also frozen before submission.

No physics seed may be discarded or replaced after results are observed.

## Source immutability

`prepare_campaign.py` checks the unrestricted source-card SHA256 against the
Phase-11 source SHA and then copies the entire source tree into the concrete
submission directory. All 480 jobs use that frozen source tree, not the mutable
`generated/` tree.

## CERN paths expected by default workflow

Repository:

`/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol`

Source card:

`/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/full6f_365gev_ee_ttbar_spinpol_v1/f6f365_ee_LR100_epmum/epmum/process.sin`

Package archive storage:

`/eos/user/c/cglenn/FCCWork/whizard/packages/`

## Typical workflow

1. unpack package from EOS into AFS;
2. prepare a timestamped concrete submission;
3. run the preflight suite;
4. record the schedd hosting any already-running diagnostic jobs;
5. optionally run `myschedd bump` immediately before the new DAG submission;
6. submit the DAG;
7. monitor with `status_campaign.sh`;
8. collect outputs with `collect_results.py`.

Do not use `condor_history` for this campaign.
