"""S1-EC78 owner authorization for one run after the EC77 release gate."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re

from .e1_common_probe_n2_r2_ec77_final_release_gate import (
    E1CommonProbeN2R2EC77FinalReleaseGate,
)


class E1CommonProbeN2R2EC78OwnerAuthorizationError(ValueError):
    """Raised when the EC78 authorization exceeds its one-shot boundary."""


S1_EC78_AUTHORIZATION_ID = (
    "e1.common-probe-n2-r2-owner-authorization.s1ec78.once.v1"
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
class E1CommonProbeN2R2EC78OwnerAuthorization:
    authorization_id: str
    source_ec77_gate_digest: str
    source_ec72_preflight_digest: str
    source_ec73_contract_digest: str
    project_owner_authorization: str
    authorized_execution_count: int
    maximum_total_field_steps: int
    maximum_runtime_seconds: float
    nonpersistent_only: bool
    automatic_retry_permitted: bool
    posthoc_parameter_change_permitted: bool
    persistence_permitted: bool
    research_decision_permitted: bool
    claims_permitted: bool
    execution_started: bool
    authorization_status: str
    authorization_digest: str

    def __post_init__(self) -> None:
        for role in (
            "source_ec77_gate_digest",
            "source_ec72_preflight_digest",
            "source_ec73_contract_digest",
            "authorization_digest",
        ):
            if not _SHA256.fullmatch(getattr(self, role)):
                raise E1CommonProbeN2R2EC78OwnerAuthorizationError(
                    f"S1-EC78 {role} is not SHA-256"
                )
        if (
            self.authorization_id != S1_EC78_AUTHORIZATION_ID
            or self.project_owner_authorization
            != "AUTHORIZED_ONE_EC77_DIAGNOSTIC_RUN"
            or self.authorized_execution_count != 1
            or self.maximum_total_field_steps != 3208
            or self.maximum_runtime_seconds != 900.0
            or self.nonpersistent_only is not True
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
            != "OWNER_AUTHORIZED_ONE_EC77_DIAGNOSTIC_RUN_NOT_STARTED"
        ):
            raise E1CommonProbeN2R2EC78OwnerAuthorizationError(
                "S1-EC78 authorization changed or exceeded one-shot scope"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "authorization_digest"
        }
        if self.authorization_digest != _digest(payload):
            raise E1CommonProbeN2R2EC78OwnerAuthorizationError(
                "S1-EC78 authorization digest changed"
            )


def bind_e1_common_probe_n2_r2_ec78_owner_authorization(
    gate: E1CommonProbeN2R2EC77FinalReleaseGate,
    *,
    explicit_owner_authorized: bool,
) -> E1CommonProbeN2R2EC78OwnerAuthorization:
    """Bind one explicit owner decision without starting the real path."""

    if not isinstance(gate, E1CommonProbeN2R2EC77FinalReleaseGate):
        raise E1CommonProbeN2R2EC78OwnerAuthorizationError(
            "S1-EC78 requires one validated EC77 gate"
        )
    gate.__post_init__()
    if explicit_owner_authorized is not True:
        raise E1CommonProbeN2R2EC78OwnerAuthorizationError(
            "S1-EC78 requires explicit owner authorization"
        )
    if (
        gate.technical_one_shot_request_ready is not True
        or gate.explicit_new_owner_authorization_required is not True
        or gate.owner_authorization_present is not False
        or gate.execution_permitted is not False
    ):
        raise E1CommonProbeN2R2EC78OwnerAuthorizationError(
            "S1-EC78 requires the unchanged closed EC77 gate"
        )
    values = {
        "authorization_id": S1_EC78_AUTHORIZATION_ID,
        "source_ec77_gate_digest": gate.gate_digest,
        "source_ec72_preflight_digest": gate.source_ec72_preflight_digest,
        "source_ec73_contract_digest": gate.source_ec73_contract_digest,
        "project_owner_authorization": "AUTHORIZED_ONE_EC77_DIAGNOSTIC_RUN",
        "authorized_execution_count": 1,
        "maximum_total_field_steps": gate.maximum_total_field_steps,
        "maximum_runtime_seconds": gate.maximum_runtime_seconds,
        "nonpersistent_only": True,
        "automatic_retry_permitted": False,
        "posthoc_parameter_change_permitted": False,
        "persistence_permitted": False,
        "research_decision_permitted": False,
        "claims_permitted": False,
        "execution_started": False,
        "authorization_status": (
            "OWNER_AUTHORIZED_ONE_EC77_DIAGNOSTIC_RUN_NOT_STARTED"
        ),
    }
    return E1CommonProbeN2R2EC78OwnerAuthorization(
        **values,
        authorization_digest=_digest(values),
    )
