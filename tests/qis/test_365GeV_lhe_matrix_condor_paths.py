from __future__ import annotations

import json
import subprocess
from pathlib import Path

import yaml


REPO = Path(__file__).resolve().parents[2]


def write_campaign(campaign: Path) -> None:
    campaign.mkdir(parents=True)
    (campaign / "sample_ids.txt").write_text("sample_a\n")
    (campaign / "campaign_manifest.json").write_text(
        json.dumps({"profile": "pilot"}) + "\n"
    )


def write_config(path: Path) -> None:
    path.write_text(
        yaml.safe_dump(
            {
                "profiles": {
                    "pilot": {"condor_job_flavour": "workday"},
                },
                "condor": {
                    "request_cpus": 1,
                    "request_memory": "2500MB",
                    "request_disk": "2500MB",
                    "getenv": True,
                    "should_transfer_files": "NO",
                },
            },
            sort_keys=False,
        )
    )


def run_submitter(campaign: Path, config: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "bash",
            str(REPO / "scripts/qis/submit_365GeV_lhe_matrix.sh"),
            "--repo-root",
            str(REPO),
            "--campaign-root",
            str(campaign),
            "--config",
            str(config),
            "--submit-only",
        ],
        check=True,
        cwd=REPO,
        text=True,
        capture_output=True,
    )


def test_submitter_creates_stable_condor_stream_directories(tmp_path: Path) -> None:
    campaign = tmp_path / "campaign"
    write_campaign(campaign)
    config = tmp_path / "matrix.yaml"
    write_config(config)

    run_submitter(campaign, config)

    stdout_dir = campaign / "condor" / "stdout"
    stderr_dir = campaign / "condor" / "stderr"
    submit_file = campaign / "condor" / "lhe_matrix.sub"

    assert stdout_dir.is_dir()
    assert stderr_dir.is_dir()
    text = submit_file.read_text()
    assert f"output = {stdout_dir}/$(sample_id).out" in text
    assert f"error = {stderr_dir}/$(sample_id).err" in text
    assert f"log = {campaign / 'condor' / 'cluster.log'}" in text
    assert "/logs/" not in text


def test_submitter_preserves_submit_visible_symlink_path(tmp_path: Path) -> None:
    physical_parent = tmp_path / "physical_eos_target"
    physical_parent.mkdir()
    physical_campaign = physical_parent / "campaign"
    write_campaign(physical_campaign)

    logical_parent = tmp_path / "afs_visible_runs"
    logical_parent.symlink_to(physical_parent, target_is_directory=True)
    logical_campaign = logical_parent / "campaign"

    config = tmp_path / "matrix.yaml"
    write_config(config)

    result = run_submitter(logical_campaign, config)

    submit_file = physical_campaign / "condor" / "lhe_matrix.sub"
    text = submit_file.read_text()
    logical = str(logical_campaign)
    physical = str(physical_campaign)

    assert f"--campaign-root {logical}" in text
    assert f"output = {logical}/condor/stdout/$(sample_id).out" in text
    assert f"error = {logical}/condor/stderr/$(sample_id).err" in text
    assert f"log = {logical}/condor/cluster.log" in text
    assert f"queue sample_id from {logical}/sample_ids.txt" in text
    assert physical not in text
    assert f"Submit-visible campaign root: {logical}" in result.stdout
    assert f"Physical campaign root (diagnostic only): {physical}" in result.stdout
