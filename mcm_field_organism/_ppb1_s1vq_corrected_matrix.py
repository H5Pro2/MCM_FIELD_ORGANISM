"""Private S1-VQ identity carry and execution-locked corrected PPB-1 plan."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re

from ._ppb1_reference import PPB1BankConfig, normalized_mean_l1_distance
from ._ppb1_s1vn_matrix import (
    S1VN_BASELINE_IDS,
    S1VN_FAMILY_IDS,
    S1VN_FIXTURE_IDS,
    S1VN_MODALITY_IDS,
    S1VN_PARAMETER_IDS,
    S1VNBaselineReadout,
    S1VNBaselineState,
    S1VNCaseReceipt,
    S1VNMatrixError,
    S1VNStepObservation,
    _execute_frames,
    advance_s1vn_baseline,
    build_s1vn_fixture,
    initial_s1vn_baseline_state,
    prepare_s1vn_matrix_runner,
    s1vn_config,
    s1vn_matrix_plan,
)
from .receptor_contract import ReceptorContactFrame


S1VQ_SCHEMA_VERSION = "ppb1.s1vq.private.v1"
S1VQ_PARENT_PLAN_DIGEST = (
    "35c1e589f749f1c1f1f24900f611fd43f8329d803a4b82ca94584d1925067ba3"
)
S1VQ_REPEAT_FIXTURE_IDS = ("F04", "F05", "F06")
S1VQ_REPEAT_IDS = ("R0", "R1")
S1VQ_EXPECTED_CASE_COUNT = 528
S1VQ_EXPECTED_PPB_CALLS = 9476
S1VQ_EXPECTED_BASELINE_CALLS = 66332
S1VQ_EXPECTED_TOTAL_CALLS = 75808

S1VQ_INVALID_IDENTITY_STATE = "S1VQ_INVALID_IDENTITY_STATE"
S1VQ_INVALID_PLAN = "S1VQ_INVALID_PLAN"
S1VQ_REPEAT_MISMATCH = "S1VQ_REPEAT_MISMATCH"
S1VQ_MATRIX_EXECUTION_BLOCKED = "S1VQ_MATRIX_EXECUTION_BLOCKED"

_IDENTITY = re.compile(r"^[a-z][a-z0-9_.-]*$")
_B01_IDENTITY = re.compile(r"^b01\.slot\.(\d{3})\.g(\d{6})$")


class S1VQMatrixError(ValueError):
    """One fail-closed S1-VQ identity or corrected-plan violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _mean(vectors: tuple[tuple[float, ...], ...]) -> tuple[float, ...]:
    return tuple(
        math.fsum(vector[index] for vector in vectors) / len(vectors)
        for index in range(len(vectors[0]))
    )


def _trace_identity(adapter_id: str) -> str:
    if adapter_id == "B02":
        return "b02.window.000"
    if adapter_id in {"B04", "B05", "B06"}:
        return f"{adapter_id.lower()}.trace.000"
    raise S1VQMatrixError(
        S1VQ_INVALID_IDENTITY_STATE, "adapter has no single-state identity"
    )


@dataclass(frozen=True, slots=True)
class S1VQBaselineCarry:
    base_state: S1VNBaselineState
    entry_ids: tuple[str, ...]
    slot_generations: tuple[int, ...]
    schema_version: str = S1VQ_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != S1VQ_SCHEMA_VERSION or not isinstance(
            self.base_state, S1VNBaselineState
        ):
            raise S1VQMatrixError(
                S1VQ_INVALID_IDENTITY_STATE, "invalid identity carry schema"
            )
        ids = tuple(self.entry_ids)
        generations = tuple(self.slot_generations)
        if len(set(ids)) != len(ids) or any(
            not isinstance(item, str) or not _IDENTITY.fullmatch(item)
            for item in ids
        ):
            raise S1VQMatrixError(
                S1VQ_INVALID_IDENTITY_STATE, "entry identities must be unique"
            )
        adapter_id = self.base_state.adapter_id
        if adapter_id == "B01":
            if (
                len(ids) != len(self.base_state.history)
                or len(generations) != self.base_state.capacity
                or any(
                    isinstance(value, bool)
                    or not isinstance(value, int)
                    or value < 0
                    for value in generations
                )
            ):
                raise S1VQMatrixError(
                    S1VQ_INVALID_IDENTITY_STATE, "B01 identity inventory mismatch"
                )
            active_slots = set()
            for entry_id in ids:
                match = _B01_IDENTITY.fullmatch(entry_id)
                if match is None:
                    raise S1VQMatrixError(
                        S1VQ_INVALID_IDENTITY_STATE, "invalid B01 entry identity"
                    )
                slot = int(match.group(1))
                generation = int(match.group(2))
                if (
                    slot >= self.base_state.capacity
                    or generation <= 0
                    or generations[slot] != generation
                    or slot in active_slots
                ):
                    raise S1VQMatrixError(
                        S1VQ_INVALID_IDENTITY_STATE,
                        "B01 generation does not match its active slot",
                    )
                active_slots.add(slot)
        elif adapter_id == "B03":
            expected = tuple(
                f"b03.slot.{index:03d}.g000001"
                for index in range(len(self.base_state.history))
            )
            if ids != expected or generations:
                raise S1VQMatrixError(
                    S1VQ_INVALID_IDENTITY_STATE, "B03 fixed identities drifted"
                )
        elif adapter_id == "B02":
            expected = () if not self.base_state.history else (_trace_identity("B02"),)
            if ids != expected or generations:
                raise S1VQMatrixError(
                    S1VQ_INVALID_IDENTITY_STATE, "B02 window identity mismatch"
                )
        elif adapter_id in {"B04", "B05", "B06"}:
            expected = () if self.base_state.trace is None else (_trace_identity(adapter_id),)
            if ids != expected or generations:
                raise S1VQMatrixError(
                    S1VQ_INVALID_IDENTITY_STATE, "trace identity mismatch"
                )
        elif adapter_id == "B07":
            if ids or generations:
                raise S1VQMatrixError(
                    S1VQ_INVALID_IDENTITY_STATE, "B07 must remain identity-free"
                )
        else:
            raise S1VQMatrixError(
                S1VQ_INVALID_IDENTITY_STATE, "unknown baseline adapter"
            )
        object.__setattr__(self, "entry_ids", ids)
        object.__setattr__(self, "slot_generations", generations)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "base_state": self.base_state.canonical_payload(),
            "entry_ids": list(self.entry_ids),
            "slot_generations": list(self.slot_generations),
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def initial_s1vq_baseline_carry(
    adapter_id: str, config: PPB1BankConfig
) -> S1VQBaselineCarry:
    base_state = initial_s1vn_baseline_state(adapter_id, config)
    generations = (0,) * config.capacity if adapter_id == "B01" else ()
    return S1VQBaselineCarry(base_state, (), generations)


def _candidate_values(carry: S1VQBaselineCarry) -> tuple[tuple[float, ...], ...]:
    adapter_id = carry.base_state.adapter_id
    if adapter_id in {"B01", "B03"}:
        return carry.base_state.history
    if adapter_id == "B02" and carry.base_state.history:
        return (_mean(carry.base_state.history),)
    if adapter_id in {"B04", "B05", "B06"} and carry.base_state.trace is not None:
        return (carry.base_state.trace,)
    return ()


def _selected_candidate(
    carry: S1VQBaselineCarry,
    vector: tuple[float, ...],
) -> tuple[float, str, tuple[float, ...]] | None:
    values = _candidate_values(carry)
    if not values:
        return None
    candidates = tuple(
        (
            normalized_mean_l1_distance(vector, candidate),
            carry.entry_ids[index],
            candidate,
        )
        for index, candidate in enumerate(values)
    )
    return min(candidates, key=lambda item: (item[0], item[1]))


@dataclass(frozen=True, slots=True)
class S1VQBaselineReadout:
    base_readout: S1VNBaselineReadout
    selected_entry_id: str | None
    written_entry_id: str | None
    selected_prestate_digest: str | None
    active_identity_count: int
    active_identity_digest: str
    postcarry_digest: str

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": S1VQ_SCHEMA_VERSION,
            "base_readout": {
                "adapter_id": self.base_readout.adapter_id,
                "event": self.base_readout.event,
                "distance": self.base_readout.distance,
                "logical_value_count": self.base_readout.logical_value_count,
                "poststate_digest": self.base_readout.poststate_digest,
            },
            "selected_entry_id": self.selected_entry_id,
            "written_entry_id": self.written_entry_id,
            "selected_prestate_digest": self.selected_prestate_digest,
            "active_identity_count": self.active_identity_count,
            "active_identity_digest": self.active_identity_digest,
            "postcarry_digest": self.postcarry_digest,
        }


@dataclass(frozen=True, slots=True)
class S1VQBaselineStepResult:
    postcarry: S1VQBaselineCarry
    readout: S1VQBaselineReadout

    def __post_init__(self) -> None:
        if self.readout.postcarry_digest != self.postcarry.digest():
            raise S1VQMatrixError(
                S1VQ_INVALID_IDENTITY_STATE, "identity result is not atomic"
            )


def advance_s1vq_baseline(
    adapter_id: str,
    config: PPB1BankConfig,
    precarry: S1VQBaselineCarry,
    values: tuple[float, ...],
) -> S1VQBaselineStepResult:
    """Advance the existing baseline and its private identity carry atomically."""

    if adapter_id != precarry.base_state.adapter_id:
        raise S1VQMatrixError(
            S1VQ_INVALID_IDENTITY_STATE, "adapter and identity carry mismatch"
        )
    vector = tuple(float(value) for value in values)
    selected = _selected_candidate(precarry, vector)
    base_result = advance_s1vn_baseline(
        adapter_id, config, precarry.base_state, vector
    )
    selected_id = None
    selected_digest = None
    if base_result.readout.event == "MATCHED":
        if selected is None or selected[0] > config.match_threshold:
            raise S1VQMatrixError(
                S1VQ_INVALID_IDENTITY_STATE, "matched baseline lacks identity"
            )
        selected_id = selected[1]
        selected_digest = _digest(
            {"entry_id": selected[1], "values": list(selected[2])}
        )

    entry_ids = precarry.entry_ids
    generations = list(precarry.slot_generations)
    written_id = None
    if adapter_id == "B01":
        if len(precarry.base_state.history) < config.capacity:
            slot = len(precarry.base_state.history)
        else:
            match = _B01_IDENTITY.fullmatch(entry_ids[0])
            assert match is not None
            slot = int(match.group(1))
            entry_ids = entry_ids[1:]
        generations[slot] += 1
        written_id = f"b01.slot.{slot:03d}.g{generations[slot]:06d}"
        entry_ids = entry_ids + (written_id,)
    elif adapter_id == "B02":
        written_id = _trace_identity(adapter_id)
        entry_ids = (written_id,)
    elif adapter_id == "B03":
        if base_result.readout.event == "STORED":
            slot = len(precarry.base_state.history)
            written_id = f"b03.slot.{slot:03d}.g000001"
            entry_ids = entry_ids + (written_id,)
    elif adapter_id in {"B04", "B05", "B06"}:
        written_id = _trace_identity(adapter_id)
        entry_ids = (written_id,)
    elif adapter_id == "B07":
        entry_ids = ()
    else:
        raise S1VQMatrixError(
            S1VQ_INVALID_IDENTITY_STATE, "unknown baseline adapter"
        )

    postcarry = S1VQBaselineCarry(
        base_result.poststate, entry_ids, tuple(generations)
    )
    readout = S1VQBaselineReadout(
        base_result.readout,
        selected_id,
        written_id,
        selected_digest,
        len(postcarry.entry_ids),
        _digest(list(postcarry.entry_ids)),
        postcarry.digest(),
    )
    return S1VQBaselineStepResult(postcarry, readout)


@dataclass(frozen=True, slots=True)
class S1VQIdentityObservation:
    step: int
    selected_entry_id: str | None
    written_entry_id: str | None
    selected_prestate_digest: str | None
    active_identity_count: int
    active_identity_digest: str

    def canonical_payload(self) -> dict[str, object]:
        return {
            "step": self.step,
            "selected_entry_id": self.selected_entry_id,
            "written_entry_id": self.written_entry_id,
            "selected_prestate_digest": self.selected_prestate_digest,
            "active_identity_count": self.active_identity_count,
            "active_identity_digest": self.active_identity_digest,
        }


@dataclass(frozen=True, slots=True)
class S1VQPathPlan:
    path_id: str
    parent_path_id: str
    repeat_id: str
    family_id: str
    parameter_id: str
    modality_id: str
    fixture_id: str
    expected_call_count: int
    config_digest: str

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": S1VQ_SCHEMA_VERSION,
            "path_id": self.path_id,
            "parent_path_id": self.parent_path_id,
            "repeat_id": self.repeat_id,
            "family_id": self.family_id,
            "parameter_id": self.parameter_id,
            "modality_id": self.modality_id,
            "fixture_id": self.fixture_id,
            "expected_call_count": self.expected_call_count,
            "config_digest": self.config_digest,
        }


def s1vq_corrected_matrix_plan() -> tuple[S1VQPathPlan, ...]:
    """Return the corrected 528 paths without executing any state step."""

    corrected: list[S1VQPathPlan] = []
    for parent in s1vn_matrix_plan():
        repeat_ids = (
            S1VQ_REPEAT_IDS
            if parent.fixture_id in S1VQ_REPEAT_FIXTURE_IDS
            else ("R0",)
        )
        for repeat_id in repeat_ids:
            corrected.append(
                S1VQPathPlan(
                    f"S1VQ-{len(corrected) + 1:03d}",
                    parent.path_id,
                    repeat_id,
                    parent.family_id,
                    parent.parameter_id,
                    parent.modality_id,
                    parent.fixture_id,
                    parent.expected_call_count,
                    parent.config_digest,
                )
            )
    return tuple(corrected)


@dataclass(frozen=True, slots=True)
class S1VQCaseReceipt:
    path: S1VQPathPlan
    base_receipt: S1VNCaseReceipt
    identity_observations: tuple[S1VQIdentityObservation, ...]

    def normalized_repeat_payload(self) -> dict[str, object]:
        base = self.base_receipt
        return {
            "family_id": base.family_id,
            "accepted_call_count": base.accepted_call_count,
            "events": list(base.events),
            "observations": [item.canonical_payload() for item in base.observations],
            "identity_observations": [
                item.canonical_payload() for item in self.identity_observations
            ],
            "input_history_digest": base.input_history_digest,
            "final_state_digest": base.final_state_digest,
        }

    def repeat_comparison_digest(self) -> str:
        return _digest(self.normalized_repeat_payload())


def _history_digest(frames: tuple[ReceptorContactFrame, ...]) -> str:
    return _digest(
        [
            {
                "modality_id": frame.modality_id,
                "geometry_id": frame.geometry_id,
                "clock_id": frame.clock_id,
                "window_start_tick": frame.window_start_tick,
                "window_end_tick": frame.window_end_tick,
                "carrier_ids": list(frame.carrier_ids),
                "values": list(frame.values),
            }
            for frame in frames
        ]
    )


def _execute_s1vq_frames(
    path: S1VQPathPlan,
    config: PPB1BankConfig,
    frames: tuple[ReceptorContactFrame, ...],
) -> S1VQCaseReceipt:
    if path.family_id == "PPB1":
        base = _execute_frames(path.path_id, "PPB1", config, frames)
        identities = tuple(
            S1VQIdentityObservation(
                observation.step,
                observation.selected_slot_id
                if observation.event == "MATCHED"
                else None,
                observation.selected_slot_id,
                None,
                observation.occupied_slot_count,
                _digest(
                    {
                        "bank_id": config.bank_id,
                        "active_slot_count": observation.occupied_slot_count,
                    }
                ),
            )
            for observation in base.observations
        )
        return S1VQCaseReceipt(path, base, identities)

    carry = initial_s1vq_baseline_carry(path.family_id, config)
    events: list[str] = []
    observations: list[S1VNStepObservation] = []
    identities: list[S1VQIdentityObservation] = []
    for frame in frames:
        result = advance_s1vq_baseline(
            path.family_id, config, carry, frame.values
        )
        carry = result.postcarry
        readout = result.readout
        events.append(readout.base_readout.event)
        observations.append(
            S1VNStepObservation(
                carry.base_state.accepted_step_count,
                readout.base_readout.event,
                readout.base_readout.distance,
                readout.base_readout.logical_value_count,
                len(carry.base_state.history),
                0,
                readout.selected_entry_id,
                None,
            )
        )
        identities.append(
            S1VQIdentityObservation(
                carry.base_state.accepted_step_count,
                readout.selected_entry_id,
                readout.written_entry_id,
                readout.selected_prestate_digest,
                readout.active_identity_count,
                readout.active_identity_digest,
            )
        )
    base = S1VNCaseReceipt(
        path.path_id,
        path.family_id,
        len(frames),
        tuple(events),
        tuple(observations),
        _history_digest(frames),
        carry.digest(),
    )
    return S1VQCaseReceipt(path, base, tuple(identities))


def run_s1vq_miniature_contract(
    family_id: str,
    config: PPB1BankConfig,
    frames: tuple[ReceptorContactFrame, ...],
    repeat_id: str = "R0",
) -> S1VQCaseReceipt:
    """Run at most four non-matrix frames for corrected wiring tests."""

    if (
        family_id not in S1VN_FAMILY_IDS
        or repeat_id not in S1VQ_REPEAT_IDS
        or not frames
        or len(frames) > 4
        or any(
            not frame.snapshot_id.startswith("s1vq.contract.") for frame in frames
        )
    ):
        raise S1VQMatrixError(
            S1VQ_INVALID_PLAN, "invalid S1-VQ miniature contract"
        )
    path = S1VQPathPlan(
        f"S1VQ-CONTRACT-{repeat_id}",
        "S1VN-CONTRACT",
        repeat_id,
        family_id,
        "P0",
        config.modality_id,
        "F00",
        len(frames),
        config.digest(),
    )
    return _execute_s1vq_frames(path, config, frames)


@dataclass(frozen=True, slots=True)
class S1VQRunnerPreparation:
    parent_plan_digest: str
    corrected_plan_digest: str
    case_count: int
    ppb_call_count: int
    baseline_call_count: int
    total_call_count: int
    execution_authorized: bool
    accepted_call_count: int


def prepare_s1vq_corrected_runner() -> S1VQRunnerPreparation:
    parent = prepare_s1vn_matrix_runner()
    plan = s1vq_corrected_matrix_plan()
    ppb_calls = sum(
        path.expected_call_count for path in plan if path.family_id == "PPB1"
    )
    baseline_calls = sum(
        path.expected_call_count for path in plan if path.family_id != "PPB1"
    )
    if (
        parent.plan_digest != S1VQ_PARENT_PLAN_DIGEST
        or len(plan) != S1VQ_EXPECTED_CASE_COUNT
        or ppb_calls != S1VQ_EXPECTED_PPB_CALLS
        or baseline_calls != S1VQ_EXPECTED_BASELINE_CALLS
        or ppb_calls + baseline_calls != S1VQ_EXPECTED_TOTAL_CALLS
        or len({path.path_id for path in plan}) != len(plan)
    ):
        raise S1VQMatrixError(
            S1VQ_INVALID_PLAN, "corrected plan does not match S1-VP"
        )
    return S1VQRunnerPreparation(
        parent.plan_digest,
        _digest([path.canonical_payload() for path in plan]),
        len(plan),
        ppb_calls,
        baseline_calls,
        ppb_calls + baseline_calls,
        False,
        0,
    )


def _execute_s1vq_registered_path(path: S1VQPathPlan) -> S1VQCaseReceipt:
    config = s1vn_config(path.parameter_id, path.modality_id)
    if config.digest() != path.config_digest:
        raise S1VQMatrixError(S1VQ_INVALID_PLAN, "path config digest drifted")
    frames = build_s1vn_fixture(config, path.fixture_id)
    if len(frames) != path.expected_call_count:
        raise S1VQMatrixError(S1VQ_INVALID_PLAN, "path call count drifted")
    return _execute_s1vq_frames(path, config, frames)


@dataclass(frozen=True, slots=True)
class S1VQMatrixResult:
    corrected_plan_digest: str
    receipts: tuple[S1VQCaseReceipt, ...]
    accepted_call_count: int
    repeat_comparison_digests: tuple[tuple[str, str], ...]


def _execute_s1vq_corrected_matrix() -> S1VQMatrixResult:
    """Complete corrected body kept unreachable behind the S1-VQ gate."""

    preparation = prepare_s1vq_corrected_runner()
    plan = s1vq_corrected_matrix_plan()
    receipts = tuple(_execute_s1vq_registered_path(path) for path in plan)
    accepted = sum(item.base_receipt.accepted_call_count for item in receipts)
    primary: dict[tuple[str, str, str, str], S1VQCaseReceipt] = {}
    comparisons: list[tuple[str, str]] = []
    for receipt in receipts:
        path = receipt.path
        key = (
            path.family_id,
            path.parameter_id,
            path.modality_id,
            path.fixture_id,
        )
        if path.repeat_id == "R0":
            primary[key] = receipt
        else:
            if key not in primary:
                raise S1VQMatrixError(
                    S1VQ_REPEAT_MISMATCH, "R1 has no preceding R0"
                )
            left = primary[key].repeat_comparison_digest()
            right = receipt.repeat_comparison_digest()
            if left != right:
                raise S1VQMatrixError(
                    S1VQ_REPEAT_MISMATCH, "R0 and R1 are not bit-equal"
                )
            comparisons.append((receipt.path.path_id, right))
    if (
        len(receipts) != preparation.case_count
        or accepted != preparation.total_call_count
        or len(comparisons) != 144
    ):
        raise S1VQMatrixError(
            S1VQ_INVALID_PLAN, "corrected execution does not match its plan"
        )
    return S1VQMatrixResult(
        preparation.corrected_plan_digest,
        receipts,
        accepted,
        tuple(comparisons),
    )


def execute_s1vq_corrected_matrix() -> None:
    """Refuse all 528 registered paths until a later preflight and release."""

    raise S1VQMatrixError(
        S1VQ_MATRIX_EXECUTION_BLOCKED,
        "S1-VQ implements corrected wiring only; matrix execution is blocked",
    )
