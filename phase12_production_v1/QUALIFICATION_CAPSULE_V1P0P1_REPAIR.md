# Phase 10/11 qualification capsule packaging correction v1p0p1

Recipe:

`WT_A07F3_S0_exactchain_v1p0p1`

## Original qualification tag

`phase12-WT_A07F3_S0-exactchain-v1p0p1-qualification-v1`

Target commit:

`d84d9806c9fb93e78be4e74fb22f9d5437c91922`

The original qualification-v1 Git tag is preserved as historical
provenance but is superseded for reproduction use.

## Problem

The capsule was constructed and internally checksum-validated correctly
in the working tree.

However, the original staging command used ordinary `git add`.

Several qualification-capsule files matched existing repository
.gitignore rules. Git therefore omitted those files from the commit
without changing the already-generated
`QUALIFICATION_CAPSULE_SHA256SUMS.txt`.

The archive-level verifier correctly detected this packaging mismatch.
The first reported missing member was:

`provenance/phase11_mpi_rank_merge_pre_regression_20260811T202402Z/repository_worktree.patch`

This was a Git packaging/staging defect only.

It does not alter:

- Phase-10 physics/process qualification;
- Phase-11 integration qualification;
- Phase-11 grid-reuse qualification;
- Phase-11 generation/rehearsal conclusions;
- the qualified frozen S0 grid;
- Phase-12 production events;
- the Phase-12 production closeout;
- the immutable Phase-12 production tag.

## Correction

v1p0p1 force-stages exactly the files already listed by the existing
qualification capsule SHA256 manifest that were absent from the
qualification-v1 Git object.

No qualification-capsule data files are regenerated or normalized.

All restored manifest members must match their original recorded
SHA256 values before staging.

The prospective Git tree is archived and the capsule verifier is run
against that archive before the correction commit is created.

## Authority

For Phase-10/11 qualification reproduction, use:

`phase12-WT_A07F3_S0-exactchain-v1p0p1-qualification-v1p0p1`

The original `phase12-WT_A07F3_S0-exactchain-v1p0p1-qualification-v1` is superseded and must not be used as
the qualification reproduction tag.
