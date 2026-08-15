"""S1-HB terminal output builder for a completed real S1-GU carrier."""

from __future__ import annotations

from .e1_formation_s1fw_synthetic_live_state_handoff import _adapter_digest
from .e1_formation_s1gh_fresh_field_bridge import E1FormationS1GHFreshFieldBinding
from .e1_formation_s1gi_fixed_adapter_output_converter import (
    E1FormationS1GIFixedAdapterRealOutput,
    S1_GI_OUTPUT_ID,
)
from .e1_formation_s1gn_live_field_carrier import (
    E1FormationS1GNLiveFieldCarrier,
    e1_formation_s1gn_current_field_digest,
)
from .e1_refined_formation_runner import _digest, _state_payload


class E1FormationS1HBRealTerminalOutputError(ValueError):
    """Raised when a carrier is incomplete or not a real in-memory result."""


S1_HB_EXECUTION_KIND = "real-in-memory-fixed-adapter-probe"


def build_e1_formation_s1hb_real_terminal_output(
    fresh: E1FormationS1GHFreshFieldBinding,
    carrier: E1FormationS1GNLiveFieldCarrier,
) -> E1FormationS1GIFixedAdapterRealOutput:
    """Read one complete real carrier without advancing or persisting its field."""

    if not isinstance(fresh, E1FormationS1GHFreshFieldBinding) or not isinstance(
        carrier, E1FormationS1GNLiveFieldCarrier
    ):
        raise E1FormationS1HBRealTerminalOutputError(
            "S1-HB requires one typed fresh binding and terminal carrier"
        )
    fresh.__post_init__()
    carrier.__post_init__()
    plan = fresh.invocation.context.probe_plan
    expected_steps = len(plan.handoff.batches)
    if (
        carrier.fresh_binding is not fresh
        or carrier.current_field is fresh.fresh_field
        or carrier.binding_digest != fresh.binding_digest
        or carrier.completed_batch_count != expected_steps
        or carrier.actual_field_steps_executed != expected_steps
        or carrier.accounted_source_support_count
        != plan.handoff.source_event_count
        or carrier.current_field_digest
        != e1_formation_s1gn_current_field_digest(carrier.current_field)
        or carrier.persistence_performed is not False
        or carrier.claims_permitted is not False
    ):
        raise E1FormationS1HBRealTerminalOutputError(
            "S1-HB carrier is incomplete, synthetic, persisted, or cross-bound"
        )
    state_digest = _digest(_state_payload(fresh.invocation.source_state))
    adapter_digest = _adapter_digest(fresh.invocation.fixed_adapter)
    values = {
        "output_id": S1_GI_OUTPUT_ID,
        "binding_digest": fresh.binding_digest,
        "terminal_field_digest": carrier.current_field_digest,
        "activation": tuple(
            neuron.activation for neuron in carrier.current_field.layer.neurons
        ),
        "afterimage": tuple(
            neuron.afterimage for neuron in carrier.current_field.layer.neurons
        ),
        "field_step_count": expected_steps,
        "source_support_count": plan.handoff.source_event_count,
        "source_state_digest_before": state_digest,
        "source_state_digest_after": state_digest,
        "fixed_adapter_digest_before": adapter_digest,
        "fixed_adapter_digest_after": adapter_digest,
        "source_state_preserved": True,
        "fixed_adapter_preserved": True,
        "field_execution_kind": S1_HB_EXECUTION_KIND,
        "actual_field_steps_executed": expected_steps,
        "persistence_performed": False,
        "claims_permitted": False,
    }
    return E1FormationS1GIFixedAdapterRealOutput(
        **values,
        output_digest=_digest(values),
    )
