"""Interactive pager support for logslice output."""

from __future__ import annotations

import os
import shutil
import subprocess
from typing import Iterable, Iterator


DEFAULT_PAGERS = ["less", "more"]
_LESS_FLAGS = ["-R", "-S", "-X", "-F"]


def _detect_pager() -> str | None:
    """Return the first available pager command, or None."""
    for pager in DEFAULT_PAGERS:
        if shutil.which(pager):
            return pager
    return None


def _build_pager_cmd(pager: str) -> list[str]:
    """Build the pager command list, adding flags for 'less'."""
    if os.path.basename(pager) == "less":
        return [pager] + _LESS_FLAGS
    return [pager]


def should_page(force: bool | None, dest: str | None) -> bool:
    """Determine whether paging should be activated.

    Args:
        force: Explicit True/False override; None means auto-detect.
        dest: Output destination path; paging only applies to stdout (None).

    Returns:
        True if lines should be sent through a pager.
    """
    if dest is not None:
        return False
    if force is not None:
        return force
    return os.isatty(1) and _detect_pager() is not None


def page_lines(lines: Iterable[str], pager: str | None = None) -> None:
    """Write *lines* through an interactive pager process.

    Args:
        lines: Iterable of text lines (newlines not required).
        pager: Explicit pager binary; auto-detected when None.

    Raises:
        RuntimeError: If no pager is available on the system.
    """
    resolved = pager or _detect_pager()
    if resolved is None:
        raise RuntimeError("No pager found on PATH (tried: less, more).")

    cmd = _build_pager_cmd(resolved)
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, text=True)
    try:
        assert proc.stdin is not None
        for line in lines:
            proc.stdin.write(line if line.endswith("\n") else line + "\n")
        proc.stdin.close()
        proc.wait()
    except BrokenPipeError:
        pass
    finally:
        if proc.stdin and not proc.stdin.closed:
            proc.stdin.close()
        proc.wait()
