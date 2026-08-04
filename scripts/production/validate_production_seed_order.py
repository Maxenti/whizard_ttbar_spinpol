#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


_TRUE_VALUES = {"1", "true", "yes", "on"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate that each production template contains exactly one "
            "WHIZARD seed assignment before every integration."
        )
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument(
        "--template-dir",
        type=Path,
        default=Path("sindarin/production"),
    )
    parser.add_argument("--output-json", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    config = args.config.resolve()
    template_dir = args.template_dir.resolve()

    checks: list[dict[str, object]] = []
    failures: list[dict[str, object]] = []

    with config.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    for row in rows:
        enabled = row.get("enabled", "").strip().lower()

        if enabled not in _TRUE_VALUES:
            continue

        sample_id = row["sample_id"].strip()
        path = template_dir / f"{sample_id}.sin.in"

        check: dict[str, object] = {
            "sample_id": sample_id,
            "template": str(path),
            "exists": path.is_file(),
        }

        if not path.is_file():
            check["passed"] = False
            check["failure"] = "missing_template"
            checks.append(check)
            failures.append(check)
            continue

        text = path.read_text(encoding="utf-8")

        seed_count = text.count("seed = __SEED__")
        integrate_count = text.count("integrate (")

        check["seed_count"] = seed_count
        check["integrate_count"] = integrate_count

        if seed_count == 1 and integrate_count >= 1:
            seed_position = text.index("seed = __SEED__")
            first_integrate_position = text.index("integrate (")

            check["seed_position"] = seed_position
            check["first_integrate_position"] = first_integrate_position
            check["seed_precedes_first_integration"] = (
                seed_position < first_integrate_position
            )
        else:
            check["seed_precedes_first_integration"] = False

        check["passed"] = (
            seed_count == 1
            and integrate_count >= 1
            and bool(check["seed_precedes_first_integration"])
        )

        if not check["passed"]:
            check["failure"] = "invalid_seed_assignment_or_order"
            failures.append(check)

        checks.append(check)

    status = "PASS" if not failures else "FAIL"

    payload = {
        "schema_version": 1,
        "status": status,
        "config": str(config),
        "template_dir": str(template_dir),
        "checks": checks,
        "failures": failures,
    }

    if args.output_json:
        output = args.output_json.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"WROTE={output}")

    print(f"PRODUCTION_SEED_ORDER_VALIDATION_STATUS={status}")
    print(f"N_CHECKS={len(checks)}")
    print(f"N_FAILURES={len(failures)}")

    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
