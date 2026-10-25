# Contributing

Thanks for your interest in improving promcraft! Bug reports, feature requests, and pull
requests are all welcome.

## Reporting issues

- **Bugs and feature requests:** open an [issue](https://github.com/xbabka01/promcraft/issues/new/choose).
  For bugs, include the Python code that builds the query, the PromQL it produces, and the
  PromQL you expected.
- **Security vulnerabilities:** do not open a public issue. Report them privately via
  [GitHub Security Advisories](https://github.com/xbabka01/promcraft/security/advisories/new).

## Development setup

The project uses [Poetry](https://python-poetry.org/) and supports Python 3.11+.

```bash
git clone https://github.com/xbabka01/promcraft.git
cd promcraft
poetry install
```

## Running checks

`pytest` is configured to run the unit tests together with mypy (strict), ruff linting,
ruff formatting checks, and coverage. CI runs the same command on every supported Python
version, so make sure it passes locally before opening a pull request:

```bash
# Everything: tests + mypy + ruff
poetry run pytest

# Only the unit tests (skips mypy and ruff)
poetry run pytest -o addopts=""

# A single test
poetry run pytest tests/test_operator.py::test_binary_helpers -o addopts=""
```

To fix formatting and auto-fixable lint issues:

```bash
poetry run ruff format
poetry run ruff check --fix
```

## Code guidelines

- Every query object extends `Query` and implements `to_string`; its output is the PromQL
  fragment. `to_string` must forward `style=style` to every child `to_string` call.
- Query objects are immutable: chaining methods (`.by()`, `.on()`, `.with_offset()`, ...)
  return new instances instead of modifying the existing one.
- All code must be fully typed (mypy runs in strict mode).
- Implementation modules are `_`-prefixed. Every user-facing name must be re-exported from
  `promcraft/__init__.py` and listed in `__all__`.
- Add tests for new behaviour and bug fixes, and update `README.md` when the public API
  changes.

## Pull requests

- Keep each pull request focused on a single change.
- Use a [Conventional Commits](https://www.conventionalcommits.org/) title, e.g.
  `feat: add holt_winters function` or `fix: quote label values containing backslashes`.
  Pull requests are squash-merged, so the title becomes the commit message.
- All CI checks must pass before a pull request can be merged.

Releases are handled by the maintainer; see [RELEASING.md](RELEASING.md).

## License

By contributing, you agree that your contributions will be licensed under the
[MIT License](LICENSE).
