# dsa-for-data-science

Data structures and algorithms practice aimed at Data Scientist interviews: LeetCode in Python,
SQL and pandas, organised by **pattern** rather than by problem number. Every solution is written
twice — once as an obvious brute force, then as the optimal version — and the two are compared on
a few hundred randomised inputs, so a solution that passes here is actually correct rather than
merely accepted once. Each problem file carries its own summary, key insight and the mistakes
made on the first attempt, and each pattern folder has a short lesson on when to reach for it.

[![CI](https://github.com/vignesh1166/dsa-for-data-science/actions/workflows/ci.yml/badge.svg)](https://github.com/vignesh1166/dsa-for-data-science/actions/workflows/ci.yml)

<!-- STATS:START -->
**3 problems** across **2 patterns** · 0 solved · 3 todo · 0 needs review
<!-- STATS:END -->

## Progress

<!-- PROGRESS:START -->
| Pattern | Solved | Todo | Needs review | Total |
| --- | --- | --- | --- | --- |
| `arrays/traversal` | 0 | 2 | 0 | 2 |
| `sql/subqueries_ctes` | 0 | 1 | 0 | 1 |
<!-- PROGRESS:END -->

## Scheduled revisits

<!-- REVISIT:START -->
_Nothing here yet._
<!-- REVISIT:END -->

## How this repo works

- **Organised by pattern, not by number.** A problem lives in `DSA/<topic>/<subpattern>/`,
  so the folder itself is the first hint about how to attack it.
- **Every solution is verified against a brute force.** Each file holds `_brute`, the optimal
  function, the worked examples, the edge cases, and a seeded randomised test that compares the
  two over at least 200 inputs.
- **Each file explains itself.** The header records the summary, the one key insight, the
  mistakes made first time round, and the time and space complexity.
- **Nothing is marked solved until it is reviewed.** A problem moves `todo` → `needs-review` →
  `solved`, and only a passing review promotes it.
- **Solved problems come back.** Each one carries a next-revisit date, and the tables above are
  generated from the file headers by `scripts/build_readme.py`, which CI checks for drift.

## Layout

```
DSA/<NN_topic>/<subpattern>/       problems, one file each, tests included
sql/<area>/                        .sql queries with DuckDB tests alongside
pandas_practice/                   dataframe drills
scripts/                           repo tooling: stub generator, README builder
templates/                         file templates used by the generator
```

## Running it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

pytest -q                               # every problem and tooling test
pytest -q DSA/01_arrays/traversal       # one pattern
ruff check . && ruff format --check .
python scripts/build_readme.py --check  # generated sections are current
```

Adding a problem:

```bash
python scripts/new_problem.py --number 238 --title "Product of Array Except Self" \
    --difficulty Medium --pattern arrays/traversal
```

## License

MIT — see [LICENSE](LICENSE).
