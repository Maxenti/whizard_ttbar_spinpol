#!/usr/bin/env bash
set -euo pipefail

REPO=${REPO:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)}
cd "$REPO"
source "$REPO/setup_lxplus.sh"

SOURCE=${SOURCE:-$REPO/tests/qis/data/smoke_lhe/ee_ttbar_epmum_LR100_sc_ISR_500GeV.lhe}
[[ -r $SOURCE ]] || { echo "ERROR: missing smoke LHE: $SOURCE" >&2; exit 1; }
[[ -x $REPO/build/qis_lhe_to_hepmc3 ]] \
  || { echo "ERROR: missing shower executable" >&2; exit 1; }

STAMP=$(date -u +%Y%m%dT%H%M%SZ)
LOCAL=$(mktemp -d "/tmp/${USER}/qis_sharded_worker_smoke_XXXXXX")
EOS_ROOT=/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/qis/qualification/sharded_worker_smoke_${STAMP}
cleanup() {
  rm -rf "$LOCAL"
  rm -rf "$EOS_ROOT"
}
trap cleanup EXIT

python3 - "$REPO" "$SOURCE" "$LOCAL" <<'PY'
import importlib.util
import sys
from pathlib import Path

repo = Path(sys.argv[1])
source = Path(sys.argv[2])
local = Path(sys.argv[3])
script = repo / "scripts/showering/prepare_lhe_shards.py"
spec = importlib.util.spec_from_file_location("prepare_lhe_shards_smoke", script)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
rows = module.write_sample_shards(
    campaign_id="sharded_worker_smoke",
    sample_id="ee_ttbar_epmum_LR100_sc_ISR_500GeV",
    source=source,
    output_dir=local / "input_shards",
    plans=module.balanced_plan(1, 1),
    created_utc="smoke",
)
(local / "row.json").write_text(__import__("json").dumps(rows[0], indent=2) + "\n")
PY

ROW=$LOCAL/row.json
SHARD=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["shard_lhe_path"])' "$ROW")
SHA=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["shard_lhe_sha256"])' "$ROW")

"$REPO/scripts/showering/run_pythia_shard.sh" \
  --input "$SHARD" \
  --input-sha256 "$SHA" \
  --parent-lhe "$SOURCE" \
  --source-event-start 0 \
  --source-event-stop 1 \
  --output-root "$EOS_ROOT/shower" \
  --sample-id ee_ttbar_epmum_LR100_sc_ISR_500GeV \
  --campaign-id sharded_worker_smoke \
  --shard-id shard_0000 \
  --seed 994001 \
  --max-events 1 \
  --executable "$REPO/build/qis_lhe_to_hepmc3" \
  --settings "$REPO/configs/pythia/level_a.cmnd" \
  --key4hep-setup "$REPO/setup_lxplus.sh" \
  --repo-root "$REPO" \
  --qed-shower-by-gamma on

META="$EOS_ROOT/shower/metadata/ee_ttbar_epmum_LR100_sc_ISR_500GeV/ee_ttbar_epmum_LR100_sc_ISR_500GeV__shard_0000.json"
python3 - "$META" <<'PY'
import json
import sys
from pathlib import Path
path = Path(sys.argv[1])
data = json.loads(path.read_text())
assert data["status"] == "success"
assert data["return_code"] == 0
assert data["accepted_events"] == 1
assert data["requested_events"] == 1
assert data["preparation_event_limit_verified"] is True
assert data["source_event_range"] == {"start": 0, "stop_exclusive": 1, "events": 1}
assert data["preparation"]["canonical_v2"]["total_events"] == 1
assert data["preparation"]["explicit_w_v3"]["total_events"] == 1
assert data["preparation"]["explicit_w_v3"]["inserted_w_resonances"] == 2
print(f"SHARDED WORKER SMOKE PASS: {path}")
PY
