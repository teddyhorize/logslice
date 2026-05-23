"""High-level pipeline: read → filter → format → write."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from logslice.filter import filter_lines
from logslice.output import write_lines, write_stats
from logslice.reader import compile_pattern, stream_lines
from logslice.stats import collect_stats


def run_pipeline(
    path: str,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    pattern: Optional[str] = None,
    fmt: str = "plain",
    show_numbers: bool = False,
    dest: Optional[str] = None,
    print_stats: bool = False,
    encoding: str = "utf-8",
) -> dict:
    """Execute the full logslice pipeline.

    Parameters
    ----------
    path:        Path to the log file.
    start:       Inclusive lower bound for timestamp filtering.
    end:         Inclusive upper bound for timestamp filtering.
    pattern:     Regex pattern string to match against each line.
    fmt:         Output format — ``"plain"`` or ``"json"``.
    show_numbers: Prefix output lines with original line numbers.
    dest:        Output file path; ``None`` writes to stdout.
    print_stats: When ``True``, emit a stats summary to stderr / *dest*.
    encoding:    File encoding (default ``"utf-8"``).

    Returns
    -------
    dict
        Stats dictionary produced by :func:`logslice.stats.collect_stats`.
    """
    regex = compile_pattern(pattern)

    raw_stream = stream_lines(path, encoding=encoding)
    filtered = filter_lines(raw_stream, start=start, end=end, pattern=regex)

    # Materialise for stats; still lazy via generator chaining.
    def _counted() -> list[tuple[int, str]]:
        return list(filtered)

    matched_lines = _counted()

    # Count total lines for stats (requires a second pass over the file).
    total = sum(1 for _ in stream_lines(path, encoding=encoding))

    stats = collect_stats(
        total_lines=total,
        matched_lines=matched_lines,
        start=start,
        end=end,
    )

    write_lines(iter(matched_lines), dest=dest, fmt=fmt, show_numbers=show_numbers)

    if print_stats:
        from logslice.stats import to_dict  # local import to avoid circular
        write_stats(to_dict(stats), dest=dest)

    return to_dict(stats)


from logslice.stats import to_dict  # noqa: E402  (module-level re-export)
