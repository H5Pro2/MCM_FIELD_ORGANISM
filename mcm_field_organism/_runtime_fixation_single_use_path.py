"""Private single-use composition for the still-locked fixation path."""

from __future__ import annotations

from ._runtime_fixation_binding import _build_private_fixation_binding
from ._runtime_fixation_handoff import _execute_private_runtime_fixation
from ._runtime_fixation_structure import _FixedDigestBundle


def _run_private_runtime_fixation_once() -> _FixedDigestBundle:
    binding = _build_private_fixation_binding()
    return _execute_private_runtime_fixation(binding)
