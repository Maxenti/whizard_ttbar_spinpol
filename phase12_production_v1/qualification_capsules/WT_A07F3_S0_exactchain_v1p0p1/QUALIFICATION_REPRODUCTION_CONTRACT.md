# Phase 10/11 qualification reproduction contract

Recipe ID:

`WT_A07F3_S0_exactchain_v1p0p1`

Base production-freeze tag:

`phase12-WT_A07F3_S0-exactchain-v1p0p1-frozen`

Base production-freeze commit:

`a48e46e802d6c29e70666022a9b8777766714492`

This capsule supplements the immutable Phase-12 production freeze.

It preserves the small source/configuration/validation surface required
to understand and rerun the qualification that led to the Phase-12
production recipe. Large Monte Carlo outputs, large workspaces, and
other bulky runtime artifacts are intentionally not duplicated in Git.

The final Phase-12 production recipe and formal production data
closeout remain in:

- `phase12_production_v1/frozen_recipe_capsules/WT_A07F3_S0_exactchain_v1p0p1/`
- `phase12_production_v1/production_closeout_v1/WT_A07F3_S0_exactchain_v1p0p1/`

## Phase 10 — production-definition qualification

Phase 10 establishes the hard-process production contract.

The preserved evidence covers:

1. the 365 GeV full-six-fermion process definition;
2. the WT resonance-restricted signal definition;
3. beam/polarization assumptions;
4. active WHIZARD model and parameter provenance;
5. runtime card rendering;
6. seed syntax and deterministic seed handling;
7. seed replay checks;
8. representative LHE headers and init blocks;
9. production worker replay and localization checks;
10. qualification/production manifest validation.

The authoritative recovered Phase-10 evidence is under:

`qualification_sources/phase10A_production_definition/`

## Phase 11A — MPI/VAMP implementation qualification

This phase establishes that the selected parallel WHIZARD integration
implementation behaves correctly before using it for production
qualification.

Preserved inputs/evidence include the Phase-11A campaign tree,
MPI qualification tree, qualified-worker provenance, rank-merge
checks, worker/runtime scripts, and encoded-iteration support.

## Phase 11B — integration-prescription qualification

The qualification logic was:

- A0/A1/A2: initial independent prescription replicas;
- B0: predetermined candidate for the stronger B prescription;
- B1/B2: independent qualification replicas when B0 passes;
- C0: over-integration/saturation check;
- C1/C2: required only if C must become the qualified prescription;
- D: conditional stronger prescription if C has not saturated.

The production grid is never selected by choosing the replica with
the most attractive statistical fluctuation.

The predetermined qualified grid is S0/B0 once the complete B
prescription passes the predefined gates.

Qualification checks include:

- cross-section stability;
- reported integration uncertainty;
- integration convergence;
- generation diagnostics;
- unweighting behavior;
- excess-weight behavior;
- consistency among independent replicas.

## Phase 11C — single frozen-grid reuse validation

A single qualified frozen grid was tested against an independent
multi-grid reference.

The acceptance criterion is statistical compatibility of predefined
physics observables, not byte-for-byte histogram identity.

The qualification additionallhat generation does not mutate
or reintegrate the frozen workspace.

## Phase 11D — generation scaling

Generation throughput/resource behavior is checked at increasing shard
sizes, including the qualified 25k-event production point.

The study covers:

- events per second;
- memory behavior;
- output integrity;
- unweighting efficiency;
- excess-weight diagnostics;
- generation-rank behavior.

The Phase-12 production choice is one MPI rank per generation shard and
25k hard events per shard.

## Phase 11E — exact-chain rehearsal

An approximately 100k-event rehearsal uses the same production chain
intended for Phase 12:

WHIZARD frozen grid
-> raw LHE
-> canonical ISR normalization
-> history-preserving serializer
-> strict topology validation
-> PYTHIA
-> HepMC3

Validation RNG seeds are kept disjoint from final Phase-12 production
seeds and validation events are not reused in the final physics sample.

## Phase-12 production rule established by Phase 10/11

The qualified production architecture is:

- WHIZARD 3.1.8;
- sqrt(s) = 365 GeV;
- LR100;
- WT-restricted full-six-fermion process;
- VAMP2;
- rng_stream;
- predetermined frozen S0 grid;
- one MPI rank per generation job;
- 25k hard events per shard;
- independent hard-generation seeds;
- independent PYTHIA seeds;
- WHIZARD ISR retained;
- PYTHIA ISR disabled;
- PYTHIA FSR enabled;
- MPI disabled in PYTHIA;
- top decay ownership retained by WHIZARD;
- exact history-preserving serialization.

## Authority rule

When duplicate source files exist:

1. exact snapshots embedded in qualification campaign directories take
   precedence;
2. frozen Phase-12 recipe files take precedence for final production;
3. files under `repo_support/` are convenience copies of the current
   working-tree implementations and their Git state is recorded
   explicitly.

Historical failed/diagnostic experiments are context, not qualified
production recipes.

A change to process physics, beam configuration, perturbative order,
integration prescription, ISR/decay ownership, nominal PYTHIA policy,
history serialization, or materially different generator versions
requires a new qualification.
