"""YAML/JSON helpers used by Package 2 validators.

PyYAML is used when available. On lxplus/Key4HEP Python environments where
PyYAML is not installed, fall back to the project-local strict YAML subset
parser installed by Package 1 and bundled here for standalone package QA.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:  # Prefer PyYAML when the runtime provides it.
    import yaml  # type: ignore
except Exception:  # pragma: no cover - depends on external environment.
    yaml = None  # type: ignore[assignment]


def load_yaml(path: Path) -> dict[str, Any]:
    if yaml is not None:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    else:
        from ttbar_spinpol.contracts.yaml_compat import load_path

        value = load_path(path)
    if not isinstance(value, dict):
        raise ValueError(f"YAML top-level value is not a mapping: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
