# Output schema

## Truth/particle ntuple

Each row corresponds to one event and includes:

- campaign, sample, beam, polarization, decay channel;
- event and generator weights;
- beam, top, antitop, `b`, `bbar`, charged-lepton, and neutrino four-vectors where available;
- `m_ttbar`, `sqrt(s')`, `beta_top`, and production angle;
- analyzer coordinates in `(k,r,n)` for top and antitop;
- paired analyzer products;
- laboratory and `ttbar`-frame dilepton observables;
- provenance fields and source path.

## Tomography JSON

The JSON product contains:

```text
schema_version
selection/bin definition
weighted event counts
B_plus
B_minus
C
coefficient ordering
rho_raw
rho_physical
state diagnostics
QIS measures
bootstrap covariance
confidence intervals
configuration fingerprint
```

Complex arrays are serialized as explicit real/imaginary pairs where necessary.

## Level B products

Detector/reconstruction tables keep truth identifiers and add acceptance flags, smeared objects, reconstruction solutions, chi-square, ambiguity metadata, and response-bin indices.

## Level C products

Theory reweighting products retain the nominal event key and add named weights or coefficient vectors. Density-state comparison outputs record the exact states, basis, and model identifiers.
