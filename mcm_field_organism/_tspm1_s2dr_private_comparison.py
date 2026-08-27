"""Private S2-DR comparison implementation for the bounded TSPM-1 study."""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
import hashlib
import json
import math
import re
from threading import Lock
from typing import Any, Iterable, Mapping, Sequence

from . import _tspm1_private as tspm1
from ._ppb1_active_receptor_batch_binding import bind_ppb1_active_receptor_batch
from ._ppb1_receptor_profiles import (
    PPB1ModalityParameters,
    PPB1ProfileParameters,
    bind_ppb1_receptor_profile,
)
from ._ppb1_reference import (
    PPB1BankState,
    advance_ppb1_bank,
    initial_ppb1_bank_state,
    normalized_mean_l1_distance,
)
from ._ppb1_s1wu_read_only_perceptual_probe import (
    S1WUReadOnlyPerceptualFinding,
    probe_s1wu_perceptual_state,
)
from .browser_receptor_bridge import BrowserReceptorSequenceBatch
from .browser_world_contract import BrowserWorldContract, BrowserWorldPhase
from .receptor_contract import CommonFieldTime, ReceptorContactFrame, technical_identifier
from .receptor_time_model import OrganismTimedReceptorFrame, ReceptorTimeSequence


S2DR_SCHEMA_VERSION = "s2dr.tspm1.private-comparison.v1"
S2DR_CANDIDATE_ID = "TSPM1"
S2DR_S2DS_PASS_DIGEST = (
    "1101642ddcabe325cc76c65a0e026e185b7c8cede7ab715ac8bec16165fbf284"
)

S2DR_OWNER_BUSY = "S2DR_OWNER_BUSY"
S2DR_OWNER_TERMINAL = "S2DR_OWNER_TERMINAL"
S2DR_INVALID_TYPE_OR_SCHEMA = "S2DR_INVALID_TYPE_OR_SCHEMA"
S2DR_DIGEST_OR_SOURCE_MISMATCH = "S2DR_DIGEST_OR_SOURCE_MISMATCH"
S2DR_AUTHORIZATION_MISMATCH = "S2DR_AUTHORIZATION_MISMATCH"
S2DR_OWNER_AUTHORIZATION_MISMATCH = "S2DR_OWNER_AUTHORIZATION_MISMATCH"
S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH = "S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH"
S2DR_RESOURCE_OR_OPERATION_LIMIT_EXCEEDED = (
    "S2DR_RESOURCE_OR_OPERATION_LIMIT_EXCEEDED"
)
S2DR_RESULT_RELATION_MISMATCH = "S2DR_RESULT_RELATION_MISMATCH"
S2DR_ATOMIC_RESULT_REQUIRED = "S2DR_ATOMIC_RESULT_REQUIRED"
S2DR_ATTEMPT_FAILED = "S2DR_ATTEMPT_FAILED"

HISTORY_IDS = ("H1", "H2", "H3", "H4", "H5", "H6", "H7")
ARM_IDS = (
    "TSPM1",
    "B0",
    "B1_DIRECT",
    "B1_BUDGET_MATCHED",
    "B2",
    "B3",
    "B4",
    "R0",
)
PREDICATE_IDS = ("P1_EARLY", "P2_LATE", "P3_CONFLICT", "P4_EVICTION", "P5_ERROR")
OUTCOMES = (
    "METHOD_INVALID",
    "TSPM1_FUNCTION_NOT_VALID",
    "FUNCTION_VALID_SIMPLE_BASELINE_EXPLAINS",
    "TSPM1_TWO_TIMESCALE_ENGINEERING_ADVANTAGE_OVER_SIMPLE_BASELINES",
)
OWNER_STATES = ("FRESH", "BUSY", "COMMITTED", "FAILED")

AUDITORY_CARRIERS = (
    "auditory.log_hz.50.000000",
    "auditory.log_hz.89.741146",
    "auditory.log_hz.161.069466",
    "auditory.log_hz.289.091169",
    "auditory.log_hz.518.867457",
    "auditory.log_hz.931.275205",
    "auditory.log_hz.1671.474085",
    "auditory.log_hz.3000.000000",
)
VISUAL_CARRIERS = tuple(
    f"visual.cell.r{row}.c{column}.channel{channel}"
    for row in range(2)
    for column in range(3)
    for channel in range(3)
)
PAIR_SCALARS = {
    "AX": (0.0, 0.0),
    "AY": (0.0, 0.6),
    "BX": (0.6, 0.0),
    "P2": (-0.8, -0.8),
    "P3": (-0.8, 0.8),
    "P4": (0.8, -0.8),
    "D1": (-1.0, -1.0),
    "D2": (-1.0, 0.0),
    "D3": (-1.0, 1.0),
    "D4": (0.0, -1.0),
    "D5": (0.0, 1.0),
    "D6": (1.0, -1.0),
    "D7": (1.0, 0.0),
    "D8": (1.0, 1.0),
    "NEAR": (0.15, 0.15),
    "PARTIAL_OUT": (0.21, 0.0),
    "OUTSIDE": (0.21, 0.21),
    "FAR": (1.0, 1.0),
}
HISTORY_DEFINITIONS = {
    "H1": (("AX",), ((1, ("AX",)),), ()),
    "H2": (("AX", "AX", "AX", "AX"), ((1, ("AX",)), (4, ("AX",))), (2, 3, 4)),
    "H3": (("AX", "AX", "AX", "AX", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"), ((12, ("AX",)),), (2, 3, 4)),
    "H4": (("AX", "AX", "AX", "AX", "AY", "BX"), ((6, ("AX", "AY", "BX")),), (2, 3, 4)),
    "H5": (("AX", "AX", "AX", "AX", "P2", "P3", "P2", "P4"), ((8, ("AX", "P4")),), (2, 3, 4, 7)),
    "H6": (("AX", "AX", "AX", "AX", "D1", "D3", "D8"), ((7, ("AX", "D1", "D3", "D8")),), (2, 3, 4)),
    "H7": (("AX", "AX", "AX", "AX"), ((4, ("AX", "NEAR", "PARTIAL_OUT", "OUTSIDE", "FAR")),), (2, 3, 4)),
}
ARM_RESOURCE_WORDS = {
    "TSPM1": 269,
    "B0": 0,
    "B1_DIRECT": 176,
    "B1_BUDGET_MATCHED": 176,
    "B2": 264,
    "B3": 29,
    "B4": 255,
    "R0": 269,
}
OPERATION_LIMITS = {
    "formation_write_limit": 293,
    "formation_distance_limit": 234,
    "probe_distance_limit": 234,
    "probe_write_limit": 0,
}
SIMPLE_BASELINE_ORDER = ("B0", "B1_DIRECT", "B1_BUDGET_MATCHED", "B2", "B3", "B4")

_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")


class S2DRError(ValueError):
    """One private fail-closed S2-DR violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _canonical(value: Any) -> Any:
    if is_dataclass(value):
        return {field.name: _canonical(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, Mapping):
        return {str(key): _canonical(item) for key, item in sorted(value.items())}
    if isinstance(value, (tuple, list)):
        return [_canonical(item) for item in value]
    return value


def _digest(value: Any) -> str:
    encoded = json.dumps(
        _canonical(value),
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _is_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST_RE.fullmatch(value) is not None


def _id(value: object, role: str) -> str:
    try:
        return technical_identifier(value, role)
    except ValueError as exc:
        raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, str(exc)) from exc


def _finite_tuple(values: object, length: int, role: str) -> tuple[float, ...]:
    if not isinstance(values, tuple) or len(values) != length:
        raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, f"{role} shape is invalid")
    normalized = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, f"{role} must be finite")
        normalized.append(float(value))
    return tuple(normalized)


def _record_payload(record: object, digest_field: str) -> dict[str, object]:
    return {
        field.name: _canonical(getattr(record, field.name))
        for field in fields(record)
        if field.name != digest_field
    }


def _validate_record(record: object, digest_field: str) -> None:
    digest_value = getattr(record, digest_field)
    if not _is_digest(digest_value) or digest_value != _digest(_record_payload(record, digest_field)):
        raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, f"invalid {digest_field}")


def _built(record_type, digest_field: str, **values):
    values[digest_field] = _digest(values)
    return record_type(**values)


@dataclass(frozen=True, slots=True)
class S2DRConfigRecord:
    schema_version: str
    candidate_id: str
    parent_artifact_digests: tuple[str, ...]
    source_blob_digests: tuple[str, ...]
    auditory_carrier_ids: tuple[str, ...]
    visual_carrier_ids: tuple[str, ...]
    fast_parameters: tuple[object, ...]
    auditory_ppb_parameters: tuple[object, ...]
    visual_ppb_parameters: tuple[object, ...]
    arm_resource_words: tuple[tuple[str, int], ...]
    operation_limits: tuple[tuple[str, int], ...]
    config_digest: str

    def __post_init__(self) -> None:
        if self.schema_version != S2DR_SCHEMA_VERSION or self.candidate_id != S2DR_CANDIDATE_ID:
            raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "invalid config identity")
        if self.auditory_carrier_ids != AUDITORY_CARRIERS or self.visual_carrier_ids != VISUAL_CARRIERS:
            raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, "carrier anatomy changed")
        if not all(_is_digest(value) for value in self.parent_artifact_digests + self.source_blob_digests):
            raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, "source digest is invalid")
        _validate_record(self, "config_digest")


@dataclass(frozen=True, slots=True)
class S2DRFixtureRecord:
    schema_version: str
    history_id: str
    formation_pair_ids: tuple[str, ...]
    probe_specs: tuple[tuple[int, tuple[str, ...]], ...]
    ppb_budget_indices: tuple[int, ...]
    field_clock_id: str
    interval_width: int
    source_id_format: str
    formation_frame_id_format: str
    probe_frame_id_format: str
    fixture_digest: str

    def __post_init__(self) -> None:
        if self.schema_version != S2DR_SCHEMA_VERSION or self.history_id not in HISTORY_IDS:
            raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "invalid fixture identity")
        expected = HISTORY_DEFINITIONS[self.history_id]
        if (self.formation_pair_ids, self.probe_specs, self.ppb_budget_indices) != expected:
            raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, "fixture differs from registry")
        if self.interval_width != 10 or self.field_clock_id != "field.synthetic.s2dq":
            raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, "fixture clock changed")
        _validate_record(self, "fixture_digest")


@dataclass(frozen=True, slots=True)
class S2DRArmSpec:
    schema_version: str
    arm_id: str
    operator_id: str
    state_schema_id: str
    resource_words: int
    formation_write_limit: int
    formation_distance_limit: int
    probe_distance_limit: int
    probe_write_limit: int
    initial_state_payload: object
    initial_state_digest: str
    arm_spec_digest: str

    def __post_init__(self) -> None:
        if self.schema_version != S2DR_SCHEMA_VERSION or self.arm_id not in ARM_IDS:
            raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "invalid arm identity")
        if self.resource_words != ARM_RESOURCE_WORDS[self.arm_id]:
            raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, "resource words changed")
        if (
            self.formation_write_limit,
            self.formation_distance_limit,
            self.probe_distance_limit,
            self.probe_write_limit,
        ) != (293, 234, 234, 0):
            raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, "operation limits changed")
        if self.initial_state_digest != _digest(self.initial_state_payload):
            raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, "initial state digest changed")
        _validate_record(self, "arm_spec_digest")


@dataclass(frozen=True, slots=True)
class S2DRCellPlan:
    schema_version: str
    cell_id: str
    history_id: str
    arm_id: str
    config_digest: str
    fixture_digest: str
    arm_spec_digest: str
    initial_state_digest: str
    formation_call_count: int
    probe_call_count: int
    authorization_digest: str
    cell_plan_digest: str

    def __post_init__(self) -> None:
        if self.schema_version != S2DR_SCHEMA_VERSION or self.history_id not in HISTORY_IDS or self.arm_id not in ARM_IDS:
            raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "invalid cell plan identity")
        _id(self.cell_id, "cell_id")
        if not all(_is_digest(value) for value in (self.config_digest, self.fixture_digest, self.arm_spec_digest, self.initial_state_digest, self.authorization_digest)):
            raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, "cell plan digest role invalid")
        expected = _authorization_digest(
            self.cell_id,
            self.config_digest,
            self.fixture_digest,
            self.arm_spec_digest,
            self.initial_state_digest,
        )
        if self.authorization_digest != expected:
            raise S2DRError(S2DR_AUTHORIZATION_MISMATCH, "cell authorization changed")
        _validate_record(self, "cell_plan_digest")


@dataclass(frozen=True, slots=True)
class S2DRBudgetReceipt:
    schema_version: str
    cell_id: str
    cell_plan_digest: str
    resource_words_bound: int
    resource_words_used: int
    formation_write_bounds: tuple[tuple[int, int], ...]
    formation_write_counts: tuple[tuple[int, int], ...]
    formation_distance_bounds: tuple[tuple[int, int], ...]
    formation_distance_counts: tuple[tuple[int, int], ...]
    probe_distance_bounds: tuple[tuple[int, int], ...]
    probe_distance_counts: tuple[tuple[int, int], ...]
    probe_write_bounds: tuple[tuple[int, int], ...]
    probe_write_counts: tuple[tuple[int, int], ...]
    remaining_resource_words: int
    remaining_formation_write_budget: tuple[tuple[int, int], ...]
    remaining_formation_distance_budget: tuple[tuple[int, int], ...]
    remaining_probe_distance_budget: tuple[tuple[int, int], ...]
    remaining_probe_write_budget: tuple[tuple[int, int], ...]
    budget_receipt_digest: str

    def __post_init__(self) -> None:
        if self.schema_version != S2DR_SCHEMA_VERSION:
            raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "invalid budget schema")
        _id(self.cell_id, "cell_id")
        if not _is_digest(self.cell_plan_digest):
            raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, "invalid budget plan digest")
        if any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in (self.resource_words_bound, self.resource_words_used)):
            raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "resource values must be nonnegative integers")
        if self.remaining_resource_words != self.resource_words_bound - self.resource_words_used:
            raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "resource remainder is inconsistent")
        groups = (
            (self.formation_write_bounds, self.formation_write_counts, self.remaining_formation_write_budget),
            (self.formation_distance_bounds, self.formation_distance_counts, self.remaining_formation_distance_budget),
            (self.probe_distance_bounds, self.probe_distance_counts, self.remaining_probe_distance_budget),
            (self.probe_write_bounds, self.probe_write_counts, self.remaining_probe_write_budget),
        )
        for bounds, counts, remaining in groups:
            keys = tuple(key for key, _ in bounds)
            if keys != tuple(key for key, _ in counts) or keys != tuple(key for key, _ in remaining):
                raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "budget tuple keys differ")
            if keys != tuple(sorted(keys)) or any(key < 1 for key in keys):
                raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "budget tuple keys are invalid")
            for (_, bound), (_, used), (_, rest) in zip(bounds, counts, remaining, strict=True):
                if any(isinstance(value, bool) or not isinstance(value, int) for value in (bound, used, rest)) or bound < 0 or used < 0:
                    raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "budget tuple value is invalid")
                if rest != bound - used:
                    raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "operation remainder is inconsistent")
        _validate_record(self, "budget_receipt_digest")


@dataclass(frozen=True, slots=True)
class S2DRCellReceipt:
    schema_version: str
    cell_id: str
    cell_plan_digest: str
    config_digest: str
    fixture_digest: str
    arm_spec_digest: str
    prestate_digest: str
    event_digest: str
    finding_digest: str
    budget_receipt_digest: str
    poststate_digest: str
    owner_id: str
    owner_terminal_state: str
    internal_error_code: str | None
    cell_receipt_digest: str

    def __post_init__(self) -> None:
        if self.schema_version != S2DR_SCHEMA_VERSION or self.owner_terminal_state not in OWNER_STATES:
            raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "invalid cell receipt")
        _id(self.cell_id, "cell_id")
        _id(self.owner_id, "owner_id")
        digests = (self.cell_plan_digest, self.config_digest, self.fixture_digest, self.arm_spec_digest, self.prestate_digest, self.event_digest, self.finding_digest, self.budget_receipt_digest, self.poststate_digest)
        if not all(_is_digest(value) for value in digests):
            raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, "cell receipt digest role invalid")
        _validate_record(self, "cell_receipt_digest")


@dataclass(frozen=True, slots=True)
class S2DRCellResult:
    schema_version: str
    cell_id: str
    cell_plan_digest: str
    prestate_digest: str
    event_payloads: tuple[object, ...]
    finding_payloads: tuple[object, ...]
    poststate_payload: object
    poststate_digest: str
    budget_receipt: S2DRBudgetReceipt
    cell_receipt: S2DRCellReceipt
    cell_result_digest: str

    def __post_init__(self) -> None:
        if self.schema_version != S2DR_SCHEMA_VERSION or type(self.budget_receipt) is not S2DRBudgetReceipt or type(self.cell_receipt) is not S2DRCellReceipt:
            raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "invalid cell result")
        if self.poststate_digest != _digest(self.poststate_payload):
            raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "poststate payload digest differs")
        _validate_record(self, "cell_result_digest")


@dataclass(frozen=True, slots=True)
class S2DRComparisonResult:
    schema_version: str
    registry_digest: str
    ordered_cell_result_digests: tuple[str, ...]
    per_arm_predicate_vectors: tuple[tuple[str, tuple[bool, ...]], ...]
    per_arm_error_counts: tuple[tuple[str, int], ...]
    strongest_simple_baseline_id: str | None
    r0_exact_equivalence: bool
    decision: str
    comparison_result_digest: str

    def __post_init__(self) -> None:
        if self.schema_version != S2DR_SCHEMA_VERSION or self.decision not in OUTCOMES:
            raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "invalid comparison result")
        if not _is_digest(self.registry_digest) or not all(_is_digest(value) for value in self.ordered_cell_result_digests):
            raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, "comparison digest role invalid")
        _validate_record(self, "comparison_result_digest")


def _authorization_digest(
    cell_id: str,
    config_digest: str,
    fixture_digest: str,
    arm_spec_digest: str,
    initial_state_digest: str,
) -> str:
    return _digest(
        (
            "S2DR_AUTH",
            cell_id,
            config_digest,
            fixture_digest,
            arm_spec_digest,
            initial_state_digest,
        )
    )


def _initial_payload(arm_id: str) -> object:
    if arm_id in {"TSPM1", "R0"}:
        return (
            "s2dr.two-level.normalized.v1",
            0,
            tuple((False, (), (), None, None, 0) for _ in range(3)),
            "auditory.ppb.empty",
            "visual.ppb.empty",
        )
    if arm_id == "B0":
        return ("s2dr.b0.state.v1",)
    if arm_id in {"B1_DIRECT", "B1_BUDGET_MATCHED"}:
        return (f"s2dr.{arm_id.lower()}.state.v1", "auditory.ppb.empty", "visual.ppb.empty")
    if arm_id == "B2":
        return (
            "s2dr.b2.state.v1",
            0,
            None,
            None,
            tuple((f"b2.slot.{index:03d}", False, (), None, None) for index in range(9)),
        )
    if arm_id == "B3":
        return ("s2dr.b3.state.v1", False, (), None, 0)
    if arm_id == "B4":
        return (
            "s2dr.b4.state.v1",
            0,
            None,
            None,
            tuple((f"b4.slot.{index:03d}", False, (), None) for index in range(9)),
        )
    raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "unknown arm")


def _operator_id(arm_id: str) -> str:
    return {
        "TSPM1": "UNCHANGED_PRIVATE_CORE",
        "B0": "NO_FUNCTIONAL_STATE",
        "B1_DIRECT": "TWO_UNCHANGED_PPB1_BANKS_ALL_ORIGINAL_FRAMES_ONCE",
        "B1_BUDGET_MATCHED": "TWO_UNCHANGED_PPB1_BANKS_PREREGISTERED_INDICES_ONLY",
        "B2": "NINE_SLOT_JOINT_ADAPTIVE_ONLINE_PROTOTYPE_OPERATOR",
        "B3": "ONE_TRACE_ALPHA_0_5_EXPIRE_8_OPERATOR",
        "B4": "NINE_ENTRY_FIFO_OPERATOR",
        "R0": "EXACT_GENERIC_TWO_LEVEL_REDUCTION",
    }[arm_id]


def _source_blob_digests() -> tuple[str, ...]:
    return (
        _digest(("auditory-source", AUDITORY_CARRIERS)),
        _digest(("visual-source", VISUAL_CARRIERS)),
        _digest(("literal-pairs", tuple(PAIR_SCALARS.items()))),
    )


def build_s2dr_registry() -> tuple[
    S2DRConfigRecord,
    tuple[S2DRFixtureRecord, ...],
    tuple[S2DRArmSpec, ...],
    tuple[S2DRCellPlan, ...],
    str,
]:
    """Build the closed 7x8 registry without creating functional states."""

    config = _built(
        S2DRConfigRecord,
        "config_digest",
        schema_version=S2DR_SCHEMA_VERSION,
        candidate_id=S2DR_CANDIDATE_ID,
        parent_artifact_digests=(
            S2DR_S2DS_PASS_DIGEST,
            "ace48bfd28e685e706d5ddf1d6647fe8e36190aa87c8fa6d80b2412c8317afed",
            "d5469f35988098020ef5ca413e641f927621dd0adb69b89914b2cbd49e9d7f18",
        ),
        source_blob_digests=_source_blob_digests(),
        auditory_carrier_ids=AUDITORY_CARRIERS,
        visual_carrier_ids=VISUAL_CARRIERS,
        fast_parameters=("tspm1.fast", 3, 0.2, 0.2, 0.5, 2, 8),
        auditory_ppb_parameters=(8, 0.02, 0.05, 3, 256),
        visual_ppb_parameters=(4, 0.01, 0.05, 3, 64),
        arm_resource_words=tuple((arm_id, ARM_RESOURCE_WORDS[arm_id]) for arm_id in ARM_IDS),
        operation_limits=tuple(OPERATION_LIMITS.items()),
    )
    fixtures = tuple(
        _built(
            S2DRFixtureRecord,
            "fixture_digest",
            schema_version=S2DR_SCHEMA_VERSION,
            history_id=history_id,
            formation_pair_ids=HISTORY_DEFINITIONS[history_id][0],
            probe_specs=HISTORY_DEFINITIONS[history_id][1],
            ppb_budget_indices=HISTORY_DEFINITIONS[history_id][2],
            field_clock_id="field.synthetic.s2dq",
            interval_width=10,
            source_id_format="s2dr.source.<modality>",
            formation_frame_id_format=f"s2dr.{history_id.lower()}.formation.<index>.<modality>",
            probe_frame_id_format=f"s2dr.{history_id.lower()}.probe.<index>.<modality>",
        )
        for history_id in HISTORY_IDS
    )
    arms = tuple(
        _built(
            S2DRArmSpec,
            "arm_spec_digest",
            schema_version=S2DR_SCHEMA_VERSION,
            arm_id=arm_id,
            operator_id=_operator_id(arm_id),
            state_schema_id=f"s2dr.{arm_id.lower()}.state.v1",
            resource_words=ARM_RESOURCE_WORDS[arm_id],
            formation_write_limit=293,
            formation_distance_limit=234,
            probe_distance_limit=234,
            probe_write_limit=0,
            initial_state_payload=_initial_payload(arm_id),
            initial_state_digest=_digest(_initial_payload(arm_id)),
        )
        for arm_id in ARM_IDS
    )
    arm_by_id = {arm.arm_id: arm for arm in arms}
    fixture_by_id = {fixture.history_id: fixture for fixture in fixtures}
    plans = []
    for history_id in HISTORY_IDS:
        fixture = fixture_by_id[history_id]
        probe_count = sum(len(pair_ids) for _, pair_ids in fixture.probe_specs)
        for arm_id in ARM_IDS:
            arm = arm_by_id[arm_id]
            cell_id = f"s2dr.cell.{history_id.lower()}.{arm_id.lower()}"
            authorization_digest = _authorization_digest(
                cell_id,
                config.config_digest,
                fixture.fixture_digest,
                arm.arm_spec_digest,
                arm.initial_state_digest,
            )
            plans.append(
                _built(
                    S2DRCellPlan,
                    "cell_plan_digest",
                    schema_version=S2DR_SCHEMA_VERSION,
                    cell_id=cell_id,
                    history_id=history_id,
                    arm_id=arm_id,
                    config_digest=config.config_digest,
                    fixture_digest=fixture.fixture_digest,
                    arm_spec_digest=arm.arm_spec_digest,
                    initial_state_digest=arm.initial_state_digest,
                    formation_call_count=len(fixture.formation_pair_ids),
                    probe_call_count=probe_count,
                    authorization_digest=authorization_digest,
                )
            )
    plans_tuple = tuple(plans)
    registry_digest = _digest(
        {
            "schema_version": S2DR_SCHEMA_VERSION,
            "config_digest": config.config_digest,
            "fixture_digests": tuple(item.fixture_digest for item in fixtures),
            "arm_spec_digests": tuple(item.arm_spec_digest for item in arms),
            "cell_plan_digests": tuple(item.cell_plan_digest for item in plans_tuple),
        }
    )
    return config, fixtures, arms, plans_tuple, registry_digest


@dataclass(frozen=True, slots=True)
class _JointSlot:
    slot_id: str
    occupied: bool
    values: tuple[float, ...]
    support: int | None
    last_selected_step: int | None


@dataclass(frozen=True, slots=True)
class _B2State:
    accepted_count: int
    slots: tuple[_JointSlot, ...]


@dataclass(frozen=True, slots=True)
class _B3State:
    occupied: bool
    values: tuple[float, ...]
    last_formation_step: int | None
    accepted_count: int


@dataclass(frozen=True, slots=True)
class _FIFOEntry:
    slot_id: str
    occupied: bool
    values: tuple[float, ...]
    formation_index: int | None


@dataclass(frozen=True, slots=True)
class _B4State:
    accepted_count: int
    entries: tuple[_FIFOEntry, ...]


@dataclass(frozen=True, slots=True)
class _PPBPairState:
    auditory: PPB1BankState
    visual: PPB1BankState


@dataclass(frozen=True, slots=True)
class _GenericFastSlot:
    slot_id: str
    occupied: bool
    auditory_values: tuple[float, ...]
    visual_values: tuple[float, ...]
    support_count: int | None
    last_selected_step: int | None
    consolidation_count: int


@dataclass(frozen=True, slots=True)
class _GenericFastState:
    accepted_count: int
    auditory_clock_id: str | None
    auditory_end_tick: int | None
    visual_clock_id: str | None
    visual_end_tick: int | None
    slots: tuple[_GenericFastSlot, ...]


@dataclass(frozen=True, slots=True)
class _GenericTwoLevelState:
    generation: int
    fast: _GenericFastState
    auditory_ppb: PPB1BankState
    visual_ppb: PPB1BankState


def _runtime_profile():
    parameters = PPB1ProfileParameters(
        PPB1ModalityParameters(8, 0.02, 0.05, 3, 256),
        PPB1ModalityParameters(4, 0.01, 0.05, 3, 64),
    )
    return bind_ppb1_receptor_profile("browser", parameters)


def _runtime_tspm_config():
    profile = _runtime_profile()
    fast = tspm1.TSPM1FastConfig("tspm1.fast", 3, 0.2, 0.2, 0.5, 2, 8)
    return profile, tspm1.TSPM1ConfigBinding.build(fast, profile)


def initial_s2dr_arm_state(config: S2DRConfigRecord, arm: S2DRArmSpec) -> object:
    if type(config) is not S2DRConfigRecord or type(arm) is not S2DRArmSpec:
        raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "exact config and arm are required")
    if arm.arm_id == "TSPM1":
        _, binding = _runtime_tspm_config()
        return tspm1.initial_tspm1_composite_state(binding)
    if arm.arm_id == "R0":
        profile = _runtime_profile()
        fast = _GenericFastState(
            0,
            None,
            None,
            None,
            None,
            tuple(
                _GenericFastSlot(
                    f"r0.fast.slot.{index:03d}", False, (), (), None, None, 0
                )
                for index in range(3)
            ),
        )
        return _GenericTwoLevelState(
            0,
            fast,
            initial_ppb1_bank_state(profile.auditory_config),
            initial_ppb1_bank_state(profile.visual_config),
        )
    if arm.arm_id == "B0":
        return ()
    if arm.arm_id in {"B1_DIRECT", "B1_BUDGET_MATCHED"}:
        profile = _runtime_profile()
        return _PPBPairState(
            initial_ppb1_bank_state(profile.auditory_config),
            initial_ppb1_bank_state(profile.visual_config),
        )
    if arm.arm_id == "B2":
        return _B2State(0, tuple(_JointSlot(f"b2.slot.{index:03d}", False, (), None, None) for index in range(9)))
    if arm.arm_id == "B3":
        return _B3State(False, (), None, 0)
    if arm.arm_id == "B4":
        return _B4State(0, tuple(_FIFOEntry(f"b4.slot.{index:03d}", False, (), None) for index in range(9)))
    raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "unknown arm")


def _ppb_projection(state: PPB1BankState) -> object:
    return (
        state.schema_version,
        state.bank_id,
        state.config_digest,
        state.accepted_step_count,
        state.source_clock_id,
        state.last_source_window_end_tick,
        tuple(
            (
                slot.slot_id,
                slot.occupied,
                tuple(slot.prototype_values),
                slot.support_count,
                slot.last_selected_step,
            )
            for slot in state.slots
        ),
    )


def _two_level_payload(
    generation: int,
    accepted_count: int,
    fast_slots: Iterable[object],
    auditory_ppb: PPB1BankState,
    visual_ppb: PPB1BankState,
    *,
    fast_slot_prefix: str,
    source_clocks: tuple[str | None, int | None, str | None, int | None],
) -> object:
    fast_slots = tuple(fast_slots)
    if tuple(slot.slot_id for slot in fast_slots) != tuple(
        f"{fast_slot_prefix}.slot.{index:03d}" for index in range(3)
    ):
        raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "fast slot identity or order differs")
    normalized_slots = []
    for slot in fast_slots:
        normalized_slots.append(
            (
                slot.occupied,
                tuple(slot.auditory_values),
                tuple(slot.visual_values),
                slot.support_count,
                slot.last_selected_step,
                slot.consolidation_count,
            )
        )
    auditory_payload = _ppb_projection(auditory_ppb)
    visual_payload = _ppb_projection(visual_ppb)
    if generation == 0:
        # Keep the registered empty descriptor only after checking its sources.
        profile = _runtime_profile()
        expected_banks = tuple(
            (
                config.schema_version,
                config.bank_id,
                config.digest(),
                0,
                None,
                None,
                tuple(
                    (f"{config.bank_id}.slot.{index:03d}", False, (), None, None)
                    for index in range(config.capacity)
                ),
            )
            for config in (profile.auditory_config, profile.visual_config)
        )
        if (
            accepted_count != 0
            or source_clocks != (None, None, None, None)
            or tuple(normalized_slots) != tuple((False, (), (), None, None, 0) for _ in range(3))
            or (auditory_payload, visual_payload) != expected_banks
        ):
            raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "initial two-level identity differs")
        return _initial_payload("R0")
    return (
        "s2dr.two-level.normalized.v1",
        generation,
        accepted_count,
        source_clocks,
        tuple(normalized_slots),
        auditory_payload,
        visual_payload,
    )


def _state_payload(arm_id: str, state: object) -> object:
    if arm_id == "TSPM1":
        if type(state) is not tspm1.TSPM1CompositeState:
            raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "TSPM-1 state required")
        return _two_level_payload(
            state.generation,
            state.fast_state.accepted_exposure_count,
            state.fast_state.slots,
            state.auditory_ppb1_state,
            state.visual_ppb1_state,
            fast_slot_prefix="tspm1.fast",
            source_clocks=(
                state.fast_state.auditory_source_clock_id,
                state.fast_state.auditory_last_end_tick,
                state.fast_state.visual_source_clock_id,
                state.fast_state.visual_last_end_tick,
            ),
        )
    if arm_id == "R0":
        if type(state) is not _GenericTwoLevelState:
            raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "R0 state required")
        return _two_level_payload(
            state.generation,
            state.fast.accepted_count,
            state.fast.slots,
            state.auditory_ppb,
            state.visual_ppb,
            fast_slot_prefix="r0.fast",
            source_clocks=(
                state.fast.auditory_clock_id,
                state.fast.auditory_end_tick,
                state.fast.visual_clock_id,
                state.fast.visual_end_tick,
            ),
        )
    if arm_id == "B0":
        if state != ():
            raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "B0 state required")
        return _initial_payload("B0")
    if arm_id in {"B1_DIRECT", "B1_BUDGET_MATCHED"}:
        if type(state) is not _PPBPairState:
            raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "PPB pair state required")
        if state.auditory.accepted_step_count == state.visual.accepted_step_count == 0:
            return _initial_payload(arm_id)
    if arm_id == "B2" and type(state) is _B2State and state.accepted_count == 0:
        return _initial_payload("B2")
    if arm_id == "B3" and type(state) is _B3State and state.accepted_count == 0:
        return _initial_payload("B3")
    if arm_id == "B4" and type(state) is _B4State and state.accepted_count == 0:
        return _initial_payload("B4")
    return _canonical(state)


def _joint_values(pair_id: str) -> tuple[float, ...]:
    try:
        auditory, visual = PAIR_SCALARS[pair_id]
    except KeyError as exc:
        raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "unknown pair") from exc
    return tuple(auditory for _ in AUDITORY_CARRIERS) + tuple(visual for _ in VISUAL_CARRIERS)


def _world() -> BrowserWorldContract:
    return BrowserWorldContract(
        contract_id="synthetic.s2dr.world.v1",
        startup_frame_count=1,
        start_lead_ns=1,
        movement_cycles=1,
        tone_frequency_hz=100.0,
        phases=(
            BrowserWorldPhase("rest.before", 10, "static", 0.0),
            BrowserWorldPhase("change", 10, "moving", 0.2),
            BrowserWorldPhase("rest.after", 10, "static", 0.0),
        ),
    )


def _sequence(modality_config, scalar: float, frame_index: int, history_id: str, role: str):
    start = (frame_index - 1) * 10
    frame = ReceptorContactFrame(
        modality_config.modality_id,
        modality_config.geometry_id,
        f"s2dr.{history_id.lower()}.{role}.{frame_index:03d}.{modality_config.modality_id}",
        f"s2dr.source.{modality_config.modality_id}",
        start,
        start + 10,
        modality_config.carrier_ids,
        tuple(scalar for _ in modality_config.carrier_ids),
    )
    timed = OrganismTimedReceptorFrame(frame, CommonFieldTime("field.synthetic.s2dq", start, start + 10))
    return ReceptorTimeSequence(modality_config.modality_id, modality_config.geometry_id, "field.synthetic.s2dq", (timed,))


def _bound_pair(history_id: str, pair_id: str, frame_index: int, role: str):
    profile = _runtime_profile()
    auditory_scalar, visual_scalar = PAIR_SCALARS[pair_id]
    auditory = _sequence(profile.auditory_config, auditory_scalar, frame_index, history_id, role)
    visual = _sequence(profile.visual_config, visual_scalar, frame_index, history_id, role)
    world = _world()
    batch = BrowserReceptorSequenceBatch(world.contract_id, world.digest(), (auditory, visual))
    envelope = bind_ppb1_active_receptor_batch(f"s2dr.binding.{history_id.lower()}.{role}.{frame_index:03d}", world, batch, profile)
    return profile, envelope, envelope.auditory_stream.timed_frames[0], envelope.visual_stream.timed_frames[0]


def _validate_operator_inputs(
    config: S2DRConfigRecord,
    fixture: S2DRFixtureRecord,
    arm: S2DRArmSpec,
) -> None:
    if type(config) is not S2DRConfigRecord or type(fixture) is not S2DRFixtureRecord or type(arm) is not S2DRArmSpec:
        raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "exact registry records are required")


def _split_distance(left: tuple[float, ...], right: tuple[float, ...]) -> tuple[float, float]:
    return (
        normalized_mean_l1_distance(left[:8], right[:8]),
        normalized_mean_l1_distance(left[8:], right[8:]),
    )


def _advance_b2(state: _B2State, values: tuple[float, ...], formation_index: int):
    if type(state) is not _B2State:
        raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "B2 state required")
    slots = []
    for slot in state.slots:
        if slot.occupied and slot.last_selected_step is not None and formation_index - slot.last_selected_step >= 8:
            slots.append(_JointSlot(slot.slot_id, False, (), None, None))
        else:
            slots.append(slot)
    matches = []
    distance_terms = 0
    for index, slot in enumerate(slots):
        if slot.occupied:
            auditory, visual = _split_distance(values, slot.values)
            distance_terms += 26
            if auditory <= 0.2 and visual <= 0.2:
                matches.append((max(auditory, visual), auditory + visual, slot.slot_id, index))
    if matches:
        _, _, _, selected_index = min(matches)
        selected = slots[selected_index]
        updated = tuple(0.5 * old + 0.5 * current for old, current in zip(selected.values, values, strict=True))
        slots[selected_index] = _JointSlot(
            selected.slot_id,
            True,
            updated,
            min(3, (selected.support or 0) + 1),
            formation_index,
        )
        event = "B2_UPDATED"
    else:
        free = [index for index, slot in enumerate(slots) if not slot.occupied]
        if free:
            selected_index = min(free, key=lambda index: slots[index].slot_id)
            event = "B2_CREATED"
        else:
            selected_index = min(
                range(len(slots)),
                key=lambda index: (slots[index].last_selected_step, slots[index].slot_id),
            )
            event = "B2_REPLACED"
        selected = slots[selected_index]
        slots[selected_index] = _JointSlot(selected.slot_id, True, values, 1, formation_index)
    poststate = _B2State(state.accepted_count + 1, tuple(slots))
    return poststate, {"event": event, "slot_id": slots[selected_index].slot_id}, (29, distance_terms)


def _advance_b3(state: _B3State, values: tuple[float, ...], formation_index: int):
    if type(state) is not _B3State:
        raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "B3 state required")
    if state.occupied:
        updated = tuple(0.5 * old + 0.5 * current for old, current in zip(state.values, values, strict=True))
        event = "B3_UPDATED"
    else:
        updated = values
        event = "B3_CREATED"
    return _B3State(True, updated, formation_index, state.accepted_count + 1), {"event": event}, (29, 26 if state.occupied else 0)


def _advance_b4(state: _B4State, values: tuple[float, ...], formation_index: int):
    if type(state) is not _B4State:
        raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "B4 state required")
    entries = list(state.entries)
    free = [index for index, entry in enumerate(entries) if not entry.occupied]
    if free:
        selected_index = min(free, key=lambda index: entries[index].slot_id)
        event = "B4_APPENDED"
    else:
        selected_index = min(
            range(len(entries)),
            key=lambda index: (entries[index].formation_index, entries[index].slot_id),
        )
        event = "B4_EVICTED_AND_APPENDED"
    selected = entries[selected_index]
    entries[selected_index] = _FIFOEntry(selected.slot_id, True, values, formation_index)
    return _B4State(state.accepted_count + 1, tuple(entries)), {"event": event, "slot_id": selected.slot_id}, (27, 0)


def _advance_r0(
    state: _GenericTwoLevelState,
    auditory_frame: ReceptorContactFrame,
    visual_frame: ReceptorContactFrame,
) -> tuple[_GenericTwoLevelState, object, tuple[int, int]]:
    if type(state) is not _GenericTwoLevelState:
        raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "generic R0 state required")
    auditory_values = tuple(auditory_frame.values)
    visual_values = tuple(visual_frame.values)
    step = state.fast.accepted_count + 1
    slots = []
    for slot in state.fast.slots:
        if (
            slot.occupied
            and slot.last_selected_step is not None
            and step - slot.last_selected_step >= 8
        ):
            slots.append(_GenericFastSlot(slot.slot_id, False, (), (), None, None, 0))
        else:
            slots.append(slot)
    matches = []
    any_auditory_match = False
    any_visual_match = False
    for index, slot in enumerate(slots):
        if not slot.occupied:
            continue
        auditory_distance = normalized_mean_l1_distance(auditory_values, slot.auditory_values)
        visual_distance = normalized_mean_l1_distance(visual_values, slot.visual_values)
        auditory_match = auditory_distance <= 0.2
        visual_match = visual_distance <= 0.2
        any_auditory_match = any_auditory_match or auditory_match
        any_visual_match = any_visual_match or visual_match
        if auditory_match and visual_match:
            matches.append(
                (
                    max(auditory_distance, visual_distance),
                    auditory_distance + visual_distance,
                    index,
                    auditory_distance,
                    visual_distance,
                )
            )
    consolidation_eligible = False
    if matches:
        _, _, selected_index, auditory_distance, visual_distance = min(matches)
        selected = slots[selected_index]
        support = min(2, (selected.support_count or 0) + 1)
        slots[selected_index] = _GenericFastSlot(
            selected.slot_id,
            True,
            tuple(0.5 * old + 0.5 * current for old, current in zip(selected.auditory_values, auditory_values, strict=True)),
            tuple(0.5 * old + 0.5 * current for old, current in zip(selected.visual_values, visual_values, strict=True)),
            support,
            step,
            selected.consolidation_count,
        )
        event = "FAST_UPDATED"
        consolidation_eligible = support >= 2
    else:
        free = [index for index, slot in enumerate(slots) if not slot.occupied]
        if free:
            selected_index = min(free)
            event = "FAST_CREATED"
        else:
            selected_index = min(
                range(len(slots)),
                key=lambda index: (slots[index].last_selected_step, index),
            )
            event = "FAST_REPLACED"
        selected = slots[selected_index]
        slots[selected_index] = _GenericFastSlot(
            selected.slot_id,
            True,
            auditory_values,
            visual_values,
            1,
            step,
            0,
        )
        auditory_distance = None
        visual_distance = None
    fast = _GenericFastState(
        step,
        auditory_frame.clock_id,
        auditory_frame.window_end_tick,
        visual_frame.clock_id,
        visual_frame.window_end_tick,
        tuple(slots),
    )
    if consolidation_eligible:
        auditory_result = advance_ppb1_bank(
            _runtime_profile().auditory_config,
            state.auditory_ppb,
            auditory_frame,
        )
        visual_result = advance_ppb1_bank(
            _runtime_profile().visual_config,
            state.visual_ppb,
            visual_frame,
        )
        selected = fast.slots[selected_index]
        updated_slots = list(fast.slots)
        updated_slots[selected_index] = _GenericFastSlot(
            selected.slot_id,
            selected.occupied,
            selected.auditory_values,
            selected.visual_values,
            selected.support_count,
            selected.last_selected_step,
            selected.consolidation_count + 1,
        )
        fast = _GenericFastState(
            fast.accepted_count,
            fast.auditory_clock_id,
            fast.auditory_end_tick,
            fast.visual_clock_id,
            fast.visual_end_tick,
            tuple(updated_slots),
        )
        auditory_ppb = auditory_result.poststate
        visual_ppb = visual_result.poststate
        consolidation_status = "COMMITTED"
    else:
        auditory_ppb = state.auditory_ppb
        visual_ppb = state.visual_ppb
        consolidation_status = "NOT_ELIGIBLE"
    poststate = _GenericTwoLevelState(
        state.generation + 1,
        fast,
        auditory_ppb,
        visual_ppb,
    )
    event_payload = {
        "event": event,
        "consolidation_status": consolidation_status,
        "generic_decision_digest": _digest(
            (
                "s2dr.r0.generic.transition.v1",
                state.generation,
                step,
                selected_index,
                auditory_distance,
                visual_distance,
                consolidation_status,
            )
        ),
    }
    return poststate, event_payload, (293, 234)


def advance_s2dr_arm(
    config: S2DRConfigRecord,
    fixture: S2DRFixtureRecord,
    arm: S2DRArmSpec,
    prestate: object,
    pair_id: str,
    formation_index: int,
) -> tuple[object, object, tuple[int, int]]:
    """Advance exactly one private arm by one registered formation frame."""

    _validate_operator_inputs(config, fixture, arm)
    if isinstance(formation_index, bool) or not isinstance(formation_index, int) or not 1 <= formation_index <= len(fixture.formation_pair_ids):
        raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "formation index is invalid")
    if fixture.formation_pair_ids[formation_index - 1] != pair_id:
        raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "formation pair is not registered")
    values = _joint_values(pair_id)
    if arm.arm_id == "B0":
        if prestate != ():
            raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "B0 state changed")
        return (), {"event": "B0_IGNORED", "formation_index": formation_index}, (0, 0)
    if arm.arm_id == "B2":
        return _advance_b2(prestate, values, formation_index)
    if arm.arm_id == "B3":
        return _advance_b3(prestate, values, formation_index)
    if arm.arm_id == "B4":
        return _advance_b4(prestate, values, formation_index)
    profile, envelope, auditory, visual = _bound_pair(
        fixture.history_id, pair_id, formation_index, "formation"
    )
    if arm.arm_id in {"B1_DIRECT", "B1_BUDGET_MATCHED"}:
        if type(prestate) is not _PPBPairState:
            raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "PPB pair state required")
        if arm.arm_id == "B1_BUDGET_MATCHED" and formation_index not in fixture.ppb_budget_indices:
            return prestate, {"event": "B1_BUDGET_SKIPPED", "formation_index": formation_index}, (0, 0)
        auditory_result = advance_ppb1_bank(profile.auditory_config, prestate.auditory, auditory.timed_frame.frame)
        visual_result = advance_ppb1_bank(profile.visual_config, prestate.visual, visual.timed_frame.frame)
        return (
            _PPBPairState(auditory_result.poststate, visual_result.poststate),
            {
                "event": "B1_PPB1_ADVANCED",
                "auditory_event": auditory_result.readout.event,
                "visual_event": visual_result.readout.event,
            },
            (176, 0),
        )
    if arm.arm_id == "R0":
        return _advance_r0(
            prestate,
            auditory.timed_frame.frame,
            visual.timed_frame.frame,
        )
    _, binding = _runtime_tspm_config()
    if arm.arm_id == "TSPM1":
        if type(prestate) is not tspm1.TSPM1CompositeState:
            raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "TSPM-1 state required")
        tspm_prestate = prestate
    else:
        raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "unknown arm")
    exposure = tspm1.bind_tspm1_exposure(binding, envelope, auditory, visual)
    owner = tspm1.TSPM1CoordinatorOwner(
        f"s2dr.tspm1.owner.{fixture.history_id.lower()}.{formation_index:03d}",
        f"s2dr.tspm1.authorization.{fixture.history_id.lower()}.{formation_index:03d}",
        f"s2dr.tspm1.consume.{fixture.history_id.lower()}.{formation_index:03d}",
        binding.config_binding_digest,
        tspm_prestate.composite_state_digest,
        exposure.exposure_digest,
    )
    result = owner.consume_once(binding, tspm_prestate, exposure)
    event = {
        "event": result.receipt.primary_event,
        "consolidation_status": result.receipt.consolidation_status,
        "receipt_digest": result.receipt.receipt_digest,
    }
    return result.poststate, event, (293, 234)


def _s1wu_evidence(
    bank_config,
    bank_state: PPB1BankState,
    frame: ReceptorContactFrame,
    probe_id: str,
) -> tuple[str, S1WUReadOnlyPerceptualFinding | None, tuple[float, ...] | None]:
    if bank_state.accepted_step_count == 0:
        return "SLOW_UNAVAILABLE", None, None
    finding = probe_s1wu_perceptual_state(bank_config, bank_state, frame, probe_id)
    if type(finding) is not S1WUReadOnlyPerceptualFinding:
        raise S2DRError(S2DR_ATOMIC_RESULT_REQUIRED, "exact S1WU finding required")
    if not finding.recognized:
        return "SLOW_NOT_RECOGNIZED", finding, None
    matching = tuple(
        slot
        for slot in bank_state.slots
        if slot.slot_id == finding.selected_slot_id and slot.occupied
    )
    if len(matching) != 1:
        raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "S1WU selected slot is not unique")
    return "SLOW_RECOGNIZED", finding, tuple(matching[0].prototype_values)


def _finding_payload(
    fixture: S2DRFixtureRecord,
    arm: S2DRArmSpec,
    checkpoint: int,
    pair_id: str,
    recognized: bool,
    context_source: str,
    observed_state_digest: str,
    *,
    fast_recognized: bool | None = None,
    fast_slot_id: str | None = None,
    fast_slot_digest: str | None = None,
    auditory_fast_distance: float | None = None,
    visual_fast_distance: float | None = None,
    auditory_slow_status: str | None = None,
    visual_slow_status: str | None = None,
    auditory_slow_finding_digest: str | None = None,
    visual_slow_finding_digest: str | None = None,
    auditory_selected_slot_id: str | None = None,
    visual_selected_slot_id: str | None = None,
    auditory_selected_prototype_digest: str | None = None,
    visual_selected_prototype_digest: str | None = None,
    auditory_slow_distance: float | None = None,
    visual_slow_distance: float | None = None,
    selected_values: tuple[tuple[float, ...], tuple[float, ...]] | None = None,
) -> dict[str, object]:
    selected_digest = None
    if selected_values is not None:
        selected_digest = _digest(("S2DR_SELECTED_AV_PAYLOAD_V1", selected_values[0], selected_values[1]))
    return {
        "history_id": fixture.history_id,
        "arm_id": arm.arm_id,
        "checkpoint": checkpoint,
        "pair_id": pair_id,
        "recognized": recognized,
        "context_source": context_source,
        "fast_recognized": fast_recognized,
        "fast_slot_id": fast_slot_id,
        "fast_slot_digest": fast_slot_digest,
        "auditory_fast_distance": auditory_fast_distance,
        "visual_fast_distance": visual_fast_distance,
        "auditory_slow_status": auditory_slow_status,
        "visual_slow_status": visual_slow_status,
        "auditory_slow_finding_digest": auditory_slow_finding_digest,
        "visual_slow_finding_digest": visual_slow_finding_digest,
        "auditory_selected_slot_id": auditory_selected_slot_id,
        "visual_selected_slot_id": visual_selected_slot_id,
        "auditory_selected_prototype_digest": auditory_selected_prototype_digest,
        "visual_selected_prototype_digest": visual_selected_prototype_digest,
        "auditory_slow_distance": auditory_slow_distance,
        "visual_slow_distance": visual_slow_distance,
        "selected_av_payload_digest": selected_digest,
        "observed_state_digest": observed_state_digest,
    }


def _probe_joint_slots(slots: Iterable[tuple[str, tuple[float, ...], int]], values: tuple[float, ...]):
    candidates = []
    for slot_id, stored, rank_step in slots:
        auditory, visual = _split_distance(values, stored)
        if auditory <= 0.2 and visual <= 0.2:
            candidates.append((max(auditory, visual), auditory + visual, -rank_step, slot_id, stored, auditory, visual))
    return min(candidates, default=None)


def probe_s2dr_arm(
    config: S2DRConfigRecord,
    fixture: S2DRFixtureRecord,
    arm: S2DRArmSpec,
    state: object,
    pair_id: str,
    probe_index: int,
) -> tuple[object, int]:
    """Read one registered probe without modifying the arm state."""

    _validate_operator_inputs(config, fixture, arm)
    flattened = tuple((after, pair) for after, pairs in fixture.probe_specs for pair in pairs)
    if isinstance(probe_index, bool) or not isinstance(probe_index, int) or not 1 <= probe_index <= len(flattened):
        raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "probe index is invalid")
    checkpoint, expected_pair = flattened[probe_index - 1]
    if pair_id != expected_pair:
        raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "probe pair is stale or foreign")
    state_payload = _state_payload(arm.arm_id, state)
    state_digest = _digest(state_payload)
    values = _joint_values(pair_id)
    if arm.arm_id == "B0":
        return _finding_payload(fixture, arm, checkpoint, pair_id, False, "NO_COMPLETE_CONTEXT", state_digest), 0
    if arm.arm_id == "B2":
        assert type(state) is _B2State
        occupied = ((slot.slot_id, slot.values, slot.last_selected_step or 0) for slot in state.slots if slot.occupied)
        selected = _probe_joint_slots(occupied, values)
        recognized = selected is not None
        return _finding_payload(
            fixture, arm, checkpoint, pair_id, recognized,
            "ADAPTIVE_PROTOTYPE_CONTEXT" if recognized else "NO_COMPLETE_CONTEXT",
            state_digest,
            fast_recognized=recognized,
            fast_slot_id=selected[3] if selected else None,
            auditory_fast_distance=selected[5] if selected else None,
            visual_fast_distance=selected[6] if selected else None,
            selected_values=(selected[4][:8], selected[4][8:]) if selected else None,
        ), sum(26 for slot in state.slots if slot.occupied)
    if arm.arm_id == "B3":
        assert type(state) is _B3State
        selected = None
        if state.occupied and state.last_formation_step is not None and state.accepted_count - state.last_formation_step < 8:
            auditory, visual = _split_distance(values, state.values)
            if auditory <= 0.2 and visual <= 0.2:
                selected = (auditory, visual)
        return _finding_payload(
            fixture, arm, checkpoint, pair_id, selected is not None,
            "REVERBERATION_CONTEXT" if selected else "NO_COMPLETE_CONTEXT", state_digest,
            fast_recognized=selected is not None,
            auditory_fast_distance=selected[0] if selected else None,
            visual_fast_distance=selected[1] if selected else None,
            selected_values=(state.values[:8], state.values[8:]) if selected else None,
        ), 26 if state.occupied else 0
    if arm.arm_id == "B4":
        assert type(state) is _B4State
        occupied = ((entry.slot_id, entry.values, entry.formation_index or 0) for entry in state.entries if entry.occupied)
        selected = _probe_joint_slots(occupied, values)
        return _finding_payload(
            fixture, arm, checkpoint, pair_id, selected is not None,
            "FIFO_CONTEXT" if selected else "NO_COMPLETE_CONTEXT", state_digest,
            fast_recognized=selected is not None,
            fast_slot_id=selected[3] if selected else None,
            auditory_fast_distance=selected[5] if selected else None,
            visual_fast_distance=selected[6] if selected else None,
            selected_values=(selected[4][:8], selected[4][8:]) if selected else None,
        ), sum(26 for entry in state.entries if entry.occupied)

    frame_index = len(fixture.formation_pair_ids) + probe_index
    profile, envelope, auditory, visual = _bound_pair(fixture.history_id, pair_id, frame_index, "probe")
    auditory_values = tuple(auditory.timed_frame.frame.values)
    visual_values = tuple(visual.timed_frame.frame.values)
    if arm.arm_id in {"B1_DIRECT", "B1_BUDGET_MATCHED"}:
        if type(state) is not _PPBPairState:
            raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "PPB pair state required")
        probe_token = _digest((fixture.history_id, arm.arm_id, checkpoint, pair_id, probe_index))
        auditory_status, auditory_finding, auditory_selected_values = _s1wu_evidence(
            profile.auditory_config,
            state.auditory,
            auditory.timed_frame.frame,
            f"s2dr.b1.probe.auditory.{probe_token}",
        )
        visual_status, visual_finding, visual_selected_values = _s1wu_evidence(
            profile.visual_config,
            state.visual,
            visual.timed_frame.frame,
            f"s2dr.b1.probe.visual.{probe_token}",
        )
        recognized = auditory_status == visual_status == "SLOW_RECOGNIZED"
        selected_values = (
            (auditory_selected_values, visual_selected_values)
            if recognized
            else None
        )
        return _finding_payload(
            fixture, arm, checkpoint, pair_id, recognized,
            "SLOW_PPB1_CONTEXT" if recognized else "NO_COMPLETE_CONTEXT", state_digest,
            auditory_slow_status=auditory_status,
            visual_slow_status=visual_status,
            auditory_slow_finding_digest=auditory_finding.finding_digest if auditory_finding else None,
            visual_slow_finding_digest=visual_finding.finding_digest if visual_finding else None,
            auditory_selected_slot_id=auditory_finding.selected_slot_id if auditory_finding and auditory_finding.recognized else None,
            visual_selected_slot_id=visual_finding.selected_slot_id if visual_finding and visual_finding.recognized else None,
            auditory_selected_prototype_digest=auditory_finding.selected_prototype_digest if auditory_finding and auditory_finding.recognized else None,
            visual_selected_prototype_digest=visual_finding.selected_prototype_digest if visual_finding and visual_finding.recognized else None,
            auditory_slow_distance=auditory_finding.match_distance if auditory_finding and auditory_finding.recognized else None,
            visual_slow_distance=visual_finding.match_distance if visual_finding and visual_finding.recognized else None,
            selected_values=selected_values,
        ), 8 * sum(slot.occupied for slot in state.auditory.slots) + 18 * sum(slot.occupied for slot in state.visual.slots)

    if arm.arm_id == "R0":
        if type(state) is not _GenericTwoLevelState:
            raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "generic R0 state required")
        matches = []
        for slot in state.fast.slots:
            if not slot.occupied:
                continue
            auditory_distance = normalized_mean_l1_distance(auditory_values, slot.auditory_values)
            visual_distance = normalized_mean_l1_distance(visual_values, slot.visual_values)
            if auditory_distance <= 0.2 and visual_distance <= 0.2:
                matches.append((max(auditory_distance, visual_distance), auditory_distance + visual_distance, slot.slot_id, auditory_distance, visual_distance, slot))
        if matches:
            _, _, _, auditory_fast_distance, visual_fast_distance, fast_slot = min(matches)
        else:
            fast_slot = None
            auditory_fast_distance = None
            visual_fast_distance = None
        probe_token = _digest((fixture.history_id, arm.arm_id, checkpoint, pair_id, probe_index))
        auditory_status, auditory_finding, auditory_selected_values = _s1wu_evidence(
            profile.auditory_config,
            state.auditory_ppb,
            auditory.timed_frame.frame,
            f"s2dr.r0.probe.auditory.{probe_token}",
        )
        visual_status, visual_finding, visual_selected_values = _s1wu_evidence(
            profile.visual_config,
            state.visual_ppb,
            visual.timed_frame.frame,
            f"s2dr.r0.probe.visual.{probe_token}",
        )
        both_slow = auditory_status == visual_status == "SLOW_RECOGNIZED"
        context_source = "SLOW_PPB1_CONTEXT" if both_slow else ("FAST_ASSOCIATIVE_CONTEXT" if fast_slot else "NO_COMPLETE_CONTEXT")
        selected_values = (
            (auditory_selected_values, visual_selected_values)
            if both_slow
            else ((fast_slot.auditory_values, fast_slot.visual_values) if fast_slot else None)
        )
        return _finding_payload(
            fixture,
            arm,
            checkpoint,
            pair_id,
            context_source != "NO_COMPLETE_CONTEXT",
            context_source,
            state_digest,
            fast_recognized=fast_slot is not None,
            fast_slot_id=fast_slot.slot_id if fast_slot else None,
            fast_slot_digest=_digest(_canonical(fast_slot)) if fast_slot else None,
            auditory_fast_distance=auditory_fast_distance,
            visual_fast_distance=visual_fast_distance,
            auditory_slow_status=auditory_status,
            visual_slow_status=visual_status,
            auditory_slow_finding_digest=auditory_finding.finding_digest if auditory_finding else None,
            visual_slow_finding_digest=visual_finding.finding_digest if visual_finding else None,
            auditory_selected_slot_id=auditory_finding.selected_slot_id if auditory_finding and auditory_finding.recognized else None,
            visual_selected_slot_id=visual_finding.selected_slot_id if visual_finding and visual_finding.recognized else None,
            auditory_selected_prototype_digest=auditory_finding.selected_prototype_digest if auditory_finding and auditory_finding.recognized else None,
            visual_selected_prototype_digest=visual_finding.selected_prototype_digest if visual_finding and visual_finding.recognized else None,
            auditory_slow_distance=auditory_finding.match_distance if auditory_finding and auditory_finding.recognized else None,
            visual_slow_distance=visual_finding.match_distance if visual_finding and visual_finding.recognized else None,
            selected_values=selected_values,
        ), 234

    _, binding = _runtime_tspm_config()
    if arm.arm_id == "TSPM1":
        if type(state) is not tspm1.TSPM1CompositeState:
            raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "TSPM-1 state required")
        composite = state
    else:
        raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "unknown arm")
    probe = tspm1.bind_tspm1_probe(binding, envelope, auditory, visual)
    finding = tspm1.probe_tspm1_read_only(binding, composite, probe)
    fast_values = None
    if finding.fast_recognized:
        slot = next(slot for slot in composite.fast_state.slots if slot.slot_id == finding.fast_slot_id)
        fast_values = (slot.auditory_values, slot.visual_values)
    auditory_status, auditory_s1wu, auditory_selected_values = _s1wu_evidence(
        profile.auditory_config,
        composite.auditory_ppb1_state,
        auditory.timed_frame.frame,
        f"tspm1.probe.auditory.{probe.probe_digest}",
    )
    visual_status, visual_s1wu, visual_selected_values = _s1wu_evidence(
        profile.visual_config,
        composite.visual_ppb1_state,
        visual.timed_frame.frame,
        f"tspm1.probe.visual.{probe.probe_digest}",
    )
    if (
        auditory_status != finding.auditory_slow_status
        or visual_status != finding.visual_slow_status
        or (auditory_s1wu.finding_digest if auditory_s1wu else None) != finding.auditory_s1wu_finding_digest
        or (visual_s1wu.finding_digest if visual_s1wu else None) != finding.visual_s1wu_finding_digest
    ):
        raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "TSPM slow finding is not bound to S1WU evidence")
    slow_values = None
    if auditory_status == visual_status == "SLOW_RECOGNIZED":
        slow_values = (auditory_selected_values, visual_selected_values)
    selected_values = slow_values if finding.context_source == "SLOW_PPB1_CONTEXT" else fast_values
    normalized = _finding_payload(
        fixture, arm, checkpoint, pair_id,
        finding.context_source != "NO_COMPLETE_CONTEXT",
        finding.context_source,
        state_digest,
        fast_recognized=finding.fast_recognized,
        fast_slot_id=finding.fast_slot_id,
        fast_slot_digest=finding.fast_slot_digest,
        auditory_fast_distance=finding.auditory_fast_distance,
        visual_fast_distance=finding.visual_fast_distance,
        auditory_slow_status=finding.auditory_slow_status,
        visual_slow_status=finding.visual_slow_status,
        auditory_slow_finding_digest=finding.auditory_s1wu_finding_digest,
        visual_slow_finding_digest=finding.visual_s1wu_finding_digest,
        auditory_selected_slot_id=auditory_s1wu.selected_slot_id if auditory_s1wu and auditory_s1wu.recognized else None,
        visual_selected_slot_id=visual_s1wu.selected_slot_id if visual_s1wu and visual_s1wu.recognized else None,
        auditory_selected_prototype_digest=auditory_s1wu.selected_prototype_digest if auditory_s1wu and auditory_s1wu.recognized else None,
        visual_selected_prototype_digest=visual_s1wu.selected_prototype_digest if visual_s1wu and visual_s1wu.recognized else None,
        auditory_slow_distance=auditory_s1wu.match_distance if auditory_s1wu and auditory_s1wu.recognized else None,
        visual_slow_distance=visual_s1wu.match_distance if visual_s1wu and visual_s1wu.recognized else None,
        selected_values=selected_values,
    )
    return normalized, 234


@dataclass(frozen=True, slots=True)
class S2DRCellOwnerSnapshot:
    owner_id: str
    cell_id: str
    authorization_digest: str
    consumption_id: str
    status: str
    cell_plan_digest: str
    internal_error_code: str | None
    committed_result_digest: str | None


def _budget_tuples(counts: Sequence[int], bound: int) -> tuple[
    tuple[tuple[int, int], ...],
    tuple[tuple[int, int], ...],
    tuple[tuple[int, int], ...],
]:
    bounds = tuple((index, bound) for index in range(1, len(counts) + 1))
    used = tuple((index, int(value)) for index, value in enumerate(counts, start=1))
    remaining = tuple((index, bound - int(value)) for index, value in enumerate(counts, start=1))
    return bounds, used, remaining


def _make_budget_receipt(
    plan: S2DRCellPlan,
    arm: S2DRArmSpec,
    formation_writes: Sequence[int],
    formation_distances: Sequence[int],
    probe_distances: Sequence[int],
    probe_writes: Sequence[int],
) -> S2DRBudgetReceipt:
    fw_bounds, fw_counts, fw_remaining = _budget_tuples(formation_writes, arm.formation_write_limit)
    fd_bounds, fd_counts, fd_remaining = _budget_tuples(formation_distances, arm.formation_distance_limit)
    pd_bounds, pd_counts, pd_remaining = _budget_tuples(probe_distances, arm.probe_distance_limit)
    pw_bounds, pw_counts, pw_remaining = _budget_tuples(probe_writes, arm.probe_write_limit)
    return _built(
        S2DRBudgetReceipt,
        "budget_receipt_digest",
        schema_version=S2DR_SCHEMA_VERSION,
        cell_id=plan.cell_id,
        cell_plan_digest=plan.cell_plan_digest,
        resource_words_bound=arm.resource_words,
        resource_words_used=arm.resource_words,
        formation_write_bounds=fw_bounds,
        formation_write_counts=fw_counts,
        formation_distance_bounds=fd_bounds,
        formation_distance_counts=fd_counts,
        probe_distance_bounds=pd_bounds,
        probe_distance_counts=pd_counts,
        probe_write_bounds=pw_bounds,
        probe_write_counts=pw_counts,
        remaining_resource_words=0,
        remaining_formation_write_budget=fw_remaining,
        remaining_formation_distance_budget=fd_remaining,
        remaining_probe_distance_budget=pd_remaining,
        remaining_probe_write_budget=pw_remaining,
    )


def _expected_budget_keys(plan: S2DRCellPlan) -> tuple[tuple[int, ...], tuple[int, ...]]:
    return (
        tuple(range(1, plan.formation_call_count + 1)),
        tuple(range(1, plan.probe_call_count + 1)),
    )


def validate_s2dr_cell_result(
    config: S2DRConfigRecord,
    fixture: S2DRFixtureRecord,
    arm: S2DRArmSpec,
    plan: S2DRCellPlan,
    result: S2DRCellResult,
) -> S2DRCellResult:
    """Relationally validate one complete cell result and its budget."""

    _validate_operator_inputs(config, fixture, arm)
    if type(plan) is not S2DRCellPlan or type(result) is not S2DRCellResult:
        raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "exact plan and result are required")
    _validate_record(plan, "cell_plan_digest")
    _validate_record(result, "cell_result_digest")
    budget = result.budget_receipt
    receipt = result.cell_receipt
    if (
        result.cell_id != plan.cell_id
        or result.cell_plan_digest != plan.cell_plan_digest
        or budget.cell_id != plan.cell_id
        or budget.cell_plan_digest != plan.cell_plan_digest
        or receipt.cell_id != plan.cell_id
        or receipt.cell_plan_digest != plan.cell_plan_digest
        or receipt.config_digest != config.config_digest
        or receipt.fixture_digest != fixture.fixture_digest
        or receipt.arm_spec_digest != arm.arm_spec_digest
        or result.prestate_digest != plan.initial_state_digest
        or receipt.prestate_digest != result.prestate_digest
        or receipt.event_digest != _digest(result.event_payloads)
        or receipt.finding_digest != _digest(result.finding_payloads)
        or receipt.budget_receipt_digest != budget.budget_receipt_digest
        or receipt.poststate_digest != result.poststate_digest
        or receipt.owner_terminal_state != "COMMITTED"
        or receipt.internal_error_code is not None
    ):
        raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "cell result relations differ")
    formation_keys, probe_keys = _expected_budget_keys(plan)
    formation_groups = (
        (budget.formation_write_bounds, budget.formation_write_counts, budget.remaining_formation_write_budget, arm.formation_write_limit),
        (budget.formation_distance_bounds, budget.formation_distance_counts, budget.remaining_formation_distance_budget, arm.formation_distance_limit),
    )
    probe_groups = (
        (budget.probe_distance_bounds, budget.probe_distance_counts, budget.remaining_probe_distance_budget, arm.probe_distance_limit),
        (budget.probe_write_bounds, budget.probe_write_counts, budget.remaining_probe_write_budget, arm.probe_write_limit),
    )
    if budget.resource_words_bound != arm.resource_words:
        raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "resource bound source differs")
    for bounds, counts, remaining, expected_bound in formation_groups:
        if tuple(key for key, _ in bounds) != formation_keys or tuple(key for key, _ in counts) != formation_keys or tuple(key for key, _ in remaining) != formation_keys:
            raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "formation budget keys differ")
        if any(bound != expected_bound for _, bound in bounds):
            raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "formation bound source differs")
        if any(rest != bound - used for (_, bound), (_, used), (_, rest) in zip(bounds, counts, remaining, strict=True)):
            raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "formation budget arithmetic differs")
    for bounds, counts, remaining, expected_bound in probe_groups:
        if tuple(key for key, _ in bounds) != probe_keys or tuple(key for key, _ in counts) != probe_keys or tuple(key for key, _ in remaining) != probe_keys:
            raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "probe budget keys differ")
        if any(bound != expected_bound for _, bound in bounds):
            raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "probe bound source differs")
        if any(rest != bound - used for (_, bound), (_, used), (_, rest) in zip(bounds, counts, remaining, strict=True)):
            raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "probe budget arithmetic differs")
    over_limit = budget.resource_words_used > budget.resource_words_bound or budget.remaining_resource_words < 0
    for bounds, counts, remaining, _ in formation_groups + probe_groups:
        over_limit = over_limit or any(
            used > bound or rest < 0
            for (_, bound), (_, used), (_, rest) in zip(bounds, counts, remaining, strict=True)
        )
    if over_limit:
        raise S2DRError(S2DR_RESOURCE_OR_OPERATION_LIMIT_EXCEEDED, "cell budget exceeded")
    return result


class S2DRCellOwner:
    """Single-use fail-closed owner for one private comparison cell."""

    def __init__(
        self,
        owner_id: str,
        cell_id: str,
        authorization_digest: str,
        consumption_id: str,
        cell_plan_digest: str,
        config_digest: str,
        fixture_digest: str,
        arm_spec_digest: str,
        prestate_digest: str,
    ) -> None:
        self._owner_id = _id(owner_id, "owner_id")
        self._cell_id = _id(cell_id, "cell_id")
        self._authorization_digest = authorization_digest
        self._consumption_id = _id(consumption_id, "consumption_id")
        self._cell_plan_digest = cell_plan_digest
        self._config_digest = config_digest
        self._fixture_digest = fixture_digest
        self._arm_spec_digest = arm_spec_digest
        self._prestate_digest = prestate_digest
        if not all(_is_digest(value) for value in (authorization_digest, cell_plan_digest, config_digest, fixture_digest, arm_spec_digest, prestate_digest)):
            raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "owner digest role invalid")
        self._status = "FRESH"
        self._internal_error_code: str | None = None
        self._committed_result_digest: str | None = None
        self._lock = Lock()

    def snapshot(self) -> S2DRCellOwnerSnapshot:
        return S2DRCellOwnerSnapshot(
            self._owner_id,
            self._cell_id,
            self._authorization_digest,
            self._consumption_id,
            self._status,
            self._cell_plan_digest,
            self._internal_error_code,
            self._committed_result_digest,
        )

    def consume_once(
        self,
        config: S2DRConfigRecord,
        fixture: S2DRFixtureRecord,
        arm: S2DRArmSpec,
        plan: S2DRCellPlan,
    ) -> S2DRCellResult:
        if not self._lock.acquire(blocking=False):
            raise S2DRError(S2DR_OWNER_BUSY, "cell owner is busy")
        try:
            if self._status != "FRESH":
                raise S2DRError(S2DR_OWNER_TERMINAL, "cell owner is terminal")
            self._status = "BUSY"
            try:
                _validate_operator_inputs(config, fixture, arm)
                if type(plan) is not S2DRCellPlan:
                    raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "exact cell plan required")
                for record, digest_field in (
                    (config, "config_digest"),
                    (fixture, "fixture_digest"),
                    (arm, "arm_spec_digest"),
                    (plan, "cell_plan_digest"),
                ):
                    _validate_record(record, digest_field)
                expected_authorization = _authorization_digest(
                    plan.cell_id,
                    plan.config_digest,
                    plan.fixture_digest,
                    plan.arm_spec_digest,
                    plan.initial_state_digest,
                )
                if plan.authorization_digest != expected_authorization:
                    raise S2DRError(S2DR_AUTHORIZATION_MISMATCH, "plan authorization is invalid")
                if (
                    self._cell_id != plan.cell_id
                    or self._authorization_digest != plan.authorization_digest
                    or self._cell_plan_digest != plan.cell_plan_digest
                ):
                    raise S2DRError(S2DR_OWNER_AUTHORIZATION_MISMATCH, "owner cell authorization differs")
                if (
                    self._config_digest != plan.config_digest
                    or self._fixture_digest != plan.fixture_digest
                    or self._arm_spec_digest != plan.arm_spec_digest
                    or config.config_digest != plan.config_digest
                    or fixture.fixture_digest != plan.fixture_digest
                    or arm.arm_spec_digest != plan.arm_spec_digest
                    or fixture.history_id != plan.history_id
                    or arm.arm_id != plan.arm_id
                    or self._prestate_digest != plan.initial_state_digest
                    or arm.initial_state_digest != plan.initial_state_digest
                ):
                    raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "fixture, arm, or prestate differs")
                state = initial_s2dr_arm_state(config, arm)
                events = []
                findings = []
                formation_writes = []
                formation_distances = []
                probe_distances = []
                probe_writes = []
                probe_number = 0
                probes_by_checkpoint = {after: pairs for after, pairs in fixture.probe_specs}
                for formation_index, pair_id in enumerate(fixture.formation_pair_ids, start=1):
                    state, event, operations = advance_s2dr_arm(
                        config, fixture, arm, state, pair_id, formation_index
                    )
                    events.append(event)
                    formation_writes.append(operations[0])
                    formation_distances.append(operations[1])
                    for probe_pair_id in probes_by_checkpoint.get(formation_index, ()):
                        probe_number += 1
                        before = _digest(_state_payload(arm.arm_id, state))
                        finding, distance_terms = probe_s2dr_arm(
                            config, fixture, arm, state, probe_pair_id, probe_number
                        )
                        after = _digest(_state_payload(arm.arm_id, state))
                        if before != after:
                            raise S2DRError(S2DR_ATOMIC_RESULT_REQUIRED, "probe changed state")
                        findings.append(finding)
                        probe_distances.append(distance_terms)
                        probe_writes.append(0)
                budget = _make_budget_receipt(
                    plan,
                    arm,
                    formation_writes,
                    formation_distances,
                    probe_distances,
                    probe_writes,
                )
                poststate_payload = _state_payload(arm.arm_id, state)
                poststate_digest = _digest(poststate_payload)
                cell_receipt = _built(
                    S2DRCellReceipt,
                    "cell_receipt_digest",
                    schema_version=S2DR_SCHEMA_VERSION,
                    cell_id=plan.cell_id,
                    cell_plan_digest=plan.cell_plan_digest,
                    config_digest=config.config_digest,
                    fixture_digest=fixture.fixture_digest,
                    arm_spec_digest=arm.arm_spec_digest,
                    prestate_digest=plan.initial_state_digest,
                    event_digest=_digest(tuple(events)),
                    finding_digest=_digest(tuple(findings)),
                    budget_receipt_digest=budget.budget_receipt_digest,
                    poststate_digest=poststate_digest,
                    owner_id=self._owner_id,
                    owner_terminal_state="COMMITTED",
                    internal_error_code=None,
                )
                result = _built(
                    S2DRCellResult,
                    "cell_result_digest",
                    schema_version=S2DR_SCHEMA_VERSION,
                    cell_id=plan.cell_id,
                    cell_plan_digest=plan.cell_plan_digest,
                    prestate_digest=plan.initial_state_digest,
                    event_payloads=tuple(events),
                    finding_payloads=tuple(findings),
                    poststate_payload=poststate_payload,
                    poststate_digest=poststate_digest,
                    budget_receipt=budget,
                    cell_receipt=cell_receipt,
                )
                validate_s2dr_cell_result(config, fixture, arm, plan, result)
                self._status = "COMMITTED"
                self._committed_result_digest = result.cell_result_digest
                return result
            except S2DRError as exc:
                self._status = "FAILED"
                self._internal_error_code = exc.code
                raise S2DRError(S2DR_ATTEMPT_FAILED, f"{exc.code}: {exc.detail}") from exc
        finally:
            self._lock.release()


def _finding(
    results: Mapping[tuple[str, str], S2DRCellResult],
    history_id: str,
    arm_id: str,
    checkpoint: int,
    pair_id: str,
) -> Mapping[str, object] | None:
    result = results.get((history_id, arm_id))
    if result is None:
        return None
    matches = [
        item
        for item in result.finding_payloads
        if isinstance(item, Mapping)
        and item.get("checkpoint") == checkpoint
        and item.get("pair_id") == pair_id
    ]
    return matches[-1] if matches else None


def _predicate_vector(
    results: Mapping[tuple[str, str], S2DRCellResult], arm_id: str
) -> tuple[bool, ...]:
    h1_ax = _finding(results, "H1", arm_id, 1, "AX")
    h3_ax = _finding(results, "H3", arm_id, 12, "AX")
    h2_ax = _finding(results, "H2", arm_id, 4, "AX")
    h4_ax = _finding(results, "H4", arm_id, 6, "AX")
    h4_ay = _finding(results, "H4", arm_id, 6, "AY")
    h4_bx = _finding(results, "H4", arm_id, 6, "BX")
    h5_ax = _finding(results, "H5", arm_id, 8, "AX")
    h5_p4 = _finding(results, "H5", arm_id, 8, "P4")
    h7 = tuple(
        _finding(results, "H7", arm_id, 4, pair_id)
        for pair_id in ("AX", "NEAR", "PARTIAL_OUT", "OUTSIDE", "FAR")
    )
    p1 = bool(h1_ax and h1_ax.get("recognized") and h1_ax.get("fast_recognized"))
    p2 = bool(
        h3_ax
        and h3_ax.get("recognized")
        and h3_ax.get("fast_recognized") is False
        and h3_ax.get("auditory_slow_status") == "SLOW_RECOGNIZED"
        and h3_ax.get("visual_slow_status") == "SLOW_RECOGNIZED"
        and h3_ax.get("auditory_selected_prototype_digest")
        and h3_ax.get("visual_selected_prototype_digest")
    )
    p3 = bool(
        h2_ax and h4_ax and h4_ay and h4_bx
        and h4_ax.get("recognized")
        and h4_ax.get("fast_recognized") is False
        and h4_ax.get("auditory_slow_status") == "SLOW_RECOGNIZED"
        and h4_ax.get("visual_slow_status") == "SLOW_RECOGNIZED"
        and h4_ay.get("fast_recognized") is True
        and h4_bx.get("fast_recognized") is True
        and not (
            h4_ay.get("auditory_slow_status") == "SLOW_RECOGNIZED"
            and h4_ay.get("visual_slow_status") == "SLOW_RECOGNIZED"
        )
        and not (
            h4_bx.get("auditory_slow_status") == "SLOW_RECOGNIZED"
            and h4_bx.get("visual_slow_status") == "SLOW_RECOGNIZED"
        )
        and h2_ax.get("selected_av_payload_digest") is not None
        and h2_ax.get("selected_av_payload_digest") == h4_ax.get("selected_av_payload_digest")
    )
    p4 = bool(h5_ax and h5_p4 and h5_ax.get("recognized") and h5_p4.get("recognized"))
    p5 = all(item is not None for item in h7) and tuple(
        bool(item.get("recognized")) for item in h7 if item is not None
    ) == (True, True, False, False, False)
    return p1, p2, p3, p4, p5


def _decision_from_vectors(
    vectors: Mapping[str, tuple[bool, ...]],
    errors: Mapping[str, int],
    r0_exact_equivalence: bool,
) -> tuple[str, str | None]:
    if set(vectors) != set(ARM_IDS) or any(len(vector) != 5 for vector in vectors.values()):
        return "METHOD_INVALID", None
    if errors.get("TSPM1", 1) != 0:
        return "TSPM1_FUNCTION_NOT_VALID", None
    if not r0_exact_equivalence:
        return "METHOD_INVALID", None
    strongest = min(
        SIMPLE_BASELINE_ORDER,
        key=lambda arm_id: (-sum(vectors[arm_id]), errors.get(arm_id, 0), arm_id),
    )
    if vectors[strongest] == vectors["TSPM1"]:
        return "FUNCTION_VALID_SIMPLE_BASELINE_EXPLAINS", strongest
    if not all(vectors["TSPM1"]):
        return "TSPM1_FUNCTION_NOT_VALID", strongest
    return "TSPM1_TWO_TIMESCALE_ENGINEERING_ADVANTAGE_OVER_SIMPLE_BASELINES", strongest


def _exact_reduction_projection(result: S2DRCellResult) -> object:
    event_keys = ("event", "consolidation_status")
    finding_keys = (
        "checkpoint", "pair_id", "recognized", "context_source",
        "fast_recognized", "auditory_fast_distance", "visual_fast_distance",
        "auditory_slow_status", "visual_slow_status",
        "auditory_selected_slot_id", "visual_selected_slot_id",
        "auditory_selected_prototype_digest", "visual_selected_prototype_digest",
        "auditory_slow_distance", "visual_slow_distance", "selected_av_payload_digest",
    )
    for entries, required_keys in (
        (result.event_payloads, event_keys),
        (result.finding_payloads, finding_keys),
    ):
        if any(not isinstance(entry, Mapping) or not all(key in entry for key in required_keys) for entry in entries):
            raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "incomplete reduction projection entry")
    event_projection = tuple(
        tuple(event[key] for key in event_keys)
        for event in result.event_payloads
    )
    finding_projection = tuple(
        tuple(finding[key] for key in finding_keys)
        for finding in result.finding_payloads
    )
    return result.poststate_payload, event_projection, finding_projection


def compare_s2dr_results(
    config: S2DRConfigRecord,
    plans: tuple[S2DRCellPlan, ...],
    results: tuple[S2DRCellResult, ...],
    registry_digest: str,
) -> S2DRComparisonResult:
    """Compare one complete, externally supplied 56-cell result set."""

    if type(config) is not S2DRConfigRecord or not _is_digest(registry_digest):
        raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "comparison source is invalid")
    if len(plans) != 56 or len(results) != 56:
        raise S2DRError(S2DR_ATOMIC_RESULT_REQUIRED, "exactly 56 plans and results are required")
    if len({plan.cell_id for plan in plans}) != 56 or len({result.cell_id for result in results}) != 56:
        raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "duplicate cell identity")
    plan_by_id = {plan.cell_id: plan for plan in plans}
    result_by_role: dict[tuple[str, str], S2DRCellResult] = {}
    for result in results:
        plan = plan_by_id.get(result.cell_id)
        if plan is None or result.cell_plan_digest != plan.cell_plan_digest:
            raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "result does not match registry plan")
        result_by_role[(plan.history_id, plan.arm_id)] = result
    if len(result_by_role) != 56:
        raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "history-arm matrix is incomplete")
    vectors = {arm_id: _predicate_vector(result_by_role, arm_id) for arm_id in ARM_IDS}
    errors = {
        arm_id: sum(
            1
            for history_id in HISTORY_IDS
            if result_by_role[(history_id, arm_id)].cell_receipt.internal_error_code is not None
        )
        for arm_id in ARM_IDS
    }
    r0_exact = all(
        _exact_reduction_projection(result_by_role[(history_id, "R0")])
        == _exact_reduction_projection(result_by_role[(history_id, "TSPM1")])
        for history_id in HISTORY_IDS
    )
    decision, strongest = _decision_from_vectors(vectors, errors, r0_exact)
    return _built(
        S2DRComparisonResult,
        "comparison_result_digest",
        schema_version=S2DR_SCHEMA_VERSION,
        registry_digest=registry_digest,
        ordered_cell_result_digests=tuple(result.cell_result_digest for result in results),
        per_arm_predicate_vectors=tuple((arm_id, vectors[arm_id]) for arm_id in ARM_IDS),
        per_arm_error_counts=tuple((arm_id, errors[arm_id]) for arm_id in ARM_IDS),
        strongest_simple_baseline_id=strongest,
        r0_exact_equivalence=r0_exact,
        decision=decision,
    )
