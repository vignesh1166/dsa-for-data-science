"""Shared fixtures for the SQL exercises: an in-memory DuckDB connection per test."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import duckdb
import pytest


@pytest.fixture
def db() -> Iterator[duckdb.DuckDBPyConnection]:
    """An empty in-memory DuckDB connection, closed when the test finishes."""
    connection = duckdb.connect(":memory:")
    try:
        yield connection
    finally:
        connection.close()


@pytest.fixture
def run_sql_file(db: duckdb.DuckDBPyConnection):
    """Run the query stored in a .sql file and return its rows as a list of tuples.

    The header comment lines are stripped so the file stays the single source of the query.
    """

    def _run(path: str | Path) -> list[tuple]:
        text = Path(path).read_text(encoding="utf-8")
        query = "\n".join(
            line for line in text.splitlines() if not line.lstrip().startswith("--")
        ).strip()
        if not query:
            raise AssertionError(f"{path} contains no query yet")
        return db.execute(query).fetchall()

    return _run
