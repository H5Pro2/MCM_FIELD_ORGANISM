"""S1-EC91 separate r4/r8 receipts, pure converters, and synthetic fixture."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

from .e1_common_probe_ec89_r4_r8_object_handoffs import (
    E1CommonProbeEC89R4R8ObjectHandoffSet,
    E1CommonProbeEC89RefinementObjectHandoff,
)
from .e1_common_probe_n2_r2_positive_step_receipt_contract import (
    S1_EC63_ROLE_STATE_ROUTES,
)
from .e1_common_probe_real_wrappers import (
    E1CommonProbeRealProbeOutput,
    E1CommonProbeResolvedSlot,
)
from .e1_confirmation_formation_runner import E1ConfirmationFormationArmAudit
from .e1_confirmation_prepared_real_formation_kernel import (
    E1PreparedRealFormationArmResult,
)
from .e1_handoff_digest_schemas import e1_handoff_digest_pair
from .e1_local_edge_plasticity import E1LocalEdgePlasticityState
from .e1_refined_chain_canonical_producer import (
    _initial_field_digest,
    _initial_state_digest,
)
from .e1_refined_formation_runner import _digest, _state_payload


class E1CommonProbeEC91RefinementReceiptConverterError(ValueError):
    """Raised when an r4/r8 synthetic output leaves its bound plan."""


S1_EC91_FIXTURE_ID = "e1.common-probe-r4-r8-receipts-converters.s1ec91.v1"
S1_EC91_EC89_RESULT_DIGEST = (
    "eadaee38d591f4ad36acbf00aec3681cd9da0069173a62055ca8ea70a34ffae9"
)
S1_EC91_STEP_BUDGETS = {
    "r4": (804, 400, 6416),
    "r8": (1608, 800, 12832),
}


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC91FormationReceipt:
    refinement_id: str
    state_role: str
    output_state_digest: str
    accounted_field_steps: int
    source_support_count: int
    source_result_digest: str
    execution_mode: str
    receipt_digest: str
    output_state: E1LocalEdgePlasticityState = field(repr=False, compare=False)

    def __post_init__(self) -> None:
        expected = S1_EC91_STEP_BUDGETS.get(self.refinement_id)
        values = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"output_state", "receipt_digest"}
        }
        if (
            expected is None
            or self.state_role
            not in ("active-ab", "active-ba", "formation-ablated-ab", "formation-ablated-ba")
            or not isinstance(self.output_state, E1LocalEdgePlasticityState)
            or self.output_state_digest != _digest(_state_payload(self.output_state))
            or self.accounted_field_steps != expected[0]
            or self.source_support_count != 220
            or not _valid_digest(self.source_result_digest)
            or self.execution_mode not in {"synthetic-typed-output", "real-wrapper"}
            or self.receipt_digest != _digest(values)
        ):
            raise E1CommonProbeEC91RefinementReceiptConverterError(
                "S1-EC91 formation receipt changed"
            )


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC91ProbeReceipt:
    refinement_id: str
    role_id: str
    binding_digest: str
    selected_state_role: str | None
    selected_state_digest: str | None
    backreaction_enabled: bool
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    accounted_field_steps: int
    source_support_count: int
    source_result_digest: str
    execution_mode: str
    receipt_digest: str

    def __post_init__(self) -> None:
        expected = S1_EC91_STEP_BUDGETS.get(self.refinement_id)
        route = dict(S1_EC63_ROLE_STATE_ROUTES).get(self.role_id, "missing")
        values = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "receipt_digest"
        }
        if (
            expected is None
            or route != self.selected_state_role
            or not _valid_digest(self.binding_digest)
            or (self.selected_state_digest is None)
            is not (self.selected_state_role is None)
            or (
                self.selected_state_digest is not None
                and not _valid_digest(self.selected_state_digest)
            )
            or self.backreaction_enabled
            is not (
                self.selected_state_role is not None
                and "probe-feedback-ablated" not in self.role_id
            )
            or not self.activation
            or len(self.activation) != len(self.afterimage)
            or self.accounted_field_steps != expected[1]
            or self.source_support_count != 110
            or not _valid_digest(self.source_result_digest)
            or self.execution_mode not in {"synthetic-typed-output", "real-wrapper"}
            or self.receipt_digest != _digest(values)
        ):
            raise E1CommonProbeEC91RefinementReceiptConverterError(
                "S1-EC91 probe receipt changed"
            )


def convert_e1_common_probe_ec91_formation_output(
    handoff: E1CommonProbeEC89RefinementObjectHandoff,
    resolved: E1CommonProbeResolvedSlot,
    output: E1PreparedRealFormationArmResult,
    *,
    execution_mode: str = "synthetic-typed-output",
) -> E1CommonProbeEC91FormationReceipt:
    """Convert one existing typed formation output using its refinement plan."""

    if (
        not isinstance(handoff, E1CommonProbeEC89RefinementObjectHandoff)
        or not isinstance(resolved, E1CommonProbeResolvedSlot)
        or resolved not in handoff.formation_slots
        or not isinstance(output, E1PreparedRealFormationArmResult)
        or resolved.formation_plan is None
    ):
        raise E1CommonProbeEC91RefinementReceiptConverterError(
            "S1-EC91 requires one bound formation output"
        )
    handoff.__post_init__()
    resolved.__post_init__()
    output.__post_init__()
    expected_steps = S1_EC91_STEP_BUDGETS[handoff.refinement_id][0]
    digests = e1_handoff_digest_pair(resolved.formation_plan.handoff)
    if (
        resolved.binding.refinement_id != handoff.refinement_id
        or output.refinement_id != handoff.refinement_id
        or output.arm_id != resolved.binding.formation_arm_id
        or output.audit.handoff_digest != digests.assignment_digest
        or resolved.formation_plan.handoff_digest != digests.envelope_digest
        or output.audit.source_support_count
        != resolved.formation_plan.handoff.source_event_count
        or len(resolved.formation_plan.proposal_steps) != expected_steps
    ):
        raise E1CommonProbeEC91RefinementReceiptConverterError(
            "S1-EC91 formation output does not match its refinement plan"
        )
    values = {
        "refinement_id": handoff.refinement_id,
        "state_role": resolved.binding.state_role,
        "output_state_digest": output.output_state_digest,
        "accounted_field_steps": expected_steps,
        "source_support_count": output.audit.source_support_count,
        "source_result_digest": output.result_digest,
        "execution_mode": execution_mode,
    }
    return E1CommonProbeEC91FormationReceipt(
        **values,
        receipt_digest=_digest(values),
        output_state=output.output_state,
    )


def convert_e1_common_probe_ec91_probe_output(
    handoff: E1CommonProbeEC89RefinementObjectHandoff,
    resolved: E1CommonProbeResolvedSlot,
    output: E1CommonProbeRealProbeOutput,
    formation: E1CommonProbeEC91FormationReceipt | None,
    *,
    execution_mode: str = "synthetic-typed-output",
) -> E1CommonProbeEC91ProbeReceipt:
    """Convert one existing typed probe output using its refinement plan."""

    if (
        not isinstance(handoff, E1CommonProbeEC89RefinementObjectHandoff)
        or not isinstance(resolved, E1CommonProbeResolvedSlot)
        or resolved not in handoff.resolved_slots
        or not isinstance(output, E1CommonProbeRealProbeOutput)
    ):
        raise E1CommonProbeEC91RefinementReceiptConverterError(
            "S1-EC91 requires one bound probe output"
        )
    handoff.__post_init__()
    resolved.__post_init__()
    output.__post_init__()
    expected_role = dict(S1_EC63_ROLE_STATE_ROUTES)[resolved.binding.role_id]
    if expected_role is None:
        if formation is not None:
            raise E1CommonProbeEC91RefinementReceiptConverterError(
                "S1-EC91 P0 cannot receive a formation receipt"
            )
        state_digest = None
    else:
        if (
            not isinstance(formation, E1CommonProbeEC91FormationReceipt)
            or formation.refinement_id != handoff.refinement_id
            or formation.state_role != expected_role
        ):
            raise E1CommonProbeEC91RefinementReceiptConverterError(
                "S1-EC91 probe formation route changed"
            )
        formation.__post_init__()
        state_digest = formation.output_state_digest
    expected_steps = S1_EC91_STEP_BUDGETS[handoff.refinement_id][1]
    if (
        resolved.binding.refinement_id != handoff.refinement_id
        or output.binding_digest != resolved.binding.binding_digest
        or output.field_step_count != len(resolved.probe_plan.proposal_steps)
        or output.field_step_count != expected_steps
        or output.source_support_count != resolved.probe_plan.handoff.source_event_count
        or output.frozen_state_digest_before != state_digest
        or output.frozen_state_digest_after != state_digest
        or output.frozen_state_preserved is not True
    ):
        raise E1CommonProbeEC91RefinementReceiptConverterError(
            "S1-EC91 probe output does not match its refinement plan"
        )
    values = {
        "refinement_id": handoff.refinement_id,
        "role_id": resolved.binding.role_id,
        "binding_digest": resolved.binding.binding_digest,
        "selected_state_role": expected_role,
        "selected_state_digest": state_digest,
        "backreaction_enabled": resolved.binding.backreaction_enabled,
        "activation": output.activation,
        "afterimage": output.afterimage,
        "accounted_field_steps": expected_steps,
        "source_support_count": output.source_support_count,
        "source_result_digest": output.result_digest,
        "execution_mode": execution_mode,
    }
    return E1CommonProbeEC91ProbeReceipt(**values, receipt_digest=_digest(values))


def _synthetic_formation_output(
    handoff: E1CommonProbeEC89RefinementObjectHandoff,
    resolved: E1CommonProbeResolvedSlot,
) -> E1PreparedRealFormationArmResult:
    arm = resolved.binding.formation_arm_id
    enabled = not arm.endswith("formation_ablated")
    state = handoff.initial_state
    audit = E1ConfirmationFormationArmAudit(
        refinement_id=handoff.refinement_id,
        arm_id=arm,
        handoff_digest=e1_handoff_digest_pair(
            resolved.formation_plan.handoff
        ).assignment_digest,
        field_digest=_digest((S1_EC91_FIXTURE_ID, handoff.refinement_id, arm)),
        source_support_count=resolved.formation_plan.handoff.source_event_count,
        assigned_event_count=resolved.formation_plan.handoff.source_event_count,
        resource_budget_error=0.0,
        formation_enabled=enabled,
        history_backreaction_enabled=False,
        state_remained_neutral=not enabled,
    )
    values = {
        "arm_id": arm,
        "refinement_id": handoff.refinement_id,
        "formation_enabled": enabled,
        "initial_field_digest": _initial_field_digest(handoff.initial_field),
        "initial_state_digest": _initial_state_digest(handoff.initial_state),
        "output_state": state,
        "output_state_digest": _digest(_state_payload(state)),
        "audit": audit,
        "input_objects_preserved": True,
        "copied_inputs_used": True,
        "canonical_execution_permitted": False,
        "claims_permitted": False,
    }
    payload = {
        name: value
        for name, value in values.items()
        if name not in {"output_state", "audit"}
    }
    payload["output_state"] = _state_payload(state)
    payload["audit"] = asdict(audit)
    return E1PreparedRealFormationArmResult(
        **values, result_digest=_digest(payload)
    )


def _synthetic_probe_output(
    handoff: E1CommonProbeEC89RefinementObjectHandoff,
    resolved: E1CommonProbeResolvedSlot,
    state_digest: str | None,
    index: int,
) -> E1CommonProbeRealProbeOutput:
    scale = (index + 1) * (4 if handoff.refinement_id == "r4" else 8)
    values = {
        "binding_digest": resolved.binding.binding_digest,
        "terminal_field_digest": _digest(
            (S1_EC91_FIXTURE_ID, handoff.refinement_id, resolved.binding.role_id)
        ),
        "activation": tuple(scale * value for value in (0.01, 0.02, 0.03)),
        "afterimage": tuple(scale * value for value in (0.001, 0.002, 0.003)),
        "field_step_count": len(resolved.probe_plan.proposal_steps),
        "source_support_count": resolved.probe_plan.handoff.source_event_count,
        "frozen_state_digest_before": state_digest,
        "frozen_state_digest_after": state_digest,
        "frozen_state_preserved": True,
        "persistence_performed": False,
        "research_decision_permitted": False,
        "memory_claim_permitted": False,
    }
    return E1CommonProbeRealProbeOutput(**values, result_digest=_digest(values))


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC91SyntheticFixtureResult:
    fixture_id: str
    source_ec89_result_digest: str
    refinement_ids: tuple[str, ...]
    formation_receipt_digests: tuple[tuple[str, tuple[str, ...]], ...]
    probe_receipt_digests: tuple[tuple[str, tuple[str, ...]], ...]
    accounted_budgets: tuple[tuple[str, int, int, int], ...]
    all_routes_exact: bool
    actual_field_steps_executed: int
    wrapper_execution_permitted: bool
    persistence_performed: bool
    ec46_decision_permitted: bool
    claims_permitted: bool
    result_digest: str
    formations: tuple[tuple[E1CommonProbeEC91FormationReceipt, ...], ...] = field(
        repr=False, compare=False
    )
    probes: tuple[tuple[E1CommonProbeEC91ProbeReceipt, ...], ...] = field(
        repr=False, compare=False
    )

    def __post_init__(self) -> None:
        if (
            self.fixture_id != S1_EC91_FIXTURE_ID
            or self.source_ec89_result_digest != S1_EC91_EC89_RESULT_DIGEST
            or self.refinement_ids != ("r4", "r8")
            or len(self.formations) != 2
            or len(self.probes) != 2
            or any(len(items) != 4 for items in self.formations)
            or any(len(items) != 8 for items in self.probes)
            or self.formation_receipt_digests
            != tuple(
                (
                    refinement,
                    tuple(item.receipt_digest for item in receipts),
                )
                for refinement, receipts in zip(
                    self.refinement_ids, self.formations, strict=True
                )
            )
            or self.probe_receipt_digests
            != tuple(
                (
                    refinement,
                    tuple(item.receipt_digest for item in receipts),
                )
                for refinement, receipts in zip(
                    self.refinement_ids, self.probes, strict=True
                )
            )
            or self.accounted_budgets
            != (("r4", 3216, 3200, 6416), ("r8", 6432, 6400, 12832))
            or self.all_routes_exact is not True
            or self.actual_field_steps_executed != 0
            or any(
                value is not False
                for value in (
                    self.wrapper_execution_permitted,
                    self.persistence_performed,
                    self.ec46_decision_permitted,
                    self.claims_permitted,
                )
            )
        ):
            raise E1CommonProbeEC91RefinementReceiptConverterError(
                "S1-EC91 fixture changed or crossed synthetic scope"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"result_digest", "formations", "probes"}
        }
        if self.result_digest != _digest(payload):
            raise E1CommonProbeEC91RefinementReceiptConverterError(
                "S1-EC91 fixture digest changed"
            )


def run_e1_common_probe_ec91_synthetic_fixture(
    handoffs: E1CommonProbeEC89R4R8ObjectHandoffSet,
) -> E1CommonProbeEC91SyntheticFixtureResult:
    """Convert complete synthetic r4/r8 typed outputs with zero field steps."""

    if (
        not isinstance(handoffs, E1CommonProbeEC89R4R8ObjectHandoffSet)
        or handoffs.result_digest != S1_EC91_EC89_RESULT_DIGEST
    ):
        raise E1CommonProbeEC91RefinementReceiptConverterError(
            "S1-EC91 requires the exact EC89 handoff set"
        )
    handoffs.__post_init__()
    formation_sets = []
    probe_sets = []
    routes = dict(S1_EC63_ROLE_STATE_ROUTES)
    for handoff in handoffs.handoffs:
        formations = tuple(
            convert_e1_common_probe_ec91_formation_output(
                handoff, slot, _synthetic_formation_output(handoff, slot)
            )
            for slot in handoff.formation_slots
        )
        states = {item.state_role: item for item in formations}
        probes = []
        for index, slot in enumerate(handoff.resolved_slots):
            state_role = routes[slot.binding.role_id]
            formation = None if state_role is None else states[state_role]
            state_digest = None if formation is None else formation.output_state_digest
            output = _synthetic_probe_output(handoff, slot, state_digest, index)
            probes.append(
                convert_e1_common_probe_ec91_probe_output(
                    handoff, slot, output, formation
                )
            )
        formation_sets.append(formations)
        probe_sets.append(tuple(probes))
    formation_tuple = tuple(formation_sets)
    probe_tuple = tuple(probe_sets)
    values = {
        "fixture_id": S1_EC91_FIXTURE_ID,
        "source_ec89_result_digest": handoffs.result_digest,
        "refinement_ids": tuple(item.refinement_id for item in handoffs.handoffs),
        "formation_receipt_digests": tuple(
            (handoff.refinement_id, tuple(item.receipt_digest for item in receipts))
            for handoff, receipts in zip(handoffs.handoffs, formation_tuple, strict=True)
        ),
        "probe_receipt_digests": tuple(
            (handoff.refinement_id, tuple(item.receipt_digest for item in receipts))
            for handoff, receipts in zip(handoffs.handoffs, probe_tuple, strict=True)
        ),
        "accounted_budgets": tuple(
            (
                handoff.refinement_id,
                sum(item.accounted_field_steps for item in formations),
                sum(item.accounted_field_steps for item in probes),
                sum(item.accounted_field_steps for item in (*formations, *probes)),
            )
            for handoff, formations, probes in zip(
                handoffs.handoffs, formation_tuple, probe_tuple, strict=True
            )
        ),
        "all_routes_exact": all(
            probe.selected_state_role == routes[probe.role_id]
            for probes in probe_tuple
            for probe in probes
        ),
        "actual_field_steps_executed": 0,
        "wrapper_execution_permitted": False,
        "persistence_performed": False,
        "ec46_decision_permitted": False,
        "claims_permitted": False,
    }
    return E1CommonProbeEC91SyntheticFixtureResult(
        **values,
        result_digest=_digest(values),
        formations=formation_tuple,
        probes=probe_tuple,
    )
