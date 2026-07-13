# WHIZARD polarized, spin-correlated ttbar production workflow

This package is an overlay for the existing repository:

```text
/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol
```

Persistent products are written only below the EOS output root:

```text
/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/
```

The first campaign is:

```text
500GeV_ISR_sc_v1
```

and contains eight configurations:

```text
ee_ttbar_epmum_LR100_sc_ISR_500GeV
ee_ttbar_epmum_RL100_sc_ISR_500GeV
ee_ttbar_mupem_LR100_sc_ISR_500GeV
ee_ttbar_mupem_RL100_sc_ISR_500GeV
mumu_ttbar_epmum_LR100_sc_ISR_500GeV
mumu_ttbar_epmum_RL100_sc_ISR_500GeV
mumu_ttbar_mupem_LR100_sc_ISR_500GeV
mumu_ttbar_mupem_RL100_sc_ISR_500GeV
```

`epmum` means

```text
t    -> b    e+  nu_e
tbar -> bbar mu- anti-nu_mu
```

and `mupem` means

```text
t    -> b    mu+ nu_mu
tbar -> bbar e-  anti-nu_e
```

The production configuration has:

- WHIZARD factorized top decays;
- exact spin-density-matrix correlations;
- pure `LR100` and `RL100` beam-helicity states;
- ISR and the recoil ISR handler enabled;
- explicit incoming-lepton masses for the ISR structure function;
- no machine-specific beam-energy spectrum;
- no showering or hadronization;
- LHEF output;
- 10 shards x 10,000 events per configuration by default.

The eight-way smoke campaign must pass before the full 80-job production is submitted.

---

## Added repository files

```text
configs/production/
└── production_500GeV_ISR_sc_v1.csv

scripts/production/
├── production_common.py
├── make_production_sindarin.py
├── run_production_shard.sh
├── submit_production.py
├── collect_production.py
├── calibrate_decay_normalization.py
├── finalize_forced_decay_lhe.py
├── make_production_manifest.py
├── validate_production_outputs.py
└── README.md

condor/
└── whizard_production.sub

sindarin/production/
├── generated_templates.csv
└── <eight .sin.in templates>
```

`production_common.py` is an internal standard-library-only helper used by the Python commands.

---

## Install the overlay

From the AFS repository root:

```bash
cd /afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol

tar -xzf /path/to/whizard_ttbar_spinpol_production_v1.tar.gz \
  --strip-components=1

chmod +x scripts/production/*.py scripts/production/*.sh
```

Verify the environment and output root:

```bash
source setup_lxplus.sh

export WHIZARD_TTBAR_OUTPUT_ROOT=/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol
export PYTHONDONTWRITEBYTECODE=1

command -v whizard
whizard --version
echo "$WHIZARD_TTBAR_OUTPUT_ROOT"
```

Syntax-check the package:

```bash
python3 -m py_compile scripts/production/*.py
bash -n scripts/production/run_production_shard.sh
```

---

## Campaign output layout

The smoke campaign is separated from full production:

```text
/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/
├── 500GeV_ISR_sc_v1_smoke/
└── 500GeV_ISR_sc_v1/
```

Each campaign root contains:

```text
runs/<sample>/shard_0000/
lhe_raw/<sample>/<sample>__shard_0000.lhe
lhe/<sample>/<sample>__shard_0000.lhe
lhe_merged/raw/<sample>.lhe
lhe_merged/final/<sample>.lhe
logs/<sample>/
condor/stdout/<sample>/
condor/stderr/<sample>/
manifests/
normalization/
validation/
failed/<sample>/shard_0000/
```

Important distinction:

- `lhe_raw/` contains untouched WHIZARD output;
- `lhe/` contains copies whose LHE cross-section metadata has been multiplied by the calibrated forced-decay branching weight;
- event kinematics and unit event weights are unchanged;
- raw and finalized files have separate checksums and provenance.

WHIZARD compilation and integration occur in `_CONDOR_SCRATCH_DIR`, never in EOS.

---

## Step 1: regenerate and inspect the SINDARIN templates

The archive already contains generated templates. Regenerate them from the CSV contract to verify determinism:

```bash
python3 scripts/production/make_production_sindarin.py --force

python3 scripts/production/make_production_sindarin.py --check
```

Inspect one electron and one muon template:

```bash
sed -n '1,180p' \
  sindarin/production/ee_ttbar_epmum_LR100_sc_ISR_500GeV.sin.in

sed -n '1,180p' \
  sindarin/production/mumu_ttbar_epmum_LR100_sc_ISR_500GeV.sin.in
```

Check the ISR masses:

```bash
grep -HnE 'beams =|isr_mass|isr_alpha|beams_pol_density|isotropic_decay' \
  sindarin/production/*.sin.in
```

Expected ISR masses are configured numerically:

```text
ee:   0.000510997 GeV
mumu: 0.105658389 GeV
```

This avoids accidentally using an electron ISR mass for a muon beam.

---

## Step 2: prepare the eight-job smoke submission

This creates one 200-event shard for every configuration in the separate smoke root. It does not submit by default.

```bash
python3 scripts/production/submit_production.py \
  --smoke \
  --smoke-events 200
```

The command prints the concrete submit-file location under:

```text
.../production/500GeV_ISR_sc_v1_smoke/manifests/submissions/<timestamp>/
```

Inspect:

```bash
SMOKE_ROOT="$WHIZARD_TTBAR_OUTPUT_ROOT/production/500GeV_ISR_sc_v1_smoke"
LATEST=$(find "$SMOKE_ROOT/manifests/submissions" -mindepth 1 -maxdepth 1 -type d | sort | tail -1)

column -s, -t < "$LATEST/jobs.csv" | less -S
sed -n '1,220p' "$LATEST/whizard_production.sub"
```

Submit after review:

```bash
python3 scripts/production/submit_production.py \
  --smoke \
  --smoke-events 200 \
  --submit
```

Monitor:

```bash
condor_q "$USER" -nobatch
```

Inspect held jobs:

```bash
condor_q "$USER" -hold
```

The wrapper stages failure logs and metadata under `failed/` before returning nonzero whenever possible.

---

## Step 3: build and validate the raw smoke manifest

After all eight jobs leave the queue:

```bash
python3 scripts/production/make_production_manifest.py --smoke

python3 scripts/production/validate_production_outputs.py \
  --smoke \
  --stage raw \
  --scan-events 0 \
  --strict
```

`--scan-events 0` checks the requested final-state particles in every LHE event. For a fast diagnostic, use a positive limit such as `--scan-events 100`.

The raw validation requires, per shard:

- WHIZARD return code zero;
- exact requested event count;
- unique seed and LHE checksum;
- ISR present in the rendered SINDARIN;
- exact spin-correlated decay settings;
- polarized-event generation enabled;
- two `helicity treated exactly` log records;
- correct LR/RL beam-polarization evidence in the WHIZARD log;
- expected incoming beam PDGs;
- required forced-decay final-state PDGs;
- acceptable integration precision;
- acceptable excess-weight fraction.

The validator intentionally does not require `ee` and `mumu` ISR cross sections to agree.

---

## Step 4: smoke-test normalization and collection

Build stable decay-width averages from the successful smoke logs:

```bash
python3 scripts/production/calibrate_decay_normalization.py --smoke
```

Create finalized LHE files without touching the raw files:

```bash
python3 scripts/production/finalize_forced_decay_lhe.py \
  --smoke \
  --overwrite
```

Refresh the manifests so final-file paths and exclusive cross sections are recorded:

```bash
python3 scripts/production/make_production_manifest.py --smoke
```

Merge the eight smoke samples separately, one merged file per configuration:

```bash
python3 scripts/production/collect_production.py \
  --smoke \
  --source final \
  --merge \
  --overwrite
```

Refresh and validate the finalized/merged smoke output:

```bash
python3 scripts/production/make_production_manifest.py --smoke

python3 scripts/production/validate_production_outputs.py \
  --smoke \
  --stage final \
  --scan-events 0 \
  --require-merged \
  --strict
```

Do not proceed to the 80-job production unless both raw and final smoke validators return zero.

---

## Step 5: prepare the full production submission

First create and inspect the 80-job submission without sending it:

```bash
python3 scripts/production/submit_production.py
```

Expected:

```text
8 samples x 10 shards = 80 jobs
10,000 events per job
800,000 events total
```

Submit:

```bash
python3 scripts/production/submit_production.py --submit
```

The default full campaign root is:

```text
/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/500GeV_ISR_sc_v1
```

### Submit only selected samples

```bash
python3 scripts/production/submit_production.py \
  --sample 'ee_*' \
  --submit
```

### Submit a selected shard

```bash
python3 scripts/production/submit_production.py \
  --sample 'ee_ttbar_epmum_LR100*' \
  --shard 3 \
  --submit
```

### Resume after successful partial production

Regenerate the manifest first, then skip completed shards:

```bash
python3 scripts/production/make_production_manifest.py

python3 scripts/production/submit_production.py \
  --resume
```

Review the generated jobs before rerunning with `--submit`.

`--resume` skips only shards whose staged `run_metadata.json` says `status=success`. Existing failed or ambiguous outputs require manual review or explicit `--force`.

### Replace a failed shard deliberately

```bash
python3 scripts/production/submit_production.py \
  --sample 'SAMPLE_ID' \
  --shard 4 \
  --force \
  --submit
```

`--force` removes the existing persistent shard products inside the worker wrapper. Do not use it on a validated successful shard without a specific reason.

---

## Step 6: validate the complete raw production

```bash
python3 scripts/production/make_production_manifest.py

python3 scripts/production/validate_production_outputs.py \
  --stage raw \
  --scan-events 0 \
  --strict
```

Inspect:

```bash
cat "$WHIZARD_TTBAR_OUTPUT_ROOT/production/500GeV_ISR_sc_v1/validation/production_validation_raw.md"
```

---

## Step 7: calibrate and finalize the production LHE files

Use the complete production shard ensemble for the final decay calibration:

```bash
python3 scripts/production/calibrate_decay_normalization.py
```

This combines decay-width integrations by inverse-variance weighting for:

```text
epmum / t_decay
epmum / tbar_decay
mupem / t_decay
mupem / tbar_decay
```

It writes:

```text
normalization/decay_width_calibration.csv
normalization/forced_decay_weights.csv
```

Finalize every raw LHE:

```bash
python3 scripts/production/finalize_forced_decay_lhe.py \
  --overwrite
```

Optional gzip output:

```bash
python3 scripts/production/finalize_forced_decay_lhe.py \
  --gzip \
  --overwrite
```

Do not mix compressed and uncompressed finalized files for the same campaign unless the older files are removed first.

Refresh:

```bash
python3 scripts/production/make_production_manifest.py
```

---

## Step 8: merge and validate the final samples

```bash
python3 scripts/production/collect_production.py \
  --source final \
  --merge \
  --overwrite

python3 scripts/production/make_production_manifest.py

python3 scripts/production/validate_production_outputs.py \
  --stage final \
  --scan-events 0 \
  --require-merged \
  --strict
```

Expected merged products:

```text
production/500GeV_ISR_sc_v1/lhe_merged/final/
├── ee_ttbar_epmum_LR100_sc_ISR_500GeV.lhe
├── ee_ttbar_epmum_RL100_sc_ISR_500GeV.lhe
├── ee_ttbar_mupem_LR100_sc_ISR_500GeV.lhe
├── ee_ttbar_mupem_RL100_sc_ISR_500GeV.lhe
├── mumu_ttbar_epmum_LR100_sc_ISR_500GeV.lhe
├── mumu_ttbar_epmum_RL100_sc_ISR_500GeV.lhe
├── mumu_ttbar_mupem_LR100_sc_ISR_500GeV.lhe
└── mumu_ttbar_mupem_RL100_sc_ISR_500GeV.lhe
```

Each merged file retains one process cross section, not a sum over shard cross sections. Shards are independent event draws from the same process.

---

## Important physics and normalization notes

### Forced decay channels

Each top and antitop has only one configured decay channel inside a particular production sample. WHIZARD consequently treats that configured decay table as branching ratio one while generating conditional decay kinematics.

The raw LHE header therefore carries the inclusive polarized `ttbar` production cross section.

The finalization stage applies:

```text
exclusive cross section
  = inclusive ttbar cross section
  x BR(t -> selected channel)
  x BR(tbar -> selected channel)
```

The raw LHE is never modified.

### Spin correlations

The production templates retain:

```sindarin
?diagonal_decay = false
?isotropic_decay = false
?polarized_events = true
```

and the strict validator requires WHIZARD to report `helicity treated exactly` for both top decays.

### ISR

The templates use:

```sindarin
beams = <lepton>, <antilepton> => isr
?isr_handler = true
$isr_handler_mode = "recoil"
?keep_beams = true
?keep_remnants = true
isr_mass = <incoming lepton mass> GeV
isr_alpha = 0.0072973525693
```

The installed WHIZARD 3.1.5 build is the authority. The smoke campaign exists specifically to verify that both electron and muon ISR configurations parse and generate valid records before full production.

### Machine spectrum

No CIRCE2 or other machine-specific energy spectrum is included in this campaign. Add such spectra only as a separately named campaign tied to a concrete collider design.

### Showering and hadronization

The products are hard-process LHE files. Pythia8/HepMC production should be a downstream campaign with its own manifest and checksums rather than modifying these generator-level samples.

---

## Troubleshooting

### Jobs are held

```bash
condor_q "$USER" -hold -af ClusterId ProcId HoldReason
```

Inspect the EOS stderr file printed in the concrete submit descriptor and the staged `failed/` directory.

### A completed shard is reported missing

Refresh the manifest:

```bash
python3 scripts/production/make_production_manifest.py
```

Then inspect:

```bash
column -s, -t \
  < "$WHIZARD_TTBAR_OUTPUT_ROOT/production/500GeV_ISR_sc_v1/manifests/shard_manifest.csv" \
  | less -S
```

### Validation warns that no ISR label was found in the log

The rendered SINDARIN ISR configuration is a strict check. `log_isr_evidence` is only a warning because WHIZARD log wording can vary. Confirm the actual beam section in the native log before accepting the smoke sample.

### Condor itemdata or submit file needs review

Every submission is preserved under:

```text
manifests/submissions/<UTC timestamp>/
```

including:

```text
jobs.csv
jobs.itemdata
sample_definitions.csv
submission.json
whizard_production.sub
```

This makes the exact submitted matrix reproducible.
