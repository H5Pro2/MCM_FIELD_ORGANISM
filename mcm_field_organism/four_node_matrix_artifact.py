"""Canonical carry-free artifact for one completed four-node matrix."""

from __future__ import annotations

import ast
from dataclasses import dataclass, fields
import hashlib
import json
import math
from pathlib import Path
import platform
import re
import sys
from types import MappingProxyType
from typing import Mapping

from .four_node_cell_lifecycle import FourNodeCellIdentity, FourNodeCheckpointRecord
from .four_node_matrix_lifecycle import (
    FourNodeMatrixCellSummary,
    FourNodeMatrixResult,
    validate_four_node_matrix_result,
)
from .four_node_model_invocation import COMPLETED


class FourNodeMatrixArtifactError(ValueError):
    """Raised when matrix artifact bytes or source provenance differ."""


SCHEMA_ID = "mcm.s1so.four-node-matrix-artifact.v1"
SOURCE_CONTRACT_ID = "S1-SO"
EXECUTION_ID = "mcm.s1ss.four-node-matrix.once.v1"
CANONICALIZATION_ID = "compact-json-ascii-sort-keys-no-nan-sha256-v1"
AUTHORIZATION = "S1-SS_REAL_FOUR_NODE_MATRIX_ONCE"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SOURCE_ROOTS = (
    "mcm_field_organism/four_node_matrix_single_run.py",
    "mcm_field_organism/four_node_matrix_artifact.py",
    "mcm_field_organism/four_node_matrix_lifecycle.py",
)
_PACKAGE_BOOTSTRAP = "mcm_field_organism/__init__.py"
_INPUT_FILES = (
    "reports/s1rk_four_node_fresh_manifest.json",
    "reports/s1sd_four_node_fresh_matrix_registration.json",
)


def _canonical(value: object) -> object:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise FourNodeMatrixArtifactError("non-finite artifact value")
        return 0.0 if value == 0.0 else value
    if isinstance(value, (tuple, list)):
        return [_canonical(item) for item in value]
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise FourNodeMatrixArtifactError("artifact keys must be strings")
        return {key: _canonical(value[key]) for key in sorted(value)}
    raise FourNodeMatrixArtifactError("artifact payload contains an object")


def canonical_json_bytes(value: object, *, trailing_lf: bool = False) -> bytes:
    encoded = json.dumps(
        _canonical(value),
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return encoded + (b"\n" if trailing_lf else b"")


def _digest(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


@dataclass(frozen=True, slots=True)
class FourNodeSourceFileDigest:
    relative_path: str
    sha256: str


@dataclass(frozen=True, slots=True)
class FourNodeSourceInventory:
    files: tuple[FourNodeSourceFileDigest, ...]
    inventory_digest: str


@dataclass(frozen=True, slots=True)
class FourNodeMatrixArtifact:
    root: Mapping[str, object]
    matrix_result: FourNodeMatrixResult
    artifact_digest: str


def _module_path(root: Path, module_parts: tuple[str, ...]) -> Path | None:
    file_path = root.joinpath(*module_parts).with_suffix(".py")
    if file_path.is_file():
        return file_path
    package_path = root.joinpath(*module_parts, "__init__.py")
    if package_path.is_file():
        return package_path
    return None


def _local_imports(project_root: Path, path: Path) -> tuple[Path, ...]:
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (OSError, UnicodeError, SyntaxError) as exc:
        raise FourNodeMatrixArtifactError(f"source parse failed:{path.name}:{exc}") from None
    relative = path.relative_to(project_root)
    module_parts = relative.with_suffix("").parts
    package_parts = module_parts[:-1]
    imports: set[Path] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level:
            remove = node.level - 1
            if remove > len(package_parts):
                raise FourNodeMatrixArtifactError("relative import escapes package")
            base = package_parts[: len(package_parts) - remove]
            if node.module:
                target_parts = base + tuple(node.module.split("."))
                target = _module_path(project_root, target_parts)
                if target is None:
                    raise FourNodeMatrixArtifactError(
                        f"local import is unresolved:{'.'.join(target_parts)}"
                    )
                imports.add(target)
            else:
                for alias in node.names:
                    target_parts = base + (alias.name,)
                    target = _module_path(project_root, target_parts)
                    if target is not None:
                        imports.add(target)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "mcm_field_organism" or alias.name.startswith(
                    "mcm_field_organism."
                ):
                    target = _module_path(
                        project_root,
                        tuple(alias.name.split(".")),
                    )
                    if target is None:
                        raise FourNodeMatrixArtifactError(
                            f"local import is unresolved:{alias.name}"
                        )
                    imports.add(target)
        elif isinstance(node, ast.Call):
            name = None
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            if name in {"__import__", "import_module", "_import_module"} and not (
                relative.as_posix() == "mcm_field_organism/__init__.py"
                and name == "_import_module"
            ):
                raise FourNodeMatrixArtifactError(
                    f"dynamic local import is forbidden:{relative.as_posix()}"
                )
    return tuple(sorted(imports))


def build_four_node_source_inventory(project_root: Path) -> FourNodeSourceInventory:
    """Hash the deterministic local import closure of the execution roots."""

    if not isinstance(project_root, Path):
        raise FourNodeMatrixArtifactError("project root must be pathlib.Path")
    root = project_root.resolve(strict=True)
    pending = [root / _PACKAGE_BOOTSTRAP]
    pending.extend(root / relative for relative in _SOURCE_ROOTS)
    seen: set[Path] = set()
    while pending:
        path = pending.pop()
        if path.is_symlink() or not path.is_file():
            raise FourNodeMatrixArtifactError(
                f"source path is absent or linked:{path.name}"
            )
        resolved = path.resolve(strict=True)
        try:
            resolved.relative_to(root)
        except ValueError:
            raise FourNodeMatrixArtifactError("source path escapes project root") from None
        if resolved in seen:
            continue
        seen.add(resolved)
        pending.extend(_local_imports(root, resolved))
    records = tuple(
        FourNodeSourceFileDigest(
            path.relative_to(root).as_posix(),
            _sha256_bytes(path.read_bytes()),
        )
        for path in sorted(seen, key=lambda item: item.relative_to(root).as_posix())
    )
    payload = tuple((item.relative_path, item.sha256) for item in records)
    return FourNodeSourceInventory(records, _digest(payload))


def build_four_node_input_file_digests(
    project_root: Path,
) -> tuple[tuple[str, str], ...]:
    root = project_root.resolve(strict=True)
    records = []
    for relative in _INPUT_FILES:
        path = root / relative
        if path.is_symlink() or not path.is_file():
            raise FourNodeMatrixArtifactError(f"input file is absent or linked:{relative}")
        records.append((relative, _sha256_bytes(path.read_bytes())))
    return tuple(records)


def four_node_runtime_identity() -> tuple[tuple[str, str], ...]:
    return (
        ("python_implementation", platform.python_implementation()),
        ("python_major_minor_micro", ".".join(str(item) for item in sys.version_info[:3])),
        ("platform_system", platform.system()),
        ("platform_machine", platform.machine()),
    )


def _identity_value(identity: FourNodeCellIdentity) -> dict[str, object]:
    return {item.name: getattr(identity, item.name) for item in fields(identity)}


def _summary_value(summary: FourNodeMatrixCellSummary) -> dict[str, object]:
    return {
        item.name: (
            _identity_value(summary.cell_identity)
            if item.name == "cell_identity"
            else getattr(summary, item.name)
        )
        for item in fields(summary)
    }


def _checkpoint_value(record: FourNodeCheckpointRecord) -> dict[str, object]:
    return {item.name: getattr(record, item.name) for item in fields(record)}


def _matrix_value(result: FourNodeMatrixResult) -> dict[str, object]:
    return {
        "status": result.status,
        "ordered_238_cell_summaries": tuple(
            _summary_value(item) for item in result.ordered_cell_summaries
        ),
        "ordered_560_checkpoint_records": tuple(
            _checkpoint_value(item) for item in result.ordered_checkpoint_records
        ),
        "per_role_configuration_digests": result.per_role_configuration_digests,
        "terminal_matrix_chain_digest": result.terminal_matrix_chain_digest_or_none,
        "matrix_result_digest": result.matrix_result_digest,
    }


def build_four_node_matrix_artifact_bytes(
    result: FourNodeMatrixResult,
    source_inventory: FourNodeSourceInventory,
    input_file_digests: tuple[tuple[str, str], ...],
    *,
    authorization: str,
    runtime_identity: tuple[tuple[str, str], ...] | None = None,
) -> bytes:
    """Build canonical artifact bytes from one validated completed matrix."""

    validate_four_node_matrix_result(result)
    if result.status != COMPLETED:
        raise FourNodeMatrixArtifactError("artifact requires a completed matrix")
    if authorization != AUTHORIZATION:
        raise FourNodeMatrixArtifactError("artifact authorization differs")
    if not isinstance(source_inventory, FourNodeSourceInventory):
        raise FourNodeMatrixArtifactError("source inventory type differs")
    if any(
        not isinstance(item, FourNodeSourceFileDigest)
        or not isinstance(item.relative_path, str)
        or not isinstance(item.sha256, str)
        for item in source_inventory.files
    ):
        raise FourNodeMatrixArtifactError("source inventory records differ")
    source_paths = tuple(item.relative_path for item in source_inventory.files)
    if (
        source_paths != tuple(sorted(source_paths))
        or len(set(source_paths)) != len(source_paths)
        or any(
            not item.relative_path.startswith("mcm_field_organism/")
            or not _SHA256.fullmatch(item.sha256)
            for item in source_inventory.files
        )
    ):
        raise FourNodeMatrixArtifactError("source inventory records differ")
    source_value = tuple(
        {"relative_path": item.relative_path, "sha256": item.sha256}
        for item in source_inventory.files
    )
    if source_inventory.inventory_digest != _digest(
        tuple((item.relative_path, item.sha256) for item in source_inventory.files)
    ):
        raise FourNodeMatrixArtifactError("source inventory digest differs")
    if tuple(path for path, _ in input_file_digests) != _INPUT_FILES:
        raise FourNodeMatrixArtifactError("input file axis differs")
    if any(
        not isinstance(digest, str) or not _SHA256.fullmatch(digest)
        for _, digest in input_file_digests
    ):
        raise FourNodeMatrixArtifactError("input file digest differs")
    runtime = four_node_runtime_identity() if runtime_identity is None else runtime_identity
    root = {
        "schema_id": SCHEMA_ID,
        "source_contract_id": SOURCE_CONTRACT_ID,
        "execution_id": EXECUTION_ID,
        "canonicalization_id": CANONICALIZATION_ID,
        "authorization_digest": _sha256_bytes(authorization.encode("ascii")),
        "source_inventory": source_value,
        "source_inventory_digest": source_inventory.inventory_digest,
        "input_file_digests": input_file_digests,
        "validated_input_identity": {
            "fresh_manifest_digest": result.fresh_manifest_digest_or_none,
            "matrix_registration_digest": result.matrix_registration_digest_or_none,
            "exposure_fixture_digest": result.exposure_fixture_digest_or_none,
            "axis_digest": result.axis_digest_or_none,
        },
        "runtime_identity": runtime,
        "budget_identity": result.budget_identity,
        "matrix_result": _matrix_value(result),
    }
    root["artifact_digest"] = _digest(root)
    encoded = canonical_json_bytes(root, trailing_lf=True)
    parse_four_node_matrix_artifact(encoded)
    return encoded


class _DuplicateKeyError(ValueError):
    pass


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError(key)
        result[key] = value
    return result


def _exact(value: object, keys: set[str], role: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != keys:
        raise FourNodeMatrixArtifactError(f"{role} fields differ")
    return value


def _array(value: object, role: str) -> list[object]:
    if not isinstance(value, list):
        raise FourNodeMatrixArtifactError(f"{role} must be an array")
    return value


def _pairs(
    value: object,
    role: str,
    *,
    key_type: type = str,
    value_types: tuple[type, ...] = (str,),
) -> tuple[tuple[object, object], ...]:
    pairs = _array(value, role)
    result: list[tuple[object, object]] = []
    seen: set[object] = set()
    for pair in pairs:
        items = _array(pair, f"{role} pair")
        if len(items) != 2:
            raise FourNodeMatrixArtifactError(f"{role} pair differs")
        key, item_value = items
        if (
            type(key) is not key_type
            or type(item_value) not in value_types
            or key in seen
        ):
            raise FourNodeMatrixArtifactError(f"{role} pair differs")
        seen.add(key)
        result.append((key, item_value))
    return tuple(result)


def _identity_from(value: object) -> FourNodeCellIdentity:
    payload = _exact(value, {item.name for item in fields(FourNodeCellIdentity)}, "identity")
    return FourNodeCellIdentity(*(payload[item.name] for item in fields(FourNodeCellIdentity)))


def _summary_from(value: object) -> FourNodeMatrixCellSummary:
    payload = _exact(value, {item.name for item in fields(FourNodeMatrixCellSummary)}, "summary")
    values = tuple(
        _identity_from(payload[item.name])
        if item.name == "cell_identity"
        else tuple(_array(payload[item.name], item.name))
        if item.name == "ordered_checkpoint_digests"
        else payload[item.name]
        for item in fields(FourNodeMatrixCellSummary)
    )
    return FourNodeMatrixCellSummary(*values)


def _checkpoint_from(value: object) -> FourNodeCheckpointRecord:
    payload = _exact(value, {item.name for item in fields(FourNodeCheckpointRecord)}, "checkpoint")
    tuple_fields = {
        "configuration_and_dependency_digests",
        "signed_receptor_contact_vector",
        "signed_activation_vector",
        "signed_afterimage_vector",
    }
    values = []
    for item in fields(FourNodeCheckpointRecord):
        raw = payload[item.name]
        if item.name == "configuration_and_dependency_digests":
            raw = _pairs(raw, item.name, value_types=(str, type(None)))
        elif item.name in tuple_fields:
            raw = tuple(_array(raw, item.name))
        values.append(raw)
    return FourNodeCheckpointRecord(*values)


def _matrix_from(root: dict[str, object]) -> FourNodeMatrixResult:
    matrix = _exact(
        root["matrix_result"],
        {
            "status",
            "ordered_238_cell_summaries",
            "ordered_560_checkpoint_records",
            "per_role_configuration_digests",
            "terminal_matrix_chain_digest",
            "matrix_result_digest",
        },
        "matrix_result",
    )
    identity = _exact(
        root["validated_input_identity"],
        {
            "fresh_manifest_digest",
            "matrix_registration_digest",
            "exposure_fixture_digest",
            "axis_digest",
        },
        "validated_input_identity",
    )
    result = FourNodeMatrixResult(
        matrix["status"],
        identity["fresh_manifest_digest"],
        identity["matrix_registration_digest"],
        identity["exposure_fixture_digest"],
        identity["axis_digest"],
        _pairs(root["budget_identity"], "budget_identity", value_types=(int,)),
        tuple(
            _summary_from(item)
            for item in _array(matrix["ordered_238_cell_summaries"], "summaries")
        ),
        tuple(
            _checkpoint_from(item)
            for item in _array(
                matrix["ordered_560_checkpoint_records"],
                "checkpoints",
            )
        ),
        _pairs(matrix["per_role_configuration_digests"], "configurations"),
        matrix["terminal_matrix_chain_digest"],
        None,
        None,
        None,
        (),
        None,
        matrix["matrix_result_digest"],
    )
    validate_four_node_matrix_result(result)
    return result


def _freeze(value: object) -> object:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def parse_four_node_matrix_artifact(raw_bytes: bytes) -> FourNodeMatrixArtifact:
    """Parse and fully validate canonical artifact bytes."""

    if not isinstance(raw_bytes, bytes):
        raise FourNodeMatrixArtifactError("artifact input must be bytes")
    try:
        decoded = raw_bytes.decode("ascii")
        root = json.loads(
            decoded,
            object_pairs_hook=_unique_object,
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
        )
    except (_DuplicateKeyError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise FourNodeMatrixArtifactError(f"artifact bytes are invalid:{exc}") from None
    root = _exact(
        root,
        {
            "schema_id",
            "source_contract_id",
            "execution_id",
            "canonicalization_id",
            "authorization_digest",
            "source_inventory",
            "source_inventory_digest",
            "input_file_digests",
            "validated_input_identity",
            "runtime_identity",
            "budget_identity",
            "matrix_result",
            "artifact_digest",
        },
        "artifact",
    )
    if raw_bytes != canonical_json_bytes(root, trailing_lf=True):
        raise FourNodeMatrixArtifactError("artifact bytes are not canonical")
    if (
        root["schema_id"] != SCHEMA_ID
        or root["source_contract_id"] != SOURCE_CONTRACT_ID
        or root["execution_id"] != EXECUTION_ID
        or root["canonicalization_id"] != CANONICALIZATION_ID
        or root["authorization_digest"]
        != _sha256_bytes(AUTHORIZATION.encode("ascii"))
    ):
        raise FourNodeMatrixArtifactError("artifact identity differs")
    source_records = _array(root["source_inventory"], "source_inventory")
    source_pairs = []
    for item in source_records:
        record = _exact(item, {"relative_path", "sha256"}, "source record")
        if (
            not isinstance(record["relative_path"], str)
            or not isinstance(record["sha256"], str)
            or not _SHA256.fullmatch(record["sha256"])
        ):
            raise FourNodeMatrixArtifactError("source record differs")
        source_pairs.append((record["relative_path"], record["sha256"]))
    source_paths = [path for path, _ in source_pairs]
    if (
        source_pairs != sorted(source_pairs)
        or len(set(source_paths)) != len(source_paths)
        or any(not path.startswith("mcm_field_organism/") for path in source_paths)
    ):
        raise FourNodeMatrixArtifactError("source inventory order differs")
    if root["source_inventory_digest"] != _digest(tuple(source_pairs)):
        raise FourNodeMatrixArtifactError("source inventory digest differs")
    inputs = _pairs(root["input_file_digests"], "inputs")
    if tuple(path for path, _ in inputs) != _INPUT_FILES or any(
        not isinstance(digest, str) or not _SHA256.fullmatch(digest)
        for _, digest in inputs
    ):
        raise FourNodeMatrixArtifactError("input file digests differ")
    runtime_pairs = _pairs(root["runtime_identity"], "runtime_identity")
    runtime = _exact(
        dict(runtime_pairs),
        {
            "python_implementation",
            "python_major_minor_micro",
            "platform_system",
            "platform_machine",
        },
        "runtime identity",
    )
    if any(not isinstance(value, str) or not value for value in runtime.values()):
        raise FourNodeMatrixArtifactError("runtime identity differs")
    try:
        matrix_result = _matrix_from(root)
    except FourNodeMatrixArtifactError:
        raise
    except (TypeError, ValueError) as exc:
        raise FourNodeMatrixArtifactError(
            f"matrix artifact payload differs:{exc}"
        ) from None
    digest_payload = dict(root)
    artifact_digest = digest_payload.pop("artifact_digest")
    if not isinstance(artifact_digest, str) or artifact_digest != _digest(digest_payload):
        raise FourNodeMatrixArtifactError("artifact digest differs")
    frozen = _freeze(root)
    if not isinstance(frozen, Mapping):
        raise FourNodeMatrixArtifactError("artifact freeze failed")
    return FourNodeMatrixArtifact(frozen, matrix_result, artifact_digest)
