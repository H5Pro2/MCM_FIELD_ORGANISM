"""Private S1-EC21 seven-arm probe consumer with synthetic fixture states."""

from __future__ import annotations

import copy
from dataclasses import dataclass
import math
from typing import Callable

import numpy as np

from .e1_confirmation_published_probe_handoff_audit import (
    E1PublishedProbeHandoffAudit,
    S1_EC20_PROBE_ARMS,
    S1_EC20_REFINEMENTS,
)
from .e1_confirmation_prepared_execution_bundle import E1PreparedExecutionBundle
from .e1_confirmation_prepared_formation_consumer import _typed_values_from_bundle
from .e1_confirmation_small_refinement_matrix import E1SmallRefinementMatrixResult
from .e1_frozen_state_transfer import (
    _field_vector,
    _fresh_field_digest,
    _state_payload,
)
from .e1_frozen_state_transfer_contract import _probe_digest
from .e1_frozen_transient_probe import (
    advance_fixed_e1_adapter_fast_shared_field_transient,
    advance_frozen_e1_fast_shared_field_transient,
)
from .e1_refined_formation_runner import _digest
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    advance_neutral_fast_shared_field_transient,
)
from .receptor_contract import CommonFieldTime
from .receptor_distributor import ReceptorDistribution
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import project_transient_docks_to_neuron_inputs


class E1ConfirmationPublishedProbeFixtureConsumerError(ValueError):
    """Raised when the S1-EC21 fixture probe loses a registered invariant."""


S1_EC21_CONSUMER_ID = "e1.published-probe-fixture-consumer.s1ec21.v1"
S1_EC21_FORMATION_SOURCE = "synthetic-full-geometry-small-step-fixture"


def _valid_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


def _vector(field, role: str) -> tuple[float, ...]:
    values = tuple(float(value) for value in _field_vector(field, role))
    if not values or any(not math.isfinite(value) for value in values):
        raise E1ConfirmationPublishedProbeFixtureConsumerError(
            "S1-EC21 probe vector is invalid"
        )
    return values


def _linf(first: tuple[float, ...], second: tuple[float, ...]) -> float:
    if len(first) != len(second) or not first:
        raise E1ConfirmationPublishedProbeFixtureConsumerError(
            "S1-EC21 probe vectors changed geometry"
        )
    return float(np.max(np.abs(np.asarray(first) - np.asarray(second))))


@dataclass(frozen=True, slots=True)
class E1PublishedProbeFixtureRefinementResult:
    refinement_id: str
    field_digests: tuple[tuple[str, str], ...]
    ab_active_s: tuple[float, ...]
    ba_active_s: tuple[float, ...]
    ab_active_h: tuple[float, ...]
    ba_active_h: tuple[float, ...]
    active_s_linf: float
    active_h_linf: float
    probe_ablation_residual: float
    fixed_adapter_residual: float
    frozen_state_change: float
    initial_fields_identical_and_separate: bool
    supports_assigned_once: bool
    result_digest: str

    def __post_init__(self) -> None:
        vectors = (
            tuple(self.ab_active_s),
            tuple(self.ba_active_s),
            tuple(self.ab_active_h),
            tuple(self.ba_active_h),
        )
        numeric = (
            self.active_s_linf,
            self.active_h_linf,
            self.probe_ablation_residual,
            self.fixed_adapter_residual,
            self.frozen_state_change,
        )
        if (
            self.refinement_id not in S1_EC20_REFINEMENTS
            or tuple(role for role, _ in self.field_digests) != S1_EC20_PROBE_ARMS
            or any(not _valid_digest(value) for _, value in self.field_digests)
            or len({len(item) for item in vectors}) != 1
            or not vectors[0]
            or any(not math.isfinite(value) for item in vectors for value in item)
            or any(not math.isfinite(value) or value < 0.0 for value in numeric)
            or self.active_s_linf != _linf(vectors[0], vectors[1])
            or self.active_h_linf != _linf(vectors[2], vectors[3])
            or self.probe_ablation_residual != 0.0
            or self.fixed_adapter_residual != 0.0
            or self.frozen_state_change != 0.0
            or self.initial_fields_identical_and_separate is not True
            or self.supports_assigned_once is not True
            or not _valid_digest(self.result_digest)
        ):
            raise E1ConfirmationPublishedProbeFixtureConsumerError(
                "S1-EC21 refinement result changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "result_digest"
        }
        if self.result_digest != _digest(payload):
            raise E1ConfirmationPublishedProbeFixtureConsumerError(
                "S1-EC21 refinement digest changed"
            )


@dataclass(frozen=True, slots=True)
class E1PublishedProbeFixtureMatrixResult:
    consumer_id: str
    audit_digest: str
    input_bundle_digest: str
    fixture_matrix_digest: str
    probe_source_digest: str
    probe_plan_set_digest: str
    fixture_probe_source_digest: str
    fixture_probe_plan_set_digest: str
    refinements: tuple[E1PublishedProbeFixtureRefinementResult, ...]
    r2_r4_probe_residual: float
    r4_r8_probe_residual: float
    convergence_nonincreasing: bool
    all_registered_controls_passed: bool
    fixture_payload_only: bool
    persistent_states_consumed: bool
    registered_probe_consumed: bool
    probe_execution_permitted: bool
    result_decision_permitted: bool
    claims_permitted: bool
    result_digest: str

    def __post_init__(self) -> None:
        refinements = tuple(self.refinements)
        if (
            self.consumer_id != S1_EC21_CONSUMER_ID
            or any(
                not _valid_digest(value)
                for value in (
                    self.audit_digest,
                    self.input_bundle_digest,
                    self.fixture_matrix_digest,
                    self.probe_source_digest,
                    self.probe_plan_set_digest,
                    self.fixture_probe_source_digest,
                    self.fixture_probe_plan_set_digest,
                    self.result_digest,
                )
            )
            or tuple(item.refinement_id for item in refinements)
            != S1_EC20_REFINEMENTS
            or not math.isfinite(self.r2_r4_probe_residual)
            or not math.isfinite(self.r4_r8_probe_residual)
            or self.r2_r4_probe_residual < 0.0
            or self.r4_r8_probe_residual < 0.0
            or self.convergence_nonincreasing
            is not (self.r4_r8_probe_residual <= self.r2_r4_probe_residual)
            or self.all_registered_controls_passed is not True
            or self.fixture_payload_only is not True
            or self.persistent_states_consumed is not False
            or self.registered_probe_consumed is not False
            or self.probe_execution_permitted is not False
            or self.result_decision_permitted is not False
            or self.claims_permitted is not False
        ):
            raise E1ConfirmationPublishedProbeFixtureConsumerError(
                "S1-EC21 matrix result changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"refinements", "result_digest"}
        }
        payload["refinement_result_digests"] = tuple(
            item.result_digest for item in refinements
        )
        if self.result_digest != _digest(payload):
            raise E1ConfirmationPublishedProbeFixtureConsumerError(
                "S1-EC21 matrix digest changed"
            )
        object.__setattr__(self, "refinements", refinements)


def _run_refinement_fixture(
    refinement,
    plan,
    initial_field,
    runtime_guard: Callable[[], None] | None = None,
) -> E1PublishedProbeFixtureRefinementResult:
    if runtime_guard is not None and not callable(runtime_guard):
        raise E1ConfirmationPublishedProbeFixtureConsumerError(
            "S1-EC21 runtime guard is invalid"
        )
    arms = {item.arm_id: item for item in refinement.arms}
    ab_state = arms["ab"].output_state
    ba_state = arms["ba"].output_state
    before_ab = _digest(_state_payload(ab_state))
    before_ba = _digest(_state_payload(ba_state))
    fields = tuple(copy.deepcopy(initial_field) for _ in S1_EC20_PROBE_ARMS)
    if len({id(item) for item in fields}) != len(fields):
        raise E1ConfirmationPublishedProbeFixtureConsumerError(
            "S1-EC21 probe fields are not object-separated"
        )
    initial_digests = tuple(_fresh_field_digest(item) for item in fields)
    if len(set(initial_digests)) != 1:
        raise E1ConfirmationPublishedProbeFixtureConsumerError(
            "S1-EC21 probe fields are not initially identical"
        )
    supports_once = (
        plan.handoff.assigned_event_count == plan.handoff.source_event_count
        and plan.handoff.every_in_horizon_event_assigned_once
        and not plan.handoff.completed_before_or_at_start_snapshot_ids
        and not plan.handoff.completed_after_horizon_snapshot_ids
    )
    if not supports_once:
        raise E1ConfirmationPublishedProbeFixtureConsumerError(
            "S1-EC21 probe supports changed"
        )

    substrate = NeutralLocalFieldSubstrateConfig(1.0)
    afterimage = NeutralFastAfterimageConfig(0.5)
    current = list(fields)
    for batch in plan.handoff.batches:
        if runtime_guard is not None:
            runtime_guard()
        trajectory = map_proposal_batch_to_transient_docks(batch, current[0].docks)
        inputs = project_transient_docks_to_neuron_inputs(
            trajectory, current[0].docks
        )
        distribution = ReceptorDistribution(
            CommonFieldTime(
                batch.step_time.clock_id,
                batch.step_time.start_tick,
                batch.step_time.end_tick,
            ),
            (),
        )
        current[0] = advance_neutral_fast_shared_field_transient(
            current[0], distribution, inputs, substrate, afterimage
        )
        ab0 = advance_frozen_e1_fast_shared_field_transient(
            current[1], ab_state, distribution, inputs, substrate, afterimage,
            backreaction_enabled=False,
        )
        ba0 = advance_frozen_e1_fast_shared_field_transient(
            current[2], ba_state, distribution, inputs, substrate, afterimage,
            backreaction_enabled=False,
        )
        ab1 = advance_frozen_e1_fast_shared_field_transient(
            current[3], ab_state, distribution, inputs, substrate, afterimage,
            backreaction_enabled=True,
        )
        ba1 = advance_frozen_e1_fast_shared_field_transient(
            current[4], ba_state, distribution, inputs, substrate, afterimage,
            backreaction_enabled=True,
        )
        current[1], current[2], current[3], current[4] = (
            ab0.field, ba0.field, ab1.field, ba1.field
        )
        current[5] = advance_fixed_e1_adapter_fast_shared_field_transient(
            current[5], ab1.applied_adapter, distribution, inputs,
            substrate, afterimage,
        )
        current[6] = advance_fixed_e1_adapter_fast_shared_field_transient(
            current[6], ba1.applied_adapter, distribution, inputs,
            substrate, afterimage,
        )
        if (
            ab0.e1_state is not ab_state
            or ab1.e1_state is not ab_state
            or ba0.e1_state is not ba_state
            or ba1.e1_state is not ba_state
        ):
            raise E1ConfirmationPublishedProbeFixtureConsumerError(
                "S1-EC21 changed a frozen state object"
            )
        if runtime_guard is not None:
            runtime_guard()

    vectors = (
        _vector(current[3], "s"),
        _vector(current[4], "s"),
        _vector(current[3], "h"),
        _vector(current[4], "h"),
    )
    ablation = max(
        _linf(_vector(current[0], role), _vector(current[index], role))
        for role in ("s", "h")
        for index in (1, 2)
    )
    fixed = max(
        _linf(_vector(current[3], role), _vector(current[5], role))
        for role in ("s", "h")
    )
    fixed = max(
        fixed,
        *(
            _linf(_vector(current[4], role), _vector(current[6], role))
            for role in ("s", "h")
        ),
    )
    frozen_change = 0.0 if (
        before_ab == _digest(_state_payload(ab_state))
        and before_ba == _digest(_state_payload(ba_state))
    ) else 1.0
    payload = {
        "refinement_id": refinement.refinement_id,
        "field_digests": tuple(
            (role, field.snapshot().digest())
            for role, field in zip(S1_EC20_PROBE_ARMS, current, strict=True)
        ),
        "ab_active_s": vectors[0],
        "ba_active_s": vectors[1],
        "ab_active_h": vectors[2],
        "ba_active_h": vectors[3],
        "active_s_linf": _linf(vectors[0], vectors[1]),
        "active_h_linf": _linf(vectors[2], vectors[3]),
        "probe_ablation_residual": ablation,
        "fixed_adapter_residual": fixed,
        "frozen_state_change": frozen_change,
        "initial_fields_identical_and_separate": True,
        "supports_assigned_once": supports_once,
    }
    return E1PublishedProbeFixtureRefinementResult(
        **payload,
        result_digest=_digest(payload),
    )


def _refinement_residual(first, second) -> float:
    return max(
        _linf(getattr(first, role), getattr(second, role))
        for role in (
            "ab_active_s",
            "ba_active_s",
            "ab_active_h",
            "ba_active_h",
        )
    )


def run_published_probe_fixture_consumer(
    audit: E1PublishedProbeHandoffAudit,
    bundle: E1PreparedExecutionBundle,
    fixture_matrix: E1SmallRefinementMatrixResult,
    fixture_probe_sequences,
    fixture_probe_plans,
) -> E1PublishedProbeFixtureMatrixResult:
    """Consume synthetic states only; never load the persistent S1-EC19 report."""

    if not isinstance(audit, E1PublishedProbeHandoffAudit):
        raise E1ConfirmationPublishedProbeFixtureConsumerError(
            "S1-EC21 requires one S1-EC20 audit"
        )
    if not isinstance(bundle, E1PreparedExecutionBundle):
        raise E1ConfirmationPublishedProbeFixtureConsumerError(
            "S1-EC21 requires one prepared bundle"
        )
    if not isinstance(fixture_matrix, E1SmallRefinementMatrixResult):
        raise E1ConfirmationPublishedProbeFixtureConsumerError(
            "S1-EC21 requires one synthetic fixture matrix"
        )
    audit.__post_init__()
    bundle.__post_init__()
    fixture_matrix.__post_init__()
    values = _typed_values_from_bundle(bundle)
    fixture_sequences = tuple(fixture_probe_sequences)
    if (
        audit.input_bundle_digest != bundle.bundle_digest
        or audit.probe_source_digest != _probe_digest(values.probe_sequences)
        or audit.probe_plan_set_digest != values.probe_plans.digest()
        or tuple(item.refinement_id for item in fixture_matrix.refinements)
        != S1_EC20_REFINEMENTS
        or not fixture_sequences
        or tuple(item.modality_id for item in fixture_sequences)
        != tuple(item.modality_id for item in values.probe_sequences)
        or tuple(item.geometry_id for item in fixture_sequences)
        != tuple(item.geometry_id for item in values.probe_sequences)
        or tuple(item.refinement_id for item in fixture_probe_plans.plans)
        != S1_EC20_REFINEMENTS
        or fixture_probe_plans.research_descriptor_digest
        != values.corridor.digest()
        or _probe_digest(fixture_sequences) == audit.probe_source_digest
    ):
        raise E1ConfirmationPublishedProbeFixtureConsumerError(
            "S1-EC21 audit, bundle, and fixture do not align"
        )
    before_fixture_digest = fixture_matrix.result_digest
    results = tuple(
        _run_refinement_fixture(refinement, plan, values.initial_field)
        for refinement, plan in zip(
            fixture_matrix.refinements,
            fixture_probe_plans.plans,
            strict=True,
        )
    )
    if fixture_matrix.result_digest != before_fixture_digest:
        raise E1ConfirmationPublishedProbeFixtureConsumerError(
            "S1-EC21 changed the fixture matrix"
        )
    r2_r4 = _refinement_residual(results[0], results[1])
    r4_r8 = _refinement_residual(results[1], results[2])
    payload = {
        "consumer_id": S1_EC21_CONSUMER_ID,
        "audit_digest": audit.audit_digest,
        "input_bundle_digest": bundle.bundle_digest,
        "fixture_matrix_digest": fixture_matrix.result_digest,
        "probe_source_digest": audit.probe_source_digest,
        "probe_plan_set_digest": audit.probe_plan_set_digest,
        "fixture_probe_source_digest": _probe_digest(fixture_sequences),
        "fixture_probe_plan_set_digest": fixture_probe_plans.digest(),
        "r2_r4_probe_residual": r2_r4,
        "r4_r8_probe_residual": r4_r8,
        "convergence_nonincreasing": r4_r8 <= r2_r4,
        "all_registered_controls_passed": all(
            item.probe_ablation_residual == 0.0
            and item.fixed_adapter_residual == 0.0
            and item.frozen_state_change == 0.0
            and item.initial_fields_identical_and_separate
            and item.supports_assigned_once
            for item in results
        ),
        "fixture_payload_only": True,
        "persistent_states_consumed": False,
        "registered_probe_consumed": False,
        "probe_execution_permitted": False,
        "result_decision_permitted": False,
        "claims_permitted": False,
    }
    digest_payload = dict(payload)
    digest_payload["refinement_result_digests"] = tuple(
        item.result_digest for item in results
    )
    return E1PublishedProbeFixtureMatrixResult(
        **payload,
        refinements=results,
        result_digest=_digest(digest_payload),
    )
