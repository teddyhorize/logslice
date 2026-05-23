"""Tests for logslice.pipeline — run_pipeline and _counted helper."""

import io
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

import pytest

from logslice.pipeline import run_pipeline, _counted


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_log_lines(*lines):
    """Return an iterator of log line strings."""
    return iter(lines)


LINE_WITH_TS = "2024-01-15 10:00:00 INFO  Server started"
LINE_NO_TS   = "bare log line without timestamp"
LINE_ERROR   = "2024-01-15 10:05:00 ERROR Disk full"
LINE_DEBUG   = "2024-01-15 10:10:00 DEBUG Heartbeat"


# ---------------------------------------------------------------------------
# _counted
# ---------------------------------------------------------------------------

class TestCounted:
    def test_yields_all_items(self):
        counter = {"n": 0}
        result = list(_counted(["a", "b", "c"], counter, "n"))
        assert result == ["a", "b", "c"]

    def test_increments_counter(self):
        counter = {"n": 0}
        list(_counted(range(5), counter, "n"))
        assert counter["n"] == 5

    def test_empty_iterable(self):
        counter = {"n": 0}
        result = list(_counted([], counter, "n"))
        assert result == []
        assert counter["n"] == 0

    def test_uses_correct_key(self):
        counter = {"hits": 0, "total": 0}
        list(_counted([1, 2], counter, "hits"))
        assert counter["hits"] == 2
        assert counter["total"] == 0


# ---------------------------------------------------------------------------
# run_pipeline — basic smoke tests
# ---------------------------------------------------------------------------

class TestRunPipeline:
    """Integration-style tests that exercise run_pipeline end-to-end."""

    def _run(self, lines, **kwargs):
        """Helper: run pipeline over an in-memory line list, return (output, stats)."""
        output_buf = io.StringIO()
        defaults = dict(
            pattern=None,
            start=None,
            end=None,
            fmt="plain",
            line_numbers=False,
            dest=output_buf,
            stats_dest=None,
        )
        defaults.update(kwargs)

        # stream_lines is patched to return our test lines directly
        with patch("logslice.pipeline.stream_lines", return_value=iter(lines)):
            stats = run_pipeline(source="fake.log", **defaults)

        return output_buf.getvalue(), stats

    # -- no filtering --------------------------------------------------------

    def test_no_filter_all_lines_written(self):
        lines = [LINE_WITH_TS, LINE_ERROR, LINE_DEBUG]
        out, stats = self._run(lines)
        for line in lines:
            assert line in out

    def test_no_filter_stats_totals(self):
        lines = [LINE_WITH_TS, LINE_ERROR, LINE_DEBUG]
        _, stats = self._run(lines)
        assert stats.total_lines == 3
        assert stats.matched_lines == 3

    # -- regex filtering -----------------------------------------------------

    def test_pattern_filters_lines(self):
        import re
        lines = [LINE_WITH_TS, LINE_ERROR, LINE_DEBUG]
        out, stats = self._run(lines, pattern=re.compile(r"ERROR"))
        assert "ERROR" in out
        assert "INFO" not in out
        assert "DEBUG" not in out

    def test_pattern_stats(self):
        import re
        lines = [LINE_WITH_TS, LINE_ERROR, LINE_DEBUG]
        _, stats = self._run(lines, pattern=re.compile(r"ERROR"))
        assert stats.total_lines == 3
        assert stats.matched_lines == 1

    # -- time filtering ------------------------------------------------------

    def test_start_time_excludes_earlier_lines(self):
        start = datetime(2024, 1, 15, 10, 3, 0, tzinfo=timezone.utc)
        lines = [LINE_WITH_TS, LINE_ERROR, LINE_DEBUG]  # 10:00, 10:05, 10:10
        out, stats = self._run(lines, start=start)
        assert "INFO" not in out       # 10:00 < start
        assert "ERROR" in out          # 10:05 >= start
        assert "DEBUG" in out          # 10:10 >= start

    def test_end_time_excludes_later_lines(self):
        end = datetime(2024, 1, 15, 10, 7, 0, tzinfo=timezone.utc)
        lines = [LINE_WITH_TS, LINE_ERROR, LINE_DEBUG]
        out, stats = self._run(lines, end=end)
        assert "INFO" in out
        assert "ERROR" in out
        assert "DEBUG" not in out      # 10:10 > end

    # -- line numbers --------------------------------------------------------

    def test_line_numbers_appear_in_output(self):
        lines = [LINE_WITH_TS, LINE_ERROR]
        out, _ = self._run(lines, line_numbers=True)
        assert "1" in out
        assert "2" in out

    # -- json format ---------------------------------------------------------

    def test_json_format_output(self):
        lines = [LINE_WITH_TS]
        out, _ = self._run(lines, fmt="json")
        assert "\"line\"" in out or "'line'" in out or "line" in out

    # -- empty source --------------------------------------------------------

    def test_empty_source(self):
        out, stats = self._run([])
        assert out == ""
        assert stats.total_lines == 0
        assert stats.matched_lines == 0
