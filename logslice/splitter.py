"""Split a log stream into chunks by line count or time window."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable, Iterator, List, Optional, Tuple

from logslice.reader import parse_timestamp

LogLine = str
Chunk = List[LogLine]


def split_by_count(lines: Iterable[LogLine], chunk_size: int) -> Iterator[Chunk]:
    """Yield successive chunks of *chunk_size* lines."""
    if chunk_size < 1:
        raise ValueError(f"chunk_size must be >= 1, got {chunk_size}")

    chunk: Chunk = []
    for line in lines:
        chunk.append(line)
        if len(chunk) == chunk_size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def split_by_time(
    lines: Iterable[LogLine],
    window: timedelta,
    ts_format: str = "%Y-%m-%d %H:%M:%S",
) -> Iterator[Chunk]:
    """Yield chunks where each chunk spans at most *window* of log time.

    Lines whose timestamp cannot be parsed are attached to the current chunk.
    """
    if window.total_seconds() <= 0:
        raise ValueError("window must be a positive timedelta")

    chunk: Chunk = []
    window_start: Optional[datetime] = None

    for line in lines:
        ts = parse_timestamp(line, ts_format)
        if ts is None:
            chunk.append(line)
            continue

        if window_start is None:
            window_start = ts

        if ts - window_start > window:
            if chunk:
                yield chunk
            chunk = [line]
            window_start = ts
        else:
            chunk.append(line)

    if chunk:
        yield chunk


def chunk_count(chunks: Iterable[Chunk]) -> Tuple[int, int]:
    """Return (number_of_chunks, total_lines) for a sequence of chunks."""
    num_chunks = 0
    total_lines = 0
    for chunk in chunks:
        num_chunks += 1
        total_lines += len(chunk)
    return num_chunks, total_lines
