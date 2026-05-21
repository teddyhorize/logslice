"""Core streaming log reader with regex and time-range filtering."""

import re
from datetime import datetime
from typing import Iterator, Optional, Pattern


def compile_pattern(pattern: Optional[str]) -> Optional[Pattern]:
    """Compile a regex pattern string, returning None if pattern is None."""
    if pattern is None:
        return None
    return re.compile(pattern)


def parse_timestamp(line: str, fmt: str) -> Optional[datetime]:
    """Attempt to parse a timestamp from the beginning of a log line."""
    # Try progressively shorter prefixes to find a parseable timestamp
    for length in range(min(len(line), 40), 0, -1):
        try:
            return datetime.strptime(line[:length], fmt)
        except ValueError:
            continue
    return None


def stream_lines(
    filepath: str,
    pattern: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    time_fmt: str = "%Y-%m-%d %H:%M:%S",
    encoding: str = "utf-8",
) -> Iterator[str]:
    """
    Stream lines from a log file, optionally filtering by regex and/or time range.

    Args:
        filepath: Path to the log file.
        pattern: Optional regex pattern to filter lines.
        start_time: Only yield lines at or after this time.
        end_time: Only yield lines at or before this time.
        time_fmt: strptime format string for parsing timestamps.
        encoding: File encoding.

    Yields:
        Matching log lines (with newline stripped).
    """
    compiled = compile_pattern(pattern)
    use_time_filter = start_time is not None or end_time is not None

    with open(filepath, "r", encoding=encoding, errors="replace") as fh:
        for raw_line in fh:
            line = raw_line.rstrip("\n")

            if use_time_filter:
                ts = parse_timestamp(line, time_fmt)
                if ts is not None:
                    if start_time and ts < start_time:
                        continue
                    if end_time and ts > end_time:
                        continue

            if compiled is not None and not compiled.search(line):
                continue

            yield line
