# Paper-spin 365 GeV campaign: Stage 1 smoke package

## Purpose

This package starts the 365 GeV campaign without reopening the frozen 500 GeV
physics convention. Its first executable deliverable is one local WHIZARD LHE
smoke sample:

```text
ee_ttbar_epmum_LR100_sc_ISR_365GeV
```

The smoke must pass before producing the full low-statistics 16-sample LHE
matrix, Pythia/HepMC products, or the final 10,000-event qualification campaign.

## Physics scope

The Stage 1 sample is a polarized, spin-correlated, tree-level continuum
`ttbar` sample near threshold, with the same WHIZARD SM input scheme and ISR
configuration validated at 500 GeV.

It is **not** a precision threshold-scan prediction. This package does not claim:

- Coulomb or nonrelativistic threshold resummation;
- a matched continuum/threshold calculation;
- nonresonant `W+b W-bbar` backgrounds;
- precision top-threshold line-shape accuracy.

At the validated top mass of 173.1 GeV, the nominal gap is

```text
365.0 - 2 * 173.1 = 18.8 GeV.
```

This is above on-shell threshold but sufficiently close that ISR-driven
`m_ttbar` compression, event-generation efficiency, and threshold occupancy
must be audited explicitly.

## Frozen inherited contract

The following are inherited unchanged from the 500 GeV `v3/v3p1` baseline:

- incoming positive lepton defines the beam reference;
- canonical `(k,r,n)` basis;
- positive analyzer transform `diag(+1,+1,-1)`;
- negative analyzer transform `diag(-1,-1,-1)`;
- raw signs `(+1,+1)`;
- four-vector analyzer reconstruction;
- `paper_cos_theta_t` as the reviewed production angle;
- explicit top and W ancestry;
- WHIZARD ISR, Pythia ISR off, Pythia FSR on;
- strict event/weight transport versus post-shower migration semantics.

## Package files

```text
configs/qis/paper_spin_365GeV.yaml
configs/qis/paper_spin_365GeV_sm_parameters.yaml
configs/qis/paper_spin_365GeV_pilot.yaml
scripts/qis/prepare_365GeV_smoke.py
scripts/qis/run_365GeV_smoke.sh
scripts/qis/validate_365GeV_threshold_inputs.py
tests/qis/test_365GeV_smoke_package.py
```

## Safe preparation pass

Run configuration validation first:

```bash
python3 scripts/qis/validate_365GeV_threshold_inputs.py \
  --repo-root "$PWD" \
  --strict
```

Prepare a new SINDARIN run directory without executing WHIZARD:

```bash
bash scripts/qis/run_365GeV_smoke.sh \
  --prepare-only
```

Review:

```bash
sed -n '1,260p' \
  runs/ee/ee_ttbar_epmum_LR100_sc_ISR_365GeV_smoke/input_500_to_365.patch

sed -n '1,260p' \
  runs/ee/ee_ttbar_epmum_LR100_sc_ISR_365GeV_smoke/input.sin
```

The preparation script must report that the frozen 500 GeV source was not
modified.

## Execute the smoke

After reviewing the patch:

```bash
rm -rf runs/ee/ee_ttbar_epmum_LR100_sc_ISR_365GeV_smoke

bash scripts/qis/run_365GeV_smoke.sh
```

Use `--template` if the current repository stores the canonical 500 GeV input
under a different path:

```bash
bash scripts/qis/run_365GeV_smoke.sh \
  --template runs/ee/<authoritative-500GeV-run>/input.sin
```

## Required smoke gates

The strict threshold report must pass:

- nominal LHE beam energies sum to 365 GeV;
- at least 200 events are present;
- every event has the requested `epmum` decay channel;
- event weights are finite and nonnegative;
- top and antitop decay closure residuals satisfy the configured tolerance;
- reconstructed `m_ttbar` does not fall below `2m_top` beyond serialization
  tolerance;
- reconstructed `m_ttbar` does not exceed nominal `sqrt(s)` beyond tolerance;
- threshold summaries include `m_ttbar`, `beta_t`, reconstructed top masses,
  cross section, and ISR-sensitive quantiles.

Outputs are written beside the smoke run:

```text
preparation_manifest.json
config_validation.json
threshold_validation.json
threshold_validation.log
input_500_to_365.patch
SHA256SUMS.txt
SMOKE_COMPLETE.md
```

## Decision gate after Stage 1

Do not launch the full matrix until the smoke output has been reviewed for:

1. stable WHIZARD integration and event generation;
2. sensible cross section and uncertainty;
3. no abnormal event weights;
4. correct explicit-W topology;
5. `m_ttbar` and `beta_t` occupancy;
6. acceptable generation efficiency;
7. appropriate near-threshold differential binning.

After Stage 1 passes, the next package should create the full low-statistics
matrix for:

```text
2 initial states × 2 decay channels × 2 polarizations × 2 spin modes
= 16 LHE samples
```

Pythia/HepMC and the 32-ntuple analysis matrix follow only after those 16 LHE
samples pass structure and kinematic audits.
