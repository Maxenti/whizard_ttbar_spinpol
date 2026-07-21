#!/usr/bin/env python3
"""Preflight dependencies, baseline inputs, configuration, and write safety."""

from __future__ import annotations

import argparse
import importlib
import json
import os
from pathlib import Path

from qis_ttbar.paper_spin.io import discover_ntuples, load_config


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qualification-root", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    qualification = Path(args.qualification_root).resolve()
    output = Path(args.output_root).resolve()
    checks = []

    for module_name in ["numpy", "pandas", "scipy", "yaml", "matplotlib", "pyarrow"]:
        try:
            module = importlib.import_module(module_name)
        except Exception as error:
            checks.append({"check": f"dependency:{module_name}", "status": "fail", "message": str(error)})
        else:
            checks.append({"check": f"dependency:{module_name}", "status": "pass", "version": getattr(module, "__version__", "unknown")})

    try:
        config = load_config(args.config)
    except Exception as error:
        checks.append({"check": "config", "status": "fail", "message": str(error)})
    else:
        checks.append({"check": "config", "status": "pass", "convention": config["convention"]["name"]})

    try:
        descriptors = discover_ntuples(qualification)
    except Exception as error:
        checks.append({"check": "ntuples", "status": "fail", "message": str(error)})
    else:
        checks.append({"check": "ntuples", "status": "pass", "samples": len(descriptors)})

    inside = output == qualification or output.is_relative_to(qualification)
    checks.append(
        {
            "check": "additive_output_path",
            "status": "fail" if inside else "pass",
            "qualification_root": str(qualification),
            "output_root": str(output),
        }
    )

    parent = output.parent
    writable = parent.exists() and os.access(parent, os.W_OK)
    checks.append({"check": "output_parent_writable", "status": "pass" if writable else "fail", "parent": str(parent)})

    status = "pass" if all(check["status"] == "pass" for check in checks) else "fail"
    payload = {"status": status, "checks": checks}
    print(json.dumps(payload, indent=2))
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
