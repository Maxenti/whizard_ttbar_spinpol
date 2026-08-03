#!/usr/bin/env bash
set -euo pipefail

REPO="${REPO:-/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol}"
CAMPAIGN_ID="${CAMPAIGN_ID:-full6f_365gev_ee_ttbar_spinpol_v1}"
STAMP="${STAMP:-$(date -u +%Y%m%dT%H%M%SZ)}"

CAMPAIGN_DIR="$REPO/campaigns/$CAMPAIGN_ID"
GENERATED_DIR="$REPO/sindarin/generated/$CAMPAIGN_ID"
TEMPLATE_DIR="$REPO/sindarin/templates/full6f_365gev_v1"

AUDIT_ROOT="$CAMPAIGN_DIR/phase10A_production_definition"
AUDIT_DIR="$AUDIT_ROOT/audits/$STAMP"
SNAPSHOT_DIR="$AUDIT_DIR/snapshot"
REPORT="$AUDIT_DIR/PHASE10A_BASELINE_AUDIT.txt"
MANIFEST="$AUDIT_DIR/phase10A_baseline_manifest.json"

mkdir -p \
  "$AUDIT_DIR" \
  "$SNAPSHOT_DIR/generated" \
  "$SNAPSHOT_DIR/templates" \
  "$SNAPSHOT_DIR/configs" \
  "$SNAPSHOT_DIR/environments"

exec > >(tee "$REPORT") 2>&1

echo "PHASE10A_BASELINE_AUDIT_BEGIN"
echo "UTC_STAMP=$STAMP"
echo "REPO=$REPO"
echo "CAMPAIGN_ID=$CAMPAIGN_ID"
echo "CAMPAIGN_DIR=$CAMPAIGN_DIR"
echo "GENERATED_DIR=$GENERATED_DIR"
echo "TEMPLATE_DIR=$TEMPLATE_DIR"
echo "AUDIT_DIR=$AUDIT_DIR"
echo

echo "================================================================"
echo "1. GIT PROVENANCE"
echo "================================================================"

git -C "$REPO" rev-parse HEAD
git -C "$REPO" branch --show-current
git -C "$REPO" status --short
git -C "$REPO" log -n 20 --oneline --decorate
git -C "$REPO" remote -v || true

git -C "$REPO" rev-parse HEAD \
  > "$AUDIT_DIR/git_commit.txt"

git -C "$REPO" branch --show-current \
  > "$AUDIT_DIR/git_branch.txt"

git -C "$REPO" status --short \
  > "$AUDIT_DIR/git_status_short.txt"

git -C "$REPO" diff \
  > "$AUDIT_DIR/git_worktree_diff.patch"

git -C "$REPO" diff --cached \
  > "$AUDIT_DIR/git_index_diff.patch"

echo

echo "================================================================"
echo "2. RUNTIME VERSIONS"
echo "================================================================"

echo "PATH=$PATH"
echo "LD_LIBRARY_PATH=${LD_LIBRARY_PATH:-}"
echo "PYTHONPATH=${PYTHONPATH:-}"

echo
echo "--- WHIZARD ---"
command -v whizard || true
whizard --version || true

echo
echo "--- PYTHIA8 ---"
command -v pythia8-config || true
pythia8-config --version || true
pythia8-config --prefix || true
pythia8-config --cxxflags || true
pythia8-config --libs || true

echo
echo "--- HEPMC3 ---"
command -v HepMC3-config || true
HepMC3-config --version || true
HepMC3-config --prefix || true

echo
echo "--- COMPILERS ---"
command -v gcc || true
gcc --version | head -n 2 || true
command -v g++ || true
g++ --version | head -n 2 || true

echo
echo "--- PYTHON ---"
command -v python3 || true
python3 --version || true

{
  echo "whizard=$(command -v whizard || true)"
  whizard --version 2>&1 || true
  echo "pythia8-config=$(command -v pythia8-config || true)"
  pythia8-config --version 2>&1 || true
  echo "HepMC3-config=$(command -v HepMC3-config || true)"
  HepMC3-config --version 2>&1 || true
  python3 --version 2>&1 || true
} > "$AUDIT_DIR/runtime_versions.txt"

echo

echo "================================================================"
echo "3. GENERATED CARD INVENTORY"
echo "================================================================"

if [[ ! -d "$GENERATED_DIR" ]]; then
  echo "ERROR: generated campaign directory does not exist:"
  echo "  $GENERATED_DIR"
  exit 1
fi

find "$GENERATED_DIR" -type f -print \
  | sort \
  | tee "$AUDIT_DIR/generated_file_inventory.txt"

echo
echo "--- Generated file count ---"
wc -l "$AUDIT_DIR/generated_file_inventory.txt"

echo
echo "--- Process cards ---"
find "$GENERATED_DIR" -type f \
  \( -name '*.sin' -o -name '*.sin.in' \) \
  -print \
  | sort \
  | tee "$AUDIT_DIR/generated_process_cards.txt"

echo
echo "--- Include/config files ---"
find "$GENERATED_DIR" -type f \
  \( \
    -name '*.inc' -o \
    -name '*.cfg' -o \
    -name '*.yaml' -o \
    -name '*.yml' -o \
    -name '*.json' -o \
    -name '*.csv' \
  \) \
  -print \
  | sort \
  | tee "$AUDIT_DIR/generated_support_files.txt"

echo
echo "--- Checksums ---"
while IFS= read -r file; do
  sha256sum "$file"
done < "$AUDIT_DIR/generated_file_inventory.txt" \
  | tee "$AUDIT_DIR/generated_sha256.txt"

echo
echo "--- Snapshot generated cards ---"
(
  cd "$GENERATED_DIR"
  while IFS= read -r relative; do
    mkdir -p "$SNAPSHOT_DIR/generated/$(dirname "$relative")"
    cp -a "$relative" "$SNAPSHOT_DIR/generated/$relative"
  done < <(
    find . -type f \
      \( \
        -name '*.sin' -o \
        -name '*.inc' -o \
        -name '*.cfg' -o \
        -name '*.yaml' -o \
        -name '*.yml' -o \
        -name '*.json' -o \
        -name '*.csv' -o \
        -name '*.md5' \
      \) \
      -printf '%P\n' \
      | sort
  )
)

echo

echo "================================================================"
echo "4. TEMPLATE INVENTORY"
echo "================================================================"

if [[ -d "$TEMPLATE_DIR" ]]; then
  find "$TEMPLATE_DIR" -type f -print \
    | sort \
    | tee "$AUDIT_DIR/template_file_inventory.txt"

  while IFS= read -r file; do
    sha256sum "$file"
  done < "$AUDIT_DIR/template_file_inventory.txt" \
    | tee "$AUDIT_DIR/template_sha256.txt"

  cp -a "$TEMPLATE_DIR/." "$SNAPSHOT_DIR/templates/"
else
  echo "WARNING: template directory not found:"
  echo "  $TEMPLATE_DIR"
fi

echo

echo "================================================================"
echo "5. RELEVANT CONFIGURATION INVENTORY"
echo "================================================================"

find \
  "$REPO/configs" \
  "$REPO/analysis_contracts" \
  "$CAMPAIGN_DIR" \
  -type f \
  \( \
    -iname '*365*' -o \
    -iname '*full6f*' -o \
    -iname '*phase9*' -o \
    -iname '*spin*' -o \
    -iname '*qis*' -o \
    -iname '*polar*' -o \
    -iname '*pythia*' -o \
    -iname '*hepmc*' \
  \) \
  -print 2>/dev/null \
  | sort -u \
  | tee "$AUDIT_DIR/relevant_config_inventory.txt"

while IFS= read -r file; do
  [[ -f "$file" ]] || continue
  relative="${file#"$REPO"/}"
  mkdir -p "$SNAPSHOT_DIR/configs/$(dirname "$relative")"
  cp -a "$file" "$SNAPSHOT_DIR/configs/$relative"
done < "$AUDIT_DIR/relevant_config_inventory.txt"

echo

echo "================================================================"
echo "6. ENVIRONMENT AND DRIVER INVENTORY"
echo "================================================================"

find \
  "$REPO/environments" \
  "$REPO/scripts/production" \
  "$REPO/scripts/showering" \
  "$REPO/scripts/sindarin" \
  -maxdepth 4 \
  -type f \
  \( \
    -name '*.sh' -o \
    -name '*.py' -o \
    -name '*.yaml' -o \
    -name '*.json' \
  \) \
  -print 2>/dev/null \
  | sort \
  | tee "$AUDIT_DIR/runtime_driver_inventory.txt"

while IFS= read -r file; do
  [[ -f "$file" ]] || continue
  relative="${file#"$REPO"/}"
  mkdir -p "$SNAPSHOT_DIR/environments/$(dirname "$relative")"
  cp -a "$file" "$SNAPSHOT_DIR/environments/$relative"
done < "$AUDIT_DIR/runtime_driver_inventory.txt"

echo

echo "================================================================"
echo "7. PHYSICS-SETTING EXTRACTION"
echo "================================================================"

PHYSICS_PATTERN='
sqrts|sqrt_s|beams|beam|polar|pol_degree|helicity|
isr|circe|beamstrahlung|spectrum|
m_top|top_mass|w_top|top_width|mass\(6\)|width\(6\)|
m_W|w_W|m_Z|w_Z|alpha_s|alpha_em|G_F|sin.*theta|
model|SM|CKM|
process|integrate|iterations|calls|grid|
seed|random|
n_events|events|unweight|weight|
sample_format|hepmc|lhe|event_output|
factorization|renormalization|scale|
pythia|shower|hadron|decay
'

find "$GENERATED_DIR" -type f \
  \( -name '*.sin' -o -name '*.inc' -o -name '*.cfg' \) \
  -print0 \
  | sort -z \
  | xargs -0 grep -nEi "$PHYSICS_PATTERN" \
  | tee "$AUDIT_DIR/generated_physics_settings_grep.txt" \
  || true

echo
echo "--- Template physics settings ---"

if [[ -d "$TEMPLATE_DIR" ]]; then
  find "$TEMPLATE_DIR" -type f \
    \( -name '*.sin.in' -o -name '*.inc.in' -o -name '*.cfg' \) \
    -print0 \
    | sort -z \
    | xargs -0 grep -nEi "$PHYSICS_PATTERN" \
    | tee "$AUDIT_DIR/template_physics_settings_grep.txt" \
    || true
fi

echo

echo "================================================================"
echo "8. POLARIZATION CARD DIFFS"
echo "================================================================"

mapfile -t EPMUM_CARDS < <(
  find "$GENERATED_DIR" -type f -path '*/epmum/process.sin' -print \
    | sort
)

printf '%s\n' "${EPMUM_CARDS[@]}" \
  > "$AUDIT_DIR/epmum_process_cards.txt"

echo "N_EPMUM_PROCESS_CARDS=${#EPMUM_CARDS[@]}"

for card in "${EPMUM_CARDS[@]}"; do
  echo
  echo "----------------------------------------------------------------"
  echo "CARD=$card"
  echo "----------------------------------------------------------------"
  sed -n '1,260p' "$card"
done | tee "$AUDIT_DIR/epmum_process_cards_full.txt"

if [[ ${#EPMUM_CARDS[@]} -ge 2 ]]; then
  : > "$AUDIT_DIR/epmum_pairwise_diffs.txt"

  for ((i = 0; i < ${#EPMUM_CARDS[@]}; i++)); do
    for ((j = i + 1; j < ${#EPMUM_CARDS[@]}; j++)); do
      {
        echo
        echo "================================================================"
        echo "DIFF"
        echo "A=${EPMUM_CARDS[$i]}"
        echo "B=${EPMUM_CARDS[$j]}"
        echo "================================================================"

        diff -u \
          "${EPMUM_CARDS[$i]}" \
          "${EPMUM_CARDS[$j]}" \
          || true
      } >> "$AUDIT_DIR/epmum_pairwise_diffs.txt"
    done
  done

  cat "$AUDIT_DIR/epmum_pairwise_diffs.txt"
fi

echo

echo "================================================================"
echo "9. INCLUDE RESOLUTION"
echo "================================================================"

python3 - "$GENERATED_DIR" "$AUDIT_DIR/include_resolution.json" <<'PY'
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2])

include_re = re.compile(
    r'^\s*include\s*\(\s*"([^"]+)"\s*\)',
    re.IGNORECASE,
)

records = []

for card in sorted(root.rglob("*.sin")):
    includes = []

    for lineno, line in enumerate(
        card.read_text(encoding="utf-8", errors="replace").splitlines(),
        1,
    ):
        match = include_re.search(line)

        if not match:
            continue

        include_text = match.group(1)
        candidate = (card.parent / include_text).resolve()

        includes.append({
            "line": lineno,
            "include": include_text,
            "resolved_path": str(candidate),
            "exists": candidate.is_file(),
        })

    records.append({
        "card": str(card),
        "includes": includes,
        "all_includes_exist": all(item["exists"] for item in includes),
    })

payload = {
    "schema_version": 1,
    "generated_root": str(root),
    "cards": records,
    "status": (
        "PASS"
        if all(record["all_includes_exist"] for record in records)
        else "FAIL"
    ),
}

output.write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

print(f"INCLUDE_RESOLUTION_STATUS={payload['status']}")
print(f"N_CARDS={len(records)}")
print(f"WROTE={output}")

for record in records:
    if not record["all_includes_exist"]:
        print(f"FAILED_CARD={record['card']}")
        for include in record["includes"]:
            if not include["exists"]:
                print(
                    f"  line={include['line']} "
                    f"include={include['include']} "
                    f"resolved={include['resolved_path']}"
                )
PY

echo

echo "================================================================"
echo "10. MACHINE-READABLE BASELINE MANIFEST"
echo "================================================================"

python3 - \
  "$REPO" \
  "$CAMPAIGN_ID" \
  "$STAMP" \
  "$GENERATED_DIR" \
  "$TEMPLATE_DIR" \
  "$AUDIT_DIR" \
  "$MANIFEST" <<'PY'
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

repo = Path(sys.argv[1]).resolve()
campaign_id = sys.argv[2]
stamp = sys.argv[3]
generated_dir = Path(sys.argv[4]).resolve()
template_dir = Path(sys.argv[5]).resolve()
audit_dir = Path(sys.argv[6]).resolve()
manifest_path = Path(sys.argv[7]).resolve()


def run(*args: str) -> str:
    return subprocess.check_output(
        args,
        cwd=repo,
        text=True,
        stderr=subprocess.STDOUT,
    ).strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest()


def inventory(root: Path) -> list[dict[str, object]]:
    if not root.is_dir():
        return []

    records = []

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue

        records.append({
            "path": str(path),
            "relative_path": str(path.relative_to(root)),
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
        })

    return records


payload = {
    "schema_version": 1,
    "status": "PASS",
    "campaign_id": campaign_id,
    "utc_stamp": stamp,
    "repository": {
        "root": str(repo),
        "git_commit": run("git", "rev-parse", "HEAD"),
        "git_branch": run("git", "branch", "--show-current"),
        "git_status_short": run("git", "status", "--short"),
    },
    "runtime": {
        "whizard_path": run("bash", "-lc", "command -v whizard || true"),
        "whizard_version": run(
            "bash",
            "-lc",
            "whizard --version 2>&1 || true",
        ),
        "pythia8_config_path": run(
            "bash",
            "-lc",
            "command -v pythia8-config || true",
        ),
        "pythia8_version": run(
            "bash",
            "-lc",
            "pythia8-config --version 2>&1 || true",
        ),
        "hepmc3_config_path": run(
            "bash",
            "-lc",
            "command -v HepMC3-config || true",
        ),
        "hepmc3_version": run(
            "bash",
            "-lc",
            "HepMC3-config --version 2>&1 || true",
        ),
        "python_version": run(
            "bash",
            "-lc",
            "python3 --version 2>&1 || true",
        ),
    },
    "generated_root": str(generated_dir),
    "template_root": str(template_dir),
    "generated_files": inventory(generated_dir),
    "template_files": inventory(template_dir),
    "audit_directory": str(audit_dir),
    "notes": [
        "This manifest captures the validated pre-Phase-10A baseline.",
        "It is an inventory product and does not yet assert production qualification.",
        "Physics differences and required changes are evaluated in later Phase 10A gates.",
    ],
}

manifest_path.write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

print("PHASE10A_BASELINE_MANIFEST_STATUS=PASS")
print(f"N_GENERATED_FILES={len(payload['generated_files'])}")
print(f"N_TEMPLATE_FILES={len(payload['template_files'])}")
print(f"WROTE_MANIFEST={manifest_path}")
PY

echo

echo "================================================================"
echo "11. AUDIT OUTPUT CHECKSUMS"
echo "================================================================"

find "$AUDIT_DIR" -type f ! -name 'audit_sha256.txt' -print0 \
  | sort -z \
  | xargs -0 sha256sum \
  | tee "$AUDIT_DIR/audit_sha256.txt"

echo
echo "PHASE10A_BASELINE_AUDIT_STATUS=PASS"
echo "PHASE10A_BASELINE_AUDIT_DIR=$AUDIT_DIR"
echo "PHASE10A_BASELINE_REPORT=$REPORT"
echo "PHASE10A_BASELINE_MANIFEST=$MANIFEST"
