"""Tests for the README builder: strict header parsing and generated section rendering."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_readme import (  # noqa: E402
    HeaderError,
    collect_problems,
    parse_header,
    progress_table,
    render_targets,
    replace_section,
    revisit_table,
    stats_line,
)

GOOD_HEADER = """\"\"\"
Problem: LC 238 | Product of Array Except Self
Difficulty: Medium
Pattern: arrays/traversal
Link: https://leetcode.com/problems/product-of-array-except-self/
Status: solved
Source: own
Added: 2026-10-01
Revisit: 2026-10-20
Time: O(n)
Space: O(1)

Summary:
    Everything except self.
\"\"\"
"""

ROOT_README = """# repo

<!-- STATS:START -->
<!-- STATS:END -->

## Progress

<!-- PROGRESS:START -->
<!-- PROGRESS:END -->

## Scheduled revisits

<!-- REVISIT:START -->
<!-- REVISIT:END -->
"""

PATTERN_README = """# Traversal

## Problems

<!-- PROBLEMS:START -->
<!-- PROBLEMS:END -->
"""


def write_problem(directory: Path, name: str, header: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text(header, encoding="utf-8")
    return path


def header_with(**overrides: str) -> str:
    """The good header with individual keys replaced, removed (None) or added."""
    lines = GOOD_HEADER.splitlines()
    out: list[str] = []
    for line in lines:
        key = line.split(":", 1)[0]
        if key in overrides:
            value = overrides.pop(key)
            if value is not None:
                out.append(f"{key}: {value}")
            continue
        out.append(line)
    for key, value in overrides.items():
        if value is not None:
            out.insert(2, f"{key}: {value}")
    return "\n".join(out) + "\n"


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A throwaway repo with a root README and one solved array problem."""
    (tmp_path / "README.md").write_text(ROOT_README, encoding="utf-8")
    traversal = tmp_path / "DSA" / "01_arrays" / "traversal"
    traversal.mkdir(parents=True)
    (traversal / "README.md").write_text(PATTERN_README, encoding="utf-8")
    write_problem(traversal, "lc0238_product_of_array_except_self.py", GOOD_HEADER)
    return tmp_path


def test_parse_header_reads_every_field(tmp_path: Path) -> None:
    path = write_problem(tmp_path, "lc0238_x.py", GOOD_HEADER)
    problem = parse_header(path)
    assert problem.problem_id == "LC 238"
    assert problem.title == "Product of Array Except Self"
    assert problem.difficulty == "Medium"
    assert problem.pattern == "arrays/traversal"
    assert problem.status == "solved"
    assert problem.added.isoformat() == "2026-10-01"
    assert problem.revisit.isoformat() == "2026-10-20"
    assert problem.time == "O(n)"


def test_parse_header_accepts_revisit_none(tmp_path: Path) -> None:
    path = write_problem(tmp_path, "lc0238_x.py", header_with(Revisit="none"))
    assert parse_header(path).revisit is None


def test_parse_header_accepts_an_x_drill(tmp_path: Path) -> None:
    path = write_problem(
        tmp_path, "x_running_median.py", header_with(Problem="X running-median | Running Median")
    )
    problem = parse_header(path)
    assert problem.problem_id == "X running-median"
    assert problem.sort_key[0] == 10**9


def test_parse_header_reads_an_sql_comment_header(tmp_path: Path) -> None:
    sql = "\n".join(f"-- {line}".rstrip() for line in GOOD_HEADER.splitlines()[1:-1])
    path = write_problem(tmp_path, "lc0176_second.sql", sql + "\n\nSELECT 1;\n")
    assert parse_header(path).problem_id == "LC 238"


def test_parse_header_rejects_a_missing_docstring(tmp_path: Path) -> None:
    path = write_problem(tmp_path, "lc0001_x.py", "x = 1\n")
    with pytest.raises(HeaderError, match="missing module docstring"):
        parse_header(path)


def test_parse_header_rejects_a_missing_key(tmp_path: Path) -> None:
    path = write_problem(tmp_path, "lc0238_x.py", header_with(Source=None))
    with pytest.raises(HeaderError, match="missing required key"):
        parse_header(path)


def test_parse_header_rejects_an_unknown_key(tmp_path: Path) -> None:
    path = write_problem(tmp_path, "lc0238_x.py", header_with(Mood="good"))
    with pytest.raises(HeaderError, match="unknown header key"):
        parse_header(path)


def test_parse_header_rejects_a_duplicate_key(tmp_path: Path) -> None:
    doubled = GOOD_HEADER.replace("Status: solved", "Status: solved\nStatus: todo")
    path = write_problem(tmp_path, "lc0238_x.py", doubled)
    with pytest.raises(HeaderError, match="duplicate header key"):
        parse_header(path)


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"Problem": "238 Product"}, "Problem must be"),
        ({"Difficulty": "Trivial"}, "Difficulty must be"),
        ({"Pattern": "arrays"}, "Pattern must be"),
        ({"Status": "done"}, "Status must be"),
        ({"Source": "borrowed"}, "Source must be"),
        ({"Added": "12-10-2026"}, "Added must be"),
        ({"Revisit": "soon"}, "Revisit must be"),
    ],
)
def test_parse_header_rejects_bad_values(tmp_path: Path, overrides: dict, message: str) -> None:
    path = write_problem(tmp_path, "lc0238_x.py", header_with(**overrides))
    with pytest.raises(HeaderError, match=message):
        parse_header(path)


def test_parse_header_requires_complexity_once_not_todo(tmp_path: Path) -> None:
    path = write_problem(tmp_path, "lc0238_x.py", header_with(Time="TODO"))
    with pytest.raises(HeaderError, match="Time and Space are required"):
        parse_header(path)


def test_parse_header_allows_todo_complexity_while_todo(tmp_path: Path) -> None:
    path = write_problem(
        tmp_path, "lc0238_x.py", header_with(Status="todo", Time="TODO", Space="TODO")
    )
    assert parse_header(path).time == "TODO"


def test_parse_header_names_the_offending_file(tmp_path: Path) -> None:
    path = write_problem(tmp_path, "lc0009_broken.py", header_with(Status="done"))
    with pytest.raises(HeaderError, match="lc0009_broken.py"):
        parse_header(path)


def test_collect_problems_finds_problems_and_ignores_other_files(repo: Path) -> None:
    traversal = repo / "DSA" / "01_arrays" / "traversal"
    write_problem(traversal, "helper.py", "x = 1\n")
    write_problem(traversal, "x_drill.py", header_with(Problem="X drill | A Drill"))
    found = {problem.problem_id for problem in collect_problems(repo)}
    assert found == {"LC 238", "X drill"}


def test_stats_line_counts_statuses_and_patterns() -> None:
    problems = []
    assert "**0 problems** across **0 patterns**" in stats_line(problems)


def test_render_targets_fills_the_root_sections(repo: Path) -> None:
    targets = render_targets(repo)
    text = targets[repo / "README.md"]
    assert "**1 problem** across **1 pattern** · 1 solved · 0 todo · 0 needs review" in text
    assert "| `arrays/traversal` | 1 | 0 | 0 | 1 |" in text
    assert "| 2026-10-20 |" in text
    assert "DSA/01_arrays/traversal/lc0238_product_of_array_except_self.py" in text


def test_render_targets_fills_the_pattern_table(repo: Path) -> None:
    targets = render_targets(repo)
    readme = repo / "DSA" / "01_arrays" / "traversal" / "README.md"
    text = targets[readme]
    assert "| Problem | Difficulty | Status | Time | Space | Source |" in text
    assert "[LC 238 Product of Array Except Self]" in text
    assert "(lc0238_product_of_array_except_self.py)" in text


def test_render_targets_scopes_a_topic_readme_to_its_subtree(repo: Path) -> None:
    (repo / "DSA" / "01_arrays" / "README.md").write_text(PATTERN_README, encoding="utf-8")
    other = repo / "DSA" / "02_strings" / "sliding_window"
    (other).mkdir(parents=True)
    (other / "README.md").write_text(PATTERN_README, encoding="utf-8")
    write_problem(
        other,
        "lc0003_longest.py",
        header_with(Problem="LC 3 | Longest", Pattern="strings/sliding_window"),
    )
    targets = render_targets(repo)
    arrays = targets[repo / "DSA" / "01_arrays" / "README.md"]
    assert "LC 238" in arrays
    assert "LC 3" not in arrays
    strings = targets[repo / "DSA" / "02_strings" / "sliding_window" / "README.md"]
    assert "LC 3" in strings
    assert "LC 238" not in strings


def test_render_targets_skips_readmes_without_markers(repo: Path) -> None:
    plain = repo / "DSA" / "01_arrays" / "traversal" / "notes.md"
    plain.write_text("# notes\n", encoding="utf-8")
    assert plain not in render_targets(repo)


def test_empty_tables_render_a_placeholder(repo: Path) -> None:
    for path in (repo / "DSA").rglob("lc*.py"):
        path.unlink()
    targets = render_targets(repo)
    assert "_Nothing here yet._" in targets[repo / "README.md"]


def test_revisit_table_lists_only_scheduled_solved_problems(repo: Path) -> None:
    traversal = repo / "DSA" / "01_arrays" / "traversal"
    write_problem(
        traversal,
        "lc0121_best_time.py",
        header_with(Problem="LC 121 | Best Time", Status="todo", Time="TODO", Space="TODO"),
    )
    table = revisit_table(collect_problems(repo), repo)
    assert "LC 238" in table
    assert "LC 121" not in table


def test_progress_table_counts_each_status(repo: Path) -> None:
    traversal = repo / "DSA" / "01_arrays" / "traversal"
    write_problem(
        traversal,
        "lc0121_best_time.py",
        header_with(Problem="LC 121 | Best Time", Status="needs-review"),
    )
    assert "| `arrays/traversal` | 1 | 0 | 1 | 2 |" in progress_table(collect_problems(repo))


def test_replace_section_is_idempotent(repo: Path) -> None:
    first = render_targets(repo)
    for path, content in first.items():
        path.write_text(content, encoding="utf-8")
    assert render_targets(repo) == first


def test_replace_section_requires_markers(tmp_path: Path) -> None:
    with pytest.raises(HeaderError, match="missing"):
        replace_section("# nothing\n", "STATS", "x", tmp_path / "README.md")
