"""Passive separation of external and endogenous causes in one shared field."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math

from .controlled_endogenous_source import (
    controlled_multiscale_endogenous_source,
)
from .field_step_time import MCMFieldStepTime
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    advance_neutral_fast_shared_field,
)
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_distributor import ReceptorDistributor, ReceptorDock
from .shared_mcm_field import (
    ReceptorDockAnatomy,
    SharedMCMField,
    build_shared_mcm_field,
)


class EndogenousExternalOverlapNullProbeError(ValueError):
    """Raised when the passive cause comparison loses a control boundary."""


@dataclass(frozen=True, slots=True)
class PassiveCauseFieldSignature:
    """Final difference from the contact-free control, not a stored field role."""

    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    activation_l2: float
    afterimage_l2: float

    def __post_init__(self) -> None:
        activation = tuple(float(value) for value in self.activation)
        afterimage = tuple(float(value) for value in self.afterimage)
        if (
            not activation
            or len(activation) != len(afterimage)
            or any(
                not math.isfinite(value)
                for value in activation + afterimage
            )
        ):
            raise EndogenousExternalOverlapNullProbeError(
                "cause signature requires equal finite field vectors"
            )
        for role in ("activation_l2", "afterimage_l2"):
            value = float(getattr(self, role))
            if not math.isfinite(value) or value < 0.0:
                raise EndogenousExternalOverlapNullProbeError(
                    f"{role} must be finite and non-negative"
                )
            object.__setattr__(self, role, value)
        object.__setattr__(self, "activation", activation)
        object.__setattr__(self, "afterimage", afterimage)


@dataclass(frozen=True, slots=True)
class EndogenousExternalOverlapNullProbeResult:
    """Four-branch passive comparison under the unchanged fast field runtime."""

    neuron_ids: tuple[str, ...]
    external_signature: PassiveCauseFieldSignature
    endogenous_signature: PassiveCauseFieldSignature
    joint_activation: tuple[float, ...]
    joint_afterimage: tuple[float, ...]
    maximum_activation_superposition_error: float
    maximum_afterimage_superposition_error: float
    external_cause_preserved: bool
    endogenous_cause_preserved: bool
    cause_signatures_distinct: bool
    exact_linear_superposition: bool
    source_states_preserved: bool
    observer_writeback_performed: bool
    memory_state_added: bool
    material_motion_added: bool
    runtime_candidate_released: bool

    def __post_init__(self) -> None:
        neuron_ids = tuple(self.neuron_ids)
        if not neuron_ids or len(set(neuron_ids)) != len(neuron_ids):
            raise EndogenousExternalOverlapNullProbeError(
                "overlap result requires unique neuron identities"
            )
        if not isinstance(self.external_signature, PassiveCauseFieldSignature):
            raise EndogenousExternalOverlapNullProbeError(
                "external_signature must be a passive cause signature"
            )
        if not isinstance(self.endogenous_signature, PassiveCauseFieldSignature):
            raise EndogenousExternalOverlapNullProbeError(
                "endogenous_signature must be a passive cause signature"
            )
        joint_activation = tuple(float(value) for value in self.joint_activation)
        joint_afterimage = tuple(float(value) for value in self.joint_afterimage)
        if (
            len(joint_activation) != len(neuron_ids)
            or len(joint_afterimage) != len(neuron_ids)
            or any(
                not math.isfinite(value)
                for value in joint_activation + joint_afterimage
            )
        ):
            raise EndogenousExternalOverlapNullProbeError(
                "joint field vectors must match the observed neurons"
            )
        for role in (
            "maximum_activation_superposition_error",
            "maximum_afterimage_superposition_error",
        ):
            value = float(getattr(self, role))
            if not math.isfinite(value) or value < 0.0:
                raise EndogenousExternalOverlapNullProbeError(
                    f"{role} must be finite and non-negative"
                )
            object.__setattr__(self, role, value)
        object.__setattr__(self, "neuron_ids", neuron_ids)
        object.__setattr__(self, "joint_activation", joint_activation)
        object.__setattr__(self, "joint_afterimage", joint_afterimage)


def _external_frames(count: int) -> tuple[ReceptorContactFrame, ...]:
    values = (0.6, -0.3, 0.45, -0.15, 0.3, -0.45, 0.15, -0.6)
    if count != len(values):
        raise EndogenousExternalOverlapNullProbeError(
            "controlled external and endogenous horizons must match"
        )
    return tuple(
        ReceptorContactFrame(
            modality_id="external.controlled",
            geometry_id="external.controlled.v1",
            snapshot_id=f"external.controlled.{index}",
            clock_id="external.controlled",
            window_start_tick=index,
            window_end_tick=index + 1,
            carrier_ids=("x0",),
            values=(value,),
        )
        for index, value in enumerate(values)
    )


def _zeroed(frame: ReceptorContactFrame, branch_id: str) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id=frame.modality_id,
        geometry_id=frame.geometry_id,
        snapshot_id=f"{frame.snapshot_id}.{branch_id}",
        clock_id=frame.clock_id,
        window_start_tick=frame.window_start_tick,
        window_end_tick=frame.window_end_tick,
        carrier_ids=frame.carrier_ids,
        values=(0.0,) * len(frame.values),
    )


def _initial_field(
    endogenous: ReceptorContactFrame,
    external: ReceptorContactFrame,
) -> SharedMCMField:
    return build_shared_mcm_field(
        (endogenous, external),
        {
            endogenous.modality_id: ReceptorDockAnatomy(
                endogenous.modality_id,
                "dock.endogenous.controlled",
                ((0, 0), (0, 1)),
            ),
            external.modality_id: ReceptorDockAnatomy(
                external.modality_id,
                "dock.external.controlled",
                ((1, 0),),
            ),
        },
        sample_offsets=((-1, 0), (0, -1), (0, 1), (1, 0)),
    )


def _distributor(
    endogenous: ReceptorContactFrame,
    external: ReceptorContactFrame,
) -> ReceptorDistributor:
    result = ReceptorDistributor()
    result.attach(
        ReceptorDock(
            "dock.endogenous.controlled",
            endogenous.modality_id,
            endogenous.geometry_id,
        )
    )
    result.attach(
        ReceptorDock(
            "dock.external.controlled",
            external.modality_id,
            external.geometry_id,
        )
    )
    return result


def _run_branch(
    initial: SharedMCMField,
    endogenous_frames: tuple[ReceptorContactFrame, ...],
    external_frames: tuple[ReceptorContactFrame, ...],
    *,
    use_endogenous: bool,
    use_external: bool,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
) -> SharedMCMField:
    distributor = _distributor(endogenous_frames[0], external_frames[0])
    current = initial
    for index, (endogenous, external) in enumerate(
        zip(endogenous_frames, external_frames, strict=True)
    ):
        selected_endogenous = (
            endogenous if use_endogenous else _zeroed(endogenous, "zero")
        )
        selected_external = (
            external if use_external else _zeroed(external, "zero")
        )
        distribution = distributor.distribute(
            (selected_external, selected_endogenous),
            CommonFieldTime("organism.clock", index, index + 1),
        )
        current = advance_neutral_fast_shared_field(
            current,
            distribution,
            MCMFieldStepTime("organism.clock", index, index + 1, 1.0),
            substrate_config,
            afterimage_config,
        )
    return current


def _vectors(field: SharedMCMField) -> tuple[tuple[float, ...], tuple[float, ...]]:
    return (
        tuple(neuron.activation for neuron in field.layer.neurons),
        tuple(neuron.afterimage for neuron in field.layer.neurons),
    )


def _difference(
    branch: tuple[tuple[float, ...], tuple[float, ...]],
    baseline: tuple[tuple[float, ...], tuple[float, ...]],
) -> PassiveCauseFieldSignature:
    activation = tuple(
        left - right
        for left, right in zip(branch[0], baseline[0], strict=True)
    )
    afterimage = tuple(
        left - right
        for left, right in zip(branch[1], baseline[1], strict=True)
    )
    return PassiveCauseFieldSignature(
        activation,
        afterimage,
        math.sqrt(math.fsum(value * value for value in activation)),
        math.sqrt(math.fsum(value * value for value in afterimage)),
    )


def run_endogenous_external_overlap_null_probe(
    *,
    response_time_seconds: float = 1.0,
    afterimage_time_seconds: float = 0.5,
) -> EndogenousExternalOverlapNullProbeResult:
    """Compare joint and ablated causes without adding a field mechanism."""

    substrate_config = NeutralLocalFieldSubstrateConfig(response_time_seconds)
    afterimage_config = NeutralFastAfterimageConfig(afterimage_time_seconds)
    endogenous_source = controlled_multiscale_endogenous_source()
    endogenous_frames = endogenous_source.frames()
    external_frames = _external_frames(len(endogenous_frames))
    initial = _initial_field(endogenous_frames[0], external_frames[0])
    initial_digest = initial.layer.digest()
    source_digest = endogenous_source.digest()

    joint = _run_branch(
        initial,
        endogenous_frames,
        external_frames,
        use_endogenous=True,
        use_external=True,
        substrate_config=substrate_config,
        afterimage_config=afterimage_config,
    )
    external_only = _run_branch(
        initial,
        endogenous_frames,
        external_frames,
        use_endogenous=False,
        use_external=True,
        substrate_config=substrate_config,
        afterimage_config=afterimage_config,
    )
    endogenous_only = _run_branch(
        initial,
        endogenous_frames,
        external_frames,
        use_endogenous=True,
        use_external=False,
        substrate_config=substrate_config,
        afterimage_config=afterimage_config,
    )
    contact_free = _run_branch(
        initial,
        endogenous_frames,
        external_frames,
        use_endogenous=False,
        use_external=False,
        substrate_config=substrate_config,
        afterimage_config=afterimage_config,
    )

    joint_vectors = _vectors(joint)
    external_vectors = _vectors(external_only)
    endogenous_vectors = _vectors(endogenous_only)
    free_vectors = _vectors(contact_free)
    external_signature = _difference(external_vectors, free_vectors)
    endogenous_signature = _difference(endogenous_vectors, free_vectors)

    expected_activation = tuple(
        free + external + endogenous
        for free, external, endogenous in zip(
            free_vectors[0],
            external_signature.activation,
            endogenous_signature.activation,
            strict=True,
        )
    )
    expected_afterimage = tuple(
        free + external + endogenous
        for free, external, endogenous in zip(
            free_vectors[1],
            external_signature.afterimage,
            endogenous_signature.afterimage,
            strict=True,
        )
    )
    activation_error = max(
        abs(actual - expected)
        for actual, expected in zip(
            joint_vectors[0],
            expected_activation,
            strict=True,
        )
    )
    afterimage_error = max(
        abs(actual - expected)
        for actual, expected in zip(
            joint_vectors[1],
            expected_afterimage,
            strict=True,
        )
    )
    tolerance = 1e-12

    return EndogenousExternalOverlapNullProbeResult(
        neuron_ids=tuple(neuron.neuron_id for neuron in joint.layer.neurons),
        external_signature=external_signature,
        endogenous_signature=endogenous_signature,
        joint_activation=joint_vectors[0],
        joint_afterimage=joint_vectors[1],
        maximum_activation_superposition_error=activation_error,
        maximum_afterimage_superposition_error=afterimage_error,
        external_cause_preserved=(
            external_signature.activation_l2 > tolerance
            and external_signature.afterimage_l2 > tolerance
        ),
        endogenous_cause_preserved=(
            endogenous_signature.activation_l2 > tolerance
            and endogenous_signature.afterimage_l2 > tolerance
        ),
        cause_signatures_distinct=(
            external_signature.activation != endogenous_signature.activation
            and external_signature.afterimage != endogenous_signature.afterimage
        ),
        exact_linear_superposition=(
            activation_error <= tolerance and afterimage_error <= tolerance
        ),
        source_states_preserved=(
            initial.layer.digest() == initial_digest
            and endogenous_source.digest() == source_digest
        ),
        observer_writeback_performed=False,
        memory_state_added=False,
        material_motion_added=False,
        runtime_candidate_released=False,
    )


def endogenous_external_overlap_null_probe_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            PassiveCauseFieldSignature,
            EndogenousExternalOverlapNullProbeResult,
        )
        for item in fields(contract)
    )
