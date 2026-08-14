"""S1-EC30 synthetic orchestration fixture for the locked n1/n2 pilot."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .e1_refined_formation_runner import _digest
from .e1_repetition_pilot_release_contract import (
    E1RepetitionPilotBatch,
    E1RepetitionPilotReleaseContract,
    S1_EC29_ARMS,
    S1_EC29_CONTRACT_ID,
)


class E1RepetitionPilotRunnerFixtureError(ValueError):
    """Raised when the S1-EC30 synthetic runner boundary is violated."""


S1_EC30_RUNNER_ID = "e1.repetition-pilot-runner-fixture.s1ec30.v1"
S1_EC30_RECEIPT_KIND = "synthetic-no-field-arm-receipt"


@dataclass(frozen=True, slots=True)
class E1PilotSyntheticArmReceipt:
    receipt_kind: str
    batch_index: int
    contact_count: int
    refinement_id: str
    arm_id: str
    expected_step_count: int
    field_steps_executed: int
    p0_role: bool
    formation_ablation_role: bool
    active_e1_role: bool
    control_passed: bool
    receipt_digest: str

    def __post_init__(self) -> None:
        roles = (
            self.arm_id.startswith("p0_"),
            "formation_ablated" in self.arm_id,
            self.arm_id.endswith("_active"),
        )
        if (
            self.receipt_kind != S1_EC30_RECEIPT_KIND
            or self.batch_index < 0
            or self.contact_count not in (1, 2)
            or self.refinement_id not in ("r2", "r4", "r8")
            or self.arm_id not in S1_EC29_ARMS
            or self.expected_step_count < 1
            or self.field_steps_executed != 0
            or roles.count(True) != 1
            or self.p0_role is not roles[0]
            or self.formation_ablation_role is not roles[1]
            or self.active_e1_role is not roles[2]
            or self.control_passed is not True
        ):
            raise E1RepetitionPilotRunnerFixtureError(
                "S1-EC30 synthetic arm receipt changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "receipt_digest"
        }
        if self.receipt_digest != _digest(payload):
            raise E1RepetitionPilotRunnerFixtureError(
                "S1-EC30 arm receipt digest changed"
            )


SyntheticArmKernel = Callable[
    [E1RepetitionPilotBatch, str],
    E1PilotSyntheticArmReceipt,
]


def build_synthetic_pilot_arm_receipt(
    batch: E1RepetitionPilotBatch,
    arm_id: str,
) -> E1PilotSyntheticArmReceipt:
    """Return one typed no-field receipt for runner lifecycle testing."""

    if not isinstance(batch, E1RepetitionPilotBatch) or arm_id not in batch.arm_order:
        raise E1RepetitionPilotRunnerFixtureError(
            "S1-EC30 fixture receipt input changed"
        )
    payload = {
        "receipt_kind": S1_EC30_RECEIPT_KIND,
        "batch_index": batch.batch_index,
        "contact_count": batch.contact_count,
        "refinement_id": batch.refinement_id,
        "arm_id": arm_id,
        "expected_step_count": batch.step_count_per_arm,
        "field_steps_executed": 0,
        "p0_role": arm_id.startswith("p0_"),
        "formation_ablation_role": "formation_ablated" in arm_id,
        "active_e1_role": arm_id.endswith("_active"),
        "control_passed": True,
    }
    return E1PilotSyntheticArmReceipt(
        **payload,
        receipt_digest=_digest(payload),
    )


@dataclass(frozen=True, slots=True)
class E1RepetitionPilotSyntheticRawResult:
    runner_id: str
    contract_digest: str
    receipt_digests: tuple[tuple[int, str, str], ...]
    batch_completion_order: tuple[int, ...]
    arm_call_count: int
    planned_field_arm_step_count: int
    executed_field_step_count: int
    p0_receipt_count: int
    formation_ablation_receipt_count: int
    active_e1_receipt_count: int
    all_controls_passed: bool
    fail_fast_enabled: bool
    partial_result_permitted: bool
    pilot_execution_performed: bool
    persistence_performed: bool
    result_decision_permitted: bool
    claims_permitted: bool
    result_digest: str

    def __post_init__(self) -> None:
        expected_inventory = tuple(
            (batch_index, arm_id)
            for batch_index in range(6)
            for arm_id in S1_EC29_ARMS
        )
        if (
            self.runner_id != S1_EC30_RUNNER_ID
            or len(self.contract_digest) != 64
            or tuple(
                (batch_index, arm_id)
                for batch_index, arm_id, _ in self.receipt_digests
            )
            != expected_inventory
            or any(len(digest) != 64 for _, _, digest in self.receipt_digests)
            or self.batch_completion_order != tuple(range(6))
            or self.arm_call_count != 36
            or self.planned_field_arm_step_count != 25_368
            or self.executed_field_step_count != 0
            or self.p0_receipt_count != 12
            or self.formation_ablation_receipt_count != 12
            or self.active_e1_receipt_count != 12
            or self.all_controls_passed is not True
            or self.fail_fast_enabled is not True
            or any(
                value is not False
                for value in (
                    self.partial_result_permitted,
                    self.pilot_execution_performed,
                    self.persistence_performed,
                    self.result_decision_permitted,
                    self.claims_permitted,
                )
            )
        ):
            raise E1RepetitionPilotRunnerFixtureError(
                "S1-EC30 synthetic raw result changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "result_digest"
        }
        if self.result_digest != _digest(payload):
            raise E1RepetitionPilotRunnerFixtureError(
                "S1-EC30 raw result digest changed"
            )


def run_repetition_pilot_runner_fixture(
    contract: E1RepetitionPilotReleaseContract,
    kernel: SyntheticArmKernel = build_synthetic_pilot_arm_receipt,
) -> E1RepetitionPilotSyntheticRawResult:
    """Exercise pilot orchestration with typed receipts and zero field steps."""

    if not isinstance(contract, E1RepetitionPilotReleaseContract) or not callable(
        kernel
    ):
        raise E1RepetitionPilotRunnerFixtureError(
            "S1-EC30 requires one EC29 contract and synthetic kernel"
        )
    contract.__post_init__()
    if (
        contract.contract_id != S1_EC29_CONTRACT_ID
        or contract.runner_implementation_permitted is not True
        or contract.pilot_execution_permitted is not False
        or contract.persistence_permitted is not False
    ):
        raise E1RepetitionPilotRunnerFixtureError(
            "S1-EC30 cannot cross the EC29 execution boundary"
        )
    receipts = []
    completed_batches = []
    for batch in contract.batches:
        batch.__post_init__()
        for arm_id in batch.arm_order:
            receipt = kernel(batch, arm_id)
            if not isinstance(receipt, E1PilotSyntheticArmReceipt):
                raise E1RepetitionPilotRunnerFixtureError(
                    "S1-EC30 kernel returned no typed synthetic receipt"
                )
            receipt.__post_init__()
            if (
                receipt.batch_index != batch.batch_index
                or receipt.contact_count != batch.contact_count
                or receipt.refinement_id != batch.refinement_id
                or receipt.arm_id != arm_id
                or receipt.expected_step_count != batch.step_count_per_arm
            ):
                raise E1RepetitionPilotRunnerFixtureError(
                    "S1-EC30 receipt does not match the current batch role"
                )
            receipts.append(receipt)
        completed_batches.append(batch.batch_index)
    values = {
        "runner_id": S1_EC30_RUNNER_ID,
        "contract_digest": contract.contract_digest,
        "receipt_digests": tuple(
            (item.batch_index, item.arm_id, item.receipt_digest)
            for item in receipts
        ),
        "batch_completion_order": tuple(completed_batches),
        "arm_call_count": len(receipts),
        "planned_field_arm_step_count": contract.field_arm_step_count,
        "executed_field_step_count": sum(
            item.field_steps_executed for item in receipts
        ),
        "p0_receipt_count": sum(item.p0_role for item in receipts),
        "formation_ablation_receipt_count": sum(
            item.formation_ablation_role for item in receipts
        ),
        "active_e1_receipt_count": sum(item.active_e1_role for item in receipts),
        "all_controls_passed": all(item.control_passed for item in receipts),
        "fail_fast_enabled": True,
        "partial_result_permitted": False,
        "pilot_execution_performed": False,
        "persistence_performed": False,
        "result_decision_permitted": False,
        "claims_permitted": False,
    }
    return E1RepetitionPilotSyntheticRawResult(
        **values,
        result_digest=_digest(values),
    )
