#!/usr/bin/env python3
"""Collect or merge HepMC3 shower shards using pyhepmc."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


def configured_root(path: Path) -> Path:
    payload: dict[str, Any] = yaml.safe_load(path.read_text()) or {}
    return Path(str(payload["campaign"]["output_root"])) / "shower"


def merge_hepmc(inputs: list[Path], output: Path) -> int:
    if not inputs:
        raise ValueError(f"no input HepMC3 files for {output.stem}")
    try:
        import pyhepmc
    except ImportError as exc:
        raise RuntimeError("pyhepmc is required to merge HepMC3 files") from exc
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.partial")
    temporary.unlink(missing_ok=True)
    events = 0
    try:
        with pyhepmc.open(temporary, "w") as writer:
            for source in inputs:
                with pyhepmc.open(source) as reader:
                    for event in reader:
                        event.event_number = events
                        writer.write(event)
                        events += 1
        temporary.replace(output)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return events


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/qis/level_a_500GeV_ISR_sc_v1.yaml"))
    parser.add_argument("--root", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    root = args.root or configured_root(args.config)
    records: list[dict[str, object]] = []
    for sample_dir in sorted((root / "hepmc3").glob("*")):
        if not sample_dir.is_dir():
            continue
        inputs = sorted(sample_dir.glob("*.hepmc3"))
        output = root / "hepmc3_merged" / f"{sample_dir.name}.hepmc3"
        if output.exists() and not args.overwrite:
            raise FileExistsError(f"merged output exists: {output}; use --overwrite")
        events = merge_hepmc(inputs, output)
        records.append({"sample_id": sample_dir.name, "inputs": [str(x) for x in inputs], "output": str(output), "events": events})
        print(f"WROTE {output} events={events}")
    if not records:
        raise RuntimeError(f"no sample directories found under {root / 'hepmc3'}")
    manifest = root / "manifests/shower_collection.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(records, indent=2, sort_keys=True) + "\n")
    print(f"Wrote {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
