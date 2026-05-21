"""Tests for logslice.formatter."""

import json
import pytest

from logslice.formatter import (
    format_line_plain,
    format_line_json,
    format_lines,
    SUPPORTED_FORMATS,
)


SAMPLE_LINES = [
    "2024-01-01 00:00:01 INFO  startup complete",
    "2024-01-01 00:00:02 DEBUG loop tick",
    "2024-01-01 00:00:03 ERROR something failed",
]


# ---------------------------------------------------------------------------
# format_line_plain
# ---------------------------------------------------------------------------

def test_format_line_plain_no_number():
    result = format_line_plain("hello world")
    assert result == "hello world"


def test_format_line_plain_with_number():
    result = format_line_plain("hello world", line_number=5)
    assert result == "5: hello world"


# ---------------------------------------------------------------------------
# format_line_json
# ---------------------------------------------------------------------------

def test_format_line_json_no_number():
    result = format_line_json("hello world")
    data = json.loads(result)
    assert data == {"line": "hello world"}


def test_format_line_json_with_number():
    result = format_line_json("hello world", line_number=3)
    data = json.loads(result)
    assert data == {"line": "hello world", "line_number": 3}


# ---------------------------------------------------------------------------
# format_lines — plain
# ---------------------------------------------------------------------------

def test_format_lines_plain_default():
    output = list(format_lines(iter(SAMPLE_LINES)))
    assert output == SAMPLE_LINES


def test_format_lines_plain_with_line_numbers():
    output = list(format_lines(iter(SAMPLE_LINES), show_line_numbers=True))
    assert output[0].startswith("1: ")
    assert output[2].startswith("3: ")


# ---------------------------------------------------------------------------
# format_lines — json
# ---------------------------------------------------------------------------

def test_format_lines_json():
    output = list(format_lines(iter(SAMPLE_LINES), fmt="json"))
    assert len(output) == len(SAMPLE_LINES)
    for raw, formatted in zip(SAMPLE_LINES, output):
        data = json.loads(formatted)
        assert data["line"] == raw
        assert "line_number" not in data


def test_format_lines_json_with_line_numbers():
    output = list(format_lines(iter(SAMPLE_LINES), fmt="json", show_line_numbers=True))
    for idx, formatted in enumerate(output, start=1):
        data = json.loads(formatted)
        assert data["line_number"] == idx


# ---------------------------------------------------------------------------
# format_lines — count
# ---------------------------------------------------------------------------

def test_format_lines_count():
    output = list(format_lines(iter(SAMPLE_LINES), fmt="count"))
    assert output == ["3"]


def test_format_lines_count_empty():
    output = list(format_lines(iter([]), fmt="count"))
    assert output == ["0"]


# ---------------------------------------------------------------------------
# unsupported format
# ---------------------------------------------------------------------------

def test_format_lines_invalid_format():
    with pytest.raises(ValueError, match="Unsupported format"):
        list(format_lines(iter(SAMPLE_LINES), fmt="xml"))
