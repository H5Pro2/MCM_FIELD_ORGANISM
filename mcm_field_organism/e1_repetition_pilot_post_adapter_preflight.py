"""S1-EC33 static post-adapter preflight for the locked n1/n2 pilot."""

from __future__ import annotations

from dataclasses import dataclass

from .e1_refined_formation_runner import _digest
from .e1_repetition_pilot_real_adapter_fixture import (
    E1RepetitionPilotRealAdapterFixtureResult,
)
from .e1_repetition_pilot_real_preflight import (
    E1PilotRealResourceSnapshot,
    E1RepetitionPilotRealPreflight,
)
from .e1_repetition_pilot_release_contract import (
    E1RepetitionPilotReleaseContract,
    S1_EC29_MIN_FREE_DISK_BYTES,
    S1_EC29_MIN_FREE_MEMORY_BYTES,
)


class E1RepetitionPilotPostAdapterPreflightError(ValueError):
    """Raised when S1-EC33 changes or bypasses the pilot release boundary."""


S1_EC33_PREFLIGHT_ID = "e1.repetition-pilot-post-adapter-preflight.s1ec33.v1"
S1_EC33_EC29_CONTRACT_DIGEST = (
    "834b2280cd55d099fe81fd3c0ba506cb6924abea94d27495e42b4480e8d7aff8"
)
S1_EC33_EC31_PREFLIGHT_DIGEST = (
    "3be17db1add68da25efb73210c9e7ab88ae34614bbcac5e19df6f30c3abb7f3c"
)
S1_EC33_EC32_ADAPTER_DIGEST = (
    "04ae04944fcace37a60b0f39417b233991886bf24dfe24819e8b47aeab1e2d12"
)
S1_EC33_REQUIRED_CHECKS = (
    "ec29-contract-exact",
    "ec31-preflight-exact-and-locked",
    "ec32-six-role-adapter-exact",
    "ec32-only-small-fixture-executed",
    "free-memory-at-least-four-gib",
    "free-disk-at-least-one-gib",
    "runtime-cap-nine-hundred-seconds",
    "in-memory-only-no-persistence",
    "no-result-decision-or-claim",
    "explicit-owner-execution-authorization-missing",
)


@dataclass(frozen=True, slots=True)
class E1RepetitionPilotPostAdapterPreflight:
    preflight_id: str
    ec29_contract_digest: str
    ec31_preflight_digest: str
    ec32_adapter_digest: str
    resource_snapshot_digest: str
    checks: tuple[tuple[str, bool], ...]
    decision: str
    reason: str
    technical_release_ready: bool
    adapter_implemented: bool
    owner_execution_authorized: bool
    pilot_execution_permitted: bool
    persistence_permitted: bool
    result_decision_permitted: bool
    claims_permitted: bool
    preflight_digest: str

    def __post_init__(self) -> None:
        checks = dict(self.checks)
        technical_names = S1_EC33_REQUIRED_CHECKS[:-1]
        ready = all(checks[name] for name in technical_names)
        expected_decision = (
            "ADAPTER_BESTAETIGT_FREIGABE_FEHLT" if ready else "KORREKTUR"
        )
        if (
            self.preflight_id != S1_EC33_PREFLIGHT_ID
            or self.ec29_contract_digest != S1_EC33_EC29_CONTRACT_DIGEST
            or self.ec31_preflight_digest != S1_EC33_EC31_PREFLIGHT_DIGEST
            or self.ec32_adapter_digest != S1_EC33_EC32_ADAPTER_DIGEST
            or len(self.resource_snapshot_digest) != 64
            or tuple(name for name, _ in self.checks) != S1_EC33_REQUIRED_CHECKS
            or self.decision != expected_decision
            or not self.reason
            or self.technical_release_ready is not ready
            or self.adapter_implemented is not True
            or any(
                value is not False
                for value in (
                    self.owner_execution_authorized,
                    self.pilot_execution_permitted,
                    self.persistence_permitted,
                    self.result_decision_permitted,
                    self.claims_permitted,
                )
            )
        ):
            raise E1RepetitionPilotPostAdapterPreflightError(
                "S1-EC33 preflight changed or released execution"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "preflight_digest"
        }
        if self.preflight_digest != _digest(payload):
            raise E1RepetitionPilotPostAdapterPreflightError(
                "S1-EC33 preflight digest changed"
            )


def audit_e1_repetition_pilot_post_adapter_preflight(
    contract: E1RepetitionPilotReleaseContract,
    previous_preflight: E1RepetitionPilotRealPreflight,
    adapter_fixture: E1RepetitionPilotRealAdapterFixtureResult,
    resources: E1PilotRealResourceSnapshot,
) -> E1RepetitionPilotPostAdapterPreflight:
    """Recheck technical gates without accepting or executing authorization."""

    for value, expected, role in (
        (contract, E1RepetitionPilotReleaseContract, "EC29 contract"),
        (previous_preflight, E1RepetitionPilotRealPreflight, "EC31 preflight"),
        (
            adapter_fixture,
            E1RepetitionPilotRealAdapterFixtureResult,
            "EC32 adapter fixture",
        ),
        (resources, E1PilotRealResourceSnapshot, "resource snapshot"),
    ):
        if not isinstance(value, expected):
            raise E1RepetitionPilotPostAdapterPreflightError(
                f"S1-EC33 requires one {role}"
            )
        value.__post_init__()
    checks = (
        ("ec29-contract-exact", (
            contract.contract_digest == S1_EC33_EC29_CONTRACT_DIGEST
        )),
        ("ec31-preflight-exact-and-locked", (
            previous_preflight.preflight_digest == S1_EC33_EC31_PREFLIGHT_DIGEST
            and previous_preflight.pilot_execution_permitted is False
        )),
        ("ec32-six-role-adapter-exact", (
            adapter_fixture.result_digest == S1_EC33_EC32_ADAPTER_DIGEST
            and adapter_fixture.six_role_adapter_implemented is True
            and adapter_fixture.role_order == contract.arms
        )),
        ("ec32-only-small-fixture-executed", (
            adapter_fixture.total_field_steps_executed == 48
            and adapter_fixture.full_pilot_executed is False
        )),
        ("free-memory-at-least-four-gib", (
            resources.free_memory_bytes >= S1_EC29_MIN_FREE_MEMORY_BYTES
        )),
        ("free-disk-at-least-one-gib", (
            resources.free_disk_bytes >= S1_EC29_MIN_FREE_DISK_BYTES
        )),
        ("runtime-cap-nine-hundred-seconds", (
            contract.maximum_runtime_seconds == 900.0
        )),
        ("in-memory-only-no-persistence", (
            contract.persistence_permitted is False
            and adapter_fixture.persistence_performed is False
        )),
        ("no-result-decision-or-claim", (
            contract.result_decision_permitted is False
            and contract.imprinting_claim_permitted is False
            and contract.memory_claim_permitted is False
            and contract.ai_claim_permitted is False
            and adapter_fixture.result_decision_permitted is False
            and adapter_fixture.claims_permitted is False
        )),
        ("explicit-owner-execution-authorization-missing", False),
    )
    technical_names = S1_EC33_REQUIRED_CHECKS[:-1]
    values = dict(checks)
    ready = all(values[name] for name in technical_names)
    failed = tuple(name for name in technical_names if not values[name])
    decision = "ADAPTER_BESTAETIGT_FREIGABE_FEHLT" if ready else "KORREKTUR"
    reason = (
        "technical-release-ready-explicit-owner-authorization-required"
        if ready
        else "failed-technical-gates:" + ",".join(failed)
    )
    payload = {
        "preflight_id": S1_EC33_PREFLIGHT_ID,
        "ec29_contract_digest": contract.contract_digest,
        "ec31_preflight_digest": previous_preflight.preflight_digest,
        "ec32_adapter_digest": adapter_fixture.result_digest,
        "resource_snapshot_digest": resources.digest(),
        "checks": checks,
        "decision": decision,
        "reason": reason,
        "technical_release_ready": ready,
        "adapter_implemented": True,
        "owner_execution_authorized": False,
        "pilot_execution_permitted": False,
        "persistence_permitted": False,
        "result_decision_permitted": False,
        "claims_permitted": False,
    }
    return E1RepetitionPilotPostAdapterPreflight(
        **payload,
        preflight_digest=_digest(payload),
    )

