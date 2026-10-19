"""Bound S2-UC three-story connection with injected one-endpoint materialization."""
from __future__ import annotations

import hashlib

from tools import _s2tu_retained_trace as tu
from tools import _s2ub_candidate_confirmation as ub
from tools import _s2uc_source_binding as binding


class S2UCConnectionError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _need(ok: bool, code: str) -> None:
    if not ok:
        raise S2UCConnectionError(code)


def _hex(values: tuple[float, ...]) -> list[str]:
    return [value.hex() for value in values]

def _materialized(value):
    """Accept the legacy neutral tuple or one bound S2-TY materialization receipt."""
    if type(value) is tuple:
        return value, None
    if type(value) is not dict:
        raise S2UCConnectionError("MATERIALIZATION_VALUES_INVALID")
    values = value.get("values")
    receipt = {key: item for key, item in value.items() if key != "values"}
    required = {"pcm_sha256", "payload_bytes", "raw_state_digest", "projection_digest", "source_values_digest", "projection_binding", "subnormal_band_indices", "underflow_band_indices"}
    _need(required <= set(receipt), "MATERIALIZATION_RECEIPT_INVALID")
    return values, receipt

def _close_pair(immediate, candidate, counts):
    receipts = {}
    for name, arm in (("immediate", immediate), ("candidate", candidate)):
        try:
            arm.close_owner(); receipts[name] = {"closed": True}
        except Exception as exc:
            receipts[name] = {"closed": False, "error": getattr(exc, "code", type(exc).__name__)}
        counts["owner_closes"] += 1
    return receipts


def execute(manifest: dict[str, object], materialize, *, owners=None) -> dict[str, object]:
    """Run all bound stories using a neutral injected materializer.

    `materialize(endpoint)` must return exactly one immutable 48-value tuple.
    The function is deliberately not a source supplier and does not open PCM.
    """
    binding.validate(manifest)
    _need(callable(materialize), "MATERIALIZER_INVALID")
    counts = {"materialization_attempts": 0, "materializations": 0, "formations": 0, "hint_frames": 0, "segment_closes": 0, "owner_closes": 0, "immediate_calls": 0, "candidate_calls": 0}
    stories, current, failure = [], None, None
    create = owners or (lambda cls, *args: cls(*args))
    for story in ("g1", "g2", "g3"):
        immediate = create(ub.ImmediateTwArm, manifest["profile"], f"s2uc-{story}-tw")
        candidate = create(ub.CandidateConfirmationArm, manifest["profile"], f"s2uc-{story}-candidate")
        events, transitions, hints, completed, hint_pre = [], [], [], 0, {}
        try:
            for event in (row for row in manifest["events"] if row["story"] == story):
                current = {"story": story, "ordinal": event["ordinal"], "story_ordinal": event["story_ordinal"], "counts": dict(counts)}
                if event["kind"] == "CLOSE":
                    counts["immediate_calls"] += 1; current["counts"] = dict(counts); left = immediate.close_segment(event["segment"])
                    counts["candidate_calls"] += 1; current["counts"] = dict(counts); right = candidate.close_segment(event["segment"])
                    transitions.append({"ordinal": event["ordinal"], "immediate": left, "candidate": right,
                                        "immediate_inventory": immediate.inventory, "candidate_inventory": candidate.inventory})
                    counts["segment_closes"] += 1
                    events.append({"ordinal": event["ordinal"], "kind": "CLOSE", "segment": event["segment"]})
                else:
                    counts["materialization_attempts"] += 1; current["counts"] = dict(counts)
                    values, materialization = _materialized(materialize(event["endpoint"]))
                    _need(type(values) is tuple and len(values) == 48 and all(type(value) is float for value in values), "MATERIALIZATION_VALUES_INVALID")
                    counts["materializations"] += 1; current["counts"] = dict(counts)
                    left_frame = tu.Frame(values, manifest["profile"], immediate.store.owner, event["segment"], event["ordinal"])
                    right_frame = tu.Frame(values, manifest["profile"], candidate.owner, event["segment"], event["ordinal"])
                    if event["kind"] == "HINT" and event["segment"] not in hint_pre:
                        hint_pre[event["segment"]] = {"immediate": immediate.evidence(), "candidate": candidate.evidence()}
                    before_hint = hint_pre.get(event["segment"])
                    counts["immediate_calls"] += 1; current["counts"] = dict(counts)
                    left = immediate.form(left_frame) if event["kind"] == "FORMATION" else immediate.hint(left_frame)
                    counts["candidate_calls"] += 1; current["counts"] = dict(counts)
                    right = candidate.form(right_frame) if event["kind"] == "FORMATION" else candidate.hint(right_frame)
                    _need(immediate.resources()["trace_frames"] <= 12 and candidate.resources()["trace_frames"] <= 12, "TRACE_FRAME_BUDGET_INVALID")
                    row = {"ordinal": event["ordinal"], "kind": event["kind"], "segment": event["segment"], "values_hex": _hex(values),
                           "source_id": event["endpoint"]["source_id"], "immediate": left, "candidate": right}
                    if materialization is not None:
                        row["materialization"] = materialization
                    events.append(row)
                    if event["kind"] == "FORMATION":
                        counts["formations"] += 1
                    else:
                        counts["hint_frames"] += 1
                        if left is not None:
                            hints.append({"ordinal": event["ordinal"], "segment": event["segment"], "immediate": left, "candidate": right,
                                          "immediate_before": before_hint["immediate"], "candidate_before": before_hint["candidate"],
                                          "immediate_after": immediate.evidence(), "candidate_after": candidate.evidence()})
                            hint_pre.pop(event["segment"], None)
                completed += 1
            before_close = {"immediate": immediate.evidence(), "candidate": candidate.evidence()}
            owner_closes = _close_pair(immediate, candidate, counts)
            if not all(receipt["closed"] for receipt in owner_closes.values()):
                failure = {"code": "OWNER_CLOSE_INVALID", "progress": {"story": story, "phase": "OWNER_CLOSE", "completed": completed, "counts": dict(counts)}, "completed_in_story": completed,
                           "owner_close_errors": {name: receipt["error"] for name, receipt in owner_closes.items() if not receipt["closed"]}}
                stories.append({"story": story, "status": "NOT_EVALUABLE", "events": events, "transitions": transitions, "hints": hints,
                                "before_close": before_close, "owner_closes": owner_closes, "closed": {"immediate": immediate.evidence(), "candidate": candidate.evidence()}, "completed": completed})
                break
            stories.append({"story": story, "status": "COMPLETE", "events": events, "transitions": transitions, "hints": hints,
                            "before_close": before_close, "owner_closes": owner_closes, "closed": {"immediate": immediate.evidence(), "candidate": candidate.evidence()}, "completed": completed})
        except Exception as exc:
            before_close = {"immediate": immediate.evidence(), "candidate": candidate.evidence()}
            owner_closes = _close_pair(immediate, candidate, counts)
            failure = {"code": getattr(exc, "code", type(exc).__name__), "progress": current, "completed_in_story": completed}
            stories.append({"story": story, "status": "NOT_EVALUABLE", "events": events, "transitions": transitions, "hints": hints,
                            "before_close": before_close, "owner_closes": owner_closes, "closed": {"immediate": immediate.evidence(), "candidate": candidate.evidence()}, "completed": completed})
            break
    started_stories = {row["story"] for row in stories}
    status = "COMPLETE" if failure is None else "NOT_EVALUABLE"
    not_executed = [story for story in ("g1", "g2", "g3") if story not in started_stories]
    return {"version": "s2uc.neutral-connection.v1", "status": status, "manifest_digest": manifest["binding_digest"],
            "counts": counts, "stories": stories, "not_executed": not_executed, "failure": failure,
            "terminal": {"status": "CLOSED" if failure is None else "CLOSED_AFTER_FAILURE", "started_stories": sorted(started_stories), "not_executed": not_executed}}
