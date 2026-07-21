# Independent analytic benchmark

## What is calculated

`analytic_tree.py` evaluates the coherent Standard Model tree-level amplitude

\[
\ell^+\ell^-\rightarrow\gamma^*,Z^*\rightarrow t\bar t
\]

using explicit Dirac spinors for fixed LR100 or RL100 initial helicities and
explicit top/antitop spin states in the frozen lepton-collider basis.

The calculation includes:

- photon exchange;
- Z exchange;
- gamma-Z interference;
- finite top and initial-lepton masses;
- finite Z width;
- color factor;
- differential spin density at fixed `sqrt(s)` and `cos(theta)`;
- Gauss-Legendre angular integration;
- event-conditioned averaging over the actual generated `mtt` and
  `cos(theta)` distribution.

It does not use fitted WHIZARD coefficient templates.

## What it is not

It is not a complete replacement for the generated `2 -> 6` matrix element.
It does not include:

- NLO QCD or electroweak corrections;
- nonfactorizable finite-width effects;
- exact spin-dependent ISR recoil beyond event conditioning;
- shower radiation;
- detector selection;
- the precise WHIZARD electroweak input scheme unless configured explicitly.

Therefore it is an independent production-density closure calculation, not an
unqualified precision prediction.

## Safety locks

The default SM YAML contains explicit numerical values but sets

```yaml
generator_match_reviewed: false
```

The main config also sets

```yaml
kinematics_map_reviewed: false
```

Until both are changed deliberately, the analytic result may be generated for
study but cannot pass a strict validation gate.

## Required generator audit

Before enabling strict comparison, record from the WHIZARD SINDARIN/model logs:

- top mass and width;
- Z mass and width;
- electromagnetic input (`alpha(0)`, `alpha(MZ)`, or `G_mu` scheme);
- weak mixing angle definition;
- CKM assumptions;
- ISR settings;
- scale and scheme choices;
- whether the LHE hard process uses on-shell or finite-width tops;
- exact direction represented by the ntuple `cos(theta)` column.

Then regenerate only the analytic tables and paper-grade analysis. No shower or
WHIZARD event regeneration is required merely to change the benchmark inputs.

## Internal analytic unit tests

The bundle includes tests for:

- density-matrix Hermiticity, trace, and positivity;
- finite differential cross sections;
- `e+e-` and `mu+mu-` universality at 500 GeV;
- a pure-QED massless cross-section normalization helper;
- LR/RL helicity handling;
- quadrature convergence.
