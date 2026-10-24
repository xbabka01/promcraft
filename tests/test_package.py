import importlib
import pkgutil

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
