"""Tests for logslice.stats module."""

import pytest
from datetime import datetime
from logslice.stats import SliceStats, collect_stats


TS1 = datetime(2024, 1, 1, 10, 0, 0)
TS2 = datetime(2024, 1, 1, 10, 5, 0)
TS3 = datetime(2024, 1, 1, 10, 10, 0)


def test_match_rate_no_lines():
    stats = SliceStats()
    assert stats.match_rate == 0.0


def test_match_rate_all_matched():
    stats = SliceStats(total_lines=10, matched_lines=10)
    assert stats.match_rate == 1.0


def test_match_rate_partial():
    stats = SliceStats(total_lines=4, matched_lines=1)
    assert stats.match_rate == 0.25


def test_to_dict_keys():
    stats = SliceStats(total_lines=5, matched_lines=3, skipped_lines=2)
    d = stats.to_dict()
    assert set(d.keys()) == {
        "total_lines", "matched_lines", "skipped_lines",
        "match_rate", "first_timestamp", "last_timestamp",
        "pattern_hits", "time_filter_hits",
    }


def test_to_dict_timestamps_none():
    stats = SliceStats()
    d = stats.to_dict()
    assert d["first_timestamp"] is None
    assert d["last_timestamp"] is None


def test_to_dict_timestamps_serialized():
    stats = SliceStats(first_timestamp=TS1, last_timestamp=TS3)
    d = stats.to_dict()
    assert d["first_timestamp"] == TS1.isoformat()
    assert d["last_timestamp"] == TS3.isoformat()


def test_collect_stats_all_matched():
    results = [
        ("line1", TS1, True),
        ("line2", TS2, True),
        ("line3", TS3, True),
    ]
    lines, stats = collect_stats(iter(results))
    assert lines == ["line1", "line2", "line3"]
    assert stats.total_lines == 3
    assert stats.matched_lines == 3
    assert stats.skipped_lines == 0
    assert stats.first_timestamp == TS1
    assert stats.last_timestamp == TS3


def test_collect_stats_some_skipped():
    results = [
        ("line1", TS1, True),
        ("line2", TS2, False),
        ("line3", TS3, True),
    ]
    lines, stats = collect_stats(iter(results))
    assert lines == ["line1", "line3"]
    assert stats.total_lines == 3
    assert stats.matched_lines == 2
    assert stats.skipped_lines == 1


def test_collect_stats_no_timestamps():
    results = [
        ("line1", None, True),
        ("line2", None, False),
    ]
    lines, stats = collect_stats(iter(results))
    assert stats.first_timestamp is None
    assert stats.last_timestamp is None
    assert stats.total_lines == 2


def test_collect_stats_empty():
    lines, stats = collect_stats(iter([]))
    assert lines == []
    assert stats.total_lines == 0
    assert stats.match_rate == 0.0
