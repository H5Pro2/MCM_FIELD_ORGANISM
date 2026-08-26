"""Observer-side component intervention for causal shared-field controls."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace

from .shared_mcm_field import SharedMCMField


class SharedFieldComponentInterventionError(ValueError):
    """Raised when a causal control would alter more than one fast component."""


@dataclass(frozen=True, slots=True)
class SharedFieldComponentInterventionAudit:
    intervention_id: str
    mode: str
    neutral_value: float
    input_layer_digest: str
    output_layer_digest: str
    neuron_count: int
    activation_preserved_exactly: bool
    afterimage_preserved_exactly: bool
    activation_reset_globally: bool
    afterimage_reset_globally: bool
    neuron_identity_preserved: bool
    geometry_preserved: bool
    perception_preserved: bool
    tick_preserved: bool
    docks_preserved: bool
    last_distribution_preserved: bool
    input_field_unchanged: bool
    observer_side_only: bool
    organism_function_added: bool
    field_time_advanced: bool
    receptor_events_introduced: bool
    field_parameters_changed: bool
    runner_implementation_allowed: bool = False
    replication_run_allowed: bool = False
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        if self.mode not in {"reset_afterimage_preserve_activation", "reset_activation_preserve_afterimage"}:
            raise SharedFieldComponentInterventionError("invalid intervention mode")
        if self.neutral_value != 0.0 or self.neuron_count < 1:
            raise SharedFieldComponentInterventionError("intervention requires global neutral zero")
        preserved = (
            self.neuron_identity_preserved,
            self.geometry_preserved,
            self.perception_preserved,
            self.tick_preserved,
            self.docks_preserved,
            self.last_distribution_preserved,
            self.input_field_unchanged,
            self.observer_side_only,
        )
        if not all(preserved):
            raise SharedFieldComponentInterventionError("intervention changed a protected field role")
        if self.mode == "reset_afterimage_preserve_activation":
            if not self.activation_preserved_exactly or not self.afterimage_reset_globally:
                raise SharedFieldComponentInterventionError("afterimage reset contract failed")
        else:
            if not self.afterimage_preserved_exactly or not self.activation_reset_globally:
                raise SharedFieldComponentInterventionError("activation reset contract failed")
        forbidden = (
            self.organism_function_added,
            self.field_time_advanced,
            self.receptor_events_introduced,
            self.field_parameters_changed,
            self.runner_implementation_allowed,
            self.replication_run_allowed,
            self.memory_claim_allowed,
            self.meaning_claim_allowed,
            self.organization_claim_allowed,
            self.ai_claim_allowed,
        )
        if any(forbidden):
            raise SharedFieldComponentInterventionError("observer intervention cannot release mechanics, runs, or claims")


@dataclass(frozen=True, slots=True)
class SharedFieldComponentIntervention:
    field: SharedMCMField
    audit: SharedFieldComponentInterventionAudit

    def __post_init__(self) -> None:
        if not isinstance(self.field, SharedMCMField):
            raise SharedFieldComponentInterventionError("intervention requires one validated field")
        if not isinstance(self.audit, SharedFieldComponentInterventionAudit):
            raise SharedFieldComponentInterventionError("intervention audit is required")


def intervene_shared_field_component(
    field: SharedMCMField,
    mode: str,
) -> SharedFieldComponentIntervention:
    """Create one causal comparison state without advancing organism time."""

    if not isinstance(field, SharedMCMField):
        raise SharedFieldComponentInterventionError("shared field is required")
    if field.last_distribution is None:
        raise SharedFieldComponentInterventionError("intervention requires a completed field state")
    if mode not in {"reset_afterimage_preserve_activation", "reset_activation_preserve_afterimage"}:
        raise SharedFieldComponentInterventionError("invalid intervention mode")

    before_digest = field.layer.digest()
    before_neuron_digests = tuple(neuron.digest() for neuron in field.layer.neurons)
    if mode == "reset_afterimage_preserve_activation":
        neurons = tuple(replace(neuron, afterimage=0.0) for neuron in field.layer.neurons)
    else:
        neurons = tuple(replace(neuron, activation=0.0) for neuron in field.layer.neurons)
    output = replace(field, layer=replace(field.layer, neurons=neurons))

    original = field.layer.neurons
    changed = output.layer.neurons
    activation_preserved = all(a.activation == b.activation for a, b in zip(original, changed, strict=True))
    afterimage_preserved = all(a.afterimage == b.afterimage for a, b in zip(original, changed, strict=True))
    activation_reset = all(item.activation == 0.0 for item in changed)
    afterimage_reset = all(item.afterimage == 0.0 for item in changed)
    identity_preserved = all(
        (a.neuron_id, a.field_id, a.modality_id) == (b.neuron_id, b.field_id, b.modality_id)
        for a, b in zip(original, changed, strict=True)
    )
    geometry_preserved = all(
        (a.geometry_id, a.position) == (b.geometry_id, b.position)
        for a, b in zip(original, changed, strict=True)
    ) and field.layer.sample_offsets == output.layer.sample_offsets and field.layer.periodic_axes == output.layer.periodic_axes
    perception_preserved = all(a.perception == b.perception for a, b in zip(original, changed, strict=True))
    tick_preserved = all(a.tick == b.tick for a, b in zip(original, changed, strict=True))
    input_unchanged = before_digest == field.layer.digest() and before_neuron_digests == tuple(
        neuron.digest() for neuron in field.layer.neurons
    )
    audit = SharedFieldComponentInterventionAudit(
        intervention_id=f"observer.shared-field-component.{mode}.v1",
        mode=mode,
        neutral_value=0.0,
        input_layer_digest=before_digest,
        output_layer_digest=output.layer.digest(),
        neuron_count=len(changed),
        activation_preserved_exactly=activation_preserved,
        afterimage_preserved_exactly=afterimage_preserved,
        activation_reset_globally=activation_reset,
        afterimage_reset_globally=afterimage_reset,
        neuron_identity_preserved=identity_preserved,
        geometry_preserved=geometry_preserved,
        perception_preserved=perception_preserved,
        tick_preserved=tick_preserved,
        docks_preserved=field.docks == output.docks,
        last_distribution_preserved=field.last_distribution == output.last_distribution,
        input_field_unchanged=input_unchanged,
        observer_side_only=True,
        organism_function_added=False,
        field_time_advanced=False,
        receptor_events_introduced=False,
        field_parameters_changed=False,
    )
    return SharedFieldComponentIntervention(output, audit)


def shared_field_component_intervention_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (SharedFieldComponentInterventionAudit, SharedFieldComponentIntervention)
        for item in fields(cls)
    )
