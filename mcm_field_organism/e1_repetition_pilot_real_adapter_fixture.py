"""S1-EC32 real six-role adapter exercised only on the small n2/r2 fixture."""

from __future__ import annotations

import copy
from dataclasses import dataclass

from .e1_confirmation_prepared_real_formation_kernel import (
    E1PreparedRealFormationArmResult,
    run_prepared_real_formation_arm_in_memory,
)
from .e1_local_edge_plasticity import E1LocalEdgePlasticityState
from .e1_refined_chain_canonical_producer import (
    _initial_field_digest,
    _initial_state_digest,
)
from .e1_refined_formation_runner import _digest
from .e1_repetition_formation_fixture_consumer import (
    _first_support_per_episode,
    _fixture_steps,
)
from .e1_repetition_formation_planner import E1RepetitionFormationPlanPair
from .e1_repetition_pilot_release_contract import S1_EC29_ARMS
from .neutral_asynchronous_field_runtime import run_neutral_asynchronous_field
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .shared_mcm_field import SharedMCMField


class E1RepetitionPilotRealAdapterFixtureError(ValueError):
    """Raised when the S1-EC32 fixture crosses the real-pilot boundary."""


S1_EC32_ADAPTER_ID = "e1.repetition-pilot-real-adapter-fixture.s1ec32.v1"
S1_EC32_CONTACT_COUNT = 2
S1_EC32_REFINEMENT_ID = "r2"
S1_EC32_STEP_COUNT_PER_ARM = 8
S1_EC32_TOTAL_FIELD_STEPS = 48
S1_EC32_ROLE_BINDINGS = (
    ("p0_repeated", "p0", "repeated", None),
    ("p0_continuous", "p0", "continuous", None),
    (
        "repeated_formation_ablated",
        "e1",
        "repeated",
        "ab_formation_ablated",
    ),
    (
        "continuous_formation_ablated",
        "e1",
        "continuous",
        "ba_formation_ablated",
    ),
    ("repeated_active", "e1", "repeated", "ab"),
    ("continuous_active", "e1", "continuous", "ba"),
)


@dataclass(frozen=True, slots=True)
class E1PilotRealAdapterArmReceipt:
    role_id: str
    kernel_kind: str
    schedule_kind: str
    internal_arm_id: str | None
    source_support_count: int
    field_step_count: int
    output_digest: str
    input_objects_preserved: bool
    copied_inputs_used: bool
    receipt_digest: str

    def __post_init__(self) -> None:
        bindings = {
            role: (kernel, schedule, arm)
            for role, kernel, schedule, arm in S1_EC32_ROLE_BINDINGS
        }
        if (
            self.role_id not in bindings
            or (self.kernel_kind, self.schedule_kind, self.internal_arm_id)
            != bindings[self.role_id]
            or self.source_support_count != 4
            or self.field_step_count != S1_EC32_STEP_COUNT_PER_ARM
            or len(self.output_digest) != 64
            or self.input_objects_preserved is not True
            or self.copied_inputs_used is not True
        ):
            raise E1RepetitionPilotRealAdapterFixtureError(
                "S1-EC32 arm receipt changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "receipt_digest"
        }
        if self.receipt_digest != _digest(payload):
            raise E1RepetitionPilotRealAdapterFixtureError(
                "S1-EC32 arm receipt digest changed"
            )


@dataclass(frozen=True, slots=True)
class E1RepetitionPilotRealAdapterFixtureResult:
    adapter_id: str
    source_pair_digest: str
    receipts: tuple[E1PilotRealAdapterArmReceipt, ...]
    role_order: tuple[str, ...]
    total_field_steps_executed: int
    p0_role_count: int
    formation_ablation_role_count: int
    active_e1_role_count: int
    source_pair_preserved: bool
    initial_inputs_preserved: bool
    six_role_adapter_implemented: bool
    full_pilot_executed: bool
    persistence_performed: bool
    result_decision_permitted: bool
    claims_permitted: bool
    result_digest: str

    def __post_init__(self) -> None:
        if (
            self.adapter_id != S1_EC32_ADAPTER_ID
            or len(self.source_pair_digest) != 64
            or self.role_order != S1_EC29_ARMS
            or tuple(item.role_id for item in self.receipts) != self.role_order
            or self.total_field_steps_executed != S1_EC32_TOTAL_FIELD_STEPS
            or self.p0_role_count != 2
            or self.formation_ablation_role_count != 2
            or self.active_e1_role_count != 2
            or any(
                value is not True
                for value in (
                    self.source_pair_preserved,
                    self.initial_inputs_preserved,
                    self.six_role_adapter_implemented,
                )
            )
            or any(
                value is not False
                for value in (
                    self.full_pilot_executed,
                    self.persistence_performed,
                    self.result_decision_permitted,
                    self.claims_permitted,
                )
            )
        ):
            raise E1RepetitionPilotRealAdapterFixtureError(
                "S1-EC32 adapter fixture boundary changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"receipts", "result_digest"}
        }
        payload["receipt_digests"] = tuple(
            (item.role_id, item.receipt_digest) for item in self.receipts
        )
        if self.result_digest != _digest(payload):
            raise E1RepetitionPilotRealAdapterFixtureError(
                "S1-EC32 adapter fixture digest changed"
            )


def _receipt(
    role_id: str,
    kernel_kind: str,
    schedule_kind: str,
    internal_arm_id: str | None,
    output_digest: str,
    preserved: bool,
) -> E1PilotRealAdapterArmReceipt:
    payload = {
        "role_id": role_id,
        "kernel_kind": kernel_kind,
        "schedule_kind": schedule_kind,
        "internal_arm_id": internal_arm_id,
        "source_support_count": 4,
        "field_step_count": S1_EC32_STEP_COUNT_PER_ARM,
        "output_digest": output_digest,
        "input_objects_preserved": preserved,
        "copied_inputs_used": True,
    }
    return E1PilotRealAdapterArmReceipt(
        **payload,
        receipt_digest=_digest(payload),
    )


def run_e1_repetition_pilot_real_adapter_fixture(
    pair: E1RepetitionFormationPlanPair,
    initial_field: SharedMCMField,
    initial_state: E1LocalEdgePlasticityState,
) -> E1RepetitionPilotRealAdapterFixtureResult:
    """Exercise all real role mappings without running the n1/n2 pilot."""

    if (
        not isinstance(pair, E1RepetitionFormationPlanPair)
        or pair.contact_count != S1_EC32_CONTACT_COUNT
        or not isinstance(initial_field, SharedMCMField)
        or not isinstance(initial_state, E1LocalEdgePlasticityState)
    ):
        raise E1RepetitionPilotRealAdapterFixtureError(
            "S1-EC32 requires one n2 pair and typed initial inputs"
        )
    pair.__post_init__()
    pair_digest = pair.pair_digest
    field_digest = _initial_field_digest(initial_field)
    state_digest = _initial_state_digest(initial_state)
    repeated = _first_support_per_episode(
        pair.repeated_sequences,
        (0, 2_000_000),
    )
    continuous = _first_support_per_episode(
        pair.continuous_sequences,
        (1_000_000, 2_000_000),
    )
    schedules = {"repeated": repeated, "continuous": continuous}
    steps = {
        name: _fixture_steps(sequences)
        for name, sequences in schedules.items()
    }
    receipts = []
    for role_id, kernel_kind, schedule_kind, internal_arm_id in S1_EC32_ROLE_BINDINGS:
        sequences = schedules[schedule_kind]
        proposal_steps = steps[schedule_kind]
        if kernel_kind == "p0":
            field_copy = copy.deepcopy(initial_field)
            run = run_neutral_asynchronous_field(
                field_copy,
                sequences,
                proposal_steps,
                NeutralLocalFieldSubstrateConfig(1.0),
                afterimage_config=NeutralFastAfterimageConfig(0.5),
            )
            output_digest = run.field.snapshot().digest()
            preserved = (
                run.source_support_count == 4
                and field_copy is not initial_field
                and _initial_field_digest(initial_field) == field_digest
                and _initial_state_digest(initial_state) == state_digest
            )
        else:
            enabled = role_id.endswith("_active")
            result = run_prepared_real_formation_arm_in_memory(
                internal_arm_id,
                S1_EC32_REFINEMENT_ID,
                sequences,
                proposal_steps,
                initial_field,
                initial_state,
                enabled,
            )
            if not isinstance(result, E1PreparedRealFormationArmResult):
                raise E1RepetitionPilotRealAdapterFixtureError(
                    "S1-EC32 E1 kernel returned no typed result"
                )
            output_digest = result.result_digest
            preserved = result.input_objects_preserved
        receipts.append(
            _receipt(
                role_id,
                kernel_kind,
                schedule_kind,
                internal_arm_id,
                output_digest,
                preserved,
            )
        )
    receipts_out = tuple(receipts)
    values = {
        "adapter_id": S1_EC32_ADAPTER_ID,
        "source_pair_digest": pair_digest,
        "role_order": tuple(item.role_id for item in receipts_out),
        "total_field_steps_executed": sum(
            item.field_step_count for item in receipts_out
        ),
        "p0_role_count": sum(item.kernel_kind == "p0" for item in receipts_out),
        "formation_ablation_role_count": sum(
            "formation_ablated" in item.role_id for item in receipts_out
        ),
        "active_e1_role_count": sum(
            item.role_id.endswith("_active") for item in receipts_out
        ),
        "source_pair_preserved": pair.pair_digest == pair_digest,
        "initial_inputs_preserved": (
            _initial_field_digest(initial_field) == field_digest
            and _initial_state_digest(initial_state) == state_digest
        ),
        "six_role_adapter_implemented": True,
        "full_pilot_executed": False,
        "persistence_performed": False,
        "result_decision_permitted": False,
        "claims_permitted": False,
    }
    payload = dict(values)
    payload["receipt_digests"] = tuple(
        (item.role_id, item.receipt_digest) for item in receipts_out
    )
    return E1RepetitionPilotRealAdapterFixtureResult(
        **values,
        receipts=receipts_out,
        result_digest=_digest(payload),
    )
