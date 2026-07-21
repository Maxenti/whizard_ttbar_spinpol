# Paper-spin v3p1 presentation upgrade

This tool creates a new output tree from the validated 500 GeV `v3` baseline.
It never edits the input tree and refuses to overwrite an existing output.

The upgrade regenerates presentation products only:

- shared-scale connected-correlation matrices;
- clearer comparison plots;
- separate marginal-closure and constrained physical-fit figures;
- complete differential atlases in `cos(theta_t)` and `m(ttbar)`;
- corrected report language for event transport versus post-shower migration;
- relative figure/checksum manifests and an in-place verifier.

All files under `tables/`, `samples/`, `paper_spin_validation.json`, and
`synthetic_closure.json` are hashed before and after the upgrade. The build
aborts unless every one is byte-identical.
