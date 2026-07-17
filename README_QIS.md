# WHIZARD + PYTHIA8 top-spin and quantum-information framework

This repository overlay turns the validated WHIZARD polarized `ttbar` production into a reproducible analysis framework spanning generator truth, showered particle level, parametric reconstruction, spin-density-matrix tomography, and advanced quantum-information observables.

The framework is organized into three interoperable levels:

- **Level A — generator and particle-level QIS:** LHE parsing, PYTHIA8 showering, HepMC3 export, truth ancestry, arbitrary spin bases, complete 15-parameter two-qubit tomography, bootstrap covariance, physical density-matrix projection, and standard QIS observables.
- **Level B — detector and reconstruction studies:** parametric detector response, dilepton and semileptonic reconstruction, response matrices, regularized unfolding, closure tests, nuisance variations, and systematic covariance construction.
- **Level C — research extensions:** longitudinal polarization mixtures, transverse-polarization generation contracts, EFT polynomial reweighting, CP-odd observables, optimized spin bases, multi-energy combinations, NLO/differential reweighting, state distances, Fisher information, steering, and magic diagnostics.

The implementation is intentionally modular. Each level consumes explicit tables or density matrices produced by the previous level, so later detector, EFT, or machine-specific additions do not require rewriting the Level A physics definitions.

## Validated source campaign

The default configuration targets the accepted campaign:

```text
/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/
  production/500GeV_ISR_sc_v1
```

It contains eight merged samples:

```text
ee_ttbar_epmum_LR100_sc_ISR_500GeV
ee_ttbar_epmum_RL100_sc_ISR_500GeV
ee_ttbar_mupem_LR100_sc_ISR_500GeV
ee_ttbar_mupem_RL100_sc_ISR_500GeV
mumu_ttbar_epmum_LR100_sc_ISR_500GeV
mumu_ttbar_epmum_RL100_sc_ISR_500GeV
mumu_ttbar_mupem_LR100_sc_ISR_500GeV
mumu_ttbar_mupem_RL100_sc_ISR_500GeV
```

The original production passed 1,360/1,360 raw checks and 1,448/1,448 final checks. The framework does not modify those authoritative LHE files.

## Quick start on lxplus

```bash
cd /afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol
source setup_lxplus.sh

python3 -m pip install --user -e '.[all]'
./scripts/qis/build_qis.sh

qis-validate --output validation/qis_framework_validation
```

Build truth ntuples from the merged final LHE files:

```bash
qis-make-ntuples \
  --config configs/qis/level_a_500GeV_ISR_sc_v1.yaml
```

Run tomography for one table:

```bash
qis-tomography \
  /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/qis/campaigns/500GeV_ISR_sc_v1/ntuples/lhe/ee_ttbar_epmum_LR100_sc_ISR_500GeV.parquet \
  --config configs/qis/level_a_500GeV_ISR_sc_v1.yaml \
  --output-dir /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/qis/campaigns/500GeV_ISR_sc_v1/tomography/ee_ttbar_epmum_LR100_sc_ISR_500GeV
```

Prepare PYTHIA jobs without submitting:

```bash
python3 scripts/showering/submit_showering.py \
  --config configs/qis/level_a_500GeV_ISR_sc_v1.yaml
```

Submit after inspecting the generated itemdata and submit file:

```bash
python3 scripts/showering/submit_showering.py \
  --config configs/qis/level_a_500GeV_ISR_sc_v1.yaml \
  --submit
```

## Repository additions

```text
CMakeLists.txt
cmake/
include/qis/
src/qis/
qis_ttbar/
configs/qis/
configs/pythia/
configs/production/production_500GeV_ISR_iso_validation_v1.csv
scripts/qis/
scripts/showering/
condor/qis/
tests/qis/
docs/qis/
```

## Core conventions

- The incoming negative lepton defines the positive beam direction.
- Spin axes are stored in `(k, r, n)` order.
- `k` is the top helicity direction in the `ttbar` rest frame.
- `n` is normal to the production plane.
- `r = n x k` completes a right-handed basis.
- The antitop uses its own helicity axis and a right-handed partner basis.
- The charged-lepton analyzing powers are configurable and default to one.
- The full density matrix and its covariance are primary outputs; nonlinear QIS measures are derived products.

Read `docs/qis/PHYSICS_CONVENTIONS.md` before comparing coefficients to another code or paper because sign and axis conventions can differ.

## Output philosophy

Persistent products are written to EOS. Code, Git history, and Condor control files remain on AFS. Event generation and heavy processing occur in worker scratch. Every workflow writes a manifest or metadata sidecar with configuration, seeds, event counts, and checksums where practical.

## Scope and limitations

The framework is fully implemented as a reusable computational system, but physical fidelity still depends on inputs supplied to it:

- Level B uses a configurable parametric detector unless replaced by a real full-simulation/reconstruction adapter.
- Level C EFT and NLO components apply supplied coefficient or weight models; they do not invent matrix elements or perturbative calculations.
- Transverse polarization requires coherent direct generation in WHIZARD and cannot be reconstructed from incoherent LR/RL mixtures.
- Threshold precision requires an appropriate off-shell/resummed generator treatment beyond the default 500 GeV factorized campaign.

These boundaries are explicit contracts rather than silent approximations.

## Spin-15 production qualification

The next production gate verifies beam polarization and the complete two-spin
coefficient set:

```text
B1k B1r B1n B2k B2r B2n
Ckk Crr Cnn Ckr Crk Ckn Cnk Crn Cnr
```

See:

- `docs/qis/SPIN15_VALIDATION.md`
- `scripts/qis/run_next_production_gate.sh`
- `scripts/qis/run_spin15_qualification_gate.sh`
- `scripts/qis/plot_spin15_distributions.py`
- `scripts/qis/validate_spin15_gate.py`
