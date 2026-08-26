"""Private finite S1-YB PPB-1 temporal-update comparison runner."""

from __future__ import annotations

from dataclasses import dataclass
import math
import re

from ._ppb1_reference import (
    PPB1BankConfig,
    PPB1BankState,
    _digest,
    initial_ppb1_bank_state,
)
from ._ppb1_s1wq_perceptual_state_lifecycle import (
    _state_identity_payload,
    advance_s1wq_perceptual_state,
)
from ._ppb1_s1wu_read_only_perceptual_probe import (
    probe_s1wu_perceptual_state,
)
from ._ppb1_s1xz_private_temporal_update_fixture import (
    S1XZHistoryPlan,
    S1XZModalityFixture,
    build_s1xz_temporal_update_fixture,
)
from ._ppb1_s1ya_private_static_prototype_baseline import (
    S1YAFrozenBaselineCarry,
    form_s1ya_static_baseline,
    receive_s1ya_frozen_exposure,
)
from .receptor_contract import ReceptorContactFrame


S1YB_SCHEMA_VERSION = "ppb1.s1yb.private-temporal-update-runner.v1"
S1YB_PREFLIGHT_DIGEST = (
    "1bf316628b75ca6ee11fb05f290713b30b758c7a35b9cb9ede19b3142c577d06"
)
S1YB_FIXTURE_BUNDLE_DIGEST = (
    "0aac41828eb64ba0f2dfc8488ba6d9c1c636998cb66023ad6bc488a0671bbadb"
)
S1YB_PASS = "TEMPORAL_UPDATE_SYNTHETIC_FUNCTION_VALID_AGAINST_STATIC_PROTOTYPE"
S1YB_FAIL = "TEMPORAL_UPDATE_SYNTHETIC_FUNCTION_FAIL"
S1YB_INVALID = "S1YB_INVALID_TEMPORAL_UPDATE_RUN"

_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_MANDATORY_ADVANTAGE = {
    ("H2", "gradual_3"),
    ("H3", "conflict_b"),
    ("H4", "origin"),
    ("H4", "opposite_c"),
    ("H5", "gradual_3"),
}
_NEGATIVE_CONTROLS = {
    ("H1", "conflict_b"),
    ("H2", "conflict_b"),
    ("H3", "opposite_c"),
    ("H4", "far_control"),
    ("H5", "conflict_b"),
}


class S1YBTemporalUpdateRunnerError(ValueError):
    """One fail-closed private runner violation."""

    def __init__(self, detail: str) -> None:
        self.code = S1YB_INVALID
        self.detail = detail
        super().__init__(f"{self.code}: {detail}")


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


def _receipt_digest(payload: dict[str, object]) -> str:
    return _digest(
        {
            "schema_version": S1YB_SCHEMA_VERSION,
            "preflight_digest": S1YB_PREFLIGHT_DIGEST,
            "fixture_bundle_digest": S1YB_FIXTURE_BUNDLE_DIGEST,
            **payload,
        }
    )


def _value_map(modality: S1XZModalityFixture) -> dict[str, float]:
    return dict(modality.named_scalar_values)


def _candidate_config(
    modality: S1XZModalityFixture,
    plan: S1XZHistoryPlan,
) -> PPB1BankConfig:
    prefix = f"s1yb.candidate.{modality.modality_id}.{plan.history_id.lower()}"
    return PPB1BankConfig(
        f"ppb1.{prefix}",
        modality.modality_id,
        f"geometry.{prefix}",
        tuple(
            f"carrier.{prefix}.{index:03d}"
            for index in range(modality.carrier_count)
        ),
        modality.capacity,
        modality.match_threshold,
        modality.update_rate,
        modality.stable_after,
        modality.expire_after_steps,
    )


def _frame(
    config: PPB1BankConfig,
    history_id: str,
    role: str,
    scalar: float,
    start_tick: int,
    arm: str,
) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        config.modality_id,
        config.geometry_id,
        f"receptor.s1yb.{arm}.{config.modality_id}.{history_id.lower()}.{role}",
        f"clock.s1yb.{arm}.{config.modality_id}.{history_id.lower()}",
        start_tick,
        start_tick + 1,
        config.carrier_ids,
        (scalar,) * len(config.carrier_ids),
    )


def _baseline_frame(
    carry: S1YAFrozenBaselineCarry,
    role: str,
    scalar: float,
) -> ReceptorContactFrame:
    config = carry.config
    history = carry.plan_id.rsplit(".", 1)[-1]
    start = carry.last_received_window_end_tick
    return ReceptorContactFrame(
        config.modality_id,
        config.geometry_id,
        f"receptor.s1ya.{config.modality_id}.{history}.{role}",
        f"clock.s1ya.{config.modality_id}.{history}",
        start,
        start + 1,
        config.carrier_ids,
        (scalar,) * len(config.carrier_ids),
    )


def _baseline_probe_frame(
    carry: S1YAFrozenBaselineCarry,
    history_id: str,
    role: str,
    scalar: float,
    start_tick: int,
) -> ReceptorContactFrame:
    config = carry.config
    if carry.frozen_state.source_clock_id is None:
        raise S1YBTemporalUpdateRunnerError("baseline source clock is not bound")
    return ReceptorContactFrame(
        config.modality_id,
        config.geometry_id,
        f"receptor.s1yb.baseline.{config.modality_id}.{history_id.lower()}.{role}",
        carry.frozen_state.source_clock_id,
        start_tick,
        start_tick + 1,
        config.carrier_ids,
        (scalar,) * len(config.carrier_ids),
    )


def _stable_prototypes(
    config: PPB1BankConfig,
    state: PPB1BankState,
) -> tuple[tuple[float, ...], ...]:
    return tuple(
        slot.prototype_values
        for slot in state.slots
        if (
            slot.occupied
            and slot.support_count is not None
            and slot.support_count >= config.stable_after
        )
    )


def _relation(
    candidate_recognized: bool,
    baseline_recognized: bool,
    candidate_distance: float,
    baseline_distance: float,
) -> str:
    if candidate_recognized != baseline_recognized:
        return "STRICT_ADVANTAGE"
    if not candidate_recognized:
        return "TIE"
    if candidate_distance < baseline_distance:
        return "STRICT_ADVANTAGE"
    if candidate_distance > baseline_distance:
        return "DIAGNOSTIC_LOSS"
    return "TIE"


@dataclass(frozen=True, slots=True)
class S1YBPairedProbeReceipt:
    cell_id: str
    plan_id: str
    plan_digest: str
    modality_id: str
    history_id: str
    probe_role: str
    candidate_finding_digest: str
    baseline_finding_digest: str
    candidate_recognized: bool
    baseline_recognized: bool
    candidate_distance: float
    baseline_distance: float
    expected_candidate_recognized: bool
    expected_baseline_recognized: bool
    expected_candidate_distance: float
    expected_baseline_distance: float
    candidate_state_unchanged: bool
    baseline_state_unchanged: bool
    relation: str
    matches_fixture: bool
    paired_receipt_digest: str

    def __post_init__(self) -> None:
        distances = (
            self.candidate_distance,
            self.baseline_distance,
            self.expected_candidate_distance,
            self.expected_baseline_distance,
        )
        expected_id = (
            f"s1yb.{self.modality_id}.{self.history_id.lower()}.{self.probe_role}"
        )
        if (
            self.cell_id != expected_id
            or not self.plan_id.startswith("s1xz.")
            or not all(
                _valid_digest(value)
                for value in (
                    self.plan_digest,
                    self.candidate_finding_digest,
                    self.baseline_finding_digest,
                )
            )
            or self.modality_id not in {"auditory", "visual"}
            or self.history_id not in {"H1", "H2", "H3", "H4", "H5"}
            or not self.probe_role
            or any(
                isinstance(value, bool)
                or not isinstance(value, float)
                or not math.isfinite(value)
                or value < 0.0
                for value in distances
            )
            or not all(
                isinstance(value, bool)
                for value in (
                    self.candidate_recognized,
                    self.baseline_recognized,
                    self.expected_candidate_recognized,
                    self.expected_baseline_recognized,
                    self.candidate_state_unchanged,
                    self.baseline_state_unchanged,
                    self.matches_fixture,
                )
            )
            or self.relation
            not in {"STRICT_ADVANTAGE", "TIE", "DIAGNOSTIC_LOSS"}
            or not self.candidate_state_unchanged
            or not self.baseline_state_unchanged
            or self.paired_receipt_digest
            != _receipt_digest(self.payload_without_digest())
        ):
            raise S1YBTemporalUpdateRunnerError("invalid paired probe receipt")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "cell_id": self.cell_id,
            "plan_id": self.plan_id,
            "plan_digest": self.plan_digest,
            "modality_id": self.modality_id,
            "history_id": self.history_id,
            "probe_role": self.probe_role,
            "candidate_finding_digest": self.candidate_finding_digest,
            "baseline_finding_digest": self.baseline_finding_digest,
            "candidate_recognized": self.candidate_recognized,
            "baseline_recognized": self.baseline_recognized,
            "candidate_distance": self.candidate_distance,
            "baseline_distance": self.baseline_distance,
            "expected_candidate_recognized": self.expected_candidate_recognized,
            "expected_baseline_recognized": self.expected_baseline_recognized,
            "expected_candidate_distance": self.expected_candidate_distance,
            "expected_baseline_distance": self.expected_baseline_distance,
            "candidate_state_unchanged": self.candidate_state_unchanged,
            "baseline_state_unchanged": self.baseline_state_unchanged,
            "relation": self.relation,
            "matches_fixture": self.matches_fixture,
        }


@dataclass(frozen=True, slots=True)
class S1YBHistoryReceipt:
    plan_id: str
    plan_digest: str
    modality_id: str
    history_id: str
    candidate_config_digest: str
    baseline_config_digest: str
    candidate_preupdate_state_digest: str
    baseline_frozen_state_digest: str
    preupdate_behavior_equal: bool
    candidate_terminal_state_digest: str
    baseline_terminal_state_digest: str
    candidate_state_identity_digest: str
    baseline_state_identity_digest: str
    ordered_candidate_transition_digests: tuple[str, ...]
    ordered_baseline_formation_transition_digests: tuple[str, ...]
    ordered_frozen_exposure_receipt_digests: tuple[str, ...]
    ordered_paired_probe_receipt_digests: tuple[str, ...]
    target_policy_satisfied: bool
    negative_control_safe: bool
    all_probe_states_unchanged: bool
    decision: str
    history_receipt_digest: str

    def __post_init__(self) -> None:
        digest_groups = (
            self.candidate_config_digest,
            self.baseline_config_digest,
            self.candidate_preupdate_state_digest,
            self.baseline_frozen_state_digest,
            self.candidate_terminal_state_digest,
            self.baseline_terminal_state_digest,
            self.candidate_state_identity_digest,
            self.baseline_state_identity_digest,
            *self.ordered_candidate_transition_digests,
            *self.ordered_baseline_formation_transition_digests,
            *self.ordered_frozen_exposure_receipt_digests,
            *self.ordered_paired_probe_receipt_digests,
        )
        expected_decision = (
            "HISTORY_VALID_EXPECTED_BEHAVIOR"
            if self.preupdate_behavior_equal
            and self.target_policy_satisfied
            and self.negative_control_safe
            and self.all_probe_states_unchanged
            else "HISTORY_FAIL"
        )
        if (
            not self.plan_id.startswith("s1xz.")
            or not _valid_digest(self.plan_digest)
            or not all(_valid_digest(value) for value in digest_groups)
            or not self.ordered_candidate_transition_digests
            or not self.ordered_baseline_formation_transition_digests
            or not self.ordered_paired_probe_receipt_digests
            or self.decision != expected_decision
            or self.history_receipt_digest
            != _receipt_digest(self.payload_without_digest())
        ):
            raise S1YBTemporalUpdateRunnerError("invalid history receipt")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "plan_id": self.plan_id,
            "plan_digest": self.plan_digest,
            "modality_id": self.modality_id,
            "history_id": self.history_id,
            "candidate_config_digest": self.candidate_config_digest,
            "baseline_config_digest": self.baseline_config_digest,
            "candidate_preupdate_state_digest": self.candidate_preupdate_state_digest,
            "baseline_frozen_state_digest": self.baseline_frozen_state_digest,
            "preupdate_behavior_equal": self.preupdate_behavior_equal,
            "candidate_terminal_state_digest": self.candidate_terminal_state_digest,
            "baseline_terminal_state_digest": self.baseline_terminal_state_digest,
            "candidate_state_identity_digest": self.candidate_state_identity_digest,
            "baseline_state_identity_digest": self.baseline_state_identity_digest,
            "ordered_candidate_transition_digests": list(
                self.ordered_candidate_transition_digests
            ),
            "ordered_baseline_formation_transition_digests": list(
                self.ordered_baseline_formation_transition_digests
            ),
            "ordered_frozen_exposure_receipt_digests": list(
                self.ordered_frozen_exposure_receipt_digests
            ),
            "ordered_paired_probe_receipt_digests": list(
                self.ordered_paired_probe_receipt_digests
            ),
            "target_policy_satisfied": self.target_policy_satisfied,
            "negative_control_safe": self.negative_control_safe,
            "all_probe_states_unchanged": self.all_probe_states_unchanged,
            "decision": self.decision,
        }


@dataclass(frozen=True, slots=True)
class S1YBAggregateReceipt:
    fixture_bundle_digest: str
    ordered_history_receipt_digests: tuple[str, ...]
    paired_probe_count: int
    candidate_transition_count: int
    baseline_formation_transition_count: int
    frozen_baseline_handoff_count: int
    candidate_probe_count: int
    baseline_probe_count: int
    strict_advantage_count: int
    diagnostic_loss_count: int
    tie_count: int
    mandatory_advantage_count: int
    negative_control_safe_count: int
    all_histories_valid: bool
    decision: str
    aggregate_receipt_digest: str

    def __post_init__(self) -> None:
        expected_decision = S1YB_PASS if self.all_histories_valid else S1YB_FAIL
        if (
            self.fixture_bundle_digest != S1YB_FIXTURE_BUNDLE_DIGEST
            or len(self.ordered_history_receipt_digests) != 10
            or not all(
                _valid_digest(value) for value in self.ordered_history_receipt_digests
            )
            or self.paired_probe_count != 32
            or self.candidate_transition_count != 64
            or self.baseline_formation_transition_count != 36
            or self.frozen_baseline_handoff_count != 28
            or self.candidate_probe_count != 32
            or self.baseline_probe_count != 32
            or self.strict_advantage_count != 14
            or self.diagnostic_loss_count != 4
            or self.tie_count != 14
            or self.mandatory_advantage_count != 10
            or self.negative_control_safe_count != 10
            or self.decision != expected_decision
            or self.aggregate_receipt_digest
            != _receipt_digest(self.payload_without_digest())
        ):
            raise S1YBTemporalUpdateRunnerError("invalid aggregate receipt")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "fixture_bundle_digest": self.fixture_bundle_digest,
            "ordered_history_receipt_digests": list(
                self.ordered_history_receipt_digests
            ),
            "paired_probe_count": self.paired_probe_count,
            "candidate_transition_count": self.candidate_transition_count,
            "baseline_formation_transition_count": (
                self.baseline_formation_transition_count
            ),
            "frozen_baseline_handoff_count": self.frozen_baseline_handoff_count,
            "candidate_probe_count": self.candidate_probe_count,
            "baseline_probe_count": self.baseline_probe_count,
            "strict_advantage_count": self.strict_advantage_count,
            "diagnostic_loss_count": self.diagnostic_loss_count,
            "tie_count": self.tie_count,
            "mandatory_advantage_count": self.mandatory_advantage_count,
            "negative_control_safe_count": self.negative_control_safe_count,
            "all_histories_valid": self.all_histories_valid,
            "decision": self.decision,
        }


@dataclass(frozen=True, slots=True)
class S1YBRunResult:
    history_receipts: tuple[S1YBHistoryReceipt, ...]
    paired_probe_receipts: tuple[S1YBPairedProbeReceipt, ...]
    aggregate_receipt: S1YBAggregateReceipt

    def __post_init__(self) -> None:
        if (
            tuple(item.history_receipt_digest for item in self.history_receipts)
            != self.aggregate_receipt.ordered_history_receipt_digests
            or len(self.paired_probe_receipts) != self.aggregate_receipt.paired_probe_count
        ):
            raise S1YBTemporalUpdateRunnerError("run result is not atomic")


def _run_history(
    modality: S1XZModalityFixture,
    plan: S1XZHistoryPlan,
) -> tuple[S1YBHistoryReceipt, tuple[S1YBPairedProbeReceipt, ...]]:
    values = _value_map(modality)
    candidate_config = _candidate_config(modality, plan)
    candidate_state = initial_ppb1_bank_state(candidate_config)
    candidate_transitions = []
    candidate_events = []
    for index, role in enumerate(plan.formation_roles):
        step = advance_s1wq_perceptual_state(
            candidate_config,
            candidate_state,
            _frame(
                candidate_config,
                plan.history_id,
                role,
                values[role],
                index,
                "candidate",
            ),
        )
        candidate_state = step.poststate
        candidate_transitions.append(step.transition)
        candidate_events.append(step.reference_readout.event)

    baseline = form_s1ya_static_baseline(modality, plan)
    candidate_preupdate_digest = candidate_state.digest()
    preupdate_equal = (
        _stable_prototypes(candidate_config, candidate_state)
        == _stable_prototypes(baseline.config, baseline.carry.frozen_state)
        and _stable_prototypes(candidate_config, candidate_state)
        == tuple(
            (value,) * modality.carrier_count
            for value in plan.expected_baseline_prototypes
        )
    )
    if not preupdate_equal:
        raise S1YBTemporalUpdateRunnerError(
            "candidate and baseline are not behaviorally equal before update"
        )

    baseline_carry = baseline.carry
    frozen_exposure_receipts = []
    start = len(plan.formation_roles)
    for offset, role in enumerate(plan.update_roles):
        candidate_step = advance_s1wq_perceptual_state(
            candidate_config,
            candidate_state,
            _frame(
                candidate_config,
                plan.history_id,
                role,
                values[role],
                start + offset,
                "candidate",
            ),
        )
        candidate_state = candidate_step.poststate
        candidate_transitions.append(candidate_step.transition)
        candidate_events.append(candidate_step.reference_readout.event)
        baseline_step = receive_s1ya_frozen_exposure(
            baseline_carry,
            _baseline_frame(baseline_carry, role, values[role]),
            role,
        )
        baseline_carry = baseline_step.carry
        frozen_exposure_receipts.append(baseline_step.receipt)

    candidate_terminal_digest = candidate_state.digest()
    candidate_identity = _digest(_state_identity_payload(candidate_state))
    if (
        tuple(candidate_events) != plan.expected_candidate_events
        or _stable_prototypes(candidate_config, candidate_state)
        != tuple(
            (value,) * modality.carrier_count
            for value in plan.expected_candidate_prototypes
        )
        or baseline_carry.frozen_state_digest != baseline.carry.frozen_state_digest
    ):
        raise S1YBTemporalUpdateRunnerError(
            "terminal candidate or frozen baseline differs from fixture"
        )

    cells = []
    probe_start = start + len(plan.update_roles) + plan.separation_ticks
    for index, role in enumerate(plan.ordered_probe_roles):
        candidate_before = candidate_state.digest()
        baseline_before = baseline_carry.frozen_state.digest()
        candidate_finding = probe_s1wu_perceptual_state(
            candidate_config,
            candidate_state,
            _frame(
                candidate_config,
                plan.history_id,
                role,
                values[role],
                probe_start + index,
                "candidate",
            ),
            f"probe.s1yb.candidate.{modality.modality_id}.{plan.history_id.lower()}.{role}",
        )
        baseline_finding = probe_s1wu_perceptual_state(
            baseline.config,
            baseline_carry.frozen_state,
            _baseline_probe_frame(
                baseline_carry,
                plan.history_id,
                role,
                values[role],
                probe_start + index,
            ),
            f"probe.s1yb.baseline.{modality.modality_id}.{plan.history_id.lower()}.{role}",
        )
        if candidate_finding.match_distance is None or baseline_finding.match_distance is None:
            raise S1YBTemporalUpdateRunnerError("all bound probes require stable slots")
        candidate_unchanged = candidate_state.digest() == candidate_before
        baseline_unchanged = baseline_carry.frozen_state.digest() == baseline_before
        matches = (
            candidate_finding.recognized == plan.expected_candidate_recognition[index]
            and baseline_finding.recognized == plan.expected_baseline_recognition[index]
            and candidate_finding.match_distance
            == plan.expected_candidate_probe_distances[index]
            and baseline_finding.match_distance
            == plan.expected_baseline_probe_distances[index]
        )
        relation = _relation(
            candidate_finding.recognized,
            baseline_finding.recognized,
            candidate_finding.match_distance,
            baseline_finding.match_distance,
        )
        cell_values = {
            "cell_id": f"s1yb.{modality.modality_id}.{plan.history_id.lower()}.{role}",
            "plan_id": plan.plan_id,
            "plan_digest": plan.plan_digest,
            "modality_id": modality.modality_id,
            "history_id": plan.history_id,
            "probe_role": role,
            "candidate_finding_digest": candidate_finding.finding_digest,
            "baseline_finding_digest": baseline_finding.finding_digest,
            "candidate_recognized": candidate_finding.recognized,
            "baseline_recognized": baseline_finding.recognized,
            "candidate_distance": candidate_finding.match_distance,
            "baseline_distance": baseline_finding.match_distance,
            "expected_candidate_recognized": plan.expected_candidate_recognition[index],
            "expected_baseline_recognized": plan.expected_baseline_recognition[index],
            "expected_candidate_distance": plan.expected_candidate_probe_distances[index],
            "expected_baseline_distance": plan.expected_baseline_probe_distances[index],
            "candidate_state_unchanged": candidate_unchanged,
            "baseline_state_unchanged": baseline_unchanged,
            "relation": relation,
            "matches_fixture": matches,
        }
        cells.append(
            S1YBPairedProbeReceipt(
                **cell_values,
                paired_receipt_digest=_receipt_digest(cell_values),
            )
        )

    mandatory = [
        item
        for item in cells
        if (item.history_id, item.probe_role) in _MANDATORY_ADVANTAGE
    ]
    controls = [
        item
        for item in cells
        if (item.history_id, item.probe_role) in _NEGATIVE_CONTROLS
    ]
    target_policy_satisfied = (
        all(item.matches_fixture for item in cells)
        and all(item.relation == "STRICT_ADVANTAGE" for item in mandatory)
    )
    negative_safe = all(
        not item.candidate_recognized and not item.baseline_recognized
        for item in controls
    )
    all_unchanged = all(
        item.candidate_state_unchanged and item.baseline_state_unchanged
        for item in cells
    )
    history_decision = (
        "HISTORY_VALID_EXPECTED_BEHAVIOR"
        if preupdate_equal and target_policy_satisfied and negative_safe and all_unchanged
        else "HISTORY_FAIL"
    )
    history_values = {
        "plan_id": plan.plan_id,
        "plan_digest": plan.plan_digest,
        "modality_id": modality.modality_id,
        "history_id": plan.history_id,
        "candidate_config_digest": candidate_config.digest(),
        "baseline_config_digest": baseline.config.digest(),
        "candidate_preupdate_state_digest": candidate_preupdate_digest,
        "baseline_frozen_state_digest": baseline.carry.frozen_state_digest,
        "preupdate_behavior_equal": preupdate_equal,
        "candidate_terminal_state_digest": candidate_terminal_digest,
        "baseline_terminal_state_digest": baseline_carry.frozen_state_digest,
        "candidate_state_identity_digest": candidate_identity,
        "baseline_state_identity_digest": baseline_carry.state_identity_digest,
        "ordered_candidate_transition_digests": tuple(
            item.record_digest for item in candidate_transitions
        ),
        "ordered_baseline_formation_transition_digests": tuple(
            item.record_digest for item in baseline.formation_transitions
        ),
        "ordered_frozen_exposure_receipt_digests": tuple(
            item.exposure_receipt_digest for item in frozen_exposure_receipts
        ),
        "ordered_paired_probe_receipt_digests": tuple(
            item.paired_receipt_digest for item in cells
        ),
        "target_policy_satisfied": target_policy_satisfied,
        "negative_control_safe": negative_safe,
        "all_probe_states_unchanged": all_unchanged,
        "decision": history_decision,
    }
    return (
        S1YBHistoryReceipt(
            **history_values,
            history_receipt_digest=_receipt_digest(history_values),
        ),
        tuple(cells),
    )


def run_s1yb_private_temporal_update_comparison() -> S1YBRunResult:
    """Run exactly the ten private synthetic candidate/baseline histories."""

    fixture = build_s1xz_temporal_update_fixture()
    if fixture.bundle_digest != S1YB_FIXTURE_BUNDLE_DIGEST:
        raise S1YBTemporalUpdateRunnerError("fixture bundle digest drift")
    modality_map = {item.modality_id: item for item in fixture.modalities}
    results = tuple(
        _run_history(modality_map[plan.modality_id], plan)
        for plan in fixture.history_plans
    )
    histories = tuple(item[0] for item in results)
    cells = tuple(cell for item in results for cell in item[1])
    strict_count = sum(item.relation == "STRICT_ADVANTAGE" for item in cells)
    loss_count = sum(item.relation == "DIAGNOSTIC_LOSS" for item in cells)
    tie_count = sum(item.relation == "TIE" for item in cells)
    mandatory_count = sum(
        item.relation == "STRICT_ADVANTAGE"
        and (item.history_id, item.probe_role) in _MANDATORY_ADVANTAGE
        for item in cells
    )
    control_count = sum(
        not item.candidate_recognized
        and not item.baseline_recognized
        and (item.history_id, item.probe_role) in _NEGATIVE_CONTROLS
        for item in cells
    )
    all_valid = (
        all(item.decision == "HISTORY_VALID_EXPECTED_BEHAVIOR" for item in histories)
        and mandatory_count == 10
        and control_count == 10
    )
    values = {
        "fixture_bundle_digest": fixture.bundle_digest,
        "ordered_history_receipt_digests": tuple(
            item.history_receipt_digest for item in histories
        ),
        "paired_probe_count": len(cells),
        "candidate_transition_count": sum(
            len(item.ordered_candidate_transition_digests) for item in histories
        ),
        "baseline_formation_transition_count": sum(
            len(item.ordered_baseline_formation_transition_digests)
            for item in histories
        ),
        "frozen_baseline_handoff_count": sum(
            len(item.ordered_frozen_exposure_receipt_digests) for item in histories
        ),
        "candidate_probe_count": len(cells),
        "baseline_probe_count": len(cells),
        "strict_advantage_count": strict_count,
        "diagnostic_loss_count": loss_count,
        "tie_count": tie_count,
        "mandatory_advantage_count": mandatory_count,
        "negative_control_safe_count": control_count,
        "all_histories_valid": all_valid,
        "decision": S1YB_PASS if all_valid else S1YB_FAIL,
    }
    aggregate = S1YBAggregateReceipt(
        **values,
        aggregate_receipt_digest=_receipt_digest(values),
    )
    return S1YBRunResult(histories, cells, aggregate)
