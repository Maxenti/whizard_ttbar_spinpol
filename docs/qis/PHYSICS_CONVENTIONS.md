# Physics conventions

## Metric and four-vectors

Four-vectors are stored as `(E, px, py, pz)` with metric signature `(+,-,-,-)`. An active boost by velocity `beta` is used; a vector is transformed to a parent rest frame with `-parent.beta`.

## Beam convention

The incoming negative lepton (`e-` or `mu-`) defines positive `z`. This convention is used after identifying the post-WHIZARD-ISR incoming particles in the LHE record.

## Production frame

The spin basis is constructed in the `ttbar` rest frame. Let `p` be the negative-lepton beam direction and `k` the top direction in this frame:

```text
k = p_top / |p_top|
n = (p x k) / |p x k|
r = n x k
```

The stored order is `(k, r, n)`.

For collinear or numerically singular production-plane configurations, the implementation uses a deterministic orthogonal fallback and records the condition through validation diagnostics.

## Antitop basis

The antitop basis is independently right handed:

```text
kbar = p_antitop / |p_antitop| = -k
nbar = n
rbar = nbar x kbar
```

This means diagonal and off-diagonal `C_ij` signs may differ from literature using a common top axis for both particles. Always rotate or sign-map coefficients before comparison.

## Spin analyzers

The positive charged lepton is boosted into the top rest frame. The negative charged lepton is boosted into the antitop rest frame. Analyzer coordinates are dot products with the associated basis axes.

Analyzing powers are configurable. Level A defaults to:

```text
alpha(l+) = 1
alpha(l-) = 1
```

The antitop analyzer sign convention is configurable and defaults to `-1`, matching the estimator definitions in this package. Synthetic-state tests protect this choice from accidental sign drift.

## Density matrix

The normalized state is decomposed as:

```text
rho = 1/4 [I x I + B+_i sigma_i x I + B-_j I x sigma_j
           + C_ij sigma_i x sigma_j]
```

The coefficient vector ordering is:

```text
B+_k, B+_r, B+_n,
B-_k, B-_r, B-_n,
C_kk, C_kr, C_kn,
C_rk, C_rr, C_rn,
C_nk, C_nr, C_nn
```

## Weighting

Event moments use the LHE/HepMC event weight. Negative weights are supported algebraically, but physical-state fitting and effective-statistics diagnostics must be reviewed for NLO samples.

## Entropies

Both natural-log and base-two forms are supported. The default configuration reports base-two entropy in bits.
