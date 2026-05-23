"""Tests for logslice.output."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from logslice.output import write_lines, write_stats


SAMPLE_LINES = [
    (1, "2024-01-01 00:00:01 INFO  server started"),
    (2, "2024-01-01 00:00:02 DEBUG loop tick"),
    (3, "2024-01-01 00:00:03 ERROR boom"),
]


# ---------------------------------------------------------------------------
# write_lines — plain format
# ---------------------------------------------------------------------------

def test_write_lines_plain_to_stdout(capsys):
    count = write_lines(SAMPLE_LINES, dest=None, fmt="plain", show_numbers=False)
    captured = capsys.readouterr()
    assert count == 3
    assert "INFO  server started" in captured.out
    assert "ERROR boom" in captured.out


def test_write_lines_plain_with_numbers(capsys):
    count = write_lines(SAMPLE_LINES, dest=None, fmt="plain", show_numbers=True)
    captured = capsys.readouterr()
    assert count == 3
    assert "1:" in captured.out
    assert "3:" in captured.out


def test_write_lines_plain_to_file(tmp_path):
    out_file = tmp_path / "out.log"
    count = write_lines(SAMPLE_LINES, dest=str(out_file), fmt="plain")
    assert count == 3
    lines = out_file.read_text().splitlines()
    assert len(lines) == 3
    assert "ERROR boom" in lines[2]


# ---------------------------------------------------------------------------
# write_lines — json format
# ---------------------------------------------------------------------------

def test_write_lines_json_to_file(tmp_path):
    out_file = tmp_path / "out.jsonl"
    count = write_lines(SAMPLE_LINES, dest=str(out_file), fmt="json")
    assert count == 3
    raw_lines = out_file.read_text().splitlines()
    obj = json.loads(raw_lines[0])
    assert "line" in obj


def test_write_lines_empty_iterable(capsys):
    count = write_lines([], dest=None, fmt="plain")
    assert count == 0
    captured = capsys.readouterr()
    assert captured.out == ""


# ---------------------------------------------------------------------------
# write_stats
# ---------------------------------------------------------------------------

def test_write_stats_to_stderr(capsys):
    stats = {"total": 10, "matched": 5, "match_rate": 0.5}
    write_stats(stats, dest=None)
    captured = capsys.readouterr()
    parsed = json.loads(captured.err)
    assert parsed["total"] == 10


def test_write_stats_to_file(tmp_path):
    out_file = tmp_path / "stats.json"
    stats = {"total": 20, "matched": 10}
    write_stats(stats, dest=str(out_file))
    content = out_file.read_text()
    parsed = json.loads(content)
    assert parsed["matched"] == 10


def test_write_stats_appends_to_existing_file(tmp_path):
    out_file = tmp_path / "stats.json"
    out_file.write_text("# existing content\n")
    write_stats({"total": 1}, dest=str(out_file))
    content = out_file.read_text()
    assert "# existing content" in content
    assert "total" in content
