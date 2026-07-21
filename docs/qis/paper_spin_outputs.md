# Output contract

The paper-grade layer writes to a new output root and never under the validated
Spin-15 baseline.

```text
paper_spin_<tag>/
├── paper_spin_manifest.json
├── synthetic_closure.json
├── paper_spin_validation.json
├── samples/
│   └── <dataset>/<sample_id>/
│       ├── moment_covariance.csv/.npz
│       ├── linear_derived_covariance.csv/.npz
│       ├── connected_covariance.csv/.npz
│       ├── rho_raw.npy
│       ├── rho_projected.npy
│       ├── rho_shape_fit.npy
│       ├── density_summary.json
│       ├── marginal_fit_summary.json
│       ├── shape_fit_summary.json
│       ├── bootstrap_replicas.npz
│       ├── bootstrap_summary.json
│       └── analytic_benchmark.json or analytic_benchmark_skipped.json
├── tables/
│   ├── paper_spin_coefficients_moments.csv
│   ├── paper_spin_derived_quantities.csv
│   ├── paper_spin_density_measures.csv
│   ├── paper_spin_moment_marginal_comparison.csv
│   ├── paper_spin_moment_shape_comparison.csv
│   ├── paper_spin_comparison_details.csv
│   ├── paper_spin_comparison_summary.csv
│   └── paper_spin_analytic_comparison.csv
├── plots/
├── report/
│   ├── paper_spin_report.md
│   └── figure_manifest.csv
└── provenance/
    ├── baseline_before.json
    └── SHA256SUMS.txt
```

## Primary coefficient result

`paper_spin_coefficients_moments.csv` is the primary linear result. Its full
covariance is in each sample's `moment_covariance` files.

## Nonlinear quantities

Use `density_summary.json` and bootstrap summaries. Always distinguish:

- raw moment matrix;
- Euclidean projected physical matrix;
- simultaneous physical-likelihood matrix.

## Comparison tables

Comparison labels include:

- `LR100_minus_RL100`;
- `SC_minus_ISO_connected`;
- `epmum_minus_mupem`;
- `ee_minus_mumu`;
- `hepmc_minus_lhe_paired` or a clearly labelled independent fallback.

No comparison silently changes its covariance model.
