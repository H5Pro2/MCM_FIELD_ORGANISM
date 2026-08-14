"""S1-EC72 corrected static preflight with mandatory source integrity."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re

from .e1_common_probe_n2_r2_final_real_preflight import (
    E1CommonProbeN2R2FinalRealPreflight,
)
from .e1_common_probe_n2_r2_source_integrity_preflight import (
    E1CommonProbeN2R2SourceIntegrityPreflight,
)


class E1CommonProbeN2R2CorrectedFinalPreflightError(ValueError):
    """Raised when EC72 changes or releases the bounded real path."""


S1_EC72_PREFLIGHT_ID = (
    "e1.common-probe-n2-r2-corrected-final-preflight.s1ec72.v1"
)
S1_EC72_EC71_PREFLIGHT_DIGEST = (
    "15966ff850b5028cab9960c6fdd11914896c85e8edfa2da8c8e29092a33aa852"
)
S1_EC72_REQUIRED_CHECKS = (
    "ec68-technical-preflight-ready",
    "ec68-owner-release-absent-and-real-path-blocked",
    "ec71-source-integrity-preflight-exact",
    "ec71-all-registered-sources-exact",
    "planned-load-exactly-3208-field-steps",
    "resource-and-protected-artifact-digests-bound",
    "runtime-cap-nine-hundred-seconds",
    "in-memory-no-retry-persistence-decision-or-claim",
    "new-owner-execution-authorization-not-present",
)
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


@dataclass(frozen=True, slots=True)
class E1CommonProbeN2R2CorrectedFinalPreflight:
    preflight_id: str
    ec68_preflight_digest: str
    ec71_preflight_digest: str
    source_digests: tuple[tuple[str, str, str], ...]
    resource_snapshot_digest: str
    protected_artifact_audit_digest: str
    planned_formation_steps: int
    planned_probe_steps: int
    planned_total_steps: int
    maximum_runtime_seconds: float
    checks: tuple[tuple[str, bool], ...]
    technical_execution_ready: bool
    owner_execution_authorized: bool
    coordinator_execution_permitted: bool
    adapter_execution_permitted: bool
    retry_permitted: bool
    persistence_permitted: bool
    research_decision_permitted: bool
    ec46_decision_permitted: bool
    memory_claim_permitted: bool
    field_time_claim_permitted: bool
    organization_claim_permitted: bool
    ai_claim_permitted: bool
    decision: str
    reason: str
    preflight_digest: str

    def __post_init__(self) -> None:
        check_names = tuple(name for name, _ in self.checks)
        technical_ready = all(value for _, value in self.checks[:-1])
        expected_decision = (
            "TECHNISCH_BEREIT_QUELLGEBUNDEN_NEUE_EINMALLAUFFREIGABE_FEHLT"
            if technical_ready
            else "KORREKTUR_GESAMTPREFLIGHT_GATES"
        )
        if (
            self.preflight_id != S1_EC72_PREFLIGHT_ID
            or any(
                not _SHA256.fullmatch(digest)
                for digest in (
                    self.ec68_preflight_digest,
                    self.ec71_preflight_digest,
                    self.resource_snapshot_digest,
                    self.protected_artifact_audit_digest,
                )
            )
            or any(
                not _SHA256.fullmatch(digest)
                for _, expected, observed in self.source_digests
                for digest in (expected, observed)
            )
            or (
                self.planned_formation_steps,
                self.planned_probe_steps,
                self.planned_total_steps,
            )
            != (1608, 1600, 3208)
            or self.maximum_runtime_seconds != 900.0
            or check_names != S1_EC72_REQUIRED_CHECKS
            or self.technical_execution_ready is not technical_ready
            or any(
                value is not False
                for value in (
                    self.owner_execution_authorized,
                    self.coordinator_execution_permitted,
                    self.adapter_execution_permitted,
                    self.retry_permitted,
                    self.persistence_permitted,
                    self.research_decision_permitted,
                    self.ec46_decision_permitted,
                    self.memory_claim_permitted,
                    self.field_time_claim_permitted,
                    self.organization_claim_permitted,
                    self.ai_claim_permitted,
                )
            )
            or self.decision != expected_decision
            or not self.reason
        ):
            raise E1CommonProbeN2R2CorrectedFinalPreflightError(
                "S1-EC72 changed or released the bounded real path"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "preflight_digest"
        }
        if self.preflight_digest != _digest(payload):
            raise E1CommonProbeN2R2CorrectedFinalPreflightError(
                "S1-EC72 preflight digest changed"
            )


def audit_e1_common_probe_n2_r2_corrected_final_preflight(
    technical: E1CommonProbeN2R2FinalRealPreflight,
    source_integrity: E1CommonProbeN2R2SourceIntegrityPreflight,
) -> E1CommonProbeN2R2CorrectedFinalPreflight:
    """Combine EC68 and EC71 without accepting release or running the path."""

    if not isinstance(technical, E1CommonProbeN2R2FinalRealPreflight) or not isinstance(
        source_integrity, E1CommonProbeN2R2SourceIntegrityPreflight
    ):
        raise E1CommonProbeN2R2CorrectedFinalPreflightError(
            "S1-EC72 requires validated EC68 and EC71 preflights"
        )
    technical.__post_init__()
    source_integrity.__post_init__()
    checks = (
        ("ec68-technical-preflight-ready", technical.technical_execution_ready),
        (
            "ec68-owner-release-absent-and-real-path-blocked",
            not any(
                (
                    technical.owner_execution_authorized,
                    technical.coordinator_execution_permitted,
                    technical.adapter_execution_permitted,
                )
            ),
        ),
        (
            "ec71-source-integrity-preflight-exact",
            source_integrity.preflight_digest == S1_EC72_EC71_PREFLIGHT_DIGEST,
        ),
        (
            "ec71-all-registered-sources-exact",
            source_integrity.all_sources_exact
            and len(source_integrity.source_digests) == 4
            and not source_integrity.failed_sources,
        ),
        (
            "planned-load-exactly-3208-field-steps",
            (
                technical.planned_formation_steps,
                technical.planned_probe_steps,
                technical.planned_total_steps,
            )
            == (1608, 1600, 3208),
        ),
        (
            "resource-and-protected-artifact-digests-bound",
            bool(technical.resource_snapshot_digest)
            and bool(technical.protected_artifact_audit_digest),
        ),
        (
            "runtime-cap-nine-hundred-seconds",
            technical.maximum_runtime_seconds == 900.0,
        ),
        (
            "in-memory-no-retry-persistence-decision-or-claim",
            not any(
                (
                    technical.persistence_permitted,
                    technical.research_decision_permitted,
                    technical.ec46_decision_permitted,
                    technical.memory_claim_permitted,
                    source_integrity.retry_permitted,
                    source_integrity.persistence_permitted,
                    source_integrity.research_decision_permitted,
                    source_integrity.memory_claim_permitted,
                    source_integrity.field_time_claim_permitted,
                    source_integrity.organization_claim_permitted,
                    source_integrity.ai_claim_permitted,
                )
            ),
        ),
        ("new-owner-execution-authorization-not-present", False),
    )
    technical_ready = all(value for _, value in checks[:-1])
    values = {
        "preflight_id": S1_EC72_PREFLIGHT_ID,
        "ec68_preflight_digest": technical.preflight_digest,
        "ec71_preflight_digest": source_integrity.preflight_digest,
        "source_digests": source_integrity.source_digests,
        "resource_snapshot_digest": technical.resource_snapshot_digest,
        "protected_artifact_audit_digest": technical.protected_artifact_audit_digest,
        "planned_formation_steps": technical.planned_formation_steps,
        "planned_probe_steps": technical.planned_probe_steps,
        "planned_total_steps": technical.planned_total_steps,
        "maximum_runtime_seconds": technical.maximum_runtime_seconds,
        "checks": checks,
        "technical_execution_ready": technical_ready,
        "owner_execution_authorized": False,
        "coordinator_execution_permitted": False,
        "adapter_execution_permitted": False,
        "retry_permitted": False,
        "persistence_permitted": False,
        "research_decision_permitted": False,
        "ec46_decision_permitted": False,
        "memory_claim_permitted": False,
        "field_time_claim_permitted": False,
        "organization_claim_permitted": False,
        "ai_claim_permitted": False,
        "decision": (
            "TECHNISCH_BEREIT_QUELLGEBUNDEN_NEUE_EINMALLAUFFREIGABE_FEHLT"
            if technical_ready
            else "KORREKTUR_GESAMTPREFLIGHT_GATES"
        ),
        "reason": (
            "ec68-and-ec71-exact-explicit-new-owner-one-shot-release-required"
            if technical_ready
            else "one-or-more-technical-or-source-integrity-gates-failed"
        ),
    }
    return E1CommonProbeN2R2CorrectedFinalPreflight(
        **values,
        preflight_digest=_digest(values),
    )
