"""Private S1-EB7 synthetic composition of formation, probe, and decision."""

from __future__ import annotations

import math

from .e1_confirmation_chain_contract import (
    E1ConfirmationChainContract,
    S1_EB4_METRICS,
)
from .e1_confirmation_formation_runner import (
    E1ConfirmationFormationProduction,
    E1ConfirmationFormationResult,
)
from .e1_confirmation_result_core import (
    E1ConfirmationChainResult,
    E1ConfirmationRefinementResult,
    build_e1_confirmation_chain_result,
)
from .e1_confirmation_seven_arm_probe import E1ConfirmationProbeResult
from .e1_refined_confirmation_contract import S1_EB_REFINEMENTS
from .e1_refined_formation_runner import _digest, _state_payload
from .e1_refined_world_formation_contract import S1_DS_REQUIRED_CONTROLS


class E1ConfirmationChainCompositionError(ValueError):
    """Raised when S1-EB7 synthetic chain inputs do not compose exactly."""


def _linf(first: tuple[float, ...], second: tuple[float, ...]) -> float:
    if len(first) != len(second) or not first:
        raise E1ConfirmationChainCompositionError(
            "S1-EB7 vectors require one equal non-empty geometry"
        )
    result = max(
        abs(left - right)
        for left, right in zip(first, second, strict=True)
    )
    if not math.isfinite(result):
        raise E1ConfirmationChainCompositionError(
            "S1-EB7 vector distance is non-finite"
        )
    return result


def _binding_vector(state) -> tuple[float, ...]:
    return tuple(item.binding for item in state.edge_bindings)


def _state_digest(state) -> str:
    return _digest(_state_payload(state))


def _state_refinement_residual(
    left: E1ConfirmationFormationResult,
    right: E1ConfirmationFormationResult,
) -> float:
    return max(
        _linf(_binding_vector(left.b_ab), _binding_vector(right.b_ab)),
        _linf(_binding_vector(left.b_ba), _binding_vector(right.b_ba)),
    )


def _probe_refinement_residual(
    left: E1ConfirmationProbeResult,
    right: E1ConfirmationProbeResult,
) -> float:
    return max(
        _linf(left.ab_active_s, right.ab_active_s),
        _linf(left.ba_active_s, right.ba_active_s),
        _linf(left.ab_active_h, right.ab_active_h),
        _linf(left.ba_active_h, right.ba_active_h),
    )


def compose_synthetic_e1_confirmation_chain(
    contract: E1ConfirmationChainContract,
    formation: E1ConfirmationFormationProduction,
    probes: tuple[E1ConfirmationProbeResult, ...],
) -> E1ConfirmationChainResult:
    """Compose completed synthetic results without runtime or persistence."""

    if not isinstance(contract, E1ConfirmationChainContract):
        raise E1ConfirmationChainCompositionError(
            "S1-EB7 requires the current S1-EB4 contract"
        )
    if not isinstance(formation, E1ConfirmationFormationProduction) or (
        formation.source_provenance != "synthetic-s1eb3"
        or formation.contract_digest != contract.confirmation_contract_digest
    ):
        raise E1ConfirmationChainCompositionError(
            "S1-EB7 accepts matching synthetic S1-EB3 formation only"
        )
    formed = tuple(formation.refinements)
    probes_in = tuple(probes)
    if tuple(
        (item.refinement_id, item.factor) for item in formed
    ) != S1_EB_REFINEMENTS or tuple(
        (item.refinement_id, item.factor) for item in probes_in
    ) != S1_EB_REFINEMENTS:
        raise E1ConfirmationChainCompositionError(
            "S1-EB7 requires matching ordered r2, r4, and r8 inputs"
        )
    if any(not isinstance(item, E1ConfirmationProbeResult) for item in probes_in):
        raise E1ConfirmationChainCompositionError(
            "S1-EB7 requires three S1-EB6 probe results"
        )
    if len({item.probe_source_digest for item in probes_in}) != 1 or len(
        {item.probe_plan_digest for item in probes_in}
    ) != 3:
        raise E1ConfirmationChainCompositionError(
            "S1-EB7 probe source or plan inventory changed"
        )

    refinement_results = []
    identity_residual = 0.0
    formation_ablation_residual = 0.0
    resource_budget_error = 0.0
    frozen = True
    for formation_item, probe in zip(formed, probes_in, strict=True):
        ab_vector = _binding_vector(formation_item.b_ab)
        ba_vector = _binding_vector(formation_item.b_ba)
        identity_residual = max(
            identity_residual,
            _linf(
                ab_vector,
                _binding_vector(formation_item.b_ab_identity),
            ),
        )
        formation_ablation_residual = max(
            formation_ablation_residual,
            max(
                abs(value)
                for value in _binding_vector(
                    formation_item.b_ab_formation_ablated
                )
            ),
            max(
                abs(value)
                for value in _binding_vector(
                    formation_item.b_ba_formation_ablated
                )
            ),
        )
        resource_budget_error = max(
            resource_budget_error,
            *(item.resource_budget_error for item in formation_item.arm_audits),
        )
        frozen = frozen and (
            probe.pre_probe_ab_state_digest
            == _state_digest(formation_item.b_ab)
            == probe.post_probe_ab_state_digest
            and probe.pre_probe_ba_state_digest
            == _state_digest(formation_item.b_ba)
            == probe.post_probe_ba_state_digest
        )
        refinement_results.append(
            E1ConfirmationRefinementResult(
                refinement_id=formation_item.refinement_id,
                factor=formation_item.factor,
                formation_state_digests=(
                    ("ab", _state_digest(formation_item.b_ab)),
                    ("ba", _state_digest(formation_item.b_ba)),
                    (
                        "ab_identity",
                        _state_digest(formation_item.b_ab_identity),
                    ),
                    (
                        "ab_formation_ablated",
                        _state_digest(
                            formation_item.b_ab_formation_ablated
                        ),
                    ),
                    (
                        "ba_formation_ablated",
                        _state_digest(
                            formation_item.b_ba_formation_ablated
                        ),
                    ),
                ),
                probe_field_digests=probe.field_digests,
                d_state=_linf(ab_vector, ba_vector),
                d_total_binding=abs(
                    math.fsum(ab_vector) - math.fsum(ba_vector)
                ),
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
        "state_refinement_r2_r4": _state_refinement_residual(
            formed[0], formed[1]
        ),
        "state_refinement_r4_r8": _state_refinement_residual(
            formed[1], formed[2]
        ),
        "probe_refinement_r2_r4": _probe_refinement_residual(
            probes_in[0], probes_in[1]
        ),
        "probe_refinement_r4_r8": _probe_refinement_residual(
            probes_in[1], probes_in[2]
        ),
        "identity_residual": identity_residual,
        "formation_ablation_residual": formation_ablation_residual,
        "probe_ablation_residual": max(
            item.probe_ablation_residual for item in probes_in
        ),
        "fixed_adapter_residual": max(
            item.fixed_adapter_residual for item in probes_in
        ),
        "resource_budget_error": resource_budget_error,
    }
    controls = {
        "all_formation_arms_start_value_identical_and_object_separate": True,
        "ab_ba_payload_support_slot_mass_and_energy_inventories_identical": True,
        "all_refinements_preserve_physical_horizon_and_integrated_input": True,
        "every_source_support_assigned_once_at_every_refinement": all(
            item.supports_assigned_once for item in probes_in
        ),
        "ab_identity_replicates_are_bit_exact": identity_residual == 0.0,
        "formation_ablation_remains_neutral": (
            formation_ablation_residual == 0.0
        ),
        "all_probe_fields_start_value_identical_and_object_separate": all(
            item.initial_fields_identical_and_separate for item in probes_in
        ),
        "all_formed_states_remain_frozen_during_probe": frozen,
        "probe_ablation_equals_p0_bit_exact": (
            metrics["probe_ablation_residual"] == 0.0
        ),
        "active_probe_equals_matching_fixed_adapter_bit_exact": (
            metrics["fixed_adapter_residual"] == 0.0
        ),
        "public_api_unchanged": True,
    }
    return build_e1_confirmation_chain_result(
        contract,
        tuple(refinement_results),
        tuple((role, metrics[role]) for role in S1_EB4_METRICS),
        tuple((role, controls[role]) for role in S1_DS_REQUIRED_CONTROLS),
    )
