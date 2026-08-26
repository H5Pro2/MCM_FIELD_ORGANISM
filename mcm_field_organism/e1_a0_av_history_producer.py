"""Private S1-DG A0 history producer without probe or public API roles."""

from __future__ import annotations

import copy
from dataclasses import dataclass
import hashlib
import json
import math

from .audio_video_field_geometry import (
    ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    audio_video_dock_anatomies,
)
from .e1_asynchronous_field_runtime import (
    E1AsynchronousFieldRuntimeError,
    run_e1_asynchronous_field,
)
from .e1_av_history_permutation import E1AVHistoryPermutation
from .e1_local_edge_plasticity import (
    E1_CONTRACT_ID,
    E1LocalEdgePlasticityContract,
    E1LocalEdgePlasticityError,
    E1LocalEdgePlasticityState,
    build_neutral_e1_state,
    e1_free_node_resources,
    validate_e1_state_for_layer,
)
from .field_step_time import MCMFieldStepTime
from .neutral_asynchronous_field_runtime import (
    NeutralAsynchronousFieldRuntimeError,
    run_neutral_asynchronous_field,
)
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .receptor_proposal_handoff import ReceptorProposalHandoff
from .shared_mcm_field import SharedMCMField, SharedMCMFieldError, build_shared_mcm_field


class E1A0AVHistoryProducerError(ValueError):
    """Raised when controlled P0/A0 histories cannot be kept isolated."""


_CLOCK_ID = "organism.e1.av-history"
_HORIZON_TICKS = 2_000_000
_TICKS_PER_SECOND = 1_000_000.0
_AB_DIGEST = "a48d3d1620afa82d12dda855bb2ec03de3a57e7a69488d46edba6ec99cbef6d6"
_BA_DIGEST = "bb1d887f1ff5809964ae8175c7fa661430e8fbc8502f0522a7003d6c6fc3c011"
_PERMUTATION_DIGEST = (
    "ad509ef23a9394009baddc8185edc5a13f76882ee79e7c31d3b0ec111bfbcc78"
)
_EXPECTED_SOURCE_SUPPORTS = 220


def _sha256(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _state_payload(state: E1LocalEdgePlasticityState) -> dict[str, object]:
    return {
        "contract": {
            "contract_id": state.contract.contract_id,
            "node_capacity": state.contract.node_capacity,
            "binding_rate_per_second": state.contract.binding_rate_per_second,
            "release_rate_per_second": state.contract.release_rate_per_second,
            "backreaction_gain": state.contract.backreaction_gain,
        },
        "edge_inventory_digest": state.edge_inventory_digest,
        "edge_bindings": [
            [item.first_neuron_id, item.second_neuron_id, item.binding]
            for item in state.edge_bindings
        ],
    }


def _fresh_field_digest(field: SharedMCMField) -> str:
    if field.last_distribution is not None:
        raise E1A0AVHistoryProducerError(
            "fresh-field digest requires an unused receptor field"
        )
    return _sha256(
        {
            "layer_digest": field.layer.digest(),
            "docks": [
                {
                    "dock_id": dock.dock_id,
                    "modality_id": dock.dock_map.modality_id,
                    "geometry_id": dock.dock_map.receptor_geometry_id,
                    "pairs": dock.dock_map.pairs,
                }
                for dock in field.docks
            ],
            "last_distribution": None,
            "substrate": None if field.substrate is None else "present",
            "development": None if field.development is None else "present",
        }
    )


def _handoff_digest(handoff: ReceptorProposalHandoff) -> str:
    return _sha256(
        {
            "clock_id": handoff.clock_id,
            "modality_ids": handoff.modality_ids,
            "source_event_count": handoff.source_event_count,
            "assigned_event_count": handoff.assigned_event_count,
            "before": handoff.completed_before_or_at_start_snapshot_ids,
            "after": handoff.completed_after_horizon_snapshot_ids,
            "assigned_once": handoff.every_in_horizon_event_assigned_once,
            "batches": [
                {
                    "batch_index": batch.batch_index,
                    "step": [
                        batch.step_time.clock_id,
                        batch.step_time.start_tick,
                        batch.step_time.end_tick,
                        batch.step_time.ticks_per_second,
                    ],
                    "groups": [
                        {
                            "completion_tick": group.completion_tick,
                            "snapshot_ids": [
                                item.frame.snapshot_id
                                for item in group.timed_frames
                            ],
                        }
                        for group in batch.completion_groups
                    ],
                }
                for batch in handoff.batches
            ],
        }
    )


def _resource_budget_error(
    field: SharedMCMField,
    state: E1LocalEdgePlasticityState,
) -> float:
    free = e1_free_node_resources(field.layer, state)
    expected = len(field.layer.neurons) * state.contract.node_capacity
    observed = math.fsum(value for _, value in free) + math.fsum(
        item.binding for item in state.edge_bindings
    )
    return abs(expected - observed)


@dataclass(frozen=True, slots=True)
class E1A0AVHistoryArmAudit:
    """One history arm after exact P0/A0 and handoff validation."""

    history_id: str
    initial_field_digest: str
    p0_field_digest: str
    a0_field_digest: str
    handoff_digest: str
    source_support_count: int
    assigned_event_count: int
    resource_budget_error: float
    all_adapters_ablated: bool

    def __post_init__(self) -> None:
        if self.history_id not in {"ab", "ba"}:
            raise E1A0AVHistoryProducerError("history audit id is invalid")
        for role in (
            "initial_field_digest",
            "p0_field_digest",
            "a0_field_digest",
            "handoff_digest",
        ):
            value = getattr(self, role)
            if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
                raise E1A0AVHistoryProducerError(f"{role} is not SHA-256")
        if self.p0_field_digest != self.a0_field_digest:
            raise E1A0AVHistoryProducerError(
                f"{self.history_id} A0 field differs from its P0 baseline"
            )
        if (
            isinstance(self.source_support_count, bool)
            or not isinstance(self.source_support_count, int)
            or self.source_support_count < 1
            or self.assigned_event_count != self.source_support_count
        ):
            raise E1A0AVHistoryProducerError(
                f"{self.history_id} source supports are incomplete"
            )
        if (
            not math.isfinite(self.resource_budget_error)
            or self.resource_budget_error > 1e-12
        ):
            raise E1A0AVHistoryProducerError(
                f"{self.history_id} E1 resource identity failed"
            )
        if self.all_adapters_ablated is not True:
            raise E1A0AVHistoryProducerError(
                f"{self.history_id} history enabled E1 backreaction"
            )


@dataclass(frozen=True, slots=True)
class E1A0AVHistoryProduction:
    """Only E1 end states and audits; historical fields never leave the core."""

    b_ab: E1LocalEdgePlasticityState
    b_ba: E1LocalEdgePlasticityState
    history_ab_digest: str
    history_ba_digest: str
    permutation_digest: str
    initial_geometry_digest: str
    initial_field_digest: str
    arm_audits: tuple[E1A0AVHistoryArmAudit, E1A0AVHistoryArmAudit]
    production_digest: str

    def __post_init__(self) -> None:
        if not isinstance(self.b_ab, E1LocalEdgePlasticityState) or not isinstance(
            self.b_ba, E1LocalEdgePlasticityState
        ):
            raise E1A0AVHistoryProducerError(
                "history production requires two E1 end states"
            )
        for role in (
            "history_ab_digest",
            "history_ba_digest",
            "permutation_digest",
            "initial_geometry_digest",
            "initial_field_digest",
            "production_digest",
        ):
            value = getattr(self, role)
            if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
                raise E1A0AVHistoryProducerError(f"{role} is not SHA-256")
        audits = tuple(self.arm_audits)
        if tuple(item.history_id for item in audits) != ("ab", "ba"):
            raise E1A0AVHistoryProducerError(
                "history production requires ordered AB and BA audits"
            )
        if any(
            item.initial_field_digest != self.initial_field_digest
            for item in audits
        ):
            raise E1A0AVHistoryProducerError(
                "history arms did not start from one value-identical snapshot"
            )
        if self.b_ab is self.b_ba:
            raise E1A0AVHistoryProducerError(
                "history end states must remain object-separated"
            )
        object.__setattr__(self, "arm_audits", audits)


def _validate_fixed_runtime_contract(
    proposal_steps: tuple[MCMFieldStepTime, ...],
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
) -> None:
    expected_step = MCMFieldStepTime(
        _CLOCK_ID,
        0,
        _HORIZON_TICKS,
        _TICKS_PER_SECOND,
    )
    if proposal_steps != (expected_step,):
        raise E1A0AVHistoryProducerError("S1-DG proposal horizon changed")
    if substrate_config != NeutralLocalFieldSubstrateConfig(1.0):
        raise E1A0AVHistoryProducerError("S1-DG S response contract changed")
    if afterimage_config != NeutralFastAfterimageConfig(0.5):
        raise E1A0AVHistoryProducerError("S1-DG H time contract changed")


def _produce_e1_a0_av_histories(
    source: E1AVHistoryPermutation,
    initial_field: SharedMCMField,
    initial_e1_state: E1LocalEdgePlasticityState,
    proposal_steps: tuple[MCMFieldStepTime, ...],
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
) -> E1A0AVHistoryProduction:
    """Execute one already preflighted source with fresh private P0/A0 arms."""

    if not isinstance(source, E1AVHistoryPermutation):
        raise E1A0AVHistoryProducerError(
            "S1-DG requires one reduced AB/BA source"
        )
    if not isinstance(initial_field, SharedMCMField):
        raise E1A0AVHistoryProducerError("S1-DG requires one initial field")
    if (
        initial_field.layer.tick != 0
        or initial_field.last_distribution is not None
        or initial_field.substrate is not None
    ):
        raise E1A0AVHistoryProducerError("S1-DG requires one fresh initial field")
    _validate_fixed_runtime_contract(
        proposal_steps,
        substrate_config,
        afterimage_config,
    )
    try:
        validate_e1_state_for_layer(initial_field.layer, initial_e1_state)
    except E1LocalEdgePlasticityError as exc:
        raise E1A0AVHistoryProducerError(str(exc)) from exc
    if any(item.binding != 0.0 for item in initial_e1_state.edge_bindings):
        raise E1A0AVHistoryProducerError(
            "S1-DG requires one neutral initial E1 state"
        )

    initial_field_digest = _fresh_field_digest(initial_field)
    initial_geometry_digest = initial_field.layer.digest()
    initial_state_payload = _state_payload(initial_e1_state)
    fields = tuple(copy.deepcopy(initial_field) for _ in range(4))
    states = tuple(copy.deepcopy(initial_e1_state) for _ in range(2))
    if len({id(item) for item in fields}) != 4 or states[0] is states[1]:
        raise E1A0AVHistoryProducerError("S1-DG arm objects are not fresh")
    if any(_fresh_field_digest(item) != initial_field_digest for item in fields):
        raise E1A0AVHistoryProducerError("S1-DG initial field copies changed")

    audits = []
    end_states = []
    histories = (("ab", source.history_ab), ("ba", source.history_ba))
    try:
        for index, (history_id, sequences) in enumerate(histories):
            p0 = run_neutral_asynchronous_field(
                fields[index * 2],
                sequences,
                proposal_steps,
                substrate_config,
                afterimage_config=afterimage_config,
            )
            a0 = run_e1_asynchronous_field(
                fields[index * 2 + 1],
                states[index],
                sequences,
                proposal_steps,
                substrate_config,
                afterimage_config,
                backreaction_enabled=False,
            )
            p0_handoff_digest = _handoff_digest(p0.handoff)
            a0_handoff_digest = _handoff_digest(a0.handoff)
            if p0_handoff_digest != a0_handoff_digest:
                raise E1A0AVHistoryProducerError(
                    f"{history_id} P0/A0 handoff differs"
                )
            all_ablated = all(
                not adapter.backreaction_enabled
                for step in a0.steps
                for adapter in step.applied_adapters
            )
            audits.append(
                E1A0AVHistoryArmAudit(
                    history_id=history_id,
                    initial_field_digest=initial_field_digest,
                    p0_field_digest=p0.field.snapshot().digest(),
                    a0_field_digest=a0.field.snapshot().digest(),
                    handoff_digest=p0_handoff_digest,
                    source_support_count=a0.source_support_count,
                    assigned_event_count=a0.handoff.assigned_event_count,
                    resource_budget_error=_resource_budget_error(
                        a0.field,
                        a0.e1_state,
                    ),
                    all_adapters_ablated=all_ablated,
                )
            )
            end_states.append(a0.e1_state)
    except (
        E1A0AVHistoryProducerError,
        E1AsynchronousFieldRuntimeError,
        NeutralAsynchronousFieldRuntimeError,
        ValueError,
    ) as exc:
        if isinstance(exc, E1A0AVHistoryProducerError):
            raise
        raise E1A0AVHistoryProducerError(str(exc)) from exc

    if _fresh_field_digest(initial_field) != initial_field_digest or (
        _state_payload(initial_e1_state) != initial_state_payload
    ):
        raise E1A0AVHistoryProducerError("S1-DG changed its initial inputs")
    production_payload = {
        "contract_id": "e1.a0.av-history-production.v1",
        "source": [
            source.history_ab_digest,
            source.history_ba_digest,
            source.permutation_digest,
        ],
        "initial_geometry_digest": initial_geometry_digest,
        "initial_field_digest": initial_field_digest,
        "states": [_state_payload(item) for item in end_states],
        "audits": [
            {
                "history_id": item.history_id,
                "p0_field_digest": item.p0_field_digest,
                "a0_field_digest": item.a0_field_digest,
                "handoff_digest": item.handoff_digest,
                "source_support_count": item.source_support_count,
                "resource_budget_error": item.resource_budget_error,
            }
            for item in audits
        ],
    }
    return E1A0AVHistoryProduction(
        b_ab=end_states[0],
        b_ba=end_states[1],
        history_ab_digest=source.history_ab_digest,
        history_ba_digest=source.history_ba_digest,
        permutation_digest=source.permutation_digest,
        initial_geometry_digest=initial_geometry_digest,
        initial_field_digest=initial_field_digest,
        arm_audits=(audits[0], audits[1]),
        production_digest=_sha256(production_payload),
    )


def _validate_canonical_source(source: E1AVHistoryPermutation) -> None:
    if not isinstance(source, E1AVHistoryPermutation):
        raise E1A0AVHistoryProducerError(
            "canonical S1-DG production requires one S1-DE source"
        )
    if (
        source.history_ab_digest != _AB_DIGEST
        or source.history_ba_digest != _BA_DIGEST
        or source.permutation_digest != _PERMUTATION_DIGEST
    ):
        raise E1A0AVHistoryProducerError("canonical S1-DE source digest changed")
    expected_counts = (("auditory", 200), ("visual", 20))
    if tuple(
        (sequence.modality_id, len(sequence.frames))
        for sequence in source.history_ab
    ) != expected_counts or any(
        audit.frame_count != count
        for audit, (_, count) in zip(
            source.modality_audits,
            expected_counts,
            strict=True,
        )
    ):
        raise E1A0AVHistoryProducerError("canonical S1-DE frame inventory changed")
    if sum(count for _, count in expected_counts) != _EXPECTED_SOURCE_SUPPORTS:
        raise E1A0AVHistoryProducerError("canonical source support contract changed")


def produce_e1_a0_av_histories(
    source: E1AVHistoryPermutation,
) -> E1A0AVHistoryProduction:
    """Run the exact canonical source only after all S1-DF bindings hold."""

    _validate_canonical_source(source)
    auditory, visual = source.history_ab
    if len(auditory.frames[0].frame.carrier_ids) != 12 or len(
        visual.frames[0].frame.carrier_ids
    ) != 72:
        raise E1A0AVHistoryProducerError("canonical AV carrier inventory changed")
    try:
        field = build_shared_mcm_field(
            (auditory.frames[0].frame, visual.frames[0].frame),
            audio_video_dock_anatomies(
                auditory_carrier_count=12,
                visual_grid_columns=6,
                visual_grid_rows=4,
                visual_channel_count=3,
            ),
            sample_offsets=ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
        )
        if len(field.layer.neurons) != 84:
            raise E1A0AVHistoryProducerError(
                "canonical S1-DG field must contain 84 nodes"
            )
        contract = E1LocalEdgePlasticityContract(
            E1_CONTRACT_ID,
            1.0,
            1.5,
            0.25,
            0.5,
        )
        state = build_neutral_e1_state(field.layer, contract)
    except (
        E1A0AVHistoryProducerError,
        E1LocalEdgePlasticityError,
        SharedMCMFieldError,
        ValueError,
    ) as exc:
        if isinstance(exc, E1A0AVHistoryProducerError):
            raise
        raise E1A0AVHistoryProducerError(str(exc)) from exc
    return _produce_e1_a0_av_histories(
        source,
        field,
        state,
        (
            MCMFieldStepTime(
                _CLOCK_ID,
                0,
                _HORIZON_TICKS,
                _TICKS_PER_SECOND,
            ),
        ),
        NeutralLocalFieldSubstrateConfig(1.0),
        NeutralFastAfterimageConfig(0.5),
    )
