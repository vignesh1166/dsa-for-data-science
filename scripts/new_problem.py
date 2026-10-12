#!/usr/bin/env python3
"""Create a new todo problem stub from the templates in templates/.

The numbered topic directories are reserved here rather than created up front: a pattern
directory and its README skeleton appear the first time a problem is added to it.

    python scripts/new_problem.py --number 238 --title "Product of Array Except Self" \
        --difficulty Medium --pattern arrays/traversal \
        --link https://leetcode.com/problems/product-of-array-except-self/
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_ROOT = "DSA"
TEMPLATES = ROOT / "templates"

DIFFICULTIES = ("Easy", "Medium", "Hard")

# Reserved topic numbering. Directories are created on demand, not up front.
TOPICS: dict[str, str] = {
    "arrays": "01_arrays",
    "strings": "02_strings",
    "linked_lists": "03_linked_lists",
    "stacks_queues": "04_stacks_queues",
    "trees": "05_trees",
    "graphs": "06_graphs",
    "heaps": "07_heaps_priority_queues",
    "binary_search": "08_binary_search",
    "dp": "09_dynamic_programming",
    "greedy": "10_greedy_intervals",
}


class NewProblemError(Exception):
    """Raised when a stub cannot be created."""


def snake_case(title: str) -> str:
    """Turn a problem title into a snake_case identifier fragment."""
    cleaned = re.sub(r"[^0-9a-zA-Z]+", "_", title).strip("_").lower()
    if not cleaned:
        raise NewProblemError(f"title {title!r} has no usable characters")
    return re.sub(r"_+", "_", cleaned)


def kebab_case(title: str) -> str:
    """Turn a problem title into the kebab-case form LeetCode uses in URLs."""
    return snake_case(title).replace("_", "-")


def title_case(slug: str) -> str:
    """Turn a directory name such as 01_arrays or two_pointers into a readable heading."""
    words = re.sub(r"^\d+_", "", slug).split("_")
    return " ".join(word.capitalize() for word in words)


def resolve_pattern(pattern: str, root: Path) -> Path:
    """Resolve a short pattern such as arrays/traversal to its directory under DSA/.

    SQL patterns (sql/<area>) resolve to the sql/ tree instead and are returned as-is.
    """
    parts = [part for part in pattern.strip().strip("/").split("/") if part]
    if len(parts) != 2:
        raise NewProblemError(
            f"pattern {pattern!r} must be '<topic>/<subpattern>', e.g. 'arrays/traversal'"
        )
    topic, subpattern = parts
    if topic == "sql":
        return root / "sql" / subpattern
    if topic in TOPICS:
        return root / PROBLEMS_ROOT / TOPICS[topic] / subpattern
    if topic in set(TOPICS.values()):
        return root / PROBLEMS_ROOT / topic / subpattern
    known = ", ".join(sorted(TOPICS))
    raise NewProblemError(f"unknown topic {topic!r} in pattern {pattern!r}; known topics: {known}")


def render(template: str, fields: dict[str, str]) -> str:
    """Substitute every {{KEY}} placeholder, failing loudly on any left over."""
    out = template
    for key, value in fields.items():
        out = out.replace("{{" + key + "}}", value)
    leftover = re.findall(r"\{\{(\w+)\}\}", out)
    if leftover:
        raise NewProblemError(f"template placeholders left unfilled: {sorted(set(leftover))}")
    return out


def ensure_pattern_readme(directory: Path, templates: Path) -> Path | None:
    """Create the pattern README skeleton if the directory does not have one yet."""
    readme = directory / "README.md"
    if readme.exists():
        return None
    template = (templates / "pattern_readme.md.tmpl").read_text(encoding="utf-8")
    readme.write_text(
        render(template, {"PATTERN_TITLE": title_case(directory.name)}), encoding="utf-8"
    )
    return readme


def ensure_topic_readme(directory: Path, templates: Path) -> Path | None:
    """Create the parent topic README skeleton if it does not exist yet."""
    parent = directory.parent
    if parent.name == PROBLEMS_ROOT or not parent.name.startswith(tuple("0123456789")):
        return None
    return ensure_pattern_readme(parent, templates)


def create_problem(
    *,
    number: int,
    title: str,
    difficulty: str,
    pattern: str,
    link: str,
    root: Path = ROOT,
    templates: Path | None = None,
    today: dt.date | None = None,
    func: str | None = None,
) -> list[Path]:
    """Create the stub files for one problem and return every path written."""
    if difficulty not in DIFFICULTIES:
        raise NewProblemError(f"difficulty must be one of {DIFFICULTIES}, got {difficulty!r}")
    templates = templates or (root / "templates")
    today = today or dt.date.today()
    directory = resolve_pattern(pattern, root)
    is_sql = directory.parent.name == "sql"

    slug = snake_case(title)
    stem = f"lc{number:04d}_{slug}"
    target = directory / (f"{stem}.sql" if is_sql else f"{stem}.py")
    if target.exists():
        raise NewProblemError(f"{target.relative_to(root)} already exists; refusing to overwrite")

    directory.mkdir(parents=True, exist_ok=True)
    fields = {
        "PROBLEM_ID": f"LC {number}",
        "TITLE": title,
        "DIFFICULTY": difficulty,
        "PATTERN": pattern,
        "LINK": link or f"https://leetcode.com/problems/{kebab_case(title)}/",
        "ADDED": today.isoformat(),
        "FUNC": func or slug,
    }
    template_name = "problem.sql.tmpl" if is_sql else "problem.py.tmpl"
    template = (templates / template_name).read_text(encoding="utf-8")
    target.write_text(render(template, fields), encoding="utf-8")

    written = [target]
    for extra in (
        ensure_pattern_readme(directory, templates),
        ensure_topic_readme(directory, templates),
    ):
        if extra is not None:
            written.append(extra)
    return written


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--number", required=True, type=int, help="LeetCode problem number")
    parser.add_argument("--title", required=True, help="problem title, as LeetCode writes it")
    parser.add_argument("--difficulty", required=True, choices=DIFFICULTIES)
    parser.add_argument(
        "--pattern", required=True, help="e.g. arrays/traversal or sql/subqueries_ctes"
    )
    parser.add_argument("--link", default="", help="problem URL; derived from the title if omitted")
    parser.add_argument("--func", default=None, help="override the generated function name")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        written = create_problem(
            number=args.number,
            title=args.title,
            difficulty=args.difficulty,
            pattern=args.pattern,
            link=args.link,
            func=args.func,
        )
    except NewProblemError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for path in written:
        print(path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
