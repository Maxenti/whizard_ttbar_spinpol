# lxplus runbook — Phase 11 unrestricted stability scan (480 DAG nodes)

## 1. Stage and unpack the package

Recommended EOS archive location:

`/eos/user/c/cglenn/FCCWork/whizard/packages/phase11_unrestricted_stability_scan_480_v1.tar.gz`

Recommended AFS package directory:

`/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/phase11_diagnostics/excess_weight_rootcause_v1/unrestricted_stability_scan_480_v1/package_v1`

## 2. Prepare a concrete campaign

The package freezes the current unrestricted source tree into the timestamped
submission directory and refuses to prepare if the original source-card SHA256
differs from the frozen Phase-11 value.

Expected unrestricted source SHA256:

`2246641146c35f49a1825344343a697cbbf6542828906b10cf7c06a3f81384f9`

The concrete DAG contains exactly:

- 120 adaptive parent nodes (15 Axx prescriptions x 8 seeds)
- 360 fixed child nodes (3 descendants per parent)
- 480 total physics nodes

## 3. Schedd handling

If other diagnostic clusters are already running, record their schedd before
calling `myschedd bump`. A bump changes the schedd used for new submissions; it
does not migrate already-running jobs and does not allocate a private CPU pool.

The package submit helper accepts `--bump-schedd` and records the selected schedd
for later monitoring.

## 4. DAG dependency behavior

Each parent produces an exact PHS+VG2 workspace. Its F0/F1/F2 children are held by
DAGMan until the parent exits successfully. A failed parent therefore prevents its
three descendants from running.

For fixed children, the worker restores the exact parent workspace and requests:

`<adaptive prefix>,<fixed suffix>`

The worker requires VAMP2 reuse evidence and fails if WHIZARD initializes a new
grid. This is deliberately strict.

## 5. Do not cherry-pick

The unit of scientific interpretation is the prescription family across all eight
predetermined seeds. Do not replace a physically bad seed with a new seed. A
technical rerun must use the identical node definition.

No result from this scan becomes a production grid solely because it looks best.
