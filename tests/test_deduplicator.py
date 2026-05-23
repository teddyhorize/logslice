"""Tests for logslice.deduplicator."""

import pytest

from logslice.deduplicator import (
    dedup_consecutive,
    dedup_global,
    format_collapsed,
)


# ---------------------------------------------------------------------------
# dedup_consecutive
# ---------------------------------------------------------------------------

class TestDedupConsecutive:
    def test_empty_input_yields_nothing(self):
        assert list(dedup_consecutive([])) == []

    def test_single_line_yields_once(self):
        assert list(dedup_consecutive(["hello"])) == [("hello", 1)]

    def test_no_duplicates_yields_all(self):
        lines = ["a", "b", "c"]
        assert list(dedup_consecutive(lines)) == [("a", 1), ("b", 1), ("c", 1)]

    def test_consecutive_duplicates_collapsed(self):
        lines = ["a", "a", "a", "b"]
        assert list(dedup_consecutive(lines)) == [("a", 3), ("b", 1)]

    def test_non_consecutive_duplicates_kept_separately(self):
        lines = ["a", "b", "a"]
        result = list(dedup_consecutive(lines))
        assert result == [("a", 1), ("b", 1), ("a", 1)]

    def test_all_same_line(self):
        lines = ["x"] * 5
        assert list(dedup_consecutive(lines)) == [("x", 5)]

    def test_alternating_lines(self):
        lines = ["a", "b", "a", "b"]
        result = list(dedup_consecutive(lines))
        assert result == [("a", 1), ("b", 1), ("a", 1), ("b", 1)]


# ---------------------------------------------------------------------------
# dedup_global
# ---------------------------------------------------------------------------

class TestDedupGlobal:
    def test_empty_input_yields_nothing(self):
        assert list(dedup_global([])) == []

    def test_no_duplicates_yields_all(self):
        lines = ["a", "b", "c"]
        assert list(dedup_global(lines)) == ["a", "b", "c"]

    def test_duplicate_non_consecutive_removed(self):
        lines = ["a", "b", "a", "c"]
        assert list(dedup_global(lines)) == ["a", "b", "c"]

    def test_all_duplicates_yields_one(self):
        lines = ["dup"] * 10
        assert list(dedup_global(lines)) == ["dup"]

    def test_max_cache_evicts_old_entries(self):
        # With max_cache=2, after seeing 3 unique lines the first is evicted.
        lines = ["a", "b", "c", "a"]  # 'a' evicted after 'c', so re-appears
        result = list(dedup_global(lines, max_cache=2))
        assert result == ["a", "b", "c", "a"]

    def test_preserves_order_of_first_occurrence(self):
        lines = ["z", "y", "x", "z", "y"]
        assert list(dedup_global(lines)) == ["z", "y", "x"]


# ---------------------------------------------------------------------------
# format_collapsed
# ---------------------------------------------------------------------------

class TestFormatCollapsed:
    def test_count_one_returns_line_unchanged(self):
        assert format_collapsed("some log line", 1) == "some log line"

    def test_count_greater_than_one_appends_annotation(self):
        result = format_collapsed("some log line", 3)
        assert result == "some log line  [repeated 3x]"

    def test_count_two(self):
        result = format_collapsed("err", 2)
        assert "[repeated 2x]" in result

    def test_large_count(self):
        result = format_collapsed("flood", 1000)
        assert "[repeated 1000x]" in result
