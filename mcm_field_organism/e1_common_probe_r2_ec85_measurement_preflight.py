"""S1-EC85 static aggregate preflight for the closed EC83/EC84 path."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path

from .e1_common_probe_n2_r2_corrected_final_preflight import (
    E1CommonProbeN2R2CorrectedFinalPreflight,
)
from .e1_common_probe_r2_ec83_one_shot_measurement_contract import (
    E1CommonProbeR2EC83OneShotMeasurementContract,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeR2EC85MeasurementPreflightError(ValueError):
    """Raised when EC85 loses a technical gate or releases execution."""


S1_EC85_PREFLIGHT_ID = "e1.common-probe-r2-measurement-preflight.s1ec85.v1"
S1_EC85_EC83_CONTRACT_DIGEST = (
    "72fc107a4ecd91ff8b8ddf5bb5226990b41c603c81cb763c99ae98d69b92ae88"
)
S1_EC85_EC84_SOURCE_RELATIVE_PATH = (
    "mcm_field_organism/e1_common_probe_r2_ec84_atomic_return.py"
)
S1_EC85_EC84_SOURCE_SHA256 = (
    "3ca115de9a70d44150da111b6538c5ad4b5d8aa96465beb6851c198f9e69aa6a"
)
S1_EC85_REQUIRED_CHECKS = (
    "ec72-current-technical-and-source-preflight-ready",
    "ec72-resource-and-protected-artifact-digests-bound",
    "ec83-closed-one-shot-measurement-contract-exact",
    "ec84-atomic-return-source-exact",
    "planned-load-exactly-3208-field-steps",
    "four-formation-eight-fresh-eight-probe-six-scalar-route",
    "runtime-cap-nine-hundred-seconds",
    "in-memory-no-retry-persistence-decision-or-claim",
    "new-owner-execution-authorization-not-present",
)


@dataclass(frozen=True, slots=True)
class E1CommonProbeR2EC85MeasurementPreflight:
    preflight_id: str
    source_ec72_preflight_digest: str
    source_ec83_contract_digest: str
    source_ec84_expected_sha256: str
    source_ec84_observed_sha256: str
    resource_snapshot_digest: str
    protected_artifact_audit_digest: str
    planned_formation_steps: int
    planned_probe_steps: int
    planned_total_steps: int
    expected_formation_count: int
    expected_fresh_field_count: int
    expected_probe_count: int
    expected_scalar_contrast_count: int
    maximum_runtime_seconds: float
    checks: tuple[tuple[str, bool], ...]
    technical_request_ready: bool
    owner_authorization_present: bool
    execution_permitted: bool
    automatic_retry_permitted: bool
    persistence_permitted: bool
    ec46_decision_permitted: bool
    research_decision_permitted: bool
    claims_permitted: bool
    decision: str
    reason: str
    preflight_digest: str

    def __post_init__(self) -> None:
        technical_ready = all(value for _, value in self.checks[:-1])
        expected_decision = (
            "MEASUREMENT_PATH_READY_TO_REQUEST_NEW_ONE_SHOT_AUTHORIZATION"
            if technical_ready
            else "CORRECT_MEASUREMENT_PREFLIGHT_GATES"
        )
        if (
            self.preflight_id != S1_EC85_PREFLIGHT_ID
            or len(self.source_ec72_preflight_digest) != 64
            or self.source_ec83_contract_digest != S1_EC85_EC83_CONTRACT_DIGEST
            or self.source_ec84_expected_sha256 != S1_EC85_EC84_SOURCE_SHA256
            or len(self.source_ec84_observed_sha256) != 64
            or len(self.resource_snapshot_digest) != 64
            or len(self.protected_artifact_audit_digest) != 64
            or (
                self.planned_formation_steps,
                self.planned_probe_steps,
                self.planned_total_steps,
            )
            != (1608, 1600, 3208)
            or (
                self.expected_formation_count,
                self.expected_fresh_field_count,
                self.expected_probe_count,
                self.expected_scalar_contrast_count,
            )
            != (4, 8, 8, 6)
            or self.maximum_runtime_seconds != 900.0
            or tuple(name for name, _ in self.checks) != S1_EC85_REQUIRED_CHECKS
            or self.technical_request_ready is not technical_ready
            or any(
                value is not False
                for value in (
                    self.owner_authorization_present,
                    self.execution_permitted,
                    self.automatic_retry_permitted,
                    self.persistence_permitted,
                    self.ec46_decision_permitted,
                    self.research_decision_permitted,
                    self.claims_permitted,
                )
            )
            or self.decision != expected_decision
            or not self.reason
        ):
            raise E1CommonProbeR2EC85MeasurementPreflightError(
                "S1-EC85 preflight changed or released execution"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "preflight_digest"
        }
        if self.preflight_digest != _digest(payload):
            raise E1CommonProbeR2EC85MeasurementPreflightError(
                "S1-EC85 preflight digest changed"
            )


def audit_e1_common_probe_r2_ec85_measurement_preflight(
    project_root: Path,
    technical: E1CommonProbeN2R2CorrectedFinalPreflight,
    contract: E1CommonProbeR2EC83OneShotMeasurementContract,
) -> E1CommonProbeR2EC85MeasurementPreflight:
    """Aggregate EC72, EC83, and EC84 without accepting authorization."""

    if not isinstance(technical, E1CommonProbeN2R2CorrectedFinalPreflight):
        raise E1CommonProbeR2EC85MeasurementPreflightError(
            "S1-EC85 requires the typed EC72 preflight"
        )
    if not isinstance(contract, E1CommonProbeR2EC83OneShotMeasurementContract):
        raise E1CommonProbeR2EC85MeasurementPreflightError(
            "S1-EC85 requires the typed EC83 contract"
        )
    technical.__post_init__()
    contract.__post_init__()
    source = Path(project_root) / S1_EC85_EC84_SOURCE_RELATIVE_PATH
    try:
        observed_ec84 = hashlib.sha256(source.read_bytes()).hexdigest()
    except OSError as exc:
        raise E1CommonProbeR2EC85MeasurementPreflightError(
            "S1-EC85 requires the exact EC84 source"
        ) from exc
    checks = (
        (
            "ec72-current-technical-and-source-preflight-ready",
            technical.technical_execution_ready
            and technical.owner_execution_authorized is False
            and technical.coordinator_execution_permitted is False,
        ),
        (
            "ec72-resource-and-protected-artifact-digests-bound",
            bool(technical.resource_snapshot_digest)
            and bool(technical.protected_artifact_audit_digest),
        ),
        (
            "ec83-closed-one-shot-measurement-contract-exact",
            contract.contract_digest == S1_EC85_EC83_CONTRACT_DIGEST
            and contract.authorized_execution_count == 0
            and contract.execution_permitted is False,
        ),
        (
            "ec84-atomic-return-source-exact",
            observed_ec84 == S1_EC85_EC84_SOURCE_SHA256,
        ),
        (
            "planned-load-exactly-3208-field-steps",
            (
                technical.planned_formation_steps,
                technical.planned_probe_steps,
                technical.planned_total_steps,
            )
            == (1608, 1600, 3208)
            and contract.maximum_total_field_steps == 3208,
        ),
        (
            "four-formation-eight-fresh-eight-probe-six-scalar-route",
            (
                contract.expected_formation_count,
                contract.expected_fresh_field_count,
                contract.expected_probe_count,
                contract.expected_scalar_contrast_count,
            )
            == (4, 8, 8, 6),
        ),
        (
            "runtime-cap-nine-hundred-seconds",
            technical.maximum_runtime_seconds
            == contract.maximum_runtime_seconds
            == 900.0,
        ),
        (
            "in-memory-no-retry-persistence-decision-or-claim",
            not any(
                (
                    technical.retry_permitted,
                    technical.persistence_permitted,
                    technical.research_decision_permitted,
                    technical.ec46_decision_permitted,
                    contract.automatic_retry_permitted,
                    contract.raw_vector_persistence_permitted,
                    contract.scalar_file_persistence_permitted,
                    contract.ec46_decision_permitted,
                    contract.research_decision_permitted,
                    contract.claims_permitted,
                )
            ),
        ),
        ("new-owner-execution-authorization-not-present", False),
    )
    technical_ready = all(value for _, value in checks[:-1])
    values = {
        "preflight_id": S1_EC85_PREFLIGHT_ID,
        "source_ec72_preflight_digest": technical.preflight_digest,
        "source_ec83_contract_digest": contract.contract_digest,
        "source_ec84_expected_sha256": S1_EC85_EC84_SOURCE_SHA256,
        "source_ec84_observed_sha256": observed_ec84,
        "resource_snapshot_digest": technical.resource_snapshot_digest,
        "protected_artifact_audit_digest": technical.protected_artifact_audit_digest,
        "planned_formation_steps": technical.planned_formation_steps,
        "planned_probe_steps": technical.planned_probe_steps,
        "planned_total_steps": technical.planned_total_steps,
        "expected_formation_count": contract.expected_formation_count,
        "expected_fresh_field_count": contract.expected_fresh_field_count,
        "expected_probe_count": contract.expected_probe_count,
        "expected_scalar_contrast_count": contract.expected_scalar_contrast_count,
        "maximum_runtime_seconds": contract.maximum_runtime_seconds,
        "checks": checks,
        "technical_request_ready": technical_ready,
        "owner_authorization_present": False,
        "execution_permitted": False,
        "automatic_retry_permitted": False,
        "persistence_permitted": False,
        "ec46_decision_permitted": False,
        "research_decision_permitted": False,
        "claims_permitted": False,
        "decision": (
            "MEASUREMENT_PATH_READY_TO_REQUEST_NEW_ONE_SHOT_AUTHORIZATION"
            if technical_ready
            else "CORRECT_MEASUREMENT_PREFLIGHT_GATES"
        ),
        "reason": (
            "ec72-ec83-ec84-exact-new-explicit-owner-authorization-required"
            if technical_ready
            else "one-or-more-measurement-path-gates-failed"
        ),
    }
    return E1CommonProbeR2EC85MeasurementPreflight(
        **values, preflight_digest=_digest(values)
    )
