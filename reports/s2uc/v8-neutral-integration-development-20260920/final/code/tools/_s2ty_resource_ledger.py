"""Static S2-TY budget accounting; this module does not authorize a run."""
from __future__ import annotations

from dataclasses import dataclass


WIDTH = 48
TRACE_FRAMES = 4
RETAINED_TRACES = 2
HINT_FRAMES = 2
ARMS = 2

LIMITS = {
    "native_float64_payload": 98_304,
    "metadata": 65_536,
    "shared": 262_144,
    "record": 262_144,
    "verification": 262_144,
    "total": 4_194_304,
}


class S2TYBudgetError(ValueError):
    def __init__(self, code: str, details: dict[str, object]) -> None:
        self.code = code
        self.details = details
        super().__init__(code)


@dataclass(frozen=True)
class PlannedShape:
    events: int
    endpoints: int
    formations: int
    hint_frames: int
    segment_closes: int

    def validate(self) -> None:
        if (
            (self.events, self.endpoints, self.formations, self.hint_frames, self.segment_closes)
            != (26, 22, 16, 6, 4)
        ):
            raise S2TYBudgetError("S2TY_SHAPE_INVALID", {"shape": self.__dict__})


def planned_shape() -> PlannedShape:
    """The S2-TW schedule shape, before any S2-TY source binding exists."""
    return PlannedShape(events=26, endpoints=22, formations=16, hint_frames=6, segment_closes=4)


def native_payload(shape: PlannedShape) -> dict[str, int]:
    shape.validate()
    frame_bytes = WIDTH * 8
    per_arm = {
        "retained": RETAINED_TRACES * TRACE_FRAMES * frame_bytes,
        "forming": TRACE_FRAMES * frame_bytes,
        "hints": HINT_FRAMES * frame_bytes,
    }
    values = {
        "adapter_retained": per_arm["retained"],
        "direct_retained": per_arm["retained"],
        "adapter_forming": per_arm["forming"],
        "direct_forming": per_arm["forming"],
        "adapter_hint_buffer": per_arm["hints"],
        "direct_hint_buffer": per_arm["hints"],
        "nj_half_endpoint": frame_bytes,
        "adapter_handoff": frame_bytes,
        "direct_handoff": frame_bytes,
        "pcm_window": 4800 * 4,
        "raw_receptor_endpoint": frame_bytes,
        # The one-at-a-time supplier does not retain PCM, but the completed
        # endpoint values remain queued until the existing trace is built.
        "materialized_half_queue": shape.endpoints * frame_bytes,
    }
    values["total"] = sum(values.values())
    return values


def materializer_workspace() -> dict[str, object]:
    """Known NumPy arrays, separate from bounded native MCM state.

    NumPy may allocate implementation-specific temporaries and Python object
    administration is not statically bounded by this package.  The number is
    therefore a lower bound, not a process-peak claim.
    """
    return {
        "receptor_configuration_bytes": 4_800 * 8 + 2_401 * 8 + 48 * 2_401 * 8,
        "fft_workspace_lower_bound_bytes": 4_800 * 8 + 2_401 * 16 + 2_401 * 8 + 2 * 48 * 2_401 * 8,
        "python_administration": "NOT_STATICALLY_BOUNDED",
    }


def _violation(code: str, branch: str, contributions: dict[str, int], total: int) -> S2TYBudgetError:
    return S2TYBudgetError(
        code,
        {
            "branch": branch,
            "contributions": contributions,
            "total_bytes": total,
            "limits": LIMITS,
            "phase": "PRESTART",
            "progress": 0,
        },
    )


def ledger(
    shape: PlannedShape,
    *,
    source_bytes: int | None,
    metadata_bytes: int,
    shared_bytes: int,
    success_record_bytes: int,
    failure_record_bytes: int,
    verification_bytes: int,
) -> dict[str, object]:
    """Return alternative success/failure envelopes without adding both records."""
    native = native_payload(shape)
    if native["total"] > LIMITS["native_float64_payload"]:
        raise _violation("NATIVE_PAYLOAD_LIMIT", "runtime", native, native["total"])
    if source_bytes is None:
        raise S2TYBudgetError("SOURCE_BINDING_UNRESOLVED", {"shape": shape.__dict__, "limits": LIMITS})
    values = (source_bytes, metadata_bytes, shared_bytes, success_record_bytes, failure_record_bytes, verification_bytes)
    if any(type(value) is not int or value < 0 for value in values):
        raise S2TYBudgetError("LEDGER_VALUE_INVALID", {"values": values})

    common = {"sources": source_bytes, "metadata": metadata_bytes, "shared": shared_bytes, "verification": verification_bytes}
    branches = {}
    for branch, record_bytes in (("success", success_record_bytes), ("failure", failure_record_bytes)):
        contributions = {**common, "record": record_bytes}
        total = sum(contributions.values())
        branches[branch] = {"contributions": contributions, "total_bytes": total}
        for key, limit in (("metadata", LIMITS["metadata"]), ("shared", LIMITS["shared"]), ("record", LIMITS["record"]), ("verification", LIMITS["verification"])):
            if contributions[key] > limit:
                raise _violation(f"{key.upper()}_LIMIT", branch, contributions, total)
        if total > LIMITS["total"]:
            raise _violation("TOTAL_LIMIT", branch, contributions, total)
    return {
        "shape": shape.__dict__,
        "native_payload_bytes": native,
        "materializer_workspace": materializer_workspace(),
        "branches": branches,
        "limits": LIMITS,
    }
