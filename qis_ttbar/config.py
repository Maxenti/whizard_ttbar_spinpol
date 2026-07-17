from __future__ import annotations

import dataclasses
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import yaml

from .exceptions import ConfigurationError


@dataclasses.dataclass(frozen=True)
class FrameworkConfig:
    path: Path
    data: dict[str, Any]
    sha256: str

    @property
    def level(self) -> str:
        return str(self.data.get("level", "")).upper()

    @property
    def output_root(self) -> Path:
        value = self.data.get("output_root")
        if value is None:
            value = self.data.get("campaign", {}).get("output_root")
        if not value:
            raise ConfigurationError("configuration has no output_root")
        return Path(str(value)).expanduser()

    def section(self, name: str) -> Mapping[str, Any]:
        value = self.data.get(name, {})
        if not isinstance(value, Mapping):
            raise ConfigurationError(f"configuration section {name!r} must be a mapping")
        return value


def load_config(path: str | Path) -> FrameworkConfig:
    path = Path(path).expanduser().resolve()
    raw = path.read_bytes()
    parsed = yaml.safe_load(raw) or {}
    if not isinstance(parsed, dict):
        raise ConfigurationError(f"top-level YAML must be a mapping: {path}")
    config = FrameworkConfig(path=path, data=parsed, sha256=hashlib.sha256(raw).hexdigest())
    validate_config(config)
    return config


def validate_config(config: FrameworkConfig) -> None:
    if int(config.data.get("schema_version", 0)) != 1:
        raise ConfigurationError("schema_version must be 1")
    if config.level not in {"A", "B", "C"}:
        raise ConfigurationError("level must be A, B, or C")
    if config.level == "A":
        physics = config.section("physics")
        order = list(physics.get("basis_order", []))
        if sorted(order) != ["k", "n", "r"]:
            raise ConfigurationError("basis_order must contain k, r, n exactly once")
        stats = config.section("statistics")
        for key in ("bootstrap_replicas_test", "bootstrap_replicas_production"):
            if int(stats.get(key, 0)) < 1:
                raise ConfigurationError(f"{key} must be positive")


def dump_resolved_config(config: FrameworkConfig, path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": str(config.path),
        "sha256": config.sha256,
        "resolved": config.data,
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
