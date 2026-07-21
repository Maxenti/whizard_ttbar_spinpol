# WHIZARD ttbar paper-grade spin-tomography upgrade

## Scope

This bundle adds a future-proof, convention-locked analysis layer to:

```text
/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol
```

It consumes the already validated 10k-event Spin-15 ntuples and **does not
replace, rewrite, or invalidate** the passing baseline qualification tree:

```text
/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/qis/qualification/
spin15_gate_10k_sharded_v2
```

The design combines the complete-coefficient and closure logic used in CMS top
spin measurements with the basis and spin-density-matrix convention appropriate
to a lepton collider.

## Physics delivered

The additive package implements:

1. a frozen incoming-positive-lepton `k,r,n` convention;
2. an explicit map from legacy `b1,b2,cij` ntuples to signed charged-lepton analyzers;
3. all six polarization and nine correlation coefficients by exact event moments;
4. a full `15 x 15` coefficient covariance calculated from event estimands;
5. CMS-style one-dimensional angular-shape likelihood fits;
6. a simultaneous unbinned 15-parameter physical density-matrix likelihood;
7. `Cij+Cji`, `Cij-Cji`, symmetric, and antisymmetric combinations;
8. renamed connected correlations `Cconn_ij=Cij-B1iB2j`;
9. lepton-collider trace markers and a separately namespaced CMS trace scalar;
10. normalized angular histograms with full bin covariance;
11. optional differential tomography in reviewed `cos(theta)` and `mtt` bins;
12. raw, Euclidean-projected, and likelihood-fitted density matrices;
13. eigenvalues, purity, partial transpose, negativity, concurrence, entropy, and CHSH maximum;
14. analytic covariance for linear quantities and deterministic bootstrap for nonlinear quantities;
15. synthetic physical-state injection tests;
16. moment-versus-marginal and moment-versus-simultaneous-fit closure;
17. paired LHE/HepMC comparison when stable event keys exist;
18. SC/ISO connected-correlation comparison with full propagated covariance;
19. `epmum/mupem` and `ee/mumu` consistency checks;
20. an independent explicit-Dirac-spinor gamma/Z tree-level benchmark;
21. exact baseline SHA-256 guards before and after analysis;
22. local and HTCondor workflows for expensive joint-bootstrap closure;
23. publication-facing tables, covariance matrices, figures, manifests, and reports.

## Important methodological choices

### Primary linear result

The unconstrained method-of-moments coefficients are the primary unbiased
linear result. They are not replaced by a physical projection.

### Nonlinear quantum quantities

Nonlinear quantities are evaluated using a positive semidefinite density matrix:

- exact Euclidean projection of the raw moment matrix;
- simultaneous Cholesky-parameterized physical likelihood;
- bootstrap propagation.

This avoids calculating concurrence or negativity from an unphysical
finite-statistics matrix.

### Analytic prediction

The independent tree-level benchmark is physically calculated, not fitted from
the generated coefficients. It remains non-strict until the exact WHIZARD input
scheme and the sign of the stored top-angle variable have been reviewed.

That safety lock is intentional. A numerically precise comparison using the
wrong electroweak scheme or axis sign is less correct than an explicitly
labelled diagnostic.

## Installation

From a fresh lxplus shell:

```bash
cd /path/where/the/bundle/was/extracted

./install.sh \
  --repo /afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol
```

The installer:

- backs up every colliding repository file;
- copies the additive package, configs, docs, scripts, and tests;
- does not touch EOS baseline outputs;
- does not patch the existing gate dispatcher unless requested.

To add the optional command:

```bash
./install.sh \
  --repo /afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol \
  --patch-gate
```

This enables:

```bash
scripts/qis/run_next_production_gate.sh paper-spin
```

The optional patch is reversible and timestamp-backed-up.

## Validate after installation

```bash
cd /afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol
source setup_lxplus.sh

python3 -m py_compile \
  qis_ttbar/paper_spin/*.py \
  scripts/qis/*.py

bash -n \
  scripts/qis/run_paper_spin_all.sh \
  scripts/qis/condor/run_paper_spin_shape_closure_job.sh

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
python3 -m pytest -q tests/qis/test_paper_spin_*.py
```

The bundle's isolated test suite contains tests for:

- convention mapping;
- independent Lorentz/basis reconstruction;
- moment estimators and full covariance;
- normalized histogram covariance;
- differential bins;
- density-matrix round trips and projection;
- marginal shape fits;
- simultaneous physical likelihood;
- deterministic bootstrap slicing;
- analytic QED normalization;
- electron/muon universality;
- additive baseline preservation.

## Run the complete local analysis

```bash
cd /afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol
source setup_lxplus.sh

export QUALIFICATION_ROOT=/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/qis/qualification/spin15_gate_10k_sharded_v2
export CONFIG=$PWD/configs/qis/paper_spin_500GeV.yaml
export OUTPUT_ROOT=/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/qis/paper_spin/paper_spin_500GeV_$(date -u +%Y%m%dT%H%M%SZ)

scripts/qis/run_paper_spin_all.sh
```

The workflow performs:

1. baseline checksum snapshot;
2. synthetic injection and shape closure;
3. all-sample tomography;
4. report generation;
5. strict validation;
6. baseline checksum verification;
7. output checksums.

## Review inputs for the analytic benchmark

First create an audit report:

```bash
python3 scripts/qis/audit_paper_spin_inputs.py \
  --repo "$PWD" \
  --qualification-root "$QUALIFICATION_ROOT" \
  --output "$OUTPUT_ROOT/provenance/analytic_input_audit.json"
```

Then review:

```text
configs/qis/paper_spin_sm_parameters.yaml
configs/qis/paper_spin_500GeV.yaml
```

Only after checking the actual WHIZARD model inputs and kinematic column signs:

```yaml
generator_match_reviewed: true
kinematics_map_reviewed: true
mapping_reviewed: true
```

should be enabled for the relevant sections.

## Distributed same-sample moment/shape closure

Create deterministic itemdata:

```bash
export CLOSURE_ROOT=/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/qis/paper_spin/shape_closure_$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p "$CLOSURE_ROOT/logs"

python3 scripts/qis/make_paper_spin_closure_itemdata.py \
  --qualification-root "$QUALIFICATION_ROOT" \
  --config "$CONFIG" \
  --output-root "$CLOSURE_ROOT/results" \
  --itemdata "$CLOSURE_ROOT/itemdata.csv" \
  --replicas 500 \
  --replicas-per-job 20
```

Submit:

```bash
export REPO=$PWD
export itemdata=$CLOSURE_ROOT/itemdata.csv
export log_dir=$CLOSURE_ROOT/logs

condor_submit scripts/qis/condor/paper_spin_shape_closure.sub
```

Collect:

```bash
python3 scripts/qis/collect_paper_spin_shape_closure.py \
  --input-dir "$CLOSURE_ROOT/results" \
  --output "$CLOSURE_ROOT/joint_moment_shape_closure.json"
```

Replica seeds depend only on the base seed and global replica ID. Splitting or
resubmitting jobs therefore does not change the statistical ensemble.

## Output policy

The paper-grade output must be a sibling of, not a child of, the baseline
qualification tree. The code refuses to write inside the baseline.

See:

```text
docs/qis/spin_convention.md
docs/qis/paper_spin_methodology.md
docs/qis/analytic_benchmark.md
docs/qis/paper_spin_outputs.md
docs/qis/references.md
```

## What still requires human physics review

The code deliberately does not auto-approve:

- an inferred sign for a vaguely named `cos(theta)` column;
- rounded PDG values as exact WHIZARD model inputs;
- Born production as an NLO or finite-width `2 -> 6` prediction;
- detector-level truth coefficients as an unfolded measurement;
- physical projection as a replacement for unbiased linear moments.

Those are analysis decisions, not software defaults.
