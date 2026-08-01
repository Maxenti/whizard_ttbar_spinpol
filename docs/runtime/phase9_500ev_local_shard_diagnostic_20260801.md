# Phase 9 500-event local shard diagnostic

## Status

- Status: `PASS`
- Completed records: `6`
- Failures: `0`
- Manifest: `/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/campaigns/full6f_365gev_ee_ttbar_spinpol_v1/showering/phase9_500ev_parton_only_LR100_semilep_3shard_diagnostic.jsonl`
- Log directory: `/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/inspection_outputs/phase7_bridge_manifest_run_20260801T023411Z`

## Purpose

This diagnostic tested whether difficult full-6f representative channels that showed unstable monolithic 10k WHIZARD unweighted generation could be run reliably as smaller 500-event shards.

## Result table

| index | label | seed | status | raw LHE | canonical LHE | HepMC3 | run directory |
|---:|---|---:|---|---:|---:|---:|---|
| 1 | `LR100_epmum_s000` | 24693000 | `PASS_WITH_RUNTIME_WARNINGS` | 500 | 500 | 500 | `/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/runs/phase7_bridge_LR100_epmum_s000_20260801T023411Z` |
| 2 | `LR100_epmum_s001` | 24693001 | `PASS_WITH_RUNTIME_WARNINGS` | 500 | 500 | 500 | `/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/runs/phase7_bridge_LR100_epmum_s001_20260801T023639Z` |
| 3 | `LR100_epmum_s002` | 24693002 | `PASS_WITH_RUNTIME_WARNINGS` | 500 | 500 | 500 | `/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/runs/phase7_bridge_LR100_epmum_s002_20260801T023908Z` |
| 4 | `unpol_epjets_Wminus_ubar_d_s000` | 24694000 | `PASS_WITH_RUNTIME_WARNINGS` | 500 | 500 | 500 | `/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/runs/phase7_bridge_unpol_epjets_Wminus_ubar_d_s000_20260801T024142Z` |
| 5 | `unpol_epjets_Wminus_ubar_d_s001` | 24694001 | `PASS_WITH_RUNTIME_WARNINGS` | 500 | 500 | 500 | `/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/runs/phase7_bridge_unpol_epjets_Wminus_ubar_d_s001_20260801T024418Z` |
| 6 | `unpol_epjets_Wminus_ubar_d_s002` | 24694002 | `PASS_WITH_RUNTIME_WARNINGS` | 500 | 500 | 500 | `/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/runs/phase7_bridge_unpol_epjets_Wminus_ubar_d_s002_20260801T024648Z` |

## Interpretation

All six 500-event shards completed with raw LHE, canonical LHE, and HepMC3 event counts equal to 500. This validates the canonical-v2 bridge and PYTHIA parton-only handoff for the tested LR100 dilepton and unpolarized semileptonic channels.

The remaining production risk is WHIZARD unweighted-generation efficiency for monolithic large-event jobs. The recommended production strategy is therefore Condor sharding with one WHIZARD/PYTHIA chain per 500-event shard, plus timeout and retry bookkeeping.

## Warning note

Each shard is marked PASS_WITH_RUNTIME_WARNINGS due to PYTHIA `SimpleTimeShower::pTnext: negative dipole mass` warnings. The jobs still accepted all requested events. The current runner warning counter counts matching log lines, not the exact multiplicity from PYTHIA's warning table.
