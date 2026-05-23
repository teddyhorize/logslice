"""Tail utilities for logslice.

Provides memory-efficient ways to retrieve the last N lines of a stream
and to follow a file as new lines are appended (like ``tail -f``).
"""

from __future__ import annotations

import collections
import time
from pathlib import Path
from typing import Generator, Iterable


def last_n_lines(
    lines: Iterable[str],
    n: int,
) -> list[str]:
    """Return the last *n* lines from *lines* using a fixed-size deque.

    Args:
        lines: Input iterable of log lines.
        n: Number of tail lines to keep; must be >= 1.

    Raises:
        ValueError: If *n* is less than 1.
    """
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    return list(collections.deque(lines, maxlen=n))


def follow(
    path: Path | str,
    poll_interval: float = 0.25,
    encoding: str = "utf-8",
) -> Generator[str, None, None]:
    """Yield new lines appended to *path* indefinitely (like ``tail -f``).

    Seeks to the end of the file on first open so only *new* content is
    emitted.  Intended for interactive use; callers should handle
    ``KeyboardInterrupt`` to stop iteration.

    Args:
        path: Path to the log file to follow.
        poll_interval: Seconds to sleep between read attempts.
        encoding: File encoding.
    """
    path = Path(path)
    with path.open(encoding=encoding) as fh:
        fh.seek(0, 2)  # seek to end
        while True:
            line = fh.readline()
            if line:
                yield line.rstrip("\n")
            else:
                time.sleep(poll_interval)


def head_n_lines(
    lines: Iterable[str],
    n: int,
) -> Generator[str, None, None]:
    """Yield at most the first *n* lines from *lines*.

    Args:
        lines: Input iterable of log lines.
        n: Maximum number of lines to yield; must be >= 1.

    Raises:
        ValueError: If *n* is less than 1.
    """
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    for i, line in enumerate(lines):
        if i >= n:
            break
        yield line
