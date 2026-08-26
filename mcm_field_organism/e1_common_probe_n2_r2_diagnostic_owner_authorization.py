"""S1-EC74 owner authorization for one EC73 diagnostic n2/r2 attempt."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re

from .e1_common_probe_n2_r2_diagnostic_one_shot_contract import (
    E1CommonProbeN2R2DiagnosticOneShotContract,
)


class E1CommonProbeN2R2DiagnosticOwnerAuthorizationError(ValueError):
    """Raised when the EC74 one-shot authorization boundary changes."""


S1_EC74_AUTHORIZATION_ID = (
    "e1.common-probe-n2-r2-diagnostic-owner-authorization.s1ec74.once.v1"
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
class E1CommonProbeN2R2DiagnosticOwnerAuthorization:
    authorization_id: str
    source_ec73_contract_digest: str
    source_ec72_preflight_digest: str
    project_owner_authorization: str
    authorized_execution_count: int
    maximum_total_field_steps: int
    maximum_runtime_seconds: float
    nonpersistent_only: bool
    stop_on_first_failed_diagnostic_gate: bool
    automatic_retry_permitted: bool
    posthoc_parameter_change_permitted: bool
    persistence_permitted: bool
    research_decision_permitted: bool
    claims_permitted: bool
    execution_started: bool
    authorization_status: str
    authorization_digest: str

    def __post_init__(self) -> None:
        if (
            self.authorization_id != S1_EC74_AUTHORIZATION_ID
            or not _SHA256.fullmatch(self.source_ec73_contract_digest)
            or not _SHA256.fullmatch(self.source_ec72_preflight_digest)
            or self.project_owner_authorization != "AUTHORIZED_ONE_DIAGNOSTIC_RUN"
            or self.authorized_execution_count != 1
            or self.maximum_total_field_steps != 3208
            or self.maximum_runtime_seconds != 900.0
            or self.nonpersistent_only is not True
            or self.stop_on_first_failed_diagnostic_gate is not True
            or any(
                value is not False
                for value in (
                    self.automatic_retry_permitted,
                    self.posthoc_parameter_change_permitted,
                    self.persistence_permitted,
                    self.research_decision_permitted,
                    self.claims_permitted,
                    self.execution_started,
                )
            )
            or self.authorization_status
            != "OWNER_AUTHORIZED_ONE_DIAGNOSTIC_RUN_NOT_STARTED"
        ):
            raise E1CommonProbeN2R2DiagnosticOwnerAuthorizationError(
                "S1-EC74 authorization changed or exceeded one-shot scope"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "authorization_digest"
        }
        if self.authorization_digest != _digest(payload):
            raise E1CommonProbeN2R2DiagnosticOwnerAuthorizationError(
                "S1-EC74 authorization digest changed"
            )


def bind_e1_common_probe_n2_r2_diagnostic_owner_authorization(
    contract: E1CommonProbeN2R2DiagnosticOneShotContract,
    *,
    explicit_owner_authorized: bool,
) -> E1CommonProbeN2R2DiagnosticOwnerAuthorization:
    """Bind one explicit owner decision without executing the diagnostic path."""

    if not isinstance(contract, E1CommonProbeN2R2DiagnosticOneShotContract):
        raise E1CommonProbeN2R2DiagnosticOwnerAuthorizationError(
            "S1-EC74 requires one validated EC73 contract"
        )
    contract.__post_init__()
    if explicit_owner_authorized is not True:
        raise E1CommonProbeN2R2DiagnosticOwnerAuthorizationError(
            "S1-EC74 requires explicit owner authorization"
        )
    if (
        contract.authorized_execution_count != 0
        or contract.execution_permitted is not False
        or contract.explicit_new_owner_authorization_required is not True
        or contract.automatic_retry_permitted is not False
    ):
        raise E1CommonProbeN2R2DiagnosticOwnerAuthorizationError(
            "S1-EC74 requires the unchanged closed EC73 contract"
        )
    values = {
        "authorization_id": S1_EC74_AUTHORIZATION_ID,
        "source_ec73_contract_digest": contract.contract_digest,
        "source_ec72_preflight_digest": contract.source_ec72_preflight_digest,
        "project_owner_authorization": "AUTHORIZED_ONE_DIAGNOSTIC_RUN",
        "authorized_execution_count": 1,
        "maximum_total_field_steps": contract.maximum_total_field_steps,
        "maximum_runtime_seconds": contract.maximum_runtime_seconds,
        "nonpersistent_only": True,
        "stop_on_first_failed_diagnostic_gate": (
            contract.stop_on_first_failed_diagnostic_gate
        ),
        "automatic_retry_permitted": False,
        "posthoc_parameter_change_permitted": False,
        "persistence_permitted": False,
        "research_decision_permitted": False,
        "claims_permitted": False,
        "execution_started": False,
        "authorization_status": "OWNER_AUTHORIZED_ONE_DIAGNOSTIC_RUN_NOT_STARTED",
    }
    return E1CommonProbeN2R2DiagnosticOwnerAuthorization(
        **values,
        authorization_digest=_digest(values),
    )
