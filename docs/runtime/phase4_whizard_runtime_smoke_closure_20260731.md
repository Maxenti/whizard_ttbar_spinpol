# Phase 4 WHIZARD Runtime Smoke Closure — 2026-07-31

This note closes the Phase 4 SINDARIN runtime-smoke gate for the
`full6f_365gev_ee_ttbar_spinpol_v1` campaign under the pinned LCG runtime:

```text
/cvmfs/sft-nightlies.cern.ch/lcg/views/devkey-head/Fri/x86_64-el9-gcc14-opt/setup.sh
WHIZARD 3.1.8
PYTHIA 8.316
HepMC3 3.03.01
```

The static card renderer and validator passed before this note was written. The
runtime closure adds five explicit WHIZARD smoke tests covering the representative
syntax and physics-channel branches needed before moving to integration,
showering, and production planning.

## Smoke matrix

| Smoke | Representative | Runtime meaning | Result |
|---|---|---|---|
| unpolarized dilepton | `proc_epmum` | baseline no-polarization card; ISR-only 365 GeV beams; LHE output | PASS |
| LR100 dilepton | `proc_epmum` | `beams_pol_density = @(-1), @(+1)` with `100%, 100%` fractions | PASS |
| RL100 dilepton | `proc_epmum` | `beams_pol_density = @(+1), @(-1)` with `100%, 100%` fractions | PASS |
| Wminus semileptonic | `proc_epjets_Wminus_ubar_d` | semileptonic Wminus representative; validates `anti_u -> ubar` | PASS |
| Wplus semileptonic | `proc_emjets_Wplus_u_dbar` | semileptonic Wplus representative; validates `anti_d -> dbar` | PASS |

All five smoke tests finished with `WHIZARD_SMOKE_RC=0`, WHIZARD reported no
errors, and the hidden error/fallback checks found no `*** ERROR`, `*** FATAL`,
`circe1:error`, `falling back`, unknown-particle, or syntax failures.

## Runtime evidence on EOS

```text
/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/runs/phase4_whizard_unpol_epmum_clean_smoke_20260731T165841Z
/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/runs/phase4_whizard_LR100_epmum_pol_smoke_20260731T173043Z
/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/runs/phase4_whizard_RL100_epmum_pol_smoke_20260731T173925Z
/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/runs/phase4_whizard_unpol_epjets_Wminus_ubar_d_smoke_20260731T174113Z
/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/runs/phase4_whizard_unpol_emjets_Wplus_u_dbar_smoke_20260731T175215Z
```

Each run directory should contain a `RUNTIME.txt`, `whizard_smoke.log`, LHE/EVX
output, and `SHA256SUMS.txt` after sealing.

## Source commits relevant to this closure

```text
fdf07de Fix WHIZARD 3.1.8 runtime-proven unpolarized SINDARIN cards
465688e Add runtime-proven WHIZARD polarization rendering
```

The renderer now performs WHIZARD-3.1.8-compatible post-render polarization
configuration:

- `_unpol_` generated cards omit the `polarization.inc` include.
- `_LR100_` generated cards use `beams_pol_density = @(-1), @(+1)` and `beams_pol_fraction = 100%, 100%`.
- `_RL100_` generated cards use `beams_pol_density = @(+1), @(-1)` and `beams_pol_fraction = 100%, 100%`.

## Scope of closure

This closes SINDARIN runtime syntax and representative process execution for
Phase 4. It does **not** certify production integration quality, PYTHIA
showering, HepMC identity propagation, spin-density reconstruction, or Delphes
pairing. Those remain later phase gates.
