# Phase 9 sharded Condor production closeout: 365 GeV full-6f parton-only bridge

## Runtime

Pinned runtime:

- WHIZARD 3.1.8
- PYTHIA 8.316
- HepMC3 3.03.01
- setup: `environments/setup_lcg_devkey_head_fri_ttsp.sh`

## Production manifest

```text
campaigns/full6f_365gev_ee_ttbar_spinpol_v1/showering/phase9_10k_parton_only_LR100_semilep_20shard_condor.jsonl
```

Production output:

```text
/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/phase9_10k_parton_only_LR100_semilep_20shard_20260803T151333Z
```

Final summary:

```text
/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/phase9_10k_parton_only_LR100_semilep_20shard_20260803T151333Z/phase9_10k_LR100_semilep_20shard_summary.json
```

## Final collector status

```text
PHASE9_SHARD_COLLECT_STATUS=PASS
TOTAL_RECORDS=40
FAILURES=0
PHASE9_10K_CONDOR_20SHARD_COLLECT_RC=0
```

## Samples produced

```text
LR100_epmum:                 20 shards x 500 events = 10000 events
unpol_epjets_Wminus_ubar_d:  20 shards x 500 events = 10000 events
```

All 40 production records have:

```text
return_code=0
runner_status=PASS_WITH_RUNTIME_WARNINGS
raw_lhe=500
canonical_lhe=500
hepmc=500
```

## Salvaged validator-collision shards

Two original shards completed WHIZARD, canonicalization, and PYTHIA, but failed during final validator bookkeeping because multiple parallel jobs attempted to create the same timestamp-only AFS phase-record directory.

```text
ProcId 10: LR100_epmum_s010
ProcId 22: unpol_epjets_Wminus_ubar_d_s002
```

They were salvaged after verifying required products and exact event counts:

```text
raw_lhe=500
canonical_lhe=500
hepmc=500
```

The repository fix is:

```text
src/ttbar_spinpol/genchain/phase_records.py
```

which now appends a deterministic suffix if a phase-record directory already exists.

Relevant commit:

```text
ca15650 Make phase records collision safe for Condor shards
```

## Retried pathological WHIZARD shard

Original ProcId 39:

```text
unpol_epjets_Wminus_ubar_d_s019
seed=24701019
```

was removed after a pathological WHIZARD unweighting tail. It had only 103/500 raw events after about 56 minutes. Its integration contained a rare high-weight spike.

Retry manifest:

```text
campaigns/full6f_365gev_ee_ttbar_spinpol_v1/showering/phase9_10k_parton_only_retry_proc39_20260803.jsonl
```

Retry output:

```text
/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/phase9_10k_parton_only_retry_proc39_20260803T161139Z
```

Retry run directory:

```text
/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/runs/phase7_bridge_unpol_epjets_Wminus_ubar_d_s019_retry00_20260803T161500Z
```

Retry collector:

```text
PHASE9_SHARD_COLLECT_STATUS=PASS
TOTAL_RECORDS=1
FAILURES=0
PHASE9_RETRY39_COLLECT_RC=0
```

The retry was promoted into the original production slot:

```text
/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/phase9_10k_parton_only_LR100_semilep_20shard_20260803T151333Z/status/job_39_unpol_epjets_Wminus_ubar_d_s019.status.json
```

Relevant commit:

```text
98504d6 Close Phase 9 sharded Condor production with retry provenance
```

## Interpretation

This validates the Phase 9 sharded Condor strategy for difficult 365 GeV full-6f production:

1. The canonical-v2 WHIZARD-to-PYTHIA bridge is stable for parton-only HepMC3 production.
2. The failure granularity is now one 500-event shard, not a monolithic 10k channel.
3. Pathological WHIZARD unweighting seeds can be removed and retried without discarding successful shards.
4. The phase-record timestamp collision was a bookkeeping artifact and is fixed for future parallel campaigns.
