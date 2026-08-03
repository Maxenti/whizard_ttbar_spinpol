# Phase 9 analysis closeout: 365 GeV parton-only spin-moment pipeline

Date: 2026-08-03  
Repository: `/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol`  
Branch context: `feature/top-qis-framework-v1`  
Campaign: `full6f_365gev_ee_ttbar_spinpol_v1`

## Executive status

Phase 9 is now closed as a validated **parton-only analysis pipeline** for the 365 GeV full-6f `e+e- -> ttbar` spin/QIS workflow.

The completed chain is:

1. sharded Condor production,
2. analysis-facing sample inventory,
3. HepMC3 inventory QA,
4. event-level truth extraction,
5. dilepton spin-moment construction,
6. boost-sign correction and sanity check,
7. unpolarized-vs-LR100 spin-moment comparison with bootstrap uncertainties,
8. spin-axis convention diagnostic.

The resulting products are suitable as a **truth-candidate, parton-only validation product**. They are not yet the final full-hadron precision sample.

## Runtime

Pinned runtime:

```text
WHIZARD 3.1.8
PYTHIA 8.316
HepMC3 3.03.01
```

Setup script:

```text
environments/setup_lcg_devkey_head_fri_ttsp.sh
```

## Final committed workflow chain

Relevant final commits:

```text
16aba34 Compare Phase 9 unpolarized and LR100 spin moments
49eb81f Fix Phase 9 spin-moment rest-frame boosts
89873b1 Build Phase 9 dilepton truth spin moments
992a215 Extract Phase 9 parton-level truth observables
686623c Add Phase 9 HepMC inventory QA
219b100 Add Phase 9 analysis-facing sample inventory
aa5178a Document Phase 9 sharded Condor production closeout
98504d6 Close Phase 9 sharded Condor production with retry provenance
ca15650 Make phase records collision safe for Condor shards
```

## Production and inventory

Analysis inventory:

```text
campaigns/full6f_365gev_ee_ttbar_spinpol_v1/analysis_inputs/phase9_parton_only_analysis_inventory_20260803.jsonl
```

Inventory summary:

```text
campaigns/full6f_365gev_ee_ttbar_spinpol_v1/analysis_inputs/phase9_parton_only_analysis_inventory_20260803.summary.json
```

Final inventory content:

```text
unpol_epmum:                 10000 events
LR100_epmum:                 10000 events
unpol_epjets_Wminus_ubar_d:  10000 events
```

Total:

```text
41 records
30000 events
```

The 41 records are:

```text
1 single 10000-event unpolarized dilepton run
20 LR100 dilepton shards x 500 events
20 unpolarized semileptonic shards x 500 events
```

## HepMC3 QA

QA script:

```text
scripts/showering/qa_phase9_hepmc_inventory.py
```

QA outputs:

```text
campaigns/full6f_365gev_ee_ttbar_spinpol_v1/analysis_inputs/phase9_parton_only_hepmc_qa_20260803.jsonl
campaigns/full6f_365gev_ee_ttbar_spinpol_v1/analysis_inputs/phase9_parton_only_hepmc_qa_20260803.summary.json
```

Final QA status:

```text
HEPMC_QA_STATUS=PASS
TOTAL_RECORDS=41
FAILED_RECORDS=0
WARNING_RECORDS=0
```

Important correction: the first QA attempt failed because the parser read the HepMC3 `production_vertex` field as the PDG ID. The corrected HepMC3 Ascii3 particle interpretation is:

```text
P id production_vertex pdg_id px py pz energy mass status ...
```

After patching the parser, all 41 records passed with no warnings.

## Truth extraction

Truth extractor:

```text
scripts/qis/extract_phase9_parton_truth_observables.py
```

Event-level truth table on EOS:

```text
/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/analysis/phase9_parton_truth_observables_20260803/phase9_parton_truth_observables.jsonl
```

Repository summary:

```text
campaigns/full6f_365gev_ee_ttbar_spinpol_v1/analysis_inputs/phase9_parton_truth_observables_20260803.summary.json
```

Final extraction status:

```text
TRUTH_EXTRACT_STATUS=PASS
TOTAL_EVENTS=30000
FAILED_EVENTS=0
```

The truth table contains event-level hard-object records and derived sanity observables for the dilepton and semileptonic samples.

## Dilepton spin moments

Spin-moment builder:

```text
scripts/qis/build_phase9_dilepton_spin_moments.py
```

Detailed outputs on EOS:

```text
/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/analysis/phase9_spin_moments_20260803/phase9_dilepton_spin_moments.json
/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/analysis/phase9_spin_moments_20260803/phase9_dilepton_spin_moments.csv
```

Repository summary:

```text
campaigns/full6f_365gev_ee_ttbar_spinpol_v1/analysis_inputs/phase9_dilepton_spin_moments_20260803.summary.json
```

Moment convention:

```text
Bplus_i  =  3 <uplus_i>
Bminus_j = -3 <uminus_j>
C_ij     = -9 <uplus_i uminus_j>
```

Component order:

```text
r, n, k
```

Subsystem order:

```text
top, antitop
```

Analyzer signs:

```text
top l+       +1
antitop l-   -1
```

Final corrected spin-moment status:

```text
SPIN_MOMENT_STATUS=PASS
TOTAL_TRUTH_EVENTS_SEEN=30000
TOTAL_DILEPTON_EVENTS_USED=20000
```

The semileptonic sample is intentionally skipped by this first dilepton `l+ l-` spin-moment table.

## Boost-sign correction

The initial spin-moment output mechanically passed, but produced unphysical or physically suspicious values with some components larger than one, including large `B_k` and `C_kk` components. The problem was a boost-sign convention error.

The implemented boost uses:

```text
E' = gamma (E - beta · p)
```

Therefore, to transform a lab-frame four-vector into the rest frame of an object with four-momentum `P`, the correct input is:

```text
beta = P_vec / P_E
```

not

```text
beta = -P_vec / P_E
```

After correcting the boost signs, the spin moments passed the hard sanity bound:

```text
SPIN_MOMENT_PHYSICS_SANITY=PASS
```

Corrected representative moments:

```text
unpol_epmum:
  Bplus_r   = +0.287878
  Bminus_r  = +0.300668
  Bplus_k   = -0.069937
  Bminus_k  = -0.061370
  C_rr      = +0.598619
  C_kk      = +0.391351

LR100_epmum:
  Bplus_r   = +0.713101
  Bminus_r  = +0.724113
  Bplus_k   = -0.186276
  Bminus_k  = -0.209079
  C_rr      = +0.515455
  C_kk      = +0.354922
```

## LR100 minus unpolarized comparison

Comparison script:

```text
scripts/qis/compare_phase9_dilepton_spin_moments.py
```

Detailed outputs on EOS:

```text
/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/analysis/phase9_spin_moments_20260803/phase9_dilepton_spin_moment_comparison_LR100_minus_unpol.json
/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/analysis/phase9_spin_moments_20260803/phase9_dilepton_spin_moment_comparison_LR100_minus_unpol.csv
```

Repository summary:

```text
campaigns/full6f_365gev_ee_ttbar_spinpol_v1/analysis_inputs/phase9_dilepton_spin_moment_comparison_20260803.summary.json
```

Final comparison status:

```text
SPIN_COMPARISON_STATUS=PASS
TOTAL_TRUTH_EVENTS_SEEN=30000
TOTAL_DILEPTON_EVENTS_SEEN=20000
USABLE_UNPOL=10000
USABLE_LR100=10000
N_BOOTSTRAP=500
```

Bootstrap settings:

```text
n_bootstrap = 500
seed = 36520260803
```

Resolved shifts using the current truth-candidate convention:

```text
Bplus_r:
  unpol = +0.287878
  LR100 = +0.713101
  delta = +0.425223
  se    =  0.022350
  z     = +19.03
  classification = large_resolved_shift

Bminus_r:
  unpol = +0.300668
  LR100 = +0.724113
  delta = +0.423444
  se    =  0.023270
  z     = +18.20
  classification = large_resolved_shift

Bminus_k:
  unpol = -0.061370
  LR100 = -0.209079
  delta = -0.147708
  se    =  0.025022
  z     = -5.90
  classification = large_resolved_shift

Bplus_k:
  unpol = -0.069937
  LR100 = -0.186276
  delta = -0.116339
  se    =  0.023293
  z     = -4.99
  classification = moderate_resolved_shift
```

Summary classification counts:

```text
large_resolved_shift:       3
moderate_resolved_shift:    1
small_but_resolved_shift:   0
not_resolved:              11
```

At the current 10000-vs-10000 statistics, the polarization-vector components show the strongest resolved response to LR100. The `C_ij` correlation shifts are not resolved in this comparison.

## Spin-axis convention diagnostic

Axis diagnostic script:

```text
scripts/qis/diagnose_phase9_spin_axis_convention.py
```

Detailed outputs on EOS:

```text
/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/analysis/phase9_spin_axis_convention_20260803/phase9_dilepton_axis_convention_comparison.json
/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/analysis/phase9_spin_axis_convention_20260803/phase9_dilepton_axis_convention_comparison.csv
```

Repository summary:

```text
campaigns/full6f_365gev_ee_ttbar_spinpol_v1/analysis_inputs/phase9_dilepton_axis_convention_20260803.summary.json
```

Compared axis definitions:

```text
nominal_beam
effective_status21_beam
```

Final axis diagnostic status:

```text
AXIS_CONVENTION_STATUS=PASS
PHASE9_AXIS_CONVENTION_RC=0
```

Event usage:

```text
unpol_epmum:
  nominal_beam              10000
  effective_status21_beam   10000

LR100_epmum:
  nominal_beam              10000
  effective_status21_beam   10000
```

Maximum absolute moment difference between the two axis definitions:

```text
MAX_ABS_AXIS_DELTA=1.0842021724855044e-18
```

This is numerical roundoff. Therefore, for this Phase 9 truth-candidate product, the nominal-beam convention can be frozen as internally stable.

## Current physics interpretation

Within the current parton-only, truth-candidate convention:

1. The pipeline is now validated end-to-end from HepMC3 inventory to moment comparison.
2. LR100 beam polarization produces large, highly resolved changes in the `r` components of both top and antitop polarization:
   - `Bplus_r`
   - `Bminus_r`
3. LR100 also produces resolved negative shifts in the `k` polarization components:
   - `Bminus_k`
   - `Bplus_k`
4. The `C_ij` spin-correlation matrix components are not significantly resolved with the current 10000-vs-10000 comparison.
5. The nominal-beam and status-21 effective-beam axis definitions are equivalent for these samples at numerical precision.

## Caveats

This is not yet the final precision physics sample.

The main limitations are:

1. The samples are parton-only:
   ```text
   HadronLevel:all = off
   ```

2. The PYTHIA bridge profile used for this validated product is a robust topology proof and truth-level analysis product, not the final full-hadron production setting.

3. The current comparison includes:
   ```text
   unpol_epmum
   LR100_epmum
   ```
   but not yet:
   ```text
   RL100_epmum
   ```
   so it is not a complete polarized beam pair.

4. The current product validates a truth-level moment pipeline. It does not yet validate detector-level reconstruction, Delphes, or full-hadron observables.

## Recommended next decision

The recommended next product is:

```text
Produce RL100_epmum with the same Phase 9 sharded parton-only pipeline.
```

Reason:

1. LR100 alone proves that beam polarization moves the spin observables, but it does not provide the symmetry partner needed for a robust polarization-basis validation.
2. RL100 should approximately flip or complement the polarization-sensitive structures relative to LR100, modulo electroweak chiral couplings and acceptance/phase-space effects.
3. Having unpol, LR100, and RL100 creates a much stronger validation set before building publication-facing QIS tables.
4. RL100 is cheaper and more targeted than launching broad new channels.
5. The sharded Condor workflow is already proven, and pathological WHIZARD seeds can now be retried cleanly.

After RL100 is produced and passed through the same inventory, QA, truth extraction, spin moments, and comparison machinery, the project should build the first density-matrix/QIS observable table.

## Recommended next workflow order

```text
1. Commit the axis-convention diagnostic summary.
2. Add this closeout note under docs/analysis/.
3. Produce RL100_epmum as a 20 x 500 event Phase 9 parton-only campaign.
4. Add RL100 to the analysis inventory.
5. Run HepMC3 QA on the updated inventory.
6. Update/re-run truth extraction.
7. Update/re-run spin moments for unpol, LR100, and RL100.
8. Compare LR100 - unpol and RL100 - unpol.
9. Check LR/RL symmetry and sign behavior.
10. Then build density-matrix and QIS-observable tables.
```

## Suggested repository location for this note

```text
docs/analysis/phase9_parton_spin_analysis_closeout_20260803.md
```
