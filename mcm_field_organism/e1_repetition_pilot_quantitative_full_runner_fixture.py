"""S1-EC42 full synthetic six-batch runner with quantitative P0 handoffs."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .e1_refined_formation_runner import _digest
from .e1_repetition_pilot_quantitative_p0_integration_contract import (
    E1QuantitativeP0BatchHandoff,
    E1RepetitionPilotQuantitativeP0IntegrationContract,
)
from .e1_repetition_pilot_quantitative_p0_runner_fixture import (
    SyntheticP0SnapshotKernel,
    build_synthetic_p0_snapshot_handoff,
)
from .e1_repetition_pilot_quantitative_p0_schema import (
    E1PilotQuantitativeP0Pair,
    build_quantitative_p0_refinement_profile,
    collect_quantitative_p0_pair,
)
from .e1_repetition_pilot_quantitative_post_handoff_preflight import (
    E1RepetitionPilotQuantitativePostHandoffPreflight,
)
from .e1_repetition_pilot_release_contract import (
    E1RepetitionPilotReleaseContract,
    S1_EC29_ARMS,
)
from .e1_repetition_pilot_runner_fixture import (
    E1PilotSyntheticArmReceipt,
    SyntheticArmKernel,
    build_synthetic_pilot_arm_receipt,
)
from .shared_mcm_field import SharedMCMFieldSnapshot


class E1RepetitionPilotQuantitativeFullRunnerFixtureError(ValueError):
    """Raised when S1-EC42 crosses its zero-field integration boundary."""


S1_EC42_RUNNER_ID = "e1.repetition-pilot-quantitative-full-runner.s1ec42.v1"
S1_EC42_EC29_CONTRACT_DIGEST = (
    "834b2280cd55d099fe81fd3c0ba506cb6924abea94d27495e42b4480e8d7aff8"
)
S1_EC42_EC37_CONTRACT_DIGEST = (
    "ad9200e960f6c0c68791a41cc2c8810af2d087a7ade4690593e226e1de37502e"
)
S1_EC42_EC41_PREFLIGHT_DIGEST = (
    "2015d17166fd6695db7f5cf6086611bd057d2ab0213d886d68275bda93a771b6"
)
S1_EC42_HANDOFF_AFTER_ROLE = "p0_continuous"


@dataclass(frozen=True, slots=True)
class E1RepetitionPilotQuantitativeFullRunnerFixtureResult:
    runner_id: str
    ec29_contract_digest: str
    ec37_contract_digest: str
    ec41_preflight_digest: str
    arm_receipt_digests: tuple[tuple[int, str, str], ...]
    p0_pair_digests: tuple[tuple[int, str], ...]
    p0_profile_digests: tuple[tuple[int, str], ...]
    batch_completion_order: tuple[int, ...]
    planned_field_arm_step_count: int
    executed_field_step_count: int
    arm_receipt_count: int
    p0_snapshot_handoff_count: int
    p0_pair_count: int
    p0_profile_count: int
    handoff_immediately_after_p0_roles: bool
    profiles_after_complete_trios: bool
    fail_fast_enabled: bool
    full_runner_integrated: bool
    pilot_execution_performed: bool
    authorization_consumed: bool
    persistence_performed: bool
    result_decision_permitted: bool
    memory_claim_permitted: bool
    result_digest: str

    def __post_init__(self) -> None:
        expected_arms = tuple(
            (batch_index, arm_id)
            for batch_index in range(6)
            for arm_id in S1_EC29_ARMS
        )
        if (
            self.runner_id != S1_EC42_RUNNER_ID
            or self.ec29_contract_digest != S1_EC42_EC29_CONTRACT_DIGEST
            or self.ec37_contract_digest != S1_EC42_EC37_CONTRACT_DIGEST
            or self.ec41_preflight_digest != S1_EC42_EC41_PREFLIGHT_DIGEST
            or tuple(
                (batch_index, arm_id)
                for batch_index, arm_id, _ in self.arm_receipt_digests
            )
            != expected_arms
            or tuple(index for index, _ in self.p0_pair_digests) != tuple(range(6))
            or tuple(count for count, _ in self.p0_profile_digests) != (1, 2)
            or self.batch_completion_order != tuple(range(6))
            or self.planned_field_arm_step_count != 25_368
            or self.executed_field_step_count != 0
            or self.arm_receipt_count != 36
            or self.p0_snapshot_handoff_count != 12
            or self.p0_pair_count != 6
            or self.p0_profile_count != 2
            or any(
                value is not True
                for value in (
                    self.handoff_immediately_after_p0_roles,
                    self.profiles_after_complete_trios,
                    self.fail_fast_enabled,
                    self.full_runner_integrated,
                )
            )
            or any(
                value is not False
                for value in (
                    self.pilot_execution_performed,
                    self.authorization_consumed,
                    self.persistence_performed,
                    self.result_decision_permitted,
                    self.memory_claim_permitted,
                )
            )
        ):
            raise E1RepetitionPilotQuantitativeFullRunnerFixtureError(
                "S1-EC42 result changed or crossed zero-field scope"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "result_digest"
        }
        if self.result_digest != _digest(payload):
            raise E1RepetitionPilotQuantitativeFullRunnerFixtureError(
                "S1-EC42 result digest changed"
            )


def run_quantitative_full_runner_fixture(
    pilot_contract: E1RepetitionPilotReleaseContract,
    integration_contract: E1RepetitionPilotQuantitativeP0IntegrationContract,
    preflight: E1RepetitionPilotQuantitativePostHandoffPreflight,
    snapshot_template: SharedMCMFieldSnapshot,
    *,
    arm_kernel: SyntheticArmKernel = build_synthetic_pilot_arm_receipt,
    snapshot_kernel: SyntheticP0SnapshotKernel = (
        build_synthetic_p0_snapshot_handoff
    ),
) -> E1RepetitionPilotQuantitativeFullRunnerFixtureResult:
    """Integrate all runner roles with receipts and zero real field steps."""

    for value, expected, role in (
        (pilot_contract, E1RepetitionPilotReleaseContract, "EC29 contract"),
        (
            integration_contract,
            E1RepetitionPilotQuantitativeP0IntegrationContract,
            "EC37 contract",
        ),
        (
            preflight,
            E1RepetitionPilotQuantitativePostHandoffPreflight,
            "EC41 preflight",
        ),
        (snapshot_template, SharedMCMFieldSnapshot, "snapshot template"),
    ):
        if not isinstance(value, expected):
            raise E1RepetitionPilotQuantitativeFullRunnerFixtureError(
                f"S1-EC42 requires one {role}"
            )
        value.__post_init__()
    if not callable(arm_kernel) or not callable(snapshot_kernel):
        raise E1RepetitionPilotQuantitativeFullRunnerFixtureError(
            "S1-EC42 requires two synthetic kernels"
        )
    if (
        pilot_contract.contract_digest != S1_EC42_EC29_CONTRACT_DIGEST
        or integration_contract.contract_digest != S1_EC42_EC37_CONTRACT_DIGEST
        or preflight.preflight_digest != S1_EC42_EC41_PREFLIGHT_DIGEST
        or preflight.full_runner_implementation_permitted is not True
        or preflight.pilot_execution_permitted is not False
    ):
        raise E1RepetitionPilotQuantitativeFullRunnerFixtureError(
            "S1-EC42 upstream binding changed"
        )
    receipts: list[E1PilotSyntheticArmReceipt] = []
    pairs: list[E1PilotQuantitativeP0Pair] = []
    completed = []
    handoff_positions = []
    for batch, handoff in zip(
        pilot_contract.batches,
        integration_contract.handoffs,
        strict=True,
    ):
        if (
            batch.batch_index != handoff.batch_index
            or batch.contact_count != handoff.contact_count
            or batch.refinement_id != handoff.refinement_id
        ):
            raise E1RepetitionPilotQuantitativeFullRunnerFixtureError(
                "S1-EC42 batch and P0 handoff are not aligned"
            )
        for arm_index, arm_id in enumerate(batch.arm_order):
            receipt = arm_kernel(batch, arm_id)
            if not isinstance(receipt, E1PilotSyntheticArmReceipt):
                raise E1RepetitionPilotQuantitativeFullRunnerFixtureError(
                    "S1-EC42 arm kernel returned no typed receipt"
                )
            receipt.__post_init__()
            if (
                receipt.batch_index != batch.batch_index
                or receipt.arm_id != arm_id
                or receipt.field_steps_executed != 0
            ):
                raise E1RepetitionPilotQuantitativeFullRunnerFixtureError(
                    "S1-EC42 arm receipt does not match current role"
                )
            receipts.append(receipt)
            if arm_id == S1_EC42_HANDOFF_AFTER_ROLE:
                snapshots = snapshot_kernel(handoff, snapshot_template)
                if (
                    not isinstance(snapshots, tuple)
                    or len(snapshots) != 2
                    or any(
                        not isinstance(item, SharedMCMFieldSnapshot)
                        for item in snapshots
                    )
                ):
                    raise E1RepetitionPilotQuantitativeFullRunnerFixtureError(
                        "S1-EC42 snapshot kernel returned no typed pair"
                    )
                pairs.append(collect_quantitative_p0_pair(
                    handoff.contact_count,
                    handoff.refinement_id,
                    snapshots[0],
                    snapshots[1],
                ))
                handoff_positions.append(arm_index)
        completed.append(batch.batch_index)
    profiles = tuple(
        build_quantitative_p0_refinement_profile(tuple(
            item for item in pairs if item.contact_count == contact_count
        ))
        for contact_count in (1, 2)
    )
    values = {
        "runner_id": S1_EC42_RUNNER_ID,
        "ec29_contract_digest": pilot_contract.contract_digest,
        "ec37_contract_digest": integration_contract.contract_digest,
        "ec41_preflight_digest": preflight.preflight_digest,
        "arm_receipt_digests": tuple(
            (item.batch_index, item.arm_id, item.receipt_digest)
            for item in receipts
        ),
        "p0_pair_digests": tuple(
            (index, item.pair_digest) for index, item in enumerate(pairs)
        ),
        "p0_profile_digests": tuple(
            (item.contact_count, item.profile_digest) for item in profiles
        ),
        "batch_completion_order": tuple(completed),
        "planned_field_arm_step_count": pilot_contract.field_arm_step_count,
        "executed_field_step_count": sum(
            item.field_steps_executed for item in receipts
        ),
        "arm_receipt_count": len(receipts),
        "p0_snapshot_handoff_count": len(pairs) * 2,
        "p0_pair_count": len(pairs),
        "p0_profile_count": len(profiles),
        "handoff_immediately_after_p0_roles": handoff_positions == [1] * 6,
        "profiles_after_complete_trios": len(pairs) == 6,
        "fail_fast_enabled": True,
        "full_runner_integrated": True,
        "pilot_execution_performed": False,
        "authorization_consumed": False,
        "persistence_performed": False,
        "result_decision_permitted": False,
        "memory_claim_permitted": False,
    }
    return E1RepetitionPilotQuantitativeFullRunnerFixtureResult(
        **values,
        result_digest=_digest(values),
    )

