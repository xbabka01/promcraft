import ast
import importlib
import inspect
import pkgutil
import subprocess
import sys

import pytest

import promcraft
from promcraft import Float, Function, InstantVector


def test_scalar_and_vector_are_functions() -> None:
    """``promcraft.scalar``/``promcraft.vector`` are the PromQL functions, not submodules."""
    assert isinstance(promcraft.scalar(InstantVector("up", [])), Function)
    assert isinstance(promcraft.vector(1), Function)


def test_importing_modules_keeps_functions() -> None:
    """Importing the implementation modules must not rebind the package attributes."""
    scalar_module = importlib.import_module("promcraft._scalar")
    vector_module = importlib.import_module("promcraft._vector")
    assert scalar_module.Float is Float
    assert vector_module.InstantVector is InstantVector
    assert str(promcraft.scalar(InstantVector("up", []))) == "scalar(up{})"
    assert str(promcraft.vector(1)) == "vector(1)"


def test_submodules_are_private() -> None:
    """Users import from ``promcraft`` only; every implementation module is ``_``-prefixed."""
    public = [
        m.name for m in pkgutil.iter_modules(promcraft.__path__) if not m.name.startswith("_")
    ]
    assert public == []


def test_all_names_are_exported() -> None:
    missing = [name for name in promcraft.__all__ if not hasattr(promcraft, name)]
    assert missing == []


def test_lazy_imports_cover_all_submodules() -> None:
    """Every module ``__init__`` imports from is listed in ``__lazy_modules__``."""
    tree = ast.parse(inspect.getsource(promcraft))
    imported = {
        node.module for node in tree.body if isinstance(node, ast.ImportFrom) and node.module
    }
    assert sorted(promcraft.__lazy_modules__) == sorted(imported)


@pytest.mark.skipif(sys.version_info < (3, 15), reason="lazy imports need Python 3.15+")
def test_submodules_load_lazily() -> None:
    code = (
        "import sys, promcraft\n"
        "print(any(m.startswith('promcraft._') for m in sys.modules))\n"
        "promcraft.rate\n"
        "print('promcraft._functions' in sys.modules)\n"
    )
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    )
    assert result.stdout.split() == ["False", "True"]
