"""Locked two-step factory execution order for one repeatability slot."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .public_av_return_replication_repeatability_single_slot_factory_order_execution_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionAcceptance,
)


SINGLE_SLOT_FACTORY_EXECUTION_ORDER_ID = (
    "public.av.nasa-earthrise.return-replication."
    "repeatability-single-slot-factory-execution-order.v1"
)


class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderError(ValueError):
    pass


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep:
    step_id: str
    step_index: int
    role: str
    factory_order_id: str
    factory_identity_id: str
    constructor_identity_id: str
    future_object_id: str
    selected_repeat_index: int
    one_time_future_step: bool
    executed: bool = False

    def __post_init__(self) -> None:
        if self.step_index not in (1, 2):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderError(
                "execution step index must be 1 or 2"
            )
        if self.role not in ("callable_factory", "gate_factory"):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderError(
                "execution step role must be callable_factory or gate_factory"
            )
        suffix = f".repeat-{self.selected_repeat_index}.v1"
        if not all(
            identifier.endswith(suffix)
            for identifier in (
                self.step_id, self.factory_order_id, self.factory_identity_id,
                self.constructor_identity_id, self.future_object_id,
            )
        ):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderError(
                "execution step identities must match selected repeat index"
            )
        if not self.one_time_future_step or self.executed:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderError(
                "execution steps must remain one-time future steps and unexecuted"
            )


@dataclass(frozen=True)
class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrder:
    execution_order_id: str
    selected_repeat_index: int
    execution_acceptance_id: str
    execution_preflight_id: str
    factory_order_acceptance_id: str
    factory_order_id: str
    factory_call_acceptance_id: str
    factory_call_preflight_id: str
    factory_acceptance_id: str
    factory_binding_id: str
    construction_acceptance_id: str
    construction_id: str
    object_reservation_id: str
    candidate_id: str
    logical_callable_id: str
    logical_gate_id: str
    reserved_executor_id: str
    future_callable_object_id: str
    future_gate_object_id: str
    callable_constructor_id: str
    gate_constructor_id: str
    future_callable_factory_id: str
    future_gate_factory_id: str
    future_callable_factory_order_id: str
    future_gate_factory_order_id: str
    ordered_factory_execution_candidate_ids: tuple[str, str]
    future_execution_steps: tuple[PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep, ...]
    source_id: str
    positive_execution_acceptance_bound: bool
    exactly_two_future_execution_steps_derived: bool
    callable_factory_step_first: bool
    gate_factory_step_second: bool
    execution_steps_one_time: bool
    execution_steps_unexecuted: bool
    selected_slot_still_fresh: bool
    factory_execution_order_complete: bool
    other_slots_unselected: tuple[int, ...]
    callable_factory_reference_stored: bool = False
    gate_factory_reference_stored: bool = False
    callable_reference_stored: bool = False
    factory_function_called: bool = False
    callable_factory_called: bool = False
    gate_factory_called: bool = False
    callable_object_created: bool = False
    gate_object_created: bool = False
    constructor_invoked: bool = False
    binding_performed: bool = False
    scheduler_available: bool = False
    media_decode_allowed: bool = False
    receptor_feed_allowed: bool = False
    start_release_granted: bool = False
    repeatability_run_allowed: bool = False
    repeat_run_started: bool = False
    stability_threshold_defined: bool = False
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        if self.selected_repeat_index not in (1, 2, 3):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderError(
                "selected repeat index must be one of 1, 2, 3"
            )
        suffix = f".repeat-{self.selected_repeat_index}.v1"
        indexed_ids = (
            self.execution_order_id, self.execution_acceptance_id,
            self.execution_preflight_id, self.factory_order_acceptance_id,
            self.factory_order_id, self.factory_call_acceptance_id,
            self.factory_call_preflight_id, self.factory_acceptance_id,
            self.factory_binding_id, self.callable_constructor_id,
            self.gate_constructor_id, self.future_callable_factory_id,
            self.future_gate_factory_id, self.future_callable_object_id,
            self.future_gate_object_id, self.future_callable_factory_order_id,
            self.future_gate_factory_order_id,
        )
        if not all(identifier.endswith(suffix) for identifier in indexed_ids):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderError(
                "factory execution order identities must match selected repeat index"
            )
        if tuple(self.ordered_factory_execution_candidate_ids) != (
            self.future_callable_factory_order_id,
            self.future_gate_factory_order_id,
        ):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderError(
                "execution candidates must remain callable then gate factory orders"
            )
        steps = tuple(self.future_execution_steps)
        if len(steps) != 2:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderError(
                "exactly two future execution steps are required"
            )
        if not (
            steps[0].step_index == 1
            and steps[0].role == "callable_factory"
            and steps[0].factory_order_id == self.future_callable_factory_order_id
            and steps[1].step_index == 2
            and steps[1].role == "gate_factory"
            and steps[1].factory_order_id == self.future_gate_factory_order_id
        ):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderError(
                "execution steps must remain callable factory first and gate factory second"
            )
        expected = tuple(index for index in (1, 2, 3) if index != self.selected_repeat_index)
        if tuple(self.other_slots_unselected) != expected:
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderError(
                "other slots must remain unselected"
            )
        required = (
            self.positive_execution_acceptance_bound,
            self.exactly_two_future_execution_steps_derived,
            self.callable_factory_step_first,
            self.gate_factory_step_second,
            self.execution_steps_one_time,
            self.execution_steps_unexecuted,
            self.selected_slot_still_fresh,
            self.factory_execution_order_complete,
        )
        forbidden = (
            self.callable_factory_reference_stored, self.gate_factory_reference_stored,
            self.callable_reference_stored, self.factory_function_called,
            self.callable_factory_called, self.gate_factory_called,
            self.callable_object_created, self.gate_object_created,
            self.constructor_invoked, self.binding_performed, self.scheduler_available,
            self.media_decode_allowed, self.receptor_feed_allowed,
            self.start_release_granted, self.repeatability_run_allowed,
            self.repeat_run_started, self.stability_threshold_defined,
            self.memory_claim_allowed, self.meaning_claim_allowed,
            self.organization_claim_allowed, self.ai_claim_allowed,
        )
        if not all(required) or any(forbidden):
            raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderError(
                "factory execution order cannot store references, call factories, create objects, bind, decode, feed receptors, start runs, or release claims"
            )
        object.__setattr__(self, "future_execution_steps", steps)
        object.__setattr__(
            self,
            "ordered_factory_execution_candidate_ids",
            tuple(self.ordered_factory_execution_candidate_ids),
        )
        object.__setattr__(self, "other_slots_unselected", tuple(self.other_slots_unselected))


def order_public_av_return_replication_repeatability_single_slot_factory_execution(
    acceptance: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionAcceptance,
) -> PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrder:
    if not isinstance(acceptance, PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionAcceptance):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderError(
            "single-slot factory order execution acceptance has the wrong type"
        )
    required = (
        acceptance.positive_execution_preflight_accepted,
        acceptance.two_ordered_execution_candidates_accepted,
        acceptance.callable_factory_candidate_first_accepted,
        acceptance.gate_factory_candidate_second_accepted,
        acceptance.fixed_candidate_order_accepted,
        acceptance.factory_order_identities_accepted,
        acceptance.selected_slot_still_fresh,
        acceptance.factory_order_execution_acceptance_complete,
    )
    forbidden = (
        acceptance.callable_factory_reference_stored, acceptance.gate_factory_reference_stored,
        acceptance.callable_reference_stored, acceptance.factory_function_called,
        acceptance.callable_factory_called, acceptance.gate_factory_called,
        acceptance.callable_object_created, acceptance.gate_object_created,
        acceptance.constructor_invoked, acceptance.binding_performed,
        acceptance.scheduler_available, acceptance.media_decode_allowed,
        acceptance.receptor_feed_allowed, acceptance.start_release_granted,
        acceptance.repeatability_run_allowed, acceptance.repeat_run_started,
    )
    if not all(required) or any(forbidden):
        raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderError(
            "one complete fresh reference-free execution acceptance is required"
        )

    index = acceptance.selected_repeat_index
    suffix = f"repeat-{index}.v1"
    steps = (
        PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep(
            step_id=(
                "public.av.nasa-earthrise.return-replication."
                f"single-slot-callable-factory-execution-step.{suffix}"
            ),
            step_index=1,
            role="callable_factory",
            factory_order_id=acceptance.future_callable_factory_order_id,
            factory_identity_id=acceptance.future_callable_factory_id,
            constructor_identity_id=acceptance.callable_constructor_id,
            future_object_id=acceptance.future_callable_object_id,
            selected_repeat_index=index,
            one_time_future_step=True,
        ),
        PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionStep(
            step_id=(
                "public.av.nasa-earthrise.return-replication."
                f"single-slot-gate-factory-execution-step.{suffix}"
            ),
            step_index=2,
            role="gate_factory",
            factory_order_id=acceptance.future_gate_factory_order_id,
            factory_identity_id=acceptance.future_gate_factory_id,
            constructor_identity_id=acceptance.gate_constructor_id,
            future_object_id=acceptance.future_gate_object_id,
            selected_repeat_index=index,
            one_time_future_step=True,
        ),
    )
    return PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrder(
        execution_order_id=f"{SINGLE_SLOT_FACTORY_EXECUTION_ORDER_ID}.{suffix}",
        selected_repeat_index=index,
        execution_acceptance_id=acceptance.acceptance_id,
        execution_preflight_id=acceptance.execution_preflight_id,
        factory_order_acceptance_id=acceptance.factory_order_acceptance_id,
        factory_order_id=acceptance.factory_order_id,
        factory_call_acceptance_id=acceptance.factory_call_acceptance_id,
        factory_call_preflight_id=acceptance.factory_call_preflight_id,
        factory_acceptance_id=acceptance.factory_acceptance_id,
        factory_binding_id=acceptance.factory_binding_id,
        construction_acceptance_id=acceptance.construction_acceptance_id,
        construction_id=acceptance.construction_id,
        object_reservation_id=acceptance.object_reservation_id,
        candidate_id=acceptance.candidate_id,
        logical_callable_id=acceptance.logical_callable_id,
        logical_gate_id=acceptance.logical_gate_id,
        reserved_executor_id=acceptance.reserved_executor_id,
        future_callable_object_id=acceptance.future_callable_object_id,
        future_gate_object_id=acceptance.future_gate_object_id,
        callable_constructor_id=acceptance.callable_constructor_id,
        gate_constructor_id=acceptance.gate_constructor_id,
        future_callable_factory_id=acceptance.future_callable_factory_id,
        future_gate_factory_id=acceptance.future_gate_factory_id,
        future_callable_factory_order_id=acceptance.future_callable_factory_order_id,
        future_gate_factory_order_id=acceptance.future_gate_factory_order_id,
        ordered_factory_execution_candidate_ids=acceptance.ordered_factory_execution_candidate_ids,
        future_execution_steps=steps,
        source_id=acceptance.source_id,
        positive_execution_acceptance_bound=True,
        exactly_two_future_execution_steps_derived=True,
        callable_factory_step_first=True,
        gate_factory_step_second=True,
        execution_steps_one_time=True,
        execution_steps_unexecuted=True,
        selected_slot_still_fresh=True,
        factory_execution_order_complete=True,
        other_slots_unselected=acceptance.other_slots_unselected,
    )


def execute_public_av_return_replication_repeatability_single_slot_factory_execution_order(
    order: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrder,
) -> None:
    del order
    raise PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderError(
        "factory execution is not released by the locked single-slot execution order"
    )


def public_av_return_replication_repeatability_single_slot_factory_execution_order_to_jsonable(
    order: PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrder,
) -> dict[str, Any]:
    return asdict(order)
