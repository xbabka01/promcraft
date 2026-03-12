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

- [src/promcraft/base.py](src/promcraft/base.py) — `Query`: abstract base class with a single required `__str__` method. Everything in the library inherits from it.
- [src/promcraft/scalar.py](src/promcraft/scalar.py) — `Scalar(Query)` (abstract), then `Float`, `Hex`, `Duration`. Scalars are used as values in other query components (offsets, range windows, etc.).
- [src/promcraft/string.py](src/promcraft/string.py) — `String(Query)`: PromQL string literals with configurable quoting (`"`, `'`, `` ` ``).
- [src/promcraft/vector.py](src/promcraft/vector.py) — `Label` (label matcher), `InstantVector(Query)`, `RangeVector(Query)`. These are the primary selector types.
- [src/promcraft/operator.py](src/promcraft/operator.py) — `Match`, `Group`, `BinaryOprator(Query)`. Note: `BinaryOprator` is the existing (intentionally preserved) spelling — do not rename it.
- [src/promcraft/aggregation.py](src/promcraft/aggregation.py) — `Grouping`, `AggregationOperator(Query)`.
- [src/promcraft/__init__.py](src/promcraft/__init__.py) — public API; all user-facing classes are re-exported here.

### Key Patterns

- Every class implements `__str__` — the output IS the PromQL query fragment.
- `BinaryOprator` auto-parenthesizes nested `BinaryOprator` operands.
- `BinaryOprator` and `AggregationOperator` support method chaining (`.on()`, `.ignoring()`, `.group_left()`, `.group_right()`, `.by()`, `.without()`) that return new instances (immutable style).
- `Label` values must be `String` instances (not raw `str`).
- Mypy is strict (`disallow_untyped_defs`, `warn_return_any`, etc.) — all new code must be fully typed.
