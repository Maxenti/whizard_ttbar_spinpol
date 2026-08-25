#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import re
import signal
import subprocess
import sys
import time
from collections import deque
from pathlib import Path
from statistics import median
from typing import Any


ITERATION_RE = re.compile(
    r"""
    ^\s*
    (?P<iteration>\d+)
    \s+
    (?P<calls>\d+)
    \s+
    (?P<integral>[+-]?\d+(?:\.\d+)?E[+-]\d+)
    \s+
    (?P<error>[+-]?\d+(?:\.\d+)?E[+-]\d+)
    \s+
    (?P<error_percent>[+-]?\d+(?:\.\d+)?)
    \s+
    (?P<accuracy>[+-]?\d+(?:\.\d+)?)
    \*?
    \s+
    (?P<efficiency>[+-]?\d+(?:\.\d+)?)
    (?:
        \s+
        (?P<chi2>[+-]?\d+(?:\.\d+)?)
        \s+
        (?P<n_iterations>\d+)
    )?
    \s*$
    """,
    re.VERBOSE,
)

FINAL_SUMMARY_RE = re.compile(
    r"""
    ^\s*
    (?P<iteration>\d+)
    \s+
    (?P<calls>\d+)
    \s+
    (?P<integral>[+-]?\d+(?:\.\d+)?E[+-]\d+)
    \s+
    (?P<error>[+-]?\d+(?:\.\d+)?E[+-]\d+)
    \s+
    (?P<error_percent>[+-]?\d+(?:\.\d+)?)
    \s+
    (?P<accuracy>[+-]?\d+(?:\.\d+)?)
    \s+
    (?P<efficiency>[+-]?\d+(?:\.\d+)?)
    \s+
    (?P<chi2>[+-]?\d+(?:\.\d+)?)
    \s+
    (?P<n_iterations>\d+)
    \s*$
    """,
    re.VERBOSE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run a WHIZARD command with integration-quality and "
            "accepted-event-rate fail-fast protection."
        )
    )

    parser.add_argument(
        "--workdir",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--log",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--lhe",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--status-json",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--target-events",
        type=int,
        default=1000,
    )
    parser.add_argument(
        "--poll-seconds",
        type=int,
        default=60,
    )
    parser.add_argument(
        "--generation-grace-seconds",
        type=int,
        default=600,
    )
    parser.add_argument(
        "--rate-window-seconds",
        type=int,
        default=600,
    )
    parser.add_argument(
        "--minimum-events-per-minute",
        type=float,
        default=5.0,
    )
    parser.add_argument(
        "--maximum-projected-runtime-seconds",
        type=int,
        default=10800,
    )
    parser.add_argument(
        "--hard-timeout-seconds",
        type=int,
        default=14400,
    )

    parser.add_argument(
        "--maximum-final-error-percent",
        type=float,
        default=3.0,
    )
    parser.add_argument(
        "--maximum-iteration-spike-factor",
        type=float,
        default=20.0,
    )
    parser.add_argument(
        "--spike-error-percent-threshold",
        type=float,
        default=50.0,
    )
    parser.add_argument(
        "--maximum-final-median-deviation-fraction",
        type=float,
        default=0.30,
    )

    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command to run after --.",
    )

    args = parser.parse_args()

    if args.command and args.command[0] == "--":
        args.command = args.command[1:]

    if not args.command:
        parser.error("missing command after --")

    return args


def count_lhe_events(path: Path) -> int:
    if not path.is_file():
        return 0

    count = 0

    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
    ) as handle:
        for line in handle:
            if line.lstrip().startswith("<event>"):
                count += 1

    return count


def parse_log(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "iteration_rows": [],
        "final_summary": None,
        "simulation_started": False,
        "event_sample_complete": False,
        "whizard_finished": False,
    }

    if not path.is_file():
        return result

    lines = path.read_text(
        encoding="utf-8",
        errors="replace",
    ).splitlines()

    result["simulation_started"] = any(
        "Starting simulation for process" in line
        for line in lines
    )
    result["event_sample_complete"] = any(
        "event sample complete" in line
        for line in lines
    )
    result["whizard_finished"] = any(
        "WHIZARD run finished." in line
        for line in lines
    )

    table_active = False

    for line in lines:
        if "| It" in line and "Integral[fb]" in line:
            table_active = True
            continue

        if not table_active:
            continue

        match = ITERATION_RE.match(line)

        if not match:
            continue

        row = {
            "iteration": int(match.group("iteration")),
            "calls": int(match.group("calls")),
            "integral_fb": float(match.group("integral")),
            "error_fb": float(match.group("error")),
            "error_percent": float(match.group("error_percent")),
            "accuracy": float(match.group("accuracy")),
            "efficiency_percent": float(match.group("efficiency")),
            "chi2": (
                float(match.group("chi2"))
                if match.group("chi2") is not None
                else None
            ),
            "n_iterations": (
                int(match.group("n_iterations"))
                if match.group("n_iterations") is not None
                else None
            ),
        }

        if row["chi2"] is None:
            result["iteration_rows"].append(row)
        else:
            result["final_summary"] = row

    return result


def integration_failure(
    parsed: dict[str, Any],
    args: argparse.Namespace,
) -> str | None:
    rows = parsed["iteration_rows"]
    final = parsed["final_summary"]

    if not rows:
        return None

    positive_integrals = [
        abs(float(row["integral_fb"]))
        for row in rows
        if math.isfinite(float(row["integral_fb"]))
        and float(row["integral_fb"]) != 0.0
    ]

    if len(positive_integrals) >= 3:
        robust_median = median(positive_integrals)

        if robust_median > 0.0:
            for row in rows:
                ratio = abs(float(row["integral_fb"])) / robust_median

                if (
                    ratio > args.maximum_iteration_spike_factor
                    and float(row["error_percent"])
                    > args.spike_error_percent_threshold
                ):
                    return (
                        "catastrophic integration iteration: "
                        f"iteration={row['iteration']} "
                        f"integral_fb={row['integral_fb']} "
                        f"error_percent={row['error_percent']} "
                        f"median_fb={robust_median} "
                        f"spike_factor={ratio}"
                    )

    if final is None:
        return None

    if (
        float(final["error_percent"])
        > args.maximum_final_error_percent
    ):
        return (
            "final integration relative error too large: "
            f"{final['error_percent']}% > "
            f"{args.maximum_final_error_percent}%"
        )

    if len(positive_integrals) >= 3:
        robust_median = median(positive_integrals)

        if robust_median > 0.0:
            deviation = (
                abs(float(final["integral_fb"]) - robust_median)
                / robust_median
            )

            if (
                deviation
                > args.maximum_final_median_deviation_fraction
            ):
                return (
                    "final integral inconsistent with iteration median: "
                    f"final_fb={final['integral_fb']} "
                    f"median_fb={robust_median} "
                    f"fractional_deviation={deviation}"
                )

    return None


def terminate_process_group(
    process: subprocess.Popen[Any],
) -> None:
    if process.poll() is not None:
        return

    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return

    try:
        process.wait(timeout=60)
        return
    except subprocess.TimeoutExpired:
        pass

    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        return


def write_status(
    path: Path,
    payload: dict[str, Any],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary = path.with_suffix(path.suffix + ".tmp")

    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    temporary.replace(path)


def main() -> int:
    args = parse_args()

    args.workdir.mkdir(parents=True, exist_ok=True)
    args.log.parent.mkdir(parents=True, exist_ok=True)
    args.status_json.parent.mkdir(parents=True, exist_ok=True)

    start_time = time.time()
    generation_start_time: float | None = None
    history: deque[tuple[float, int]] = deque()

    with args.log.open(
        "w",
        encoding="utf-8",
    ) as log_handle:
        process = subprocess.Popen(
            args.command,
            cwd=args.workdir,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            text=True,
        )

    failure_reason: str | None = None
    final_state = "RUNNING"

    try:
        while True:
            now = time.time()
            elapsed = now - start_time

            parsed = parse_log(args.log)
            event_count = count_lhe_events(args.lhe)

            if (
                parsed["simulation_started"]
                and generation_start_time is None
            ):
                generation_start_time = now
                history.clear()

            if generation_start_time is not None:
                history.append((now, event_count))

                while (
                    history
                    and now - history[0][0]
                    > args.rate_window_seconds
                ):
                    history.popleft()

            integration_problem = integration_failure(
                parsed,
                args,
            )

            if integration_problem is not None:
                failure_reason = integration_problem
                final_state = "FAILED_INTEGRATION_QUALITY"
                break

            rate_events_per_minute: float | None = None
            projected_total_seconds: float | None = None

            if (
                generation_start_time is not None
                and len(history) >= 2
            ):
                first_time, first_count = history[0]
                last_time, last_count = history[-1]

                delta_time = last_time - first_time
                delta_events = last_count - first_count

                if delta_time > 0:
                    rate_events_per_minute = (
                        delta_events / delta_time * 60.0
                    )

                    if rate_events_per_minute > 0:
                        remaining = max(
                            args.target_events - event_count,
                            0,
                        )

                        projected_total_seconds = (
                            now
                            - generation_start_time
                            + remaining
                            / rate_events_per_minute
                            * 60.0
                        )

            generation_elapsed = (
                now - generation_start_time
                if generation_start_time is not None
                else None
            )

            status = {
                "state": final_state,
                "pid": process.pid,
                "command": args.command,
                "elapsed_seconds": elapsed,
                "generation_elapsed_seconds": generation_elapsed,
                "event_count": event_count,
                "target_events": args.target_events,
                "rate_events_per_minute": rate_events_per_minute,
                "projected_total_seconds": projected_total_seconds,
                "integration": parsed,
                "failure_reason": failure_reason,
                "timestamp_epoch": now,
            }

            write_status(args.status_json, status)

            if process.poll() is not None:
                if process.returncode == 0:
                    final_state = "COMPLETED"
                else:
                    final_state = "FAILED_COMMAND"

                break

            if elapsed > args.hard_timeout_seconds:
                failure_reason = (
                    "hard runtime timeout exceeded: "
                    f"{elapsed:.1f}s > "
                    f"{args.hard_timeout_seconds}s"
                )
                final_state = "FAILED_HARD_TIMEOUT"
                break

            if (
                generation_start_time is not None
                and generation_elapsed is not None
                and generation_elapsed
                >= args.generation_grace_seconds
                and rate_events_per_minute is not None
            ):
                if (
                    rate_events_per_minute
                    < args.minimum_events_per_minute
                ):
                    failure_reason = (
                        "accepted-event rate too low: "
                        f"{rate_events_per_minute:.3f} events/min "
                        f"< {args.minimum_events_per_minute}"
                    )
                    final_state = "FAILED_LOW_EVENT_RATE"
                    break

                if (
                    projected_total_seconds is not None
                    and projected_total_seconds
                    > args.maximum_projected_runtime_seconds
                ):
                    failure_reason = (
                        "projected generation runtime too long: "
                        f"{projected_total_seconds:.1f}s > "
                        f"{args.maximum_projected_runtime_seconds}s"
                    )
                    final_state = "FAILED_PROJECTED_RUNTIME"
                    break

            time.sleep(args.poll_seconds)

    finally:
        if final_state.startswith("FAILED"):
            terminate_process_group(process)

        return_code = process.poll()

        parsed = parse_log(args.log)
        event_count = count_lhe_events(args.lhe)

        final_payload = {
            "state": final_state,
            "pid": process.pid,
            "command": args.command,
            "elapsed_seconds": time.time() - start_time,
            "event_count": event_count,
            "target_events": args.target_events,
            "integration": parsed,
            "failure_reason": failure_reason,
            "command_return_code": return_code,
            "timestamp_epoch": time.time(),
        }

        write_status(args.status_json, final_payload)

    print(f"WHIZARD_GUARD_STATE={final_state}")
    print(f"WHIZARD_GUARD_EVENTS={event_count}")
    print(f"WHIZARD_GUARD_STATUS={args.status_json}")

    if failure_reason:
        print(
            f"WHIZARD_GUARD_FAILURE={failure_reason}",
            file=sys.stderr,
        )

    return 0 if final_state == "COMPLETED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
