"""Passive S1-SV comparison of already reconstructed baseline profiles."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import itertools
import json
import math
import re


CONTRACT_ID = "mcm.s1su.baseline-reference-comparator.v1"
CONTRACT_DIGEST = "639cf70ab24892fb0e59e5baaba6c952b99b8ad16c498acf2a399841d44c5a50"
SOURCE_ARTIFACT_DIGEST = "69a3c11613d2d83660a870dfdb288b98b23e7af9934463d7836ccd77340618bb"
SOURCE_MATRIX_RESULT_DIGEST = "1188e83b4ebfb8327e8fed22e85c8a17751f9b2eaf846632091ac01c1499dde5"
ABSOLUTE_CONTROL_TOLERANCE = 1e-12
PROFILE_EQUIVALENCE_LIMIT = 0.05
COMPUTABLE = "BASELINE_REFERENCE_ATLAS_COMPUTABLE"
INVALID = "AUDIT_INVALID_NOT_COMPUTABLE"
CANDIDATE_NOT_APPLICABLE = "S1PX_CANDIDATE_GATES_NOT_APPLICABLE"
PROFILE_EQUIVALENT = "PROFILE_EQUIVALENT"
PROFILE_DISTINCT = "PROFILE_DISTINCT"

MODEL_ROLES = (
    "A0_CURRENT_CONTACT", "A1_FAST_SH", "A2_B1_FIXED_ADAPTER",
    "A2_B2_INTEGRATOR", "A2_B3_LOCAL_LEAKY", "A2_B4_LINEAR_COUPLED",
    "A2_B5_F3_FULL", "A2_B6_CONST_V", "A3_NORM", "M1_PARALLEL_LEAK",
    "M2_DELAY", "M2_REPLAY", "M4_DTS1_T1", "M5_DIRECT",
)
PLAN_ROLES = (
    "F_A", "F_C", "F_G", "T_EARLY", "T_LATER", "I_LOCAL",
    "I_REMOTE", "I_GAP", "C_LOCAL", "C_REMOTE", "C_GAP", "R_EARLY",
    "R_LATE", "U_RELEASED", "U_EARLY", "U_FRESH_B_EARLY",
    "U_FRESH_B_LATE",
)
NODE_ORDER = ("node-a", "node-b", "node-c", "node-d")
CONTRAST_ROLES = (
    "F_AC", "F_AG", "F_CG", "T_LE", "I_LR", "I_LG", "I_RG",
    "C_PRE_LR", "C_PRE_LG", "C_PRE_RG", "C_POST_MINUS_PRE_LOCAL",
    "C_POST_MINUS_PRE_REMOTE", "C_POST_MINUS_PRE_GAP", "C_DELTA_LR",
    "C_DELTA_LG", "C_DELTA_RG", "C_READOUT_LR", "C_READOUT_LG",
    "C_READOUT_RG", "R_LE", "U_RELEASED_FRESH", "U_EARLY_FRESH",
    "U_RELEASED_EARLY",
)
_SHA = re.compile(r"^[0-9a-f]{64}$")
_EXPECTED_CHECKPOINT_AXIS = tuple(
    (plan_role, checkpoint_role)
    for plan_role in PLAN_ROLES
    for checkpoint_role in (
        ("PRE_COMPETITION", "POST_COMPETITION", "ALIGNED_PRE_PROBE", "POST_PROBE_READOUT")
        if plan_role.startswith("C_")
        else ("ALIGNED_PRE_PROBE", "POST_PROBE_READOUT")
    )
)


class FourNodeBaselineComparatorError(ValueError):
    """Raised internally and converted to one atomic invalid result."""


def _canonical(value: object) -> object:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise FourNodeBaselineComparatorError("NONFINITE_VALUE")
        return 0.0 if value == 0.0 else value
    if isinstance(value, (tuple, list)):
        return [_canonical(item) for item in value]
    if isinstance(value, dict):
        return {key: _canonical(value[key]) for key in sorted(value)}
    raise FourNodeBaselineComparatorError("NONCANONICAL_VALUE")


def _digest(value: object) -> str:
    raw = json.dumps(_canonical(value), ensure_ascii=True, allow_nan=False,
                     sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True, slots=True)
class FourNodeBaselineCheckpointVector:
    plan_position: int
    plan_role: str
    checkpoint_role: str
    checkpoint_tick: int
    fixture_event_digest: str
    receptor_contact: tuple[float | None, float | None, float | None, float | None]
    activation: tuple[float, float, float, float]
    afterimage: tuple[float, float, float, float]
    checkpoint_digest: str


@dataclass(frozen=True, slots=True)
class FourNodeBaselineModelProfile:
    role_position: int
    model_role: str
    configuration_digest: str
    checkpoints: tuple[FourNodeBaselineCheckpointVector, ...]
    profile_digest: str


@dataclass(frozen=True, slots=True)
class FourNodeBaselineComparatorInput:
    artifact_digest: str
    matrix_result_digest: str
    profiles: tuple[FourNodeBaselineModelProfile, ...]
    input_digest: str


@dataclass(frozen=True, slots=True)
class FourNodeBaselineContrast:
    model_role: str
    contrast_role: str
    activation_residual: tuple[float, float, float, float]
    afterimage_residual: tuple[float, float, float, float]
    activation_linf: float
    afterimage_linf: float
    diagnostic_only: bool
    contrast_digest: str


@dataclass(frozen=True, slots=True)
class FourNodeBaselinePairComparison:
    left_model_role: str
    right_model_role: str
    left_configuration_digest: str
    right_configuration_digest: str
    left_profile_digest: str
    right_profile_digest: str
    left_checkpoint_digests: tuple[str, ...]
    right_checkpoint_digests: tuple[str, ...]
    signed_residual: tuple[float, ...]
    absolute_distance: float
    scale: float
    relative_distance: float
    status: str
    pair_digest: str


@dataclass(frozen=True, slots=True)
class FourNodeBaselineReferenceResult:
    status: str
    candidate_gate_status: str | None
    profiles: tuple[FourNodeBaselineModelProfile, ...]
    contrasts: tuple[FourNodeBaselineContrast, ...]
    pairs: tuple[FourNodeBaselinePairComparison, ...]
    failure_codes: tuple[str, ...]
    result_digest: str


def checkpoint_payload(item: FourNodeBaselineCheckpointVector) -> dict[str, object]:
    return {field.name: getattr(item, field.name) for field in fields(item)}


def profile_payload(item: FourNodeBaselineModelProfile, *, include_digest: bool = True) -> dict[str, object]:
    payload = {
        "role_position": item.role_position,
        "model_role": item.model_role,
        "configuration_digest": item.configuration_digest,
        "checkpoints": tuple(checkpoint_payload(cp) for cp in item.checkpoints),
    }
    if include_digest:
        payload["profile_digest"] = item.profile_digest
    return payload


def build_profile(role_position: int, model_role: str, configuration_digest: str,
                  checkpoints: tuple[FourNodeBaselineCheckpointVector, ...]) -> FourNodeBaselineModelProfile:
    partial = FourNodeBaselineModelProfile(role_position, model_role, configuration_digest, checkpoints, "")
    return FourNodeBaselineModelProfile(role_position, model_role, configuration_digest,
                                        checkpoints, _digest(profile_payload(partial, include_digest=False)))


def build_comparator_input(artifact_digest: str, matrix_result_digest: str,
                           profiles: tuple[FourNodeBaselineModelProfile, ...]) -> FourNodeBaselineComparatorInput:
    payload = {"contract_digest": CONTRACT_DIGEST, "artifact_digest": artifact_digest,
               "matrix_result_digest": matrix_result_digest,
               "profile_digests": tuple(item.profile_digest for item in profiles)}
    return FourNodeBaselineComparatorInput(artifact_digest, matrix_result_digest, profiles, _digest(payload))


def _vector(profile: FourNodeBaselineModelProfile) -> tuple[float, ...]:
    return tuple(value for cp in profile.checkpoints for channel in (cp.activation, cp.afterimage) for value in channel)


def _by_key(profile: FourNodeBaselineModelProfile) -> dict[tuple[str, str], FourNodeBaselineCheckpointVector]:
    return {(cp.plan_role, cp.checkpoint_role): cp for cp in profile.checkpoints}


def _sub(left: tuple[float, ...], right: tuple[float, ...]) -> tuple[float, ...]:
    return tuple(a - b for a, b in zip(left, right, strict=True))


def _linf(values: tuple[float, ...]) -> float:
    return max((abs(value) for value in values), default=0.0)


def _is_finite_number(value: object) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)


def _valid_numeric_vector(values: tuple[object, ...]) -> bool:
    return len(values) == 4 and all(_is_finite_number(value) for value in values)


def _valid_receptor_provenance(item: FourNodeBaselineCheckpointVector) -> bool:
    values = item.receptor_contact
    if len(values) != 4:
        return False
    if all(value is None for value in values):
        return item.plan_role == "C_GAP" and item.checkpoint_role == "POST_COMPETITION"
    if any(value is None for value in values):
        return False
    return all(_is_finite_number(value) for value in values)


def _contrast_endpoints(role: str) -> tuple[tuple[str, str], tuple[str, str]]:
    post = "POST_PROBE_READOUT"
    pre = "PRE_COMPETITION"
    after = "POST_COMPETITION"
    simple = {
        "F_AC": (("F_A", post), ("F_C", post)), "F_AG": (("F_A", post), ("F_G", post)),
        "F_CG": (("F_C", post), ("F_G", post)), "T_LE": (("T_LATER", post), ("T_EARLY", post)),
        "I_LR": (("I_LOCAL", post), ("I_REMOTE", post)), "I_LG": (("I_LOCAL", post), ("I_GAP", post)),
        "I_RG": (("I_REMOTE", post), ("I_GAP", post)), "C_PRE_LR": (("C_LOCAL", pre), ("C_REMOTE", pre)),
        "C_PRE_LG": (("C_LOCAL", pre), ("C_GAP", pre)), "C_PRE_RG": (("C_REMOTE", pre), ("C_GAP", pre)),
        "C_READOUT_LR": (("C_LOCAL", post), ("C_REMOTE", post)), "C_READOUT_LG": (("C_LOCAL", post), ("C_GAP", post)),
        "C_READOUT_RG": (("C_REMOTE", post), ("C_GAP", post)), "R_LE": (("R_LATE", post), ("R_EARLY", post)),
        "U_RELEASED_FRESH": (("U_RELEASED", post), ("U_FRESH_B_LATE", post)),
        "U_EARLY_FRESH": (("U_EARLY", post), ("U_FRESH_B_EARLY", post)),
        "U_RELEASED_EARLY": (("U_RELEASED", post), ("U_EARLY", post)),
    }
    if role in simple:
        return simple[role]
    if role.startswith("C_POST_MINUS_PRE_"):
        plan = "C_" + role.removeprefix("C_POST_MINUS_PRE_")
        return (plan, after), (plan, pre)
    raise FourNodeBaselineComparatorError("CONTRAST_REQUIRES_DELTA")


def _contrast(profile: FourNodeBaselineModelProfile, role: str) -> FourNodeBaselineContrast:
    keyed = _by_key(profile)
    if role.startswith("C_DELTA_"):
        suffix = role.removeprefix("C_DELTA_")
        left_name, right_name = {"LR": ("C_LOCAL", "C_REMOTE"), "LG": ("C_LOCAL", "C_GAP"), "RG": ("C_REMOTE", "C_GAP")}[suffix]
        def delta(name: str, channel: str) -> tuple[float, ...]:
            return _sub(getattr(keyed[(name, "POST_COMPETITION")], channel), getattr(keyed[(name, "PRE_COMPETITION")], channel))
        s = _sub(delta(left_name, "activation"), delta(right_name, "activation"))
        h = _sub(delta(left_name, "afterimage"), delta(right_name, "afterimage"))
    else:
        left, right = _contrast_endpoints(role)
        s = _sub(keyed[left].activation, keyed[right].activation)
        h = _sub(keyed[left].afterimage, keyed[right].afterimage)
    payload = {"model_role": profile.model_role, "contrast_role": role,
               "activation_residual": s, "afterimage_residual": h,
               "activation_linf": _linf(s), "afterimage_linf": _linf(h),
               "diagnostic_only": role == "U_RELEASED_EARLY"}
    return FourNodeBaselineContrast(*payload.values(), _digest(payload))


def _validate(value: FourNodeBaselineComparatorInput) -> None:
    if value.artifact_digest != SOURCE_ARTIFACT_DIGEST or value.matrix_result_digest != SOURCE_MATRIX_RESULT_DIGEST:
        raise FourNodeBaselineComparatorError("SOURCE_IDENTITY_MISMATCH")
    if tuple((p.role_position, p.model_role) for p in value.profiles) != tuple(enumerate(MODEL_ROLES, 1)):
        raise FourNodeBaselineComparatorError("MODEL_AXIS_INVALID")
    for profile in value.profiles:
        if not _SHA.fullmatch(profile.configuration_digest) or profile.profile_digest != _digest(profile_payload(profile, include_digest=False)):
            raise FourNodeBaselineComparatorError("PROFILE_IDENTITY_INVALID")
        if len(profile.checkpoints) != 40 or len(_vector(profile)) != 320:
            raise FourNodeBaselineComparatorError("PROFILE_CARDINALITY_INVALID")
        checkpoint_axis = tuple((cp.plan_role, cp.checkpoint_role) for cp in profile.checkpoints)
        if checkpoint_axis != _EXPECTED_CHECKPOINT_AXIS or any(
            cp.plan_position != PLAN_ROLES.index(cp.plan_role) + 1 for cp in profile.checkpoints
        ):
            raise FourNodeBaselineComparatorError("PLAN_AXIS_INVALID")
        for cp in profile.checkpoints:
            if (
                not _SHA.fullmatch(cp.fixture_event_digest)
                or not _SHA.fullmatch(cp.checkpoint_digest)
                or not _valid_receptor_provenance(cp)
                or not _valid_numeric_vector(cp.activation)
                or not _valid_numeric_vector(cp.afterimage)
            ):
                raise FourNodeBaselineComparatorError("CHECKPOINT_VALUE_INVALID")
    expected_input = build_comparator_input(value.artifact_digest, value.matrix_result_digest, value.profiles)
    if value.input_digest != expected_input.input_digest:
        raise FourNodeBaselineComparatorError("INPUT_DIGEST_INVALID")
    for index in range(40):
        reference = value.profiles[0].checkpoints[index]
        for profile in value.profiles[1:]:
            current = profile.checkpoints[index]
            if (current.plan_position, current.plan_role, current.checkpoint_role, current.checkpoint_tick,
                current.fixture_event_digest, current.receptor_contact) != (reference.plan_position, reference.plan_role,
                reference.checkpoint_role, reference.checkpoint_tick, reference.fixture_event_digest, reference.receptor_contact):
                raise FourNodeBaselineComparatorError("PUBLIC_PROVENANCE_MISMATCH")
        if reference.checkpoint_role == "ALIGNED_PRE_PROBE":
            for profile in value.profiles[1:]:
                current = profile.checkpoints[index]
                if max(_linf(_sub(current.activation, reference.activation)), _linf(_sub(current.afterimage, reference.afterimage))) > ABSOLUTE_CONTROL_TOLERANCE:
                    raise FourNodeBaselineComparatorError("PRE_READOUT_ALIGNMENT_INVALID")


def _invalid(code: str) -> FourNodeBaselineReferenceResult:
    payload = {"status": INVALID, "candidate_gate_status": None, "profiles": (),
               "contrasts": (), "pairs": (), "failure_codes": (code,)}
    return FourNodeBaselineReferenceResult(*payload.values(), _digest(payload))


def compare_four_node_baseline_reference(value: FourNodeBaselineComparatorInput) -> FourNodeBaselineReferenceResult:
    """Return the complete atlas or one atomic invalid receipt."""
    try:
        if not isinstance(value, FourNodeBaselineComparatorInput):
            raise FourNodeBaselineComparatorError("INPUT_TYPE_INVALID")
        _validate(value)
        contrasts = tuple(_contrast(profile, role) for profile in value.profiles for role in CONTRAST_ROLES)
        pairs = []
        for left, right in itertools.combinations(value.profiles, 2):
            x, y = _vector(left), _vector(right)
            residual = _sub(x, y)
            absolute = _linf(residual)
            scale = max(_linf(x), _linf(y), ABSOLUTE_CONTROL_TOLERANCE)
            relative = absolute / scale
            payload = {"left_model_role": left.model_role, "right_model_role": right.model_role,
                       "left_configuration_digest": left.configuration_digest,
                       "right_configuration_digest": right.configuration_digest,
                       "left_profile_digest": left.profile_digest,
                       "right_profile_digest": right.profile_digest,
                       "left_checkpoint_digests": tuple(cp.checkpoint_digest for cp in left.checkpoints),
                       "right_checkpoint_digests": tuple(cp.checkpoint_digest for cp in right.checkpoints),
                       "signed_residual": residual, "absolute_distance": absolute, "scale": scale,
                       "relative_distance": relative,
                       "status": PROFILE_EQUIVALENT if relative <= PROFILE_EQUIVALENCE_LIMIT else PROFILE_DISTINCT}
            pairs.append(FourNodeBaselinePairComparison(*payload.values(), _digest(payload)))
        payload = {"status": COMPUTABLE, "candidate_gate_status": CANDIDATE_NOT_APPLICABLE,
                   "profile_digests": tuple(item.profile_digest for item in value.profiles),
                   "contrast_digests": tuple(item.contrast_digest for item in contrasts),
                   "pair_digests": tuple(item.pair_digest for item in pairs), "failure_codes": ()}
        return FourNodeBaselineReferenceResult(COMPUTABLE, CANDIDATE_NOT_APPLICABLE, value.profiles, contrasts,
                                               tuple(pairs), (), _digest(payload))
    except (FourNodeBaselineComparatorError, KeyError, TypeError, ValueError) as exc:
        return _invalid(str(exc) or type(exc).__name__)


def contrast_payload(item: FourNodeBaselineContrast, *, include_digest: bool = True) -> dict[str, object]:
    payload = {field.name: getattr(item, field.name) for field in fields(item)
               if field.name != "contrast_digest"}
    if include_digest:
        payload["contrast_digest"] = item.contrast_digest
    return payload


def pair_payload(item: FourNodeBaselinePairComparison, *, include_digest: bool = True) -> dict[str, object]:
    payload = {field.name: getattr(item, field.name) for field in fields(item)
               if field.name != "pair_digest"}
    if include_digest:
        payload["pair_digest"] = item.pair_digest
    return payload


def result_digest_payload(result: FourNodeBaselineReferenceResult) -> dict[str, object]:
    if result.status == COMPUTABLE:
        return {
            "status": result.status,
            "candidate_gate_status": result.candidate_gate_status,
            "profile_digests": tuple(item.profile_digest for item in result.profiles),
            "contrast_digests": tuple(item.contrast_digest for item in result.contrasts),
            "pair_digests": tuple(item.pair_digest for item in result.pairs),
            "failure_codes": result.failure_codes,
        }
    return {
        "status": result.status,
        "candidate_gate_status": result.candidate_gate_status,
        "profiles": result.profiles,
        "contrasts": result.contrasts,
        "pairs": result.pairs,
        "failure_codes": result.failure_codes,
    }


def validate_four_node_baseline_reference_result(result: FourNodeBaselineReferenceResult) -> None:
    """Validate one result without invoking the comparator or any producer."""
    if not isinstance(result, FourNodeBaselineReferenceResult):
        raise FourNodeBaselineComparatorError("RESULT_TYPE_INVALID")
    if result.status == INVALID:
        if (result.candidate_gate_status is not None or result.profiles or result.contrasts
                or result.pairs or not result.failure_codes):
            raise FourNodeBaselineComparatorError("INVALID_RESULT_LEAKS_PARTIAL_STATE")
    elif result.status == COMPUTABLE:
        if (result.candidate_gate_status != CANDIDATE_NOT_APPLICABLE
                or result.failure_codes
                or tuple((p.role_position, p.model_role) for p in result.profiles)
                != tuple(enumerate(MODEL_ROLES, 1))
                or len(result.contrasts) != 322 or len(result.pairs) != 91):
            raise FourNodeBaselineComparatorError("COMPUTABLE_RESULT_SHAPE_INVALID")
        _validate(build_comparator_input(
            SOURCE_ARTIFACT_DIGEST, SOURCE_MATRIX_RESULT_DIGEST, result.profiles
        ))
        profile_by_role = {item.model_role: item for item in result.profiles}
        for profile in result.profiles:
            if profile.profile_digest != _digest(profile_payload(profile, include_digest=False)):
                raise FourNodeBaselineComparatorError("RESULT_PROFILE_DIGEST_INVALID")
        expected_contrast_axis = tuple((model, contrast) for model in MODEL_ROLES for contrast in CONTRAST_ROLES)
        if tuple((item.model_role, item.contrast_role) for item in result.contrasts) != expected_contrast_axis:
            raise FourNodeBaselineComparatorError("RESULT_CONTRAST_AXIS_INVALID")
        for item in result.contrasts:
            if (item != _contrast(profile_by_role[item.model_role], item.contrast_role)
                    or item.contrast_digest != _digest(contrast_payload(item, include_digest=False))):
                raise FourNodeBaselineComparatorError("RESULT_CONTRAST_DIGEST_INVALID")
        expected_pairs = tuple(itertools.combinations(MODEL_ROLES, 2))
        if tuple((item.left_model_role, item.right_model_role) for item in result.pairs) != expected_pairs:
            raise FourNodeBaselineComparatorError("RESULT_PAIR_AXIS_INVALID")
        for item in result.pairs:
            left = profile_by_role[item.left_model_role]
            right = profile_by_role[item.right_model_role]
            residual = _sub(_vector(left), _vector(right))
            absolute = _linf(residual)
            scale = max(_linf(_vector(left)), _linf(_vector(right)), ABSOLUTE_CONTROL_TOLERANCE)
            relative = absolute / scale
            if (
                item.left_configuration_digest != left.configuration_digest
                or item.right_configuration_digest != right.configuration_digest
                or item.left_profile_digest != left.profile_digest
                or item.right_profile_digest != right.profile_digest
                or item.left_checkpoint_digests != tuple(cp.checkpoint_digest for cp in left.checkpoints)
                or item.right_checkpoint_digests != tuple(cp.checkpoint_digest for cp in right.checkpoints)
                or item.signed_residual != residual
                or item.absolute_distance != absolute
                or item.scale != scale
                or item.relative_distance != relative
                or item.status != (PROFILE_EQUIVALENT if relative <= PROFILE_EQUIVALENCE_LIMIT else PROFILE_DISTINCT)
                or item.pair_digest != _digest(pair_payload(item, include_digest=False))
            ):
                raise FourNodeBaselineComparatorError("RESULT_PAIR_PROVENANCE_INVALID")
    else:
        raise FourNodeBaselineComparatorError("RESULT_STATUS_INVALID")
    if result.result_digest != _digest(result_digest_payload(result)):
        raise FourNodeBaselineComparatorError("RESULT_DIGEST_INVALID")
