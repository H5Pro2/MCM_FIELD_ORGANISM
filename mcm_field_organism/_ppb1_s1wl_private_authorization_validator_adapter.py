"""Private pure S1-WL validator for injected authorization text."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re

from ._ppb1_s1wb_private_production_h0_types import (
    S1WB_AUTHORIZATION_TEMPLATE,
    S1WB_CALIBRATION_DIGEST,
    S1WB_CASE_COUNT,
    S1WB_CONTRACT_DIGEST,
    S1WB_CORRECTED_PLAN_DIGEST,
    S1WB_MAXIMUM_CALL_COUNT,
    S1WB_PARENT_PLAN_DIGEST,
    S1WB_PRODUCTION_ENTRYPOINT_ID,
)
from ._ppb1_s1wh_private_injected_coordinator_shell import (
    S1WGExactProductionAuthorizationActivator,
    S1WHInjectedStageAdapter,
)


S1WL_SCHEMA_VERSION = "ppb1.s1wl.private.injected-authorization-validator.v1"
S1WL_MODE = "INJECTED_TEXT_VALIDATION_NOT_AUTHORIZATION"
S1WL_ADAPTER_ID = "s1wh.injected.authorization"
S1WL_INVALID_INJECTED_ROLE = "S1WL_INVALID_INJECTED_ROLE"
S1WL_PRODUCTION_AUTHORIZATION_BLOCKED = (
    "S1WL_PRODUCTION_AUTHORIZATION_BLOCKED"
)

_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_EXECUTION_ID = re.compile(r"^ppb1\.[a-z0-9][a-z0-9.-]{2,80}$")


class S1WLAuthorizationValidatorError(ValueError):
    """One fail-closed injected authorization validation violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _canonical_bytes(payload: object) -> bytes:
    return json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _digest(payload: object) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _text_digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


@dataclass(frozen=True, slots=True)
class S1WLInjectedAuthorizationValidationReceipt:
    execution_id: str
    rendered_authorization_text_digest: str
    contract_digest: str
    calibration_digest: str
    resource_gate_digest: str
    parent_plan_digest: str
    corrected_plan_digest: str
    case_count: int
    maximum_registered_call_count: int
    production_entrypoint_id: str
    execution_id_format_valid: bool
    exact_text_match: bool
    digest_roles_match: bool
    production_authorization_instantiated: bool
    execution_id_freshness_check_count: int
    authorization_instantiation_count: int
    filesystem_read_count: int
    filesystem_write_count: int
    producer_resolution_count: int
    producer_call_count: int
    matrix_path_count: int
    production_artifact_count: int
    receipt_digest: str

    def __post_init__(self) -> None:
        digests = (
            self.rendered_authorization_text_digest,
            self.contract_digest,
            self.calibration_digest,
            self.resource_gate_digest,
            self.parent_plan_digest,
            self.corrected_plan_digest,
        )
        if (
            not isinstance(self.execution_id, str)
            or not all(_valid_digest(value) for value in digests)
            or self.case_count != S1WB_CASE_COUNT
            or self.maximum_registered_call_count != S1WB_MAXIMUM_CALL_COUNT
            or self.production_entrypoint_id != S1WB_PRODUCTION_ENTRYPOINT_ID
            or not all(
                isinstance(value, bool)
                for value in (
                    self.execution_id_format_valid,
                    self.exact_text_match,
                    self.digest_roles_match,
                    self.production_authorization_instantiated,
                )
            )
            or self.production_authorization_instantiated is not False
            or any(
                value != 0
                for value in (
                    self.execution_id_freshness_check_count,
                    self.authorization_instantiation_count,
                    self.filesystem_read_count,
                    self.filesystem_write_count,
                    self.producer_resolution_count,
                    self.producer_call_count,
                    self.matrix_path_count,
                    self.production_artifact_count,
                )
            )
            or self.receipt_digest != _digest(self.payload_without_digest())
        ):
            raise S1WLAuthorizationValidatorError(
                S1WL_INVALID_INJECTED_ROLE,
                "invalid injected authorization validation receipt",
            )

    @property
    def injected_text_and_digests_match(self) -> bool:
        return (
            self.execution_id_format_valid
            and self.exact_text_match
            and self.digest_roles_match
        )

    @property
    def ready_for_production_authorization(self) -> bool:
        return False

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": S1WL_SCHEMA_VERSION,
            "mode": S1WL_MODE,
            "execution_id": self.execution_id,
            "rendered_authorization_text_digest": (
                self.rendered_authorization_text_digest
            ),
            "contract_digest": self.contract_digest,
            "calibration_digest": self.calibration_digest,
            "resource_gate_digest": self.resource_gate_digest,
            "parent_plan_digest": self.parent_plan_digest,
            "corrected_plan_digest": self.corrected_plan_digest,
            "case_count": self.case_count,
            "maximum_registered_call_count": (
                self.maximum_registered_call_count
            ),
            "production_entrypoint_id": self.production_entrypoint_id,
            "execution_id_format_valid": self.execution_id_format_valid,
            "exact_text_match": self.exact_text_match,
            "digest_roles_match": self.digest_roles_match,
            "production_authorization_instantiated": (
                self.production_authorization_instantiated
            ),
            "execution_id_freshness_check_count": (
                self.execution_id_freshness_check_count
            ),
            "authorization_instantiation_count": (
                self.authorization_instantiation_count
            ),
            "filesystem_read_count": self.filesystem_read_count,
            "filesystem_write_count": self.filesystem_write_count,
            "producer_resolution_count": self.producer_resolution_count,
            "producer_call_count": self.producer_call_count,
            "matrix_path_count": self.matrix_path_count,
            "production_artifact_count": self.production_artifact_count,
            "injected_text_and_digests_match": (
                self.injected_text_and_digests_match
            ),
            "ready_for_production_authorization": (
                self.ready_for_production_authorization
            ),
        }

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "receipt_digest": self.receipt_digest,
        }


def validate_s1wl_injected_authorization_text(
    rendered_authorization_text: str,
    execution_id: str,
    resource_gate_digest: str,
    *,
    contract_digest: str = S1WB_CONTRACT_DIGEST,
    calibration_digest: str = S1WB_CALIBRATION_DIGEST,
    parent_plan_digest: str = S1WB_PARENT_PLAN_DIGEST,
    corrected_plan_digest: str = S1WB_CORRECTED_PLAN_DIGEST,
) -> S1WLInjectedAuthorizationValidationReceipt:
    """Compare injected values without creating a production authorization."""

    supplied_digests = (
        contract_digest,
        calibration_digest,
        resource_gate_digest,
        parent_plan_digest,
        corrected_plan_digest,
    )
    if (
        not isinstance(rendered_authorization_text, str)
        or not isinstance(execution_id, str)
        or not all(_valid_digest(value) for value in supplied_digests)
    ):
        raise S1WLAuthorizationValidatorError(
            S1WL_INVALID_INJECTED_ROLE,
            "authorization text, execution id and digest roles are required",
        )

    expected_text = S1WB_AUTHORIZATION_TEMPLATE.format(
        execution_id=execution_id,
        contract_digest=S1WB_CONTRACT_DIGEST,
        resource_gate_digest=resource_gate_digest,
    )
    values = {
        "execution_id": execution_id,
        "rendered_authorization_text_digest": _text_digest(
            rendered_authorization_text
        ),
        "contract_digest": contract_digest,
        "calibration_digest": calibration_digest,
        "resource_gate_digest": resource_gate_digest,
        "parent_plan_digest": parent_plan_digest,
        "corrected_plan_digest": corrected_plan_digest,
        "case_count": S1WB_CASE_COUNT,
        "maximum_registered_call_count": S1WB_MAXIMUM_CALL_COUNT,
        "production_entrypoint_id": S1WB_PRODUCTION_ENTRYPOINT_ID,
        "execution_id_format_valid": _EXECUTION_ID.fullmatch(execution_id)
        is not None,
        "exact_text_match": rendered_authorization_text == expected_text,
        "digest_roles_match": (
            contract_digest == S1WB_CONTRACT_DIGEST
            and calibration_digest == S1WB_CALIBRATION_DIGEST
            and parent_plan_digest == S1WB_PARENT_PLAN_DIGEST
            and corrected_plan_digest == S1WB_CORRECTED_PLAN_DIGEST
        ),
        "production_authorization_instantiated": False,
        "execution_id_freshness_check_count": 0,
        "authorization_instantiation_count": 0,
        "filesystem_read_count": 0,
        "filesystem_write_count": 0,
        "producer_resolution_count": 0,
        "producer_call_count": 0,
        "matrix_path_count": 0,
        "production_artifact_count": 0,
    }
    probe = {
        "schema_version": S1WL_SCHEMA_VERSION,
        "mode": S1WL_MODE,
        **values,
        "injected_text_and_digests_match": (
            values["execution_id_format_valid"]
            and values["exact_text_match"]
            and values["digest_roles_match"]
        ),
        "ready_for_production_authorization": False,
    }
    return S1WLInjectedAuthorizationValidationReceipt(
        **values,
        receipt_digest=_digest(probe),
    )


def build_s1wl_injected_h0d_adapter(
    receipt: S1WLInjectedAuthorizationValidationReceipt,
) -> S1WGExactProductionAuthorizationActivator:
    if not isinstance(receipt, S1WLInjectedAuthorizationValidationReceipt):
        raise S1WLAuthorizationValidatorError(
            S1WL_INVALID_INJECTED_ROLE,
            "H0D adapter requires an injected validation receipt",
        )
    stage = S1WHInjectedStageAdapter(
        S1WL_ADAPTER_ID,
        "H0D",
        passed=receipt.injected_text_and_digests_match,
        detail_role=f"S1WL_AUTHORIZATION_TEXT_{receipt.receipt_digest}",
    )
    return S1WGExactProductionAuthorizationActivator(
        S1WL_ADAPTER_ID,
        stage,
        production_authorization_enabled=False,
    )


def execute_s1wl_production_once() -> None:
    raise S1WLAuthorizationValidatorError(
        S1WL_PRODUCTION_AUTHORIZATION_BLOCKED,
        "S1-WL validates injected text but cannot authorize production",
    )
