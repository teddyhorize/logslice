"""Output formatting utilities for logslice."""

import json
from typing import Iterator, Optional


DEFAULT_FORMAT = "plain"
SUPPORTED_FORMATS = ("plain", "json", "count")


def format_line_plain(line: str, line_number: Optional[int] = None) -> str:
    """Return the line as-is, optionally prefixed with line number."""
    if line_number is not None:
        return f"{line_number}: {line}"
    return line


def format_line_json(line: str, line_number: Optional[int] = None) -> str:
    """Return the line serialised as a JSON object."""
    record = {"line": line}
    if line_number is not None:
        record["line_number"] = line_number
    return json.dumps(record)


def format_lines(
    lines: Iterator[str],
    fmt: str = DEFAULT_FORMAT,
    show_line_numbers: bool = False,
) -> Iterator[str]:
    """Yield formatted versions of each line.

    Args:
        lines: Iterator of raw log lines (stripped of trailing newline).
        fmt: Output format — one of 'plain', 'json', or 'count'.
        show_line_numbers: Prefix each line with its 1-based index.

    Yields:
        Formatted string for each line, or a single count summary when
        ``fmt`` is ``'count'``.

    Raises:
        ValueError: If *fmt* is not a supported format.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format {fmt!r}. Choose from: {SUPPORTED_FORMATS}"
        )

    if fmt == "count":
        total = sum(1 for _ in lines)
        yield str(total)
        return

    for idx, line in enumerate(lines, start=1):
        lineno = idx if show_line_numbers else None
        if fmt == "json":
            yield format_line_json(line, lineno)
        else:
            yield format_line_plain(line, lineno)
