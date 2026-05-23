"""Tests for logslice.splitter."""

from datetime import timedelta

import pytest

from logslice.splitter import chunk_count, split_by_count, split_by_time


TIMESTAMPED = [
    "2024-01-01 00:00:00 server started",
    "2024-01-01 00:00:30 request received",
    "2024-01-01 00:01:10 request processed",
    "2024-01-01 00:02:05 connection closed",
    "2024-01-01 00:03:00 server stopped",
]

PLAIN = ["alpha", "beta", "gamma", "delta", "epsilon"]


# ---------------------------------------------------------------------------
# split_by_count
# ---------------------------------------------------------------------------

def test_split_by_count_exact_multiple():
    chunks = list(split_by_count(PLAIN, 2))
    assert len(chunks) == 3
    assert chunks[0] == ["alpha", "beta"]
    assert chunks[-1] == ["epsilon"]


def test_split_by_count_larger_than_input():
    chunks = list(split_by_count(PLAIN, 10))
    assert chunks == [PLAIN]


def test_split_by_count_size_one():
    chunks = list(split_by_count(PLAIN, 1))
    assert len(chunks) == len(PLAIN)
    assert all(len(c) == 1 for c in chunks)


def test_split_by_count_empty_input():
    assert list(split_by_count([], 3)) == []


def test_split_by_count_invalid_size_raises():
    with pytest.raises(ValueError):
        list(split_by_count(PLAIN, 0))


# ---------------------------------------------------------------------------
# split_by_time
# ---------------------------------------------------------------------------

def test_split_by_time_one_minute_window():
    chunks = list(split_by_time(TIMESTAMPED, timedelta(minutes=1)))
    # window 0:00:00–0:01:00 → first 3 lines; 0:01:10–0:02:10 → next; 0:03:00 → last
    assert len(chunks) == 3


def test_split_by_time_large_window_single_chunk():
    chunks = list(split_by_time(TIMESTAMPED, timedelta(hours=1)))
    assert len(chunks) == 1
    assert chunks[0] == TIMESTAMPED


def test_split_by_time_unparseable_lines_stay_in_chunk():
    lines = [
        "2024-01-01 00:00:00 start",
        "no timestamp here",
        "2024-01-01 00:00:10 end",
    ]
    chunks = list(split_by_time(lines, timedelta(seconds=30)))
    assert len(chunks) == 1
    assert "no timestamp here" in chunks[0]


def test_split_by_time_empty_input():
    assert list(split_by_time([], timedelta(minutes=1))) == []


def test_split_by_time_invalid_window_raises():
    with pytest.raises(ValueError):
        list(split_by_time(TIMESTAMPED, timedelta(seconds=0)))


# ---------------------------------------------------------------------------
# chunk_count
# ---------------------------------------------------------------------------

def test_chunk_count_basic():
    chunks = list(split_by_count(PLAIN, 2))
    num, total = chunk_count(chunks)
    assert num == 3
    assert total == 5


def test_chunk_count_empty():
    num, total = chunk_count([])
    assert num == 0
    assert total == 0
