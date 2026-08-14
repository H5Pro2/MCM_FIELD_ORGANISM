"""S1-EC76 synthetic full route through the corrected EC75 converters."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field

from .e1_common_probe_n2_r2_object_handoff import E1CommonProbeN2R2ObjectHandoff
from .e1_common_probe_n2_r2_positive_step_receipt_contract import (
    E1PositiveStepFormationReceipt,
    E1PositiveStepProbeReceipt,
    S1_EC63_ROLE_STATE_ROUTES,
)
from .e1_common_probe_n2_r2_real_output_converters import (
    _synthetic_typed_formation_output,
    _synthetic_typed_probe_output,
    convert_e1_common_probe_real_formation_output,
    convert_e1_common_probe_real_probe_output,
    diagnose_e1_common_probe_real_formation_output,
)
from .e1_common_probe_real_wrappers import E1CommonProbeFreshField
from .e1_refined_chain_canonical_producer import _initial_field_digest
from .e1_refined_formation_runner import _digest


class E1CommonProbeN2R2EC75SyntheticRouteError(ValueError):
    """Raised when EC76 leaves its zero-field synthetic route."""


S1_EC76_ROUTE_ID = "e1.common-probe-n2-r2-ec75-synthetic-route.s1ec76.v1"
S1_EC76_EC59_HANDOFF_DIGEST = (
    "5acf624ffaa209e058b74134a069946e21eb2db6609ad7db8301c2c122bca3cb"
)


@dataclass(frozen=True, slots=True)
class E1CommonProbeN2R2EC75SyntheticRouteResult:
    route_id: str
    source_handoff_digest: str
    execution_mode: str
    formation_count: int
    fresh_field_count: int
    probe_count: int
    formation_diagnostic_digests: tuple[str, ...]
    formation_receipt_digests: tuple[str, ...]
    probe_receipt_digests: tuple[str, ...]
    accounted_formation_steps: int
    accounted_probe_steps: int
    accounted_total_steps: int
    actual_field_steps_executed: int
    all_six_diagnostic_gates_passed_for_all_formations: bool
    all_state_routes_exact: bool
    all_backreaction_routes_exact: bool
    all_fresh_fields_identical_and_object_separate: bool
    real_wrapper_execution_permitted: bool
    real_adapter_execution_permitted: bool
    real_coordinator_execution_permitted: bool
    persistence_performed: bool
    research_decision_permitted: bool
    memory_claim_permitted: bool
    result_digest: str
    formations: tuple[E1PositiveStepFormationReceipt, ...] = field(
        repr=False, compare=False
    )
    fresh_fields: tuple[E1CommonProbeFreshField, ...] = field(
        repr=False, compare=False
    )
    probes: tuple[E1PositiveStepProbeReceipt, ...] = field(
        repr=False, compare=False
    )

    def __post_init__(self) -> None:
        metadata = _metadata(self)
        if (
            self.route_id != S1_EC76_ROUTE_ID
            or self.source_handoff_digest != S1_EC76_EC59_HANDOFF_DIGEST
            or self.execution_mode != "synthetic-typed-output-through-real-converters"
            or (self.formation_count, self.fresh_field_count, self.probe_count)
            != (4, 8, 8)
            or len(self.formation_diagnostic_digests) != 4
            or self.formation_receipt_digests
            != tuple(item.receipt_digest for item in self.formations)
            or self.probe_receipt_digests
            != tuple(item.receipt_digest for item in self.probes)
            or (
                self.accounted_formation_steps,
                self.accounted_probe_steps,
                self.accounted_total_steps,
            )
            != (1608, 1600, 3208)
            or self.actual_field_steps_executed != 0
            or any(
                value is not True
                for value in (
                    self.all_six_diagnostic_gates_passed_for_all_formations,
                    self.all_state_routes_exact,
                    self.all_backreaction_routes_exact,
                    self.all_fresh_fields_identical_and_object_separate,
                )
            )
            or any(
                value is not False
                for value in (
                    self.real_wrapper_execution_permitted,
                    self.real_adapter_execution_permitted,
                    self.real_coordinator_execution_permitted,
                    self.persistence_performed,
                    self.research_decision_permitted,
                    self.memory_claim_permitted,
                )
            )
            or self.result_digest != _digest(metadata)
        ):
            raise E1CommonProbeN2R2EC75SyntheticRouteError(
                "S1-EC76 route changed or crossed zero-field scope"
            )


def _metadata(
    result: E1CommonProbeN2R2EC75SyntheticRouteResult,
) -> dict[str, object]:
    return {
        name: getattr(result, name)
        for name in result.__dataclass_fields__
        if name not in {"result_digest", "formations", "fresh_fields", "probes"}
    }


def run_e1_common_probe_n2_r2_ec75_synthetic_route(
    handoff: E1CommonProbeN2R2ObjectHandoff,
) -> E1CommonProbeN2R2EC75SyntheticRouteResult:
    """Exercise all corrected converters and routes without a field kernel."""

    if (
        not isinstance(handoff, E1CommonProbeN2R2ObjectHandoff)
        or handoff.handoff_digest != S1_EC76_EC59_HANDOFF_DIGEST
    ):
        raise E1CommonProbeN2R2EC75SyntheticRouteError(
            "S1-EC76 requires the exact EC59 object handoff"
        )
    handoff.__post_init__()
    formations = []
    diagnostics = []
    for slot in handoff.formation_slots:
        output = _synthetic_typed_formation_output(handoff, slot)
        diagnostic = diagnose_e1_common_probe_real_formation_output(slot, output)
        if not diagnostic.all_passed or len(diagnostic.gates) != 6:
            raise E1CommonProbeN2R2EC75SyntheticRouteError(
                "S1-EC76 formation did not pass all six EC75 gates"
            )
        diagnostics.append(diagnostic)
        formations.append(convert_e1_common_probe_real_formation_output(slot, output))
    states = {item.state_role: item for item in formations}
    routes = dict(S1_EC63_ROLE_STATE_ROUTES)
    fresh_fields = []
    probes = []
    for index, slot in enumerate(handoff.resolved_slots):
        field = copy.deepcopy(handoff.initial_field)
        fresh = E1CommonProbeFreshField(
            slot.binding.binding_digest,
            _initial_field_digest(field),
            field,
        )
        state_role = routes[slot.binding.role_id]
        formation = None if state_role is None else states[state_role]
        state_digest = None if formation is None else formation.output_state_digest
        output = _synthetic_typed_probe_output(slot, state_digest, index)
        receipt = convert_e1_common_probe_real_probe_output(
            slot, output, formation
        )
        fresh_fields.append(fresh)
        probes.append(receipt)
    initial_digests = {_initial_field_digest(item.field) for item in fresh_fields}
    values = {
        "route_id": S1_EC76_ROUTE_ID,
        "source_handoff_digest": handoff.handoff_digest,
        "execution_mode": "synthetic-typed-output-through-real-converters",
        "formation_count": len(formations),
        "fresh_field_count": len(fresh_fields),
        "probe_count": len(probes),
        "formation_diagnostic_digests": tuple(
            item.diagnostic_digest for item in diagnostics
        ),
        "formation_receipt_digests": tuple(
            item.receipt_digest for item in formations
        ),
        "probe_receipt_digests": tuple(item.receipt_digest for item in probes),
        "accounted_formation_steps": sum(
            item.accounted_field_steps for item in formations
        ),
        "accounted_probe_steps": sum(item.accounted_field_steps for item in probes),
        "accounted_total_steps": sum(
            item.accounted_field_steps for item in (*formations, *probes)
        ),
        "actual_field_steps_executed": 0,
        "all_six_diagnostic_gates_passed_for_all_formations": all(
            item.all_passed and len(item.gates) == 6 for item in diagnostics
        ),
        "all_state_routes_exact": all(
            item.selected_state_role == routes[slot.binding.role_id]
            for slot, item in zip(handoff.resolved_slots, probes, strict=True)
        ),
        "all_backreaction_routes_exact": all(
            item.backreaction_enabled is slot.binding.backreaction_enabled
            for slot, item in zip(handoff.resolved_slots, probes, strict=True)
        ),
        "all_fresh_fields_identical_and_object_separate": (
            initial_digests == {handoff.initial_field_digest}
            and len({id(item.field) for item in fresh_fields}) == 8
        ),
        "real_wrapper_execution_permitted": False,
        "real_adapter_execution_permitted": False,
        "real_coordinator_execution_permitted": False,
        "persistence_performed": False,
        "research_decision_permitted": False,
        "memory_claim_permitted": False,
    }
    return E1CommonProbeN2R2EC75SyntheticRouteResult(
        **values,
        result_digest=_digest(values),
        formations=tuple(formations),
        fresh_fields=tuple(fresh_fields),
        probes=tuple(probes),
    )
