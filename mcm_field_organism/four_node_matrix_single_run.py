"""Fail-closed one-shot publisher for the authorized four-node matrix."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path

from .four_node_exposure_fixture import build_four_node_exposure_fixture
from .four_node_fresh_manifest import load_four_node_fresh_manifest
from .four_node_fresh_matrix_registration import (
    load_four_node_fresh_matrix_registration,
    validate_four_node_fresh_matrix_registration_against_manifest,
)
from .four_node_matrix_artifact import (
    AUTHORIZATION,
    EXECUTION_ID,
    FourNodeMatrixArtifact,
    build_four_node_input_file_digests,
    build_four_node_matrix_artifact_bytes,
    build_four_node_source_inventory,
    canonical_json_bytes,
    four_node_runtime_identity,
    parse_four_node_matrix_artifact,
)
from .four_node_matrix_lifecycle import (
    execute_four_node_matrix,
    validate_four_node_matrix_result,
)
from .four_node_model_invocation import COMPLETED


class FourNodeMatrixSingleRunError(RuntimeError):
    """Raised with one stable technical one-shot error code."""


_MANIFEST = "reports/s1rk_four_node_fresh_manifest.json"
_REGISTRATION = "reports/s1sd_four_node_fresh_matrix_registration.json"
RESULT = "reports/s1ss_four_node_matrix_once_v1.json"
ATTEMPT = "reports/s1ss_four_node_matrix_once_v1.attempt.json"
LOCK = "reports/s1ss_four_node_matrix_once_v1.lock"
STAGING = "reports/.s1ss_four_node_matrix_once_v1.json.staging"
_BUDGET = (
    ("cell_count", 238),
    ("model_interval_count", 1778),
    ("align_count", 238),
    ("checkpoint_count", 560),
)


@dataclass(frozen=True, slots=True)
class _RunPaths:
    result: Path
    attempt: Path
    lock: Path
    staging: Path


def _record(payload: dict[str, object], digest_field: str) -> bytes:
    value = dict(payload)
    value[digest_field] = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    return canonical_json_bytes(value, trailing_lf=True)


def _write_exclusive(path: Path, raw_bytes: bytes) -> None:
    try:
        with path.open("xb") as handle:
            handle.write(raw_bytes)
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as exc:
        raise FourNodeMatrixSingleRunError("ONE_SHOT_EXCLUSIVE_WRITE_FAILED") from exc


def _paths(project_root: Path) -> tuple[Path, _RunPaths]:
    if not isinstance(project_root, Path):
        raise FourNodeMatrixSingleRunError("ONE_SHOT_PROJECT_ROOT_INVALID")
    try:
        root = project_root.resolve(strict=True)
    except OSError as exc:
        raise FourNodeMatrixSingleRunError("ONE_SHOT_PROJECT_ROOT_INVALID") from exc
    reports = root / "reports"
    if reports.is_symlink() or not reports.is_dir():
        raise FourNodeMatrixSingleRunError("ONE_SHOT_REPORT_DIRECTORY_INVALID")
    paths = _RunPaths(
        root / RESULT,
        root / ATTEMPT,
        root / LOCK,
        root / STAGING,
    )
    fixed_names = {
        paths.result.name.casefold(),
        paths.attempt.name.casefold(),
        paths.lock.name.casefold(),
        paths.staging.name.casefold(),
    }
    try:
        present_names = {item.name.casefold() for item in reports.iterdir()}
    except OSError as exc:
        raise FourNodeMatrixSingleRunError("ONE_SHOT_REPORT_DIRECTORY_INVALID") from exc
    if fixed_names & present_names:
        raise FourNodeMatrixSingleRunError("ONE_SHOT_PATH_ALREADY_PRESENT")
    return root, paths


def _preflight(project_root: Path, authorization: str):
    if authorization != AUTHORIZATION:
        raise FourNodeMatrixSingleRunError("ONE_SHOT_AUTHORIZATION_INVALID")
    root, paths = _paths(project_root)
    try:
        source_inventory = build_four_node_source_inventory(root)
        input_file_digests = build_four_node_input_file_digests(root)
        manifest = load_four_node_fresh_manifest(root / _MANIFEST)
        registration = load_four_node_fresh_matrix_registration(root / _REGISTRATION)
        validate_four_node_fresh_matrix_registration_against_manifest(
            registration,
            manifest,
        )
        fixture = build_four_node_exposure_fixture(registration)
    except FourNodeMatrixSingleRunError:
        raise
    except Exception as exc:
        raise FourNodeMatrixSingleRunError("ONE_SHOT_PREFLIGHT_FAILED") from exc
    return (
        root,
        paths,
        source_inventory,
        input_file_digests,
        manifest,
        registration,
        fixture,
    )


def run_four_node_matrix_once(
    project_root: Path,
    authorization: str,
) -> FourNodeMatrixArtifact:
    """Execute and atomically publish exactly one authorized matrix attempt."""

    (
        root,
        paths,
        source_before,
        inputs_before,
        manifest,
        registration,
        fixture,
    ) = _preflight(project_root, authorization)
    lock_payload = {
        "execution_id": EXECUTION_ID,
        "authorization": authorization,
        "source_inventory_digest": source_before.inventory_digest,
        "manifest_file_digest": inputs_before[0][1],
        "registration_file_digest": inputs_before[1][1],
    }
    attempt_payload = {
        **lock_payload,
        "status": "STARTED",
        "budget": _BUDGET,
    }
    started = False
    published = False
    try:
        _write_exclusive(paths.lock, _record(lock_payload, "lock_digest"))
        started = True
        _write_exclusive(paths.attempt, _record(attempt_payload, "attempt_digest"))

        result = execute_four_node_matrix(manifest, registration, fixture)
        validate_four_node_matrix_result(result)
        if result.status != COMPLETED or result.failure_codes:
            raise FourNodeMatrixSingleRunError("ONE_SHOT_MATRIX_NOT_COMPLETED")

        source_after = build_four_node_source_inventory(root)
        inputs_after = build_four_node_input_file_digests(root)
        if source_after != source_before or inputs_after != inputs_before:
            raise FourNodeMatrixSingleRunError("ONE_SHOT_SOURCE_DRIFT")

        artifact_bytes = build_four_node_matrix_artifact_bytes(
            result,
            source_before,
            inputs_before,
            authorization=authorization,
            runtime_identity=four_node_runtime_identity(),
        )
        _write_exclusive(paths.staging, artifact_bytes)
        try:
            staged_bytes = paths.staging.read_bytes()
        except OSError as exc:
            raise FourNodeMatrixSingleRunError("ONE_SHOT_STAGING_READ_FAILED") from exc
        artifact = parse_four_node_matrix_artifact(staged_bytes)
        if staged_bytes != artifact_bytes:
            raise FourNodeMatrixSingleRunError("ONE_SHOT_STAGING_BYTES_DIFFER")
        try:
            os.link(paths.staging, paths.result)
        except OSError as exc:
            raise FourNodeMatrixSingleRunError("ONE_SHOT_RESULT_LINK_FAILED") from exc
        published = True
        try:
            if paths.result.read_bytes() != artifact_bytes:
                raise FourNodeMatrixSingleRunError("ONE_SHOT_RESULT_BYTES_DIFFER")
        except OSError as exc:
            raise FourNodeMatrixSingleRunError("ONE_SHOT_RESULT_READ_FAILED") from exc
        for path in (paths.staging, paths.attempt, paths.lock):
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
        return artifact
    except Exception as exc:
        if started and not published:
            try:
                paths.staging.unlink(missing_ok=True)
            except OSError:
                pass
        if isinstance(exc, FourNodeMatrixSingleRunError):
            raise
        raise FourNodeMatrixSingleRunError("ONE_SHOT_STARTED_FAILURE") from exc


def main(argv: tuple[str, ...] | None = None) -> int:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--authorization", required=True)
    args = parser.parse_args(argv)
    try:
        artifact = run_four_node_matrix_once(Path.cwd(), args.authorization)
    except FourNodeMatrixSingleRunError as exc:
        print(f"error_code={exc}")
        print(f"attempt_path={ATTEMPT}")
        return 1
    print(f"execution_id={EXECUTION_ID}")
    print(f"status={artifact.matrix_result.status}")
    print(f"result_path={RESULT}")
    print(f"artifact_digest={artifact.artifact_digest}")
    print(f"matrix_result_digest={artifact.matrix_result.matrix_result_digest}")
    for key, value in _BUDGET:
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
