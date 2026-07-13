#!/usr/bin/env python3
"""Shared helpers for the WHIZARD ttbar production workflow.

This module intentionally uses only the Python standard library so that every
workflow stage can run inside the Key4HEP environment on lxplus and Condor
worker nodes without adding a Python package dependency.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator, Sequence

FLOAT_RE = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][+-]?\d+)?"
LHE_SUFFIXES = (".lhe", ".lhef", ".lhe.gz", ".lhef.gz")

CONFIG_FIELDS = [
    "campaign_id",
    "sample_id",
    "enabled",
    "initial_state",
    "beam1",
    "beam2",
    "decay_channel",
    "polarization",
    "beam1_helicity",
    "beam2_helicity",
    "beam1_pol_fraction",
    "beam2_pol_fraction",
    "sqrt_s_GeV",
    "isr_enabled",
    "isr_mass_GeV",
    "isr_alpha",
    "spin_correlated",
    "beam_spectrum",
    "n_shards",
    "events_per_shard",
    "seed_base",
    "request_cpus",
    "request_memory_mb",
    "job_flavour",
    "archive_workspace",
]


@dataclass(frozen=True)
class SampleConfig:
    campaign_id: str
    sample_id: str
    enabled: bool
    initial_state: str
    beam1: str
    beam2: str
    decay_channel: str
    polarization: str
    beam1_helicity: int
    beam2_helicity: int
    beam1_pol_fraction: float
    beam2_pol_fraction: float
    sqrt_s_GeV: float
    isr_enabled: bool
    isr_mass_GeV: float
    isr_alpha: float
    spin_correlated: bool
    beam_spectrum: str
    n_shards: int
    events_per_shard: int
    seed_base: int
    request_cpus: int
    request_memory_mb: int
    job_flavour: str
    archive_workspace: bool

    @property
    def template_name(self) -> str:
        return f"{self.sample_id}.sin.in"

    def shard_seed(self, shard_index: int) -> int:
        if shard_index < 0 or shard_index >= self.n_shards:
            raise ValueError(
                f"shard index {shard_index} outside [0, {self.n_shards}) "
                f"for {self.sample_id}"
            )
        return self.seed_base + shard_index

    def shard_label(self, shard_index: int) -> str:
        return f"shard_{shard_index:04d}"

    def output_sample_name(self, shard_index: int) -> str:
        return f"{self.sample_id}__{self.shard_label(shard_index)}"


@dataclass(frozen=True)
class IntegrationResult:
    value: float
    error: float
    source_line: str


@dataclass(frozen=True)
class LHEInit:
    incoming_pdg1: int
    incoming_pdg2: int
    beam_energy1_GeV: float
    beam_energy2_GeV: float
    cross_section_pb: float
    cross_section_error_pb: float
    max_weight: float
    process_id: int
    declared_events: int | None
    total_cross_section_pb: float | None


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_bool(value: str | bool | int) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off", ""}:
        return False
    raise ValueError(f"cannot parse boolean value: {value!r}")


def as_float(value: object, default: float | None = None) -> float | None:
    try:
        return float(str(value).replace("D", "E").replace("d", "e"))
    except (TypeError, ValueError):
        return default


def as_int(value: object, default: int | None = None) -> int | None:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def repo_root_from_script(script_file: str | Path) -> Path:
    return Path(script_file).resolve().parents[2]


def default_output_root() -> Path:
    return Path(
        os.environ.get(
            "WHIZARD_TTBAR_OUTPUT_ROOT",
            "/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol",
        )
    )


def canonical(path: Path) -> Path:
    try:
        return path.resolve(strict=False)
    except OSError:
        return Path(os.path.realpath(path))


def ensure_eos(path: Path, *, allow_non_eos: bool = False) -> None:
    resolved = canonical(path)
    text = str(resolved)
    if text.startswith("/eos/"):
        return
    if allow_non_eos or os.environ.get("WHIZARD_ALLOW_NON_EOS_OUTPUT") == "1":
        return
    raise ValueError(
        f"persistent output path is not on EOS: {path} -> {resolved}. "
        "Use --allow-non-eos only for an intentional local test."
    )


def read_configs(path: Path, *, include_disabled: bool = False) -> list[SampleConfig]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream)
        missing = [field for field in CONFIG_FIELDS if field not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"configuration is missing fields: {', '.join(missing)}")
        configs: list[SampleConfig] = []
        for line_no, row in enumerate(reader, start=2):
            try:
                cfg = SampleConfig(
                    campaign_id=row["campaign_id"].strip(),
                    sample_id=row["sample_id"].strip(),
                    enabled=parse_bool(row["enabled"]),
                    initial_state=row["initial_state"].strip(),
                    beam1=row["beam1"].strip(),
                    beam2=row["beam2"].strip(),
                    decay_channel=row["decay_channel"].strip(),
                    polarization=row["polarization"].strip(),
                    beam1_helicity=int(row["beam1_helicity"]),
                    beam2_helicity=int(row["beam2_helicity"]),
                    beam1_pol_fraction=float(row["beam1_pol_fraction"]),
                    beam2_pol_fraction=float(row["beam2_pol_fraction"]),
                    sqrt_s_GeV=float(row["sqrt_s_GeV"]),
                    isr_enabled=parse_bool(row["isr_enabled"]),
                    isr_mass_GeV=float(row["isr_mass_GeV"]),
                    isr_alpha=float(row["isr_alpha"]),
                    spin_correlated=parse_bool(row["spin_correlated"]),
                    beam_spectrum=row["beam_spectrum"].strip(),
                    n_shards=int(row["n_shards"]),
                    events_per_shard=int(row["events_per_shard"]),
                    seed_base=int(row["seed_base"]),
                    request_cpus=int(row["request_cpus"]),
                    request_memory_mb=int(row["request_memory_mb"]),
                    job_flavour=row["job_flavour"].strip(),
                    archive_workspace=parse_bool(row["archive_workspace"]),
                )
            except Exception as exc:
                raise ValueError(f"invalid configuration row {line_no}: {exc}") from exc
            if cfg.enabled or include_disabled:
                configs.append(cfg)
    validate_configs(configs)
    return configs


def validate_configs(configs: Sequence[SampleConfig]) -> None:
    if not configs:
        raise ValueError("configuration contains no enabled samples")
    campaigns = {cfg.campaign_id for cfg in configs}
    if len(campaigns) != 1:
        raise ValueError(f"configuration must contain exactly one campaign_id, got {campaigns}")
    seen_ids: set[str] = set()
    used_seeds: dict[int, str] = {}
    for cfg in configs:
        if cfg.sample_id in seen_ids:
            raise ValueError(f"duplicate sample_id: {cfg.sample_id}")
        seen_ids.add(cfg.sample_id)
        if cfg.initial_state not in {"ee", "mumu"}:
            raise ValueError(f"unsupported initial_state for {cfg.sample_id}: {cfg.initial_state}")
        if cfg.decay_channel not in {"epmum", "mupem"}:
            raise ValueError(f"unsupported decay_channel for {cfg.sample_id}: {cfg.decay_channel}")
        if cfg.polarization not in {"LR100", "RL100"}:
            raise ValueError(f"unsupported polarization for {cfg.sample_id}: {cfg.polarization}")
        if cfg.beam1_helicity not in {-1, 1} or cfg.beam2_helicity not in {-1, 1}:
            raise ValueError(f"beam helicities must be +/-1 for {cfg.sample_id}")
        if not 0.0 <= cfg.beam1_pol_fraction <= 1.0:
            raise ValueError(f"invalid beam1_pol_fraction for {cfg.sample_id}")
        if not 0.0 <= cfg.beam2_pol_fraction <= 1.0:
            raise ValueError(f"invalid beam2_pol_fraction for {cfg.sample_id}")
        if cfg.n_shards <= 0 or cfg.events_per_shard <= 0:
            raise ValueError(f"n_shards and events_per_shard must be positive for {cfg.sample_id}")
        if cfg.request_cpus <= 0 or cfg.request_memory_mb <= 0:
            raise ValueError(f"invalid Condor resources for {cfg.sample_id}")
        if cfg.isr_mass_GeV <= 0 or cfg.isr_alpha <= 0:
            raise ValueError(f"invalid ISR mass/alpha for {cfg.sample_id}")
        if not cfg.isr_enabled:
            raise ValueError(f"production-v1 requires ISR enabled for {cfg.sample_id}")
        if not cfg.spin_correlated:
            raise ValueError(f"production-v1 requires spin-correlated decays for {cfg.sample_id}")
        for shard in range(cfg.n_shards):
            seed = cfg.shard_seed(shard)
            owner = used_seeds.get(seed)
            if owner is not None:
                raise ValueError(f"duplicate seed {seed}: {owner} and {cfg.sample_id}/shard_{shard:04d}")
            used_seeds[seed] = f"{cfg.sample_id}/shard_{shard:04d}"


def filter_configs(configs: Sequence[SampleConfig], patterns: Sequence[str]) -> list[SampleConfig]:
    if not patterns:
        return list(configs)
    import fnmatch

    selected = [cfg for cfg in configs if any(fnmatch.fnmatch(cfg.sample_id, p) for p in patterns)]
    if not selected:
        raise ValueError(f"no samples matched patterns: {patterns}")
    return selected


def campaign_root(output_root: Path, campaign_id: str, *, smoke: bool = False) -> Path:
    suffix = "_smoke" if smoke else ""
    return output_root / "production" / f"{campaign_id}{suffix}"


def write_csv(path: Path, fieldnames: Sequence[str], rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with atomic_text_writer(path) as stream:
        writer = csv.DictWriter(stream, fieldnames=list(fieldnames), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


class atomic_text_writer:
    def __init__(self, path: Path, encoding: str = "utf-8") -> None:
        self.path = path
        self.encoding = encoding
        self.tmp: Path | None = None
        self.stream = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, name = tempfile.mkstemp(prefix=f".{self.path.name}.", dir=self.path.parent)
        self.tmp = Path(name)
        self.stream = os.fdopen(fd, "w", encoding=self.encoding, newline="")
        return self.stream

    def __exit__(self, exc_type, exc, tb):
        assert self.stream is not None and self.tmp is not None
        self.stream.close()
        if exc_type is None:
            os.replace(self.tmp, self.path)
        else:
            self.tmp.unlink(missing_ok=True)
        return False


def atomic_write_text(path: Path, text: str) -> None:
    with atomic_text_writer(path) as stream:
        stream.write(text)


def atomic_write_json(path: Path, payload: object) -> None:
    atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def open_text(path: Path, mode: str = "rt"):
    if path.name.endswith(".gz"):
        return gzip.open(path, mode, encoding="utf-8", errors="replace")
    return path.open(mode, encoding="utf-8", errors="replace")


def is_lhe(path: Path) -> bool:
    return any(path.name.endswith(suffix) for suffix in LHE_SUFFIXES)


def count_lhe_events(path: Path) -> int:
    count = 0
    with open_text(path) as stream:
        for line in stream:
            if line.lstrip().startswith("<event"):
                count += 1
    return count


def read_lhe_init(path: Path) -> LHEInit:
    with open_text(path) as stream:
        text_lines: list[str] = []
        in_init = False
        for line in stream:
            stripped = line.strip()
            if stripped == "<init>":
                in_init = True
                continue
            if in_init and stripped == "</init>":
                break
            if in_init and stripped and not stripped.startswith("<"):
                text_lines.append(stripped)
            elif in_init and stripped.startswith("<xsecinfo"):
                text_lines.append(stripped)
    if len(text_lines) < 2:
        raise ValueError(f"could not parse <init> block in {path}")
    beam = text_lines[0].split()
    proc = text_lines[1].split()
    if len(beam) < 10 or len(proc) < 4:
        raise ValueError(f"malformed LHE init block in {path}")
    declared_events = None
    total_xsec = None
    with open_text(path) as stream:
        for line in stream:
            if "<xsecinfo" in line:
                m = re.search(r'neve="(\d+)"', line)
                if m:
                    declared_events = int(m.group(1))
                m = re.search(r'totxsec="(' + FLOAT_RE + r')"', line)
                if m:
                    total_xsec = float(m.group(1).replace("D", "E"))
                break
    return LHEInit(
        incoming_pdg1=int(beam[0]),
        incoming_pdg2=int(beam[1]),
        beam_energy1_GeV=float(beam[2].replace("D", "E")),
        beam_energy2_GeV=float(beam[3].replace("D", "E")),
        cross_section_pb=float(proc[0].replace("D", "E")),
        cross_section_error_pb=float(proc[1].replace("D", "E")),
        max_weight=float(proc[2].replace("D", "E")),
        process_id=int(proc[3]),
        declared_events=declared_events,
        total_cross_section_pb=total_xsec,
    )


def iter_lhe_event_blocks(path: Path) -> Iterator[list[str]]:
    with open_text(path) as stream:
        block: list[str] | None = None
        for line in stream:
            if line.lstrip().startswith("<event"):
                block = [line]
                continue
            if block is not None:
                block.append(line)
                if line.lstrip().startswith("</event"):
                    yield block
                    block = None


def final_state_pdgs_from_block(block: Sequence[str]) -> list[int]:
    final: list[int] = []
    header_seen = False
    for raw in block:
        stripped = raw.strip()
        if not stripped or stripped.startswith("<") or stripped.startswith("#"):
            continue
        fields = stripped.split()
        if not header_seen:
            header_seen = True
            continue
        if len(fields) < 10:
            continue
        try:
            pdg = int(fields[0])
            status = int(fields[1])
        except ValueError:
            continue
        if status == 1:
            final.append(pdg)
    return final


def expected_final_state(decay_channel: str) -> list[int]:
    if decay_channel == "epmum":
        return [5, -11, 12, -5, 13, -14]
    if decay_channel == "mupem":
        return [5, -13, 14, -5, 11, -12]
    raise ValueError(f"unsupported decay channel: {decay_channel}")


def parse_process_integration(log_path: Path, process: str, unit: str) -> IntegrationResult | None:
    lines = log_path.read_text(errors="replace").splitlines()
    start_marker = f"Starting integration for process '{process}'"
    in_section = False
    in_table = False
    candidates: list[IntegrationResult] = []
    row_re = re.compile(rf"^\s*(\d+)\s+(\d+)\s+({FLOAT_RE})\s+({FLOAT_RE})(?:\s|$)")
    for line in lines:
        if start_marker in line:
            in_section = True
            in_table = False
            candidates = []
            continue
        if not in_section:
            continue
        lower = line.lower()
        if f"integral[{unit.lower()}]" in lower and f"error[{unit.lower()}]" in lower:
            in_table = True
            continue
        if not in_table:
            if "starting integration for process" in lower:
                break
            continue
        if (
            "time estimate for generating" in lower
            or "starting integration for process" in lower
            or "unstable particle" in lower
            or "starting simulation" in lower
        ):
            break
        cleaned = line.strip().strip("|").strip()
        match = row_re.match(cleaned)
        if not match:
            continue
        value = float(match.group(3).replace("D", "E"))
        error = float(match.group(4).replace("D", "E"))
        if value >= 0.0 and error >= 0.0:
            candidates.append(IntegrationResult(value, error, cleaned))
    return candidates[-1] if candidates else None


def parse_preset_top_widths(log_path: Path) -> dict[str, float]:
    result: dict[str, float] = {}
    lines = log_path.read_text(errors="replace").splitlines()
    current: str | None = None
    for line in lines:
        m = re.search(r"Unstable particle\s+(tbar|t):", line)
        if m:
            current = m.group(1)
            continue
        if current and "(preset)" in line:
            m = re.search(r"=\s*(" + FLOAT_RE + r")\s*GeV", line)
            if m:
                result[current] = float(m.group(1).replace("D", "E"))
                current = None
    return result


def parse_excess_weight(log_path: Path) -> tuple[int, float, float]:
    text = log_path.read_text(errors="replace")
    count = 0
    fraction_percent = 0.0
    maximum = 0.0
    m = re.search(
        r"Encountered events with excess weight:\s*(\d+)\s*events\s*\(\s*(" + FLOAT_RE + r")\s*%\)",
        text,
    )
    if m:
        count = int(m.group(1))
        fraction_percent = float(m.group(2).replace("D", "E"))
    m = re.search(r"Maximum excess weight\s*=\s*(" + FLOAT_RE + r")", text)
    if m:
        maximum = float(m.group(1).replace("D", "E"))
    return count, fraction_percent, maximum


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open() as stream:
        payload = json.load(stream)
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object in {path}")
    return payload


def inverse_variance_mean(values: Sequence[tuple[float, float]]) -> tuple[float, float, float]:
    clean = [(v, e) for v, e in values if math.isfinite(v) and math.isfinite(e) and e > 0]
    if not clean:
        raise ValueError("no finite positive-error measurements")
    weights = [1.0 / (e * e) for _, e in clean]
    total = sum(weights)
    mean = sum(v * w for (v, _), w in zip(clean, weights)) / total
    error = math.sqrt(1.0 / total)
    if len(clean) > 1:
        variance = sum((v - mean) ** 2 for v, _ in clean) / (len(clean) - 1)
        scatter = math.sqrt(max(0.0, variance))
    else:
        scatter = 0.0
    return mean, error, scatter


def remove_tree(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink(missing_ok=True)
    elif path.exists():
        shutil.rmtree(path)
