#!/usr/bin/env python3
"""Rewrite the generated sections of every README from the problem file headers.

Headers are parsed strictly: a malformed header is an error naming the file, never a silently
skipped problem. Run with --check in CI to assert that nothing would change.

    python scripts/build_readme.py          # rewrite
    python scripts/build_readme.py --check  # exit 1 if anything is out of date
"""

from __future__ import annotations

import argparse
import ast
import datetime as dt
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SEARCH_DIRS = ("DSA", "sql", "pandas_practice")
PROBLEM_GLOBS = ("lc*.py", "x_*.py", "lc*.sql", "x_*.sql")

REQUIRED_KEYS = (
    "Problem",
    "Difficulty",
    "Pattern",
    "Link",
    "Status",
    "Source",
    "Added",
    "Revisit",
)
OPTIONAL_KEYS = ("Time", "Space")

DIFFICULTIES = ("Easy", "Medium", "Hard")
STATUSES = ("todo", "solved", "needs-review")
SOURCES = ("own", "studied-reference")

STATUS_LABEL = {"todo": "todo", "solved": "solved", "needs-review": "needs review"}

PROBLEM_RE = re.compile(r"^(LC \d+|X [a-z0-9][a-z0-9-]*) \| (.+)$")
PATTERN_RE = re.compile(r"^[a-z0-9_]+/[a-z0-9_]+$")
KEY_RE = re.compile(r"^([A-Z][A-Za-z ]*):\s*(.*)$")
EMPTY_SECTION = "_Nothing here yet._"


class HeaderError(Exception):
    """Raised when a problem header cannot be parsed or fails validation."""


@dataclass(frozen=True)
class Problem:
    """One parsed problem header."""

    path: Path
    problem_id: str
    title: str
    difficulty: str
    pattern: str
    link: str
    status: str
    source: str
    added: dt.date
    revisit: dt.date | None
    time: str
    space: str

    @property
    def sort_key(self) -> tuple[int, str]:
        match = re.match(r"LC (\d+)", self.problem_id)
        return (int(match.group(1)) if match else 10**9, self.title)

    @property
    def display(self) -> str:
        return f"{self.problem_id} {self.title}"


def raw_header(path: Path) -> str:
    """Return the header text of a problem file: its docstring, or its leading -- comments."""
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".sql":
        lines: list[str] = []
        for line in text.splitlines():
            if line.startswith("--"):
                lines.append(line[2:].lstrip() if line[2:3] == " " else line[2:])
            elif line.strip() == "":
                if lines:
                    break
            else:
                break
        if not lines:
            raise HeaderError(f"{path}: no leading '--' header comment block")
        return "\n".join(lines)
    try:
        module = ast.parse(text)
    except SyntaxError as exc:
        raise HeaderError(f"{path}: cannot parse file ({exc})") from exc
    docstring = ast.get_docstring(module)
    if docstring is None:
        raise HeaderError(f"{path}: missing module docstring header")
    return docstring


def parse_header(path: Path) -> Problem:
    """Parse and validate one problem header, raising HeaderError naming the file."""
    fields: dict[str, str] = {}
    for line in raw_header(path).splitlines():
        if not line.strip():
            break
        match = KEY_RE.match(line.strip())
        if match is None:
            raise HeaderError(f"{path}: malformed header line {line.strip()!r}")
        key, value = match.group(1).strip(), match.group(2).strip()
        if key in fields:
            raise HeaderError(f"{path}: duplicate header key {key!r}")
        fields[key] = value

    missing = [key for key in REQUIRED_KEYS if key not in fields]
    if missing:
        raise HeaderError(f"{path}: header missing required key(s) {missing}")
    unknown = sorted(set(fields) - set(REQUIRED_KEYS) - set(OPTIONAL_KEYS))
    if unknown:
        raise HeaderError(f"{path}: unknown header key(s) {unknown}")

    problem_match = PROBLEM_RE.match(fields["Problem"])
    if problem_match is None:
        raise HeaderError(
            f"{path}: Problem must be 'LC <number> | <Title>' or 'X <slug> | <Title>', "
            f"got {fields['Problem']!r}"
        )
    if fields["Difficulty"] not in DIFFICULTIES:
        raise HeaderError(f"{path}: Difficulty must be one of {DIFFICULTIES}")
    if not PATTERN_RE.match(fields["Pattern"]):
        raise HeaderError(f"{path}: Pattern must be '<topic>/<subpattern>'")
    if fields["Status"] not in STATUSES:
        raise HeaderError(f"{path}: Status must be one of {STATUSES}")
    if fields["Source"] not in SOURCES:
        raise HeaderError(f"{path}: Source must be one of {SOURCES}")
    if not fields["Link"]:
        raise HeaderError(f"{path}: Link must be a URL or 'none'")

    status = fields["Status"]
    time = fields.get("Time", "TODO")
    space = fields.get("Space", "TODO")
    if status != "todo" and "TODO" in (time, space):
        raise HeaderError(f"{path}: Time and Space are required once Status is not 'todo'")

    return Problem(
        path=path,
        problem_id=problem_match.group(1),
        title=problem_match.group(2).strip(),
        difficulty=fields["Difficulty"],
        pattern=fields["Pattern"],
        link=fields["Link"],
        status=status,
        source=fields["Source"],
        added=parse_date(path, "Added", fields["Added"], allow_none=False),
        revisit=parse_date(path, "Revisit", fields["Revisit"], allow_none=True),
        time=time,
        space=space,
    )


def parse_date(path: Path, key: str, value: str, *, allow_none: bool) -> dt.date | None:
    if allow_none and value == "none":
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        expected = "YYYY-MM-DD or 'none'" if allow_none else "YYYY-MM-DD"
        raise HeaderError(f"{path}: {key} must be {expected}, got {value!r}") from exc


def collect_problems(root: Path = ROOT) -> list[Problem]:
    """Parse every problem file under the searched directories, sorted by path."""
    paths: set[Path] = set()
    for directory in SEARCH_DIRS:
        base = root / directory
        if not base.is_dir():
            continue
        for pattern in PROBLEM_GLOBS:
            paths.update(base.rglob(pattern))
    return [parse_header(path) for path in sorted(paths)]


def link_cell(problem: Problem, relative_to: Path) -> str:
    rel = Path(problem.path).relative_to(relative_to).as_posix()
    return f"[{problem.display}]({rel})"


def problems_table(problems: list[Problem], relative_to: Path) -> str:
    """Render the per-pattern PROBLEMS table."""
    if not problems:
        return EMPTY_SECTION
    rows = [
        "| Problem | Difficulty | Status | Time | Space | Source |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for problem in sorted(problems, key=lambda item: item.sort_key):
        rows.append(
            f"| {link_cell(problem, relative_to)} | {problem.difficulty} "
            f"| {STATUS_LABEL[problem.status]} | {problem.time} | {problem.space} "
            f"| {problem.source} |"
        )
    return "\n".join(rows)


def progress_table(problems: list[Problem]) -> str:
    """Render the root README progress table, one row per pattern."""
    if not problems:
        return EMPTY_SECTION
    rows = [
        "| Pattern | Solved | Todo | Needs review | Total |",
        "| --- | --- | --- | --- | --- |",
    ]
    for pattern in sorted({problem.pattern for problem in problems}):
        group = [problem for problem in problems if problem.pattern == pattern]
        counts = {status: sum(1 for p in group if p.status == status) for status in STATUSES}
        rows.append(
            f"| `{pattern}` | {counts['solved']} | {counts['todo']} "
            f"| {counts['needs-review']} | {len(group)} |"
        )
    return "\n".join(rows)


def revisit_table(problems: list[Problem], root: Path) -> str:
    """Render the scheduled-revisit table: solved problems that have a next date."""
    scheduled = [p for p in problems if p.status == "solved" and p.revisit is not None]
    if not scheduled:
        return EMPTY_SECTION
    rows = ["| Next revisit | Problem | Pattern |", "| --- | --- | --- |"]
    for problem in sorted(scheduled, key=lambda item: (item.revisit, item.sort_key)):
        rows.append(
            f"| {problem.revisit.isoformat()} | {link_cell(problem, root)} | `{problem.pattern}` |"
        )
    return "\n".join(rows)


def stats_line(problems: list[Problem]) -> str:
    """Render the one-line summary for the root README."""
    patterns = {problem.pattern for problem in problems}
    counts = {status: sum(1 for p in problems if p.status == status) for status in STATUSES}
    problem_word = "problem" if len(problems) == 1 else "problems"
    pattern_word = "pattern" if len(patterns) == 1 else "patterns"
    return (
        f"**{len(problems)} {problem_word}** across **{len(patterns)} {pattern_word}** "
        f"· {counts['solved']} solved · {counts['todo']} todo "
        f"· {counts['needs-review']} needs review"
    )


def replace_section(text: str, marker: str, body: str, path: Path) -> str:
    """Replace the content between <!-- MARKER:START --> and <!-- MARKER:END -->."""
    start = f"<!-- {marker}:START -->"
    end = f"<!-- {marker}:END -->"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    if not pattern.search(text):
        raise HeaderError(f"{path}: missing {start} / {end} markers")
    return pattern.sub(f"{start}\n{body}\n{end}", text, count=1)


def render_targets(root: Path = ROOT) -> dict[Path, str]:
    """Compute the desired content of every README that owns a generated section."""
    problems = collect_problems(root)
    targets: dict[Path, str] = {}

    root_readme = root / "README.md"
    if root_readme.exists():
        text = root_readme.read_text(encoding="utf-8")
        text = replace_section(text, "STATS", stats_line(problems), root_readme)
        text = replace_section(text, "PROGRESS", progress_table(problems), root_readme)
        text = replace_section(text, "REVISIT", revisit_table(problems, root), root_readme)
        targets[root_readme] = text

    for directory in SEARCH_DIRS:
        base = root / directory
        if not base.is_dir():
            continue
        for readme in sorted(base.rglob("README.md")):
            text = readme.read_text(encoding="utf-8")
            if "<!-- PROBLEMS:START -->" not in text:
                continue
            scoped = [
                problem for problem in problems if readme.parent in Path(problem.path).parents
            ]
            targets[readme] = replace_section(
                text, "PROBLEMS", problems_table(scoped, readme.parent), readme
            )
    return targets


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--check", action="store_true", help="exit 1 if any generated section is out of date"
    )
    args = parser.parse_args(argv)

    try:
        targets = render_targets()
    except HeaderError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    stale = [
        path for path, content in targets.items() if path.read_text(encoding="utf-8") != content
    ]
    if args.check:
        for path in stale:
            print(f"out of date: {path.relative_to(ROOT)}", file=sys.stderr)
        if stale:
            print("run: python scripts/build_readme.py", file=sys.stderr)
            return 1
        print(f"up to date ({len(targets)} file(s) checked)")
        return 0

    for path in stale:
        path.write_text(targets[path], encoding="utf-8")
        print(f"updated: {path.relative_to(ROOT)}")
    if not stale:
        print("already up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
