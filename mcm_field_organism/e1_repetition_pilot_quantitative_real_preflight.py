"""S1-EC39 static real preflight for the quantitative P0 pilot path."""

from __future__ import annotations

from dataclasses import dataclass

from .e1_refined_formation_runner import _digest
from .e1_repetition_pilot_quantitative_p0_integration_contract import (
    E1RepetitionPilotQuantitativeP0IntegrationContract,
)
from .e1_repetition_pilot_quantitative_p0_runner_fixture import (
    E1RepetitionPilotQuantitativeP0RunnerFixtureResult,
)
from .e1_repetition_pilot_real_preflight import E1PilotRealResourceSnapshot
from .e1_repetition_pilot_release_contract import (
    E1RepetitionPilotReleaseContract,
    S1_EC29_FIELD_ARM_STEPS,
    S1_EC29_MIN_FREE_DISK_BYTES,
    S1_EC29_MIN_FREE_MEMORY_BYTES,
)


class E1RepetitionPilotQuantitativeRealPreflightError(ValueError):
    """Raised when S1-EC39 changes or releases the corrected real path."""


S1_EC39_PREFLIGHT_ID = "e1.repetition-pilot-quantitative-real-preflight.s1ec39.v1"
S1_EC39_EC29_CONTRACT_DIGEST = (
    "834b2280cd55d099fe81fd3c0ba506cb6924abea94d27495e42b4480e8d7aff8"
)
S1_EC39_EC37_CONTRACT_DIGEST = (
    "ad9200e960f6c0c68791a41cc2c8810af2d087a7ade4690593e226e1de37502e"
)
S1_EC39_EC38_FIXTURE_DIGEST = (
    "e8f6b0d4140e95fffd33096cbb7a35bea455924a420efbdbaaf1fc188bb3b53e"
)
S1_EC39_REQUIRED_CHECKS = (
    "ec29-matrix-exactly-25368-steps",
    "ec37-quantitative-contract-exact",
    "ec38-synthetic-handoff-fixture-exact",
    "twelve-p0-snapshot-handoffs-bound",
    "free-memory-at-least-four-gib",
    "free-disk-at-least-one-gib",
    "runtime-cap-nine-hundred-seconds",
    "in-memory-only-no-persistence",
    "old-ec34-result-and-authorization-excluded",
    "no-result-decision-or-memory-claim",
    "real-quantitative-p0-handoff-not-yet-implemented",
    "new-owner-execution-authorization-not-present",
)


@dataclass(frozen=True, slots=True)
class E1RepetitionPilotQuantitativeRealPreflight:
    preflight_id: str
    ec29_contract_digest: str
    ec37_contract_digest: str
    ec38_fixture_digest: str
    resource_snapshot_digest: str
    checks: tuple[tuple[str, bool], ...]
    decision: str
    reason: str
    real_runner_implementation_permitted: bool
    real_quantitative_handoff_implemented: bool
    owner_execution_authorized: bool
    pilot_execution_permitted: bool
    persistence_permitted: bool
    result_decision_permitted: bool
    memory_claim_permitted: bool
    preflight_digest: str

    def __post_init__(self) -> None:
        checks = dict(self.checks)
        base_names = S1_EC39_REQUIRED_CHECKS[:10]
        base_ready = all(checks[name] for name in base_names)
        expected_decision = (
            "VORBEREITET_REAL_HANDOFF_FEHLT" if base_ready else "KORREKTUR"
        )
        if (
            self.preflight_id != S1_EC39_PREFLIGHT_ID
            or self.ec29_contract_digest != S1_EC39_EC29_CONTRACT_DIGEST
            or self.ec37_contract_digest != S1_EC39_EC37_CONTRACT_DIGEST
            or self.ec38_fixture_digest != S1_EC39_EC38_FIXTURE_DIGEST
            or len(self.resource_snapshot_digest) != 64
            or tuple(name for name, _ in self.checks) != S1_EC39_REQUIRED_CHECKS
            or self.decision != expected_decision
            or not self.reason
            or self.real_runner_implementation_permitted is not base_ready
            or any(
                value is not False
                for value in (
                    self.real_quantitative_handoff_implemented,
                    self.owner_execution_authorized,
                    self.pilot_execution_permitted,
                    self.persistence_permitted,
                    self.result_decision_permitted,
                    self.memory_claim_permitted,
                )
            )
        ):
            raise E1RepetitionPilotQuantitativeRealPreflightError(
                "S1-EC39 preflight changed or released execution"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "preflight_digest"
        }
        if self.preflight_digest != _digest(payload):
            raise E1RepetitionPilotQuantitativeRealPreflightError(
                "S1-EC39 preflight digest changed"
            )


def audit_e1_repetition_pilot_quantitative_real_preflight(
    pilot_contract: E1RepetitionPilotReleaseContract,
    integration_contract: E1RepetitionPilotQuantitativeP0IntegrationContract,
    runner_fixture: E1RepetitionPilotQuantitativeP0RunnerFixtureResult,
    resources: E1PilotRealResourceSnapshot,
) -> E1RepetitionPilotQuantitativeRealPreflight:
    """Audit corrected real-path prerequisites without running a field."""

    for value, expected, role in (
        (pilot_contract, E1RepetitionPilotReleaseContract, "EC29 contract"),
        (
            integration_contract,
            E1RepetitionPilotQuantitativeP0IntegrationContract,
            "EC37 contract",
        ),
        (
            runner_fixture,
            E1RepetitionPilotQuantitativeP0RunnerFixtureResult,
            "EC38 fixture",
        ),
        (resources, E1PilotRealResourceSnapshot, "resource snapshot"),
    ):
        if not isinstance(value, expected):
            raise E1RepetitionPilotQuantitativeRealPreflightError(
                f"S1-EC39 requires one {role}"
            )
        value.__post_init__()
    checks = (
        ("ec29-matrix-exactly-25368-steps", (
            pilot_contract.contract_digest == S1_EC39_EC29_CONTRACT_DIGEST
            and pilot_contract.field_arm_step_count == S1_EC29_FIELD_ARM_STEPS
        )),
        ("ec37-quantitative-contract-exact", (
            integration_contract.contract_digest == S1_EC39_EC37_CONTRACT_DIGEST
        )),
        ("ec38-synthetic-handoff-fixture-exact", (
            runner_fixture.result_digest == S1_EC39_EC38_FIXTURE_DIGEST
            and runner_fixture.field_execution_performed is False
        )),
        ("twelve-p0-snapshot-handoffs-bound", (
            integration_contract.total_p0_snapshot_count == 12
            and runner_fixture.snapshot_handoff_count == 12
        )),
        ("free-memory-at-least-four-gib", (
            resources.free_memory_bytes >= S1_EC29_MIN_FREE_MEMORY_BYTES
        )),
        ("free-disk-at-least-one-gib", (
            resources.free_disk_bytes >= S1_EC29_MIN_FREE_DISK_BYTES
        )),
        ("runtime-cap-nine-hundred-seconds", (
            pilot_contract.maximum_runtime_seconds == 900.0
        )),
        ("in-memory-only-no-persistence", (
            pilot_contract.persistence_permitted is False
            and integration_contract.persistence_permitted is False
            and runner_fixture.persistence_performed is False
        )),
        ("old-ec34-result-and-authorization-excluded", (
            integration_contract.old_ec34_result_accepted is False
            and integration_contract.old_ec34_authorization_reusable is False
            and runner_fixture.authorization_consumed is False
        )),
        ("no-result-decision-or-memory-claim", (
            integration_contract.result_decision_permitted is False
            and integration_contract.memory_claim_permitted is False
            and runner_fixture.result_decision_permitted is False
            and runner_fixture.memory_claim_permitted is False
        )),
        ("real-quantitative-p0-handoff-not-yet-implemented", False),
        ("new-owner-execution-authorization-not-present", False),
    )
    base_names = S1_EC39_REQUIRED_CHECKS[:10]
    values = dict(checks)
    base_ready = all(values[name] for name in base_names)
    failed = tuple(name for name in base_names if not values[name])
    decision = "VORBEREITET_REAL_HANDOFF_FEHLT" if base_ready else "KORREKTUR"
    reason = (
        "base-gates-ready-real-handoff-and-new-authorization-required"
        if base_ready
        else "failed-base-gates:" + ",".join(failed)
    )
    payload = {
        "preflight_id": S1_EC39_PREFLIGHT_ID,
        "ec29_contract_digest": pilot_contract.contract_digest,
        "ec37_contract_digest": integration_contract.contract_digest,
        "ec38_fixture_digest": runner_fixture.result_digest,
        "resource_snapshot_digest": resources.digest(),
        "checks": checks,
        "decision": decision,
        "reason": reason,
        "real_runner_implementation_permitted": base_ready,
        "real_quantitative_handoff_implemented": False,
        "owner_execution_authorized": False,
        "pilot_execution_permitted": False,
        "persistence_permitted": False,
        "result_decision_permitted": False,
        "memory_claim_permitted": False,
    }
    return E1RepetitionPilotQuantitativeRealPreflight(
        **payload,
        preflight_digest=_digest(payload),
    )

