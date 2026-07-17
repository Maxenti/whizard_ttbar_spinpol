# WHIZARD ttbar spin-correlation and beam-polarization samples

This repository is a reproducible starter production workflow for

- `e- e+ -> t tbar`, and
- `mu- mu+ -> t tbar`,

with explicit mixed-flavour dilepton decays

```text
t    -> b    e+  nu_e
tbar -> bbar mu- anti-nu_mu
```

at `sqrt(s) = 500 GeV`.

The initial validation matrix contains unpolarized, pure `LR`, and pure `RL`
beams, each with either full cascade spin correlations (`sc`) or an isotropic,
spin-uncorrelated decay control (`iso`).

## Physics scope

The supplied samples intentionally use a minimal hard-process setup:

- Standard Model tree-level matrix elements;
- no ISR;
- no beam-energy spread or beamstrahlung;
- no parton shower or hadronization;
- factorized narrow-width top decays through WHIZARD's `unstable` machinery;
- LHEF output for downstream showering and detector simulation.

This separation is deliberate. First validate the hard process, polarization,
and spin treatment. ISR, machine spectra, Pythia8, threshold-resummed top
production, and detector simulation should be added as later, separately
validated axes.

## Sample matrix

| Initial state | Polarization | Spin mode | Sample count |
|---|---|---|---:|
| `ee` | `unpol`, `LR100`, `RL100` | `sc`, `iso` | 6 |
| `mumu` | `unpol`, `LR100`, `RL100` | `sc`, `iso` | 6 |

Definitions:

- `LR100`: the negative lepton is 100% left-handed and the positive antilepton
  is 100% right-handed;
- `RL100`: the negative lepton is 100% right-handed and the positive antilepton
  is 100% left-handed;
- `sc`: `?diagonal_decay = false` and `?isotropic_decay = false`;
- `iso`: `?diagonal_decay = false` and `?isotropic_decay = true`.

The steering files set `?polarized_events = true` in integration and simulation
blocks. This follows standard WHIZARD polarized-event examples and makes the
helicity treatment explicit for the pure-polarization samples.

## Repository layout

```text
whizard_ttbar_spinpol/
├── README.md
├── metadata/
│   ├── whizard_version.txt
│   ├── environment.txt
│   └── sample_manifest.csv
├── sindarin/
│   ├── ee/
│   └── mumu/
├── scripts/
│   ├── run_one.sh
│   ├── run_validation_matrix.sh
│   ├── make_sample_manifest.py
│   └── validate_cross_sections.py
├── runs/
│   ├── ee/
│   └── mumu/
├── lhe/
├── logs/
└── validation/
    ├── summaries/
    └── plots/
```

Each sample runs in its own directory under `runs/<initial-state>/<sample-id>/`.
WHIZARD creates process libraries, integration grids, and generated files in
its current working directory, so isolated workspaces are mandatory.

## Requirements

- WHIZARD available as `whizard` in `PATH`;
- Bash 4 or newer;
- Python 3.9 or newer.

The helper scripts use only the Python standard library.

Before production, record the actual environment:

```bash
cd whizard_ttbar_spinpol

which whizard
whizard --version

{
  echo "captured_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname -f 2>/dev/null || hostname)"
  echo "whizard_path=$(command -v whizard)"
  whizard --version
} | tee metadata/whizard_version.txt

{
  echo "captured_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname -f 2>/dev/null || hostname)"
  echo "pwd=$PWD"
  echo "shell=${SHELL:-unknown}"
  echo "path=$PATH"
  echo
  env | sort
} > metadata/environment.txt
```

On lxplus, first enter the environment that supplies the intended WHIZARD
build. Do not mix integration grids between different WHIZARD versions,
compilers, models, or beam configurations.

## Static dry run

```bash
./scripts/run_validation_matrix.sh --dry-run
```

Run one dry-run check:

```bash
./scripts/run_one.sh --dry-run \
  sindarin/ee/ee_ttbar_emu_LR100_sc_500GeV.sin
```

## Run one sample

```bash
./scripts/run_one.sh \
  sindarin/ee/ee_ttbar_emu_LR100_sc_500GeV.sin
```

The default workspace is

```text
runs/ee/ee_ttbar_emu_LR100_sc_500GeV/
```

An explicit run directory can be supplied:

```bash
./scripts/run_one.sh \
  sindarin/ee/ee_ttbar_emu_LR100_sc_500GeV.sin \
  /path/to/custom/run_directory
```

Use `--force` to replace an existing non-empty workspace:

```bash
./scripts/run_one.sh --force \
  sindarin/ee/ee_ttbar_emu_LR100_sc_500GeV.sin
```

After a successful run, the wrapper copies the main log to `logs/` and copies
discovered LHE/LHEF files to `lhe/<initial-state>/`. The complete WHIZARD
workspace remains under `runs/`.

## Run the validation matrix

Run all 12 samples sequentially:

```bash
./scripts/run_validation_matrix.sh
```

Useful filters:

```bash
./scripts/run_validation_matrix.sh --initial-state ee
./scripts/run_validation_matrix.sh --spin sc
./scripts/run_validation_matrix.sh --polarization LR100
./scripts/run_validation_matrix.sh --continue-on-error
```

The matrix runner is intentionally sequential. It is for initial physics
validation, not high-statistics production. Once all configurations are stable,
separate integration-grid preparation from seeded event shards in HTCondor.

## Build or refresh the manifest

```bash
python3 scripts/make_sample_manifest.py
```

Include SHA-256 checksums of discovered LHE files:

```bash
python3 scripts/make_sample_manifest.py --checksums
```

The manifest records steering metadata, requested/generated event counts,
run status, cross section and integration error when parsable, output paths,
and optional checksums.

## Validate cross sections

```bash
python3 scripts/validate_cross_sections.py
```

Outputs:

```text
validation/summaries/cross_section_validation.csv
validation/summaries/cross_section_validation.md
```

Checks performed when results exist:

1. individual integration precision;
2. `ee` versus `mumu` equality for otherwise identical hard-process settings;
3. `sc` versus `iso` normalization consistency for the same initial state and
   polarization.

For a CI-style gate:

```bash
python3 scripts/validate_cross_sections.py --strict
```

Thresholds are configurable:

```bash
python3 scripts/validate_cross_sections.py \
  --max-relative-integration-error 0.02 \
  --max-pair-relative-difference 0.03 \
  --max-pair-pull 3.0
```

## Required first validation plots

After event generation, compare `sc` and `iso` in:

- top production angle `cos(theta_t)`;
- dilepton azimuthal separation `|Delta phi_ll|`;
- dilepton three-dimensional opening angle;
- top-frame lepton helicity angles;
- `cos(theta*_+) cos(theta*_-)`;
- a two-dimensional `cos(theta*_+)` versus `cos(theta*_-)` map.

Production-only quantities should remain compatible between `sc` and `iso`.
Decay-angle distributions should change. `LR100_sc` and `RL100_sc` should also
show polarization-dependent rates and angular shapes.

## Interpretation limits

### Factorized decays

These samples use narrow-width factorization. Full spin correlations are kept
in `sc`, but off-shell top/W effects, singly resonant and nonresonant diagrams,
and their interference are not equivalent to a complete six-fermion matrix
element. After validation, compare one point to the full final states

```text
e- e+   -> b e+ nu_e bbar mu- anti-nu_mu
mu- mu+ -> b e+ nu_e bbar mu- anti-nu_mu
```

### 500 GeV versus threshold

The supplied point is for continuum validation. A later 365 GeV/toponium
campaign must state the actual threshold treatment. Plain LO continuum samples
are useful for detector studies but are not precision threshold predictions.

### Polarization convention

Beam order is always negative lepton first and positive antilepton second:

```sindarin
beams = e1, E1
```

or

```sindarin
beams = e2, E2
```

Pure LR uses

```sindarin
beams_pol_density  = @(-1), @(+1)
beams_pol_fraction = 100%, 100%
```

and pure RL reverses the signs. Validate this convention numerically before
constructing partially polarized mixtures.

## References

- WHIZARD project/manual: `https://whizard.hepforge.org/`
- Public source: `https://gitlab.tp.nt.uni-siegen.de/whizard/public`
- W. Kilian, T. Ohl, J. Reuter, Eur. Phys. J. C 71 (2011) 1742.
- J. Reuter et al., *Top Physics in WHIZARD*, arXiv:1602.08035.

## Production gate

Require all of the following before scaling up:

1. all 12 files parse and integrate;
2. integration uncertainties meet the chosen target;
3. `ee` and `mumu` agree before ISR and beam spectra;
4. `sc` and `iso` normalizations agree while decay-angle shapes differ;
5. LHE final-state content and ancestry are correct.
