"""Command-line interface for logslice."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from typing import Optional

from logslice.pipeline import run_pipeline
from logslice.pager import should_page, page_lines


def parse_datetime(value: str) -> datetime:
    """Parse an ISO-8601-like datetime string into a datetime object."""
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise argparse.ArgumentTypeError(
        f"Cannot parse datetime: {value!r}. "
        "Expected format: YYYY-MM-DDTHH:MM:SS or YYYY-MM-DD."
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="logslice",
        description="Stream and filter large log files by time range or regex.",
    )
    parser.add_argument("file", nargs="?", default="-", help="Log file path (default: stdin).")
    parser.add_argument("--start", type=parse_datetime, default=None, metavar="DATETIME")
    parser.add_argument("--end", type=parse_datetime, default=None, metavar="DATETIME")
    parser.add_argument("--pattern", default=None, help="Regex pattern to filter lines.")
    parser.add_argument("--output", "-o", default=None, help="Write output to file.")
    parser.add_argument("--format", choices=["plain", "json"], default="plain", dest="fmt")
    parser.add_argument("--numbers", "-n", action="store_true", help="Show line numbers.")
    parser.add_argument("--stats", action="store_true", help="Print match statistics.")
    parser.add_argument("--highlight", action="store_true", help="Highlight regex matches.")
    parser.add_argument(
        "--pager",
        action="store_true",
        default=None,
        help="Force output through a pager (auto-detected by default).",
    )
    parser.add_argument(
        "--no-pager",
        action="store_false",
        dest="pager",
        help="Disable pager even when writing to a terminal.",
    )
    return parser


def run(args: argparse.Namespace) -> None:
    """Execute the logslice pipeline with parsed arguments."""
    use_pager = should_page(force=args.pager, dest=args.output)

    result = run_pipeline(
        source=args.file,
        start=args.start,
        end=args.end,
        pattern=args.pattern,
        fmt=args.fmt,
        numbers=args.numbers,
        highlight=args.highlight,
        dest=args.output,
        show_stats=args.stats,
        pager=use_pager,
    )
    return result


def main(argv: Optional[list[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run(args)
    except BrokenPipeError:
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
