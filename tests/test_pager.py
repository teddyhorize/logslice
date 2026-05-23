"""Tests for logslice.pager."""

from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from logslice.pager import (
    _build_pager_cmd,
    _detect_pager,
    page_lines,
    should_page,
)


# ---------------------------------------------------------------------------
# _detect_pager
# ---------------------------------------------------------------------------

def test_detect_pager_returns_less_when_available():
    with patch("shutil.which", side_effect=lambda p: "/usr/bin/less" if p == "less" else None):
        assert _detect_pager() == "less"


def test_detect_pager_falls_back_to_more():
    with patch("shutil.which", side_effect=lambda p: "/bin/more" if p == "more" else None):
        assert _detect_pager() == "more"


def test_detect_pager_returns_none_when_nothing_found():
    with patch("shutil.which", return_value=None):
        assert _detect_pager() is None


# ---------------------------------------------------------------------------
# _build_pager_cmd
# ---------------------------------------------------------------------------

def test_build_pager_cmd_less_includes_flags():
    cmd = _build_pager_cmd("less")
    assert cmd[0] == "less"
    assert "-R" in cmd


def test_build_pager_cmd_more_no_flags():
    assert _build_pager_cmd("more") == ["more"]


def test_build_pager_cmd_full_path_less():
    cmd = _build_pager_cmd("/usr/bin/less")
    assert "-R" in cmd


# ---------------------------------------------------------------------------
# should_page
# ---------------------------------------------------------------------------

def test_should_page_false_when_dest_is_file():
    assert should_page(force=None, dest="output.txt") is False


def test_should_page_force_true_on_stdout():
    assert should_page(force=True, dest=None) is True


def test_should_page_force_false_overrides_tty():
    assert should_page(force=False, dest=None) is False


def test_should_page_auto_true_when_tty_and_pager_available():
    with patch("os.isatty", return_value=True), \
         patch("logslice.pager._detect_pager", return_value="less"):
        assert should_page(force=None, dest=None) is True


def test_should_page_auto_false_when_not_tty():
    with patch("os.isatty", return_value=False):
        assert should_page(force=None, dest=None) is False


# ---------------------------------------------------------------------------
# page_lines
# ---------------------------------------------------------------------------

def test_page_lines_raises_when_no_pager():
    with patch("logslice.pager._detect_pager", return_value=None):
        with pytest.raises(RuntimeError, match="No pager found"):
            page_lines(["hello"])


def test_page_lines_writes_to_pager_stdin():
    mock_stdin = MagicMock()
    mock_stdin.closed = False
    mock_proc = MagicMock()
    mock_proc.stdin = mock_stdin

    with patch("subprocess.Popen", return_value=mock_proc), \
         patch("logslice.pager._detect_pager", return_value="less"):
        page_lines(["line one", "line two"])

    calls = [str(c) for c in mock_stdin.write.call_args_list]
    assert any("line one" in c for c in calls)
    assert any("line two" in c for c in calls)


def test_page_lines_uses_explicit_pager():
    mock_stdin = MagicMock()
    mock_stdin.closed = False
    mock_proc = MagicMock()
    mock_proc.stdin = mock_stdin

    with patch("subprocess.Popen", return_value=mock_proc) as mock_popen:
        page_lines(["x"], pager="more")
        assert mock_popen.call_args[0][0][0] == "more"
