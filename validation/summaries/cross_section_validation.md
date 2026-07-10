# WHIZARD cross-section validation

- Manifest: `/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/metadata/sample_manifest.csv`
- Samples with parsed cross sections: **12/12**
- Pending or unparsable samples: **0**
- Completed checks: **24**
- Failed checks: **0**

| Check | Sample A | Sample B | Relative difference | Pull | Verdict |
|---|---|---|---:|---:|---|
| integration_precision | `ee_ttbar_emu_LR100_iso_500GeV` | `` | — | — | **PASS** |
| integration_precision | `ee_ttbar_emu_LR100_sc_500GeV` | `` | — | — | **PASS** |
| integration_precision | `ee_ttbar_emu_RL100_iso_500GeV` | `` | — | — | **PASS** |
| integration_precision | `ee_ttbar_emu_RL100_sc_500GeV` | `` | — | — | **PASS** |
| integration_precision | `ee_ttbar_emu_unpol_iso_500GeV` | `` | — | — | **PASS** |
| integration_precision | `ee_ttbar_emu_unpol_sc_500GeV` | `` | — | — | **PASS** |
| integration_precision | `mumu_ttbar_emu_LR100_iso_500GeV` | `` | — | — | **PASS** |
| integration_precision | `mumu_ttbar_emu_LR100_sc_500GeV` | `` | — | — | **PASS** |
| integration_precision | `mumu_ttbar_emu_RL100_iso_500GeV` | `` | — | — | **PASS** |
| integration_precision | `mumu_ttbar_emu_RL100_sc_500GeV` | `` | — | — | **PASS** |
| integration_precision | `mumu_ttbar_emu_unpol_iso_500GeV` | `` | — | — | **PASS** |
| integration_precision | `mumu_ttbar_emu_unpol_sc_500GeV` | `` | — | — | **PASS** |
| ee_vs_mumu | `ee_ttbar_emu_unpol_sc_500GeV` | `mumu_ttbar_emu_unpol_sc_500GeV` | 1.55915828102e-05 | 1.76004558205 | **PASS** |
| ee_vs_mumu | `ee_ttbar_emu_unpol_iso_500GeV` | `mumu_ttbar_emu_unpol_iso_500GeV` | 3.30070248519e-06 | 0.372594444849 | **PASS** |
| ee_vs_mumu | `ee_ttbar_emu_LR100_sc_500GeV` | `mumu_ttbar_emu_LR100_sc_500GeV` | 5.39626198329e-06 | 0.649222557578 | **PASS** |
| ee_vs_mumu | `ee_ttbar_emu_LR100_iso_500GeV` | `mumu_ttbar_emu_LR100_iso_500GeV` | 1.27429921183e-05 | 1.5382123098 | **PASS** |
| ee_vs_mumu | `ee_ttbar_emu_RL100_sc_500GeV` | `mumu_ttbar_emu_RL100_sc_500GeV` | 6.86647330882e-06 | 0.679181260691 | **PASS** |
| ee_vs_mumu | `ee_ttbar_emu_RL100_iso_500GeV` | `mumu_ttbar_emu_RL100_iso_500GeV` | 1.17187460662e-05 | 1.16162074302 | **PASS** |
| sc_vs_iso_normalization | `ee_ttbar_emu_unpol_sc_500GeV` | `ee_ttbar_emu_unpol_iso_500GeV` | 2.40714321932e-06 | 0.27212272628 | **PASS** |
| sc_vs_iso_normalization | `ee_ttbar_emu_LR100_sc_500GeV` | `ee_ttbar_emu_LR100_iso_500GeV` | 4.61610263692e-06 | 0.555665625599 | **PASS** |
| sc_vs_iso_normalization | `ee_ttbar_emu_RL100_sc_500GeV` | `ee_ttbar_emu_RL100_iso_500GeV` | 6.30189483563e-06 | 0.624673654775 | **PASS** |
| sc_vs_iso_normalization | `mumu_ttbar_emu_unpol_sc_500GeV` | `mumu_ttbar_emu_unpol_iso_500GeV` | 1.46980235444e-05 | 1.65676763266 | **PASS** |
| sc_vs_iso_normalization | `mumu_ttbar_emu_LR100_sc_500GeV` | `mumu_ttbar_emu_LR100_iso_500GeV` | 2.73062749825e-06 | 0.329434057044 | **PASS** |
| sc_vs_iso_normalization | `mumu_ttbar_emu_RL100_sc_500GeV` | `mumu_ttbar_emu_RL100_iso_500GeV` | 1.22833245394e-05 | 1.21497981079 | **PASS** |

## Interpretation

- `ee_vs_mumu` should agree before ISR and machine spectra are enabled.
- `sc_vs_iso_normalization` should agree in normalization; the intended
  difference is in decay-angle shapes.
- A pair fails only when both the relative difference and pull exceed
  their thresholds.
- These checks do not replace LHE-level angular-distribution validation.
