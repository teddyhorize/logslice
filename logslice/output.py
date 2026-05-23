"""Output writers for logslice — write filtered results to file or stdout."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Iterable, Iterator, Optional, TextIO

from logslice.formatter import format_line_json, format_line_plain


def _open_dest(dest: Optional[str]) -> tuple[TextIO, bool]:
    """Return (file_handle, should_close). Uses stdout when dest is None."""
    if dest is None:
        return sys.stdout, False
    return open(dest, "w", encoding="utf-8"), True  # noqa: WPS515


def write_lines(
    lines: Iterable[tuple[int, str]],
    dest: Optional[str] = None,
    fmt: str = "plain",
    show_numbers: bool = False,
) -> int:
    """Write formatted lines to *dest* (path string) or stdout.

    Parameters
    ----------
    lines:
        Iterable of (line_number, raw_line) tuples.
    dest:
        File path to write to, or ``None`` for stdout.
    fmt:
        ``"plain"`` or ``"json"``.
    show_numbers:
        Prefix each line with its original line number.

    Returns
    -------
    int
        Number of lines written.
    """
    handle, should_close = _open_dest(dest)
    count = 0
    try:
        for lineno, raw in lines:
            if fmt == "json":
                formatted = format_line_json(lineno, raw, show_numbers)
            else:
                formatted = format_line_plain(lineno, raw, show_numbers)
            handle.write(formatted + "\n")
            count += 1
    finally:
        if should_close:
            handle.close()
    return count


def write_stats(stats: dict, dest: Optional[str] = None) -> None:
    """Append a JSON stats summary to *dest* or print to stderr."""
    payload = json.dumps(stats, default=str, indent=2)
    if dest is None:
        print(payload, file=sys.stderr)
    else:
        with open(dest, "a", encoding="utf-8") as fh:
            fh.write(payload + "\n")
