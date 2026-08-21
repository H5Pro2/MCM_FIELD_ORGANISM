"""Atomic execution envelope for one S1-SI four-node matrix cell."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math

from .four_node_exposure_fixture import (
    ALIGN,
    CHECKPOINT,
    INTERVAL,
    FourNodeExposureEvent,
    FourNodeExposureFixture,
    FourNodeExposurePlan,
    validate_four_node_exposure_fixture,
)
from .four_node_fresh_factory import (
    FourNodeSubstrateFreshState,
    build_four_node_role_fresh_bundle,
)
from .four_node_fresh_manifest import FourNodeFreshManifest
from .four_node_fresh_matrix_registration import FourNodeFreshMatrixRegistration
from .four_node_model_input_assembly import assemble_four_node_model_input
from .four_node_model_invocation import (
    COMPLETED,
    NOT_COMPUTABLE,
    FourNodeModelCarry,
    four_node_model_field_digest,
    four_node_model_private_state_digest,
    invoke_four_node_model,
    rebind_four_node_model_carry_field,
)
from .mcm_neuron import MCMFieldPerception, MCMNeuron
from .mcm_neuron_layer import MCMNeuronLayer
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_distributor import DistributedReceptorContact, ReceptorDistribution
from .shared_mcm_field import SharedMCMField


class FourNodeCellLifecycleError(ValueError):
    """Raised only when a published lifecycle value is malformed."""


_F3_ROLES = frozenset(
    {
        "A2_B3_LOCAL_LEAKY",
        "A2_B4_LINEAR_COUPLED",
        "A2_B5_F3_FULL",
        "A2_B6_CONST_V",
    }
)
_NODE_ORDER = ("node-a", "node-b", "node-c", "node-d")
_ZERO = (0.0, 0.0, 0.0, 0.0)
_CHAIN_ORIGIN = "CELL_CHAIN_ORIGIN"


class _CellStop(Exception):
    pass


def _canonical(value: object) -> object:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise FourNodeCellLifecycleError("non-finite lifecycle value")
        return 0.0 if value == 0.0 else value
    if isinstance(value, (tuple, list)):
        return [_canonical(item) for item in value]
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise FourNodeCellLifecycleError("lifecycle keys must be strings")
        return {key: _canonical(value[key]) for key in sorted(value)}
    raise FourNodeCellLifecycleError("lifecycle payload contains an object")


def _digest(value: object) -> str:
    encoded = json.dumps(
        _canonical(value),
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class FourNodeCellIdentity:
    matrix_registration_digest: str
    exposure_fixture_digest: str
    model_role: str
    exposure_plan_position: int
    exposure_plan_role: str
    fresh_manifest_digest: str
    model_configuration_digest: str
    refinement_or_none: int | None


@dataclass(frozen=True, slots=True)
class FourNodeAlignReceipt:
    model_role: str
    plan_position: int
    align_event_digest: str
    common_field_end_tick: int
    layer_tick: int
    pre_field_digest: str
    post_field_digest: str
    pre_last_distribution_digest: str
    projection_distribution_digest: str
    private_state_digest_or_none: str | None
    pre_carry_digest: str
    post_carry_digest: str
    configuration_and_dependency_digests: tuple[tuple[str, str | None], ...]
    receipt_digest: str


@dataclass(frozen=True, slots=True)
class FourNodeCheckpointRecord:
    model_role: str
    plan_position: int
    plan_role: str
    checkpoint_role: str
    checkpoint_tick: int
    fixture_event_digest: str
    event_chain_digest: str
    field_digest: str
    carry_digest: str
    private_state_digest_or_none: str | None
    configuration_and_dependency_digests: tuple[tuple[str, str | None], ...]
    last_distribution_digest: str
    signed_receptor_contact_vector: tuple[float, float, float, float]
    signed_activation_vector: tuple[float, float, float, float]
    signed_afterimage_vector: tuple[float, float, float, float]
    layer_tick: int
    common_field_end_tick: int
    align_receipt_digest_or_none: str | None
    checkpoint_digest: str


@dataclass(frozen=True, slots=True)
class FourNodeCellResult:
    status: str
    cell_identity_or_none: FourNodeCellIdentity | None
    matrix_registration_digest_or_none: str | None
    exposure_fixture_digest_or_none: str | None
    exposure_plan_digest_or_none: str | None
    model_configuration_digest_or_none: str | None
    refinement_or_none: int | None
    final_carry_or_none: FourNodeModelCarry | None
    ordered_checkpoint_records: tuple[FourNodeCheckpointRecord, ...]
    terminal_event_chain_digest_or_none: str | None
    failure_codes: tuple[str, ...]
    failure_receipt_digest_or_none: str | None
    cell_result_digest: str

    def __post_init__(self) -> None:
        if self.status == COMPLETED:
            if (
                self.cell_identity_or_none is None
                or self.final_carry_or_none is None
                or self.terminal_event_chain_digest_or_none is None
                or self.failure_codes
                or self.failure_receipt_digest_or_none is not None
            ):
                raise FourNodeCellLifecycleError("completed cell result is incomplete")
        elif self.status == NOT_COMPUTABLE:
            if (
                self.final_carry_or_none is not None
                or self.ordered_checkpoint_records
                or self.terminal_event_chain_digest_or_none is not None
                or not self.failure_codes
                or self.failure_receipt_digest_or_none is None
            ):
                raise FourNodeCellLifecycleError("failed cell result leaks partial state")
        else:
            raise FourNodeCellLifecycleError("cell result status is invalid")


def _dependencies(carry: FourNodeModelCarry) -> tuple[tuple[str, str | None], ...]:
    return (
        ("configuration_binding", carry.configuration_binding_or_none),
        ("registered_edge_inventory", carry.registered_edge_inventory_digest_or_none),
        ("native_edge_inventory", carry.native_edge_inventory_digest_or_none),
        ("registered_geometry", carry.registered_geometry_digest_or_none),
        ("native_geometry", carry.native_geometry_digest_or_none),
    )


def _field_end_tick(field: SharedMCMField) -> int:
    if field.last_distribution is None:
        raise _CellStop("CELL_FIELD_TIME_ABSENT")
    return field.last_distribution.field_time.window_end_tick


def _event_chain(
    previous: str,
    event: FourNodeExposureEvent,
    operation: str,
    pre_carry_digest: str,
    post_carry_digest: str,
    operation_receipt_digest: str,
) -> str:
    return _digest(
        {
            "previous_event_chain_digest": previous,
            "fixture_event_digest": event.event_digest,
            "operation": operation,
            "pre_carry_digest": pre_carry_digest,
            "post_carry_digest": post_carry_digest,
            "operation_receipt_digest": operation_receipt_digest,
        }
    )


def _projection_distribution(end_tick: int) -> ReceptorDistribution:
    start_tick = end_tick - 10
    frame = ReceptorContactFrame(
        modality_id="technical-control",
        geometry_id="mcm.s1rf.receptor.4n",
        snapshot_id=f"s1si.align.{start_tick}.{end_tick}",
        clock_id="mcm.s1sf.source",
        window_start_tick=start_tick,
        window_end_tick=end_tick,
        carrier_ids=("carrier-a", "carrier-b", "carrier-c", "carrier-d"),
        values=_ZERO,
    )
    return ReceptorDistribution(
        CommonFieldTime("mcm.s1sf.field", start_tick, end_tick),
        (DistributedReceptorContact("dock.s1rf.technical-control.4n", frame),),
    )


def _aligned_field(source: SharedMCMField, end_tick: int) -> SharedMCMField:
    neurons = tuple(
        MCMNeuron(
            neuron_id=neuron.neuron_id,
            field_id=neuron.field_id,
            modality_id=neuron.modality_id,
            geometry_id=neuron.geometry_id,
            position=neuron.position,
            activation=0.0,
            afterimage=0.0,
            perception=MCMFieldPerception(
                tick=neuron.perception.tick,
                receptor_contact=0.0,
                local_samples=neuron.perception.local_samples,
            ),
        )
        for neuron in source.layer.neurons
    )
    layer = MCMNeuronLayer(
        layer_id=source.layer.layer_id,
        neurons=neurons,
        sample_offsets=source.layer.sample_offsets,
        periodic_axes=source.layer.periodic_axes,
        receptor_dock_ids=source.layer.docked_neuron_ids,
    )
    return SharedMCMField(
        layer=layer,
        docks=source.docks,
        last_distribution=_projection_distribution(end_tick),
        substrate=source.substrate,
        development=source.development,
    )


def _align(
    carry: FourNodeModelCarry,
    event: FourNodeExposureEvent,
    plan: FourNodeExposurePlan,
) -> tuple[FourNodeModelCarry, FourNodeAlignReceipt]:
    target = event.align_target_or_none
    if target is None or event.event_kind != ALIGN:
        raise _CellStop("CELL_ALIGN_EVENT_INVALID")
    if (
        target.receptor_contact != _ZERO
        or target.activation != _ZERO
        or target.afterimage != _ZERO
        or _field_end_tick(carry.field) != target.field_tick
    ):
        raise _CellStop("CELL_ALIGN_TARGET_INVALID")

    pre_field_digest = four_node_model_field_digest(carry.field)
    previous_distribution = carry.field.last_distribution
    if previous_distribution is None:
        raise _CellStop("CELL_ALIGN_PREVIOUS_DISTRIBUTION_ABSENT")
    previous_distribution_digest = previous_distribution.digest()
    projected_field = _aligned_field(carry.field, target.field_tick)
    rebound = rebind_four_node_model_carry_field(carry, projected_field)
    post_field_digest = four_node_model_field_digest(projected_field)
    projection_digest = projected_field.last_distribution.digest()  # type: ignore[union-attr]
    private_digest = four_node_model_private_state_digest(carry.private_state_or_none)
    payload = {
        "model_role": carry.model_role,
        "plan_position": plan.position,
        "align_event_digest": event.event_digest,
        "common_field_end_tick": target.field_tick,
        "layer_tick": carry.field.layer.tick,
        "pre_field_digest": pre_field_digest,
        "post_field_digest": post_field_digest,
        "pre_last_distribution_digest": previous_distribution_digest,
        "projection_distribution_digest": projection_digest,
        "private_state_digest_or_none": private_digest,
        "pre_carry_digest": carry.carry_digest,
        "post_carry_digest": rebound.carry_digest,
        "configuration_and_dependency_digests": _dependencies(carry),
    }
    receipt = FourNodeAlignReceipt(
        carry.model_role,
        plan.position,
        event.event_digest,
        target.field_tick,
        carry.field.layer.tick,
        pre_field_digest,
        post_field_digest,
        previous_distribution_digest,
        projection_digest,
        private_digest,
        carry.carry_digest,
        rebound.carry_digest,
        _dependencies(carry),
        _digest(payload),
    )
    return rebound, receipt


def _checkpoint(
    carry: FourNodeModelCarry,
    event: FourNodeExposureEvent,
    plan: FourNodeExposurePlan,
    previous_chain: str,
    align_receipt: FourNodeAlignReceipt | None,
) -> tuple[FourNodeCheckpointRecord, str]:
    role = event.checkpoint_role_or_none
    tick = event.checkpoint_tick_or_none
    if role is None or tick is None or tick != _field_end_tick(carry.field):
        raise _CellStop("CELL_CHECKPOINT_TIME_INVALID")
    neurons = carry.field.layer.neurons
    if tuple(item.neuron_id for item in neurons) != _NODE_ORDER:
        raise _CellStop("CELL_CHECKPOINT_NODE_ORDER_INVALID")
    distribution = carry.field.last_distribution
    if distribution is None:
        raise _CellStop("CELL_CHECKPOINT_DISTRIBUTION_ABSENT")
    base_payload = {
        "model_role": carry.model_role,
        "plan_position": plan.position,
        "plan_role": plan.replica_role,
        "checkpoint_role": role,
        "checkpoint_tick": tick,
        "fixture_event_digest": event.event_digest,
        "field_digest": four_node_model_field_digest(carry.field),
        "carry_digest": carry.carry_digest,
        "private_state_digest_or_none": four_node_model_private_state_digest(
            carry.private_state_or_none
        ),
        "configuration_and_dependency_digests": _dependencies(carry),
        "last_distribution_digest": distribution.digest(),
        "signed_receptor_contact_vector": tuple(
            item.perception.receptor_contact for item in neurons
        ),
        "signed_activation_vector": tuple(item.activation for item in neurons),
        "signed_afterimage_vector": tuple(item.afterimage for item in neurons),
        "layer_tick": carry.field.layer.tick,
        "common_field_end_tick": tick,
        "align_receipt_digest_or_none": (
            None if align_receipt is None else align_receipt.receipt_digest
        ),
    }
    operation_receipt_digest = _digest(base_payload)
    chain = _event_chain(
        previous_chain,
        event,
        CHECKPOINT,
        carry.carry_digest,
        carry.carry_digest,
        operation_receipt_digest,
    )
    payload = dict(base_payload)
    payload["event_chain_digest"] = chain
    checkpoint_digest = _digest(payload)
    contacts = base_payload["signed_receptor_contact_vector"]
    activation = base_payload["signed_activation_vector"]
    afterimage = base_payload["signed_afterimage_vector"]
    if not all(isinstance(value, tuple) and len(value) == 4 for value in (contacts, activation, afterimage)):
        raise _CellStop("CELL_CHECKPOINT_VECTOR_INVALID")
    return (
        FourNodeCheckpointRecord(
            carry.model_role,
            plan.position,
            plan.replica_role,
            role,
            tick,
            event.event_digest,
            chain,
            base_payload["field_digest"],  # type: ignore[arg-type]
            carry.carry_digest,
            base_payload["private_state_digest_or_none"],  # type: ignore[arg-type]
            _dependencies(carry),
            distribution.digest(),
            contacts,  # type: ignore[arg-type]
            activation,  # type: ignore[arg-type]
            afterimage,  # type: ignore[arg-type]
            carry.field.layer.tick,
            tick,
            base_payload["align_receipt_digest_or_none"],  # type: ignore[arg-type]
            checkpoint_digest,
        ),
        chain,
    )


def _result_payload(result: FourNodeCellResult) -> dict[str, object]:
    identity = result.cell_identity_or_none
    return {
        item.name: (
            getattr(result, item.name)
            if item.name
            not in {
                "cell_identity_or_none",
                "final_carry_or_none",
                "ordered_checkpoint_records",
                "cell_result_digest",
            }
            else None
        )
        for item in fields(result)
        if item.name != "cell_result_digest"
    } | {
        "cell_identity_or_none": (
            None
            if identity is None
            else {item.name: getattr(identity, item.name) for item in fields(identity)}
        ),
        "final_carry_digest_or_none": (
            None if result.final_carry_or_none is None else result.final_carry_or_none.carry_digest
        ),
        "ordered_checkpoint_digests": tuple(
            item.checkpoint_digest for item in result.ordered_checkpoint_records
        ),
    }


def _publish(result: FourNodeCellResult) -> FourNodeCellResult:
    values = tuple(
        getattr(result, item.name)
        if item.name != "cell_result_digest"
        else _digest(_result_payload(result))
        for item in fields(result)
    )
    return FourNodeCellResult(*values)


def execute_four_node_cell(
    manifest: FourNodeFreshManifest,
    registration: FourNodeFreshMatrixRegistration,
    fixture: FourNodeExposureFixture,
    model_role: str,
    exposure_plan_position: int,
) -> FourNodeCellResult:
    """Execute one isolated model/plan cell and publish only an atomic result."""

    matrix_digest: str | None = None
    fixture_digest: str | None = None
    plan_digest: str | None = None
    configuration_digest: str | None = None
    identity: FourNodeCellIdentity | None = None
    refinement: int | None = None
    try:
        if not isinstance(manifest, FourNodeFreshManifest):
            raise _CellStop("CELL_FRESH_MANIFEST_INVALID")
        if not isinstance(registration, FourNodeFreshMatrixRegistration):
            raise _CellStop("CELL_MATRIX_REGISTRATION_INVALID")
        if not isinstance(fixture, FourNodeExposureFixture):
            raise _CellStop("CELL_EXPOSURE_FIXTURE_INVALID")
        if not isinstance(model_role, str):
            raise _CellStop("CELL_MODEL_ROLE_INVALID")
        matrix_digest = registration.registration_digest
        fixture_digest = fixture.fixture_digest
        refinement = 2 if model_role in _F3_ROLES else None
        validate_four_node_exposure_fixture(fixture, registration)
        if (
            isinstance(exposure_plan_position, bool)
            or not isinstance(exposure_plan_position, int)
            or not 1 <= exposure_plan_position <= len(fixture.plans)
        ):
            raise _CellStop("CELL_PLAN_POSITION_INVALID")
        plan = fixture.plans[exposure_plan_position - 1]
        plan_digest = plan.plan_digest
        if plan.position != exposure_plan_position:
            raise _CellStop("CELL_PLAN_IDENTITY_INVALID")

        assembly = assemble_four_node_model_input(
            build_four_node_role_fresh_bundle(manifest, model_role)
        )
        expected_dependencies = (
            ("configuration_binding", assembly.configuration_binding_or_none),
            (
                "registered_edge_inventory",
                assembly.registered_edge_inventory_digest_or_none,
            ),
            ("native_edge_inventory", assembly.native_edge_inventory_digest_or_none),
            (
                "registered_geometry",
                assembly.registered_geometry_digest_or_none,
            ),
            ("native_geometry", assembly.native_geometry_digest_or_none),
        )
        carry: FourNodeModelCarry | None = None
        chain = _CHAIN_ORIGIN
        checkpoints: list[FourNodeCheckpointRecord] = []
        last_align_receipt: FourNodeAlignReceipt | None = None
        interval_count = align_count = checkpoint_count = 0

        for index, event in enumerate(plan.events):
            if event.event_kind == INTERVAL:
                interval = event.interval_or_none
                if interval is None:
                    raise _CellStop("CELL_INTERVAL_EVENT_INVALID")
                source = assembly if carry is None else carry
                expected_start = 0 if carry is None else _field_end_tick(carry.field)
                step = interval.step_time
                time = interval.distribution.field_time
                if (
                    step.clock_id != time.clock_id
                    or step.start_tick != time.window_start_tick
                    or step.end_tick != time.window_end_tick
                    or step.start_tick != expected_start
                ):
                    raise _CellStop("CELL_INTERVAL_TIME_INVALID")
                pre_digest = assembly.assembly_digest if carry is None else carry.carry_digest
                pre_layer_tick = assembly.model_input_field.layer.tick if carry is None else carry.field.layer.tick
                result = invoke_four_node_model(
                    source,
                    interval.distribution,
                    step,
                    refinement=refinement,
                )
                if (
                    result.status != COMPLETED
                    or result.field_time_advance_count != 1
                    or result.next_carry_or_none is None
                    or result.output_field_or_none is None
                ):
                    code = result.failure_codes[0] if result.failure_codes else "UNKNOWN"
                    raise _CellStop(f"CELL_INTERVAL_NOT_COMPUTABLE:{code}")
                next_carry = result.next_carry_or_none
                if (
                    result.model_role != model_role
                    or next_carry.model_role != model_role
                    or result.output_field_or_none.last_distribution != interval.distribution
                    or result.output_field_or_none is not next_carry.field
                    or result.next_private_state_or_none
                    is not next_carry.private_state_or_none
                    or result.output_field_digest_or_none
                    != four_node_model_field_digest(next_carry.field)
                    or result.next_private_state_digest_or_none
                    != four_node_model_private_state_digest(
                        next_carry.private_state_or_none
                    )
                    or _field_end_tick(next_carry.field) != step.end_tick
                    or next_carry.field.layer.tick != pre_layer_tick + 1
                    or next_carry.field.geometry_id != assembly.model_input_field.geometry_id
                    or next_carry.field.field_id != assembly.model_input_field.field_id
                    or next_carry.field.docks != assembly.model_input_field.docks
                    or _dependencies(next_carry) != expected_dependencies
                ):
                    raise _CellStop("CELL_INTERVAL_RESULT_INVALID")
                if model_role in _F3_ROLES:
                    private = next_carry.private_state_or_none
                    if (
                        not isinstance(private, FourNodeSubstrateFreshState)
                        or private.substrate is not next_carry.field.substrate
                    ):
                        raise _CellStop("CELL_INTERVAL_SUBSTRATE_IDENTITY_INVALID")
                if configuration_digest is None:
                    configuration_digest = result.configuration_digest
                    identity = FourNodeCellIdentity(
                        registration.registration_digest,
                        fixture.fixture_digest,
                        model_role,
                        plan.position,
                        plan.replica_role,
                        manifest.manifest_digest,
                        configuration_digest,
                        refinement,
                    )
                elif result.configuration_digest != configuration_digest:
                    raise _CellStop("CELL_CONFIGURATION_DIGEST_CHANGED")
                carry = next_carry
                chain = _event_chain(
                    chain,
                    event,
                    INTERVAL,
                    pre_digest,
                    carry.carry_digest,
                    result.result_digest,
                )
                interval_count += 1

            elif event.event_kind == ALIGN:
                if carry is None or interval_count == 0:
                    raise _CellStop("CELL_ALIGN_WITHOUT_INTERVAL")
                if (
                    index + 1 >= len(plan.events)
                    or plan.events[index + 1].event_kind != CHECKPOINT
                    or plan.events[index + 1].checkpoint_role_or_none != "ALIGNED_PRE_PROBE"
                ):
                    raise _CellStop("CELL_ALIGN_SUCCESSOR_INVALID")
                pre_digest = carry.carry_digest
                carry, last_align_receipt = _align(carry, event, plan)
                chain = _event_chain(
                    chain,
                    event,
                    ALIGN,
                    pre_digest,
                    carry.carry_digest,
                    last_align_receipt.receipt_digest,
                )
                align_count += 1

            elif event.event_kind == CHECKPOINT:
                if carry is None:
                    raise _CellStop("CELL_CHECKPOINT_WITHOUT_CARRY")
                role = event.checkpoint_role_or_none
                previous = plan.events[index - 1] if index else None
                if role == "ALIGNED_PRE_PROBE":
                    if previous is None or previous.event_kind != ALIGN or last_align_receipt is None:
                        raise _CellStop("CELL_ALIGNED_CHECKPOINT_ORDER_INVALID")
                    receipt = last_align_receipt
                elif role == "POST_PROBE_READOUT":
                    interval = None if previous is None else previous.interval_or_none
                    if (
                        previous is None
                        or previous.event_kind != INTERVAL
                        or interval is None
                        or not interval.payload_role.startswith("PROBE_")
                        or last_align_receipt is None
                    ):
                        raise _CellStop("CELL_POST_PROBE_CHECKPOINT_ORDER_INVALID")
                    receipt = last_align_receipt
                else:
                    if last_align_receipt is not None:
                        raise _CellStop("CELL_COMPETITION_CHECKPOINT_ALIGN_INVALID")
                    receipt = None
                record, chain = _checkpoint(
                    carry,
                    event,
                    plan,
                    chain,
                    receipt,
                )
                checkpoints.append(record)
                checkpoint_count += 1
            else:
                raise _CellStop("CELL_EVENT_KIND_INVALID")

        if carry is None or identity is None or configuration_digest is None:
            raise _CellStop("CELL_TERMINAL_CARRY_ABSENT")
        if (
            interval_count != plan.model_interval_count
            or align_count != 1
            or checkpoint_count != plan.checkpoint_count
            or _field_end_tick(carry.field) != plan.terminal_tick
        ):
            raise _CellStop("CELL_TERMINAL_COUNTS_INVALID")
        result = FourNodeCellResult(
            COMPLETED,
            identity,
            registration.registration_digest,
            fixture.fixture_digest,
            plan.plan_digest,
            configuration_digest,
            refinement,
            carry,
            tuple(checkpoints),
            chain,
            (),
            None,
            "",
        )
        return _publish(result)
    except Exception as exc:
        code = str(exc) if isinstance(exc, _CellStop) else f"CELL_LIFECYCLE_INVALID:{type(exc).__name__}:{exc}"
        failure_receipt = _digest(
            {
                "cell_identity_or_none": (
                    None
                    if identity is None
                    else {item.name: getattr(identity, item.name) for item in fields(identity)}
                ),
                "matrix_registration_digest_or_none": matrix_digest,
                "exposure_fixture_digest_or_none": fixture_digest,
                "exposure_plan_digest_or_none": plan_digest,
                "failure_codes": (code,),
            }
        )
        failed = FourNodeCellResult(
            NOT_COMPUTABLE,
            identity,
            matrix_digest,
            fixture_digest,
            plan_digest,
            configuration_digest,
            refinement,
            None,
            (),
            None,
            (code,),
            failure_receipt,
            "",
        )
        return _publish(failed)
