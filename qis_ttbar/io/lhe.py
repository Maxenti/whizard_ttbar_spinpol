from __future__ import annotations

import dataclasses
import gzip
import re
from pathlib import Path
from typing import Iterator, TextIO

from ..exceptions import EventFormatError
from ..models import FourVector, LHEEvent, Particle, TTbarTruth


@dataclasses.dataclass(frozen=True)
class LHEHeader:
    beam1_pdg: int
    beam2_pdg: int
    beam1_energy_GeV: float
    beam2_energy_GeV: float
    cross_section_pb: float
    cross_section_error_pb: float
    declared_events: int | None


def open_text(path: Path) -> TextIO:
    return gzip.open(path, "rt", errors="replace") if path.suffix == ".gz" else path.open(errors="replace")


def _float(value: str) -> float:
    return float(value.replace("D", "E").replace("d", "e"))


def parse_particle(line: str) -> Particle:
    fields = line.split()
    if len(fields) < 13:
        raise EventFormatError(f"particle row has {len(fields)} columns, expected >=13: {line}")
    return Particle(
        pdg=int(fields[0]), status=int(fields[1]), mother1=int(fields[2]), mother2=int(fields[3]),
        color1=int(fields[4]), color2=int(fields[5]),
        p4=FourVector(_float(fields[9]), _float(fields[6]), _float(fields[7]), _float(fields[8])),
        mass_record=_float(fields[10]), lifetime=_float(fields[11]), spin=_float(fields[12]),
    )


def iter_lhe_events(path: str | Path, max_events: int | None = None) -> Iterator[LHEEvent]:
    path = Path(path)
    inside = False
    block: list[str] = []
    index = 0
    with open_text(path) as stream:
        for raw in stream:
            line = raw.strip()
            if line == "<event>":
                if inside:
                    raise EventFormatError(f"nested <event> in {path}")
                inside, block = True, []
            elif line == "</event>":
                if not inside:
                    continue
                clean = [x.strip() for x in block if x.strip() and not x.lstrip().startswith("#")]
                header = clean[0].split()
                if len(header) < 6:
                    raise EventFormatError(f"malformed event header in {path}: {clean[0]}")
                nup = int(header[0])
                rows = [x for x in clean[1:] if not x.startswith("<")]
                if len(rows) < nup:
                    raise EventFormatError(f"NUP={nup}, particle rows={len(rows)} in event {index}")
                yield LHEEvent(
                    index=index, idprup=int(header[1]), weight=_float(header[2]), scale=_float(header[3]),
                    aqed=_float(header[4]), aqcd=_float(header[5]),
                    particles=tuple(parse_particle(row) for row in rows[:nup]),
                )
                index += 1
                inside, block = False, []
                if max_events is not None and index >= max_events:
                    return
            elif inside:
                block.append(raw)
    if inside:
        raise EventFormatError(f"unterminated event block in {path}")


def parse_lhe_header(path: str | Path) -> LHEHeader:
    path = Path(path)
    init: list[str] = []
    in_init = False
    declared: int | None = None
    xsec_re = re.compile(r'<xsecinfo\s+[^>]*neve="(\d+)"')
    with open_text(path) as stream:
        for raw in stream:
            line = raw.strip()
            match = xsec_re.search(line)
            if match:
                declared = int(match.group(1))
            if line == "<init>":
                in_init = True
            elif line == "</init>":
                break
            elif in_init and line and not line.startswith("<") and not line.startswith("#"):
                init.append(line)
    if len(init) < 2:
        raise EventFormatError(f"missing complete <init> block in {path}")
    beam, process = init[0].split(), init[1].split()
    return LHEHeader(
        beam1_pdg=int(beam[0]), beam2_pdg=int(beam[1]),
        beam1_energy_GeV=_float(beam[2]), beam2_energy_GeV=_float(beam[3]),
        cross_section_pb=_float(process[0]), cross_section_error_pb=_float(process[1]),
        declared_events=declared,
    )


def _unique_by_pdg_and_status(event: LHEEvent, pdg: int, statuses: set[int]) -> tuple[int, Particle]:
    matches = [(i + 1, p) for i, p in enumerate(event.particles) if p.pdg == pdg and p.status in statuses]
    if len(matches) != 1:
        raise EventFormatError(
            f"event {event.index}: expected one PDG {pdg} with status {sorted(statuses)}, found {len(matches)}"
        )
    return matches[0]


def _child_of(event: LHEEvent, parent_index: int, allowed_pdgs: set[int]) -> Particle:
    matches = [
        p for p in event.particles
        if p.pdg in allowed_pdgs and parent_index in {p.mother1, p.mother2}
    ]
    if len(matches) != 1:
        raise EventFormatError(
            f"event {event.index}: parent {parent_index} expected one child in {sorted(allowed_pdgs)}, found {len(matches)}"
        )
    return matches[0]


def extract_ttbar_truth(event: LHEEvent, initial_state: str | None = None) -> TTbarTruth:
    top_index, top = _unique_by_pdg_and_status(event, 6, {2})
    antitop_index, antitop = _unique_by_pdg_and_status(event, -6, {2})
    beam_minus_pdg = 11 if initial_state in (None, "ee") else 13
    if initial_state is None:
        beam_minus_pdg = abs(event.particles[0].pdg)
    minus_candidates = [p for p in event.particles if p.pdg == beam_minus_pdg and p.status == -1]
    plus_candidates = [p for p in event.particles if p.pdg == -beam_minus_pdg and p.status == -1]
    if len(minus_candidates) != 1 or len(plus_candidates) != 1:
        raise EventFormatError(f"event {event.index}: cannot identify post-ISR incoming beams")
    b = _child_of(event, top_index, {5})
    bbar = _child_of(event, antitop_index, {-5})
    lp = _child_of(event, top_index, {-11, -13, -15})
    lm = _child_of(event, antitop_index, {11, 13, 15})
    nu = _child_of(event, top_index, {12, 14, 16})
    nubar = _child_of(event, antitop_index, {-12, -14, -16})
    decay = "epmum" if lp.pdg == -11 and lm.pdg == 13 else "mupem" if lp.pdg == -13 and lm.pdg == 11 else "other"
    state = initial_state or ("ee" if beam_minus_pdg == 11 else "mumu")
    return TTbarTruth(
        event_index=event.index, event_weight=event.weight,
        beam_minus=minus_candidates[0].p4, beam_plus=plus_candidates[0].p4,
        top=top.p4, antitop=antitop.p4, b=b.p4, bbar=bbar.p4,
        lepton_plus=lp.p4, lepton_minus=lm.p4, neutrino=nu.p4, antineutrino=nubar.p4,
        initial_state=state, decay_channel=decay,
    )
