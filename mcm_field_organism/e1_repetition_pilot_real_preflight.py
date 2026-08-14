"""Static S1-EC31 real preflight for the locked n1/n2 pilot."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .e1_confirmation_prepared_real_formation_kernel import (
    run_prepared_real_formation_arm_in_memory,
)
from .e1_refined_formation_runner import _digest
from .e1_repetition_formation_planner import E1RepetitionFormationPlanSet
from .e1_repetition_pilot_release_contract import (
    E1RepetitionPilotReleaseContract,
    S1_EC29_MIN_FREE_DISK_BYTES,
    S1_EC29_MIN_FREE_MEMORY_BYTES,
)
from .e1_repetition_pilot_runner_fixture import (
    E1RepetitionPilotSyntheticRawResult,
)
from .neutral_asynchronous_field_runtime import run_neutral_asynchronous_field


class E1RepetitionPilotRealPreflightError(ValueError):
    """Raised when S1-EC31 changes the real-pilot safety boundary."""


S1_EC31_PREFLIGHT_ID = "e1.repetition-pilot-real-preflight.s1ec31.v1"
S1_EC31_EC29_CONTRACT_DIGEST = (
    "834b2280cd55d099fe81fd3c0ba506cb6924abea94d27495e42b4480e8d7aff8"
)
S1_EC31_EC30_RESULT_DIGEST = (
    "700b0296be5cc04ac5049a447d0c6feb9f6b6ec50eb19915fc235c0c2fd697c0"
)
S1_EC31_KERNEL_BINDINGS = (
    (
        "p0_repeated",
        "neutral_asynchronous_field_runtime.run_neutral_asynchronous_field",
        "no-e1-state-no-adapter",
    ),
    (
        "p0_continuous",
        "neutral_asynchronous_field_runtime.run_neutral_asynchronous_field",
        "no-e1-state-no-adapter",
    ),
    (
        "repeated_formation_ablated",
        "e1_confirmation_prepared_real_formation_kernel.run_prepared_real_formation_arm_in_memory",
        "neutral-e1-state-formation-disabled",
    ),
    (
        "continuous_formation_ablated",
        "e1_confirmation_prepared_real_formation_kernel.run_prepared_real_formation_arm_in_memory",
        "neutral-e1-state-formation-disabled",
    ),
    (
        "repeated_active",
        "e1_confirmation_prepared_real_formation_kernel.run_prepared_real_formation_arm_in_memory",
        "neutral-e1-state-formation-enabled",
    ),
    (
        "continuous_active",
        "e1_confirmation_prepared_real_formation_kernel.run_prepared_real_formation_arm_in_memory",
        "neutral-e1-state-formation-enabled",
    ),
)
S1_EC31_REQUIRED_CHECKS = (
    "ec29-contract-digest-exact",
    "corrected-ec27-plan-digest-exact",
    "ec30-zero-field-runner-fixture-exact",
    "neutral-p0-kernel-callable",
    "copied-input-e1-kernel-callable",
    "six-real-role-bindings-complete",
    "free-memory-at-least-four-gib",
    "free-disk-at-least-one-gib",
    "runtime-cap-nine-hundred-seconds",
    "in-memory-only-no-target-path",
    "real-role-adapter-not-yet-implemented",
    "owner-execution-authorization-not-yet-present",
    "no-result-decision-or-claim",
)


@dataclass(frozen=True, slots=True)
class E1PilotRealResourceSnapshot:
    free_memory_bytes: int
    free_disk_bytes: int

    def __post_init__(self) -> None:
        if (
            isinstance(self.free_memory_bytes, bool)
            or not isinstance(self.free_memory_bytes, int)
            or self.free_memory_bytes < 0
            or isinstance(self.free_disk_bytes, bool)
            or not isinstance(self.free_disk_bytes, int)
            or self.free_disk_bytes < 0
        ):
            raise E1RepetitionPilotRealPreflightError(
                "S1-EC31 resource snapshot is invalid"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


@dataclass(frozen=True, slots=True)
class E1RepetitionPilotRealPreflight:
    preflight_id: str
    ec29_contract_digest: str
    ec27_plan_set_digest: str
    ec30_result_digest: str
    resource_snapshot_digest: str
    kernel_bindings: tuple[tuple[str, str, str], ...]
    checks: tuple[tuple[str, bool], ...]
    decision: str
    reason: str
    adapter_implementation_permitted: bool
    real_role_adapter_implemented: bool
    owner_execution_authorized: bool
    pilot_execution_permitted: bool
    persistence_permitted: bool
    result_decision_permitted: bool
    claims_permitted: bool
    preflight_digest: str

    def __post_init__(self) -> None:
        checks = dict(self.checks)
        technical_names = S1_EC31_REQUIRED_CHECKS[:10] + (
            S1_EC31_REQUIRED_CHECKS[-1],
        )
        technical_ready = all(checks[name] for name in technical_names)
        expected_decision = (
            "VORBEREITET_NICHT_FREIGEGEBEN"
            if technical_ready
            else "KORREKTUR"
        )
        if (
            self.preflight_id != S1_EC31_PREFLIGHT_ID
            or self.ec29_contract_digest != S1_EC31_EC29_CONTRACT_DIGEST
            or len(self.ec27_plan_set_digest) != 64
            or self.ec30_result_digest != S1_EC31_EC30_RESULT_DIGEST
            or len(self.resource_snapshot_digest) != 64
            or self.kernel_bindings != S1_EC31_KERNEL_BINDINGS
            or tuple(name for name, _ in self.checks) != S1_EC31_REQUIRED_CHECKS
            or self.decision != expected_decision
            or not self.reason
            or self.adapter_implementation_permitted is not technical_ready
            or any(
                value is not False
                for value in (
                    self.real_role_adapter_implemented,
                    self.owner_execution_authorized,
                    self.pilot_execution_permitted,
                    self.persistence_permitted,
                    self.result_decision_permitted,
                    self.claims_permitted,
                )
            )
        ):
            raise E1RepetitionPilotRealPreflightError(
                "S1-EC31 preflight changed or released execution"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "preflight_digest"
        }
        if self.preflight_digest != _digest(payload):
            raise E1RepetitionPilotRealPreflightError(
                "S1-EC31 preflight digest changed"
            )


def audit_e1_repetition_pilot_real_preflight(
    contract: E1RepetitionPilotReleaseContract,
    plans: E1RepetitionFormationPlanSet,
    runner_fixture: E1RepetitionPilotSyntheticRawResult,
    resources: E1PilotRealResourceSnapshot,
) -> E1RepetitionPilotRealPreflight:
    """Audit real-run prerequisites without constructing an adapter or field."""

    for value, expected, role in (
        (contract, E1RepetitionPilotReleaseContract, "EC29 contract"),
        (plans, E1RepetitionFormationPlanSet, "EC27 plans"),
        (runner_fixture, E1RepetitionPilotSyntheticRawResult, "EC30 fixture"),
        (resources, E1PilotRealResourceSnapshot, "resource snapshot"),
    ):
        if not isinstance(value, expected):
            raise E1RepetitionPilotRealPreflightError(
                f"S1-EC31 requires one {role}"
            )
    contract.__post_init__()
    plans.__post_init__()
    runner_fixture.__post_init__()
    resources.__post_init__()
    role_inventory = tuple(role for role, _, _ in S1_EC31_KERNEL_BINDINGS)
    checks = (
        ("ec29-contract-digest-exact", (
            contract.contract_digest == S1_EC31_EC29_CONTRACT_DIGEST
        )),
        ("corrected-ec27-plan-digest-exact", (
            plans.plan_set_digest == contract.source_plan_set_digest
        )),
        ("ec30-zero-field-runner-fixture-exact", (
            runner_fixture.result_digest == S1_EC31_EC30_RESULT_DIGEST
            and runner_fixture.executed_field_step_count == 0
        )),
        ("neutral-p0-kernel-callable", (
            callable(run_neutral_asynchronous_field)
            and run_neutral_asynchronous_field.__name__
            == "run_neutral_asynchronous_field"
        )),
        ("copied-input-e1-kernel-callable", (
            callable(run_prepared_real_formation_arm_in_memory)
            and run_prepared_real_formation_arm_in_memory.__name__
            == "run_prepared_real_formation_arm_in_memory"
        )),
        ("six-real-role-bindings-complete", role_inventory == contract.arms),
        ("free-memory-at-least-four-gib", (
            resources.free_memory_bytes >= S1_EC29_MIN_FREE_MEMORY_BYTES
        )),
        ("free-disk-at-least-one-gib", (
            resources.free_disk_bytes >= S1_EC29_MIN_FREE_DISK_BYTES
        )),
        ("runtime-cap-nine-hundred-seconds", (
            contract.maximum_runtime_seconds == 900.0
        )),
        ("in-memory-only-no-target-path", (
            contract.persistence_permitted is False
        )),
        ("real-role-adapter-not-yet-implemented", False),
        ("owner-execution-authorization-not-yet-present", False),
        ("no-result-decision-or-claim", (
            contract.result_decision_permitted is False
            and contract.imprinting_claim_permitted is False
            and contract.memory_claim_permitted is False
            and contract.ai_claim_permitted is False
        )),
    )
    technical_names = S1_EC31_REQUIRED_CHECKS[:10] + (
        S1_EC31_REQUIRED_CHECKS[-1],
    )
    values = dict(checks)
    technical_ready = all(values[name] for name in technical_names)
    failed = tuple(name for name in technical_names if not values[name])
    decision = (
        "VORBEREITET_NICHT_FREIGEGEBEN"
        if technical_ready
        else "KORREKTUR"
    )
    reason = (
        "technical-preflight-ready-adapter-and-owner-authorization-still-required"
        if technical_ready
        else "failed-technical-gates:" + ",".join(failed)
    )
    payload = {
        "preflight_id": S1_EC31_PREFLIGHT_ID,
        "ec29_contract_digest": contract.contract_digest,
        "ec27_plan_set_digest": plans.plan_set_digest,
        "ec30_result_digest": runner_fixture.result_digest,
        "resource_snapshot_digest": resources.digest(),
        "kernel_bindings": S1_EC31_KERNEL_BINDINGS,
        "checks": checks,
        "decision": decision,
        "reason": reason,
        "adapter_implementation_permitted": technical_ready,
        "real_role_adapter_implemented": False,
        "owner_execution_authorized": False,
        "pilot_execution_permitted": False,
        "persistence_permitted": False,
        "result_decision_permitted": False,
        "claims_permitted": False,
    }
    return E1RepetitionPilotRealPreflight(
        **payload,
        preflight_digest=_digest(payload),
    )
