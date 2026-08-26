"""S1-EC73 static contract for one diagnostic n2/r2 follow-up after EC69."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re

from .e1_common_probe_n2_r2_corrected_final_preflight import (
    E1CommonProbeN2R2CorrectedFinalPreflight,
)
from .e1_common_probe_n2_r2_real_output_converters import (
    S1_EC70_FORMATION_DIAGNOSTIC_GATES,
)


class E1CommonProbeN2R2DiagnosticOneShotContractError(ValueError):
    """Raised when the EC73 diagnostic one-shot boundary changes."""


S1_EC73_CONTRACT_ID = (
    "e1.common-probe-n2-r2-diagnostic-one-shot-contract.s1ec73.v1"
)
S1_EC73_REPORT_SECTIONS = (
    "measurement",
    "technical-interpretation",
    "non-evidence",
    "open-assumptions",
)
_SHA256 = re.compile(r"[0-9a-f]{64}")


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class E1CommonProbeN2R2DiagnosticOneShotContract:
    contract_id: str
    source_ec72_preflight_digest: str
    source_ec71_preflight_digest: str
    prior_attempt_id: str
    attempt_kind: str
    refinement_id: str
    planned_execution_count: int
    authorized_execution_count: int
    formation_arm_count: int
    fresh_field_count: int
    probe_count: int
    maximum_formation_steps: int
    maximum_probe_steps: int
    maximum_total_field_steps: int
    first_formation_arm_steps: int
    maximum_runtime_seconds: float
    diagnostic_gate_names: tuple[str, ...]
    stop_on_first_failed_diagnostic_gate: bool
    failed_gate_names_must_be_reported: bool
    report_sections: tuple[str, ...]
    preflight_refresh_required_before_execution: bool
    explicit_new_owner_authorization_required: bool
    owner_authorization_present: bool
    execution_permitted: bool
    automatic_retry_permitted: bool
    posthoc_parameter_change_permitted: bool
    raw_output_persistence_permitted: bool
    protected_artifact_change_permitted: bool
    research_decision_permitted: bool
    memory_claim_permitted: bool
    field_time_claim_permitted: bool
    organization_claim_permitted: bool
    ai_claim_permitted: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        if (
            self.contract_id != S1_EC73_CONTRACT_ID
            or not _SHA256.fullmatch(self.source_ec72_preflight_digest)
            or not _SHA256.fullmatch(self.source_ec71_preflight_digest)
            or self.prior_attempt_id != "S1-EC69"
            or self.attempt_kind != "diagnostic-follow-up-after-partial-abort"
            or self.refinement_id != "n2/r2"
            or (self.planned_execution_count, self.authorized_execution_count)
            != (1, 0)
            or (self.formation_arm_count, self.fresh_field_count, self.probe_count)
            != (4, 8, 8)
            or (
                self.maximum_formation_steps,
                self.maximum_probe_steps,
                self.maximum_total_field_steps,
                self.first_formation_arm_steps,
            )
            != (1608, 1600, 3208, 402)
            or self.maximum_runtime_seconds != 900.0
            or self.diagnostic_gate_names != S1_EC70_FORMATION_DIAGNOSTIC_GATES
            or self.report_sections != S1_EC73_REPORT_SECTIONS
            or any(
                value is not True
                for value in (
                    self.stop_on_first_failed_diagnostic_gate,
                    self.failed_gate_names_must_be_reported,
                    self.preflight_refresh_required_before_execution,
                    self.explicit_new_owner_authorization_required,
                )
            )
            or any(
                value is not False
                for value in (
                    self.owner_authorization_present,
                    self.execution_permitted,
                    self.automatic_retry_permitted,
                    self.posthoc_parameter_change_permitted,
                    self.raw_output_persistence_permitted,
                    self.protected_artifact_change_permitted,
                    self.research_decision_permitted,
                    self.memory_claim_permitted,
                    self.field_time_claim_permitted,
                    self.organization_claim_permitted,
                    self.ai_claim_permitted,
                )
            )
            or self.decision
            != "DIAGNOSTIC_ONE_SHOT_CONTRACT_BOUND_AWAITING_EXPLICIT_OWNER_AUTHORIZATION"
        ):
            raise E1CommonProbeN2R2DiagnosticOneShotContractError(
                "S1-EC73 contract changed or released execution"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "contract_digest"
        }
        if self.contract_digest != _digest(payload):
            raise E1CommonProbeN2R2DiagnosticOneShotContractError(
                "S1-EC73 contract digest changed"
            )


def prepare_e1_common_probe_n2_r2_diagnostic_one_shot_contract(
    preflight: E1CommonProbeN2R2CorrectedFinalPreflight,
) -> E1CommonProbeN2R2DiagnosticOneShotContract:
    """Bind one closed diagnostic attempt without accepting authorization."""

    if not isinstance(preflight, E1CommonProbeN2R2CorrectedFinalPreflight):
        raise E1CommonProbeN2R2DiagnosticOneShotContractError(
            "S1-EC73 requires one validated EC72 preflight"
        )
    preflight.__post_init__()
    if (
        preflight.technical_execution_ready is not True
        or preflight.owner_execution_authorized is not False
        or preflight.coordinator_execution_permitted is not False
        or preflight.adapter_execution_permitted is not False
        or preflight.retry_permitted is not False
    ):
        raise E1CommonProbeN2R2DiagnosticOneShotContractError(
            "S1-EC73 requires ready but unreleased EC72"
        )
    values = {
        "contract_id": S1_EC73_CONTRACT_ID,
        "source_ec72_preflight_digest": preflight.preflight_digest,
        "source_ec71_preflight_digest": preflight.ec71_preflight_digest,
        "prior_attempt_id": "S1-EC69",
        "attempt_kind": "diagnostic-follow-up-after-partial-abort",
        "refinement_id": "n2/r2",
        "planned_execution_count": 1,
        "authorized_execution_count": 0,
        "formation_arm_count": 4,
        "fresh_field_count": 8,
        "probe_count": 8,
        "maximum_formation_steps": 1608,
        "maximum_probe_steps": 1600,
        "maximum_total_field_steps": 3208,
        "first_formation_arm_steps": 402,
        "maximum_runtime_seconds": 900.0,
        "diagnostic_gate_names": S1_EC70_FORMATION_DIAGNOSTIC_GATES,
        "stop_on_first_failed_diagnostic_gate": True,
        "failed_gate_names_must_be_reported": True,
        "report_sections": S1_EC73_REPORT_SECTIONS,
        "preflight_refresh_required_before_execution": True,
        "explicit_new_owner_authorization_required": True,
        "owner_authorization_present": False,
        "execution_permitted": False,
        "automatic_retry_permitted": False,
        "posthoc_parameter_change_permitted": False,
        "raw_output_persistence_permitted": False,
        "protected_artifact_change_permitted": False,
        "research_decision_permitted": False,
        "memory_claim_permitted": False,
        "field_time_claim_permitted": False,
        "organization_claim_permitted": False,
        "ai_claim_permitted": False,
        "decision": (
            "DIAGNOSTIC_ONE_SHOT_CONTRACT_BOUND_AWAITING_EXPLICIT_OWNER_AUTHORIZATION"
        ),
    }
    return E1CommonProbeN2R2DiagnosticOneShotContract(
        **values,
        contract_digest=_digest(values),
    )
