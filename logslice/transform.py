"""Line transformation utilities for logslice.

Provides composable, memory-efficient transformations that operate on
streams of log lines: stripping ANSI codes, truncating long lines, and
adding a sequential line-number prefix.
"""

from __future__ import annotations

import re
from typing import Generator, Iterable

_ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*[mGKHF]")


def strip_ansi(
    lines: Iterable[str],
) -> Generator[str, None, None]:
    """Yield lines with ANSI escape sequences removed."""
    for line in lines:
        yield _ANSI_ESCAPE.sub("", line)


def truncate_lines(
    lines: Iterable[str],
    max_length: int,
    suffix: str = "…",
) -> Generator[str, None, None]:
    """Yield lines truncated to *max_length* characters.

    Lines longer than *max_length* have *suffix* appended (and the line
    body is shortened so that ``len(result) == max_length``).

    Args:
        lines: Input iterable of log lines.
        max_length: Maximum allowed length; must be > len(suffix).
        suffix: String appended to truncated lines.

    Raises:
        ValueError: If *max_length* is not greater than ``len(suffix)``.
    """
    if max_length <= len(suffix):
        raise ValueError(
            f"max_length ({max_length}) must be > len(suffix) ({len(suffix)})"
        )
    cut = max_length - len(suffix)
    for line in lines:
        if len(line) > max_length:
            yield line[:cut] + suffix
        else:
            yield line


def add_line_numbers(
    lines: Iterable[str],
    start: int = 1,
    template: str = "{n:>6}: {line}",
) -> Generator[str, None, None]:
    """Yield lines prefixed with a sequential line number.

    Args:
        lines: Input iterable of log lines.
        start: Starting line number (default 1).
        template: Format string with ``{n}`` (number) and ``{line}`` placeholders.
    """
    for n, line in enumerate(lines, start=start):
        yield template.format(n=n, line=line)


def apply_transforms(
    lines: Iterable[str],
    *,
    strip_ansi_codes: bool = False,
    max_length: int | None = None,
    number_lines: bool = False,
    line_number_start: int = 1,
) -> Iterable[str]:
    """Apply a standard set of transformations to *lines* in a fixed order.

    Order: strip ANSI → truncate → number lines.
    """
    result: Iterable[str] = lines
    if strip_ansi_codes:
        result = strip_ansi(result)
    if max_length is not None:
        result = truncate_lines(result, max_length)
    if number_lines:
        result = add_line_numbers(result, start=line_number_start)
    return result
