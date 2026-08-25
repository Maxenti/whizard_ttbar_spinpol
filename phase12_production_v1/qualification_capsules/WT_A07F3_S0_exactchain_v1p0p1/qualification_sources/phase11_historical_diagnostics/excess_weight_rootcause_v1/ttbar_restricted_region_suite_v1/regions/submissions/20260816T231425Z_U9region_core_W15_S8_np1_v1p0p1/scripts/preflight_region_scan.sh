#!/usr/bin/env bash
set -euo pipefail
C=$(readlink -f "$1"); "$C/scripts/preflight_common.sh" "$C"
# All region cards MUST remain diagram-unrestricted.
if grep -R '\$restrictions' "$C/region_sources"; then echo 'ERROR region source contains restrictions' >&2; exit 9; fi
for f in "$C"/region_sources/*/*/common/region_cuts.inc; do grep -F 'cuts =' "$f" >/dev/null; done
# Real WHIZARD syntax smoke using a tiny fixed integration on W15/II.
source "$C/campaign.env"; SRC=$(find "$REGION_SOURCE_ROOT" -path '*/W15/II/process.sin' -print -quit); [[ -f "$SRC" ]] || SRC=$(find "$REGION_SOURCE_ROOT" -path '*/II/process.sin' -print -quit)
source "$REPO/environments/setup_whizard_3p1p8_mpi_qualified.sh"; W=$(mktemp -d /tmp/${USER}_region_syntax_XXXX); trap 'rm -rf "$W"' EXIT; mkdir -p "$W/common"; cp "$SRC" "$W/process.sin"; cp -a "$(dirname "$SRC")/common/." "$W/common/"
python3 - "$W/process.sin" "$(dirname "$SRC")/common" <<'PY_R'
from pathlib import Path
import re,sys
p=Path(sys.argv[1]);src=sys.argv[2];t=p.read_text();t,n=re.subn(r'include\("'+re.escape(src)+r'/([^\"]+)"\)',lambda m:f'include("common/{m.group(1)}")',t);t,n2=re.subn(r'^.*include\("common/event_output\.inc"\).*$\n?','',t,flags=re.M);p.write_text(t)
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
(cd "$W" && whizard process.sin > smoke.log 2>&1) || { cat "$W/smoke.log"; echo 'ERROR: real WHIZARD region-cut syntax smoke failed' >&2; exit 10; }
grep -E 'proc_epmum|integral|VAMP' "$W/smoke.log" | tail -n 30 || true
echo REGION_PREFLIGHT=PASS
