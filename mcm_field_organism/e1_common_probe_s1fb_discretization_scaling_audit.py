"""S1-FB static localization of r2/r4/r8 discretization sensitivity."""

from __future__ import annotations

import ast
from dataclasses import asdict, dataclass
import inspect

from .e1_common_probe_ec87_r2_ec46_complement_contract import S1_EC87_R2_SCALARS
from .e1_common_probe_ec88_r4_r8_budget_inventory import S1_EC88_EXPECTED_BUDGETS
from .e1_common_probe_ec97_ec46_data_sufficiency_audit import (
    S1_EC97_R4_R8_ACTIVE_SCALARS,
)
from .e1_confirmation_refinement_planner import E1ConfirmationRefinementPlan
from .e1_frozen_transient_probe import _advance_with_fixed_adapter
from .e1_local_edge_plasticity import advance_e1_local_edge_plasticity
from .e1_refined_formation_runner import _digest
from .e1_transient_coupled_field import _advance_e1_over_observed_boundaries
from .neutral_local_field_substrate import (
    _advance_projected_activation_afterimage,
)


class E1CommonProbeS1FBDiscretizationScalingAuditError(ValueError):
    """Raised when S1-FB overstates or changes the static localization."""


S1_FB_AUDIT_ID = "e1.common-probe-discretization-scaling-audit.s1fb.v1"
S1_FB_REFINEMENT_BUDGETS = (
    ("r2", 2, 402, 200),
    ("r4", 4, 804, 400),
    ("r8", 8, 1608, 800),
)


def _called_names(source: str) -> frozenset[str]:
    names: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            names.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            names.add(node.func.attr)
    return frozenset(names)


@dataclass(frozen=True, slots=True)
class E1CommonProbeS1FBObservedScalarScaling:
    component: str
    r2_norm: float
    r4_norm: float
    r8_norm: float
    r2_to_r4_decrease: float
    r4_to_r8_decrease: float
    successive_decrease_ratio: float
    r4_relative_change: float
    r8_relative_change: float
    first_order_like_but_not_proven: bool

    def __post_init__(self) -> None:
        if (
            self.component not in {"activation", "afterimage"}
            or not (self.r2_norm > self.r4_norm > self.r8_norm > 0.0)
            or self.r2_to_r4_decrease != self.r2_norm - self.r4_norm
            or self.r4_to_r8_decrease != self.r4_norm - self.r8_norm
            or self.successive_decrease_ratio
            != self.r4_to_r8_decrease / self.r2_to_r4_decrease
            or self.r4_relative_change != self.r2_to_r4_decrease / self.r4_norm
            or self.r8_relative_change != self.r4_to_r8_decrease / self.r8_norm
            or self.first_order_like_but_not_proven is not True
            or not 0.4 < self.successive_decrease_ratio < 0.55
        ):
            raise E1CommonProbeS1FBDiscretizationScalingAuditError(
                "S1-FB scalar scaling changed or was overstated"
            )


def _serializable_payload(values: dict[str, object]) -> dict[str, object]:
    payload = dict(values)
    payload["observed_scaling"] = tuple(
        asdict(item) for item in payload["observed_scaling"]  # type: ignore[union-attr]
    )
    return payload


@dataclass(frozen=True, slots=True)
class E1CommonProbeS1FBDiscretizationScalingAudit:
    audit_id: str
    refinement_budgets: tuple[tuple[str, int, int, int], ...]
    same_physical_horizon_across_refinements: bool
    same_source_supports_across_refinements: bool
    same_completion_ticks_across_refinements: bool
    step_width_scales_inverse_to_factor: bool
    field_rates_are_per_second: bool
    e1_rates_are_per_second: bool
    fixed_per_step_accumulation_present: bool
    neutral_field_piecewise_exact: bool
    frozen_probe_piecewise_exact: bool
    e1_formation_uses_endpoint_half_steps: bool
    first_structurally_discretization_sensitive_stage: str
    observed_scaling: tuple[E1CommonProbeS1FBObservedScalarScaling, ...]
    observed_scaling_proves_convergence_order: bool
    observed_scaling_proves_instability: bool
    missing_dt_scaling_defect_found: bool
    ec46_posthoc_change_permitted: bool
    field_execution_permitted: bool
    rerun_permitted: bool
    memory_claim_permitted: bool
    decision: str
    reason: str
    audit_digest: str

    def __post_init__(self) -> None:
        payload = _serializable_payload({
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "audit_digest"
        })
        if (
            self.audit_id != S1_FB_AUDIT_ID
            or self.refinement_budgets != S1_FB_REFINEMENT_BUDGETS
            or any(
                value is not True
                for value in (
                    self.same_physical_horizon_across_refinements,
                    self.same_source_supports_across_refinements,
                    self.same_completion_ticks_across_refinements,
                    self.step_width_scales_inverse_to_factor,
                    self.field_rates_are_per_second,
                    self.e1_rates_are_per_second,
                    self.neutral_field_piecewise_exact,
                    self.frozen_probe_piecewise_exact,
                    self.e1_formation_uses_endpoint_half_steps,
                )
            )
            or self.fixed_per_step_accumulation_present is not False
            or self.first_structurally_discretization_sensitive_stage
            != "nonlinear-e1-formation-endpoint-splitting"
            or tuple(item.component for item in self.observed_scaling)
            != ("activation", "afterimage")
            or any(
                value is not False
                for value in (
                    self.observed_scaling_proves_convergence_order,
                    self.observed_scaling_proves_instability,
                    self.missing_dt_scaling_defect_found,
                    self.ec46_posthoc_change_permitted,
                    self.field_execution_permitted,
                    self.rerun_permitted,
                    self.memory_claim_permitted,
                )
            )
            or self.decision
            != "TIME_SCALING_SOUND_E1_FORMATION_IS_FIRST_NONEXACT_STAGE"
            or not self.reason
            or self.audit_digest != _digest(payload)
        ):
            raise E1CommonProbeS1FBDiscretizationScalingAuditError(
                "S1-FB audit changed, invented a defect, or opened execution"
            )
        for item in self.observed_scaling:
            item.__post_init__()


def _scaling(
    component: str,
    r2_norm: float,
    r4_norm: float,
    r8_norm: float,
) -> E1CommonProbeS1FBObservedScalarScaling:
    first = r2_norm - r4_norm
    second = r4_norm - r8_norm
    return E1CommonProbeS1FBObservedScalarScaling(
        component=component,
        r2_norm=r2_norm,
        r4_norm=r4_norm,
        r8_norm=r8_norm,
        r2_to_r4_decrease=first,
        r4_to_r8_decrease=second,
        successive_decrease_ratio=second / first,
        r4_relative_change=first / r4_norm,
        r8_relative_change=second / r8_norm,
        first_order_like_but_not_proven=True,
    )


def audit_e1_common_probe_s1fb_discretization_scaling(
) -> E1CommonProbeS1FBDiscretizationScalingAudit:
    """Inspect scaling contracts and retained norms without running a field."""

    plan_source = inspect.getsource(E1ConfirmationRefinementPlan.__post_init__)
    field_source = inspect.getsource(_advance_projected_activation_afterimage)
    probe_source = inspect.getsource(_advance_with_fixed_adapter)
    e1_source = inspect.getsource(advance_e1_local_edge_plasticity)
    coupling_source = inspect.getsource(_advance_e1_over_observed_boundaries)
    r2 = next(item for item in S1_EC87_R2_SCALARS if item[0] == "e1-active-order")
    r4 = next(item for item in S1_EC97_R4_R8_ACTIVE_SCALARS if item[0] == "r4")
    r8 = next(item for item in S1_EC97_R4_R8_ACTIVE_SCALARS if item[0] == "r8")
    observed = (
        _scaling("activation", r2[1], r4[1], r8[1]),
        _scaling("afterimage", r2[2], r4[2], r8[2]),
    )
    expected_r4_r8 = tuple(
        (item[0], item[1], item[2]) for item in S1_EC88_EXPECTED_BUDGETS
    )
    if expected_r4_r8 != (("r4", 804, 400), ("r8", 1608, 800)):
        raise E1CommonProbeS1FBDiscretizationScalingAuditError(
            "S1-FB source budgets changed"
        )
    values = {
        "audit_id": S1_FB_AUDIT_ID,
        "refinement_budgets": S1_FB_REFINEMENT_BUDGETS,
        "same_physical_horizon_across_refinements": (
            "horizon_end_tick" in plan_source and "first.horizon_end_tick" not in plan_source
        ),
        "same_source_supports_across_refinements": (
            "assigned_event_count" in plan_source
            and "source_event_count" in plan_source
        ),
        "same_completion_ticks_across_refinements": "completion_ticks" in plan_source,
        "step_width_scales_inverse_to_factor": "base_interval_count * self.factor" in plan_source,
        "field_rates_are_per_second": (
            "elapsed_seconds" in field_source and "np.exp" in field_source
        ),
        "e1_rates_are_per_second": (
            "elapsed_seconds" in e1_source
            and "binding_rate_per_second" in e1_source
            and "release_rate_per_second" in e1_source
        ),
        "fixed_per_step_accumulation_present": False,
        "neutral_field_piecewise_exact": (
            "activation_exponent" in field_source
            and "afterimage_exponent" in field_source
        ),
        "frozen_probe_piecewise_exact": (
            "_advance_projected_activation_afterimage" in probe_source
            and "_apply_projected_point_contacts" in probe_source
        ),
        "e1_formation_uses_endpoint_half_steps": (
            coupling_source.count("elapsed / 2.0") == 2
            and "start_layer" in coupling_source
            and "end_layer" in coupling_source
        ),
        "first_structurally_discretization_sensitive_stage": (
            "nonlinear-e1-formation-endpoint-splitting"
        ),
        "observed_scaling": observed,
        "observed_scaling_proves_convergence_order": False,
        "observed_scaling_proves_instability": False,
        "missing_dt_scaling_defect_found": False,
        "ec46_posthoc_change_permitted": False,
        "field_execution_permitted": False,
        "rerun_permitted": False,
        "memory_claim_permitted": False,
        "decision": "TIME_SCALING_SOUND_E1_FORMATION_IS_FIRST_NONEXACT_STAGE",
        "reason": (
            "horizons-supports-and-completion-times-are-fixed;field-and-probe-use-"
            "elapsed-time-exponentials;e1-rates-use-seconds;nonlinear-e1-formation-"
            "is-split-over-start-and-end-layers;scalar-decrements-nearly-halve-but-"
            "three-levels-do-not-prove-order"
        ),
    }
    forbidden_calls = {
        "run_e1_common_probe_n2_r2_real_mode_coordinator",
        "run_e1_common_probe_ec96_authorized_r4_r8_once",
        "run_prepared_real_formation_arm_in_memory",
        "run_e1_common_probe_real_probe_wrapper",
        "decide_common_probe_evidence",
        "write_text",
        "write_bytes",
        "open",
    }
    if not _called_names(inspect.getsource(
        audit_e1_common_probe_s1fb_discretization_scaling
    )).isdisjoint(forbidden_calls):
        raise E1CommonProbeS1FBDiscretizationScalingAuditError(
            "S1-FB audit invoked an execution or writer path"
        )
    return E1CommonProbeS1FBDiscretizationScalingAudit(
        **values,
        audit_digest=_digest(_serializable_payload(values)),
    )
