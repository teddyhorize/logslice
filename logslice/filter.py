"""Filter log lines by time range and/or regex pattern."""

from datetime import datetime
from typing import Iterator, Optional
import re

from logslice.reader import parse_timestamp, compile_pattern, stream_lines


def filter_lines(
    filepath: str,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    pattern: Optional[str] = None,
    timestamp_format: str = "%Y-%m-%d %H:%M:%S",
) -> Iterator[str]:
    """Yield log lines matching the given time range and/or regex pattern.

    Args:
        filepath: Path to the log file.
        start: Inclusive start datetime filter.
        end: Inclusive end datetime filter.
        pattern: Optional regex pattern to match against each line.
        timestamp_format: strftime format used to parse timestamps in log lines.

    Yields:
        Lines that satisfy all provided filter criteria.
    """
    compiled = compile_pattern(pattern)
    time_filtering = start is not None or end is not None

    for line in stream_lines(filepath):
        stripped = line.rstrip("\n")

        if time_filtering:
            ts = parse_timestamp(stripped, timestamp_format)
            if ts is not None:
                if start is not None and ts < start:
                    continue
                if end is not None and ts > end:
                    continue
            # If no timestamp found and time filtering is active, skip the line
            elif start is not None or end is not None:
                continue

        if compiled is not None and not compiled.search(stripped):
            continue

        yield stripped


def count_matches(
    filepath: str,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    pattern: Optional[str] = None,
    timestamp_format: str = "%Y-%m-%d %H:%M:%S",
) -> int:
    """Return the number of lines matching the filter criteria."""
    return sum(
        1
        for _ in filter_lines(
            filepath,
            start=start,
            end=end,
            pattern=pattern,
            timestamp_format=timestamp_format,
        )
    )
