"""Lossless, versioned S2-UC record codecs; V1 remains readable."""
from __future__ import annotations

import json
import math
import struct

from tools import _s2tu_retained_trace as tu


VERSION = "s2uc.record-codec.v3"
PREVIOUS_VERSION = "s2uc.record-codec.v2"
LEGACY_VERSION = "s2uc.record-codec.v1"


def _bits(value: float) -> bytes:
    return struct.pack(">d", value)


def _vector_from_values_hex(value) -> tuple[bytes, ...] | None:
    """Accept only the canonical finite representation emitted by `_hex`."""
    if type(value) is not list or len(value) != 48 or not all(type(item) is str for item in value):
        return None
    try:
        values = tuple(float.fromhex(item) for item in value)
    except ValueError:
        return None
    if not all(math.isfinite(item) and item.hex() == text for item, text in zip(values, value, strict=True)):
        return None
    return tuple(_bits(item) for item in values)


def _vector_index(key, vectors, vector_indexes) -> int:
    index = vector_indexes.setdefault(key, len(vectors))
    if index == len(vectors):
        vectors.append({"values_bits": [item.hex() for item in key]})
    return index


def _encode_v2(value, frames, frame_indexes, vectors, vector_indexes):
    if isinstance(value, tu.Frame):
        vector_key = tuple(_bits(item) for item in value.values)
        vector_index = _vector_index(vector_key, vectors, vector_indexes)
        frame_key = (vector_index, value.profile, value.owner, value.segment, value.ordinal)
        frame_index = frame_indexes.setdefault(frame_key, len(frames))
        if frame_index == len(frames):
            frames.append({"vector": vector_index, "profile": value.profile, "owner": value.owner,
                           "segment": value.segment, "ordinal": value.ordinal})
        return {"@frame": frame_index}
    if isinstance(value, tuple):
        return {"@tuple": [_encode_v2(item, frames, frame_indexes, vectors, vector_indexes) for item in value]}
    if isinstance(value, list):
        return [_encode_v2(item, frames, frame_indexes, vectors, vector_indexes) for item in value]
    if isinstance(value, dict):
        encoded = {}
        for key, item in value.items():
            values_hex = _vector_from_values_hex(item) if key == "values_hex" else None
            encoded[key] = {"@values_hex": _vector_index(values_hex, vectors, vector_indexes)} if values_hex is not None else _encode_v2(item, frames, frame_indexes, vectors, vector_indexes)
        return encoded
    return value


def _decode(value, frames, vectors):
    if isinstance(value, list):
        return [_decode(item, frames, vectors) for item in value]
    if not isinstance(value, dict):
        return value
    if set(value) == {"@tuple"}:
        return tuple(_decode(item, frames, vectors) for item in value["@tuple"])
    if set(value) == {"@frame"}:
        index = value["@frame"]
        if type(index) is not int or not 0 <= index < len(frames):
            raise ValueError("RECORD_FRAME_REFERENCE_INVALID")
        return frames[index]
    if set(value) == {"@values_hex"}:
        index = value["@values_hex"]
        if type(index) is not int or not 0 <= index < len(vectors):
            raise ValueError("RECORD_VECTOR_REFERENCE_INVALID")
        return [item.hex() for item in vectors[index]]
    return {key: _decode(item, frames, vectors) for key, item in value.items()}


def dumps(record: dict[str, object]) -> bytes:
    frames, frame_indexes, vectors, vector_indexes = [], {}, [], {}
    encoded = _encode_v2(record, frames, frame_indexes, vectors, vector_indexes)
    return json.dumps({"version": VERSION, "vectors": vectors, "frames": frames, "record": encoded},
                      allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _loads_v1(value: dict[str, object]) -> dict[str, object]:
    if set(value) != {"version", "frames", "record"} or type(value["frames"]) is not list:
        raise ValueError("RECORD_CODEC_INVALID")
    frames = [tu.Frame(tuple(float.fromhex(item) for item in frame["values_hex"]), frame["profile"], frame["owner"],
                       frame["segment"], frame["ordinal"]) for frame in value["frames"]]
    return _decode(value["record"], frames, [])


def _loads_vectors(value: dict[str, object], *, permit_values_hex: bool) -> dict[str, object]:
    if set(value) != {"version", "vectors", "frames", "record"} or type(value["vectors"]) is not list or type(value["frames"]) is not list:
        raise ValueError("RECORD_CODEC_INVALID")
    vectors = []
    for vector in value["vectors"]:
        if type(vector) is not dict or set(vector) != {"values_bits"} or type(vector["values_bits"]) is not list or len(vector["values_bits"]) != 48:
            raise ValueError("RECORD_VECTOR_INVALID")
        try:
            values = tuple(struct.unpack(">d", bytes.fromhex(item))[0] for item in vector["values_bits"])
        except (TypeError, ValueError, struct.error) as exc:
            raise ValueError("RECORD_VECTOR_INVALID") from exc
        vectors.append(values)
    frames = []
    for frame in value["frames"]:
        if type(frame) is not dict or set(frame) != {"vector", "profile", "owner", "segment", "ordinal"}:
            raise ValueError("RECORD_FRAME_INVALID")
        index = frame["vector"]
        if type(index) is not int or not 0 <= index < len(vectors):
            raise ValueError("RECORD_VECTOR_REFERENCE_INVALID")
        frames.append(tu.Frame(vectors[index], frame["profile"], frame["owner"], frame["segment"], frame["ordinal"]))
    decoded = _decode(value["record"], frames, vectors)
    if not permit_values_hex:
        def reject_values_hex(item):
            if isinstance(item, dict):
                if set(item) == {"@values_hex"}:
                    raise ValueError("RECORD_CODEC_INVALID")
                for nested in item.values(): reject_values_hex(nested)
            elif isinstance(item, list):
                for nested in item: reject_values_hex(nested)
        reject_values_hex(value["record"])
    return decoded


def loads(data: bytes) -> dict[str, object]:
    value = json.loads(data)
    if type(value) is not dict:
        raise ValueError("RECORD_CODEC_INVALID")
    if value.get("version") == LEGACY_VERSION:
        decoded = _loads_v1(value)
    elif value.get("version") == PREVIOUS_VERSION:
        decoded = _loads_vectors(value, permit_values_hex=False)
    elif value.get("version") == VERSION:
        decoded = _loads_vectors(value, permit_values_hex=True)
    else:
        raise ValueError("RECORD_CODEC_INVALID")
    if type(decoded) is not dict:
        raise ValueError("RECORD_CODEC_INVALID")
    return decoded


def estimate_worst_case(*, frame_count: int, record_metadata_bytes: int) -> int:
    """Conservative V2 bound for distinct Binary64 vectors and metadata.

    V2 stores every value as exactly sixteen hexadecimal bytes.  The bound is
    intentionally independent of a value's decimal or ``float.hex`` spelling.
    """
    if type(frame_count) is not int or type(record_metadata_bytes) is not int or frame_count < 0 or record_metadata_bytes < 0:
        raise ValueError("RECORD_ESTIMATE_INVALID")
    # JSON string quotes and a comma need at most eighteen bytes per 16-byte
    # Binary64 token.  Keep one extra byte per token as a structural margin.
    vector_bytes = frame_count * (48 * 19 + len('{"values_bits":[]}'))
    frame_bytes = frame_count * (64 + 64 + 64 + 64 + 32 + len('{"ordinal":,"owner":"","profile":"","segment":"","vector":}'))
    return len('{"frames":[],"record":,"vectors":[],"version":"s2uc.record-codec.v3"}') + vector_bytes + frame_bytes + record_metadata_bytes


def record_metadata_bytes(data: bytes) -> int:
    """Return the serialized non-table record payload size for preflight limits."""
    value = json.loads(data)
    if type(value) is not dict or value.get("version") not in {PREVIOUS_VERSION, VERSION} or "record" not in value:
        raise ValueError("RECORD_CODEC_INVALID")
    return len(json.dumps(value["record"], allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def conservative_metadata_ceiling(*, record_limit: int, frame_count: int) -> int:
    """Largest metadata payload that remains safe even with distinct frame vectors."""
    baseline = estimate_worst_case(frame_count=frame_count, record_metadata_bytes=0)
    if type(record_limit) is not int or record_limit < baseline:
        raise ValueError("RECORD_ESTIMATE_INVALID")
    return record_limit - baseline
