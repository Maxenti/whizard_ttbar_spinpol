# paper_spin_v3p1_upgrade_v1

Presentation-layer upgrade for the validated WHIZARD ttbar paper-spin 500 GeV
`v3` output.

## Install

Extract at the repository root with `--strip-components=1`. The bundle adds only
new files under `scripts/qis/`, `docs/qis/`, and `tests/qis/`.

## Run

```bash
bash scripts/qis/run_paper_spin_v3p1.sh \
  --input-root /path/to/paper_spin_500GeV_10k_v3 \
  --output-root /path/to/paper_spin_500GeV_10k_v3p1 \
  --archive /path/to/paper_spin_500GeV_10k_v3p1.tar.gz
```

The command refuses to overwrite an existing output or archive.

## Verify

```bash
cd /path/to/paper_spin_500GeV_10k_v3p1
./verify_bundle.sh
```

or

```bash
python3 scripts/qis/verify_paper_spin_bundle.py \
  /path/to/paper_spin_500GeV_10k_v3p1
```
