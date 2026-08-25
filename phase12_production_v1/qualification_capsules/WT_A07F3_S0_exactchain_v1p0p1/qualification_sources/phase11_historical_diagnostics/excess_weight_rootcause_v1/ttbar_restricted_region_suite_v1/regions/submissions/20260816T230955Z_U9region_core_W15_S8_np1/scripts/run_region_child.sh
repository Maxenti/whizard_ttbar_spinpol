#!/usr/bin/env bash
set -euo pipefail
REGION_ID=""; WINDOW_ID=""; REST=()
while [[ $# -gt 0 ]]; do case "$1" in --region-id) REGION_ID="$2";shift 2;; --window-id) WINDOW_ID="$2";shift 2;; *) REST+=("$1");shift;; esac; done
CAMPAIGN_DIR=""
for ((i=0;i<${#REST[@]};i++)); do [[ "${REST[$i]}" == --campaign-dir ]] && CAMPAIGN_DIR="${REST[$((i+1))]}"; done
source "$CAMPAIGN_DIR/campaign.env"
SOURCE_CARD="$REGION_SOURCE_ROOT/$WINDOW_ID/$REGION_ID/process.sin"; export SOURCE_CARD; export FROZEN_SOURCE_CARD_SHA256=$(sha256sum "$SOURCE_CARD"|awk '{print $1}')
# Standard worker sources campaign.env, so write a process-local overlay and point it through env variables is not possible. Create temp campaign.env copy? Instead worker accepts sourced variables only.
TMPENV=$(mktemp "$CAMPAIGN_DIR/.campaign.env.region.XXXXXX")
cp "$CAMPAIGN_DIR/campaign.env" "$TMPENV"
printf "SOURCE_CARD='%s'\nFROZEN_SOURCE_CARD_SHA256='%s'\n" "$SOURCE_CARD" "$FROZEN_SOURCE_CARD_SHA256" >> "$TMPENV"
# Standard worker is taught to honor CAMPAIGN_ENV_OVERRIDE. Use mktemp rather
# than a PID-only name because different execute hosts can share a PID.
export CAMPAIGN_ENV_OVERRIDE="$TMPENV"
set +e
"$CAMPAIGN_DIR/scripts/run_fixed_child.sh" "${REST[@]}"
RC=$?
set -e
rm -f "$TMPENV"
exit "$RC"
