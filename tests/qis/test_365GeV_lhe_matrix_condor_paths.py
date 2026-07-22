from __future__ import annotations

import json
import subprocess
from pathlib import Path

import yaml


REPO = Path(__file__).resolve().parents[2]


def test_submitter_creates_stable_condor_stream_directories(tmp_path: Path) -> None:
    campaign = tmp_path / "campaign"
    campaign.mkdir()
    (campaign / "sample_ids.txt").write_text("sample_a\n")
    (campaign / "campaign_manifest.json").write_text(
        json.dumps({"profile": "pilot"}) + "\n"
    )

    config = tmp_path / "matrix.yaml"
    config.write_text(
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

    subprocess.run(
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

    physical = campaign.resolve()
    stdout_dir = physical / "condor" / "stdout"
    stderr_dir = physical / "condor" / "stderr"
    submit_file = physical / "condor" / "lhe_matrix.sub"

    assert stdout_dir.is_dir()
    assert stderr_dir.is_dir()
    text = submit_file.read_text()
    assert f"output = {stdout_dir}/$(sample_id).out" in text
    assert f"error = {stderr_dir}/$(sample_id).err" in text
    assert f"log = {physical / 'condor' / 'cluster.log'}" in text
    assert "/logs/" not in text
