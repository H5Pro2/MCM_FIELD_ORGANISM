"""Passive provenance adapter from the S1-SS artifact to the S1-SV comparator."""

from __future__ import annotations

from .four_node_baseline_reference_comparator import (
    MODEL_ROLES, SOURCE_ARTIFACT_DIGEST, SOURCE_MATRIX_RESULT_DIGEST,
    FourNodeBaselineCheckpointVector, FourNodeBaselineComparatorInput,
    build_comparator_input, build_profile,
)
from .four_node_exposure_fixture import CHECKPOINT, FourNodeExposureFixture, validate_four_node_exposure_fixture
from .four_node_fresh_manifest import FourNodeFreshManifest
from .four_node_fresh_matrix_registration import FourNodeFreshMatrixRegistration, validate_four_node_fresh_matrix_registration_against_manifest
from .four_node_matrix_artifact import FourNodeMatrixArtifact, FourNodeSourceInventory
from .four_node_matrix_lifecycle import validate_four_node_matrix_result


class FourNodeBaselineInputError(ValueError):
    """Raised when artifact and current passive side inputs differ."""


def prepare_four_node_baseline_reference_input(
    artifact: FourNodeMatrixArtifact,
    manifest: FourNodeFreshManifest,
    registration: FourNodeFreshMatrixRegistration,
    fixture: FourNodeExposureFixture,
    source_inventory: FourNodeSourceInventory,
    input_file_digests: tuple[tuple[str, str], ...],
) -> FourNodeBaselineComparatorInput:
    """Reconstruct immutable profiles without filesystem access or model execution."""
    if not isinstance(artifact, FourNodeMatrixArtifact) or artifact.artifact_digest != SOURCE_ARTIFACT_DIGEST:
        raise FourNodeBaselineInputError("SOURCE_ARTIFACT_MISMATCH")
    validate_four_node_matrix_result(artifact.matrix_result)
    result = artifact.matrix_result
    if result.matrix_result_digest != SOURCE_MATRIX_RESULT_DIGEST:
        raise FourNodeBaselineInputError("SOURCE_MATRIX_RESULT_MISMATCH")
    validate_four_node_fresh_matrix_registration_against_manifest(registration, manifest)
    validate_four_node_exposure_fixture(fixture, registration)
    identity = artifact.root["validated_input_identity"]
    expected_identity = {
        "fresh_manifest_digest": manifest.manifest_digest,
        "matrix_registration_digest": registration.registration_digest,
        "exposure_fixture_digest": fixture.fixture_digest,
        "axis_digest": result.axis_digest_or_none,
    }
    if dict(identity) != expected_identity:
        raise FourNodeBaselineInputError("SIDE_INPUT_IDENTITY_MISMATCH")
    source_pairs = tuple((item.relative_path, item.sha256) for item in source_inventory.files)
    artifact_sources = tuple((item["relative_path"], item["sha256"]) for item in artifact.root["source_inventory"])
    if source_pairs != artifact_sources or source_inventory.inventory_digest != artifact.root["source_inventory_digest"]:
        raise FourNodeBaselineInputError("SOURCE_INVENTORY_MISMATCH")
    if tuple(input_file_digests) != tuple(tuple(item) for item in artifact.root["input_file_digests"]):
        raise FourNodeBaselineInputError("INPUT_FILE_DIGEST_MISMATCH")

    summary_by_key = {(item.model_role, item.plan_position): item for item in result.ordered_cell_summaries}
    record_by_digest = {item.checkpoint_digest: item for item in result.ordered_checkpoint_records}
    if len(record_by_digest) != 560:
        raise FourNodeBaselineInputError("CHECKPOINT_DIGEST_NOT_UNIQUE")
    configurations = dict(result.per_role_configuration_digests)
    profiles = []
    nullable_receptor_locations = []
    for role_position, model_role in enumerate(MODEL_ROLES, 1):
        checkpoints = []
        for plan in fixture.plans:
            summary = summary_by_key.get((model_role, plan.position))
            events = tuple(event for event in plan.events if event.event_kind == CHECKPOINT)
            if summary is None or len(summary.ordered_checkpoint_digests) != len(events):
                raise FourNodeBaselineInputError("SUMMARY_CHECKPOINT_BINDING_INVALID")
            for digest, event in zip(summary.ordered_checkpoint_digests, events, strict=True):
                record = record_by_digest.get(digest)
                if record is None or (record.model_role, record.plan_position, record.plan_role,
                                      record.checkpoint_role, record.checkpoint_tick,
                                      record.fixture_event_digest) != (model_role, plan.position,
                                      plan.replica_role, event.checkpoint_role_or_none,
                                      event.checkpoint_tick_or_none, event.event_digest):
                    raise FourNodeBaselineInputError("CHECKPOINT_FIXTURE_BINDING_INVALID")
                receptor = record.signed_receptor_contact_vector
                if any(value is None for value in receptor):
                    if (
                        receptor != (None, None, None, None)
                        or plan.replica_role != "C_GAP"
                        or record.checkpoint_role != "POST_COMPETITION"
                    ):
                        raise FourNodeBaselineInputError("RECEPTOR_PROVENANCE_NULLABILITY_INVALID")
                    nullable_receptor_locations.append((model_role, plan.replica_role, record.checkpoint_role))
                checkpoints.append(FourNodeBaselineCheckpointVector(
                    plan.position, plan.replica_role, record.checkpoint_role,
                    record.checkpoint_tick, record.fixture_event_digest,
                    record.signed_receptor_contact_vector, record.signed_activation_vector,
                    record.signed_afterimage_vector, record.checkpoint_digest,
                ))
        profiles.append(build_profile(role_position, model_role, configurations[model_role], tuple(checkpoints)))
    if nullable_receptor_locations != [
        (model_role, "C_GAP", "POST_COMPETITION") for model_role in MODEL_ROLES
    ]:
        raise FourNodeBaselineInputError("RECEPTOR_PROVENANCE_NULLABILITY_AXIS_INVALID")
    return build_comparator_input(artifact.artifact_digest, result.matrix_result_digest, tuple(profiles))
