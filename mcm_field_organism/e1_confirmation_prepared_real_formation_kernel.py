"""Private S1-EC8 real formation kernel adapter for small in-memory use."""

from __future__ import annotations

import copy
from dataclasses import asdict, dataclass
from typing import Any

from .e1_confirmation_formation_runner import (
    E1ConfirmationFormationArmAudit,
    _run_arm,
)
from .e1_confirmation_prepared_formation_consumer import (
    S1_EC7_FORMATION_ARMS,
    S1_EC7_REFINEMENTS,
)
from .e1_local_edge_plasticity import E1LocalEdgePlasticityState
from .e1_refined_chain_canonical_producer import (
    _initial_field_digest,
    _initial_state_digest,
)
from .e1_refined_formation_runner import _digest, _state_payload
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .shared_mcm_field import SharedMCMField


class E1ConfirmationPreparedRealFormationKernelError(ValueError):
    """Raised when the S1-EC8 real in-memory arm fails closed."""


def _valid_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


@dataclass(frozen=True, slots=True)
class E1PreparedRealFormationArmResult:
    arm_id: str
    refinement_id: str
    formation_enabled: bool
    initial_field_digest: str
    initial_state_digest: str
    output_state: E1LocalEdgePlasticityState
    output_state_digest: str
    audit: E1ConfirmationFormationArmAudit
    input_objects_preserved: bool
    copied_inputs_used: bool
    canonical_execution_permitted: bool
    claims_permitted: bool
    result_digest: str

    def __post_init__(self) -> None:
        expected_enabled = not self.arm_id.endswith("formation_ablated")
        if (
            self.arm_id not in S1_EC7_FORMATION_ARMS
            or self.refinement_id not in {item[0] for item in S1_EC7_REFINEMENTS}
            or self.formation_enabled is not expected_enabled
            or not _valid_digest(self.initial_field_digest)
            or not _valid_digest(self.initial_state_digest)
            or not isinstance(self.output_state, E1LocalEdgePlasticityState)
            or self.output_state_digest != _digest(_state_payload(self.output_state))
            or not isinstance(self.audit, E1ConfirmationFormationArmAudit)
            or self.audit.arm_id != self.arm_id
            or self.audit.refinement_id != self.refinement_id
            or self.audit.formation_enabled is not self.formation_enabled
            or self.input_objects_preserved is not True
            or self.copied_inputs_used is not True
            or self.canonical_execution_permitted is not False
            or self.claims_permitted is not False
        ):
            raise E1ConfirmationPreparedRealFormationKernelError(
                "S1-EC8 real formation arm result changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"output_state", "audit", "result_digest"}
        }
        payload["output_state"] = _state_payload(self.output_state)
        payload["audit"] = asdict(self.audit)
        if self.result_digest != _digest(payload):
            raise E1ConfirmationPreparedRealFormationKernelError(
                "S1-EC8 result digest does not match its payload"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


def run_prepared_real_formation_arm_in_memory(
    arm_id: str,
    refinement_id: str,
    sequences: Any,
    proposal_steps: Any,
    initial_field: SharedMCMField,
    initial_state: E1LocalEdgePlasticityState,
    formation_enabled: bool,
) -> E1PreparedRealFormationArmResult:
    """Run one real arm on copies while preserving every prepared input."""

    expected_enabled = not arm_id.endswith("formation_ablated")
    if (
        arm_id not in S1_EC7_FORMATION_ARMS
        or refinement_id not in {item[0] for item in S1_EC7_REFINEMENTS}
        or formation_enabled is not expected_enabled
        or not isinstance(initial_field, SharedMCMField)
        or not isinstance(initial_state, E1LocalEdgePlasticityState)
    ):
        raise E1ConfirmationPreparedRealFormationKernelError(
            "S1-EC8 real formation arm inputs changed"
        )
    field_digest = _initial_field_digest(initial_field)
    state_digest = _initial_state_digest(initial_state)
    field_copy = copy.deepcopy(initial_field)
    state_copy = copy.deepcopy(initial_state)
    if field_copy is initial_field or state_copy is initial_state:
        raise E1ConfirmationPreparedRealFormationKernelError(
            "S1-EC8 failed to separate prepared arm inputs"
        )
    output_state, audit = _run_arm(
        arm_id,
        refinement_id,
        field_copy,
        state_copy,
        sequences,
        proposal_steps,
        NeutralLocalFieldSubstrateConfig(1.0),
        NeutralFastAfterimageConfig(0.5),
        formation_enabled=formation_enabled,
    )
    preserved = (
        _initial_field_digest(initial_field) == field_digest
        and _initial_state_digest(initial_state) == state_digest
    )
    values = {
        "arm_id": arm_id,
        "refinement_id": refinement_id,
        "formation_enabled": formation_enabled,
        "initial_field_digest": field_digest,
        "initial_state_digest": state_digest,
        "output_state": output_state,
        "output_state_digest": _digest(_state_payload(output_state)),
        "audit": audit,
        "input_objects_preserved": preserved,
        "copied_inputs_used": True,
        "canonical_execution_permitted": False,
        "claims_permitted": False,
    }
    payload = {
        name: value
        for name, value in values.items()
        if name not in {"output_state", "audit"}
    }
    payload["output_state"] = _state_payload(output_state)
    payload["audit"] = asdict(audit)
    return E1PreparedRealFormationArmResult(
        **values,
        result_digest=_digest(payload),
    )


def prepared_real_formation_kernel_digest(
    arm_id: str,
    refinement_id: str,
    sequences: Any,
    proposal_steps: Any,
    initial_field: SharedMCMField,
    initial_state: E1LocalEdgePlasticityState,
    formation_enabled: bool,
) -> str:
    """Expose the real copied-input arm through the S1-EC7 digest interface."""

    return run_prepared_real_formation_arm_in_memory(
        arm_id,
        refinement_id,
        sequences,
        proposal_steps,
        initial_field,
        initial_state,
        formation_enabled,
    ).result_digest
