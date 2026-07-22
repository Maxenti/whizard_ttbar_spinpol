#!/usr/bin/env python3
"""Shared contracts for the 365 GeV polarized ttbar LHE matrix campaign.

This module is intentionally independent of WHIZARD execution.  It defines the
16-sample campaign, validates qualified 500 GeV ISR production templates, and
materializes deterministic 365 GeV SINDARIN inputs without modifying the
source templates.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


INITIAL_STATES = ("ee", "mumu")
DECAY_CHANNELS = ("epmum", "mupem")
POLARIZATIONS = ("LR100", "RL100")
SPIN_MODES = ("sc", "iso")

META_PATTERN = re.compile(
    r"(?im)^\s*!\s*META\s+(?P<key>[A-Za-z0-9_]+)\s*=\s*(?P<value>.*?)\s*$"
)
ENERGY_PATTERN = re.compile(
    r"(?im)^(?P<prefix>\s*sqrts\s*=\s*)500(?:\.0+)?"
    r"(?P<unit>\s*GeV)(?P<tail>\s*(?:!.*)?)$"
)
SEED_PATTERN = re.compile(
    r"(?im)^(?P<prefix>\s*seed\s*=\s*)(?P<value>[^!\r\n]*?\S)"
    r"(?P<tail>\s*(?:!.*)?)$"
)
EVENT_PATTERN = re.compile(
    r"(?im)^(?P<prefix>\s*n_events\s*=\s*)(?P<value>[^!\r\n]*?\S)"
    r"(?P<tail>\s*(?:!.*)?)$"
)
SAMPLE_PATTERN = re.compile(
    r"(?im)^(?P<prefix>\s*\$sample\s*=\s*)(?P<value>[^!\r\n]*?\S)"
    r"(?P<tail>\s*(?:!.*)?)$"
)

CONTROLLED_META_KEYS = {
    "campaign_id",
    "campaign_sample_id",
    "sample_id",
    "nominal_sqrt_s_GeV",
    "sqrt_s_GeV",
    "initial_state",
    "decay_channel",
    "polarization",
    "beam1_helicity",
    "beam2_helicity",
    "beam1_pol_fraction",
    "beam2_pol_fraction",
    "spin_mode",
    "isr_enabled",
    "beam_spectrum",
    "model",
    "seed",
    "random_seed",
    "requested_events",
}


@dataclass(frozen=True)
class SampleSpec:
    index: int
    initial_state: str
    decay_channel: str
    polarization: str
    spin_mode: str
    isr: bool
    source_sqrt_s_GeV: float
    nominal_sqrt_s_GeV: float
    events: int
    random_seed: int
    source_sample_id: str
    sample_id: str
    template_relative_path: str
    run_relative_path: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def metadata_values(text: str) -> dict[str, list[str]]:
    values: dict[str, list[str]] = {}
    for match in META_PATTERN.finditer(text):
        values.setdefault(match.group("key"), []).append(match.group("value").strip())
    return values


def truthy(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes", "on"}


def expected_beam_particles(initial_state: str) -> tuple[str, str]:
    if initial_state == "ee":
        return "e1", "E1"
    if initial_state == "mumu":
        return "e2", "E2"
    raise ValueError(f"Unsupported initial_state={initial_state}")


def expected_decay_processes(decay_channel: str) -> tuple[tuple[str, str, str], tuple[str, str, str]]:
    if decay_channel == "epmum":
        return (("b", "E1", "n1"), ("bbar", "e2", "N2"))
    if decay_channel == "mupem":
        return (("b", "E2", "n2"), ("bbar", "e1", "N1"))
    raise ValueError(f"Unsupported decay_channel={decay_channel}")


def expected_helicities(polarization: str) -> tuple[int, int]:
    if polarization == "LR100":
        return -1, +1
    if polarization == "RL100":
        return +1, -1
    raise ValueError(f"Unsupported polarization={polarization}")


def source_sample_id(
    initial_state: str,
    decay_channel: str,
    polarization: str,
    spin_mode: str,
    source_energy_GeV: int = 500,
) -> str:
    return (
        f"{initial_state}_ttbar_{decay_channel}_{polarization}_{spin_mode}_"
        f"ISR_{source_energy_GeV}GeV"
    )


def target_sample_id(
    initial_state: str,
    decay_channel: str,
    polarization: str,
    spin_mode: str,
    target_energy_GeV: int = 365,
) -> str:
    return (
        f"{initial_state}_ttbar_{decay_channel}_{polarization}_{spin_mode}_"
        f"ISR_{target_energy_GeV}GeV"
    )


def build_matrix(
    *,
    events: int,
    seed_base: int,
    output_root: str,
    template_root: str = "sindarin/production",
    source_energy_GeV: int = 500,
    target_energy_GeV: int = 365,
) -> list[SampleSpec]:
    if events <= 0:
        raise ValueError("events must be positive")
    if seed_base <= 0:
        raise ValueError("seed_base must be positive")

    samples: list[SampleSpec] = []
    index = 0
    for initial_state in INITIAL_STATES:
        for decay_channel in DECAY_CHANNELS:
            for polarization in POLARIZATIONS:
                for spin_mode in SPIN_MODES:
                    index += 1
                    source_id = source_sample_id(
                        initial_state,
                        decay_channel,
                        polarization,
                        spin_mode,
                        source_energy_GeV,
                    )
                    sample_id = target_sample_id(
                        initial_state,
                        decay_channel,
                        polarization,
                        spin_mode,
                        target_energy_GeV,
                    )
                    samples.append(
                        SampleSpec(
                            index=index,
                            initial_state=initial_state,
                            decay_channel=decay_channel,
                            polarization=polarization,
                            spin_mode=spin_mode,
                            isr=True,
                            source_sqrt_s_GeV=float(source_energy_GeV),
                            nominal_sqrt_s_GeV=float(target_energy_GeV),
                            events=int(events),
                            random_seed=int(seed_base) + index,
                            source_sample_id=source_id,
                            sample_id=sample_id,
                            template_relative_path=f"{template_root}/{source_id}.sin.in",
                            run_relative_path=f"{output_root}/{initial_state}/{sample_id}",
                        )
                    )

    if len(samples) != 16:
        raise AssertionError(f"Expected 16 samples, built {len(samples)}")
    if len({sample.sample_id for sample in samples}) != 16:
        raise AssertionError("Target sample IDs are not unique")
    if len({sample.random_seed for sample in samples}) != 16:
        raise AssertionError("Random seeds are not unique")
    return samples


def _record(checks: list[dict[str, Any]], name: str, passed: bool, message: str) -> None:
    checks.append(
        {
            "check": name,
            "status": "pass" if passed else "fail",
            "message": message,
        }
    )


def _metadata_exact(meta: dict[str, list[str]], key: str, expected: str) -> bool:
    return meta.get(key, []) == [expected]


def _process_pattern(name: str, parent: str, daughters: Iterable[str]) -> re.Pattern[str]:
    rhs = r"\s*,\s*".join(re.escape(value) for value in daughters)
    return re.compile(
        rf"(?im)^\s*process\s+{re.escape(name)}\s*=\s*"
        rf"{re.escape(parent)}\s*=>\s*{rhs}\s*(?:!.*)?$"
    )


def source_template_checks(text: str, sample: SampleSpec) -> list[dict[str, Any]]:
    meta = metadata_values(text)
    checks: list[dict[str, Any]] = []

    _record(
        checks,
        "source_sample_id",
        _metadata_exact(meta, "sample_id", sample.source_sample_id),
        f"source sample_id={meta.get('sample_id', [])}, expected {sample.source_sample_id}",
    )
    _record(
        checks,
        "source_initial_state",
        _metadata_exact(meta, "initial_state", sample.initial_state),
        f"source initial_state={meta.get('initial_state', [])}",
    )
    _record(
        checks,
        "source_decay_channel",
        _metadata_exact(meta, "decay_channel", sample.decay_channel),
        f"source decay_channel={meta.get('decay_channel', [])}",
    )
    _record(
        checks,
        "source_polarization",
        _metadata_exact(meta, "polarization", sample.polarization),
        f"source polarization={meta.get('polarization', [])}",
    )
    _record(
        checks,
        "source_spin_mode",
        _metadata_exact(meta, "spin_mode", sample.spin_mode),
        f"source spin_mode={meta.get('spin_mode', [])}",
    )
    isr_values = meta.get("isr_enabled", [])
    _record(
        checks,
        "source_isr_enabled",
        len(isr_values) == 1 and truthy(isr_values[0]),
        f"source isr_enabled={isr_values}",
    )
    _record(
        checks,
        "source_sqrts",
        len(ENERGY_PATTERN.findall(text)) == 1,
        "source has exactly one sqrts=500 GeV assignment",
    )
    _record(
        checks,
        "source_seed_assignment",
        len(SEED_PATTERN.findall(text)) == 1,
        "source has exactly one seed assignment",
    )
    _record(
        checks,
        "source_event_assignment",
        len(EVENT_PATTERN.findall(text)) == 1,
        "source has exactly one n_events assignment",
    )
    _record(
        checks,
        "source_sample_assignment",
        len(SAMPLE_PATTERN.findall(text)) == 1,
        "source has exactly one $sample assignment",
    )

    beam_minus, beam_plus = expected_beam_particles(sample.initial_state)
    _record(
        checks,
        "source_isr_beams",
        re.search(
            rf"(?im)^\s*beams\s*=\s*{beam_minus}\s*,\s*{beam_plus}\s*=>\s*isr\s*(?:!.*)?$",
            text,
        )
        is not None,
        f"source uses {beam_minus},{beam_plus} => isr",
    )
    _record(
        checks,
        "source_isr_handler",
        re.search(r"(?im)^\s*\?isr_handler\s*=\s*true\s*(?:!.*)?$", text)
        is not None,
        "source enables the ISR handler",
    )
    _record(
        checks,
        "source_isr_recoil_mode",
        re.search(
            r'(?im)^\s*\$isr_handler_mode\s*=\s*["\']recoil["\']\s*(?:!.*)?$',
            text,
        )
        is not None,
        "source uses ISR recoil mode",
    )

    top_daughters, antitop_daughters = expected_decay_processes(sample.decay_channel)
    _record(
        checks,
        "source_top_decay_process",
        _process_pattern("t_decay", "t", top_daughters).search(text) is not None,
        f"source t_decay daughters={top_daughters}",
    )
    _record(
        checks,
        "source_antitop_decay_process",
        _process_pattern("tbar_decay", "tbar", antitop_daughters).search(text) is not None,
        f"source tbar_decay daughters={antitop_daughters}",
    )

    h1, h2 = expected_helicities(sample.polarization)
    h1_text = re.escape(f"{h1:+d}")
    h2_text = re.escape(f"{h2:+d}")
    _record(
        checks,
        "source_beam_helicities",
        re.search(
            rf"(?im)^\s*beams_pol_density\s*=\s*@\({h1_text}\)\s*,\s*@\({h2_text}\)\s*(?:!.*)?$",
            text,
        )
        is not None,
        f"source beam helicities=({h1:+d},{h2:+d})",
    )

    expected_iso = "true" if sample.spin_mode == "iso" else "false"
    _record(
        checks,
        "source_isotropic_decay",
        re.search(
            rf"(?im)^\s*\?isotropic_decay\s*=\s*{expected_iso}\s*(?:!.*)?$",
            text,
        )
        is not None,
        f"source isotropic_decay={expected_iso}",
    )
    return checks


def require_checks(checks: list[dict[str, Any]], label: str) -> None:
    failures = [item for item in checks if item["status"] != "pass"]
    if not failures:
        return
    details = "\n".join(
        f"  - {item['check']}: {item['message']}" for item in failures
    )
    raise ValueError(f"{label} failed:\n{details}")


def strip_controlled_metadata(text: str) -> tuple[str, int]:
    removed = 0
    retained: list[str] = []
    for line in text.splitlines(keepends=True):
        match = META_PATTERN.match(line.rstrip("\n"))
        if match and match.group("key") in CONTROLLED_META_KEYS:
            removed += 1
            continue
        retained.append(line)
    return "".join(retained), removed


def canonical_header(campaign_id: str, sample: SampleSpec) -> str:
    h1, h2 = expected_helicities(sample.polarization)
    return (
        "! PAPER_SPIN_365GEV_LHE_MATRIX_V1\n"
        f"! META campaign_id={campaign_id}\n"
        f"! META campaign_sample_id={sample.sample_id}\n"
        f"! META sample_id={sample.sample_id}\n"
        f"! META nominal_sqrt_s_GeV={sample.nominal_sqrt_s_GeV:g}\n"
        f"! META sqrt_s_GeV={sample.nominal_sqrt_s_GeV:g}\n"
        f"! META initial_state={sample.initial_state}\n"
        f"! META decay_channel={sample.decay_channel}\n"
        f"! META polarization={sample.polarization}\n"
        f"! META beam1_helicity={h1:+d}\n"
        f"! META beam2_helicity={h2:+d}\n"
        "! META beam1_pol_fraction=1.0\n"
        "! META beam2_pol_fraction=1.0\n"
        f"! META spin_mode={sample.spin_mode}\n"
        "! META isr_enabled=true\n"
        "! META beam_spectrum=none\n"
        "! META model=SM\n"
        f"! META seed={sample.random_seed}\n"
        f"! META random_seed={sample.random_seed}\n"
        f"! META requested_events={sample.events}\n"
    )


def prepared_input_checks(text: str, campaign_id: str, sample: SampleSpec) -> list[dict[str, Any]]:
    meta = metadata_values(text)
    checks: list[dict[str, Any]] = []
    expected_meta = {
        "campaign_id": campaign_id,
        "sample_id": sample.sample_id,
        "sqrt_s_GeV": f"{sample.nominal_sqrt_s_GeV:g}",
        "initial_state": sample.initial_state,
        "decay_channel": sample.decay_channel,
        "polarization": sample.polarization,
        "spin_mode": sample.spin_mode,
        "isr_enabled": "true",
        "seed": str(sample.random_seed),
        "requested_events": str(sample.events),
    }
    for key, expected in expected_meta.items():
        _record(
            checks,
            f"prepared_meta_{key}",
            meta.get(key, []) == [expected],
            f"{key}={meta.get(key, [])}, expected [{expected}]",
        )

    _record(
        checks,
        "prepared_sqrts_assignment",
        len(
            re.findall(
                rf"(?im)^\s*sqrts\s*=\s*{sample.nominal_sqrt_s_GeV:g}(?:\.0+)?\s*GeV\s*(?:!.*)?$",
                text,
            )
        )
        == 1,
        "exactly one target-energy sqrts assignment",
    )
    _record(
        checks,
        "prepared_seed_assignment",
        len(
            re.findall(
                rf"(?im)^\s*seed\s*=\s*{sample.random_seed}\s*(?:!.*)?$",
                text,
            )
        )
        == 1,
        "exactly one materialized seed assignment",
    )
    _record(
        checks,
        "prepared_event_assignment",
        len(
            re.findall(
                rf"(?im)^\s*n_events\s*=\s*{sample.events}\s*(?:!.*)?$",
                text,
            )
        )
        == 1,
        "exactly one materialized event assignment",
    )
    _record(
        checks,
        "prepared_sample_assignment",
        len(
            re.findall(
                rf'(?im)^\s*\$sample\s*=\s*["\']{re.escape(sample.sample_id)}["\']\s*(?:!.*)?$',
                text,
            )
        )
        == 1,
        "exactly one materialized output sample assignment",
    )

    controlled_lines = "\n".join(
        line
        for line in text.splitlines()
        if re.match(r"(?i)^\s*(?:seed|n_events|\$sample)\s*=", line)
    )
    _record(
        checks,
        "prepared_no_placeholders",
        re.search(
            r"__[A-Z0-9_]+__|@[A-Z_][A-Z0-9_]*@|\$\{[A-Za-z_][A-Za-z0-9_]*\}",
            controlled_lines,
        )
        is None,
        "no unresolved controlled placeholders",
    )
    _record(
        checks,
        "prepared_no_source_energy_tokens",
        re.search(
            r"500GeV|(?<![0-9])500(?:\.0+)?\s*GeV|sqrt\s*\(s\)\s*=\s*500|sqrts\s*=\s*500",
            text,
            re.I,
        )
        is None,
        "no stale 500 GeV tokens",
    )
    _record(
        checks,
        "prepared_no_source_sample_id",
        sample.source_sample_id not in text,
        "source sample ID removed",
    )

    # Reuse the physics-level source checks with the target metadata and energy
    # handled separately.  The ISR, beam, decay, polarization and spin controls
    # must remain unchanged by materialization.
    beam_minus, beam_plus = expected_beam_particles(sample.initial_state)
    _record(
        checks,
        "prepared_isr_beams",
        re.search(
            rf"(?im)^\s*beams\s*=\s*{beam_minus}\s*,\s*{beam_plus}\s*=>\s*isr\s*(?:!.*)?$",
            text,
        )
        is not None,
        "ISR beam mapping preserved",
    )
    _record(
        checks,
        "prepared_isr_handler",
        re.search(r"(?im)^\s*\?isr_handler\s*=\s*true\s*(?:!.*)?$", text)
        is not None,
        "ISR handler preserved",
    )
    expected_iso = "true" if sample.spin_mode == "iso" else "false"
    _record(
        checks,
        "prepared_isotropic_decay",
        re.search(
            rf"(?im)^\s*\?isotropic_decay\s*=\s*{expected_iso}\s*(?:!.*)?$",
            text,
        )
        is not None,
        f"isotropic_decay={expected_iso} preserved",
    )
    return checks


def transform_template(text: str, campaign_id: str, sample: SampleSpec) -> tuple[str, dict[str, int], list[dict[str, Any]]]:
    source_checks = source_template_checks(text, sample)
    require_checks(source_checks, f"source template contract for {sample.source_sample_id}")

    output, removed_meta = strip_controlled_metadata(text)
    counts: dict[str, int] = {"controlled_metadata_removed": removed_meta}

    output, counts["sqrts_assignments"] = ENERGY_PATTERN.subn(
        lambda match: (
            f"{match.group('prefix')}{sample.nominal_sqrt_s_GeV:g}"
            f"{match.group('unit')}{match.group('tail')}"
        ),
        output,
    )
    output, counts["seed_assignments"] = SEED_PATTERN.subn(
        lambda match: f"{match.group('prefix')}{sample.random_seed}{match.group('tail')}",
        output,
    )
    output, counts["event_assignments"] = EVENT_PATTERN.subn(
        lambda match: f"{match.group('prefix')}{sample.events}{match.group('tail')}",
        output,
    )
    output, counts["sample_assignments"] = SAMPLE_PATTERN.subn(
        lambda match: f'{match.group("prefix")}"{sample.sample_id}"{match.group("tail")}',
        output,
    )

    for key in ("sqrts_assignments", "seed_assignments", "event_assignments", "sample_assignments"):
        if counts[key] != 1:
            raise ValueError(f"Expected exactly one {key}; found {counts[key]}")

    output, counts["source_sample_tokens"] = re.subn(
        re.escape(sample.source_sample_id), sample.sample_id, output
    )
    output, counts["energy_name_tokens"] = re.subn(r"500GeV", "365GeV", output)
    output, counts["prose_energy_tokens"] = re.subn(
        r"sqrt\s*\(s\)\s*=\s*500\s*GeV",
        "sqrt(s)=365 GeV",
        output,
        flags=re.I,
    )
    output, counts["generic_energy_tokens"] = re.subn(
        r"(?<![0-9])500(?:\.0+)?\s*GeV",
        "365 GeV",
        output,
        flags=re.I,
    )
    output = canonical_header(campaign_id, sample) + output.lstrip("\n")

    prepared_checks = prepared_input_checks(output, campaign_id, sample)
    require_checks(prepared_checks, f"prepared input contract for {sample.sample_id}")
    return output, counts, source_checks + prepared_checks


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n")
