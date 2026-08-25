#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


if len(sys.argv) != 5:
    raise SystemExit(
        "usage: run_relaxed_canonicalizer.py "
        "CANONICALIZER INPUT OUTPUT SUMMARY"
    )


module_path = Path(sys.argv[1]).resolve()
input_path = Path(sys.argv[2]).resolve()
output_path = Path(sys.argv[3]).resolve()
summary_path = Path(sys.argv[4]).resolve()


module_name = "phase11e_canonicalizer_relaxed"

spec = importlib.util.spec_from_file_location(
    module_name,
    module_path,
)

if spec is None or spec.loader is None:
    raise SystemExit(
        f"ERROR: cannot import {module_path}"
    )

module = importlib.util.module_from_spec(spec)

# Required by Python dataclasses for dynamically imported modules.
sys.modules[module_name] = module

spec.loader.exec_module(module)


# DIAGNOSTIC ONLY.
#
# All canonical-v2 ISR transformations remain authoritative.
# We suppress only the final daughter-range assertion so that the resulting
# graph can be tested by the row-reordering feasibility audit.
module.validate_contiguous_daughter_ranges = (
    lambda *args, **kwargs: None
)


old_argv = sys.argv[:]

try:
    sys.argv = [
        str(module_path),
        "--input",
        str(input_path),
        "--output",
        str(output_path),
        "--summary",
        str(summary_path),
    ]

    rc = module.main()

finally:
    sys.argv = old_argv


if rc not in (None, 0):
    raise SystemExit(rc)


if not output_path.is_file():
    raise SystemExit(
        f"ERROR: output not created: {output_path}"
    )


print(
    "RELAXED_CANONICALIZATION=PASS "
    f"input={input_path} "
    f"output={output_path}"
)
