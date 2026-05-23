"""High-level pipeline that wires reader → filter → dedup → format → output."""

from __future__ import annotations

from typing import Iterator, NamedTuple

from logslice.deduplicator import dedup_consecutive, dedup_global, format_collapsed
from logslice.filter import filter_lines
from logslice.formatter import format_lines
from logslice.output import write_lines
from logslice.reader import compile_pattern, stream_lines
from logslice.stats import collect_stats


class _Counter:
    """Mutable integer counter passed by reference into generators."""

    def __init__(self) -> None:
        self.value = 0


def _counted(iterable, counter: _Counter):
    """Yield every item from *iterable* while incrementing *counter*."""
    for item in iterable:
        counter.value += 1
        yield item


class PipelineResult(NamedTuple):
    total_lines: int
    matched_lines: int


def run_pipeline(
    source: str,
    *,
    start=None,
    end=None,
    pattern: str | None = None,
    fmt: str = "plain",
    numbers: bool = False,
    dest: str = "-",
    dedup: str | None = None,
    dedup_cache: int = 10_000,
    show_stats: bool = False,
) -> PipelineResult:
    """Execute the full logslice pipeline.

    Args:
        source: Path to log file (``"-"`` for stdin).
        start: Optional start datetime for time filtering.
        end: Optional end datetime for time filtering.
        pattern: Optional regex pattern string.
        fmt: Output format – ``"plain"`` or ``"json"``.
        numbers: Prefix lines with line numbers.
        dest: Output destination path (``"-"`` for stdout).
        dedup: Deduplication strategy: ``None``, ``"consecutive"``, or
            ``"global"``.
        dedup_cache: Max cache size for global dedup.
        show_stats: Whether to print stats after output.

    Returns:
        :class:`PipelineResult` with total and matched line counts.
    """
    regex = compile_pattern(pattern)

    total_counter = _Counter()
    matched_counter = _Counter()

    raw: Iterator[str] = stream_lines(source)
    counted_raw = _counted(raw, total_counter)
    filtered = filter_lines(counted_raw, start=start, end=end, pattern=regex)
    counted_filtered = _counted(filtered, matched_counter)

    lines: Iterator[str]
    if dedup == "consecutive":
        lines = (
            format_collapsed(ln, cnt)
            for ln, cnt in dedup_consecutive(counted_filtered)
        )
    elif dedup == "global":
        lines = dedup_global(counted_filtered, max_cache=dedup_cache)
    else:
        lines = counted_filtered

    formatted = format_lines(lines, fmt=fmt, numbers=numbers)
    write_lines(formatted, dest=dest)

    result = PipelineResult(
        total_lines=total_counter.value,
        matched_lines=matched_counter.value,
    )

    if show_stats:
        stats = collect_stats(
            total=result.total_lines,
            matched=result.matched_lines,
        )
        from logslice.output import write_stats
        write_stats(stats, dest=dest)

    return result
