"""S1-EC38 synthetic runner fixture for quantitative P0 handoffs."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass, replace

from .e1_refined_formation_runner import _digest
from .e1_repetition_pilot_quantitative_p0_integration_contract import (
    E1QuantitativeP0BatchHandoff,
    E1RepetitionPilotQuantitativeP0IntegrationContract,
    S1_EC37_CONTRACT_ID,
)
from .e1_repetition_pilot_quantitative_p0_schema import (
    E1PilotQuantitativeP0Pair,
    E1PilotQuantitativeP0RefinementProfile,
    build_quantitative_p0_refinement_profile,
    collect_quantitative_p0_pair,
)
from .shared_mcm_field import SharedMCMFieldSnapshot


class E1RepetitionPilotQuantitativeP0RunnerFixtureError(ValueError):
    """Raised when S1-EC38 crosses its synthetic-only runner boundary."""


S1_EC38_RUNNER_ID = "e1.repetition-pilot-quantitative-p0-runner.s1ec38.v1"
S1_EC38_EC37_CONTRACT_DIGEST = (
    "ad9200e960f6c0c68791a41cc2c8810af2d087a7ade4690593e226e1de37502e"
)


SyntheticP0SnapshotKernel = Callable[
    [E1QuantitativeP0BatchHandoff, SharedMCMFieldSnapshot],
    tuple[SharedMCMFieldSnapshot, SharedMCMFieldSnapshot],
]


def build_synthetic_p0_snapshot_handoff(
    handoff: E1QuantitativeP0BatchHandoff,
    template: SharedMCMFieldSnapshot,
) -> tuple[SharedMCMFieldSnapshot, SharedMCMFieldSnapshot]:
    """Return two deterministic snapshot copies without advancing a field."""

    if not isinstance(handoff, E1QuantitativeP0BatchHandoff) or not isinstance(
        template, SharedMCMFieldSnapshot
    ):
        raise E1RepetitionPilotQuantitativeP0RunnerFixtureError(
            "S1-EC38 requires one handoff and one snapshot template"
        )
    handoff.__post_init__()
    template.__post_init__()
    refinement_scale = {"r2": 3.0, "r4": 2.0, "r8": 1.5}[
        handoff.refinement_id
    ]
    amount = handoff.contact_count * refinement_scale * 1e-6
    neurons = list(template.layer.neurons)
    first = neurons[0]
    neurons[0] = replace(
        first,
        activation=first.activation + amount,
        afterimage=first.afterimage - 0.5 * amount,
    )
    repeated = replace(
        template,
        layer=replace(template.layer, neurons=tuple(neurons)),
    )
    continuous = replace(template)
    if repeated is template or continuous is template or repeated is continuous:
        raise E1RepetitionPilotQuantitativeP0RunnerFixtureError(
            "S1-EC38 snapshot copies are not separated"
        )
    return repeated, continuous


@dataclass(frozen=True, slots=True)
class E1RepetitionPilotQuantitativeP0RunnerFixtureResult:
    runner_id: str
    source_contract_digest: str
    pair_digests: tuple[tuple[int, str], ...]
    profile_digests: tuple[tuple[int, str], ...]
    batch_completion_order: tuple[int, ...]
    snapshot_handoff_count: int
    pair_collection_count: int
    profile_count: int
    all_snapshot_objects_separated: bool
    all_pairs_collected_before_profile: bool
    fail_fast_enabled: bool
    field_execution_performed: bool
    authorization_consumed: bool
    persistence_performed: bool
    result_decision_permitted: bool
    memory_claim_permitted: bool
    result_digest: str

    def __post_init__(self) -> None:
        if (
            self.runner_id != S1_EC38_RUNNER_ID
            or self.source_contract_digest != S1_EC38_EC37_CONTRACT_DIGEST
            or tuple(index for index, _ in self.pair_digests) != tuple(range(6))
            or tuple(count for count, _ in self.profile_digests) != (1, 2)
            or any(len(digest) != 64 for _, digest in self.pair_digests)
            or any(len(digest) != 64 for _, digest in self.profile_digests)
            or self.batch_completion_order != tuple(range(6))
            or self.snapshot_handoff_count != 12
            or self.pair_collection_count != 6
            or self.profile_count != 2
            or any(
                value is not True
                for value in (
                    self.all_snapshot_objects_separated,
                    self.all_pairs_collected_before_profile,
                    self.fail_fast_enabled,
                )
            )
            or any(
                value is not False
                for value in (
                    self.field_execution_performed,
                    self.authorization_consumed,
                    self.persistence_performed,
                    self.result_decision_permitted,
                    self.memory_claim_permitted,
                )
            )
        ):
            raise E1RepetitionPilotQuantitativeP0RunnerFixtureError(
                "S1-EC38 result changed or crossed synthetic scope"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "result_digest"
        }
        if self.result_digest != _digest(payload):
            raise E1RepetitionPilotQuantitativeP0RunnerFixtureError(
                "S1-EC38 result digest changed"
            )


def run_quantitative_p0_handoff_runner_fixture(
    contract: E1RepetitionPilotQuantitativeP0IntegrationContract,
    template: SharedMCMFieldSnapshot,
    *,
    kernel: SyntheticP0SnapshotKernel = build_synthetic_p0_snapshot_handoff,
) -> E1RepetitionPilotQuantitativeP0RunnerFixtureResult:
    """Exercise all EC37 handoffs without invoking a field runtime."""

    if (
        not isinstance(
            contract, E1RepetitionPilotQuantitativeP0IntegrationContract
        )
        or not isinstance(template, SharedMCMFieldSnapshot)
        or not callable(kernel)
    ):
        raise E1RepetitionPilotQuantitativeP0RunnerFixtureError(
            "S1-EC38 requires contract, snapshot template, and kernel"
        )
    contract.__post_init__()
    template.__post_init__()
    if (
        contract.contract_id != S1_EC37_CONTRACT_ID
        or contract.contract_digest != S1_EC38_EC37_CONTRACT_DIGEST
        or contract.runner_implementation_permitted is not True
        or contract.field_execution_permitted is not False
    ):
        raise E1RepetitionPilotQuantitativeP0RunnerFixtureError(
            "S1-EC38 contract is not implementation-only"
        )
    pairs: list[E1PilotQuantitativeP0Pair] = []
    completed = []
    snapshots_separated = []
    for handoff in contract.handoffs:
        produced = kernel(handoff, template)
        if (
            not isinstance(produced, tuple)
            or len(produced) != 2
            or any(not isinstance(item, SharedMCMFieldSnapshot) for item in produced)
        ):
            raise E1RepetitionPilotQuantitativeP0RunnerFixtureError(
                "S1-EC38 kernel returned no typed snapshot pair"
            )
        repeated, continuous = produced
        snapshots_separated.append(
            repeated is not continuous
            and repeated is not template
            and continuous is not template
        )
        pair = collect_quantitative_p0_pair(
            handoff.contact_count,
            handoff.refinement_id,
            repeated,
            continuous,
        )
        pairs.append(pair)
        completed.append(handoff.batch_index)
    profiles: list[E1PilotQuantitativeP0RefinementProfile] = []
    for contact_count in (1, 2):
        trio = tuple(item for item in pairs if item.contact_count == contact_count)
        profiles.append(build_quantitative_p0_refinement_profile(trio))
    values = {
        "runner_id": S1_EC38_RUNNER_ID,
        "source_contract_digest": contract.contract_digest,
        "pair_digests": tuple(
            (handoff.batch_index, pair.pair_digest)
            for handoff, pair in zip(contract.handoffs, pairs, strict=True)
        ),
        "profile_digests": tuple(
            (item.contact_count, item.profile_digest) for item in profiles
        ),
        "batch_completion_order": tuple(completed),
        "snapshot_handoff_count": len(pairs) * 2,
        "pair_collection_count": len(pairs),
        "profile_count": len(profiles),
        "all_snapshot_objects_separated": all(snapshots_separated),
        "all_pairs_collected_before_profile": True,
        "fail_fast_enabled": True,
        "field_execution_performed": False,
        "authorization_consumed": False,
        "persistence_performed": False,
        "result_decision_permitted": False,
        "memory_claim_permitted": False,
    }
    return E1RepetitionPilotQuantitativeP0RunnerFixtureResult(
        **values,
        result_digest=_digest(values),
    )

