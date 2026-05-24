"""Merge and interleave multiple log streams in chronological order."""

from __future__ import annotations

import heapq
from typing import Iterable, Iterator, Optional, Tuple

from logslice.reader import parse_timestamp


def _timestamped(lines: Iterable[str], source: str) -> Iterator[Tuple]:
    """Yield (timestamp_or_None, source, line) tuples from a line iterable."""
    for line in lines:
        ts = parse_timestamp(line)
        yield (ts, source, line)


def merge_streams(
    sources: Iterable[Tuple[str, Iterable[str]]],
    *,
    fallback_order: bool = True,
) -> Iterator[str]:
    """Merge multiple named log streams into a single chronological stream.

    Lines without a parseable timestamp are emitted in the order they arrive
    relative to their source when *fallback_order* is True, otherwise they are
    dropped.

    Args:
        sources: Iterable of (name, line_iterable) pairs.
        fallback_order: If True, lines without timestamps are kept in source
            order; if False they are discarded.

    Yields:
        Log lines interleaved in ascending timestamp order.
    """
    iterators = [
        _timestamped(lines, name) for name, lines in sources
    ]

    # Heap entries: (timestamp, tie_breaker, source, line)
    # tie_breaker keeps heapq stable when timestamps are equal.
    heap: list = []
    counter = 0

    def _push(it, entry):
        nonlocal counter
        ts, source, line = entry
        if ts is not None:
            heapq.heappush(heap, (ts, counter, source, line, it))
        elif fallback_order:
            heapq.heappush(heap, (None, counter, source, line, it))
        counter += 1

    # Seed the heap with the first item from each iterator.
    for it in iterators:
        try:
            _push(it, next(it))
        except StopIteration:
            pass

    # Drain the heap, refilling from the exhausted iterator's source.
    while heap:
        ts, _, source, line, it = heapq.heappop(heap)
        yield line
        try:
            _push(it, next(it))
        except StopIteration:
            pass


def merge_files(
    paths: Iterable[str],
    *,
    encoding: str = "utf-8",
    errors: str = "replace",
    fallback_order: bool = True,
) -> Iterator[str]:
    """Open multiple log files and merge them chronologically.

    Args:
        paths: File paths to open and merge.
        encoding: File encoding.
        errors: Error handling for decoding.
        fallback_order: Passed through to :func:`merge_streams`.

    Yields:
        Merged log lines.
    """
    handles = []
    try:
        sources = []
        for path in paths:
            fh = open(path, encoding=encoding, errors=errors)  # noqa: WPS515
            handles.append(fh)
            sources.append((path, fh))
        yield from merge_streams(sources, fallback_order=fallback_order)
    finally:
        for fh in handles:
            fh.close()
