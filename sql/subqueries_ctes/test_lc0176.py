"""Tests for LC 176 Second Highest Salary.

The query itself lives in lc0176_second_highest_salary.sql and is read from disk, so the file
under review is the one being executed. Remove the skip mark once the query is written.
"""

from __future__ import annotations

from pathlib import Path

import duckdb
import pytest

QUERY = Path(__file__).parent / "lc0176_second_highest_salary.sql"

CASES: list[tuple[list[tuple[int, int]], int | None]] = [
    ([(1, 100), (2, 200), (3, 300)], 200),
    ([(1, 100)], None),
]


def create_employee(db: duckdb.DuckDBPyConnection, rows: list[tuple[int, int]]) -> None:
    """Build the Employee(id, salary) table and insert the given rows."""
    db.execute("CREATE TABLE Employee (id INTEGER, salary INTEGER)")
    for employee_id, salary in rows:
        db.execute("INSERT INTO Employee VALUES (?, ?)", [employee_id, salary])


@pytest.mark.skip(reason="todo")
@pytest.mark.parametrize(("rows", "expected"), CASES)
def test_second_highest_salary(
    db: duckdb.DuckDBPyConnection,
    run_sql_file,
    rows: list[tuple[int, int]],
    expected: int | None,
) -> None:
    create_employee(db, rows)
    assert run_sql_file(QUERY) == [(expected,)]
