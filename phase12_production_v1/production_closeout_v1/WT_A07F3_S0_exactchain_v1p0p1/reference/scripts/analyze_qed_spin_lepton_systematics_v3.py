#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import dataclasses
import gzip
import json
import math
from collections import deque
from pathlib import Path

import numpy as np

from qis_ttbar.io.lhe import iter_lhe_events
from qis_ttbar.models import FourVector, TTbarTruth
from qis_ttbar.physics.observables import (
    SPIN15_COEFFICIENT_NAMES,
    SPIN15_EVENT_COLUMNS,
    event_observables,
)


VARIANTS = (
    "G0_H0",
    "G1_H0",
    "G0_H1",
    "G1_H1",
)

REPRESENTATIONS = (
    "hard",
    "bare",
    "dressed_all",
    "dressed_prompt",
)

SCALAR_OBSERVABLES = (
    "lepton_plus_pt_GeV",
    "lepton_minus_pt_GeV",
    "delta_phi_ll_lab",
    "delta_phi_ll_tt",
    "cos_opening_ll_tt",
    "opening_ll_tt",
    "cp_triple_product",
)

SPIN_MULTIPLIERS = np.asarray(
    [3.0] * 6 + [9.0] * 9,
    dtype=float,
)


# =====================================================================
# CLI
# =====================================================================

def parse_args() -> argparse.Namespace:

    parser = argparse.ArgumentParser(
        description=(
            "Phase-12 PYTHIA QED 2x2 spin/lepton systematic. "
            "Hard spin basis is reconstructed from the common "
            "six-fermion LHE. Prompt post-shower leptons are selected "
            "by stable-particle ancestry, not LHE four-vector matching."
        )
    )

    parser.add_argument(
        "--root",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--sample-id",
        required=True,
    )

    parser.add_argument(
        "--hard-lhe",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--expected-events",
        default=25000,
        type=int,
    )

    parser.add_argument(
        "--max-events",
        default=None,
        type=int,
    )

    parser.add_argument(
        "--progress-every",
        default=2500,
        type=int,
    )

    parser.add_argument(
        "--dress-dr",
        default=0.10,
        type=float,
    )

    return parser.parse_args()


# =====================================================================
# Weighted mean/covariance of mean
# =====================================================================

def weighted_mean_cov_mean(
    values: np.ndarray,
    weights: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, float]:

    values = np.asarray(
        values,
        dtype=float,
    )

    weights = np.asarray(
        weights,
        dtype=float,
    )

    if values.ndim != 2:
        raise ValueError(
            f"values must be (N,D), got {values.shape}"
        )

    if weights.shape != (len(values),):
        raise ValueError(
            f"weights shape mismatch: {weights.shape}"
        )

    if len(values) < 2:
        raise ValueError(
            "at least two events required"
        )

    if not np.all(np.isfinite(values)):
        raise ValueError(
            "non-finite observable values"
        )

    if not np.all(np.isfinite(weights)):
        raise ValueError(
            "non-finite weights"
        )

    if np.any(weights < 0):
        raise ValueError(
            "negative weights not supported by this paired helper"
        )

    sw = float(
        np.sum(weights)
    )

    if sw <= 0:
        raise ValueError(
            "non-positive total weight"
        )

    a = weights / sw

    mean = np.einsum(
        "n,nd->d",
        a,
        values,
    )

    centered = (
        values - mean
    )

    sum_a2 = float(
        np.dot(a, a)
    )

    denominator = (
        1.0 - sum_a2
    )

    if denominator <= 0:
        raise ValueError(
            "effective sample size <= 1"
        )

    covariance = np.einsum(
        "n,ni,nj->ij",
        a * a,
        centered,
        centered,
    ) / denominator

    covariance = (
        0.5
        * (
            covariance
            + covariance.T
        )
    )

    neff = (
        1.0 / sum_a2
    )

    return (
        mean,
        covariance,
        neff,
    )


def scalar_mean_error(
    values: np.ndarray,
    weights: np.ndarray,
) -> tuple[float, float, float]:

    mean, cov, neff = weighted_mean_cov_mean(
        np.asarray(
            values,
            dtype=float,
        ).reshape(-1, 1),
        weights,
    )

    return (
        float(mean[0]),
        float(
            math.sqrt(
                max(
                    cov[0, 0],
                    0.0,
                )
            )
        ),
        float(neff),
    )


# =====================================================================
# LHE six-fermion hard truth
# =====================================================================

def unique_lhe(
    event,
    *,
    pid: int,
    status: int,
    label: str,
):

    matches = [
        p
        for p in event.particles
        if (
            p.pdg == pid
            and p.status == status
        )
    ]

    if len(matches) != 1:
        raise RuntimeError(
            f"LHE event {event.index}: "
            f"{label}: expected one "
            f"PDG={pid} status={status}; "
            f"found {len(matches)}"
        )

    return matches[0]


def build_hard_truth(
    event,
) -> TTbarTruth:

    beam_minus = unique_lhe(
        event,
        pid=11,
        status=-1,
        label="post-ISR e-",
    )

    beam_plus = unique_lhe(
        event,
        pid=-11,
        status=-1,
        label="post-ISR e+",
    )

    b = unique_lhe(
        event,
        pid=5,
        status=1,
        label="b",
    )

    bbar = unique_lhe(
        event,
        pid=-5,
        status=1,
        label="bbar",
    )

    positive_leptons = [
        p
        for p in event.particles
        if (
            p.status == 1
            and p.pdg in {
                -11,
                -13,
                -15,
            }
        )
    ]

    positive_neutrinos = [
        p
        for p in event.particles
        if (
            p.status == 1
            and p.pdg in {
                12,
                14,
                16,
            }
        )
    ]

    negative_leptons = [
        p
        for p in event.particles
        if (
            p.status == 1
            and p.pdg in {
                11,
                13,
                15,
            }
        )
    ]

    negative_neutrinos = [
        p
        for p in event.particles
        if (
            p.status == 1
            and p.pdg in {
                -12,
                -14,
                -16,
            }
        )
    ]

    plus_pairs = [
        (lep, nu)
        for lep in positive_leptons
        for nu in positive_neutrinos
        if (
            abs(nu.pdg)
            == abs(lep.pdg) + 1
        )
    ]

    minus_pairs = [
        (lep, nu)
        for lep in negative_leptons
        for nu in negative_neutrinos
        if (
            abs(nu.pdg)
            == abs(lep.pdg) + 1
        )
    ]

    if (
        len(plus_pairs) != 1
        or len(minus_pairs) != 1
    ):
        raise RuntimeError(
            f"LHE event {event.index}: "
            "ambiguous charged-current assignment "
            f"plus={[(a.pdg,b.pdg) for a,b in plus_pairs]} "
            f"minus={[(a.pdg,b.pdg) for a,b in minus_pairs]}"
        )

    lepton_plus, neutrino = (
        plus_pairs[0]
    )

    lepton_minus, antineutrino = (
        minus_pairs[0]
    )

    # Analysis top basis valid whether or not optional resonance
    # particles are present in the serialized history.
    top = (
        b.p4
        + lepton_plus.p4
        + neutrino.p4
    )

    antitop = (
        bbar.p4
        + lepton_minus.p4
        + antineutrino.p4
    )

    if (
        lepton_plus.pdg == -11
        and lepton_minus.pdg == 13
    ):
        decay_channel = "epmum"

    elif (
        lepton_plus.pdg == -13
        and lepton_minus.pdg == 11
    ):
        decay_channel = "mupem"

    else:
        decay_channel = "other"

    return TTbarTruth(
        event_index=event.index,
        event_weight=event.weight,
        beam_minus=beam_minus.p4,
        beam_plus=beam_plus.p4,
        top=top,
        antitop=antitop,
        b=b.p4,
        bbar=bbar.p4,
        lepton_plus=lepton_plus.p4,
        lepton_minus=lepton_minus.p4,
        neutrino=neutrino.p4,
        antineutrino=antineutrino.p4,
        initial_state="ee",
        decay_channel=decay_channel,
    )


def load_hard_truth(
    path: Path,
    count: int,
) -> list[TTbarTruth]:

    print()
    print("=" * 78)
    print("LOADING COMMON SIX-FERMION HARD TRUTH")
    print("=" * 78)
    print(path)

    output = []

    for event in iter_lhe_events(
        path,
        max_events=count,
    ):

        truth = build_hard_truth(
            event
        )

        if truth.decay_channel == "other":
            raise RuntimeError(
                f"LHE event {event.index}: "
                "unexpected decay channel"
            )

        output.append(
            truth
        )

        n = len(output)

        if (
            n == 1
            or n % 2500 == 0
            or n == count
        ):
            print(
                f"LHE: {n}/{count} "
                f"({100*n/count:.1f}%)",
                flush=True,
            )

    if len(output) != count:
        raise RuntimeError(
            f"requested {count} LHE events, "
            f"found {len(output)}"
        )

    print(
        "LHE_DECAY_CHANNELS="
        f"{sorted({x.decay_channel for x in output})}"
    )

    return output


# =====================================================================
# HepMC graph utilities
# =====================================================================

def particle_identity(
    particle,
) -> int:

    identifier = int(
        getattr(
            particle,
            "id",
            0,
        )
    )

    return (
        identifier
        if identifier
        else id(particle)
    )


def parents(
    particle,
) -> list:

    if particle.production_vertex is None:
        return []

    return list(
        particle.production_vertex.particles_in
    )


def ancestor_abs_pids(
    particle,
    *,
    max_depth: int = 80,
) -> set[int]:

    queue = deque(
        (
            parent,
            1,
        )
        for parent in parents(
            particle
        )
    )

    visited = set()
    output = set()

    while queue:

        current, depth = (
            queue.popleft()
        )

        identity = particle_identity(
            current
        )

        if identity in visited:
            continue

        visited.add(
            identity
        )

        if depth > max_depth:
            continue

        output.add(
            abs(
                int(current.pid)
            )
        )

        for parent in parents(
            current
        ):
            queue.append(
                (
                    parent,
                    depth + 1,
                )
            )

    return output


def has_hadron_ancestor(
    ancestor_pids: set[int],
) -> bool:
    """
    PDG IDs >=100 correspond to composite hadrons in the event records
    relevant here. Top, W, photons, leptons and partons are below 100.
    """

    return any(
        pid >= 100
        for pid in ancestor_pids
    )


def p4_hepmc(
    particle,
) -> FourVector:

    p = particle.momentum

    return FourVector(
        float(p.e),
        float(p.px),
        float(p.py),
        float(p.pz),
    )


def p4_component_residual(
    first: FourVector,
    second: FourVector,
) -> float:

    return float(
        max(
            abs(first.e - second.e),
            abs(first.px - second.px),
            abs(first.py - second.py),
            abs(first.pz - second.pz),
        )
    )


def wrap_delta_phi(
    x: float,
) -> float:

    return float(
        (
            x + math.pi
        )
        % (
            2.0 * math.pi
        )
        - math.pi
    )


def delta_r(
    first: FourVector,
    second: FourVector,
) -> float:

    return float(
        math.hypot(
            first.eta - second.eta,
            wrap_delta_phi(
                first.phi
                - second.phi
            ),
        )
    )


# =====================================================================
# Prompt charged-lepton selector
# =====================================================================

def select_prompt_stable_lepton(
    event,
    *,
    pid: int,
    hard_reference: FourVector,
    label: str,
):
    """
    Select the post-PYTHIA prompt charged analyzer.

    Required:
      * correct signed PDG ID
      * status == 1
      * no hadron ancestor
      * no tau ancestor
      * no photon ancestor

    Top/W ancestry is explicitly NOT required because the production
    preserves all resonance-history-presence classes.

    LHE proximity is diagnostic only and is never used as a cut.
    """

    all_same_pid = [
        particle
        for particle
        in event.particles
        if int(particle.pid) == pid
    ]

    stable = [
        particle
        for particle
        in all_same_pid
        if int(particle.status) == 1
    ]

    candidates = []

    diagnostic = []

    for particle in stable:

        ancestry = ancestor_abs_pids(
            particle
        )

        from_hadron = (
            has_hadron_ancestor(
                ancestry
            )
        )

        from_tau = (
            15 in ancestry
        )

        from_gamma = (
            22 in ancestry
        )

        p4 = p4_hepmc(
            particle
        )

        record = {
            "id": int(
                getattr(
                    particle,
                    "id",
                    0,
                )
            ),
            "status": int(
                particle.status
            ),
            "from_hadron": from_hadron,
            "from_tau": from_tau,
            "from_gamma": from_gamma,
            "has_top_ancestor": (
                6 in ancestry
            ),
            "has_W_ancestor": (
                24 in ancestry
            ),
            "deltaR_from_LHE": delta_r(
                p4,
                hard_reference,
            ),
            "p4max_from_LHE_GeV": (
                p4_component_residual(
                    p4,
                    hard_reference,
                )
            ),
        }

        diagnostic.append(
            record
        )

        if (
            not from_hadron
            and not from_tau
            and not from_gamma
        ):
            candidates.append(
                particle
            )

    if len(candidates) != 1:

        raise RuntimeError(
            f"{label}: expected exactly one prompt stable "
            f"PDG={pid} lepton after ancestry filtering; "
            f"found {len(candidates)}; "
            f"stable_candidates={diagnostic}"
        )

    selected = (
        candidates[0]
    )

    selected_p4 = p4_hepmc(
        selected
    )

    selected_ancestry = (
        ancestor_abs_pids(
            selected
        )
    )

    return {
        "particle": selected,
        "p4": selected_p4,
        "delta_r_from_lhe": delta_r(
            selected_p4,
            hard_reference,
        ),
        "p4max_from_lhe_GeV": (
            p4_component_residual(
                selected_p4,
                hard_reference,
            )
        ),
        "has_top_ancestor": (
            6 in selected_ancestry
        ),
        "has_W_ancestor": (
            24 in selected_ancestry
        ),
        "n_same_pid_total": (
            len(all_same_pid)
        ),
        "n_same_pid_stable": (
            len(stable)
        ),
        "n_prompt_candidates": (
            len(candidates)
        ),
    }


# =====================================================================
# Stable-photon dressing
# =====================================================================

def stable_photons(
    event,
) -> list:

    return [
        particle
        for particle in event.particles
        if (
            int(particle.pid) == 22
            and int(particle.status) == 1
            and particle.end_vertex is None
        )
    ]


def is_prompt_dressing_photon(
    particle,
) -> bool:

    ancestry = ancestor_abs_pids(
        particle
    )

    if 15 in ancestry:
        return False

    if has_hadron_ancestor(
        ancestry
    ):
        return False

    return True


def dress_lepton(
    bare: FourVector,
    photons: list,
    *,
    radius: float,
    prompt_only: bool,
) -> tuple[
    FourVector,
    int,
    float,
]:

    output = bare
    count = 0
    energy = 0.0

    for photon in photons:

        if (
            prompt_only
            and not is_prompt_dressing_photon(
                photon
            )
        ):
            continue

        photon_p4 = p4_hepmc(
            photon
        )

        if delta_r(
            bare,
            photon_p4,
        ) >= radius:
            continue

        output = (
            output
            + photon_p4
        )

        count += 1
        energy += (
            photon_p4.e
        )

    return (
        output,
        count,
        energy,
    )


# =====================================================================
# Observable helpers
# =====================================================================

def spin_vector(
    observables: dict,
) -> np.ndarray:

    raw = np.asarray(
        [
            float(
                observables[name]
            )
            for name
            in SPIN15_EVENT_COLUMNS
        ],
        dtype=float,
    )

    return (
        raw
        * SPIN_MULTIPLIERS
    )


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
        directory.glob(
            "*.hepmc3"
        )
    )

    if len(matches) != 1:
        raise RuntimeError(
            f"{variant}: expected one HepMC file "
            f"in {directory}, found {len(matches)}"
        )

    return matches[0]


# =====================================================================
# Scan one variant
# =====================================================================

def scan_variant(
    *,
    variant: str,
    path: Path,
    hard_truths: list[TTbarTruth],
    output_path: Path,
    progress_every: int,
    dress_dr: float,
) -> dict:

    try:
        import pyhepmc
    except ImportError as exc:
        raise RuntimeError(
            "pyhepmc unavailable; source setup_lxplus.sh"
        ) from exc

    total = len(
        hard_truths
    )

    print()
    print("=" * 78)
    print(f"SCANNING {variant}")
    print("=" * 78)
    print(path)

    event_numbers = []
    weights = []

    plus_dr = []
    minus_dr = []

    plus_dp4 = []
    minus_dp4 = []

    plus_has_top = []
    plus_has_w = []
    minus_has_top = []
    minus_has_w = []

    spin = {
        representation: []
        for representation
        in REPRESENTATIONS
    }

    scalar = {
        representation: {
            name: []
            for name
            in SCALAR_OBSERVABLES
        }
        for representation
        in REPRESENTATIONS
    }

    fieldnames = [
        "variant",
        "sequence_index",
        "hepmc_event_number",
        "event_weight",
        "decay_channel",

        "plus_bare_dR_from_hard",
        "minus_bare_dR_from_hard",

        "plus_bare_p4max_from_hard_GeV",
        "minus_bare_p4max_from_hard_GeV",

        "plus_has_top_ancestor",
        "minus_has_top_ancestor",

        "plus_has_W_ancestor",
        "minus_has_W_ancestor",

        "plus_same_pid_total",
        "minus_same_pid_total",

        "plus_same_pid_stable",
        "minus_same_pid_stable",

        "plus_prompt_candidate_count",
        "minus_prompt_candidate_count",

        "plus_all_dress_photons_r01",
        "minus_all_dress_photons_r01",

        "plus_prompt_dress_photons_r01",
        "minus_prompt_dress_photons_r01",

        "plus_all_dress_energy_r01_GeV",
        "minus_all_dress_energy_r01_GeV",

        "plus_prompt_dress_energy_r01_GeV",
        "minus_prompt_dress_energy_r01_GeV",
    ]

    for representation in REPRESENTATIONS:

        for name in SCALAR_OBSERVABLES:
            fieldnames.append(
                f"{representation}_{name}"
            )

        for name in SPIN15_EVENT_COLUMNS:
            fieldnames.append(
                f"{representation}_{name}"
            )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    processed = 0

    with gzip.open(
        output_path,
        "wt",
        newline="",
    ) as output_stream:

        writer = csv.DictWriter(
            output_stream,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        with pyhepmc.open(
            path
        ) as stream:

            for sequence_index, event in enumerate(
                stream
            ):

                if sequence_index >= total:
                    break

                hard = (
                    hard_truths[
                        sequence_index
                    ]
                )

                if hard.decay_channel == "epmum":
                    plus_pid = -11
                    minus_pid = 13

                elif hard.decay_channel == "mupem":
                    plus_pid = -13
                    minus_pid = 11

                else:
                    raise RuntimeError(
                        f"{variant} event {sequence_index}: "
                        f"unsupported channel "
                        f"{hard.decay_channel}"
                    )

                plus = (
                    select_prompt_stable_lepton(
                        event,
                        pid=plus_pid,
                        hard_reference=(
                            hard.lepton_plus
                        ),
                        label=(
                            f"{variant} event "
                            f"{sequence_index} positive analyzer"
                        ),
                    )
                )

                minus = (
                    select_prompt_stable_lepton(
                        event,
                        pid=minus_pid,
                        hard_reference=(
                            hard.lepton_minus
                        ),
                        label=(
                            f"{variant} event "
                            f"{sequence_index} negative analyzer"
                        ),
                    )
                )

                photons = stable_photons(
                    event
                )

                (
                    plus_dressed_all,
                    plus_all_n,
                    plus_all_e,
                ) = dress_lepton(
                    plus["p4"],
                    photons,
                    radius=dress_dr,
                    prompt_only=False,
                )

                (
                    minus_dressed_all,
                    minus_all_n,
                    minus_all_e,
                ) = dress_lepton(
                    minus["p4"],
                    photons,
                    radius=dress_dr,
                    prompt_only=False,
                )

                (
                    plus_dressed_prompt,
                    plus_prompt_n,
                    plus_prompt_e,
                ) = dress_lepton(
                    plus["p4"],
                    photons,
                    radius=dress_dr,
                    prompt_only=True,
                )

                (
                    minus_dressed_prompt,
                    minus_prompt_n,
                    minus_prompt_e,
                ) = dress_lepton(
                    minus["p4"],
                    photons,
                    radius=dress_dr,
                    prompt_only=True,
                )

                truths = {
                    "hard": hard,

                    "bare": dataclasses.replace(
                        hard,
                        lepton_plus=(
                            plus["p4"]
                        ),
                        lepton_minus=(
                            minus["p4"]
                        ),
                    ),

                    "dressed_all": dataclasses.replace(
                        hard,
                        lepton_plus=(
                            plus_dressed_all
                        ),
                        lepton_minus=(
                            minus_dressed_all
                        ),
                    ),

                    "dressed_prompt": dataclasses.replace(
                        hard,
                        lepton_plus=(
                            plus_dressed_prompt
                        ),
                        lepton_minus=(
                            minus_dressed_prompt
                        ),
                    ),
                }

                observables = {
                    name: event_observables(
                        truth
                    )
                    for name, truth
                    in truths.items()
                }

                event_number = int(
                    getattr(
                        event,
                        "event_number",
                        sequence_index,
                    )
                )

                event_numbers.append(
                    event_number
                )

                weights.append(
                    hard.event_weight
                )

                plus_dr.append(
                    plus[
                        "delta_r_from_lhe"
                    ]
                )

                minus_dr.append(
                    minus[
                        "delta_r_from_lhe"
                    ]
                )

                plus_dp4.append(
                    plus[
                        "p4max_from_lhe_GeV"
                    ]
                )

                minus_dp4.append(
                    minus[
                        "p4max_from_lhe_GeV"
                    ]
                )

                plus_has_top.append(
                    int(
                        plus[
                            "has_top_ancestor"
                        ]
                    )
                )

                minus_has_top.append(
                    int(
                        minus[
                            "has_top_ancestor"
                        ]
                    )
                )

                plus_has_w.append(
                    int(
                        plus[
                            "has_W_ancestor"
                        ]
                    )
                )

                minus_has_w.append(
                    int(
                        minus[
                            "has_W_ancestor"
                        ]
                    )
                )

                row = {
                    "variant": variant,

                    "sequence_index": (
                        sequence_index
                    ),

                    "hepmc_event_number": (
                        event_number
                    ),

                    "event_weight": (
                        hard.event_weight
                    ),

                    "decay_channel": (
                        hard.decay_channel
                    ),

                    "plus_bare_dR_from_hard": (
                        plus[
                            "delta_r_from_lhe"
                        ]
                    ),

                    "minus_bare_dR_from_hard": (
                        minus[
                            "delta_r_from_lhe"
                        ]
                    ),

                    "plus_bare_p4max_from_hard_GeV": (
                        plus[
                            "p4max_from_lhe_GeV"
                        ]
                    ),

                    "minus_bare_p4max_from_hard_GeV": (
                        minus[
                            "p4max_from_lhe_GeV"
                        ]
                    ),

                    "plus_has_top_ancestor": int(
                        plus[
                            "has_top_ancestor"
                        ]
                    ),

                    "minus_has_top_ancestor": int(
                        minus[
                            "has_top_ancestor"
                        ]
                    ),

                    "plus_has_W_ancestor": int(
                        plus[
                            "has_W_ancestor"
                        ]
                    ),

                    "minus_has_W_ancestor": int(
                        minus[
                            "has_W_ancestor"
                        ]
                    ),

                    "plus_same_pid_total": (
                        plus[
                            "n_same_pid_total"
                        ]
                    ),

                    "minus_same_pid_total": (
                        minus[
                            "n_same_pid_total"
                        ]
                    ),

                    "plus_same_pid_stable": (
                        plus[
                            "n_same_pid_stable"
                        ]
                    ),

                    "minus_same_pid_stable": (
                        minus[
                            "n_same_pid_stable"
                        ]
                    ),

                    "plus_prompt_candidate_count": (
                        plus[
                            "n_prompt_candidates"
                        ]
                    ),

                    "minus_prompt_candidate_count": (
                        minus[
                            "n_prompt_candidates"
                        ]
                    ),

                    "plus_all_dress_photons_r01": (
                        plus_all_n
                    ),

                    "minus_all_dress_photons_r01": (
                        minus_all_n
                    ),

                    "plus_prompt_dress_photons_r01": (
                        plus_prompt_n
                    ),

                    "minus_prompt_dress_photons_r01": (
                        minus_prompt_n
                    ),

                    "plus_all_dress_energy_r01_GeV": (
                        plus_all_e
                    ),

                    "minus_all_dress_energy_r01_GeV": (
                        minus_all_e
                    ),

                    "plus_prompt_dress_energy_r01_GeV": (
                        plus_prompt_e
                    ),

                    "minus_prompt_dress_energy_r01_GeV": (
                        minus_prompt_e
                    ),
                }

                for representation in REPRESENTATIONS:

                    obs = (
                        observables[
                            representation
                        ]
                    )

                    spin[
                        representation
                    ].append(
                        spin_vector(
                            obs
                        )
                    )

                    for name in SCALAR_OBSERVABLES:

                        value = float(
                            obs[name]
                        )

                        scalar[
                            representation
                        ][name].append(
                            value
                        )

                        row[
                            f"{representation}_{name}"
                        ] = value

                    for name in SPIN15_EVENT_COLUMNS:

                        row[
                            f"{representation}_{name}"
                        ] = float(
                            obs[name]
                        )

                writer.writerow(
                    row
                )

                processed += 1

                if (
                    processed == 1
                    or processed % progress_every == 0
                    or processed == total
                ):

                    print(
                        f"{variant}: "
                        f"{processed}/{total} "
                        f"({100*processed/total:.1f}%) "
                        f"max_dR="
                        f"{max(max(plus_dr),max(minus_dr)):.4g} "
                        f"max_dP4="
                        f"{max(max(plus_dp4),max(minus_dp4)):.4g} GeV",
                        flush=True,
                    )

    if processed != total:
        raise RuntimeError(
            f"{variant}: expected {total} events; "
            f"processed {processed}"
        )

    return {
        "event_numbers": (
            event_numbers
        ),

        "weights": np.asarray(
            weights,
            dtype=float,
        ),

        "plus_dr": np.asarray(
            plus_dr,
            dtype=float,
        ),

        "minus_dr": np.asarray(
            minus_dr,
            dtype=float,
        ),

        "plus_dp4": np.asarray(
            plus_dp4,
            dtype=float,
        ),

        "minus_dp4": np.asarray(
            minus_dp4,
            dtype=float,
        ),

        "plus_has_top": np.asarray(
            plus_has_top,
            dtype=int,
        ),

        "minus_has_top": np.asarray(
            minus_has_top,
            dtype=int,
        ),

        "plus_has_w": np.asarray(
            plus_has_w,
            dtype=int,
        ),

        "minus_has_w": np.asarray(
            minus_has_w,
            dtype=int,
        ),

        "spin": {
            representation: np.asarray(
                values,
                dtype=float,
            )
            for representation, values
            in spin.items()
        },

        "scalar": {
            representation: {
                name: np.asarray(
                    values,
                    dtype=float,
                )
                for name, values
                in columns.items()
            }
            for representation, columns
            in scalar.items()
        },
    }


# =====================================================================
# Output helper
# =====================================================================

def write_csv(
    path: Path,
    rows: list[dict],
):

    if not rows:
        raise RuntimeError(
            f"no rows for {path}"
        )

    with path.open(
        "w",
        newline="",
    ) as stream:

        writer = csv.DictWriter(
            stream,
            fieldnames=list(
                rows[0].keys()
            ),
        )

        writer.writeheader()

        writer.writerows(
            rows
        )


# =====================================================================
# Main analysis
# =====================================================================

def main() -> int:

    args = parse_args()

    args.output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    n_events = (
        args.expected_events
    )

    if args.max_events is not None:

        if args.max_events < 2:
            raise ValueError(
                "--max-events must be >=2"
            )

        n_events = min(
            n_events,
            args.max_events,
        )

    hard_truths = load_hard_truth(
        args.hard_lhe,
        n_events,
    )

    paths = {}
    data = {}

    for variant in VARIANTS:

        path = find_hepmc(
            args.root,
            variant,
            args.sample_id,
        )

        paths[variant] = path

        data[variant] = scan_variant(
            variant=variant,
            path=path,
            hard_truths=hard_truths,
            output_path=(
                args.output_dir
                / (
                    f"{variant}"
                    "_spin_lepton_events.csv.gz"
                )
            ),
            progress_every=max(
                1,
                min(
                    args.progress_every,
                    n_events,
                ),
            ),
            dress_dr=args.dress_dr,
        )

    reference = (
        "G0_H0"
    )

    print()
    print("=" * 78)
    print("PAIRING / SELECTOR VALIDATION")
    print("=" * 78)

    pairing_pass = True

    for variant in VARIANTS:

        events_ok = (
            data[variant][
                "event_numbers"
            ]
            == data[reference][
                "event_numbers"
            ]
        )

        weights_ok = np.allclose(
            data[variant]["weights"],
            data[reference]["weights"],
            rtol=1e-12,
            atol=0.0,
        )

        pairing_pass &= bool(
            events_ok
            and weights_ok
        )

        print(
            f"{variant}: "
            f"EVENT_KEYS="
            f"{'PASS' if events_ok else 'FAIL'} "
            f"WEIGHTS="
            f"{'PASS' if weights_ok else 'FAIL'} "
            f"plus_top_frac="
            f"{np.mean(data[variant]['plus_has_top']):.6f} "
            f"plus_W_frac="
            f"{np.mean(data[variant]['plus_has_w']):.6f} "
            f"minus_top_frac="
            f"{np.mean(data[variant]['minus_has_top']):.6f} "
            f"minus_W_frac="
            f"{np.mean(data[variant]['minus_has_w']):.6f}"
        )

    if not pairing_pass:
        raise RuntimeError(
            "event pairing validation failed"
        )

    weights = (
        data[reference][
            "weights"
        ]
    )

    # ================================================================
    # Hard representation must be numerically identical because all
    # variants share one LHE hard basis.
    # ================================================================

    hard_identical = True

    for variant in VARIANTS:

        delta = (
            data[variant]["spin"]["hard"]
            - data[reference]["spin"]["hard"]
        )

        max_delta = float(
            np.max(
                np.abs(delta)
            )
        )

        print(
            f"HARD_SPIN_IDENTITY {variant}: "
            f"max_abs_delta={max_delta:.3e}"
        )

        hard_identical &= (
            max_delta <= 1e-14
        )

    if not hard_identical:
        raise RuntimeError(
            "common hard-spin representation "
            "is unexpectedly non-identical"
        )

    # ================================================================
    # Spin tables
    # ================================================================

    coefficient_rows = []
    paired_spin_rows = []
    factorial_spin_rows = []

    for representation in REPRESENTATIONS:

        for variant in VARIANTS:

            values = (
                data[variant][
                    "spin"
                ][representation]
            )

            mean, cov, neff = (
                weighted_mean_cov_mean(
                    values,
                    weights,
                )
            )

            errors = np.sqrt(
                np.clip(
                    np.diag(cov),
                    0.0,
                    None,
                )
            )

            for i, coefficient in enumerate(
                SPIN15_COEFFICIENT_NAMES
            ):

                coefficient_rows.append(
                    {
                        "variant": variant,
                        "representation": representation,
                        "coefficient": coefficient,
                        "value": float(
                            mean[i]
                        ),
                        "standard_error": float(
                            errors[i]
                        ),
                        "effective_events": float(
                            neff
                        ),
                    }
                )

        for variant in (
            "G1_H0",
            "G0_H1",
            "G1_H1",
        ):

            difference = (
                data[variant][
                    "spin"
                ][representation]
                - data[reference][
                    "spin"
                ][representation]
            )

            delta, cov, neff = (
                weighted_mean_cov_mean(
                    difference,
                    weights,
                )
            )

            errors = np.sqrt(
                np.clip(
                    np.diag(cov),
                    0.0,
                    None,
                )
            )

            z = np.divide(
                delta,
                errors,
                out=np.zeros_like(delta),
                where=errors > 0,
            )

            for i, coefficient in enumerate(
                SPIN15_COEFFICIENT_NAMES
            ):

                paired_spin_rows.append(
                    {
                        "comparison": (
                            f"{variant}-G0_H0"
                        ),
                        "representation": representation,
                        "coefficient": coefficient,
                        "delta": float(
                            delta[i]
                        ),
                        "paired_standard_error": float(
                            errors[i]
                        ),
                        "paired_z": float(
                            z[i]
                        ),
                        "effective_events": float(
                            neff
                        ),
                    }
                )

        gamma_effect = (
            0.5
            * (
                (
                    data["G1_H0"]["spin"][representation]
                    - data["G0_H0"]["spin"][representation]
                )
                + (
                    data["G1_H1"]["spin"][representation]
                    - data["G0_H1"]["spin"][representation]
                )
            )
        )

        hadron_effect = (
            0.5
            * (
                (
                    data["G0_H1"]["spin"][representation]
                    - data["G0_H0"]["spin"][representation]
                )
                + (
                    data["G1_H1"]["spin"][representation]
                    - data["G1_H0"]["spin"][representation]
                )
            )
        )

        interaction = (
            data["G1_H1"]["spin"][representation]
            - data["G1_H0"]["spin"][representation]
            - data["G0_H1"]["spin"][representation]
            + data["G0_H0"]["spin"][representation]
        )

        for contrast, values in (
            (
                "gamma_main_effect",
                gamma_effect,
            ),
            (
                "hadron_qed_main_effect",
                hadron_effect,
            ),
            (
                "gamma_x_hadron_interaction",
                interaction,
            ),
        ):

            effect, cov, neff = (
                weighted_mean_cov_mean(
                    values,
                    weights,
                )
            )

            errors = np.sqrt(
                np.clip(
                    np.diag(cov),
                    0.0,
                    None,
                )
            )

            z = np.divide(
                effect,
                errors,
                out=np.zeros_like(effect),
                where=errors > 0,
            )

            for i, coefficient in enumerate(
                SPIN15_COEFFICIENT_NAMES
            ):

                factorial_spin_rows.append(
                    {
                        "contrast": contrast,
                        "representation": representation,
                        "coefficient": coefficient,
                        "effect": float(
                            effect[i]
                        ),
                        "standard_error": float(
                            errors[i]
                        ),
                        "z": float(
                            z[i]
                        ),
                        "effective_events": float(
                            neff
                        ),
                    }
                )

    # ================================================================
    # Scalar tables
    # ================================================================

    scalar_rows = []
    paired_scalar_rows = []
    factorial_scalar_rows = []

    for representation in REPRESENTATIONS:

        for variant in VARIANTS:

            for observable in SCALAR_OBSERVABLES:

                mean, error, neff = (
                    scalar_mean_error(
                        data[variant][
                            "scalar"
                        ][representation][observable],
                        weights,
                    )
                )

                scalar_rows.append(
                    {
                        "variant": variant,
                        "representation": representation,
                        "observable": observable,
                        "mean": mean,
                        "standard_error": error,
                        "effective_events": neff,
                    }
                )

        for variant in (
            "G1_H0",
            "G0_H1",
            "G1_H1",
        ):

            for observable in SCALAR_OBSERVABLES:

                difference = (
                    data[variant][
                        "scalar"
                    ][representation][observable]
                    - data[reference][
                        "scalar"
                    ][representation][observable]
                )

                mean, error, neff = (
                    scalar_mean_error(
                        difference,
                        weights,
                    )
                )

                paired_scalar_rows.append(
                    {
                        "comparison": (
                            f"{variant}-G0_H0"
                        ),
                        "representation": representation,
                        "observable": observable,
                        "paired_mean_delta": mean,
                        "paired_standard_error": error,
                        "paired_z": (
                            mean / error
                            if error > 0
                            else 0.0
                        ),
                        "effective_events": neff,
                    }
                )

        for observable in SCALAR_OBSERVABLES:

            gamma_effect = (
                0.5
                * (
                    (
                        data["G1_H0"]["scalar"][representation][observable]
                        - data["G0_H0"]["scalar"][representation][observable]
                    )
                    + (
                        data["G1_H1"]["scalar"][representation][observable]
                        - data["G0_H1"]["scalar"][representation][observable]
                    )
                )
            )

            hadron_effect = (
                0.5
                * (
                    (
                        data["G0_H1"]["scalar"][representation][observable]
                        - data["G0_H0"]["scalar"][representation][observable]
                    )
                    + (
                        data["G1_H1"]["scalar"][representation][observable]
                        - data["G1_H0"]["scalar"][representation][observable]
                    )
                )
            )

            interaction = (
                data["G1_H1"]["scalar"][representation][observable]
                - data["G1_H0"]["scalar"][representation][observable]
                - data["G0_H1"]["scalar"][representation][observable]
                + data["G0_H0"]["scalar"][representation][observable]
            )

            for contrast, values in (
                (
                    "gamma_main_effect",
                    gamma_effect,
                ),
                (
                    "hadron_qed_main_effect",
                    hadron_effect,
                ),
                (
                    "gamma_x_hadron_interaction",
                    interaction,
                ),
            ):

                mean, error, neff = (
                    scalar_mean_error(
                        values,
                        weights,
                    )
                )

                factorial_scalar_rows.append(
                    {
                        "contrast": contrast,
                        "representation": representation,
                        "observable": observable,
                        "effect": mean,
                        "standard_error": error,
                        "z": (
                            mean / error
                            if error > 0
                            else 0.0
                        ),
                        "effective_events": neff,
                    }
                )

    # ================================================================
    # Save tables
    # ================================================================

    write_csv(
        args.output_dir
        / "spin15_coefficients.csv",
        coefficient_rows,
    )

    write_csv(
        args.output_dir
        / "spin15_paired_differences.csv",
        paired_spin_rows,
    )

    write_csv(
        args.output_dir
        / "spin15_factorial_contrasts.csv",
        factorial_spin_rows,
    )

    write_csv(
        args.output_dir
        / "scalar_observable_summary.csv",
        scalar_rows,
    )

    write_csv(
        args.output_dir
        / "scalar_paired_differences.csv",
        paired_scalar_rows,
    )

    write_csv(
        args.output_dir
        / "scalar_factorial_contrasts.csv",
        factorial_scalar_rows,
    )

    # ================================================================
    # Compact selector diagnostics
    # ================================================================

    selector_rows = []

    for variant in VARIANTS:

        selector_rows.append(
            {
                "variant": variant,

                "events": n_events,

                "max_plus_dR_from_LHE": float(
                    np.max(
                        data[variant][
                            "plus_dr"
                        ]
                    )
                ),

                "max_minus_dR_from_LHE": float(
                    np.max(
                        data[variant][
                            "minus_dr"
                        ]
                    )
                ),

                "max_plus_p4max_from_LHE_GeV": float(
                    np.max(
                        data[variant][
                            "plus_dp4"
                        ]
                    )
                ),

                "max_minus_p4max_from_LHE_GeV": float(
                    np.max(
                        data[variant][
                            "minus_dp4"
                        ]
                    )
                ),

                "plus_top_ancestor_fraction": float(
                    np.mean(
                        data[variant][
                            "plus_has_top"
                        ]
                    )
                ),

                "minus_top_ancestor_fraction": float(
                    np.mean(
                        data[variant][
                            "minus_has_top"
                        ]
                    )
                ),

                "plus_W_ancestor_fraction": float(
                    np.mean(
                        data[variant][
                            "plus_has_w"
                        ]
                    )
                ),

                "minus_W_ancestor_fraction": float(
                    np.mean(
                        data[variant][
                            "minus_has_w"
                        ]
                    )
                ),
            }
        )

    write_csv(
        args.output_dir
        / "prompt_selector_summary.csv",
        selector_rows,
    )

    # ================================================================
    # Terminal decision summary
    # ================================================================

    print()
    print("=" * 78)
    print("SPIN-15 PAIRED DIFFERENCE SUMMARY")
    print("=" * 78)

    for representation in REPRESENTATIONS:

        print()
        print(
            f"REPRESENTATION={representation}"
        )

        for variant in (
            "G1_H0",
            "G0_H1",
            "G1_H1",
        ):

            subset = [
                row
                for row in paired_spin_rows
                if (
                    row["comparison"]
                    == f"{variant}-G0_H0"
                    and row["representation"]
                    == representation
                )
            ]

            worst = max(
                subset,
                key=lambda row: abs(
                    float(
                        row["paired_z"]
                    )
                ),
            )

            max_delta = max(
                abs(
                    float(
                        row["delta"]
                    )
                )
                for row in subset
            )

            print(
                f"  {variant}: "
                f"max|delta|={max_delta:.6g} "
                f"max|paired z|="
                f"{abs(float(worst['paired_z'])):.3f} "
                f"worst={worst['coefficient']}"
            )

    print()
    print("=" * 78)
    print("LEPTON PT PAIRED DIFFERENCES")
    print("=" * 78)

    for representation in (
        "bare",
        "dressed_all",
        "dressed_prompt",
    ):

        print()
        print(
            f"REPRESENTATION={representation}"
        )

        for row in paired_scalar_rows:

            if (
                row["representation"]
                != representation
            ):
                continue

            if row["observable"] not in {
                "lepton_plus_pt_GeV",
                "lepton_minus_pt_GeV",
            }:
                continue

            print(
                f"  {row['comparison']} "
                f"{row['observable']}: "
                f"delta="
                f"{row['paired_mean_delta']:.6g} GeV "
                f"+/- "
                f"{row['paired_standard_error']:.6g} "
                f"z={row['paired_z']:.3f}"
            )

    report = {
        "status": "PASS",

        "analysis_version": (
            "qed_spin_lepton_systematics_v3"
        ),

        "hard_basis": (
            "common_six_fermion_LHE"
        ),

        "prompt_lepton_definition": {
            "status": 1,
            "correct_signed_pdg": True,
            "reject_hadron_ancestor": True,
            "reject_tau_ancestor": True,
            "reject_gamma_ancestor": True,
            "require_top_ancestor": False,
            "require_W_ancestor": False,
            "require_LHE_momentum_match": False,
            "require_unique_candidate": True,
        },

        "representations": list(
            REPRESENTATIONS
        ),

        "dress_dr": (
            args.dress_dr
        ),

        "events_analyzed": (
            n_events
        ),

        "reference": (
            reference
        ),

        "variants": list(
            VARIANTS
        ),

        "hard_lhe": str(
            args.hard_lhe
        ),

        "inputs": {
            variant: str(path)
            for variant, path
            in paths.items()
        },
    }

    (
        args.output_dir
        / "spin_lepton_systematics_report.json"
    ).write_text(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    print()
    print("=" * 78)
    print("FINAL")
    print("=" * 78)

    print(
        "PROMPT_SELECTOR=PASS"
    )

    print(
        "HARD_SPIN_COMMON_LHE=PASS"
    )

    print(
        "PAIRING=PASS"
    )

    print(
        "QED_SPIN_LEPTON_ANALYSIS_V3=PASS"
    )

    print(
        f"OUTPUT_DIR={args.output_dir}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
