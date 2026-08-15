"""Private pure S1-JF two-node common S/H boundary fixture and operator."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
import hashlib
import json

from .dynamic_substrate_s1je_finite_pih_boundary_fixture_contract import (
    S1_JE_BOUNDARY_FIXTURE,
    build_dts1_s1je_finite_pih_boundary_fixture_contract,
)
from .mcm_neuron import MCMNeuronValidationError
from .mcm_neuron_layer import MCMNeuronLayerError
from .mcm_substrate_state import (
    MCMSubstrateStateError,
    mcm_substrate_edge_inventory,
)
from .shared_mcm_field import SharedMCMField, SharedMCMFieldError


class DTS1CommonBoundary2NError(ValueError):
    """Raised before output when the two-node boundary is invalid."""


S1_JF_IMPLEMENTATION_ID = "dynamic-substrate.pure-common-boundary-2n.s1jf.v1"
S1_JF_SOURCE_S1JE_DIGEST = (
    "b1da58d2e2e1d6e6e7df1275a5fb6d51221f10866f746f18a7224ecccb745aae"
)
S1_JF_MATRIX_CASE_IDS = tuple(f"T{index:02d}" for index in range(1, 12))
S1_JF_DECISION = "PRIVATE_PURE_TWO_NODE_COMMON_SH_BOUNDARY_IMPLEMENTED_TECHNICALLY_ACCEPTED"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


_FIXTURE_VALUES = dict(S1_JE_BOUNDARY_FIXTURE)


@dataclass(frozen=True, slots=True)
class DTS1CommonBoundary2NFixture:
    """The one immutable canonical S1-JE two-node fixture."""

    role: str
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    expected_participation: tuple[float, ...]

    def __post_init__(self) -> None:
        expected = (
            _FIXTURE_VALUES["role"],
            _FIXTURE_VALUES["S"],
            _FIXTURE_VALUES["H"],
            _FIXTURE_VALUES["expected_S1_HK_participation"],
        )
        values = (
            self.role,
            tuple(self.activation),
            tuple(self.afterimage),
            tuple(self.expected_participation),
        )
        if values != expected:
            raise DTS1CommonBoundary2NError(
                "two-node boundary fixture must equal the complete S1-JE registration"
            )
        object.__setattr__(self, "activation", values[1])
        object.__setattr__(self, "afterimage", values[2])
        object.__setattr__(self, "expected_participation", values[3])

    def canonical_payload(self) -> dict[str, object]:
        return {
            "role": self.role,
            "activation": self.activation,
            "afterimage": self.afterimage,
            "expected_participation": self.expected_participation,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


S1_JF_BOUNDARY_FIXTURE = DTS1CommonBoundary2NFixture(
    _FIXTURE_VALUES["role"],
    _FIXTURE_VALUES["S"],
    _FIXTURE_VALUES["H"],
    _FIXTURE_VALUES["expected_S1_HK_participation"],
)


def canonical_dts1_common_boundary_2n_fixture() -> DTS1CommonBoundary2NFixture:
    """Return the immutable private fixture without applying it."""

    return S1_JF_BOUNDARY_FIXTURE


def _canonical_two_node_order(field: SharedMCMField) -> tuple[str, ...]:
    if not isinstance(field, SharedMCMField):
        raise DTS1CommonBoundary2NError(
            "two-node boundary input must be one complete shared field"
        )
    neurons = tuple(sorted(field.layer.neurons, key=lambda item: item.position))
    if len(neurons) != 2 or any(len(item.position) != 1 for item in neurons):
        raise DTS1CommonBoundary2NError(
            "two-node boundary field must have one-dimensional width two"
        )
    if neurons[1].position[0] - neurons[0].position[0] != 1:
        raise DTS1CommonBoundary2NError(
            "two-node boundary positions must form one contiguous open line"
        )
    node_ids = tuple(item.neuron_id for item in neurons)
    expected_edge = (tuple(sorted(node_ids)),)
    try:
        actual_edges = mcm_substrate_edge_inventory(field.layer)
    except MCMSubstrateStateError as exc:
        raise DTS1CommonBoundary2NError(str(exc)) from exc
    if actual_edges != expected_edge:
        raise DTS1CommonBoundary2NError(
            "two-node boundary field must have exactly one open-line edge"
        )
    return node_ids


def apply_dts1_common_sh_boundary_2n(
    field: SharedMCMField,
    boundary_role: str,
) -> SharedMCMField:
    """Replace only two-node S/H using S1-JE; consume no model time."""

    node_ids = _canonical_two_node_order(field)
    if boundary_role != S1_JF_BOUNDARY_FIXTURE.role or not isinstance(
        boundary_role, str
    ):
        raise DTS1CommonBoundary2NError(
            "two-node boundary role must be exactly A_BOUNDARY_2N"
        )
    activation_by_id = dict(
        zip(node_ids, S1_JF_BOUNDARY_FIXTURE.activation, strict=True)
    )
    afterimage_by_id = dict(
        zip(node_ids, S1_JF_BOUNDARY_FIXTURE.afterimage, strict=True)
    )
    try:
        neurons = tuple(
            replace(
                neuron,
                activation=activation_by_id[neuron.neuron_id],
                afterimage=afterimage_by_id[neuron.neuron_id],
            )
            for neuron in field.layer.neurons
        )
        output = replace(field, layer=replace(field.layer, neurons=neurons))
    except (MCMNeuronValidationError, MCMNeuronLayerError, SharedMCMFieldError) as exc:
        raise DTS1CommonBoundary2NError(str(exc)) from exc
    if (
        output.docks != field.docks
        or output.last_distribution is not field.last_distribution
        or output.substrate is not field.substrate
        or output.development is not field.development
        or output.layer.sample_offsets != field.layer.sample_offsets
        or output.layer.periodic_axes != field.layer.periodic_axes
        or output.layer.receptor_dock_ids != field.layer.receptor_dock_ids
    ):
        raise DTS1CommonBoundary2NError(
            "two-node boundary changed a non-S/H field component"
        )
    return output


@dataclass(frozen=True, slots=True)
class DTS1S1JFImplementationReceipt:
    implementation_id: str
    source_s1je_digest: str
    matrix_case_ids: tuple[str, ...]
    canonical_fixture_count: int
    pure_two_node_boundary_implemented: bool
    exact_two_node_geometry_required: bool
    non_sh_field_state_preserved: bool
    three_node_s1iz_operator_changed: bool
    external_dts1_anatomy_reachable: bool
    external_b1_adapter_reachable: bool
    model_kernel_import_present: bool
    resource_step_import_present: bool
    runtime_integration_present: bool
    baseline_models_executed: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    common_interval_envelope_contract_authorized_next_stage: bool
    decision: str
    receipt_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "receipt_digest"
        }
        if (
            self.implementation_id != S1_JF_IMPLEMENTATION_ID
            or self.source_s1je_digest != S1_JF_SOURCE_S1JE_DIGEST
            or self.matrix_case_ids != S1_JF_MATRIX_CASE_IDS
            or self.canonical_fixture_count != 1
            or any(
                value is not True
                for value in (
                    self.pure_two_node_boundary_implemented,
                    self.exact_two_node_geometry_required,
                    self.non_sh_field_state_preserved,
                    self.common_interval_envelope_contract_authorized_next_stage,
                )
            )
            or any(
                value is not False
                for value in (
                    self.three_node_s1iz_operator_changed,
                    self.external_dts1_anatomy_reachable,
                    self.external_b1_adapter_reachable,
                    self.model_kernel_import_present,
                    self.resource_step_import_present,
                    self.runtime_integration_present,
                    self.baseline_models_executed,
                    self.research_execution_permitted,
                )
            )
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.decision != S1_JF_DECISION
            or self.receipt_digest != _digest(payload)
        ):
            raise DTS1CommonBoundary2NError("S1-JF implementation receipt weakened")


def build_dts1_s1jf_implementation_receipt() -> DTS1S1JFImplementationReceipt:
    """Return static S1-JF acceptance without applying a boundary."""

    source = build_dts1_s1je_finite_pih_boundary_fixture_contract()
    values = {
        "implementation_id": S1_JF_IMPLEMENTATION_ID,
        "source_s1je_digest": source.contract_digest,
        "matrix_case_ids": S1_JF_MATRIX_CASE_IDS,
        "canonical_fixture_count": 1,
        "pure_two_node_boundary_implemented": True,
        "exact_two_node_geometry_required": True,
        "non_sh_field_state_preserved": True,
        "three_node_s1iz_operator_changed": False,
        "external_dts1_anatomy_reachable": False,
        "external_b1_adapter_reachable": False,
        "model_kernel_import_present": False,
        "resource_step_import_present": False,
        "runtime_integration_present": False,
        "baseline_models_executed": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "common_interval_envelope_contract_authorized_next_stage": True,
        "decision": S1_JF_DECISION,
    }
    return DTS1S1JFImplementationReceipt(**values, receipt_digest=_digest(values))
