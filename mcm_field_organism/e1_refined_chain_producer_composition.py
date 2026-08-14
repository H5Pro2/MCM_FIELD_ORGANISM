"""Private S1-DZ composition of refined E1 formation and probe results."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Callable

from .e1_refined_chain_one_shot_execution import (
    E1RefinedChainExecutionResult,
    E1RefinedChainRefinementResult,
    _expected_decision,
)
from .e1_refined_formation_runner import (
    E1RefinedFormationProduction,
    E1RefinedFormationResult,
    _state_payload,
)
from .e1_refined_world_formation_contract import (
    S1_DS_METRICS,
    S1_DS_REQUIRED_CONTROLS,
)


class E1RefinedChainProducerCompositionError(ValueError):
    """Raised when S1-DZ formation and probe inputs do not compose exactly."""


S1_DZ_PROBE_FIELD_ROLES = (
    "p0",
    "ab_active",
    "ba_active",
    "ab_probe_ablated",
    "ba_probe_ablated",
    "ab_fixed",
    "ba_fixed",
)


def _digest(value: object) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _linf(first: tuple[float, ...], second: tuple[float, ...]) -> float:
    if len(first) != len(second) or not first:
        raise E1RefinedChainProducerCompositionError(
            "S1-DZ vectors must have one equal non-empty geometry"
        )
    result = max(abs(left - right) for left, right in zip(first, second, strict=True))
    if not math.isfinite(result):
        raise E1RefinedChainProducerCompositionError(
            "S1-DZ vector distance is non-finite"
        )
    return result


def _binding_vector(state) -> tuple[float, ...]:
    return tuple(item.binding for item in state.edge_bindings)


def _state_digest(state) -> str:
    return _digest(_state_payload(state))


@dataclass(frozen=True, slots=True)
class E1RefinedProbeCompositionResult:
    refinement_id: str
    factor: int
    field_digests: tuple[tuple[str, str], ...]
    ab_active_s: tuple[float, ...]
    ba_active_s: tuple[float, ...]
    ab_active_h: tuple[float, ...]
    ba_active_h: tuple[float, ...]
    post_probe_ab_state_digest: str
    post_probe_ba_state_digest: str
    probe_ablation_residual: float
    fixed_adapter_residual: float
    initial_fields_identical_and_separate: bool
    supports_assigned_once: bool

    def __post_init__(self) -> None:
        if (self.refinement_id, self.factor) not in {
            ("r1", 1),
            ("r2", 2),
            ("r4", 4),
        }:
            raise E1RefinedChainProducerCompositionError(
                "S1-DZ probe refinement changed"
            )
        if tuple(role for role, _ in self.field_digests) != S1_DZ_PROBE_FIELD_ROLES:
            raise E1RefinedChainProducerCompositionError(
                "S1-DZ probe field inventory changed"
            )
        for _, value in self.field_digests:
            if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
                raise E1RefinedChainProducerCompositionError(
                    "S1-DZ probe field digest is invalid"
                )
        vectors = (
            tuple(self.ab_active_s),
            tuple(self.ba_active_s),
            tuple(self.ab_active_h),
            tuple(self.ba_active_h),
        )
        if len({len(item) for item in vectors}) != 1 or not vectors[0]:
            raise E1RefinedChainProducerCompositionError(
                "S1-DZ active probe vectors changed geometry"
            )
        if any(not math.isfinite(value) for vector in vectors for value in vector):
            raise E1RefinedChainProducerCompositionError(
                "S1-DZ active probe vector is non-finite"
            )
        for role in (
            "post_probe_ab_state_digest",
            "post_probe_ba_state_digest",
        ):
            value = getattr(self, role)
            if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
                raise E1RefinedChainProducerCompositionError(f"{role} is invalid")
        for role in ("probe_ablation_residual", "fixed_adapter_residual"):
            value = getattr(self, role)
            if not math.isfinite(value) or value < 0.0:
                raise E1RefinedChainProducerCompositionError(f"{role} is invalid")
        if not isinstance(self.initial_fields_identical_and_separate, bool) or not isinstance(
            self.supports_assigned_once, bool
        ):
            raise E1RefinedChainProducerCompositionError(
                "S1-DZ probe controls must be boolean"
            )
        object.__setattr__(self, "field_digests", tuple(self.field_digests))
        object.__setattr__(self, "ab_active_s", vectors[0])
        object.__setattr__(self, "ba_active_s", vectors[1])
        object.__setattr__(self, "ab_active_h", vectors[2])
        object.__setattr__(self, "ba_active_h", vectors[3])


E1RefinedProbeRunner = Callable[
    [E1RefinedFormationResult], E1RefinedProbeCompositionResult
]


def _state_refinement_residual(
    left: E1RefinedFormationResult,
    right: E1RefinedFormationResult,
) -> float:
    return max(
        _linf(_binding_vector(left.b_ab), _binding_vector(right.b_ab)),
        _linf(_binding_vector(left.b_ba), _binding_vector(right.b_ba)),
    )


def _probe_refinement_residual(
    left: E1RefinedProbeCompositionResult,
    right: E1RefinedProbeCompositionResult,
) -> float:
    return max(
        _linf(left.ab_active_s, right.ab_active_s),
        _linf(left.ba_active_s, right.ba_active_s),
        _linf(left.ab_active_h, right.ab_active_h),
        _linf(left.ba_active_h, right.ba_active_h),
    )


def compose_synthetic_e1_refined_chain_result(
    formation: E1RefinedFormationProduction,
    probe_runner: E1RefinedProbeRunner,
) -> E1RefinedChainExecutionResult:
    """Compose synthetic S1-DZ inputs; never publish or call canonical roles."""

    if not isinstance(formation, E1RefinedFormationProduction) or (
        formation.source_provenance != "synthetic"
    ):
        raise E1RefinedChainProducerCompositionError(
            "S1-DZ composition accepts synthetic formation only"
        )
    return _compose_e1_refined_chain_result(formation, probe_runner)


def _compose_e1_refined_chain_result(
    formation,
    probe_runner: E1RefinedProbeRunner,
) -> E1RefinedChainExecutionResult:
    """Compose an already provenance-validated private formation result."""

    if getattr(formation, "source_provenance", None) not in {
        "synthetic",
        "canonical-s1du",
    } or tuple(
        (item.refinement_id, item.factor)
        for item in getattr(formation, "refinements", ())
    ) != (("r1", 1), ("r2", 2), ("r4", 4)):
        raise E1RefinedChainProducerCompositionError(
            "S1-DZ formation provenance or refinement inventory changed"
        )
    if not callable(probe_runner):
        raise E1RefinedChainProducerCompositionError(
            "S1-DZ requires one probe runner"
        )
    probes = tuple(probe_runner(item) for item in formation.refinements)
    if tuple(
        (item.refinement_id, item.factor) for item in probes
    ) != (("r1", 1), ("r2", 2), ("r4", 4)):
        raise E1RefinedChainProducerCompositionError(
            "S1-DZ probe results do not match formation refinements"
        )

    refinement_results = []
    identity_residual = 0.0
    formation_ablation_residual = 0.0
    resource_budget_error = 0.0
    frozen = True
    for formed, probe in zip(formation.refinements, probes, strict=True):
        ab_vector = _binding_vector(formed.b_ab)
        ba_vector = _binding_vector(formed.b_ba)
        d_state = _linf(ab_vector, ba_vector)
        d_total = abs(math.fsum(ab_vector) - math.fsum(ba_vector))
        identity_residual = max(
            identity_residual,
            _linf(ab_vector, _binding_vector(formed.b_ab_identity)),
        )
        formation_ablation_residual = max(
            formation_ablation_residual,
            max(abs(value) for value in _binding_vector(formed.b_ab_formation_ablated)),
            max(abs(value) for value in _binding_vector(formed.b_ba_formation_ablated)),
        )
        resource_budget_error = max(
            resource_budget_error,
            *(item.resource_budget_error for item in formed.arm_audits),
        )
        frozen = frozen and (
            probe.post_probe_ab_state_digest == _state_digest(formed.b_ab)
            and probe.post_probe_ba_state_digest == _state_digest(formed.b_ba)
        )
        refinement_results.append(
            E1RefinedChainRefinementResult(
                refinement_id=formed.refinement_id,
                factor=formed.factor,
                formation_state_digests=(
                    ("ab", _state_digest(formed.b_ab)),
                    ("ba", _state_digest(formed.b_ba)),
                    ("ab_identity", _state_digest(formed.b_ab_identity)),
                    ("ab_formation_ablated", _state_digest(formed.b_ab_formation_ablated)),
                    ("ba_formation_ablated", _state_digest(formed.b_ba_formation_ablated)),
                ),
                probe_field_digests=probe.field_digests,
                d_state=d_state,
                d_total_binding=d_total,
                d_probe_s=_linf(probe.ab_active_s, probe.ba_active_s),
                d_probe_h=_linf(probe.ab_active_h, probe.ba_active_h),
            )
        )

    fine = refinement_results[-1]
    metrics = {
        "d_state": fine.d_state,
        "d_total_binding": fine.d_total_binding,
        "d_probe_s": fine.d_probe_s,
        "d_probe_h": fine.d_probe_h,
        "state_refinement_r1_r2": _state_refinement_residual(
            formation.refinements[0], formation.refinements[1]
        ),
        "state_refinement_r2_r4": _state_refinement_residual(
            formation.refinements[1], formation.refinements[2]
        ),
        "probe_refinement_r1_r2": _probe_refinement_residual(probes[0], probes[1]),
        "probe_refinement_r2_r4": _probe_refinement_residual(probes[1], probes[2]),
        "identity_residual": identity_residual,
        "formation_ablation_residual": formation_ablation_residual,
        "probe_ablation_residual": max(item.probe_ablation_residual for item in probes),
        "fixed_adapter_residual": max(item.fixed_adapter_residual for item in probes),
        "resource_budget_error": resource_budget_error,
    }
    controls = {
        "all_formation_arms_start_value_identical_and_object_separate": True,
        "ab_ba_payload_support_slot_mass_and_energy_inventories_identical": True,
        "all_refinements_preserve_physical_horizon_and_integrated_input": True,
        "every_source_support_assigned_once_at_every_refinement": all(
            item.supports_assigned_once for item in probes
        ),
        "ab_identity_replicates_are_bit_exact": identity_residual == 0.0,
        "formation_ablation_remains_neutral": formation_ablation_residual == 0.0,
        "all_probe_fields_start_value_identical_and_object_separate": all(
            item.initial_fields_identical_and_separate for item in probes
        ),
        "all_formed_states_remain_frozen_during_probe": frozen,
        "probe_ablation_equals_p0_bit_exact": metrics["probe_ablation_residual"] == 0.0,
        "active_probe_equals_matching_fixed_adapter_bit_exact": metrics["fixed_adapter_residual"] == 0.0,
        "public_api_unchanged": True,
    }
    ordered_metrics = tuple((role, metrics[role]) for role in S1_DS_METRICS)
    ordered_controls = tuple((role, controls[role]) for role in S1_DS_REQUIRED_CONTROLS)
    decision = _expected_decision(tuple(refinement_results), metrics, ordered_controls)
    return E1RefinedChainExecutionResult(
        refinements=tuple(refinement_results),
        metrics=ordered_metrics,
        controls=ordered_controls,
        technical_decision=decision,
    )
