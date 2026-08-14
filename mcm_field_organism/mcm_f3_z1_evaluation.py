"""Pure preregistered evaluation for one completed Z1 technical packet."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields

from .mcm_f3_z1_runner import (
    MCMF3Z1ArmTrajectory,
    MCMF3Z1TechnicalPacket,
)
from .mcm_f3_z1_trajectory import (
    MCMF3Z1PathDistances,
    MCMF3Z1TrajectoryError,
    numerical_envelope,
    trajectory_path_distances,
)


class MCMF3Z1EvaluationError(ValueError):
    """Raised when a Z1 packet cannot enter the preregistered evaluation."""


_MODEL_IDS = ("f3-candidate", "linear-coupled-field")
_ARM_IDS = (
    "a.reference",
    "a.partitioned",
    "a.stretched",
    "a.compressed",
    "a.reversed",
    "a.permuted",
    "b.independent",
)
_ROLES = ("activation", "afterimage", "mass")
_STRUCTURAL_LIMIT = 0.05
_BASELINE_LIMIT = 0.05


@dataclass(frozen=True, slots=True)
class MCMF3Z1ArmEvaluation:
    model_id: str
    arm_id: str
    n_to_2n: MCMF3Z1PathDistances
    two_n_to_4n: MCMF3Z1PathDistances
    numerical_envelope: MCMF3Z1PathDistances
    distance_from_reference: MCMF3Z1PathDistances
    comparison_envelope: MCMF3Z1PathDistances

    def __post_init__(self) -> None:
        if self.model_id not in _MODEL_IDS or self.arm_id not in _ARM_IDS:
            raise MCMF3Z1EvaluationError("unknown Z1 arm evaluation identity")
        for role in (
            "n_to_2n",
            "two_n_to_4n",
            "numerical_envelope",
            "distance_from_reference",
            "comparison_envelope",
        ):
            if not isinstance(getattr(self, role), MCMF3Z1PathDistances):
                raise MCMF3Z1EvaluationError("Z1 arm evaluation requires path distances")


@dataclass(frozen=True, slots=True)
class MCMF3Z1ModelEvaluation:
    model_id: str
    arms: tuple[MCMF3Z1ArmEvaluation, ...]
    technical_partition_invariant: bool
    time_reparameterization_covariant: bool
    order_sensitive_field_path: bool
    classification_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.model_id not in _MODEL_IDS:
            raise MCMF3Z1EvaluationError("unknown Z1 model evaluation")
        if tuple(item.arm_id for item in self.arms) != _ARM_IDS:
            raise MCMF3Z1EvaluationError("Z1 model arm evaluations changed")
        allowed = {
            "TECHNICAL_PARTITION_INVARIANT",
            "WORLD_TIME_BOUND_FIELD_PATH",
            "TIME_REPARAMETERIZATION_COVARIANT",
            "ORDER_SENSITIVE_FIELD_PATH",
            "TECHNICALLY_UNDECIDABLE",
        }
        if not self.classification_ids or not set(self.classification_ids) <= allowed:
            raise MCMF3Z1EvaluationError("Z1 model classification is outside the contract")


@dataclass(frozen=True, slots=True)
class MCMF3Z1BaselineComparison:
    arm_id: str
    f3_to_linear_distance: MCMF3Z1PathDistances
    within_limit: bool

    def __post_init__(self) -> None:
        if self.arm_id not in _ARM_IDS:
            raise MCMF3Z1EvaluationError("unknown Z1 baseline comparison arm")
        if not isinstance(self.f3_to_linear_distance, MCMF3Z1PathDistances):
            raise MCMF3Z1EvaluationError("Z1 baseline comparison requires distances")


@dataclass(frozen=True, slots=True)
class MCMF3Z1EvaluationResult:
    preregistration_id: str
    source_execution_digests: tuple[tuple[str, str], ...]
    packet_controls: tuple[tuple[str, bool], ...]
    model_evaluations: tuple[MCMF3Z1ModelEvaluation, ...]
    baseline_comparisons: tuple[MCMF3Z1BaselineComparison, ...]
    baseline_explains_f3: bool
    decision_ids: tuple[str, ...]
    evaluation_error: str | None = None
    raw_trajectories_retained: bool = False
    memory_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    topology_claim_allowed: bool = False
    semantics_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        if self.preregistration_id != "mcm.f3.z1.trajectory-covariance.v1":
            raise MCMF3Z1EvaluationError("Z1 evaluation preregistration changed")
        if self.evaluation_error is None:
            if tuple(item.model_id for item in self.model_evaluations) != _MODEL_IDS:
                raise MCMF3Z1EvaluationError("Z1 evaluation requires both models")
            if tuple(item.arm_id for item in self.baseline_comparisons) != _ARM_IDS:
                raise MCMF3Z1EvaluationError("Z1 evaluation requires all baseline arms")
        elif self.decision_ids != ("TECHNICALLY_UNDECIDABLE",):
            raise MCMF3Z1EvaluationError("failed Z1 evaluation must be undecidable")
        if any(
            (
                self.raw_trajectories_retained,
                self.memory_claim_allowed,
                self.organization_claim_allowed,
                self.topology_claim_allowed,
                self.semantics_claim_allowed,
                self.ai_claim_allowed,
            )
        ):
            raise MCMF3Z1EvaluationError("Z1 evaluation cannot release claims or raw paths")


def _zero_distances() -> MCMF3Z1PathDistances:
    return MCMF3Z1PathDistances(0.0, 0.0, 0.0)


def _componentwise_max(
    left: MCMF3Z1PathDistances,
    right: MCMF3Z1PathDistances,
) -> MCMF3Z1PathDistances:
    return MCMF3Z1PathDistances(
        *(max(getattr(left, role), getattr(right, role)) for role in _ROLES)
    )


def _all_at_most(
    values: MCMF3Z1PathDistances,
    limits: MCMF3Z1PathDistances,
    *,
    floor: float = 0.0,
) -> bool:
    return all(
        getattr(values, role) <= max(floor, getattr(limits, role))
        for role in _ROLES
    )


def _any_above(
    values: MCMF3Z1PathDistances,
    limits: MCMF3Z1PathDistances,
) -> bool:
    return any(getattr(values, role) > getattr(limits, role) for role in _ROLES)


def _indexed(
    packet: MCMF3Z1TechnicalPacket,
) -> dict[tuple[str, str, int, bool], MCMF3Z1ArmTrajectory]:
    return {item.task_key: item for item in packet.trajectories}


def _model_evaluation(
    model_id: str,
    indexed: dict[tuple[str, str, int, bool], MCMF3Z1ArmTrajectory],
) -> MCMF3Z1ModelEvaluation:
    interim = []
    envelopes = {}
    for arm_id in _ARM_IDS:
        n = indexed[(model_id, arm_id, 1, False)].trajectory
        two_n = indexed[(model_id, arm_id, 2, False)].trajectory
        four_n = indexed[(model_id, arm_id, 4, False)].trajectory
        n_to_2n = trajectory_path_distances(two_n, n)
        two_n_to_4n = trajectory_path_distances(four_n, two_n)
        envelope = numerical_envelope(two_n, four_n)
        envelopes[arm_id] = envelope
        interim.append((arm_id, n_to_2n, two_n_to_4n, envelope, four_n))

    reference = indexed[(model_id, "a.reference", 4, False)].trajectory
    reference_envelope = envelopes["a.reference"]
    arms = []
    for arm_id, n_to_2n, two_n_to_4n, envelope, four_n in interim:
        distance = (
            _zero_distances()
            if arm_id == "a.reference"
            else trajectory_path_distances(reference, four_n)
        )
        arms.append(
            MCMF3Z1ArmEvaluation(
                model_id,
                arm_id,
                n_to_2n,
                two_n_to_4n,
                envelope,
                distance,
                _componentwise_max(reference_envelope, envelope),
            )
        )
    by_arm = {item.arm_id: item for item in arms}
    partition_invariant = _all_at_most(
        by_arm["a.partitioned"].distance_from_reference,
        by_arm["a.partitioned"].comparison_envelope,
    )
    time_covariant = all(
        _all_at_most(
            by_arm[arm_id].distance_from_reference,
            by_arm[arm_id].comparison_envelope,
            floor=_STRUCTURAL_LIMIT,
        )
        for arm_id in ("a.stretched", "a.compressed")
    )

    def order_threshold(arm_id: str) -> MCMF3Z1PathDistances:
        envelope = by_arm[arm_id].comparison_envelope
        return MCMF3Z1PathDistances(
            *(max(_STRUCTURAL_LIMIT, 4.0 * getattr(envelope, role)) for role in _ROLES)
        )

    order_sensitive = all(
        _any_above(
            by_arm[arm_id].distance_from_reference,
            order_threshold(arm_id),
        )
        for arm_id in ("a.reversed", "a.permuted", "b.independent")
    )
    if not partition_invariant:
        classification_ids = ("TECHNICALLY_UNDECIDABLE",)
    else:
        values = ["TECHNICAL_PARTITION_INVARIANT"]
        values.append(
            "TIME_REPARAMETERIZATION_COVARIANT"
            if time_covariant
            else "WORLD_TIME_BOUND_FIELD_PATH"
        )
        if order_sensitive:
            values.append("ORDER_SENSITIVE_FIELD_PATH")
        classification_ids = tuple(values)
    return MCMF3Z1ModelEvaluation(
        model_id,
        tuple(arms),
        partition_invariant,
        time_covariant,
        order_sensitive,
        classification_ids,
    )


def _undecidable(
    packet: MCMF3Z1TechnicalPacket,
    reason: str,
) -> MCMF3Z1EvaluationResult:
    return MCMF3Z1EvaluationResult(
        packet.preregistration_id,
        packet.source_execution_digests,
        packet.controls,
        (),
        (),
        False,
        ("TECHNICALLY_UNDECIDABLE",),
        reason,
    )


def evaluate_mcm_f3_z1_packet(
    packet: MCMF3Z1TechnicalPacket,
) -> MCMF3Z1EvaluationResult:
    """Evaluate one packet without writing files or assigning a run number."""

    if not isinstance(packet, MCMF3Z1TechnicalPacket):
        raise MCMF3Z1EvaluationError("Z1 evaluation requires one technical packet")
    failed_controls = tuple(name for name, value in packet.controls if not value)
    if failed_controls:
        return _undecidable(packet, f"failed packet controls: {', '.join(failed_controls)}")
    try:
        indexed = _indexed(packet)
        models = tuple(_model_evaluation(model_id, indexed) for model_id in _MODEL_IDS)
        comparisons = []
        for arm_id in _ARM_IDS:
            distance = trajectory_path_distances(
                indexed[("f3-candidate", arm_id, 4, False)].trajectory,
                indexed[("linear-coupled-field", arm_id, 4, False)].trajectory,
            )
            comparisons.append(
                MCMF3Z1BaselineComparison(
                    arm_id,
                    distance,
                    all(getattr(distance, role) <= _BASELINE_LIMIT for role in _ROLES),
                )
            )
    except (KeyError, MCMF3Z1TrajectoryError, ValueError) as exc:
        return _undecidable(packet, str(exc))

    candidate, baseline = models
    baseline_explains = (
        candidate.classification_ids != ("TECHNICALLY_UNDECIDABLE",)
        and candidate.classification_ids == baseline.classification_ids
        and all(item.within_limit for item in comparisons)
    )
    return MCMF3Z1EvaluationResult(
        packet.preregistration_id,
        packet.source_execution_digests,
        packet.controls,
        models,
        tuple(comparisons),
        baseline_explains,
        candidate.classification_ids,
    )


def mcm_f3_z1_evaluation_json_value(
    result: MCMF3Z1EvaluationResult,
) -> dict[str, object]:
    """Project scalar Z1 results to JSON without retaining raw trajectories."""

    if not isinstance(result, MCMF3Z1EvaluationResult):
        raise MCMF3Z1EvaluationError("Z1 JSON projection requires an evaluation result")
    payload = asdict(result)
    payload["schema_id"] = "mcm.f3.z1.evaluation.v1"
    return payload


def mcm_f3_z1_evaluation_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            MCMF3Z1ArmEvaluation,
            MCMF3Z1ModelEvaluation,
            MCMF3Z1BaselineComparison,
            MCMF3Z1EvaluationResult,
        )
        for item in fields(cls)
    )
