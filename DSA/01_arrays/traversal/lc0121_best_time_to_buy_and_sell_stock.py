"""
Problem: LC 121 | Best Time to Buy and Sell Stock
Difficulty: Easy
Pattern: arrays/traversal
Link: https://leetcode.com/problems/best-time-to-buy-and-sell-stock/
Status: todo
Source: own
Added: 2026-10-12
Revisit: none
Time: TODO
Space: TODO

Summary:
    TODO: what this problem asks, in your own words.

Key insight:
    TODO: the one idea that makes the optimal solution work.

Mistakes:
    - TODO: what you got wrong on the first attempt.
"""

import random

import pytest

# (input, expected) straight from the problem statement.
EXAMPLES: list[tuple[list[int], int]] = [
    ([7, 1, 5, 3, 6, 4], 5),
    ([7, 6, 4, 3, 1], 0),
]

# Inputs worth checking on their own: empty, single element, duplicates, negatives, extremes.
# Each is asserted against _brute, so no expected value has to be worked out by hand.
EDGES: list[list[int]] = [
    [],
    [5],
    [5, 5],
    [1, 2],
    [2, 1],
    [0, 0, 0],
    [10000, 1, 10000],
]


def _brute(prices: list[int]) -> int:
    """Obviously-correct reference implementation. Write this one first."""
    raise NotImplementedError


def max_profit(prices: list[int]) -> int:
    """Optimal solution. Write this second."""
    raise NotImplementedError


@pytest.mark.skip(reason="todo")
def test_examples() -> None:
    for prices, expected in EXAMPLES:
        assert max_profit(prices) == expected, prices


@pytest.mark.skip(reason="todo")
def test_edges() -> None:
    for prices in EDGES:
        assert max_profit(prices) == _brute(prices), prices


@pytest.mark.skip(reason="todo")
def test_matches_brute_force() -> None:
    rng = random.Random(0)
    for _ in range(200):
        prices = [rng.randint(0, 30) for _ in range(rng.randint(0, 12))]
        assert max_profit(prices) == _brute(prices), prices
