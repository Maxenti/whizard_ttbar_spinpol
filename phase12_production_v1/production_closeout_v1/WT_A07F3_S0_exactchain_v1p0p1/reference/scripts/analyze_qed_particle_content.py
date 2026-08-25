#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
from collections import Counter, deque
from pathlib import Path

import numpy as np


VARIANTS = (
    "G0_H0",
    "G1_H0",
    "G0_H1",
    "G1_H1",
)

FERMION_ABS_PIDS = {
    1, 2, 3, 4, 5, 6,
    11, 12, 13, 14, 15, 16,
}

EVENT_METRICS = (
    "conversion_vertices",
    "conversion_e",
    "conversion_mu",
    "conversion_tau",
    "conversion_quark",
    "stable_particles",
    "stable_photons",
    "stable_photons_gt_1MeV",
    "stable_photons_gt_100MeV",
    "stable_photons_gt_1GeV",
    "stable_photon_energy_GeV",
    "stable_electrons",
    "stable_positrons",
    "stable_mu_minus",
    "stable_mu_plus",
    "stable_photons_with_tau_ancestor",
    "stable_photons_with_emu_ancestor",
    "stable_photons_with_hadron_ancestor",
    "stable_photons_with_W_ancestor",
    "stable_photons_with_top_ancestor",
)

EVENT_FIELDS = (
    "variant",
    "event_index",
    "event_weight",
    *EVENT_METRICS,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze the Phase-12 2x2 PYTHIA QED systematic "
            "using identical hard events."
        )
    )

    parser.add_argument(
        "--root",
        type=Path,
        required=True,
        help="EOS root containing G0_H0/G1_H0/G0_H1/G1_H1.",
    )

    parser.add_argument(
        "--sample-id",
        required=True,
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--expected-events",
        type=int,
        default=25000,
    )

    parser.add_argument(
        "--progress-every",
        type=int,
        default=2500,
    )

    return parser.parse_args()


def particle_identity(particle) -> int:
    identifier = int(getattr(particle, "id", 0))
    return identifier if identifier != 0 else id(particle)


def parents(particle) -> list:
    vertex = particle.production_vertex

    if vertex is None:
        return []

    return list(vertex.particles_in)


def ancestor_abs_pids(
    particle,
    *,
    max_depth: int = 40,
) -> set[int]:

    queue = deque(
        (parent, 1)
        for parent in parents(particle)
    )

    visited: set[int] = set()
    pids: set[int] = set()

    while queue:

        current, depth = queue.popleft()

        identity = particle_identity(current)

        if identity in visited:
            continue

        visited.add(identity)

        if depth > max_depth:
            continue

        pids.add(abs(int(current.pid)))

        for parent in parents(current):
            queue.append(
                (parent, depth + 1)
            )

    return pids


def is_stable(particle) -> bool:
    return (
        int(particle.status) == 1
        and particle.end_vertex is None
    )


def conversion_species(particle) -> int | None:
    """Return abs(PDG) for gamma -> f fbar, else None."""

    if int(particle.pid) != 22:
        return None

    if particle.end_vertex is None:
        return None

    daughters = list(
        particle.end_vertex.particles_out
    )

    if len(daughters) != 2:
        return None

    first = int(daughters[0].pid)
    second = int(daughters[1].pid)

    if first != -second:
        return None

    abs_pid = abs(first)

    if abs_pid not in FERMION_ABS_PIDS:
        return None

    return abs_pid


def classify_event(event) -> dict[str, float | int]:

    values: dict[str, float | int] = {
        metric: 0
        for metric in EVENT_METRICS
    }

    conversion_counts = Counter()

    for particle in event.particles:

        species = conversion_species(particle)

        if species is not None:
            values["conversion_vertices"] += 1
            conversion_counts[species] += 1

        if not is_stable(particle):
            continue

        values["stable_particles"] += 1

        pid = int(particle.pid)

        if pid == 11:
            values["stable_electrons"] += 1

        elif pid == -11:
            values["stable_positrons"] += 1

        elif pid == 13:
            values["stable_mu_minus"] += 1

        elif pid == -13:
            values["stable_mu_plus"] += 1

        if pid != 22:
            continue

        energy = float(
            particle.momentum.e
        )

        values["stable_photons"] += 1
        values["stable_photon_energy_GeV"] += energy

        if energy > 1.0e-3:
            values["stable_photons_gt_1MeV"] += 1

        if energy > 1.0e-1:
            values["stable_photons_gt_100MeV"] += 1

        if energy > 1.0:
            values["stable_photons_gt_1GeV"] += 1

        ancestors = ancestor_abs_pids(
            particle
        )

        if 15 in ancestors:
            values[
                "stable_photons_with_tau_ancestor"
            ] += 1

        if ancestors & {11, 13}:
            values[
                "stable_photons_with_emu_ancestor"
            ] += 1

        if any(
            pdg >= 100
            for pdg in ancestors
        ):
            values[
                "stable_photons_with_hadron_ancestor"
            ] += 1

        if 24 in ancestors:
            values[
                "stable_photons_with_W_ancestor"
            ] += 1

        if 6 in ancestors:
            values[
                "stable_photons_with_top_ancestor"
            ] += 1

    values["conversion_e"] = (
        conversion_counts[11]
    )

    values["conversion_mu"] = (
        conversion_counts[13]
    )

    values["conversion_tau"] = (
        conversion_counts[15]
    )

    values["conversion_quark"] = sum(
        conversion_counts[pid]
        for pid in range(1, 7)
    )

    return values


def find_hepmc(
    root: Path,
    variant: str,
    sample_id: str,
) -> Path:

    directory = (
        root
        / variant
        / "hepmc3"
        / sample_id
    )

    matches = sorted(
        directory.glob("*.hepmc3")
    )

    if len(matches) != 1:
        raise RuntimeError(
            f"{variant}: expected exactly one HepMC3 "
            f"file under {directory}; found {len(matches)}"
        )

    return matches[0]


def scan_variant(
    *,
    variant: str,
    path: Path,
    expected_events: int,
    progress_every: int,
    event_output: Path,
) -> tuple[list[int], np.ndarray, dict[str, np.ndarray]]:

    try:
        import pyhepmc
    except ImportError as exc:
        raise RuntimeError(
            "pyhepmc is required; source setup_lxplus.sh first"
        ) from exc

    print()
    print("=" * 72)
    print(f"SCANNING {variant}")
    print("=" * 72)
    print(path)

    event_ids: list[int] = []
    weights: list[float] = []

    metric_lists: dict[str, list[float]] = {
        metric: []
        for metric in EVENT_METRICS
    }

    event_output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with gzip.open(
        event_output,
        "wt",
        newline="",
    ) as output_stream:

        writer = csv.DictWriter(
            output_stream,
            fieldnames=EVENT_FIELDS,
        )

        writer.writeheader()

        with pyhepmc.open(path) as stream:

            for index, event in enumerate(
                stream,
                start=1,
            ):

                event_number = int(
                    getattr(
                        event,
                        "event_number",
                        index - 1,
                    )
                )

                weight = (
                    float(event.weights[0])
                    if event.weights
                    else 1.0
                )

                values = classify_event(
                    event
                )

                row = {
                    "variant": variant,
                    "event_index": event_number,
                    "event_weight": weight,
                    **values,
                }

                writer.writerow(row)

                event_ids.append(
                    event_number
                )

                weights.append(
                    weight
                )

                for metric in EVENT_METRICS:
                    metric_lists[metric].append(
                        float(values[metric])
                    )

                if (
                    index == 1
                    or index % progress_every == 0
                    or index == expected_events
                ):
                    print(
                        f"{variant}: "
                        f"{index}/{expected_events} "
                        f"({100.0 * index / expected_events:.1f}%)",
                        flush=True,
                    )

    if len(event_ids) != expected_events:
        raise RuntimeError(
            f"{variant}: expected {expected_events} "
            f"events, found {len(event_ids)}"
        )

    arrays = {
        metric: np.asarray(
            metric_lists[metric],
            dtype=float,
        )
        for metric in EVENT_METRICS
    }

    return (
        event_ids,
        np.asarray(weights, dtype=float),
        arrays,
    )


def paired_stats(
    values: np.ndarray,
) -> dict[str, float]:

    n = len(values)

    mean = float(
        np.mean(values)
    )

    if n > 1:
        standard_error = float(
            np.std(
                values,
                ddof=1,
            )
            / math.sqrt(n)
        )
    else:
        standard_error = float("nan")

    return {
        "events": n,
        "mean": mean,
        "standard_error": standard_error,
        "min": float(np.min(values)),
        "max": float(np.max(values)),
        "fraction_nonzero": float(
            np.count_nonzero(values) / n
        ),
        "mean_abs": float(
            np.mean(np.abs(values))
        ),
        "max_abs": float(
            np.max(np.abs(values))
        ),
    }


def main() -> int:

    args = parse_args()

    args.output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    event_ids: dict[str, list[int]] = {}
    weights: dict[str, np.ndarray] = {}
    arrays: dict[
        str,
        dict[str, np.ndarray],
    ] = {}

    paths: dict[str, Path] = {}

    for variant in VARIANTS:

        path = find_hepmc(
            args.root,
            variant,
            args.sample_id,
        )

        paths[variant] = path

        (
            event_ids[variant],
            weights[variant],
            arrays[variant],
        ) = scan_variant(
            variant=variant,
            path=path,
            expected_events=args.expected_events,
            progress_every=args.progress_every,
            event_output=(
                args.output_dir
                / f"{variant}_event_content.csv.gz"
            ),
        )

    reference = "G0_H0"

    print()
    print("=" * 72)
    print("PAIRING CHECKS")
    print("=" * 72)

    for variant in VARIANTS:

        if event_ids[variant] != event_ids[reference]:
            raise RuntimeError(
                f"{variant}: event identities differ "
                f"from {reference}"
            )

        if not np.allclose(
            weights[variant],
            weights[reference],
            rtol=1.0e-12,
            atol=0.0,
        ):
            raise RuntimeError(
                f"{variant}: event weights differ "
                f"from {reference}"
            )

        print(
            f"{variant}: "
            "EVENT_KEYS=PASS "
            "WEIGHTS=PASS"
        )

    summary_rows: list[dict[str, object]] = []

    for variant in VARIANTS:

        for metric in EVENT_METRICS:

            values = arrays[variant][metric]

            summary_rows.append(
                {
                    "variant": variant,
                    "metric": metric,
                    "total": float(
                        np.sum(values)
                    ),
                    "mean_per_event": float(
                        np.mean(values)
                    ),
                    "std_per_event": float(
                        np.std(
                            values,
                            ddof=1,
                        )
                    ),
                    "min": float(
                        np.min(values)
                    ),
                    "max": float(
                        np.max(values)
                    ),
                    "events_nonzero": int(
                        np.count_nonzero(values)
                    ),
                    "fraction_events_nonzero": float(
                        np.count_nonzero(values)
                        / len(values)
                    ),
                }
            )

    summary_path = (
        args.output_dir
        / "qed_particle_content_summary.csv"
    )

    with summary_path.open(
        "w",
        newline="",
    ) as stream:

        writer = csv.DictWriter(
            stream,
            fieldnames=list(
                summary_rows[0]
            ),
        )

        writer.writeheader()
        writer.writerows(
            summary_rows
        )

    paired_rows: list[dict[str, object]] = []

    for variant in (
        "G1_H0",
        "G0_H1",
        "G1_H1",
    ):

        for metric in EVENT_METRICS:

            delta = (
                arrays[variant][metric]
                - arrays[reference][metric]
            )

            stats = paired_stats(
                delta
            )

            paired_rows.append(
                {
                    "comparison": (
                        f"{variant}-G0_H0"
                    ),
                    "metric": metric,
                    **stats,
                }
            )

    contrast_rows: list[dict[str, object]] = []

    for metric in EVENT_METRICS:

        g0h0 = arrays["G0_H0"][metric]
        g1h0 = arrays["G1_H0"][metric]
        g0h1 = arrays["G0_H1"][metric]
        g1h1 = arrays["G1_H1"][metric]

        contrasts = {
            "gamma_main_effect": (
                0.5
                * (
                    (g1h0 - g0h0)
                    + (g1h1 - g0h1)
                )
            ),
            "hadron_qed_main_effect": (
                0.5
                * (
                    (g0h1 - g0h0)
                    + (g1h1 - g1h0)
                )
            ),
            "gamma_x_hadron_interaction": (
                g1h1
                - g1h0
                - g0h1
                + g0h0
            ),
        }

        for name, values in contrasts.items():

            stats = paired_stats(
                values
            )

            contrast_rows.append(
                {
                    "contrast": name,
                    "metric": metric,
                    **stats,
                }
            )

    paired_path = (
        args.output_dir
        / "qed_particle_content_paired_differences.csv"
    )

    with paired_path.open(
        "w",
        newline="",
    ) as stream:

        writer = csv.DictWriter(
            stream,
            fieldnames=list(
                paired_rows[0]
            ),
        )

        writer.writeheader()
        writer.writerows(
            paired_rows
        )

    contrast_path = (
        args.output_dir
        / "qed_particle_content_factorial_contrasts.csv"
    )

    with contrast_path.open(
        "w",
        newline="",
    ) as stream:

        writer = csv.DictWriter(
            stream,
            fieldnames=list(
                contrast_rows[0]
            ),
        )

        writer.writeheader()
        writer.writerows(
            contrast_rows
        )

    report = {
        "status": "PASS",
        "expected_events_per_variant": (
            args.expected_events
        ),
        "variants": list(
            VARIANTS
        ),
        "reference": reference,
        "paths": {
            key: str(value)
            for key, value in paths.items()
        },
        "pairing": {
            "event_keys": "PASS",
            "weights": "PASS",
        },
        "outputs": {
            "summary_csv": str(
                summary_path
            ),
            "paired_csv": str(
                paired_path
            ),
            "factorial_contrasts_csv": str(
                contrast_path
            ),
        },
    }

    report_path = (
        args.output_dir
        / "qed_particle_content_report.json"
    )

    report_path.write_text(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    print()
    print("=" * 72)
    print("KEY RESULTS")
    print("=" * 72)

    key_metrics = (
        "conversion_vertices",
        "conversion_e",
        "conversion_mu",
        "conversion_tau",
        "conversion_quark",
        "stable_photons",
        "stable_photons_gt_100MeV",
        "stable_photons_gt_1GeV",
        "stable_photon_energy_GeV",
        "stable_electrons",
        "stable_positrons",
        "stable_mu_minus",
        "stable_mu_plus",
        "stable_photons_with_tau_ancestor",
        "stable_photons_with_hadron_ancestor",
    )

    for metric in key_metrics:

        print()
        print(metric)

        for variant in VARIANTS:

            values = arrays[variant][metric]

            print(
                f"  {variant}: "
                f"total={np.sum(values):.8g} "
                f"mean/event={np.mean(values):.8g} "
                f"nonzero_events={np.count_nonzero(values)}"
            )

    print()
    print("=" * 72)
    print("OUTPUTS")
    print("=" * 72)
    print(summary_path)
    print(paired_path)
    print(contrast_path)
    print(report_path)
    print()
    print("QED_PARTICLE_CONTENT_ANALYSIS=PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
