#!/usr/bin/env python3
"""Prepare a 365 GeV ISR smoke run from a qualified 500 GeV ISR template.

The tool is deliberately strict. It refuses a source template unless the
source metadata identifies an ISR-enabled 500 GeV sample and the explicit
mixed-flavour top decays match the requested epmum channel. Controlled
metadata are rewritten into one canonical block, eliminating stale duplicate
values before WHIZARD is allowed to run.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any

import yaml


ENERGY_PATTERNS = (
    re.compile(
        r"(?im)^(?P<prefix>\s*sqrts\s*=\s*)500(?:\.0+)?"
        r"(?P<unit>\s*GeV)(?P<tail>\s*(?:!.*)?)$"
    ),
    re.compile(
        r"(?im)^(?P<prefix>\s*sqrts\s*=\s*)500(?:\.0+)?"
        r"(?P<tail>\s*(?:!.*)?)$"
    ),
)
# Production .sin.in files may use a template token on the right-hand side
# (for example, a renderer placeholder) rather than a decimal event count.
# Match one complete SINDARIN assignment and replace only its value.  Comments
# remain intact, while an empty or comment-only right-hand side is rejected.
EVENT_PATTERN = re.compile(
    r"(?im)^(?P<prefix>\s*n_events\s*=\s*)"
    r"(?P<value>[^!\r\n]*?\S)"
    r"(?P<tail>\s*(?:!.*)?)$"
)
# Production .sin.in sources use renderer placeholders for seed and output
# sample names.  Match the complete assignment RHS, not only decimal seeds.
SEED_PATTERN = re.compile(
    r"(?im)^(?P<prefix>\s*seed\s*=\s*)"
    r"(?P<value>[^!\r\n]*?\S)"
    r"(?P<tail>\s*(?:!.*)?)$"
)
SAMPLE_PATTERN = re.compile(
    r"(?im)^(?P<prefix>\s*\$sample\s*=\s*)"
    r"(?P<value>[^!\r\n]*?\S)"
    r"(?P<tail>\s*(?:!.*)?)$"
)
META_PATTERN = re.compile(
    r"(?im)^\s*!\s*META\s+(?P<key>[A-Za-z0-9_]+)\s*=\s*(?P<value>.*?)\s*$"
)
CONTROLLED_META_KEYS = {
    "campaign_id",
    "campaign_sample_id",
    "sample_id",
    "nominal_sqrt_s_GeV",
    "sqrt_s_GeV",
    "initial_state",
    "decay_channel",
    "polarization",
    "beam1_helicity",
    "beam2_helicity",
    "beam1_pol_fraction",
    "beam2_pol_fraction",
    "spin_mode",
    "isr_enabled",
    "beam_spectrum",
    "model",
    "seed",
    "random_seed",
    "requested_events",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text())
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a YAML mapping in {path}")
    return payload


def metadata_values(text: str) -> dict[str, list[str]]:
    values: dict[str, list[str]] = {}
    for match in META_PATTERN.finditer(text):
        values.setdefault(match.group("key"), []).append(match.group("value").strip())
    return values


def truthy(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes", "on"}


def template_contract_checks(text: str, config: dict[str, Any]) -> list[dict[str, Any]]:
    production = config.get("production", {})
    contract = production.get("source_template_contract", {})
    meta = metadata_values(text)
    checks: list[dict[str, Any]] = []

    def record(name: str, passed: bool, message: str) -> None:
        checks.append({"check": name, "status": "pass" if passed else "fail", "message": message})

    expected_sample = str(contract.get("sample_id", ""))
    sample_values = meta.get("sample_id", [])
    record(
        "source_sample_id",
        expected_sample in sample_values or expected_sample in text,
        f"expected qualified source sample {expected_sample}",
    )

    isr_values = meta.get("isr_enabled", [])
    require_isr = bool(contract.get("require_isr_metadata", True))
    record(
        "source_isr_enabled",
        (not require_isr) or (len(isr_values) == 1 and truthy(isr_values[0])),
        f"source isr_enabled metadata={isr_values}",
    )
    record(
        "source_no_isr_false",
        not any(not truthy(value) for value in isr_values),
        "source must not declare isr_enabled=false",
    )

    accepted_decay = {str(value) for value in contract.get("accepted_decay_metadata", ["epmum"])}
    decay_values = meta.get("decay_channel", [])
    record(
        "source_decay_metadata",
        len(decay_values) == 1 and decay_values[0] in accepted_decay,
        f"source decay_channel metadata={decay_values}",
    )

    # Process-level truth is required in addition to metadata.
    record(
        "source_top_decay_process",
        re.search(r"(?im)^\s*process\s+t_decay\s*=\s*t\s*=>\s*b\s*,\s*E1\s*,\s*n1\s*$", text)
        is not None,
        "source contains t -> b e+ nu_e",
    )
    record(
        "source_antitop_decay_process",
        re.search(
            r"(?im)^\s*process\s+tbar_decay\s*=\s*tbar\s*=>\s*bbar\s*,\s*e2\s*,\s*N2\s*$",
            text,
        )
        is not None,
        "source contains tbar -> bbar mu- anti-nu_mu",
    )
    record(
        "source_nominal_energy",
        re.search(r"(?im)^\s*sqrts\s*=\s*500(?:\.0+)?\s*GeV\s*(?:!.*)?$", text)
        is not None,
        "source has exactly the expected 500 GeV sqrts assignment",
    )
    return checks


def require_template_contract(path: Path, config: dict[str, Any]) -> list[dict[str, Any]]:
    checks = template_contract_checks(path.read_text(), config)
    failures = [item for item in checks if item["status"] != "pass"]
    if failures:
        details = "\n".join(
            f"  - {item['check']}: {item['message']}" for item in failures
        )
        raise ValueError(
            f"Template is not an eligible qualified 500 GeV ISR source: {path}\n{details}"
        )
    return checks


def find_template(repo: Path, config: dict[str, Any], override: Path | None) -> tuple[Path, list[dict[str, Any]]]:
    if override is not None:
        candidate = override if override.is_absolute() else repo / override
        if not candidate.is_file():
            raise FileNotFoundError(candidate)
        candidate = candidate.resolve()
        return candidate, require_template_contract(candidate, config)

    production = config.get("production", {})
    rejected: list[str] = []
    for relative in production.get("template_candidates", []):
        candidate = (repo / str(relative)).resolve()
        if not candidate.is_file():
            rejected.append(f"missing: {candidate}")
            continue
        try:
            checks = require_template_contract(candidate, config)
        except ValueError as error:
            rejected.append(str(error))
            continue
        return candidate, checks

    diagnostic = "\n\n".join(rejected) if rejected else "no candidates configured"
    raise FileNotFoundError(
        "No eligible qualified 500 GeV ISR SINDARIN template was found.\n"
        "Pass the authoritative source explicitly with --template.\n\n"
        + diagnostic
    )


def replace_once_or_more(
    text: str,
    patterns: tuple[re.Pattern[str], ...],
    replacement_factory,
    label: str,
    required: bool = True,
) -> tuple[str, int]:
    total = 0
    output = text
    for pattern in patterns:
        output, count = pattern.subn(replacement_factory, output)
        total += count
    if required and total == 0:
        raise ValueError(f"Could not find a supported {label} assignment in input.sin")
    return output, total


def strip_controlled_metadata(text: str) -> tuple[str, int]:
    removed = 0
    output_lines: list[str] = []
    for line in text.splitlines(keepends=True):
        match = META_PATTERN.match(line.rstrip("\n"))
        if match and match.group("key") in CONTROLLED_META_KEYS:
            removed += 1
            continue
        output_lines.append(line)
    return "".join(output_lines), removed


def canonical_header(config: dict[str, Any]) -> str:
    sample = config["sample"]
    energy = float(config["nominal_sqrt_s_GeV"])
    return (
        "! PAPER_SPIN_365GEV_SMOKE_PREPARATION_V1P3\n"
        f"! META campaign_id={config.get('campaign_id', 'paper_spin_365GeV_smoke')}\n"
        f"! META campaign_sample_id={sample['sample_id']}\n"
        f"! META sample_id={sample['sample_id']}\n"
        f"! META nominal_sqrt_s_GeV={energy:g}\n"
        f"! META sqrt_s_GeV={energy:g}\n"
        f"! META initial_state={sample['initial_state']}\n"
        f"! META decay_channel={sample['decay_channel']}\n"
        f"! META polarization={sample['polarization']}\n"
        "! META beam1_helicity=-1\n"
        "! META beam2_helicity=+1\n"
        "! META beam1_pol_fraction=1.0\n"
        "! META beam2_pol_fraction=1.0\n"
        f"! META spin_mode={sample['spin_mode']}\n"
        f"! META isr_enabled={'true' if sample['isr'] else 'false'}\n"
        "! META beam_spectrum=none\n"
        "! META model=SM\n"
        f"! META seed={int(sample['random_seed'])}\n"
        f"! META random_seed={int(sample['random_seed'])}\n"
        f"! META requested_events={int(sample['events'])}\n"
    )


def prepared_contract_checks(text: str, config: dict[str, Any]) -> list[dict[str, Any]]:
    sample = config["sample"]
    energy = float(config["nominal_sqrt_s_GeV"])
    meta = metadata_values(text)
    checks: list[dict[str, Any]] = []

    def record(name: str, passed: bool, message: str) -> None:
        checks.append({"check": name, "status": "pass" if passed else "fail", "message": message})

    expected_meta = {
        "sample_id": str(sample["sample_id"]),
        "sqrt_s_GeV": f"{energy:g}",
        "initial_state": str(sample["initial_state"]),
        "decay_channel": str(sample["decay_channel"]),
        "polarization": str(sample["polarization"]),
        "spin_mode": str(sample["spin_mode"]),
        "isr_enabled": "true" if sample["isr"] else "false",
        "seed": str(int(sample["random_seed"])),
        "requested_events": str(int(sample["events"])),
    }
    for key, expected in expected_meta.items():
        values = meta.get(key, [])
        record(
            f"prepared_meta_{key}",
            values == [expected],
            f"{key}={values}, expected one value {expected}",
        )

    record(
        "prepared_sqrts_assignment",
        len(re.findall(r"(?im)^\s*sqrts\s*=\s*365(?:\.0+)?\s*GeV\s*(?:!.*)?$", text)) == 1,
        "exactly one 365 GeV sqrts assignment",
    )
    record(
        "prepared_event_assignment",
        len(re.findall(r"(?im)^\s*n_events\s*=\s*200\s*(?:!.*)?$", text)) == 1,
        "exactly one n_events=200 assignment",
    )
    record(
        "prepared_seed_assignment",
        len(re.findall(r"(?im)^\s*seed\s*=\s*365001\s*(?:!.*)?$", text)) == 1,
        "exactly one seed=365001 assignment",
    )
    record(
        "prepared_sample_assignment",
        len(
            re.findall(
                rf'(?im)^\s*\$sample\s*=\s*["\']{re.escape(str(sample["sample_id"]))}["\']\s*(?:!.*)?$',
                text,
            )
        )
        == 1,
        f'exactly one $sample assignment for {sample["sample_id"]}',
    )
    controlled_lines = "\n".join(
        line
        for line in text.splitlines()
        if re.match(r"(?i)^\s*(?:seed|n_events|\$sample)\s*=", line)
    )
    record(
        "prepared_no_control_placeholders",
        re.search(
            r"__[A-Z0-9_]+__|@[A-Z_][A-Z0-9_]*@|\$\{[A-Za-z_][A-Za-z0-9_]*\}",
            controlled_lines,
        )
        is None,
        "no unresolved seed, event-count, or output-sample placeholders",
    )
    record(
        "prepared_no_500_tokens",
        re.search(r"500GeV|sqrt\s*\(s\)\s*=\s*500|sqrts\s*=\s*500", text, re.I) is None,
        "no stale 500 GeV campaign tokens",
    )
    record(
        "prepared_no_isr_false",
        re.search(r"(?im)^\s*!\s*META\s+isr_enabled\s*=\s*false\s*$", text) is None,
        "no stale isr_enabled=false metadata",
    )
    return checks


def require_prepared_contract(text: str, config: dict[str, Any]) -> list[dict[str, Any]]:
    checks = prepared_contract_checks(text, config)
    failures = [item for item in checks if item["status"] != "pass"]
    if failures:
        details = "\n".join(
            f"  - {item['check']}: {item['message']}" for item in failures
        )
        raise ValueError("Prepared SINDARIN contract failed:\n" + details)
    return checks


def transform_input(text: str, config: dict[str, Any]) -> tuple[str, dict[str, int], list[dict[str, Any]]]:
    sample = config["sample"]
    sample_id = str(sample["sample_id"])
    energy = float(config["nominal_sqrt_s_GeV"])
    events = int(sample["events"])
    seed = int(sample["random_seed"])

    output, removed_meta = strip_controlled_metadata(text)
    counts: dict[str, int] = {"controlled_metadata_removed": removed_meta}

    output, counts["sqrts_assignments"] = replace_once_or_more(
        output,
        ENERGY_PATTERNS,
        lambda match: f"{match.group('prefix')}{energy:g} GeV{match.groupdict().get('tail', '')}",
        "sqrts",
    )
    output, counts["event_assignments"] = EVENT_PATTERN.subn(
        lambda match: f"{match.group('prefix')}{events}{match.group('tail')}", output
    )
    if counts["event_assignments"] != 1:
        raise ValueError(
            f"Expected exactly one n_events assignment; found {counts['event_assignments']}"
        )
    output, counts["seed_assignments"] = SEED_PATTERN.subn(
        lambda match: f"{match.group('prefix')}{seed}{match.group('tail')}", output
    )
    if counts["seed_assignments"] != 1:
        raise ValueError(
            f"Expected exactly one seed assignment; found {counts['seed_assignments']}"
        )
    output, counts["sample_assignments"] = SAMPLE_PATTERN.subn(
        lambda match: (
            f'{match.group("prefix")}"{sample_id}"{match.group("tail")}'
        ),
        output,
    )
    if counts["sample_assignments"] != 1:
        raise ValueError(
            f"Expected exactly one $sample assignment; found {counts['sample_assignments']}"
        )

    sample_patterns = (
        r"ee_ttbar_emu_LR100_sc_500GeV",
        r"ee_ttbar_epmum_LR100_sc_ISR_500GeV",
        r"ee_ttbar_epmum_LR100_sc_500GeV",
    )
    sample_replacements = 0
    for old_sample in sample_patterns:
        output, count = re.subn(old_sample, sample_id, output)
        sample_replacements += count
    counts["sample_id_tokens"] = sample_replacements
    output, counts["energy_tokens"] = re.subn(r"500GeV", "365GeV", output)
    output, counts["prose_energy_tokens"] = re.subn(
        r"sqrt\s*\(s\)\s*=\s*500\s*GeV", "sqrt(s)=365 GeV", output, flags=re.I
    )

    output = canonical_header(config) + output.lstrip("\n")
    prepared_checks = require_prepared_contract(output, config)
    return output, counts, prepared_checks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--pilot-config",
        type=Path,
        default=Path("configs/qis/paper_spin_365GeV_pilot.yaml"),
    )
    parser.add_argument("--template", type=Path)
    parser.add_argument("--output-run-dir", type=Path)
    parser.add_argument("--force", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo = args.repo_root.expanduser().resolve()
    config_path = args.pilot_config
    if not config_path.is_absolute():
        config_path = repo / config_path
    config_path = config_path.resolve()
    config = load_yaml(config_path)

    sample = config["sample"]
    production = config["production"]
    template, source_checks = find_template(repo, config, args.template)
    output_dir = args.output_run_dir or Path(str(production["output_run_dir"]))
    if not output_dir.is_absolute():
        output_dir = repo / output_dir
    output_dir = output_dir.resolve()

    if output_dir.exists():
        if not args.force:
            raise FileExistsError(f"Refusing to overwrite existing smoke directory: {output_dir}")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    source_text = template.read_text()
    transformed, counts, prepared_checks = transform_input(source_text, config)
    output_input = output_dir / str(production.get("input_filename", "input.sin"))
    output_input.write_text(transformed)

    diff = "".join(
        difflib.unified_diff(
            source_text.splitlines(keepends=True),
            transformed.splitlines(keepends=True),
            fromfile=str(template),
            tofile=str(output_input),
        )
    )
    (output_dir / "input_500_to_365.patch").write_text(diff)

    manifest = {
        "schema_version": 2,
        "tool": "prepare_365GeV_smoke.py",
        "pilot_config": str(config_path),
        "template": str(template),
        "template_sha256": sha256(template),
        "source_template_contract": source_checks,
        "output_run_dir": str(output_dir),
        "output_input": str(output_input),
        "output_input_sha256": sha256(output_input),
        "sample_id": str(sample["sample_id"]),
        "nominal_sqrt_s_GeV": float(config["nominal_sqrt_s_GeV"]),
        "events": int(sample["events"]),
        "random_seed": int(sample["random_seed"]),
        "replacement_counts": counts,
        "prepared_input_contract": prepared_checks,
        "prepared_input_status": "pass",
        "frozen_500GeV_source_modified": False,
    }
    manifest_path = output_dir / "preparation_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    print(json.dumps(manifest, indent=2))
    print(f"Prepared: {output_input}")
    print(f"Review:   {output_dir / 'input_500_to_365.patch'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
