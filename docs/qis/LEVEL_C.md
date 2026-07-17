# Level C: research extensions

## Implemented capabilities

- arbitrary longitudinal beam mixtures from helicity-basis samples;
- explicit detection of requests that require coherent direct transverse-polarization generation;
- polynomial EFT event reweighting from supplied linear and quadratic coefficients;
- CP tensor and triple-product observables;
- local optimized spin bases using SVD of the correlation matrix;
- multi-energy weighted combinations with covariance propagation;
- differential NLO or external-theory reweighting with normalization controls;
- trace distance, fidelity, Bures distance, and relative entropy;
- quantum and classical Fisher information;
- steering diagnostics;
- magic/coherence diagnostics.

## External physics inputs

The framework does not fabricate EFT amplitudes, NLO corrections, luminosity spectra, or detector calibrations. It validates and applies supplied inputs using explicit schemas.

## Coherent polarization

Transverse polarization and off-diagonal beam density matrices require direct WHIZARD generation. The framework records this as a hard contract and refuses to represent coherent interference as an incoherent LR/RL mixture.

## Future generator campaigns

Recommended additions are threshold/off-shell six-fermion controls, semileptonic channels, realistic machine spectra, LL/RR validation samples, and selected EFT points. Each must remain a separately named campaign.
