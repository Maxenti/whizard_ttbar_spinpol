from pathlib import Path
import sys

diag = Path(sys.argv[1])
out = Path(sys.argv[2])

base = diag / "run_d1d2_integration_v4.sh"

if not base.is_file():
    raise SystemExit(f"ERROR: missing base worker: {base}")

source = base.read_text()

FULL = '10:100000:"gw",2:200000:""'

controls = {
    "D2_vamp_tao_np1": {
        "base_mode": "D2_vamp_np1",
        "method": "vamp",
        "rng": "tao",
        "seed": 1740114216,
        "iterations": FULL,
    },
    "D4_vamp2_rngstream_gonly_np1": {
        "base_mode": "D1_vamp2_np1",
        "method": "vamp2",
        "rng": "rng_stream",
        "seed": 1740114216,
        "iterations": '10:100000:"g",2:200000:""',
    },
    "D5_vamp2_rngstream_stopw5_np1": {
        "base_mode": "D1_vamp2_np1",
        "method": "vamp2",
        "rng": "rng_stream",
        "seed": 1740114216,
        "iterations": '5:100000:"gw",5:100000:"g",2:200000:""',
    },
    "D6_vamp2_rngstream_seedA1_np1": {
        "base_mode": "D1_vamp2_np1",
        "method": "vamp2",
        "rng": "rng_stream",
        "seed": 1751949026,
        "iterations": FULL,
    },
    "D7_vamp2_rngstream_seedA2_np1": {
        "base_mode": "D1_vamp2_np1",
        "method": "vamp2",
        "rng": "rng_stream",
        "seed": 1885084773,
        "iterations": FULL,
    },
}


def replace_one(text, old, new, description):
    n = text.count(old)
    if n != 1:
        raise RuntimeError(
            f"{description}: expected exactly 1 occurrence of {old!r}, found {n}"
        )
    return text.replace(old, new, 1)


for mode, cfg in controls.items():
    text = source

    # Dedicated mode identity.
    base_mode = cfg["base_mode"]
    count = text.count(base_mode)
    if count < 2:
        raise RuntimeError(
            f"{mode}: too few occurrences of base mode {base_mode}: {count}"
        )
    text = text.replace(base_mode, mode)

    # Worker banner/version.
    text = replace_one(
        text,
        "PHASE11_B0_ADAPTATION_DIAGNOSTIC_V4",
        f"PHASE11_B0_ADAPTATION_DIAGNOSTIC_{mode.upper()}",
        f"{mode} banner",
    )

    text = replace_one(
        text,
        '"worker_version": "v4",',
        f'"worker_version": "parallel_controls_v1/{mode}",',
        f"{mode} worker version",
    )

    # Seed. Dedicated workers only run their named mode, so replacing the
    # canonical diagnostic seed everywhere keeps shell/config/metadata aligned.
    old_seed = "1740114216"
    new_seed = str(cfg["seed"])
    if cfg["seed"] != 1740114216:
        nseed = text.count(old_seed)
        if nseed < 3:
            raise RuntimeError(
                f"{mode}: unexpectedly few seed occurrences: {nseed}"
            )
        text = text.replace(old_seed, new_seed)

    # Schedule: shell variable + both integration-card branches.
    old_schedule = FULL
    new_schedule = cfg["iterations"]

    if new_schedule != old_schedule:
        nsched = text.count(old_schedule)
        if nsched != 3:
            raise RuntimeError(
                f"{mode}: expected 3 full-schedule occurrences, found {nsched}"
            )
        text = text.replace(old_schedule, new_schedule)

    # RNG handling.
    #
    # Base worker has two Sindarin occurrences of rng_stream:
    # first = VAMP2 branch
    # second = VAMP branch.
    if cfg["rng"] == "tao":
        needle = '$rng_method = "rng_stream"'
        positions = []
        start = 0

        while True:
            i = text.find(needle, start)
            if i < 0:
                break
            positions.append(i)
            start = i + len(needle)

        if len(positions) != 2:
            raise RuntimeError(
                f"{mode}: expected 2 rng_stream Sindarin lines, "
                f"found {len(positions)}"
            )

        target = 0 if cfg["method"] == "vamp2" else 1
        i = positions[target]

        text = (
            text[:i]
            + '$rng_method = "tao"'
            + text[i + len(needle):]
        )

        # Metadata is one fixed field in this dedicated worker.
        text = replace_one(
            text,
            '"rng_method": "rng_stream",',
            '"rng_method": "tao",',
            f"{mode} metadata RNG",
        )

    path = out / f"run_{mode}.sh"
    path.write_text(text)
    path.chmod(0o755)

    print(
        f"{mode}\t"
        f"method={cfg['method']}\t"
        f"rng={cfg['rng']}\t"
        f"seed={cfg['seed']}\t"
        f"iterations={cfg['iterations']}\t"
        f"worker={path}"
    )
