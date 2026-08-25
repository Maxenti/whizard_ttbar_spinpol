#!/usr/bin/env bash
set -euo pipefail
MODE=""; SEED_ID=""; CAMPAIGN_DIR=""; OUTPUT_ROOT=""
while [[ $# -gt 0 ]]; do case "$1" in
 --mode) MODE="$2"; shift 2;; --seed-id) SEED_ID="$2"; shift 2;; --campaign-dir) CAMPAIGN_DIR="$2"; shift 2;; --output-root) OUTPUT_ROOT="$2"; shift 2;; *) echo "ERROR unknown $1" >&2; exit 2;; esac; done
for V in MODE SEED_ID CAMPAIGN_DIR OUTPUT_ROOT; do [[ -n "${!V}" ]] || { echo "missing $V" >&2; exit 2; }; done
source "$CAMPAIGN_DIR/campaign.env"
SEEDS="$CAMPAIGN_DIR/frozen_config/seeds.tsv"
SEED=$(awk -F '\t' -v id="$SEED_ID" 'NR>1 && $1==id {print $2;exit}' "$SEEDS")
[[ -n "$SEED" ]] || exit 2
DEST="$OUTPUT_ROOT/control/$MODE"; mkdir -p "$DEST"
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 BLIS_NUM_THREADS=1 MALLOC_ARENA_MAX=2
SP="${_CONDOR_SCRATCH_DIR:-/tmp}"; WORK=$(mktemp -d "$SP/${USER:-u}_${MODE}_XXXX"); trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK/common"; cp -a "$SOURCE_CARD" "$WORK/process.sin"; cp -a "$(dirname "$SOURCE_CARD")/common/." "$WORK/common/"
[[ -f "$(dirname "$SOURCE_CARD")/render_context.json" ]] && cp -a "$(dirname "$SOURCE_CARD")/render_context.json" "$WORK/"
python3 - "$WORK/process.sin" "$(dirname "$SOURCE_CARD")/common" <<'PY_LOCAL'
from pathlib import Path
import re,sys
p=Path(sys.argv[1]); src=sys.argv[2]; t=p.read_text()
t,n=re.subn(r'include\("'+re.escape(src)+r'/([^\"]+)"\)',lambda m:f'include("common/{m.group(1)}")',t)
t,n2=re.subn(r'^.*include\("common/event_output\.inc"\).*$\n?','',t,flags=re.M)
if n<5 or n2!=1: raise SystemExit(f'localization failed n={n} event={n2}')
p.write_text(t)
PY_LOCAL
cat > "$WORK/common/integration.inc" <<EOF_CTL
\$integration_method = "vamp"
\$rng_method = "tao"
\$vamp_parallel_method = "simple"
?omega_openmp = false
openmp_num_threads = 1
seed = $SEED
iterations = 10:100000:"gw",10:200000:""
integrate (proc_epmum)
EOF_CTL
source "$REPO/environments/setup_whizard_3p1p8_mpi_qualified.sh"
EXPECTED=$(readlink -f "$REPO/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/whizard"); ACTUAL=$(readlink -f "$(command -v whizard)")
[[ "$EXPECTED" == "$ACTUAL" ]] || { echo 'WHIZARD path mismatch' >&2; exit 5; }
cd "$WORK"; set +e; set -o pipefail; whizard process.sin 2>&1 | tee console.log; RC=${PIPESTATUS[0]}; set +o pipefail; set -e
STATUS=PASS; [[ $RC -eq 0 ]] || STATUS=FAIL_WHIZARD
python3 - metadata.json "$STATUS" "$MODE" "$SEED_ID" "$SEED" "$RC" "$ACTUAL" <<'PY_META'
import json,sys
from pathlib import Path
out,status,mode,sid,seed,rc,exe=sys.argv[1:]
Path(out).write_text(json.dumps(dict(schema='phase11_ttbar_suite_legacy_control_v1',status=status,mode=mode,seed_id=sid,adaptive_seed=int(seed),schedule='10:100000:"gw",10:200000:""',integration_method='vamp',rng_method='tao',whizard_rc=int(rc),whizard_realpath=exe),indent=2)+'\n')
PY_META
cp -a console.log metadata.json process.sin "$DEST/"; rm -rf "$DEST/common"; cp -a common "$DEST/common"; printf '%s\n' "$STATUS" > "$DEST/STATUS.txt"
# VAMP artifact suffixes differ from VAMP2; archive whatever integration state exists.
find . -maxdepth 1 -type f \( -name '*.phs' -o -name '*.vg*' -o -name '*.grd' \) -print0 | tar --null -T - -czf integration_artifacts.tar.gz 2>/dev/null || true
[[ -s integration_artifacts.tar.gz ]] && cp -a integration_artifacts.tar.gz "$DEST/"
[[ "$STATUS" == PASS ]] || exit 20
touch "$DEST/EXECUTION_SUCCESS"; echo CONTROL_STATUS=PASS
