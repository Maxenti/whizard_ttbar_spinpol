#!/usr/bin/env python3

from collections import deque
from math import atan2, asinh, hypot, pi, sqrt

import pyhepmc

from qis_ttbar.io.lhe import iter_lhe_events


LHE_PATH = r"""/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/full6f_365gev_ee_ttbar_spinpol_v1/phase12_production_v1/20260821T162202Z_WT_A07F3_S0_1M_40x25k_v1p0p1/whizard_raw/S0_P12_1M_0001/phase11c_S0_P12_1M_0001_seed412100001.lhe"""
HEPMC_PATH = r"""/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/full6f_365gev_ee_ttbar_spinpol_v1/phase12_production_v1/20260821T162202Z_WT_A07F3_S0_1M_40x25k_v1p0p1/shower/qed_systematics_v1/20260824T154629Z_P12_QED4x25k_samehard_seed812100001_v1/G0_H0/hepmc3/full6f365_ee_LR100_epmum_WT_A07F3_S0/full6f365_ee_LR100_epmum_WT_A07F3_S0__P12_1M_0001_G0_H0.hepmc3"""

N_EVENTS = 10


def particle_id(p):
    value = int(getattr(p, "id", 0))
    return value if value else id(p)


def parents(p):
    if p.production_vertex is None:
        return []
    return list(p.production_vertex.particles_in)


def children(p):
    if p.end_vertex is None:
        return []
    return list(p.end_vertex.particles_out)


def ancestor_records(p, max_depth=12):
    q = deque(
        (parent, 1)
        for parent in parents(p)
    )

    seen = set()
    output = []

    while q:
        current, depth = q.popleft()

        ident = particle_id(current)

        if ident in seen or depth > max_depth:
            continue

        seen.add(ident)

        output.append(
            (
                depth,
                int(getattr(current, "id", 0)),
                int(current.pid),
                int(current.status),
            )
        )

        for parent in parents(current):
            q.append(
                (parent, depth + 1)
            )

    return output


def p4_tuple_hepmc(p):
    m = p.momentum
    return (
        float(m.e),
        float(m.px),
        float(m.py),
        float(m.pz),
    )


def p4_tuple_lhe(p):
    v = p.p4
    return (
        float(v.e),
        float(v.px),
        float(v.py),
        float(v.pz),
    )


def component_residual(a, b):
    return max(
        abs(x - y)
        for x, y in zip(a, b)
    )


def pt_eta_phi(v):
    e, px, py, pz = v

    pt = hypot(px, py)

    phi = atan2(py, px)

    eta = (
        asinh(pz / pt)
        if pt > 0.0
        else (
            float("inf")
            if pz >= 0.0
            else -float("inf")
        )
    )

    return pt, eta, phi


def wrap_phi(x):
    while x > pi:
        x -= 2.0 * pi
    while x <= -pi:
        x += 2.0 * pi
    return x


def delta_r(a, b):
    _, eta1, phi1 = pt_eta_phi(a)
    _, eta2, phi2 = pt_eta_phi(b)

    return hypot(
        eta1 - eta2,
        wrap_phi(phi1 - phi2),
    )


def final_lhe_particle(event, pid):
    matches = [
        p
        for p in event.particles
        if p.status == 1 and p.pdg == pid
    ]

    if len(matches) != 1:
        raise RuntimeError(
            f"LHE event {event.index}: "
            f"PDG {pid} final matches={len(matches)}"
        )

    return matches[0]


def ancestry_flags(records):
    pids = {
        abs(pid)
        for _, _, pid, _
        in records
    }

    return {
        "top": 6 in pids,
        "W": 24 in pids,
        "tau": 15 in pids,
        "gamma": 22 in pids,
        "hadron": any(
            pid >= 100
            for pid in pids
        ),
        "b": 5 in pids,
    }


lhe_iter = iter_lhe_events(
    LHE_PATH,
    max_events=N_EVENTS,
)

with pyhepmc.open(HEPMC_PATH) as stream:

    for sequence, (lhe, event) in enumerate(
        zip(lhe_iter, stream)
    ):

        print()
        print("=" * 100)
        print(
            f"EVENT sequence={sequence} "
            f"LHE_index={lhe.index} "
            f"HepMC_event={getattr(event, 'event_number', sequence)}"
        )
        print("=" * 100)

        for label, pid in (
            ("POSITIVE_ANALYZER_eplus", -11),
            ("NEGATIVE_ANALYZER_muminus", 13),
        ):
            target_particle = final_lhe_particle(
                lhe,
                pid,
            )

            target = p4_tuple_lhe(
                target_particle
            )

            print()
            print(
                f"{label} PDG={pid}"
            )
            print(
                "  LHE hard p4 "
                f"E={target[0]:.9g} "
                f"px={target[1]:.9g} "
                f"py={target[2]:.9g} "
                f"pz={target[3]:.9g}"
            )

            candidates = [
                p
                for p in event.particles
                if int(p.pid) == pid
            ]

            ranked = sorted(
                candidates,
                key=lambda p: (
                    0 if int(p.status) == 1 else 1,
                    delta_r(
                        p4_tuple_hepmc(p),
                        target,
                    ),
                    component_residual(
                        p4_tuple_hepmc(p),
                        target,
                    ),
                    int(getattr(p, "id", 0)),
                ),
            )

            print(
                f"  HepMC candidates={len(ranked)}"
            )

            for candidate in ranked:
                hp4 = p4_tuple_hepmc(
                    candidate
                )

                records = ancestor_records(
                    candidate
                )

                flags = ancestry_flags(
                    records
                )

                parent_summary = [
                    (
                        int(getattr(p, "id", 0)),
                        int(p.pid),
                        int(p.status),
                    )
                    for p in parents(candidate)
                ]

                child_summary = [
                    (
                        int(getattr(p, "id", 0)),
                        int(p.pid),
                        int(p.status),
                    )
                    for p in children(candidate)
                ]

                print(
                    "  CAND "
                    f"id={int(getattr(candidate, 'id', 0)):4d} "
                    f"status={int(candidate.status):3d} "
                    f"E={hp4[0]:11.6f} "
                    f"pt={pt_eta_phi(hp4)[0]:11.6f} "
                    f"dR={delta_r(hp4, target):.6e} "
                    f"dP4max={component_residual(hp4, target):.6e}"
                )

                print(
                    "       flags="
                    f"{flags}"
                )

                print(
                    "       parents="
                    f"{parent_summary}"
                )

                print(
                    "       children="
                    f"{child_summary}"
                )

                print(
                    "       ancestors="
                    f"{records[:20]}"
                )

        resonances = [
            p
            for p in event.particles
            if abs(int(p.pid)) in {
                6,
                24,
            }
        ]

        print()
        print(
            "  RESONANCE RECORDS:",
            [
                (
                    int(getattr(p, "id", 0)),
                    int(p.pid),
                    int(p.status),
                    [
                        int(c.pid)
                        for c in children(p)
                    ],
                )
                for p in resonances
            ],
        )
