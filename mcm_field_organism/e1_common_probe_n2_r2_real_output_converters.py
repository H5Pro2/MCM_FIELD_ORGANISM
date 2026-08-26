"""S1-EC64 pure converters from EC54 outputs to EC63 receipts."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import inspect

from .e1_common_probe_n2_r2_positive_step_receipt_contract import (
    E1PositiveStepFormationReceipt,
    E1PositiveStepProbeReceipt,
    S1_EC63_ROLE_STATE_ROUTES,
)
from .e1_common_probe_n2_r2_object_handoff import E1CommonProbeN2R2ObjectHandoff
from .e1_common_probe_real_wrappers import (
    E1CommonProbeRealProbeOutput,
    E1CommonProbeResolvedSlot,
)
from .e1_confirmation_prepared_real_formation_kernel import (
    E1PreparedRealFormationArmResult,
)
from .e1_confirmation_formation_runner import E1ConfirmationFormationArmAudit
from .e1_handoff_digest_schemas import e1_handoff_digest_pair
from .e1_refined_chain_canonical_producer import (
    _initial_field_digest,
    _initial_state_digest,
)
from .e1_refined_formation_runner import _digest, _state_payload


class E1CommonProbeN2R2RealOutputConverterError(ValueError):
    """Raised when EC64 cannot losslessly bind one real wrapper output."""


S1_EC64_AUDIT_ID = "e1.common-probe-n2-r2-real-output-converters.s1ec64.v1"
S1_EC64_EC63_FIXTURE_DIGEST = (
    "a1dce7d6ee522f5953556bc7ae4b090a21687bece3c23ac07bbc81f68fda400a"
)
S1_EC64_EC59_HANDOFF_DIGEST = (
    "5acf624ffaa209e058b74134a069946e21eb2db6609ad7db8301c2c122bca3cb"
)
S1_EC70_FORMATION_DIAGNOSTIC_GATES = (
    "formation-arm-identity-exact",
    "formation-refinement-identity-exact",
    "formation-runtime-assignment-digest-exact",
    "formation-plan-envelope-digest-exact",
    "formation-source-support-count-exact",
    "formation-plan-step-count-exactly-402",
)


@dataclass(frozen=True, slots=True)
class E1CommonProbeFormationOutputDiagnostic:
    gates: tuple[tuple[str, bool], ...]
    all_passed: bool
    failed_gates: tuple[str, ...]
    diagnostic_digest: str

    def __post_init__(self) -> None:
        if (
            tuple(name for name, _ in self.gates) != S1_EC70_FORMATION_DIAGNOSTIC_GATES
            or self.all_passed is not all(value for _, value in self.gates)
            or self.failed_gates != tuple(name for name, value in self.gates if not value)
            or self.diagnostic_digest != _digest({
                "gates": self.gates,
                "all_passed": self.all_passed,
                "failed_gates": self.failed_gates,
            })
        ):
            raise E1CommonProbeN2R2RealOutputConverterError(
                "S1-EC70 formation diagnostic changed"
            )


def diagnose_e1_common_probe_real_formation_output(
    resolved: E1CommonProbeResolvedSlot,
    output: E1PreparedRealFormationArmResult,
) -> E1CommonProbeFormationOutputDiagnostic:
    """Evaluate five named converter gates without invoking a wrapper."""

    if (
        not isinstance(resolved, E1CommonProbeResolvedSlot)
        or resolved.binding.state_role is None
        or resolved.binding.formation_arm_id is None
        or resolved.formation_plan is None
        or not isinstance(output, E1PreparedRealFormationArmResult)
    ):
        raise E1CommonProbeN2R2RealOutputConverterError(
            "S1-EC70 diagnostic requires one resolved E1 output"
        )
    resolved.__post_init__()
    output.__post_init__()
    handoff_digests = e1_handoff_digest_pair(resolved.formation_plan.handoff)
    gates = (
        ("formation-arm-identity-exact", output.arm_id == resolved.binding.formation_arm_id),
        ("formation-refinement-identity-exact", output.refinement_id == resolved.binding.refinement_id),
        ("formation-runtime-assignment-digest-exact", output.audit.handoff_digest == handoff_digests.assignment_digest),
        ("formation-plan-envelope-digest-exact", resolved.formation_plan.handoff_digest == handoff_digests.envelope_digest),
        ("formation-source-support-count-exact", output.audit.source_support_count == resolved.formation_plan.handoff.source_event_count),
        ("formation-plan-step-count-exactly-402", len(resolved.formation_plan.proposal_steps) == 402),
    )
    values = {
        "gates": gates,
        "all_passed": all(value for _, value in gates),
        "failed_gates": tuple(name for name, value in gates if not value),
    }
    return E1CommonProbeFormationOutputDiagnostic(
        **values,
        diagnostic_digest=_digest(values),
    )


def convert_e1_common_probe_real_formation_output(
    resolved: E1CommonProbeResolvedSlot,
    output: E1PreparedRealFormationArmResult,
) -> E1PositiveStepFormationReceipt:
    """Convert one already-produced formation output without running a wrapper."""

    if (
        not isinstance(resolved, E1CommonProbeResolvedSlot)
        or resolved.binding.state_role is None
        or resolved.binding.formation_arm_id is None
        or resolved.formation_plan is None
        or not isinstance(output, E1PreparedRealFormationArmResult)
    ):
        raise E1CommonProbeN2R2RealOutputConverterError(
            "S1-EC64 formation conversion requires one resolved E1 output"
        )
    diagnostic = diagnose_e1_common_probe_real_formation_output(
        resolved, output
    )
    if not diagnostic.all_passed:
        raise E1CommonProbeN2R2RealOutputConverterError(
            "S1-EC70 formation output failed gates: "
            + ",".join(diagnostic.failed_gates)
        )
    values = {
        "state_role": resolved.binding.state_role,
        "output_state_digest": output.output_state_digest,
        "accounted_field_steps": len(resolved.formation_plan.proposal_steps),
        "source_result_digest": output.result_digest,
        "execution_mode": "real-wrapper",
    }
    return E1PositiveStepFormationReceipt(
        **values,
        output_state=output.output_state,
        receipt_digest=_digest(values),
    )


def convert_e1_common_probe_real_probe_output(
    resolved: E1CommonProbeResolvedSlot,
    output: E1CommonProbeRealProbeOutput,
    formation: E1PositiveStepFormationReceipt | None,
) -> E1PositiveStepProbeReceipt:
    """Convert one already-produced probe output without running a wrapper."""

    if (
        not isinstance(resolved, E1CommonProbeResolvedSlot)
        or not isinstance(output, E1CommonProbeRealProbeOutput)
    ):
        raise E1CommonProbeN2R2RealOutputConverterError(
            "S1-EC64 probe conversion requires resolved EC54 output"
        )
    resolved.__post_init__()
    output.__post_init__()
    expected_role = dict(S1_EC63_ROLE_STATE_ROUTES)[resolved.binding.role_id]
    if expected_role is None:
        selected_digest = None
        if formation is not None:
            raise E1CommonProbeN2R2RealOutputConverterError(
                "S1-EC64 P0 cannot receive a formation receipt"
            )
    else:
        if (
            not isinstance(formation, E1PositiveStepFormationReceipt)
            or formation.state_role != expected_role
            or formation.execution_mode != "real-wrapper"
        ):
            raise E1CommonProbeN2R2RealOutputConverterError(
                "S1-EC64 E1 probe formation route changed"
            )
        formation.__post_init__()
        selected_digest = formation.output_state_digest
    if (
        output.binding_digest != resolved.binding.binding_digest
        or output.field_step_count != len(resolved.probe_plan.proposal_steps)
        or output.field_step_count != 200
        or output.source_support_count != resolved.probe_plan.handoff.source_event_count
        or output.frozen_state_digest_before != selected_digest
        or output.frozen_state_digest_after != selected_digest
        or output.frozen_state_preserved is not True
    ):
        raise E1CommonProbeN2R2RealOutputConverterError(
            "S1-EC64 probe output does not match its slot or state"
        )
    values = {
        "role_id": resolved.binding.role_id,
        "binding_digest": resolved.binding.binding_digest,
        "selected_state_role": expected_role,
        "selected_state_digest": selected_digest,
        "backreaction_enabled": resolved.binding.backreaction_enabled,
        "activation": output.activation,
        "afterimage": output.afterimage,
        "accounted_field_steps": output.field_step_count,
        "source_support_count": output.source_support_count,
        "source_result_digest": output.result_digest,
        "execution_mode": "real-wrapper",
    }
    return E1PositiveStepProbeReceipt(**values, receipt_digest=_digest(values))


@dataclass(frozen=True, slots=True)
class E1CommonProbeN2R2RealOutputConverterAudit:
    audit_id: str
    source_ec63_fixture_digest: str
    converter_names: tuple[str, ...]
    checks: tuple[tuple[str, bool], ...]
    lossless_formation_mapping_implemented: bool
    lossless_probe_mapping_implemented: bool
    typed_conversion_fixture_permitted: bool
    wrapper_execution_permitted: bool
    persistence_permitted: bool
    research_decision_permitted: bool
    memory_claim_permitted: bool
    decision: str
    audit_digest: str

    def __post_init__(self) -> None:
        if (
            self.audit_id != S1_EC64_AUDIT_ID
            or self.source_ec63_fixture_digest != S1_EC64_EC63_FIXTURE_DIGEST
            or self.converter_names != (
                "convert_e1_common_probe_real_formation_output",
                "convert_e1_common_probe_real_probe_output",
            )
            or any(value is not True for _, value in self.checks)
            or any(value is not True for value in (
                self.lossless_formation_mapping_implemented,
                self.lossless_probe_mapping_implemented,
                self.typed_conversion_fixture_permitted,
            ))
            or any(value is not False for value in (
                self.wrapper_execution_permitted,
                self.persistence_permitted,
                self.research_decision_permitted,
                self.memory_claim_permitted,
            ))
            or self.decision != "REAL_OUTPUT_CONVERTERS_IMPLEMENTED_TYPED_FIXTURE_AVAILABLE"
        ):
            raise E1CommonProbeN2R2RealOutputConverterError(
                "S1-EC64 audit changed or released wrapper execution"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "audit_digest"
        }
        if self.audit_digest != _digest(payload):
            raise E1CommonProbeN2R2RealOutputConverterError(
                "S1-EC64 audit digest changed"
            )


def audit_e1_common_probe_n2_r2_real_output_converters(
) -> E1CommonProbeN2R2RealOutputConverterAudit:
    """Audit converter signatures and source without invoking either converter."""

    formation_source = inspect.getsource(convert_e1_common_probe_real_formation_output)
    probe_source = inspect.getsource(convert_e1_common_probe_real_probe_output)
    checks = (
        ("formation-converter-signature-exact", tuple(inspect.signature(convert_e1_common_probe_real_formation_output).parameters) == ("resolved", "output")),
        ("probe-converter-signature-exact", tuple(inspect.signature(convert_e1_common_probe_real_probe_output).parameters) == ("resolved", "output", "formation")),
        ("formation-converter-binds-state-step-and-source", all(token in formation_source for token in ("output.output_state", "output.output_state_digest", "len(resolved.formation_plan.proposal_steps)", "output.result_digest"))),
        ("probe-converter-binds-observations-step-support-and-source", all(token in probe_source for token in ("output.activation", "output.afterimage", "output.field_step_count", "output.source_support_count", "output.result_digest"))),
        ("converters-bind-real-wrapper-mode", '"real-wrapper"' in formation_source and '"real-wrapper"' in probe_source),
        ("converters-have-no-wrapper-kernel-or-write-call", all(token not in source for source in (formation_source, probe_source) for token in ("run_e1_common_probe_real_formation_wrapper(", "run_e1_common_probe_real_probe_wrapper(", "write_text", "write_bytes", "open("))),
    )
    values = {
        "audit_id": S1_EC64_AUDIT_ID,
        "source_ec63_fixture_digest": S1_EC64_EC63_FIXTURE_DIGEST,
        "converter_names": (
            "convert_e1_common_probe_real_formation_output",
            "convert_e1_common_probe_real_probe_output",
        ),
        "checks": checks,
        "lossless_formation_mapping_implemented": True,
        "lossless_probe_mapping_implemented": True,
        "typed_conversion_fixture_permitted": True,
        "wrapper_execution_permitted": False,
        "persistence_permitted": False,
        "research_decision_permitted": False,
        "memory_claim_permitted": False,
        "decision": "REAL_OUTPUT_CONVERTERS_IMPLEMENTED_TYPED_FIXTURE_AVAILABLE",
    }
    return E1CommonProbeN2R2RealOutputConverterAudit(
        **values,
        audit_digest=_digest(values),
    )


@dataclass(frozen=True, slots=True)
class E1CommonProbeN2R2TypedConversionFixtureResult:
    fixture_id: str
    source_handoff_digest: str
    formation_count: int
    probe_count: int
    formation_receipt_digests: tuple[str, ...]
    probe_receipt_digests: tuple[str, ...]
    accounted_formation_steps: int
    accounted_probe_steps: int
    accounted_total_steps: int
    actual_field_steps_executed: int
    all_formation_fields_lossless: bool
    all_probe_fields_lossless: bool
    wrapper_execution_permitted: bool
    persistence_performed: bool
    research_decision_permitted: bool
    memory_claim_permitted: bool
    result_digest: str
    formations: tuple[E1PositiveStepFormationReceipt, ...] = field(repr=False, compare=False)
    probes: tuple[E1PositiveStepProbeReceipt, ...] = field(repr=False, compare=False)

    def __post_init__(self) -> None:
        metadata = _typed_fixture_metadata(self)
        if (
            self.fixture_id != "e1.common-probe-n2-r2-typed-conversion-fixture.s1ec64.v1"
            or self.source_handoff_digest != S1_EC64_EC59_HANDOFF_DIGEST
            or (self.formation_count, self.probe_count) != (4, 8)
            or self.formation_receipt_digests != tuple(item.receipt_digest for item in self.formations)
            or self.probe_receipt_digests != tuple(item.receipt_digest for item in self.probes)
            or (self.accounted_formation_steps, self.accounted_probe_steps, self.accounted_total_steps) != (1608, 1600, 3208)
            or self.actual_field_steps_executed != 0
            or self.all_formation_fields_lossless is not True
            or self.all_probe_fields_lossless is not True
            or any(value is not False for value in (
                self.wrapper_execution_permitted,
                self.persistence_performed,
                self.research_decision_permitted,
                self.memory_claim_permitted,
            ))
            or self.result_digest != _digest(metadata)
        ):
            raise E1CommonProbeN2R2RealOutputConverterError(
                "S1-EC64 typed fixture changed or crossed synthetic scope"
            )


def _typed_fixture_metadata(
    result: E1CommonProbeN2R2TypedConversionFixtureResult,
) -> dict[str, object]:
    return {
        name: getattr(result, name)
        for name in (
            "fixture_id",
            "source_handoff_digest",
            "formation_count",
            "probe_count",
            "formation_receipt_digests",
            "probe_receipt_digests",
            "accounted_formation_steps",
            "accounted_probe_steps",
            "accounted_total_steps",
            "actual_field_steps_executed",
            "all_formation_fields_lossless",
            "all_probe_fields_lossless",
            "wrapper_execution_permitted",
            "persistence_performed",
            "research_decision_permitted",
            "memory_claim_permitted",
        )
    }


def _synthetic_typed_formation_output(
    handoff: E1CommonProbeN2R2ObjectHandoff,
    resolved: E1CommonProbeResolvedSlot,
) -> E1PreparedRealFormationArmResult:
    arm = resolved.binding.formation_arm_id
    enabled = not arm.endswith("formation_ablated")
    state = handoff.initial_state
    audit = E1ConfirmationFormationArmAudit(
        refinement_id="r2",
        arm_id=arm,
        handoff_digest=e1_handoff_digest_pair(
            resolved.formation_plan.handoff
        ).assignment_digest,
        field_digest=_digest(("synthetic-typed-output", arm, "field")),
        source_support_count=resolved.formation_plan.handoff.source_event_count,
        assigned_event_count=resolved.formation_plan.handoff.source_event_count,
        resource_budget_error=0.0,
        formation_enabled=enabled,
        history_backreaction_enabled=False,
        state_remained_neutral=not enabled,
    )
    values = {
        "arm_id": arm,
        "refinement_id": "r2",
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
    payload = {name: value for name, value in values.items() if name not in {"output_state", "audit"}}
    payload["output_state"] = _state_payload(state)
    payload["audit"] = asdict(audit)
    return E1PreparedRealFormationArmResult(**values, result_digest=_digest(payload))


def _synthetic_typed_probe_output(
    resolved: E1CommonProbeResolvedSlot,
    state_digest: str | None,
    index: int,
) -> E1CommonProbeRealProbeOutput:
    activation = tuple((index + 1) * value for value in (0.01, 0.02, 0.03))
    afterimage = tuple((index + 1) * value for value in (0.001, 0.002, 0.003))
    values = {
        "binding_digest": resolved.binding.binding_digest,
        "terminal_field_digest": _digest(("synthetic-typed-output", resolved.binding.role_id, "field")),
        "activation": activation,
        "afterimage": afterimage,
        "field_step_count": 200,
        "source_support_count": resolved.probe_plan.handoff.source_event_count,
        "frozen_state_digest_before": state_digest,
        "frozen_state_digest_after": state_digest,
        "frozen_state_preserved": True,
        "persistence_performed": False,
        "research_decision_permitted": False,
        "memory_claim_permitted": False,
    }
    return E1CommonProbeRealProbeOutput(**values, result_digest=_digest(values))


def run_e1_common_probe_n2_r2_typed_conversion_fixture(
    handoff: E1CommonProbeN2R2ObjectHandoff,
) -> E1CommonProbeN2R2TypedConversionFixtureResult:
    """Convert synthetic typed EC54 outputs without invoking any wrapper."""

    if (
        not isinstance(handoff, E1CommonProbeN2R2ObjectHandoff)
        or handoff.handoff_digest != S1_EC64_EC59_HANDOFF_DIGEST
    ):
        raise E1CommonProbeN2R2RealOutputConverterError(
            "S1-EC64 fixture requires the exact EC59 handoff"
        )
    handoff.__post_init__()
    formations = tuple(
        convert_e1_common_probe_real_formation_output(
            slot, _synthetic_typed_formation_output(handoff, slot)
        )
        for slot in handoff.formation_slots
    )
    states = {item.state_role: item for item in formations}
    probes = []
    source_outputs = []
    routes = dict(S1_EC63_ROLE_STATE_ROUTES)
    for index, slot in enumerate(handoff.resolved_slots):
        state_role = routes[slot.binding.role_id]
        formation = None if state_role is None else states[state_role]
        state_digest = None if formation is None else formation.output_state_digest
        output = _synthetic_typed_probe_output(slot, state_digest, index)
        source_outputs.append(output)
        probes.append(convert_e1_common_probe_real_probe_output(slot, output, formation))
    values = {
        "fixture_id": "e1.common-probe-n2-r2-typed-conversion-fixture.s1ec64.v1",
        "source_handoff_digest": handoff.handoff_digest,
        "formation_count": len(formations),
        "probe_count": len(probes),
        "formation_receipt_digests": tuple(item.receipt_digest for item in formations),
        "probe_receipt_digests": tuple(item.receipt_digest for item in probes),
        "accounted_formation_steps": sum(item.accounted_field_steps for item in formations),
        "accounted_probe_steps": sum(item.accounted_field_steps for item in probes),
        "accounted_total_steps": sum(item.accounted_field_steps for item in (*formations, *probes)),
        "actual_field_steps_executed": 0,
        "all_formation_fields_lossless": all(item.execution_mode == "real-wrapper" and item.accounted_field_steps == 402 for item in formations),
        "all_probe_fields_lossless": all(
            receipt.activation == output.activation
            and receipt.afterimage == output.afterimage
            and receipt.source_support_count == output.source_support_count
            and receipt.source_result_digest == output.result_digest
            for receipt, output in zip(probes, source_outputs, strict=True)
        ),
        "wrapper_execution_permitted": False,
        "persistence_performed": False,
        "research_decision_permitted": False,
        "memory_claim_permitted": False,
    }
    return E1CommonProbeN2R2TypedConversionFixtureResult(
        **values,
        result_digest=_digest(values),
        formations=formations,
        probes=tuple(probes),
    )
