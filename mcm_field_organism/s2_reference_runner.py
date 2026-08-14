"""Scalar-only orchestration boundary for the S2 technical reference packet."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import math
import re
from typing import Callable, Iterable

from .finite_audio_video_field_run import (
    ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    audio_video_dock_anatomies,
)
from .mcm_local_development_state import MCMLocalDevelopmentContract
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
    advance_neutral_fast_shared_field_transient,
)
from .receptor_distributor import ReceptorDistribution
from .s1b_reciprocal_accommodation import (
    advance_s1b_reciprocal_shared_field_transient,
)
from .receptor_contract import CommonFieldTime
from .receptor_proposal_handoff_audit import handoff_receptor_completion_groups
from .shared_mcm_field import (
    SharedMCMField,
    SharedMCMFieldError,
    attach_zero_mcm_local_development,
    build_shared_mcm_field,
)
from .s2_reference_worlds import (
    S2PreparedC1Plan,
    S2PreparedN8Plan,
    S2PreparedProbePlan,
    S2PreparedR2C2Plan,
    S2PreparedR4C4Plan,
    S2PreparedR8C8Plan,
    S2PreparedR8BC8BPlan,
    S2PreparedWorldPlan,
    S2ReferenceTask,
    build_s2_reference_tasks,
    prepare_s2c4_probe_plan,
    prepare_s2c11_r8c8_receptor_plans,
    prepare_s2c13_r8bc8b_receptor_plans,
    s2_reference_inventory_digest,
)
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import TransientNeuronInputSet
from .transient_neuron_input import project_transient_docks_to_neuron_inputs


class S2ReferenceRunnerError(ValueError):
    """Raised when S2 orchestration or scalar projection violates its contract."""


S2_PACKET_SCHEMA = "mcm.s2.reference.packet.v1"
S2_METRIC_IDS = (
    "d_l",
    "d_s",
    "d_h",
    "d_pair",
    "swap_error",
    "neutral_error",
    "resume_error",
    "reproduction_error",
    "balance_error",
    "range_error",
    "partition_error",
)
S2_CONTROL_IDS = (
    "world_budget_valid",
    "handoff_valid",
    "fast_state_equalized",
    "intervention_isolated",
    "observer_neutral",
    "resume_exact",
    "reproduction_exact",
    "finite_scalars",
)
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def equalize_fast_state_for_probe(field: SharedMCMField) -> SharedMCMField:
    """External S2 test intervention setting only S and H exactly to zero."""

    if not isinstance(field, SharedMCMField):
        raise S2ReferenceRunnerError("fast-state equalization requires one field")
    if field.last_distribution is None:
        raise S2ReferenceRunnerError("fast-state equalization requires a completed history")
    try:
        neurons = tuple(
            replace(neuron, activation=0.0, afterimage=0.0)
            for neuron in field.layer.neurons
        )
        layer = replace(field.layer, neurons=neurons)
        result = SharedMCMField(
            layer=layer,
            docks=field.docks,
            last_distribution=field.last_distribution,
            development=field.development,
        )
    except (SharedMCMFieldError, ValueError) as exc:
        raise S2ReferenceRunnerError(str(exc)) from exc
    if result.development != field.development:
        raise S2ReferenceRunnerError("fast-state equalization changed L")
    if result.layer.tick != field.layer.tick or result.docks != field.docks:
        raise S2ReferenceRunnerError("fast-state equalization changed field identity")
    return result


@dataclass(frozen=True, slots=True)
class S2ControlledBatchResult:
    """One technical B0/B2 batch result without research metrics or decision."""

    model_id: str
    start_layer_digest: str
    end_snapshot_digest: str
    local_contact_count: int
    field: SharedMCMField

    def __post_init__(self) -> None:
        if self.model_id not in ("b0", "b2"):
            raise S2ReferenceRunnerError("controlled batch supports only B0 or B2")
        if not _DIGEST.fullmatch(self.start_layer_digest):
            raise S2ReferenceRunnerError("controlled batch start digest is invalid")
        if not _DIGEST.fullmatch(self.end_snapshot_digest):
            raise S2ReferenceRunnerError("controlled batch end digest is invalid")
        if (
            isinstance(self.local_contact_count, bool)
            or not isinstance(self.local_contact_count, int)
            or self.local_contact_count < 0
        ):
            raise S2ReferenceRunnerError("controlled batch contact count is invalid")
        if not isinstance(self.field, SharedMCMField):
            raise S2ReferenceRunnerError("controlled batch requires one resulting field")
        if self.field.snapshot().digest() != self.end_snapshot_digest:
            raise S2ReferenceRunnerError("controlled batch field and digest differ")


def advance_s2_controlled_receptor_batch(
    model_id: str,
    field: SharedMCMField,
    distribution: ReceptorDistribution,
    transient_inputs: TransientNeuronInputSet,
    field_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
    *,
    _state_observer: Callable[[int, object, object, object | None], None] | None = None,
) -> S2ControlledBatchResult:
    """Advance exactly one prepared receptor batch through B0 or B2."""

    if model_id not in ("b0", "b2"):
        raise S2ReferenceRunnerError("S2-C2 permits only the B0/B2 batch bridge")
    if not isinstance(field, SharedMCMField):
        raise S2ReferenceRunnerError("S2-C2 batch requires one shared field")
    if not isinstance(distribution, ReceptorDistribution):
        raise S2ReferenceRunnerError("S2-C2 batch requires one distribution")
    if not isinstance(transient_inputs, TransientNeuronInputSet):
        raise S2ReferenceRunnerError("S2-C2 batch requires transient inputs")
    if _state_observer is not None and not callable(_state_observer):
        raise S2ReferenceRunnerError("S2 batch state observer must be callable")
    if model_id == "b0":
        if field.development is not None or field.substrate is not None:
            raise S2ReferenceRunnerError("B0 batch requires the plain fast field")
        next_field = advance_neutral_fast_shared_field_transient(
            field,
            distribution,
            transient_inputs,
            field_config,
            afterimage_config,
            dissipation_config,
            _state_observer=(
                None
                if _state_observer is None
                else lambda tick, activation, afterimage: _state_observer(
                    tick,
                    activation,
                    afterimage,
                    None,
                )
            ),
        )
    else:
        if field.development is None or field.substrate is not None:
            raise S2ReferenceRunnerError("B2 batch requires exactly one L corridor")
        next_field = advance_s1b_reciprocal_shared_field_transient(
            field,
            distribution,
            transient_inputs,
            field_config,
            afterimage_config,
            dissipation_config,
            observer=_state_observer,
        )
    snapshot = next_field.snapshot()
    return S2ControlledBatchResult(
        model_id=model_id,
        start_layer_digest=field.layer.digest(),
        end_snapshot_digest=snapshot.digest(),
        local_contact_count=transient_inputs.contact_count,
        field=next_field,
    )


@dataclass(frozen=True, slots=True)
class S2ControlledWorldResult:
    """Technical result of the sole S2-C3 r1.a B0/B2 world path."""

    world_id: str
    model_id: str
    coupling_rate_per_second: float
    plan_digest: str
    world_digest: str
    start_layer_digest: str
    end_snapshot_digest: str
    source_support_count: int
    assigned_support_count: int
    batch_count: int
    field: SharedMCMField

    def __post_init__(self) -> None:
        if self.world_id != "r1.a" or self.model_id not in ("b0", "b2"):
            raise S2ReferenceRunnerError("S2-C3 result permits only r1.a B0/B2")
        coupling = float(self.coupling_rate_per_second)
        if coupling not in (0.0, 0.25):
            raise S2ReferenceRunnerError("S2-C3 result coupling is invalid")
        if self.model_id == "b0" and coupling != 0.0:
            raise S2ReferenceRunnerError("S2-C3 B0 cannot carry L coupling")
        object.__setattr__(self, "coupling_rate_per_second", coupling)
        for role in (
            "plan_digest",
            "world_digest",
            "start_layer_digest",
            "end_snapshot_digest",
        ):
            if not _DIGEST.fullmatch(getattr(self, role)):
                raise S2ReferenceRunnerError(f"invalid S2-C3 {role}")
        for role in (
            "source_support_count",
            "assigned_support_count",
            "batch_count",
        ):
            value = getattr(self, role)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise S2ReferenceRunnerError(f"invalid S2-C3 {role}")
        if self.source_support_count != self.assigned_support_count:
            raise S2ReferenceRunnerError("S2-C3 must assign every source support once")
        if not isinstance(self.field, SharedMCMField):
            raise S2ReferenceRunnerError("S2-C3 result requires one field")
        if self.field.snapshot().digest() != self.end_snapshot_digest:
            raise S2ReferenceRunnerError("S2-C3 result field and digest differ")


def advance_s2c3_r1_world(
    plan: S2PreparedWorldPlan,
    model_id: str,
    field_config: NeutralLocalFieldSubstrateConfig = (
        NeutralLocalFieldSubstrateConfig(1.0)
    ),
    afterimage_config: NeutralFastAfterimageConfig = (
        NeutralFastAfterimageConfig(0.5)
    ),
    *,
    coupling_rate_per_second: float | None = None,
) -> S2ControlledWorldResult:
    """Advance only prepared r1.a through B0 or B2 without probe or report."""

    if not isinstance(plan, S2PreparedWorldPlan) or plan.world_id != "r1.a":
        raise S2ReferenceRunnerError("S2-C3 requires the canonical r1.a plan")
    if model_id not in ("b0", "b2"):
        raise S2ReferenceRunnerError("S2-C3 permits only B0 or B2")
    if field_config.response_time_seconds != 1.0:
        raise S2ReferenceRunnerError("S2-C3 field response must remain 1.0 s")
    if afterimage_config.time_constant_seconds != 0.5:
        raise S2ReferenceRunnerError("S2-C3 afterimage time must remain 0.5 s")
    coupling_rate = (
        0.0
        if model_id == "b0"
        else (
            0.25
            if coupling_rate_per_second is None
            else float(coupling_rate_per_second)
        )
    )
    if model_id == "b0" and coupling_rate_per_second not in (None, 0.0):
        raise S2ReferenceRunnerError("S2-C3 B0 does not accept L coupling")
    if model_id == "b2" and coupling_rate not in (0.0, 0.25):
        raise S2ReferenceRunnerError("S2-C3 B2 coupling must be 0 or 0.25 / s")
    reference_frames = tuple(
        sequence.frames[0].frame for sequence in plan.receptor_sequences
    )
    visual_count = len(reference_frames[1].carrier_ids)
    if visual_count != 6 * 4 * 3:
        raise S2ReferenceRunnerError("S2-C3 visual receptor geometry changed")
    anatomies = audio_video_dock_anatomies(
        auditory_carrier_count=len(reference_frames[0].carrier_ids),
        visual_grid_columns=6,
        visual_grid_rows=4,
    )
    field = build_shared_mcm_field(
        reference_frames,
        anatomies,
        sample_offsets=ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    )
    if model_id == "b2":
        field = attach_zero_mcm_local_development(
            field,
            MCMLocalDevelopmentContract(
                "mcm.s1b.capacity-weighted-reciprocal-accommodation.v1",
                8.0,
                coupling_rate,
            ),
        )
    start_layer_digest = field.layer.digest()
    handoff = handoff_receptor_completion_groups(
        plan.receptor_sequences,
        plan.proposal_steps,
    )
    if (
        handoff.completed_before_or_at_start_snapshot_ids
        or handoff.completed_after_horizon_snapshot_ids
        or not handoff.every_in_horizon_event_assigned_once
        or handoff.assigned_event_count != plan.source_support_count
    ):
        raise S2ReferenceRunnerError("S2-C3 receptor handoff is incomplete")
    for batch in handoff.batches:
        trajectory = map_proposal_batch_to_transient_docks(batch, field.docks)
        inputs = project_transient_docks_to_neuron_inputs(
            trajectory,
            field.docks,
        )
        distribution = ReceptorDistribution(
            CommonFieldTime(
                batch.step_time.clock_id,
                batch.step_time.start_tick,
                batch.step_time.end_tick,
            ),
            (),
        )
        field = advance_s2_controlled_receptor_batch(
            model_id,
            field,
            distribution,
            inputs,
            field_config,
            afterimage_config,
        ).field
    snapshot = field.snapshot()
    return S2ControlledWorldResult(
        world_id=plan.world_id,
        model_id=model_id,
        coupling_rate_per_second=coupling_rate,
        plan_digest=plan.digest(),
        world_digest=plan.world_digest,
        start_layer_digest=start_layer_digest,
        end_snapshot_digest=snapshot.digest(),
        source_support_count=plan.source_support_count,
        assigned_support_count=handoff.assigned_event_count,
        batch_count=len(handoff.batches),
        field=field,
    )


@dataclass(frozen=True, slots=True)
class S2ControlledC1Result:
    """Technical c1.a B0/B2 formation for the n=1 identity control."""

    world_id: str
    model_id: str
    coupling_rate_per_second: float
    plan_digest: str
    world_digest: str
    start_layer_digest: str
    end_snapshot_digest: str
    source_support_count: int
    assigned_support_count: int
    batch_count: int
    field: SharedMCMField

    def __post_init__(self) -> None:
        if self.world_id != "c1.a" or self.model_id not in ("b0", "b2"):
            raise S2ReferenceRunnerError("S2-C8 formation permits only c1.a B0/B2")
        coupling = float(self.coupling_rate_per_second)
        if coupling not in (0.0, 0.25):
            raise S2ReferenceRunnerError("S2-C8 formation coupling is invalid")
        if self.model_id == "b0" and coupling != 0.0:
            raise S2ReferenceRunnerError("S2-C8 B0 cannot carry L coupling")
        object.__setattr__(self, "coupling_rate_per_second", coupling)
        for role in (
            "plan_digest",
            "world_digest",
            "start_layer_digest",
            "end_snapshot_digest",
        ):
            if not _DIGEST.fullmatch(getattr(self, role)):
                raise S2ReferenceRunnerError(f"invalid S2-C8 formation {role}")
        for role in ("source_support_count", "assigned_support_count", "batch_count"):
            value = getattr(self, role)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise S2ReferenceRunnerError(f"invalid S2-C8 formation {role}")
        if self.source_support_count != self.assigned_support_count:
            raise S2ReferenceRunnerError("S2-C8 must assign every c1.a support once")
        if self.batch_count != 3:
            raise S2ReferenceRunnerError("S2-C8 c1.a formation requires three batches")
        if not isinstance(self.field, SharedMCMField):
            raise S2ReferenceRunnerError("S2-C8 formation requires one field")
        if self.field.snapshot().digest() != self.end_snapshot_digest:
            raise S2ReferenceRunnerError("S2-C8 formation field and digest differ")


def advance_s2c8_c1_world(
    plan: S2PreparedC1Plan,
    model_id: str,
    field_config: NeutralLocalFieldSubstrateConfig = (
        NeutralLocalFieldSubstrateConfig(1.0)
    ),
    afterimage_config: NeutralFastAfterimageConfig = (
        NeutralFastAfterimageConfig(0.5)
    ),
    *,
    coupling_rate_per_second: float | None = None,
) -> S2ControlledC1Result:
    """Advance only prepared c1.a through B0 or B2 without report."""

    if not isinstance(plan, S2PreparedC1Plan):
        raise S2ReferenceRunnerError("S2-C8 requires the canonical c1.a plan")
    if model_id not in ("b0", "b2"):
        raise S2ReferenceRunnerError("S2-C8 permits only B0 or B2")
    if field_config.response_time_seconds != 1.0:
        raise S2ReferenceRunnerError("S2-C8 field response must remain 1.0 s")
    if afterimage_config.time_constant_seconds != 0.5:
        raise S2ReferenceRunnerError("S2-C8 afterimage time must remain 0.5 s")
    coupling_rate = (
        0.0
        if model_id == "b0"
        else (
            0.25
            if coupling_rate_per_second is None
            else float(coupling_rate_per_second)
        )
    )
    if model_id == "b0" and coupling_rate_per_second not in (None, 0.0):
        raise S2ReferenceRunnerError("S2-C8 B0 does not accept L coupling")
    if model_id == "b2" and coupling_rate not in (0.0, 0.25):
        raise S2ReferenceRunnerError("S2-C8 B2 coupling must be 0 or 0.25 / s")
    reference_frames = tuple(
        sequence.frames[0].frame for sequence in plan.receptor_sequences
    )
    if len(reference_frames[1].carrier_ids) != 6 * 4 * 3:
        raise S2ReferenceRunnerError("S2-C8 visual receptor geometry changed")
    anatomies = audio_video_dock_anatomies(
        auditory_carrier_count=len(reference_frames[0].carrier_ids),
        visual_grid_columns=6,
        visual_grid_rows=4,
    )
    field = build_shared_mcm_field(
        reference_frames,
        anatomies,
        sample_offsets=ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    )
    if model_id == "b2":
        field = attach_zero_mcm_local_development(
            field,
            MCMLocalDevelopmentContract(
                "mcm.s1b.capacity-weighted-reciprocal-accommodation.v1",
                8.0,
                coupling_rate,
            ),
        )
    start_layer_digest = field.layer.digest()
    handoff = handoff_receptor_completion_groups(
        plan.receptor_sequences,
        plan.proposal_steps,
    )
    if (
        handoff.completed_before_or_at_start_snapshot_ids
        or handoff.completed_after_horizon_snapshot_ids
        or not handoff.every_in_horizon_event_assigned_once
        or handoff.assigned_event_count != plan.source_support_count
        or len(handoff.batches) != 3
    ):
        raise S2ReferenceRunnerError("S2-C8 c1.a receptor handoff is incomplete")
    for batch in handoff.batches:
        trajectory = map_proposal_batch_to_transient_docks(batch, field.docks)
        inputs = project_transient_docks_to_neuron_inputs(trajectory, field.docks)
        distribution = ReceptorDistribution(
            CommonFieldTime(
                batch.step_time.clock_id,
                batch.step_time.start_tick,
                batch.step_time.end_tick,
            ),
            (),
        )
        field = advance_s2_controlled_receptor_batch(
            model_id,
            field,
            distribution,
            inputs,
            field_config,
            afterimage_config,
        ).field
    snapshot = field.snapshot()
    return S2ControlledC1Result(
        world_id=plan.world_id,
        model_id=model_id,
        coupling_rate_per_second=coupling_rate,
        plan_digest=plan.digest(),
        world_digest=plan.world_digest,
        start_layer_digest=start_layer_digest,
        end_snapshot_digest=snapshot.digest(),
        source_support_count=plan.source_support_count,
        assigned_support_count=handoff.assigned_event_count,
        batch_count=len(handoff.batches),
        field=field,
    )


@dataclass(frozen=True, slots=True)
class S2ControlledR2C2Result:
    """Technical r2.a/c2.a B0/B2 formation for the first time contrast."""

    world_id: str
    model_id: str
    coupling_rate_per_second: float
    plan_digest: str
    world_digest: str
    start_layer_digest: str
    end_snapshot_digest: str
    source_support_count: int
    assigned_support_count: int
    batch_count: int
    field: SharedMCMField

    def __post_init__(self) -> None:
        if self.world_id not in ("r2.a", "c2.a") or self.model_id not in (
            "b0",
            "b2",
        ):
            raise S2ReferenceRunnerError("S2-C9 formation permits only r2.a/c2.a B0/B2")
        coupling = float(self.coupling_rate_per_second)
        if coupling not in (0.0, 0.25):
            raise S2ReferenceRunnerError("S2-C9 formation coupling is invalid")
        if self.model_id == "b0" and coupling != 0.0:
            raise S2ReferenceRunnerError("S2-C9 B0 cannot carry L coupling")
        object.__setattr__(self, "coupling_rate_per_second", coupling)
        for role in (
            "plan_digest",
            "world_digest",
            "start_layer_digest",
            "end_snapshot_digest",
        ):
            if not _DIGEST.fullmatch(getattr(self, role)):
                raise S2ReferenceRunnerError(f"invalid S2-C9 formation {role}")
        for role in ("source_support_count", "assigned_support_count", "batch_count"):
            value = getattr(self, role)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise S2ReferenceRunnerError(f"invalid S2-C9 formation {role}")
        expected_batches = 5 if self.world_id == "r2.a" else 3
        if self.source_support_count != self.assigned_support_count:
            raise S2ReferenceRunnerError("S2-C9 must assign every r2/c2 support once")
        if self.batch_count != expected_batches:
            raise S2ReferenceRunnerError("S2-C9 r2/c2 batch count differs")
        if not isinstance(self.field, SharedMCMField):
            raise S2ReferenceRunnerError("S2-C9 formation requires one field")
        if self.field.snapshot().digest() != self.end_snapshot_digest:
            raise S2ReferenceRunnerError("S2-C9 formation field and digest differ")


def advance_s2c9_r2c2_world(
    plan: S2PreparedR2C2Plan,
    model_id: str,
    field_config: NeutralLocalFieldSubstrateConfig = (
        NeutralLocalFieldSubstrateConfig(1.0)
    ),
    afterimage_config: NeutralFastAfterimageConfig = (
        NeutralFastAfterimageConfig(0.5)
    ),
    *,
    coupling_rate_per_second: float | None = None,
) -> S2ControlledR2C2Result:
    """Advance only prepared r2.a or c2.a through B0/B2 without report."""

    if not isinstance(plan, S2PreparedR2C2Plan):
        raise S2ReferenceRunnerError("S2-C9 requires one canonical r2/c2 plan")
    if model_id not in ("b0", "b2"):
        raise S2ReferenceRunnerError("S2-C9 permits only B0 or B2")
    if field_config.response_time_seconds != 1.0:
        raise S2ReferenceRunnerError("S2-C9 field response must remain 1.0 s")
    if afterimage_config.time_constant_seconds != 0.5:
        raise S2ReferenceRunnerError("S2-C9 afterimage time must remain 0.5 s")
    coupling_rate = (
        0.0
        if model_id == "b0"
        else (
            0.25
            if coupling_rate_per_second is None
            else float(coupling_rate_per_second)
        )
    )
    if model_id == "b0" and coupling_rate_per_second not in (None, 0.0):
        raise S2ReferenceRunnerError("S2-C9 B0 does not accept L coupling")
    if model_id == "b2" and coupling_rate not in (0.0, 0.25):
        raise S2ReferenceRunnerError("S2-C9 B2 coupling must be 0 or 0.25 / s")
    reference_frames = tuple(
        sequence.frames[0].frame for sequence in plan.receptor_sequences
    )
    if len(reference_frames[1].carrier_ids) != 6 * 4 * 3:
        raise S2ReferenceRunnerError("S2-C9 visual receptor geometry changed")
    anatomies = audio_video_dock_anatomies(
        auditory_carrier_count=len(reference_frames[0].carrier_ids),
        visual_grid_columns=6,
        visual_grid_rows=4,
    )
    field = build_shared_mcm_field(
        reference_frames,
        anatomies,
        sample_offsets=ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    )
    if model_id == "b2":
        field = attach_zero_mcm_local_development(
            field,
            MCMLocalDevelopmentContract(
                "mcm.s1b.capacity-weighted-reciprocal-accommodation.v1",
                8.0,
                coupling_rate,
            ),
        )
    start_layer_digest = field.layer.digest()
    handoff = handoff_receptor_completion_groups(
        plan.receptor_sequences,
        plan.proposal_steps,
    )
    if (
        handoff.completed_before_or_at_start_snapshot_ids
        or handoff.completed_after_horizon_snapshot_ids
        or not handoff.every_in_horizon_event_assigned_once
        or handoff.assigned_event_count != plan.source_support_count
        or len(handoff.batches) != len(plan.proposal_steps)
    ):
        raise S2ReferenceRunnerError("S2-C9 r2/c2 receptor handoff is incomplete")
    for batch in handoff.batches:
        trajectory = map_proposal_batch_to_transient_docks(batch, field.docks)
        inputs = project_transient_docks_to_neuron_inputs(trajectory, field.docks)
        distribution = ReceptorDistribution(
            CommonFieldTime(
                batch.step_time.clock_id,
                batch.step_time.start_tick,
                batch.step_time.end_tick,
            ),
            (),
        )
        field = advance_s2_controlled_receptor_batch(
            model_id,
            field,
            distribution,
            inputs,
            field_config,
            afterimage_config,
        ).field
    snapshot = field.snapshot()
    return S2ControlledR2C2Result(
        world_id=plan.world_id,
        model_id=model_id,
        coupling_rate_per_second=coupling_rate,
        plan_digest=plan.digest(),
        world_digest=plan.world_digest,
        start_layer_digest=start_layer_digest,
        end_snapshot_digest=snapshot.digest(),
        source_support_count=plan.source_support_count,
        assigned_support_count=handoff.assigned_event_count,
        batch_count=len(handoff.batches),
        field=field,
    )


@dataclass(frozen=True, slots=True)
class S2ControlledR4C4Result:
    """Technical r4.a/c4.a B0/B2 formation for the second time contrast."""

    world_id: str
    model_id: str
    coupling_rate_per_second: float
    plan_digest: str
    world_digest: str
    start_layer_digest: str
    end_snapshot_digest: str
    source_support_count: int
    assigned_support_count: int
    batch_count: int
    field: SharedMCMField

    def __post_init__(self) -> None:
        if self.world_id not in ("r4.a", "c4.a") or self.model_id not in (
            "b0",
            "b2",
        ):
            raise S2ReferenceRunnerError("S2-C10 formation permits only r4.a/c4.a B0/B2")
        coupling = float(self.coupling_rate_per_second)
        if coupling not in (0.0, 0.25):
            raise S2ReferenceRunnerError("S2-C10 formation coupling is invalid")
        if self.model_id == "b0" and coupling != 0.0:
            raise S2ReferenceRunnerError("S2-C10 B0 cannot carry L coupling")
        object.__setattr__(self, "coupling_rate_per_second", coupling)
        for role in (
            "plan_digest",
            "world_digest",
            "start_layer_digest",
            "end_snapshot_digest",
        ):
            if not _DIGEST.fullmatch(getattr(self, role)):
                raise S2ReferenceRunnerError(f"invalid S2-C10 formation {role}")
        for role in ("source_support_count", "assigned_support_count", "batch_count"):
            value = getattr(self, role)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise S2ReferenceRunnerError(f"invalid S2-C10 formation {role}")
        expected_batches = 9 if self.world_id == "r4.a" else 3
        if self.source_support_count != self.assigned_support_count:
            raise S2ReferenceRunnerError("S2-C10 must assign every r4/c4 support once")
        if self.batch_count != expected_batches:
            raise S2ReferenceRunnerError("S2-C10 r4/c4 batch count differs")
        if not isinstance(self.field, SharedMCMField):
            raise S2ReferenceRunnerError("S2-C10 formation requires one field")
        if self.field.snapshot().digest() != self.end_snapshot_digest:
            raise S2ReferenceRunnerError("S2-C10 formation field and digest differ")


def advance_s2c10_r4c4_world(
    plan: S2PreparedR4C4Plan,
    model_id: str,
    field_config: NeutralLocalFieldSubstrateConfig = (
        NeutralLocalFieldSubstrateConfig(1.0)
    ),
    afterimage_config: NeutralFastAfterimageConfig = (
        NeutralFastAfterimageConfig(0.5)
    ),
    *,
    coupling_rate_per_second: float | None = None,
) -> S2ControlledR4C4Result:
    """Advance only prepared r4.a or c4.a through B0/B2 without report."""

    if not isinstance(plan, S2PreparedR4C4Plan):
        raise S2ReferenceRunnerError("S2-C10 requires one canonical r4/c4 plan")
    if model_id not in ("b0", "b2"):
        raise S2ReferenceRunnerError("S2-C10 permits only B0 or B2")
    if field_config.response_time_seconds != 1.0:
        raise S2ReferenceRunnerError("S2-C10 field response must remain 1.0 s")
    if afterimage_config.time_constant_seconds != 0.5:
        raise S2ReferenceRunnerError("S2-C10 afterimage time must remain 0.5 s")
    coupling_rate = (
        0.0
        if model_id == "b0"
        else (
            0.25
            if coupling_rate_per_second is None
            else float(coupling_rate_per_second)
        )
    )
    if model_id == "b0" and coupling_rate_per_second not in (None, 0.0):
        raise S2ReferenceRunnerError("S2-C10 B0 does not accept L coupling")
    if model_id == "b2" and coupling_rate not in (0.0, 0.25):
        raise S2ReferenceRunnerError("S2-C10 B2 coupling must be 0 or 0.25 / s")
    reference_frames = tuple(
        sequence.frames[0].frame for sequence in plan.receptor_sequences
    )
    if len(reference_frames[1].carrier_ids) != 6 * 4 * 3:
        raise S2ReferenceRunnerError("S2-C10 visual receptor geometry changed")
    anatomies = audio_video_dock_anatomies(
        auditory_carrier_count=len(reference_frames[0].carrier_ids),
        visual_grid_columns=6,
        visual_grid_rows=4,
    )
    field = build_shared_mcm_field(
        reference_frames,
        anatomies,
        sample_offsets=ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    )
    if model_id == "b2":
        field = attach_zero_mcm_local_development(
            field,
            MCMLocalDevelopmentContract(
                "mcm.s1b.capacity-weighted-reciprocal-accommodation.v1",
                8.0,
                coupling_rate,
            ),
        )
    start_layer_digest = field.layer.digest()
    handoff = handoff_receptor_completion_groups(
        plan.receptor_sequences,
        plan.proposal_steps,
    )
    if (
        handoff.completed_before_or_at_start_snapshot_ids
        or handoff.completed_after_horizon_snapshot_ids
        or not handoff.every_in_horizon_event_assigned_once
        or handoff.assigned_event_count != plan.source_support_count
        or len(handoff.batches) != len(plan.proposal_steps)
    ):
        raise S2ReferenceRunnerError("S2-C10 r4/c4 receptor handoff is incomplete")
    for batch in handoff.batches:
        trajectory = map_proposal_batch_to_transient_docks(batch, field.docks)
        inputs = project_transient_docks_to_neuron_inputs(trajectory, field.docks)
        distribution = ReceptorDistribution(
            CommonFieldTime(
                batch.step_time.clock_id,
                batch.step_time.start_tick,
                batch.step_time.end_tick,
            ),
            (),
        )
        field = advance_s2_controlled_receptor_batch(
            model_id,
            field,
            distribution,
            inputs,
            field_config,
            afterimage_config,
        ).field
    snapshot = field.snapshot()
    return S2ControlledR4C4Result(
        world_id=plan.world_id,
        model_id=model_id,
        coupling_rate_per_second=coupling_rate,
        plan_digest=plan.digest(),
        world_digest=plan.world_digest,
        start_layer_digest=start_layer_digest,
        end_snapshot_digest=snapshot.digest(),
        source_support_count=plan.source_support_count,
        assigned_support_count=handoff.assigned_event_count,
        batch_count=len(handoff.batches),
        field=field,
    )


@dataclass(frozen=True, slots=True)
class S2ControlledR8C8Result:
    """Technical r8.a/c8.a B0/B2 formation for the third time contrast."""

    world_id: str
    model_id: str
    coupling_rate_per_second: float
    plan_digest: str
    world_digest: str
    start_layer_digest: str
    end_snapshot_digest: str
    source_support_count: int
    assigned_support_count: int
    batch_count: int
    field: SharedMCMField

    def __post_init__(self) -> None:
        if self.world_id not in ("r8.a", "c8.a") or self.model_id not in (
            "b0",
            "b2",
        ):
            raise S2ReferenceRunnerError("S2-C11 formation permits only r8.a/c8.a B0/B2")
        coupling = float(self.coupling_rate_per_second)
        if coupling not in (0.0, 0.25):
            raise S2ReferenceRunnerError("S2-C11 formation coupling is invalid")
        if self.model_id == "b0" and coupling != 0.0:
            raise S2ReferenceRunnerError("S2-C11 B0 cannot carry L coupling")
        object.__setattr__(self, "coupling_rate_per_second", coupling)
        for role in (
            "plan_digest",
            "world_digest",
            "start_layer_digest",
            "end_snapshot_digest",
        ):
            if not _DIGEST.fullmatch(getattr(self, role)):
                raise S2ReferenceRunnerError(f"invalid S2-C11 formation {role}")
        for role in ("source_support_count", "assigned_support_count", "batch_count"):
            value = getattr(self, role)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise S2ReferenceRunnerError(f"invalid S2-C11 formation {role}")
        expected_batches = 17 if self.world_id == "r8.a" else 3
        if self.source_support_count != self.assigned_support_count:
            raise S2ReferenceRunnerError("S2-C11 must assign every r8/c8 support once")
        if self.batch_count != expected_batches:
            raise S2ReferenceRunnerError("S2-C11 r8/c8 batch count differs")
        if not isinstance(self.field, SharedMCMField):
            raise S2ReferenceRunnerError("S2-C11 formation requires one field")
        if self.field.snapshot().digest() != self.end_snapshot_digest:
            raise S2ReferenceRunnerError("S2-C11 formation field and digest differ")


def advance_s2c11_r8c8_world(
    plan: S2PreparedR8C8Plan,
    model_id: str,
    field_config: NeutralLocalFieldSubstrateConfig = (
        NeutralLocalFieldSubstrateConfig(1.0)
    ),
    afterimage_config: NeutralFastAfterimageConfig = (
        NeutralFastAfterimageConfig(0.5)
    ),
    *,
    coupling_rate_per_second: float | None = None,
) -> S2ControlledR8C8Result:
    """Advance only prepared r8.a or c8.a through B0/B2 without report."""

    if not isinstance(plan, S2PreparedR8C8Plan):
        raise S2ReferenceRunnerError("S2-C11 requires one canonical r8/c8 plan")
    if model_id not in ("b0", "b2"):
        raise S2ReferenceRunnerError("S2-C11 permits only B0 or B2")
    if field_config.response_time_seconds != 1.0:
        raise S2ReferenceRunnerError("S2-C11 field response must remain 1.0 s")
    if afterimage_config.time_constant_seconds != 0.5:
        raise S2ReferenceRunnerError("S2-C11 afterimage time must remain 0.5 s")
    coupling_rate = (
        0.0
        if model_id == "b0"
        else (
            0.25
            if coupling_rate_per_second is None
            else float(coupling_rate_per_second)
        )
    )
    if model_id == "b0" and coupling_rate_per_second not in (None, 0.0):
        raise S2ReferenceRunnerError("S2-C11 B0 does not accept L coupling")
    if model_id == "b2" and coupling_rate not in (0.0, 0.25):
        raise S2ReferenceRunnerError("S2-C11 B2 coupling must be 0 or 0.25 / s")
    reference_frames = tuple(
        sequence.frames[0].frame for sequence in plan.receptor_sequences
    )
    if len(reference_frames[1].carrier_ids) != 6 * 4 * 3:
        raise S2ReferenceRunnerError("S2-C11 visual receptor geometry changed")
    anatomies = audio_video_dock_anatomies(
        auditory_carrier_count=len(reference_frames[0].carrier_ids),
        visual_grid_columns=6,
        visual_grid_rows=4,
    )
    field = build_shared_mcm_field(
        reference_frames,
        anatomies,
        sample_offsets=ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    )
    if model_id == "b2":
        field = attach_zero_mcm_local_development(
            field,
            MCMLocalDevelopmentContract(
                "mcm.s1b.capacity-weighted-reciprocal-accommodation.v1",
                8.0,
                coupling_rate,
            ),
        )
    start_layer_digest = field.layer.digest()
    handoff = handoff_receptor_completion_groups(
        plan.receptor_sequences,
        plan.proposal_steps,
    )
    if (
        handoff.completed_before_or_at_start_snapshot_ids
        or handoff.completed_after_horizon_snapshot_ids
        or not handoff.every_in_horizon_event_assigned_once
        or handoff.assigned_event_count != plan.source_support_count
        or len(handoff.batches) != len(plan.proposal_steps)
    ):
        raise S2ReferenceRunnerError("S2-C11 r8/c8 receptor handoff is incomplete")
    for batch in handoff.batches:
        trajectory = map_proposal_batch_to_transient_docks(batch, field.docks)
        inputs = project_transient_docks_to_neuron_inputs(trajectory, field.docks)
        distribution = ReceptorDistribution(
            CommonFieldTime(
                batch.step_time.clock_id,
                batch.step_time.start_tick,
                batch.step_time.end_tick,
            ),
            (),
        )
        field = advance_s2_controlled_receptor_batch(
            model_id,
            field,
            distribution,
            inputs,
            field_config,
            afterimage_config,
        ).field
    snapshot = field.snapshot()
    return S2ControlledR8C8Result(
        world_id=plan.world_id,
        model_id=model_id,
        coupling_rate_per_second=coupling_rate,
        plan_digest=plan.digest(),
        world_digest=plan.world_digest,
        start_layer_digest=start_layer_digest,
        end_snapshot_digest=snapshot.digest(),
        source_support_count=plan.source_support_count,
        assigned_support_count=handoff.assigned_event_count,
        batch_count=len(handoff.batches),
        field=field,
    )


@dataclass(frozen=True, slots=True)
class S2ControlledR8BC8BResult:
    """Technical r8.b/c8.b B0/B2 formation for the second world pair."""

    world_id: str
    model_id: str
    coupling_rate_per_second: float
    plan_digest: str
    world_digest: str
    start_layer_digest: str
    end_snapshot_digest: str
    source_support_count: int
    assigned_support_count: int
    batch_count: int
    field: SharedMCMField

    def __post_init__(self) -> None:
        if self.world_id not in ("r8.b", "c8.b") or self.model_id not in (
            "b0",
            "b2",
        ):
            raise S2ReferenceRunnerError("S2-C13 formation permits only r8.b/c8.b B0/B2")
        coupling = float(self.coupling_rate_per_second)
        if coupling not in (0.0, 0.25):
            raise S2ReferenceRunnerError("S2-C13 formation coupling is invalid")
        if self.model_id == "b0" and coupling != 0.0:
            raise S2ReferenceRunnerError("S2-C13 B0 cannot carry L coupling")
        object.__setattr__(self, "coupling_rate_per_second", coupling)
        for role in (
            "plan_digest",
            "world_digest",
            "start_layer_digest",
            "end_snapshot_digest",
        ):
            if not _DIGEST.fullmatch(getattr(self, role)):
                raise S2ReferenceRunnerError(f"invalid S2-C13 formation {role}")
        for role in ("source_support_count", "assigned_support_count", "batch_count"):
            value = getattr(self, role)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise S2ReferenceRunnerError(f"invalid S2-C13 formation {role}")
        expected_batches = 17 if self.world_id == "r8.b" else 3
        if self.source_support_count != self.assigned_support_count:
            raise S2ReferenceRunnerError("S2-C13 must assign every r8.b/c8.b support once")
        if self.batch_count != expected_batches:
            raise S2ReferenceRunnerError("S2-C13 r8.b/c8.b batch count differs")
        if not isinstance(self.field, SharedMCMField):
            raise S2ReferenceRunnerError("S2-C13 formation requires one field")
        if self.field.snapshot().digest() != self.end_snapshot_digest:
            raise S2ReferenceRunnerError("S2-C13 formation field and digest differ")


def advance_s2c13_r8bc8b_world(
    plan: S2PreparedR8BC8BPlan,
    model_id: str,
    field_config: NeutralLocalFieldSubstrateConfig = (
        NeutralLocalFieldSubstrateConfig(1.0)
    ),
    afterimage_config: NeutralFastAfterimageConfig = (
        NeutralFastAfterimageConfig(0.5)
    ),
    *,
    coupling_rate_per_second: float | None = None,
) -> S2ControlledR8BC8BResult:
    """Advance only prepared r8.b or c8.b through B0/B2 without report."""

    if not isinstance(plan, S2PreparedR8BC8BPlan):
        raise S2ReferenceRunnerError("S2-C13 requires one canonical r8.b/c8.b plan")
    if model_id not in ("b0", "b2"):
        raise S2ReferenceRunnerError("S2-C13 permits only B0 or B2")
    if field_config.response_time_seconds != 1.0:
        raise S2ReferenceRunnerError("S2-C13 field response must remain 1.0 s")
    if afterimage_config.time_constant_seconds != 0.5:
        raise S2ReferenceRunnerError("S2-C13 afterimage time must remain 0.5 s")
    coupling_rate = (
        0.0
        if model_id == "b0"
        else (
            0.25
            if coupling_rate_per_second is None
            else float(coupling_rate_per_second)
        )
    )
    if model_id == "b0" and coupling_rate_per_second not in (None, 0.0):
        raise S2ReferenceRunnerError("S2-C13 B0 does not accept L coupling")
    if model_id == "b2" and coupling_rate not in (0.0, 0.25):
        raise S2ReferenceRunnerError("S2-C13 B2 coupling must be 0 or 0.25 / s")
    reference_frames = tuple(
        sequence.frames[0].frame for sequence in plan.receptor_sequences
    )
    if len(reference_frames[1].carrier_ids) != 6 * 4 * 3:
        raise S2ReferenceRunnerError("S2-C13 visual receptor geometry changed")
    anatomies = audio_video_dock_anatomies(
        auditory_carrier_count=len(reference_frames[0].carrier_ids),
        visual_grid_columns=6,
        visual_grid_rows=4,
    )
    field = build_shared_mcm_field(
        reference_frames,
        anatomies,
        sample_offsets=ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    )
    if model_id == "b2":
        field = attach_zero_mcm_local_development(
            field,
            MCMLocalDevelopmentContract(
                "mcm.s1b.capacity-weighted-reciprocal-accommodation.v1",
                8.0,
                coupling_rate,
            ),
        )
    start_layer_digest = field.layer.digest()
    handoff = handoff_receptor_completion_groups(
        plan.receptor_sequences,
        plan.proposal_steps,
    )
    if (
        handoff.completed_before_or_at_start_snapshot_ids
        or handoff.completed_after_horizon_snapshot_ids
        or not handoff.every_in_horizon_event_assigned_once
        or handoff.assigned_event_count != plan.source_support_count
        or len(handoff.batches) != len(plan.proposal_steps)
    ):
        raise S2ReferenceRunnerError("S2-C13 r8.b/c8.b receptor handoff is incomplete")
    for batch in handoff.batches:
        trajectory = map_proposal_batch_to_transient_docks(batch, field.docks)
        inputs = project_transient_docks_to_neuron_inputs(trajectory, field.docks)
        distribution = ReceptorDistribution(
            CommonFieldTime(
                batch.step_time.clock_id,
                batch.step_time.start_tick,
                batch.step_time.end_tick,
            ),
            (),
        )
        field = advance_s2_controlled_receptor_batch(
            model_id,
            field,
            distribution,
            inputs,
            field_config,
            afterimage_config,
        ).field
    snapshot = field.snapshot()
    return S2ControlledR8BC8BResult(
        world_id=plan.world_id,
        model_id=model_id,
        coupling_rate_per_second=coupling_rate,
        plan_digest=plan.digest(),
        world_digest=plan.world_digest,
        start_layer_digest=start_layer_digest,
        end_snapshot_digest=snapshot.digest(),
        source_support_count=plan.source_support_count,
        assigned_support_count=handoff.assigned_event_count,
        batch_count=len(handoff.batches),
        field=field,
    )


@dataclass(frozen=True, slots=True)
class S2R1ProbeResult:
    """Technical r1.a plus P result without N8 comparison or interpretation."""

    world_id: str
    model_id: str
    coupling_rate_per_second: float
    formation_snapshot_digest: str
    equalized_snapshot_digest: str
    probe_plan_digest: str
    probe_digest: str
    end_snapshot_digest: str
    probe_support_count: int
    assigned_probe_support_count: int
    development_digest_before_probe: str | None
    field: SharedMCMField

    def __post_init__(self) -> None:
        if self.world_id != "r1.a" or self.model_id not in ("b0", "b2"):
            raise S2ReferenceRunnerError("S2-C4 result permits only r1.a B0/B2")
        coupling = float(self.coupling_rate_per_second)
        if coupling not in (0.0, 0.25):
            raise S2ReferenceRunnerError("S2-C4 coupling is invalid")
        if self.model_id == "b0" and coupling != 0.0:
            raise S2ReferenceRunnerError("S2-C4 B0 cannot carry L coupling")
        object.__setattr__(self, "coupling_rate_per_second", coupling)
        for role in (
            "formation_snapshot_digest",
            "equalized_snapshot_digest",
            "probe_plan_digest",
            "probe_digest",
            "end_snapshot_digest",
        ):
            if not _DIGEST.fullmatch(getattr(self, role)):
                raise S2ReferenceRunnerError(f"invalid S2-C4 {role}")
        if self.development_digest_before_probe is not None and not _DIGEST.fullmatch(
            self.development_digest_before_probe
        ):
            raise S2ReferenceRunnerError("invalid S2-C4 development digest")
        if self.model_id == "b0" and self.development_digest_before_probe is not None:
            raise S2ReferenceRunnerError("S2-C4 B0 cannot expose an L digest")
        if self.model_id == "b2" and self.development_digest_before_probe is None:
            raise S2ReferenceRunnerError("S2-C4 B2 requires an L digest")
        if (
            self.probe_support_count < 1
            or self.probe_support_count != self.assigned_probe_support_count
        ):
            raise S2ReferenceRunnerError("S2-C4 must assign every probe support once")
        if not isinstance(self.field, SharedMCMField):
            raise S2ReferenceRunnerError("S2-C4 result requires one field")
        if self.field.snapshot().digest() != self.end_snapshot_digest:
            raise S2ReferenceRunnerError("S2-C4 result field and digest differ")


def advance_s2c4_r1_probe(
    formation: S2ControlledWorldResult,
    probe_plan: S2PreparedProbePlan,
    field_config: NeutralLocalFieldSubstrateConfig = (
        NeutralLocalFieldSubstrateConfig(1.0)
    ),
    afterimage_config: NeutralFastAfterimageConfig = (
        NeutralFastAfterimageConfig(0.5)
    ),
) -> S2R1ProbeResult:
    """Equalize r1.a S/H and continue only canonical P through B0 or B2."""

    if not isinstance(formation, S2ControlledWorldResult):
        raise S2ReferenceRunnerError("S2-C4 requires one S2-C3 formation")
    if not isinstance(probe_plan, S2PreparedProbePlan):
        raise S2ReferenceRunnerError("S2-C4 requires the canonical probe plan")
    if field_config.response_time_seconds != 1.0:
        raise S2ReferenceRunnerError("S2-C4 field response must remain 1.0 s")
    if afterimage_config.time_constant_seconds != 0.5:
        raise S2ReferenceRunnerError("S2-C4 afterimage time must remain 0.5 s")
    if formation.field.last_distribution is None:
        raise S2ReferenceRunnerError("S2-C4 requires a completed r1.a formation")
    previous_time = formation.field.last_distribution.field_time
    if (
        previous_time.clock_id != probe_plan.clock_id
        or previous_time.window_end_tick != probe_plan.proposal_step.start_tick
    ):
        raise S2ReferenceRunnerError("S2-C4 probe must continue r1.a at 8.0 s")

    equalized = equalize_fast_state_for_probe(formation.field)
    if any(
        neuron.activation != 0.0 or neuron.afterimage != 0.0
        for neuron in equalized.layer.neurons
    ):
        raise S2ReferenceRunnerError("S2-C4 failed to equalize S/H exactly")
    development_digest = (
        None
        if equalized.development is None
        else equalized.development.digest()
    )
    if formation.field.development != equalized.development:
        raise S2ReferenceRunnerError("S2-C4 equalization changed L")

    handoff = handoff_receptor_completion_groups(
        probe_plan.receptor_sequences,
        (probe_plan.proposal_step,),
    )
    if (
        handoff.completed_before_or_at_start_snapshot_ids
        or handoff.completed_after_horizon_snapshot_ids
        or not handoff.every_in_horizon_event_assigned_once
        or handoff.assigned_event_count != probe_plan.source_support_count
        or len(handoff.batches) != 1
    ):
        raise S2ReferenceRunnerError("S2-C4 probe handoff is incomplete")
    batch = handoff.batches[0]
    trajectory = map_proposal_batch_to_transient_docks(batch, equalized.docks)
    inputs = project_transient_docks_to_neuron_inputs(
        trajectory,
        equalized.docks,
    )
    distribution = ReceptorDistribution(
        CommonFieldTime(
            batch.step_time.clock_id,
            batch.step_time.start_tick,
            batch.step_time.end_tick,
        ),
        (),
    )
    probed = advance_s2_controlled_receptor_batch(
        formation.model_id,
        equalized,
        distribution,
        inputs,
        field_config,
        afterimage_config,
    ).field
    return S2R1ProbeResult(
        world_id=formation.world_id,
        model_id=formation.model_id,
        coupling_rate_per_second=formation.coupling_rate_per_second,
        formation_snapshot_digest=formation.end_snapshot_digest,
        equalized_snapshot_digest=equalized.snapshot().digest(),
        probe_plan_digest=probe_plan.digest(),
        probe_digest=probe_plan.probe_digest,
        end_snapshot_digest=probed.snapshot().digest(),
        probe_support_count=probe_plan.source_support_count,
        assigned_probe_support_count=handoff.assigned_event_count,
        development_digest_before_probe=development_digest,
        field=probed,
    )


@dataclass(frozen=True, slots=True)
class S2ControlledN8Result:
    """Technical n8 B0/B2 formation without comparison or interpretation."""

    world_id: str
    model_id: str
    coupling_rate_per_second: float
    plan_digest: str
    world_digest: str
    start_layer_digest: str
    end_snapshot_digest: str
    source_support_count: int
    assigned_support_count: int
    batch_count: int
    field: SharedMCMField

    def __post_init__(self) -> None:
        if self.world_id != "n8" or self.model_id not in ("b0", "b2"):
            raise S2ReferenceRunnerError("S2-C5 formation permits only n8 B0/B2")
        coupling = float(self.coupling_rate_per_second)
        if coupling not in (0.0, 0.25):
            raise S2ReferenceRunnerError("S2-C5 formation coupling is invalid")
        if self.model_id == "b0" and coupling != 0.0:
            raise S2ReferenceRunnerError("S2-C5 B0 cannot carry L coupling")
        object.__setattr__(self, "coupling_rate_per_second", coupling)
        for role in (
            "plan_digest",
            "world_digest",
            "start_layer_digest",
            "end_snapshot_digest",
        ):
            if not _DIGEST.fullmatch(getattr(self, role)):
                raise S2ReferenceRunnerError(f"invalid S2-C5 formation {role}")
        for role in (
            "source_support_count",
            "assigned_support_count",
            "batch_count",
        ):
            value = getattr(self, role)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise S2ReferenceRunnerError(f"invalid S2-C5 formation {role}")
        if self.source_support_count != self.assigned_support_count:
            raise S2ReferenceRunnerError("S2-C5 must assign every n8 support once")
        if self.batch_count != 1:
            raise S2ReferenceRunnerError("S2-C5 n8 formation requires one batch")
        if not isinstance(self.field, SharedMCMField):
            raise S2ReferenceRunnerError("S2-C5 formation requires one field")
        if self.field.snapshot().digest() != self.end_snapshot_digest:
            raise S2ReferenceRunnerError("S2-C5 formation field and digest differ")


def advance_s2c5_n8_world(
    plan: S2PreparedN8Plan,
    model_id: str,
    field_config: NeutralLocalFieldSubstrateConfig = (
        NeutralLocalFieldSubstrateConfig(1.0)
    ),
    afterimage_config: NeutralFastAfterimageConfig = (
        NeutralFastAfterimageConfig(0.5)
    ),
    *,
    coupling_rate_per_second: float | None = None,
) -> S2ControlledN8Result:
    """Advance only prepared n8 through B0 or B2 without probe or report."""

    if not isinstance(plan, S2PreparedN8Plan):
        raise S2ReferenceRunnerError("S2-C5 requires the canonical n8 plan")
    if model_id not in ("b0", "b2"):
        raise S2ReferenceRunnerError("S2-C5 permits only B0 or B2")
    if field_config.response_time_seconds != 1.0:
        raise S2ReferenceRunnerError("S2-C5 field response must remain 1.0 s")
    if afterimage_config.time_constant_seconds != 0.5:
        raise S2ReferenceRunnerError("S2-C5 afterimage time must remain 0.5 s")
    coupling_rate = (
        0.0
        if model_id == "b0"
        else (
            0.25
            if coupling_rate_per_second is None
            else float(coupling_rate_per_second)
        )
    )
    if model_id == "b0" and coupling_rate_per_second not in (None, 0.0):
        raise S2ReferenceRunnerError("S2-C5 B0 does not accept L coupling")
    if model_id == "b2" and coupling_rate not in (0.0, 0.25):
        raise S2ReferenceRunnerError("S2-C5 B2 coupling must be 0 or 0.25 / s")
    reference_frames = tuple(
        sequence.frames[0].frame for sequence in plan.receptor_sequences
    )
    if len(reference_frames[1].carrier_ids) != 6 * 4 * 3:
        raise S2ReferenceRunnerError("S2-C5 visual receptor geometry changed")
    anatomies = audio_video_dock_anatomies(
        auditory_carrier_count=len(reference_frames[0].carrier_ids),
        visual_grid_columns=6,
        visual_grid_rows=4,
    )
    field = build_shared_mcm_field(
        reference_frames,
        anatomies,
        sample_offsets=ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    )
    if model_id == "b2":
        field = attach_zero_mcm_local_development(
            field,
            MCMLocalDevelopmentContract(
                "mcm.s1b.capacity-weighted-reciprocal-accommodation.v1",
                8.0,
                coupling_rate,
            ),
        )
    start_layer_digest = field.layer.digest()
    handoff = handoff_receptor_completion_groups(
        plan.receptor_sequences,
        (plan.proposal_step,),
    )
    if (
        handoff.completed_before_or_at_start_snapshot_ids
        or handoff.completed_after_horizon_snapshot_ids
        or not handoff.every_in_horizon_event_assigned_once
        or handoff.assigned_event_count != plan.source_support_count
        or len(handoff.batches) != 1
    ):
        raise S2ReferenceRunnerError("S2-C5 n8 receptor handoff is incomplete")
    batch = handoff.batches[0]
    trajectory = map_proposal_batch_to_transient_docks(batch, field.docks)
    inputs = project_transient_docks_to_neuron_inputs(trajectory, field.docks)
    distribution = ReceptorDistribution(
        CommonFieldTime(
            batch.step_time.clock_id,
            batch.step_time.start_tick,
            batch.step_time.end_tick,
        ),
        (),
    )
    field = advance_s2_controlled_receptor_batch(
        model_id,
        field,
        distribution,
        inputs,
        field_config,
        afterimage_config,
    ).field
    snapshot = field.snapshot()
    return S2ControlledN8Result(
        world_id=plan.world_id,
        model_id=model_id,
        coupling_rate_per_second=coupling_rate,
        plan_digest=plan.digest(),
        world_digest=plan.world_digest,
        start_layer_digest=start_layer_digest,
        end_snapshot_digest=snapshot.digest(),
        source_support_count=plan.source_support_count,
        assigned_support_count=handoff.assigned_event_count,
        batch_count=len(handoff.batches),
        field=field,
    )


@dataclass(frozen=True, slots=True)
class S2N8ProbeResult:
    """Technical n8 plus P result without history comparison or decision."""

    world_id: str
    model_id: str
    coupling_rate_per_second: float
    formation_snapshot_digest: str
    equalized_snapshot_digest: str
    probe_plan_digest: str
    probe_digest: str
    end_snapshot_digest: str
    probe_support_count: int
    assigned_probe_support_count: int
    development_digest_before_probe: str | None
    field: SharedMCMField

    def __post_init__(self) -> None:
        if self.world_id != "n8" or self.model_id not in ("b0", "b2"):
            raise S2ReferenceRunnerError("S2-C5 probe permits only n8 B0/B2")
        coupling = float(self.coupling_rate_per_second)
        if coupling not in (0.0, 0.25):
            raise S2ReferenceRunnerError("S2-C5 probe coupling is invalid")
        if self.model_id == "b0" and coupling != 0.0:
            raise S2ReferenceRunnerError("S2-C5 probe B0 cannot carry L coupling")
        object.__setattr__(self, "coupling_rate_per_second", coupling)
        for role in (
            "formation_snapshot_digest",
            "equalized_snapshot_digest",
            "probe_plan_digest",
            "probe_digest",
            "end_snapshot_digest",
        ):
            if not _DIGEST.fullmatch(getattr(self, role)):
                raise S2ReferenceRunnerError(f"invalid S2-C5 probe {role}")
        if self.development_digest_before_probe is not None and not _DIGEST.fullmatch(
            self.development_digest_before_probe
        ):
            raise S2ReferenceRunnerError("invalid S2-C5 probe development digest")
        if self.model_id == "b0" and self.development_digest_before_probe is not None:
            raise S2ReferenceRunnerError("S2-C5 probe B0 cannot expose an L digest")
        if self.model_id == "b2" and self.development_digest_before_probe is None:
            raise S2ReferenceRunnerError("S2-C5 probe B2 requires an L digest")
        if (
            self.probe_support_count < 1
            or self.probe_support_count != self.assigned_probe_support_count
        ):
            raise S2ReferenceRunnerError("S2-C5 must assign every probe support once")
        if not isinstance(self.field, SharedMCMField):
            raise S2ReferenceRunnerError("S2-C5 probe requires one field")
        if self.field.snapshot().digest() != self.end_snapshot_digest:
            raise S2ReferenceRunnerError("S2-C5 probe field and digest differ")


def advance_s2c5_n8_probe(
    formation: S2ControlledN8Result,
    probe_plan: S2PreparedProbePlan,
    field_config: NeutralLocalFieldSubstrateConfig = (
        NeutralLocalFieldSubstrateConfig(1.0)
    ),
    afterimage_config: NeutralFastAfterimageConfig = (
        NeutralFastAfterimageConfig(0.5)
    ),
) -> S2N8ProbeResult:
    """Equalize n8 S/H and continue canonical P through B0 or B2."""

    if not isinstance(formation, S2ControlledN8Result):
        raise S2ReferenceRunnerError("S2-C5 requires one n8 formation")
    if not isinstance(probe_plan, S2PreparedProbePlan):
        raise S2ReferenceRunnerError("S2-C5 requires the canonical probe plan")
    if field_config.response_time_seconds != 1.0:
        raise S2ReferenceRunnerError("S2-C5 field response must remain 1.0 s")
    if afterimage_config.time_constant_seconds != 0.5:
        raise S2ReferenceRunnerError("S2-C5 afterimage time must remain 0.5 s")
    if formation.field.last_distribution is None:
        raise S2ReferenceRunnerError("S2-C5 requires a completed n8 formation")
    previous_time = formation.field.last_distribution.field_time
    if (
        previous_time.clock_id != probe_plan.clock_id
        or previous_time.window_end_tick != probe_plan.proposal_step.start_tick
    ):
        raise S2ReferenceRunnerError("S2-C5 probe must continue n8 at 8.0 s")

    equalized = equalize_fast_state_for_probe(formation.field)
    if any(
        neuron.activation != 0.0 or neuron.afterimage != 0.0
        for neuron in equalized.layer.neurons
    ):
        raise S2ReferenceRunnerError("S2-C5 failed to equalize S/H exactly")
    development_digest = (
        None if equalized.development is None else equalized.development.digest()
    )
    if formation.field.development != equalized.development:
        raise S2ReferenceRunnerError("S2-C5 equalization changed L")

    handoff = handoff_receptor_completion_groups(
        probe_plan.receptor_sequences,
        (probe_plan.proposal_step,),
    )
    if (
        handoff.completed_before_or_at_start_snapshot_ids
        or handoff.completed_after_horizon_snapshot_ids
        or not handoff.every_in_horizon_event_assigned_once
        or handoff.assigned_event_count != probe_plan.source_support_count
        or len(handoff.batches) != 1
    ):
        raise S2ReferenceRunnerError("S2-C5 probe handoff is incomplete")
    batch = handoff.batches[0]
    trajectory = map_proposal_batch_to_transient_docks(batch, equalized.docks)
    inputs = project_transient_docks_to_neuron_inputs(trajectory, equalized.docks)
    distribution = ReceptorDistribution(
        CommonFieldTime(
            batch.step_time.clock_id,
            batch.step_time.start_tick,
            batch.step_time.end_tick,
        ),
        (),
    )
    probed = advance_s2_controlled_receptor_batch(
        formation.model_id,
        equalized,
        distribution,
        inputs,
        field_config,
        afterimage_config,
    ).field
    return S2N8ProbeResult(
        world_id=formation.world_id,
        model_id=formation.model_id,
        coupling_rate_per_second=formation.coupling_rate_per_second,
        formation_snapshot_digest=formation.end_snapshot_digest,
        equalized_snapshot_digest=equalized.snapshot().digest(),
        probe_plan_digest=probe_plan.digest(),
        probe_digest=probe_plan.probe_digest,
        end_snapshot_digest=probed.snapshot().digest(),
        probe_support_count=probe_plan.source_support_count,
        assigned_probe_support_count=handoff.assigned_event_count,
        development_digest_before_probe=development_digest,
        field=probed,
    )


@dataclass(frozen=True, slots=True)
class S2ProbeTraceSample:
    completion_tick: int
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]

    def __post_init__(self) -> None:
        if (
            isinstance(self.completion_tick, bool)
            or not isinstance(self.completion_tick, int)
            or self.completion_tick < 0
        ):
            raise S2ReferenceRunnerError("S2-C6 completion tick is invalid")
        activation = tuple(float(value) for value in self.activation)
        afterimage = tuple(float(value) for value in self.afterimage)
        if not activation or len(activation) != len(afterimage):
            raise S2ReferenceRunnerError("S2-C6 sample requires matching S/H vectors")
        if any(
            not math.isfinite(value) or abs(value) > 1.0 + 1e-12
            for value in (*activation, *afterimage)
        ):
            raise S2ReferenceRunnerError("S2-C6 sample left the finite field domain")
        object.__setattr__(self, "activation", activation)
        object.__setattr__(self, "afterimage", afterimage)


@dataclass(frozen=True, slots=True)
class S2ProbeTrace:
    world_id: str
    model_id: str
    coupling_rate_per_second: float
    probe_plan_digest: str
    probe_digest: str
    formation_snapshot_digest: str
    equalized_snapshot_digest: str
    end_snapshot_digest: str
    clock_id: str
    ticks_per_second: float
    samples: tuple[S2ProbeTraceSample, ...]

    def __post_init__(self) -> None:
        if self.world_id not in (
            "r1.a",
            "c1.a",
            "r2.a",
            "c2.a",
            "r4.a",
            "c4.a",
            "r8.a",
            "c8.a",
            "r8.b",
            "c8.b",
            "n8",
        ) or (
            self.model_id not in ("b0", "b2")
        ):
            raise S2ReferenceRunnerError(
                "S2 trace permits only bound R/C/N8 B0/B2 worlds"
            )
        coupling = float(self.coupling_rate_per_second)
        if coupling not in (0.0, 0.25):
            raise S2ReferenceRunnerError("S2-C6 trace coupling is invalid")
        if self.model_id == "b0" and coupling != 0.0:
            raise S2ReferenceRunnerError("S2-C6 B0 trace cannot carry L coupling")
        rate = float(self.ticks_per_second)
        if not math.isfinite(rate) or rate <= 0.0:
            raise S2ReferenceRunnerError("S2-C6 trace tick rate is invalid")
        for role in (
            "probe_plan_digest",
            "probe_digest",
            "formation_snapshot_digest",
            "equalized_snapshot_digest",
            "end_snapshot_digest",
        ):
            if not _DIGEST.fullmatch(getattr(self, role)):
                raise S2ReferenceRunnerError(f"invalid S2-C6 trace {role}")
        samples = tuple(self.samples)
        if not samples or any(not isinstance(item, S2ProbeTraceSample) for item in samples):
            raise S2ReferenceRunnerError("S2-C6 trace requires passive S/H samples")
        ticks = tuple(item.completion_tick for item in samples)
        if ticks != tuple(sorted(set(ticks))):
            raise S2ReferenceRunnerError("S2-C6 trace ticks must be unique and ordered")
        vector_sizes = {len(item.activation) for item in samples}
        if len(vector_sizes) != 1:
            raise S2ReferenceRunnerError("S2-C6 trace field anatomy changed")
        object.__setattr__(self, "coupling_rate_per_second", coupling)
        object.__setattr__(self, "ticks_per_second", rate)
        object.__setattr__(self, "samples", samples)

    @property
    def completion_ticks(self) -> tuple[int, ...]:
        return tuple(item.completion_tick for item in self.samples)


@dataclass(frozen=True, slots=True)
class S2ProbeTracePair:
    history: S2ProbeTrace
    neutral: S2ProbeTrace

    def __post_init__(self) -> None:
        if not isinstance(self.history, S2ProbeTrace) or not isinstance(
            self.neutral,
            S2ProbeTrace,
        ):
            raise S2ReferenceRunnerError("S2-C6 pair requires two probe traces")
        if self.history.world_id != "r1.a" or self.neutral.world_id != "n8":
            raise S2ReferenceRunnerError("S2-C6 pair order must remain r1.a then n8")
        if (
            self.history.model_id != self.neutral.model_id
            or self.history.coupling_rate_per_second
            != self.neutral.coupling_rate_per_second
        ):
            raise S2ReferenceRunnerError("S2-C6 pair requires one identical model arm")
        if (
            self.history.probe_plan_digest != self.neutral.probe_plan_digest
            or self.history.probe_digest != self.neutral.probe_digest
            or self.history.clock_id != self.neutral.clock_id
            or self.history.ticks_per_second != self.neutral.ticks_per_second
            or self.history.completion_ticks != self.neutral.completion_ticks
        ):
            raise S2ReferenceRunnerError("S2-C6 pair requires one identical probe support")


def _observe_s2c6_probe_trace(
    formation: (
        S2ControlledWorldResult
        | S2ControlledC1Result
        | S2ControlledR2C2Result
        | S2ControlledR4C4Result
        | S2ControlledR8C8Result
        | S2ControlledR8BC8BResult
        | S2ControlledN8Result
    ),
    probe_plan: S2PreparedProbePlan,
    field_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
) -> S2ProbeTrace:
    if not isinstance(
        formation,
        (
            S2ControlledWorldResult,
            S2ControlledC1Result,
            S2ControlledR2C2Result,
            S2ControlledR4C4Result,
            S2ControlledR8C8Result,
            S2ControlledR8BC8BResult,
            S2ControlledN8Result,
        ),
    ):
        raise S2ReferenceRunnerError("S2 trace requires one bound formation")
    if not isinstance(probe_plan, S2PreparedProbePlan):
        raise S2ReferenceRunnerError("S2-C6 requires the canonical probe plan")
    if formation.field.last_distribution is None:
        raise S2ReferenceRunnerError("S2-C6 requires a completed formation")
    previous_time = formation.field.last_distribution.field_time
    if (
        previous_time.clock_id != probe_plan.clock_id
        or previous_time.window_end_tick != probe_plan.proposal_step.start_tick
    ):
        raise S2ReferenceRunnerError("S2-C6 probe must continue formation at 8.0 s")

    equalized = equalize_fast_state_for_probe(formation.field)
    handoff = handoff_receptor_completion_groups(
        probe_plan.receptor_sequences,
        (probe_plan.proposal_step,),
    )
    if (
        handoff.completed_before_or_at_start_snapshot_ids
        or handoff.completed_after_horizon_snapshot_ids
        or not handoff.every_in_horizon_event_assigned_once
        or handoff.assigned_event_count != probe_plan.source_support_count
        or len(handoff.batches) != 1
    ):
        raise S2ReferenceRunnerError("S2-C6 probe handoff is incomplete")
    batch = handoff.batches[0]
    trajectory = map_proposal_batch_to_transient_docks(batch, equalized.docks)
    inputs = project_transient_docks_to_neuron_inputs(trajectory, equalized.docks)
    distribution = ReceptorDistribution(
        CommonFieldTime(
            batch.step_time.clock_id,
            batch.step_time.start_tick,
            batch.step_time.end_tick,
        ),
        (),
    )
    samples: list[S2ProbeTraceSample] = []

    def observer(tick: int, activation: object, afterimage: object, _local: object) -> None:
        samples.append(
            S2ProbeTraceSample(
                tick,
                tuple(float(value) for value in activation),
                tuple(float(value) for value in afterimage),
            )
        )

    probed = advance_s2_controlled_receptor_batch(
        formation.model_id,
        equalized,
        distribution,
        inputs,
        field_config,
        afterimage_config,
        _state_observer=observer,
    ).field
    expected_ticks = tuple(group.completion_tick for group in batch.completion_groups)
    if tuple(item.completion_tick for item in samples) != expected_ticks:
        raise S2ReferenceRunnerError("S2-C6 observer support differs from probe completions")
    return S2ProbeTrace(
        world_id=formation.world_id,
        model_id=formation.model_id,
        coupling_rate_per_second=formation.coupling_rate_per_second,
        probe_plan_digest=probe_plan.digest(),
        probe_digest=probe_plan.probe_digest,
        formation_snapshot_digest=formation.end_snapshot_digest,
        equalized_snapshot_digest=equalized.snapshot().digest(),
        end_snapshot_digest=probed.snapshot().digest(),
        clock_id=probe_plan.clock_id,
        ticks_per_second=probe_plan.ticks_per_second,
        samples=tuple(samples),
    )


def observe_s2c6_probe_pair(
    history: S2ControlledWorldResult,
    neutral: S2ControlledN8Result,
    probe_plan: S2PreparedProbePlan,
    field_config: NeutralLocalFieldSubstrateConfig = (
        NeutralLocalFieldSubstrateConfig(1.0)
    ),
    afterimage_config: NeutralFastAfterimageConfig = (
        NeutralFastAfterimageConfig(0.5)
    ),
) -> S2ProbeTracePair:
    """Observe r1.a and n8 at identical probe completions without metrics."""

    if not isinstance(history, S2ControlledWorldResult):
        raise S2ReferenceRunnerError("S2-C6 history must be one r1.a formation")
    if not isinstance(neutral, S2ControlledN8Result):
        raise S2ReferenceRunnerError("S2-C6 neutral must be one n8 formation")
    if (
        history.model_id != neutral.model_id
        or history.coupling_rate_per_second != neutral.coupling_rate_per_second
    ):
        raise S2ReferenceRunnerError("S2-C6 requires matching B0 or B2 formations")
    if field_config.response_time_seconds != 1.0:
        raise S2ReferenceRunnerError("S2-C6 field response must remain 1.0 s")
    if afterimage_config.time_constant_seconds != 0.5:
        raise S2ReferenceRunnerError("S2-C6 afterimage time must remain 0.5 s")
    return S2ProbeTracePair(
        history=_observe_s2c6_probe_trace(
            history,
            probe_plan,
            field_config,
            afterimage_config,
        ),
        neutral=_observe_s2c6_probe_trace(
            neutral,
            probe_plan,
            field_config,
            afterimage_config,
        ),
    )


def observe_s2c8_c1_probe(
    formation: S2ControlledC1Result,
    probe_plan: S2PreparedProbePlan,
    field_config: NeutralLocalFieldSubstrateConfig = (
        NeutralLocalFieldSubstrateConfig(1.0)
    ),
    afterimage_config: NeutralFastAfterimageConfig = (
        NeutralFastAfterimageConfig(0.5)
    ),
) -> S2ProbeTrace:
    """Observe c1.a at the canonical probe completions without metrics."""

    if not isinstance(formation, S2ControlledC1Result):
        raise S2ReferenceRunnerError("S2-C8 requires one c1.a formation")
    if field_config.response_time_seconds != 1.0:
        raise S2ReferenceRunnerError("S2-C8 field response must remain 1.0 s")
    if afterimage_config.time_constant_seconds != 0.5:
        raise S2ReferenceRunnerError("S2-C8 afterimage time must remain 0.5 s")
    return _observe_s2c6_probe_trace(
        formation,
        probe_plan,
        field_config,
        afterimage_config,
    )


def observe_s2c9_r2c2_probe(
    formation: S2ControlledR2C2Result,
    probe_plan: S2PreparedProbePlan,
    field_config: NeutralLocalFieldSubstrateConfig = (
        NeutralLocalFieldSubstrateConfig(1.0)
    ),
    afterimage_config: NeutralFastAfterimageConfig = (
        NeutralFastAfterimageConfig(0.5)
    ),
) -> S2ProbeTrace:
    """Observe r2.a or c2.a at the canonical probe completions."""

    if not isinstance(formation, S2ControlledR2C2Result):
        raise S2ReferenceRunnerError("S2-C9 requires one r2.a or c2.a formation")
    if field_config.response_time_seconds != 1.0:
        raise S2ReferenceRunnerError("S2-C9 field response must remain 1.0 s")
    if afterimage_config.time_constant_seconds != 0.5:
        raise S2ReferenceRunnerError("S2-C9 afterimage time must remain 0.5 s")
    return _observe_s2c6_probe_trace(
        formation,
        probe_plan,
        field_config,
        afterimage_config,
    )


def observe_s2c10_r4c4_probe(
    formation: S2ControlledR4C4Result,
    probe_plan: S2PreparedProbePlan,
    field_config: NeutralLocalFieldSubstrateConfig = (
        NeutralLocalFieldSubstrateConfig(1.0)
    ),
    afterimage_config: NeutralFastAfterimageConfig = (
        NeutralFastAfterimageConfig(0.5)
    ),
) -> S2ProbeTrace:
    """Observe r4.a or c4.a at the canonical probe completions."""

    if not isinstance(formation, S2ControlledR4C4Result):
        raise S2ReferenceRunnerError("S2-C10 requires one r4.a or c4.a formation")
    if field_config.response_time_seconds != 1.0:
        raise S2ReferenceRunnerError("S2-C10 field response must remain 1.0 s")
    if afterimage_config.time_constant_seconds != 0.5:
        raise S2ReferenceRunnerError("S2-C10 afterimage time must remain 0.5 s")
    return _observe_s2c6_probe_trace(
        formation,
        probe_plan,
        field_config,
        afterimage_config,
    )


def observe_s2c11_r8c8_probe(
    formation: S2ControlledR8C8Result,
    probe_plan: S2PreparedProbePlan,
    field_config: NeutralLocalFieldSubstrateConfig = (
        NeutralLocalFieldSubstrateConfig(1.0)
    ),
    afterimage_config: NeutralFastAfterimageConfig = (
        NeutralFastAfterimageConfig(0.5)
    ),
) -> S2ProbeTrace:
    """Observe r8.a or c8.a at the canonical probe completions."""

    if not isinstance(formation, S2ControlledR8C8Result):
        raise S2ReferenceRunnerError("S2-C11 requires one r8.a or c8.a formation")
    if field_config.response_time_seconds != 1.0:
        raise S2ReferenceRunnerError("S2-C11 field response must remain 1.0 s")
    if afterimage_config.time_constant_seconds != 0.5:
        raise S2ReferenceRunnerError("S2-C11 afterimage time must remain 0.5 s")
    return _observe_s2c6_probe_trace(
        formation,
        probe_plan,
        field_config,
        afterimage_config,
    )


def observe_s2c13_r8bc8b_probe(
    formation: S2ControlledR8BC8BResult,
    probe_plan: S2PreparedProbePlan,
    field_config: NeutralLocalFieldSubstrateConfig = (
        NeutralLocalFieldSubstrateConfig(1.0)
    ),
    afterimage_config: NeutralFastAfterimageConfig = (
        NeutralFastAfterimageConfig(0.5)
    ),
) -> S2ProbeTrace:
    """Observe r8.b or c8.b at the canonical probe completions."""

    if not isinstance(formation, S2ControlledR8BC8BResult):
        raise S2ReferenceRunnerError("S2-C13 requires one r8.b or c8.b formation")
    if field_config.response_time_seconds != 1.0:
        raise S2ReferenceRunnerError("S2-C13 field response must remain 1.0 s")
    if afterimage_config.time_constant_seconds != 0.5:
        raise S2ReferenceRunnerError("S2-C13 afterimage time must remain 0.5 s")
    return _observe_s2c6_probe_trace(
        formation,
        probe_plan,
        field_config,
        afterimage_config,
    )


@dataclass(frozen=True, slots=True)
class S2ScalarMetric:
    metric_id: str
    value: float

    def __post_init__(self) -> None:
        if self.metric_id not in S2_METRIC_IDS:
            raise S2ReferenceRunnerError("unknown S2 metric id")
        value = float(self.value)
        if not math.isfinite(value) or value < 0.0:
            raise S2ReferenceRunnerError("S2 metrics must be finite and nonnegative")
        object.__setattr__(self, "value", value)

    def canonical_payload(self) -> dict[str, object]:
        return {"metric_id": self.metric_id, "value": self.value}


@dataclass(frozen=True, slots=True)
class S2SinglePairDistances:
    model_id: str
    coupling_rate_per_second: float
    history_formation_digest: str
    neutral_formation_digest: str
    probe_plan_digest: str
    probe_digest: str
    support_count: int
    metrics: tuple[S2ScalarMetric, ...]

    def __post_init__(self) -> None:
        if self.model_id not in ("b0", "b2"):
            raise S2ReferenceRunnerError("S2-C7 permits only B0 or B2")
        coupling = float(self.coupling_rate_per_second)
        if coupling not in (0.0, 0.25):
            raise S2ReferenceRunnerError("S2-C7 coupling is invalid")
        if self.model_id == "b0" and coupling != 0.0:
            raise S2ReferenceRunnerError("S2-C7 B0 cannot carry L coupling")
        for role in (
            "history_formation_digest",
            "neutral_formation_digest",
            "probe_plan_digest",
            "probe_digest",
        ):
            if not _DIGEST.fullmatch(getattr(self, role)):
                raise S2ReferenceRunnerError(f"invalid S2-C7 {role}")
        if (
            isinstance(self.support_count, bool)
            or not isinstance(self.support_count, int)
            or self.support_count < 1
        ):
            raise S2ReferenceRunnerError("S2-C7 support count is invalid")
        metrics = tuple(self.metrics)
        if any(not isinstance(item, S2ScalarMetric) for item in metrics):
            raise S2ReferenceRunnerError("S2-C7 requires scalar S2 metrics")
        expected_ids = ("d_s", "d_h") if self.model_id == "b0" else (
            "d_l",
            "d_s",
            "d_h",
        )
        if tuple(item.metric_id for item in metrics) != expected_ids:
            raise S2ReferenceRunnerError("S2-C7 metric roles or order are invalid")
        if any(item.value > 2.0 + 1e-12 for item in metrics):
            raise S2ReferenceRunnerError("S2-C7 distance left the field domain")
        if self.model_id == "b0" and any(item.value != 0.0 for item in metrics):
            raise S2ReferenceRunnerError("S2-C7 B0 null control must be exactly zero")
        object.__setattr__(self, "coupling_rate_per_second", coupling)
        object.__setattr__(self, "metrics", metrics)

    def metric(self, metric_id: str) -> float:
        for item in self.metrics:
            if item.metric_id == metric_id:
                return item.value
        raise KeyError(metric_id)

    @property
    def d_l(self) -> float | None:
        return None if self.model_id == "b0" else self.metric("d_l")

    @property
    def d_s(self) -> float:
        return self.metric("d_s")

    @property
    def d_h(self) -> float:
        return self.metric("d_h")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "model_id": self.model_id,
            "coupling_rate_per_second": self.coupling_rate_per_second,
            "history_formation_digest": self.history_formation_digest,
            "neutral_formation_digest": self.neutral_formation_digest,
            "probe_plan_digest": self.probe_plan_digest,
            "probe_digest": self.probe_digest,
            "support_count": self.support_count,
            "metrics": [item.canonical_payload() for item in self.metrics],
        }


def measure_s2c7_single_pair_distances(
    history: S2ControlledWorldResult,
    neutral: S2ControlledN8Result,
    traces: S2ProbeTracePair,
) -> S2SinglePairDistances:
    """Reduce one r1.a/n8 trace pair to preregistered scalar distances."""

    if not isinstance(history, S2ControlledWorldResult):
        raise S2ReferenceRunnerError("S2-C7 history must be one r1.a formation")
    if not isinstance(neutral, S2ControlledN8Result):
        raise S2ReferenceRunnerError("S2-C7 neutral must be one n8 formation")
    if not isinstance(traces, S2ProbeTracePair):
        raise S2ReferenceRunnerError("S2-C7 requires one S2-C6 trace pair")
    if (
        history.model_id != neutral.model_id
        or history.model_id != traces.history.model_id
        or history.coupling_rate_per_second != neutral.coupling_rate_per_second
        or history.coupling_rate_per_second
        != traces.history.coupling_rate_per_second
    ):
        raise S2ReferenceRunnerError("S2-C7 formations and traces must share one arm")
    if (
        traces.history.formation_snapshot_digest != history.end_snapshot_digest
        or traces.neutral.formation_snapshot_digest != neutral.end_snapshot_digest
    ):
        raise S2ReferenceRunnerError("S2-C7 traces do not belong to the formations")

    d_s = max(
        abs(history_value - neutral_value)
        for history_sample, neutral_sample in zip(
            traces.history.samples,
            traces.neutral.samples,
            strict=True,
        )
        for history_value, neutral_value in zip(
            history_sample.activation,
            neutral_sample.activation,
            strict=True,
        )
    )
    d_h = max(
        abs(history_value - neutral_value)
        for history_sample, neutral_sample in zip(
            traces.history.samples,
            traces.neutral.samples,
            strict=True,
        )
        for history_value, neutral_value in zip(
            history_sample.afterimage,
            neutral_sample.afterimage,
            strict=True,
        )
    )
    if history.model_id == "b0":
        if history.field.development is not None or neutral.field.development is not None:
            raise S2ReferenceRunnerError("S2-C7 B0 formations cannot contain L")
        metrics = (
            S2ScalarMetric("d_s", d_s),
            S2ScalarMetric("d_h", d_h),
        )
    else:
        history_l = history.field.development
        neutral_l = neutral.field.development
        if history_l is None or neutral_l is None:
            raise S2ReferenceRunnerError("S2-C7 B2 formations require L")
        if history_l.contract != neutral_l.contract:
            raise S2ReferenceRunnerError("S2-C7 B2 L contracts differ")
        d_l = max(
            abs(history_value - neutral_value)
            for history_value, neutral_value in zip(
                history_l.dispositions,
                neutral_l.dispositions,
                strict=True,
            )
        )
        metrics = (
            S2ScalarMetric("d_l", d_l),
            S2ScalarMetric("d_s", d_s),
            S2ScalarMetric("d_h", d_h),
        )
    return S2SinglePairDistances(
        model_id=history.model_id,
        coupling_rate_per_second=history.coupling_rate_per_second,
        history_formation_digest=history.end_snapshot_digest,
        neutral_formation_digest=neutral.end_snapshot_digest,
        probe_plan_digest=traces.history.probe_plan_digest,
        probe_digest=traces.history.probe_digest,
        support_count=len(traces.history.samples),
        metrics=metrics,
    )


@dataclass(frozen=True, slots=True)
class S2C1IdentityControl:
    model_id: str
    coupling_rate_per_second: float
    r1_formation_digest: str
    c1_formation_digest: str
    probe_plan_digest: str
    probe_digest: str
    support_count: int
    metric: S2ScalarMetric

    def __post_init__(self) -> None:
        if self.model_id not in ("b0", "b2"):
            raise S2ReferenceRunnerError("S2-C8 identity permits only B0 or B2")
        coupling = float(self.coupling_rate_per_second)
        if coupling not in (0.0, 0.25):
            raise S2ReferenceRunnerError("S2-C8 identity coupling is invalid")
        if self.model_id == "b0" and coupling != 0.0:
            raise S2ReferenceRunnerError("S2-C8 B0 identity cannot carry L coupling")
        for role in (
            "r1_formation_digest",
            "c1_formation_digest",
            "probe_plan_digest",
            "probe_digest",
        ):
            if not _DIGEST.fullmatch(getattr(self, role)):
                raise S2ReferenceRunnerError(f"invalid S2-C8 identity {role}")
        if (
            isinstance(self.support_count, bool)
            or not isinstance(self.support_count, int)
            or self.support_count < 1
        ):
            raise S2ReferenceRunnerError("S2-C8 identity support count is invalid")
        if not isinstance(self.metric, S2ScalarMetric) or self.metric.metric_id != "d_pair":
            raise S2ReferenceRunnerError("S2-C8 identity requires only d_pair")
        if self.metric.value != 0.0:
            raise S2ReferenceRunnerError("S2-C8 D_pair(1) must be exactly zero")
        object.__setattr__(self, "coupling_rate_per_second", coupling)

    @property
    def d_pair(self) -> float:
        return self.metric.value


def measure_s2c8_c1_identity(
    r1_trace: S2ProbeTrace,
    c1_trace: S2ProbeTrace,
) -> S2C1IdentityControl:
    """Measure the preregistered n=1 R/C identity control only."""

    if not isinstance(r1_trace, S2ProbeTrace) or r1_trace.world_id != "r1.a":
        raise S2ReferenceRunnerError("S2-C8 identity requires an r1.a trace first")
    if not isinstance(c1_trace, S2ProbeTrace) or c1_trace.world_id != "c1.a":
        raise S2ReferenceRunnerError("S2-C8 identity requires a c1.a trace second")
    if (
        r1_trace.model_id != c1_trace.model_id
        or r1_trace.coupling_rate_per_second
        != c1_trace.coupling_rate_per_second
    ):
        raise S2ReferenceRunnerError("S2-C8 identity requires one matching model arm")
    if (
        r1_trace.probe_plan_digest != c1_trace.probe_plan_digest
        or r1_trace.probe_digest != c1_trace.probe_digest
        or r1_trace.clock_id != c1_trace.clock_id
        or r1_trace.ticks_per_second != c1_trace.ticks_per_second
        or r1_trace.completion_ticks != c1_trace.completion_ticks
    ):
        raise S2ReferenceRunnerError("S2-C8 identity requires one probe support")
    d_s = max(
        abs(r1_value - c1_value)
        for r1_sample, c1_sample in zip(
            r1_trace.samples,
            c1_trace.samples,
            strict=True,
        )
        for r1_value, c1_value in zip(
            r1_sample.activation,
            c1_sample.activation,
            strict=True,
        )
    )
    d_h = max(
        abs(r1_value - c1_value)
        for r1_sample, c1_sample in zip(
            r1_trace.samples,
            c1_trace.samples,
            strict=True,
        )
        for r1_value, c1_value in zip(
            r1_sample.afterimage,
            c1_sample.afterimage,
            strict=True,
        )
    )
    return S2C1IdentityControl(
        model_id=r1_trace.model_id,
        coupling_rate_per_second=r1_trace.coupling_rate_per_second,
        r1_formation_digest=r1_trace.formation_snapshot_digest,
        c1_formation_digest=c1_trace.formation_snapshot_digest,
        probe_plan_digest=r1_trace.probe_plan_digest,
        probe_digest=r1_trace.probe_digest,
        support_count=len(r1_trace.samples),
        metric=S2ScalarMetric("d_pair", max(d_s, d_h)),
    )


@dataclass(frozen=True, slots=True)
class S2R2C2PairResult:
    model_id: str
    coupling_rate_per_second: float
    r2_formation_digest: str
    c2_formation_digest: str
    probe_plan_digest: str
    probe_digest: str
    support_count: int
    metric: S2ScalarMetric

    def __post_init__(self) -> None:
        if self.model_id not in ("b0", "b2"):
            raise S2ReferenceRunnerError("S2-C9 pair permits only B0 or B2")
        coupling = float(self.coupling_rate_per_second)
        if coupling not in (0.0, 0.25):
            raise S2ReferenceRunnerError("S2-C9 pair coupling is invalid")
        if self.model_id == "b0" and coupling != 0.0:
            raise S2ReferenceRunnerError("S2-C9 B0 pair cannot carry L coupling")
        for role in (
            "r2_formation_digest",
            "c2_formation_digest",
            "probe_plan_digest",
            "probe_digest",
        ):
            if not _DIGEST.fullmatch(getattr(self, role)):
                raise S2ReferenceRunnerError(f"invalid S2-C9 pair {role}")
        if (
            isinstance(self.support_count, bool)
            or not isinstance(self.support_count, int)
            or self.support_count < 1
        ):
            raise S2ReferenceRunnerError("S2-C9 pair support count is invalid")
        if not isinstance(self.metric, S2ScalarMetric) or self.metric.metric_id != "d_pair":
            raise S2ReferenceRunnerError("S2-C9 pair requires only d_pair")
        if self.metric.value > 2.0 + 1e-12:
            raise S2ReferenceRunnerError("S2-C9 pair distance left the field domain")
        if self.model_id == "b0" and self.metric.value != 0.0:
            raise S2ReferenceRunnerError("S2-C9 B0 D_pair(2) must be exactly zero")
        object.__setattr__(self, "coupling_rate_per_second", coupling)

    @property
    def d_pair(self) -> float:
        return self.metric.value


def measure_s2c9_r2c2_pair(
    r2_trace: S2ProbeTrace,
    c2_trace: S2ProbeTrace,
) -> S2R2C2PairResult:
    """Measure only the preregistered n=2 R/C probe distance."""

    if not isinstance(r2_trace, S2ProbeTrace) or r2_trace.world_id != "r2.a":
        raise S2ReferenceRunnerError("S2-C9 pair requires an r2.a trace first")
    if not isinstance(c2_trace, S2ProbeTrace) or c2_trace.world_id != "c2.a":
        raise S2ReferenceRunnerError("S2-C9 pair requires a c2.a trace second")
    if (
        r2_trace.model_id != c2_trace.model_id
        or r2_trace.coupling_rate_per_second
        != c2_trace.coupling_rate_per_second
    ):
        raise S2ReferenceRunnerError("S2-C9 pair requires one matching model arm")
    if (
        r2_trace.probe_plan_digest != c2_trace.probe_plan_digest
        or r2_trace.probe_digest != c2_trace.probe_digest
        or r2_trace.clock_id != c2_trace.clock_id
        or r2_trace.ticks_per_second != c2_trace.ticks_per_second
        or r2_trace.completion_ticks != c2_trace.completion_ticks
    ):
        raise S2ReferenceRunnerError("S2-C9 pair requires one probe support")
    d_s = max(
        abs(r2_value - c2_value)
        for r2_sample, c2_sample in zip(
            r2_trace.samples,
            c2_trace.samples,
            strict=True,
        )
        for r2_value, c2_value in zip(
            r2_sample.activation,
            c2_sample.activation,
            strict=True,
        )
    )
    d_h = max(
        abs(r2_value - c2_value)
        for r2_sample, c2_sample in zip(
            r2_trace.samples,
            c2_trace.samples,
            strict=True,
        )
        for r2_value, c2_value in zip(
            r2_sample.afterimage,
            c2_sample.afterimage,
            strict=True,
        )
    )
    return S2R2C2PairResult(
        model_id=r2_trace.model_id,
        coupling_rate_per_second=r2_trace.coupling_rate_per_second,
        r2_formation_digest=r2_trace.formation_snapshot_digest,
        c2_formation_digest=c2_trace.formation_snapshot_digest,
        probe_plan_digest=r2_trace.probe_plan_digest,
        probe_digest=r2_trace.probe_digest,
        support_count=len(r2_trace.samples),
        metric=S2ScalarMetric("d_pair", max(d_s, d_h)),
    )


@dataclass(frozen=True, slots=True)
class S2R4C4PairResult:
    model_id: str
    coupling_rate_per_second: float
    r4_formation_digest: str
    c4_formation_digest: str
    probe_plan_digest: str
    probe_digest: str
    support_count: int
    metric: S2ScalarMetric

    def __post_init__(self) -> None:
        if self.model_id not in ("b0", "b2"):
            raise S2ReferenceRunnerError("S2-C10 pair permits only B0 or B2")
        coupling = float(self.coupling_rate_per_second)
        if coupling not in (0.0, 0.25):
            raise S2ReferenceRunnerError("S2-C10 pair coupling is invalid")
        if self.model_id == "b0" and coupling != 0.0:
            raise S2ReferenceRunnerError("S2-C10 B0 pair cannot carry L coupling")
        for role in (
            "r4_formation_digest",
            "c4_formation_digest",
            "probe_plan_digest",
            "probe_digest",
        ):
            if not _DIGEST.fullmatch(getattr(self, role)):
                raise S2ReferenceRunnerError(f"invalid S2-C10 pair {role}")
        if (
            isinstance(self.support_count, bool)
            or not isinstance(self.support_count, int)
            or self.support_count < 1
        ):
            raise S2ReferenceRunnerError("S2-C10 pair support count is invalid")
        if not isinstance(self.metric, S2ScalarMetric) or self.metric.metric_id != "d_pair":
            raise S2ReferenceRunnerError("S2-C10 pair requires only d_pair")
        if self.metric.value > 2.0 + 1e-12:
            raise S2ReferenceRunnerError("S2-C10 pair distance left the field domain")
        if self.model_id == "b0" and self.metric.value != 0.0:
            raise S2ReferenceRunnerError("S2-C10 B0 D_pair(4) must be exactly zero")
        object.__setattr__(self, "coupling_rate_per_second", coupling)

    @property
    def d_pair(self) -> float:
        return self.metric.value


def measure_s2c10_r4c4_pair(
    r4_trace: S2ProbeTrace,
    c4_trace: S2ProbeTrace,
) -> S2R4C4PairResult:
    """Measure only the preregistered n=4 R/C probe distance."""

    if not isinstance(r4_trace, S2ProbeTrace) or r4_trace.world_id != "r4.a":
        raise S2ReferenceRunnerError("S2-C10 pair requires an r4.a trace first")
    if not isinstance(c4_trace, S2ProbeTrace) or c4_trace.world_id != "c4.a":
        raise S2ReferenceRunnerError("S2-C10 pair requires a c4.a trace second")
    if (
        r4_trace.model_id != c4_trace.model_id
        or r4_trace.coupling_rate_per_second
        != c4_trace.coupling_rate_per_second
    ):
        raise S2ReferenceRunnerError("S2-C10 pair requires one matching model arm")
    if (
        r4_trace.probe_plan_digest != c4_trace.probe_plan_digest
        or r4_trace.probe_digest != c4_trace.probe_digest
        or r4_trace.clock_id != c4_trace.clock_id
        or r4_trace.ticks_per_second != c4_trace.ticks_per_second
        or r4_trace.completion_ticks != c4_trace.completion_ticks
    ):
        raise S2ReferenceRunnerError("S2-C10 pair requires one probe support")
    d_s = max(
        abs(r4_value - c4_value)
        for r4_sample, c4_sample in zip(
            r4_trace.samples,
            c4_trace.samples,
            strict=True,
        )
        for r4_value, c4_value in zip(
            r4_sample.activation,
            c4_sample.activation,
            strict=True,
        )
    )
    d_h = max(
        abs(r4_value - c4_value)
        for r4_sample, c4_sample in zip(
            r4_trace.samples,
            c4_trace.samples,
            strict=True,
        )
        for r4_value, c4_value in zip(
            r4_sample.afterimage,
            c4_sample.afterimage,
            strict=True,
        )
    )
    return S2R4C4PairResult(
        model_id=r4_trace.model_id,
        coupling_rate_per_second=r4_trace.coupling_rate_per_second,
        r4_formation_digest=r4_trace.formation_snapshot_digest,
        c4_formation_digest=c4_trace.formation_snapshot_digest,
        probe_plan_digest=r4_trace.probe_plan_digest,
        probe_digest=r4_trace.probe_digest,
        support_count=len(r4_trace.samples),
        metric=S2ScalarMetric("d_pair", max(d_s, d_h)),
    )


@dataclass(frozen=True, slots=True)
class S2R8C8PairResult:
    model_id: str
    coupling_rate_per_second: float
    r8_formation_digest: str
    c8_formation_digest: str
    probe_plan_digest: str
    probe_digest: str
    support_count: int
    metric: S2ScalarMetric

    def __post_init__(self) -> None:
        if self.model_id not in ("b0", "b2"):
            raise S2ReferenceRunnerError("S2-C11 pair permits only B0 or B2")
        coupling = float(self.coupling_rate_per_second)
        if coupling not in (0.0, 0.25):
            raise S2ReferenceRunnerError("S2-C11 pair coupling is invalid")
        if self.model_id == "b0" and coupling != 0.0:
            raise S2ReferenceRunnerError("S2-C11 B0 pair cannot carry L coupling")
        for role in (
            "r8_formation_digest",
            "c8_formation_digest",
            "probe_plan_digest",
            "probe_digest",
        ):
            if not _DIGEST.fullmatch(getattr(self, role)):
                raise S2ReferenceRunnerError(f"invalid S2-C11 pair {role}")
        if (
            isinstance(self.support_count, bool)
            or not isinstance(self.support_count, int)
            or self.support_count < 1
        ):
            raise S2ReferenceRunnerError("S2-C11 pair support count is invalid")
        if not isinstance(self.metric, S2ScalarMetric) or self.metric.metric_id != "d_pair":
            raise S2ReferenceRunnerError("S2-C11 pair requires only d_pair")
        if self.metric.value > 2.0 + 1e-12:
            raise S2ReferenceRunnerError("S2-C11 pair distance left the field domain")
        if self.model_id == "b0" and self.metric.value != 0.0:
            raise S2ReferenceRunnerError("S2-C11 B0 D_pair(8) must be exactly zero")
        object.__setattr__(self, "coupling_rate_per_second", coupling)

    @property
    def d_pair(self) -> float:
        return self.metric.value


def measure_s2c11_r8c8_pair(
    r8_trace: S2ProbeTrace,
    c8_trace: S2ProbeTrace,
) -> S2R8C8PairResult:
    """Measure only the preregistered n=8 R/C probe distance."""

    if not isinstance(r8_trace, S2ProbeTrace) or r8_trace.world_id != "r8.a":
        raise S2ReferenceRunnerError("S2-C11 pair requires an r8.a trace first")
    if not isinstance(c8_trace, S2ProbeTrace) or c8_trace.world_id != "c8.a":
        raise S2ReferenceRunnerError("S2-C11 pair requires a c8.a trace second")
    if (
        r8_trace.model_id != c8_trace.model_id
        or r8_trace.coupling_rate_per_second
        != c8_trace.coupling_rate_per_second
    ):
        raise S2ReferenceRunnerError("S2-C11 pair requires one matching model arm")
    if (
        r8_trace.probe_plan_digest != c8_trace.probe_plan_digest
        or r8_trace.probe_digest != c8_trace.probe_digest
        or r8_trace.clock_id != c8_trace.clock_id
        or r8_trace.ticks_per_second != c8_trace.ticks_per_second
        or r8_trace.completion_ticks != c8_trace.completion_ticks
    ):
        raise S2ReferenceRunnerError("S2-C11 pair requires one probe support")
    d_s = max(
        abs(r8_value - c8_value)
        for r8_sample, c8_sample in zip(
            r8_trace.samples,
            c8_trace.samples,
            strict=True,
        )
        for r8_value, c8_value in zip(
            r8_sample.activation,
            c8_sample.activation,
            strict=True,
        )
    )
    d_h = max(
        abs(r8_value - c8_value)
        for r8_sample, c8_sample in zip(
            r8_trace.samples,
            c8_trace.samples,
            strict=True,
        )
        for r8_value, c8_value in zip(
            r8_sample.afterimage,
            c8_sample.afterimage,
            strict=True,
        )
    )
    return S2R8C8PairResult(
        model_id=r8_trace.model_id,
        coupling_rate_per_second=r8_trace.coupling_rate_per_second,
        r8_formation_digest=r8_trace.formation_snapshot_digest,
        c8_formation_digest=c8_trace.formation_snapshot_digest,
        probe_plan_digest=r8_trace.probe_plan_digest,
        probe_digest=r8_trace.probe_digest,
        support_count=len(r8_trace.samples),
        metric=S2ScalarMetric("d_pair", max(d_s, d_h)),
    )


@dataclass(frozen=True, slots=True)
class S2R8BC8BPairResult:
    model_id: str
    coupling_rate_per_second: float
    r8b_formation_digest: str
    c8b_formation_digest: str
    probe_plan_digest: str
    probe_digest: str
    support_count: int
    metric: S2ScalarMetric

    def __post_init__(self) -> None:
        if self.model_id not in ("b0", "b2"):
            raise S2ReferenceRunnerError("S2-C13 pair permits only B0 or B2")
        coupling = float(self.coupling_rate_per_second)
        if coupling not in (0.0, 0.25):
            raise S2ReferenceRunnerError("S2-C13 pair coupling is invalid")
        if self.model_id == "b0" and coupling != 0.0:
            raise S2ReferenceRunnerError("S2-C13 B0 pair cannot carry L coupling")
        for role in (
            "r8b_formation_digest",
            "c8b_formation_digest",
            "probe_plan_digest",
            "probe_digest",
        ):
            if not _DIGEST.fullmatch(getattr(self, role)):
                raise S2ReferenceRunnerError(f"invalid S2-C13 pair {role}")
        if (
            isinstance(self.support_count, bool)
            or not isinstance(self.support_count, int)
            or self.support_count < 1
        ):
            raise S2ReferenceRunnerError("S2-C13 pair support count is invalid")
        if not isinstance(self.metric, S2ScalarMetric) or self.metric.metric_id != "d_pair":
            raise S2ReferenceRunnerError("S2-C13 pair requires only d_pair")
        if self.metric.value > 2.0 + 1e-12:
            raise S2ReferenceRunnerError("S2-C13 pair distance left the field domain")
        if self.model_id == "b0" and self.metric.value != 0.0:
            raise S2ReferenceRunnerError("S2-C13 B0 D_pair_B(8) must be exactly zero")
        object.__setattr__(self, "coupling_rate_per_second", coupling)

    @property
    def d_pair(self) -> float:
        return self.metric.value


def measure_s2c13_r8bc8b_pair(
    r8b_trace: S2ProbeTrace,
    c8b_trace: S2ProbeTrace,
) -> S2R8BC8BPairResult:
    """Measure only the preregistered n=8 B-world R/C probe distance."""

    if not isinstance(r8b_trace, S2ProbeTrace) or r8b_trace.world_id != "r8.b":
        raise S2ReferenceRunnerError("S2-C13 pair requires an r8.b trace first")
    if not isinstance(c8b_trace, S2ProbeTrace) or c8b_trace.world_id != "c8.b":
        raise S2ReferenceRunnerError("S2-C13 pair requires a c8.b trace second")
    if (
        r8b_trace.model_id != c8b_trace.model_id
        or r8b_trace.coupling_rate_per_second
        != c8b_trace.coupling_rate_per_second
    ):
        raise S2ReferenceRunnerError("S2-C13 pair requires one matching model arm")
    if (
        r8b_trace.probe_plan_digest != c8b_trace.probe_plan_digest
        or r8b_trace.probe_digest != c8b_trace.probe_digest
        or r8b_trace.clock_id != c8b_trace.clock_id
        or r8b_trace.ticks_per_second != c8b_trace.ticks_per_second
        or r8b_trace.completion_ticks != c8b_trace.completion_ticks
    ):
        raise S2ReferenceRunnerError("S2-C13 pair requires one probe support")
    d_s = max(
        abs(r8b_value - c8b_value)
        for r8b_sample, c8b_sample in zip(
            r8b_trace.samples,
            c8b_trace.samples,
            strict=True,
        )
        for r8b_value, c8b_value in zip(
            r8b_sample.activation,
            c8b_sample.activation,
            strict=True,
        )
    )
    d_h = max(
        abs(r8b_value - c8b_value)
        for r8b_sample, c8b_sample in zip(
            r8b_trace.samples,
            c8b_trace.samples,
            strict=True,
        )
        for r8b_value, c8b_value in zip(
            r8b_sample.afterimage,
            c8b_sample.afterimage,
            strict=True,
        )
    )
    return S2R8BC8BPairResult(
        model_id=r8b_trace.model_id,
        coupling_rate_per_second=r8b_trace.coupling_rate_per_second,
        r8b_formation_digest=r8b_trace.formation_snapshot_digest,
        c8b_formation_digest=c8b_trace.formation_snapshot_digest,
        probe_plan_digest=r8b_trace.probe_plan_digest,
        probe_digest=r8b_trace.probe_digest,
        support_count=len(r8b_trace.samples),
        metric=S2ScalarMetric("d_pair", max(d_s, d_h)),
    )


@dataclass(frozen=True, slots=True)
class S2APairProfileEntry:
    contact_count: int
    source_pair_digest: str
    metric: S2ScalarMetric

    def __post_init__(self) -> None:
        if self.contact_count not in (1, 2, 4, 8):
            raise S2ReferenceRunnerError("S2-C12 contact count must be 1, 2, 4, or 8")
        if not _DIGEST.fullmatch(self.source_pair_digest):
            raise S2ReferenceRunnerError("S2-C12 source pair digest is invalid")
        if not isinstance(self.metric, S2ScalarMetric) or self.metric.metric_id != "d_pair":
            raise S2ReferenceRunnerError("S2-C12 entries require only d_pair")

    @property
    def d_pair(self) -> float:
        return self.metric.value

    def canonical_payload(self) -> dict[str, object]:
        return {
            "contact_count": self.contact_count,
            "source_pair_digest": self.source_pair_digest,
            "metric": self.metric.canonical_payload(),
        }


@dataclass(frozen=True, slots=True)
class S2APairProfile:
    model_id: str
    coupling_rate_per_second: float
    probe_plan_digest: str
    probe_digest: str
    support_count: int
    entries: tuple[S2APairProfileEntry, ...]

    def __post_init__(self) -> None:
        if self.model_id not in ("b0", "b2"):
            raise S2ReferenceRunnerError("S2-C12 profile permits only B0 or B2")
        coupling = float(self.coupling_rate_per_second)
        if coupling not in (0.0, 0.25):
            raise S2ReferenceRunnerError("S2-C12 profile coupling is invalid")
        if self.model_id == "b0" and coupling != 0.0:
            raise S2ReferenceRunnerError("S2-C12 B0 profile cannot carry L coupling")
        if not _DIGEST.fullmatch(self.probe_plan_digest) or not _DIGEST.fullmatch(
            self.probe_digest
        ):
            raise S2ReferenceRunnerError("S2-C12 profile probe digest is invalid")
        if (
            isinstance(self.support_count, bool)
            or not isinstance(self.support_count, int)
            or self.support_count < 1
        ):
            raise S2ReferenceRunnerError("S2-C12 profile support count is invalid")
        entries = tuple(self.entries)
        if not all(isinstance(item, S2APairProfileEntry) for item in entries):
            raise S2ReferenceRunnerError("S2-C12 profile entries are invalid")
        if tuple(item.contact_count for item in entries) != (1, 2, 4, 8):
            raise S2ReferenceRunnerError("S2-C12 profile order must remain 1, 2, 4, 8")
        if entries[0].d_pair != 0.0:
            raise S2ReferenceRunnerError("S2-C12 D_pair(1) must remain exactly zero")
        if self.model_id == "b0" and any(item.d_pair != 0.0 for item in entries):
            raise S2ReferenceRunnerError("S2-C12 B0 profile must remain exactly zero")
        object.__setattr__(self, "coupling_rate_per_second", coupling)
        object.__setattr__(self, "entries", entries)

    @property
    def contact_counts(self) -> tuple[int, ...]:
        return tuple(item.contact_count for item in self.entries)

    @property
    def d_pair_values(self) -> tuple[float, ...]:
        return tuple(item.d_pair for item in self.entries)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "profile_id": "s2.a-pair-profile.n1-2-4-8.v1",
            "model_id": self.model_id,
            "coupling_rate_per_second": self.coupling_rate_per_second,
            "probe_plan_digest": self.probe_plan_digest,
            "probe_digest": self.probe_digest,
            "support_count": self.support_count,
            "entries": [item.canonical_payload() for item in self.entries],
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def _s2_pair_result_digest(pair: object, contact_count: int) -> str:
    if isinstance(pair, S2C1IdentityControl):
        pair_id = "r1.a/c1.a"
        formation_digests = (
            pair.r1_formation_digest,
            pair.c1_formation_digest,
        )
    elif isinstance(pair, S2R2C2PairResult):
        pair_id = "r2.a/c2.a"
        formation_digests = (
            pair.r2_formation_digest,
            pair.c2_formation_digest,
        )
    elif isinstance(pair, S2R4C4PairResult):
        pair_id = "r4.a/c4.a"
        formation_digests = (
            pair.r4_formation_digest,
            pair.c4_formation_digest,
        )
    elif isinstance(pair, S2R8C8PairResult):
        pair_id = "r8.a/c8.a"
        formation_digests = (
            pair.r8_formation_digest,
            pair.c8_formation_digest,
        )
    elif isinstance(pair, S2R8BC8BPairResult):
        pair_id = "r8.b/c8.b"
        formation_digests = (
            pair.r8b_formation_digest,
            pair.c8b_formation_digest,
        )
    else:
        raise S2ReferenceRunnerError("S2 pair digest requires a typed pair result")
    return _digest(
        {
            "pair_id": pair_id,
            "contact_count": contact_count,
            "formation_digests": formation_digests,
            "model_id": pair.model_id,
            "coupling_rate_per_second": pair.coupling_rate_per_second,
            "probe_plan_digest": pair.probe_plan_digest,
            "probe_digest": pair.probe_digest,
            "support_count": pair.support_count,
            "d_pair": pair.d_pair,
        }
    )


def assemble_s2c12_a_pair_profile(
    n1: S2C1IdentityControl,
    n2: S2R2C2PairResult,
    n4: S2R4C4PairResult,
    n8: S2R8C8PairResult,
) -> S2APairProfile:
    """Assemble only the immutable A-pair scalar profile without a decision."""

    pairs = (n1, n2, n4, n8)
    expected_types = (
        S2C1IdentityControl,
        S2R2C2PairResult,
        S2R4C4PairResult,
        S2R8C8PairResult,
    )
    if any(not isinstance(pair, expected) for pair, expected in zip(pairs, expected_types)):
        raise S2ReferenceRunnerError("S2-C12 requires typed n=1,2,4,8 pairs")
    first = n1
    if any(
        pair.model_id != first.model_id
        or pair.coupling_rate_per_second != first.coupling_rate_per_second
        for pair in pairs[1:]
    ):
        raise S2ReferenceRunnerError("S2-C12 pairs require one matching model arm")
    if any(
        pair.probe_plan_digest != first.probe_plan_digest
        or pair.probe_digest != first.probe_digest
        or pair.support_count != first.support_count
        for pair in pairs[1:]
    ):
        raise S2ReferenceRunnerError("S2-C12 pairs require one probe support")
    return S2APairProfile(
        model_id=first.model_id,
        coupling_rate_per_second=first.coupling_rate_per_second,
        probe_plan_digest=first.probe_plan_digest,
        probe_digest=first.probe_digest,
        support_count=first.support_count,
        entries=tuple(
            S2APairProfileEntry(
                contact_count,
                _s2_pair_result_digest(pair, contact_count),
                pair.metric,
            )
            for contact_count, pair in zip((1, 2, 4, 8), pairs, strict=True)
        ),
    )


@dataclass(frozen=True, slots=True)
class S2N8ABScalarContainer:
    model_id: str
    coupling_rate_per_second: float
    probe_plan_digest: str
    probe_digest: str
    support_count: int
    a_pair_digest: str
    b_pair_digest: str
    a_metric: S2ScalarMetric
    b_metric: S2ScalarMetric

    def __post_init__(self) -> None:
        if self.model_id not in ("b0", "b2"):
            raise S2ReferenceRunnerError("S2-C14 container permits only B0 or B2")
        coupling = float(self.coupling_rate_per_second)
        if coupling not in (0.0, 0.25):
            raise S2ReferenceRunnerError("S2-C14 container coupling is invalid")
        if self.model_id == "b0" and coupling != 0.0:
            raise S2ReferenceRunnerError("S2-C14 B0 container cannot carry L coupling")
        for role in (
            "probe_plan_digest",
            "probe_digest",
            "a_pair_digest",
            "b_pair_digest",
        ):
            if not _DIGEST.fullmatch(getattr(self, role)):
                raise S2ReferenceRunnerError(f"invalid S2-C14 container {role}")
        if (
            isinstance(self.support_count, bool)
            or not isinstance(self.support_count, int)
            or self.support_count < 1
        ):
            raise S2ReferenceRunnerError("S2-C14 container support count is invalid")
        for metric in (self.a_metric, self.b_metric):
            if not isinstance(metric, S2ScalarMetric) or metric.metric_id != "d_pair":
                raise S2ReferenceRunnerError("S2-C14 container requires only d_pair")
        if self.model_id == "b0" and (
            self.a_metric.value != 0.0 or self.b_metric.value != 0.0
        ):
            raise S2ReferenceRunnerError("S2-C14 B0 A/B scalars must remain zero")
        object.__setattr__(self, "coupling_rate_per_second", coupling)

    @property
    def a_d_pair(self) -> float:
        return self.a_metric.value

    @property
    def b_d_pair(self) -> float:
        return self.b_metric.value

    def canonical_payload(self) -> dict[str, object]:
        return {
            "container_id": "s2.n8.a-b-scalar-container.v1",
            "model_id": self.model_id,
            "coupling_rate_per_second": self.coupling_rate_per_second,
            "probe_plan_digest": self.probe_plan_digest,
            "probe_digest": self.probe_digest,
            "support_count": self.support_count,
            "a_pair_digest": self.a_pair_digest,
            "b_pair_digest": self.b_pair_digest,
            "a_metric": self.a_metric.canonical_payload(),
            "b_metric": self.b_metric.canonical_payload(),
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def assemble_s2c14_n8_ab_scalar_container(
    a_pair: S2R8C8PairResult,
    b_pair: S2R8BC8BPairResult,
) -> S2N8ABScalarContainer:
    """Bind A8 and B8 pair scalars without computing an A/B difference."""

    if not isinstance(a_pair, S2R8C8PairResult) or not isinstance(
        b_pair,
        S2R8BC8BPairResult,
    ):
        raise S2ReferenceRunnerError("S2-C14 requires typed A8 and B8 pairs")
    if (
        a_pair.model_id != b_pair.model_id
        or a_pair.coupling_rate_per_second != b_pair.coupling_rate_per_second
    ):
        raise S2ReferenceRunnerError("S2-C14 pairs require one matching model arm")
    if (
        a_pair.probe_plan_digest != b_pair.probe_plan_digest
        or a_pair.probe_digest != b_pair.probe_digest
        or a_pair.support_count != b_pair.support_count
    ):
        raise S2ReferenceRunnerError("S2-C14 pairs require one probe support")
    return S2N8ABScalarContainer(
        model_id=a_pair.model_id,
        coupling_rate_per_second=a_pair.coupling_rate_per_second,
        probe_plan_digest=a_pair.probe_plan_digest,
        probe_digest=a_pair.probe_digest,
        support_count=a_pair.support_count,
        a_pair_digest=_s2_pair_result_digest(a_pair, 8),
        b_pair_digest=_s2_pair_result_digest(b_pair, 8),
        a_metric=a_pair.metric,
        b_metric=b_pair.metric,
    )


@dataclass(frozen=True, slots=True)
class S2WorldPairMetric:
    metric_id: str
    value: float

    def __post_init__(self) -> None:
        if self.metric_id != "d_world_pair":
            raise S2ReferenceRunnerError("S2-C15 permits only d_world_pair")
        value = float(self.value)
        if not math.isfinite(value) or value < 0.0:
            raise S2ReferenceRunnerError("S2-C15 metric must be finite and nonnegative")
        if value > 2.0 + 1e-12:
            raise S2ReferenceRunnerError("S2-C15 metric left the field domain")
        object.__setattr__(self, "value", value)

    def canonical_payload(self) -> dict[str, object]:
        return {"metric_id": self.metric_id, "value": self.value}


@dataclass(frozen=True, slots=True)
class S2N8WorldPairDistance:
    model_id: str
    coupling_rate_per_second: float
    container_digest: str
    probe_plan_digest: str
    probe_digest: str
    support_count: int
    a_d_pair: float
    b_d_pair: float
    metric: S2WorldPairMetric

    def __post_init__(self) -> None:
        if self.model_id not in ("b0", "b2"):
            raise S2ReferenceRunnerError("S2-C15 result permits only B0 or B2")
        coupling = float(self.coupling_rate_per_second)
        if coupling not in (0.0, 0.25):
            raise S2ReferenceRunnerError("S2-C15 result coupling is invalid")
        if self.model_id == "b0" and coupling != 0.0:
            raise S2ReferenceRunnerError("S2-C15 B0 result cannot carry L coupling")
        for role in ("container_digest", "probe_plan_digest", "probe_digest"):
            if not _DIGEST.fullmatch(getattr(self, role)):
                raise S2ReferenceRunnerError(f"invalid S2-C15 result {role}")
        if (
            isinstance(self.support_count, bool)
            or not isinstance(self.support_count, int)
            or self.support_count < 1
        ):
            raise S2ReferenceRunnerError("S2-C15 result support count is invalid")
        a_value = float(self.a_d_pair)
        b_value = float(self.b_d_pair)
        if not all(
            math.isfinite(value) and 0.0 <= value <= 2.0 + 1e-12
            for value in (a_value, b_value)
        ):
            raise S2ReferenceRunnerError("S2-C15 source scalars left the field domain")
        if not isinstance(self.metric, S2WorldPairMetric):
            raise S2ReferenceRunnerError("S2-C15 result requires d_world_pair")
        if self.metric.value != abs(a_value - b_value):
            raise S2ReferenceRunnerError("S2-C15 metric differs from source scalars")
        if self.model_id == "b0" and self.metric.value != 0.0:
            raise S2ReferenceRunnerError("S2-C15 B0 D_world_pair(8) must be zero")
        object.__setattr__(self, "coupling_rate_per_second", coupling)
        object.__setattr__(self, "a_d_pair", a_value)
        object.__setattr__(self, "b_d_pair", b_value)

    @property
    def d_world_pair(self) -> float:
        return self.metric.value

    def canonical_payload(self) -> dict[str, object]:
        return {
            "result_id": "s2.n8.d-world-pair.v1",
            "model_id": self.model_id,
            "coupling_rate_per_second": self.coupling_rate_per_second,
            "container_digest": self.container_digest,
            "probe_plan_digest": self.probe_plan_digest,
            "probe_digest": self.probe_digest,
            "support_count": self.support_count,
            "a_d_pair": self.a_d_pair,
            "b_d_pair": self.b_d_pair,
            "metric": self.metric.canonical_payload(),
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def measure_s2c15_n8_world_pair_distance(
    container: S2N8ABScalarContainer,
) -> S2N8WorldPairDistance:
    """Measure only |D_pair_A(8)-D_pair_B(8)| without a threshold."""

    if not isinstance(container, S2N8ABScalarContainer):
        raise S2ReferenceRunnerError("S2-C15 requires the bound n=8 A/B container")
    return S2N8WorldPairDistance(
        model_id=container.model_id,
        coupling_rate_per_second=container.coupling_rate_per_second,
        container_digest=container.digest(),
        probe_plan_digest=container.probe_plan_digest,
        probe_digest=container.probe_digest,
        support_count=container.support_count,
        a_d_pair=container.a_d_pair,
        b_d_pair=container.b_d_pair,
        metric=S2WorldPairMetric(
            "d_world_pair",
            abs(container.a_d_pair - container.b_d_pair),
        ),
    )


@dataclass(frozen=True, slots=True)
class S2C16N8ABCanonicalComposition:
    model_id: str
    a_plan_digests: tuple[str, str]
    b_plan_digests: tuple[str, str]
    a_pair: S2R8C8PairResult
    b_pair: S2R8BC8BPairResult
    container: S2N8ABScalarContainer
    distance: S2N8WorldPairDistance

    def __post_init__(self) -> None:
        if self.model_id not in ("b0", "b2"):
            raise S2ReferenceRunnerError("S2-C16 permits only B0 or B2")
        a_plan_digests = tuple(self.a_plan_digests)
        b_plan_digests = tuple(self.b_plan_digests)
        if len(a_plan_digests) != 2 or len(b_plan_digests) != 2:
            raise S2ReferenceRunnerError("S2-C16 requires two A and two B plans")
        if any(
            not _DIGEST.fullmatch(value)
            for value in (*a_plan_digests, *b_plan_digests)
        ):
            raise S2ReferenceRunnerError("S2-C16 plan digest is invalid")
        if not isinstance(self.a_pair, S2R8C8PairResult) or not isinstance(
            self.b_pair,
            S2R8BC8BPairResult,
        ):
            raise S2ReferenceRunnerError("S2-C16 requires typed A8 and B8 pairs")
        if not isinstance(self.container, S2N8ABScalarContainer):
            raise S2ReferenceRunnerError("S2-C16 requires the C14 container")
        if not isinstance(self.distance, S2N8WorldPairDistance):
            raise S2ReferenceRunnerError("S2-C16 requires the C15 distance")
        if any(
            item.model_id != self.model_id
            for item in (self.a_pair, self.b_pair, self.container, self.distance)
        ):
            raise S2ReferenceRunnerError("S2-C16 components require one model arm")
        if (
            self.container.a_d_pair != self.a_pair.d_pair
            or self.container.b_d_pair != self.b_pair.d_pair
        ):
            raise S2ReferenceRunnerError("S2-C16 container differs from its pairs")
        if self.distance.container_digest != self.container.digest():
            raise S2ReferenceRunnerError("S2-C16 distance provenance is broken")
        if self.distance.d_world_pair != abs(
            self.a_pair.d_pair - self.b_pair.d_pair
        ):
            raise S2ReferenceRunnerError("S2-C16 distance differs from its pairs")
        if self.model_id == "b0" and self.distance.d_world_pair != 0.0:
            raise S2ReferenceRunnerError("S2-C16 B0 composition must remain zero")
        object.__setattr__(self, "a_plan_digests", a_plan_digests)
        object.__setattr__(self, "b_plan_digests", b_plan_digests)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "composition_id": "s2.c16.n8-a-b-canonical.v1",
            "model_id": self.model_id,
            "a_plan_digests": self.a_plan_digests,
            "b_plan_digests": self.b_plan_digests,
            "a_pair_digest": _s2_pair_result_digest(self.a_pair, 8),
            "b_pair_digest": _s2_pair_result_digest(self.b_pair, 8),
            "container": self.container.canonical_payload(),
            "distance": self.distance.canonical_payload(),
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def compose_s2c16_n8_ab_reference(
    model_id: str,
) -> S2C16N8ABCanonicalComposition:
    """Compose the canonical A8/B8 reference path entirely in memory."""

    if model_id not in ("b0", "b2"):
        raise S2ReferenceRunnerError("S2-C16 permits only B0 or B2")
    a_plans = prepare_s2c11_r8c8_receptor_plans()
    b_plans = prepare_s2c13_r8bc8b_receptor_plans()
    probe_plan = prepare_s2c4_probe_plan()
    a_results = tuple(
        advance_s2c11_r8c8_world(plan, model_id)
        for plan in a_plans
    )
    b_results = tuple(
        advance_s2c13_r8bc8b_world(plan, model_id)
        for plan in b_plans
    )
    a_pair = measure_s2c11_r8c8_pair(
        *(observe_s2c11_r8c8_probe(result, probe_plan) for result in a_results)
    )
    b_pair = measure_s2c13_r8bc8b_pair(
        *(observe_s2c13_r8bc8b_probe(result, probe_plan) for result in b_results)
    )
    container = assemble_s2c14_n8_ab_scalar_container(a_pair, b_pair)
    distance = measure_s2c15_n8_world_pair_distance(container)
    return S2C16N8ABCanonicalComposition(
        model_id=model_id,
        a_plan_digests=tuple(plan.digest() for plan in a_plans),
        b_plan_digests=tuple(plan.digest() for plan in b_plans),
        a_pair=a_pair,
        b_pair=b_pair,
        container=container,
        distance=distance,
    )


@dataclass(frozen=True, slots=True)
class S2TechnicalControl:
    control_id: str
    passed: bool

    def __post_init__(self) -> None:
        if self.control_id not in S2_CONTROL_IDS:
            raise S2ReferenceRunnerError("unknown S2 control id")
        if not isinstance(self.passed, bool):
            raise S2ReferenceRunnerError("S2 control result must be boolean")

    def canonical_payload(self) -> dict[str, object]:
        return {"control_id": self.control_id, "passed": self.passed}


@dataclass(frozen=True, slots=True)
class S2ReferenceMeasurement:
    task_id: str
    world_id: str
    model_id: str
    intervention_id: str
    start_snapshot_digest: str
    boundary_snapshot_digest: str
    end_snapshot_digest: str
    event_count: int
    audio_hop_count: int
    video_frame_count: int
    field_tick_count: int
    metrics: tuple[S2ScalarMetric, ...]
    controls: tuple[S2TechnicalControl, ...]

    def __post_init__(self) -> None:
        for role in (
            "start_snapshot_digest",
            "boundary_snapshot_digest",
            "end_snapshot_digest",
        ):
            if not _DIGEST.fullmatch(getattr(self, role)):
                raise S2ReferenceRunnerError(f"{role} must be one SHA-256 digest")
        for role in (
            "event_count",
            "audio_hop_count",
            "video_frame_count",
            "field_tick_count",
        ):
            value = getattr(self, role)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise S2ReferenceRunnerError(f"{role} must be nonnegative")
        metrics = tuple(self.metrics)
        controls = tuple(self.controls)
        if tuple(item.metric_id for item in metrics) != S2_METRIC_IDS:
            raise S2ReferenceRunnerError("S2 metrics must use canonical complete order")
        if tuple(item.control_id for item in controls) != S2_CONTROL_IDS:
            raise S2ReferenceRunnerError("S2 controls must use canonical complete order")
        object.__setattr__(self, "metrics", metrics)
        object.__setattr__(self, "controls", controls)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "task_id": self.task_id,
            "world_id": self.world_id,
            "model_id": self.model_id,
            "intervention_id": self.intervention_id,
            "start_snapshot_digest": self.start_snapshot_digest,
            "boundary_snapshot_digest": self.boundary_snapshot_digest,
            "end_snapshot_digest": self.end_snapshot_digest,
            "event_count": self.event_count,
            "audio_hop_count": self.audio_hop_count,
            "video_frame_count": self.video_frame_count,
            "field_tick_count": self.field_tick_count,
            "metrics": [item.canonical_payload() for item in self.metrics],
            "controls": [item.canonical_payload() for item in self.controls],
        }


@dataclass(frozen=True, slots=True)
class S2ReferencePacket:
    schema: str
    inventory_digest: str
    implementation_digest: str
    measurements: tuple[S2ReferenceMeasurement, ...]
    all_technical_controls_passed: bool

    def __post_init__(self) -> None:
        if self.schema != S2_PACKET_SCHEMA:
            raise S2ReferenceRunnerError("unexpected S2 packet schema")
        if not _DIGEST.fullmatch(self.inventory_digest):
            raise S2ReferenceRunnerError("invalid S2 inventory digest")
        if not _DIGEST.fullmatch(self.implementation_digest):
            raise S2ReferenceRunnerError("invalid S2 implementation digest")
        measurements = tuple(self.measurements)
        if len(measurements) != 152:
            raise S2ReferenceRunnerError("S2 packet requires 152 measurements")
        if not isinstance(self.all_technical_controls_passed, bool):
            raise S2ReferenceRunnerError("aggregate S2 control must be boolean")
        object.__setattr__(self, "measurements", measurements)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "inventory_digest": self.inventory_digest,
            "implementation_digest": self.implementation_digest,
            "task_count": len(self.measurements),
            "all_technical_controls_passed": self.all_technical_controls_passed,
            "measurements": [item.canonical_payload() for item in self.measurements],
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


S2MeasurementExecutor = Callable[[S2ReferenceTask], S2ReferenceMeasurement]


def orchestrate_s2_reference_subset(
    tasks: Iterable[S2ReferenceTask],
    executor: S2MeasurementExecutor,
) -> tuple[S2ReferenceMeasurement, ...]:
    """Execute only an explicit technical subset; the full matrix stays gated."""

    tasks_in = tuple(tasks)
    if not tasks_in or any(not isinstance(task, S2ReferenceTask) for task in tasks_in):
        raise S2ReferenceRunnerError("S2 subset requires explicit tasks")
    if len(tasks_in) >= 152:
        raise S2ReferenceRunnerError("S2-C cannot execute the 152-task full matrix")
    if len({task.task_id for task in tasks_in}) != len(tasks_in):
        raise S2ReferenceRunnerError("S2 subset task ids must be unique")
    if not callable(executor):
        raise S2ReferenceRunnerError("S2 subset requires one executor")
    measurements = []
    for task in tasks_in:
        measurement = executor(task)
        if not isinstance(measurement, S2ReferenceMeasurement):
            raise S2ReferenceRunnerError("S2 executor returned an invalid measurement")
        if (
            measurement.task_id != task.task_id
            or measurement.world_id != task.world_id
            or measurement.model_id != task.model_id
            or measurement.intervention_id != task.intervention_id
        ):
            raise S2ReferenceRunnerError("S2 measurement does not match its task")
        measurements.append(measurement)
    return tuple(measurements)


def assemble_s2_reference_packet(
    measurements: Iterable[S2ReferenceMeasurement],
    implementation_digest: str,
) -> S2ReferencePacket:
    """Assemble already measured scalars without executing a world or model."""

    expected = build_s2_reference_tasks()
    supplied = tuple(measurements)
    if len(supplied) != len(expected):
        raise S2ReferenceRunnerError("S2 packet measurements are incomplete")
    by_id = {item.task_id: item for item in supplied}
    if len(by_id) != len(supplied):
        raise S2ReferenceRunnerError("S2 packet measurements contain duplicates")
    ordered = []
    for task in expected:
        measurement = by_id.get(task.task_id)
        if measurement is None:
            raise S2ReferenceRunnerError("S2 packet is missing a canonical task")
        if (
            measurement.world_id,
            measurement.model_id,
            measurement.intervention_id,
        ) != (task.world_id, task.model_id, task.intervention_id):
            raise S2ReferenceRunnerError("S2 packet task roles mismatch")
        ordered.append(measurement)
    passed = all(
        control.passed
        for measurement in ordered
        for control in measurement.controls
    )
    return S2ReferencePacket(
        S2_PACKET_SCHEMA,
        s2_reference_inventory_digest(),
        implementation_digest,
        tuple(ordered),
        passed,
    )


def project_s2_reference_packet(packet: S2ReferencePacket) -> dict[str, object]:
    """Return the scalar JSON projection; no persistence is performed here."""

    if not isinstance(packet, S2ReferencePacket):
        raise S2ReferenceRunnerError("S2 projection requires one packet")
    payload = packet.canonical_payload()
    payload["packet_digest"] = packet.digest()
    encoded = json.dumps(payload, allow_nan=False, sort_keys=True, separators=(",", ":"))
    forbidden = ("audio_samples", "video_frames", "pixels", "trajectory", "run_id", "decision")
    if any(token in encoded for token in forbidden):
        raise S2ReferenceRunnerError("S2 projection contains a forbidden role")
    return payload
