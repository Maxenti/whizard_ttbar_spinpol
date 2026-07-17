# Spin-density-matrix reconstruction

## Primary output

The primary result in each phase-space bin is not one angular histogram. It is:

```text
B_plus[3]
B_minus[3]
C[3,3]
rho_raw[4,4]
rho_physical[4,4]
covariance[15,15]
```

## Direct moment estimator

For ideal charged-lepton analyzers, single-particle angular moments determine polarization coefficients and paired moments determine spin correlations. The implementation applies configurable analyzer powers and sign conventions, computes weighted sums, and returns effective event counts.

## Bootstrap covariance

Bootstrap resampling is deterministic for a fixed seed. Each replica resamples event rows, repeats the complete coefficient extraction, and stores the 15-component vector. The covariance is calculated across replicas. Percentile intervals are produced for nonlinear QIS measures.

## Physical-state enforcement

Finite samples can produce a Hermitian, unit-trace matrix with small negative eigenvalues. The package retains the raw estimate and also provides a physical projection:

1. Hermitize.
2. Diagonalize.
3. Project eigenvalues onto the probability simplex.
4. Reconstruct and renormalize.

A constrained likelihood interface is included for analyses that supply an explicit angular likelihood. The eigenvalue-simplex projection is the robust default for general moment outputs.

## Diagnostics

Each state is checked for:

- Hermiticity residual;
- trace residual;
- minimum eigenvalue;
- purity range;
- basis orthogonality;
- finite coefficients;
- bootstrap covariance symmetry and positive-semidefinite tolerance.

## Differential tomography

The workflow supports inclusive, one-dimensional, and two-dimensional bins. Empty or low-statistics bins are reported rather than silently filled. Bin edges use half-open intervals except for the configured terminal edge.
