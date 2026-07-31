# Phase 7 canonical-v2 representative bridge closure — 2026-07-31

Status: `PASS_WITH_RUNTIME_WARNINGS`

This note records the representative Phase 7 runtime bridge closure for the
`full6f_365gev_ee_ttbar_spinpol_v1` campaign under the pinned LCG runtime:

```text
/cvmfs/sft-nightlies.cern.ch/lcg/views/devkey-head/Fri/x86_64-el9-gcc14-opt/setup.sh
WHIZARD 3.1.8
PYTHIA 8.316
HepMC3 3.03.01
```

The required runtime chain is:

```text
WHIZARD full-six-fermion LHE
→ canonical-v2 ISR-history repair
→ external PYTHIA8
→ HepMC3
→ Phase 7 runtime validator
```

## Representative samples

| Sample | Coverage | Status | Events | Notes |
|---|---|---:|---:|---|
| `unpol_epmum` | Baseline unpolarized dilepton bridge | `PASS_WITH_RUNTIME_WARNINGS` | 100 | accepted 100/100; PYTHIA runtime warnings observed |
| `LR100_epmum` | Polarized e-_L e+_R representative bridge | `PASS_WITH_RUNTIME_WARNINGS` | 100 | accepted 100/100; PYTHIA runtime warnings observed |
| `unpol_epjets_Wminus_ubar_d` | Semileptonic Wminus anti-up branch bridge | `PASS_WITH_RUNTIME_WARNINGS` | 100 | accepted 100/100; PYTHIA runtime warnings observed |

## EOS evidence

```text
/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/runs/phase5_phase7_bridge_unpol_epmum_lhe_20260731T180140Z
/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/runs/phase7_bridge_LR100_epmum_20260731T183107Z
/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/runs/phase7_bridge_unpol_epjets_Wminus_ubar_d_20260731T183157Z
```

Each run directory contains the raw WHIZARD LHE, canonical-v2 LHE, canonical
summary JSON, PYTHIA/HepMC log, HepMC3 output, metadata JSON, runtime note,
and SHA256 checksums.

## Interpretation

The original WHIZARD LHE uses an extended ISR-history representation with
beam leptons, post-ISR bridge leptons, explicit ISR photons, and hard final
states attached to the post-ISR leptons. The Phase 7 bridge requires
canonical-v2 repair before PYTHIA showering. This repair preserves the
surviving final-state four-vectors while promoting nominal beams, removing
post-ISR bridge leptons, rewiring hard-system mothers, and removing WHIZARD
`sqme_prc` diagnostic weights.

The representative bridge is therefore closed for unpolarized dilepton,
polarized dilepton, and semileptonic Wminus anti-up topology. The samples are
not yet final production shower certification because PYTHIA reported
runtime shower warnings, especially negative dipole mass warnings. Those
warnings need tracking and tuning before large-scale production.

## Closure directory

```text
/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/inspection_outputs/phase7_representative_bridge_closure_20260731T183405Z
```
