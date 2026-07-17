# Complete 15-observable polarization and spin-correlation gate

## Purpose

The production qualification must establish more than successful event
conversion.  It must verify that:

1. the configured LR100 and RL100 beam helicities are correct;
2. the generated samples exhibit polarization-dependent angular structure;
3. the spin-correlated samples differ from matched isotropic-decay controls;
4. canonicalization, explicit-W insertion, PYTHIA showering, and HepMC3 export
   preserve the hard-process spin information used by the QIS analysis.

The gate uses the complete `6 + 9` coefficient set of a two-spin density
matrix in the ordered `(k,r,n)` basis.

## Basis convention

In the `ttbar` rest frame:

```text
k = unit top direction
n = unit(negative-lepton beam x k)
r = n x k
```

The antitop basis is independently right handed:

```text
kbar = unit antitop direction = -k
nbar = n
rbar = nbar x kbar
```

The positive charged lepton is analyzed in the top rest frame.  The negative
charged lepton is analyzed in the antitop rest frame with the framework
convention `antitop_analyzer_sign = -1`.

## Fifteen event-level observables

The lower-case values are bounded event-by-event angular analyzers.

### Polarization analyzers

```text
b1k  b1r  b1n
b2k  b2r  b2n
```

Here `1` denotes the top/positive-lepton analyzer and `2` denotes the
antitop/negative-lepton analyzer.

### Correlation analyzers

```text
ckk  ckr  ckn
crk  crr  crn
cnk  cnr  cnn
```

For example:

```text
ckr = b1k * b2r
crn = b1r * b2n
```

The plotting package displays the diagonal terms first for readability:

```text
ckk crr cnn ckr crk ckn cnk crn cnr
```

but every named matrix element retains its physical `(first axis, second
axis)` meaning.

## Extracted coefficients

For charged-lepton analyzing powers `alpha_plus` and `alpha_minus`:

```text
B1_i = 3 <b1i> / alpha_plus
B2_i = 3 <b2i> / alpha_minus
C_ij = 9 <cij> / (alpha_plus alpha_minus)
```

The Level-A defaults use:

```text
alpha_plus  = 1
alpha_minus = 1
```

The connected correlation used for the SC-versus-ISO gate is:

```text
D_ij = C_ij - B1_i B2_j
```

This removes the factorized product of single-particle polarizations and tests
the genuinely connected part of the two-spin distribution.

## Qualification datasets

The gate uses four matched ntuple families:

```text
lhe_sc
hepmc_sc
lhe_iso
hepmc_iso
```

The recommended qualification statistics are:

```text
8 spin-correlated samples x 10,000 events = 80,000
8 isotropic controls       x 10,000 events = 80,000
```

The eight samples in each family span:

```text
initial state:  ee, mumu
polarization:   LR100, RL100
decay channel: epmum, mupem
```

## Gate logic

### 1. Beam configuration audit

The production CSV is checked directly:

```text
LR100: beam1_helicity = -1, beam2_helicity = +1
RL100: beam1_helicity = +1, beam2_helicity = -1
beam polarization fractions = 1.0
```

The `spin_correlated` flag must agree with the `sc` or `iso` sample ID.

### 2. LR100 versus RL100 separation

For each initial state, decay channel, spin mode, and analysis stage, the six
`B` coefficients are compared.  At least one component must exceed the
configured separation threshold.  The default qualification threshold is
`5 sigma`.

No hard-coded Standard Model sign is imposed.  This protects the analysis from
silently assuming a convention that differs from the implemented antitop basis.

### 3. SC versus ISO separation

For every matched initial-state/polarization/decay sample, the nine connected
correlations `D_ij` are compared between the spin-correlated and isotropic
samples.  At least one component must exceed the configured threshold.  The
default is `5 sigma`.

### 4. LHE versus HepMC preservation

All 15 coefficients are compared between the authoritative LHE truth and the
showered HepMC record.  The default gate requires both:

```text
absolute shift <= 0.02
combined significance <= 5 sigma
```

The purpose is not to demand that every final-state particle remain unchanged.
It is to verify that the resonance-level truth objects selected by the QIS
reader preserve the intended spin information through the production chain.

### 5. Decay-flavour consistency

The `epmum` and `mupem` channels are independent samples of the same underlying
spin configuration with exchanged charged-lepton flavours.  Differences above
the configured threshold are reported as warnings because finite statistics
and flavour-dependent QED effects can produce small differences.

## Distribution products

For every dataset and sample, the plotting script writes:

```text
spin15_polarization_panel.{png,pdf}
spin15_correlation_panel.{png,pdf}
individual/b1k.{png,pdf}
...
individual/cnr.{png,pdf}
```

The full coefficient table is:

```text
spin15_coefficients.csv
```

The gate products include:

```text
spin15_lhe_hepmc_preservation.csv
spin15_lr_rl_details.csv
spin15_lr_rl_gate.csv
spin15_connected_correlations.csv
spin15_sc_iso_details.csv
spin15_sc_iso_gate.csv
spin15_decay_flavour_details.csv
spin15_decay_flavour_gate.csv
spin15_gate_report.md
spin15_gate_summary.json
```

## Production preparation policy

The qualification shower worker uses:

```text
authoritative WHIZARD LHE
  -> canonical LHA v2
  -> explicit-W v3
  -> PYTHIA8
  -> HepMC3
```

The central qualification keeps:

```text
TimeShower:QEDshowerByGamma = on
```

and records the nonfatal negative-dipole warning count in metadata.  The
gamma-conversion-off configuration remains a generator systematic.

## Commands

Prepare and submit the SC qualification shower jobs:

```bash
python3 scripts/showering/submit_showering.py \
  --config configs/qis/qualification_500GeV_ISR_sc_v1.yaml \
  --submit
```

Prepare and submit the ISO qualification shower jobs:

```bash
python3 scripts/showering/submit_showering.py \
  --config configs/qis/qualification_500GeV_ISR_iso_v1.yaml \
  --submit
```

After all jobs finish, merge each campaign:

```bash
python3 scripts/showering/collect_showering.py \
  --config configs/qis/qualification_500GeV_ISR_sc_v1.yaml

python3 scripts/showering/collect_showering.py \
  --config configs/qis/qualification_500GeV_ISR_iso_v1.yaml
```

Then run the complete Spin-15 gate:

```bash
scripts/qis/run_spin15_qualification_gate.sh
```

The production qualification is closed only when the structural and strict
physics statuses both pass.
