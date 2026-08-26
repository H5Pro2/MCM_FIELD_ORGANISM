"""Canonical one-shot artifact for the passive baseline reference atlas."""

from __future__ import annotations

import ast
from dataclasses import dataclass, fields
import hashlib
import json
from pathlib import Path
import re
from types import MappingProxyType
from typing import Mapping

from .four_node_baseline_reference_comparator import (
    ABSOLUTE_CONTROL_TOLERANCE, CANDIDATE_NOT_APPLICABLE, COMPUTABLE,
    CONTRACT_DIGEST, CONTRACT_ID, PROFILE_EQUIVALENCE_LIMIT,
    SOURCE_ARTIFACT_DIGEST, SOURCE_MATRIX_RESULT_DIGEST,
    FourNodeBaselineCheckpointVector, FourNodeBaselineContrast,
    FourNodeBaselineModelProfile, FourNodeBaselinePairComparison,
    FourNodeBaselineReferenceResult, checkpoint_payload, contrast_payload,
    build_comparator_input, pair_payload, profile_payload,
    validate_four_node_baseline_reference_result,
)
from .four_node_matrix_artifact import (
    FourNodeSourceFileDigest, FourNodeSourceInventory, canonical_json_bytes,
    four_node_runtime_identity,
)


class FourNodeBaselineReferenceArtifactError(ValueError):
    """Raised when atlas bytes or their passive provenance differ."""


SCHEMA_ID = "mcm.s1tc.baseline-reference-atlas-artifact.v2"
SOURCE_CONTRACT_ID = "S1-TC"
EXECUTION_ID = "mcm.s1tg.baseline-reference-atlas.once.v2"
CANONICALIZATION_ID = "compact-json-ascii-sort-keys-no-nan-sha256-v1"
AUTHORIZATION = "S1-TG_REAL_BASELINE_REFERENCE_ATLAS_ONCE_V2"
INPUT_FILES = (
    "reports/s1ss_four_node_matrix_once_v1.json",
    "reports/s1rk_four_node_fresh_manifest.json",
    "reports/s1sd_four_node_fresh_matrix_registration.json",
)
_SOURCE_ROOTS = (
    "mcm_field_organism/four_node_baseline_reference_single_run.py",
    "mcm_field_organism/four_node_baseline_reference_artifact.py",
    "mcm_field_organism/four_node_baseline_reference_input.py",
    "mcm_field_organism/four_node_baseline_reference_comparator.py",
)
_PACKAGE_BOOTSTRAP = "mcm_field_organism/__init__.py"
_SHA = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class FourNodeBaselineReferenceArtifact:
    root: Mapping[str, object]
    result: FourNodeBaselineReferenceResult
    artifact_digest: str


def _digest(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _module_path(root: Path, parts: tuple[str, ...]) -> Path | None:
    file_path = root.joinpath(*parts).with_suffix(".py")
    if file_path.is_file():
        return file_path
    package_path = root.joinpath(*parts, "__init__.py")
    return package_path if package_path.is_file() else None


def _local_imports(root: Path, path: Path) -> tuple[Path, ...]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, UnicodeError, SyntaxError) as exc:
        raise FourNodeBaselineReferenceArtifactError("SOURCE_PARSE_FAILED") from exc
    relative = path.relative_to(root)
    package = relative.with_suffix("").parts[:-1]
    imports: set[Path] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level:
            remove = node.level - 1
            if remove > len(package):
                raise FourNodeBaselineReferenceArtifactError("SOURCE_IMPORT_ESCAPES_PACKAGE")
            base = package[: len(package) - remove]
            candidates = (base + tuple(node.module.split(".")),) if node.module else tuple(
                base + (alias.name,) for alias in node.names
            )
            for parts in candidates:
                target = _module_path(root, parts)
                if target is None and node.module:
                    raise FourNodeBaselineReferenceArtifactError("SOURCE_IMPORT_UNRESOLVED")
                if target is not None:
                    imports.add(target)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "mcm_field_organism" or alias.name.startswith("mcm_field_organism."):
                    target = _module_path(root, tuple(alias.name.split(".")))
                    if target is None:
                        raise FourNodeBaselineReferenceArtifactError("SOURCE_IMPORT_UNRESOLVED")
                    imports.add(target)
        elif isinstance(node, ast.Call):
            name = node.func.id if isinstance(node.func, ast.Name) else (
                node.func.attr if isinstance(node.func, ast.Attribute) else None
            )
            if name in {"__import__", "import_module", "_import_module"} and not (
                relative.as_posix() == _PACKAGE_BOOTSTRAP and name == "_import_module"
            ):
                raise FourNodeBaselineReferenceArtifactError("DYNAMIC_SOURCE_IMPORT_FORBIDDEN")
    return tuple(sorted(imports))


def build_baseline_reference_source_inventory(project_root: Path) -> FourNodeSourceInventory:
    """Hash the deterministic local import closure of the atlas path."""
    if not isinstance(project_root, Path):
        raise FourNodeBaselineReferenceArtifactError("PROJECT_ROOT_INVALID")
    try:
        root = project_root.resolve(strict=True)
    except OSError as exc:
        raise FourNodeBaselineReferenceArtifactError("PROJECT_ROOT_INVALID") from exc
    pending = [root / _PACKAGE_BOOTSTRAP, *(root / item for item in _SOURCE_ROOTS)]
    seen: set[Path] = set()
    while pending:
        path = pending.pop()
        if path.is_symlink() or not path.is_file():
            raise FourNodeBaselineReferenceArtifactError("SOURCE_PATH_INVALID")
        resolved = path.resolve(strict=True)
        try:
            resolved.relative_to(root)
        except ValueError:
            raise FourNodeBaselineReferenceArtifactError("SOURCE_PATH_ESCAPES_ROOT") from None
        if resolved in seen:
            continue
        seen.add(resolved)
        pending.extend(_local_imports(root, resolved))
    records = tuple(
        FourNodeSourceFileDigest(path.relative_to(root).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest())
        for path in sorted(seen, key=lambda item: item.relative_to(root).as_posix())
    )
    return FourNodeSourceInventory(records, _digest(tuple((item.relative_path, item.sha256) for item in records)))


def build_baseline_reference_input_file_digests(project_root: Path) -> tuple[tuple[str, str], ...]:
    root = project_root.resolve(strict=True)
    result = []
    for relative in INPUT_FILES:
        path = root / relative
        if path.is_symlink() or not path.is_file():
            raise FourNodeBaselineReferenceArtifactError("INPUT_FILE_INVALID")
        result.append((relative, hashlib.sha256(path.read_bytes()).hexdigest()))
    return tuple(result)


def _result_value(result: FourNodeBaselineReferenceResult) -> dict[str, object]:
    return {
        "status": result.status,
        "candidate_gate_status": result.candidate_gate_status,
        "ordered_14_complete_profiles": tuple(profile_payload(item) for item in result.profiles),
        "ordered_322_contrasts": tuple(contrast_payload(item) for item in result.contrasts),
        "ordered_91_pair_comparisons": tuple(pair_payload(item) for item in result.pairs),
        "failure_codes": result.failure_codes,
        "result_digest": result.result_digest,
    }


def build_baseline_reference_artifact_bytes(
    result: FourNodeBaselineReferenceResult,
    source_inventory: FourNodeSourceInventory,
    input_file_digests: tuple[tuple[str, str], ...],
    validated_input_identity: tuple[tuple[str, str], ...],
    *, authorization: str,
    runtime_identity: tuple[tuple[str, str], ...] | None = None,
) -> bytes:
    try:
        validate_four_node_baseline_reference_result(result)
    except (TypeError, ValueError) as exc:
        raise FourNodeBaselineReferenceArtifactError("RESULT_INVALID") from exc
    if result.status != COMPUTABLE or result.candidate_gate_status != CANDIDATE_NOT_APPLICABLE:
        raise FourNodeBaselineReferenceArtifactError("RESULT_NOT_PUBLISHABLE")
    if authorization != AUTHORIZATION:
        raise FourNodeBaselineReferenceArtifactError("AUTHORIZATION_INVALID")
    source_records = tuple((item.relative_path, item.sha256) for item in source_inventory.files)
    if (not source_records or tuple(sorted(source_records)) != source_records
            or any(not path.startswith("mcm_field_organism/") or not _SHA.fullmatch(sha) for path, sha in source_records)
            or source_inventory.inventory_digest != _digest(source_records)):
        raise FourNodeBaselineReferenceArtifactError("SOURCE_INVENTORY_INVALID")
    if tuple(path for path, _ in input_file_digests) != INPUT_FILES or any(
        not _SHA.fullmatch(digest) for _, digest in input_file_digests
    ):
        raise FourNodeBaselineReferenceArtifactError("INPUT_FILE_AXIS_INVALID")
    identity_keys = (
        "source_artifact_file_sha256", "source_artifact_digest", "matrix_result_digest",
        "manifest_file_sha256", "registration_file_sha256", "fresh_manifest_digest",
        "matrix_registration_digest", "exposure_fixture_digest", "axis_digest",
        "comparator_input_digest",
    )
    if tuple(key for key, _ in validated_input_identity) != identity_keys or any(
        not _SHA.fullmatch(value) for _, value in validated_input_identity
    ):
        raise FourNodeBaselineReferenceArtifactError("VALIDATED_INPUT_IDENTITY_INVALID")
    root = {
        "schema_id": SCHEMA_ID,
        "source_contract_id": SOURCE_CONTRACT_ID,
        "execution_id": EXECUTION_ID,
        "canonicalization_id": CANONICALIZATION_ID,
        "authorization_digest": hashlib.sha256(authorization.encode("ascii")).hexdigest(),
        "comparator_contract_identity": {
            "contract_id": CONTRACT_ID,
            "contract_digest": CONTRACT_DIGEST,
            "absolute_control_tolerance": ABSOLUTE_CONTROL_TOLERANCE,
            "profile_equivalence_limit": PROFILE_EQUIVALENCE_LIMIT,
        },
        "comparator_source_inventory": tuple(
            {"relative_path": item.relative_path, "sha256": item.sha256} for item in source_inventory.files
        ),
        "comparator_source_inventory_digest": source_inventory.inventory_digest,
        "input_file_digests": input_file_digests,
        "validated_input_identity": dict(validated_input_identity),
        "runtime_identity": four_node_runtime_identity() if runtime_identity is None else runtime_identity,
        "baseline_reference_result": _result_value(result),
    }
    root["artifact_digest"] = _digest(root)
    raw = canonical_json_bytes(root, trailing_lf=True)
    parse_baseline_reference_artifact(raw)
    return raw


class _DuplicateKey(ValueError):
    pass


def _unique(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKey(key)
        result[key] = value
    return result


def _exact(value: object, keys: set[str], role: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != keys:
        raise FourNodeBaselineReferenceArtifactError(f"{role.upper()}_FIELDS_INVALID")
    return value


def _numeric_tuple4(value: object) -> tuple[float, float, float, float]:
    if not isinstance(value, list) or len(value) != 4:
        raise FourNodeBaselineReferenceArtifactError("VECTOR_INVALID")
    if any(isinstance(item, bool) or not isinstance(item, (int, float)) for item in value):
        raise FourNodeBaselineReferenceArtifactError("NUMERIC_VECTOR_INVALID")
    return tuple(value)  # type: ignore[return-value]


def _receptor_tuple4(
    value: object,
) -> tuple[float | None, float | None, float | None, float | None]:
    if not isinstance(value, list) or len(value) != 4:
        raise FourNodeBaselineReferenceArtifactError("RECEPTOR_VECTOR_INVALID")
    if all(item is None for item in value):
        return (None, None, None, None)
    if any(item is None or isinstance(item, bool) or not isinstance(item, (int, float)) for item in value):
        raise FourNodeBaselineReferenceArtifactError("RECEPTOR_VECTOR_INVALID")
    return tuple(value)  # type: ignore[return-value]


def _checkpoint_from(value: object) -> FourNodeBaselineCheckpointVector:
    raw = _exact(value, {item.name for item in fields(FourNodeBaselineCheckpointVector)}, "checkpoint")
    return FourNodeBaselineCheckpointVector(
        raw["plan_position"], raw["plan_role"], raw["checkpoint_role"], raw["checkpoint_tick"],
        raw["fixture_event_digest"], _receptor_tuple4(raw["receptor_contact"]),
        _numeric_tuple4(raw["activation"]), _numeric_tuple4(raw["afterimage"]),
        raw["checkpoint_digest"],
    )


def _profile_from(value: object) -> FourNodeBaselineModelProfile:
    raw = _exact(value, {item.name for item in fields(FourNodeBaselineModelProfile)}, "profile")
    if not isinstance(raw["checkpoints"], list):
        raise FourNodeBaselineReferenceArtifactError("PROFILE_CHECKPOINTS_INVALID")
    return FourNodeBaselineModelProfile(raw["role_position"], raw["model_role"], raw["configuration_digest"],
                                        tuple(_checkpoint_from(item) for item in raw["checkpoints"]), raw["profile_digest"])


def _contrast_from(value: object) -> FourNodeBaselineContrast:
    raw = _exact(value, {item.name for item in fields(FourNodeBaselineContrast)}, "contrast")
    return FourNodeBaselineContrast(raw["model_role"], raw["contrast_role"],
                                    _numeric_tuple4(raw["activation_residual"]),
                                    _numeric_tuple4(raw["afterimage_residual"]),
                                    raw["activation_linf"], raw["afterimage_linf"], raw["diagnostic_only"],
                                    raw["contrast_digest"])


def _pair_from(value: object) -> FourNodeBaselinePairComparison:
    raw = _exact(value, {item.name for item in fields(FourNodeBaselinePairComparison)}, "pair")
    tuple_fields = ("left_checkpoint_digests", "right_checkpoint_digests", "signed_residual")
    if any(not isinstance(raw[name], list) for name in tuple_fields):
        raise FourNodeBaselineReferenceArtifactError("PAIR_ARRAY_INVALID")
    return FourNodeBaselinePairComparison(*(
        tuple(raw[item.name]) if item.name in tuple_fields else raw[item.name]
        for item in fields(FourNodeBaselinePairComparison)
    ))


def _freeze(value: object) -> object:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def parse_baseline_reference_artifact(raw_bytes: bytes) -> FourNodeBaselineReferenceArtifact:
    """Strictly parse canonical successful atlas bytes."""
    if not isinstance(raw_bytes, bytes):
        raise FourNodeBaselineReferenceArtifactError("ARTIFACT_BYTES_INVALID")
    try:
        root = json.loads(raw_bytes.decode("ascii"), object_pairs_hook=_unique,
                          parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    except (_DuplicateKey, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise FourNodeBaselineReferenceArtifactError("ARTIFACT_BYTES_INVALID") from exc
    root = _exact(root, {
        "schema_id", "source_contract_id", "execution_id", "canonicalization_id",
        "authorization_digest", "comparator_contract_identity", "comparator_source_inventory",
        "comparator_source_inventory_digest", "input_file_digests", "validated_input_identity",
        "runtime_identity", "baseline_reference_result", "artifact_digest",
    }, "artifact")
    if raw_bytes != canonical_json_bytes(root, trailing_lf=True):
        raise FourNodeBaselineReferenceArtifactError("ARTIFACT_NOT_CANONICAL")
    if (root["schema_id"], root["source_contract_id"], root["execution_id"], root["canonicalization_id"]) != (
        SCHEMA_ID, SOURCE_CONTRACT_ID, EXECUTION_ID, CANONICALIZATION_ID
    ) or root["authorization_digest"] != hashlib.sha256(AUTHORIZATION.encode("ascii")).hexdigest():
        raise FourNodeBaselineReferenceArtifactError("ARTIFACT_IDENTITY_INVALID")
    contract = _exact(root["comparator_contract_identity"], {
        "contract_id", "contract_digest", "absolute_control_tolerance", "profile_equivalence_limit"
    }, "contract")
    if contract != {"contract_id": CONTRACT_ID, "contract_digest": CONTRACT_DIGEST,
                    "absolute_control_tolerance": ABSOLUTE_CONTROL_TOLERANCE,
                    "profile_equivalence_limit": PROFILE_EQUIVALENCE_LIMIT}:
        raise FourNodeBaselineReferenceArtifactError("CONTRACT_IDENTITY_INVALID")
    records = root["comparator_source_inventory"]
    if not isinstance(records, list):
        raise FourNodeBaselineReferenceArtifactError("SOURCE_INVENTORY_INVALID")
    source_pairs = []
    for value in records:
        item = _exact(value, {"relative_path", "sha256"}, "source")
        source_pairs.append((item["relative_path"], item["sha256"]))
    if (not source_pairs or source_pairs != sorted(source_pairs)
            or len({path for path, _ in source_pairs}) != len(source_pairs)
            or any(not isinstance(path, str) or not path.startswith("mcm_field_organism/")
                   or not isinstance(sha, str) or not _SHA.fullmatch(sha) for path, sha in source_pairs)
            or root["comparator_source_inventory_digest"] != _digest(tuple(source_pairs))):
        raise FourNodeBaselineReferenceArtifactError("SOURCE_INVENTORY_INVALID")
    input_pairs = root["input_file_digests"]
    if (not isinstance(input_pairs, list)
            or any(not isinstance(item, list) or len(item) != 2
                   or not isinstance(item[0], str) or not isinstance(item[1], str)
                   or not _SHA.fullmatch(item[1]) for item in input_pairs)
            or tuple(item[0] for item in input_pairs) != INPUT_FILES):
        raise FourNodeBaselineReferenceArtifactError("INPUT_FILE_AXIS_INVALID")
    identity = _exact(root["validated_input_identity"], {
        "source_artifact_file_sha256", "source_artifact_digest", "matrix_result_digest",
        "manifest_file_sha256", "registration_file_sha256", "fresh_manifest_digest",
        "matrix_registration_digest", "exposure_fixture_digest", "axis_digest",
        "comparator_input_digest",
    }, "validated_input_identity")
    if any(not isinstance(value, str) or not _SHA.fullmatch(value) for value in identity.values()):
        raise FourNodeBaselineReferenceArtifactError("VALIDATED_INPUT_IDENTITY_INVALID")
    runtime_pairs = root["runtime_identity"]
    runtime_keys = (
        "python_implementation", "python_major_minor_micro", "platform_system", "platform_machine"
    )
    if (not isinstance(runtime_pairs, list)
            or any(not isinstance(item, list) or len(item) != 2
                   or not isinstance(item[0], str) or not isinstance(item[1], str)
                   or not item[1] for item in runtime_pairs)
            or tuple(item[0] for item in runtime_pairs) != runtime_keys):
        raise FourNodeBaselineReferenceArtifactError("RUNTIME_IDENTITY_INVALID")
    if (
        identity["source_artifact_file_sha256"] != input_pairs[0][1]
        or identity["manifest_file_sha256"] != input_pairs[1][1]
        or identity["registration_file_sha256"] != input_pairs[2][1]
        or identity["source_artifact_digest"] != SOURCE_ARTIFACT_DIGEST
        or identity["matrix_result_digest"] != SOURCE_MATRIX_RESULT_DIGEST
    ):
        raise FourNodeBaselineReferenceArtifactError("INPUT_CROSS_IDENTITY_INVALID")
    result_raw = _exact(root["baseline_reference_result"], {
        "status", "candidate_gate_status", "ordered_14_complete_profiles", "ordered_322_contrasts",
        "ordered_91_pair_comparisons", "failure_codes", "result_digest",
    }, "result")
    arrays = tuple(result_raw[name] for name in (
        "ordered_14_complete_profiles", "ordered_322_contrasts", "ordered_91_pair_comparisons", "failure_codes"
    ))
    if any(not isinstance(item, list) for item in arrays):
        raise FourNodeBaselineReferenceArtifactError("RESULT_ARRAY_INVALID")
    result = FourNodeBaselineReferenceResult(
        result_raw["status"], result_raw["candidate_gate_status"],
        tuple(_profile_from(item) for item in arrays[0]), tuple(_contrast_from(item) for item in arrays[1]),
        tuple(_pair_from(item) for item in arrays[2]), tuple(arrays[3]), result_raw["result_digest"],
    )
    try:
        validate_four_node_baseline_reference_result(result)
        comparator_input = build_comparator_input(
            SOURCE_ARTIFACT_DIGEST, SOURCE_MATRIX_RESULT_DIGEST, result.profiles
        )
    except (TypeError, ValueError) as exc:
        raise FourNodeBaselineReferenceArtifactError("RESULT_INVALID") from exc
    if comparator_input.input_digest != identity["comparator_input_digest"]:
        raise FourNodeBaselineReferenceArtifactError("COMPARATOR_INPUT_IDENTITY_INVALID")
    digest_payload = dict(root)
    artifact_digest = digest_payload.pop("artifact_digest")
    if not isinstance(artifact_digest, str) or artifact_digest != _digest(digest_payload):
        raise FourNodeBaselineReferenceArtifactError("ARTIFACT_DIGEST_INVALID")
    frozen = _freeze(root)
    if not isinstance(frozen, Mapping):
        raise FourNodeBaselineReferenceArtifactError("ARTIFACT_FREEZE_FAILED")
    return FourNodeBaselineReferenceArtifact(frozen, result, artifact_digest)
