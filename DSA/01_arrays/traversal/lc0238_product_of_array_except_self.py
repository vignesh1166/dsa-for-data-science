"""
Problem: LC 238 | Product of Array Except Self
Difficulty: Medium
Pattern: arrays/traversal
Link: https://leetcode.com/problems/product-of-array-except-self/
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
EXAMPLES: list[tuple[list[int], list[int]]] = [
    ([1, 2, 3, 4], [24, 12, 8, 6]),
    ([-1, 1, 0, -3, 3], [0, 0, 9, 0, 0]),
]

# Inputs worth checking on their own: empty, single element, duplicates, negatives, extremes.
# Each is asserted against _brute, so no expected value has to be worked out by hand.
EDGES: list[list[int]] = [
    [],
    [5],
    [0, 0],
    [1, 0, 3],
    [2, 2, 2, 2],
    [-1, -2, -3, -4],
]


def _brute(nums: list[int]) -> list[int]:
    """Obviously-correct reference implementation. Write this one first."""
    raise NotImplementedError


def product_except_self(nums: list[int]) -> list[int]:
    """Optimal solution. Write this second."""
    raise NotImplementedError


@pytest.mark.skip(reason="todo")
def test_examples() -> None:
    for nums, expected in EXAMPLES:
        assert product_except_self(nums) == expected, nums


@pytest.mark.skip(reason="todo")
def test_edges() -> None:
    for nums in EDGES:
        assert product_except_self(nums) == _brute(nums), nums


@pytest.mark.skip(reason="todo")
def test_matches_brute_force() -> None:
    rng = random.Random(0)
    for _ in range(200):
        nums = [rng.randint(-20, 20) for _ in range(rng.randint(0, 12))]
        assert product_except_self(nums) == _brute(nums), nums
