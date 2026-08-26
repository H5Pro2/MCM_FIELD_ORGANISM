"""S1-GE private fixed-adapter wrapper shell behind a zero-batch gate."""

from __future__ import annotations

from dataclasses import dataclass, field

from .e1_formation_s1gd_fixed_adapter_invocation_binding import (
    E1FormationS1GDFixedAdapterInvocation,
    E1FormationS1GDFixedAdapterInvocationBindingResult,
)
from .e1_refined_formation_runner import _digest, _state_payload
from .e1_formation_s1fw_synthetic_live_state_handoff import _adapter_digest


class E1FormationS1GEFixedAdapterNullBatchShellError(ValueError):
    """Raised when the S1-GE shell receives work or opens a field path."""


S1_GE_SHELL_ID = "e1.fixed-adapter-nullbatch-shell.s1ge.v1"
S1_GE_GATE_ID = "e1.synthetic-zero-batch-gate.s1ge.v1"


@dataclass(frozen=True, slots=True)
class E1FormationS1GESyntheticNullBatchGate:
    gate_id: str
    synthetic: bool
    batch_count: int
    field_object_present: bool
    observed_payload_present: bool
    positive_plan_consumption_permitted: bool
    kernel_call_permitted: bool
    gate_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "gate_digest"
        }
        if (
            self.gate_id != S1_GE_GATE_ID
            or self.synthetic is not True
            or self.batch_count != 0
            or any(
                value is not False
                for value in (
                    self.field_object_present,
                    self.observed_payload_present,
                    self.positive_plan_consumption_permitted,
                    self.kernel_call_permitted,
                )
            )
            or self.gate_digest != _digest(payload)
        ):
            raise E1FormationS1GEFixedAdapterNullBatchShellError(
                "S1-GE gate is not a closed synthetic zero-batch gate"
            )


def build_e1_formation_s1ge_synthetic_nullbatch_gate(
) -> E1FormationS1GESyntheticNullBatchGate:
    """Create the only gate accepted by the S1-GE shell."""

    values = {
        "gate_id": S1_GE_GATE_ID,
        "synthetic": True,
        "batch_count": 0,
        "field_object_present": False,
        "observed_payload_present": False,
        "positive_plan_consumption_permitted": False,
        "kernel_call_permitted": False,
    }
    return E1FormationS1GESyntheticNullBatchGate(
        **values,
        gate_digest=_digest(values),
    )


@dataclass(frozen=True, slots=True)
class E1FormationS1GENullBatchValidationOutput:
    shell_id: str
    source_invocation_digest: str
    gate_digest: str
    binding_digest: str
    context_digest: str
    source_state_digest: str
    fixed_adapter_digest: str
    input_validation_complete: bool
    batch_count: int
    field_steps_executed: int
    field_object_constructed: bool
    kernel_called: bool
    observed_vectors_present: bool
    probe_output_emitted: bool
    receipt_emitted: bool
    persistence_performed: bool
    claims_permitted: bool
    output_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "output_digest"
        }
        if (
            self.shell_id != S1_GE_SHELL_ID
            or any(
                len(value) != 64
                for value in (
                    self.source_invocation_digest,
                    self.gate_digest,
                    self.binding_digest,
                    self.context_digest,
                    self.source_state_digest,
                    self.fixed_adapter_digest,
                )
            )
            or self.input_validation_complete is not True
            or self.batch_count != 0
            or self.field_steps_executed != 0
            or any(
                value is not False
                for value in (
                    self.field_object_constructed,
                    self.kernel_called,
                    self.observed_vectors_present,
                    self.probe_output_emitted,
                    self.receipt_emitted,
                    self.persistence_performed,
                    self.claims_permitted,
                )
            )
            or self.output_digest != _digest(payload)
        ):
            raise E1FormationS1GEFixedAdapterNullBatchShellError(
                "S1-GE validation output contains work or observed data"
            )


def validate_e1_formation_s1ge_fixed_adapter_nullbatch(
    invocation: E1FormationS1GDFixedAdapterInvocation,
    gate: E1FormationS1GESyntheticNullBatchGate,
) -> E1FormationS1GENullBatchValidationOutput:
    """Validate one invocation without reading its positive plan or a field."""

    if not isinstance(invocation, E1FormationS1GDFixedAdapterInvocation):
        raise E1FormationS1GEFixedAdapterNullBatchShellError(
            "S1-GE requires one typed S1-GD invocation"
        )
    if not isinstance(gate, E1FormationS1GESyntheticNullBatchGate):
        raise E1FormationS1GEFixedAdapterNullBatchShellError(
            "S1-GE requires the typed nullbatch gate"
        )
    invocation.__post_init__()
    gate.__post_init__()
    if (
        invocation.source_state_digest
        != _digest(_state_payload(invocation.source_state))
        or invocation.fixed_adapter_digest != _adapter_digest(invocation.fixed_adapter)
        or invocation.context.binding is not invocation.handoff.binding
        or invocation.source_state is not invocation.handoff.state
        or invocation.fixed_adapter is not invocation.handoff.fixed_adapter
        or gate.batch_count != 0
        or gate.field_object_present is not False
        or gate.positive_plan_consumption_permitted is not False
        or gate.kernel_call_permitted is not False
    ):
        raise E1FormationS1GEFixedAdapterNullBatchShellError(
            "S1-GE invocation or nullbatch gate changed"
        )
    values = {
        "shell_id": S1_GE_SHELL_ID,
        "source_invocation_digest": invocation.invocation_digest,
        "gate_digest": gate.gate_digest,
        "binding_digest": invocation.binding_digest,
        "context_digest": invocation.context_digest,
        "source_state_digest": invocation.source_state_digest,
        "fixed_adapter_digest": invocation.fixed_adapter_digest,
        "input_validation_complete": True,
        "batch_count": 0,
        "field_steps_executed": 0,
        "field_object_constructed": False,
        "kernel_called": False,
        "observed_vectors_present": False,
        "probe_output_emitted": False,
        "receipt_emitted": False,
        "persistence_performed": False,
        "claims_permitted": False,
    }
    return E1FormationS1GENullBatchValidationOutput(
        **values,
        output_digest=_digest(values),
    )


@dataclass(frozen=True, slots=True)
class E1FormationS1GENullBatchShellResult:
    shell_id: str
    source_s1gd_result_digest: str
    gate_digest: str
    outputs: tuple[E1FormationS1GENullBatchValidationOutput, ...] = field(
        repr=False
    )
    output_digests: tuple[str, ...]
    validated_invocation_count: int
    all_six_inputs_validated: bool
    any_positive_plan_consumed: bool
    field_objects_constructed: int
    kernel_calls: int
    field_steps_executed: int
    observed_outputs_emitted: int
    persistence_performed: bool
    execution_permitted: bool
    claims_permitted: bool
    decision: str
    reason: str
    result_digest: str

    def __post_init__(self) -> None:
        outputs = tuple(self.outputs)
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"outputs", "result_digest"}
        }
        if (
            self.shell_id != S1_GE_SHELL_ID
            or len(self.source_s1gd_result_digest) != 64
            or len(self.gate_digest) != 64
            or len(outputs) != 6
            or self.output_digests != tuple(item.output_digest for item in outputs)
            or self.validated_invocation_count != 6
            or self.all_six_inputs_validated is not True
            or self.any_positive_plan_consumed is not False
            or any(
                value != 0
                for value in (
                    self.field_objects_constructed,
                    self.kernel_calls,
                    self.field_steps_executed,
                    self.observed_outputs_emitted,
                )
            )
            or any(
                value is not False
                for value in (
                    self.persistence_performed,
                    self.execution_permitted,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "FIXED_ADAPTER_NULLBATCH_SHELL_VALIDATED_POSITIVE_PATH_CLOSED"
            or not self.reason
            or self.result_digest != _digest(payload)
        ):
            raise E1FormationS1GEFixedAdapterNullBatchShellError(
                "S1-GE shell result changed or opened positive work"
            )
        object.__setattr__(self, "outputs", outputs)


def validate_all_e1_formation_s1ge_fixed_adapter_nullbatches(
    bindings: E1FormationS1GDFixedAdapterInvocationBindingResult,
    gate: E1FormationS1GESyntheticNullBatchGate,
) -> E1FormationS1GENullBatchShellResult:
    """Validate all six invocations atomically through the zero-batch shell."""

    if not isinstance(bindings, E1FormationS1GDFixedAdapterInvocationBindingResult):
        raise E1FormationS1GEFixedAdapterNullBatchShellError(
            "S1-GE requires the typed S1-GD aggregate"
        )
    bindings.__post_init__()
    if bindings.wrapper_implementation_permitted is not False:
        raise E1FormationS1GEFixedAdapterNullBatchShellError(
            "S1-GE requires the closed S1-GD wrapper path"
        )
    pending = tuple(
        validate_e1_formation_s1ge_fixed_adapter_nullbatch(item, gate)
        for item in bindings.invocations
    )
    values = {
        "shell_id": S1_GE_SHELL_ID,
        "source_s1gd_result_digest": bindings.result_digest,
        "gate_digest": gate.gate_digest,
        "outputs": pending,
        "output_digests": tuple(item.output_digest for item in pending),
        "validated_invocation_count": len(pending),
        "all_six_inputs_validated": len(pending) == 6,
        "any_positive_plan_consumed": False,
        "field_objects_constructed": 0,
        "kernel_calls": 0,
        "field_steps_executed": 0,
        "observed_outputs_emitted": 0,
        "persistence_performed": False,
        "execution_permitted": False,
        "claims_permitted": False,
        "decision": (
            "FIXED_ADAPTER_NULLBATCH_SHELL_VALIDATED_POSITIVE_PATH_CLOSED"
        ),
        "reason": (
            "six-invocation-input-sets-validated-through-zero-batch-gate;"
            "no-plan-field-kernel-output-or-receipt-consumed-or-created"
        ),
    }
    payload = {name: value for name, value in values.items() if name != "outputs"}
    return E1FormationS1GENullBatchShellResult(
        **values,
        result_digest=_digest(payload),
    )
