#!/usr/bin/env python3

from pathlib import Path
import sys


root = Path(sys.argv[1])

template_path = root / "run_G_template_v1.sh"

if not template_path.is_file():
    raise SystemExit(
        f"ERROR: missing template: {template_path}"
    )

base = template_path.read_text()


BASE_MODE = "F5_S0"
BASE_SEED = "1740114216"
BASE_SCHEDULE = '5:100000:"gw",3:200000:""'


families = {
    "G1": '5:50000:"gw",5:100000:""',
    "G2": '5:50000:"gw",3:200000:""',
}

seeds = {
    "S0": 1740114216,
    "S1": 1751949026,
    "S2": 1885084773,
}


def replace_exact(text, old, new, count, label):
    n = text.count(old)

    if n != count:
        raise RuntimeError(
            f"{label}: expected {count} occurrences "
            f"of {old!r}, found {n}"
        )

    return text.replace(old, new)


manifest = []


for family, schedule in families.items():

    for seed_name, seed in seeds.items():

        mode = f"{family}_{seed_name}"

        text = base

        # ----------------------------------------------------------
        # Mode replacement.
        # ----------------------------------------------------------

        nmode = text.count(BASE_MODE)

        if nmode < 2:
            raise RuntimeError(
                f"{mode}: unexpectedly few mode occurrences: "
                f"{nmode}"
            )

        text = text.replace(
            BASE_MODE,
            mode,
        )

        # ----------------------------------------------------------
        # Rename diagnostic banner/namespace.
        # ----------------------------------------------------------

        text = text.replace(
            "PHASE11_FREEZE_AFTER_N_V1_",
            "PHASE11_CANDIDATE_A_STRESS_V1_",
        )

        text = replace_exact(
            text,
            '"diagnostic": "phase11_freeze_after_n_v1",',
            '"diagnostic": "phase11_candidate_A_stress_v1",',
            1,
            f"{mode} diagnostic",
        )

        text = replace_exact(
            text,
            f'"worker_version": "freeze_after_n_v1/{mode}",',
            f'"worker_version": "candidate_A_stress_v1/{mode}",',
            1,
            f"{mode} worker_version",
        )

        # ----------------------------------------------------------
        # Seed.
        # ----------------------------------------------------------

        nseed = text.count(BASE_SEED)

        if nseed < 2:
            raise RuntimeError(
                f"{mode}: unexpectedly few seed occurrences: "
                f"{nseed}"
            )

        text = text.replace(
            BASE_SEED,
            str(seed),
        )

        # ----------------------------------------------------------
        # Integration schedule.
        #
        # The current worker contains the same schedule in:
        #   shell ITERATIONS,
        #   VAMP2 branch,
        #   unused legacy-VAMP branch.
        # ----------------------------------------------------------

        nsched = text.count(BASE_SCHEDULE)

        if nsched != 3:
            raise RuntimeError(
                f"{mode}: expected 3 schedule occurrences, "
                f"found {nsched}"
            )

        text = text.replace(
            BASE_SCHEDULE,
            schedule,
        )

        # ----------------------------------------------------------
        # Save worker.
        # ----------------------------------------------------------

        worker = root / f"run_{mode}.sh"

        worker.write_text(text)
        worker.chmod(0o755)

        manifest.append(
            (
                mode,
                family,
                seed_name,
                seed,
                schedule,
                worker,
            )
        )


manifest_path = root / "G_SERIES_WORKER_MANIFEST.tsv"

with manifest_path.open("w", encoding="utf-8") as f:

    f.write(
        "mode\tfamily\tseed_name\tseed\t"
        "iterations\tworker\n"
    )

    for (
        mode,
        family,
        seed_name,
        seed,
        schedule,
        worker,
    ) in manifest:

        f.write(
            f"{mode}\t"
            f"{family}\t"
            f"{seed_name}\t"
            f"{seed}\t"
            f"{schedule}\t"
            f"{worker}\n"
        )


print(f"CREATED_WORKERS={len(manifest)}")
print(f"MANIFEST={manifest_path}")

for row in manifest:
    print(
        f"{row[0]} "
        f"seed={row[3]} "
        f"iterations={row[4]}"
    )
