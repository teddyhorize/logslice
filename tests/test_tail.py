"""Tests for logslice.tail."""

from __future__ import annotations

import textwrap
import time
from pathlib import Path

import pytest

from logslice.tail import follow, head_n_lines, last_n_lines


# ---------------------------------------------------------------------------
# last_n_lines
# ---------------------------------------------------------------------------

def test_last_n_lines_fewer_than_n():
    assert last_n_lines(["a", "b"], 5) == ["a", "b"]


def test_last_n_lines_exact_n():
    assert last_n_lines(["a", "b", "c"], 3) == ["a", "b", "c"]


def test_last_n_lines_more_than_n():
    assert last_n_lines(["a", "b", "c", "d", "e"], 3) == ["c", "d", "e"]


def test_last_n_lines_n1():
    assert last_n_lines(["x", "y", "z"], 1) == ["z"]


def test_last_n_lines_empty_input():
    assert last_n_lines([], 3) == []


def test_last_n_lines_invalid_n_raises():
    with pytest.raises(ValueError, match="n must be >= 1"):
        last_n_lines(["a"], 0)


# ---------------------------------------------------------------------------
# head_n_lines
# ---------------------------------------------------------------------------

def test_head_n_lines_fewer_than_n():
    assert list(head_n_lines(["a", "b"], 5)) == ["a", "b"]


def test_head_n_lines_exact_n():
    assert list(head_n_lines(["a", "b", "c"], 3)) == ["a", "b", "c"]


def test_head_n_lines_more_than_n():
    assert list(head_n_lines(["a", "b", "c", "d"], 2)) == ["a", "b"]


def test_head_n_lines_n1():
    assert list(head_n_lines(["x", "y", "z"], 1)) == ["x"]


def test_head_n_lines_empty_input():
    assert list(head_n_lines([], 3)) == []


def test_head_n_lines_invalid_n_raises():
    with pytest.raises(ValueError, match="n must be >= 1"):
        list(head_n_lines(["a"], 0))


# ---------------------------------------------------------------------------
# follow
# ---------------------------------------------------------------------------

def test_follow_yields_appended_lines(tmp_path: Path):
    log = tmp_path / "app.log"
    log.write_text("")  # create empty file

    gen = follow(log, poll_interval=0.05)

    # Append lines after the generator has been created
    log.write_text("line one\nline two\n")

    results = []
    deadline = time.monotonic() + 2.0
    while len(results) < 2 and time.monotonic() < deadline:
        try:
            results.append(next(gen))
        except StopIteration:
            break

    assert results == ["line one", "line two"]


def test_follow_skips_existing_content(tmp_path: Path):
    log = tmp_path / "existing.log"
    log.write_text("old line\n")

    gen = follow(log, poll_interval=0.05)

    # Append a new line
    with log.open("a") as fh:
        fh.write("new line\n")

    result = next(gen)
    assert result == "new line"
