"""Private S1-DR classification of the completed E1 transfer milestone."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from .e1_frozen_state_transfer_result_audit import (
    S1_DQ_RESULT_SHA256,
    audit_e1_frozen_state_transfer_result,
)


class E1SubstrateMilestoneClassificationError(ValueError):
    """Raised when the narrow S1-DR evidence classification changes."""


S1_DR_STATUS = "GIVEN_STATE_TRANSFER_MILESTONE_ONLY"
S1_DR_NEXT_STAGE = "NEW_REFINED_WORLD_FORMATION_CONTRACT_REQUIRED"


def _digest(value: object) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class E1SubstrateMilestoneClassification:
    result_sha256: str
    status: str
    given_state_changes_later_field: bool
    effect_is_ablatable: bool
    fixed_adapter_equivalent: bool
    world_formation_causality_established: bool
    reconstruction_established: bool
    memory_lifecycle_established: bool
    full_s1_dc_decision_permitted: bool
    next_stage: str
    classification_digest: str

    def __post_init__(self) -> None:
        if (
            self.result_sha256 != S1_DQ_RESULT_SHA256
            or self.status != S1_DR_STATUS
            or self.given_state_changes_later_field is not True
            or self.effect_is_ablatable is not True
            or self.fixed_adapter_equivalent is not True
            or self.world_formation_causality_established is not False
            or self.reconstruction_established is not False
            or self.memory_lifecycle_established is not False
            or self.full_s1_dc_decision_permitted is not False
            or self.next_stage != S1_DR_NEXT_STAGE
            or len(self.classification_digest) != 64
        ):
            raise E1SubstrateMilestoneClassificationError(
                "S1-DR classification boundary changed"
            )


def classify_e1_substrate_milestone(
    transfer_report_path: Path,
) -> E1SubstrateMilestoneClassification:
    """Classify only what follows from the audited, already published report."""

    audit = audit_e1_frozen_state_transfer_result(transfer_report_path)
    report = json.loads(Path(transfer_report_path).read_text(encoding="ascii"))
    metrics = dict(report["metrics"])
    controls = dict(report["controls"])
    payload = {
        "result_sha256": audit.result_sha256,
        "status": S1_DR_STATUS,
        "given_state_changes_later_field": (
            min(audit.d_active_s, audit.d_active_h) > audit.d_probe_partition
        ),
        "effect_is_ablatable": (
            metrics["d_ablation"] == 0.0
            and controls["p0_equals_ab0_equals_ba0_bit_exact"] is True
        ),
        "fixed_adapter_equivalent": (
            metrics["d_fixed_adapter"] == 0.0
            and controls["ab1_equals_abf_bit_exact"] is True
            and controls["ba1_equals_baf_bit_exact"] is True
        ),
        "world_formation_causality_established": False,
        "reconstruction_established": False,
        "memory_lifecycle_established": False,
        "full_s1_dc_decision_permitted": False,
        "next_stage": S1_DR_NEXT_STAGE,
    }
    return E1SubstrateMilestoneClassification(
        **payload,
        classification_digest=_digest(payload),
    )
