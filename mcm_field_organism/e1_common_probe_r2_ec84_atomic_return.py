"""S1-EC84 atomic in-memory return for one completed EC67 result and EC80 receipt."""

from __future__ import annotations

from dataclasses import dataclass, field

from .e1_common_probe_n2_r2_ec79_static_evaluation_contract import (
    E1CommonProbeN2R2EC79StaticEvaluationContract,
)
from .e1_common_probe_n2_r2_real_mode_coordinator import (
    E1CommonProbeN2R2RealModeCoordinatorResult,
)
from .e1_common_probe_r2_ec80_scalar_contract import (
    E1CommonProbeR2EC80ScalarReceipt,
)
from .e1_common_probe_r2_ec82_coordinator_handoff import (
    E1CommonProbeR2EC82CoordinatorHandoffContract,
    reduce_e1_common_probe_r2_ec82_completed_result,
)
from .e1_common_probe_r2_ec83_one_shot_measurement_contract import (
    E1CommonProbeR2EC83OneShotMeasurementContract,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeR2EC84AtomicReturnError(ValueError):
    """Raised when EC84 cannot return the result and scalar receipt together."""


S1_EC84_RETURN_ID = "e1.common-probe-r2-atomic-return.s1ec84.v1"
S1_EC84_EC83_CONTRACT_DIGEST = (
    "72fc107a4ecd91ff8b8ddf5bb5226990b41c603c81cb763c99ae98d69b92ae88"
)


@dataclass(frozen=True, slots=True)
class E1CommonProbeR2EC84AtomicReturn:
    return_id: str
    source_ec83_contract_digest: str
    coordinator_result_digest: str
    scalar_receipt_digest: str
    formation_count: int
    fresh_field_count: int
    probe_count: int
    total_field_steps: int
    scalar_contrast_count: int
    result_and_scalars_returned_together: bool
    raw_vectors_persisted: bool
    scalar_file_persisted: bool
    additional_field_execution_performed: bool
    ec46_decision_permitted: bool
    research_decision_permitted: bool
    claims_permitted: bool
    status: str
    return_digest: str
    coordinator_result: E1CommonProbeN2R2RealModeCoordinatorResult = field(
        repr=False, compare=False
    )
    scalar_receipt: E1CommonProbeR2EC80ScalarReceipt = field(
        repr=False, compare=False
    )

    def __post_init__(self) -> None:
        if (
            self.return_id != S1_EC84_RETURN_ID
            or self.source_ec83_contract_digest != S1_EC84_EC83_CONTRACT_DIGEST
            or self.coordinator_result_digest != self.coordinator_result.result_digest
            or self.scalar_receipt_digest != self.scalar_receipt.receipt_digest
            or self.scalar_receipt.source_result_digest
            != self.coordinator_result.result_digest
            or (
                self.formation_count,
                self.fresh_field_count,
                self.probe_count,
                self.total_field_steps,
                self.scalar_contrast_count,
            )
            != (4, 8, 8, 3208, 6)
            or self.result_and_scalars_returned_together is not True
            or any(
                value is not False
                for value in (
                    self.raw_vectors_persisted,
                    self.scalar_file_persisted,
                    self.additional_field_execution_performed,
                    self.ec46_decision_permitted,
                    self.research_decision_permitted,
                    self.claims_permitted,
                )
            )
            or self.status != "TECHNICAL_RESULT_AND_R2_SCALARS_RETURNED_ATOMICALLY"
        ):
            raise E1CommonProbeR2EC84AtomicReturnError(
                "S1-EC84 atomic return changed or is incomplete"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"return_digest", "coordinator_result", "scalar_receipt"}
        }
        if self.return_digest != _digest(payload):
            raise E1CommonProbeR2EC84AtomicReturnError(
                "S1-EC84 return digest changed"
            )


def build_e1_common_probe_r2_ec84_atomic_return(
    contract: E1CommonProbeR2EC83OneShotMeasurementContract,
    handoff: E1CommonProbeR2EC82CoordinatorHandoffContract,
    boundary: E1CommonProbeN2R2EC79StaticEvaluationContract,
    completed_result: E1CommonProbeN2R2RealModeCoordinatorResult,
) -> E1CommonProbeR2EC84AtomicReturn:
    """Return a completed result only after its in-memory scalar reduction succeeds."""

    if not isinstance(contract, E1CommonProbeR2EC83OneShotMeasurementContract):
        raise E1CommonProbeR2EC84AtomicReturnError(
            "S1-EC84 requires the typed closed EC83 contract"
        )
    contract.__post_init__()
    if (
        contract.contract_digest != S1_EC84_EC83_CONTRACT_DIGEST
        or contract.owner_authorization_present is not False
        or contract.execution_permitted is not False
    ):
        raise E1CommonProbeR2EC84AtomicReturnError(
            "S1-EC84 requires the exact closed EC83 contract"
        )
    if not isinstance(completed_result, E1CommonProbeN2R2RealModeCoordinatorResult):
        raise E1CommonProbeR2EC84AtomicReturnError(
            "S1-EC84 requires one already completed EC67 result"
        )

    scalar_receipt = reduce_e1_common_probe_r2_ec82_completed_result(
        handoff, boundary, completed_result
    )
    values = {
        "return_id": S1_EC84_RETURN_ID,
        "source_ec83_contract_digest": contract.contract_digest,
        "coordinator_result_digest": completed_result.result_digest,
        "scalar_receipt_digest": scalar_receipt.receipt_digest,
        "formation_count": completed_result.formation_count,
        "fresh_field_count": completed_result.fresh_field_count,
        "probe_count": completed_result.probe_count,
        "total_field_steps": completed_result.actual_field_steps_executed,
        "scalar_contrast_count": len(scalar_receipt.contrast_scalars),
        "result_and_scalars_returned_together": True,
        "raw_vectors_persisted": False,
        "scalar_file_persisted": False,
        "additional_field_execution_performed": False,
        "ec46_decision_permitted": False,
        "research_decision_permitted": False,
        "claims_permitted": False,
        "status": "TECHNICAL_RESULT_AND_R2_SCALARS_RETURNED_ATOMICALLY",
    }
    return E1CommonProbeR2EC84AtomicReturn(
        **values,
        return_digest=_digest(values),
        coordinator_result=completed_result,
        scalar_receipt=scalar_receipt,
    )
