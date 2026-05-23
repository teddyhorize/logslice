"""Tests for logslice.sampler."""

from __future__ import annotations

import pytest

from logslice.sampler import reservoir_sample, sample_every_nth, sample_random


# ---------------------------------------------------------------------------
# sample_every_nth
# ---------------------------------------------------------------------------

def test_every_nth_n1_returns_all():
    lines = ["a", "b", "c", "d"]
    assert list(sample_every_nth(lines, 1)) == lines


def test_every_nth_n2_returns_even_indexed():
    lines = ["a", "b", "c", "d", "e"]
    assert list(sample_every_nth(lines, 2)) == ["a", "c", "e"]


def test_every_nth_n_larger_than_input():
    lines = ["a", "b", "c"]
    assert list(sample_every_nth(lines, 10)) == ["a"]


def test_every_nth_empty_input():
    assert list(sample_every_nth([], 3)) == []


def test_every_nth_invalid_n_raises():
    with pytest.raises(ValueError, match="n must be >= 1"):
        list(sample_every_nth(["a"], 0))


# ---------------------------------------------------------------------------
# sample_random
# ---------------------------------------------------------------------------

def test_sample_random_rate_1_returns_all():
    lines = ["a", "b", "c", "d"]
    assert list(sample_random(lines, 1.0, seed=42)) == lines


def test_sample_random_rate_0_returns_nothing():
    lines = ["a", "b", "c"]
    assert list(sample_random(lines, 0.0, seed=42)) == []


def test_sample_random_partial_rate_is_reproducible():
    lines = [str(i) for i in range(100)]
    result1 = list(sample_random(lines, 0.5, seed=7))
    result2 = list(sample_random(lines, 0.5, seed=7))
    assert result1 == result2
    assert 0 < len(result1) < 100


def test_sample_random_invalid_rate_low_raises():
    with pytest.raises(ValueError, match="rate must be in"):
        list(sample_random(["a"], -0.1))


def test_sample_random_invalid_rate_high_raises():
    with pytest.raises(ValueError, match="rate must be in"):
        list(sample_random(["a"], 1.1))


def test_sample_random_empty_input():
    assert list(sample_random([], 0.5, seed=0)) == []


# ---------------------------------------------------------------------------
# reservoir_sample
# ---------------------------------------------------------------------------

def test_reservoir_sample_k_larger_than_input_returns_all():
    lines = ["a", "b", "c"]
    result = reservoir_sample(lines, k=10, seed=0)
    assert sorted(result) == sorted(lines)


def test_reservoir_sample_k1_returns_one_item():
    lines = ["a", "b", "c", "d", "e"]
    result = reservoir_sample(lines, k=1, seed=99)
    assert len(result) == 1
    assert result[0] in lines


def test_reservoir_sample_exact_k():
    lines = [str(i) for i in range(50)]
    result = reservoir_sample(lines, k=10, seed=3)
    assert len(result) == 10
    for item in result:
        assert item in lines


def test_reservoir_sample_is_reproducible():
    lines = [str(i) for i in range(200)]
    r1 = reservoir_sample(lines, k=20, seed=42)
    r2 = reservoir_sample(lines, k=20, seed=42)
    assert r1 == r2


def test_reservoir_sample_empty_input_returns_empty():
    assert reservoir_sample([], k=5) == []


def test_reservoir_sample_invalid_k_raises():
    with pytest.raises(ValueError, match="k must be >= 1"):
        reservoir_sample(["a"], k=0)
