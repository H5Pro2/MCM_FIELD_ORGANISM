"""Fail-closed one-shot publisher for the passive baseline reference atlas."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path

from .four_node_baseline_reference_artifact import (
    AUTHORIZATION, EXECUTION_ID, FourNodeBaselineReferenceArtifact,
    build_baseline_reference_artifact_bytes,
    build_baseline_reference_input_file_digests,
    build_baseline_reference_source_inventory,
    parse_baseline_reference_artifact,
)
from .four_node_baseline_reference_comparator import (
    COMPUTABLE, compare_four_node_baseline_reference,
    validate_four_node_baseline_reference_result,
)
from .four_node_baseline_reference_input import prepare_four_node_baseline_reference_input
from .four_node_exposure_fixture import build_four_node_exposure_fixture
from .four_node_fresh_manifest import load_four_node_fresh_manifest
from .four_node_fresh_matrix_registration import (
    load_four_node_fresh_matrix_registration,
    validate_four_node_fresh_matrix_registration_against_manifest,
)
from .four_node_matrix_artifact import (
    build_four_node_input_file_digests, build_four_node_source_inventory,
    canonical_json_bytes, four_node_runtime_identity, parse_four_node_matrix_artifact,
)


class FourNodeBaselineReferenceSingleRunError(RuntimeError):
    """Raised with one stable technical atlas one-shot error code."""


RESULT = "reports/s1tg_baseline_reference_atlas_once_v2.json"
ATTEMPT = "reports/s1tg_baseline_reference_atlas_once_v2.attempt.json"
LOCK = "reports/s1tg_baseline_reference_atlas_once_v2.lock"
STAGING = "reports/.s1tg_baseline_reference_atlas_once_v2.json.staging"
_SOURCE_ARTIFACT = "reports/s1ss_four_node_matrix_once_v1.json"
_MANIFEST = "reports/s1rk_four_node_fresh_manifest.json"
_REGISTRATION = "reports/s1sd_four_node_fresh_matrix_registration.json"
_BUDGET = (
    ("input_file_count", 3), ("adapter_reconstruction_count", 1),
    ("profile_count", 14), ("comparator_call_count", 1),
    ("contrast_count", 322), ("pair_count", 91),
    ("model_producer_count", 0), ("field_step_count", 0),
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
        raise FourNodeBaselineReferenceSingleRunError("ATLAS_ONE_SHOT_EXCLUSIVE_WRITE_FAILED") from exc


def _paths(project_root: Path) -> tuple[Path, _RunPaths]:
    if not isinstance(project_root, Path):
        raise FourNodeBaselineReferenceSingleRunError("ATLAS_ONE_SHOT_PROJECT_ROOT_INVALID")
    try:
        root = project_root.resolve(strict=True)
    except OSError as exc:
        raise FourNodeBaselineReferenceSingleRunError("ATLAS_ONE_SHOT_PROJECT_ROOT_INVALID") from exc
    reports = root / "reports"
    if reports.is_symlink() or not reports.is_dir():
        raise FourNodeBaselineReferenceSingleRunError("ATLAS_ONE_SHOT_REPORT_DIRECTORY_INVALID")
    paths = _RunPaths(root / RESULT, root / ATTEMPT, root / LOCK, root / STAGING)
    fixed = {path.name.casefold() for path in (paths.result, paths.attempt, paths.lock, paths.staging)}
    try:
        present = {path.name.casefold() for path in reports.iterdir()}
    except OSError as exc:
        raise FourNodeBaselineReferenceSingleRunError("ATLAS_ONE_SHOT_REPORT_DIRECTORY_INVALID") from exc
    if fixed & present:
        raise FourNodeBaselineReferenceSingleRunError("ATLAS_ONE_SHOT_PATH_ALREADY_PRESENT")
    return root, paths


def _preflight(project_root: Path, authorization: str):
    if authorization != AUTHORIZATION:
        raise FourNodeBaselineReferenceSingleRunError("ATLAS_ONE_SHOT_AUTHORIZATION_INVALID")
    root, paths = _paths(project_root)
    try:
        current_sources = build_baseline_reference_source_inventory(root)
        all_input_digests = build_baseline_reference_input_file_digests(root)
        source_artifact = parse_four_node_matrix_artifact((root / _SOURCE_ARTIFACT).read_bytes())
        manifest = load_four_node_fresh_manifest(root / _MANIFEST)
        registration = load_four_node_fresh_matrix_registration(root / _REGISTRATION)
        validate_four_node_fresh_matrix_registration_against_manifest(registration, manifest)
        fixture = build_four_node_exposure_fixture(registration)
        historical_sources = build_four_node_source_inventory(root)
        historical_inputs = build_four_node_input_file_digests(root)
        comparator_input = prepare_four_node_baseline_reference_input(
            source_artifact, manifest, registration, fixture, historical_sources, historical_inputs
        )
    except FourNodeBaselineReferenceSingleRunError:
        raise
    except Exception as exc:
        raise FourNodeBaselineReferenceSingleRunError("ATLAS_ONE_SHOT_PREFLIGHT_FAILED") from exc
    root_identity = source_artifact.root["validated_input_identity"]
    validated_identity = (
        ("source_artifact_file_sha256", all_input_digests[0][1]),
        ("source_artifact_digest", source_artifact.artifact_digest),
        ("matrix_result_digest", source_artifact.matrix_result.matrix_result_digest),
        ("manifest_file_sha256", all_input_digests[1][1]),
        ("registration_file_sha256", all_input_digests[2][1]),
        ("fresh_manifest_digest", manifest.manifest_digest),
        ("matrix_registration_digest", registration.registration_digest),
        ("exposure_fixture_digest", fixture.fixture_digest),
        ("axis_digest", root_identity["axis_digest"]),
        ("comparator_input_digest", comparator_input.input_digest),
    )
    return root, paths, current_sources, all_input_digests, comparator_input, validated_identity


def run_baseline_reference_atlas_once(
    project_root: Path,
    authorization: str,
) -> FourNodeBaselineReferenceArtifact:
    """Compare and atomically publish exactly one authorized passive atlas."""
    root, paths, sources_before, inputs_before, comparator_input, identity = _preflight(
        project_root, authorization
    )
    lock_payload = {
        "execution_id": EXECUTION_ID, "authorization": authorization,
        "comparator_source_inventory_digest": sources_before.inventory_digest,
        "input_file_digests": inputs_before,
    }
    attempt_payload = {**lock_payload, "status": "STARTED", "budget": _BUDGET}
    started = False
    published = False
    try:
        _write_exclusive(paths.lock, _record(lock_payload, "lock_digest"))
        started = True
        _write_exclusive(paths.attempt, _record(attempt_payload, "attempt_digest"))
        result = compare_four_node_baseline_reference(comparator_input)
        validate_four_node_baseline_reference_result(result)
        if result.status != COMPUTABLE or result.failure_codes:
            raise FourNodeBaselineReferenceSingleRunError("ATLAS_ONE_SHOT_NOT_COMPUTABLE")
        sources_after = build_baseline_reference_source_inventory(root)
        inputs_after = build_baseline_reference_input_file_digests(root)
        if sources_after != sources_before or inputs_after != inputs_before:
            raise FourNodeBaselineReferenceSingleRunError("ATLAS_ONE_SHOT_SOURCE_DRIFT")
        artifact_bytes = build_baseline_reference_artifact_bytes(
            result, sources_before, inputs_before, identity,
            authorization=authorization, runtime_identity=four_node_runtime_identity(),
        )
        _write_exclusive(paths.staging, artifact_bytes)
        try:
            staged = paths.staging.read_bytes()
        except OSError as exc:
            raise FourNodeBaselineReferenceSingleRunError("ATLAS_ONE_SHOT_STAGING_READ_FAILED") from exc
        artifact = parse_baseline_reference_artifact(staged)
        if staged != artifact_bytes:
            raise FourNodeBaselineReferenceSingleRunError("ATLAS_ONE_SHOT_STAGING_BYTES_DIFFER")
        try:
            os.link(paths.staging, paths.result)
        except OSError as exc:
            raise FourNodeBaselineReferenceSingleRunError("ATLAS_ONE_SHOT_RESULT_LINK_FAILED") from exc
        published = True
        try:
            if paths.result.read_bytes() != artifact_bytes:
                raise FourNodeBaselineReferenceSingleRunError("ATLAS_ONE_SHOT_RESULT_BYTES_DIFFER")
        except OSError as exc:
            raise FourNodeBaselineReferenceSingleRunError("ATLAS_ONE_SHOT_RESULT_READ_FAILED") from exc
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
        if isinstance(exc, FourNodeBaselineReferenceSingleRunError):
            raise
        raise FourNodeBaselineReferenceSingleRunError("ATLAS_ONE_SHOT_STARTED_FAILURE") from exc


def main(argv: tuple[str, ...] | None = None) -> int:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--authorization", required=True)
    args = parser.parse_args(argv)
    try:
        artifact = run_baseline_reference_atlas_once(Path.cwd(), args.authorization)
    except FourNodeBaselineReferenceSingleRunError as exc:
        print(f"error_code={exc}")
        print(f"attempt_path={ATTEMPT}")
        return 1
    print(f"execution_id={EXECUTION_ID}")
    print(f"status={artifact.result.status}")
    print(f"result_path={RESULT}")
    print(f"artifact_digest={artifact.artifact_digest}")
    print(f"baseline_reference_result_digest={artifact.result.result_digest}")
    for key, value in _BUDGET:
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
