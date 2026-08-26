"""Typed digest schemas for one receptor proposal handoff."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re

from .receptor_proposal_handoff import ReceptorProposalHandoff


class E1HandoffDigestSchemaError(ValueError):
    """Raised when typed handoff digest roles are incomplete."""


_SHA256 = re.compile(r"[0-9a-f]{64}")


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _assignments(handoff: ReceptorProposalHandoff) -> list[tuple[object, ...]]:
    return [
        (
            group.completion_tick,
            tuple(
                (item.frame.modality_id, item.frame.snapshot_id)
                for item in group.timed_frames
            ),
        )
        for batch in handoff.batches
        for group in batch.completion_groups
    ]


@dataclass(frozen=True, slots=True)
class E1HandoffDigestPair:
    assignment_digest: str
    envelope_digest: str

    def __post_init__(self) -> None:
        if (
            not _SHA256.fullmatch(self.assignment_digest)
            or not _SHA256.fullmatch(self.envelope_digest)
        ):
            raise E1HandoffDigestSchemaError(
                "handoff digest pair requires two SHA-256 roles"
            )


def e1_handoff_digest_pair(
    handoff: ReceptorProposalHandoff,
) -> E1HandoffDigestPair:
    """Return the legacy runner assignment and planner envelope digests."""

    if not isinstance(handoff, ReceptorProposalHandoff):
        raise E1HandoffDigestSchemaError(
            "handoff digest pair requires ReceptorProposalHandoff"
        )
    assignments = _assignments(handoff)
    return E1HandoffDigestPair(
        assignment_digest=_digest(assignments),
        envelope_digest=_digest(
            {
                "clock_id": handoff.clock_id,
                "modality_ids": handoff.modality_ids,
                "source_event_count": handoff.source_event_count,
                "assigned_event_count": handoff.assigned_event_count,
                "assigned_once": handoff.every_in_horizon_event_assigned_once,
                "assignments": assignments,
            }
        ),
    )
