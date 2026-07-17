from __future__ import annotations

import csv
import dataclasses
from pathlib import Path
from typing import Iterable

from ..exceptions import ConfigurationError


@dataclasses.dataclass(frozen=True)
class SampleRecord:
    campaign_id: str
    sample_id: str
    initial_state: str
    decay_channel: str
    polarization: str
    sqrt_s_GeV: float
    expected_events: int
    generated_events: int
    inclusive_cross_section_fb: float
    exclusive_cross_section_fb: float
    forced_decay_weight: float
    merged_final_lhe_path: Path
    status: str


def _number(row: dict[str, str], key: str, kind: type, default: object = 0) -> object:
    value = row.get(key, "")
    return kind(value) if value not in ("", None) else default


def load_sample_manifest(path: str | Path, *, require_success: bool = True) -> list[SampleRecord]:
    path = Path(path).expanduser()
    if not path.is_file():
        raise FileNotFoundError(path)
    records: list[SampleRecord] = []
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream):
            record = SampleRecord(
                campaign_id=row["campaign_id"], sample_id=row["sample_id"],
                initial_state=row["initial_state"], decay_channel=row["decay_channel"],
                polarization=row["polarization"], sqrt_s_GeV=float(row["sqrt_s_GeV"]),
                expected_events=int(_number(row, "expected_events", int, 0)),
                generated_events=int(_number(row, "generated_events", int, 0)),
                inclusive_cross_section_fb=float(_number(row, "inclusive_cross_section_fb", float, 0.0)),
                exclusive_cross_section_fb=float(_number(row, "exclusive_cross_section_fb", float, 0.0)),
                forced_decay_weight=float(_number(row, "forced_decay_weight", float, 1.0)),
                merged_final_lhe_path=Path(row.get("merged_final_lhe_path", "")),
                status=row.get("status", "unknown"),
            )
            if require_success and record.status != "success":
                continue
            records.append(record)
    if not records:
        raise ConfigurationError(f"no usable samples found in {path}")
    ids = [record.sample_id for record in records]
    if len(ids) != len(set(ids)):
        raise ConfigurationError(f"duplicate sample_id values in {path}")
    return records


def select_records(records: Iterable[SampleRecord], patterns: Iterable[str]) -> list[SampleRecord]:
    from fnmatch import fnmatch
    patterns = list(patterns)
    if not patterns:
        return list(records)
    return [record for record in records if any(fnmatch(record.sample_id, p) for p in patterns)]
