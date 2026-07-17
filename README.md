# WHIZARD polarized ttbar production and QIS framework

This repository contains two connected, independently validated layers:

1. **WHIZARD production:** ISR-enabled, longitudinally polarized, spin-correlated `e+e- -> ttbar` and `mu+mu- -> ttbar` LHE generation with HTCondor/EOS production, normalization, collection, and validation.
2. **Top-spin/QIS framework:** PYTHIA8/HepMC3 showering, truth and particle-level observables, complete spin-density-matrix tomography, detector/reconstruction closure, and advanced QIS/theory extensions.

The accepted hard-process campaign is:

```text
/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/
  production/500GeV_ISR_sc_v1
```

It contains eight merged samples, 100,000 events each, covering:

- `ee` and `mumu` beams;
- `LR100` and `RL100` longitudinal helicity configurations;
- `epmum` and `mupem` opposite-flavour dilepton assignments;
- incoming-lepton ISR;
- exact spin-correlated factorized top decays.

Production validation passed:

```text
raw:   1360 / 1360 PASS
final: 1448 / 1448 PASS
WARN:  0
FAIL:  0
```

## QIS framework

Read [README_QIS.md](README_QIS.md) for installation and framework usage.

Key documentation:

- [Quick start](docs/qis/QUICKSTART.md)
- [Architecture](docs/qis/ARCHITECTURE.md)
- [Physics conventions](docs/qis/PHYSICS_CONVENTIONS.md)
- [Spin-density-matrix reconstruction](docs/qis/SPIN_DENSITY_MATRIX.md)
- [QIS observables](docs/qis/QIS_OBSERVABLES.md)
- [PYTHIA8 configuration](docs/qis/PYTHIA_CONFIGURATION.md)
- [HTCondor workflow](docs/qis/CONDOR_WORKFLOW.md)
- [Level B detector/reconstruction](docs/qis/LEVEL_B.md)
- [Level C research extensions](docs/qis/LEVEL_C.md)
- [Validation](docs/qis/VALIDATION.md)
- [Limitations](docs/qis/LIMITATIONS.md)

## Fast validation

```bash
source setup_lxplus.sh
python3 -m pip install --user -e '.[all]'
pytest -q tests/qis
qis-validate --output validation/qis_framework_validation
```

## Production workflow

The established production scripts remain under `scripts/production/`. Their operational guide is:

```text
scripts/production/README.md
```

The initial historical starter README is retained at:

```text
docs/qis/WHIZARD_PRODUCTION_HISTORY.md
```

## Filesystem contract

```text
AFS: code, Git, builds, Condor control files
worker scratch: WHIZARD/PYTHIA/analysis execution
EOS: persistent LHE, HepMC3, ntuples, tomography, plots, reports
```

Do not overwrite accepted hard-process outputs when adding shower, detector, machine-spectrum, EFT, NLO, or off-shell variants. Use separately named campaigns with explicit provenance.
