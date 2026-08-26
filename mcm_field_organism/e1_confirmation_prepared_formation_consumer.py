"""Private S1-EC7 synthetic formation consumer for prepared bundle inputs."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import Any

from .e1_confirmation_descriptor_refinement_planner import (
    E1ConfirmationDescriptorRefinementPlanSet,
)
from .e1_confirmation_prepared_execution_bundle import E1PreparedExecutionBundle
from .e1_confirmation_research_corridor import (
    E1ConfirmationResearchCorridorDescriptor,
    S1_EC3_RUN_ID,
)
from .e1_confirmation_typed_prepared_inputs import (
    E1ConfirmationTypedPreparedInputs,
    S1_EC2_INPUT_ROLES,
)
from .e1_refined_formation_runner import _digest


class E1ConfirmationPreparedFormationConsumerError(ValueError):
    """Raised when S1-EC7 cannot consume the prepared formation inputs."""


S1_EC7_FORMATION_ARMS = (
    "ab",
    "ba",
    "ab_identity",
    "ab_formation_ablated",
    "ba_formation_ablated",
)
S1_EC7_REFINEMENTS = (("r2", 2), ("r4", 4), ("r8", 8))


SyntheticFormationKernel = Callable[
    [str, str, Any, Any, Any, Any, bool],
    str,
]


def _valid_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


@dataclass(frozen=True, slots=True)
class E1PreparedFormationConsumerResult:
    execution_id: str
    run_contract_digest: str
    bundle_digest: str
    refinement_digests: tuple[
        tuple[str, int, tuple[tuple[str, str], ...]], ...
    ]
    prepared_inputs_only: bool
    synthetic_kernels_only: bool
    field_execution_permitted: bool
    claims_permitted: bool
    result_digest: str

    def __post_init__(self) -> None:
        refinements = tuple(self.refinement_digests)
        if (
            self.execution_id != S1_EC3_RUN_ID
            or not _valid_digest(self.run_contract_digest)
            or not _valid_digest(self.bundle_digest)
            or tuple((role, factor) for role, factor, _ in refinements)
            != S1_EC7_REFINEMENTS
            or any(
                tuple(role for role, _ in arms) != S1_EC7_FORMATION_ARMS
                or any(not _valid_digest(value) for _, value in arms)
                for _, _, arms in refinements
            )
            or self.prepared_inputs_only is not True
            or self.synthetic_kernels_only is not True
            or self.field_execution_permitted is not False
            or self.claims_permitted is not False
        ):
            raise E1ConfirmationPreparedFormationConsumerError(
                "S1-EC7 formation consumer result changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "result_digest"
        }
        if self.result_digest != _digest(payload):
            raise E1ConfirmationPreparedFormationConsumerError(
                "S1-EC7 result digest does not match its payload"
            )
        object.__setattr__(self, "refinement_digests", refinements)

    def digest(self) -> str:
        return _digest(asdict(self))


def _typed_values_from_bundle(
    bundle: E1PreparedExecutionBundle,
) -> E1ConfirmationTypedPreparedInputs:
    if tuple(role for role, _ in bundle.input_manifest) != S1_EC2_INPUT_ROLES:
        raise E1ConfirmationPreparedFormationConsumerError(
            "S1-EC7 requires the complete ordered S1-EC2 input manifest"
        )
    values = E1ConfirmationTypedPreparedInputs(
        corridor=bundle.value("corridor"),
        av_permutation=bundle.value("av_permutation"),
        history_ab_plans=bundle.value("history_ab_plans"),
        history_ba_plans=bundle.value("history_ba_plans"),
        probe_sequences=bundle.value("probe_sequences"),
        probe_plans=bundle.value("probe_plans"),
        initial_field=bundle.value("initial_field"),
        initial_state=bundle.value("initial_state"),
    )
    if not isinstance(
        values.corridor, E1ConfirmationResearchCorridorDescriptor
    ) or any(
        not isinstance(item, E1ConfirmationDescriptorRefinementPlanSet)
        for item in (
            values.history_ab_plans,
            values.history_ba_plans,
            values.probe_plans,
        )
    ):
        raise E1ConfirmationPreparedFormationConsumerError(
            "S1-EC7 requires descriptor-bound prepared inputs"
        )
    return values


def run_prepared_formation_consumer_synthetically(
    bundle: E1PreparedExecutionBundle,
    kernel: SyntheticFormationKernel,
) -> E1PreparedFormationConsumerResult:
    """Map prepared inputs to synthetic arm kernels without resolving inputs."""

    if not isinstance(bundle, E1PreparedExecutionBundle) or (
        bundle.execution_id != S1_EC3_RUN_ID
        or not callable(kernel)
    ):
        raise E1ConfirmationPreparedFormationConsumerError(
            "S1-EC7 requires one S1-EC3 bundle and one synthetic kernel"
        )
    bundle.__post_init__()
    values = _typed_values_from_bundle(bundle)
    source = values.av_permutation
    outputs = []
    for ab_plan, ba_plan in zip(
        values.history_ab_plans.plans,
        values.history_ba_plans.plans,
        strict=True,
    ):
        if (
            (ab_plan.refinement_id, ab_plan.factor)
            != (ba_plan.refinement_id, ba_plan.factor)
        ):
            raise E1ConfirmationPreparedFormationConsumerError(
                "S1-EC7 AB and BA refinements do not align"
            )
        arm_inputs = (
            ("ab", source.history_ab, ab_plan.proposal_steps, True),
            ("ba", source.history_ba, ba_plan.proposal_steps, True),
            ("ab_identity", source.history_ab, ab_plan.proposal_steps, True),
            (
                "ab_formation_ablated",
                source.history_ab,
                ab_plan.proposal_steps,
                False,
            ),
            (
                "ba_formation_ablated",
                source.history_ba,
                ba_plan.proposal_steps,
                False,
            ),
        )
        arm_digests = []
        for arm_id, sequences, steps, formation_enabled in arm_inputs:
            produced = kernel(
                arm_id,
                ab_plan.refinement_id,
                sequences,
                steps,
                values.initial_field,
                values.initial_state,
                formation_enabled,
            )
            if not _valid_digest(produced):
                raise E1ConfirmationPreparedFormationConsumerError(
                    f"S1-EC7 synthetic {arm_id} kernel returned no SHA-256"
                )
            arm_digests.append((arm_id, produced))
        outputs.append(
            (ab_plan.refinement_id, ab_plan.factor, tuple(arm_digests))
        )
    payload = {
        "execution_id": bundle.execution_id,
        "run_contract_digest": bundle.run_contract_digest,
        "bundle_digest": bundle.bundle_digest,
        "refinement_digests": tuple(outputs),
        "prepared_inputs_only": True,
        "synthetic_kernels_only": True,
        "field_execution_permitted": False,
        "claims_permitted": False,
    }
    return E1PreparedFormationConsumerResult(
        **payload,
        result_digest=_digest(payload),
    )
