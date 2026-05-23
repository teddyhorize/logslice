"""Line sampling utilities for logslice.

Provides strategies to sample lines from a stream without loading
everything into memory: every-nth, random rate, and reservoir sampling.
"""

from __future__ import annotations

import random
from typing import Generator, Iterable


def sample_every_nth(
    lines: Iterable[str],
    n: int,
) -> Generator[str, None, None]:
    """Yield every n-th line from *lines* (1-based: first kept line is line 1).

    Args:
        lines: Input iterable of log lines.
        n: Step size; must be >= 1.

    Raises:
        ValueError: If *n* is less than 1.
    """
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    for i, line in enumerate(lines):
        if i % n == 0:
            yield line


def sample_random(
    lines: Iterable[str],
    rate: float,
    seed: int | None = None,
) -> Generator[str, None, None]:
    """Yield each line with probability *rate*.

    Args:
        lines: Input iterable of log lines.
        rate: Probability in [0.0, 1.0] that any given line is kept.
        seed: Optional RNG seed for reproducibility.

    Raises:
        ValueError: If *rate* is outside [0.0, 1.0].
    """
    if not (0.0 <= rate <= 1.0):
        raise ValueError(f"rate must be in [0.0, 1.0], got {rate}")
    rng = random.Random(seed)
    for line in lines:
        if rng.random() < rate:
            yield line


def reservoir_sample(
    lines: Iterable[str],
    k: int,
    seed: int | None = None,
) -> list[str]:
    """Return a uniformly random sample of up to *k* lines.

    Uses Vitter's Algorithm R so the full stream is never held in memory
    beyond the reservoir itself.

    Args:
        lines: Input iterable of log lines.
        k: Desired reservoir size; must be >= 1.
        seed: Optional RNG seed for reproducibility.

    Raises:
        ValueError: If *k* is less than 1.
    """
    if k < 1:
        raise ValueError(f"k must be >= 1, got {k}")
    rng = random.Random(seed)
    reservoir: list[str] = []
    for i, line in enumerate(lines):
        if i < k:
            reservoir.append(line)
        else:
            j = rng.randint(0, i)
            if j < k:
                reservoir[j] = line
    return reservoir
