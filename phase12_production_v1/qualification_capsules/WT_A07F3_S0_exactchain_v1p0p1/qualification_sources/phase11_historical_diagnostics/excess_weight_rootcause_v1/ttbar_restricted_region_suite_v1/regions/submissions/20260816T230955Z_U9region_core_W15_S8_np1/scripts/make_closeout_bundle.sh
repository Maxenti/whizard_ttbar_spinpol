#!/usr/bin/env bash
set -euo pipefail
[[ $# -eq 1 ]] || { echo 'usage make_closeout_bundle.sh CAMPAIGN_DIR' >&2;exit 2;}; C=$(readlink -f "$1"); ST=$(date -u +%Y%m%dT%H%M%SZ); OUT="$C/closeout_${ST}.tar.gz"
tar -czf "$OUT" -C "$C" campaign_manifest.tsv CAMPAIGN_DESIGN.json DECISION_POLICY.txt frozen_config collected analysis records 2>/dev/null || tar -czf "$OUT" -C "$C" campaign_manifest.tsv CAMPAIGN_DESIGN.json DECISION_POLICY.txt frozen_config collected analysis
sha256sum "$OUT" > "$OUT.sha256"; echo "$OUT"
