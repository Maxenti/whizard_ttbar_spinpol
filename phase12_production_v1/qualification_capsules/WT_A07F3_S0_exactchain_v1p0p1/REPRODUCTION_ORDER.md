# Recommended qualification replay order

## 1. Phase 10

Start with:

    qualification_sources/phase10A_production_definition/

Use the preserved manifest/config/model/seed evidence to establish the
hard-process production contract.

Relevant reusable support code is under:

    repo_support/scripts/production/
    repo_support/scripts/sindarin/

## 2. Phase 11A

Replay MPI/VAMP implementation qualification using:

    qualification_sources/phase11A_integration_qualification/
    qualification_sources/phase11_mpi_integration_qualification_v1/
    qualification_sources/mpi_qualification/

Cross-check against:

    provenance/

## 3. Phase 11B

Reproduce the integration-prescription comparison in the historical
order A -> B -> C, with D conditional.

Do not select a stochastic grid after looking at which replica gives
the most favorable diagnostics.

## 4. Phase 11C

Replay frozen-grid reuse validation from:

    qualification_sources/phase11_grid_reuse_validation_v1/

Require statistical compatibility between the predetermined single-grid
sample and the independent multi-grid reference.

## 5. Phase 11D

Replay generation scaling/resource checks from the preserved
production-readiness sources.

The production target to recover is:

    one MPI rank
    25k hard events per shard

## 6. Phase 11E

Replay the exact-chain rehearsal from:

    qualificatsources/phase11_production_readiness_v1/

The rehearsal chain must match the frozen Phase-12 production chain.

## 7. Phase 12

Once qualification passes, use:

    ../../frozen_recipe_capsules/WT_A07F3_S0_exactchain_v1p0p1/

and verify output against:

    ../../production_closeout_v1/WT_A07F3_S0_exactchain_v1p0p1/
