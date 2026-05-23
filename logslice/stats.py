"""Statistics collection for log slicing operations."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class SliceStats:
    """Holds statistics gathered during a log slice operation."""

    total_lines: int = 0
    matched_lines: int = 0
    skipped_lines: int = 0
    first_timestamp: Optional[datetime] = None
    last_timestamp: Optional[datetime] = None
    pattern_hits: int = 0
    time_filter_hits: int = 0

    @property
    def match_rate(self) -> float:
        """Return fraction of lines that matched (0.0 if no lines)."""
        if self.total_lines == 0:
            return 0.0
        return self.matched_lines / self.total_lines

    def to_dict(self) -> dict:
        """Serialize stats to a plain dictionary."""
        return {
            "total_lines": self.total_lines,
            "matched_lines": self.matched_lines,
            "skipped_lines": self.skipped_lines,
            "match_rate": round(self.match_rate, 4),
            "first_timestamp": self.first_timestamp.isoformat() if self.first_timestamp else None,
            "last_timestamp": self.last_timestamp.isoformat() if self.last_timestamp else None,
            "pattern_hits": self.pattern_hits,
            "time_filter_hits": self.time_filter_hits,
        }


def collect_stats(filtered_results) -> tuple:
    """Consume an iterable of (line, timestamp, matched) tuples and return
    (lines, stats) where lines is a list of matched line strings."""
    stats = SliceStats()
    matched_lines = []

    for line, timestamp, matched in filtered_results:
        stats.total_lines += 1
        if timestamp is not None:
            if stats.first_timestamp is None:
                stats.first_timestamp = timestamp
            stats.last_timestamp = timestamp
        if matched:
            stats.matched_lines += 1
            matched_lines.append(line)
        else:
            stats.skipped_lines += 1

    return matched_lines, stats
