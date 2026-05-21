"""Command-line interface for logslice."""

import argparse
import sys
from datetime import datetime
from typing import Optional

from logslice.reader import compile_pattern, stream_lines
from logslice.filter import filter_lines, count_matches


DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def parse_datetime(value: str) -> datetime:
    """Parse a datetime string in ISO format."""
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid datetime format: '{value}'. Expected ISO format (e.g. 2024-01-15T10:30:00)"
        )


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for logslice CLI."""
    parser = argparse.ArgumentParser(
        prog="logslice",
        description="Stream and filter large log files by time range or regex.",
    )
    parser.add_argument(
        "file",
        nargs="?",
        default="-",
        help="Log file to read (default: stdin)",
    )
    parser.add_argument(
        "--start",
        type=parse_datetime,
        metavar="DATETIME",
        help="Start of time range (ISO format)",
    )
    parser.add_argument(
        "--end",
        type=parse_datetime,
        metavar="DATETIME",
        help="End of time range (ISO format)",
    )
    parser.add_argument(
        "--pattern",
        metavar="REGEX",
        help="Regex pattern to filter lines",
    )
    parser.add_argument(
        "--count",
        action="store_true",
        help="Print count of matching lines instead of lines themselves",
    )
    parser.add_argument(
        "--ignore-case",
        action="store_true",
        help="Case-insensitive pattern matching",
    )
    return parser


def run(argv: Optional[list] = None) -> int:
    """Entry point for the CLI. Returns exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        pattern = compile_pattern(args.pattern, ignore_case=args.ignore_case)
    except Exception as exc:
        print(f"logslice: invalid pattern: {exc}", file=sys.stderr)
        return 2

    try:
        lines = stream_lines(args.file)
        filtered = filter_lines(
            lines,
            start=args.start,
            end=args.end,
            pattern=pattern,
        )

        if args.count:
            print(count_matches(filtered))
        else:
            for line in filtered:
                print(line, end="")
    except FileNotFoundError:
        print(f"logslice: file not found: {args.file}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 0

    return 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
