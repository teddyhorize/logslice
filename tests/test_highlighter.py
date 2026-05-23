"""Tests for logslice.highlighter."""

import re
import pytest

from logslice.highlighter import (
    highlight_match,
    highlight_lines,
    ANSI_RESET,
    ANSI_YELLOW,
    ANSI_RED,
    ANSI_CYAN,
    ANSI_GREEN,
)


# ---------------------------------------------------------------------------
# highlight_match
# ---------------------------------------------------------------------------

def test_highlight_match_no_pattern_returns_original():
    line = "2024-01-01 ERROR something went wrong"
    assert highlight_match(line, None) == line


def test_highlight_match_no_match_returns_original():
    pattern = re.compile(r"DEBUG")
    line = "2024-01-01 INFO nothing here"
    assert highlight_match(line, pattern) == line


def test_highlight_match_wraps_matched_text():
    pattern = re.compile(r"ERROR")
    line = "2024-01-01 ERROR something"
    result = highlight_match(line, pattern)
    assert f"{ANSI_YELLOW}ERROR{ANSI_RESET}" in result
    assert "2024-01-01" in result
    assert "something" in result


def test_highlight_match_multiple_occurrences():
    pattern = re.compile(r"foo")
    line = "foo bar foo baz foo"
    result = highlight_match(line, pattern)
    assert result.count(f"{ANSI_YELLOW}foo{ANSI_RESET}") == 3


def test_highlight_match_custom_color_red():
    pattern = re.compile(r"CRITICAL")
    line = "CRITICAL failure"
    result = highlight_match(line, pattern, color="red")
    assert f"{ANSI_RED}CRITICAL{ANSI_RESET}" in result


def test_highlight_match_custom_color_cyan():
    pattern = re.compile(r"INFO")
    line = "INFO startup complete"
    result = highlight_match(line, pattern, color="cyan")
    assert f"{ANSI_CYAN}INFO{ANSI_RESET}" in result


def test_highlight_match_unknown_color_falls_back_to_yellow():
    pattern = re.compile(r"WARN")
    line = "WARN disk usage high"
    result = highlight_match(line, pattern, color="purple")
    assert f"{ANSI_YELLOW}WARN{ANSI_RESET}" in result


# ---------------------------------------------------------------------------
# highlight_lines
# ---------------------------------------------------------------------------

def test_highlight_lines_no_pattern_yields_unchanged():
    lines = ["line one", "line two"]
    result = list(highlight_lines(lines, None))
    assert result == lines


def test_highlight_lines_disabled_yields_unchanged():
    pattern = re.compile(r"one")
    lines = ["line one", "line two"]
    result = list(highlight_lines(lines, pattern, enabled=False))
    assert result == lines


def test_highlight_lines_applies_to_matching_lines():
    pattern = re.compile(r"ERROR")
    lines = [
        "2024-01-01 INFO all good",
        "2024-01-01 ERROR bad thing",
        "2024-01-01 INFO recovered",
    ]
    result = list(highlight_lines(lines, pattern))
    assert f"{ANSI_YELLOW}ERROR{ANSI_RESET}" in result[1]
    assert ANSI_YELLOW not in result[0]
    assert ANSI_YELLOW not in result[2]


def test_highlight_lines_preserves_line_count():
    pattern = re.compile(r"x")
    lines = ["a", "b", "x", "c", "x x"]
    result = list(highlight_lines(lines, pattern))
    assert len(result) == len(lines)


def test_highlight_lines_empty_input():
    pattern = re.compile(r"ERROR")
    result = list(highlight_lines([], pattern))
    assert result == []
