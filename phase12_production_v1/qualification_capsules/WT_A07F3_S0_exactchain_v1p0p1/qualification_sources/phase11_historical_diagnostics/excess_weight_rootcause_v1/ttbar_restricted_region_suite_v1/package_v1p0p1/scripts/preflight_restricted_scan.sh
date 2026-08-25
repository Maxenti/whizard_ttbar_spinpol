#!/usr/bin/env bash
set -euo pipefail
C=$(readlink -f "$1")
"$C/scripts/preflight_common.sh" "$C"
grep -F '$restrictions = "5+6~W+ && 7+8~W- && 3+5+6~t && 4+7+8~tbar"' "$C/frozen_source/process.sin" >/dev/null

# Exercise all 15 schedule lookups/source-contract paths without spending CPU.
for A in $(seq -w 0 14); do
  "$C/scripts/run_adaptive_parent.sh" --mode "A${A}_S0" --adaptive-id "A${A}" --seed-id S0 --campaign-dir "$C" --output-root /tmp/ttbar_suite_preflight --preflight-only >/dev/null
done

# Then run one genuinely small integration.  This catches a malformed O'Mega
# restriction or version-specific SINDARIN problem that shell/Python syntax
# checks cannot detect.
source "$C/campaign.env"
source "$REPO/environments/setup_whizard_3p1p8_mpi_qualified.sh"
W=$(mktemp -d /tmp/${USER}_restricted_syntax_XXXX)
trap 'rm -rf "$W"' EXIT
mkdir -p "$W/common"
cp "$SOURCE_CARD" "$W/process.sin"
cp -a "$(dirname "$SOURCE_CARD")/common/." "$W/common/"
python3 - "$W/process.sin" "$(dirname "$SOURCE_CARD")/common" <<'PY_R'
from pathlib import Path
import re,sys
p=Path(sys.argv[1]);src=sys.argv[2];t=p.read_text()
t,_=re.subn(r'include\("'+re.escape(src)+r'/([^\"]+)"\)',lambda m:f'include("common/{m.group(1)}")',t)
t,n=re.subn(r'^.*include\("common/event_output\.inc"\).*$\n?','',t,flags=re.M)
if n!=1: raise SystemExit(f'expected one event-output include, removed {n}')
p.write_text(t)
PY_R
cat > "$W/common/integration.inc" <<'EOF_R'
$integration_method = "vamp2"
$rng_method = "rng_stream"
$vamp_parallel_method = "simple"
?omega_openmp = false
openmp_num_threads = 1
seed = 1740114216
iterations = 1:2000:""
integrate (proc_epmum)
EOF_R
(cd "$W" && whizard process.sin > smoke.log 2>&1) || { cat "$W/smoke.log"; echo 'ERROR: real restricted-WT WHIZARD smoke failed' >&2; exit 10; }
grep -E 'proc_epmum|channels,|VAMP|FATAL' "$W/smoke.log" | tail -n 40 || true
"$C/scripts/audit_source_physics.py" --campaign-dir "$C" >/dev/null
echo RESTRICTED_PREFLIGHT=PASS
