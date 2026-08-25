> **v1.0.2 Condor hotfix:** use this version for any new restricted submission. The v1.0 restricted DAG omitted the `node_output_root` DAG variable consumed by the Condor submit files, causing first-wave Condor workers to exit before real integration. v1.0.1 also fixes the region nested-binary `combine` syntax.

# LXPLUS runbook

Assume the archive is placed at `/eos/user/c/cglenn/FCCWork/whizard/packages/phase11_ttbar_restricted_region_suite_v1p0p2.tar.gz`.

```bash
export REPO=/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol
export CAMPAIGN=full6f_365gev_ee_ttbar_spinpol_v1
export PROD=/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/$CAMPAIGN
export PKG_EOS=/eos/user/c/cglenn/FCCWork/whizard/packages/phase11_ttbar_restricted_region_suite_v1p0p2.tar.gz
export SUITE_BASE=$REPO/phase11_diagnostics/excess_weight_rootcause_v1/ttbar_restricted_region_suite_v1
export PKG=$SUITE_BASE/package_v1p0p2
rm -rf "$PKG"; mkdir -p "$PKG"
tar -xzf "$PKG_EOS" --strip-components=1 -C "$PKG"
cd "$PKG"; sha256sum -c PACKAGE_MANIFEST.sha256
export SOURCE_CARD=$REPO/sindarin/generated/$CAMPAIGN/f6f365_ee_LR100_epmum/epmum/process.sin
sha256sum "$SOURCE_CARD"
```

## A. Restricted WT qualification (496 nodes)

```bash
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
export R_TAG=${STAMP}_WT_A15xS8_F012_FCC_np1
export R_SUB=$SUITE_BASE/restricted/submissions/$R_TAG
export R_OUT=$PROD/phase11_diagnostics/excess_weight_rootcause_v1/ttbar_restricted_region_suite_v1/restricted/$R_TAG
python3 "$PKG/scripts/prepare_restricted_scan.py" --package-root "$PKG" --repo "$REPO" --source-card "$SOURCE_CARD" --submission-dir "$R_SUB" --output-root "$R_OUT"
"$R_SUB/scripts/preflight_restricted_scan.sh" "$R_SUB" | tee "$R_SUB/PREFLIGHT_TRANSCRIPT.txt"
"$R_SUB/scripts/submit_campaign.sh" "$R_SUB" --bump-schedd | tee "$R_SUB/SUBMIT_TRANSCRIPT.txt"
```

Monitor:
```bash
source "$R_SUB/submission_runtime.env"
"$R_SUB/scripts/status_campaign.sh" "$R_SUB"
"$R_SUB/scripts/show_live_tails.sh" "$R_SUB"
```

Collect/analyze/validate:
```bash
python3 "$R_SUB/scripts/collect_campaign.py" --campaign-dir "$R_SUB"
python3 "$R_SUB/scripts/analyze_stability.py" --campaign-dir "$R_SUB"
python3 "$R_SUB/scripts/validate_restricted.py" --campaign-dir "$R_SUB"
python3 "$R_SUB/scripts/audit_source_physics.py" --campaign-dir "$R_SUB"
python3 "$R_SUB/scripts/plot_stability.py" --campaign-dir "$R_SUB"
```

## B. Unrestricted nine-region core campaign (432 nodes)

Recommended first profile uses M0/M1/M2, the same frozen S0--S7 seed identities, and W15 around 172.5 GeV.

```bash
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
export G_TAG=${STAMP}_U9region_core_W15_S8_np1
export G_SUB=$SUITE_BASE/regions/submissions/$G_TAG
export G_OUT=$PROD/phase11_diagnostics/excess_weight_rootcause_v1/ttbar_restricted_region_suite_v1/regions/$G_TAG
python3 "$PKG/scripts/prepare_region_scan.py" --package-root "$PKG" --repo "$REPO" --source-card "$SOURCE_CARD" --submission-dir "$G_SUB" --output-root "$G_OUT" --profile core --top-mass-GeV 172.5 --half-width-GeV 15
"$G_SUB/scripts/preflight_region_scan.sh" "$G_SUB" | tee "$G_SUB/PREFLIGHT_TRANSCRIPT.txt"
"$G_SUB/scripts/submit_campaign.sh" "$G_SUB" --bump-schedd | tee "$G_SUB/SUBMIT_TRANSCRIPT.txt"
```

Collect/analyze:
```bash
python3 "$G_SUB/scripts/collect_campaign.py" --campaign-dir "$G_SUB"
python3 "$G_SUB/scripts/analyze_stability.py" --campaign-dir "$G_SUB"
python3 "$G_SUB/scripts/analyze_regions.py" --campaign-dir "$G_SUB"
python3 "$G_SUB/scripts/audit_source_physics.py" --campaign-dir "$G_SUB"
python3 "$G_SUB/scripts/plot_stability.py" --campaign-dir "$G_SUB"
```

## C. Make the existing monolithic 480 scan comparable

```bash
export MONO_BASE=$REPO/phase11_diagnostics/excess_weight_rootcause_v1/unrestricted_stability_scan_480_v1
export MONO_SUB=$(find "$MONO_BASE/submissions" -mindepth 1 -maxdepth 1 -type d -name '*_unrestricted_A15xS8xF3_np1' -printf '%T@ %p
' | sort -nr | head -1 | cut -d' ' -f2-)
python3 "$MONO_SUB/scripts/collect_results.py" --campaign-dir "$MONO_SUB"
# Use the NEW analyzer on the OLD collected tables; it is schema-tolerant.
rm -rf "$MONO_SUB/analysis"
python3 "$G_SUB/scripts/analyze_stability.py" --campaign-dir "$MONO_SUB" --thresholds "$G_SUB/frozen_config/validation_thresholds.json"
python3 "$G_SUB/scripts/compare_region_to_monolithic.py" --region-campaign-dir "$G_SUB" --monolithic-analysis "$MONO_SUB/analysis/node_numerical_metrics.tsv"
python3 "$G_SUB/scripts/validate_regions.py" --campaign-dir "$G_SUB"
python3 "$G_SUB/scripts/plot_regions.py" --campaign-dir "$G_SUB"
```

## D. Optional region extensions

After core results, prepare separate DAGs rather than mutating the core campaign:
- `--profile extended`: M0--M4, 720 nodes
- `--profile historical_fcc`: MFCC only, 144 nodes
- `--profile window_scan`: M1 over 10/15/20 GeV half-widths, 432 nodes

Each gets a fresh timestamped submission/output directory.

## E. Closeout

```bash
"$R_SUB/scripts/make_closeout_bundle.sh" "$R_SUB"
"$G_SUB/scripts/make_closeout_bundle.sh" "$G_SUB"
```
