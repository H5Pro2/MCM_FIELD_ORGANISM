"""S1-GN explicit live-field carrier and synthetic carrier transition."""

from __future__ import annotations

from dataclasses import dataclass, field

from .e1_formation_s1gh_fresh_field_bridge import E1FormationS1GHFreshFieldBinding
from .e1_refined_chain_canonical_producer import _initial_field_digest
from .e1_refined_formation_runner import _digest
from .receptor_proposal_handoff import ReceptorProposalBatch
from .shared_mcm_field import SharedMCMField


class E1FormationS1GNLiveFieldCarrierError(ValueError):
    """Raised when a carrier loses its explicit field object or accounting."""


S1_GN_CARRIER_ID = "e1.live-field-carrier.s1gn.v1"
S1_GN_TRANSITION_ID = "e1.synthetic-live-field-carrier-transition.s1gn.v1"


def e1_formation_s1gn_current_field_digest(field: SharedMCMField) -> str:
    """Digest an initial or completed field without advancing it."""

    if not isinstance(field, SharedMCMField):
        raise E1FormationS1GNLiveFieldCarrierError(
            "S1-GN field digest requires one SharedMCMField"
        )
    if field.last_distribution is None:
        return _initial_field_digest(field)
    return field.snapshot().digest()


@dataclass(frozen=True, slots=True)
class E1FormationS1GNLiveFieldCarrier:
    carrier_id: str
    fresh_binding: E1FormationS1GHFreshFieldBinding = field(repr=False)
    current_field: SharedMCMField = field(repr=False, compare=False)
    binding_digest: str
    initial_field_digest: str
    current_field_digest: str
    ordered_neuron_ids: tuple[str, ...]
    completed_batch_count: int
    accounted_source_support_count: int
    actual_field_steps_executed: int
    persistence_performed: bool
    claims_permitted: bool
    carrier_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"fresh_binding", "current_field", "carrier_digest"}
        }
        if (
            self.carrier_id != S1_GN_CARRIER_ID
            or not isinstance(self.fresh_binding, E1FormationS1GHFreshFieldBinding)
            or not isinstance(self.current_field, SharedMCMField)
            or self.binding_digest != self.fresh_binding.binding_digest
            or self.initial_field_digest != self.fresh_binding.initial_field_digest
            or self.current_field_digest
            != e1_formation_s1gn_current_field_digest(self.current_field)
            or self.ordered_neuron_ids
            != tuple(item.neuron_id for item in self.current_field.layer.neurons)
            or self.ordered_neuron_ids != self.fresh_binding.ordered_neuron_ids
            or isinstance(self.completed_batch_count, bool)
            or not isinstance(self.completed_batch_count, int)
            or self.completed_batch_count < 0
            or isinstance(self.accounted_source_support_count, bool)
            or not isinstance(self.accounted_source_support_count, int)
            or self.accounted_source_support_count < 0
            or isinstance(self.actual_field_steps_executed, bool)
            or not isinstance(self.actual_field_steps_executed, int)
            or self.actual_field_steps_executed < 0
            or self.actual_field_steps_executed > self.completed_batch_count
            or self.persistence_performed is not False
            or self.claims_permitted is not False
            or self.carrier_digest != _digest(payload)
        ):
            raise E1FormationS1GNLiveFieldCarrierError(
                "S1-GN carrier lost field identity, digest, or accounting"
            )
        if self.completed_batch_count == 0 and (
            self.current_field is not self.fresh_binding.fresh_field
            or self.current_field_digest != self.initial_field_digest
            or self.accounted_source_support_count != 0
            or self.actual_field_steps_executed != 0
        ):
            raise E1FormationS1GNLiveFieldCarrierError(
                "S1-GN initial carrier is not the exact fresh field"
            )


def build_e1_formation_s1gn_initial_live_field_carrier(
    fresh: E1FormationS1GHFreshFieldBinding,
) -> E1FormationS1GNLiveFieldCarrier:
    """Wrap the exact S1-GH fresh field as explicit initial runtime state."""

    if not isinstance(fresh, E1FormationS1GHFreshFieldBinding):
        raise E1FormationS1GNLiveFieldCarrierError(
            "S1-GN requires one typed S1-GH fresh binding"
        )
    fresh.__post_init__()
    values = {
        "carrier_id": S1_GN_CARRIER_ID,
        "fresh_binding": fresh,
        "current_field": fresh.fresh_field,
        "binding_digest": fresh.binding_digest,
        "initial_field_digest": fresh.initial_field_digest,
        "current_field_digest": e1_formation_s1gn_current_field_digest(
            fresh.fresh_field
        ),
        "ordered_neuron_ids": fresh.ordered_neuron_ids,
        "completed_batch_count": 0,
        "accounted_source_support_count": 0,
        "actual_field_steps_executed": 0,
        "persistence_performed": False,
        "claims_permitted": False,
    }
    payload = {
        name: value
        for name, value in values.items()
        if name not in {"fresh_binding", "current_field"}
    }
    return E1FormationS1GNLiveFieldCarrier(
        **values,
        carrier_digest=_digest(payload),
    )


@dataclass(frozen=True, slots=True)
class E1FormationS1GNLiveFieldCarrierTransition:
    transition_id: str
    previous_carrier: E1FormationS1GNLiveFieldCarrier = field(repr=False)
    next_carrier: E1FormationS1GNLiveFieldCarrier = field(repr=False)
    binding_digest: str
    batch_index: int
    batch_step_start_tick: int
    batch_step_end_tick: int
    batch_source_support_count: int
    previous_field_digest: str
    next_field_digest: str
    previous_field_object_carried_explicitly: bool
    next_field_object_carried_explicitly: bool
    synthetic_no_field_advance: bool
    field_object_replaced: bool
    accounted_field_steps: int
    actual_field_steps_executed: int
    persistence_performed: bool
    claims_permitted: bool
    transition_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name
            not in {
                "previous_carrier",
                "next_carrier",
                "transition_digest",
            }
        }
        if (
            self.transition_id != S1_GN_TRANSITION_ID
            or not isinstance(
                self.previous_carrier, E1FormationS1GNLiveFieldCarrier
            )
            or not isinstance(self.next_carrier, E1FormationS1GNLiveFieldCarrier)
            or self.binding_digest != self.previous_carrier.binding_digest
            or self.binding_digest != self.next_carrier.binding_digest
            or self.batch_index != self.previous_carrier.completed_batch_count
            or self.batch_step_start_tick < 0
            or self.batch_step_end_tick <= self.batch_step_start_tick
            or self.batch_source_support_count < 0
            or self.previous_field_digest
            != self.previous_carrier.current_field_digest
            or self.next_field_digest != self.next_carrier.current_field_digest
            or self.next_carrier.completed_batch_count
            != self.previous_carrier.completed_batch_count + 1
            or self.next_carrier.accounted_source_support_count
            != self.previous_carrier.accounted_source_support_count
            + self.batch_source_support_count
            or any(
                value is not True
                for value in (
                    self.previous_field_object_carried_explicitly,
                    self.next_field_object_carried_explicitly,
                    self.synthetic_no_field_advance,
                )
            )
            or self.field_object_replaced is not False
            or self.next_carrier.current_field
            is not self.previous_carrier.current_field
            or self.previous_field_digest != self.next_field_digest
            or self.accounted_field_steps != 1
            or self.actual_field_steps_executed != 0
            or self.next_carrier.actual_field_steps_executed
            != self.previous_carrier.actual_field_steps_executed
            or self.persistence_performed is not False
            or self.claims_permitted is not False
            or self.transition_digest != _digest(payload)
        ):
            raise E1FormationS1GNLiveFieldCarrierError(
                "S1-GN synthetic transition changed field state or accounting"
            )


def advance_e1_formation_s1gn_live_field_carrier_synthetically(
    fresh: E1FormationS1GHFreshFieldBinding,
    batch: ReceptorProposalBatch,
    carrier: E1FormationS1GNLiveFieldCarrier,
) -> E1FormationS1GNLiveFieldCarrierTransition:
    """Advance carrier metadata while retaining the explicit field unchanged."""

    if (
        not isinstance(fresh, E1FormationS1GHFreshFieldBinding)
        or not isinstance(batch, ReceptorProposalBatch)
        or not isinstance(carrier, E1FormationS1GNLiveFieldCarrier)
    ):
        raise E1FormationS1GNLiveFieldCarrierError(
            "S1-GN transition requires fresh binding, batch, and carrier"
        )
    fresh.__post_init__()
    carrier.__post_init__()
    batches = fresh.invocation.context.probe_plan.handoff.batches
    if (
        carrier.fresh_binding is not fresh
        or carrier.binding_digest != fresh.binding_digest
        or carrier.completed_batch_count >= len(batches)
        or batches[carrier.completed_batch_count] is not batch
        or batch.batch_index != carrier.completed_batch_count
    ):
        raise E1FormationS1GNLiveFieldCarrierError(
            "S1-GN carrier and exact next batch do not share one route"
        )
    next_values = {
        "carrier_id": S1_GN_CARRIER_ID,
        "fresh_binding": fresh,
        "current_field": carrier.current_field,
        "binding_digest": carrier.binding_digest,
        "initial_field_digest": carrier.initial_field_digest,
        "current_field_digest": carrier.current_field_digest,
        "ordered_neuron_ids": carrier.ordered_neuron_ids,
        "completed_batch_count": carrier.completed_batch_count + 1,
        "accounted_source_support_count": (
            carrier.accounted_source_support_count + batch.event_count
        ),
        "actual_field_steps_executed": carrier.actual_field_steps_executed,
        "persistence_performed": False,
        "claims_permitted": False,
    }
    next_payload = {
        name: value
        for name, value in next_values.items()
        if name not in {"fresh_binding", "current_field"}
    }
    next_carrier = E1FormationS1GNLiveFieldCarrier(
        **next_values,
        carrier_digest=_digest(next_payload),
    )
    values = {
        "transition_id": S1_GN_TRANSITION_ID,
        "previous_carrier": carrier,
        "next_carrier": next_carrier,
        "binding_digest": fresh.binding_digest,
        "batch_index": batch.batch_index,
        "batch_step_start_tick": batch.step_time.start_tick,
        "batch_step_end_tick": batch.step_time.end_tick,
        "batch_source_support_count": batch.event_count,
        "previous_field_digest": carrier.current_field_digest,
        "next_field_digest": next_carrier.current_field_digest,
        "previous_field_object_carried_explicitly": isinstance(
            carrier.current_field, SharedMCMField
        ),
        "next_field_object_carried_explicitly": isinstance(
            next_carrier.current_field, SharedMCMField
        ),
        "synthetic_no_field_advance": True,
        "field_object_replaced": False,
        "accounted_field_steps": 1,
        "actual_field_steps_executed": 0,
        "persistence_performed": False,
        "claims_permitted": False,
    }
    payload = {
        name: value
        for name, value in values.items()
        if name not in {"previous_carrier", "next_carrier"}
    }
    return E1FormationS1GNLiveFieldCarrierTransition(
        **values,
        transition_digest=_digest(payload),
    )
