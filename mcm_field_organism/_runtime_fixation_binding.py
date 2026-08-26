"""Private construction-only binding for the still-locked fixation path."""

from __future__ import annotations

from ._previous_state_minimal_runner import PreviousStateMinimalRunnerError
from ._runtime_fixation_adapters import _build_private_fixation_operations
from ._runtime_fixation_structure import (
    _FixationOperations,
    _LockedFixationStructure,
    build_locked_runtime_fixation_structure,
)


class _PrivateFixationBinding:
    __slots__ = ("_structure", "_operations")

    def __init__(
        self,
        *,
        structure: _LockedFixationStructure,
        operations: _FixationOperations,
    ) -> None:
        if not isinstance(structure, _LockedFixationStructure) or not isinstance(
            operations, _FixationOperations
        ):
            raise PreviousStateMinimalRunnerError("private fixation binding invalid")
        object.__setattr__(self, "_structure", structure)
        object.__setattr__(self, "_operations", operations)

    @property
    def structure(self) -> _LockedFixationStructure:
        return self._structure

    @property
    def operations(self) -> _FixationOperations:
        return self._operations

    def __setattr__(self, name: str, value: object) -> None:
        raise PreviousStateMinimalRunnerError("private fixation binding is immutable")

    def __copy__(self) -> object:
        raise PreviousStateMinimalRunnerError("private fixation binding cannot be copied")

    def __deepcopy__(self, memo: object) -> object:
        raise PreviousStateMinimalRunnerError("private fixation binding cannot be copied")

    def __reduce__(self) -> object:
        raise PreviousStateMinimalRunnerError(
            "private fixation binding cannot be serialized"
        )

    __hash__ = None


def _build_private_fixation_binding() -> _PrivateFixationBinding:
    try:
        structure = build_locked_runtime_fixation_structure()
        operations = _build_private_fixation_operations()
        return _PrivateFixationBinding(
            structure=structure,
            operations=operations,
        )
    except Exception:
        raise PreviousStateMinimalRunnerError(
            "private fixation binding construction failed"
        ) from None
