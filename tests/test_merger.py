"""Tests for logslice.merger."""

from __future__ import annotations

import os
import tempfile
from typing import List

import pytest

from logslice.merger import merge_streams, merge_files


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

STREAM_A = [
    "2024-01-01 10:00:00 alpha one\n",
    "2024-01-01 10:00:02 alpha two\n",
    "2024-01-01 10:00:04 alpha three\n",
]

STREAM_B = [
    "2024-01-01 10:00:01 beta one\n",
    "2024-01-01 10:00:03 beta two\n",
    "2024-01-01 10:00:05 beta three\n",
]

NO_TS_STREAM = [
    "no timestamp here\n",
    "also no timestamp\n",
]


def _names(lines: List[str]) -> List[str]:
    """Extract the last word token from each line (our marker word)."""
    return [line.split()[-1].strip() for line in lines]


# ---------------------------------------------------------------------------
# merge_streams
# ---------------------------------------------------------------------------

def test_merge_streams_interleaves_chronologically():
    sources = [("a", iter(STREAM_A)), ("b", iter(STREAM_B))]
    result = list(merge_streams(sources))
    assert _names(result) == ["one", "one", "two", "two", "three", "three"]


def test_merge_streams_single_source_passthrough():
    sources = [("a", iter(STREAM_A))]
    result = list(merge_streams(sources))
    assert result == STREAM_A


def test_merge_streams_empty_sources_yields_nothing():
    result = list(merge_streams([]))
    assert result == []


def test_merge_streams_one_empty_source():
    sources = [("a", iter(STREAM_A)), ("b", iter([]))]
    result = list(merge_streams(sources))
    assert result == STREAM_A


def test_merge_streams_no_timestamp_kept_when_fallback_true():
    sources = [("a", iter(STREAM_A)), ("b", iter(NO_TS_STREAM))]
    result = list(merge_streams(sources, fallback_order=True))
    assert len(result) == len(STREAM_A) + len(NO_TS_STREAM)


def test_merge_streams_no_timestamp_dropped_when_fallback_false():
    sources = [("a", iter(STREAM_A)), ("b", iter(NO_TS_STREAM))]
    result = list(merge_streams(sources, fallback_order=False))
    assert result == STREAM_A


def test_merge_streams_equal_timestamps_both_emitted():
    same_ts = [
        "2024-01-01 10:00:00 x\n",
        "2024-01-01 10:00:00 y\n",
    ]
    sources = [("a", iter(same_ts)), ("b", iter(same_ts))]
    result = list(merge_streams(sources))
    assert len(result) == 4


# ---------------------------------------------------------------------------
# merge_files
# ---------------------------------------------------------------------------

def _write_tmp(lines: List[str]) -> str:
    fd, path = tempfile.mkstemp(suffix=".log")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.writelines(lines)
    return path


def test_merge_files_interleaves_two_files():
    path_a = _write_tmp(STREAM_A)
    path_b = _write_tmp(STREAM_B)
    try:
        result = list(merge_files([path_a, path_b]))
        assert _names(result) == ["one", "one", "two", "two", "three", "three"]
    finally:
        os.unlink(path_a)
        os.unlink(path_b)


def test_merge_files_single_file_passthrough():
    path = _write_tmp(STREAM_A)
    try:
        result = list(merge_files([path]))
        assert result == STREAM_A
    finally:
        os.unlink(path)


def test_merge_files_empty_list_yields_nothing():
    result = list(merge_files([]))
    assert result == []
