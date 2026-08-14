"""S1-EC47 zero-field synthetic integration of the EC45/EC46 common probe."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import math

from .e1_common_probe_acceptance_contract import (
    E1CommonProbeAcceptanceContract,
    decide_common_probe_evidence,
)
from .e1_common_probe_identifiability_contract import S1_EC45_PROBE_ROLES
from .e1_refined_formation_runner import _digest


class E1CommonProbeSyntheticRunnerFixtureError(ValueError):
    """Raised when EC47 crosses its synthetic zero-field boundary."""


S1_EC47_RUNNER_ID = "e1.common-probe-synthetic-runner.s1ec47.v1"
S1_EC47_EC46_CONTRACT_DIGEST = (
    "672239cddf2a1e8a8856a5bd2570ebaf0a9bdda5f52fb45aa0306e2570dd144b"
)
S1_EC47_REFINEMENTS = ("r2", "r4", "r8")


def _finite_vector(values: tuple[float, ...], role: str) -> tuple[float, ...]:
    result = tuple(float(value) for value in values)
    if not result or any(not math.isfinite(value) for value in result):
        raise E1CommonProbeSyntheticRunnerFixtureError(
            f"S1-EC47 {role} must be one finite nonempty vector"
        )
    return result


def _linf(values: tuple[float, ...]) -> float:
    return max(abs(value) for value in values)


def _difference(left: tuple[float, ...], right: tuple[float, ...]) -> tuple[float, ...]:
    if len(left) != len(right):
        raise E1CommonProbeSyntheticRunnerFixtureError(
            "S1-EC47 vectors have different geometries"
        )
    return tuple(a - b for a, b in zip(left, right, strict=True))


@dataclass(frozen=True, slots=True)
class E1SyntheticCommonProbeSample:
    role_id: str
    refinement_id: str
    neuron_ids: tuple[str, ...]
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    field_steps_executed: int
    synthetic: bool
    sample_digest: str

    def __post_init__(self) -> None:
        activation = _finite_vector(self.activation, "activation")
        afterimage = _finite_vector(self.afterimage, "afterimage")
        if (
            self.role_id not in S1_EC45_PROBE_ROLES
            or self.refinement_id not in S1_EC47_REFINEMENTS
            or not self.neuron_ids
            or len(set(self.neuron_ids)) != len(self.neuron_ids)
            or len(activation) != len(self.neuron_ids)
            or len(afterimage) != len(self.neuron_ids)
            or self.field_steps_executed != 0
            or self.synthetic is not True
        ):
            raise E1CommonProbeSyntheticRunnerFixtureError(
                "S1-EC47 synthetic sample changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "sample_digest"
        }
        if self.sample_digest != _digest(payload):
            raise E1CommonProbeSyntheticRunnerFixtureError(
                "S1-EC47 sample digest changed"
            )


@dataclass(frozen=True, slots=True)
class E1CommonProbeSyntheticRunnerFixtureResult:
    runner_id: str
    source_contract_digest: str
    sample_digests: tuple[tuple[str, str, str], ...]
    active_s_by_refinement: tuple[float, ...]
    active_h_by_refinement: tuple[float, ...]
    coarse_s: float
    coarse_h: float
    fine_s: float
    fine_h: float
    maximum_p0_reset_s: float
    maximum_p0_reset_h: float
    maximum_feedback_ablation_s: float
    maximum_feedback_ablation_h: float
    maximum_formation_ablation_s: float
    maximum_formation_ablation_h: float
    synthetic_decision: str
    sample_count: int
    all_roles_present_per_refinement: bool
    common_neuron_order_preserved: bool
    field_steps_executed: int
    synthetic_integration_complete: bool
    pilot_execution_performed: bool
    persistence_performed: bool
    research_decision_permitted: bool
    memory_claim_permitted: bool
    result_digest: str

    def __post_init__(self) -> None:
        expected_order = tuple(
            (refinement, role)
            for refinement in S1_EC47_REFINEMENTS
            for role in S1_EC45_PROBE_ROLES
        )
        if (
            self.runner_id != S1_EC47_RUNNER_ID
            or self.source_contract_digest != S1_EC47_EC46_CONTRACT_DIGEST
            or tuple((r, role) for r, role, _ in self.sample_digests)
            != expected_order
            or len(self.active_s_by_refinement) != 3
            or len(self.active_h_by_refinement) != 3
            or self.synthetic_decision
            != "NUMERICALLY_CLEAR_STATE_DEPENDENT_COMMON_PROBE_DIFFERENCE"
            or self.sample_count != 24
            or any(value is not True for value in (
                self.all_roles_present_per_refinement,
                self.common_neuron_order_preserved,
                self.synthetic_integration_complete,
            ))
            or self.field_steps_executed != 0
            or any(value is not False for value in (
                self.pilot_execution_performed,
                self.persistence_performed,
                self.research_decision_permitted,
                self.memory_claim_permitted,
            ))
        ):
            raise E1CommonProbeSyntheticRunnerFixtureError(
                "S1-EC47 result changed or crossed zero-field scope"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "result_digest"
        }
        if self.result_digest != _digest(payload):
            raise E1CommonProbeSyntheticRunnerFixtureError(
                "S1-EC47 result digest changed"
            )


def build_synthetic_common_probe_sample(
    role_id: str,
    refinement_id: str,
) -> E1SyntheticCommonProbeSample:
    """Return one deterministic typed vector without invoking a field."""

    active_levels = {
        "r2": (0.0010015, 0.0020030),
        "r4": (0.0010005, 0.0020010),
        "r8": (0.0010000, 0.0020000),
    }
    if role_id not in S1_EC45_PROBE_ROLES or refinement_id not in S1_EC47_REFINEMENTS:
        raise E1CommonProbeSyntheticRunnerFixtureError(
            "S1-EC47 unknown synthetic role or refinement"
        )
    activation = (0.0, 0.0, 0.0)
    afterimage = (0.0, 0.0, 0.0)
    if role_id == "e1-active-ab":
        activation_level, afterimage_level = active_levels[refinement_id]
        activation = (activation_level, -0.5 * activation_level, 0.0)
        afterimage = (afterimage_level, -0.5 * afterimage_level, 0.0)
    values = {
        "role_id": role_id,
        "refinement_id": refinement_id,
        "neuron_ids": ("n0", "n1", "n2"),
        "activation": activation,
        "afterimage": afterimage,
        "field_steps_executed": 0,
        "synthetic": True,
    }
    return E1SyntheticCommonProbeSample(
        **values,
        sample_digest=_digest(values),
    )


SyntheticCommonProbeKernel = Callable[
    [str, str], E1SyntheticCommonProbeSample
]


def run_e1_common_probe_synthetic_runner_fixture(
    contract: E1CommonProbeAcceptanceContract,
    *,
    sample_kernel: SyntheticCommonProbeKernel = build_synthetic_common_probe_sample,
) -> E1CommonProbeSyntheticRunnerFixtureResult:
    """Integrate all EC45 roles and EC46 metrics with zero field steps."""

    if not isinstance(contract, E1CommonProbeAcceptanceContract):
        raise E1CommonProbeSyntheticRunnerFixtureError(
            "S1-EC47 requires the typed EC46 contract"
        )
    contract.__post_init__()
    if (
        contract.contract_digest != S1_EC47_EC46_CONTRACT_DIGEST
        or contract.common_probe_implementation_permitted is not True
        or contract.field_execution_permitted is not False
        or not callable(sample_kernel)
    ):
        raise E1CommonProbeSyntheticRunnerFixtureError(
            "S1-EC47 upstream binding or kernel changed"
        )
    samples = []
    for refinement in S1_EC47_REFINEMENTS:
        for role in S1_EC45_PROBE_ROLES:
            sample = sample_kernel(role, refinement)
            if not isinstance(sample, E1SyntheticCommonProbeSample):
                raise E1CommonProbeSyntheticRunnerFixtureError(
                    "S1-EC47 kernel returned no typed sample"
                )
            sample.__post_init__()
            if sample.role_id != role or sample.refinement_id != refinement:
                raise E1CommonProbeSyntheticRunnerFixtureError(
                    "S1-EC47 sample identity differs from requested slot"
                )
            samples.append(sample)

    neuron_orders = {item.neuron_ids for item in samples}
    by_key = {(item.refinement_id, item.role_id): item for item in samples}

    def order_vectors(prefix: str, component: str) -> tuple[tuple[float, ...], ...]:
        return tuple(
            _difference(
                getattr(by_key[(refinement, f"{prefix}-ab")], component),
                getattr(by_key[(refinement, f"{prefix}-ba")], component),
            )
            for refinement in S1_EC47_REFINEMENTS
        )

    active_s_vectors = order_vectors("e1-active", "activation")
    active_h_vectors = order_vectors("e1-active", "afterimage")
    controls = {
        (prefix, component): order_vectors(prefix, component)
        for prefix in (
            "p0-reset",
            "e1-probe-feedback-ablated",
            "e1-formation-ablated",
        )
        for component in ("activation", "afterimage")
    }
    active_s = tuple(_linf(item) for item in active_s_vectors)
    active_h = tuple(_linf(item) for item in active_h_vectors)
    coarse_s = _linf(_difference(active_s_vectors[0], active_s_vectors[1]))
    coarse_h = _linf(_difference(active_h_vectors[0], active_h_vectors[1]))
    fine_s = _linf(_difference(active_s_vectors[1], active_s_vectors[2]))
    fine_h = _linf(_difference(active_h_vectors[1], active_h_vectors[2]))

    def control_max(prefix: str, component: str) -> float:
        return max(_linf(item) for item in controls[(prefix, component)])

    decision_inputs = {
        "active_s": active_s[-1],
        "active_h": active_h[-1],
        "coarse_s": coarse_s,
        "coarse_h": coarse_h,
        "fine_s": fine_s,
        "fine_h": fine_h,
        "p0_reset_s": control_max("p0-reset", "activation"),
        "p0_reset_h": control_max("p0-reset", "afterimage"),
        "feedback_ablation_s": control_max(
            "e1-probe-feedback-ablated", "activation"
        ),
        "feedback_ablation_h": control_max(
            "e1-probe-feedback-ablated", "afterimage"
        ),
        "formation_ablation_s": control_max(
            "e1-formation-ablated", "activation"
        ),
        "formation_ablation_h": control_max(
            "e1-formation-ablated", "afterimage"
        ),
    }
    values = {
        "runner_id": S1_EC47_RUNNER_ID,
        "source_contract_digest": contract.contract_digest,
        "sample_digests": tuple(
            (item.refinement_id, item.role_id, item.sample_digest)
            for item in samples
        ),
        "active_s_by_refinement": active_s,
        "active_h_by_refinement": active_h,
        "coarse_s": coarse_s,
        "coarse_h": coarse_h,
        "fine_s": fine_s,
        "fine_h": fine_h,
        "maximum_p0_reset_s": decision_inputs["p0_reset_s"],
        "maximum_p0_reset_h": decision_inputs["p0_reset_h"],
        "maximum_feedback_ablation_s": decision_inputs["feedback_ablation_s"],
        "maximum_feedback_ablation_h": decision_inputs["feedback_ablation_h"],
        "maximum_formation_ablation_s": decision_inputs["formation_ablation_s"],
        "maximum_formation_ablation_h": decision_inputs["formation_ablation_h"],
        "synthetic_decision": decide_common_probe_evidence(**decision_inputs),
        "sample_count": len(samples),
        "all_roles_present_per_refinement": all(
            all((refinement, role) in by_key for role in S1_EC45_PROBE_ROLES)
            for refinement in S1_EC47_REFINEMENTS
        ),
        "common_neuron_order_preserved": len(neuron_orders) == 1,
        "field_steps_executed": sum(item.field_steps_executed for item in samples),
        "synthetic_integration_complete": True,
        "pilot_execution_performed": False,
        "persistence_performed": False,
        "research_decision_permitted": False,
        "memory_claim_permitted": False,
    }
    return E1CommonProbeSyntheticRunnerFixtureResult(
        **values,
        result_digest=_digest(values),
    )
