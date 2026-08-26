"""Private S1-EC12 static resource preflight for full prepared formation."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .e1_confirmation_prepared_execution_bundle import E1PreparedExecutionBundle
from .e1_confirmation_prepared_formation_consumer import (
    S1_EC7_FORMATION_ARMS,
    _typed_values_from_bundle,
)
from .e1_confirmation_research_corridor import S1_EC3_RUN_ID
from .e1_confirmation_typed_prepared_inputs import S1_EC2_INPUT_ROLES
from .e1_refined_formation_runner import _digest


class E1ConfirmationFullFormationResourcePreflightError(ValueError):
    """Raised when the S1-EC12 full-formation inventory is not bounded."""


S1_EC12_EXPECTED_REFINEMENTS = (
    ("r2", 2, 400, 400),
    ("r4", 4, 800, 800),
    ("r8", 8, 1600, 1600),
)
S1_EC12_LIMITS = (
    ("maximum_field_nodes", 128),
    ("maximum_state_edges", 256),
    ("maximum_single_arm_steps", 1600),
    ("maximum_total_arm_steps", 14_000),
    ("maximum_node_step_units", 1_500_000),
    ("maximum_edge_step_units", 2_500_000),
    ("maximum_retained_output_bindings", 2_500),
)
S1_EC12_ABORT_CONDITIONS = (
    "prepared-input-digest-change",
    "refinement-or-step-inventory-change",
    "field-geometry-limit-exceeded",
    "arm-step-limit-exceeded",
    "node-step-limit-exceeded",
    "edge-step-limit-exceeded",
    "retained-output-limit-exceeded",
    "canonical-path-requested",
    "probe-requested",
)


@dataclass(frozen=True, slots=True)
class E1FullFormationResourcePreflight:
    execution_id: str
    research_descriptor_digest: str
    input_manifest_digest: str
    refinement_step_counts: tuple[tuple[str, int, int, int], ...]
    formation_arm_ids: tuple[str, ...]
    formation_arm_runs: int
    field_nodes: int
    state_edges: int
    docks: int
    history_sequences_ab: int
    history_sequences_ba: int
    total_arm_steps: int
    node_step_units_upper_bound: int
    edge_step_units_upper_bound: int
    copied_runtime_objects_upper_bound: int
    retained_output_bindings_upper_bound: int
    limits: tuple[tuple[str, int], ...]
    abort_conditions: tuple[str, ...]
    resource_gate_passed: bool
    path_independent: bool
    field_execution_performed: bool
    attempt_created: bool
    report_created: bool
    canonical_execution_permitted: bool
    probe_execution_permitted: bool
    claims_permitted: bool
    result_digest: str

    def __post_init__(self) -> None:
        numeric_digests = (
            self.research_descriptor_digest,
            self.input_manifest_digest,
        )
        if (
            self.execution_id != S1_EC3_RUN_ID
            or any(
                len(value) != 64
                or any(char not in "0123456789abcdef" for char in value)
                for value in numeric_digests
            )
            or self.refinement_step_counts != S1_EC12_EXPECTED_REFINEMENTS
            or self.formation_arm_ids != S1_EC7_FORMATION_ARMS
            or self.formation_arm_runs != 15
            or self.field_nodes != 84
            or self.state_edges != 145
            or self.docks != 2
            or self.history_sequences_ab != 2
            or self.history_sequences_ba != 2
            or self.total_arm_steps != 14_000
            or self.node_step_units_upper_bound != 1_176_000
            or self.edge_step_units_upper_bound != 2_030_000
            or self.copied_runtime_objects_upper_bound != 30
            or self.retained_output_bindings_upper_bound != 2_175
            or self.limits != S1_EC12_LIMITS
            or self.abort_conditions != S1_EC12_ABORT_CONDITIONS
            or self.resource_gate_passed is not True
            or self.path_independent is not True
            or self.field_execution_performed is not False
            or self.attempt_created is not False
            or self.report_created is not False
            or self.canonical_execution_permitted is not False
            or self.probe_execution_permitted is not False
            or self.claims_permitted is not False
        ):
            raise E1ConfirmationFullFormationResourcePreflightError(
                "S1-EC12 resource preflight changed or failed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "result_digest"
        }
        if self.result_digest != _digest(payload):
            raise E1ConfirmationFullFormationResourcePreflightError(
                "S1-EC12 result digest does not match its payload"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


def preflight_prepared_full_formation_resources(
    bundle: E1PreparedExecutionBundle,
) -> E1FullFormationResourcePreflight:
    """Count full prepared work without Lock, Attempt, field step, or report."""

    if (
        not isinstance(bundle, E1PreparedExecutionBundle)
        or tuple(role for role, _ in bundle.input_manifest) != S1_EC2_INPUT_ROLES
    ):
        raise E1ConfirmationFullFormationResourcePreflightError(
            "S1-EC12 requires the complete prepared descriptor bundle"
        )
    bundle.require_inputs_unchanged()
    values = _typed_values_from_bundle(bundle)
    ab_plans = values.history_ab_plans.plans
    ba_plans = values.history_ba_plans.plans
    refinements = tuple(
        (
            ab.refinement_id,
            ab.factor,
            len(ab.proposal_steps),
            len(ba.proposal_steps),
        )
        for ab, ba in zip(ab_plans, ba_plans, strict=True)
    )
    if refinements != S1_EC12_EXPECTED_REFINEMENTS:
        raise E1ConfirmationFullFormationResourcePreflightError(
            "S1-EC12 full refinement inventory changed"
        )
    field_nodes = len(values.initial_field.layer.neurons)
    state_edges = len(values.initial_state.edge_bindings)
    total_arm_steps = sum(
        3 * ab_steps + 2 * ba_steps
        for _, _, ab_steps, ba_steps in refinements
    )
    limit = dict(S1_EC12_LIMITS)
    retained_bindings = len(S1_EC7_FORMATION_ARMS) * len(refinements) * state_edges
    inventory = {
        "field_nodes": field_nodes,
        "state_edges": state_edges,
        "single_arm_steps": max(
            max(ab_steps, ba_steps)
            for _, _, ab_steps, ba_steps in refinements
        ),
        "total_arm_steps": total_arm_steps,
        "node_step_units": total_arm_steps * field_nodes,
        "edge_step_units": total_arm_steps * state_edges,
        "retained_output_bindings": retained_bindings,
    }
    gate = (
        inventory["field_nodes"] <= limit["maximum_field_nodes"]
        and inventory["state_edges"] <= limit["maximum_state_edges"]
        and inventory["single_arm_steps"] <= limit["maximum_single_arm_steps"]
        and inventory["total_arm_steps"] <= limit["maximum_total_arm_steps"]
        and inventory["node_step_units"] <= limit["maximum_node_step_units"]
        and inventory["edge_step_units"] <= limit["maximum_edge_step_units"]
        and inventory["retained_output_bindings"]
        <= limit["maximum_retained_output_bindings"]
    )
    if not gate:
        raise E1ConfirmationFullFormationResourcePreflightError(
            "S1-EC12 prepared workload exceeds a fixed resource limit"
        )
    bundle.require_inputs_unchanged()
    payload = {
        "execution_id": bundle.execution_id,
        "research_descriptor_digest": values.corridor.digest(),
        "input_manifest_digest": _digest(bundle.input_manifest),
        "refinement_step_counts": refinements,
        "formation_arm_ids": S1_EC7_FORMATION_ARMS,
        "formation_arm_runs": len(S1_EC7_FORMATION_ARMS) * len(refinements),
        "field_nodes": field_nodes,
        "state_edges": state_edges,
        "docks": len(values.initial_field.docks),
        "history_sequences_ab": len(values.av_permutation.history_ab),
        "history_sequences_ba": len(values.av_permutation.history_ba),
        "total_arm_steps": total_arm_steps,
        "node_step_units_upper_bound": inventory["node_step_units"],
        "edge_step_units_upper_bound": inventory["edge_step_units"],
        "copied_runtime_objects_upper_bound": 2
        * len(S1_EC7_FORMATION_ARMS)
        * len(refinements),
        "retained_output_bindings_upper_bound": retained_bindings,
        "limits": S1_EC12_LIMITS,
        "abort_conditions": S1_EC12_ABORT_CONDITIONS,
        "resource_gate_passed": gate,
        "path_independent": True,
        "field_execution_performed": False,
        "attempt_created": False,
        "report_created": False,
        "canonical_execution_permitted": False,
        "probe_execution_permitted": False,
        "claims_permitted": False,
    }
    return E1FullFormationResourcePreflight(
        **payload,
        result_digest=_digest(payload),
    )
