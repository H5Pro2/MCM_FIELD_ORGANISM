"""Fail-closed structural validator for the S1-TK candidate envelope."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, fields
import hashlib
import json
import math
import re
from typing import Any


CONTRACT_ID = "mcm.s1tm.candidate-observation-envelope-implementation.v1"
CONTRACT_DIGEST = "ffc178618cf873f617d4d8238d6310a0994ef77572d51b8050e8f20ad5987ee4"
SCHEMA_ID = "mcm.s1tk.candidate-observation-envelope.v1"
VALIDATION_SCHEMA_ID = "mcm.s1tm.candidate-observation-envelope-validation.v1"
SOURCE_CONTRACT_ID = "S1-TK"
CANONICALIZATION_ID = "compact-json-ascii-sort-keys-no-nan-sha256-v1"
VALID_STATUS = "CANDIDATE_ENVELOPE_STRUCTURALLY_VALID"
INVALID_STATUS = "AUDIT_INVALID_NOT_COMPUTABLE"

ATLAS_FILE_SHA256 = "b8df5c0cb010169432b93b1af42b3e5720edc8299060a994298e996bfcbefe3a"
ATLAS_ARTIFACT_DIGEST = "b63c12967fbab69740341af2f011839652762efcd71c8b29c851511ce0c20a9f"
ATLAS_RESULT_DIGEST = "dd38f95829e04934ffd678956d52e380729042fe5d7710e99d672a92885b3a56"
EXPOSURE_FIXTURE_DIGEST = "ca66f3a673eaca663a0973f7e956a90f4788e6f51963b71de4952801936bac3e"
AXIS_DIGEST = "124ee8e19a9e3ce35816ff65370f6775131b0be413c7a2816b01605cf3d03cfd"

PLAN_ROLES = (
    "F_A", "F_C", "F_G", "T_EARLY", "T_LATER", "I_LOCAL",
    "I_REMOTE", "I_GAP", "C_LOCAL", "C_REMOTE", "C_GAP", "R_EARLY",
    "R_LATE", "U_RELEASED", "U_EARLY", "U_FRESH_B_EARLY",
    "U_FRESH_B_LATE",
)
NODE_ORDER = ("node-a", "node-b", "node-c", "node-d")
ROOT_FAMILIES = (
    "envelope_identity", "candidate_field_profile",
    "candidate_internal_evidence", "candidate_controls", "lifecycle_links",
    "completion",
)
FAILURE_CODES = (
    "ENVELOPE_CANONICAL_FORM_INVALID", "ENVELOPE_ROOT_SCHEMA_INVALID",
    "ENVELOPE_IDENTITY_INVALID", "CANDIDATE_CONFIGURATION_IDENTITY_INVALID",
    "ATLAS_REFERENCE_INVALID", "EXPOSURE_REFERENCE_INVALID",
    "PLAN_AXIS_INVALID", "CHECKPOINT_AXIS_INVALID", "FIELD_VECTOR_INVALID",
    "RECEPTOR_NULLABILITY_INVALID", "FIELD_PROFILE_DIGEST_INVALID",
    "STATE_CHECKPOINT_COUNT_INVALID", "STATE_CARRY_CHAIN_INVALID",
    "TRANSITION_COUNT_INVALID", "TRANSITION_CAUSAL_SOURCE_INVALID",
    "BALANCE_SCHEMA_INVALID", "BALANCE_CHECKPOINT_COUNT_INVALID",
    "BALANCE_TRANSITION_COUNT_INVALID", "BALANCE_RECORD_INVALID",
    "ABLATION_COUNT_INVALID", "ABLATION_PRECONDITION_MISMATCH",
    "ABLATION_SCOPE_INVALID", "NULL_PATH_CARDINALITY_INVALID",
    "NULL_PATH_REFERENCE_INVALID", "NULL_PATH_MISMATCH",
    "NULL_PATH_CANDIDATE_STATE_LEAK", "RELEASE_LINK_INVALID",
    "REUSE_LINK_WITHOUT_RELEASE", "REUSE_LINK_INVALID",
    "INFORMATION_BARRIER_VIOLATION", "ENVELOPE_COMPLETION_INVALID",
    "PARTIAL_RESULT_FORBIDDEN",
)
_SHA = re.compile(r"^[0-9a-f]{64}$")
_CHECKPOINT_AXIS = tuple(
    (position, plan_role, checkpoint_role)
    for position, plan_role in enumerate(PLAN_ROLES, 1)
    for checkpoint_role in (
        ("PRE_COMPETITION", "POST_COMPETITION", "ALIGNED_PRE_PROBE", "POST_PROBE_READOUT")
        if plan_role.startswith("C_") else
        ("ALIGNED_PRE_PROBE", "POST_PROBE_READOUT")
    )
)
_READOUT_AXIS = tuple(item for item in _CHECKPOINT_AXIS if item[2] == "POST_PROBE_READOUT")
_FORBIDDEN_INFORMATION_TOKENS = (
    "arm_target", "baseline_payload", "baseline_result", "baseline_value",
    "comparator_result", "future_state", "outcome", "result_selection",
)


@dataclass(frozen=True, slots=True)
class CandidateEnvelopeValidationRegistry:
    contract_id: str
    contract_digest: str
    schema_id: str
    validation_schema_id: str
    source_contract_id: str
    canonicalization_id: str
    plan_roles: tuple[str, ...]
    checkpoint_axis: tuple[tuple[int, str, str], ...]
    interval_ordinals: tuple[int, ...]
    readout_axis: tuple[tuple[int, str, str], ...]
    node_order: tuple[str, ...]
    root_families: tuple[str, ...]
    failure_codes: tuple[str, ...]
    forbidden_information_tokens: tuple[str, ...]
    allowed_causal_sources: tuple[str, ...]
    atlas_file_sha256: str
    atlas_artifact_digest: str
    atlas_result_digest: str
    exposure_fixture_digest: str
    axis_digest: str
    registry_digest: str


@dataclass(frozen=True, slots=True)
class CandidateEnvelopeIdentity:
    schema_id: str
    contract_id: str
    contract_digest: str
    candidate_role_id: str
    candidate_configuration_id: str
    exposure_plan_id: str
    exposure_fixture_digest: str
    manifest_digest: str
    registration_digest: str
    geometry_id: str
    node_order_id: str
    source_inventory_digest: str
    atlas_file_sha256: str
    atlas_artifact_digest: str
    atlas_result_digest: str
    axis_digest: str
    canonicalization_id: str
    runtime_id: str
    identity_digest: str


@dataclass(frozen=True, slots=True)
class CandidatePlanRecord:
    plan_position: int
    plan_role: str
    exposure_plan_id: str
    fresh_state_id: str
    candidate_configuration_id: str
    checkpoint_digests: tuple[str, ...]
    first_carry_digest: str
    last_carry_digest: str
    terminal_event_chain_digest: str
    completion_status: str
    plan_digest: str


@dataclass(frozen=True, slots=True)
class CandidateFieldCheckpointRecord:
    checkpoint_ordinal: int
    plan_position: int
    plan_role: str
    checkpoint_role: str
    checkpoint_tick: int
    fixture_event_digest: str
    event_chain_digest: str
    field_state_digest: str
    carry_digest: str
    private_state_digest: str
    candidate_configuration_id: str
    dependency_digest: str
    distribution_digest_or_none: str | None
    alignment_digest_or_none: str | None
    receptor_contact: tuple[float | None, ...]
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    field_tick: int
    layer_tick: int
    checkpoint_digest: str


@dataclass(frozen=True, slots=True)
class CandidateFieldProfile:
    checkpoint_digests: tuple[str, ...]
    signed_components: tuple[float, ...]
    profile_digest: str


@dataclass(frozen=True, slots=True)
class CandidateStateCheckpointRecord:
    checkpoint_ordinal: int
    field_checkpoint_digest: str
    private_state_digest: str
    candidate_configuration_id: str
    carry_digest: str
    event_chain_digest: str
    balance_schema_id: str
    balance_checkpoint_digest: str
    state_checkpoint_digest: str


@dataclass(frozen=True, slots=True)
class CandidateTransitionRecord:
    interval_ordinal: int
    plan_position: int
    plan_role: str
    event_source_digest: str
    before_state_digest: str
    after_state_digest: str
    before_carry_digest: str
    after_carry_digest: str
    before_balance_digest: str
    after_balance_digest: str
    field_progress_digest: str
    causal_source: str
    receipt_or_diagnostic_digest: str
    transition_digest: str


@dataclass(frozen=True, slots=True)
class CandidateBalanceCheckpointRecord:
    checkpoint_ordinal: int
    balance_schema_id: str
    role_axis: tuple[str, ...]
    local_coordinates: tuple[tuple[float, ...], ...]
    local_totals: tuple[float, ...]
    local_dissipation: tuple[float, ...]
    global_total: float
    inflow: tuple[float, ...]
    outflow: tuple[float, ...]
    transfers: tuple[float, ...]
    residual: float
    private_state_digest: str
    field_checkpoint_digest: str
    balance_checkpoint_digest: str


@dataclass(frozen=True, slots=True)
class CandidateTransitionBalanceRecord:
    interval_ordinal: int
    before_balance_digest: str
    after_balance_digest: str
    transfers: tuple[float, ...]
    inflows: tuple[float, ...]
    outflows: tuple[float, ...]
    dissipation: tuple[float, ...]
    residual: float
    causal_source: str
    transition_balance_digest: str


@dataclass(frozen=True, slots=True)
class ReadoutAblationRecord:
    plan_position: int
    plan_role: str
    exposure_plan_id: str
    fresh_state_id: str
    candidate_configuration_id: str
    history_prefix_digest: str
    event_chain_digest: str
    receptor_contact: tuple[float, ...]
    aligned_activation_before: tuple[float, ...]
    aligned_afterimage_before: tuple[float, ...]
    private_state_before_digest: str
    geometry_id: str
    readout_tick: int
    probe_digest: str
    original_readout: tuple[float, ...]
    ablated_readout: tuple[float, ...]
    disabled_scope: str
    exclusive_disable_proof: bool
    excluded_from_main_profile: bool
    ablation_digest: str


@dataclass(frozen=True, slots=True)
class DisabledFullPathProfile:
    path_role: str
    candidate_updates_enabled: bool
    plan_records: tuple[CandidatePlanRecord, ...]
    checkpoint_records: tuple[CandidateFieldCheckpointRecord, ...]
    candidate_state_digests: tuple[str, ...]
    candidate_carry_digests: tuple[str, ...]
    terminal_event_chain_digest: str
    path_digest: str


@dataclass(frozen=True, slots=True)
class NullPathPairRecord:
    checkpoint_ordinal: int
    disabled_checkpoint_digest: str
    reference_checkpoint_digest: str
    bit_equal: bool
    pair_digest: str


@dataclass(frozen=True, slots=True)
class ReleaseLifecycleLink:
    early_plan_digest: str
    late_plan_digest: str
    early_checkpoint_digests: tuple[str, ...]
    late_checkpoint_digests: tuple[str, ...]
    state_checkpoint_digests: tuple[str, ...]
    balance_checkpoint_digests: tuple[str, ...]
    shared_provenance_digest: str
    functional_loss_proof_digest: str
    reusable_local_capacity: tuple[float, ...]
    reset_exclusion: bool
    clipping_exclusion: bool
    restart_exclusion: bool
    recovery_toggle_exclusion: bool
    release_link_digest: str


@dataclass(frozen=True, slots=True)
class ReuseLifecycleLink:
    released_plan_digest: str
    early_plan_digest: str
    fresh_early_plan_digest: str
    fresh_late_plan_digest: str
    release_link_digest: str
    pre_history_balance_digests: tuple[str, ...]
    local_reuse_demand: tuple[float, ...]
    readout_checkpoint_digests: tuple[str, ...]
    role_identity_digest: str
    reuse_link_digest: str


@dataclass(frozen=True, slots=True)
class EnvelopeCompletionRecord:
    ordered_family_digests: tuple[str, ...]
    plan_count: int
    field_checkpoint_count: int
    candidate_interval_count: int
    post_probe_readout_count: int
    null_path_pair_count: int
    information_barriers_status: str
    envelope_digest: str
    completion_status: str
    partial_result: bool
    completion_digest: str


@dataclass(frozen=True, slots=True)
class CandidateObservationEnvelope:
    identity: CandidateEnvelopeIdentity
    plans: tuple[CandidatePlanRecord, ...]
    field_checkpoints: tuple[CandidateFieldCheckpointRecord, ...]
    field_profile: CandidateFieldProfile
    state_checkpoints: tuple[CandidateStateCheckpointRecord, ...]
    transitions: tuple[CandidateTransitionRecord, ...]
    balance_schema_id: str
    balance_role_axis: tuple[str, ...]
    balance_checkpoints: tuple[CandidateBalanceCheckpointRecord, ...]
    transition_balances: tuple[CandidateTransitionBalanceRecord, ...]
    readout_ablations: tuple[ReadoutAblationRecord, ...]
    disabled_candidate_path: DisabledFullPathProfile
    independent_reference_path: DisabledFullPathProfile
    null_path_pairs: tuple[NullPathPairRecord, ...]
    release_link: ReleaseLifecycleLink
    reuse_link: ReuseLifecycleLink
    completion: EnvelopeCompletionRecord


@dataclass(frozen=True, slots=True)
class CandidateEnvelopeValidationResult:
    status: str
    envelope_or_none: CandidateObservationEnvelope | None
    failure_code_or_none: str | None
    input_bytes_digest: str
    registry_digest: str
    result_digest: str


__all__ = (
    "ATLAS_ARTIFACT_DIGEST", "ATLAS_FILE_SHA256", "ATLAS_RESULT_DIGEST",
    "AXIS_DIGEST", "CANONICALIZATION_ID", "CONTRACT_DIGEST", "CONTRACT_ID",
    "EXPOSURE_FIXTURE_DIGEST", "FAILURE_CODES", "INVALID_STATUS", "NODE_ORDER",
    "PLAN_ROLES", "ROOT_FAMILIES", "SCHEMA_ID", "SOURCE_CONTRACT_ID",
    "VALIDATION_SCHEMA_ID", "VALID_STATUS", "CandidateEnvelopeValidationRegistry",
    "CandidateEnvelopeIdentity", "CandidatePlanRecord",
    "CandidateFieldCheckpointRecord", "CandidateFieldProfile",
    "CandidateStateCheckpointRecord", "CandidateTransitionRecord",
    "CandidateBalanceCheckpointRecord", "CandidateTransitionBalanceRecord",
    "ReadoutAblationRecord", "DisabledFullPathProfile", "NullPathPairRecord",
    "ReleaseLifecycleLink", "ReuseLifecycleLink", "EnvelopeCompletionRecord",
    "CandidateObservationEnvelope", "CandidateEnvelopeValidationResult",
    "build_candidate_envelope_validation_registry",
    "validate_candidate_observation_envelope",
)


class _ValidationError(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def _canonical(value: object) -> object:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value) or (value == 0.0 and math.copysign(1.0, value) < 0):
            raise ValueError("noncanonical number")
        return value
    if isinstance(value, (tuple, list)):
        return [_canonical(item) for item in value]
    if isinstance(value, Mapping):
        if not all(isinstance(key, str) for key in value):
            raise ValueError("non-string key")
        return {key: _canonical(value[key]) for key in sorted(value)}
    if hasattr(value, "__dataclass_fields__"):
        return {field.name: _canonical(getattr(value, field.name)) for field in fields(value)}
    raise ValueError("noncanonical value")


def _bytes(value: object) -> bytes:
    return json.dumps(_canonical(value), ensure_ascii=True, allow_nan=False,
                      sort_keys=True, separators=(",", ":")).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_bytes(value)).hexdigest()


def _without(value: Mapping[str, object], *names: str) -> dict[str, object]:
    return {key: item for key, item in value.items() if key not in names}


def _registry_payload(registry: CandidateEnvelopeValidationRegistry) -> dict[str, object]:
    return {field.name: getattr(registry, field.name) for field in fields(registry)
            if field.name != "registry_digest"}


def build_candidate_envelope_validation_registry() -> CandidateEnvelopeValidationRegistry:
    base = CandidateEnvelopeValidationRegistry(
        CONTRACT_ID, CONTRACT_DIGEST, SCHEMA_ID, VALIDATION_SCHEMA_ID,
        SOURCE_CONTRACT_ID, CANONICALIZATION_ID, PLAN_ROLES, _CHECKPOINT_AXIS,
        tuple(range(1, 128)), _READOUT_AXIS, NODE_ORDER, ROOT_FAMILIES,
        FAILURE_CODES, _FORBIDDEN_INFORMATION_TOKENS, ("FIELD_HISTORY",),
        ATLAS_FILE_SHA256, ATLAS_ARTIFACT_DIGEST, ATLAS_RESULT_DIGEST,
        EXPOSURE_FIXTURE_DIGEST, AXIS_DIGEST, "",
    )
    return CandidateEnvelopeValidationRegistry(
        *tuple(getattr(base, field.name) for field in fields(base) if field.name != "registry_digest"),
        _digest(_registry_payload(base)),
    )


def _pairs(pairs: Sequence[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def _parse(raw_bytes: bytes) -> dict[str, object]:
    try:
        value = json.loads(raw_bytes.decode("utf-8"), object_pairs_hook=_pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(ValueError("constant")))
        if not isinstance(value, dict) or _bytes(value) != raw_bytes:
            raise ValueError("not canonical")
        return value
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError, TypeError, OverflowError) as exc:
        raise _ValidationError(FAILURE_CODES[0]) from exc


def _exact(value: object, names: Sequence[str], code: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != set(names):
        raise _ValidationError(code)
    return value


def _list(value: object, code: str) -> list[object]:
    if not isinstance(value, list):
        raise _ValidationError(code)
    return value


def _text(value: object, code: str) -> str:
    if not isinstance(value, str) or not value:
        raise _ValidationError(code)
    return value


def _sha(value: object, code: str) -> str:
    text = _text(value, code)
    if not _SHA.fullmatch(text):
        raise _ValidationError(code)
    return text


def _integer(value: object, code: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise _ValidationError(code)
    return value


def _number(value: object, code: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise _ValidationError(code)
    return float(value)


def _numbers(value: object, length: int, code: str) -> tuple[float, ...]:
    items = _list(value, code)
    if len(items) != length:
        raise _ValidationError(code)
    return tuple(_number(item, code) for item in items)


def _shas(value: object, length: int, code: str) -> tuple[str, ...]:
    items = _list(value, code)
    if len(items) != length:
        raise _ValidationError(code)
    return tuple(_sha(item, code) for item in items)


def _strings(value: object, code: str) -> tuple[str, ...]:
    return tuple(_text(item, code) for item in _list(value, code))


def _record(value: object, cls: type[Any], digest_name: str, code: str) -> tuple[dict[str, object], Any]:
    names = tuple(field.name for field in fields(cls))
    payload = _exact(value, names, code)
    if _sha(payload[digest_name], code) != _digest(_without(payload, digest_name)):
        raise _ValidationError(code)
    return payload, None


def _identity(value: object, registry: CandidateEnvelopeValidationRegistry) -> CandidateEnvelopeIdentity:
    p, _ = _record(value, CandidateEnvelopeIdentity, "identity_digest", "ENVELOPE_IDENTITY_INVALID")
    code = "ENVELOPE_IDENTITY_INVALID"
    if (p["schema_id"], p["contract_id"], p["contract_digest"], p["canonicalization_id"]) != (
        registry.schema_id, registry.contract_id, registry.contract_digest, registry.canonicalization_id
    ):
        raise _ValidationError(code)
    for name in ("candidate_role_id", "exposure_plan_id", "geometry_id", "node_order_id", "runtime_id"):
        _text(p[name], code)
    _sha(p["manifest_digest"], code); _sha(p["registration_digest"], code); _sha(p["source_inventory_digest"], code)
    if not _SHA.fullmatch(str(p["candidate_configuration_id"])):
        raise _ValidationError("CANDIDATE_CONFIGURATION_IDENTITY_INVALID")
    if (p["atlas_file_sha256"], p["atlas_artifact_digest"], p["atlas_result_digest"]) != (
        registry.atlas_file_sha256, registry.atlas_artifact_digest, registry.atlas_result_digest
    ):
        raise _ValidationError("ATLAS_REFERENCE_INVALID")
    if (p["exposure_fixture_digest"], p["axis_digest"]) != (registry.exposure_fixture_digest, registry.axis_digest):
        raise _ValidationError("EXPOSURE_REFERENCE_INVALID")
    return CandidateEnvelopeIdentity(**p)


def _plan(value: object, identity: CandidateEnvelopeIdentity, expected: tuple[int, str],
          checkpoints: tuple[CandidateFieldCheckpointRecord, ...]) -> CandidatePlanRecord:
    code = "PLAN_AXIS_INVALID"
    p, _ = _record(value, CandidatePlanRecord, "plan_digest", code)
    position, role = expected
    selected = tuple(item for item in checkpoints if item.plan_position == position)
    if (p["plan_position"], p["plan_role"]) != expected or p["exposure_plan_id"] != identity.exposure_plan_id:
        raise _ValidationError(code)
    if p["candidate_configuration_id"] != identity.candidate_configuration_id:
        raise _ValidationError("CANDIDATE_CONFIGURATION_IDENTITY_INVALID")
    if tuple(p["checkpoint_digests"]) != tuple(item.checkpoint_digest for item in selected):
        raise _ValidationError(code)
    if (p["first_carry_digest"], p["last_carry_digest"]) != (selected[0].carry_digest, selected[-1].carry_digest):
        raise _ValidationError(code)
    _text(p["fresh_state_id"], code); _sha(p["terminal_event_chain_digest"], code)
    if p["completion_status"] != "PLAN_STRUCTURALLY_COMPLETE":
        raise _ValidationError(code)
    return CandidatePlanRecord(**{**p, "checkpoint_digests": tuple(p["checkpoint_digests"])})


def _field_checkpoint(value: object, identity: CandidateEnvelopeIdentity,
                      expected_ordinal: int, expected: tuple[int, str, str]) -> CandidateFieldCheckpointRecord:
    code = "CHECKPOINT_AXIS_INVALID"
    p, _ = _record(value, CandidateFieldCheckpointRecord, "checkpoint_digest", "FIELD_PROFILE_DIGEST_INVALID")
    if (p["checkpoint_ordinal"], p["plan_position"], p["plan_role"], p["checkpoint_role"]) != (
        expected_ordinal, *expected
    ):
        raise _ValidationError(code)
    _integer(p["checkpoint_tick"], code); _integer(p["field_tick"], code); _integer(p["layer_tick"], code)
    if p["candidate_configuration_id"] != identity.candidate_configuration_id:
        raise _ValidationError("CANDIDATE_CONFIGURATION_IDENTITY_INVALID")
    for name in ("fixture_event_digest", "event_chain_digest", "field_state_digest", "carry_digest",
                 "private_state_digest", "dependency_digest"):
        _sha(p[name], code)
    for name in ("distribution_digest_or_none", "alignment_digest_or_none"):
        if p[name] is not None:
            _sha(p[name], code)
    activation = _numbers(p["activation"], 4, "FIELD_VECTOR_INVALID")
    afterimage = _numbers(p["afterimage"], 4, "FIELD_VECTOR_INVALID")
    receptor = _list(p["receptor_contact"], "RECEPTOR_NULLABILITY_INVALID")
    nullable = expected[1:] == ("C_GAP", "POST_COMPETITION")
    if len(receptor) != 4 or (nullable and not all(item is None for item in receptor)) or (
        not nullable and (any(item is None for item in receptor) or any(
            isinstance(item, bool) or not isinstance(item, (int, float)) or not math.isfinite(item) for item in receptor
        ))
    ):
        raise _ValidationError("RECEPTOR_NULLABILITY_INVALID")
    contact = tuple(None if item is None else float(item) for item in receptor)
    return CandidateFieldCheckpointRecord(**{
        **p, "receptor_contact": contact, "activation": activation, "afterimage": afterimage,
    })


def _field_profile(value: object, checkpoints: tuple[CandidateFieldCheckpointRecord, ...]) -> CandidateFieldProfile:
    code = "FIELD_PROFILE_DIGEST_INVALID"
    p, _ = _record(value, CandidateFieldProfile, "profile_digest", code)
    digests = tuple(item.checkpoint_digest for item in checkpoints)
    components = tuple(component for item in checkpoints for vector in (item.activation, item.afterimage) for component in vector)
    if tuple(p["checkpoint_digests"]) != digests or tuple(p["signed_components"]) != components or len(components) != 320:
        raise _ValidationError(code)
    return CandidateFieldProfile(digests, components, p["profile_digest"])


def _balance_checkpoint(value: object, expected_ordinal: int, schema_id: str,
                        role_axis: tuple[str, ...], field_cp: CandidateFieldCheckpointRecord) -> CandidateBalanceCheckpointRecord:
    code = "BALANCE_RECORD_INVALID"
    p, _ = _record(value, CandidateBalanceCheckpointRecord, "balance_checkpoint_digest", code)
    if p["checkpoint_ordinal"] != expected_ordinal or p["balance_schema_id"] != schema_id or tuple(p["role_axis"]) != role_axis:
        raise _ValidationError(code)
    if p["private_state_digest"] != field_cp.private_state_digest or p["field_checkpoint_digest"] != field_cp.checkpoint_digest:
        raise _ValidationError(code)
    coordinates = _list(p["local_coordinates"], code)
    if len(coordinates) != 4:
        raise _ValidationError(code)
    local_coordinates = tuple(_numbers(item, len(role_axis), code) for item in coordinates)
    converted = {
        "local_totals": _numbers(p["local_totals"], 4, code),
        "local_dissipation": _numbers(p["local_dissipation"], 4, code),
        "inflow": _numbers(p["inflow"], len(role_axis), code),
        "outflow": _numbers(p["outflow"], len(role_axis), code),
        "transfers": _numbers(p["transfers"], len(role_axis), code),
        "global_total": _number(p["global_total"], code), "residual": _number(p["residual"], code),
    }
    return CandidateBalanceCheckpointRecord(**{**p, **converted, "role_axis": role_axis,
                                                "local_coordinates": local_coordinates})


def _state_checkpoint(value: object, expected_ordinal: int, identity: CandidateEnvelopeIdentity,
                      field_cp: CandidateFieldCheckpointRecord,
                      balance: CandidateBalanceCheckpointRecord) -> CandidateStateCheckpointRecord:
    code = "STATE_CARRY_CHAIN_INVALID"
    p, _ = _record(value, CandidateStateCheckpointRecord, "state_checkpoint_digest", code)
    if (p["checkpoint_ordinal"] != expected_ordinal or p["field_checkpoint_digest"] != field_cp.checkpoint_digest
            or p["private_state_digest"] != field_cp.private_state_digest
            or p["candidate_configuration_id"] != identity.candidate_configuration_id
            or p["carry_digest"] != field_cp.carry_digest or p["event_chain_digest"] != field_cp.event_chain_digest
            or p["balance_schema_id"] != balance.balance_schema_id
            or p["balance_checkpoint_digest"] != balance.balance_checkpoint_digest):
        raise _ValidationError(code)
    return CandidateStateCheckpointRecord(**p)


def _transition_balance(value: object, expected: int, balances: tuple[CandidateBalanceCheckpointRecord, ...],
                        causal_source: str) -> CandidateTransitionBalanceRecord:
    code = "BALANCE_RECORD_INVALID"
    p, _ = _record(value, CandidateTransitionBalanceRecord, "transition_balance_digest", code)
    before = balances[(expected - 1) % len(balances)]
    after = balances[expected % len(balances)]
    if (p["interval_ordinal"], p["before_balance_digest"], p["after_balance_digest"], p["causal_source"]) != (
        expected, before.balance_checkpoint_digest, after.balance_checkpoint_digest, causal_source
    ):
        raise _ValidationError(code)
    converted = {name: _numbers(p[name], len(before.role_axis), code)
                 for name in ("transfers", "inflows", "outflows", "dissipation")}
    return CandidateTransitionBalanceRecord(**{**p, **converted, "residual": _number(p["residual"], code)})


def _transition(value: object, expected: int, registry: CandidateEnvelopeValidationRegistry,
                plans: tuple[CandidatePlanRecord, ...], states: tuple[CandidateStateCheckpointRecord, ...],
                balances: tuple[CandidateBalanceCheckpointRecord, ...]) -> CandidateTransitionRecord:
    p, _ = _record(value, CandidateTransitionRecord, "transition_digest", "STATE_CARRY_CHAIN_INVALID")
    if p["interval_ordinal"] != expected:
        raise _ValidationError("TRANSITION_COUNT_INVALID")
    plan_position = ((expected - 1) * len(plans)) // 127 + 1
    plan = plans[plan_position - 1]
    before = states[(expected - 1) % len(states)]
    after = states[expected % len(states)]
    before_balance = balances[(expected - 1) % len(balances)]
    after_balance = balances[expected % len(balances)]
    if (p["plan_position"], p["plan_role"]) != (plan_position, plan.plan_role):
        raise _ValidationError("STATE_CARRY_CHAIN_INVALID")
    if (p["before_state_digest"], p["after_state_digest"], p["before_carry_digest"], p["after_carry_digest"],
        p["before_balance_digest"], p["after_balance_digest"]) != (
        before.state_checkpoint_digest, after.state_checkpoint_digest, before.carry_digest, after.carry_digest,
        before_balance.balance_checkpoint_digest, after_balance.balance_checkpoint_digest,
    ):
        raise _ValidationError("STATE_CARRY_CHAIN_INVALID")
    if p["causal_source"] not in registry.allowed_causal_sources:
        raise _ValidationError("TRANSITION_CAUSAL_SOURCE_INVALID")
    for name in ("event_source_digest", "field_progress_digest", "receipt_or_diagnostic_digest"):
        _sha(p[name], "STATE_CARRY_CHAIN_INVALID")
    return CandidateTransitionRecord(**p)


def _ablation(value: object, expected: tuple[int, str, str], identity: CandidateEnvelopeIdentity,
              checkpoint: CandidateFieldCheckpointRecord) -> ReadoutAblationRecord:
    code = "ABLATION_PRECONDITION_MISMATCH"
    p, _ = _record(value, ReadoutAblationRecord, "ablation_digest", code)
    if (p["plan_position"], p["plan_role"]) != expected[:2] or p["exposure_plan_id"] != identity.exposure_plan_id:
        raise _ValidationError(code)
    if p["candidate_configuration_id"] != identity.candidate_configuration_id or p["geometry_id"] != identity.geometry_id:
        raise _ValidationError(code)
    if tuple(p["receptor_contact"]) != checkpoint.receptor_contact or p["private_state_before_digest"] != checkpoint.private_state_digest:
        raise _ValidationError(code)
    for name in ("fresh_state_id", "history_prefix_digest", "event_chain_digest", "probe_digest"):
        _text(p[name], code) if name == "fresh_state_id" else _sha(p[name], code)
    converted = {name: _numbers(p[name], 4 if "before" in name or name == "receptor_contact" else 8, code)
                 for name in ("receptor_contact", "aligned_activation_before", "aligned_afterimage_before",
                              "original_readout", "ablated_readout")}
    if not isinstance(p["readout_tick"], int):
        raise _ValidationError(code)
    if (p["disabled_scope"] != "CANDIDATE_READOUT_FEEDBACK_ONLY" or p["exclusive_disable_proof"] is not True
            or p["excluded_from_main_profile"] is not True):
        raise _ValidationError("ABLATION_SCOPE_INVALID")
    return ReadoutAblationRecord(**{**p, **converted})


def _path_plan(value: object, expected: tuple[int, str], checkpoints: tuple[CandidateFieldCheckpointRecord, ...],
               identity: CandidateEnvelopeIdentity) -> CandidatePlanRecord:
    return _plan(value, identity, expected, checkpoints)


def _disabled_path(value: object, expected_role: str, identity: CandidateEnvelopeIdentity,
                   registry: CandidateEnvelopeValidationRegistry) -> DisabledFullPathProfile:
    code = "NULL_PATH_CARDINALITY_INVALID"
    p, _ = _record(value, DisabledFullPathProfile, "path_digest", code)
    if p["path_role"] != expected_role or p["candidate_updates_enabled"] is not False:
        raise _ValidationError("NULL_PATH_CANDIDATE_STATE_LEAK")
    raw_checkpoints = _list(p["checkpoint_records"], code)
    if len(raw_checkpoints) != 40:
        raise _ValidationError(code)
    checkpoints = tuple(_field_checkpoint(item, identity, index, registry.checkpoint_axis[index - 1])
                        for index, item in enumerate(raw_checkpoints, 1))
    raw_plans = _list(p["plan_records"], code)
    if len(raw_plans) != 17:
        raise _ValidationError(code)
    plans = tuple(_path_plan(item, (index, registry.plan_roles[index - 1]), checkpoints, identity)
                  for index, item in enumerate(raw_plans, 1))
    states = tuple(p["candidate_state_digests"])
    carries = tuple(p["candidate_carry_digests"])
    if states or carries:
        raise _ValidationError("NULL_PATH_CANDIDATE_STATE_LEAK")
    _sha(p["terminal_event_chain_digest"], code)
    return DisabledFullPathProfile(p["path_role"], False, plans, checkpoints, states, carries,
                                   p["terminal_event_chain_digest"], p["path_digest"])


def _null_pair(value: object, expected: int, disabled: DisabledFullPathProfile,
               reference: DisabledFullPathProfile) -> NullPathPairRecord:
    p, _ = _record(value, NullPathPairRecord, "pair_digest", "NULL_PATH_REFERENCE_INVALID")
    if (p["checkpoint_ordinal"], p["disabled_checkpoint_digest"], p["reference_checkpoint_digest"]) != (
        expected, disabled.checkpoint_records[expected - 1].checkpoint_digest,
        reference.checkpoint_records[expected - 1].checkpoint_digest,
    ):
        raise _ValidationError("NULL_PATH_REFERENCE_INVALID")
    left = _without(_canonical(disabled.checkpoint_records[expected - 1]), "checkpoint_digest")
    right = _without(_canonical(reference.checkpoint_records[expected - 1]), "checkpoint_digest")
    if p["bit_equal"] is not True or left != right:
        raise _ValidationError("NULL_PATH_MISMATCH")
    return NullPathPairRecord(**p)


def _release(value: object, plans: tuple[CandidatePlanRecord, ...], checkpoints: tuple[CandidateFieldCheckpointRecord, ...],
             states: tuple[CandidateStateCheckpointRecord, ...], balances: tuple[CandidateBalanceCheckpointRecord, ...]) -> ReleaseLifecycleLink:
    code = "RELEASE_LINK_INVALID"
    p, _ = _record(value, ReleaseLifecycleLink, "release_link_digest", code)
    early, late = plans[11], plans[12]
    selected = tuple(item for item in checkpoints if item.plan_position in (12, 13))
    ordinals = tuple(item.checkpoint_ordinal for item in selected)
    if (p["early_plan_digest"], p["late_plan_digest"]) != (early.plan_digest, late.plan_digest):
        raise _ValidationError(code)
    if tuple(p["early_checkpoint_digests"]) != early.checkpoint_digests or tuple(p["late_checkpoint_digests"]) != late.checkpoint_digests:
        raise _ValidationError(code)
    if tuple(p["state_checkpoint_digests"]) != tuple(states[i - 1].state_checkpoint_digest for i in ordinals):
        raise _ValidationError(code)
    if tuple(p["balance_checkpoint_digests"]) != tuple(balances[i - 1].balance_checkpoint_digest for i in ordinals):
        raise _ValidationError(code)
    for name in ("shared_provenance_digest", "functional_loss_proof_digest"):
        _sha(p[name], code)
    capacity = tuple(_number(item, code) for item in _list(p["reusable_local_capacity"], code))
    if not capacity or any(item < 0 for item in capacity) or not all(p[name] is True for name in (
        "reset_exclusion", "clipping_exclusion", "restart_exclusion", "recovery_toggle_exclusion"
    )):
        raise _ValidationError(code)
    return ReleaseLifecycleLink(**{**p, "early_checkpoint_digests": tuple(p["early_checkpoint_digests"]),
                                   "late_checkpoint_digests": tuple(p["late_checkpoint_digests"]),
                                   "state_checkpoint_digests": tuple(p["state_checkpoint_digests"]),
                                   "balance_checkpoint_digests": tuple(p["balance_checkpoint_digests"]),
                                   "reusable_local_capacity": capacity})


def _reuse(value: object, plans: tuple[CandidatePlanRecord, ...], release: ReleaseLifecycleLink) -> ReuseLifecycleLink:
    code = "REUSE_LINK_INVALID"
    p, _ = _record(value, ReuseLifecycleLink, "reuse_link_digest", code)
    if p["release_link_digest"] != release.release_link_digest:
        raise _ValidationError("REUSE_LINK_WITHOUT_RELEASE")
    expected = (plans[13].plan_digest, plans[14].plan_digest, plans[15].plan_digest, plans[16].plan_digest)
    actual = (p["released_plan_digest"], p["early_plan_digest"], p["fresh_early_plan_digest"], p["fresh_late_plan_digest"])
    if actual != expected:
        raise _ValidationError(code)
    for name in ("pre_history_balance_digests", "readout_checkpoint_digests"):
        if not _list(p[name], code) or not all(_SHA.fullmatch(str(item)) for item in p[name]):
            raise _ValidationError(code)
    _sha(p["role_identity_digest"], code)
    demand = tuple(_number(item, code) for item in _list(p["local_reuse_demand"], code))
    if not demand or any(item < 0 for item in demand):
        raise _ValidationError(code)
    return ReuseLifecycleLink(**{**p, "pre_history_balance_digests": tuple(p["pre_history_balance_digests"]),
                                 "local_reuse_demand": demand,
                                 "readout_checkpoint_digests": tuple(p["readout_checkpoint_digests"])})


def _contains_forbidden(value: object, registry: CandidateEnvelopeValidationRegistry) -> bool:
    tokens = registry.forbidden_information_tokens
    if isinstance(value, Mapping):
        return any(any(token in key.lower() for token in tokens) or _contains_forbidden(item, registry)
                   for key, item in value.items())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_contains_forbidden(item, registry) for item in value)
    return isinstance(value, str) and any(token in value.lower() for token in tokens)


def _completion(value: object, family_digests: tuple[str, ...], envelope_digest: str) -> EnvelopeCompletionRecord:
    code = "ENVELOPE_COMPLETION_INVALID"
    p, _ = _record(value, EnvelopeCompletionRecord, "completion_digest", code)
    if (tuple(p["ordered_family_digests"]) != family_digests
            or (p["plan_count"], p["field_checkpoint_count"], p["candidate_interval_count"],
                p["post_probe_readout_count"], p["null_path_pair_count"]) != (17, 40, 127, 17, 40)
            or p["information_barriers_status"] != "INFORMATION_BARRIERS_SATISFIED"
            or p["envelope_digest"] != envelope_digest
            or p["completion_status"] != "CANDIDATE_ENVELOPE_STRUCTURALLY_COMPLETE"):
        raise _ValidationError(code)
    if p["partial_result"] is not False:
        raise _ValidationError("PARTIAL_RESULT_FORBIDDEN")
    return EnvelopeCompletionRecord(**{**p, "ordered_family_digests": tuple(p["ordered_family_digests"])})


def _validate_root(root: dict[str, object], registry: CandidateEnvelopeValidationRegistry) -> CandidateObservationEnvelope:
    if tuple(sorted(root)) != tuple(sorted(registry.root_families)):
        raise _ValidationError("ENVELOPE_ROOT_SCHEMA_INVALID")
    identity = _identity(root["envelope_identity"], registry)

    field_root = _exact(root["candidate_field_profile"], ("plans", "field_checkpoints", "field_profile"),
                        "ENVELOPE_ROOT_SCHEMA_INVALID")
    raw_checkpoints = _list(field_root["field_checkpoints"], "CHECKPOINT_AXIS_INVALID")
    if len(raw_checkpoints) != 40:
        raise _ValidationError("CHECKPOINT_AXIS_INVALID")
    checkpoints = tuple(_field_checkpoint(item, identity, index, registry.checkpoint_axis[index - 1])
                        for index, item in enumerate(raw_checkpoints, 1))
    raw_plans = _list(field_root["plans"], "PLAN_AXIS_INVALID")
    if len(raw_plans) != 17:
        raise _ValidationError("PLAN_AXIS_INVALID")
    plans = tuple(_plan(item, identity, (index, registry.plan_roles[index - 1]), checkpoints)
                  for index, item in enumerate(raw_plans, 1))
    profile = _field_profile(field_root["field_profile"], checkpoints)

    internal = _exact(root["candidate_internal_evidence"], (
        "balance_schema_id", "balance_role_axis", "state_checkpoints", "transitions",
        "balance_checkpoints", "transition_balances",
    ), "ENVELOPE_ROOT_SCHEMA_INVALID")
    schema_id = _text(internal["balance_schema_id"], "BALANCE_SCHEMA_INVALID")
    role_axis = _strings(internal["balance_role_axis"], "BALANCE_SCHEMA_INVALID")
    if not role_axis or len(set(role_axis)) != len(role_axis):
        raise _ValidationError("BALANCE_SCHEMA_INVALID")
    raw_balances = _list(internal["balance_checkpoints"], "BALANCE_CHECKPOINT_COUNT_INVALID")
    if len(raw_balances) != 40:
        raise _ValidationError("BALANCE_CHECKPOINT_COUNT_INVALID")
    balances = tuple(_balance_checkpoint(item, index, schema_id, role_axis, checkpoints[index - 1])
                     for index, item in enumerate(raw_balances, 1))
    raw_states = _list(internal["state_checkpoints"], "STATE_CHECKPOINT_COUNT_INVALID")
    if len(raw_states) != 40:
        raise _ValidationError("STATE_CHECKPOINT_COUNT_INVALID")
    states = tuple(_state_checkpoint(item, index, identity, checkpoints[index - 1], balances[index - 1])
                   for index, item in enumerate(raw_states, 1))
    raw_transitions = _list(internal["transitions"], "TRANSITION_COUNT_INVALID")
    if len(raw_transitions) != 127:
        raise _ValidationError("TRANSITION_COUNT_INVALID")
    transitions = tuple(_transition(item, index, registry, plans, states, balances)
                        for index, item in enumerate(raw_transitions, 1))
    raw_transition_balances = _list(internal["transition_balances"], "BALANCE_TRANSITION_COUNT_INVALID")
    if len(raw_transition_balances) != 127:
        raise _ValidationError("BALANCE_TRANSITION_COUNT_INVALID")
    transition_balances = tuple(
        _transition_balance(item, index, balances, transitions[index - 1].causal_source)
        for index, item in enumerate(raw_transition_balances, 1)
    )

    controls = _exact(root["candidate_controls"], (
        "readout_ablations", "disabled_candidate_path", "independent_reference_path", "null_path_pairs",
    ), "ENVELOPE_ROOT_SCHEMA_INVALID")
    raw_ablations = _list(controls["readout_ablations"], "ABLATION_COUNT_INVALID")
    if len(raw_ablations) != 17:
        raise _ValidationError("ABLATION_COUNT_INVALID")
    readout_checkpoints = tuple(item for item in checkpoints if item.checkpoint_role == "POST_PROBE_READOUT")
    ablations = tuple(_ablation(item, registry.readout_axis[index - 1], identity, readout_checkpoints[index - 1])
                      for index, item in enumerate(raw_ablations, 1))
    disabled = _disabled_path(controls["disabled_candidate_path"], "CANDIDATE_DISABLED_FULL_PATH", identity, registry)
    reference = _disabled_path(controls["independent_reference_path"], "INDEPENDENT_FIELD_CORE_REFERENCE", identity, registry)
    raw_pairs = _list(controls["null_path_pairs"], "NULL_PATH_CARDINALITY_INVALID")
    if len(raw_pairs) != 40:
        raise _ValidationError("NULL_PATH_CARDINALITY_INVALID")
    null_pairs = tuple(_null_pair(item, index, disabled, reference) for index, item in enumerate(raw_pairs, 1))

    links = _exact(root["lifecycle_links"], ("release", "reuse"), "ENVELOPE_ROOT_SCHEMA_INVALID")
    release = _release(links["release"], plans, checkpoints, states, balances)
    reuse_payload = _exact(links["reuse"], tuple(field.name for field in fields(ReuseLifecycleLink)),
                           "REUSE_LINK_INVALID")
    if reuse_payload["release_link_digest"] != release.release_link_digest:
        raise _ValidationError("REUSE_LINK_WITHOUT_RELEASE")
    reuse = _reuse(links["reuse"], plans, release)

    non_completion = {key: root[key] for key in ROOT_FAMILIES if key != "completion"}
    family_digests = tuple(_digest(root[key]) for key in ROOT_FAMILIES if key != "completion")
    envelope_digest = _digest(non_completion)
    if _contains_forbidden(non_completion, registry):
        raise _ValidationError("INFORMATION_BARRIER_VIOLATION")
    completion = _completion(root["completion"], family_digests, envelope_digest)
    return CandidateObservationEnvelope(
        identity, plans, checkpoints, profile, states, transitions, schema_id, role_axis,
        balances, transition_balances, ablations, disabled, reference, null_pairs,
        release, reuse, completion,
    )


def _result(status: str, envelope: CandidateObservationEnvelope | None, failure: str | None,
            input_digest: str, registry_digest: str) -> CandidateEnvelopeValidationResult:
    payload = {
        "status": status, "failure_code_or_none": failure,
        "input_bytes_digest": input_digest, "registry_digest": registry_digest,
    }
    return CandidateEnvelopeValidationResult(status, envelope, failure, input_digest,
                                             registry_digest, _digest(payload))


def validate_candidate_observation_envelope(
    raw_bytes: bytes,
    registry: CandidateEnvelopeValidationRegistry,
) -> CandidateEnvelopeValidationResult:
    if type(raw_bytes) is not bytes:
        raise TypeError("raw_bytes must have exact bytes type")
    expected_registry = build_candidate_envelope_validation_registry()
    if type(registry) is not CandidateEnvelopeValidationRegistry or registry != expected_registry:
        raise TypeError("registry must equal the bound validation registry")
    input_digest = hashlib.sha256(raw_bytes).hexdigest()
    try:
        envelope = _validate_root(_parse(raw_bytes), registry)
        return _result(VALID_STATUS, envelope, None, input_digest, registry.registry_digest)
    except _ValidationError as exc:
        return _result(INVALID_STATUS, None, exc.code, input_digest, registry.registry_digest)
