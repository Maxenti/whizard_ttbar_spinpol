# Canonical lepton-collider spin convention

## Purpose

This document freezes the convention used by the additive paper-grade
`qis_ttbar.paper_spin` package.  The validated legacy Spin-15 products remain
unchanged.  All publication-facing coefficients must carry the convention name
`lepton_collider_paper_v1`.

## Reference frame and axes

All production axes are defined in the reconstructed or truth-level
`ttbar` center-of-mass frame.

Let `p_plus` be the incoming **positively charged lepton** direction and let
`k` be the top-quark direction. Define

\[
\hat k = \frac{\vec p_t}{|\vec p_t|},
\qquad
\cos\Theta = \hat p_+\cdot\hat k,
\]

\[
\hat r = \frac{\hat p_+-\hat k\cos\Theta}{\sin\Theta},
\qquad
\hat n = \frac{\hat p_+\times\hat k}{\sin\Theta}.
\]

This follows the basis used in *Quantum tops at circular lepton colliders*,
JHEP 09 (2024) 001, arXiv:2404.08049.

The labelled basis obeys

\[
\hat k\times\hat r=-\hat n.
\]

For Pauli-matrix reconstruction, the package maps the named axes to a standard
right-handed Cartesian Pauli basis as

\[
(k,r,n)\longrightarrow(\sigma_z,\sigma_x,-\sigma_y).
\]

This map is explicit in `contracts.py` and tested in density-matrix round trips.

## Charged-lepton analyzers

The top analyzer is

\[
\vec a_+ = \widehat{\ell^+}_{\,t\text{ rest}},
\]

and the antitop analyzer is signed as

\[
\vec a_- = -\widehat{\ell^-}_{\,\bar t\text{ rest}}.
\]

The minus sign gives both charged leptons analyzing power `+1` at tree level.
It also removes an otherwise hidden convention sign from the density matrix.

The existing validated ntuples contain

- `b1{k,r,n}` = raw positive-lepton direction;
- `b2{k,r,n}` = raw negative-lepton direction.

The adapter therefore applies

```text
canonical_plus  = +legacy_b1
canonical_minus = -legacy_b2
```

without modifying the baseline ntuples.

## Angular density and moments

The normalized full angular density is

\[
p(\vec a_+,\vec a_-)=\frac{1}{(4\pi)^2}
\left[
1+\vec B_1\cdot\vec a_+
 +\vec B_2\cdot\vec a_-
 +a_+^i C_{ij}a_-^j
\right].
\]

The corresponding spin density matrix is

\[
\rho=\frac14\left[
I\otimes I+B_{1i}\sigma_i\otimes I
+B_{2j}I\otimes\sigma_j
+C_{ij}\sigma_i\otimes\sigma_j
\right].
\]

Full-phase-space moment estimators are

\[
\widehat B_{1i}=3\langle a_+^i\rangle,
\qquad
\widehat B_{2j}=3\langle a_-^j\rangle,
\qquad
\widehat C_{ij}=9\langle a_+^i a_-^j\rangle.
\]

These are exact method-of-moments estimators of the coefficients, not visual or
ad hoc estimates.

## Relation to the legacy internal convention

The legacy event products were built from the raw negative-lepton direction.
Consequently, publication-facing antitop and correlation coefficients are
related to a legacy `+9 <b1*b2>` table by

\[
B_1^{\rm paper}=B_1^{\rm legacy},
\qquad
B_2^{\rm paper}=-B_2^{\rm legacy},
\qquad
C^{\rm paper}=-C^{\rm legacy}.
\]

The package keeps both convention names and refuses to assign the publication
convention unless `legacy_map_reviewed: true` is set explicitly.

## Connected correlations and the symbol D

The old validation quantity

\[
C^{\rm conn}_{ij}=C_{ij}-B_{1i}B_{2j}
\]

is retained but renamed `Cconn_ij`. It is nine times the angular covariance.
It must not be called simply `D_ij`, because several papers use `D` for trace
markers.

This package records the lepton-collider markers

\[
D^{(1)}=\frac{C_{kk}+C_{rr}+C_{nn}}{3},
\]

\[
D^{(k)}=\frac{C_{kk}-C_{rr}-C_{nn}}{3},
\quad
D^{(r)}=\frac{-C_{kk}+C_{rr}-C_{nn}}{3},
\quad
D^{(n)}=\frac{-C_{kk}-C_{rr}+C_{nn}}{3}.
\]

It also records the separately named CMS-style trace scalar

\[
D_{\rm CMS}=-\frac{\operatorname{Tr}C}{3}
\]

when the same labelled `C` convention is used. Namespaces are deliberate and
must not be collapsed.

## Off-diagonal combinations

For each unordered axis pair, the package calculates

\[
C_{ij}+C_{ji},\qquad C_{ij}-C_{ji},
\]

and

\[
C^{\rm sym}_{ij}=\frac{C_{ij}+C_{ji}}2,
\qquad
C^{\rm anti}_{ij}=\frac{C_{ij}-C_{ji}}2.
\]

These expose symmetry-even and symmetry-odd matrix structures without losing
the individual entries.

## Singular forward/backward events

The `r,n` basis is undefined at exactly `|cos(theta)|=1`. Generated floating
point events are not expected to land exactly at the singular point. Any future
basis reconstruction must define a documented tolerance and either reject or
flag singular events; it must not silently invent an axis.
