"""Tests for logslice.filter module."""

import os
import tempfile
from datetime import datetime

import pytest

from logslice.filter import filter_lines, count_matches


SAMPLE_LOGS = [
    "2024-01-10 08:00:00 INFO  Server started\n",
    "2024-01-10 09:15:00 DEBUG Request received from 192.168.1.1\n",
    "2024-01-10 10:30:00 ERROR Failed to connect to database\n",
    "2024-01-10 11:45:00 INFO  Health check passed\n",
    "2024-01-10 13:00:00 WARN  High memory usage detected\n",
    "2024-01-10 14:20:00 ERROR Timeout on request /api/data\n",
]


@pytest.fixture
def log_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.writelines(SAMPLE_LOGS)
        path = f.name
    yield path
    os.unlink(path)


def test_filter_no_criteria_returns_all(log_file):
    results = list(filter_lines(log_file))
    assert len(results) == len(SAMPLE_LOGS)


def test_filter_by_start_time(log_file):
    start = datetime(2024, 1, 10, 10, 0, 0)
    results = list(filter_lines(log_file, start=start))
    assert len(results) == 4
    assert all("08:00" not in r and "09:15" not in r for r in results)


def test_filter_by_end_time(log_file):
    end = datetime(2024, 1, 10, 10, 30, 0)
    results = list(filter_lines(log_file, end=end))
    assert len(results) == 3


def test_filter_by_time_range(log_file):
    start = datetime(2024, 1, 10, 9, 0, 0)
    end = datetime(2024, 1, 10, 11, 59, 59)
    results = list(filter_lines(log_file, start=start, end=end))
    assert len(results) == 3


def test_filter_by_pattern(log_file):
    results = list(filter_lines(log_file, pattern=r"ERROR"))
    assert len(results) == 2
    assert all("ERROR" in r for r in results)


def test_filter_by_pattern_and_time(log_file):
    start = datetime(2024, 1, 10, 10, 0, 0)
    results = list(filter_lines(log_file, start=start, pattern=r"ERROR"))
    assert len(results) == 2


def test_filter_pattern_no_match(log_file):
    results = list(filter_lines(log_file, pattern=r"CRITICAL"))
    assert results == []


def test_count_matches_all(log_file):
    assert count_matches(log_file) == len(SAMPLE_LOGS)


def test_count_matches_with_pattern(log_file):
    assert count_matches(log_file, pattern=r"INFO") == 2


def test_count_matches_with_time_range(log_file):
    start = datetime(2024, 1, 10, 13, 0, 0)
    end = datetime(2024, 1, 10, 14, 20, 0)
    assert count_matches(log_file, start=start, end=end) == 2
