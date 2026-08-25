#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
from pathlib import Path

EXPECTED_ORIGINAL_SOURCE_SHA = "2246641146c35f49a1825344343a697cbbf6542828906b10cf7c06a3f81384f9"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def shell_quote_simple(value: str) -> str:
    if "'" in value:
        raise ValueError(f"single quote unsupported in shell value: {value}")
    return "'" + value + "'"


def dag_quote(value: str) -> str:
    if '"' in value or "\n" in value:
        raise ValueError(f"unsupported DAG VARS value: {value!r}")
    return value


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--package-root", type=Path, required=True)
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--source-card", type=Path, required=True)
    p.add_argument("--submission-dir", type=Path, required=True)
    p.add_argument("--output-root", type=Path, required=True)
    p.add_argument(
        "--expected-original-source-sha",
        default=EXPECTED_ORIGINAL_SOURCE_SHA,
    )
    p.add_argument("--allow-source-sha-mismatch", action="store_true")
    args = p.parse_args()

    pkg = args.package_root.resolve()
    repo = args.repo.resolve()
    source_card = args.source_card.resolve()
    sub = args.submission_dir.resolve()
    out = args.output_root

    if not source_card.is_file():
        raise SystemExit(f"ERROR: missing source card: {source_card}")
    if not repo.is_dir():
        raise SystemExit(f"ERROR: missing repo: {repo}")

    original_sha = sha256(source_card)
    if original_sha != args.expected_original_source_sha and not args.allow_source_sha_mismatch:
        raise SystemExit(
            "ERROR: unrestricted source-card SHA differs from the frozen Phase-11 value.\n"
            f"expected={args.expected_original_source_sha}\n"
            f"actual  ={original_sha}\n"
            "Refusing to prepare 480 jobs. Inspect the change first."
        )

    if sub.exists() and any(sub.iterdir()):
        raise SystemExit(f"ERROR: submission directory is not empty: {sub}")

    sub.mkdir(parents=True, exist_ok=True)
    (sub / "logs").mkdir()
    (sub / "frozen_config").mkdir()
    (sub / "frozen_source" / "common").mkdir(parents=True)
    (sub / "scripts").mkdir()

    for name in ("adaptive_prescriptions.tsv", "fixed_prescriptions.tsv", "seeds.tsv"):
        shutil.copy2(pkg / "config" / name, sub / "frozen_config" / name)

    for name in (
        "run_adaptive_parent.sh",
        "run_fixed_child.sh",
        "status_campaign.sh",
        "collect_results.py",
        "submit_campaign.sh",
        "preflight_campaign.sh",
    ):
        src = pkg / "scripts" / name
        if not src.is_file():
            raise SystemExit(f"ERROR: package script missing: {src}")
        shutil.copy2(src, sub / "scripts" / name)
        os.chmod(sub / "scripts" / name, 0o755)

    source_dir = source_card.parent
    frozen_source = sub / "frozen_source"
    shutil.copytree(source_dir / "common", frozen_source / "common", dirs_exist_ok=True)
    if (source_dir / "render_context.json").is_file():
        shutil.copy2(source_dir / "render_context.json", frozen_source / "render_context.json")

    text = source_card.read_text()
    old_common = str(source_dir / "common")
    new_common = str(frozen_source / "common")
    if old_common not in text:
        raise SystemExit("ERROR: process.sin does not contain expected absolute common path")
    text = text.replace(old_common, new_common)
    frozen_card = frozen_source / "process.sin"
    frozen_card.write_text(text)
    frozen_sha = sha256(frozen_card)

    adaptive = read_tsv(sub / "frozen_config" / "adaptive_prescriptions.tsv")
    fixed = read_tsv(sub / "frozen_config" / "fixed_prescriptions.tsv")
    seeds = read_tsv(sub / "frozen_config" / "seeds.tsv")

    if (len(adaptive), len(fixed), len(seeds)) != (15, 3, 8):
        raise SystemExit(
            f"ERROR: design cardinality mismatch: adaptive={len(adaptive)} "
            f"fixed={len(fixed)} seeds={len(seeds)}"
        )

    campaign_env = sub / "campaign.env"
    campaign_env.write_text(
        "\n".join(
            [
                f"REPO={shell_quote_simple(str(repo))}",
                f"SOURCE_CARD={shell_quote_simple(str(frozen_card))}",
                f"FROZEN_SOURCE_CARD_SHA256={shell_quote_simple(frozen_sha)}",
                f"ORIGINAL_SOURCE_CARD={shell_quote_simple(str(source_card))}",
                f"ORIGINAL_SOURCE_CARD_SHA256={shell_quote_simple(original_sha)}",
                f"OUTPUT_ROOT={shell_quote_simple(str(out))}",
                "",
            ]
        )
    )

    parent_sub = sub / "adaptive_parent.sub"
    parent_sub.write_text(
        f"""universe = vanilla

executable = {sub}/scripts/run_adaptive_parent.sh
arguments = --mode $(mode) --adaptive-id $(adaptive_id) --seed-id $(seed_id) --campaign-dir {sub} --output-root {out}

initialdir = {sub}
should_transfer_files = NO
getenv = True

request_cpus = 1
request_memory = 3000MB
request_disk = 6000MB

+JobFlavour = \"tomorrow\"

output = logs/$(mode).$(ClusterId).$(ProcId).out
error  = logs/$(mode).$(ClusterId).$(ProcId).err
log    = logs/adaptive.$(ClusterId).log

notification = Never
queue
"""
    )

    fixed_sub = sub / "fixed_child.sub"
    fixed_sub.write_text(
        f"""universe = vanilla

executable = {sub}/scripts/run_fixed_child.sh
arguments = --mode $(mode) --parent-mode $(parent_mode) --adaptive-id $(adaptive_id) --fixed-id $(fixed_id) --seed-id $(seed_id) --campaign-dir {sub} --output-root {out}

initialdir = {sub}
should_transfer_files = NO
getenv = True

request_cpus = 1
request_memory = 3000MB
request_disk = 6000MB

+JobFlavour = \"tomorrow\"

output = logs/$(mode).$(ClusterId).$(ProcId).out
error  = logs/$(mode).$(ClusterId).$(ProcId).err
log    = logs/fixed.$(ClusterId).log

notification = Never
queue
"""
    )

    dag_lines: list[str] = []
    rows: list[dict[str, str]] = []

    for a in adaptive:
        aid = a["adaptive_id"]
        for s in seeds:
            sid = s["seed_id"]
            parent_mode = f"{aid}_{sid}"
            pnode = f"P_{parent_mode}"
            dag_lines.append(f"JOB {pnode} {parent_sub}")
            dag_lines.append(
                f'VARS {pnode} mode="{dag_quote(parent_mode)}" '
                f'adaptive_id="{aid}" seed_id="{sid}"'
            )
            rows.append(
                {
                    "node": pnode,
                    "stage": "adaptive",
                    "mode": parent_mode,
                    "parent_mode": "",
                    "adaptive_id": aid,
                    "fixed_id": "",
                    "seed_id": sid,
                    "adaptive_seed": s["adaptive_seed"],
                    "fixed_seed": s["fixed_seed"],
                    "adaptive_schedule": a["schedule"],
                    "fixed_schedule": "",
                    "output_dir": str(out / "adaptive" / parent_mode),
                }
            )

            children = []
            for frow in fixed:
                fid = frow["fixed_id"]
                cmode = f"{parent_mode}_{fid}"
                cnode = f"C_{cmode}"
                children.append(cnode)
                dag_lines.append(f"JOB {cnode} {fixed_sub}")
                dag_lines.append(
                    f'VARS {cnode} mode="{cmode}" parent_mode="{parent_mode}" '
                    f'adaptive_id="{aid}" fixed_id="{fid}" seed_id="{sid}"'
                )
                rows.append(
                    {
                        "node": cnode,
                        "stage": "fixed",
                        "mode": cmode,
                        "parent_mode": parent_mode,
                        "adaptive_id": aid,
                        "fixed_id": fid,
                        "seed_id": sid,
                        "adaptive_seed": s["adaptive_seed"],
                        "fixed_seed": s["fixed_seed"],
                        "adaptive_schedule": a["schedule"],
                        "fixed_schedule": frow["suffix_schedule"],
                        "output_dir": str(out / "fixed" / parent_mode / fid),
                    }
                )
            dag_lines.append(f"PARENT {pnode} CHILD {' '.join(children)}")
            dag_lines.append("")

    if len(rows) != 480:
        raise SystemExit(f"ERROR: expected 480 DAG nodes, got {len(rows)}")

    (sub / "campaign.dag").write_text("\n".join(dag_lines))

    manifest = sub / "campaign_manifest.tsv"
    fields = list(rows[0].keys())
    with manifest.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    design = {
        "schema": "phase11_unrestricted_stability_scan_480_v1",
        "physics": "unrestricted full6f e- e+ -> b bbar e+ nue mu- numubar",
        "sqrt_s_GeV": 365,
        "polarization": "LR100",
        "integrator": "VAMP2",
        "rng_method": "rng_stream",
        "vamp_parallel_method": "simple",
        "mpi_ranks": 1,
        "omp_threads": 1,
        "adaptive_prescriptions": 15,
        "seed_replicas": 8,
        "fixed_prescriptions": 3,
        "adaptive_parent_jobs": 120,
        "fixed_child_jobs": 360,
        "total_dag_nodes": 480,
        "original_source_card": str(source_card),
        "original_source_card_sha256": original_sha,
        "frozen_source_card": str(frozen_card),
        "frozen_source_card_sha256": frozen_sha,
        "output_root": str(out),
    }
    (sub / "CAMPAIGN_DESIGN.json").write_text(json.dumps(design, indent=2) + "\n")

    policy_text = """Phase 11 unrestricted integration-stability scan v1

This campaign is diagnostic. No single Axx/Sx/Fx result may be promoted
because it looks numerically favorable. Qualification is by prescription
family across all eight predetermined adaptive seeds.

The adaptive and fixed stages are intentionally separated. Each F0/F1/F2
sibling restores the byte-identical adaptive-parent PHS/VG2 workspace.
The fixed-stage worker requests the complete stored adaptive prefix plus
the fixed suffix, so VAMP2 must reuse the stored prefix and compute only
the missing fixed iterations. A child fails if WHIZARD initializes a new
grid rather than reusing the parent workspace.

Do not replace failed physics seeds with new seeds. Technical reruns, if
needed, must use the identical node configuration.
"""
    (sub / "DECISION_POLICY.txt").write_text(policy_text)

    hash_targets = [
        sub / "campaign.env",
        sub / "CAMPAIGN_DESIGN.json",
        sub / "DECISION_POLICY.txt",
        sub / "campaign_manifest.tsv",
        sub / "campaign.dag",
        sub / "adaptive_parent.sub",
        sub / "fixed_child.sub",
        *sorted((sub / "frozen_config").glob("*")),
        *sorted((sub / "frozen_source").rglob("*")),
        *sorted((sub / "scripts").glob("*")),
    ]
    hash_targets = [x for x in hash_targets if x.is_file()]
    with (sub / "PRE_SUBMISSION_INPUTS.sha256").open("w") as f:
        for path in hash_targets:
            f.write(f"{sha256(path)}  {path}\n")

    print(f"SUBMISSION_DIR={sub}")
    print(f"OUTPUT_ROOT={out}")
    print(f"ORIGINAL_SOURCE_SHA256={original_sha}")
    print(f"FROZEN_SOURCE_SHA256={frozen_sha}")
    print("ADAPTIVE_PARENT_JOBS=120")
    print("FIXED_CHILD_JOBS=360")
    print("TOTAL_DAG_NODES=480")
    print("CAMPAIGN_PREPARE=PASS")


if __name__ == "__main__":
    main()
