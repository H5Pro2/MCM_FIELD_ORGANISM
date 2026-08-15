"""Private pure S1-IZ common S/H boundary fixtures and operator."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
import hashlib
import json

from .dynamic_substrate_s1iy_finite_boundary_fixture_contract import (
    S1_IY_BOUNDARY_FIXTURES,
    build_dts1_s1iy_finite_boundary_fixture_contract,
)
from .mcm_neuron import MCMNeuronValidationError
from .mcm_neuron_layer import MCMNeuronLayerError
from .mcm_substrate_state import (
    MCMSubstrateStateError,
    mcm_substrate_edge_inventory,
)
from .shared_mcm_field import SharedMCMField, SharedMCMFieldError


class DTS1CommonBoundaryError(ValueError):
    """Raised before output when one common S/H boundary is invalid."""


S1_IZ_IMPLEMENTATION_ID = "dynamic-substrate.pure-common-boundary.s1iz.v1"
S1_IZ_SOURCE_S1IY_DIGEST = (
    "86ce6d3837fce14fa1cf4452ea58f37f17d38ff4da13a7fb8213e6950cccf73d"
)
S1_IZ_MATRIX_CASE_IDS = tuple(f"T{index:02d}" for index in range(1, 15))
S1_IZ_DECISION = "PRIVATE_PURE_COMMON_SH_BOUNDARY_IMPLEMENTED_TECHNICALLY_ACCEPTED"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _expected_fixture(role: str) -> tuple[
    str, tuple[float, ...], tuple[float, ...], tuple[float, ...]
]:
    if not isinstance(role, str):
        raise DTS1CommonBoundaryError("boundary role must be one exact string")
    matches = tuple(item for item in S1_IY_BOUNDARY_FIXTURES if item[0] == role)
    if len(matches) != 1:
        raise DTS1CommonBoundaryError("boundary role is not registered by S1-IY")
    return matches[0]


@dataclass(frozen=True, slots=True)
class DTS1CommonBoundaryFixture:
    """One immutable canonical S1-IY boundary fixture."""

    role: str
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    expected_participation: tuple[float, ...]

    def __post_init__(self) -> None:
        expected = _expected_fixture(self.role)
        values = (
            self.role,
            tuple(self.activation),
            tuple(self.afterimage),
            tuple(self.expected_participation),
        )
        if values != expected:
            raise DTS1CommonBoundaryError(
                "boundary fixture must equal one complete S1-IY registration"
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


S1_IZ_BOUNDARY_FIXTURES = tuple(
    DTS1CommonBoundaryFixture(*values) for values in S1_IY_BOUNDARY_FIXTURES
)


def canonical_dts1_common_boundary_fixtures() -> tuple[DTS1CommonBoundaryFixture, ...]:
    """Return the four immutable private fixtures without applying a boundary."""

    return S1_IZ_BOUNDARY_FIXTURES


def _canonical_three_node_order(field: SharedMCMField) -> tuple[str, ...]:
    if not isinstance(field, SharedMCMField):
        raise DTS1CommonBoundaryError("boundary input must be one complete shared field")
    neurons = tuple(sorted(field.layer.neurons, key=lambda item: item.position))
    if len(neurons) != 3 or any(len(item.position) != 1 for item in neurons):
        raise DTS1CommonBoundaryError(
            "boundary field must be one three-node one-dimensional geometry"
        )
    positions = tuple(item.position[0] for item in neurons)
    if positions[1] - positions[0] != 1 or positions[2] - positions[1] != 1:
        raise DTS1CommonBoundaryError(
            "boundary field positions must be one contiguous open line"
        )
    node_ids = tuple(item.neuron_id for item in neurons)
    expected_edges = tuple(
        sorted(
            (
                tuple(sorted((node_ids[0], node_ids[1]))),
                tuple(sorted((node_ids[1], node_ids[2]))),
            )
        )
    )
    try:
        actual_edges = mcm_substrate_edge_inventory(field.layer)
    except MCMSubstrateStateError as exc:
        raise DTS1CommonBoundaryError(str(exc)) from exc
    if actual_edges != expected_edges:
        raise DTS1CommonBoundaryError(
            "boundary field must have exactly the open-line A/B edge inventory"
        )
    return node_ids


def apply_dts1_common_sh_boundary(
    field: SharedMCMField,
    boundary_role: str,
) -> SharedMCMField:
    """Replace only S/H using one S1-IY fixture; consume no model time."""

    node_ids = _canonical_three_node_order(field)
    expected = _expected_fixture(boundary_role)
    fixture = next(item for item in S1_IZ_BOUNDARY_FIXTURES if item.role == expected[0])
    activation_by_id = dict(zip(node_ids, fixture.activation, strict=True))
    afterimage_by_id = dict(zip(node_ids, fixture.afterimage, strict=True))
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
        raise DTS1CommonBoundaryError(str(exc)) from exc
    if (
        output.docks != field.docks
        or output.last_distribution is not field.last_distribution
        or output.substrate is not field.substrate
        or output.development is not field.development
        or output.layer.sample_offsets != field.layer.sample_offsets
        or output.layer.periodic_axes != field.layer.periodic_axes
        or output.layer.receptor_dock_ids != field.layer.receptor_dock_ids
    ):
        raise DTS1CommonBoundaryError("boundary changed a non-S/H field component")
    return output


@dataclass(frozen=True, slots=True)
class DTS1S1IZImplementationReceipt:
    implementation_id: str
    source_s1iy_digest: str
    matrix_case_ids: tuple[str, ...]
    canonical_fixture_count: int
    pure_boundary_operator_implemented: bool
    exact_three_node_geometry_required: bool
    non_sh_field_state_preserved: bool
    external_dts1_anatomy_reachable: bool
    external_b1_adapter_reachable: bool
    model_kernel_import_present: bool
    resource_step_import_present: bool
    runtime_integration_present: bool
    baseline_models_executed: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    finite_adapter_configuration_contract_authorized_next_stage: bool
    decision: str
    receipt_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "receipt_digest"
        }
        if (
            self.implementation_id != S1_IZ_IMPLEMENTATION_ID
            or self.source_s1iy_digest != S1_IZ_SOURCE_S1IY_DIGEST
            or self.matrix_case_ids != S1_IZ_MATRIX_CASE_IDS
            or self.canonical_fixture_count != 4
            or any(
                value is not True
                for value in (
                    self.pure_boundary_operator_implemented,
                    self.exact_three_node_geometry_required,
                    self.non_sh_field_state_preserved,
                    self.finite_adapter_configuration_contract_authorized_next_stage,
                )
            )
            or any(
                value is not False
                for value in (
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
            or self.decision != S1_IZ_DECISION
            or self.receipt_digest != _digest(payload)
        ):
            raise DTS1CommonBoundaryError("S1-IZ implementation receipt weakened")


def build_dts1_s1iz_implementation_receipt() -> DTS1S1IZImplementationReceipt:
    """Return static S1-IZ acceptance without applying a boundary."""

    source = build_dts1_s1iy_finite_boundary_fixture_contract()
    values = {
        "implementation_id": S1_IZ_IMPLEMENTATION_ID,
        "source_s1iy_digest": source.contract_digest,
        "matrix_case_ids": S1_IZ_MATRIX_CASE_IDS,
        "canonical_fixture_count": len(S1_IZ_BOUNDARY_FIXTURES),
        "pure_boundary_operator_implemented": True,
        "exact_three_node_geometry_required": True,
        "non_sh_field_state_preserved": True,
        "external_dts1_anatomy_reachable": False,
        "external_b1_adapter_reachable": False,
        "model_kernel_import_present": False,
        "resource_step_import_present": False,
        "runtime_integration_present": False,
        "baseline_models_executed": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "finite_adapter_configuration_contract_authorized_next_stage": True,
        "decision": S1_IZ_DECISION,
    }
    return DTS1S1IZImplementationReceipt(**values, receipt_digest=_digest(values))
