# Phase 10/11 qualification-reproduction capsule

This is the Git-resident qualification supplement for:

`WT_A07F3_S0_exactchain_v1p0p1`

It is intended to answer not only:

> How do I run the qualified Phase-12 recipe?

but also:

> How was the integration/grid/seed/generation architecture qualified?

The immutable Phase-12 production tag is:

`phase12-WT_A07F3_S0-exactchain-v1p0p1-frozen`

at commit:

`a48e46e802d6c29e70666022a9b8777766714492`

This capsule is deliberately additive. It does not alter the original
production-freeze commit or tag.

## Main directories

- `qualification_sources/phase10A_production_definition/`
  - hard-process definition, runtime/model audit, seed qualification,
    LHE/worker replay evidence.

- `qualification_sources/phase11A_integration_qualification/`
  - initial integration qualification.

- `qualification_sources/phase11_mpi_integration_qualification_v1/`
  - MPI/VAMP integration qualification.

- `qualification_sources/mpi_qualification/`
  - MPI implementation qualification material.

- `qualification_sources/phase11_grid_reuse_validation_v1/`
  - predetermined single-grid versus multi-grid validation.

- `qualification_sources/phase11_production_readiness_v1/`
  - final production-readiness work including later Phase-11 gates.

- `qualification_sources/phase11_historical_diagnostics/`
  - small diagnostic/history records only; these are not authoritative
    production recipes.

- `provenance/`
  - qualified MPI-worker/rank-merge provenance snapshots.

- `repo_support/`
  - current small support scripts/configs useful to replay qualification.
    Their Git working-tree state at capsule creation is recorded.

## Large artifacts

Large LHE/HepMC/ROOT/archive/binary outputs are intentionally not copied
into Git.

Important omitted artifacts are recorded where discoverable in:

`EXTERNAL_ARTIFACT_POINTERS.tsv`

Paths embedded in the copied evidence are also extracted into:

`EXTERNAL_PATH_REFERENCES.txt`

The final qualified production grid/recipe is already frozen in the
Phase-12 recipe capsule, and the final production data are checksum
indexed by the Phase-12 closeout.

## Verification

Run:

    python3 tools/verify_qualification_capsule.py

A successful result must end with:

    QUALIFICATION_CAPSULE_VERIFY=PASS
