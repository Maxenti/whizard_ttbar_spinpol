# 365 GeV LHE matrix campaign

## Purpose

The validated 500 GeV sample is frozen. The 365 GeV program therefore reuses
its qualified WHIZARD production definitions and changes only controlled
campaign quantities:

- nominal collision energy: 500 to 365 GeV;
- output sample ID;
- event count;
- random seed;
- canonical campaign metadata.

The ISR implementation, beam definition, polarization, explicit top decays,
and spin-correlation controls are inherited from the corresponding qualified
500 GeV production template and are checked before materialization.

## Matrix

The campaign contains exactly 16 LHE samples:

```text
2 initial states
x 2 mixed-flavour decay assignments
x 2 beam polarizations
x 2 spin modes
= 16 LHE samples
```

The sample naming contract is:

```text
<initial>_ttbar_<decay>_<polarization>_<spin>_ISR_365GeV
```

Examples:

```text
ee_ttbar_epmum_LR100_sc_ISR_365GeV
mumu_ttbar_mupem_RL100_iso_ISR_365GeV
```

## Physics scope

These samples are polarized, ISR-enabled, tree-level continuum ttbar samples
with factorized explicit top decays. They are suitable for validating the
energy-dependent spin-analysis pipeline and for producing the matched LHE and
post-shower samples used by the paper workflow.

They do not claim precision threshold-scan accuracy from Coulomb resummation,
nonresonant W+b W-bbar contributions, or matched threshold/continuum theory.

## Gating policy

Run the 1,000-event pilot profile first. Promotion to the 10,000-event profile
requires:

1. all 16 source templates pass the qualified-template contract;
2. all 16 prepared SINDARIN files pass their materialization contract;
3. all 16 WHIZARD jobs finish without errors;
4. every LHE has the exact requested event count and topology;
5. all weights are finite and nonnegative;
6. top-decay four-momentum closure passes;
7. every mtt value is between the on-shell threshold and 365 GeV;
8. ISR produces a nonzero effective-energy spread;
9. the integrated cross sections have adequate precision;
10. SC/ISO and epmum/mupem rate comparisons are statistically consistent.

The ee and mumu rates are not required to match because their ISR radiator
masses differ.

## Output structure

Each campaign root contains:

```text
campaign_manifest.json
campaign_config_snapshot.yaml
campaign_samples.csv
campaign_samples.tsv
sample_ids.txt
cross_sections.csv
cross_section_consistency_checks.csv
campaign_validation.json
CAMPAIGN_SUMMARY.md
CAMPAIGN_SHA256SUMS.txt
logs/
condor/
<initial_state>/<sample_id>/
```

Each sample directory contains the prepared input, source-to-target diff,
preparation manifest, WHIZARD outputs, LHE validation, completion record, and
sample-level checksums.

## Command outline

### Pilot preparation

```bash
python3 scripts/qis/prepare_365GeV_lhe_matrix.py \
  --repo-root "$REPO" \
  --profile pilot
```

### Pilot execution with HTCondor

```bash
bash scripts/qis/submit_365GeV_lhe_matrix.sh \
  --repo-root "$REPO" \
  --campaign-root "$REPO/runs/paper_spin_365GeV_lhe_matrix_pilot_v1"
```

### Pilot collection

```bash
python3 scripts/qis/collect_365GeV_lhe_matrix.py \
  --repo-root "$REPO" \
  --campaign-root "$REPO/runs/paper_spin_365GeV_lhe_matrix_pilot_v1" \
  --strict
```

### Production preparation

```bash
python3 scripts/qis/prepare_365GeV_lhe_matrix.py \
  --repo-root "$REPO" \
  --profile production_10k
```

The production profile is intentionally separate from the pilot root and uses
its own deterministic seed block.
