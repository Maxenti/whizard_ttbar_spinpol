# Level B: detector and reconstruction

Level B is implemented as a complete generic closure framework rather than a claim to reproduce a particular detector.

## Components

- configurable lepton and jet resolution functions;
- efficiency and acceptance cuts;
- reproducible random smearing;
- missing-momentum construction;
- constrained dilepton neutrino reconstruction with multiple starts and both `b`-lepton pairings;
- semileptonic combinatorial reconstruction;
- response-matrix construction;
- SVD/Tikhonov-style regularized unfolding;
- iterative Bayesian unfolding;
- toy and bootstrap covariance propagation;
- named systematic variations and covariance accumulation.

## Detector integration

A real Delphes, EDM4hep, Key4HEP, or experiment-specific reconstruction adapter should produce the same object/table contract. The tomography code then remains unchanged.

## Required closure

Before physics use, demonstrate truth -> detector -> reconstruction -> unfolding closure for all 15 coefficients and nonlinear QIS measures, including pull widths and positivity behavior.
