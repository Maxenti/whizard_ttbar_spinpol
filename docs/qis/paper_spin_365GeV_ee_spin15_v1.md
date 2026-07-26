# 365 GeV ee Spin-15 qualification

## Scope

This workflow builds and validates the complete truth-level 15-observable
top-pair polarization and spin-correlation package for the validated

    e+ e- -> t tbar -> b l+ nu_l bbar l'- nubar_l'

sample matrix at a nominal center-of-mass energy of 365 GeV.

The sample matrix contains:

- initial state: `ee`;
- decay channels: `epmum`, `mupem`;
- beam-polarization states: `LR100`, `RL100`;
- decay-spin treatments:
  - `sc`: spin-correlated matrix-element decays;
  - `iso`: isotropic-decay control;
- 10,000 events per sample;
- four SC samples and four ISO samples.

## Authoritative generator campaign

Campaign identifier:

    paper_spin_365GeV_lhe_matrix_10k_v1

The authoritative LHE validation record is:

    runs/paper_spin_365GeV_lhe_matrix_10k_v1/campaign_validation.json

The Spin-15 workflow uses the generated SC and ISO source manifests:

    runs/paper_spin_365GeV_lhe_matrix_10k_v1/manifests/source_manifest_ee_sc.csv
    runs/paper_spin_365GeV_lhe_matrix_10k_v1/manifests/source_manifest_ee_iso.csv

## Transport inputs

The PYTHIA8/HepMC3 transport stage uses:

- WHIZARD 3.1.5;
- PYTHIA 8.315;
- HepMC3 3.03.01;
- incoming-lepton ISR from WHIZARD;
- PYTHIA incoming ISR disabled;
- PYTHIA final-state showering and hadronization enabled;
- MPI disabled;
- PYTHIA top and resonance redecays disabled;
- WHIZARD top-decay and W-decay kinematics preserved;
- explicit-W LHE topology adapter;
- ten deterministic 1,000-event transport shards per sample.

The strict shower validator passed all checks for both campaigns:

    SC:  1102 / 1102 checks passed
    ISO: 1102 / 1102 checks passed

The merged transport products contain:

    4 SC samples  x 10,000 events
    4 ISO samples x 10,000 events
    80,000 total events

## Spin-15 datasets

The generic gate constructs four matched analysis datasets:

    lhe_sc
    hepmc_sc
    lhe_iso
    hepmc_iso

The LHE datasets test the authoritative matrix-element truth.

The HepMC3 datasets test whether showering, hadronization, and event-record
translation preserve the extracted polarization and spin information.

## Observable convention

The basis order is:

    [k, r, n]

The antitop-axis convention is:

    particle_helicity_right_handed

The analysis uses:

    antitop_analyzer_sign = -1

For unit charged-lepton analyzing powers, the extracted coefficients are:

    B1_i = 3 <b1_i>
    B2_i = 3 <b2_i>
    C_ij = 9 <c_ij>

The nine connected correlations used for SC-versus-ISO discrimination are:

    D_ij = C_ij - B1_i B2_j

## Gate categories

The validator checks:

1. structural completeness and event-level observable bounds;
2. LR100/RL100 beam-helicity configuration;
3. preservation of all 15 extracted coefficients from LHE to HepMC3;
4. LR100-versus-RL100 polarization separation;
5. SC-versus-ISO connected-correlation separation;
6. `epmum`-versus-`mupem` flavour consistency.

The authoritative LHE result is used as the physics reference. No hard-coded
Standard Model coefficient sign is imposed by the validator.

## Run commands

### Contract tests

    cd /afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol

    source setup_lxplus.sh

    python3 -m pytest -q \
      tests/qis/test_365GeV_ee_spin15_contract.py \
      tests/qis/test_spin15_observables.py \
      tests/qis/test_spin15_gate_policy.py \
      tests/qis/test_hepmc_topology.py

### Small structural smoke test

    MAX_EVENTS=100 \
    STRICT_PHYSICS=0 \
    PLOT_FORMATS=png \
    FORCE=1 \
    OUT=/tmp/${USER}/paper_spin_365GeV_ee_spin15_smoke \
    ./scripts/qis/run_365GeV_ee_spin15_gate.sh

### Full strict gate

    ./scripts/qis/run_365GeV_ee_spin15_gate.sh

The default full output root is:

    /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/qis/qualification/paper_spin_365GeV_ee_spin15_10k_v1

## Interpretation boundary

These samples are a validated leading-order continuum production and transport
baseline at 365 GeV. They are suitable for:

- software and convention validation;
- LHE-to-HepMC preservation tests;
- polarization and spin-observable extraction;
- SC-versus-isotropic control comparisons;
- methodological development for QIS and quantum-steering observables.

They are not, by themselves, a final precision threshold prediction. A final
precision program near the top threshold would additionally require a
controlled treatment of threshold resummation, off-shell and nonresonant
contributions, higher-order corrections, beam-energy spectra, and associated
mass-scheme and uncertainty choices.
