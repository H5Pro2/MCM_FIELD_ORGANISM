"""Private, explicitly executing boundary for the still-locked fixation path."""

from __future__ import annotations

from ._previous_state_minimal_runner import PreviousStateMinimalRunnerError
from ._runtime_fixation_binding import _PrivateFixationBinding
from ._runtime_fixation_structure import (
    _FixedDigestBundle,
    _orchestrate_runtime_fixation_with_operations,
)


def _execute_private_runtime_fixation(
    binding: _PrivateFixationBinding,
) -> _FixedDigestBundle:
    if not isinstance(binding, _PrivateFixationBinding):
        raise PreviousStateMinimalRunnerError(
            "private runtime fixation execution failed"
        )

    try:
        result = _orchestrate_runtime_fixation_with_operations(
            binding.structure,
            binding.operations,
        )
        if not isinstance(result, _FixedDigestBundle):
            raise TypeError("unexpected private fixation result")
        return result
    except Exception:
        raise PreviousStateMinimalRunnerError(
            "private runtime fixation execution failed"
        ) from None
