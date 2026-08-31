"""Private byte-block fixtures for the bounded S2-HQ role conflict.

The module does not form memory states or call a receptor. It binds literal
uint8 block values and can materialize one image only when explicitly called.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re

import numpy as np


S2HQ_FIXTURE_SCHEMA = "s2hq.private.byte-block-conflict-fixture.v1"
IMAGE_SHAPE = (80, 120, 3)
GRID_SHAPE = (2, 3, 3)
BLOCK_SHAPE = (40, 40)
VISIBLE_POSITIONS = (0, 2, 4, 6, 8, 10, 12, 14, 16)
MASKED_POSITIONS = (1, 3, 5, 7, 9, 11, 13, 15, 17)

_IDENTIFIER = re.compile(r"^[a-z][a-z0-9.-]{1,31}$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class S2HQFixtureError(ValueError):
    """One fail-closed private fixture violation."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2HQFixtureError(message)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _expanded_raw_bytes(block_values: tuple[int, ...]) -> bytes:
    raw = bytearray(IMAGE_SHAPE[0] * IMAGE_SHAPE[1] * IMAGE_SHAPE[2])
    offset = 0
    for row in range(IMAGE_SHAPE[0]):
        grid_row = row // BLOCK_SHAPE[0]
        for column in range(IMAGE_SHAPE[1]):
            grid_column = column // BLOCK_SHAPE[1]
            base = grid_row * 9 + grid_column * 3
            for channel in range(3):
                raw[offset] = block_values[base + channel]
                offset += 1
    return bytes(raw)


@dataclass(frozen=True, slots=True)
class ByteBlockVisualFixture:
    fixture_id: str
    block_values: tuple[int, ...]
    raw_sha256: str
    fixture_digest: str
    schema: str = S2HQ_FIXTURE_SCHEMA

    def __post_init__(self) -> None:
        _require(
            isinstance(self.fixture_id, str)
            and _IDENTIFIER.fullmatch(self.fixture_id) is not None,
            "visual fixture id differs",
        )
        _require(
            type(self.block_values) is tuple
            and len(self.block_values) == 18
            and all(
                type(value) is int and 0 <= value <= 255
                for value in self.block_values
            ),
            "visual fixture requires exactly 18 uint8 block values",
        )
        _require(
            isinstance(self.raw_sha256, str)
            and _DIGEST.fullmatch(self.raw_sha256) is not None
            and hashlib.sha256(_expanded_raw_bytes(self.block_values)).hexdigest()
            == self.raw_sha256,
            "visual raw-byte digest differs",
        )
        _require(
            self.schema == S2HQ_FIXTURE_SCHEMA
            and self.fixture_digest == _digest(self.payload_without_digest()),
            "visual fixture digest differs",
        )

    @property
    def receptor_values(self) -> tuple[float, ...]:
        return tuple(value / 255.0 for value in self.block_values)

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "fixture_id": self.fixture_id,
            "block_values": list(self.block_values),
            "raw_sha256": self.raw_sha256,
            "image_shape": list(IMAGE_SHAPE),
            "grid_shape": list(GRID_SHAPE),
            "block_shape": list(BLOCK_SHAPE),
        }

    @classmethod
    def build(
        cls,
        fixture_id: str,
        block_values: tuple[int, ...],
        raw_sha256: str,
    ) -> "ByteBlockVisualFixture":
        payload = {
            "schema": S2HQ_FIXTURE_SCHEMA,
            "fixture_id": fixture_id,
            "block_values": list(block_values),
            "raw_sha256": raw_sha256,
            "image_shape": list(IMAGE_SHAPE),
            "grid_shape": list(GRID_SHAPE),
            "block_shape": list(BLOCK_SHAPE),
        }
        return cls(fixture_id, block_values, raw_sha256, _digest(payload))


@dataclass(frozen=True, slots=True)
class SyntheticAuditoryFixture:
    fixture_id: str
    values: tuple[float, ...]
    fixture_digest: str
    schema: str = S2HQ_FIXTURE_SCHEMA

    def __post_init__(self) -> None:
        _require(
            isinstance(self.fixture_id, str)
            and _IDENTIFIER.fullmatch(self.fixture_id) is not None,
            "auditory fixture id differs",
        )
        _require(
            type(self.values) is tuple
            and len(self.values) == 8
            and all(
                type(value) in (int, float)
                and math.isfinite(float(value))
                and 0.0 <= float(value) <= 1.0
                for value in self.values
            ),
            "auditory fixture requires eight normalized values",
        )
        _require(
            self.schema == S2HQ_FIXTURE_SCHEMA
            and self.fixture_digest == _digest(self.payload_without_digest()),
            "auditory fixture digest differs",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "fixture_id": self.fixture_id,
            "values": list(self.values),
            "kind": "SYNTHETIC_AUDITORY_RECEPTOR_STATE",
        }

    @classmethod
    def build(
        cls,
        fixture_id: str,
        values: tuple[float, ...],
    ) -> "SyntheticAuditoryFixture":
        payload = {
            "schema": S2HQ_FIXTURE_SCHEMA,
            "fixture_id": fixture_id,
            "values": list(values),
            "kind": "SYNTHETIC_AUDITORY_RECEPTOR_STATE",
        }
        return cls(fixture_id, values, _digest(payload))


@dataclass(frozen=True, slots=True)
class ConflictDirectionFixture:
    direction_id: str
    recent_visual_id: str
    recent_auditory_id: str
    stable_visual_id: str
    stable_auditory_id: str
    full_probe_visual_id: str
    full_probe_auditory_id: str
    direction_digest: str
    schema: str = S2HQ_FIXTURE_SCHEMA

    def __post_init__(self) -> None:
        identifiers = (
            self.direction_id,
            self.recent_visual_id,
            self.recent_auditory_id,
            self.stable_visual_id,
            self.stable_auditory_id,
            self.full_probe_visual_id,
            self.full_probe_auditory_id,
        )
        _require(
            all(
                isinstance(value, str) and _IDENTIFIER.fullmatch(value) is not None
                for value in identifiers
            ),
            "conflict direction identifier differs",
        )
        _require(
            self.recent_visual_id != self.stable_visual_id
            and self.recent_auditory_id != self.stable_auditory_id,
            "recent and stable sources must remain distinct",
        )
        _require(
            self.schema == S2HQ_FIXTURE_SCHEMA
            and self.direction_digest == _digest(self.payload_without_digest()),
            "conflict direction digest differs",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "direction_id": self.direction_id,
            "recent_visual_id": self.recent_visual_id,
            "recent_auditory_id": self.recent_auditory_id,
            "stable_visual_id": self.stable_visual_id,
            "stable_auditory_id": self.stable_auditory_id,
            "full_probe_visual_id": self.full_probe_visual_id,
            "full_probe_auditory_id": self.full_probe_auditory_id,
        }

    @classmethod
    def build(
        cls,
        direction_id: str,
        recent_visual_id: str,
        recent_auditory_id: str,
        stable_visual_id: str,
        stable_auditory_id: str,
        full_probe_visual_id: str,
        full_probe_auditory_id: str,
    ) -> "ConflictDirectionFixture":
        payload = {
            "schema": S2HQ_FIXTURE_SCHEMA,
            "direction_id": direction_id,
            "recent_visual_id": recent_visual_id,
            "recent_auditory_id": recent_auditory_id,
            "stable_visual_id": stable_visual_id,
            "stable_auditory_id": stable_auditory_id,
            "full_probe_visual_id": full_probe_visual_id,
            "full_probe_auditory_id": full_probe_auditory_id,
        }
        return cls(
            direction_id,
            recent_visual_id,
            recent_auditory_id,
            stable_visual_id,
            stable_auditory_id,
            full_probe_visual_id,
            full_probe_auditory_id,
            _digest(payload),
        )


@dataclass(frozen=True, slots=True)
class DirectedRoleCase:
    case_id: str
    direction_id: str
    requested_area: str
    case_digest: str
    schema: str = S2HQ_FIXTURE_SCHEMA

    def __post_init__(self) -> None:
        _require(
            isinstance(self.case_id, str)
            and _IDENTIFIER.fullmatch(self.case_id) is not None
            and isinstance(self.direction_id, str)
            and _IDENTIFIER.fullmatch(self.direction_id) is not None
            and self.requested_area in ("A_RECENT", "B_STABLE"),
            "directed role case differs",
        )
        _require(
            self.schema == S2HQ_FIXTURE_SCHEMA
            and self.case_digest == _digest(self.payload_without_digest()),
            "directed role case digest differs",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "case_id": self.case_id,
            "direction_id": self.direction_id,
            "requested_area": self.requested_area,
        }

    @classmethod
    def build(
        cls,
        case_id: str,
        direction_id: str,
        requested_area: str,
    ) -> "DirectedRoleCase":
        payload = {
            "schema": S2HQ_FIXTURE_SCHEMA,
            "case_id": case_id,
            "direction_id": direction_id,
            "requested_area": requested_area,
        }
        return cls(case_id, direction_id, requested_area, _digest(payload))


@dataclass(frozen=True, slots=True)
class EvaluationExpectation:
    case_id: str
    expected_visual_id: str

    def __post_init__(self) -> None:
        _require(
            isinstance(self.case_id, str)
            and _IDENTIFIER.fullmatch(self.case_id) is not None
            and isinstance(self.expected_visual_id, str)
            and _IDENTIFIER.fullmatch(self.expected_visual_id) is not None,
            "evaluation expectation differs",
        )


V0 = ByteBlockVisualFixture.build(
    "v0",
    (255, 0, 0, 255, 255, 0, 0, 255, 255, 0, 0, 255, 255, 0, 0, 255, 255, 0),
    "36b9c3295ab4130569bf69abe8375c8358c112cf016935478b62a0a81d4f94a9",
)
V1 = ByteBlockVisualFixture.build(
    "v1",
    (255, 255, 0, 0, 255, 0, 0, 255, 255, 0, 0, 255, 255, 0, 0, 255, 255, 0),
    "f73995c9ee54c8347d5884e515d1a18b1d418e4440c17c6419e55983a656925e",
)
Q0 = ByteBlockVisualFixture.build(
    "q0",
    (255, 127, 0, 128, 255, 0, 0, 255, 255, 0, 0, 255, 255, 0, 0, 255, 255, 0),
    "9d0752305a2c2fc17b81c8df6cfef6ae8043a0fd7739b3876ba0ff5c4451dca0",
)
Q1 = ByteBlockVisualFixture.build(
    "q1",
    (255, 128, 0, 127, 255, 0, 0, 255, 255, 0, 0, 255, 255, 0, 0, 255, 255, 0),
    "b748bf97f53f4e45e32a21c6387daea8fc005fbfa830c399095e43523f2817e9",
)
M0 = SyntheticAuditoryFixture.build("m0", (1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0))
M1 = SyntheticAuditoryFixture.build("m1", (1.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0))
MQ = SyntheticAuditoryFixture.build("mq", (1.0, 1.0, 1.0, 0.5, 0.5, 0.0, 0.0, 0.0))

VISUAL_FIXTURES = (V0, V1, Q0, Q1)
AUDITORY_FIXTURES = (M0, M1, MQ)
VISUAL_BY_ID = {item.fixture_id: item for item in VISUAL_FIXTURES}
AUDITORY_BY_ID = {item.fixture_id: item for item in AUDITORY_FIXTURES}

DIRECTIONS = (
    ConflictDirectionFixture.build("d0", "v0", "m0", "v1", "m1", "q0", "mq"),
    ConflictDirectionFixture.build("d1", "v1", "m1", "v0", "m0", "q1", "mq"),
)
DIRECTION_BY_ID = {item.direction_id: item for item in DIRECTIONS}

ROLE_CASES = (
    DirectedRoleCase.build("c01", "d0", "A_RECENT"),
    DirectedRoleCase.build("c02", "d0", "B_STABLE"),
    DirectedRoleCase.build("c03", "d1", "A_RECENT"),
    DirectedRoleCase.build("c04", "d1", "B_STABLE"),
)

# Evaluation-only data is not accepted by either functional implementation.
EVALUATION_EXPECTATIONS = (
    EvaluationExpectation("c01", "v0"),
    EvaluationExpectation("c02", "v1"),
    EvaluationExpectation("c03", "v1"),
    EvaluationExpectation("c04", "v0"),
)

MASKED_VISUAL_VALUES: tuple[float | None, ...] = (
    1.0, None, 0.0, None, 1.0, None, 0.0, None, 1.0,
    None, 0.0, None, 1.0, None, 0.0, None, 1.0, None,
)


def materialize_uint8_image(fixture: ByteBlockVisualFixture) -> np.ndarray:
    """Materialize one exact image without changing the bound fixture."""

    _require(type(fixture) is ByteBlockVisualFixture, "exact byte-block fixture required")
    fixture.__post_init__()
    cells = np.asarray(fixture.block_values, dtype=np.uint8).reshape(GRID_SHAPE)
    image = np.repeat(np.repeat(cells, BLOCK_SHAPE[0], axis=0), BLOCK_SHAPE[1], axis=1)
    _require(image.shape == IMAGE_SHAPE and image.dtype == np.uint8, "materialized image anatomy differs")
    _require(hashlib.sha256(image.tobytes()).hexdigest() == fixture.raw_sha256, "materialized image digest differs")
    image.setflags(write=False)
    return image


__all__: tuple[str, ...] = ()
