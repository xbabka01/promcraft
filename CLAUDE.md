# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
poetry install

# Run all checks (tests + mypy type checking + ruff linting)
poetry run pytest

# Run only unit tests (skip mypy and ruff)
poetry run pytest --no-header -p no:mypy -p no:ruff

# Run a single test file
poetry run pytest tests/test_operator.py -p no:mypy -p no:ruff

# Run a single test by name
poetry run pytest tests/test_operator.py::test_binary_operator -p no:mypy -p no:ruff
```

`pytest` is configured (in `pyproject.toml`) to always run `--mypy`, `--ruff`, `--ruff-format`, and `--cov` alongside unit tests. Mypy and ruff violations are reported as test failures.

## Architecture

This is a Python library for building PromQL query strings programmatically. All query objects extend `Query` and implement `__str__` to serialize to valid PromQL syntax. Composing objects by nesting them is the core design pattern.

### Class Hierarchy

- [src/prom_ql/base.py](src/prom_ql/base.py) — `Query`: abstract base class with a single required `__str__` method. Everything in the library inherits from it.
- [src/prom_ql/scalar.py](src/prom_ql/scalar.py) — `Scalar(Query)` (abstract), then `Float`, `Hex`, `Duration`. Scalars are used as values in other query components (offsets, range windows, etc.).
- [src/prom_ql/string.py](src/prom_ql/string.py) — `String(Query)`: PromQL string literals with configurable quoting (`"`, `'`, `` ` ``).
- [src/prom_ql/vector.py](src/prom_ql/vector.py) — `Label` (label matcher), `InstantVector(Query)`, `RangeVector(Query)`. These are the primary selector types.
- [src/prom_ql/operator.py](src/prom_ql/operator.py) — `Match`, `Group`, `BinaryOprator(Query)`. Note: `BinaryOprator` is the existing (intentionally preserved) spelling — do not rename it.
- [src/prom_ql/aggregation.py](src/prom_ql/aggregation.py) — `Grouping`, `AggregationOperator(Query)`.
- [src/prom_ql/__init__.py](src/prom_ql/__init__.py) — public API; all user-facing classes are re-exported here.

### Key Patterns

- Every class implements `__str__` — the output IS the PromQL query fragment.
- `BinaryOprator` auto-parenthesizes nested `BinaryOprator` operands.
- `BinaryOprator` and `AggregationOperator` support method chaining (`.on()`, `.ignoring()`, `.group_left()`, `.group_right()`, `.by()`, `.without()`) that return new instances (immutable style).
- `Label` values must be `String` instances (not raw `str`).
- Mypy is strict (`disallow_untyped_defs`, `warn_return_any`, etc.) — all new code must be fully typed.
