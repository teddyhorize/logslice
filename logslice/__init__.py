"""logslice — Stream and filter large log files by time range or regex."""

from logslice.filter import filter_lines, count_matches
from logslice.merger import merge_streams, merge_files
from logslice.pipeline import run_pipeline

__all__ = [
    "filter_lines",
    "count_matches",
    "merge_streams",
    "merge_files",
    "run_pipeline",
]
