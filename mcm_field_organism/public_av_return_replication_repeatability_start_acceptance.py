from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_executor_binding import (
    PublicAVReturnReplicationRepeatabilityExecutorBindingContract,
)
from .public_av_return_replication_repeatability_preflight import (
    PublicAVReturnReplicationRepeatabilityPreflight,
)
from .public_av_return_replication_repeatability_slot_start import (
    PublicAVReturnReplicationRepeatabilitySlotStartContract,
)


START_ACCEPTANCE_ID = (
    "public.av.nasa-earthrise.return-replication.repeatability-start-acceptance.v1"
)


class PublicAVReturnReplicationRepeatabilityStartAcceptanceError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatSlotStartAcceptance:
    repeat_index: int
    acceptance_id: str
    slot_binding_id: str
    executor_binding_id: str
    future_one_shot_entrypoint_id: str
    future_executor_id: str
    base_preflight_id: str
    base_runner_id: str
    permutation_contract_id: str
    permutation_contract_digest: str
    source_id: str
    slot_start_identity_matches: bool
    executor_binding_identity_matches: bool
    preflight_identity_matches: bool
    runner_identity_matches: bool
    permutation_identity_matches: bool
    one_shot_release_available: bool
    one_shot_release_unconsumed: bool
    fresh_one_shot_gate_required: bool
    gate_instance_created: bool = False
    executor_callable_created: bool = False
    executor_bound: bool = False
    start_release_granted: bool = False
    repeat_run_started: bool = False
    reusable: bool = False

    def __post_init__(self) -> None:
        if self.repeat_index not in (1, 2, 3):
            raise PublicAVReturnReplicationRepeatabilityStartAcceptanceError(
                "repeat_index must be one of 1, 2, 3"
            )
        if not self.acceptance_id.endswith(f".repeat-{self.repeat_index}.v1"):
            raise PublicAVReturnReplicationRepeatabilityStartAcceptanceError(
                "slot acceptance identity does not match repeat_index"
            )
        required = (
            self.slot_start_identity_matches,
            self.executor_binding_identity_matches,
            self.preflight_identity_matches,
            self.runner_identity_matches,
            self.permutation_identity_matches,
            self.one_shot_release_available,
            self.one_shot_release_unconsumed,
            self.fresh_one_shot_gate_required,
        )
        if not all(required):
            raise PublicAVReturnReplicationRepeatabilityStartAcceptanceError(
                "slot start acceptance requires a complete consistent identity chain"
            )
        forbidden = (
            self.gate_instance_created,
            self.executor_callable_created,
            self.executor_bound,
            self.start_release_granted,
            self.repeat_run_started,
            self.reusable,
        )
        if any(forbidden):
            raise PublicAVReturnReplicationRepeatabilityStartAcceptanceError(
                "slot start acceptance must remain non-executable and unconsumed"
            )


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilityStartAcceptance:
    acceptance_id: str
    repeatability_preflight_id: str
    repeatability_runner_id: str
    slot_start_contract_id: str
    executor_binding_contract_id: str
    source_id: str
    slot_acceptances: tuple[PublicAVReturnReplicationRepeatSlotStartAcceptance, ...]
    all_three_slots_consistent: bool
    all_three_one_shot_releases_unconsumed: bool
    all_future_gate_ids_unique: bool
    all_future_executor_ids_unique: bool
    start_acceptance_complete: bool
    gate_instances_created: bool = False
    executor_callables_created: bool = False
    executor_binding_allowed: bool = False
    start_release_granted: bool = False
    repeatability_run_allowed: bool = False
    automatic_repeat_loop_available: bool = False
    stability_threshold_defined: bool = False
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        if self.acceptance_id != START_ACCEPTANCE_ID:
            raise PublicAVReturnReplicationRepeatabilityStartAcceptanceError(
                "unexpected repeatability start acceptance identity"
            )
        if tuple(item.repeat_index for item in self.slot_acceptances) != (1, 2, 3):
            raise PublicAVReturnReplicationRepeatabilityStartAcceptanceError(
                "start acceptance must contain exactly the ordered slots 1, 2, 3"
            )
        required = (
            self.all_three_slots_consistent,
            self.all_three_one_shot_releases_unconsumed,
            self.all_future_gate_ids_unique,
            self.all_future_executor_ids_unique,
            self.start_acceptance_complete,
        )
        if not all(required):
            raise PublicAVReturnReplicationRepeatabilityStartAcceptanceError(
                "repeatability start acceptance is incomplete"
            )
        forbidden = (
            self.gate_instances_created,
            self.executor_callables_created,
            self.executor_binding_allowed,
            self.start_release_granted,
            self.repeatability_run_allowed,
            self.automatic_repeat_loop_available,
            self.stability_threshold_defined,
            self.memory_claim_allowed,
            self.meaning_claim_allowed,
            self.organization_claim_allowed,
            self.ai_claim_allowed,
        )
        if any(forbidden):
            raise PublicAVReturnReplicationRepeatabilityStartAcceptanceError(
                "repeatability start acceptance must remain run- and claim-locked"
            )


def build_public_av_return_replication_repeatability_start_acceptance(
    *,
    preflight: PublicAVReturnReplicationRepeatabilityPreflight,
    slot_start_contract: PublicAVReturnReplicationRepeatabilitySlotStartContract,
    executor_binding_contract: PublicAVReturnReplicationRepeatabilityExecutorBindingContract,
) -> PublicAVReturnReplicationRepeatabilityStartAcceptance:
    if not isinstance(preflight, PublicAVReturnReplicationRepeatabilityPreflight):
        raise PublicAVReturnReplicationRepeatabilityStartAcceptanceError(
            "preflight has the wrong contract type"
        )
    if not isinstance(
        slot_start_contract, PublicAVReturnReplicationRepeatabilitySlotStartContract
    ):
        raise PublicAVReturnReplicationRepeatabilityStartAcceptanceError(
            "slot_start_contract has the wrong contract type"
        )
    if not isinstance(
        executor_binding_contract,
        PublicAVReturnReplicationRepeatabilityExecutorBindingContract,
    ):
        raise PublicAVReturnReplicationRepeatabilityStartAcceptanceError(
            "executor_binding_contract has the wrong contract type"
        )

    if preflight.preflight_id != slot_start_contract.repeatability_preflight_id:
        raise PublicAVReturnReplicationRepeatabilityStartAcceptanceError(
            "slot start contract is not bound to the supplied preflight"
        )
    if (
        slot_start_contract.contract_id
        != executor_binding_contract.slot_start_contract_id
    ):
        raise PublicAVReturnReplicationRepeatabilityStartAcceptanceError(
            "executor bindings are not bound to the supplied slot start contract"
        )
    if len({preflight.source_id, slot_start_contract.source_id, executor_binding_contract.source_id}) != 1:
        raise PublicAVReturnReplicationRepeatabilityStartAcceptanceError(
            "source identity differs across repeatability contracts"
        )
    if preflight.repeatability_run_allowed or slot_start_contract.repeatability_run_allowed:
        raise PublicAVReturnReplicationRepeatabilityStartAcceptanceError(
            "an input contract unexpectedly permits a repeatability start"
        )
    if executor_binding_contract.executor_callables_created:
        raise PublicAVReturnReplicationRepeatabilityStartAcceptanceError(
            "executor callables must not exist during start acceptance"
        )

    accepted_slots = []
    for preflight_slot, start_slot, executor_slot in zip(
        preflight.repeat_slot_preflights,
        slot_start_contract.slot_bindings,
        executor_binding_contract.slot_executor_bindings,
        strict=True,
    ):
        index = preflight_slot.repeat_index
        identity_checks = {
            "repeat_index": index == start_slot.repeat_index == executor_slot.repeat_index,
            "slot_binding": executor_slot.slot_binding_id == start_slot.binding_id,
            "entrypoint": (
                executor_slot.one_shot_entrypoint_id
                == start_slot.one_shot_entrypoint_id
            ),
            "preflight": (
                start_slot.base_preflight_id
                == executor_slot.base_preflight_id
                == preflight_slot.base_preflight_id
            ),
            "runner": (
                start_slot.base_runner_id
                == executor_slot.base_runner_id
                == preflight_slot.slot_runner_id
            ),
            "source": (
                start_slot.source_id
                == executor_slot.source_id
                == preflight.source_id
            ),
        }
        if not all(identity_checks.values()):
            failed = ", ".join(name for name, ok in identity_checks.items() if not ok)
            raise PublicAVReturnReplicationRepeatabilityStartAcceptanceError(
                f"slot {index} identity chain mismatch: {failed}"
            )
        if not (
            preflight_slot.positive_one_shot_release_available
            and preflight_slot.one_shot_release_unconsumed
            and start_slot.positive_preflight_bound
            and start_slot.one_shot_release_unconsumed
        ):
            raise PublicAVReturnReplicationRepeatabilityStartAcceptanceError(
                f"slot {index} does not have an unconsumed one-shot release"
            )
        accepted_slots.append(
            PublicAVReturnReplicationRepeatSlotStartAcceptance(
                repeat_index=index,
                acceptance_id=f"{START_ACCEPTANCE_ID}.repeat-{index}.v1",
                slot_binding_id=start_slot.binding_id,
                executor_binding_id=executor_slot.executor_binding_id,
                future_one_shot_entrypoint_id=start_slot.one_shot_entrypoint_id,
                future_executor_id=executor_slot.future_executor_id,
                base_preflight_id=preflight_slot.base_preflight_id,
                base_runner_id=preflight_slot.slot_runner_id,
                permutation_contract_id=executor_slot.permutation_contract_id,
                permutation_contract_digest=executor_slot.permutation_contract_digest,
                source_id=preflight.source_id,
                slot_start_identity_matches=True,
                executor_binding_identity_matches=True,
                preflight_identity_matches=True,
                runner_identity_matches=True,
                permutation_identity_matches=True,
                one_shot_release_available=True,
                one_shot_release_unconsumed=True,
                fresh_one_shot_gate_required=True,
            )
        )

    gate_ids = tuple(item.future_one_shot_entrypoint_id for item in accepted_slots)
    executor_ids = tuple(item.future_executor_id for item in accepted_slots)
    return PublicAVReturnReplicationRepeatabilityStartAcceptance(
        acceptance_id=START_ACCEPTANCE_ID,
        repeatability_preflight_id=preflight.preflight_id,
        repeatability_runner_id=preflight.repeatability_runner_id,
        slot_start_contract_id=slot_start_contract.contract_id,
        executor_binding_contract_id=executor_binding_contract.contract_id,
        source_id=preflight.source_id,
        slot_acceptances=tuple(accepted_slots),
        all_three_slots_consistent=True,
        all_three_one_shot_releases_unconsumed=True,
        all_future_gate_ids_unique=len(set(gate_ids)) == 3,
        all_future_executor_ids_unique=len(set(executor_ids)) == 3,
        start_acceptance_complete=True,
    )


def start_public_av_return_replication_repeatability_from_acceptance(
    acceptance: PublicAVReturnReplicationRepeatabilityStartAcceptance,
) -> None:
    del acceptance
    raise PublicAVReturnReplicationRepeatabilityStartAcceptanceError(
        "start release is not granted by the locked repeatability start acceptance"
    )


def public_av_return_replication_repeatability_start_acceptance_to_jsonable(
    acceptance: PublicAVReturnReplicationRepeatabilityStartAcceptance,
) -> dict[str, Any]:
    return asdict(acceptance)
