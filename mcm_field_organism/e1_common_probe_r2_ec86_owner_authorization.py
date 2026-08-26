"""S1-EC86 owner authorization for one EC83/EC85 measurement run."""

from __future__ import annotations

from dataclasses import dataclass

from .e1_common_probe_r2_ec85_measurement_preflight import (
    E1CommonProbeR2EC85MeasurementPreflight,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeR2EC86OwnerAuthorizationError(ValueError):
    """Raised when EC86 exceeds the explicit one-shot authorization."""


S1_EC86_AUTHORIZATION_ID = (
    "e1.common-probe-r2-owner-authorization.s1ec86.once.v1"
)


@dataclass(frozen=True, slots=True)
class E1CommonProbeR2EC86OwnerAuthorization:
    authorization_id: str
    source_ec85_preflight_digest: str
    source_ec83_contract_digest: str
    project_owner_authorization: str
    authorized_execution_count: int
    maximum_total_field_steps: int
    maximum_runtime_seconds: float
    atomic_ec84_return_required: bool
    expected_scalar_contrast_count: int
    nonpersistent_only: bool
    automatic_retry_permitted: bool
    posthoc_parameter_change_permitted: bool
    persistence_permitted: bool
    ec46_decision_permitted: bool
    research_decision_permitted: bool
    claims_permitted: bool
    execution_started: bool
    status: str
    authorization_digest: str

    def __post_init__(self) -> None:
        if (
            self.authorization_id != S1_EC86_AUTHORIZATION_ID
            or len(self.source_ec85_preflight_digest) != 64
            or len(self.source_ec83_contract_digest) != 64
            or self.project_owner_authorization
            != "AUTHORIZED_ONE_EC83_EC85_R2_MEASUREMENT_RUN"
            or self.authorized_execution_count != 1
            or self.maximum_total_field_steps != 3208
            or self.maximum_runtime_seconds != 900.0
            or self.atomic_ec84_return_required is not True
            or self.expected_scalar_contrast_count != 6
            or self.nonpersistent_only is not True
            or any(
                value is not False
                for value in (
                    self.automatic_retry_permitted,
                    self.posthoc_parameter_change_permitted,
                    self.persistence_permitted,
                    self.ec46_decision_permitted,
                    self.research_decision_permitted,
                    self.claims_permitted,
                    self.execution_started,
                )
            )
            or self.status
            != "OWNER_AUTHORIZED_ONE_EC83_EC85_R2_MEASUREMENT_RUN_NOT_STARTED"
        ):
            raise E1CommonProbeR2EC86OwnerAuthorizationError(
                "S1-EC86 authorization changed or exceeded one-shot scope"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "authorization_digest"
        }
        if self.authorization_digest != _digest(payload):
            raise E1CommonProbeR2EC86OwnerAuthorizationError(
                "S1-EC86 authorization digest changed"
            )


def bind_e1_common_probe_r2_ec86_owner_authorization(
    preflight: E1CommonProbeR2EC85MeasurementPreflight,
    *,
    explicit_owner_authorized: bool,
) -> E1CommonProbeR2EC86OwnerAuthorization:
    """Bind one explicit owner decision without starting the measurement path."""

    if not isinstance(preflight, E1CommonProbeR2EC85MeasurementPreflight):
        raise E1CommonProbeR2EC86OwnerAuthorizationError(
            "S1-EC86 requires one typed EC85 preflight"
        )
    preflight.__post_init__()
    if explicit_owner_authorized is not True:
        raise E1CommonProbeR2EC86OwnerAuthorizationError(
            "S1-EC86 requires explicit owner authorization"
        )
    if (
        preflight.technical_request_ready is not True
        or preflight.owner_authorization_present is not False
        or preflight.execution_permitted is not False
        or preflight.planned_total_steps != 3208
        or preflight.expected_scalar_contrast_count != 6
    ):
        raise E1CommonProbeR2EC86OwnerAuthorizationError(
            "S1-EC86 requires the unchanged ready but closed EC85 preflight"
        )
    values = {
        "authorization_id": S1_EC86_AUTHORIZATION_ID,
        "source_ec85_preflight_digest": preflight.preflight_digest,
        "source_ec83_contract_digest": preflight.source_ec83_contract_digest,
        "project_owner_authorization": (
            "AUTHORIZED_ONE_EC83_EC85_R2_MEASUREMENT_RUN"
        ),
        "authorized_execution_count": 1,
        "maximum_total_field_steps": preflight.planned_total_steps,
        "maximum_runtime_seconds": preflight.maximum_runtime_seconds,
        "atomic_ec84_return_required": True,
        "expected_scalar_contrast_count": preflight.expected_scalar_contrast_count,
        "nonpersistent_only": True,
        "automatic_retry_permitted": False,
        "posthoc_parameter_change_permitted": False,
        "persistence_permitted": False,
        "ec46_decision_permitted": False,
        "research_decision_permitted": False,
        "claims_permitted": False,
        "execution_started": False,
        "status": (
            "OWNER_AUTHORIZED_ONE_EC83_EC85_R2_MEASUREMENT_RUN_NOT_STARTED"
        ),
    }
    return E1CommonProbeR2EC86OwnerAuthorization(
        **values, authorization_digest=_digest(values)
    )
