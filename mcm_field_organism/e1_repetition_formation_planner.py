"""S1-EC27 source and schedule planner without E1 or field execution."""

from __future__ import annotations

from dataclasses import dataclass, replace
import math

from .e1_confirmation_descriptor_refinement_planner import (
    E1ConfirmationDescriptorRefinementPlanSet,
    build_e1_confirmation_descriptor_refinement_plans,
)
from .e1_confirmation_prepared_execution_bundle import E1PreparedExecutionBundle
from .e1_confirmation_prepared_formation_consumer import _typed_values_from_bundle
from .e1_frozen_state_transfer_contract import _probe_digest
from .e1_refined_formation_runner import _digest
from .e1_repetition_formation_contract import (
    E1RepetitionFormationContract,
    S1_EC26_CONTACT_COUNTS,
    S1_EC26_EPISODE_INTEGRALS,
    S1_EC26_EPISODE_TICKS,
    S1_EC26_HORIZON_TICKS,
    S1_EC26_INPUT_BUNDLE_DIGEST,
)
from .receptor_contract import CommonFieldTime
from .receptor_time_model import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)


class E1RepetitionFormationPlannerError(ValueError):
    """Raised when S1-EC27 changes source evidence or schedule exposure."""


S1_EC27_PLANNER_ID = "e1.repetition-formation-planner.s1ec27.v1"


def _replay_episode(
    sequences: tuple[ReceptorTimeSequence, ...],
    starts: tuple[int, ...],
    *,
    role: str,
    contact_count: int,
) -> tuple[ReceptorTimeSequence, ...]:
    result = []
    for sequence in sequences:
        frames = []
        for episode_index, offset in enumerate(starts):
            for item in sequence.frames:
                local_start = item.field_time.window_start_tick
                local_end = item.field_time.window_end_tick
                frame = replace(
                    item.frame,
                    snapshot_id=(
                        f"{item.frame.snapshot_id}.ec27.{role}."
                        f"n{contact_count}.e{episode_index}"
                    ),
                    window_start_tick=(
                        offset + item.frame.window_start_tick
                    ),
                    window_end_tick=(
                        offset + item.frame.window_end_tick
                    ),
                )
                frames.append(
                    OrganismTimedReceptorFrame(
                        frame=frame,
                        field_time=CommonFieldTime(
                            sequence.clock_id,
                            offset + local_start,
                            offset + local_end,
                        ),
                    )
                )
        result.append(
            ReceptorTimeSequence(
                sequence.modality_id,
                sequence.geometry_id,
                sequence.clock_id,
                tuple(frames),
            )
        )
    return tuple(result)


def _episode_payloads(
    sequences: tuple[ReceptorTimeSequence, ...],
    starts: tuple[int, ...],
) -> tuple[tuple[object, ...], ...]:
    payloads = []
    for offset in starts:
        episode = []
        for sequence in sequences:
            matching = tuple(
                item
                for item in sequence.frames
                if offset <= item.field_time.window_start_tick
                and item.field_time.window_end_tick <= offset + S1_EC26_EPISODE_TICKS
            )
            episode.append(
                (
                    sequence.modality_id,
                    sequence.geometry_id,
                    tuple(
                        (
                            item.field_time.window_start_tick - offset,
                            item.field_time.window_end_tick - offset,
                            item.frame.window_start_tick - offset,
                            item.frame.window_end_tick - offset,
                            item.frame.carrier_ids,
                            item.frame.values,
                        )
                        for item in matching
                    ),
                )
            )
        payloads.append(tuple(episode))
    return tuple(payloads)


@dataclass(frozen=True, slots=True)
class E1RepetitionFormationPlanPair:
    contact_count: int
    repeated_sequences: tuple[ReceptorTimeSequence, ...]
    continuous_sequences: tuple[ReceptorTimeSequence, ...]
    repeated_plans: E1ConfirmationDescriptorRefinementPlanSet
    continuous_plans: E1ConfirmationDescriptorRefinementPlanSet
    repeated_sequence_digest: str
    continuous_sequence_digest: str
    neutral_gap_intervals: tuple[tuple[int, int], ...]
    source_payloads_value_identical: bool
    total_exposure_identical: bool
    horizon_identical: bool
    all_supports_assigned_once: bool
    pair_digest: str

    def __post_init__(self) -> None:
        if self.contact_count not in S1_EC26_CONTACT_COUNTS:
            raise E1RepetitionFormationPlannerError(
                "S1-EC27 contact count changed"
            )
        starts = tuple(
            index * 2 * S1_EC26_EPISODE_TICKS
            for index in range(self.contact_count)
        )
        expected_gaps = tuple(
            (
                starts[index] + S1_EC26_EPISODE_TICKS,
                starts[index + 1],
            )
            for index in range(len(starts) - 1)
        )
        expected_events = self.contact_count * 110
        repeated_first = self.repeated_plans.plans[0]
        continuous_first = self.continuous_plans.plans[0]
        if (
            self.neutral_gap_intervals != expected_gaps
            or self.repeated_plans.source_event_count != expected_events
            or self.continuous_plans.source_event_count != expected_events
            or repeated_first.horizon_end_tick != S1_EC26_HORIZON_TICKS
            or continuous_first.horizon_end_tick != S1_EC26_HORIZON_TICKS
            or any(
                len(value) != 64
                for value in (
                    self.repeated_sequence_digest,
                    self.continuous_sequence_digest,
                    self.pair_digest,
                )
            )
            or any(
                value is not True
                for value in (
                    self.source_payloads_value_identical,
                    self.total_exposure_identical,
                    self.horizon_identical,
                    self.all_supports_assigned_once,
                )
            )
        ):
            raise E1RepetitionFormationPlannerError(
                "S1-EC27 plan pair changed exposure or support assignment"
            )
        payload = {
            "contact_count": self.contact_count,
            "repeated_sequence_digest": self.repeated_sequence_digest,
            "continuous_sequence_digest": self.continuous_sequence_digest,
            "repeated_plan_digest": self.repeated_plans.digest(),
            "continuous_plan_digest": self.continuous_plans.digest(),
            "neutral_gap_intervals": self.neutral_gap_intervals,
            "source_payloads_value_identical": self.source_payloads_value_identical,
            "total_exposure_identical": self.total_exposure_identical,
            "horizon_identical": self.horizon_identical,
            "all_supports_assigned_once": self.all_supports_assigned_once,
        }
        if self.pair_digest != _digest(payload):
            raise E1RepetitionFormationPlannerError(
                "S1-EC27 pair digest changed"
            )


@dataclass(frozen=True, slots=True)
class E1RepetitionFormationPlanSet:
    planner_id: str
    contract_digest: str
    input_bundle_digest: str
    pairs: tuple[E1RepetitionFormationPlanPair, ...]
    all_exposure_gates_passed: bool
    field_execution_performed: bool
    e1_state_constructed: bool
    result_decision_permitted: bool
    claims_permitted: bool
    plan_set_digest: str

    def __post_init__(self) -> None:
        if (
            self.planner_id != S1_EC27_PLANNER_ID
            or len(self.contract_digest) != 64
            or self.input_bundle_digest != S1_EC26_INPUT_BUNDLE_DIGEST
            or tuple(item.contact_count for item in self.pairs)
            != S1_EC26_CONTACT_COUNTS
            or self.all_exposure_gates_passed is not True
            or any(
                value is not False
                for value in (
                    self.field_execution_performed,
                    self.e1_state_constructed,
                    self.result_decision_permitted,
                    self.claims_permitted,
                )
            )
        ):
            raise E1RepetitionFormationPlannerError(
                "S1-EC27 plan set exceeded its technical boundary"
            )
        payload = {
            "planner_id": self.planner_id,
            "contract_digest": self.contract_digest,
            "input_bundle_digest": self.input_bundle_digest,
            "pair_digests": tuple(item.pair_digest for item in self.pairs),
            "all_exposure_gates_passed": self.all_exposure_gates_passed,
            "field_execution_performed": self.field_execution_performed,
            "e1_state_constructed": self.e1_state_constructed,
            "result_decision_permitted": self.result_decision_permitted,
            "claims_permitted": self.claims_permitted,
        }
        if self.plan_set_digest != _digest(payload):
            raise E1RepetitionFormationPlannerError(
                "S1-EC27 plan-set digest changed"
            )


def build_e1_repetition_formation_plans(
    contract: E1RepetitionFormationContract,
    bundle: E1PreparedExecutionBundle,
) -> E1RepetitionFormationPlanSet:
    """Materialize only receptor schedules and completion-aligned plans."""

    if not isinstance(contract, E1RepetitionFormationContract):
        raise E1RepetitionFormationPlannerError(
            "S1-EC27 requires the current S1-EC26 contract"
        )
    if not isinstance(bundle, E1PreparedExecutionBundle):
        raise E1RepetitionFormationPlannerError(
            "S1-EC27 requires the canonical prepared bundle"
        )
    contract.__post_init__()
    bundle.__post_init__()
    if (
        contract.input_bundle_digest != bundle.bundle_digest
        or contract.planner_implementation_permitted is not True
        or contract.field_execution_permitted is not False
    ):
        raise E1RepetitionFormationPlannerError(
            "S1-EC27 contract and bundle are not aligned"
        )
    values = _typed_values_from_bundle(bundle)
    episode = tuple(values.probe_sequences)
    pairs = []
    for schedule in contract.schedules:
        count = schedule.contact_count
        repeated_starts = schedule.repeated_start_ticks
        continuous_starts = tuple(
            schedule.continuous_start_tick
            + index * S1_EC26_EPISODE_TICKS
            for index in range(count)
        )
        repeated = _replay_episode(
            episode,
            repeated_starts,
            role="repeated",
            contact_count=count,
        )
        continuous = _replay_episode(
            episode,
            continuous_starts,
            role="continuous",
            contact_count=count,
        )
        repeated_plans = build_e1_confirmation_descriptor_refinement_plans(
            values.corridor,
            repeated,
            horizon_start_tick=0,
            horizon_end_tick=S1_EC26_HORIZON_TICKS,
            ticks_per_second=1_000_000.0,
        )
        continuous_plans = build_e1_confirmation_descriptor_refinement_plans(
            values.corridor,
            continuous,
            horizon_start_tick=0,
            horizon_end_tick=S1_EC26_HORIZON_TICKS,
            ticks_per_second=1_000_000.0,
        )
        repeated_integrals = (
            repeated_plans.plans[0].source_signed_integral,
            repeated_plans.plans[0].source_absolute_integral,
            repeated_plans.plans[0].source_quadratic_integral,
        )
        continuous_integrals = (
            continuous_plans.plans[0].source_signed_integral,
            continuous_plans.plans[0].source_absolute_integral,
            continuous_plans.plans[0].source_quadratic_integral,
        )
        expected_integrals = tuple(
            count * value for value in S1_EC26_EPISODE_INTEGRALS
        )
        repeated_payloads = _episode_payloads(repeated, repeated_starts)
        continuous_payloads = _episode_payloads(continuous, continuous_starts)
        base_payload = repeated_payloads[0]
        payload_identical = (
            all(item == base_payload for item in repeated_payloads)
            and all(item == base_payload for item in continuous_payloads)
        )
        exposure_identical = (
            repeated_integrals == continuous_integrals
            and all(
                math.isclose(observed, expected, rel_tol=0.0, abs_tol=1e-14)
                for observed, expected in zip(
                    repeated_integrals, expected_integrals, strict=True
                )
            )
        )
        gaps = tuple(
            (
                repeated_starts[index] + S1_EC26_EPISODE_TICKS,
                repeated_starts[index + 1],
            )
            for index in range(len(repeated_starts) - 1)
        )
        pair_payload = {
            "contact_count": count,
            "repeated_sequence_digest": _probe_digest(repeated),
            "continuous_sequence_digest": _probe_digest(continuous),
            "repeated_plan_digest": repeated_plans.digest(),
            "continuous_plan_digest": continuous_plans.digest(),
            "neutral_gap_intervals": gaps,
            "source_payloads_value_identical": payload_identical,
            "total_exposure_identical": exposure_identical,
            "horizon_identical": all(
                plan.horizon_end_tick == S1_EC26_HORIZON_TICKS
                for plan in (*repeated_plans.plans, *continuous_plans.plans)
            ) and repeated_plans.completion_ticks[-1]
            == continuous_plans.completion_ticks[-1],
            "all_supports_assigned_once": all(
                plan.handoff.every_in_horizon_event_assigned_once
                for plan in (*repeated_plans.plans, *continuous_plans.plans)
            ),
        }
        pairs.append(
            E1RepetitionFormationPlanPair(
                contact_count=count,
                repeated_sequences=repeated,
                continuous_sequences=continuous,
                repeated_plans=repeated_plans,
                continuous_plans=continuous_plans,
                repeated_sequence_digest=pair_payload[
                    "repeated_sequence_digest"
                ],
                continuous_sequence_digest=pair_payload[
                    "continuous_sequence_digest"
                ],
                neutral_gap_intervals=gaps,
                source_payloads_value_identical=payload_identical,
                total_exposure_identical=exposure_identical,
                horizon_identical=pair_payload["horizon_identical"],
                all_supports_assigned_once=pair_payload[
                    "all_supports_assigned_once"
                ],
                pair_digest=_digest(pair_payload),
            )
        )
    plan_payload = {
        "planner_id": S1_EC27_PLANNER_ID,
        "contract_digest": contract.contract_digest,
        "input_bundle_digest": bundle.bundle_digest,
        "pair_digests": tuple(item.pair_digest for item in pairs),
        "all_exposure_gates_passed": True,
        "field_execution_performed": False,
        "e1_state_constructed": False,
        "result_decision_permitted": False,
        "claims_permitted": False,
    }
    return E1RepetitionFormationPlanSet(
        planner_id=S1_EC27_PLANNER_ID,
        contract_digest=contract.contract_digest,
        input_bundle_digest=bundle.bundle_digest,
        pairs=tuple(pairs),
        all_exposure_gates_passed=True,
        field_execution_performed=False,
        e1_state_constructed=False,
        result_decision_permitted=False,
        claims_permitted=False,
        plan_set_digest=_digest(plan_payload),
    )
