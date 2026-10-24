import importlib

import promcraft
from promcraft import Float, InstantVector
from promcraft.functions import Function


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
