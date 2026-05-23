"""Deduplicate consecutive or global repeated log lines."""

from __future__ import annotations

from collections import OrderedDict
from typing import Iterable, Iterator, Tuple


def dedup_consecutive(lines: Iterable[str]) -> Iterator[Tuple[str, int]]:
    """Yield (line, count) collapsing consecutive duplicate lines.

    Args:
        lines: Iterable of raw log line strings.

    Yields:
        Tuples of (line, repeat_count) where repeat_count >= 1.
    """
    prev: str | None = None
    count = 0

    for line in lines:
        if line == prev:
            count += 1
        else:
            if prev is not None:
                yield prev, count
            prev = line
            count = 1

    if prev is not None:
        yield prev, count


def dedup_global(
    lines: Iterable[str], max_cache: int = 10_000
) -> Iterator[str]:
    """Yield only the first occurrence of each unique line.

    Uses an OrderedDict as a bounded LRU-style cache to limit memory use.

    Args:
        lines: Iterable of raw log line strings.
        max_cache: Maximum number of unique lines to remember.

    Yields:
        Lines that have not been seen before (within cache window).
    """
    seen: OrderedDict[str, None] = OrderedDict()

    for line in lines:
        if line in seen:
            seen.move_to_end(line)
            continue
        seen[line] = None
        if len(seen) > max_cache:
            seen.popitem(last=False)
        yield line


def format_collapsed(line: str, count: int) -> str:
    """Format a collapsed duplicate entry with its repeat count.

    Args:
        line: The log line text.
        count: Number of times the line appeared consecutively.

    Returns:
        Original line if count == 1, otherwise appends a repeat annotation.
    """
    if count == 1:
        return line
    return f"{line}  [repeated {count}x]"
