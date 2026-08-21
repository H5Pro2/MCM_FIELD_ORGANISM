"""Atomic finite-matrix envelope over the accepted four-node cell producer."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math
import re

from .four_node_cell_lifecycle import (
    FourNodeCellIdentity,
    FourNodeCellResult,
    FourNodeCheckpointRecord,
    execute_four_node_cell,
    validate_four_node_cell_result,
)
from .four_node_exposure_fixture import (
    CHECKPOINT,
    FourNodeExposureFixture,
    validate_four_node_exposure_fixture,
)
from .four_node_fresh_manifest import FourNodeFreshManifest
from .four_node_fresh_matrix_registration import (
    FourNodeFreshMatrixRegistration,
    validate_four_node_fresh_matrix_registration_against_manifest,
)
from .four_node_model_invocation import COMPLETED, NOT_COMPUTABLE


class FourNodeMatrixLifecycleError(ValueError):
    """Raised only when a published matrix value is malformed."""


_MODEL_ROLES = (
    "A0_CURRENT_CONTACT",
    "A1_FAST_SH",
    "A2_B1_FIXED_ADAPTER",
    "A2_B2_INTEGRATOR",
    "A2_B3_LOCAL_LEAKY",
    "A2_B4_LINEAR_COUPLED",
    "A2_B5_F3_FULL",
    "A2_B6_CONST_V",
    "A3_NORM",
    "M1_PARALLEL_LEAK",
    "M2_DELAY",
    "M2_REPLAY",
    "M4_DTS1_T1",
    "M5_DIRECT",
)
_F3_ROLES = frozenset(_MODEL_ROLES[4:8])
_MATRIX_CHAIN_ORIGIN = "MATRIX_CHAIN_ORIGIN"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_BUDGET_IDENTITY = (
    ("cell_count", 238),
    ("model_interval_count", 1778),
    ("align_count", 238),
    ("checkpoint_count", 560),
    ("f3_cell_count", 68),
    ("f3_model_interval_count", 508),
)


class _MatrixStop(Exception):
    pass


def _canonical(value: object) -> object:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise FourNodeMatrixLifecycleError("non-finite matrix value")
        return 0.0 if value == 0.0 else value
    if isinstance(value, (tuple, list)):
        return [_canonical(item) for item in value]
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise FourNodeMatrixLifecycleError("matrix keys must be strings")
        return {key: _canonical(value[key]) for key in sorted(value)}
    raise FourNodeMatrixLifecycleError("matrix payload contains an object")


def _digest(value: object) -> str:
    encoded = json.dumps(
        _canonical(value),
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _identity_payload(identity: FourNodeCellIdentity) -> dict[str, object]:
    return {item.name: getattr(identity, item.name) for item in fields(identity)}


@dataclass(frozen=True, slots=True)
class FourNodeMatrixCellSummary:
    cell_ordinal: int
    model_role_position: int
    model_role: str
    plan_position: int
    plan_role: str
    cell_identity: FourNodeCellIdentity
    model_configuration_digest: str
    refinement_or_none: int | None
    final_carry_digest: str
    terminal_event_chain_digest: str
    ordered_checkpoint_digests: tuple[str, ...]
    cell_result_digest: str
    matrix_chain_digest: str
    cell_summary_digest: str


@dataclass(frozen=True, slots=True)
class FourNodeMatrixResult:
    status: str
    fresh_manifest_digest_or_none: str | None
    matrix_registration_digest_or_none: str | None
    exposure_fixture_digest_or_none: str | None
    axis_digest_or_none: str | None
    budget_identity: tuple[tuple[str, int], ...]
    ordered_cell_summaries: tuple[FourNodeMatrixCellSummary, ...]
    ordered_checkpoint_records: tuple[FourNodeCheckpointRecord, ...]
    per_role_configuration_digests: tuple[tuple[str, str], ...]
    terminal_matrix_chain_digest_or_none: str | None
    failed_cell_ordinal_or_none: int | None
    failed_cell_identity_or_none: FourNodeCellIdentity | None
    cell_failure_digest_or_none: str | None
    failure_codes: tuple[str, ...]
    failure_receipt_digest_or_none: str | None
    matrix_result_digest: str

    def __post_init__(self) -> None:
        if self.status == COMPLETED:
            if (
                len(self.ordered_cell_summaries) != 238
                or len(self.ordered_checkpoint_records) != 560
                or len(self.per_role_configuration_digests) != 14
                or self.terminal_matrix_chain_digest_or_none is None
                or self.failed_cell_ordinal_or_none is not None
                or self.failed_cell_identity_or_none is not None
                or self.cell_failure_digest_or_none is not None
                or self.failure_codes
                or self.failure_receipt_digest_or_none is not None
            ):
                raise FourNodeMatrixLifecycleError("completed matrix result is incomplete")
        elif self.status == NOT_COMPUTABLE:
            if (
                self.ordered_cell_summaries
                or self.ordered_checkpoint_records
                or self.per_role_configuration_digests
                or self.terminal_matrix_chain_digest_or_none is not None
                or not self.failure_codes
                or self.failure_receipt_digest_or_none is None
            ):
                raise FourNodeMatrixLifecycleError("failed matrix result leaks partial state")
        else:
            raise FourNodeMatrixLifecycleError("matrix result status is invalid")


def _axis_digest(fixture: FourNodeExposureFixture) -> str:
    return _digest(
        {
            "model_roles": tuple(enumerate(_MODEL_ROLES, start=1)),
            "plans": tuple(
                (plan.position, plan.replica_role, plan.plan_digest)
                for plan in fixture.plans
            ),
            "order": "PLAN_MAJOR_ROLE_MINOR",
            "budget_identity": _BUDGET_IDENTITY,
        }
    )


def _manifest_model_roles(manifest: FourNodeFreshManifest) -> tuple[str, ...]:
    records = tuple(manifest.root["stateless_markers"]) + tuple(
        manifest.root["private_fresh_states"]
    )
    ordered = sorted(records, key=lambda item: item["position"])
    return tuple(item["model_role"] for item in ordered)


def _summary_payload(summary: FourNodeMatrixCellSummary) -> dict[str, object]:
    return {
        item.name: (
            _identity_payload(summary.cell_identity)
            if item.name == "cell_identity"
            else getattr(summary, item.name)
        )
        for item in fields(summary)
        if item.name != "cell_summary_digest"
    }


def _matrix_result_payload(result: FourNodeMatrixResult) -> dict[str, object]:
    identity = result.failed_cell_identity_or_none
    return {
        "status": result.status,
        "fresh_manifest_digest_or_none": result.fresh_manifest_digest_or_none,
        "matrix_registration_digest_or_none": result.matrix_registration_digest_or_none,
        "exposure_fixture_digest_or_none": result.exposure_fixture_digest_or_none,
        "axis_digest_or_none": result.axis_digest_or_none,
        "budget_identity": result.budget_identity,
        "ordered_cell_summary_digests": tuple(
            item.cell_summary_digest for item in result.ordered_cell_summaries
        ),
        "ordered_checkpoint_digests": tuple(
            item.checkpoint_digest for item in result.ordered_checkpoint_records
        ),
        "per_role_configuration_digests": result.per_role_configuration_digests,
        "terminal_matrix_chain_digest_or_none": result.terminal_matrix_chain_digest_or_none,
        "failed_cell_ordinal_or_none": result.failed_cell_ordinal_or_none,
        "failed_cell_identity_or_none": (
            None if identity is None else _identity_payload(identity)
        ),
        "cell_failure_digest_or_none": result.cell_failure_digest_or_none,
        "failure_codes": result.failure_codes,
        "failure_receipt_digest_or_none": result.failure_receipt_digest_or_none,
    }


def _publish(result: FourNodeMatrixResult) -> FourNodeMatrixResult:
    values = tuple(
        getattr(result, item.name)
        if item.name != "matrix_result_digest"
        else _digest(_matrix_result_payload(result))
        for item in fields(result)
    )
    return FourNodeMatrixResult(*values)


def _expected_checkpoint_events(plan) -> tuple[object, ...]:
    return tuple(event for event in plan.events if event.event_kind == CHECKPOINT)


def _validate_completed_cell(
    result: FourNodeCellResult,
    *,
    manifest: FourNodeFreshManifest,
    registration: FourNodeFreshMatrixRegistration,
    fixture: FourNodeExposureFixture,
    model_role: str,
    plan,
    expected_refinement: int | None,
) -> None:
    validate_four_node_cell_result(result)
    if result.status != COMPLETED:
        raise _MatrixStop("MATRIX_CELL_NOT_COMPLETED")
    identity = result.cell_identity_or_none
    carry = result.final_carry_or_none
    expected_identity = FourNodeCellIdentity(
        registration.registration_digest,
        fixture.fixture_digest,
        model_role,
        plan.position,
        plan.replica_role,
        manifest.manifest_digest,
        result.model_configuration_digest_or_none,
        expected_refinement,
    )
    if (
        identity != expected_identity
        or result.matrix_registration_digest_or_none != registration.registration_digest
        or result.exposure_fixture_digest_or_none != fixture.fixture_digest
        or result.exposure_plan_digest_or_none != plan.plan_digest
        or result.refinement_or_none != expected_refinement
        or carry is None
        or carry.model_role != model_role
        or not isinstance(carry.carry_digest, str)
        or not _SHA256.fullmatch(carry.carry_digest)
        or carry.field.last_distribution is None
        or carry.field.last_distribution.field_time.window_end_tick != plan.terminal_tick
        or result.terminal_event_chain_digest_or_none is None
        or not _SHA256.fullmatch(result.terminal_event_chain_digest_or_none)
        or len(result.ordered_checkpoint_records) != plan.checkpoint_count
    ):
        raise _MatrixStop("MATRIX_CELL_IDENTITY_OR_TERMINUS_INVALID")
    expected_events = _expected_checkpoint_events(plan)
    for record, event in zip(
        result.ordered_checkpoint_records,
        expected_events,
        strict=True,
    ):
        if (
            record.model_role != model_role
            or record.plan_position != plan.position
            or record.plan_role != plan.replica_role
            or record.checkpoint_role != event.checkpoint_role_or_none
            or record.checkpoint_tick != event.checkpoint_tick_or_none
            or record.common_field_end_tick != event.checkpoint_tick_or_none
            or record.fixture_event_digest != event.event_digest
            or not _SHA256.fullmatch(record.checkpoint_digest)
        ):
            raise _MatrixStop("MATRIX_CELL_CHECKPOINT_IDENTITY_INVALID")


def execute_four_node_matrix(
    manifest: FourNodeFreshManifest,
    registration: FourNodeFreshMatrixRegistration,
    fixture: FourNodeExposureFixture,
) -> FourNodeMatrixResult:
    """Execute the finite matrix and publish only a complete atomic ledger."""

    manifest_digest: str | None = None
    registration_digest: str | None = None
    fixture_digest: str | None = None
    axis_digest: str | None = None
    failed_ordinal: int | None = None
    failed_identity: FourNodeCellIdentity | None = None
    cell_failure_digest: str | None = None
    try:
        if not isinstance(manifest, FourNodeFreshManifest):
            raise _MatrixStop("MATRIX_FRESH_MANIFEST_INVALID")
        if not isinstance(registration, FourNodeFreshMatrixRegistration):
            raise _MatrixStop("MATRIX_REGISTRATION_INVALID")
        if not isinstance(fixture, FourNodeExposureFixture):
            raise _MatrixStop("MATRIX_FIXTURE_INVALID")
        validate_four_node_fresh_matrix_registration_against_manifest(
            registration,
            manifest,
        )
        validate_four_node_exposure_fixture(fixture, registration)
        if _manifest_model_roles(manifest) != _MODEL_ROLES:
            raise _MatrixStop("MATRIX_MODEL_ROLE_AXIS_INVALID")
        manifest_digest = manifest.manifest_digest
        registration_digest = registration.registration_digest
        fixture_digest = fixture.fixture_digest
        axis_digest = _axis_digest(fixture)

        summaries: list[FourNodeMatrixCellSummary] = []
        checkpoints: list[FourNodeCheckpointRecord] = []
        configuration_by_role: dict[str, str] = {}
        checkpoint_digests: set[str] = set()
        matrix_chain = _MATRIX_CHAIN_ORIGIN
        interval_count = align_count = checkpoint_count = 0
        f3_cell_count = f3_interval_count = 0

        for plan in fixture.plans:
            for role_position, model_role in enumerate(_MODEL_ROLES, start=1):
                failed_ordinal = (plan.position - 1) * 14 + role_position
                expected_refinement = 2 if model_role in _F3_ROLES else None
                cell_result = execute_four_node_cell(
                    manifest,
                    registration,
                    fixture,
                    model_role,
                    plan.position,
                )
                candidate_failure_digest = getattr(
                    cell_result,
                    "cell_result_digest",
                    None,
                )
                cell_failure_digest = (
                    candidate_failure_digest
                    if isinstance(candidate_failure_digest, str)
                    and _SHA256.fullmatch(candidate_failure_digest)
                    else None
                )
                candidate_identity = getattr(
                    cell_result,
                    "cell_identity_or_none",
                    None,
                )
                failed_identity = (
                    candidate_identity
                    if isinstance(candidate_identity, FourNodeCellIdentity)
                    else None
                )
                _validate_completed_cell(
                    cell_result,
                    manifest=manifest,
                    registration=registration,
                    fixture=fixture,
                    model_role=model_role,
                    plan=plan,
                    expected_refinement=expected_refinement,
                )
                identity = cell_result.cell_identity_or_none
                carry = cell_result.final_carry_or_none
                configuration = cell_result.model_configuration_digest_or_none
                terminal_chain = cell_result.terminal_event_chain_digest_or_none
                if (
                    identity is None
                    or carry is None
                    or configuration is None
                    or terminal_chain is None
                    or not _SHA256.fullmatch(configuration)
                ):
                    raise _MatrixStop("MATRIX_CELL_SUMMARY_SOURCE_INVALID")
                previous_configuration = configuration_by_role.setdefault(
                    model_role,
                    configuration,
                )
                if previous_configuration != configuration:
                    raise _MatrixStop("MATRIX_ROLE_CONFIGURATION_CHANGED")

                ordered_checkpoint_digests = tuple(
                    record.checkpoint_digest
                    for record in cell_result.ordered_checkpoint_records
                )
                if (
                    len(set(ordered_checkpoint_digests))
                    != len(ordered_checkpoint_digests)
                    or checkpoint_digests.intersection(ordered_checkpoint_digests)
                ):
                    raise _MatrixStop("MATRIX_CHECKPOINT_DIGEST_DUPLICATED")
                checkpoint_digests.update(ordered_checkpoint_digests)
                matrix_chain = _digest(
                    {
                        "previous_matrix_chain_digest": matrix_chain,
                        "cell_ordinal": failed_ordinal,
                        "model_role_position": role_position,
                        "model_role": model_role,
                        "plan_position": plan.position,
                        "plan_role": plan.replica_role,
                        "cell_identity": _identity_payload(identity),
                        "cell_result_digest": cell_result.cell_result_digest,
                        "terminal_event_chain_digest": terminal_chain,
                        "ordered_checkpoint_digests": ordered_checkpoint_digests,
                    }
                )
                summary = FourNodeMatrixCellSummary(
                    failed_ordinal,
                    role_position,
                    model_role,
                    plan.position,
                    plan.replica_role,
                    identity,
                    configuration,
                    expected_refinement,
                    carry.carry_digest,
                    terminal_chain,
                    ordered_checkpoint_digests,
                    cell_result.cell_result_digest,
                    matrix_chain,
                    "",
                )
                summary = FourNodeMatrixCellSummary(
                    *(
                        getattr(summary, item.name)
                        if item.name != "cell_summary_digest"
                        else _digest(_summary_payload(summary))
                        for item in fields(summary)
                    )
                )
                summaries.append(summary)
                checkpoints.extend(cell_result.ordered_checkpoint_records)
                interval_count += plan.model_interval_count
                align_count += 1
                checkpoint_count += plan.checkpoint_count
                if model_role in _F3_ROLES:
                    f3_cell_count += 1
                    f3_interval_count += plan.model_interval_count

        if (
            len(summaries) != 238
            or interval_count != 1778
            or align_count != 238
            or checkpoint_count != 560
            or len(checkpoints) != 560
            or f3_cell_count != 68
            or f3_interval_count != 508
            or len(configuration_by_role) != 14
        ):
            raise _MatrixStop("MATRIX_TERMINAL_BUDGET_INVALID")
        configurations = tuple(
            (role, configuration_by_role[role]) for role in _MODEL_ROLES
        )
        completed = FourNodeMatrixResult(
            COMPLETED,
            manifest_digest,
            registration_digest,
            fixture_digest,
            axis_digest,
            _BUDGET_IDENTITY,
            tuple(summaries),
            tuple(checkpoints),
            configurations,
            matrix_chain,
            None,
            None,
            None,
            (),
            None,
            "",
        )
        return _publish(completed)
    except Exception as exc:
        code = (
            str(exc)
            if isinstance(exc, _MatrixStop)
            else f"MATRIX_LIFECYCLE_INVALID:{type(exc).__name__}:{exc}"
        )
        failure_receipt = _digest(
            {
                "fresh_manifest_digest_or_none": manifest_digest,
                "matrix_registration_digest_or_none": registration_digest,
                "exposure_fixture_digest_or_none": fixture_digest,
                "axis_digest_or_none": axis_digest,
                "failed_cell_ordinal_or_none": failed_ordinal,
                "failed_cell_identity_or_none": (
                    None
                    if failed_identity is None
                    else _identity_payload(failed_identity)
                ),
                "cell_failure_digest_or_none": cell_failure_digest,
                "failure_codes": (code,),
            }
        )
        failed = FourNodeMatrixResult(
            NOT_COMPUTABLE,
            manifest_digest,
            registration_digest,
            fixture_digest,
            axis_digest,
            _BUDGET_IDENTITY,
            (),
            (),
            (),
            None,
            failed_ordinal,
            failed_identity,
            cell_failure_digest,
            (code,),
            failure_receipt,
            "",
        )
        return _publish(failed)
