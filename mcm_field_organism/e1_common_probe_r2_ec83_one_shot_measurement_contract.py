"""S1-EC83 closed one-shot contract for EC67 -> EC82 -> EC80."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path

from .e1_common_probe_r2_ec82_coordinator_handoff import (
    E1CommonProbeR2EC82CoordinatorHandoffContract,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeR2EC83OneShotMeasurementContractError(ValueError):
    """Raised when EC83 releases execution or changes its measurement scope."""


S1_EC83_CONTRACT_ID = "e1.common-probe-r2-one-shot-measurement.s1ec83.v1"
S1_EC83_EC82_CONTRACT_DIGEST = (
    "ea3154aa4cd71640d056b9e2fae9a1b68819f1d36821bf16bc11fadb96848452"
)
S1_EC83_EC82_SOURCE_SHA256 = (
    "77591b7c4448ecb304e0ba52e6b079d2378ed2be01793e30a2371b2e9729f257"
)
S1_EC83_EC82_SOURCE_RELATIVE_PATH = (
    "mcm_field_organism/e1_common_probe_r2_ec82_coordinator_handoff.py"
)
S1_EC83_STAGES = (
    "fresh-technical-preflight",
    "new-explicit-owner-authorization",
    "one-ec67-coordinator-call",
    "immediate-ec82-in-memory-handoff",
    "one-ec80-r2-scalar-receipt",
    "technical-report-without-ec46-decision",
)


@dataclass(frozen=True, slots=True)
class E1CommonProbeR2EC83OneShotMeasurementContract:
    contract_id: str
    source_ec82_contract_digest: str
    source_ec82_sha256: str
    prior_authorization_id: str
    prior_authorization_consumed: bool
    refinement_id: str
    stages: tuple[str, ...]
    planned_execution_count: int
    authorized_execution_count: int
    maximum_formation_steps: int
    maximum_probe_steps: int
    maximum_total_field_steps: int
    maximum_runtime_seconds: float
    expected_formation_count: int
    expected_fresh_field_count: int
    expected_probe_count: int
    expected_scalar_contrast_count: int
    fresh_preflight_required: bool
    explicit_new_owner_authorization_required: bool
    scalar_receipt_required_before_result_release: bool
    stop_on_execution_or_handoff_error: bool
    owner_authorization_present: bool
    execution_permitted: bool
    automatic_retry_permitted: bool
    posthoc_parameter_change_permitted: bool
    raw_vector_persistence_permitted: bool
    scalar_file_persistence_permitted: bool
    protected_artifact_change_permitted: bool
    ec46_decision_permitted: bool
    research_decision_permitted: bool
    claims_permitted: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        if (
            self.contract_id != S1_EC83_CONTRACT_ID
            or self.source_ec82_contract_digest != S1_EC83_EC82_CONTRACT_DIGEST
            or self.source_ec82_sha256 != S1_EC83_EC82_SOURCE_SHA256
            or self.prior_authorization_id != "S1-EC78"
            or self.prior_authorization_consumed is not True
            or self.refinement_id != "n2/r2"
            or self.stages != S1_EC83_STAGES
            or (self.planned_execution_count, self.authorized_execution_count)
            != (1, 0)
            or (
                self.maximum_formation_steps,
                self.maximum_probe_steps,
                self.maximum_total_field_steps,
            )
            != (1608, 1600, 3208)
            or self.maximum_runtime_seconds != 900.0
            or (
                self.expected_formation_count,
                self.expected_fresh_field_count,
                self.expected_probe_count,
                self.expected_scalar_contrast_count,
            )
            != (4, 8, 8, 6)
            or any(
                value is not True
                for value in (
                    self.fresh_preflight_required,
                    self.explicit_new_owner_authorization_required,
                    self.scalar_receipt_required_before_result_release,
                    self.stop_on_execution_or_handoff_error,
                )
            )
            or any(
                value is not False
                for value in (
                    self.owner_authorization_present,
                    self.execution_permitted,
                    self.automatic_retry_permitted,
                    self.posthoc_parameter_change_permitted,
                    self.raw_vector_persistence_permitted,
                    self.scalar_file_persistence_permitted,
                    self.protected_artifact_change_permitted,
                    self.ec46_decision_permitted,
                    self.research_decision_permitted,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "R2_ONE_SHOT_MEASUREMENT_CONTRACT_BOUND_AWAITING_NEW_AUTHORIZATION"
        ):
            raise E1CommonProbeR2EC83OneShotMeasurementContractError(
                "S1-EC83 contract changed or released execution"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "contract_digest"
        }
        if self.contract_digest != _digest(payload):
            raise E1CommonProbeR2EC83OneShotMeasurementContractError(
                "S1-EC83 contract digest changed"
            )


def build_e1_common_probe_r2_ec83_one_shot_measurement_contract(
    project_root: Path,
    handoff: E1CommonProbeR2EC82CoordinatorHandoffContract,
) -> E1CommonProbeR2EC83OneShotMeasurementContract:
    """Bind one closed measurement attempt without accepting authorization."""

    if not isinstance(handoff, E1CommonProbeR2EC82CoordinatorHandoffContract):
        raise E1CommonProbeR2EC83OneShotMeasurementContractError(
            "S1-EC83 requires the typed EC82 handoff contract"
        )
    handoff.__post_init__()
    if handoff.contract_digest != S1_EC83_EC82_CONTRACT_DIGEST:
        raise E1CommonProbeR2EC83OneShotMeasurementContractError(
            "S1-EC83 EC82 contract binding changed"
        )
    source = Path(project_root) / S1_EC83_EC82_SOURCE_RELATIVE_PATH
    try:
        observed_source_sha256 = hashlib.sha256(source.read_bytes()).hexdigest()
    except OSError as exc:
        raise E1CommonProbeR2EC83OneShotMeasurementContractError(
            "S1-EC83 requires the exact EC82 source"
        ) from exc
    values = {
        "contract_id": S1_EC83_CONTRACT_ID,
        "source_ec82_contract_digest": handoff.contract_digest,
        "source_ec82_sha256": observed_source_sha256,
        "prior_authorization_id": "S1-EC78",
        "prior_authorization_consumed": True,
        "refinement_id": "n2/r2",
        "stages": S1_EC83_STAGES,
        "planned_execution_count": 1,
        "authorized_execution_count": 0,
        "maximum_formation_steps": 1608,
        "maximum_probe_steps": 1600,
        "maximum_total_field_steps": 3208,
        "maximum_runtime_seconds": 900.0,
        "expected_formation_count": 4,
        "expected_fresh_field_count": 8,
        "expected_probe_count": 8,
        "expected_scalar_contrast_count": 6,
        "fresh_preflight_required": True,
        "explicit_new_owner_authorization_required": True,
        "scalar_receipt_required_before_result_release": True,
        "stop_on_execution_or_handoff_error": True,
        "owner_authorization_present": False,
        "execution_permitted": False,
        "automatic_retry_permitted": False,
        "posthoc_parameter_change_permitted": False,
        "raw_vector_persistence_permitted": False,
        "scalar_file_persistence_permitted": False,
        "protected_artifact_change_permitted": False,
        "ec46_decision_permitted": False,
        "research_decision_permitted": False,
        "claims_permitted": False,
        "decision": (
            "R2_ONE_SHOT_MEASUREMENT_CONTRACT_BOUND_AWAITING_NEW_AUTHORIZATION"
        ),
    }
    return E1CommonProbeR2EC83OneShotMeasurementContract(
        **values, contract_digest=_digest(values)
    )
