# Paper-grade ttbar spin-tomography methodology

## Analysis layers

The package deliberately keeps several estimators instead of forcing one method
to serve every purpose.

### 1. Unconstrained angular moments

The primary linear estimator is the event average of the 15 unbiased estimands:

```text
3*a_plus[k,r,n]
3*a_minus[k,r,n]
9*a_plus[i]*a_minus[j]
```

A full `15 x 15` covariance matrix is calculated directly from the same event
estimands. For positive normalized event weights `alpha_n`,

\[
\operatorname{Cov}(\bar x)=
\frac{\sum_n\alpha_n^2(x_n-\bar x)(x_n-\bar x)^T}
{1-\sum_n\alpha_n^2}.
\]

For equal weights this is exactly the sample covariance divided by `N`.

This is the authoritative unbiased result for the linear coefficients.

### 2. CMS-style one-dimensional shape extraction

Every `B` coefficient is also fitted from

\[
f(x;B)=\frac12(1+Bx),\qquad x=\cos\theta.
\]

Every `C_ij` is fitted from the product variable

\[
x=a_+^i a_-^j,
\]

whose full-phase-space marginal is

\[
f(x;C_{ij})=-\frac12\log|x|\,(1+C_{ij}x).
\]

Terms independent of the parameter cancel from the likelihood, so the fitted
likelihood term is `sum w log(1+coefficient*x)`.

The opening-angle scalar is independently fitted from

\[
\cos\varphi=\vec a_+\cdot\vec a_-,
\]

with

\[
f(\cos\varphi;D^{(1)})=rac12
\left[1+D^{(1)}\cos\varphi\right].
\]

The marginal fit errors are individual profile-curvature errors. They are not a
full 15-dimensional covariance because all fits share events. Joint bootstrap
or the simultaneous likelihood supplies the correlation information.

### 3. Simultaneous physical angular likelihood

The complete angular density is fit in one operation. The density matrix is
parameterized as

\[
\rho(T)=\frac{TT^\dagger}{\operatorname{Tr}(TT^\dagger)},
\]

where `T` is lower triangular with real diagonal entries. This has exactly 15
real free parameters and guarantees Hermiticity, unit trace, and positivity.

The fit maximizes the unbinned likelihood of the full pair of unit vectors.
No independent-coefficient approximation is made.

### 4. Physical projection

Finite-statistics moment coefficients can produce a raw density matrix with a
small negative eigenvalue. This does not make the linear moment estimates
invalid. For nonlinear quantum measures, the package additionally computes the
exact Euclidean projection onto the set of positive semidefinite trace-one
matrices by projecting the eigenvalues onto the probability simplex.

Report both:

- raw moment matrix and eigenvalues;
- projected matrix and projection distance;
- simultaneous physical-likelihood matrix.

Do not replace the raw coefficients silently.

### 5. Covariance and replicas

- Linear coefficient covariance: calculated analytically from event estimands.
- Linear derived quantities: exact matrix propagation.
- `Cconn_ij`: first-order Jacobian propagation with the full coefficient covariance.
- Nonlinear quantum measures: nonparametric event bootstrap.
- Moment-versus-shape same-sample closure: joint bootstrap of both estimators.
- LHE-versus-HepMC: paired event differences whenever stable event keys exist.

The replica RNG uses `SeedSequence([base_seed, replica_id])`, so disjoint
HTCondor ranges are identical to one monolithic run.

## Validation hierarchy

### Structural

- 32 expected datasets;
- 15 coefficient rows per dataset;
- finite unit analyzers;
- positive total weight;
- explicit convention metadata;
- baseline checksum unchanged.

### Beam polarization

For every SC stage/initial-state/decay-channel group, LR100 and RL100 must differ
by more than the configured significance in at least one `B` component.

ISO samples are not required to retain LR/RL analyzer separation. They are
instead tested against the six-dimensional zero-polarization hypothesis using
the full `B` covariance.

### Spin correlation

SC and ISO samples are compared using

\[
C^{\rm conn}_{ij}=C_{ij}-B_{1i}B_{2j}
\]

and the propagated full `9 x 9` covariance. At least one component must show a
significant separation in every matched group.

### Decay-flavour closure

`epmum` and `mupem` use charged-lepton analyzers with essentially identical
spin-analyzing power. They must agree after the frozen charge/top convention.

### LHE/HepMC preservation

The preferred comparison is event paired. A coefficient is fatal only when its
shift is both larger than the absolute physics tolerance and statistically
significant. Single-limit exceedances remain warnings.

### Extraction closure

- Synthetic physical states are injected and recovered by moments.
- The simultaneous fit must remain physical.
- Moment and shape methods are compared.
- The direct opening-angle fit must close against `Tr(C)/3`.

### Analytic closure

An independent explicit-spinor `gamma/Z` tree-level calculation is supplied.
A strict comparison is enabled only after:

1. exact WHIZARD SM input parameters are copied into the benchmark config;
2. the stored `cos(theta)` sign is reviewed against the positive incoming
   lepton direction;
3. the comparison is restricted to spin-correlated LHE samples;
4. the limitations of the Born/narrow-width production benchmark are stated.

The default safety locks intentionally prevent an unreviewed analytic curve
from being promoted to a validation gate.

## Detector-level extension

The present campaign is truth-level. A detector-level CMS-style measurement
would additionally require:

- reconstruction-level observable definitions;
- response matrices;
- acceptance and efficiency treatment;
- purity/stability studies and binning optimization;
- pseudo-data linearity and pull closure;
- unfolding or a detector-folded likelihood;
- systematic nuisance covariance;
- regularization-bias studies.

The package creates clean interfaces for those additions but does not pretend
that truth-level coefficients are already an unfolded experimental result.
