#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SEED_RE = re.compile(r"(?m)^\s*seed\s*=\s*(\d+)\s*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the Phase 10A direct-full6f WHIZARD seed contract."
        )
    )
    parser.add_argument("--generated-root", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    generated_root = args.generated_root.resolve()
    output_json = args.output_json.resolve()

    process_cards = sorted(generated_root.glob("**/process.sin"))
    process_cards = [
        path
        for path in process_cards
        if "/common/" not in path.as_posix()
    ]

    checks: list[dict[str, object]] = []
    failures: list[dict[str, object]] = []

    for process_card in process_cards:
        process_dir = process_card.parent
        context_path = process_dir / "render_context.json"
        integration_path = process_dir / "common" / "integration.inc"
        event_output_path = process_dir / "common" / "event_output.inc"

        record: dict[str, object] = {
            "process_card": str(process_card),
            "render_context": str(context_path),
            "integration_include": str(integration_path),
            "event_output_include": str(event_output_path),
            "process_card_exists": process_card.is_file(),
            "render_context_exists": context_path.is_file(),
            "integration_include_exists": integration_path.is_file(),
            "event_output_include_exists": event_output_path.is_file(),
        }

        local_failures: list[str] = []

        required_paths = {
            "process_card": process_card,
            "render_context": context_path,
            "integration_include": integration_path,
            "event_output_include": event_output_path,
        }

        for name, path in required_paths.items():
            if not path.is_file():
                local_failures.append(f"missing_{name}")

        if not local_failures:
            process_text = process_card.read_text(
                encoding="utf-8",
                errors="replace",
            )
            integration_text = integration_path.read_text(
                encoding="utf-8",
                errors="replace",
            )
            context = json.loads(
                context_path.read_text(encoding="utf-8")
            )

            expected_seed = int(context["generator_seed"])
            seed_matches = SEED_RE.findall(integration_text)

            record["expected_generator_seed"] = expected_seed
            record["rendered_seed_matches"] = [
                int(value)
                for value in seed_matches
            ]
            record["seed_assignment_count"] = len(seed_matches)
            record["integrate_count"] = integration_text.count(
                "integrate ("
            )

            if len(seed_matches) != 1:
                local_failures.append(
                    "seed_assignment_count_not_one"
                )
            else:
                rendered_seed = int(seed_matches[0])
                record["rendered_seed"] = rendered_seed
                record["seed_matches_render_context"] = (
                    rendered_seed == expected_seed
                )

                if rendered_seed != expected_seed:
                    local_failures.append(
                        "seed_does_not_match_render_context"
                    )

            if "integrate (" not in integration_text:
                local_failures.append("missing_integrate")
                record["seed_precedes_integrate"] = False
            elif len(seed_matches) == 1:
                seed_position = integration_text.index(
                    seed_matches[0]
                )
                integrate_position = integration_text.index(
                    "integrate ("
                )
                record["seed_position"] = seed_position
                record["integrate_position"] = integrate_position
                record["seed_precedes_integrate"] = (
                    seed_position < integrate_position
                )

                if seed_position >= integrate_position:
                    local_failures.append(
                        "seed_does_not_precede_integrate"
                    )

            integration_marker = "common/integration.inc"
            event_marker = "common/event_output.inc"

            record["process_includes_integration"] = (
                integration_marker in process_text
            )
            record["process_includes_event_output"] = (
                event_marker in process_text
            )

            if integration_marker not in process_text:
                local_failures.append(
                    "process_missing_integration_include"
                )

            if event_marker not in process_text:
                local_failures.append(
                    "process_missing_event_output_include"
                )

            if (
                integration_marker in process_text
                and event_marker in process_text
            ):
                record["integration_include_precedes_event_output"] = (
                    process_text.index(integration_marker)
                    < process_text.index(event_marker)
                )

                if not record[
                    "integration_include_precedes_event_output"
                ]:
                    local_failures.append(
                        "integration_include_after_event_output"
                    )

        record["failures"] = local_failures
        record["passed"] = not local_failures

        checks.append(record)

        if local_failures:
            failures.append(record)

    if not process_cards:
        failures.append({
            "failure": "no_process_cards_found",
            "generated_root": str(generated_root),
        })

    status = "PASS" if not failures else "FAIL"

    payload = {
        "schema_version": 1,
        "status": status,
        "test": "Phase 10A direct-full6f WHIZARD seed contract",
        "generated_root": str(generated_root),
        "n_process_cards": len(process_cards),
        "n_failures": len(failures),
        "checks": checks,
        "failures": failures,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"PHASE10A_FULL6F_SEED_CONTRACT_STATUS={status}")
    print(f"N_PROCESS_CARDS={len(process_cards)}")
    print(f"N_FAILURES={len(failures)}")
    print(f"WROTE={output_json}")

    if failures:
        for failure in failures[:20]:
            print(
                "FAILURE="
                + json.dumps(failure, sort_keys=True)
            )

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
