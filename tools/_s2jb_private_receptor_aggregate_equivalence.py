"""Private prospective receptor aggregate provenance and pure equivalence."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re

import numpy as np

from mcm_field_organism._ppb1_reference import (
    PPB1BankConfig,
    PPB1BankState,
    PPB1StepResult,
    advance_ppb1_bank,
    normalized_mean_l1_distance,
)
from mcm_field_organism.finite_video_path import (
    LocalChannelGridReceptor,
    VisualGridConfig,
    VisualReceptorState,
)
from mcm_field_organism.receptor_contract import ReceptorContactFrame


S2JB_SCHEMA = "s2jb.private.receptor-aggregate-equivalence.v1"
AGGREGATE_CODE_SCHEMA = "s2jb.private.receptor-aggregate-code.v1"
PPB_LINEAGE_SCHEMA = "s2jb.private.ppb-aggregate-lineage.v1"
SAMPLE_COUNT = 1600
VALUE_DENOMINATOR = 408000
VISUAL_DIMENSION = 18
MAX_PPB_LINEAGES = 4
MAX_QUALIFICATION_FORMATIONS_PER_LINEAGE = 32
NATIVE_VISUAL_L1_THRESHOLD = 0.01
FUNCTIONAL_VISUAL_L1_THRESHOLD = 44.0 / 765.0
SAME_RECEPTOR_AGGREGATE = "SAME_RECEPTOR_AGGREGATE"
DIFFERENT_RECEPTOR_AGGREGATE = "DIFFERENT_RECEPTOR_AGGREGATE"

S2JB_INVALID_FRAME = "S2JB_INVALID_FRAME"
S2JB_SOURCE_MISMATCH = "S2JB_SOURCE_MISMATCH"
S2JB_AGGREGATE_INVALID = "S2JB_AGGREGATE_INVALID"
S2JB_LINEAGE_INVALID = "S2JB_LINEAGE_INVALID"
S2JB_CAPACITY_EXCEEDED = "S2JB_CAPACITY_EXCEEDED"

_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]*$")


class S2JBError(ValueError):
    """One fail-closed S2-JB contract violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _bytes_digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _require_digest(value: object, role: str, code: str) -> str:
    if not isinstance(value, str) or _DIGEST.fullmatch(value) is None:
        raise S2JBError(code, f"{role} must be a lowercase SHA-256 digest")
    return value


def _require_identifier(value: object, role: str, code: str) -> str:
    if not isinstance(value, str) or _IDENTIFIER.fullmatch(value) is None:
        raise S2JBError(code, f"{role} must be a technical identifier")
    return value


def _config_payload(config: VisualGridConfig) -> dict[str, object]:
    return {
        "schema": S2JB_SCHEMA,
        "source_width": config.source_width,
        "source_height": config.source_height,
        "grid_columns": config.grid_columns,
        "grid_rows": config.grid_rows,
        "frames_per_second": config.frames_per_second,
        "geometry_id": config.geometry_id,
        "carrier_ids": list(config.carrier_ids),
    }


def _geometry_payload(config: VisualGridConfig) -> dict[str, object]:
    return {
        "schema": S2JB_SCHEMA,
        "source_width": config.source_width,
        "source_height": config.source_height,
        "grid_columns": config.grid_columns,
        "grid_rows": config.grid_rows,
        "channels": 3,
        "block_width": config.source_width // config.grid_columns,
        "block_height": config.source_height // config.grid_rows,
        "geometry_id": config.geometry_id,
    }


def _aggregate_payload(
    geometry_digest: str,
    carrier_id: str,
    block_row: int,
    block_column: int,
    channel: int,
    byte_sum: int,
) -> dict[str, object]:
    return {
        "schema": AGGREGATE_CODE_SCHEMA,
        "geometry_digest": geometry_digest,
        "carrier_id": carrier_id,
        "block_row": block_row,
        "block_column": block_column,
        "channel": channel,
        "sample_count": SAMPLE_COUNT,
        "byte_sum": byte_sum,
    }


@dataclass(frozen=True, slots=True)
class ReceptorAggregateCodeV1:
    source_frame_digest: str
    raw_block_digest: str
    receptor_config_digest: str
    geometry_digest: str
    carrier_id: str
    block_row: int
    block_column: int
    channel: int
    sample_count: int
    byte_sum: int
    value_numerator: int
    value_denominator: int
    receptor_state_digest: str
    receptor_receipt_digest: str
    aggregate_code_digest: str
    evidence_digest: str
    schema: str = AGGREGATE_CODE_SCHEMA

    def __post_init__(self) -> None:
        for role in (
            "source_frame_digest",
            "raw_block_digest",
            "receptor_config_digest",
            "geometry_digest",
            "receptor_state_digest",
            "receptor_receipt_digest",
            "aggregate_code_digest",
            "evidence_digest",
        ):
            _require_digest(getattr(self, role), role, S2JB_AGGREGATE_INVALID)
        _require_identifier(self.carrier_id, "carrier_id", S2JB_AGGREGATE_INVALID)
        if (
            self.schema != AGGREGATE_CODE_SCHEMA
            or isinstance(self.block_row, bool)
            or not isinstance(self.block_row, int)
            or self.block_row < 0
            or isinstance(self.block_column, bool)
            or not isinstance(self.block_column, int)
            or self.block_column < 0
            or isinstance(self.channel, bool)
            or not isinstance(self.channel, int)
            or not 0 <= self.channel < 3
            or self.sample_count != SAMPLE_COUNT
            or isinstance(self.byte_sum, bool)
            or not isinstance(self.byte_sum, int)
            or not 0 <= self.byte_sum <= VALUE_DENOMINATOR
            or self.value_numerator != self.byte_sum
            or self.value_denominator != VALUE_DENOMINATOR
        ):
            raise S2JBError(
                S2JB_AGGREGATE_INVALID,
                "aggregate role, sample count, or integer value is invalid",
            )
        aggregate_payload = _aggregate_payload(
            self.geometry_digest,
            self.carrier_id,
            self.block_row,
            self.block_column,
            self.channel,
            self.byte_sum,
        )
        if self.aggregate_code_digest != _digest(aggregate_payload):
            raise S2JBError(
                S2JB_AGGREGATE_INVALID,
                "aggregate code digest does not match integer source fields",
            )
        if self.evidence_digest != _digest(self.payload_without_evidence_digest()):
            raise S2JBError(
                S2JB_AGGREGATE_INVALID,
                "aggregate evidence digest is inconsistent",
            )

    def payload_without_evidence_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "source_frame_digest": self.source_frame_digest,
            "raw_block_digest": self.raw_block_digest,
            "receptor_config_digest": self.receptor_config_digest,
            "geometry_digest": self.geometry_digest,
            "carrier_id": self.carrier_id,
            "block_row": self.block_row,
            "block_column": self.block_column,
            "channel": self.channel,
            "sample_count": self.sample_count,
            "byte_sum": self.byte_sum,
            "value_numerator": self.value_numerator,
            "value_denominator": self.value_denominator,
            "receptor_state_digest": self.receptor_state_digest,
            "receptor_receipt_digest": self.receptor_receipt_digest,
            "aggregate_code_digest": self.aggregate_code_digest,
        }

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_evidence_digest(),
            "evidence_digest": self.evidence_digest,
        }


def _validate_receptor_scope(receptor: object) -> LocalChannelGridReceptor:
    if type(receptor) is not LocalChannelGridReceptor:
        raise S2JBError(S2JB_INVALID_FRAME, "exact LocalChannelGridReceptor required")
    config = receptor.config
    if (
        type(config) is not VisualGridConfig
        or config.source_width != 120
        or config.source_height != 80
        or config.grid_columns != 3
        or config.grid_rows != 2
        or config.carrier_count != VISUAL_DIMENSION
    ):
        raise S2JBError(S2JB_INVALID_FRAME, "visual receptor scope differs from S2-JA")
    return receptor


def analyze_uint8_frame_with_aggregate_codes(
    frame: object,
    receptor: LocalChannelGridReceptor,
    *,
    frame_index: int,
) -> tuple[VisualReceptorState, tuple[ReceptorAggregateCodeV1, ...]]:
    """Bind integer aggregate codes before invoking the unchanged receptor."""

    bound_receptor = _validate_receptor_scope(receptor)
    if (
        type(frame) is not np.ndarray
        or frame.dtype != np.uint8
        or frame.shape != (80, 120, 3)
        or isinstance(frame_index, bool)
        or not isinstance(frame_index, int)
        or frame_index < 0
    ):
        raise S2JBError(S2JB_INVALID_FRAME, "exact uint8 frame and index required")

    image = np.array(frame, dtype=np.uint8, copy=True, order="C")
    image.setflags(write=False)
    raw_bytes = image.tobytes(order="C")
    raw_bytes_sha256 = _bytes_digest(raw_bytes)
    config_digest = _digest(_config_payload(bound_receptor.config))
    geometry_digest = _digest(_geometry_payload(bound_receptor.config))
    source_frame_digest = _digest(
        {
            "schema": S2JB_SCHEMA,
            "shape": [80, 120, 3],
            "dtype": "uint8",
            "raw_bytes_sha256": raw_bytes_sha256,
            "receptor_config_digest": config_digest,
        }
    )

    block_view = image.reshape(2, 40, 3, 40, 3)
    integer_sums = block_view.sum(axis=(1, 3), dtype=np.uint64)
    if integer_sums.shape != (2, 3, 3):
        raise S2JBError(S2JB_AGGREGATE_INVALID, "aggregate sum geometry differs")
    sum_values = tuple(int(value) for value in integer_sums.reshape(-1))
    if len(sum_values) != VISUAL_DIMENSION or any(
        value < 0 or value > VALUE_DENOMINATOR for value in sum_values
    ):
        raise S2JBError(S2JB_AGGREGATE_INVALID, "aggregate sum domain differs")

    aggregate_cores: list[tuple[dict[str, object], str, str]] = []
    carrier_index = 0
    for row in range(2):
        for column in range(3):
            for channel in range(3):
                block = np.ascontiguousarray(
                    image[
                        row * 40 : (row + 1) * 40,
                        column * 40 : (column + 1) * 40,
                        channel,
                    ]
                )
                raw_block_digest = _bytes_digest(block.tobytes(order="C"))
                carrier_id = bound_receptor.config.carrier_ids[carrier_index]
                aggregate_payload = _aggregate_payload(
                    geometry_digest,
                    carrier_id,
                    row,
                    column,
                    channel,
                    sum_values[carrier_index],
                )
                aggregate_cores.append(
                    (aggregate_payload, _digest(aggregate_payload), raw_block_digest)
                )
                carrier_index += 1

    receptor_state = bound_receptor.analyze(image, frame_index=frame_index)
    if _bytes_digest(image.tobytes(order="C")) != raw_bytes_sha256:
        raise S2JBError(S2JB_SOURCE_MISMATCH, "source frame changed during analysis")
    if (
        receptor_state.geometry_id != bound_receptor.config.geometry_id
        or receptor_state.carrier_ids != bound_receptor.config.carrier_ids
        or len(receptor_state.channel_values) != VISUAL_DIMENSION
    ):
        raise S2JBError(S2JB_SOURCE_MISMATCH, "receptor output geometry differs")

    expected_values = tuple(
        (float(value) / float(SAMPLE_COUNT)) / 255.0 for value in sum_values
    )
    if tuple(receptor_state.channel_values) != expected_values:
        raise S2JBError(
            S2JB_SOURCE_MISMATCH,
            "receptor float output does not match the bound integer aggregates",
        )

    receptor_state_digest = receptor_state.digest()
    receptor_receipt_digest = _digest(
        {
            "schema": "s2jb.private.receptor-receipt-binding.v1",
            "source_frame_digest": source_frame_digest,
            "receptor_config_digest": config_digest,
            "receptor_state_digest": receptor_state_digest,
            "frame_index": frame_index,
        }
    )
    codes = []
    for index, (aggregate_payload, code_digest, raw_block_digest) in enumerate(
        aggregate_cores
    ):
        evidence = {
            "schema": AGGREGATE_CODE_SCHEMA,
            "source_frame_digest": source_frame_digest,
            "raw_block_digest": raw_block_digest,
            "receptor_config_digest": config_digest,
            "geometry_digest": geometry_digest,
            "carrier_id": aggregate_payload["carrier_id"],
            "block_row": aggregate_payload["block_row"],
            "block_column": aggregate_payload["block_column"],
            "channel": aggregate_payload["channel"],
            "sample_count": SAMPLE_COUNT,
            "byte_sum": sum_values[index],
            "value_numerator": sum_values[index],
            "value_denominator": VALUE_DENOMINATOR,
            "receptor_state_digest": receptor_state_digest,
            "receptor_receipt_digest": receptor_receipt_digest,
            "aggregate_code_digest": code_digest,
        }
        codes.append(
            ReceptorAggregateCodeV1(
                source_frame_digest,
                raw_block_digest,
                config_digest,
                geometry_digest,
                str(aggregate_payload["carrier_id"]),
                int(aggregate_payload["block_row"]),
                int(aggregate_payload["block_column"]),
                int(aggregate_payload["channel"]),
                SAMPLE_COUNT,
                sum_values[index],
                sum_values[index],
                VALUE_DENOMINATOR,
                receptor_state_digest,
                receptor_receipt_digest,
                code_digest,
                _digest(evidence),
            )
        )
    return receptor_state, tuple(codes)


def _validate_code_pair(
    first: object,
    second: object,
) -> tuple[ReceptorAggregateCodeV1, ReceptorAggregateCodeV1]:
    if type(first) is not ReceptorAggregateCodeV1 or type(second) is not ReceptorAggregateCodeV1:
        raise S2JBError(S2JB_AGGREGATE_INVALID, "exact aggregate code types required")
    if (
        first.geometry_digest != second.geometry_digest
        or first.carrier_id != second.carrier_id
        or first.block_row != second.block_row
        or first.block_column != second.block_column
        or first.channel != second.channel
        or first.sample_count != second.sample_count
    ):
        raise S2JBError(S2JB_SOURCE_MISMATCH, "aggregate coordinate roles differ")
    return first, second


def aggregate_codes_equivalent(first: object, second: object) -> str:
    left, right = _validate_code_pair(first, second)
    if left.aggregate_code_digest == right.aggregate_code_digest:
        return SAME_RECEPTOR_AGGREGATE
    return DIFFERENT_RECEPTOR_AGGREGATE


def aggregate_frame_evidence_digest(
    codes: object,
) -> str:
    validated = _validate_code_inventory(codes)
    return _digest(
        {
            "schema": "s2jb.private.aggregate-frame-evidence.v1",
            "source_frame_digest": validated[0].source_frame_digest,
            "receptor_state_digest": validated[0].receptor_state_digest,
            "receptor_receipt_digest": validated[0].receptor_receipt_digest,
            "ordered_evidence_digests": [item.evidence_digest for item in validated],
        }
    )


def _validate_code_inventory(
    codes: object,
) -> tuple[ReceptorAggregateCodeV1, ...]:
    if type(codes) is not tuple or len(codes) != VISUAL_DIMENSION or any(
        type(item) is not ReceptorAggregateCodeV1 for item in codes
    ):
        raise S2JBError(S2JB_AGGREGATE_INVALID, "exact 18-code tuple required")
    result = tuple(codes)
    if len({item.carrier_id for item in result}) != VISUAL_DIMENSION:
        raise S2JBError(S2JB_AGGREGATE_INVALID, "aggregate carriers must be unique")
    shared = {
        (
            item.source_frame_digest,
            item.receptor_config_digest,
            item.geometry_digest,
            item.receptor_state_digest,
            item.receptor_receipt_digest,
        )
        for item in result
    }
    if len(shared) != 1:
        raise S2JBError(S2JB_SOURCE_MISMATCH, "aggregate frame evidence is mixed")
    return result


@dataclass(frozen=True, slots=True)
class PPBAggregateLineageV1:
    lineage_id: str
    bank_id: str
    slot_id: str
    ppb_config_digest: str
    carrier_ids: tuple[str, ...]
    homogeneous_aggregate_code_digests: tuple[str, ...]
    ordered_formation_receipt_digests: tuple[str, ...]
    ordered_source_aggregate_evidence_digests: tuple[str, ...]
    ordered_prestate_digests: tuple[str, ...]
    ordered_poststate_digests: tuple[str, ...]
    support_sequence: tuple[int, ...]
    final_support: int
    stabilized: bool
    final_prototype_digest: str
    lineage_digest: str
    schema: str = PPB_LINEAGE_SCHEMA

    def __post_init__(self) -> None:
        for role in ("lineage_id", "bank_id", "slot_id"):
            _require_identifier(getattr(self, role), role, S2JB_LINEAGE_INVALID)
        _require_digest(self.ppb_config_digest, "ppb_config_digest", S2JB_LINEAGE_INVALID)
        _require_digest(
            self.final_prototype_digest,
            "final_prototype_digest",
            S2JB_LINEAGE_INVALID,
        )
        _require_digest(self.lineage_digest, "lineage_digest", S2JB_LINEAGE_INVALID)
        carriers = tuple(self.carrier_ids)
        code_digests = tuple(self.homogeneous_aggregate_code_digests)
        formation = tuple(self.ordered_formation_receipt_digests)
        source = tuple(self.ordered_source_aggregate_evidence_digests)
        prestates = tuple(self.ordered_prestate_digests)
        poststates = tuple(self.ordered_poststate_digests)
        supports = tuple(self.support_sequence)
        length = len(formation)
        if (
            self.schema != PPB_LINEAGE_SCHEMA
            or len(carriers) != VISUAL_DIMENSION
            or len(set(carriers)) != VISUAL_DIMENSION
            or len(code_digests) != VISUAL_DIMENSION
            or length < 1
            or length > MAX_QUALIFICATION_FORMATIONS_PER_LINEAGE
            or any(len(items) != length for items in (source, prestates, poststates, supports))
            or any(not isinstance(item, int) or isinstance(item, bool) for item in supports)
            or any(not _IDENTIFIER.fullmatch(item) for item in carriers)
            or any(
                not _DIGEST.fullmatch(item)
                for items in (code_digests, formation, source, prestates, poststates)
                for item in items
            )
            or len(set(formation)) != length
        ):
            raise S2JBError(S2JB_LINEAGE_INVALID, "lineage shape or digest inventory is invalid")
        expected_supports = tuple(min(3, index + 1) for index in range(length))
        if (
            supports != expected_supports
            or self.final_support != supports[-1]
            or self.stabilized != (self.final_support >= 3)
            or any(prestates[index] != poststates[index - 1] for index in range(1, length))
        ):
            raise S2JBError(S2JB_LINEAGE_INVALID, "lineage order or support relation is invalid")
        object.__setattr__(self, "carrier_ids", carriers)
        object.__setattr__(self, "homogeneous_aggregate_code_digests", code_digests)
        object.__setattr__(self, "ordered_formation_receipt_digests", formation)
        object.__setattr__(self, "ordered_source_aggregate_evidence_digests", source)
        object.__setattr__(self, "ordered_prestate_digests", prestates)
        object.__setattr__(self, "ordered_poststate_digests", poststates)
        object.__setattr__(self, "support_sequence", supports)
        if self.lineage_digest != _digest(self.payload_without_digest()):
            raise S2JBError(S2JB_LINEAGE_INVALID, "lineage digest is inconsistent")

    @classmethod
    def build(
        cls,
        lineage_id: str,
        bank_id: str,
        slot_id: str,
        ppb_config_digest: str,
        carrier_ids: tuple[str, ...],
        homogeneous_aggregate_code_digests: tuple[str, ...],
        ordered_formation_receipt_digests: tuple[str, ...],
        ordered_source_aggregate_evidence_digests: tuple[str, ...],
        ordered_prestate_digests: tuple[str, ...],
        ordered_poststate_digests: tuple[str, ...],
        support_sequence: tuple[int, ...],
        final_prototype_digest: str,
    ) -> "PPBAggregateLineageV1":
        values = {
            "schema": PPB_LINEAGE_SCHEMA,
            "lineage_id": lineage_id,
            "bank_id": bank_id,
            "slot_id": slot_id,
            "ppb_config_digest": ppb_config_digest,
            "carrier_ids": list(carrier_ids),
            "homogeneous_aggregate_code_digests": list(
                homogeneous_aggregate_code_digests
            ),
            "ordered_formation_receipt_digests": list(
                ordered_formation_receipt_digests
            ),
            "ordered_source_aggregate_evidence_digests": list(
                ordered_source_aggregate_evidence_digests
            ),
            "ordered_prestate_digests": list(ordered_prestate_digests),
            "ordered_poststate_digests": list(ordered_poststate_digests),
            "support_sequence": list(support_sequence),
            "final_support": support_sequence[-1],
            "stabilized": support_sequence[-1] >= 3,
            "final_prototype_digest": final_prototype_digest,
        }
        return cls(
            lineage_id,
            bank_id,
            slot_id,
            ppb_config_digest,
            carrier_ids,
            homogeneous_aggregate_code_digests,
            ordered_formation_receipt_digests,
            ordered_source_aggregate_evidence_digests,
            ordered_prestate_digests,
            ordered_poststate_digests,
            support_sequence,
            support_sequence[-1],
            support_sequence[-1] >= 3,
            final_prototype_digest,
            _digest(values),
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "lineage_id": self.lineage_id,
            "bank_id": self.bank_id,
            "slot_id": self.slot_id,
            "ppb_config_digest": self.ppb_config_digest,
            "carrier_ids": list(self.carrier_ids),
            "homogeneous_aggregate_code_digests": list(
                self.homogeneous_aggregate_code_digests
            ),
            "ordered_formation_receipt_digests": list(
                self.ordered_formation_receipt_digests
            ),
            "ordered_source_aggregate_evidence_digests": list(
                self.ordered_source_aggregate_evidence_digests
            ),
            "ordered_prestate_digests": list(self.ordered_prestate_digests),
            "ordered_poststate_digests": list(self.ordered_poststate_digests),
            "support_sequence": list(self.support_sequence),
            "final_support": self.final_support,
            "stabilized": self.stabilized,
            "final_prototype_digest": self.final_prototype_digest,
        }

    def canonical_payload(self) -> dict[str, object]:
        return {**self.payload_without_digest(), "lineage_digest": self.lineage_digest}


def validate_ppb_aggregate_lineage(
    lineage: object,
    *,
    bank_id: str,
    slot_id: str,
    ppb_config_digest: str,
    carrier_ids: tuple[str, ...],
) -> PPBAggregateLineageV1:
    if type(lineage) is not PPBAggregateLineageV1:
        raise S2JBError(S2JB_LINEAGE_INVALID, "exact PPB aggregate lineage required")
    if (
        lineage.bank_id != bank_id
        or lineage.slot_id != slot_id
        or lineage.ppb_config_digest != ppb_config_digest
        or lineage.carrier_ids != carrier_ids
    ):
        raise S2JBError(S2JB_LINEAGE_INVALID, "lineage bank, slot, config, or carriers differ")
    return lineage


def _prototype_digest(values: tuple[float, ...]) -> str:
    return _digest({"schema": S2JB_SCHEMA, "prototype_values": list(values)})


def _validate_lineage_inventory(
    config: PPB1BankConfig,
    state: PPB1BankState,
    lineages: object,
) -> tuple[PPBAggregateLineageV1, ...]:
    if type(lineages) is not tuple or any(
        type(item) is not PPBAggregateLineageV1 for item in lineages
    ):
        raise S2JBError(S2JB_LINEAGE_INVALID, "exact lineage tuple required")
    result = tuple(lineages)
    if len(result) > MAX_PPB_LINEAGES:
        raise S2JBError(S2JB_CAPACITY_EXCEEDED, "more than four PPB lineages")
    if len({item.slot_id for item in result}) != len(result):
        raise S2JBError(S2JB_LINEAGE_INVALID, "duplicate PPB slot lineage")
    occupied = {slot.slot_id: slot for slot in state.slots if slot.occupied}
    if set(occupied) != {item.slot_id for item in result}:
        raise S2JBError(S2JB_LINEAGE_INVALID, "lineages do not mirror occupied PPB slots")
    for item in result:
        slot = occupied[item.slot_id]
        validate_ppb_aggregate_lineage(
            item,
            bank_id=config.bank_id,
            slot_id=slot.slot_id,
            ppb_config_digest=config.digest(),
            carrier_ids=config.carrier_ids,
        )
        if (
            item.final_support != slot.support_count
            or item.stabilized != (slot.support_count >= config.stable_after)
            or item.final_prototype_digest != _prototype_digest(slot.prototype_values)
        ):
            raise S2JBError(S2JB_LINEAGE_INVALID, "lineage does not match PPB slot")
    return tuple(sorted(result, key=lambda item: item.slot_id))


def advance_visual_ppb_with_aggregate_lineage(
    config: PPB1BankConfig,
    prestate: PPB1BankState,
    frame: ReceptorContactFrame,
    codes: tuple[ReceptorAggregateCodeV1, ...],
    lineages: tuple[PPBAggregateLineageV1, ...],
) -> tuple[PPB1StepResult, tuple[PPBAggregateLineageV1, ...]]:
    if (
        type(config) is not PPB1BankConfig
        or config.modality_id != "visual"
        or config.capacity > MAX_PPB_LINEAGES
        or len(config.carrier_ids) != VISUAL_DIMENSION
        or config.stable_after != 3
    ):
        raise S2JBError(S2JB_CAPACITY_EXCEEDED, "visual PPB configuration exceeds S2-JB")
    validated_codes = _validate_code_inventory(codes)
    if (
        type(frame) is not ReceptorContactFrame
        or frame.modality_id != "visual"
        or frame.geometry_id != config.geometry_id
        or frame.carrier_ids != config.carrier_ids
        or tuple(item.carrier_id for item in validated_codes) != frame.carrier_ids
        or tuple(
            (float(item.byte_sum) / float(SAMPLE_COUNT)) / 255.0
            for item in validated_codes
        )
        != frame.values
    ):
        raise S2JBError(S2JB_SOURCE_MISMATCH, "PPB frame and aggregate sources differ")
    validated_lineages = _validate_lineage_inventory(config, prestate, lineages)

    result = advance_ppb1_bank(config, prestate, frame)
    readout = result.readout
    code_digests = tuple(item.aggregate_code_digest for item in validated_codes)
    frame_evidence_digest = aggregate_frame_evidence_digest(validated_codes)
    formation_receipt_digest = _digest(
        {
            "schema": "s2jb.private.ppb-formation-binding.v1",
            "config_digest": config.digest(),
            "prestate_digest": prestate.digest(),
            "input_digest": readout.input_digest,
            "aggregate_frame_evidence_digest": frame_evidence_digest,
            "ppb_readout_digest": readout.digest(),
            "poststate_digest": result.poststate.digest(),
        }
    )
    by_slot = {item.slot_id: item for item in validated_lineages}
    if readout.event == "MATCHED":
        previous = by_slot.get(readout.slot_id)
        if previous is None or previous.homogeneous_aggregate_code_digests != code_digests:
            raise S2JBError(
                S2JB_LINEAGE_INVALID,
                "matched PPB slot has mixed or missing aggregate provenance",
            )
        formation = previous.ordered_formation_receipt_digests + (formation_receipt_digest,)
        source = previous.ordered_source_aggregate_evidence_digests + (frame_evidence_digest,)
        prestates = previous.ordered_prestate_digests + (prestate.digest(),)
        poststates = previous.ordered_poststate_digests + (result.poststate.digest(),)
        supports = previous.support_sequence + (readout.support_count,)
        lineage_id = previous.lineage_id
    else:
        formation = (formation_receipt_digest,)
        source = (frame_evidence_digest,)
        prestates = (prestate.digest(),)
        poststates = (result.poststate.digest(),)
        supports = (readout.support_count,)
        lineage_id = f"s2jb.{readout.slot_id}.lineage.{result.poststate.accepted_step_count:03d}"
    by_slot[readout.slot_id] = PPBAggregateLineageV1.build(
        lineage_id,
        config.bank_id,
        readout.slot_id,
        config.digest(),
        config.carrier_ids,
        code_digests,
        formation,
        source,
        prestates,
        poststates,
        supports,
        _prototype_digest(readout.prototype_values),
    )
    occupied_post = {slot.slot_id for slot in result.poststate.slots if slot.occupied}
    post_lineages = tuple(
        sorted(
            (item for slot_id, item in by_slot.items() if slot_id in occupied_post),
            key=lambda item: item.slot_id,
        )
    )
    _validate_lineage_inventory(config, result.poststate, post_lineages)
    return result, post_lineages


def lineage_equivalent_to_codes(
    lineage: object,
    codes: object,
) -> str:
    if type(lineage) is not PPBAggregateLineageV1:
        raise S2JBError(S2JB_LINEAGE_INVALID, "exact lineage required")
    validated_codes = _validate_code_inventory(codes)
    if lineage.carrier_ids != tuple(item.carrier_id for item in validated_codes):
        raise S2JBError(S2JB_SOURCE_MISMATCH, "lineage and probe carrier roles differ")
    probe_digests = tuple(item.aggregate_code_digest for item in validated_codes)
    if probe_digests == lineage.homogeneous_aggregate_code_digests:
        return SAME_RECEPTOR_AGGREGATE
    return DIFFERENT_RECEPTOR_AGGREGATE


def diagnostic_float_and_l1_baselines(
    first: tuple[float, ...],
    second: tuple[float, ...],
) -> tuple[bool, bool, bool]:
    distance = normalized_mean_l1_distance(first, second)
    return (
        first == second,
        distance <= NATIVE_VISUAL_L1_THRESHOLD,
        distance <= FUNCTIONAL_VISUAL_L1_THRESHOLD,
    )


QUALIFICATION_LIMITS = {
    "cases": 50,
    "source_materializations": 286,
    "aggregate_code_formations": 286,
    "ppb_formation_steps": 214,
    "aggregate_comparisons": 50,
    "diagnostic_baseline_comparisons": 126,
    "validated_ppb_lineage_steps": 230,
    "logical_work_items": 1192,
}
