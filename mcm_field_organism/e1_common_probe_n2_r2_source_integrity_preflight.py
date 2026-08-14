"""S1-EC71 static source-integrity preflight for the bounded n2/r2 real path."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re


class E1CommonProbeN2R2SourceIntegrityPreflightError(ValueError):
    """Raised when the EC71 source-integrity contract is incomplete."""


S1_EC71_PREFLIGHT_ID = (
    "e1.common-probe-n2-r2-source-integrity-preflight.s1ec71.v1"
)
S1_EC71_EXPECTED_SOURCE_DIGESTS = (
    (
        "e1_common_probe_n2_r2_real_output_converters.py",
        "6e72f30489be527a6da1cb06fa8d45c16bff518e6bedddc55a45c8101a70225d",
    ),
    (
        "e1_common_probe_n2_r2_real_call_adapters.py",
        "4fc2159d573570f11df27e0437f4dead219abfa6ccae6f71f9bb1dc313c69220",
    ),
    (
        "e1_common_probe_n2_r2_real_mode_coordinator.py",
        "b56a922153959b97ed69b4936074f2bed6b0cdc2a787aaf80a07f88e4d25c230",
    ),
    (
        "e1_handoff_digest_schemas.py",
        "92265285bf4482faafa6cef3f1c64e3fad97e3ea686ad188debeb9dc6733a105",
    ),
)
S1_EC71_REQUIRED_CHECKS = (
    "ec64-output-converter-source-exact",
    "ec65-real-call-adapter-source-exact",
    "ec67-real-mode-coordinator-source-exact",
    "ec75-handoff-digest-schema-source-exact",
    "source-set-complete-and-ordered",
    "real-execution-remains-blocked",
    "persistence-decision-and-claims-remain-blocked",
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


def _normalized_source_digest(path: Path) -> str:
    if not path.is_file():
        raise E1CommonProbeN2R2SourceIntegrityPreflightError(
            f"S1-EC71 source is missing: {path.name}"
        )
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class E1CommonProbeN2R2SourceIntegrityPreflight:
    preflight_id: str
    source_digests: tuple[tuple[str, str, str], ...]
    checks: tuple[tuple[str, bool], ...]
    all_sources_exact: bool
    failed_sources: tuple[str, ...]
    real_execution_permitted: bool
    retry_permitted: bool
    persistence_permitted: bool
    research_decision_permitted: bool
    memory_claim_permitted: bool
    field_time_claim_permitted: bool
    organization_claim_permitted: bool
    ai_claim_permitted: bool
    decision: str
    preflight_digest: str

    def __post_init__(self) -> None:
        expected_names = tuple(name for name, _ in S1_EC71_EXPECTED_SOURCE_DIGESTS)
        observed_names = tuple(name for name, _, _ in self.source_digests)
        source_exact = tuple(
            expected == observed for _, expected, observed in self.source_digests
        )
        expected_failed = tuple(
            name
            for (name, _, _), exact in zip(
                self.source_digests, source_exact, strict=True
            )
            if not exact
        )
        expected_decision = (
            "SOURCE_INTEGRITY_EXACT_REAL_EXECUTION_STILL_BLOCKED"
            if all(source_exact)
            else "KORREKTUR_SOURCE_INTEGRITY_MISMATCH"
        )
        if (
            self.preflight_id != S1_EC71_PREFLIGHT_ID
            or observed_names != expected_names
            or any(
                expected != registered
                for (_, expected, _), (_, registered) in zip(
                    self.source_digests,
                    S1_EC71_EXPECTED_SOURCE_DIGESTS,
                    strict=True,
                )
            )
            or any(
                not _SHA256.fullmatch(digest)
                for _, expected, observed in self.source_digests
                for digest in (expected, observed)
            )
            or tuple(name for name, _ in self.checks) != S1_EC71_REQUIRED_CHECKS
            or self.all_sources_exact is not all(source_exact)
            or self.failed_sources != expected_failed
            or any(
                value is not False
                for value in (
                    self.real_execution_permitted,
                    self.retry_permitted,
                    self.persistence_permitted,
                    self.research_decision_permitted,
                    self.memory_claim_permitted,
                    self.field_time_claim_permitted,
                    self.organization_claim_permitted,
                    self.ai_claim_permitted,
                )
            )
            or self.decision != expected_decision
        ):
            raise E1CommonProbeN2R2SourceIntegrityPreflightError(
                "S1-EC71 source-integrity contract changed or released execution"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "preflight_digest"
        }
        if self.preflight_digest != _digest(payload):
            raise E1CommonProbeN2R2SourceIntegrityPreflightError(
                "S1-EC71 preflight digest changed"
            )


def audit_e1_common_probe_n2_r2_source_integrity(
    package_root: Path | None = None,
) -> E1CommonProbeN2R2SourceIntegrityPreflight:
    """Hash the three registered sources without invoking the real path."""

    root = Path(__file__).parent if package_root is None else Path(package_root)
    source_digests = tuple(
        (name, expected, _normalized_source_digest(root / name))
        for name, expected in S1_EC71_EXPECTED_SOURCE_DIGESTS
    )
    source_exact = tuple(
        expected == observed for _, expected, observed in source_digests
    )
    all_exact = all(source_exact)
    checks = (
        ("ec64-output-converter-source-exact", source_exact[0]),
        ("ec65-real-call-adapter-source-exact", source_exact[1]),
        ("ec67-real-mode-coordinator-source-exact", source_exact[2]),
        ("ec75-handoff-digest-schema-source-exact", source_exact[3]),
        (
            "source-set-complete-and-ordered",
            tuple(name for name, _, _ in source_digests)
            == tuple(name for name, _ in S1_EC71_EXPECTED_SOURCE_DIGESTS),
        ),
        ("real-execution-remains-blocked", True),
        ("persistence-decision-and-claims-remain-blocked", True),
    )
    values = {
        "preflight_id": S1_EC71_PREFLIGHT_ID,
        "source_digests": source_digests,
        "checks": checks,
        "all_sources_exact": all_exact,
        "failed_sources": tuple(
            name
            for (name, _, _), exact in zip(source_digests, source_exact, strict=True)
            if not exact
        ),
        "real_execution_permitted": False,
        "retry_permitted": False,
        "persistence_permitted": False,
        "research_decision_permitted": False,
        "memory_claim_permitted": False,
        "field_time_claim_permitted": False,
        "organization_claim_permitted": False,
        "ai_claim_permitted": False,
        "decision": (
            "SOURCE_INTEGRITY_EXACT_REAL_EXECUTION_STILL_BLOCKED"
            if all_exact
            else "KORREKTUR_SOURCE_INTEGRITY_MISMATCH"
        ),
    }
    return E1CommonProbeN2R2SourceIntegrityPreflight(
        **values,
        preflight_digest=_digest(values),
    )
