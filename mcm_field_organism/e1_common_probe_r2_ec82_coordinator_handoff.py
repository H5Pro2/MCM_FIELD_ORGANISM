"""S1-EC82 static handoff from one completed EC67 result to EC80."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path

from .e1_common_probe_n2_r2_ec79_static_evaluation_contract import (
    E1CommonProbeN2R2EC79StaticEvaluationContract,
)
from .e1_common_probe_n2_r2_real_mode_coordinator import (
    E1CommonProbeN2R2RealModeCoordinatorResult,
)
from .e1_common_probe_r2_ec80_scalar_contract import (
    E1CommonProbeR2EC80ScalarReceipt,
    build_e1_common_probe_r2_ec80_scalar_receipt,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeR2EC82CoordinatorHandoffError(ValueError):
    """Raised when the EC67-to-EC80 handoff loses its closed scope."""


S1_EC82_CONTRACT_ID = "e1.common-probe-r2-coordinator-handoff.s1ec82.v1"
S1_EC82_SOURCE_FILES = (
    (
        "e1_common_probe_n2_r2_real_mode_coordinator.py",
        "b56a922153959b97ed69b4936074f2bed6b0cdc2a787aaf80a07f88e4d25c230",
    ),
    (
        "e1_common_probe_r2_ec80_scalar_contract.py",
        "e0cac22f3ef5f3b27c1ca673058004b8ec4d1db7315ac2d1d11609b513b4986e",
    ),
)


@dataclass(frozen=True, slots=True)
class E1CommonProbeR2EC82CoordinatorHandoffContract:
    contract_id: str
    source_digests: tuple[tuple[str, str, str], ...]
    accepted_result_type: str
    required_probe_count: int
    required_refinement_id: str
    handoff_timing: str
    reduction_target: str
    raw_vectors_leave_process: bool
    coordinator_execution_permitted: bool
    owner_authorization_present: bool
    persistence_permitted: bool
    ec46_decision_permitted: bool
    research_decision_permitted: bool
    claims_permitted: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        if (
            self.contract_id != S1_EC82_CONTRACT_ID
            or len(self.source_digests) != 2
            or any(expected != observed for _, expected, observed in self.source_digests)
            or self.accepted_result_type
            != "E1CommonProbeN2R2RealModeCoordinatorResult"
            or (self.required_probe_count, self.required_refinement_id) != (8, "r2")
            or self.handoff_timing != "same-process-immediately-after-result-return"
            or self.reduction_target != "S1-EC80-r2-six-contrast-scalar-receipt"
            or any(
                value is not False
                for value in (
                    self.raw_vectors_leave_process,
                    self.coordinator_execution_permitted,
                    self.owner_authorization_present,
                    self.persistence_permitted,
                    self.ec46_decision_permitted,
                    self.research_decision_permitted,
                    self.claims_permitted,
                )
            )
            or self.decision != "EC67_TO_EC80_HANDOFF_BOUND_EXECUTION_NOT_AUTHORIZED"
        ):
            raise E1CommonProbeR2EC82CoordinatorHandoffError(
                "S1-EC82 contract changed or crossed its closed scope"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "contract_digest"
        }
        if self.contract_digest != _digest(payload):
            raise E1CommonProbeR2EC82CoordinatorHandoffError(
                "S1-EC82 contract digest changed"
            )


def build_e1_common_probe_r2_ec82_coordinator_handoff_contract(
    project_root: Path,
) -> E1CommonProbeR2EC82CoordinatorHandoffContract:
    """Bind the two handoff sources without invoking either execution path."""

    source_root = Path(project_root) / "mcm_field_organism"
    source_digests = []
    for name, expected in S1_EC82_SOURCE_FILES:
        try:
            observed = hashlib.sha256((source_root / name).read_bytes()).hexdigest()
        except OSError as exc:
            raise E1CommonProbeR2EC82CoordinatorHandoffError(
                f"S1-EC82 source missing: {name}"
            ) from exc
        source_digests.append((name, expected, observed))
    values = {
        "contract_id": S1_EC82_CONTRACT_ID,
        "source_digests": tuple(source_digests),
        "accepted_result_type": "E1CommonProbeN2R2RealModeCoordinatorResult",
        "required_probe_count": 8,
        "required_refinement_id": "r2",
        "handoff_timing": "same-process-immediately-after-result-return",
        "reduction_target": "S1-EC80-r2-six-contrast-scalar-receipt",
        "raw_vectors_leave_process": False,
        "coordinator_execution_permitted": False,
        "owner_authorization_present": False,
        "persistence_permitted": False,
        "ec46_decision_permitted": False,
        "research_decision_permitted": False,
        "claims_permitted": False,
        "decision": "EC67_TO_EC80_HANDOFF_BOUND_EXECUTION_NOT_AUTHORIZED",
    }
    return E1CommonProbeR2EC82CoordinatorHandoffContract(
        **values, contract_digest=_digest(values)
    )


def reduce_e1_common_probe_r2_ec82_completed_result(
    contract: E1CommonProbeR2EC82CoordinatorHandoffContract,
    boundary: E1CommonProbeN2R2EC79StaticEvaluationContract,
    result: E1CommonProbeN2R2RealModeCoordinatorResult,
) -> E1CommonProbeR2EC80ScalarReceipt:
    """Reduce one already returned EC67 object; never start or persist a run."""

    if not isinstance(contract, E1CommonProbeR2EC82CoordinatorHandoffContract):
        raise E1CommonProbeR2EC82CoordinatorHandoffError(
            "S1-EC82 requires its typed handoff contract"
        )
    contract.__post_init__()
    if not isinstance(result, E1CommonProbeN2R2RealModeCoordinatorResult):
        raise E1CommonProbeR2EC82CoordinatorHandoffError(
            "S1-EC82 requires one completed typed EC67 result"
        )
    result.__post_init__()
    if (
        result.probe_count != contract.required_probe_count
        or result.persistence_performed is not False
        or result.research_decision_permitted is not False
        or result.memory_claim_permitted is not False
    ):
        raise E1CommonProbeR2EC82CoordinatorHandoffError(
            "S1-EC82 EC67 result crossed the reduction boundary"
        )
    return build_e1_common_probe_r2_ec80_scalar_receipt(
        boundary,
        result.probes,
        source_result_digest=result.result_digest,
    )
