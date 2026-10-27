"""Doctest setup for the docstring examples under `src/`."""

from collections.abc import Iterator
from typing import Any

import pytest

import promcraft


@pytest.fixture(autouse=True)
def _public_names(doctest_namespace: dict[str, Any]) -> Iterator[None]:
    """Make every public `promcraft` name available to docstring examples.

    `doctest_namespace` is session-scoped, so the names are removed again
    afterwards; the Markdown pages must keep importing what they use.
    """
    names = {name: getattr(promcraft, name) for name in promcraft.__all__}
    doctest_namespace.update(names)
    yield
    for name in names:
        doctest_namespace.pop(name, None)
