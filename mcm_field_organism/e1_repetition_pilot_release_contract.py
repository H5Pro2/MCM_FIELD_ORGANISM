"""Static S1-EC29 release contract for a noncanonical n1/n2 pilot."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .e1_refined_formation_runner import _digest
from .e1_repetition_formation_fixture_consumer import (
    E1RepetitionFormationFixtureResult,
)
from .e1_repetition_formation_planner import (
    E1RepetitionFormationPlanSet,
)


class E1RepetitionPilotReleaseContractError(ValueError):
    """Raised when S1-EC29 changes pilot scope or permits execution."""


S1_EC29_CONTRACT_ID = "e1.repetition-pilot-release-contract.s1ec29.v1"
S1_EC29_PLAN_SET_DIGEST = (
    "b53d1e1c94dedaf4d7cd8aac250d8c81bd0ebc0b0e2ea69ecd7e0e3716b365ea"
)
S1_EC29_FIXTURE_RESULT_DIGEST = (
    "1b36c259202d8e8b27941a91ca508af181b7391afc2ca9f1b9f6e616f1fadff6"
)
S1_EC29_CONTACT_COUNTS = (1, 2)
S1_EC29_REFINEMENTS = ("r2", "r4", "r8")
S1_EC29_ARMS = (
    "p0_repeated",
    "p0_continuous",
    "repeated_formation_ablated",
    "continuous_formation_ablated",
    "repeated_active",
    "continuous_active",
)
S1_EC29_STEP_COUNTS = (
    (1, (202, 404, 808)),
    (2, (402, 804, 1608)),
)
S1_EC29_FIELD_ARM_STEPS = 25_368
S1_EC29_MIN_FREE_MEMORY_BYTES = 4 * 1024**3
S1_EC29_MIN_FREE_DISK_BYTES = 1 * 1024**3
S1_EC29_MAX_RUNTIME_SECONDS = 900.0
S1_EC29_REQUIRED_GATES = (
    "corrected-ec27-plan-set-bound",
    "ec28-real-fixture-complete",
    "n1-before-n2",
    "r2-before-r4-before-r8-per-contact-count",
    "p0-before-ablation-before-active-per-refinement",
    "repeated-and-continuous-step-counts-pairwise-equal",
    "repeated-and-continuous-last-contact-completions-equal",
    "all-source-supports-assigned-once",
    "fresh-identical-field-and-e1-starts-per-arm",
    "p0-contains-no-e1-state-or-adapter",
    "formation-ablation-contains-neutral-e1-with-updates-disabled",
    "active-arms-use-unchanged-e1-mechanism",
    "abort-before-next-batch-on-control-failure",
    "no-output-path-or-persistence",
    "no-result-decision-or-claim",
)


@dataclass(frozen=True, slots=True)
class E1RepetitionPilotBatch:
    batch_index: int
    contact_count: int
    refinement_id: str
    step_count_per_arm: int
    arm_order: tuple[str, ...]
    field_arm_step_count: int

    def __post_init__(self) -> None:
        expected_counts = dict(S1_EC29_STEP_COUNTS)
        expected_index = (
            S1_EC29_CONTACT_COUNTS.index(self.contact_count) * 3
            + S1_EC29_REFINEMENTS.index(self.refinement_id)
        )
        expected_steps = expected_counts[self.contact_count][
            S1_EC29_REFINEMENTS.index(self.refinement_id)
        ]
        if (
            self.batch_index != expected_index
            or self.arm_order != S1_EC29_ARMS
            or self.step_count_per_arm != expected_steps
            or self.field_arm_step_count
            != self.step_count_per_arm * len(S1_EC29_ARMS)
        ):
            raise E1RepetitionPilotReleaseContractError(
                "S1-EC29 batch order or load changed"
            )


@dataclass(frozen=True, slots=True)
class E1RepetitionPilotReleaseContract:
    contract_id: str
    source_plan_set_digest: str
    fixture_result_digest: str
    contact_counts: tuple[int, ...]
    refinements: tuple[str, ...]
    arms: tuple[str, ...]
    batches: tuple[E1RepetitionPilotBatch, ...]
    field_arm_step_count: int
    minimum_free_memory_bytes: int
    minimum_free_disk_bytes: int
    maximum_runtime_seconds: float
    required_gates: tuple[str, ...]
    failure_policy: str
    evidence_scope: str
    runner_implementation_permitted: bool
    pilot_execution_permitted: bool
    persistence_permitted: bool
    result_decision_permitted: bool
    imprinting_claim_permitted: bool
    memory_claim_permitted: bool
    ai_claim_permitted: bool
    contract_digest: str

    def __post_init__(self) -> None:
        if (
            self.contract_id != S1_EC29_CONTRACT_ID
            or self.source_plan_set_digest != S1_EC29_PLAN_SET_DIGEST
            or self.fixture_result_digest != S1_EC29_FIXTURE_RESULT_DIGEST
            or self.contact_counts != S1_EC29_CONTACT_COUNTS
            or self.refinements != S1_EC29_REFINEMENTS
            or self.arms != S1_EC29_ARMS
            or tuple(item.batch_index for item in self.batches)
            != tuple(range(6))
            or self.field_arm_step_count != S1_EC29_FIELD_ARM_STEPS
            or sum(item.field_arm_step_count for item in self.batches)
            != self.field_arm_step_count
            or self.minimum_free_memory_bytes != S1_EC29_MIN_FREE_MEMORY_BYTES
            or self.minimum_free_disk_bytes != S1_EC29_MIN_FREE_DISK_BYTES
            or self.maximum_runtime_seconds != S1_EC29_MAX_RUNTIME_SECONDS
            or self.required_gates != S1_EC29_REQUIRED_GATES
            or self.failure_policy != "abort-before-next-batch-no-partial-result"
            or self.evidence_scope != "technical-n1-n2-pilot-readiness-only"
            or self.runner_implementation_permitted is not True
            or any(
                value is not False
                for value in (
                    self.pilot_execution_permitted,
                    self.persistence_permitted,
                    self.result_decision_permitted,
                    self.imprinting_claim_permitted,
                    self.memory_claim_permitted,
                    self.ai_claim_permitted,
                )
            )
        ):
            raise E1RepetitionPilotReleaseContractError(
                "S1-EC29 release contract changed or exceeded pilot scope"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"batches", "contract_digest"}
        }
        payload["batches"] = tuple(asdict(item) for item in self.batches)
        if self.contract_digest != _digest(payload):
            raise E1RepetitionPilotReleaseContractError(
                "S1-EC29 contract digest changed"
            )


def build_e1_repetition_pilot_release_contract(
    plans: E1RepetitionFormationPlanSet,
    fixture: E1RepetitionFormationFixtureResult,
) -> E1RepetitionPilotReleaseContract:
    """Bind pilot load and order without running or persisting a pilot arm."""

    if not isinstance(plans, E1RepetitionFormationPlanSet):
        raise E1RepetitionPilotReleaseContractError(
            "S1-EC29 requires the corrected S1-EC27 plan set"
        )
    if not isinstance(fixture, E1RepetitionFormationFixtureResult):
        raise E1RepetitionPilotReleaseContractError(
            "S1-EC29 requires the complete S1-EC28 fixture result"
        )
    plans.__post_init__()
    fixture.__post_init__()
    if (
        plans.plan_set_digest != S1_EC29_PLAN_SET_DIGEST
        or fixture.result_digest != S1_EC29_FIXTURE_RESULT_DIGEST
        or fixture.source_pair_digest != plans.pairs[1].pair_digest
    ):
        raise E1RepetitionPilotReleaseContractError(
            "S1-EC29 upstream evidence changed"
        )
    batches = []
    observed_step_counts = []
    for contact_index, pair in enumerate(plans.pairs[:2]):
        repeated_counts = tuple(
            len(item.proposal_steps) for item in pair.repeated_plans.plans
        )
        continuous_counts = tuple(
            len(item.proposal_steps) for item in pair.continuous_plans.plans
        )
        if repeated_counts != continuous_counts:
            raise E1RepetitionPilotReleaseContractError(
                "S1-EC29 pair step counts differ"
            )
        observed_step_counts.append((pair.contact_count, repeated_counts))
        for refinement_index, (refinement_id, step_count) in enumerate(
            zip(S1_EC29_REFINEMENTS, repeated_counts, strict=True)
        ):
            batches.append(
                E1RepetitionPilotBatch(
                    batch_index=contact_index * 3 + refinement_index,
                    contact_count=pair.contact_count,
                    refinement_id=refinement_id,
                    step_count_per_arm=step_count,
                    arm_order=S1_EC29_ARMS,
                    field_arm_step_count=step_count * len(S1_EC29_ARMS),
                )
            )
    if tuple(observed_step_counts) != S1_EC29_STEP_COUNTS:
        raise E1RepetitionPilotReleaseContractError(
            "S1-EC29 observed step inventory changed"
        )
    payload = {
        "contract_id": S1_EC29_CONTRACT_ID,
        "source_plan_set_digest": plans.plan_set_digest,
        "fixture_result_digest": fixture.result_digest,
        "contact_counts": S1_EC29_CONTACT_COUNTS,
        "refinements": S1_EC29_REFINEMENTS,
        "arms": S1_EC29_ARMS,
        "batches": tuple(asdict(item) for item in batches),
        "field_arm_step_count": S1_EC29_FIELD_ARM_STEPS,
        "minimum_free_memory_bytes": S1_EC29_MIN_FREE_MEMORY_BYTES,
        "minimum_free_disk_bytes": S1_EC29_MIN_FREE_DISK_BYTES,
        "maximum_runtime_seconds": S1_EC29_MAX_RUNTIME_SECONDS,
        "required_gates": S1_EC29_REQUIRED_GATES,
        "failure_policy": "abort-before-next-batch-no-partial-result",
        "evidence_scope": "technical-n1-n2-pilot-readiness-only",
        "runner_implementation_permitted": True,
        "pilot_execution_permitted": False,
        "persistence_permitted": False,
        "result_decision_permitted": False,
        "imprinting_claim_permitted": False,
        "memory_claim_permitted": False,
        "ai_claim_permitted": False,
    }
    digest = _digest(payload)
    payload["batches"] = tuple(batches)
    return E1RepetitionPilotReleaseContract(
        **payload,
        contract_digest=digest,
    )
