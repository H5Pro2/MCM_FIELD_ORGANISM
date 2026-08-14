"""S1-EC28 small real formation fixture for one S1-EC27 plan pair."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .e1_completion_aligned_refinement import _refined_steps
from .e1_confirmation_prepared_real_formation_kernel import (
    E1PreparedRealFormationArmResult,
    run_prepared_real_formation_arm_in_memory,
)
from .e1_frozen_state_transfer import _load_state, _state_payload
from .e1_local_edge_plasticity import E1LocalEdgePlasticityState
from .e1_refined_chain_canonical_producer import (
    _initial_field_digest,
    _initial_state_digest,
)
from .e1_refined_formation_runner import _digest
from .e1_repetition_formation_planner import (
    E1RepetitionFormationPlanPair,
)
from .receptor_time_model import ReceptorTimeSequence
from .shared_mcm_field import SharedMCMField


class E1RepetitionFormationFixtureConsumerError(ValueError):
    """Raised when the S1-EC28 fixture violates its lifecycle controls."""


S1_EC28_CONSUMER_ID = "e1.repetition-formation-fixture-consumer.s1ec28.v1"
S1_EC28_CONTACT_COUNT = 2
S1_EC28_REFINEMENT_ID = "r2"
S1_EC28_ROLE_BINDINGS = (
    ("repeated_active", "ab", True),
    ("continuous_active", "ba", True),
    ("repeated_formation_ablated", "ab_formation_ablated", False),
)


FormationKernel = Callable[
    [
        str,
        str,
        tuple[ReceptorTimeSequence, ...],
        tuple[object, ...],
        SharedMCMField,
        E1LocalEdgePlasticityState,
        bool,
    ],
    E1PreparedRealFormationArmResult,
]


def _first_support_per_episode(
    sequences: tuple[ReceptorTimeSequence, ...],
    starts: tuple[int, ...],
) -> tuple[ReceptorTimeSequence, ...]:
    result = []
    for sequence in sequences:
        frames = []
        for start in starts:
            candidates = tuple(
                item
                for item in sequence.frames
                if item.field_time.window_start_tick >= start
            )
            if not candidates:
                raise E1RepetitionFormationFixtureConsumerError(
                    "S1-EC28 fixture episode has no receptor support"
                )
            frames.append(candidates[0])
        result.append(
            ReceptorTimeSequence(
                sequence.modality_id,
                sequence.geometry_id,
                sequence.clock_id,
                tuple(frames),
            )
        )
    return tuple(result)


def _fixture_steps(
    sequences: tuple[ReceptorTimeSequence, ...],
) -> tuple[object, ...]:
    clock_ids = {item.clock_id for item in sequences}
    completions = tuple(sorted({
        frame.field_time.window_end_tick
        for sequence in sequences
        for frame in sequence.frames
    }))
    if len(clock_ids) != 1 or len(completions) != 4:
        raise E1RepetitionFormationFixtureConsumerError(
            "S1-EC28 fixture requires four asynchronous AV completion groups"
        )
    return _refined_steps(
        next(iter(clock_ids)),
        1_000_000.0,
        (0, *completions),
        2,
    )


@dataclass(frozen=True, slots=True)
class E1RepetitionFormationFixtureResult:
    consumer_id: str
    source_pair_digest: str
    source_plan_digests_before: tuple[str, str]
    source_plan_digests_after: tuple[str, str]
    fixture_support_count_per_active_arm: int
    fixture_step_count_per_arm: int
    arms: tuple[tuple[str, E1PreparedRealFormationArmResult], ...]
    initial_inputs_preserved: bool
    source_plans_preserved: bool
    output_states_object_separated: bool
    formation_ablation_neutral: bool
    snapshot_restore_roundtrip_exact: bool
    atomic_result_only: bool
    canonical_execution_permitted: bool
    result_decision_permitted: bool
    claims_permitted: bool
    result_digest: str

    def __post_init__(self) -> None:
        if (
            self.consumer_id != S1_EC28_CONSUMER_ID
            or len(self.source_pair_digest) != 64
            or self.source_plan_digests_before != self.source_plan_digests_after
            or self.fixture_support_count_per_active_arm != 4
            or self.fixture_step_count_per_arm != 8
            or tuple(role for role, _ in self.arms)
            != tuple(item[0] for item in S1_EC28_ROLE_BINDINGS)
            or tuple(item.arm_id for _, item in self.arms)
            != tuple(item[1] for item in S1_EC28_ROLE_BINDINGS)
            or any(
                value is not True
                for value in (
                    self.initial_inputs_preserved,
                    self.source_plans_preserved,
                    self.output_states_object_separated,
                    self.formation_ablation_neutral,
                    self.snapshot_restore_roundtrip_exact,
                    self.atomic_result_only,
                )
            )
            or any(
                value is not False
                for value in (
                    self.canonical_execution_permitted,
                    self.result_decision_permitted,
                    self.claims_permitted,
                )
            )
        ):
            raise E1RepetitionFormationFixtureConsumerError(
                "S1-EC28 fixture controls changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"arms", "result_digest"}
        }
        payload["arm_result_digests"] = tuple(
            (role, item.result_digest) for role, item in self.arms
        )
        if self.result_digest != _digest(payload):
            raise E1RepetitionFormationFixtureConsumerError(
                "S1-EC28 fixture digest changed"
            )


def run_repetition_formation_fixture_consumer(
    pair: E1RepetitionFormationPlanPair,
    initial_field: SharedMCMField,
    initial_state: E1LocalEdgePlasticityState,
    *,
    kernel: FormationKernel = run_prepared_real_formation_arm_in_memory,
) -> E1RepetitionFormationFixtureResult:
    """Run three copied-input fixture arms without consuming full plans."""

    if (
        not isinstance(pair, E1RepetitionFormationPlanPair)
        or pair.contact_count != S1_EC28_CONTACT_COUNT
        or not isinstance(initial_field, SharedMCMField)
        or not isinstance(initial_state, E1LocalEdgePlasticityState)
        or not callable(kernel)
    ):
        raise E1RepetitionFormationFixtureConsumerError(
            "S1-EC28 requires one n2 pair, field, state, and kernel"
        )
    pair.__post_init__()
    plan_digests_before = (
        pair.repeated_plans.digest(),
        pair.continuous_plans.digest(),
    )
    field_digest = _initial_field_digest(initial_field)
    state_digest = _initial_state_digest(initial_state)
    repeated = _first_support_per_episode(
        pair.repeated_sequences,
        (0, 2_000_000),
    )
    continuous = _first_support_per_episode(
        pair.continuous_sequences,
        (1_000_000, 2_000_000),
    )
    repeated_steps = _fixture_steps(repeated)
    continuous_steps = _fixture_steps(continuous)
    specs = (
        (S1_EC28_ROLE_BINDINGS[0], repeated, repeated_steps),
        (S1_EC28_ROLE_BINDINGS[1], continuous, continuous_steps),
        (S1_EC28_ROLE_BINDINGS[2], repeated, repeated_steps),
    )
    completed = []
    for (role, arm_id, enabled), sequences, steps in specs:
        arm = kernel(
            arm_id,
            S1_EC28_REFINEMENT_ID,
            sequences,
            steps,
            initial_field,
            initial_state,
            enabled,
        )
        if not isinstance(arm, E1PreparedRealFormationArmResult):
            raise E1RepetitionFormationFixtureConsumerError(
                "S1-EC28 kernel returned no typed arm result"
            )
        completed.append((role, arm))
    arms = tuple(completed)
    states = tuple(item.output_state for _, item in arms)
    restored = tuple(
        _load_state(_state_payload(state), role)
        for (role, _), state in zip(arms, states, strict=True)
    )
    plan_digests_after = (
        pair.repeated_plans.digest(),
        pair.continuous_plans.digest(),
    )
    values = {
        "consumer_id": S1_EC28_CONSUMER_ID,
        "source_pair_digest": pair.pair_digest,
        "source_plan_digests_before": plan_digests_before,
        "source_plan_digests_after": plan_digests_after,
        "fixture_support_count_per_active_arm": sum(
            len(item.frames) for item in repeated
        ),
        "fixture_step_count_per_arm": len(repeated_steps),
        "initial_inputs_preserved": (
            _initial_field_digest(initial_field) == field_digest
            and _initial_state_digest(initial_state) == state_digest
            and all(item.input_objects_preserved for _, item in arms)
        ),
        "source_plans_preserved": plan_digests_before == plan_digests_after,
        "output_states_object_separated": len({id(item) for item in states}) == 3,
        "formation_ablation_neutral": all(
            binding.binding == 0.0 for binding in states[-1].edge_bindings
        ),
        "snapshot_restore_roundtrip_exact": states == restored,
        "atomic_result_only": True,
        "canonical_execution_permitted": False,
        "result_decision_permitted": False,
        "claims_permitted": False,
    }
    payload = dict(values)
    payload["arm_result_digests"] = tuple(
        (role, item.result_digest) for role, item in arms
    )
    return E1RepetitionFormationFixtureResult(
        **values,
        arms=arms,
        result_digest=_digest(payload),
    )
