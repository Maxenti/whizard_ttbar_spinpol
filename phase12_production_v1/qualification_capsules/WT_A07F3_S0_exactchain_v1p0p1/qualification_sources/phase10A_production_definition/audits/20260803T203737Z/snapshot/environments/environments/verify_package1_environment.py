#!/usr/bin/env python3
"""Verify dependencies needed for Package 1 static checks.

This check deliberately does not require PyYAML.  The repository ships a small
YAML compatibility layer for static contract parsing in minimal lxplus Python
environments.
"""

from __future__ import annotations

import json
import platform
import sys
from ttbar_spinpol.contracts.yaml_compat import load_text

result = {
    "status": "PASS",
    "python": platform.python_version(),
    "yaml_parser": "ttbar_spinpol.contracts.yaml_compat",
}

try:
    loaded = load_text("schema:\n  status: test\n", source="inline probe")
    if loaded.get("schema", {}).get("status") != "test":
        result = {"status": "FAIL", "error": "YAML compatibility probe returned wrong value", **result}
except Exception as exc:
    result = {"status": "FAIL", "error": f"YAML compatibility probe failed: {exc}", **result}

if sys.version_info < (3, 9):
    result = {"status": "FAIL", "error": "Python >=3.9 required", **result}

print(json.dumps(result, indent=2, sort_keys=True))
raise SystemExit(0 if result["status"] == "PASS" else 1)
