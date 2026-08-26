"""Static S1-EC25 audit of remaining functions after the S1-EC24 result."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .e1_confirmation_full_probe_result_audit import (
    E1FullProbeResultAudit,
    audit_full_published_probe_result,
)
from .e1_refined_formation_runner import _digest


class E1MemoryFunctionGapAuditError(ValueError):
    """Raised when the S1-EC25 evidence map or ordering is inconsistent."""


S1_EC25_AUDIT_ID = "e1.memory-function-gap-audit.s1ec25.v1"
S1_EC25_FUNCTIONS = (
    "locally-field-changeable-substrate",
    "repetition-dependent-formation",
    "field-internal-attenuation",
    "partial-cue-reconstruction",
    "released-capacity-reuse",
    "changed-substrate-affects-later-field-intake",
)
S1_EC25_STATUSES = (
    "TECHNICALLY_AVAILABLE_NOT_MEMORY",
    "OPEN_NEXT_CAUSAL_FUNCTION",
    "BLOCKED_UNTIL_REPETITION_FORMATION",
    "CURRENT_E1_CUE_RESPONSE_LINEAR_NOT_RECONSTRUCTION",
    "TECHNICALLY_AVAILABLE_OUTSIDE_CURRENT_AV_CHAIN_NOT_MEMORY",
    "NUMERICALLY_CONFIRMED_NOT_MEMORY",
)
S1_EC25_NEXT_FUNCTION = "repetition-dependent-formation"
S1_EC25_NEXT_STEP = "S1-EC26_STATIC_REPETITION_FORMATION_CONTRACT"
S1_EC25_REQUIRED_COMPARISONS = (
    "one-two-four-eight-separated-contacts",
    "duration-matched-continuous-contact",
    "energy-and-time-matched-passive-baseline",
    "p0-and-formation-ablation",
    "same-later-probe-on-fresh-identical-fields",
    "matching-fixed-adapter-as-transfer-control-only",
    "r2-r4-r8-numerical-refinement",
)
S1_EC25_STOPPED_CONTINUATIONS = (
    "more-partial-cue-amplitude-variants-of-current-linear-e1-path",
    "gap-or-attenuation-interpretation-before-repetition-formation",
    "memory-ai-semantics-organization-or-topology-claim",
)


@dataclass(frozen=True, slots=True)
class E1MemoryFunctionGapAudit:
    audit_id: str
    upstream_audit_digest: str
    upstream_technical_decision: str
    functions: tuple[tuple[str, str], ...]
    next_function: str
    next_step: str
    required_comparisons: tuple[str, ...]
    stopped_continuations: tuple[str, ...]
    selection_reason: str
    field_execution_performed: bool
    mechanism_implemented: bool
    memory_claim_permitted: bool
    ai_claim_permitted: bool
    audit_digest: str

    def __post_init__(self) -> None:
        expected_functions = tuple(zip(
            S1_EC25_FUNCTIONS,
            S1_EC25_STATUSES,
            strict=True,
        ))
        if (
            self.audit_id != S1_EC25_AUDIT_ID
            or len(self.upstream_audit_digest) != 64
            or self.upstream_technical_decision
            != "CONFIRMED_NUMERICALLY_CLEAR_PERSISTENT_STATE_PROBE_DIFFERENCE"
            or self.functions != expected_functions
            or self.next_function != S1_EC25_NEXT_FUNCTION
            or self.next_step != S1_EC25_NEXT_STEP
            or self.required_comparisons != S1_EC25_REQUIRED_COMPARISONS
            or self.stopped_continuations != S1_EC25_STOPPED_CONTINUATIONS
            or self.selection_reason
            != "formation-before-attenuation-reconstruction-and-memory-interpretation"
            or any(
                value is not False
                for value in (
                    self.field_execution_performed,
                    self.mechanism_implemented,
                    self.memory_claim_permitted,
                    self.ai_claim_permitted,
                )
            )
        ):
            raise E1MemoryFunctionGapAuditError(
                "S1-EC25 function ordering or evidence boundary changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "audit_digest"
        }
        if self.audit_digest != _digest(payload):
            raise E1MemoryFunctionGapAuditError(
                "S1-EC25 audit digest changed"
            )


def audit_e1_memory_function_gaps(
    s1ec23_report_path: Path,
) -> E1MemoryFunctionGapAudit:
    """Rank open functions from protected evidence without running a field."""

    upstream: E1FullProbeResultAudit = audit_full_published_probe_result(
        s1ec23_report_path
    )
    functions = tuple(zip(
        S1_EC25_FUNCTIONS,
        S1_EC25_STATUSES,
        strict=True,
    ))
    payload = {
        "audit_id": S1_EC25_AUDIT_ID,
        "upstream_audit_digest": upstream.audit_digest,
        "upstream_technical_decision": upstream.technical_decision,
        "functions": functions,
        "next_function": S1_EC25_NEXT_FUNCTION,
        "next_step": S1_EC25_NEXT_STEP,
        "required_comparisons": S1_EC25_REQUIRED_COMPARISONS,
        "stopped_continuations": S1_EC25_STOPPED_CONTINUATIONS,
        "selection_reason": (
            "formation-before-attenuation-reconstruction-and-memory-interpretation"
        ),
        "field_execution_performed": False,
        "mechanism_implemented": False,
        "memory_claim_permitted": False,
        "ai_claim_permitted": False,
    }
    return E1MemoryFunctionGapAudit(
        **payload,
        audit_digest=_digest(payload),
    )
