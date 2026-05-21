"""Tests for logslice.reader streaming and filtering logic."""

import os
import tempfile
from datetime import datetime

import pytest

from logslice.reader import compile_pattern, parse_timestamp, stream_lines

SAMPLE_LINES = [
    "2024-01-10 08:00:00 INFO  Server started",
    "2024-01-10 08:05:00 DEBUG Connection accepted from 192.168.1.1",
    "2024-01-10 08:10:00 ERROR Disk usage at 95%",
    "2024-01-10 08:15:00 INFO  Backup completed successfully",
    "2024-01-10 08:20:00 WARN  Memory usage high",
]


@pytest.fixture()
def log_file():
    """Create a temporary log file and return its path."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as fh:
        fh.write("\n".join(SAMPLE_LINES) + "\n")
        path = fh.name
    yield path
    os.unlink(path)


def test_compile_pattern_none():
    assert compile_pattern(None) is None


def test_compile_pattern_valid():
    p = compile_pattern(r"ERROR|WARN")
    assert p is not None
    assert p.search("2024-01-10 ERROR something")


def test_parse_timestamp_valid():
    ts = parse_timestamp("2024-01-10 08:00:00 INFO msg", "%Y-%m-%d %H:%M:%S")
    assert ts == datetime(2024, 1, 10, 8, 0, 0)


def test_parse_timestamp_invalid():
    ts = parse_timestamp("no timestamp here", "%Y-%m-%d %H:%M:%S")
    assert ts is None


def test_stream_all_lines(log_file):
    lines = list(stream_lines(log_file))
    assert lines == SAMPLE_LINES


def test_stream_regex_filter(log_file):
    lines = list(stream_lines(log_file, pattern=r"ERROR|WARN"))
    assert len(lines) == 2
    assert all("ERROR" in l or "WARN" in l for l in lines)


def test_stream_time_range(log_file):
    start = datetime(2024, 1, 10, 8, 5, 0)
    end = datetime(2024, 1, 10, 8, 15, 0)
    lines = list(stream_lines(log_file, start_time=start, end_time=end))
    assert len(lines) == 3
    assert "DEBUG" in lines[0]
    assert "Backup" in lines[-1]


def test_stream_combined_filter(log_file):
    start = datetime(2024, 1, 10, 8, 0, 0)
    end = datetime(2024, 1, 10, 8, 20, 0)
    lines = list(stream_lines(log_file, pattern=r"INFO", start_time=start, end_time=end))
    assert len(lines) == 2
    assert all("INFO" in l for l in lines)


def test_stream_no_matches(log_file):
    lines = list(stream_lines(log_file, pattern=r"CRITICAL"))
    assert lines == []
