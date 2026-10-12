# SQL

SQL practice, one query per file, each with a test that builds the tables and checks the result.

Queries are written in portable ANSI SQL and run against an in-memory
[DuckDB](https://duckdb.org) database, so the tests need no server and no fixtures beyond the
`db` connection fixture in `conftest.py`.

Each problem is a pair:

```
sql/<area>/lc0176_second_highest_salary.sql   the query, with the header as -- comments
sql/<area>/test_lc0176.py                     builds the tables, runs the query, asserts rows
```

The test reads the `.sql` file rather than duplicating the query, so the file under review is the
one being executed. Results are compared as sorted lists of tuples unless the problem specifies
an order.

## Problems

<!-- PROBLEMS:START -->
| Problem | Difficulty | Status | Time | Space | Source |
| --- | --- | --- | --- | --- | --- |
| [LC 176 Second Highest Salary](subqueries_ctes/lc0176_second_highest_salary.sql) | Medium | todo | TODO | TODO | own |
<!-- PROBLEMS:END -->
