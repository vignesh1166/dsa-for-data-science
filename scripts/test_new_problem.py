"""Tests for the problem stub generator."""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from new_problem import (  # noqa: E402
    NewProblemError,
    create_problem,
    kebab_case,
    resolve_pattern,
    snake_case,
    title_case,
)

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A throwaway repo root with the real templates available."""
    (tmp_path / "DSA").mkdir()
    (tmp_path / "sql").mkdir()
    return tmp_path


def make(repo: Path, **kwargs) -> list[Path]:
    defaults = {
        "number": 238,
        "title": "Product of Array Except Self",
        "difficulty": "Medium",
        "pattern": "arrays/traversal",
        "link": "",
        "root": repo,
        "templates": TEMPLATES,
        "today": dt.date(2026, 10, 12),
    }
    return create_problem(**{**defaults, **kwargs})


def test_snake_and_kebab_case() -> None:
    assert snake_case("Product of Array Except Self") == "product_of_array_except_self"
    assert snake_case("Best Time to Buy and Sell Stock II") == "best_time_to_buy_and_sell_stock_ii"
    assert snake_case("Two Sum!!  ") == "two_sum"
    assert kebab_case("Product of Array Except Self") == "product-of-array-except-self"


def test_snake_case_rejects_empty_title() -> None:
    with pytest.raises(NewProblemError):
        snake_case("!!!")


def test_title_case_strips_topic_number() -> None:
    assert title_case("01_arrays") == "Arrays"
    assert title_case("two_pointers") == "Two Pointers"


def test_resolve_pattern_maps_short_topic_to_numbered_directory(tmp_path: Path) -> None:
    assert resolve_pattern("arrays/traversal", tmp_path) == (
        tmp_path / "DSA" / "01_arrays" / "traversal"
    )
    assert resolve_pattern("dp/one_dimension", tmp_path) == (
        tmp_path / "DSA" / "09_dynamic_programming" / "one_dimension"
    )


def test_resolve_pattern_accepts_the_numbered_form(tmp_path: Path) -> None:
    assert resolve_pattern("01_arrays/traversal", tmp_path) == (
        tmp_path / "DSA" / "01_arrays" / "traversal"
    )


def test_resolve_pattern_routes_sql_outside_patterns(tmp_path: Path) -> None:
    assert resolve_pattern("sql/subqueries_ctes", tmp_path) == (
        tmp_path / "sql" / "subqueries_ctes"
    )


@pytest.mark.parametrize("pattern", ["arrays", "", "a/b/c", "nope/traversal"])
def test_resolve_pattern_rejects_bad_patterns(tmp_path: Path, pattern: str) -> None:
    with pytest.raises(NewProblemError):
        resolve_pattern(pattern, tmp_path)


def test_create_problem_writes_the_expected_path(repo: Path) -> None:
    written = make(repo)
    target = repo / "DSA" / "01_arrays" / "traversal" / "lc0238_product_of_array_except_self.py"
    assert target in written
    assert target.exists()


def test_create_problem_fills_every_placeholder(repo: Path) -> None:
    target = make(repo)[0]
    text = target.read_text(encoding="utf-8")
    assert "{{" not in text
    assert "Problem: LC 238 | Product of Array Except Self" in text
    assert "Difficulty: Medium" in text
    assert "Pattern: arrays/traversal" in text
    assert "Status: todo" in text
    assert "Added: 2026-10-12" in text
    assert "def product_of_array_except_self(" in text


def test_create_problem_derives_the_leetcode_link(repo: Path) -> None:
    text = make(repo)[0].read_text(encoding="utf-8")
    assert "Link: https://leetcode.com/problems/product-of-array-except-self/" in text


def test_create_problem_keeps_an_explicit_link(repo: Path) -> None:
    text = make(repo, link="https://example.com/x")[0].read_text(encoding="utf-8")
    assert "Link: https://example.com/x" in text


def test_create_problem_honours_a_function_name_override(repo: Path) -> None:
    text = make(repo, func="product_except_self")[0].read_text(encoding="utf-8")
    assert "def product_except_self(" in text
    assert "def product_of_array_except_self(" not in text


def test_create_problem_stubs_raise_not_implemented(repo: Path) -> None:
    text = make(repo)[0].read_text(encoding="utf-8")
    assert text.count("raise NotImplementedError") == 2
    assert text.count('@pytest.mark.skip(reason="todo")') == 3


def test_create_problem_creates_pattern_and_topic_readmes(repo: Path) -> None:
    make(repo)
    subpattern = repo / "DSA" / "01_arrays" / "traversal" / "README.md"
    topic = repo / "DSA" / "01_arrays" / "README.md"
    assert subpattern.exists() and topic.exists()
    assert subpattern.read_text(encoding="utf-8").startswith("# Traversal")
    assert topic.read_text(encoding="utf-8").startswith("# Arrays")
    assert "<!-- PROBLEMS:START -->" in subpattern.read_text(encoding="utf-8")


def test_create_problem_leaves_an_existing_readme_alone(repo: Path) -> None:
    directory = repo / "DSA" / "01_arrays" / "traversal"
    directory.mkdir(parents=True)
    (directory / "README.md").write_text("# Mine\n", encoding="utf-8")
    make(repo)
    assert (directory / "README.md").read_text(encoding="utf-8") == "# Mine\n"


def test_create_problem_refuses_to_overwrite(repo: Path) -> None:
    make(repo)
    with pytest.raises(NewProblemError, match="refusing to overwrite"):
        make(repo)


def test_create_problem_rejects_an_unknown_difficulty(repo: Path) -> None:
    with pytest.raises(NewProblemError, match="difficulty"):
        make(repo, difficulty="Trivial")


def test_create_problem_writes_sql_for_an_sql_pattern(repo: Path) -> None:
    written = make(
        repo,
        number=176,
        title="Second Highest Salary",
        pattern="sql/subqueries_ctes",
        difficulty="Medium",
    )
    target = repo / "sql" / "subqueries_ctes" / "lc0176_second_highest_salary.sql"
    assert target in written
    text = target.read_text(encoding="utf-8")
    assert text.startswith("-- Problem: LC 176 | Second Highest Salary")
    assert "{{" not in text
