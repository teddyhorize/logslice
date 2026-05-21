"""Stream lines from log files with optional pattern compilation."""

import re
import sys
from datetime import datetime
from typing import Generator, Optional


TIMESTAMP_PATTERNS = [
    re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})"),
    re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"),
    re.compile(r"(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})"),
]

TIMESTAMP_FORMATS = [
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%d/%b/%Y:%H:%M:%S",
]


def compile_pattern(
    pattern: Optional[str],
    ignore_case: bool = False,
) -> Optional[re.Pattern]:
    """Compile a regex pattern string. Returns None if pattern is None."""
    if pattern is None:
        return None
    flags = re.IGNORECASE if ignore_case else 0
    return re.compile(pattern, flags)


def parse_timestamp(line: str) -> Optional[datetime]:
    """Extract and parse a timestamp from a log line. Returns None if not found."""
    for regex, fmt in zip(TIMESTAMP_PATTERNS, TIMESTAMP_FORMATS):
        match = regex.search(line)
        if match:
            try:
                return datetime.strptime(match.group(1), fmt)
            except ValueError:
                continue
    return None


def stream_lines(source: str) -> Generator[str, None, None]:
    """Yield lines from a file path or stdin ('-') without loading into memory."""
    if source == "-":
        yield from sys.stdin
    else:
        with open(source, "r", encoding="utf-8", errors="replace") as fh:
            yield from fh
