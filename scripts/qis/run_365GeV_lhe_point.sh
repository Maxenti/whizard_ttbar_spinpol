#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  bash scripts/qis/run_365GeV_lhe_point.sh \
    --campaign-root PATH --sample-id SAMPLE [options]

Options:
  --repo-root PATH       Repository root (default: inferred from script)
  --campaign-root PATH   Prepared campaign root
  --sample-id ID         Exact 365 GeV sample ID
  --rerun                Replace prior generated outputs for this sample
  --validate-only        Skip WHIZARD and validate the existing LHE
  -h, --help             Show this help
EOF
}

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=$(cd "$SCRIPT_DIR/../.." && pwd)
CAMPAIGN_ROOT=
SAMPLE_ID=
RERUN=0
VALIDATE_ONLY=0

while (($#)); do
  case "$1" in
    --repo-root) REPO=$2; shift 2 ;;
    --campaign-root) CAMPAIGN_ROOT=$2; shift 2 ;;
    --sample-id) SAMPLE_ID=$2; shift 2 ;;
    --rerun) RERUN=1; shift ;;
    --validate-only) VALIDATE_ONLY=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z $CAMPAIGN_ROOT || -z $SAMPLE_ID ]]; then
  echo "ERROR: --campaign-root and --sample-id are required" >&2
  usage >&2
  exit 2
fi

REPO=$(cd "$REPO" && pwd)
if [[ $CAMPAIGN_ROOT != /* ]]; then
  CAMPAIGN_ROOT="$REPO/$CAMPAIGN_ROOT"
fi
CAMPAIGN_ROOT=$(cd "$CAMPAIGN_ROOT" && pwd)
cd "$REPO"

if [[ -f setup_lxplus.sh ]]; then
  # shellcheck disable=SC1091
  source ./setup_lxplus.sh
fi

mapfile -t VALUES < <(
  python3 - "$CAMPAIGN_ROOT/campaign_samples.tsv" "$SAMPLE_ID" <<'PY'
import csv
import sys
from pathlib import Path

path = Path(sys.argv[1])
sample_id = sys.argv[2]
with path.open(newline="") as stream:
    rows = list(csv.DictReader(stream, delimiter="\t"))
rows = [row for row in rows if row["sample_id"] == sample_id]
if len(rows) != 1:
    raise SystemExit(f"Expected one campaign row for {sample_id}; found {len(rows)}")
row = rows[0]
for key in ("run_dir", "input_path", "expected_lhe_path", "events"):
    print(row[key])
PY
)

RUN_DIR=${VALUES[0]}
INPUT_PATH=${VALUES[1]}
LHE=${VALUES[2]}
EVENTS=${VALUES[3]}

if [[ ! -f $INPUT_PATH ]]; then
  echo "ERROR: prepared input missing: $INPUT_PATH" >&2
  exit 1
fi

if ((RERUN)); then
  find "$RUN_DIR" -maxdepth 1 -type f \
    \( -name '*.lhe' -o -name '*.lhe.gz' -o -name '*.lhef' -o -name '*.lhef.gz' \
       -o -name '*.evx' -o -name '*.vg' -o -name '*.phs' -o -name '*.f90' \
       -o -name '*.lo' -o -name '*.la' -o -name '*.o' -o -name '*.mod' \
       -o -name 'console.log' -o -name 'sample_validation.json' \
       -o -name 'sample_validation.log' -o -name 'sample_complete.json' \
       -o -name 'SHA256SUMS.txt' \) -delete
elif [[ -e $RUN_DIR/sample_complete.json && $VALIDATE_ONLY -eq 0 ]]; then
  echo "ERROR: sample already complete: $SAMPLE_ID" >&2
  echo "Use --rerun only when intentionally regenerating it." >&2
  exit 1
fi

if ((VALIDATE_ONLY == 0)); then
  if ! command -v whizard >/dev/null 2>&1; then
    echo "ERROR: whizard is not available in PATH" >&2
    exit 1
  fi

  printf '%s\n' \
    "============================================================" \
    "365 GeV LHE matrix point" \
    "============================================================" \
    "Sample:           $SAMPLE_ID" \
    "Events:           $EVENTS" \
    "Run directory:    $RUN_DIR" \
    "WHIZARD:          $(command -v whizard)" \
    "============================================================"

  cd "$RUN_DIR"
  set +e
  whizard "$(basename "$INPUT_PATH")" 2>&1 | tee console.log
  WHIZARD_STATUS=${PIPESTATUS[0]}
  set -e
  if ((WHIZARD_STATUS != 0)); then
    echo "ERROR: WHIZARD failed with status $WHIZARD_STATUS" >&2
    exit "$WHIZARD_STATUS"
  fi
  if ! grep -Fq 'WHIZARD run finished.' console.log; then
    echo "ERROR: WHIZARD completion marker missing" >&2
    exit 1
  fi
  if grep -Eq 'There were [1-9][0-9]* errors' console.log; then
    echo "ERROR: WHIZARD reported errors" >&2
    exit 1
  fi
  cd "$REPO"
fi

if [[ ! -s $LHE ]]; then
  echo "ERROR: expected LHE missing or empty: $LHE" >&2
  exit 1
fi

python3 scripts/qis/validate_365GeV_lhe_sample.py \
  --repo-root "$REPO" \
  --campaign-root "$CAMPAIGN_ROOT" \
  --sample-id "$SAMPLE_ID" \
  --lhe "$LHE" \
  --strict \
  --output "$RUN_DIR/sample_validation.json" \
  | tee "$RUN_DIR/sample_validation.log"

python3 - "$RUN_DIR" "$SAMPLE_ID" "$LHE" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

run_dir = Path(sys.argv[1])
sample_id = sys.argv[2]
lhe = Path(sys.argv[3])
validation = json.loads((run_dir / "sample_validation.json").read_text())
if validation.get("status") != "pass":
    raise SystemExit("sample validation did not pass")
payload = {
    "schema_version": 1,
    "sample_id": sample_id,
    "completed_utc": datetime.now(timezone.utc).isoformat(),
    "lhe_path": str(lhe),
    "events_audited": validation["events_audited"],
    "cross_section_pb": validation["header"]["cross_section_pb"],
    "cross_section_error_pb": validation["header"]["cross_section_error_pb"],
    "validation_path": str(run_dir / "sample_validation.json"),
    "status": "pass",
}
(run_dir / "sample_complete.json").write_text(json.dumps(payload, indent=2) + "\n")
PY

(
  cd "$RUN_DIR"
  find . -maxdepth 1 -type f ! -name SHA256SUMS.txt -print0 \
    | sort -z \
    | xargs -0 sha256sum \
    > SHA256SUMS.txt
  sha256sum -c SHA256SUMS.txt >/dev/null
)

echo "PASS: $SAMPLE_ID"
