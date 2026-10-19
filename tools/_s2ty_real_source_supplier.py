"""Lazy, source-bound PCM supplier for the prospective S2-TY run only."""
from __future__ import annotations

from collections.abc import Callable

from tools import _s2nu_private_source_binding as nu
from tools import _s2ts_temporal_trace_run as source
from tools import _s2ty_source_time_binding as binding


VERSION = "s2ty.real-source-supplier.v1"


class S2TYRealSourceError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _need(ok: bool, code: str) -> None:
    if not ok:
        raise S2TYRealSourceError(code)


def _expected_endpoint(row: dict[str, object], profile: str) -> dict[str, object]:
    return {
        "source_id": row["source_id"],
        "pcm_sha256": row["pcm_sha256"],
        "profile": profile,
        "nj_snapshot_index": row["nj_snapshot_index"],
        "window_start_sample": row["window_start_sample"],
        "window_end_sample": row["window_end_sample"],
    }


def source_binding(manifest: dict[str, object]) -> dict[str, object]:
    """Resolve the sealed NU rows needed by this manifest without opening PCM."""
    binding.validate_static(manifest)
    source_rows, plan = source.source_rows()
    _need(plan["profiles"]["half_profile_digest"] == manifest["profile"], "SOURCE_PROFILE_INVALID")
    expected: dict[int, dict[str, object]] = {}
    for item in manifest["events"]:
        endpoint = item.get("endpoint")
        if endpoint is None:
            continue
        _need(type(endpoint) is dict and endpoint["source_id"] in source_rows, "SOURCE_ID_INVALID")
        row = source_rows[endpoint["source_id"]]
        _need(endpoint == _expected_endpoint(row, manifest["profile"]), "SOURCE_ENDPOINT_INVALID")
        expected[item["ordinal"]] = row
    _need(len(expected) == 22, "SOURCE_ENDPOINT_COUNT_INVALID")
    return {
        "version": VERSION,
        "source_plan_sha256": source.SOURCE_PLAN_SHA256,
        "source_execution_digest": plan["execution_digest"],
        "profile": manifest["profile"],
        "endpoint_ordinals": tuple(expected),
        "source_rows": expected,
    }


def create_payload_supplier(
    manifest: dict[str, object],
    *,
    pcm_window: Callable[[nu.WindowSpec], bytearray] = nu.pcm_window,
) -> Callable[[int, dict[str, object]], bytearray]:
    """Return a demand-only supplier; no payload is opened while binding it."""
    _need(callable(pcm_window), "PCM_WINDOW_FACTORY_INVALID")
    bound = source_binding(manifest)

    def supply(ordinal: int, endpoint: dict[str, object]) -> bytearray:
        _need(type(ordinal) is int and ordinal in bound["source_rows"], "SOURCE_ORDINAL_INVALID")
        row = bound["source_rows"][ordinal]
        _need(endpoint == _expected_endpoint(row, bound["profile"]), "SOURCE_ENDPOINT_INVALID")
        stream = row["stream_id"]
        window = row["window_ordinal"]
        _need(type(stream) is str and stream.startswith("s") and stream[1:].isdigit(), "SOURCE_ROW_INVALID")
        _need(type(window) is int, "SOURCE_ROW_INVALID")
        payload = pcm_window(nu.WindowSpec(int(stream[1:]), window))
        _need(type(payload) is bytearray and len(payload) == row["pcm_byte_count"], "PCM_SUPPLIER_OUTPUT_INVALID")
        return payload

    return supply
