# Design decisions

1. **Additive instead of replacing the baseline.** The existing validation is a
   valuable frozen reference and remains reproducible.
2. **Named conventions instead of implicit signs.** Every coefficient is
   meaningless without the beam, antitop, analyzer, and axis definitions.
3. **Moments for unbiased linear coefficients.** No positivity constraint is
   allowed to bias the primary 15 linear estimates.
4. **Physical likelihood/projection for nonlinear quantum measures.** Those
   quantities are undefined or misleading for a non-positive matrix.
5. **Analytic covariance where exact; replicas where nonlinear.** Bootstrap is
   not used as a substitute for a closed-form linear covariance.
6. **Paired comparisons where event lineage exists.** LHE/HepMC is not treated
   as independent when stable event keys allow a stronger calculation.
7. **Strict external theory gates require reviewed generator inputs.** The code
   refuses false precision from guessed electroweak schemes or angle signs.
8. **Truth-level and detector-level claims remain separate.** Unfolding and
   systematics are extension points, not silently assumed accomplishments.
