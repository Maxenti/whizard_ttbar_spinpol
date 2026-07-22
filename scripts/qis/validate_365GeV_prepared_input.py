#!/usr/bin/env python3
"""Independently validate a prepared 365 GeV SINDARIN before WHIZARD runs."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

import yaml


def load_prepare_module(repo: Path):
    path = repo / "scripts/qis/prepare_365GeV_smoke.py"
    spec = importlib.util.spec_from_file_location("prepare_365_contract", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def resolve(repo: Path, path: Path) -> Path:
    return path.expanduser().resolve() if path.is_absolute() else (repo / path).resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--pilot-config",
        type=Path,
        default=Path("configs/qis/paper_spin_365GeV_pilot.yaml"),
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    repo = args.repo_root.expanduser().resolve()
    config_path = resolve(repo, args.pilot_config)
    input_path = resolve(repo, args.input)
    config: dict[str, Any] = yaml.safe_load(config_path.read_text())
    module = load_prepare_module(repo)
    checks = module.prepared_contract_checks(input_path.read_text(), config)
    status = "pass" if all(item["status"] == "pass" for item in checks) else "fail"
    payload = {
        "schema_version": 1,
        "input": str(input_path),
        "pilot_config": str(config_path),
        "checks": checks,
        "status": status,
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        output = resolve(repo, args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered)
    print(rendered, end="")
    return 1 if args.strict and status != "pass" else 0


if __name__ == "__main__":
    raise SystemExit(main())
