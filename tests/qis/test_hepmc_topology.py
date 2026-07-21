from __future__ import annotations

from dataclasses import dataclass, field

from qis_ttbar.io.hepmc import (
    _find_decaying_resonance,
    _find_primary_leptonic_products,
)


@dataclass
class Momentum:
    e: float
    px: float = 0.0
    py: float = 0.0
    pz: float = 0.0


@dataclass
class Vertex:
    particles_in: list["Particle"] = field(default_factory=list)
    particles_out: list["Particle"] = field(default_factory=list)


@dataclass
class Particle:
    pid: int
    id: int
    energy: float
    status: int = 2
    production_vertex: Vertex | None = None
    end_vertex: Vertex | None = None

    @property
    def momentum(self) -> Momentum:
        return Momentum(self.energy)


def decay(parent: Particle, *children: Particle) -> None:
    vertex = Vertex(particles_in=[parent], particles_out=list(children))
    parent.end_vertex = vertex
    for child in children:
        child.production_vertex = vertex


def make_complete_antitop(identifier: int, energy: float) -> tuple[Particle, Particle, Particle]:
    antitop = Particle(-6, identifier, energy)
    wminus = Particle(-24, identifier + 1, 80.0)
    bbar = Particle(-5, identifier + 2, 30.0, status=1)
    lepton = Particle(13, identifier + 3, 35.0, status=1)
    antineutrino = Particle(-14, identifier + 4, 25.0, status=1)
    decay(antitop, wminus, bbar)
    decay(wminus, lepton, antineutrino)
    return antitop, lepton, antineutrino


def test_complete_semileptonic_copy_beats_higher_energy_b_only_copy():
    incomplete = Particle(-6, 1, 260.0)
    decay(incomplete, Particle(-5, 2, 40.0, status=1))

    complete, lepton, antineutrino = make_complete_antitop(10, 230.0)

    selected = _find_decaying_resonance([incomplete, complete], -6, "antitop")
    assert selected is complete
    found_lepton, found_neutrino = _find_primary_leptonic_products(selected, -6)
    assert found_lepton is lepton
    assert found_neutrino is antineutrino


def test_complete_root_copy_is_preserved_for_hard_process_kinematics():
    root = Particle(-6, 100, 250.0)
    final, lepton, antineutrino = make_complete_antitop(110, 225.0)
    photon = Particle(22, 101, 25.0, status=1)
    decay(root, final, photon)

    selected = _find_decaying_resonance([root, final], -6, "antitop")
    assert selected is root
    found_lepton, found_neutrino = _find_primary_leptonic_products(selected, -6)
    assert found_lepton is lepton
    assert found_neutrino is antineutrino


def test_primary_w_branch_is_used_instead_of_secondary_b_lepton():
    top = Particle(6, 200, 230.0)
    wplus = Particle(24, 201, 80.0)
    b = Particle(5, 202, 35.0)
    primary_lepton = Particle(-11, 203, 45.0, status=1)
    neutrino = Particle(12, 204, 30.0, status=1)
    secondary_lepton = Particle(-13, 205, 60.0, status=1)

    decay(top, wplus, b)
    decay(wplus, primary_lepton, neutrino)
    decay(b, secondary_lepton)

    found_lepton, found_neutrino = _find_primary_leptonic_products(top, 6)
    assert found_lepton is primary_lepton
    assert found_neutrino is neutrino


def test_terminal_w_decay_beats_photon_conversion_pair_from_earlier_w_copy():
    antitop = Particle(-6, 300, 250.0)
    bbar = Particle(-5, 301, 135.0)
    w_early = Particle(-24, 302, 102.0, status=22)
    decay(antitop, bbar, w_early)

    w_terminal = Particle(-24, 303, 101.0, status=52)
    photon = Particle(22, 304, 2.5, status=51)
    decay(w_early, w_terminal, photon)

    conversion_positron = Particle(-11, 305, 1.1, status=1)
    conversion_electron = Particle(11, 306, 1.4, status=1)
    decay(photon, conversion_positron, conversion_electron)

    primary_muon = Particle(13, 307, 59.9, status=23)
    primary_antineutrino = Particle(-14, 308, 42.2, status=23)
    decay(w_terminal, primary_muon, primary_antineutrino)

    found_lepton, found_neutrino = _find_primary_leptonic_products(
        antitop,
        -6,
    )

    assert found_lepton is primary_muon
    assert found_neutrino is primary_antineutrino


def test_direct_w_pair_must_have_matching_lepton_neutrino_flavour():
    antitop = Particle(-6, 400, 250.0)
    bbar = Particle(-5, 401, 135.0)
    wminus = Particle(-24, 402, 102.0, status=52)
    decay(antitop, bbar, wminus)

    electron = Particle(11, 403, 30.0, status=1)
    muon_antineutrino = Particle(-14, 404, 40.0, status=1)
    decay(wminus, electron, muon_antineutrino)

    try:
        _find_primary_leptonic_products(antitop, -6)
    except Exception as exc:
        assert "no direct flavour-consistent" in str(exc)
    else:
        raise AssertionError("flavour-mismatched W decay was accepted")
