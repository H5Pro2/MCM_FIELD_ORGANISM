"""Fresh single-run preflight after the nullable baseline correction."""

from __future__ import annotations

from dataclasses import dataclass, fields
from pathlib import Path
from typing import get_args, get_origin, get_type_hints
import types

from .public_av_two_stage_return_execution import PublicAVTwoStageReturnArmResult
from .public_av_two_stage_return_preflight import (
    PublicAVTwoStageReturnPreflight,
    audit_public_av_two_stage_return_preflight,
)
from .public_media_source_contract import (
    PublicMediaSourceAudit,
    PublicMediaSourceContract,
)


class PublicAVTwoStageReturnRerunPreflightError(ValueError):
    """Raised when the corrected rerun preflight would exceed its boundary."""


@dataclass(frozen=True, slots=True)
class PublicAVTwoStageReturnRerunPreflight:
    preflight_id: str
    base_preflight_id: str
    source_id: str
    media_path: str
    nullable_baseline_role: str
    nullable_baseline_role_accepted: bool
    baseline_null_snapshot_is_not_synthetic: bool
    continued_snapshot_digest_required: bool
    base_single_run_release_granted: bool
    corrected_single_run_release_granted: bool
    release_scope: str
    field_run_started: bool = False
    repeat_count_authorized: int = 1
    raw_payload_retained: bool = False
    metadata_used_by_field: bool = False
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        if self.nullable_baseline_role != "post_resolution_snapshot_digest":
            raise PublicAVTwoStageReturnRerunPreflightError(
                "nullable baseline role changed"
            )
        if self.repeat_count_authorized != 1:
            raise PublicAVTwoStageReturnRerunPreflightError(
                "exactly one corrected rerun can be authorized"
            )
        required = (
            self.nullable_baseline_role_accepted,
            self.baseline_null_snapshot_is_not_synthetic,
            self.continued_snapshot_digest_required,
            self.base_single_run_release_granted,
        )
        if self.corrected_single_run_release_granted != all(required):
            raise PublicAVTwoStageReturnRerunPreflightError(
                "corrected single-run release must exactly follow the gate"
            )
        if (
            self.release_scope
            != "one_corrected_public_av_two_stage_return_run_nullable_baseline_v1"
        ):
            raise PublicAVTwoStageReturnRerunPreflightError("release scope changed")
        forbidden = (
            self.field_run_started,
            self.raw_payload_retained,
            self.metadata_used_by_field,
            self.memory_claim_allowed,
            self.meaning_claim_allowed,
            self.organization_claim_allowed,
            self.ai_claim_allowed,
        )
        if any(forbidden):
            raise PublicAVTwoStageReturnRerunPreflightError(
                "rerun preflight cannot start a run, retain payloads, or release claims"
            )


def _role_accepts_none(role: str) -> bool:
    annotation = get_type_hints(PublicAVTwoStageReturnArmResult)[role]
    origin = get_origin(annotation)
    args = get_args(annotation)
    return (
        annotation is None
        or type(None) in args
        or (origin is types.UnionType and type(None) in args)
    )


def audit_public_av_two_stage_return_rerun_preflight(
    path: Path,
    contract: PublicMediaSourceContract | None = None,
    *,
    source_audit: PublicMediaSourceAudit | None = None,
    base_preflight: PublicAVTwoStageReturnPreflight | None = None,
) -> PublicAVTwoStageReturnRerunPreflight:
    """Create a fresh preflight for one corrected full run; do not execute it."""

    base = base_preflight or audit_public_av_two_stage_return_preflight(
        path,
        contract,
        source_audit=source_audit,
    )
    if not isinstance(base, PublicAVTwoStageReturnPreflight):
        raise PublicAVTwoStageReturnRerunPreflightError(
            "base two-stage preflight is required"
        )
    nullable_role = "post_resolution_snapshot_digest"
    nullable_accepted = _role_accepts_none(nullable_role)
    corrected_release = (
        base.single_bounded_run_release_granted
        and nullable_accepted
        and not base.field_run_started
    )
    return PublicAVTwoStageReturnRerunPreflight(
        preflight_id="public.av.nasa-earthrise.two-stage-return.rerun-preflight.v1",
        base_preflight_id=base.preflight_id,
        source_id=base.source_id,
        media_path=base.media_path,
        nullable_baseline_role=nullable_role,
        nullable_baseline_role_accepted=nullable_accepted,
        baseline_null_snapshot_is_not_synthetic=True,
        continued_snapshot_digest_required=True,
        base_single_run_release_granted=base.single_bounded_run_release_granted,
        corrected_single_run_release_granted=corrected_release,
        release_scope="one_corrected_public_av_two_stage_return_run_nullable_baseline_v1",
    )


def public_av_two_stage_return_rerun_preflight_json_value(
    preflight: PublicAVTwoStageReturnRerunPreflight,
) -> dict[str, object]:
    if not isinstance(preflight, PublicAVTwoStageReturnRerunPreflight):
        raise PublicAVTwoStageReturnRerunPreflightError(
            "corrected rerun preflight is required"
        )
    return {item.name: getattr(preflight, item.name) for item in fields(preflight)}


def public_av_two_stage_return_rerun_preflight_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(PublicAVTwoStageReturnRerunPreflight))
