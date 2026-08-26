"""S1-EC43 final static preflight for the quantitative n1/n2 pilot."""

from __future__ import annotations

from dataclasses import dataclass

from .e1_refined_formation_runner import _digest
from .e1_repetition_pilot_quantitative_full_runner_fixture import (
    E1RepetitionPilotQuantitativeFullRunnerFixtureResult,
)
from .e1_repetition_pilot_quantitative_p0_integration_contract import (
    E1RepetitionPilotQuantitativeP0IntegrationContract,
)
from .e1_repetition_pilot_quantitative_post_handoff_preflight import (
    E1RepetitionPilotQuantitativePostHandoffPreflight,
)
from .e1_repetition_pilot_real_preflight import E1PilotRealResourceSnapshot
from .e1_repetition_pilot_release_contract import (
    E1RepetitionPilotReleaseContract,
    S1_EC29_MIN_FREE_DISK_BYTES,
    S1_EC29_MIN_FREE_MEMORY_BYTES,
)


class E1RepetitionPilotQuantitativeFinalPreflightError(ValueError):
    """Raised when S1-EC43 changes or bypasses the final release gate."""


S1_EC43_PREFLIGHT_ID = "e1.repetition-pilot-quantitative-final-preflight.s1ec43.v1"
S1_EC43_EC29_CONTRACT_DIGEST = (
    "834b2280cd55d099fe81fd3c0ba506cb6924abea94d27495e42b4480e8d7aff8"
)
S1_EC43_EC37_CONTRACT_DIGEST = (
    "ad9200e960f6c0c68791a41cc2c8810af2d087a7ade4690593e226e1de37502e"
)
S1_EC43_EC41_PREFLIGHT_DIGEST = (
    "2015d17166fd6695db7f5cf6086611bd057d2ab0213d886d68275bda93a771b6"
)
S1_EC43_EC42_INTEGRATION_DIGEST = (
    "9073aa10c0ee6c3ca906efacc198bcdaef16782346af4b720df05a8c605eafc9"
)
S1_EC43_REQUIRED_CHECKS = (
    "ec29-matrix-exactly-25368-steps",
    "ec37-twelve-snapshot-contract-exact",
    "ec41-small-real-handoff-confirmed",
    "ec42-full-runner-integration-exact",
    "ec42-zero-real-field-steps",
    "twelve-immediate-p0-handoffs",
    "six-pairs-and-two-profiles",
    "free-memory-at-least-four-gib",
    "free-disk-at-least-one-gib",
    "runtime-cap-nine-hundred-seconds",
    "in-memory-no-persistence-decision-or-claim",
    "new-owner-execution-authorization-not-present",
)


@dataclass(frozen=True, slots=True)
class E1RepetitionPilotQuantitativeFinalPreflight:
    preflight_id: str
    ec29_contract_digest: str
    ec37_contract_digest: str
    ec41_preflight_digest: str
    ec42_integration_digest: str
    resource_snapshot_digest: str
    checks: tuple[tuple[str, bool], ...]
    decision: str
    reason: str
    technical_execution_ready: bool
    owner_execution_authorized: bool
    pilot_execution_permitted: bool
    persistence_permitted: bool
    result_decision_permitted: bool
    memory_claim_permitted: bool
    preflight_digest: str

    def __post_init__(self) -> None:
        checks = dict(self.checks)
        technical_names = S1_EC43_REQUIRED_CHECKS[:-1]
        ready = all(checks[name] for name in technical_names)
        expected = "TECHNISCH_BEREIT_NEUE_FREIGABE_FEHLT" if ready else "KORREKTUR"
        if (
            self.preflight_id != S1_EC43_PREFLIGHT_ID
            or self.ec29_contract_digest != S1_EC43_EC29_CONTRACT_DIGEST
            or self.ec37_contract_digest != S1_EC43_EC37_CONTRACT_DIGEST
            or self.ec41_preflight_digest != S1_EC43_EC41_PREFLIGHT_DIGEST
            or self.ec42_integration_digest != S1_EC43_EC42_INTEGRATION_DIGEST
            or len(self.resource_snapshot_digest) != 64
            or tuple(name for name, _ in self.checks) != S1_EC43_REQUIRED_CHECKS
            or self.decision != expected
            or not self.reason
            or self.technical_execution_ready is not ready
            or any(
                value is not False
                for value in (
                    self.owner_execution_authorized,
                    self.pilot_execution_permitted,
                    self.persistence_permitted,
                    self.result_decision_permitted,
                    self.memory_claim_permitted,
                )
            )
        ):
            raise E1RepetitionPilotQuantitativeFinalPreflightError(
                "S1-EC43 preflight changed or released execution"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "preflight_digest"
        }
        if self.preflight_digest != _digest(payload):
            raise E1RepetitionPilotQuantitativeFinalPreflightError(
                "S1-EC43 preflight digest changed"
            )


def audit_e1_repetition_pilot_quantitative_final_preflight(
    pilot_contract: E1RepetitionPilotReleaseContract,
    integration_contract: E1RepetitionPilotQuantitativeP0IntegrationContract,
    previous_preflight: E1RepetitionPilotQuantitativePostHandoffPreflight,
    full_runner_fixture: E1RepetitionPilotQuantitativeFullRunnerFixtureResult,
    resources: E1PilotRealResourceSnapshot,
) -> E1RepetitionPilotQuantitativeFinalPreflight:
    """Check final technical gates without accepting an authorization."""

    for value, expected, role in (
        (pilot_contract, E1RepetitionPilotReleaseContract, "EC29 contract"),
        (
            integration_contract,
            E1RepetitionPilotQuantitativeP0IntegrationContract,
            "EC37 contract",
        ),
        (
            previous_preflight,
            E1RepetitionPilotQuantitativePostHandoffPreflight,
            "EC41 preflight",
        ),
        (
            full_runner_fixture,
            E1RepetitionPilotQuantitativeFullRunnerFixtureResult,
            "EC42 fixture",
        ),
        (resources, E1PilotRealResourceSnapshot, "resource snapshot"),
    ):
        if not isinstance(value, expected):
            raise E1RepetitionPilotQuantitativeFinalPreflightError(
                f"S1-EC43 requires one {role}"
            )
        value.__post_init__()
    checks = (
        ("ec29-matrix-exactly-25368-steps", (
            pilot_contract.contract_digest == S1_EC43_EC29_CONTRACT_DIGEST
            and pilot_contract.field_arm_step_count == 25_368
        )),
        ("ec37-twelve-snapshot-contract-exact", (
            integration_contract.contract_digest == S1_EC43_EC37_CONTRACT_DIGEST
            and integration_contract.total_p0_snapshot_count == 12
        )),
        ("ec41-small-real-handoff-confirmed", (
            previous_preflight.preflight_digest == S1_EC43_EC41_PREFLIGHT_DIGEST
            and previous_preflight.small_real_handoff_confirmed is True
            and previous_preflight.pilot_execution_permitted is False
        )),
        ("ec42-full-runner-integration-exact", (
            full_runner_fixture.result_digest == S1_EC43_EC42_INTEGRATION_DIGEST
            and full_runner_fixture.full_runner_integrated is True
        )),
        ("ec42-zero-real-field-steps", (
            full_runner_fixture.executed_field_step_count == 0
            and full_runner_fixture.pilot_execution_performed is False
        )),
        ("twelve-immediate-p0-handoffs", (
            full_runner_fixture.p0_snapshot_handoff_count == 12
            and full_runner_fixture.handoff_immediately_after_p0_roles is True
        )),
        ("six-pairs-and-two-profiles", (
            full_runner_fixture.p0_pair_count == 6
            and full_runner_fixture.p0_profile_count == 2
            and full_runner_fixture.profiles_after_complete_trios is True
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
        ("in-memory-no-persistence-decision-or-claim", (
            pilot_contract.persistence_permitted is False
            and integration_contract.persistence_permitted is False
            and full_runner_fixture.persistence_performed is False
            and full_runner_fixture.result_decision_permitted is False
            and full_runner_fixture.memory_claim_permitted is False
        )),
        ("new-owner-execution-authorization-not-present", False),
    )
    technical_names = S1_EC43_REQUIRED_CHECKS[:-1]
    values = dict(checks)
    ready = all(values[name] for name in technical_names)
    failed = tuple(name for name in technical_names if not values[name])
    decision = "TECHNISCH_BEREIT_NEUE_FREIGABE_FEHLT" if ready else "KORREKTUR"
    reason = (
        "all-technical-gates-ready-new-owner-authorization-required"
        if ready
        else "failed-technical-gates:" + ",".join(failed)
    )
    payload = {
        "preflight_id": S1_EC43_PREFLIGHT_ID,
        "ec29_contract_digest": pilot_contract.contract_digest,
        "ec37_contract_digest": integration_contract.contract_digest,
        "ec41_preflight_digest": previous_preflight.preflight_digest,
        "ec42_integration_digest": full_runner_fixture.result_digest,
        "resource_snapshot_digest": resources.digest(),
        "checks": checks,
        "decision": decision,
        "reason": reason,
        "technical_execution_ready": ready,
        "owner_execution_authorized": False,
        "pilot_execution_permitted": False,
        "persistence_permitted": False,
        "result_decision_permitted": False,
        "memory_claim_permitted": False,
    }
    return E1RepetitionPilotQuantitativeFinalPreflight(
        **payload,
        preflight_digest=_digest(payload),
    )

