"""S1-EC41 static post-handoff preflight for the quantitative P0 path."""

from __future__ import annotations

from dataclasses import dataclass

from .e1_refined_formation_runner import _digest
from .e1_repetition_pilot_quantitative_p0_integration_contract import (
    E1RepetitionPilotQuantitativeP0IntegrationContract,
)
from .e1_repetition_pilot_quantitative_real_handoff_fixture import (
    E1RepetitionPilotQuantitativeRealHandoffFixtureResult,
)
from .e1_repetition_pilot_quantitative_real_preflight import (
    E1RepetitionPilotQuantitativeRealPreflight,
)
from .e1_repetition_pilot_release_contract import E1RepetitionPilotReleaseContract


class E1RepetitionPilotQuantitativePostHandoffPreflightError(ValueError):
    """Raised when S1-EC41 releases or overstates the full runner path."""


S1_EC41_PREFLIGHT_ID = (
    "e1.repetition-pilot-quantitative-post-handoff-preflight.s1ec41.v1"
)
S1_EC41_EC29_CONTRACT_DIGEST = (
    "834b2280cd55d099fe81fd3c0ba506cb6924abea94d27495e42b4480e8d7aff8"
)
S1_EC41_EC37_CONTRACT_DIGEST = (
    "ad9200e960f6c0c68791a41cc2c8810af2d087a7ade4690593e226e1de37502e"
)
S1_EC41_EC39_PREFLIGHT_DIGEST = (
    "9a0d128b20e5fc39c9efb378c1180a92c5f58f4bc3e81b110f89bb5faa618313"
)
S1_EC41_EC40_FIXTURE_DIGEST = (
    "489bbebc403634d501daecea102b19860413e4b5b0c46dc7b743551888c8d26e"
)
S1_EC41_REQUIRED_CHECKS = (
    "ec29-matrix-exact",
    "ec37-twelve-snapshot-contract-exact",
    "ec39-preflight-exact-and-locked",
    "ec40-small-real-handoff-exact",
    "ec40-only-sixteen-field-steps",
    "ec40-no-authorization-or-persistence",
    "quantitative-components-retained",
    "no-result-decision-or-memory-claim",
    "full-six-batch-runner-not-yet-integrated",
    "new-owner-execution-authorization-not-present",
)


@dataclass(frozen=True, slots=True)
class E1RepetitionPilotQuantitativePostHandoffPreflight:
    preflight_id: str
    ec29_contract_digest: str
    ec37_contract_digest: str
    ec39_preflight_digest: str
    ec40_fixture_digest: str
    checks: tuple[tuple[str, bool], ...]
    decision: str
    reason: str
    small_real_handoff_confirmed: bool
    full_runner_implementation_permitted: bool
    full_runner_integrated: bool
    owner_execution_authorized: bool
    pilot_execution_permitted: bool
    persistence_permitted: bool
    result_decision_permitted: bool
    memory_claim_permitted: bool
    preflight_digest: str

    def __post_init__(self) -> None:
        checks = dict(self.checks)
        base_names = S1_EC41_REQUIRED_CHECKS[:8]
        ready = all(checks[name] for name in base_names)
        expected = (
            "SMALL_HANDOFF_CONFIRMED_FULL_RUNNER_MISSING"
            if ready
            else "KORREKTUR"
        )
        if (
            self.preflight_id != S1_EC41_PREFLIGHT_ID
            or self.ec29_contract_digest != S1_EC41_EC29_CONTRACT_DIGEST
            or self.ec37_contract_digest != S1_EC41_EC37_CONTRACT_DIGEST
            or self.ec39_preflight_digest != S1_EC41_EC39_PREFLIGHT_DIGEST
            or self.ec40_fixture_digest != S1_EC41_EC40_FIXTURE_DIGEST
            or tuple(name for name, _ in self.checks) != S1_EC41_REQUIRED_CHECKS
            or self.decision != expected
            or not self.reason
            or self.small_real_handoff_confirmed is not ready
            or self.full_runner_implementation_permitted is not ready
            or any(
                value is not False
                for value in (
                    self.full_runner_integrated,
                    self.owner_execution_authorized,
                    self.pilot_execution_permitted,
                    self.persistence_permitted,
                    self.result_decision_permitted,
                    self.memory_claim_permitted,
                )
            )
        ):
            raise E1RepetitionPilotQuantitativePostHandoffPreflightError(
                "S1-EC41 preflight changed or released execution"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "preflight_digest"
        }
        if self.preflight_digest != _digest(payload):
            raise E1RepetitionPilotQuantitativePostHandoffPreflightError(
                "S1-EC41 preflight digest changed"
            )


def audit_e1_repetition_pilot_quantitative_post_handoff_preflight(
    pilot_contract: E1RepetitionPilotReleaseContract,
    integration_contract: E1RepetitionPilotQuantitativeP0IntegrationContract,
    previous_preflight: E1RepetitionPilotQuantitativeRealPreflight,
    real_fixture: E1RepetitionPilotQuantitativeRealHandoffFixtureResult,
) -> E1RepetitionPilotQuantitativePostHandoffPreflight:
    """Confirm the small handoff while keeping full execution unavailable."""

    for value, expected, role in (
        (pilot_contract, E1RepetitionPilotReleaseContract, "EC29 contract"),
        (
            integration_contract,
            E1RepetitionPilotQuantitativeP0IntegrationContract,
            "EC37 contract",
        ),
        (
            previous_preflight,
            E1RepetitionPilotQuantitativeRealPreflight,
            "EC39 preflight",
        ),
        (
            real_fixture,
            E1RepetitionPilotQuantitativeRealHandoffFixtureResult,
            "EC40 fixture",
        ),
    ):
        if not isinstance(value, expected):
            raise E1RepetitionPilotQuantitativePostHandoffPreflightError(
                f"S1-EC41 requires one {role}"
            )
        value.__post_init__()
    pair = real_fixture.quantitative_pair
    checks = (
        ("ec29-matrix-exact", (
            pilot_contract.contract_digest == S1_EC41_EC29_CONTRACT_DIGEST
            and pilot_contract.field_arm_step_count == 25_368
        )),
        ("ec37-twelve-snapshot-contract-exact", (
            integration_contract.contract_digest == S1_EC41_EC37_CONTRACT_DIGEST
            and integration_contract.total_p0_snapshot_count == 12
        )),
        ("ec39-preflight-exact-and-locked", (
            previous_preflight.preflight_digest == S1_EC41_EC39_PREFLIGHT_DIGEST
            and previous_preflight.pilot_execution_permitted is False
        )),
        ("ec40-small-real-handoff-exact", (
            real_fixture.result_digest == S1_EC41_EC40_FIXTURE_DIGEST
            and real_fixture.real_quantitative_handoff_implemented is True
        )),
        ("ec40-only-sixteen-field-steps", (
            real_fixture.total_field_steps_executed == 16
            and real_fixture.full_pilot_executed is False
        )),
        ("ec40-no-authorization-or-persistence", (
            real_fixture.authorization_consumed is False
            and real_fixture.persistence_performed is False
        )),
        ("quantitative-components-retained", (
            len(pair.activation_contrast) == len(pair.neuron_ids)
            and len(pair.afterimage_contrast) == len(pair.neuron_ids)
            and pair.activation_linf >= 0.0
            and pair.afterimage_linf >= 0.0
        )),
        ("no-result-decision-or-memory-claim", (
            integration_contract.result_decision_permitted is False
            and integration_contract.memory_claim_permitted is False
            and real_fixture.result_decision_permitted is False
            and real_fixture.memory_claim_permitted is False
        )),
        ("full-six-batch-runner-not-yet-integrated", False),
        ("new-owner-execution-authorization-not-present", False),
    )
    base_names = S1_EC41_REQUIRED_CHECKS[:8]
    values = dict(checks)
    ready = all(values[name] for name in base_names)
    failed = tuple(name for name in base_names if not values[name])
    decision = (
        "SMALL_HANDOFF_CONFIRMED_FULL_RUNNER_MISSING"
        if ready
        else "KORREKTUR"
    )
    reason = (
        "small-real-handoff-confirmed-full-runner-and-new-authorization-required"
        if ready
        else "failed-base-gates:" + ",".join(failed)
    )
    payload = {
        "preflight_id": S1_EC41_PREFLIGHT_ID,
        "ec29_contract_digest": pilot_contract.contract_digest,
        "ec37_contract_digest": integration_contract.contract_digest,
        "ec39_preflight_digest": previous_preflight.preflight_digest,
        "ec40_fixture_digest": real_fixture.result_digest,
        "checks": checks,
        "decision": decision,
        "reason": reason,
        "small_real_handoff_confirmed": ready,
        "full_runner_implementation_permitted": ready,
        "full_runner_integrated": False,
        "owner_execution_authorized": False,
        "pilot_execution_permitted": False,
        "persistence_permitted": False,
        "result_decision_permitted": False,
        "memory_claim_permitted": False,
    }
    return E1RepetitionPilotQuantitativePostHandoffPreflight(
        **payload,
        preflight_digest=_digest(payload),
    )

