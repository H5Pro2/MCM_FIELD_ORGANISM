"""S1-EC40 small real n2/r2 quantitative P0 handoff fixture."""

from __future__ import annotations

import copy
from dataclasses import dataclass

from .e1_refined_chain_canonical_producer import _initial_field_digest
from .e1_refined_formation_runner import _digest
from .e1_repetition_formation_fixture_consumer import (
    _first_support_per_episode,
    _fixture_steps,
)
from .e1_repetition_formation_planner import E1RepetitionFormationPlanPair
from .e1_repetition_pilot_quantitative_p0_schema import (
    E1PilotQuantitativeP0Pair,
    collect_quantitative_p0_pair,
)
from .e1_repetition_pilot_quantitative_real_preflight import (
    E1RepetitionPilotQuantitativeRealPreflight,
)
from .neutral_asynchronous_field_runtime import run_neutral_asynchronous_field
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .shared_mcm_field import SharedMCMField


class E1RepetitionPilotQuantitativeRealHandoffFixtureError(ValueError):
    """Raised when S1-EC40 crosses its small real P0 fixture boundary."""


S1_EC40_FIXTURE_ID = "e1.repetition-pilot-quantitative-real-handoff.s1ec40.v1"
S1_EC40_EC39_PREFLIGHT_DIGEST = (
    "9a0d128b20e5fc39c9efb378c1180a92c5f58f4bc3e81b110f89bb5faa618313"
)
S1_EC40_CONTACT_COUNT = 2
S1_EC40_REFINEMENT_ID = "r2"
S1_EC40_SUPPORTS_PER_ARM = 4
S1_EC40_STEPS_PER_ARM = 8
S1_EC40_TOTAL_FIELD_STEPS = 16


@dataclass(frozen=True, slots=True)
class E1RepetitionPilotQuantitativeRealHandoffFixtureResult:
    fixture_id: str
    source_pair_digest: str
    source_preflight_digest: str
    quantitative_pair: E1PilotQuantitativeP0Pair
    repeated_snapshot_digest: str
    continuous_snapshot_digest: str
    source_support_count_per_arm: int
    field_step_count_per_arm: int
    total_field_steps_executed: int
    snapshot_objects_separated: bool
    snapshots_collected_before_field_discard: bool
    initial_field_preserved: bool
    source_pair_preserved: bool
    real_quantitative_handoff_implemented: bool
    full_pilot_executed: bool
    authorization_consumed: bool
    persistence_performed: bool
    result_decision_permitted: bool
    memory_claim_permitted: bool
    result_digest: str

    def __post_init__(self) -> None:
        if (
            self.fixture_id != S1_EC40_FIXTURE_ID
            or len(self.source_pair_digest) != 64
            or self.source_preflight_digest != S1_EC40_EC39_PREFLIGHT_DIGEST
            or not isinstance(self.quantitative_pair, E1PilotQuantitativeP0Pair)
            or self.quantitative_pair.contact_count != S1_EC40_CONTACT_COUNT
            or self.quantitative_pair.refinement_id != S1_EC40_REFINEMENT_ID
            or self.repeated_snapshot_digest
            != self.quantitative_pair.repeated_snapshot_digest
            or self.continuous_snapshot_digest
            != self.quantitative_pair.continuous_snapshot_digest
            or self.source_support_count_per_arm != S1_EC40_SUPPORTS_PER_ARM
            or self.field_step_count_per_arm != S1_EC40_STEPS_PER_ARM
            or self.total_field_steps_executed != S1_EC40_TOTAL_FIELD_STEPS
            or any(
                value is not True
                for value in (
                    self.snapshot_objects_separated,
                    self.snapshots_collected_before_field_discard,
                    self.initial_field_preserved,
                    self.source_pair_preserved,
                    self.real_quantitative_handoff_implemented,
                )
            )
            or any(
                value is not False
                for value in (
                    self.full_pilot_executed,
                    self.authorization_consumed,
                    self.persistence_performed,
                    self.result_decision_permitted,
                    self.memory_claim_permitted,
                )
            )
        ):
            raise E1RepetitionPilotQuantitativeRealHandoffFixtureError(
                "S1-EC40 fixture changed or crossed its boundary"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"quantitative_pair", "result_digest"}
        }
        payload["quantitative_pair_digest"] = self.quantitative_pair.pair_digest
        if self.result_digest != _digest(payload):
            raise E1RepetitionPilotQuantitativeRealHandoffFixtureError(
                "S1-EC40 result digest changed"
            )


def run_quantitative_real_p0_handoff_fixture(
    preflight: E1RepetitionPilotQuantitativeRealPreflight,
    pair: E1RepetitionFormationPlanPair,
    initial_field: SharedMCMField,
) -> E1RepetitionPilotQuantitativeRealHandoffFixtureResult:
    """Run two small P0 arms and immediately collect their snapshots."""

    if not isinstance(preflight, E1RepetitionPilotQuantitativeRealPreflight):
        raise E1RepetitionPilotQuantitativeRealHandoffFixtureError(
            "S1-EC40 requires the exact EC39 preflight"
        )
    if (
        not isinstance(pair, E1RepetitionFormationPlanPair)
        or pair.contact_count != S1_EC40_CONTACT_COUNT
        or not isinstance(initial_field, SharedMCMField)
    ):
        raise E1RepetitionPilotQuantitativeRealHandoffFixtureError(
            "S1-EC40 requires one n2 pair and one initial field"
        )
    preflight.__post_init__()
    pair.__post_init__()
    if (
        preflight.preflight_digest != S1_EC40_EC39_PREFLIGHT_DIGEST
        or preflight.real_runner_implementation_permitted is not True
        or preflight.pilot_execution_permitted is not False
    ):
        raise E1RepetitionPilotQuantitativeRealHandoffFixtureError(
            "S1-EC40 preflight binding changed"
        )
    source_pair_digest = pair.pair_digest
    initial_digest = _initial_field_digest(initial_field)
    repeated_sequences = _first_support_per_episode(
        pair.repeated_sequences,
        (0, 2_000_000),
    )
    continuous_sequences = _first_support_per_episode(
        pair.continuous_sequences,
        (1_000_000, 2_000_000),
    )
    repeated_steps = _fixture_steps(repeated_sequences)
    continuous_steps = _fixture_steps(continuous_sequences)
    repeated_field = copy.deepcopy(initial_field)
    continuous_field = copy.deepcopy(initial_field)
    repeated_run = run_neutral_asynchronous_field(
        repeated_field,
        repeated_sequences,
        repeated_steps,
        NeutralLocalFieldSubstrateConfig(1.0),
        afterimage_config=NeutralFastAfterimageConfig(0.5),
    )
    continuous_run = run_neutral_asynchronous_field(
        continuous_field,
        continuous_sequences,
        continuous_steps,
        NeutralLocalFieldSubstrateConfig(1.0),
        afterimage_config=NeutralFastAfterimageConfig(0.5),
    )
    repeated_snapshot = repeated_run.field.snapshot()
    continuous_snapshot = continuous_run.field.snapshot()
    quantitative_pair = collect_quantitative_p0_pair(
        S1_EC40_CONTACT_COUNT,
        S1_EC40_REFINEMENT_ID,
        repeated_snapshot,
        continuous_snapshot,
    )
    values = {
        "fixture_id": S1_EC40_FIXTURE_ID,
        "source_pair_digest": source_pair_digest,
        "source_preflight_digest": preflight.preflight_digest,
        "repeated_snapshot_digest": repeated_snapshot.digest(),
        "continuous_snapshot_digest": continuous_snapshot.digest(),
        "source_support_count_per_arm": repeated_run.source_support_count,
        "field_step_count_per_arm": len(repeated_steps),
        "total_field_steps_executed": len(repeated_steps) + len(continuous_steps),
        "snapshot_objects_separated": repeated_snapshot is not continuous_snapshot,
        "snapshots_collected_before_field_discard": True,
        "initial_field_preserved": _initial_field_digest(initial_field)
        == initial_digest,
        "source_pair_preserved": pair.pair_digest == source_pair_digest,
        "real_quantitative_handoff_implemented": True,
        "full_pilot_executed": False,
        "authorization_consumed": False,
        "persistence_performed": False,
        "result_decision_permitted": False,
        "memory_claim_permitted": False,
    }
    if continuous_run.source_support_count != S1_EC40_SUPPORTS_PER_ARM:
        raise E1RepetitionPilotQuantitativeRealHandoffFixtureError(
            "S1-EC40 continuous support count changed"
        )
    payload = dict(values)
    payload["quantitative_pair_digest"] = quantitative_pair.pair_digest
    return E1RepetitionPilotQuantitativeRealHandoffFixtureResult(
        **values,
        quantitative_pair=quantitative_pair,
        result_digest=_digest(payload),
    )

