"""Pure private A/B context projection for S2-KJ."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from tools import _s2kj_validated_perceptual_finding_336 as binding


S2KJ_CONTEXT_SCHEMA = "s2kj.two-area-perceptual-context-336.v1"
S2KJ_CONTRACT_DIGEST = "2b350c0117b73c3367c8bad1f8f555e59e1170377beb539c41bb6e2df4b4de81"
S2KJ_CONTEXT_INVALID = "S2KJ_CONTEXT_INVALID"
S2KJ_CONTEXT_DIGEST_MISMATCH = "S2KJ_CONTEXT_DIGEST_MISMATCH"
S2KJ_CONTEXT_CAPACITY_EXCEEDED = "S2KJ_CONTEXT_CAPACITY_EXCEEDED"
MAX_OUTPUT_BYTES = 65_536
LOGICAL_OPERATIONS = 6
MAX_NEW_DIGESTS = 9


class S2KJContextError(ValueError):
    """The two-area projection cannot produce one complete valid bundle."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise S2KJContextError(code, message)


def _canonical_bytes(payload: object) -> bytes:
    return json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")


def _digest(payload: object) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


@dataclass(frozen=True, slots=True)
class ARecent336V1:
    area: str
    b4_recent: binding.RoleFinding336V1
    tspm_fast: binding.RoleFinding336V1
    area_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "area": self.area,
            "b4_recent_finding_digest": self.b4_recent.finding_digest,
            "tspm_fast_finding_digest": self.tspm_fast.finding_digest,
        }


@dataclass(frozen=True, slots=True)
class BStable336V1:
    area: str
    auditory: binding.RoleFinding336V1
    visual: binding.RoleFinding336V1
    stability_status: str
    area_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "area": self.area,
            "auditory_finding_digest": self.auditory.finding_digest,
            "visual_finding_digest": self.visual.finding_digest,
            "stability_status": self.stability_status,
        }


@dataclass(frozen=True, slots=True)
class Context336ResourceLedgerV1:
    input_finding_count: int
    role_finding_count: int
    candidate_count: int
    referenced_value_count: int
    logical_operation_count: int
    digest_operation_count: int
    serialized_output_bytes: int
    ledger_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "input_finding_count": self.input_finding_count,
            "role_finding_count": self.role_finding_count,
            "candidate_count": self.candidate_count,
            "referenced_value_count": self.referenced_value_count,
            "logical_operation_count": self.logical_operation_count,
            "digest_operation_count": self.digest_operation_count,
            "serialized_output_bytes": self.serialized_output_bytes,
        }


@dataclass(frozen=True, slots=True)
class TwoAreaPerceptualContext336:
    contract_digest: str
    input_finding_digest: str
    config_digest: str
    composite_state_digest: str
    probe_digest: str
    source_digest: str
    a_recent: ARecent336V1
    b_stable: BStable336V1
    b_stability_status: str
    context_presence: str
    resource_ledger: Context336ResourceLedgerV1
    prestate_digest: str
    poststate_digest: str
    automatic_selection: None
    bundle_digest: str
    schema: str = S2KJ_CONTEXT_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "contract_digest": self.contract_digest,
            "input_finding_digest": self.input_finding_digest,
            "config_digest": self.config_digest,
            "composite_state_digest": self.composite_state_digest,
            "probe_digest": self.probe_digest,
            "source_digest": self.source_digest,
            "a_recent_digest": self.a_recent.area_digest,
            "b_stable_digest": self.b_stable.area_digest,
            "b_stability_status": self.b_stability_status,
            "context_presence": self.context_presence,
            "resource_ledger_digest": self.resource_ledger.ledger_digest,
            "prestate_digest": self.prestate_digest,
            "poststate_digest": self.poststate_digest,
            "automatic_selection": self.automatic_selection,
        }

    def canonical_payload(self) -> dict[str, object]:
        def candidate_payload(candidate: binding.Candidate336 | None) -> object:
            if candidate is None:
                return None
            return {**candidate.payload_without_digest(), "candidate_digest": candidate.candidate_digest}

        def role_payload(finding: binding.RoleFinding336V1) -> dict[str, object]:
            return {
                **finding.payload_without_digest(),
                "candidate": candidate_payload(finding.candidate),
                "finding_digest": finding.finding_digest,
            }

        return {
            **self.payload_without_digest(),
            "a_recent": {
                "area": self.a_recent.area,
                "b4_recent": role_payload(self.a_recent.b4_recent),
                "tspm_fast": role_payload(self.a_recent.tspm_fast),
                "area_digest": self.a_recent.area_digest,
            },
            "b_stable": {
                "area": self.b_stable.area,
                "auditory": role_payload(self.b_stable.auditory),
                "visual": role_payload(self.b_stable.visual),
                "stability_status": self.b_stable.stability_status,
                "area_digest": self.b_stable.area_digest,
            },
            "resource_ledger": {
                **self.resource_ledger.payload_without_digest(),
                "ledger_digest": self.resource_ledger.ledger_digest,
            },
            "bundle_digest": self.bundle_digest,
        }


def _validate_area_a(value: ARecent336V1) -> None:
    _require(
        type(value) is ARecent336V1
        and value.area == "A_RECENT"
        and value.b4_recent.role == "B4_RECENT"
        and value.tspm_fast.role == "TSPM_FAST"
        and value.area_digest == _digest(value.payload_without_digest()),
        S2KJ_CONTEXT_INVALID,
        "A_RECENT relation differs",
    )


def _validate_area_b(value: BStable336V1) -> None:
    _require(
        type(value) is BStable336V1
        and value.area == "B_STABLE"
        and value.auditory.role == "B_STABLE_AUDITORY"
        and value.visual.role == "B_STABLE_VISUAL"
        and value.stability_status
        in {
            "AUDITORY_AND_VISUAL_STABLE",
            "AUDITORY_STABLE_ONLY",
            "VISUAL_STABLE_ONLY",
            "NO_STABLE_CONTEXT",
        }
        and value.area_digest == _digest(value.payload_without_digest()),
        S2KJ_CONTEXT_INVALID,
        "B_STABLE relation differs",
    )


def _validate_context(value: TwoAreaPerceptualContext336) -> TwoAreaPerceptualContext336:
    _require(type(value) is TwoAreaPerceptualContext336, S2KJ_CONTEXT_INVALID, "exact context required")
    _validate_area_a(value.a_recent)
    _validate_area_b(value.b_stable)
    _require(
        type(value.resource_ledger) is Context336ResourceLedgerV1
        and value.resource_ledger.ledger_digest
        == _digest(value.resource_ledger.payload_without_digest())
        and value.resource_ledger.input_finding_count == 1
        and value.resource_ledger.role_finding_count == 4
        and value.resource_ledger.candidate_count <= binding.MAX_CANDIDATES
        and value.resource_ledger.referenced_value_count <= binding.MAX_REFERENCED_VALUES
        and value.resource_ledger.logical_operation_count == LOGICAL_OPERATIONS
        and value.resource_ledger.digest_operation_count <= MAX_NEW_DIGESTS
        and value.resource_ledger.serialized_output_bytes <= MAX_OUTPUT_BYTES,
        S2KJ_CONTEXT_CAPACITY_EXCEEDED,
        "context ledger differs",
    )
    _require(
        value.schema == S2KJ_CONTEXT_SCHEMA
        and value.contract_digest == S2KJ_CONTRACT_DIGEST
        and value.prestate_digest == value.composite_state_digest == value.poststate_digest
        and value.b_stability_status == value.b_stable.stability_status
        and value.automatic_selection is None
        and value.bundle_digest == _digest(value.payload_without_digest()),
        S2KJ_CONTEXT_DIGEST_MISMATCH,
        "context binding differs",
    )
    actual_size = len(_canonical_bytes(value.canonical_payload()))
    _require(
        actual_size == value.resource_ledger.serialized_output_bytes,
        S2KJ_CONTEXT_CAPACITY_EXCEEDED,
        "serialized output size differs",
    )
    all_absent = all(
        item.status == "ABSENT_VALID"
        for item in (
            value.a_recent.b4_recent,
            value.a_recent.tspm_fast,
            value.b_stable.auditory,
            value.b_stable.visual,
        )
    )
    _require(
        value.context_presence == ("NO_CONTEXT" if all_absent else "CONTEXT_AVAILABLE"),
        S2KJ_CONTEXT_INVALID,
        "context presence differs",
    )
    return value


def project_two_area_perceptual_context_336(
    source: binding.ValidatedPerceptualFinding336V1,
) -> TwoAreaPerceptualContext336:
    """Project one validated finding without querying or changing memory."""

    try:
        source = binding._validate_validated_finding(source)
    except binding.S2KJBindingError as exc:
        raise S2KJContextError(S2KJ_CONTEXT_INVALID, "input finding is invalid") from exc
    before = source.binding_digest
    b4, fast, auditory, visual = source.role_findings
    a_payload = {
        "area": "A_RECENT",
        "b4_recent_finding_digest": b4.finding_digest,
        "tspm_fast_finding_digest": fast.finding_digest,
    }
    area_a = ARecent336V1("A_RECENT", b4, fast, _digest(a_payload))
    statuses = (auditory.status == "AVAILABLE", visual.status == "AVAILABLE")
    stability = {
        (True, True): "AUDITORY_AND_VISUAL_STABLE",
        (True, False): "AUDITORY_STABLE_ONLY",
        (False, True): "VISUAL_STABLE_ONLY",
        (False, False): "NO_STABLE_CONTEXT",
    }[statuses]
    b_payload = {
        "area": "B_STABLE",
        "auditory_finding_digest": auditory.finding_digest,
        "visual_finding_digest": visual.finding_digest,
        "stability_status": stability,
    }
    area_b = BStable336V1("B_STABLE", auditory, visual, stability, _digest(b_payload))
    all_absent = all(item.status == "ABSENT_VALID" for item in source.role_findings)
    context_presence = "NO_CONTEXT" if all_absent else "CONTEXT_AVAILABLE"

    # Size is part of the final ledger and the ledger is part of the bundle. Iterate
    # to the stable decimal width; the sequence is bounded and deterministic.
    size = 0
    for _ in range(4):
        ledger_payload = {
            "input_finding_count": 1,
            "role_finding_count": 4,
            "candidate_count": source.candidate_count,
            "referenced_value_count": source.referenced_value_count,
            "logical_operation_count": LOGICAL_OPERATIONS,
            "digest_operation_count": 4,
            "serialized_output_bytes": size,
        }
        ledger = Context336ResourceLedgerV1(
            1,
            4,
            source.candidate_count,
            source.referenced_value_count,
            LOGICAL_OPERATIONS,
            4,
            size,
            _digest(ledger_payload),
        )
        payload = {
            "schema": S2KJ_CONTEXT_SCHEMA,
            "contract_digest": S2KJ_CONTRACT_DIGEST,
            "input_finding_digest": source.binding_digest,
            "config_digest": source.config_digest,
            "composite_state_digest": source.composite_state_digest,
            "probe_digest": source.probe_digest,
            "source_digest": source.source_digest,
            "a_recent_digest": area_a.area_digest,
            "b_stable_digest": area_b.area_digest,
            "b_stability_status": stability,
            "context_presence": context_presence,
            "resource_ledger_digest": ledger.ledger_digest,
            "prestate_digest": source.prestate_digest,
            "poststate_digest": source.poststate_digest,
            "automatic_selection": None,
        }
        result = TwoAreaPerceptualContext336(
            S2KJ_CONTRACT_DIGEST,
            source.binding_digest,
            source.config_digest,
            source.composite_state_digest,
            source.probe_digest,
            source.source_digest,
            area_a,
            area_b,
            stability,
            context_presence,
            ledger,
            source.prestate_digest,
            source.poststate_digest,
            None,
            _digest(payload),
        )
        next_size = len(_canonical_bytes(result.canonical_payload()))
        if next_size == size:
            break
        size = next_size
    _require(size <= MAX_OUTPUT_BYTES, S2KJ_CONTEXT_CAPACITY_EXCEEDED, "context output is too large")
    _require(before == source.binding_digest, S2KJ_CONTEXT_INVALID, "projection changed input")
    return _validate_context(result)


__all__ = ()
