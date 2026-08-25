# Research notes used to design this suite

- FCC Winter2023 official top card explicitly defines 365 GeV `ttbar` with W/t restrictions, finite-width resonance handling, polarization retained, Gaussian beam spread then ISR, and `10:100000:"gw",10:200000:""` integration.
- WHIZARD/O'Mega computes multiparticle tree-level helicity amplitudes and retains spin correlations; WHIZARD top-physics documentation explicitly discusses full six-fermion processes and spin correlations.
- WHIZARD examples/tutorial material uses `cuts = ... M ... [combine[...]]` syntax for invariant-mass cuts. Because exact SINDARIN syntax/version details matter, this package does not trust static construction alone: `preflight_region_scan.sh` performs a real tiny integration on the actual qualified WHIZARD 3.1.8 executable before any region DAG is submitted.
