from pathlib import Path
import sys

root = Path(sys.argv[1])

template = root / "run_freeze_template_v1.sh"

if not template.is_file():
    raise SystemExit(f"ERROR: missing template: {template}")

source = template.read_text()

BASE_MODE = "D6_vamp2_rngstream_seedA1_np1"
BASE_SEED = "1751949026"
BASE_SCHEDULE = '10:100000:"gw",2:200000:""'

BASE_BANNER = (
    "PHASE11_B0_ADAPTATION_DIAGNOSTIC_"
    "D6_VAMP2_RNGSTREAM_SEEDA1_NP1"
)

families = {
    "F5": '5:100000:"gw",3:200000:""',
    "F6": '6:100000:"gw",3:200000:""',
    "F7": '7:100000:"gw",3:200000:""',
}

seeds = {
    "S0": 1740114216,
    "S1": 1751949026,
    "S2": 1885084773,
}


def replace_exact(text, old, new, expected, label):
    n = text.count(old)

    if n != expected:
        raise RuntimeError(
            f"{label}: expected {expected} occurrences of "
            f"{old!r}, found {n}"
        )

    return text.replace(old, new)


manifest = []

for family, schedule in families.items():
    for seed_name, seed in seeds.items():

        mode = f"{family}_{seed_name}"

        text = source

        # ----------------------------------------------------------
        # Dedicated mode.
        # ----------------------------------------------------------

        nmode = text.count(BASE_MODE)

        if nmode < 2:
            raise RuntimeError(
                f"{mode}: expected >=2 BASE_MODE occurrences, "
                f"found {nmode}"
            )

        text = text.replace(BASE_MODE, mode)

        # ----------------------------------------------------------
        # Banner.
        # ----------------------------------------------------------

        banner = (
            "PHASE11_FREEZE_AFTER_N_V1_"
            + mode.upper()
        )

        text = replace_exact(
            text,
            BASE_BANNER,
            banner,
            1,
            f"{mode} banner",
        )

        # ----------------------------------------------------------
        # Diagnostic namespace.
        # ----------------------------------------------------------

        text = replace_exact(
            text,
            '"diagnostic": "phase11_b0_adaptation_failure_v1",',
            '"diagnostic": "phase11_freeze_after_n_v1",',
            1,
            f"{mode} diagnostic",
        )

        # ----------------------------------------------------------
        # Worker version.
        #
        # BASE_MODE was already replaced, so the current literal is
        # parallel_controls_v1/<new mode>.
        # ----------------------------------------------------------

        text = replace_exact(
            text,
            f'"worker_version": "parallel_controls_v1/{mode}",',
            f'"worker_version": "freeze_after_n_v1/{mode}",',
            1,
            f"{mode} worker version",
        )

        # ----------------------------------------------------------
        # Seed.
        # Replace all occurrences in this dedicated worker.
        # ----------------------------------------------------------

        nseed = text.count(BASE_SEED)

        if nseed < 2:
            raise RuntimeError(
                f"{mode}: unexpectedly few base-seed occurrences: "
                f"{nseed}"
            )

        text = text.replace(
            BASE_SEED,
            str(seed),
        )

        # ----------------------------------------------------------
        # Schedule.
        #
        # Expected locations:
        #   shell ITERATIONS
        #   VAMP2 branch
        #   unused VAMP branch
        # ----------------------------------------------------------

        nsched = text.count(BASE_SCHEDULE)

        if nsched != 3:
            raise RuntimeError(
                f"{mode}: expected exactly 3 base-schedule "
                f"occurrences, found {nsched}"
            )

        text = text.replace(
            BASE_SCHEDULE,
            schedule,
        )

        # ----------------------------------------------------------
        # Save.
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


manifest_path = root / "F_SERIES_WORKER_MANIFEST.tsv"

with manifest_path.open("w") as f:
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
