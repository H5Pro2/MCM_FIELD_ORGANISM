"""Private, pure S2-GI projection of one validated S2-GC context bundle."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re

from tools import _s2gb_private_perceptual_context_bundle as context


S2GI_SCHEMA = "s2gi.two-area-context-bundle.v1"
S2GH_CONTRACT_DIGEST = (
    "379597b4705755c83f336dee7e42460d7fa608d9572cdda9dde00e8cc7977e13"
)
AREAS = ("A_RECENT", "B_STABLE")

S2GI_INVALID_TYPE_OR_SCHEMA = "S2GI_INVALID_TYPE_OR_SCHEMA"
S2GI_BUNDLE_INVALID = "S2GI_BUNDLE_INVALID"
S2GI_BINDING_INVALID = "S2GI_BINDING_INVALID"
S2GI_ROLE_INVALID = "S2GI_ROLE_INVALID"
S2GI_DIMENSION_INVALID = "S2GI_DIMENSION_INVALID"
S2GI_CAPACITY_EXCEEDED = "S2GI_CAPACITY_EXCEEDED"
S2GI_DIGEST_MISMATCH = "S2GI_DIGEST_MISMATCH"
S2GI_READ_ONLY_VIOLATION = "S2GI_READ_ONLY_VIOLATION"

_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class S2GIProjectionError(RuntimeError):
    """One terminal, fail-closed S2-GI projection error."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise S2GIProjectionError(code, message)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


def _translate_s2gb_error(error: context.S2GBProjectionError) -> S2GIProjectionError:
    code_map = {
        context.S2GB_INVALID_TYPE_OR_SCHEMA: S2GI_INVALID_TYPE_OR_SCHEMA,
        context.S2GB_SOURCE_BINDING_INVALID: S2GI_BINDING_INVALID,
        context.S2GB_PROBE_MISMATCH: S2GI_BINDING_INVALID,
        context.S2GB_STATE_DIGEST_MISMATCH: S2GI_BINDING_INVALID,
        context.S2GB_EVIDENCE_INVALID: S2GI_BUNDLE_INVALID,
        context.S2GB_DIMENSION_INVALID: S2GI_DIMENSION_INVALID,
        context.S2GB_DUPLICATE_SOURCE: S2GI_BUNDLE_INVALID,
        context.S2GB_CAPACITY_EXCEEDED: S2GI_CAPACITY_EXCEEDED,
        context.S2GB_DIGEST_MISMATCH: S2GI_DIGEST_MISMATCH,
        context.S2GB_READ_ONLY_VIOLATION: S2GI_READ_ONLY_VIOLATION,
    }
    return S2GIProjectionError(
        code_map.get(error.code, S2GI_BUNDLE_INVALID),
        "S2-GC bundle validation failed",
    )


@dataclass(frozen=True, slots=True)
class AreaARecentFinding:
    area: str
    recent_content: context.PerceptualContextRoleFinding
    fast_internal: context.PerceptualContextRoleFinding
    short_sequence: context.B4ShortSequenceFinding
    finding_digest: str
    schema: str = S2GI_SCHEMA

    def __post_init__(self) -> None:
        _require(self.area == "A_RECENT", S2GI_ROLE_INVALID, "A area differs")
        _require(
            type(self.recent_content) is context.PerceptualContextRoleFinding
            and self.recent_content.role == "B4_RECENT",
            S2GI_ROLE_INVALID,
            "A recent role differs",
        )
        _require(
            type(self.fast_internal) is context.PerceptualContextRoleFinding
            and self.fast_internal.role == "TSPM_FAST",
            S2GI_ROLE_INVALID,
            "A fast role differs",
        )
        _require(
            type(self.short_sequence) is context.B4ShortSequenceFinding,
            S2GI_INVALID_TYPE_OR_SCHEMA,
            "A sequence finding differs",
        )
        _require(
            self.schema == S2GI_SCHEMA
            and self.finding_digest == _digest(self.payload_without_digest()),
            S2GI_DIGEST_MISMATCH,
            "A finding digest differs",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "area": self.area,
            "recent_content_finding_digest": self.recent_content.finding_digest,
            "fast_internal_finding_digest": self.fast_internal.finding_digest,
            "short_sequence_finding_digest": self.short_sequence.finding_digest,
        }


@dataclass(frozen=True, slots=True)
class AreaBStableFinding:
    area: str
    stable_content: context.PerceptualContextRoleFinding
    finding_digest: str
    schema: str = S2GI_SCHEMA

    def __post_init__(self) -> None:
        _require(self.area == "B_STABLE", S2GI_ROLE_INVALID, "B area differs")
        _require(
            type(self.stable_content) is context.PerceptualContextRoleFinding
            and self.stable_content.role == "TSPM_SLOW",
            S2GI_ROLE_INVALID,
            "B Slow role differs",
        )
        if self.stable_content.status == "ABSENT_VALID":
            _require(
                self.stable_content.candidate is None,
                S2GI_BUNDLE_INVALID,
                "absent B area contains a candidate",
            )
        else:
            candidate = self.stable_content.candidate
            _require(
                candidate is not None
                and all(component.stable is True for component in candidate.components),
                S2GI_BUNDLE_INVALID,
                "B area contains a nonstable component",
            )
        _require(
            self.schema == S2GI_SCHEMA
            and self.finding_digest == _digest(self.payload_without_digest()),
            S2GI_DIGEST_MISMATCH,
            "B finding digest differs",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "area": self.area,
            "stable_content_finding_digest": self.stable_content.finding_digest,
        }


@dataclass(frozen=True, slots=True)
class TwoAreaContextResourceLedger:
    validated_bundle_count: int
    validated_role_count: int
    candidate_reference_count: int
    component_reference_count: int
    value_reference_count: int
    sequence_reference_count: int
    area_projection_count: int
    digest_operation_count: int
    source_ledger_digest: str
    ledger_digest: str
    schema: str = S2GI_SCHEMA

    def __post_init__(self) -> None:
        counts = (
            self.validated_bundle_count,
            self.validated_role_count,
            self.candidate_reference_count,
            self.component_reference_count,
            self.value_reference_count,
            self.sequence_reference_count,
            self.area_projection_count,
            self.digest_operation_count,
        )
        _require(
            all(type(value) is int and value >= 0 for value in counts),
            S2GI_BUNDLE_INVALID,
            "ledger count differs",
        )
        _require(
            self.validated_bundle_count == 1
            and self.validated_role_count == 3
            and self.candidate_reference_count <= context.MAX_CANDIDATES
            and self.component_reference_count <= context.MAX_COMPONENTS
            and self.value_reference_count <= context.MAX_VALUES
            and self.sequence_reference_count <= context.MAX_SEQUENCE_REFERENCES
            and self.area_projection_count == 2
            and self.digest_operation_count == 4,
            S2GI_CAPACITY_EXCEEDED,
            "two-area ledger exceeds a bound",
        )
        _require(
            _valid_digest(self.source_ledger_digest),
            S2GI_DIGEST_MISMATCH,
            "source ledger digest differs",
        )
        _require(
            self.schema == S2GI_SCHEMA
            and self.ledger_digest == _digest(self.payload_without_digest()),
            S2GI_DIGEST_MISMATCH,
            "two-area ledger digest differs",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "validated_bundle_count": self.validated_bundle_count,
            "validated_role_count": self.validated_role_count,
            "candidate_reference_count": self.candidate_reference_count,
            "component_reference_count": self.component_reference_count,
            "value_reference_count": self.value_reference_count,
            "sequence_reference_count": self.sequence_reference_count,
            "area_projection_count": self.area_projection_count,
            "digest_operation_count": self.digest_operation_count,
            "source_ledger_digest": self.source_ledger_digest,
        }


@dataclass(frozen=True, slots=True)
class TwoAreaContextBundle:
    contract_digest: str
    source_bundle_digest: str
    binding_digest: str
    config_digest: str
    composite_state_digest: str
    probe_digest: str
    source_digest: str
    area_findings: tuple[AreaARecentFinding, AreaBStableFinding]
    resource_ledger: TwoAreaContextResourceLedger
    prestate_digest: str
    poststate_digest: str
    automatic_selection: None
    bundle_digest: str
    schema: str = S2GI_SCHEMA

    def __post_init__(self) -> None:
        _require(
            type(self.area_findings) is tuple
            and len(self.area_findings) == 2
            and type(self.area_findings[0]) is AreaARecentFinding
            and type(self.area_findings[1]) is AreaBStableFinding
            and tuple(item.area for item in self.area_findings) == AREAS,
            S2GI_ROLE_INVALID,
            "exactly two canonical areas are required",
        )
        _require(
            type(self.resource_ledger) is TwoAreaContextResourceLedger,
            S2GI_INVALID_TYPE_OR_SCHEMA,
            "two-area resource ledger differs",
        )
        _require(
            self.contract_digest == S2GH_CONTRACT_DIGEST,
            S2GI_BINDING_INVALID,
            "S2-GH contract binding differs",
        )
        _require(
            all(
                _valid_digest(value)
                for value in (
                    self.source_bundle_digest,
                    self.binding_digest,
                    self.config_digest,
                    self.composite_state_digest,
                    self.probe_digest,
                    self.source_digest,
                )
            ),
            S2GI_BINDING_INVALID,
            "two-area source binding differs",
        )
        _require(
            self.prestate_digest == self.poststate_digest == self.composite_state_digest,
            S2GI_READ_ONLY_VIOLATION,
            "two-area projection changed the source state",
        )
        _require(
            self.automatic_selection is None,
            S2GI_BUNDLE_INVALID,
            "automatic selection is forbidden",
        )
        _require(
            self.schema == S2GI_SCHEMA
            and self.bundle_digest == _digest(self.payload_without_digest()),
            S2GI_DIGEST_MISMATCH,
            "two-area bundle digest differs",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "contract_digest": self.contract_digest,
            "source_bundle_digest": self.source_bundle_digest,
            "binding_digest": self.binding_digest,
            "config_digest": self.config_digest,
            "composite_state_digest": self.composite_state_digest,
            "probe_digest": self.probe_digest,
            "source_digest": self.source_digest,
            "area_finding_digests": [item.finding_digest for item in self.area_findings],
            "resource_ledger_digest": self.resource_ledger.ledger_digest,
            "prestate_digest": self.prestate_digest,
            "poststate_digest": self.poststate_digest,
            "automatic_selection": self.automatic_selection,
        }


def _validate_s2gc_bundle(bundle: context.PerceptualContextBundle) -> None:
    _require(
        type(bundle) is context.PerceptualContextBundle,
        S2GI_INVALID_TYPE_OR_SCHEMA,
        "exact S2-GC bundle type required",
    )
    _require(
        bundle.schema == context.S2GB_SCHEMA
        and bundle.contract_digest == context.S2GA_CONTRACT_DIGEST,
        S2GI_INVALID_TYPE_OR_SCHEMA,
        "S2-GC schema or contract differs",
    )
    _require(
        all(
            _valid_digest(value)
            for value in (
                bundle.binding_digest,
                bundle.config_digest,
                bundle.composite_state_digest,
                bundle.probe_digest,
                bundle.source_digest,
                bundle.prestate_digest,
                bundle.poststate_digest,
                bundle.bundle_digest,
            )
        ),
        S2GI_BINDING_INVALID,
        "S2-GC source binding differs",
    )
    _require(
        type(bundle.role_findings) is tuple
        and len(bundle.role_findings) == 3
        and tuple(item.role for item in bundle.role_findings) == context.ROLES,
        S2GI_ROLE_INVALID,
        "S2-GC roles differ",
    )
    _require(
        type(bundle.sequence_finding) is context.B4ShortSequenceFinding
        and type(bundle.resource_ledger) is context.PerceptualContextResourceLedger,
        S2GI_INVALID_TYPE_OR_SCHEMA,
        "S2-GC sequence or ledger differs",
    )

    candidates: list[context.PerceptualContextCandidate] = []
    components: list[context.PerceptualContextComponent] = []
    try:
        for role_finding in bundle.role_findings:
            _require(
                type(role_finding) is context.PerceptualContextRoleFinding,
                S2GI_INVALID_TYPE_OR_SCHEMA,
                "S2-GC role finding type differs",
            )
            if role_finding.candidate is not None:
                candidates.append(role_finding.candidate)
                components.extend(role_finding.candidate.components)
                for component in role_finding.candidate.components:
                    component.__post_init__()
                role_finding.candidate.__post_init__()
            role_finding.__post_init__()
        for reference in bundle.sequence_finding.references:
            reference.__post_init__()
        bundle.sequence_finding.__post_init__()
        bundle.resource_ledger.__post_init__()
        bundle.__post_init__()
    except context.S2GBProjectionError as error:
        raise _translate_s2gb_error(error) from error

    value_count = sum(len(component.values) for component in components)
    _require(
        len(candidates) == bundle.resource_ledger.candidate_count
        and len(components) == bundle.resource_ledger.component_count
        and value_count == bundle.resource_ledger.value_count
        and len(bundle.sequence_finding.references)
        == bundle.resource_ledger.sequence_reference_count,
        S2GI_BUNDLE_INVALID,
        "S2-GC resource ledger does not describe its bundle",
    )
    source_digests = tuple(component.source_digest for component in components)
    _require(
        len(source_digests) == len(set(source_digests)),
        S2GI_BUNDLE_INVALID,
        "S2-GC selected sources are duplicated",
    )


def project_two_area_context(
    bundle: context.PerceptualContextBundle,
) -> TwoAreaContextBundle:
    """Project one validated S2-GC bundle without storage access or mutation."""

    _validate_s2gc_bundle(bundle)
    source_bundle_digest = bundle.bundle_digest
    b4_recent, tspm_fast, tspm_slow = bundle.role_findings

    area_a_payload = {
        "schema": S2GI_SCHEMA,
        "area": "A_RECENT",
        "recent_content_finding_digest": b4_recent.finding_digest,
        "fast_internal_finding_digest": tspm_fast.finding_digest,
        "short_sequence_finding_digest": bundle.sequence_finding.finding_digest,
    }
    area_a = AreaARecentFinding(
        "A_RECENT",
        b4_recent,
        tspm_fast,
        bundle.sequence_finding,
        _digest(area_a_payload),
    )

    area_b_payload = {
        "schema": S2GI_SCHEMA,
        "area": "B_STABLE",
        "stable_content_finding_digest": tspm_slow.finding_digest,
    }
    area_b = AreaBStableFinding(
        "B_STABLE",
        tspm_slow,
        _digest(area_b_payload),
    )

    candidates = tuple(
        finding.candidate
        for finding in bundle.role_findings
        if finding.candidate is not None
    )
    components = tuple(
        component for candidate in candidates for component in candidate.components
    )
    ledger_payload = {
        "schema": S2GI_SCHEMA,
        "validated_bundle_count": 1,
        "validated_role_count": 3,
        "candidate_reference_count": len(candidates),
        "component_reference_count": len(components),
        "value_reference_count": sum(len(component.values) for component in components),
        "sequence_reference_count": len(bundle.sequence_finding.references),
        "area_projection_count": 2,
        "digest_operation_count": 4,
        "source_ledger_digest": bundle.resource_ledger.ledger_digest,
    }
    ledger = TwoAreaContextResourceLedger(
        1,
        3,
        len(candidates),
        len(components),
        sum(len(component.values) for component in components),
        len(bundle.sequence_finding.references),
        2,
        4,
        bundle.resource_ledger.ledger_digest,
        _digest(ledger_payload),
    )

    output_payload = {
        "schema": S2GI_SCHEMA,
        "contract_digest": S2GH_CONTRACT_DIGEST,
        "source_bundle_digest": source_bundle_digest,
        "binding_digest": bundle.binding_digest,
        "config_digest": bundle.config_digest,
        "composite_state_digest": bundle.composite_state_digest,
        "probe_digest": bundle.probe_digest,
        "source_digest": bundle.source_digest,
        "area_finding_digests": [area_a.finding_digest, area_b.finding_digest],
        "resource_ledger_digest": ledger.ledger_digest,
        "prestate_digest": bundle.prestate_digest,
        "poststate_digest": bundle.poststate_digest,
        "automatic_selection": None,
    }
    output = TwoAreaContextBundle(
        S2GH_CONTRACT_DIGEST,
        source_bundle_digest,
        bundle.binding_digest,
        bundle.config_digest,
        bundle.composite_state_digest,
        bundle.probe_digest,
        bundle.source_digest,
        (area_a, area_b),
        ledger,
        bundle.prestate_digest,
        bundle.poststate_digest,
        None,
        _digest(output_payload),
    )
    _require(
        bundle.bundle_digest == source_bundle_digest
        and bundle.prestate_digest == bundle.poststate_digest,
        S2GI_READ_ONLY_VIOLATION,
        "S2-GC bundle changed during projection",
    )
    return output


__all__: tuple[str, ...] = ()
