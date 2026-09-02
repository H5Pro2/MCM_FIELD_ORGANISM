"""Profile-derived resource ledgers for the private S2-JW memory boundary."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re

from tools._s2jw_default_live_profile import S2JWDefaultLiveProfileV1


S2JW_LEDGER_SCHEMA = "s2jw.profiled-memory-ledger.v1"
PLAN_FORMATION_COUNT = 15
PLAN_PROBE_COUNT = 3
PLAN_TOP_LEVEL_OPERATIONS = 72
PLAN_FORMATION_L1_TERMS = 22_512
PLAN_PROBE_L1_TERMS = 21_168
PLAN_TOTAL_L1_TERMS = 43_680
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class S2JWLedgerError(ValueError):
    """A resource ledger is incomplete or not profile-derived."""


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


@dataclass(frozen=True, slots=True)
class S2JVLedgerLimitsV1:
    profile_binding_digest: str
    auditory_dimension: int
    visual_dimension: int
    av_dimension: int
    b4_capacity: int
    fast_capacity: int
    auditory_slow_capacity: int
    visual_slow_capacity: int
    formation_l1_term_limit: int
    read_only_l1_term_limit: int
    maximum_state_float_words: int
    maximum_state_float64_bytes: int
    plan_formation_count: int
    plan_probe_count: int
    plan_top_level_operations: int
    plan_formation_l1_terms: int
    plan_probe_l1_terms: int
    plan_total_l1_terms: int
    limits_digest: str
    schema: str = S2JW_LEDGER_SCHEMA

    def __post_init__(self) -> None:
        numbers = (
            self.auditory_dimension,
            self.visual_dimension,
            self.av_dimension,
            self.b4_capacity,
            self.fast_capacity,
            self.auditory_slow_capacity,
            self.visual_slow_capacity,
            self.formation_l1_term_limit,
            self.read_only_l1_term_limit,
            self.maximum_state_float_words,
            self.maximum_state_float64_bytes,
            self.plan_formation_count,
            self.plan_probe_count,
            self.plan_top_level_operations,
            self.plan_formation_l1_terms,
            self.plan_probe_l1_terms,
            self.plan_total_l1_terms,
        )
        if (
            self.schema != S2JW_LEDGER_SCHEMA
            or not _valid_digest(self.profile_binding_digest)
            or any(type(value) is not int or value <= 0 for value in numbers)
            or self.av_dimension != self.auditory_dimension + self.visual_dimension
            or self.maximum_state_float64_bytes != self.maximum_state_float_words * 8
            or self.plan_total_l1_terms
            != self.plan_formation_l1_terms + self.plan_probe_l1_terms
            or self.limits_digest != _digest(self.payload_without_digest())
        ):
            raise S2JWLedgerError("ledger limits are incomplete or inconsistent")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "profile_binding_digest": self.profile_binding_digest,
            "auditory_dimension": self.auditory_dimension,
            "visual_dimension": self.visual_dimension,
            "av_dimension": self.av_dimension,
            "b4_capacity": self.b4_capacity,
            "fast_capacity": self.fast_capacity,
            "auditory_slow_capacity": self.auditory_slow_capacity,
            "visual_slow_capacity": self.visual_slow_capacity,
            "formation_l1_term_limit": self.formation_l1_term_limit,
            "read_only_l1_term_limit": self.read_only_l1_term_limit,
            "maximum_state_float_words": self.maximum_state_float_words,
            "maximum_state_float64_bytes": self.maximum_state_float64_bytes,
            "plan_formation_count": self.plan_formation_count,
            "plan_probe_count": self.plan_probe_count,
            "plan_top_level_operations": self.plan_top_level_operations,
            "plan_formation_l1_terms": self.plan_formation_l1_terms,
            "plan_probe_l1_terms": self.plan_probe_l1_terms,
            "plan_total_l1_terms": self.plan_total_l1_terms,
        }


def build_s2jv_ledger_limits(
    profile: S2JWDefaultLiveProfileV1,
) -> S2JVLedgerLimitsV1:
    if type(profile) is not S2JWDefaultLiveProfileV1:
        raise S2JWLedgerError("exact default-live profile binding required")
    auditory = profile.auditory_dimension
    visual = profile.visual_dimension
    av = profile.av_dimension
    fast_capacity = profile.tspm_config.fast_config.capacity
    auditory_capacity = profile.profile.auditory_config.capacity
    visual_capacity = profile.profile.visual_config.capacity
    formation_limit = 2 * fast_capacity * av + auditory_capacity * auditory + visual_capacity * visual
    read_limit = (
        profile.b4_capacity * av
        + 3 * fast_capacity * av
        + 2 * (auditory_capacity * auditory + visual_capacity * visual)
    )
    state_words = (
        profile.b4_capacity * av
        + fast_capacity * av
        + auditory_capacity * auditory
        + visual_capacity * visual
    )
    payload = {
        "schema": S2JW_LEDGER_SCHEMA,
        "profile_binding_digest": profile.binding_digest,
        "auditory_dimension": auditory,
        "visual_dimension": visual,
        "av_dimension": av,
        "b4_capacity": profile.b4_capacity,
        "fast_capacity": fast_capacity,
        "auditory_slow_capacity": auditory_capacity,
        "visual_slow_capacity": visual_capacity,
        "formation_l1_term_limit": formation_limit,
        "read_only_l1_term_limit": read_limit,
        "maximum_state_float_words": state_words,
        "maximum_state_float64_bytes": state_words * 8,
        "plan_formation_count": PLAN_FORMATION_COUNT,
        "plan_probe_count": PLAN_PROBE_COUNT,
        "plan_top_level_operations": PLAN_TOP_LEVEL_OPERATIONS,
        "plan_formation_l1_terms": PLAN_FORMATION_L1_TERMS,
        "plan_probe_l1_terms": PLAN_PROBE_L1_TERMS,
        "plan_total_l1_terms": PLAN_TOTAL_L1_TERMS,
    }
    return S2JVLedgerLimitsV1(
        profile.binding_digest,
        auditory,
        visual,
        av,
        profile.b4_capacity,
        fast_capacity,
        auditory_capacity,
        visual_capacity,
        formation_limit,
        read_limit,
        state_words,
        state_words * 8,
        PLAN_FORMATION_COUNT,
        PLAN_PROBE_COUNT,
        PLAN_TOP_LEVEL_OPERATIONS,
        PLAN_FORMATION_L1_TERMS,
        PLAN_PROBE_L1_TERMS,
        PLAN_TOTAL_L1_TERMS,
        _digest(payload),
    )


@dataclass(frozen=True, slots=True)
class S2JVResourceLedgerV1:
    operation_id: str
    operation_role: str
    profile_binding_digest: str
    limits_digest: str
    common_projection_terms: int
    functional_write_words: int
    functional_l1_term_limit: int
    validation_terms: int
    digest_operations: int
    result_digest: str
    ledger_digest: str
    schema: str = S2JW_LEDGER_SCHEMA

    def __post_init__(self) -> None:
        numbers = (
            self.common_projection_terms,
            self.functional_write_words,
            self.functional_l1_term_limit,
            self.validation_terms,
            self.digest_operations,
        )
        if (
            self.schema != S2JW_LEDGER_SCHEMA
            or not isinstance(self.operation_id, str)
            or not self.operation_id
            or self.operation_role not in {"FORMATION", "READ_ONLY"}
            or not all(
                _valid_digest(value)
                for value in (
                    self.profile_binding_digest,
                    self.limits_digest,
                    self.result_digest,
                )
            )
            or any(type(value) is not int or value < 0 for value in numbers)
            or self.ledger_digest != _digest(self.payload_without_digest())
        ):
            raise S2JWLedgerError("resource ledger is incomplete or inconsistent")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "operation_id": self.operation_id,
            "operation_role": self.operation_role,
            "profile_binding_digest": self.profile_binding_digest,
            "limits_digest": self.limits_digest,
            "common_projection_terms": self.common_projection_terms,
            "functional_write_words": self.functional_write_words,
            "functional_l1_term_limit": self.functional_l1_term_limit,
            "validation_terms": self.validation_terms,
            "digest_operations": self.digest_operations,
            "result_digest": self.result_digest,
        }


def derive_s2jv_resource_ledger(
    *,
    profile: S2JWDefaultLiveProfileV1,
    limits: S2JVLedgerLimitsV1,
    operation_id: str,
    operation_role: str,
    result_digest: str,
) -> S2JVResourceLedgerV1:
    expected = build_s2jv_ledger_limits(profile)
    if limits != expected or not _valid_digest(result_digest):
        raise S2JWLedgerError("ledger source binding differs")
    if operation_role == "FORMATION":
        write_words = 2 * profile.av_dimension + profile.auditory_dimension + profile.visual_dimension
        l1_limit = limits.formation_l1_term_limit
        validation_terms = 2 * profile.av_dimension + 18
        digest_operations = 12
    elif operation_role == "READ_ONLY":
        write_words = 0
        l1_limit = limits.read_only_l1_term_limit
        validation_terms = profile.av_dimension + 16
        digest_operations = 10
    else:
        raise S2JWLedgerError("unknown resource operation role")
    payload = {
        "schema": S2JW_LEDGER_SCHEMA,
        "operation_id": operation_id,
        "operation_role": operation_role,
        "profile_binding_digest": profile.binding_digest,
        "limits_digest": limits.limits_digest,
        "common_projection_terms": profile.av_dimension,
        "functional_write_words": write_words,
        "functional_l1_term_limit": l1_limit,
        "validation_terms": validation_terms,
        "digest_operations": digest_operations,
        "result_digest": result_digest,
    }
    return S2JVResourceLedgerV1(
        operation_id,
        operation_role,
        profile.binding_digest,
        limits.limits_digest,
        profile.av_dimension,
        write_words,
        l1_limit,
        validation_terms,
        digest_operations,
        result_digest,
        _digest(payload),
    )


def validate_s2jv_resource_ledger(
    *,
    profile: S2JWDefaultLiveProfileV1,
    limits: S2JVLedgerLimitsV1,
    ledger: S2JVResourceLedgerV1,
    expected_role: str,
) -> S2JVResourceLedgerV1:
    expected = derive_s2jv_resource_ledger(
        profile=profile,
        limits=limits,
        operation_id=ledger.operation_id,
        operation_role=expected_role,
        result_digest=ledger.result_digest,
    )
    if ledger != expected:
        raise S2JWLedgerError("resource ledger differs from profile-derived limits")
    return ledger
