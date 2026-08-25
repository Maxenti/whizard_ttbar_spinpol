#!/usr/bin/env python3

import argparse
import csv
import hashlib
import re
from collections import defaultdict
from pathlib import Path


EXPECTED_COMPONENTS = (
    "S0_C",
    "S0_D",
    "S1_B",
    "S2_B",
)

EXPECTED_FILES_PER_COMPONENT = 32
EXPECTED_EVENTS_PER_FILE = 1000
EXPECTED_EVENTS_PER_COMPONENT = 32000

EVENT_RE = re.compile(
    r"<event\b[^>]*>.*?</event>",
    flags=re.S,
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        for block in iter(
            lambda: f.read(8 * 1024 * 1024),
            b"",
        ):
            h.update(block)

    return h.hexdigest()


def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument(
        "--manifest",
        required=True,
        type=Path,
    )

    p.add_argument(
        "--outdir",
        required=True,
        type=Path,
    )

    return p.parse_args()


def main():

    a = parse_args()

    if a.outdir.exists():
        raise SystemExit(
            f"ERROR: refusing to overwrite {a.outdir}"
        )

    with a.manifest.open(
        newline=""
    ) as f:
        rows = list(
            csv.DictReader(
                f,
                delimiter="\t",
            )
        )

    required = {
        "component",
        "mode",
        "grid",
        "lhe_path",
    }

    if not rows:
        raise SystemExit(
            "ERROR: empty component manifest"
        )

    if not required.issubset(rows[0]):
        raise SystemExit(
            "ERROR: manifest missing required columns"
        )

    grouped = defaultdict(list)

    for row in rows:

        component = row["component"]

        if component not in EXPECTED_COMPONENTS:
            raise SystemExit(
                f"ERROR: invalid component={component}"
            )

        grouped[component].append(row)

    if set(grouped) != set(EXPECTED_COMPONENTS):
        raise SystemExit(
            "ERROR: component set mismatch"
        )

    for component in EXPECTED_COMPONENTS:

        if (
            len(grouped[component])
            != EXPECTED_FILES_PER_COMPONENT
        ):
            raise SystemExit(
                f"ERROR: {component}: files="
                f"{len(grouped[component])}, "
                f"expected={EXPECTED_FILES_PER_COMPONENT}"
            )

    a.outdir.mkdir(
        parents=True,
        exist_ok=False,
    )

    provenance = []

    for component in EXPECTED_COMPONENTS:

        output = (
            a.outdir
            / f"{component}.lhe"
        )

        header = None
        footer = None
        total_events = 0

        with output.open(
            "w"
        ) as out:

            for index, row in enumerate(
                grouped[component]
            ):

                path = Path(
                    row["lhe_path"]
                ).resolve()

                if not path.is_file():
                    raise SystemExit(
                        f"ERROR: missing LHE {path}"
                    )

                text = path.read_text(
                    errors="strict"
                )

                events = list(
                    EVENT_RE.finditer(text)
                )

                if (
                    len(events)
                    != EXPECTED_EVENTS_PER_FILE
                ):
                    raise SystemExit(
                        f"ERROR: {path}: events="
                        f"{len(events)}, expected="
                        f"{EXPECTED_EVENTS_PER_FILE}"
                    )

                if index == 0:

                    header = text[
                        :events[0].start()
                    ]

                    footer = text[
                        events[-1].end():
                    ]

                    out.write(header)

                for match in events:
                    out.write(
                        match.group(0)
                    )
                    out.write("\n")

                total_events += len(events)

                provenance.append({
                    "component": component,
                    "component_file_index":
                        index + 1,
                    "mode": row["mode"],
                    "grid": row["grid"],
                    "input_path": str(path),
                    "input_sha256":
                        sha256_file(path),
                    "input_events":
                        len(events),
                })

            if footer is None:
                raise SystemExit(
                    f"ERROR: no footer for {component}"
                )

            out.write(footer)

        if (
            total_events
            != EXPECTED_EVENTS_PER_COMPONENT
        ):
            raise SystemExit(
                f"ERROR: {component}: total_events="
                f"{total_events}"
            )

        print(
            f"{component}: "
            f"files={len(grouped[component])} "
            f"events={total_events} "
            f"sha256={sha256_file(output)}"
        )

    prov_path = (
        a.outdir
        / "MERGE_INPUT_PROVENANCE.tsv"
    )

    with prov_path.open(
        "w",
        newline="",
    ) as f:

        fields = [
            "component",
            "component_file_index",
            "mode",
            "grid",
            "input_path",
            "input_sha256",
            "input_events",
        ]

        w = csv.DictWriter(
            f,
            fieldnames=fields,
            delimiter="\t",
            lineterminator="\n",
        )

        w.writeheader()
        w.writerows(provenance)

    manifest = (
        a.outdir
        / "MERGED_COMPONENTS.sha256"
    )

    with manifest.open("w") as f:

        for component in EXPECTED_COMPONENTS:

            path = (
                a.outdir
                / f"{component}.lhe"
            )

            f.write(
                f"{sha256_file(path)}  {path}\n"
            )

    print(
        "FINAL_HOLDOUT_LHE_MERGE=PASS"
    )


if __name__ == "__main__":
    main()
