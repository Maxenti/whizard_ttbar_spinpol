#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


SQRTS_GEV = 365.0


REQUIRED_PIDS_BY_PARENT = {
    "unpol_epmum": {5, -5, -11, 12, 13, -14},
    "LR100_epmum": {5, -5, -11, 12, 13, -14},
    "unpol_epjets_Wminus_ubar_d": {5, -5, -11, 12, -2, 1},
}


# charge in units of 1/3 e, so integer arithmetic is exact.
CHARGE3 = {
    1: -1,   -1: +1,   # d
    2: +2,   -2: -2,   # u
    3: -1,   -3: +1,   # s
    4: +2,   -4: -2,   # c
    5: -1,   -5: +1,   # b
    6: +2,   -6: -2,   # t
    11: -3, -11: +3,   # e
    13: -3, -13: +3,   # mu
    15: -3, -15: +3,   # tau
    12: 0,  -12: 0,
    14: 0,  -14: 0,
    16: 0,  -16: 0,
    21: 0,
    22: 0,
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open("r", encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except Exception as exc:
                raise SystemExit(f"ERROR: could not parse JSONL line {lineno} in {path}: {exc}") from exc
    return records


def try_int(value: str) -> int | None:
    try:
        return int(value)
    except Exception:
        return None


def try_float(value: str) -> float | None:
    try:
        return float(value)
    except Exception:
        return None


def parse_particle_line(line: str) -> tuple[int | None, int | None, float | None]:
    """Return pid, status, energy from a HepMC3 ASCII particle line.

    HepMC3 Ascii3 particle records normally have the form

      P id production_vertex pdg_id px py pz energy mass status ...

    The previous QA parser accidentally read the production-vertex field as the
    PDG ID.  That made every event appear to be missing its required hard-process
    particles and also corrupted the charge/energy checks.
    """
    parts = line.split()
    if len(parts) < 10 or parts[0] != "P":
        return None, None, None

    # HepMC3 Ascii3 convention:
    #   0 P
    #   1 particle barcode/id
    #   2 production vertex id
    #   3 PDG id
    #   4 px
    #   5 py
    #   6 pz
    #   7 energy
    #   8 generated mass
    #   9 status
    pid = try_int(parts[3])
    energy = try_float(parts[7])
    status = try_int(parts[9])

    return pid, status, energy

def empty_event_accumulator() -> dict[str, Any]:
    return {
        "pids_any": set(),
        "final_pids": Counter(),
        "n_particles": 0,
        "n_final_status1": 0,
        "final_charge3": 0,
        "final_energy_sum": 0.0,
    }


def scan_hepmc(path: Path, required_pids: set[int]) -> dict[str, Any]:
    event_count = 0
    total_particle_lines = 0
    pid_counts_any = Counter()
    pid_counts_final = Counter()

    missing_required_events = 0
    no_final_status1_events = 0
    charge_imbalance_events = 0
    final_energy_bad_events = 0

    max_abs_charge3 = 0
    max_abs_final_energy_delta = 0.0

    current = None

    def close_event(acc: dict[str, Any] | None) -> None:
        nonlocal missing_required_events
        nonlocal no_final_status1_events
        nonlocal charge_imbalance_events
        nonlocal final_energy_bad_events
        nonlocal max_abs_charge3
        nonlocal max_abs_final_energy_delta

        if acc is None:
            return

        if not required_pids.issubset(acc["pids_any"]):
            missing_required_events += 1

        if acc["n_final_status1"] == 0:
            no_final_status1_events += 1
            return

        abs_charge3 = abs(acc["final_charge3"])
        max_abs_charge3 = max(max_abs_charge3, abs_charge3)
        if abs_charge3 != 0:
            charge_imbalance_events += 1

        delta_e = abs(acc["final_energy_sum"] - SQRTS_GEV)
        max_abs_final_energy_delta = max(max_abs_final_energy_delta, delta_e)
        if delta_e > 1.0e-3:
            final_energy_bad_events += 1

    with path.open("r", errors="replace") as handle:
        for line in handle:
            if line.startswith("E "):
                close_event(current)
                current = empty_event_accumulator()
                event_count += 1
                continue

            if not line.startswith("P "):
                continue

            total_particle_lines += 1
            if current is None:
                current = empty_event_accumulator()

            pid, status, energy = parse_particle_line(line)
            if pid is None:
                continue

            current["n_particles"] += 1
            current["pids_any"].add(pid)
            pid_counts_any[pid] += 1

            if status == 1:
                current["n_final_status1"] += 1
                current["final_pids"][pid] += 1
                pid_counts_final[pid] += 1
                current["final_charge3"] += CHARGE3.get(pid, 0)
                if energy is not None and math.isfinite(energy):
                    current["final_energy_sum"] += energy

    close_event(current)

    return {
        "hepmc_events": event_count,
        "total_particle_lines": total_particle_lines,
        "pid_counts_any": dict(sorted(pid_counts_any.items(), key=lambda kv: (abs(kv[0]), kv[0]))),
        "pid_counts_final_status1": dict(sorted(pid_counts_final.items(), key=lambda kv: (abs(kv[0]), kv[0]))),
        "required_pids": sorted(required_pids),
        "missing_required_events": missing_required_events,
        "no_final_status1_events": no_final_status1_events,
        "charge_imbalance_events": charge_imbalance_events,
        "final_energy_bad_events": final_energy_bad_events,
        "max_abs_charge3": max_abs_charge3,
        "max_abs_final_energy_delta_GeV": max_abs_final_energy_delta,
    }


def qa_record(record: dict[str, Any]) -> dict[str, Any]:
    label = record["label"]
    parent = record["parent_label"]
    hepmc = Path(record["hepmc"])
    expected_events = int(record["events"])

    errors = []
    warnings = []

    if not hepmc.is_file():
        return {
            "label": label,
            "parent_label": parent,
            "status": "FAIL",
            "errors": [f"missing HepMC3 file: {hepmc}"],
            "warnings": [],
            "hepmc": str(hepmc),
            "expected_events": expected_events,
        }

    required = REQUIRED_PIDS_BY_PARENT.get(parent, set())
    scan = scan_hepmc(hepmc, required)

    if scan["hepmc_events"] != expected_events:
        errors.append(f"event count mismatch: expected {expected_events}, found {scan['hepmc_events']}")

    if required and scan["missing_required_events"] != 0:
        errors.append(
            f"required hard-process PID content missing in {scan['missing_required_events']} events"
        )

    if scan["no_final_status1_events"] != 0:
        warnings.append(f"{scan['no_final_status1_events']} events have no status==1 final particles")

    if scan["charge_imbalance_events"] != 0:
        warnings.append(
            f"{scan['charge_imbalance_events']} events have nonzero status==1 charge sum"
        )

    if scan["final_energy_bad_events"] != 0:
        warnings.append(
            f"{scan['final_energy_bad_events']} events have status==1 energy sum differing from 365 GeV by >1e-3 GeV"
        )

    return {
        "schema_version": 1,
        "label": label,
        "parent_label": parent,
        "category": record.get("category"),
        "beam_polarization": record.get("beam_polarization"),
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
        "hepmc": str(hepmc),
        "expected_events": expected_events,
        "salvaged": bool(record.get("salvaged")),
        "salvaged_from_retry": bool(record.get("salvaged_from_retry")),
        "retry_label": record.get("retry_label"),
        "scan": scan,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", required=True)
    ap.add_argument("--output-jsonl", required=True)
    ap.add_argument("--output-summary", required=True)
    args = ap.parse_args()

    inventory = load_jsonl(Path(args.inventory))

    qa_records = []
    for i, record in enumerate(inventory):
        print(f"QA_RECORD={i+1}/{len(inventory)} LABEL={record.get('label')}", flush=True)
        qa_records.append(qa_record(record))

    out_jsonl = Path(args.output_jsonl)
    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with out_jsonl.open("w", encoding="utf-8") as handle:
        for record in qa_records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    total_records = len(qa_records)
    fail_records = [r for r in qa_records if r["status"] != "PASS"]
    warning_records = [r for r in qa_records if r["warnings"]]

    events_by_parent = defaultdict(int)
    records_by_parent = defaultdict(int)
    failures_by_parent = defaultdict(int)
    warnings_by_parent = defaultdict(int)

    for r in qa_records:
        parent = r["parent_label"]
        records_by_parent[parent] += 1
        events_by_parent[parent] += int(r["scan"]["hepmc_events"])
        if r["status"] != "PASS":
            failures_by_parent[parent] += 1
        if r["warnings"]:
            warnings_by_parent[parent] += 1

    summary = {
        "schema_version": 1,
        "status": "PASS" if not fail_records else "FAIL",
        "total_records": total_records,
        "failed_records": len(fail_records),
        "warning_records": len(warning_records),
        "records_by_parent_label": dict(sorted(records_by_parent.items())),
        "events_by_parent_label": dict(sorted(events_by_parent.items())),
        "failures_by_parent_label": dict(sorted(failures_by_parent.items())),
        "warnings_by_parent_label": dict(sorted(warnings_by_parent.items())),
        "failed_labels": [r["label"] for r in fail_records],
        "warning_labels": [r["label"] for r in warning_records],
        "qa_jsonl": str(out_jsonl),
    }

    Path(args.output_summary).write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"HEPMC_QA_STATUS={summary['status']}")
    print(f"TOTAL_RECORDS={total_records}")
    print(f"FAILED_RECORDS={len(fail_records)}")
    print(f"WARNING_RECORDS={len(warning_records)}")
    print(f"WROTE_JSONL={out_jsonl}")
    print(f"WROTE_SUMMARY={args.output_summary}")

    return 0 if not fail_records else 1


if __name__ == "__main__":
    raise SystemExit(main())
