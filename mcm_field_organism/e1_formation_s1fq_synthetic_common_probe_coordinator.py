"""S1-FQ synthetic integration of fresh formation and 30 probe slots."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import math

from .e1_common_probe_acceptance_contract import decide_common_probe_evidence
from .e1_formation_s1ff_in_memory_capture_adapter import (
    capture_e1_formation_s1ff_in_memory,
)
from .e1_formation_s1fd_state_convergence_evaluator import (
    evaluate_e1_formation_s1fd_state_convergence,
)
from .e1_formation_s1fj_synthetic_coordinator import (
    E1FormationS1FJSyntheticInventory,
)
from .e1_formation_s1fp_common_probe_contract import (
    E1FormationS1FPCommonProbeContract,
    S1_FP_PROBE_ROLES,
    S1_FP_REFINEMENTS,
)
from .e1_refined_formation_runner import _digest, _state_payload


class E1FormationS1FQSyntheticCoordinatorError(ValueError):
    """Raised when S1-FQ leaves its zero-field synthetic scope."""


S1_FQ_COORDINATOR_ID = "e1.fresh-formation-common-probe-synthetic.s1fq.v1"


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


def _finite_vector(values: tuple[float, ...], role: str) -> tuple[float, ...]:
    result = tuple(float(value) for value in values)
    if not result or any(not math.isfinite(value) for value in result):
        raise E1FormationS1FQSyntheticCoordinatorError(
            f"S1-FQ {role} must be one finite nonempty vector"
        )
    return result


def _difference(
    left: tuple[float, ...], right: tuple[float, ...]
) -> tuple[float, ...]:
    if len(left) != len(right):
        raise E1FormationS1FQSyntheticCoordinatorError(
            "S1-FQ probe vectors have different geometries"
        )
    return tuple(a - b for a, b in zip(left, right, strict=True))


def _linf(values: tuple[float, ...]) -> float:
    return max(abs(value) for value in values)


@dataclass(frozen=True, slots=True)
class E1FormationS1FQSyntheticProbeSample:
    refinement_id: str
    role_id: str
    source_state_digest: str | None
    neuron_ids: tuple[str, ...]
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    field_steps_executed: int
    synthetic: bool
    sample_digest: str

    def __post_init__(self) -> None:
        activation = _finite_vector(self.activation, "activation")
        afterimage = _finite_vector(self.afterimage, "afterimage")
        is_p0 = self.role_id.startswith("p0-reset-")
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "sample_digest"
        }
        if (
            self.refinement_id not in S1_FP_REFINEMENTS
            or self.role_id not in S1_FP_PROBE_ROLES
            or (self.source_state_digest is None) is not is_p0
            or (
                self.source_state_digest is not None
                and not _valid_digest(self.source_state_digest)
            )
            or not self.neuron_ids
            or len(set(self.neuron_ids)) != len(self.neuron_ids)
            or len(activation) != len(self.neuron_ids)
            or len(afterimage) != len(self.neuron_ids)
            or self.field_steps_executed != 0
            or self.synthetic is not True
            or self.sample_digest != _digest(payload)
        ):
            raise E1FormationS1FQSyntheticCoordinatorError(
                "S1-FQ synthetic probe sample changed"
            )


def build_e1_formation_s1fq_synthetic_probe_sample(
    refinement_id: str,
    role_id: str,
    source_state_digest: str | None,
) -> E1FormationS1FQSyntheticProbeSample:
    """Build one deterministic typed sample without advancing a field."""

    if refinement_id not in S1_FP_REFINEMENTS or role_id not in S1_FP_PROBE_ROLES:
        raise E1FormationS1FQSyntheticCoordinatorError(
            "S1-FQ unknown refinement or probe role"
        )
    active_levels = {
        "r2": (0.0010015, 0.0020030),
        "r4": (0.0010005, 0.0020010),
        "r8": (0.0010000, 0.0020000),
    }
    activation = (0.0, 0.0, 0.0)
    afterimage = (0.0, 0.0, 0.0)
    if role_id in {"e1-active-ab", "fixed-adapter-ab"}:
        activation_level, afterimage_level = active_levels[refinement_id]
        activation = (activation_level, -0.5 * activation_level, 0.0)
        afterimage = (afterimage_level, -0.5 * afterimage_level, 0.0)
    values = {
        "refinement_id": refinement_id,
        "role_id": role_id,
        "source_state_digest": source_state_digest,
        "neuron_ids": ("n0", "n1", "n2"),
        "activation": activation,
        "afterimage": afterimage,
        "field_steps_executed": 0,
        "synthetic": True,
    }
    return E1FormationS1FQSyntheticProbeSample(
        **values,
        sample_digest=_digest(values),
    )


SyntheticProbeKernel = Callable[
    [str, str, str | None], E1FormationS1FQSyntheticProbeSample
]


@dataclass(frozen=True, slots=True)
class E1FormationS1FQSyntheticCoordinatorResult:
    coordinator_id: str
    source_contract_digest: str
    source_inventory_digest: str
    formation_capture_digest: str
    formation_evaluation_digest: str
    sample_digests: tuple[tuple[str, str, str], ...]
    active_activation_by_refinement: tuple[float, ...]
    active_afterimage_by_refinement: tuple[float, ...]
    coarse_activation: float
    coarse_afterimage: float
    fine_activation: float
    fine_afterimage: float
    maximum_p0_reset_error: float
    maximum_feedback_ablation_error: float
    maximum_formation_ablation_error: float
    maximum_fixed_adapter_error: float
    formation_result_count: int
    probe_sample_count: int
    fresh_probe_field_object_count: int
    formation_states_preserved: bool
    all_probe_roles_present: bool
    common_neuron_order_preserved: bool
    atomic_result_complete: bool
    field_steps_executed: int
    real_formation_performed: bool
    real_probe_performed: bool
    persistence_performed: bool
    owner_authorization_present: bool
    execution_permitted: bool
    memory_claim_permitted: bool
    decision: str
    reason: str
    result_digest: str

    def __post_init__(self) -> None:
        expected = tuple(
            (refinement, role)
            for refinement in S1_FP_REFINEMENTS
            for role in S1_FP_PROBE_ROLES
        )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "result_digest"
        }
        if (
            self.coordinator_id != S1_FQ_COORDINATOR_ID
            or any(
                not _valid_digest(value)
                for value in (
                    self.source_contract_digest,
                    self.source_inventory_digest,
                    self.formation_capture_digest,
                    self.formation_evaluation_digest,
                )
            )
            or tuple((refinement, role) for refinement, role, _ in self.sample_digests)
            != expected
            or len(self.active_activation_by_refinement) != 3
            or len(self.active_afterimage_by_refinement) != 3
            or self.formation_result_count != 15
            or self.probe_sample_count != 30
            or self.fresh_probe_field_object_count != 30
            or any(
                value is not True
                for value in (
                    self.formation_states_preserved,
                    self.all_probe_roles_present,
                    self.common_neuron_order_preserved,
                    self.atomic_result_complete,
                )
            )
            or self.field_steps_executed != 0
            or any(
                value is not False
                for value in (
                    self.real_formation_performed,
                    self.real_probe_performed,
                    self.persistence_performed,
                    self.owner_authorization_present,
                    self.execution_permitted,
                    self.memory_claim_permitted,
                )
            )
            or self.decision not in (
                "SYNTHETIC_FRESH_FORMATION_COMMON_PROBE_FIXED_ADAPTER_EXPLAINED",
                "SYNTHETIC_FRESH_FORMATION_COMMON_PROBE_NOT_FIXED_ADAPTER_EXPLAINED",
            )
            or (
                self.decision.endswith("FIXED_ADAPTER_EXPLAINED")
                and "NOT_FIXED" not in self.decision
                and self.maximum_fixed_adapter_error != 0.0
            )
            or not self.reason
            or self.result_digest != _digest(payload)
        ):
            raise E1FormationS1FQSyntheticCoordinatorError(
                "S1-FQ result changed or crossed zero-field scope"
            )


def coordinate_e1_formation_s1fq_synthetically(
    contract: E1FormationS1FPCommonProbeContract,
    inventory: E1FormationS1FJSyntheticInventory,
    *,
    probe_kernel: SyntheticProbeKernel = build_e1_formation_s1fq_synthetic_probe_sample,
) -> E1FormationS1FQSyntheticCoordinatorResult:
    """Integrate prebuilt formation results and 30 synthetic probe samples."""

    if not isinstance(contract, E1FormationS1FPCommonProbeContract):
        raise E1FormationS1FQSyntheticCoordinatorError(
            "S1-FQ requires the typed S1-FP contract"
        )
    if not isinstance(inventory, E1FormationS1FJSyntheticInventory):
        raise E1FormationS1FQSyntheticCoordinatorError(
            "S1-FQ requires the typed prebuilt S1-FJ inventory"
        )
    if not callable(probe_kernel):
        raise E1FormationS1FQSyntheticCoordinatorError(
            "S1-FQ requires one synthetic probe kernel"
        )
    contract.__post_init__()
    inventory.__post_init__()
    if (
        contract.probe_contract_implementation_permitted is not True
        or contract.field_execution_permitted is not False
        or inventory.field_steps_executed != 0
    ):
        raise E1FormationS1FQSyntheticCoordinatorError(
            "S1-FQ source contract or inventory is not closed"
        )

    capture = capture_e1_formation_s1ff_in_memory(inventory.results)
    formation_evaluation = evaluate_e1_formation_s1fd_state_convergence(
        capture.state_vectors
    )
    if formation_evaluation.decision != "FORMATION_STATE_CONVERGED_DIAGNOSTIC_ONLY":
        raise E1FormationS1FQSyntheticCoordinatorError(
            "S1-FQ formation fixture did not converge"
        )
    source_by_key = {
        (item.refinement_id, item.arm_id): item for item in inventory.results
    }
    state_role_to_arm = {
        "ab": "ab",
        "ba": "ba",
        "formation-ablated-ab": "ab_formation_ablated",
        "formation-ablated-ba": "ba_formation_ablated",
    }

    def source_digest(refinement: str, role: str) -> str | None:
        if role.startswith("p0-reset-"):
            return None
        side = "ab" if role.endswith("-ab") else "ba"
        state_role = (
            f"formation-ablated-{side}"
            if "formation-ablated" in role
            else side
        )
        return source_by_key[(refinement, state_role_to_arm[state_role])].output_state_digest

    state_digests_before = tuple(
        _digest(_state_payload(item.output_state)) for item in inventory.results
    )
    fresh_field_objects = []
    samples = []
    for refinement in S1_FP_REFINEMENTS:
        for role in S1_FP_PROBE_ROLES:
            fresh_field_objects.append(object())
            sample = probe_kernel(refinement, role, source_digest(refinement, role))
            if not isinstance(sample, E1FormationS1FQSyntheticProbeSample):
                raise E1FormationS1FQSyntheticCoordinatorError(
                    "S1-FQ probe kernel returned no typed sample"
                )
            sample.__post_init__()
            if (
                sample.refinement_id != refinement
                or sample.role_id != role
                or sample.source_state_digest != source_digest(refinement, role)
            ):
                raise E1FormationS1FQSyntheticCoordinatorError(
                    "S1-FQ probe sample identity or source state changed"
                )
            samples.append(sample)
    state_digests_after = tuple(
        _digest(_state_payload(item.output_state)) for item in inventory.results
    )
    by_key = {(item.refinement_id, item.role_id): item for item in samples}

    def order_vectors(prefix: str, component: str) -> tuple[tuple[float, ...], ...]:
        return tuple(
            _difference(
                getattr(by_key[(refinement, f"{prefix}-ab")], component),
                getattr(by_key[(refinement, f"{prefix}-ba")], component),
            )
            for refinement in S1_FP_REFINEMENTS
        )

    active_activation_vectors = order_vectors("e1-active", "activation")
    active_afterimage_vectors = order_vectors("e1-active", "afterimage")
    active_activation = tuple(_linf(item) for item in active_activation_vectors)
    active_afterimage = tuple(_linf(item) for item in active_afterimage_vectors)

    def control_max(prefix: str) -> float:
        return max(
            _linf(vector)
            for component in ("activation", "afterimage")
            for vector in order_vectors(prefix, component)
        )

    fixed_errors = tuple(
        _linf(
            _difference(
                getattr(by_key[(refinement, f"e1-active-{side}")], component),
                getattr(by_key[(refinement, f"fixed-adapter-{side}")], component),
            )
        )
        for refinement in S1_FP_REFINEMENTS
        for side in ("ab", "ba")
        for component in ("activation", "afterimage")
    )
    coarse_activation = _linf(
        _difference(active_activation_vectors[0], active_activation_vectors[1])
    )
    coarse_afterimage = _linf(
        _difference(active_afterimage_vectors[0], active_afterimage_vectors[1])
    )
    fine_activation = _linf(
        _difference(active_activation_vectors[1], active_activation_vectors[2])
    )
    fine_afterimage = _linf(
        _difference(active_afterimage_vectors[1], active_afterimage_vectors[2])
    )
    p0_error = control_max("p0-reset")
    feedback_error = control_max("e1-probe-feedback-ablated")
    formation_error = control_max("e1-formation-ablated")
    ec46_decision = decide_common_probe_evidence(
        active_s=active_activation[-1],
        active_h=active_afterimage[-1],
        coarse_s=coarse_activation,
        coarse_h=coarse_afterimage,
        fine_s=fine_activation,
        fine_h=fine_afterimage,
        p0_reset_s=p0_error,
        p0_reset_h=p0_error,
        feedback_ablation_s=feedback_error,
        feedback_ablation_h=feedback_error,
        formation_ablation_s=formation_error,
        formation_ablation_h=formation_error,
    )
    maximum_fixed_error = max(fixed_errors)
    if ec46_decision != "NUMERICALLY_CLEAR_STATE_DEPENDENT_COMMON_PROBE_DIFFERENCE":
        raise E1FormationS1FQSyntheticCoordinatorError(
            "S1-FQ synthetic fixture did not reach the registered EC46 signal"
        )
    decision = (
        "SYNTHETIC_FRESH_FORMATION_COMMON_PROBE_FIXED_ADAPTER_EXPLAINED"
        if maximum_fixed_error <= contract.absolute_control_tolerance
        else "SYNTHETIC_FRESH_FORMATION_COMMON_PROBE_NOT_FIXED_ADAPTER_EXPLAINED"
    )
    values = {
        "coordinator_id": S1_FQ_COORDINATOR_ID,
        "source_contract_digest": contract.contract_digest,
        "source_inventory_digest": inventory.fixture_digest,
        "formation_capture_digest": capture.capture_digest,
        "formation_evaluation_digest": formation_evaluation.result_digest,
        "sample_digests": tuple(
            (item.refinement_id, item.role_id, item.sample_digest) for item in samples
        ),
        "active_activation_by_refinement": active_activation,
        "active_afterimage_by_refinement": active_afterimage,
        "coarse_activation": coarse_activation,
        "coarse_afterimage": coarse_afterimage,
        "fine_activation": fine_activation,
        "fine_afterimage": fine_afterimage,
        "maximum_p0_reset_error": p0_error,
        "maximum_feedback_ablation_error": feedback_error,
        "maximum_formation_ablation_error": formation_error,
        "maximum_fixed_adapter_error": maximum_fixed_error,
        "formation_result_count": len(inventory.results),
        "probe_sample_count": len(samples),
        "fresh_probe_field_object_count": len({id(item) for item in fresh_field_objects}),
        "formation_states_preserved": state_digests_before == state_digests_after,
        "all_probe_roles_present": len(by_key) == 30,
        "common_neuron_order_preserved": len({item.neuron_ids for item in samples}) == 1,
        "atomic_result_complete": True,
        "field_steps_executed": sum(item.field_steps_executed for item in samples),
        "real_formation_performed": False,
        "real_probe_performed": False,
        "persistence_performed": False,
        "owner_authorization_present": False,
        "execution_permitted": False,
        "memory_claim_permitted": False,
        "decision": decision,
        "reason": (
            "fifteen-prebuilt-formation-results-and-thirty-zero-step-probe-"
            "samples-integrated;registered-signal-fully-matched-fixed-adapters"
        ),
    }
    return E1FormationS1FQSyntheticCoordinatorResult(
        **values,
        result_digest=_digest(values),
    )
