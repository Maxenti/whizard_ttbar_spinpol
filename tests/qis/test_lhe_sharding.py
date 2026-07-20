from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts/showering/prepare_lhe_shards.py"
SPEC = importlib.util.spec_from_file_location("prepare_lhe_shards", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def make_lhe(path: Path, events: int) -> None:
    lines = [
        '<LesHouchesEvents version="2.0">\n',
        '<header></header>\n',
        '<init>\n',
        ' 11 -11 250 250 -1 -1 -1 -1 3 1\n',
        ' 1.0 0.0 1.0 1\n',
        f'<xsecinfo neve="{events}" totxsec="1.0" />\n',
        '</init>\n',
    ]
    for index in range(events):
        lines.extend(
            [
                '<event>\n',
                f' 2 1 1.0 500.0 0.0 0.1 # EVENT_INDEX={index}\n',
                ' 11 -1 0 0 0 0 0 0 250 250 0 0 9\n',
                ' -11 -1 0 0 0 0 0 0 -250 250 0 0 9\n',
                '</event>\n',
            ]
        )
    lines.append('</LesHouchesEvents>\n')
    path.write_text("".join(lines))


def event_markers(path: Path) -> list[int]:
    return [
        int(value)
        for value in re.findall(r"EVENT_INDEX=(\d+)", path.read_text())
    ]


def test_balanced_plan_is_contiguous() -> None:
    plan = MODULE.balanced_plan(13, 4)
    assert [item.events for item in plan] == [4, 3, 3, 3]
    assert [(item.start, item.stop) for item in plan] == [
        (0, 4),
        (4, 7),
        (7, 10),
        (10, 13),
    ]


def test_streaming_split_reads_only_requested_window(tmp_path: Path) -> None:
    source = tmp_path / "source.lhe"
    make_lhe(source, 20)
    output = tmp_path / "shards"
    plans = MODULE.balanced_plan(13, 4)

    rows = MODULE.write_sample_shards(
        campaign_id="test_campaign",
        sample_id="test_sample",
        source=source,
        output_dir=output,
        plans=plans,
        created_utc="2026-07-20T00:00:00Z",
    )

    assert len(rows) == 4
    assert [int(row["requested_events"]) for row in rows] == [4, 3, 3, 3]
    assert [int(row["source_event_start"]) for row in rows] == [0, 4, 7, 10]
    assert [int(row["source_event_stop_exclusive"]) for row in rows] == [4, 7, 10, 13]
    assert len({row["selected_event_window_sha256"] for row in rows}) == 1

    all_markers: list[int] = []
    for row in rows:
        shard = Path(row["shard_lhe_path"])
        text = shard.read_text()
        markers = event_markers(shard)
        all_markers.extend(markers)
        assert len(markers) == int(row["requested_events"])
        assert text.count("<event>") == int(row["requested_events"])
        assert text.rstrip().endswith("</LesHouchesEvents>")
        assert f'neve="{len(markers)}"' in text
        assert MODULE.sha256(shard) == row["shard_lhe_sha256"]

    assert all_markers == list(range(13))
    assert 13 not in all_markers
    assert 19 not in all_markers


def test_existing_rows_validation_detects_tampering(tmp_path: Path) -> None:
    source = tmp_path / "source.lhe"
    make_lhe(source, 8)
    output = tmp_path / "shards"
    plans = MODULE.balanced_plan(8, 2)
    rows = MODULE.write_sample_shards(
        campaign_id="test_campaign",
        sample_id="test_sample",
        source=source,
        output_dir=output,
        plans=plans,
        created_utc="2026-07-20T00:00:00Z",
    )
    assert MODULE.existing_rows_valid(rows, source=source, plans=plans)
    Path(rows[0]["shard_lhe_path"]).write_text("corrupt\n")
    assert not MODULE.existing_rows_valid(rows, source=source, plans=plans)
