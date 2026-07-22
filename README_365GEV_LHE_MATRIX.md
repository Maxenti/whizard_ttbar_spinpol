# 365 GeV polarized ttbar LHE matrix package

This package prepares, runs, and validates the complete 16-sample WHIZARD LHE
matrix at 365 GeV:

- initial states: `ee`, `mumu`;
- mixed-flavour assignments: `epmum`, `mupem`;
- beam polarizations: `LR100`, `RL100`;
- decay-spin modes: `sc`, `iso`;
- WHIZARD ISR enabled in recoil mode for every sample.

The package never edits the qualified 500 GeV `.sin.in` templates. It creates
new 365 GeV `input.sin` files under a separate campaign root, records template
and input hashes, and validates each generated LHE before campaign collection.

## Profiles

- `pilot`: 1,000 events per sample, 16,000 total events. Run this first.
- `production_10k`: 10,000 events per sample, 160,000 total events. Run only
  after the pilot matrix passes.

This package stops at validated LHE. Pythia, HepMC, ntuple extraction, and the
Spin-15 paper analysis belong to the next stage.

Detailed commands are in:

```text
docs/qis/paper_spin_365GeV_lhe_matrix.md
```
