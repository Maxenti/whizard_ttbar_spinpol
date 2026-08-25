# WT_A07F3_S0_exactchain_v1p0p1 production contract

## Status

This recipe is the qualified Phase-12 LO production recipe for

- e+ e- collisions at sqrt(s) = 365 GeV,
- LR100 beam configuration,
- WT-restricted full six-fermion
  e+ e- -> b bbar e+ nu_e mu- anti-nu_mu,
- WHIZARD hard generation followed by PYTHIA8 shower/hadronization.

The Phase-12 1M sample is frozen and must not be silently modified.

## Hard generation

Qualified hard-generation conditions:

- WHIZARD 3.1.8.
- LO matrix element.
- VAMP2.
- rng_stream.
- VAMP simple balancing.
- predetermined qualified S0 grid.
- one MPI rank per generation job.
- OMP_NUM_THREADS=1.
- 25,000 hard events per production shard.

The S0 grid is an importance-sampling representation of the same fixed
integrand. Event independence comes from independent generation RNG seeds,
not from regenerating an integration grid for each shard.

Do not reintegrate per production shard.

For additional statistics with unchanged physics, reuse the qualified grid
and use a new, disjoint hard-event seed namespace.

## Resonance/history contract

The sample is a WT-restricted full-six-fermion sample.

Serialized resonance presence is not required to be identical event by event.
The validated record can contain different explicit top/W history-presence
classes.

The preparation chain must:

1. perform canonical ISR normalization;
2. preserve existing resonance/history information;
3. perform strict topology validation;
4. never synthesize W bosons;
5. never add/remove hard-process particles simply to regularize history.

## PYTHIA contract

Canonical nominal policy:

- WHIZARD ISR retained.
- PYTHIA ISR OFF.
- PYTHIA FSR ON.
- MPI OFF.
- hadronization ON.
- unstable-particle decays ON.
- PYTHIA hard-process resonance decays OFF.
- top decay OFF (`6:mayDecay=off`).
- `TimeShower:QEDshowerByL=on`.
- `TimeShower:QEDshowerByQ=on`.
- `SpaceShower:QEDshowerByL=off`.
- `TimeShower:QEDshowerByGamma=off`.
- `HadronLevel:QED=off`.

Qualified PYTHIA version: 8.315.
Qualified HepMC3 version: 3.3.1.

For future production, use the frozen
`frozen_exact_worker_v1p0p1_string_join`
worker implementation.

The two historical string-joining occurrences in the original 1M campaign
were recoverable and did not invalidate the sample. The corrected worker is
the canonical future implementation.

## QED systematic decision

The controlled same-hard-event 2x2 study tested:

- G0_H0: gamma conversion OFF, hadron QED OFF — nominal;
- G1_H0: gamma conversion ON, hadron QED OFF;
- G0_H1: gamma conversion OFF, hadron QED ON;
- G1_H1: both ON.

The hard spin representation is identical by construction across all four
samples. No statistically compelling Spin-15 bias requiring a production
change was observed.

Therefore G0_H0 remains the nominal configuration.

The three other configurations are retained as generator-systematic
variations.

## Changes that DO NOT automatically require grid requalification

If the physics definition and software recipe are unchanged:

- increasing event count;
- changing number of output shards;
- changing production bookkeeping/tag;
- using new independent generation and PYTHIA seeds.

These still require normal production smoke tests and validation.

## Changes that DO require a new qualification

At minimum:

- center-of-mass energy;
- beam polarization/helicity definition;
- process/final-state definition;
- resonance restrictions;
- matrix-element oer, including LO -> NLO;
- NLO/PS matching prescription;
- integration prescription;
- materially different WHIZARD version;
- materially different PYTHIA version;
- ISR/FSR ownership;
- top-decay ownership;
- nominal QED shower policy;
- history-serialization algorithm;
- any change that alters event weights or the hard integrand.

Do not call such a campaign `WT_A07F3_S0_exactchain_v1p0p1`.
Create and qualify a new recipe identifier.

## Required future-production validation

Every production using this recipe should retain:

- exact recipe checksum;
- exact software/environment record;
- grid/workspace checksum;
- shard manifest;
- event ranges;
- hard RNG seeds;
- PYTHIA RNG seeds;
- input LHE checksums;
- output HepMC checksums;
- accepted/failed event counts;
- bad-weight count;
- known and unknown PYTHIA-error accounting;
- preparation/history validation;
- final production gate.

No shard should be selected because it has the "best" stochastic behavior.
Predetermined seed/grid choices must be preserved.
