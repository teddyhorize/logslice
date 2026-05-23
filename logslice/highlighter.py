"""Terminal color highlighting for matched regex patterns in log lines."""

import re
from typing import Optional

ANSI_RESET = "\033[0m"
ANSI_YELLOW = "\033[33m"
ANSI_RED = "\033[31m"
ANSI_CYAN = "\033[36m"
ANSI_GREEN = "\033[32m"

COLOR_MAP = {
    "yellow": ANSI_YELLOW,
    "red": ANSI_RED,
    "cyan": ANSI_CYAN,
    "green": ANSI_GREEN,
}


def highlight_match(
    line: str,
    pattern: Optional[re.Pattern],
    color: str = "yellow",
) -> str:
    """Return line with regex matches wrapped in ANSI color codes.

    If pattern is None or no match is found, the original line is returned.
    """
    if pattern is None:
        return line

    ansi_code = COLOR_MAP.get(color, ANSI_YELLOW)

    def _replace(match: re.Match) -> str:
        return f"{ansi_code}{match.group(0)}{ANSI_RESET}"

    return pattern.sub(_replace, line)


def highlight_lines(
    lines: "Iterable[str]",
    pattern: Optional[re.Pattern],
    color: str = "yellow",
    enabled: bool = True,
) -> "Iterable[str]":
    """Yield lines with optional highlighting applied to each.

    When enabled is False, lines are yielded unchanged (e.g. when writing
    to a file where ANSI codes would be noise).
    """
    from typing import Iterable  # local import to avoid circular issues

    if not enabled or pattern is None:
        yield from lines
        return

    for line in lines:
        yield highlight_match(line, pattern, color=color)
