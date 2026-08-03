#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PARENT_ORDER = {
    "unpol_epmum": 0,
    "LR100_epmum": 1,
    "unpol_epjets_Wminus_ubar_d": 2,
}


@dataclass(frozen=True)
class Particle:
    pid: int
    status: int
    px: float
    py: float
    pz: float
    e: float
    m: float


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except Exception as exc:
                raise SystemExit(f"ERROR: bad JSONL line {lineno} in {path}: {exc}") from exc
    return records


def try_int(x: str) -> int | None:
    try:
        return int(x)
    except Exception:
        return None


def try_float(x: str) -> float | None:
    try:
        return float(x)
    except Exception:
        return None


def parse_particle_line(line: str) -> Particle | None:
    """Parse HepMC3 Ascii3 P records.

    Observed format:

      P id production_vertex pdg_id px py pz energy mass status ...

    Example:

      P 9 -3 -11 px py pz E m 1
    """
    parts = line.split()
    if len(parts) < 10 or parts[0] != "P":
        return None

    pid = try_int(parts[3])
    px = try_float(parts[4])
    py = try_float(parts[5])
    pz = try_float(parts[6])
    e = try_float(parts[7])
    m = try_float(parts[8])
    status = try_int(parts[9])

    if None in (pid, px, py, pz, e, m, status):
        return None

    return Particle(
        pid=int(pid),
        status=int(status),
        px=float(px),
        py=float(py),
        pz=float(pz),
        e=float(e),
        m=float(m),
    )


def iter_hepmc_events(path: Path):
    event_index = -1
    particles: list[Particle] = []

    with path.open("r", errors="replace") as handle:
        for line in handle:
            if line.startswith("E "):
                if event_index >= 0:
                    yield event_index, particles
                event_index += 1
                particles = []
                continue

            if not line.startswith("P "):
                continue

            p = parse_particle_line(line)
            if p is not None:
                particles.append(p)

    if event_index >= 0:
        yield event_index, particles


def p4(p: Particle) -> dict[str, float]:
    return {
        "px": p.px,
        "py": p.py,
        "pz": p.pz,
        "e": p.e,
        "m": p.m,
        "pt": pt((p.e, p.px, p.py, p.pz)),
        "eta": eta((p.e, p.px, p.py, p.pz)),
        "phi": phi((p.e, p.px, p.py, p.pz)),
    }


def add4(*vectors: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    e = sum(v[0] for v in vectors)
    px = sum(v[1] for v in vectors)
    py = sum(v[2] for v in vectors)
    pz = sum(v[3] for v in vectors)
    return e, px, py, pz


def v4_particle(p: Particle) -> tuple[float, float, float, float]:
    return p.e, p.px, p.py, p.pz


def mass(v: tuple[float, float, float, float]) -> float:
    e, px, py, pz = v
    m2 = e * e - px * px - py * py - pz * pz
    return math.sqrt(max(m2, 0.0))


def pt(v: tuple[float, float, float, float]) -> float:
    _, px, py, _ = v
    return math.hypot(px, py)


def p_abs(v: tuple[float, float, float, float]) -> float:
    _, px, py, pz = v
    return math.sqrt(px * px + py * py + pz * pz)


def eta(v: tuple[float, float, float, float]) -> float | None:
    _, px, py, pz = v
    p = math.sqrt(px * px + py * py + pz * pz)
    if p <= 0:
        return None
    denom = p - pz
    numer = p + pz
    if denom <= 0 or numer <= 0:
        return None
    return 0.5 * math.log(numer / denom)


def phi(v: tuple[float, float, float, float]) -> float:
    _, px, py, _ = v
    return math.atan2(py, px)


def delta_phi(phi1: float, phi2: float) -> float:
    d = phi1 - phi2
    while d > math.pi:
        d -= 2.0 * math.pi
    while d <= -math.pi:
        d += 2.0 * math.pi
    return d


def delta_r(v1: tuple[float, float, float, float], v2: tuple[float, float, float, float]) -> float | None:
    e1 = eta(v1)
    e2 = eta(v2)
    if e1 is None or e2 is None:
        return None
    return math.hypot(e1 - e2, delta_phi(phi(v1), phi(v2)))


def cos_opening(v1: tuple[float, float, float, float], v2: tuple[float, float, float, float]) -> float | None:
    _, px1, py1, pz1 = v1
    _, px2, py2, pz2 = v2
    n1 = math.sqrt(px1 * px1 + py1 * py1 + pz1 * pz1)
    n2 = math.sqrt(px2 * px2 + py2 * py2 + pz2 * pz2)
    if n1 <= 0 or n2 <= 0:
        return None
    c = (px1 * px2 + py1 * py2 + pz1 * pz2) / (n1 * n2)
    return max(-1.0, min(1.0, c))


def select_particle(
    particles: list[Particle],
    pid: int,
    preferred_statuses: tuple[int, ...],
) -> Particle | None:
    for status in preferred_statuses:
        candidates = [p for p in particles if p.pid == pid and p.status == status]
        if candidates:
            return max(candidates, key=lambda p: p.e)

    candidates = [p for p in particles if p.pid == pid and p.status not in {4, 21}]
    if candidates:
        return max(candidates, key=lambda p: p.e)

    return None


def extract_event(record: dict[str, Any], event_index: int, particles: list[Particle], sample_event_index: int) -> dict[str, Any]:
    parent = record["parent_label"]
    label = record["label"]

    errors: list[str] = []
    objects: dict[str, Any] = {}

    # Object definitions use the full-6f channel conventions:
    #
    # dilepton epmum:
    #   t    -> b W+    -> b e+ nu_e
    #   tbar -> bbar W- -> bbar mu- anti_nu_mu
    #
    # semileptonic Wminus ubar d:
    #   t    -> b W+    -> b e+ nu_e
    #   tbar -> bbar W- -> bbar anti_u d
    b = select_particle(particles, 5, (23, 1))
    bbar = select_particle(particles, -5, (23, 1))
    eplus = select_particle(particles, -11, (1, 23))
    nue = select_particle(particles, 12, (1, 23))

    if b is None:
        errors.append("missing b")
    if bbar is None:
        errors.append("missing bbar")
    if eplus is None:
        errors.append("missing eplus")
    if nue is None:
        errors.append("missing nu_e")

    if b is not None:
        objects["b"] = {"pid": b.pid, "status": b.status, **p4(b)}
    if bbar is not None:
        objects["bbar"] = {"pid": bbar.pid, "status": bbar.status, **p4(bbar)}
    if eplus is not None:
        objects["lplus"] = {"pid": eplus.pid, "status": eplus.status, **p4(eplus)}
    if nue is not None:
        objects["nu_e"] = {"pid": nue.pid, "status": nue.status, **p4(nue)}

    mum = None
    numubar = None
    ubar = None
    dquark = None

    if parent in {"unpol_epmum", "LR100_epmum"}:
        mum = select_particle(particles, 13, (1, 23))
        numubar = select_particle(particles, -14, (1, 23))

        if mum is None:
            errors.append("missing mu_minus")
        if numubar is None:
            errors.append("missing anti_nu_mu")

        if mum is not None:
            objects["lminus"] = {"pid": mum.pid, "status": mum.status, **p4(mum)}
        if numubar is not None:
            objects["anti_nu_mu"] = {"pid": numubar.pid, "status": numubar.status, **p4(numubar)}

    elif parent == "unpol_epjets_Wminus_ubar_d":
        ubar = select_particle(particles, -2, (23, 1))
        dquark = select_particle(particles, 1, (23, 1))

        if ubar is None:
            errors.append("missing anti_u")
        if dquark is None:
            errors.append("missing d")
        if ubar is not None:
            objects["anti_u"] = {"pid": ubar.pid, "status": ubar.status, **p4(ubar)}
        if dquark is not None:
            objects["d"] = {"pid": dquark.pid, "status": dquark.status, **p4(dquark)}
    else:
        errors.append(f"unknown parent_label={parent}")

    observables: dict[str, Any] = {}

    if b is not None and bbar is not None and eplus is not None and nue is not None:
        wplus = add4(v4_particle(eplus), v4_particle(nue))
        top = add4(v4_particle(b), v4_particle(eplus), v4_particle(nue))

        observables["wplus_mass"] = mass(wplus)
        observables["top_candidate_mass"] = mass(top)
        observables["top_candidate_pt"] = pt(top)
        observables["top_candidate_eta"] = eta(top)
        observables["top_candidate_phi"] = phi(top)

        if parent in {"unpol_epmum", "LR100_epmum"} and mum is not None and numubar is not None:
            wminus = add4(v4_particle(mum), v4_particle(numubar))
            antitop = add4(v4_particle(bbar), v4_particle(mum), v4_particle(numubar))
            ttbar = add4(top, antitop)

            lplus_v = v4_particle(eplus)
            lminus_v = v4_particle(mum)

            observables.update(
                {
                    "wminus_mass": mass(wminus),
                    "antitop_candidate_mass": mass(antitop),
                    "antitop_candidate_pt": pt(antitop),
                    "antitop_candidate_eta": eta(antitop),
                    "antitop_candidate_phi": phi(antitop),
                    "ttbar_candidate_mass": mass(ttbar),
                    "ttbar_candidate_pt": pt(ttbar),
                    "lplus_pt": pt(lplus_v),
                    "lminus_pt": pt(lminus_v),
                    "lplus_eta": eta(lplus_v),
                    "lminus_eta": eta(lminus_v),
                    "lplus_phi": phi(lplus_v),
                    "lminus_phi": phi(lminus_v),
                    "delta_phi_ll": abs(delta_phi(phi(lplus_v), phi(lminus_v))),
                    "delta_r_ll": delta_r(lplus_v, lminus_v),
                    "cos_opening_ll_lab": cos_opening(lplus_v, lminus_v),
                }
            )

        if parent == "unpol_epjets_Wminus_ubar_d" and ubar is not None and dquark is not None:
            whad = add4(v4_particle(ubar), v4_particle(dquark))
            antitop = add4(v4_particle(bbar), v4_particle(ubar), v4_particle(dquark))
            ttbar = add4(top, antitop)
            lplus_v = v4_particle(eplus)

            observables.update(
                {
                    "whad_mass": mass(whad),
                    "antitop_candidate_mass": mass(antitop),
                    "antitop_candidate_pt": pt(antitop),
                    "antitop_candidate_eta": eta(antitop),
                    "antitop_candidate_phi": phi(antitop),
                    "ttbar_candidate_mass": mass(ttbar),
                    "ttbar_candidate_pt": pt(ttbar),
                    "lplus_pt": pt(lplus_v),
                    "lplus_eta": eta(lplus_v),
                    "lplus_phi": phi(lplus_v),
                }
            )

    pid_counts = Counter(p.pid for p in particles)
    status_counts = Counter(p.status for p in particles)

    return {
        "schema_version": 1,
        "campaign_id": record.get("campaign_id"),
        "sample_group": record.get("sample_group"),
        "source_label": label,
        "parent_label": parent,
        "category": record.get("category"),
        "beam_polarization": record.get("beam_polarization"),
        "pythia_profile": record.get("pythia_profile"),
        "bridge_policy": record.get("bridge_policy"),
        "event_index_in_file": event_index,
        "event_index_in_parent": sample_event_index,
        "source_hepmc": record["hepmc"],
        "salvaged": bool(record.get("salvaged")),
        "salvaged_from_retry": bool(record.get("salvaged_from_retry")),
        "retry_label": record.get("retry_label"),
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "objects": objects,
        "observables": observables,
        "event_particle_summary": {
            "n_particles": len(particles),
            "pid_counts": dict(sorted(pid_counts.items(), key=lambda kv: (abs(kv[0]), kv[0]))),
            "status_counts": dict(sorted(status_counts.items())),
        },
    }


def inventory_sort_key(record: dict[str, Any]) -> tuple[int, int, str]:
    parent = record.get("parent_label", "")
    shard = record.get("shard_index")
    if shard is None:
        shard = -1
    return (PARENT_ORDER.get(parent, 999), int(shard), record.get("label", ""))


def summarize(records: list[dict[str, Any]], output_jsonl: Path) -> dict[str, Any]:
    total_events = len(records)
    failed = [r for r in records if r["status"] != "PASS"]

    events_by_parent: dict[str, int] = defaultdict(int)
    failures_by_parent: dict[str, int] = defaultdict(int)
    observables_by_parent: dict[str, dict[str, Any]] = {}

    for r in records:
        parent = r["parent_label"]
        events_by_parent[parent] += 1
        if r["status"] != "PASS":
            failures_by_parent[parent] += 1

    for parent in sorted(events_by_parent):
        subset = [r for r in records if r["parent_label"] == parent and r["status"] == "PASS"]
        obs_keys = sorted({k for r in subset for k in r["observables"]})
        stats = {}
        for key in obs_keys:
            vals = [
                r["observables"][key]
                for r in subset
                if isinstance(r["observables"].get(key), (int, float))
            ]
            if vals:
                vals_sorted = sorted(float(v) for v in vals)
                n = len(vals_sorted)
                stats[key] = {
                    "n": n,
                    "mean": sum(vals_sorted) / n,
                    "min": vals_sorted[0],
                    "max": vals_sorted[-1],
                    "p50": vals_sorted[n // 2],
                }
        observables_by_parent[parent] = stats

    return {
        "schema_version": 1,
        "status": "PASS" if not failed else "FAIL",
        "truth_jsonl": str(output_jsonl),
        "total_events": total_events,
        "failed_events": len(failed),
        "events_by_parent_label": dict(sorted(events_by_parent.items())),
        "failures_by_parent_label": dict(sorted(failures_by_parent.items())),
        "failed_examples": failed[:10],
        "observables_by_parent_label": observables_by_parent,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", required=True)
    ap.add_argument("--output-jsonl", required=True)
    ap.add_argument("--summary-json", required=True)
    args = ap.parse_args()

    inventory = sorted(load_jsonl(Path(args.inventory)), key=inventory_sort_key)
    output_jsonl = Path(args.output_jsonl)
    output_jsonl.parent.mkdir(parents=True, exist_ok=True)

    all_records: list[dict[str, Any]] = []
    parent_event_counter: dict[str, int] = defaultdict(int)

    with output_jsonl.open("w", encoding="utf-8") as out:
        for source_i, record in enumerate(inventory, 1):
            parent = record["parent_label"]
            hepmc = Path(record["hepmc"])
            expected = int(record["events"])

            print(
                f"EXTRACT_SOURCE={source_i}/{len(inventory)} "
                f"PARENT={parent} LABEL={record['label']} EVENTS={expected}",
                flush=True,
            )

            n_seen = 0
            for event_index, particles in iter_hepmc_events(hepmc):
                sample_event_index = parent_event_counter[parent]
                event_record = extract_event(record, event_index, particles, sample_event_index)
                out.write(json.dumps(event_record, sort_keys=True) + "\n")
                all_records.append(event_record)
                parent_event_counter[parent] += 1
                n_seen += 1

            if n_seen != expected:
                raise SystemExit(
                    f"ERROR: event count mismatch while extracting {record['label']}: "
                    f"expected {expected}, saw {n_seen}"
                )

    summary = summarize(all_records, output_jsonl)
    Path(args.summary_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.summary_json).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"TRUTH_EXTRACT_STATUS={summary['status']}")
    print(f"TOTAL_EVENTS={summary['total_events']}")
    print(f"FAILED_EVENTS={summary['failed_events']}")
    print(f"WROTE_JSONL={output_jsonl}")
    print(f"WROTE_SUMMARY={args.summary_json}")

    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
