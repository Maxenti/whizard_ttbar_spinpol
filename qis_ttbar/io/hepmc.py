from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import Iterator

from ..exceptions import EventFormatError
from ..models import FourVector, TTbarTruth


def _p4(particle) -> FourVector:
    momentum = particle.momentum
    return FourVector(float(momentum.e), float(momentum.px), float(momentum.py), float(momentum.pz))


def _children(particle) -> list:
    if particle.end_vertex is None:
        return []
    return list(particle.end_vertex.particles_out)


def _parents(particle) -> list:
    if particle.production_vertex is None:
        return []
    return list(particle.production_vertex.particles_in)


def _has_ancestor_with_pid(particle, pid: int, max_depth: int = 20) -> bool:
    queue = deque((parent, 1) for parent in _parents(particle))
    visited: set[int] = set()
    while queue:
        current, depth = queue.popleft()
        identity = id(current)
        if identity in visited or depth > max_depth:
            continue
        visited.add(identity)
        if current.pid == pid:
            return True
        queue.extend((parent, depth + 1) for parent in _parents(current))
    return False


def _nearest_descendants(parent, pdgs: set[int], *, max_depth: int = 12) -> list[tuple[int, object]]:
    """Return matching descendants at the first depth where matches exist.

    Restricting to the nearest generation prevents leptons from b-hadron decays
    from competing with the charged lepton in the primary top decay.
    """
    queue = deque((child, 1) for child in _children(parent))
    visited: set[int] = set()
    matches: list[tuple[int, object]] = []
    match_depth: int | None = None
    while queue:
        current, depth = queue.popleft()
        identity = id(current)
        if identity in visited or depth > max_depth:
            continue
        visited.add(identity)
        if match_depth is not None and depth > match_depth:
            break
        if current.pid in pdgs:
            match_depth = depth
            matches.append((depth, current))
            continue
        queue.extend((child, depth + 1) for child in _children(current))
    return matches


def _find_descendant(parent, pdgs: set[int], label: str):
    matches = _nearest_descendants(parent, pdgs)
    if not matches:
        raise EventFormatError(f"no {label} descendant of PDG {parent.pid}")
    if len(matches) == 1:
        return matches[0][1]
    # Repeated event-record copies can appear at one depth. Prefer a particle
    # that is not itself followed by an identical-PDG copy, then the highest
    # energy candidate. This selection is deterministic.
    candidates = [particle for _, particle in matches]
    terminal = [p for p in candidates if not any(child.pid == p.pid for child in _children(p))]
    pool = terminal or candidates
    pool.sort(key=lambda particle: (-float(particle.momentum.e), int(getattr(particle, "id", 0))))
    if len(pool) > 1 and abs(float(pool[0].momentum.e) - float(pool[1].momentum.e)) < 1e-12:
        raise EventFormatError(f"ambiguous {label} descendants of PDG {parent.pid}: {len(pool)}")
    return pool[0]


def _find_decaying_resonance(particles: list, pid: int, label: str):
    candidates = [p for p in particles if p.pid == pid and p.end_vertex is not None]
    if not candidates:
        raise EventFormatError(f"expected a decaying {label}, found none")
    # Prefer the first resonance copy, then require that its decay chain has
    # the expected b child. This remains stable across PYTHIA status-copying.
    roots = [p for p in candidates if not _has_ancestor_with_pid(p, pid)] or candidates
    expected_b = {5} if pid == 6 else {-5}
    compatible = []
    for candidate in roots:
        try:
            _find_descendant(candidate, expected_b, "b child")
        except EventFormatError:
            continue
        compatible.append(candidate)
    pool = compatible or roots
    pool.sort(key=lambda particle: (-float(particle.momentum.e), int(getattr(particle, "status", 0))))
    return pool[0]


def _find_beam(particles: list, pid: int, label: str):
    candidates = [p for p in particles if p.pid == pid and p.status in {4, -1}]
    if not candidates:
        # Some HepMC converters map incoming hard particles to status 3.
        candidates = [p for p in particles if p.pid == pid and p.production_vertex is None]
    if not candidates:
        raise EventFormatError(f"cannot identify {label}")
    # Beam direction is the relevant quantity for basis construction. Prefer
    # the highest-energy beam-line representative and deterministic barcode.
    candidates.sort(key=lambda particle: (-float(particle.momentum.e), int(getattr(particle, "id", 0))))
    return candidates[0]


def iter_hepmc_ttbar(
    path: str | Path,
    *,
    initial_state: str,
    max_events: int | None = None,
) -> Iterator[TTbarTruth]:
    try:
        import pyhepmc
    except ImportError as exc:
        raise RuntimeError("pyhepmc is required to read HepMC3 files") from exc
    if initial_state not in {"ee", "mumu"}:
        raise ValueError(f"unsupported initial state: {initial_state}")
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    beam_pdg = 11 if initial_state == "ee" else 13
    with pyhepmc.open(path) as stream:
        for index, event in enumerate(stream):
            particles = list(event.particles)
            top = _find_decaying_resonance(particles, 6, "top")
            antitop = _find_decaying_resonance(particles, -6, "antitop")
            incoming_minus = _find_beam(particles, beam_pdg, "incoming negative lepton")
            incoming_plus = _find_beam(particles, -beam_pdg, "incoming positive lepton")
            b = _find_descendant(top, {5}, "b")
            bbar = _find_descendant(antitop, {-5}, "bbar")
            lp = _find_descendant(top, {-11, -13, -15}, "positive lepton")
            lm = _find_descendant(antitop, {11, 13, 15}, "negative lepton")
            nu = _find_descendant(top, {12, 14, 16}, "neutrino")
            nubar = _find_descendant(antitop, {-12, -14, -16}, "antineutrino")
            decay = (
                "epmum" if lp.pid == -11 and lm.pid == 13
                else "mupem" if lp.pid == -13 and lm.pid == 11
                else "other"
            )
            weight = float(event.weights[0]) if event.weights else 1.0
            yield TTbarTruth(
                event_index=int(getattr(event, "event_number", index)),
                event_weight=weight,
                beam_minus=_p4(incoming_minus),
                beam_plus=_p4(incoming_plus),
                top=_p4(top),
                antitop=_p4(antitop),
                b=_p4(b),
                bbar=_p4(bbar),
                lepton_plus=_p4(lp),
                lepton_minus=_p4(lm),
                neutrino=_p4(nu),
                antineutrino=_p4(nubar),
                initial_state=initial_state,
                decay_channel=decay,
            )
            if max_events is not None and index + 1 >= max_events:
                return
