"""Tests for the logslice CLI module."""

import pytest
from datetime import datetime
from pathlib import Path

from logslice.cli import build_parser, parse_datetime, run


LOG_CONTENT = (
    "2024-01-15T10:00:00 INFO  Server started\n"
    "2024-01-15T10:05:00 DEBUG Request received from 192.168.1.1\n"
    "2024-01-15T10:10:00 ERROR Failed to connect to database\n"
    "2024-01-15T10:15:00 INFO  Retrying connection\n"
    "2024-01-15T10:20:00 INFO  Connection established\n"
)


@pytest.fixture
def log_file(tmp_path: Path) -> Path:
    f = tmp_path / "app.log"
    f.write_text(LOG_CONTENT)
    return f


def test_parse_datetime_valid():
    dt = parse_datetime("2024-01-15T10:00:00")
    assert dt == datetime(2024, 1, 15, 10, 0, 0)


def test_parse_datetime_invalid():
    import argparse
    with pytest.raises(argparse.ArgumentTypeError):
        parse_datetime("not-a-date")


def test_build_parser_defaults():
    parser = build_parser()
    args = parser.parse_args([])
    assert args.file == "-"
    assert args.start is None
    assert args.end is None
    assert args.pattern is None
    assert args.count is False
    assert args.ignore_case is False


def test_run_no_filter_prints_all(log_file, capsys):
    exit_code = run([str(log_file)])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Server started" in captured.out
    assert "ERROR" in captured.out
    assert len(captured.out.strip().splitlines()) == 5


def test_run_with_pattern(log_file, capsys):
    exit_code = run([str(log_file), "--pattern", "ERROR|DEBUG"])
    captured = capsys.readouterr()
    assert exit_code == 0
    lines = captured.out.strip().splitlines()
    assert len(lines) == 2
    assert any("ERROR" in l for l in lines)
    assert any("DEBUG" in l for l in lines)


def test_run_with_count(log_file, capsys):
    exit_code = run([str(log_file), "--pattern", "INFO", "--count"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.strip() == "3"


def test_run_with_start_time(log_file, capsys):
    exit_code = run([str(log_file), "--start", "2024-01-15T10:10:00"])
    captured = capsys.readouterr()
    assert exit_code == 0
    lines = captured.out.strip().splitlines()
    assert len(lines) == 3
    assert all("10:10" in l or "10:15" in l or "10:20" in l for l in lines)


def test_run_with_time_range(log_file, capsys):
    exit_code = run([
        str(log_file),
        "--start", "2024-01-15T10:05:00",
        "--end", "2024-01-15T10:10:00",
    ])
    captured = capsys.readouterr()
    assert exit_code == 0
    lines = captured.out.strip().splitlines()
    assert len(lines) == 2


def test_run_file_not_found(capsys):
    exit_code = run(["/nonexistent/path/app.log"])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "file not found" in captured.err


def test_run_invalid_pattern(log_file, capsys):
    exit_code = run([str(log_file), "--pattern", "[invalid"])
    captured = capsys.readouterr()
    assert exit_code == 2
    assert "invalid pattern" in captured.err


def test_run_ignore_case(log_file, capsys):
    exit_code = run([str(log_file), "--pattern", "error", "--ignore-case"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "ERROR" in captured.out
