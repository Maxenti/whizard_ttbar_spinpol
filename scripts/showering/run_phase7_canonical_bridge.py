#!/usr/bin/env python3
"""Run a WHIZARD -> canonical-v2 LHE -> PYTHIA8 -> HepMC3 Phase 7 bridge.

This runner is the scripted version of the manually validated Phase 7 bridge:

  generated process.sin + common/
  -> local bridge SINDARIN card
  -> WHIZARD low-stat LHE
  -> canonicalize_whizard_lhe_for_pythia_v2.py
  -> run_external_pythia.sh using the project qis_lhe_to_hepmc3 driver
  -> validate_phase7_showering.py
  -> runtime summary, JSON summary, SHA256SUMS

It intentionally does not modify the authoritative generated SINDARIN cards.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping


DEFAULT_CAMPAIGN_ID = "full6f_365gev_ee_ttbar_spinpol_v1"
DEFAULT_RUNTIME_VIEW = "/cvmfs/sft-nightlies.cern.ch/lcg/views/devkey-head/Fri/x86_64-el9-gcc14-opt/setup.sh"
DEFAULT_OUTPUT_BASE = Path("/eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/runs")


class BridgeError(RuntimeError):
    """Raised for a controlled bridge failure."""


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_text(
    command: list[str],
    *,
    cwd: Path,
    env: Mapping[str, str] | None = None,
) -> str:
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        env=dict(env) if env is not None else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    return completed.stdout.strip()


def run_logged(
    command: list[str],
    *,
    cwd: Path,
    log_path: Path,
    env: Mapping[str, str],
    timeout_seconds: int | None = None,
) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)

    print()
    print("=" * 100)
    print(f"RUN_LOGGED_CWD={cwd}")
    print("RUN_LOGGED_COMMAND=" + " ".join(command))
    print(f"RUN_LOGGED_LOG={log_path}")
    print("=" * 100)

    with log_path.open("w", encoding="utf-8") as log:
        proc = subprocess.Popen(
            command,
            cwd=str(cwd),
            env=dict(env),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            bufsize=1,
        )

        start = time.monotonic()
        assert proc.stdout is not None

        try:
            for line in proc.stdout:
                print(line, end="")
                log.write(line)
                log.flush()

                if timeout_seconds is not None and time.monotonic() - start > timeout_seconds:
                    proc.kill()
                    message = (
                        f"\nERROR: command timed out after {timeout_seconds} seconds\n"
                    )
                    print(message, end="")
                    log.write(message)
                    return 124

            return proc.wait()
        finally:
            if proc.poll() is None:
                proc.kill()


def count_lhe_events(path: Path) -> int:
    return sum(
        1
        for line in path.open("r", encoding="utf-8", errors="replace")
        if "<event>" in line
    )


def count_hepmc_events(path: Path) -> int:
    return sum(
        1
        for line in path.open("r", encoding="utf-8", errors="replace")
        if line.startswith("E ")
    )


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def command_exists(command: str, env: Mapping[str, str]) -> bool:
    resolved = shutil.which(command, path=env.get("PATH"))
    return resolved is not None


def ensure_pythonpath(env: dict[str, str], repo: Path) -> None:
    src = str(repo / "src")
    old = env.get("PYTHONPATH", "")
    pieces = [p for p in old.split(":") if p]
    if src not in pieces:
        pieces.insert(0, src)
    env["PYTHONPATH"] = ":".join(pieces)


def localize_card(
    *,
    source_card: Path,
    source_common: Path,
    run_dir: Path,
    events: int,
    iterations: str,
    sample_basename: str,
) -> Path:
    if not source_card.is_file():
        raise BridgeError(f"missing source card: {source_card}")
    if not source_common.is_dir():
        raise BridgeError(f"missing source common directory: {source_common}")

    run_dir.mkdir(parents=True, exist_ok=False)

    shutil.copy2(source_card, run_dir / "process.original.sin")
    shutil.copytree(source_common, run_dir / "common")

    src = run_dir / "process.original.sin"
    dst = run_dir / "process.bridge.sin"

    text = src.read_text(encoding="utf-8")

    def repl_include(match: re.Match[str]) -> str:
        return f'include("common/{Path(match.group(1)).name}")'

    text = re.sub(
        r'(?m)^\s*include\("([^"]*/common/[^"]+)"\)\s*$',
        repl_include,
        text,
    )

    kept: list[str] = []
    for line in text.splitlines():
        m = re.match(r'\s*include\("common/([^"]+)"\)\s*$', line)
        if m:
            inc = run_dir / "common" / m.group(1)
            if inc.exists() and inc.read_text(encoding="utf-8").strip() == "":
                print(f"DROPPING_EMPTY_INCLUDE={inc}")
                continue
        kept.append(line)

    dst.write_text("\n".join(kept) + "\n", encoding="utf-8")

    integration = run_dir / "common" / "integration.inc"
    if not integration.is_file():
        raise BridgeError(f"missing integration include: {integration}")

    t = integration.read_text(encoding="utf-8")
    t, n_iter = re.subn(
        r"(?m)^(\s*iterations\s*=\s*).*$",
        rf"\g<1>{iterations}",
        t,
    )
    if n_iter == 0:
        t = f"iterations = {iterations}\n" + t
    integration.write_text(t, encoding="utf-8")

    event_output = run_dir / "common" / "event_output.inc"
    if not event_output.is_file():
        raise BridgeError(f"missing event-output include: {event_output}")

    t = event_output.read_text(encoding="utf-8")
    t, n_events = re.subn(
        r"(?m)^(\s*n_events\s*=\s*).*$",
        rf"\g<1>{events}",
        t,
    )
    t, n_sample = re.subn(
        r'(?m)^(\s*\$sample\s*=\s*).*$',
        rf'\g<1>"{sample_basename}"',
        t,
    )

    if n_events == 0:
        raise BridgeError(f"could not find n_events assignment in {event_output}")
    if n_sample == 0:
        raise BridgeError(f"could not find $sample assignment in {event_output}")

    event_output.write_text(t, encoding="utf-8")

    return dst


def write_pythia_cmnd(path: Path, events: int, profile: str) -> None:
    if profile == "full_hadron":
        hadron_level = "on"
        description = "full perturbative shower plus hadronization"
    elif profile == "parton_only":
        hadron_level = "off"
        description = "perturbative shower only; hadronization disabled"
    else:
        raise BridgeError(f"unsupported PYTHIA profile: {profile}")

    path.write_text(
        f"""! Phase 7 canonical-v2 bridge PYTHIA settings.
! Input LHE has already been canonicalized from WHIZARD extended ISR-history form.
! Profile: {profile} ({description})

Main:numberOfEvents = {events}
Main:timesAllowErrors = 100

Beams:frameType = 4

HadronLevel:all = {hadron_level}
PartonLevel:ISR = on
PartonLevel:FSR = on
PartonLevel:MPI = off

Next:numberShowInfo = 1
Next:numberShowProcess = 1
Next:numberShowEvent = 0

Stat:showProcessLevel = on
Stat:showErrors = on
""",
        encoding="utf-8",
    )


def write_sha256sums(run_dir: Path) -> None:
    rows: list[tuple[str, str]] = []

    for path in sorted(run_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(run_dir).as_posix()
        if rel == "SHA256SUMS.txt":
            continue

        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        rows.append((h.hexdigest(), rel))

    with (run_dir / "SHA256SUMS.txt").open("w", encoding="utf-8") as out:
        for digest, rel in rows:
            out.write(f"{digest}  {rel}\n")


def count_pattern(path: Path, pattern: str) -> int:
    if not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8", errors="replace")
    return len(re.findall(pattern, text, flags=re.IGNORECASE))


def build_summary(
    *,
    repo: Path,
    run_dir: Path,
    label: str,
    source_card: Path,
    raw_lhe: Path,
    canon_lhe: Path,
    canon_summary_path: Path,
    hepmc: Path,
    metadata_path: Path,
    pythia_log: Path,
    pythia_profile: str,
    whizard_rc: int,
    canon_rc: int,
    pythia_rc: int,
    validator_rc: int,
    env: Mapping[str, str],
    runtime_view: str,
) -> dict:
    canon_summary = load_json(canon_summary_path) if canon_summary_path.is_file() else {}
    metadata = load_json(metadata_path) if metadata_path.is_file() else {}

    warning_counts = {
        "negative_dipole_mass": count_pattern(
            pythia_log,
            r"Warning in SimpleTimeShower::pTnext: negative dipole mass",
        ),
        "ministring_fragmentation_failed": count_pattern(
            pythia_log,
            r"ministring fragmentation failed",
        ),
        "hadronlevel_failed_try_again": count_pattern(
            pythia_log,
            r"hadronLevel failed; try again",
        ),
        "range_check": count_pattern(pythia_log, r"range_check"),
        "fatal": count_pattern(pythia_log, r"fatal"),
        "segmentation": count_pattern(pythia_log, r"segmentation"),
    }

    errors: list[str] = []
    warnings: list[str] = []

    if whizard_rc != 0:
        errors.append(f"WHIZARD returned nonzero rc={whizard_rc}")
    if canon_rc != 0:
        errors.append(f"canonicalizer returned nonzero rc={canon_rc}")
    if pythia_rc != 0:
        errors.append(f"PYTHIA/HepMC driver returned nonzero rc={pythia_rc}")
    if validator_rc != 0:
        errors.append(f"Phase 7 validator returned nonzero rc={validator_rc}")

    raw_events = count_lhe_events(raw_lhe) if raw_lhe.is_file() else None
    canon_events = count_lhe_events(canon_lhe) if canon_lhe.is_file() else None
    hepmc_events = count_hepmc_events(hepmc) if hepmc.is_file() else None

    if raw_events != canon_events:
        errors.append(f"raw/canonical LHE event count mismatch: {raw_events} != {canon_events}")

    if metadata:
        if metadata.get("status") != "success":
            errors.append(f"metadata status is not success: {metadata.get('status')}")
        if metadata.get("return_code") != 0:
            errors.append(f"metadata return_code is not 0: {metadata.get('return_code')}")
        if metadata.get("accepted_events") != hepmc_events:
            errors.append(
                f"metadata accepted_events != HepMC event count: "
                f"{metadata.get('accepted_events')} != {hepmc_events}"
            )
        if metadata.get("failed_events", 0) != 0:
            warnings.append(f"metadata failed_events nonzero: {metadata.get('failed_events')}")
        if metadata.get("pythia_version") != "8.316":
            errors.append(f"unexpected PYTHIA version: {metadata.get('pythia_version')}")
        if metadata.get("hepmc_version") != "3.03.01":
            errors.append(f"unexpected HepMC3 version: {metadata.get('hepmc_version')}")

    if warning_counts["range_check"] or warning_counts["fatal"] or warning_counts["segmentation"]:
        errors.append(f"fatal-like PYTHIA log patterns observed: {warning_counts}")

    if (
        warning_counts["negative_dipole_mass"]
        or warning_counts["ministring_fragmentation_failed"]
        or warning_counts["hadronlevel_failed_try_again"]
    ):
        warnings.append(f"PYTHIA runtime warning patterns observed: {warning_counts}")

    status = "FAIL" if errors else ("PASS_WITH_RUNTIME_WARNINGS" if warnings else "PASS")

    try:
        commit = run_text(["git", "rev-parse", "HEAD"], cwd=repo, env=env)
    except Exception:
        commit = "UNKNOWN"

    try:
        branch = run_text(["git", "branch", "--show-current"], cwd=repo, env=env)
    except Exception:
        branch = "UNKNOWN"

    return {
        "schema_version": 1,
        "phase_name": "phase7_canonical_bridge_runner",
        "status": status,
        "label": label,
        "repo": str(repo),
        "branch": branch,
        "commit": commit,
        "runtime_view": runtime_view,
        "run_dir": str(run_dir),
        "pythia_profile": pythia_profile,
        "source_card": str(source_card),
        "raw_lhe": str(raw_lhe),
        "canonical_lhe": str(canon_lhe),
        "canonical_summary": str(canon_summary_path),
        "hepmc": str(hepmc),
        "metadata": str(metadata_path),
        "pythia_log": str(pythia_log),
        "return_codes": {
            "whizard": whizard_rc,
            "canonicalizer": canon_rc,
            "pythia": pythia_rc,
            "validator": validator_rc,
        },
        "event_counts": {
            "raw_lhe": raw_events,
            "canonical_lhe": canon_events,
            "hepmc": hepmc_events,
        },
        "canonical_summary_data": canon_summary,
        "metadata_data": metadata,
        "warning_counts": warning_counts,
        "errors": errors,
        "warnings": warnings,
    }


def write_runtime_note(
    *,
    run_dir: Path,
    summary: dict,
    env: Mapping[str, str],
    repo: Path,
    pythia_exec: Path,
    pythia_config: Path,
    validator_log: Path,
) -> None:
    def safe_command_output(command: list[str]) -> str:
        try:
            return run_text(command, cwd=repo, env=env)
        except Exception as exc:
            return f"UNAVAILABLE: {exc}"

    lines = [
        f"REPO={repo}",
        f"COMMIT={summary.get('commit')}",
        f"BRANCH={summary.get('branch')}",
        f"DATE_UTC={utc_iso()}",
        f"HOST={safe_command_output(['hostname'])}",
        f"VIEW={summary.get('runtime_view')}",
        f"WHIZARD={safe_command_output(['bash', '-lc', 'command -v whizard'])}",
        f"WHIZARD_VERSION={safe_command_output(['bash', '-lc', 'whizard --version | head -1'])}",
        f"PYTHIA8_CONFIG={safe_command_output(['bash', '-lc', 'command -v pythia8-config'])}",
        f"PYTHIA8_VERSION={safe_command_output(['pythia8-config', '--version'])}",
        f"HEPMC3_CONFIG={safe_command_output(['bash', '-lc', 'command -v HepMC3-config'])}",
        f"HEPMC3_VERSION={safe_command_output(['HepMC3-config', '--version'])}",
        f"SHOWER_DRIVER={pythia_exec}",
        f"LABEL={summary.get('label')}",
        f"SOURCE_CARD={summary.get('source_card')}",
        f"RAW_LHE={summary.get('raw_lhe')}",
        f"CANONICAL_LHE={summary.get('canonical_lhe')}",
        f"CANONICAL_SUMMARY={summary.get('canonical_summary')}",
        f"PYTHIA_CONFIG={pythia_config}",
        f"HEPMC_OUT={summary.get('hepmc')}",
        f"HEPMC_METADATA={summary.get('metadata')}",
        f"PYTHIA_LOG={summary.get('pythia_log')}",
        f"PYTHIA_PROFILE={summary.get('pythia_profile')}",
        f"VALIDATOR_LOG={validator_log}",
        f"RAW_LHE_EVENT_COUNT={summary['event_counts'].get('raw_lhe')}",
        f"CANONICAL_LHE_EVENT_COUNT={summary['event_counts'].get('canonical_lhe')}",
        f"HEPMC_EVENT_COUNT={summary['event_counts'].get('hepmc')}",
        f"WHIZARD_BRIDGE_RC={summary['return_codes'].get('whizard')}",
        f"CANON_RC={summary['return_codes'].get('canonicalizer')}",
        f"PYTHIA_CANON_V2_RC={summary['return_codes'].get('pythia')}",
        f"PHASE7_VALIDATE_RUNTIME_BRIDGE_RC={summary['return_codes'].get('validator')}",
        f"PHASE7_BRIDGE_STATUS={summary.get('status')}",
        "NOTES=Phase 7 canonical-v2 bridge runner output. PASS_WITH_RUNTIME_WARNINGS is acceptable for bridge proof but not final production shower certification.",
    ]

    (run_dir / "RUNTIME_PHASE7_BRIDGE.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one Phase 7 canonical-v2 WHIZARD/PYTHIA/HepMC bridge sample."
    )
    parser.add_argument("--repo", type=Path, default=Path(os.environ.get("REPO", ".")).resolve())
    parser.add_argument("--card", type=Path, required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--sample-id", default=None)
    parser.add_argument("--campaign-id", default=DEFAULT_CAMPAIGN_ID)
    parser.add_argument("--shard-id", default=None)
    parser.add_argument("--seed", type=int, default=12345)
    parser.add_argument("--events", type=int, default=100)
    parser.add_argument("--iterations", default="3:5000")
    parser.add_argument(
        "--pythia-profile",
        choices=["full_hadron", "parton_only"],
        default="full_hadron",
        help="PYTHIA final-state profile. Use parton_only for stable spin/QIS qualification without Lund fragmentation.",
    )
    parser.add_argument("--output-base", type=Path, default=Path(os.environ.get("TTSP_RUN_BASE", str(DEFAULT_OUTPUT_BASE))))
    parser.add_argument("--build-dir", type=Path, default=None)
    parser.add_argument("--pythia-exec", type=Path, default=None)
    parser.add_argument("--timeout-whizard-minutes", type=int, default=120)
    parser.add_argument("--runtime-view", default=DEFAULT_RUNTIME_VIEW)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    repo = args.repo.resolve()
    card = args.card.resolve()
    output_base = args.output_base
    build_dir = args.build_dir or (repo / "build-lcg-devkey-fri")
    pythia_exec = args.pythia_exec or (build_dir / "qis_lhe_to_hepmc3")

    sample_id = args.sample_id or f"{args.label}_canonical_v2"
    shard_id = args.shard_id or f"bridge_{args.events}ev_{args.label}"

    env = dict(os.environ)
    ensure_pythonpath(env, repo)

    if not repo.is_dir():
        raise BridgeError(f"repo does not exist: {repo}")
    if not card.is_file():
        raise BridgeError(f"card does not exist: {card}")
    if not pythia_exec.is_file():
        raise BridgeError(f"PYTHIA/HepMC driver does not exist: {pythia_exec}")
    if not command_exists("whizard", env):
        raise BridgeError("whizard is not available in PATH; source the pinned runtime first")
    if not command_exists("pythia8-config", env):
        raise BridgeError("pythia8-config is not available in PATH; source the pinned runtime first")
    if not command_exists("HepMC3-config", env):
        raise BridgeError("HepMC3-config is not available in PATH; source the pinned runtime first")

    canonicalizer = repo / "scripts/showering/canonicalize_whizard_lhe_for_pythia_v2.py"
    wrapper = repo / "scripts/showering/run_external_pythia.sh"
    validator = repo / "scripts/showering/validate_phase7_showering.py"

    for path, label in [
        (canonicalizer, "canonicalizer"),
        (wrapper, "external PYTHIA wrapper"),
        (validator, "Phase 7 validator"),
    ]:
        if not path.is_file():
            raise BridgeError(f"missing {label}: {path}")

    run_dir = output_base / f"phase7_bridge_{args.label}_{utc_stamp()}"

    print("=" * 100)
    print("PHASE7_CANONICAL_BRIDGE_RUNNER")
    print(f"REPO={repo}")
    print(f"CARD={card}")
    print(f"LABEL={args.label}")
    print(f"SAMPLE_ID={sample_id}")
    print(f"SHARD_ID={shard_id}")
    print(f"EVENTS={args.events}")
    print(f"ITERATIONS={args.iterations}")
    print(f"PYTHIA_PROFILE={args.pythia_profile}")
    print(f"RUN_DIR={run_dir}")
    print(f"PYTHIA_EXEC={pythia_exec}")
    print("=" * 100)

    if args.dry_run:
        print("DRY_RUN=1")
        return 0

    source_common = card.parent / "common"

    bridge_card = localize_card(
        source_card=card,
        source_common=source_common,
        run_dir=run_dir,
        events=args.events,
        iterations=args.iterations,
        sample_basename="bridge_raw",
    )

    whizard_log = run_dir / "whizard_bridge.log"
    whizard_rc = run_logged(
        ["whizard", bridge_card.name],
        cwd=run_dir,
        log_path=whizard_log,
        env=env,
        timeout_seconds=args.timeout_whizard_minutes * 60,
    )
    (run_dir / "whizard_bridge.rc").write_text(f"WHIZARD_BRIDGE_RC={whizard_rc}\n", encoding="utf-8")

    if whizard_rc != 0:
        raise BridgeError(f"WHIZARD failed with rc={whizard_rc}; see {whizard_log}")

    raw_lhe = run_dir / "bridge_raw.lhe"
    if not raw_lhe.is_file() or raw_lhe.stat().st_size == 0:
        raise BridgeError(f"raw WHIZARD LHE not produced: {raw_lhe}")

    canon_lhe = run_dir / f"{args.label}.canonical_v2.lhe"
    canon_summary = run_dir / f"{args.label}.canonical_v2.summary.json"

    canon_log = run_dir / "canonicalize.log"
    canon_rc = run_logged(
        [
            sys.executable,
            str(canonicalizer),
            "--input",
            str(raw_lhe),
            "--output",
            str(canon_lhe),
            "--summary",
            str(canon_summary),
        ],
        cwd=repo,
        log_path=canon_log,
        env=env,
    )
    (run_dir / "canonicalize.rc").write_text(f"CANON_RC={canon_rc}\n", encoding="utf-8")

    if canon_rc != 0:
        raise BridgeError(f"canonicalizer failed with rc={canon_rc}; see {canon_log}")

    pythia_config = run_dir / "pythia8_bridge_canonical_v2.cmnd"
    write_pythia_cmnd(pythia_config, args.events, args.pythia_profile)

    hepmc = run_dir / f"{args.label}.canonical_v2.hepmc3"
    pythia_log = run_dir / "run_external_pythia_canonical_v2.log"

    pythia_env = dict(env)
    pythia_env.update(
        {
            "PYTHIA_EXEC": str(pythia_exec),
            "SAMPLE_ID": sample_id,
            "CAMPAIGN_ID": args.campaign_id,
            "SHARD_ID": shard_id,
            "MAX_EVENTS": str(args.events),
            "SEED": str(args.seed),
        }
    )

    pythia_rc = run_logged(
        [
            "bash",
            str(wrapper),
            "--config",
            str(pythia_config),
            "--lhe",
            str(canon_lhe),
            "--out",
            str(hepmc),
        ],
        cwd=repo,
        log_path=pythia_log,
        env=pythia_env,
    )
    (run_dir / "pythia_canonical_v2.rc").write_text(
        f"PYTHIA_CANON_V2_RC={pythia_rc}\n",
        encoding="utf-8",
    )

    if pythia_rc != 0:
        raise BridgeError(f"PYTHIA/HepMC bridge failed with rc={pythia_rc}; see {pythia_log}")

    validator_log = run_dir / "phase7_validate_runtime_bridge.log"
    metadata = Path(str(hepmc) + ".metadata.json")

    validator_rc = run_logged(
        [
            sys.executable,
            str(validator),
            "--repo",
            str(repo),
            "--lhe",
            str(canon_lhe),
            "--canonical-summary",
            str(canon_summary),
            "--hepmc",
            str(hepmc),
            "--metadata",
            str(metadata),
        ],
        cwd=repo,
        log_path=validator_log,
        env=env,
    )
    (run_dir / "phase7_validate_runtime_bridge.rc").write_text(
        f"PHASE7_VALIDATE_RUNTIME_BRIDGE_RC={validator_rc}\n",
        encoding="utf-8",
    )

    if validator_rc != 0:
        raise BridgeError(f"Phase 7 validator failed with rc={validator_rc}; see {validator_log}")

    summary = build_summary(
        repo=repo,
        run_dir=run_dir,
        label=args.label,
        source_card=card,
        raw_lhe=raw_lhe,
        canon_lhe=canon_lhe,
        canon_summary_path=canon_summary,
        hepmc=hepmc,
        metadata_path=metadata,
        pythia_log=pythia_log,
        pythia_profile=args.pythia_profile,
        whizard_rc=whizard_rc,
        canon_rc=canon_rc,
        pythia_rc=pythia_rc,
        validator_rc=validator_rc,
        env=env,
        runtime_view=args.runtime_view,
    )

    (run_dir / "phase7_bridge_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    write_runtime_note(
        run_dir=run_dir,
        summary=summary,
        env=env,
        repo=repo,
        pythia_exec=pythia_exec,
        pythia_config=pythia_config,
        validator_log=validator_log,
    )

    write_sha256sums(run_dir)

    print()
    print("=" * 100)
    print(f"PHASE7_BRIDGE_RUNNER_STATUS={summary['status']}")
    print(f"PHASE7_BRIDGE_RUNNER_RUN_DIR={run_dir}")
    print(f"RAW_LHE_EVENTS={summary['event_counts'].get('raw_lhe')}")
    print(f"CANONICAL_LHE_EVENTS={summary['event_counts'].get('canonical_lhe')}")
    print(f"HEPMC_EVENTS={summary['event_counts'].get('hepmc')}")
    print(f"WARNING_COUNTS={summary['warning_counts']}")
    if summary["warnings"]:
        print("WARNINGS:")
        for warning in summary["warnings"]:
            print(f"  - {warning}")
    if summary["errors"]:
        print("ERRORS:")
        for error in summary["errors"]:
            print(f"  - {error}")
    print("=" * 100)

    return 0 if summary["status"] in {"PASS", "PASS_WITH_RUNTIME_WARNINGS"} else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BridgeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
