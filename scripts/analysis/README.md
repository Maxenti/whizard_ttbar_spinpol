# WHIZARD ttbar angular/spin validation package

This package is an overlay for the validated repository at:

```text
/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol
```

It analyzes the existing 12 WHIZARD LHE samples:

- initial state: `ee`, `mumu`
- polarization: `unpol`, `LR100`, `RL100`
- decay treatment: exact spin correlations (`sc`) and isotropic control (`iso`)
- forced final state:
  `t -> b e+ nu_e`, `tbar -> bbar mu- anti-nu_mu`

## Dependencies

The scripts use only Python 3, NumPy, and Matplotlib. In the same Key4HEP environment used for WHIZARD:

```bash
source /cvmfs/sw.hsf.org/key4hep/setup.sh
python3 - <<'PY'
import numpy
import matplotlib
print("numpy", numpy.__version__)
print("matplotlib", matplotlib.__version__)
PY
```

## Installation

Extract the archive into the repository root with one leading package directory removed:

```bash
cd /afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol

tar -xzf /path/to/whizard_ttbar_spinpol_analysis_validation_v1.tar.gz \
  --strip-components=1
```

Confirm the scripts:

```bash
find scripts/analysis -maxdepth 1 -type f -printf '%f\n' | sort
python3 -m py_compile scripts/analysis/*.py
```

## Full workflow

Run from the repository root.

### 1. Parse and validate the LHE records

```bash
python3 scripts/analysis/parse_lhe_ttbar.py \
  --overwrite \
  --strict
```

This writes:

```text
validation/angular_tables/events/<sample>_events.csv
validation/angular_summaries/lhe_parse_summary.csv
```

The parser checks:

- all generated events are present;
- the expected status-2 `t` and `tbar` records exist;
- the final state is exactly identifiable as
  `b e+ nu_e bbar mu- anti-nu_mu`;
- daughters point to the expected top parent through LHE mother indices;
- top and antitop decay four-momenta close within the configured tolerance;
- the LHE-header cross section in pb agrees with the manifest cross section in fb;
- forced-decay branching weights can be reconstructed from the WHIZARD log.

### 2. Build spin and production observables

```bash
python3 scripts/analysis/make_spin_observables.py \
  --overwrite \
  --strict
```

This writes:

```text
validation/angular_tables/observables/<sample>_spin_observables.csv
validation/angular_summaries/spin_observable_summary.csv
```

The helicity-angle convention is:

1. form the reconstructed `ttbar` four-vector;
2. boost the beams, tops, and charged leptons into the `ttbar` rest frame;
3. use the top or antitop flight direction in that frame as its helicity axis;
4. boost each charged lepton into its parent rest frame;
5. compute the lepton-axis cosine.

The key quantities are:

```text
cos_theta_star_plus
cos_theta_star_minus
cos_theta_star_product
omega_ll
```

where `omega_ll` is currently an explicit alias of the helicity-angle product.

### 3. Compare the samples and make plots

```bash
python3 scripts/analysis/compare_spin_samples.py \
  --overwrite
```

This writes:

```text
validation/angular_summaries/spin_shape_comparisons.csv
validation/angular_summaries/spin_shape_comparisons.md
validation/plots/production/
validation/plots/dilepton/
validation/plots/helicity_angles/
validation/plots/two_dimensional/
```

The default comparison groups are:

- `sc_vs_iso`
- `ee_vs_mumu`
- `polarization`

Use a subset when needed:

```bash
python3 scripts/analysis/compare_spin_samples.py \
  --comparison-groups sc_vs_iso \
  --overwrite
```

A fast metrics-only run that skips plot rendering is:

```bash
python3 scripts/analysis/compare_spin_samples.py --no-plots
```

### 4. Run the strict validation

```bash
python3 scripts/analysis/validate_spin_shapes.py --strict
RC=$?

echo "validator return code: $RC"
cat validation/angular_summaries/spin_shape_validation.md
```

A clean run returns `0` and writes:

```text
validation/angular_summaries/spin_shape_validation.csv
validation/angular_summaries/spin_shape_validation.md
```

## Observable groups

### Production controls

```text
cos_theta_t
top_pt_GeV
top_rapidity
m_tt_GeV
```

For a fixed initial state and beam polarization, these should agree between
`sc` and `iso`, because the production matrix element is unchanged.

### Dilepton observables

```text
delta_phi_ll
delta_R_ll
cos_opening_ll
m_ll_GeV
```

These are direct lab-frame observables. At the current no-ISR baseline, the lab
and hard-process center-of-mass frame coincide.

### Helicity observables

```text
cos_theta_star_plus
cos_theta_star_minus
cos_theta_star_product
lplus_energy_lab_GeV
lminus_energy_lab_GeV
```

The two-dimensional core product is:

```text
cos_theta_star_plus versus cos_theta_star_minus
```

## Metrics

For every one-dimensional pair, the comparison table stores:

- sample sizes, means, and standard deviations;
- mean difference and Cohen's d;
- two-sample Kolmogorov-Smirnov statistic and asymptotic p-value;
- Jensen-Shannon divergence;
- normalized histogram L1 distance;
- symmetric binned chi-square and chi-square per degree of freedom;
- maximum absolute normalized bin difference.

For the two-dimensional helicity plane, it stores JS divergence, L1 distance,
binned chi-square, and the maximum absolute bin difference.

## Normalization

The current WHIZARD files force one decay mode per top and therefore report the
inclusive `ttbar` production normalization conditional on that decay choice.
The parser stores both:

```text
production_cross_section_fb
exclusive_cross_section_fb
```

with

```text
exclusive_cross_section = production_cross_section
                          * Gamma(t -> b e+ nu_e) / Gamma_top
                          * Gamma(tbar -> bbar mu- anti-nu_mu) / Gamma_topbar
```

All shape-comparison plots are unit normalized. Absolute-yield work should use
the exclusive normalization explicitly.

## Selective/debug operation

Parse one sample:

```bash
python3 scripts/analysis/parse_lhe_ttbar.py \
  --sample 'ee_ttbar_emu_LR100_sc_500GeV' \
  --max-events 100 \
  --overwrite
```

Analyze an entire family:

```bash
python3 scripts/analysis/make_spin_observables.py \
  --sample 'ee_*' \
  --overwrite
```

Make only the central electron LR spin comparison:

```bash
python3 scripts/analysis/compare_spin_samples.py \
  --sample 'ee_ttbar_emu_LR100_*' \
  --comparison-groups sc_vs_iso \
  --overwrite
```

## Important scope limits

- The parser currently targets the mixed-flavour charge assignment used by the
  generated baseline. A charge-conjugate sample should be added through an
  explicit channel definition rather than silently accepted as the same mode.
- The isotropic sample is a deliberately unphysical spin-off control.
- The present validation tests generator-level shapes. It does not replace
  shower/hadronization, detector-level, or reconstruction-level validation.
- When ISR or machine beam spectra are enabled, the `ee_vs_mumu` assumptions
  and validation thresholds must be revisited.
