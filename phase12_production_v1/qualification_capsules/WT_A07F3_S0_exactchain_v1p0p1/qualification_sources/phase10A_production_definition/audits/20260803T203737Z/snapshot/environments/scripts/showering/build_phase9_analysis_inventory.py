#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def count_lhe_events(path: Path) -> int:
    return path.read_text(errors="replace").count("<event>")


def count_hepmc_events(path: Path) -> int:
    n = 0
    with path.open("r", errors="replace") as handle:
        for line in handle:
            if line.startswith("E "):
                n += 1
    return n


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def add_single_10k_unpol(records: list[dict[str, Any]], run_dir: Path) -> None:
    label = "unpol_epmum"

    raw_lhe = run_dir / "bridge_raw.lhe"
    canonical_lhe = run_dir / "unpol_epmum.canonical_v2.lhe"
    hepmc = run_dir / "unpol_epmum.canonical_v2.hepmc3"
    metadata = run_dir / "unpol_epmum.canonical_v2.hepmc3.metadata.json"
    canonical_summary = run_dir / "unpol_epmum.canonical_v2.summary.json"
    pythia_log = run_dir / "run_external_pythia_canonical_v2.log"

    required = [raw_lhe, canonical_lhe, hepmc, metadata, canonical_summary, pythia_log]
    missing = [str(p) for p in required if not p.is_file()]
    if missing:
        raise SystemExit("ERROR: missing unpol_epmum products:\n" + "\n".join(missing))

    counts = {
        "raw_lhe": count_lhe_events(raw_lhe),
        "canonical_lhe": count_lhe_events(canonical_lhe),
        "hepmc": count_hepmc_events(hepmc),
    }

    if counts != {"raw_lhe": 10000, "canonical_lhe": 10000, "hepmc": 10000}:
        raise SystemExit(f"ERROR: unpol_epmum event counts are not 10000/10000/10000: {counts}")

    records.append(
        {
            "schema_version": 1,
            "campaign_id": "full6f_365gev_ee_ttbar_spinpol_v1",
            "sample_group": "phase9_parton_only_analysis_inputs",
            "record_type": "single_run",
            "label": label,
            "parent_label": label,
            "category": "dilepton_unpolarized",
            "beam_polarization": "unpolarized",
            "final_state": "b bbar e+ nu_e mu- anti_nu_mu",
            "events": 10000,
            "run_dir": str(run_dir),
            "raw_lhe": str(raw_lhe),
            "canonical_lhe": str(canonical_lhe),
            "hepmc": str(hepmc),
            "metadata": str(metadata),
            "canonical_summary": str(canonical_summary),
            "pythia_log": str(pythia_log),
            "event_counts": counts,
            "pythia_profile": "parton_only",
            "bridge_policy": "canonical_v2",
            "status": "PASS_WITH_RUNTIME_WARNINGS",
            "notes": [
                "Existing 10k unpolarized dilepton parton-only canonical-v2 bridge product.",
                "Use as analysis-facing unpolarized dilepton input unless superseded by a later production note.",
            ],
        }
    )


def add_sharded_records(records: list[dict[str, Any]], summary_path: Path, prod_out_dir: Path) -> None:
    summary = load_json(summary_path)

    if summary.get("status") != "PASS":
        raise SystemExit(f"ERROR: production summary is not PASS: {summary.get('status')}")

    entries = summary.get("records") or summary.get("results") or []
    if not entries:
        # Fall back to status JSONs if collector schema has no top-level records/results.
        entries = []
        for status_path in sorted((prod_out_dir / "status").glob("job_*.status.json")):
            entries.append(load_json(status_path))

    if len(entries) != 40:
        raise SystemExit(f"ERROR: expected 40 sharded entries, found {len(entries)}")

    for entry in entries:
        rc = entry.get("return_code")
        runner = entry.get("runner_status")
        counts = entry.get("event_counts") or {}

        if rc != 0 or runner not in {"PASS", "PASS_WITH_RUNTIME_WARNINGS"}:
            raise SystemExit(f"ERROR: bad sharded entry: label={entry.get('label')} rc={rc} runner={runner}")

        if counts != {"raw_lhe": 500, "canonical_lhe": 500, "hepmc": 500}:
            raise SystemExit(f"ERROR: bad event counts for {entry.get('label')}: {counts}")

        run_dir = Path(entry["run_dir"])
        label = entry["label"]

        # For retry-promoted ProcId 39, the status label is original s019 but run_dir points to retry00.
        retry_label = entry.get("retry_label")
        file_stem = retry_label if retry_label else label

        raw_lhe = run_dir / "bridge_raw.lhe"
        canonical_lhe = run_dir / f"{file_stem}.canonical_v2.lhe"
        hepmc = run_dir / f"{file_stem}.canonical_v2.hepmc3"
        metadata = run_dir / f"{file_stem}.canonical_v2.hepmc3.metadata.json"
        canonical_summary = run_dir / f"{file_stem}.canonical_v2.summary.json"
        pythia_log = run_dir / "run_external_pythia_canonical_v2.log"

        required = [raw_lhe, canonical_lhe, hepmc, metadata, canonical_summary, pythia_log]
        missing = [str(p) for p in required if not p.is_file()]
        if missing:
            raise SystemExit("ERROR: missing sharded products for "
                             f"{label}:\n" + "\n".join(missing))

        parent = entry.get("parent_label", "")

        if parent == "LR100_epmum":
            category = "dilepton_polarized"
            beam_polarization = "LR100"
            final_state = "b bbar e+ nu_e mu- anti_nu_mu"
        elif parent == "unpol_epjets_Wminus_ubar_d":
            category = "semileptonic_unpolarized"
            beam_polarization = "unpolarized"
            final_state = "b bbar e+ nu_e anti_u d"
        else:
            category = "unknown"
            beam_polarization = "unknown"
            final_state = "unknown"

        records.append(
            {
                "schema_version": 1,
                "campaign_id": "full6f_365gev_ee_ttbar_spinpol_v1",
                "sample_group": "phase9_parton_only_analysis_inputs",
                "record_type": "condor_shard",
                "label": label,
                "file_stem": file_stem,
                "parent_label": parent,
                "category": category,
                "beam_polarization": beam_polarization,
                "final_state": final_state,
                "events": 500,
                "proc_id": entry.get("proc_id"),
                "shard_index": entry.get("shard_index"),
                "seed": entry.get("seed"),
                "run_dir": str(run_dir),
                "raw_lhe": str(raw_lhe),
                "canonical_lhe": str(canonical_lhe),
                "hepmc": str(hepmc),
                "metadata": str(metadata),
                "canonical_summary": str(canonical_summary),
                "pythia_log": str(pythia_log),
                "summary_copy": entry.get("summary_copy"),
                "event_counts": counts,
                "pythia_profile": "parton_only",
                "bridge_policy": "canonical_v2",
                "status": runner,
                "salvaged": bool(entry.get("salvaged")),
                "salvaged_from_retry": bool(entry.get("salvaged_from_retry")),
                "retry_label": retry_label,
                "retry_out_dir": entry.get("retry_out_dir"),
            }
        )


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for r in records:
            handle.write(json.dumps(r, sort_keys=True) + "\n")


def write_summary(path: Path, records: list[dict[str, Any]]) -> None:
    by_parent: dict[str, int] = {}
    for r in records:
        by_parent[r["parent_label"]] = by_parent.get(r["parent_label"], 0) + int(r["events"])

    payload = {
        "schema_version": 1,
        "status": "PASS",
        "total_records": len(records),
        "total_events": sum(int(r["events"]) for r in records),
        "events_by_parent_label": by_parent,
        "hepmc_files": len([r for r in records if r.get("hepmc")]),
        "records": [
            {
                "label": r["label"],
                "parent_label": r["parent_label"],
                "events": r["events"],
                "hepmc": r["hepmc"],
                "salvaged": r.get("salvaged", False),
                "salvaged_from_retry": r.get("salvaged_from_retry", False),
            }
            for r in records
        ],
    }

    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--unpol-epmum-run", required=True)
    ap.add_argument("--prod-summary", required=True)
    ap.add_argument("--prod-out-dir", required=True)
    ap.add_argument("--output-jsonl", required=True)
    ap.add_argument("--output-summary", required=True)
    args = ap.parse_args()

    records: list[dict[str, Any]] = []

    add_single_10k_unpol(records, Path(args.unpol_epmum_run))
    add_sharded_records(records, Path(args.prod_summary), Path(args.prod_out_dir))

    write_jsonl(Path(args.output_jsonl), records)
    write_summary(Path(args.output_summary), records)

    print(f"INVENTORY_STATUS=PASS")
    print(f"TOTAL_RECORDS={len(records)}")
    print(f"TOTAL_EVENTS={sum(int(r['events']) for r in records)}")
    print(f"WROTE_JSONL={args.output_jsonl}")
    print(f"WROTE_SUMMARY={args.output_summary}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
