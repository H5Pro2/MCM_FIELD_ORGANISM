"""Current public contracts for one shared MCM field.

Earlier separate-field experiments remain available from their explicit
modules, but are intentionally not part of this package-level architecture API.
"""

from __future__ import annotations

from importlib import import_module as _import_module

from .root_lazy_exports import ROOT_ALL as _ROOT_ALL
from .root_lazy_exports import ROOT_LAZY_EXPORTS as _ROOT_LAZY_EXPORTS


__all__ = list(_ROOT_ALL)


def __getattr__(name: str) -> object:
    try:
        source_module, source_attribute = _ROOT_LAZY_EXPORTS[name]
    except KeyError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None
    module = _import_module(f".{source_module}", __name__)
    value = getattr(module, source_attribute)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
