# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
poetry install

# Run all checks (tests + mypy type checking + ruff linting)
poetry run pytest

# Run only unit tests (skip mypy and ruff)
poetry run pytest -o addopts=""

# Run a single test file
poetry run pytest tests/test_operator.py -o addopts=""

# Run a single test by name
poetry run pytest tests/test_operator.py::test_binary_helpers -o addopts=""

# Docs (optional `docs` group): live preview, and the strict build CI runs
poetry install --with docs
poetry run zensical serve
poetry run zensical build --strict
```

User documentation lives in `docs/` (built with [Zensical](https://zensical.org/), config in `zensical.toml`; API pages via mkdocstrings-python), deployed to GitHub Pages by [.github/workflows/docs.yml](.github/workflows/docs.yml) on release tags; PRs and `main` only build it. `docs/guide/*.md` are hand-written guides; `docs/api/*.md` hold one `::: promcraft.<name>` mkdocstrings block per public name, so a new public name must be added to the matching API page. `README.md` is kept short (it is also the PyPI description) and links to the site with absolute URLs only.

The `version` in `pyproject.toml` (`0.0.0`) is a placeholder and is never bumped by hand. The release workflow ([.github/workflows/release.yaml](.github/workflows/release.yaml)) sets the real version from the pushed git tag (`poetry version "${GITHUB_REF_NAME#v}"`, so tag `v0.5.0` publishes `0.5.0`). Do not flag the mismatch between `pyproject.toml` and the tags, and do not suggest bumping it.

`pytest` is configured (in `pyproject.toml`) to always run `--mypy`, `--ruff`, `--ruff-format`, and `--cov` alongside unit tests. Mypy and ruff violations are reported as test failures. `-p no:mypy -p no:ruff` does NOT work to skip them here — the plugins would be disabled while `addopts` still passes their `--mypy`/`--ruff`/`--ruff-format` flags, which pytest then rejects as unrecognized. Use `-o addopts=""` to clear the ini `addopts` instead.

## Architecture

This is a Python library for building PromQL query strings programmatically. All query objects extend `Query` and implement `to_string(indent=None, _indent_level=0, *, style=None)` to serialize to valid PromQL syntax (`__str__` delegates to it; `indent` enables multi-line pretty-printing; `style` is a `Style` from `_base.py` selecting formatting options). Composing objects by nesting them is the core design pattern.

### Class Hierarchy

- [src/promcraft/_base.py](src/promcraft/_base.py) — `Query`: abstract base class with a single required `to_string` method. Everything in the library inherits from it. It also provides the Python operator overloads (`+`, `==`, unary `-`, ...) that build `BinaryOprator`/`Negation`, and `subquery()`/slice syntax.
- [src/promcraft/_scalar.py](src/promcraft/_scalar.py) — `Scalar(Query)` (abstract), then `Float`, `Hex`, `Duration`. Scalars are used as values in other query components (offsets, range windows, etc.).
- [src/promcraft/_variable.py](src/promcraft/_variable.py) — `Variable(Query)`: Grafana template variable (`$name` / `${name}`). `from_value` passes it through unchanged everywhere; only `Label` quotes it (`"$name"`) as a label matcher value.
- [src/promcraft/_string.py](src/promcraft/_string.py) — `String(Query)`: PromQL string literals with configurable quoting (`"`, `'`, `` ` ``).
- [src/promcraft/_vector.py](src/promcraft/_vector.py) — `Label` (label matcher), `InstantVector(Query)`, `RangeVector(Query)`. These are the primary selector types.
- [src/promcraft/_modifiers.py](src/promcraft/_modifiers.py) — `TimeModifiers` mixin shared by `InstantVector`, `RangeVector`, `Subquery`: `offset`/`@` normalisation, rendering, and `with_offset`/`with_at`/`with_at_start`/`with_at_end`. Each class implements only `_replace_modifiers`.
- [src/promcraft/_subquery.py](src/promcraft/_subquery.py) — `Subquery(Query)`: `<expr>[range:resolution]` over any instant-vector expression, built via `Query.subquery()` or slice syntax (`expr[range:resolution]`). On `InstantVector`, plain and tuple indexing still return a `RangeVector`; only slices return a `Subquery`. mypy rejects non-int slice bounds at call sites, so tests using `Duration` slices carry `# type: ignore[misc]`.
- [src/promcraft/_operator.py](src/promcraft/_operator.py) — `Match`, `Group`, `BinaryOprator(Query)`, `Negation(Query)`, plus helper functions (`add`, `eq`, `and_`, ...). Note: `BinaryOprator` is the existing (intentionally preserved) spelling — do not rename it.
- [src/promcraft/_aggregation.py](src/promcraft/_aggregation.py) — `Grouping`, `Aggregation(Query)`, plus helpers (`sum_`, `topk`, ...; trailing `_` where the name shadows a builtin).
- [src/promcraft/_functions.py](src/promcraft/_functions.py) — `Function(Query)` and one helper per PromQL function (`rate`, `abs_`, `histogram_quantile`, ...).
- [src/promcraft/__init__.py](src/promcraft/__init__.py) — public API; all user-facing classes are re-exported here.

All implementation modules are `_`-prefixed: users import only from `promcraft`, so every user-facing name must be re-exported in `__init__.py` and listed in `__all__` (enforced by `tests/test_package.py`). Do not add compatibility shims at the old unprefixed paths: `promcraft.scalar`/`promcraft.vector` are also PromQL function names, and a shim submodule would rebind them on first import.

### Key Patterns

- Every `Query` implements `to_string` — the output IS the PromQL query fragment.
- `to_string` must forward `style=style` to every child `to_string` call (and pass it to `Label`/`Grouping`/`Match`/`Group.to_string(style)`). `Style()` defaults must reproduce `str(query)` exactly; leaf literals accept `style` and ignore it (`# noqa: ARG002`).
- `BinaryOprator` auto-parenthesizes nested `BinaryOprator`/`Negation` operands (and a negative `^` base). A `group_left`/`group_right` without `on`/`ignoring` renders `ignoring ()`; group modifiers on `and`/`or`/`unless` raise.
- `BinaryOprator` and `Aggregation` support method chaining (`.on()`, `.ignoring()`, `.group_left()`, `.group_right()`, `.bool()`, `.by()`, `.without()`) that return new instances (immutable style).
- Raw Python values are coerced via `from_value`: `str` → `String` in string positions (`Variable` passes through, except as a `Label` value), numbers → `Float`/`Duration` in scalar positions.
- Mypy is strict (`disallow_untyped_defs`, `warn_return_any`, etc.) — all new code must be fully typed.
- Docstrings are Google style with Markdown (ruff `pydocstyle.convention = "google"`): `Args:`/`Raises:`/`Example:` sections, examples in fenced ```` ```python ```` blocks, single-backtick code, and cross-references as mkdocstrings autorefs to the public path (`` [`Float`][promcraft.Float] ``, never `promcraft._scalar.Float`).
