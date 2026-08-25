# FCC Winter2023 reference control

Official card used for comparison:
`FCCee/Generator/Whizard/v3.0.3/wzp6_ee_SM_tt_tlepTlep_noCKMmix_keepPolInfo_ecm365.sin`

Key facts from the official Winter2023 card:
- WHIZARD 3.1.0 (key4hep-stack/2023-04-08)
- 365 GeV
- resonance history enabled, on-shell limit 10, background factor 0
- W+/W-/t/tbar restrictions
- polarized final-state declarations
- Gaussian beam spread 0.221% on both beams, then ISR
- integration schedule `10:100000:"gw", 10:200000:""`

This suite deliberately separates **schedule comparison** from **physics-model comparison**:
- A07+F3 reproduces the exact Winter2023 iteration counts under the current qualified WHIZARD3.1.8 VAMP2+rng_stream runtime.
- `FCCLEGACY_S*` uses current WHIZARD3.1.8 with VAMP+TAO and the exact Winter2023 iteration counts, but still inherits the current project source physics rather than silently adding the historical Gaussian spread.

Neither is claimed to be a byte-for-byte reproduction of the old WHIZARD3.1.0 production.
