# Quick start

## 1. Install the overlay

Extract the tarball at the repository root:

```bash
cd /afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol
tar -xzf whizard_ttbar_spinpol_qis_framework_v1.tar.gz --strip-components=1
```

## 2. Enter the validated environment

```bash
source setup_lxplus.sh
export PYTHONDONTWRITEBYTECODE=1
```

## 3. Install Python entry points

```bash
python3 -m pip install --user -e '.[all]'
```

For a non-user local installation:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e '.[all]'
```

## 4. Build the C++ shower executable

```bash
./scripts/qis/build_qis.sh
```

Expected executable:

```text
build/qis_lhe_to_hepmc3
```

## 5. Run mathematical validation

```bash
qis-validate --output validation/qis_framework_validation
```

## 6. Test one supplied or local LHE file

```bash
python3 scripts/qis/make_qis_ntuples.py \
  --manifest /path/to/sample_manifest.csv \
  --sample ee_ttbar_epmum_LR100_sc_ISR_500GeV \
  --max-events 100 \
  --output-dir /tmp/qis_ntuples
```

## 7. Run tomography

```bash
python3 scripts/qis/run_tomography.py \
  /tmp/qis_ntuples/ee_ttbar_epmum_LR100_sc_ISR_500GeV.csv \
  --output-dir /tmp/qis_tomography \
  --replicas 100 \
  --minimum-events 20
```

## 8. Shower one file

```bash
build/qis_lhe_to_hepmc3 \
  --input /path/to/sample.lhe \
  --output /tmp/sample.hepmc3 \
  --metadata /tmp/sample.metadata.json \
  --settings configs/pythia/level_a.cmnd \
  --campaign-id 500GeV_ISR_sc_v1 \
  --sample-id ee_ttbar_epmum_LR100_sc_ISR_500GeV \
  --shard-id merged \
  --seed 710001 \
  --max-events 100
```

## 9. Run tests

```bash
pytest -q tests/qis
```

## 10. Production Condor sequence

```bash
python3 scripts/showering/submit_showering.py --config configs/qis/level_a_500GeV_ISR_sc_v1.yaml
python3 scripts/showering/submit_showering.py --config configs/qis/level_a_500GeV_ISR_sc_v1.yaml --submit
python3 scripts/showering/validate_showering.py --config configs/qis/level_a_500GeV_ISR_sc_v1.yaml --strict
python3 scripts/showering/collect_showering.py --config configs/qis/level_a_500GeV_ISR_sc_v1.yaml
```
