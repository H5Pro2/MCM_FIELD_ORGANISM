"""Private static fixtures for the S2-FU 18-step functional plan.

Pattern identifiers and expected outcomes are evaluation metadata only. This
module provides no receptor, memory, coordinator, runner, or file operation.
Auditory tuples describe synthetic auditory receptor states, not analyzed
audio signals.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from types import MappingProxyType


S2FU_FIXTURE_SCHEMA = "s2fu.private.fixture.v1"
S2FU_EXPECTATION_SCHEMA = "s2fu.private.expectation.v1"
S2FU_RESOURCE_SCHEMA = "s2fu.private.resources.v1"

_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_PATTERN_ID = re.compile(r"^P(?:[1-9]|1[01])$")


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


def _positions(values: tuple[int, ...], high: int) -> str:
    return "".join(str(index) for index, value in enumerate(values) if value == high)


def _minimum_auditory_difference(patterns: tuple[S2FUPatternFixture, ...]) -> int:
    return min(
        sum(abs(left - right) for left, right in zip(first.auditory_values, second.auditory_values))
        for index, first in enumerate(patterns)
        for second in patterns[index + 1 :]
    )


def _minimum_visual_cell_difference(patterns: tuple[S2FUPatternFixture, ...]) -> int:
    return min(
        sum(
            abs(left - right)
            for left, right in zip(first.visual_cell_values, second.visual_cell_values)
        )
        for index, first in enumerate(patterns)
        for second in patterns[index + 1 :]
    )


@dataclass(frozen=True, slots=True)
class S2FUPatternFixture:
    pattern_id: str
    auditory_high_positions: str
    auditory_values: tuple[int, ...]
    visual_high_positions: str
    visual_cell_values: tuple[int, ...]
    pattern_digest: str
    schema: str = S2FU_FIXTURE_SCHEMA

    def __post_init__(self) -> None:
        _require(_PATTERN_ID.fullmatch(self.pattern_id) is not None, "invalid pattern id")
        _require(
            type(self.auditory_values) is tuple
            and len(self.auditory_values) == 8
            and all(type(value) is int and value in (0, 1) for value in self.auditory_values)
            and sum(self.auditory_values) == 4,
            "auditory state must be one literal binary 4-of-8 tuple",
        )
        _require(
            self.auditory_high_positions == _positions(self.auditory_values, 1),
            "auditory position metadata differs from literal values",
        )
        _require(
            type(self.visual_cell_values) is tuple
            and len(self.visual_cell_values) == 6
            and all(type(value) is int and value in (30, 210) for value in self.visual_cell_values)
            and self.visual_cell_values.count(210) == 3
            and self.visual_cell_values.count(30) == 3
            and sum(self.visual_cell_values) == 720,
            "visual state must be one literal equally weighted 3-of-6 tuple",
        )
        _require(
            self.visual_high_positions == _positions(self.visual_cell_values, 210),
            "visual position metadata differs from literal cells",
        )
        _require(
            self.pattern_digest == _digest(self.payload_without_digest()),
            "pattern digest mismatch",
        )

    @property
    def visual_values(self) -> tuple[float, ...]:
        return tuple(value / 255.0 for value in self.visual_cell_values for _ in range(3))

    @property
    def av_values(self) -> tuple[float, ...]:
        return tuple(float(value) for value in self.auditory_values) + self.visual_values

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "pattern_id": self.pattern_id,
            "auditory_high_positions": self.auditory_high_positions,
            "auditory_values": list(self.auditory_values),
            "visual_high_positions": self.visual_high_positions,
            "visual_cell_values": list(self.visual_cell_values),
        }


def _pattern(
    pattern_id: str,
    auditory_high_positions: str,
    auditory_values: tuple[int, ...],
    visual_high_positions: str,
    visual_cell_values: tuple[int, ...],
) -> S2FUPatternFixture:
    payload = {
        "schema": S2FU_FIXTURE_SCHEMA,
        "pattern_id": pattern_id,
        "auditory_high_positions": auditory_high_positions,
        "auditory_values": list(auditory_values),
        "visual_high_positions": visual_high_positions,
        "visual_cell_values": list(visual_cell_values),
    }
    return S2FUPatternFixture(
        pattern_id,
        auditory_high_positions,
        auditory_values,
        visual_high_positions,
        visual_cell_values,
        _digest(payload),
    )


PATTERNS = (
    _pattern("P1", "0123", (1, 1, 1, 1, 0, 0, 0, 0), "012", (210, 210, 210, 30, 30, 30)),
    _pattern("P2", "0124", (1, 1, 1, 0, 1, 0, 0, 0), "013", (210, 210, 30, 210, 30, 30)),
    _pattern("P3", "0125", (1, 1, 1, 0, 0, 1, 0, 0), "014", (210, 210, 30, 30, 210, 30)),
    _pattern("P4", "0126", (1, 1, 1, 0, 0, 0, 1, 0), "015", (210, 210, 30, 30, 30, 210)),
    _pattern("P5", "0127", (1, 1, 1, 0, 0, 0, 0, 1), "023", (210, 30, 210, 210, 30, 30)),
    _pattern("P6", "0134", (1, 1, 0, 1, 1, 0, 0, 0), "024", (210, 30, 210, 30, 210, 30)),
    _pattern("P7", "0135", (1, 1, 0, 1, 0, 1, 0, 0), "025", (210, 30, 210, 30, 30, 210)),
    _pattern("P8", "0136", (1, 1, 0, 1, 0, 0, 1, 0), "034", (210, 30, 30, 210, 210, 30)),
    _pattern("P9", "0137", (1, 1, 0, 1, 0, 0, 0, 1), "035", (210, 30, 30, 210, 30, 210)),
    _pattern("P10", "0145", (1, 1, 0, 0, 1, 1, 0, 0), "045", (210, 30, 30, 30, 210, 210)),
    _pattern("P11", "0146", (1, 1, 0, 0, 1, 0, 1, 0), "123", (30, 210, 210, 210, 30, 30)),
)
PATTERN_BY_ID = MappingProxyType({pattern.pattern_id: pattern for pattern in PATTERNS})


@dataclass(frozen=True, slots=True)
class S2FUDistanceBinding:
    role: str
    numerator: int
    denominator: int
    native_threshold_numerator: int
    native_threshold_denominator: int

    def __post_init__(self) -> None:
        _require(
            self.role in {"AUDITORY_MINIMUM", "VISUAL_MINIMUM", "VISUAL_FUNCTIONAL"}
            and type(self.numerator) is int
            and type(self.denominator) is int
            and self.numerator >= 0
            and self.denominator > 0
            and type(self.native_threshold_numerator) is int
            and type(self.native_threshold_denominator) is int
            and self.native_threshold_denominator > 0,
            "invalid distance binding",
        )

    @property
    def value(self) -> float:
        return self.numerator / self.denominator

    @property
    def native_threshold(self) -> float:
        return self.native_threshold_numerator / self.native_threshold_denominator


AUDITORY_MINIMUM = S2FUDistanceBinding("AUDITORY_MINIMUM", 2, 8, 1, 5)
VISUAL_MINIMUM = S2FUDistanceBinding("VISUAL_MINIMUM", 180, 765, 1, 5)
VISUAL_FUNCTIONAL_THRESHOLD = S2FUDistanceBinding("VISUAL_FUNCTIONAL", 44, 765, 1, 5)


@dataclass(frozen=True, slots=True)
class S2FUExposureFixture:
    step: int
    pattern_id: str
    window_start_tick: int
    window_end_tick: int

    def __post_init__(self) -> None:
        _require(type(self.step) is int and 1 <= self.step <= 18, "invalid exposure step")
        _require(self.pattern_id in PATTERN_BY_ID, "unknown exposure pattern")
        _require(
            type(self.window_start_tick) is int
            and type(self.window_end_tick) is int
            and self.window_start_tick >= 0
            and self.window_end_tick == self.window_start_tick + 1,
            "invalid exposure window",
        )


EXPOSURES = (
    S2FUExposureFixture(1, "P1", 0, 1),
    S2FUExposureFixture(2, "P2", 1, 2),
    S2FUExposureFixture(3, "P3", 2, 3),
    S2FUExposureFixture(4, "P4", 3, 4),
    S2FUExposureFixture(5, "P2", 8, 9),
    S2FUExposureFixture(6, "P1", 9, 10),
    S2FUExposureFixture(7, "P1", 10, 11),
    S2FUExposureFixture(8, "P1", 11, 12),
    S2FUExposureFixture(9, "P1", 12, 13),
    S2FUExposureFixture(10, "P5", 13, 14),
    S2FUExposureFixture(11, "P6", 14, 15),
    S2FUExposureFixture(12, "P7", 15, 16),
    S2FUExposureFixture(13, "P8", 16, 17),
    S2FUExposureFixture(14, "P9", 17, 18),
    S2FUExposureFixture(15, "P10", 18, 19),
    S2FUExposureFixture(16, "P11", 19, 20),
    S2FUExposureFixture(17, "P3", 20, 21),
    S2FUExposureFixture(18, "P4", 21, 22),
)


@dataclass(frozen=True, slots=True)
class S2FUProbeFixture:
    probe_id: str
    role: str
    checkpoint_after_step: int
    ordinal: int
    pattern_id: str
    window_start_tick: int
    window_end_tick: int

    def __post_init__(self) -> None:
        _require(
            self.role in {"EARLY_SEQUENCE", "FINAL_CONTENT"}
            and self.pattern_id in PATTERN_BY_ID
            and type(self.checkpoint_after_step) is int
            and self.checkpoint_after_step in {4, 18}
            and type(self.ordinal) is int
            and self.ordinal >= 1
            and self.window_end_tick == self.window_start_tick + 1,
            "invalid probe fixture",
        )
        _require(
            self.probe_id
            == f"s2fu.probe.{self.role.lower()}.{self.ordinal:02d}.{self.pattern_id.lower()}",
            "probe id is not canonical",
        )


PROBES = (
    S2FUProbeFixture("s2fu.probe.early_sequence.01.p1", "EARLY_SEQUENCE", 4, 1, "P1", 4, 5),
    S2FUProbeFixture("s2fu.probe.early_sequence.02.p2", "EARLY_SEQUENCE", 4, 2, "P2", 5, 6),
    S2FUProbeFixture("s2fu.probe.early_sequence.03.p3", "EARLY_SEQUENCE", 4, 3, "P3", 6, 7),
    S2FUProbeFixture("s2fu.probe.early_sequence.04.p4", "EARLY_SEQUENCE", 4, 4, "P4", 7, 8),
    S2FUProbeFixture("s2fu.probe.final_content.01.p1", "FINAL_CONTENT", 18, 1, "P1", 22, 23),
    S2FUProbeFixture("s2fu.probe.final_content.02.p2", "FINAL_CONTENT", 18, 2, "P2", 23, 24),
)


@dataclass(frozen=True, slots=True)
class S2FUStepExpectation:
    step: int
    pattern_id: str
    b4_event: str
    tspm_fast_event: str
    fast_loss_pattern_id: str | None
    ppb_calls_per_modality: int
    p1_slow_support: int
    p2_slow_support: int
    schema: str = S2FU_EXPECTATION_SCHEMA

    def __post_init__(self) -> None:
        _require(self.schema == S2FU_EXPECTATION_SCHEMA, "invalid expectation schema")
        _require(type(self.step) is int and 1 <= self.step <= 18, "invalid expected step")
        _require(self.pattern_id in PATTERN_BY_ID, "unknown expected pattern")
        _require(
            self.b4_event in {"B4_APPENDED", "B4_EVICTED_AND_APPENDED"}
            and self.tspm_fast_event in {"FAST_CREATED", "FAST_UPDATED", "FAST_REPLACED"},
            "invalid expected event",
        )
        _require(
            self.fast_loss_pattern_id is None or self.fast_loss_pattern_id in PATTERN_BY_ID,
            "invalid expected fast loss",
        )
        _require(
            all(
                type(value) is int and value >= 0
                for value in (
                    self.ppb_calls_per_modality,
                    self.p1_slow_support,
                    self.p2_slow_support,
                )
            ),
            "invalid expected support",
        )


STEP_EXPECTATIONS = (
    S2FUStepExpectation(1, "P1", "B4_APPENDED", "FAST_CREATED", None, 0, 0, 0),
    S2FUStepExpectation(2, "P2", "B4_APPENDED", "FAST_CREATED", None, 0, 0, 0),
    S2FUStepExpectation(3, "P3", "B4_APPENDED", "FAST_CREATED", None, 0, 0, 0),
    S2FUStepExpectation(4, "P4", "B4_APPENDED", "FAST_REPLACED", "P1", 0, 0, 0),
    S2FUStepExpectation(5, "P2", "B4_APPENDED", "FAST_UPDATED", None, 1, 0, 1),
    S2FUStepExpectation(6, "P1", "B4_APPENDED", "FAST_REPLACED", "P3", 1, 0, 1),
    S2FUStepExpectation(7, "P1", "B4_APPENDED", "FAST_UPDATED", None, 2, 1, 1),
    S2FUStepExpectation(8, "P1", "B4_APPENDED", "FAST_UPDATED", None, 3, 2, 1),
    S2FUStepExpectation(9, "P1", "B4_APPENDED", "FAST_UPDATED", None, 4, 3, 1),
    S2FUStepExpectation(10, "P5", "B4_EVICTED_AND_APPENDED", "FAST_REPLACED", "P4", 4, 3, 1),
    S2FUStepExpectation(11, "P6", "B4_EVICTED_AND_APPENDED", "FAST_REPLACED", "P2", 4, 3, 1),
    S2FUStepExpectation(12, "P7", "B4_EVICTED_AND_APPENDED", "FAST_REPLACED", "P1", 4, 3, 1),
    S2FUStepExpectation(13, "P8", "B4_EVICTED_AND_APPENDED", "FAST_REPLACED", "P5", 4, 3, 1),
    S2FUStepExpectation(14, "P9", "B4_EVICTED_AND_APPENDED", "FAST_REPLACED", "P6", 4, 3, 1),
    S2FUStepExpectation(15, "P10", "B4_EVICTED_AND_APPENDED", "FAST_REPLACED", "P7", 4, 3, 1),
    S2FUStepExpectation(16, "P11", "B4_EVICTED_AND_APPENDED", "FAST_REPLACED", "P8", 4, 3, 1),
    S2FUStepExpectation(17, "P3", "B4_EVICTED_AND_APPENDED", "FAST_REPLACED", "P9", 4, 3, 1),
    S2FUStepExpectation(18, "P4", "B4_EVICTED_AND_APPENDED", "FAST_REPLACED", "P10", 4, 3, 1),
)


@dataclass(frozen=True, slots=True)
class S2FUResourceBinding:
    unique_receptor_analyses: int
    composite_formations: int
    standalone_b4_formations: int
    standalone_tspm_formations: int
    component_identity_checks: int
    sequence_probe_calls: int
    composite_content_probe_calls: int
    standalone_b4_content_probe_calls: int
    standalone_tspm_content_probe_calls: int
    high_level_operations: int
    common_projection_terms: int
    b4_arm_words: int
    tspm_arm_words: int
    coordinator_words: int
    composite_formation_words: int
    b4_distance_terms: int
    tspm_distance_terms: int
    composite_formation_distance_terms: int
    coordinator_validation_terms: int
    coordinator_digest_operations: int
    composite_control_terms: int
    native_b4_formation_words: int
    native_tspm_formation_word_limit: int
    composite_probe_result_words: int
    composite_probe_distance_terms: int
    composite_probe_control_terms: int
    sequence_functional_terms: int
    sequence_validation_terms: int
    sequence_ordered_bits: int
    sequence_blind_bits: int
    standalone_formation_word_limit: int
    standalone_formation_distance_limit: int
    standalone_content_distance_limit: int
    resource_digest: str
    schema: str = S2FU_RESOURCE_SCHEMA

    def __post_init__(self) -> None:
        values = tuple(
            getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"resource_digest", "schema"}
        )
        _require(
            self.schema == S2FU_RESOURCE_SCHEMA
            and all(type(value) is int and value >= 0 for value in values)
            and self.high_level_operations
            == self.unique_receptor_analyses
            + self.composite_formations
            + self.standalone_b4_formations
            + self.standalone_tspm_formations
            + self.component_identity_checks
            + self.sequence_probe_calls
            + self.composite_content_probe_calls
            + self.standalone_b4_content_probe_calls
            + self.standalone_tspm_content_probe_calls
            and self.composite_formation_words
            == self.b4_arm_words + self.tspm_arm_words + self.coordinator_words
            and self.composite_formation_distance_terms
            == self.b4_distance_terms + self.tspm_distance_terms
            and self.composite_control_terms
            == self.common_projection_terms
            + self.coordinator_validation_terms
            + self.coordinator_digest_operations
            and self.resource_digest == _digest(self.payload_without_digest()),
            "resource binding is incomplete or inconsistent",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            **{
                name: getattr(self, name)
                for name in self.__dataclass_fields__
                if name not in {"resource_digest", "schema"}
            },
        }


_RESOURCE_VALUES = {
    "unique_receptor_analyses": 24,
    "composite_formations": 18,
    "standalone_b4_formations": 18,
    "standalone_tspm_formations": 18,
    "component_identity_checks": 18,
    "sequence_probe_calls": 1,
    "composite_content_probe_calls": 2,
    "standalone_b4_content_probe_calls": 2,
    "standalone_tspm_content_probe_calls": 2,
    "high_level_operations": 103,
    "common_projection_terms": 468,
    "b4_arm_words": 5274,
    "tspm_arm_words": 5274,
    "coordinator_words": 558,
    "composite_formation_words": 11106,
    "b4_distance_terms": 4212,
    "tspm_distance_terms": 4212,
    "composite_formation_distance_terms": 8424,
    "coordinator_validation_terms": 324,
    "coordinator_digest_operations": 180,
    "composite_control_terms": 972,
    "native_b4_formation_words": 486,
    "native_tspm_formation_word_limit": 5274,
    "composite_probe_result_words": 28,
    "composite_probe_distance_terms": 936,
    "composite_probe_control_terms": 96,
    "sequence_functional_terms": 416,
    "sequence_validation_terms": 416,
    "sequence_ordered_bits": 4,
    "sequence_blind_bits": 96,
    "standalone_formation_word_limit": 10548,
    "standalone_formation_distance_limit": 8424,
    "standalone_content_distance_limit": 936,
}
RESOURCES = S2FUResourceBinding(
    **_RESOURCE_VALUES,
    resource_digest=_digest({"schema": S2FU_RESOURCE_SCHEMA, **_RESOURCE_VALUES}),
)


SOURCE_HASHES = (
    (
        "mcm_field_organism/_tspm1_s2dr_private_comparison.py",
        "96cdd018be34afe67de0139428fed5254cff945ba74db98163a91273f5d21b2c",
    ),
    (
        "mcm_field_organism/_tspm1_private.py",
        "321ce786c42edd217dc6dbf2210c495016b2babaa78d53449a13b0039965d516",
    ),
    (
        "tools/_retention_capacity_read_only.py",
        "524a42ae8294a14e58adfda29afa8602f3a799e0caaccae9675dc50bf0109ff7",
    ),
    (
        "tools/_visual_sequence_memory_probe.py",
        "d5fef4aa9fbbc06502f630e729161274b13c972f9ae2a1f13fb2084bb00593ec",
    ),
    (
        "tools/_s2fs_b4_tspm1_private_coordinator.py",
        "95ee05ccc0eeb14abbcda036971da5c33ac79363dd546789f4878aace5677db0",
    ),
)

OPERATOR_INPUT_FIELDS = (
    "config_digest",
    "prestate_digest",
    "bound_source_digest",
)
EVALUATION_ONLY_FIELDS = (
    "pattern_id",
    "expected_b4_event",
    "expected_tspm_fast_event",
    "expected_fast_loss_pattern_id",
    "expected_support",
)


def _fixture_payload() -> dict[str, object]:
    return {
        "schema": S2FU_FIXTURE_SCHEMA,
        "patterns": [
            {**pattern.payload_without_digest(), "pattern_digest": pattern.pattern_digest}
            for pattern in PATTERNS
        ],
        "auditory_minimum": {
            "numerator": AUDITORY_MINIMUM.numerator,
            "denominator": AUDITORY_MINIMUM.denominator,
        },
        "visual_minimum": {
            "numerator": VISUAL_MINIMUM.numerator,
            "denominator": VISUAL_MINIMUM.denominator,
        },
        "visual_functional_threshold": {
            "numerator": VISUAL_FUNCTIONAL_THRESHOLD.numerator,
            "denominator": VISUAL_FUNCTIONAL_THRESHOLD.denominator,
        },
        "exposures": [
            {
                "step": item.step,
                "pattern_id": item.pattern_id,
                "window_start_tick": item.window_start_tick,
                "window_end_tick": item.window_end_tick,
            }
            for item in EXPOSURES
        ],
        "probes": [
            {
                "probe_id": item.probe_id,
                "role": item.role,
                "checkpoint_after_step": item.checkpoint_after_step,
                "ordinal": item.ordinal,
                "pattern_id": item.pattern_id,
                "window_start_tick": item.window_start_tick,
                "window_end_tick": item.window_end_tick,
            }
            for item in PROBES
        ],
        "expectations": [
            {
                "step": item.step,
                "pattern_id": item.pattern_id,
                "b4_event": item.b4_event,
                "tspm_fast_event": item.tspm_fast_event,
                "fast_loss_pattern_id": item.fast_loss_pattern_id,
                "ppb_calls_per_modality": item.ppb_calls_per_modality,
                "p1_slow_support": item.p1_slow_support,
                "p2_slow_support": item.p2_slow_support,
            }
            for item in STEP_EXPECTATIONS
        ],
        "resources_digest": RESOURCES.resource_digest,
        "source_hashes": [list(item) for item in SOURCE_HASHES],
        "operator_input_fields": list(OPERATOR_INPUT_FIELDS),
        "evaluation_only_fields": list(EVALUATION_ONLY_FIELDS),
    }


FIXTURE_DIGEST = _digest(_fixture_payload())


_require(len(PATTERNS) == 11 and len(PATTERN_BY_ID) == 11, "eleven unique patterns required")
_require(tuple(item.step for item in EXPOSURES) == tuple(range(1, 19)), "18 ordered steps required")
_require(len(PROBES) == 6 and len({item.probe_id for item in PROBES}) == 6, "six unique probes required")
_require(tuple(item.step for item in STEP_EXPECTATIONS) == tuple(range(1, 19)), "18 expectations required")
_require(all(_valid_digest(digest) for _, digest in SOURCE_HASHES), "invalid source digest")
_require(_minimum_auditory_difference(PATTERNS) == 2, "auditory literal minimum differs from 2/8")
_require(
    _minimum_visual_cell_difference(PATTERNS) == 360,
    "visual literal minimum differs from 180/765",
)
_require(AUDITORY_MINIMUM.value == 0.25 and AUDITORY_MINIMUM.value > 0.2, "auditory distance binding")
_require(VISUAL_MINIMUM.value == 180 / 765 and VISUAL_MINIMUM.value > 0.2, "visual distance binding")
_require(VISUAL_FUNCTIONAL_THRESHOLD.value < VISUAL_MINIMUM.value, "visual functional separation")
_require(
    tuple(item.pattern_id for item in EXPOSURES)
    == tuple(item.pattern_id for item in STEP_EXPECTATIONS),
    "exposure and expectation sequence differ",
)
_require(
    set(OPERATOR_INPUT_FIELDS).isdisjoint(EVALUATION_ONLY_FIELDS),
    "evaluation metadata leaked into operator input fields",
)
