"""Private S1-EC17 synthetic aggregate lifecycle with a small real fixture."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Callable

from .e1_confirmation_full_formation_handoff import (
    _load_refinement,
    _refinement_payload,
)
from .e1_confirmation_full_formation_resource_preflight import (
    preflight_prepared_full_formation_resources,
)
from .e1_confirmation_full_published_run_contract import (
    E1FullFormationPublishedRunContract,
    S1_EC16_EXECUTION_ID,
    S1_EC16_TRANSITIONS,
)
from .e1_confirmation_prepared_execution_bundle import (
    E1PreparedExecutionBundle,
    _atomic_publish,
    _exclusive_marker,
)
from .e1_confirmation_prepared_formation_consumer import (
    _typed_values_from_bundle,
)
from .e1_confirmation_small_refinement_matrix import (
    E1SmallRefinementMatrixResult,
    run_small_real_refinement_matrix,
)
from .e1_refined_formation_runner import _digest


class E1ConfirmationFullPublishedRunFixtureError(RuntimeError):
    """Raised when the S1-EC17 synthetic aggregate lifecycle fails closed."""


S1_EC17_SCHEMA_ID = "e1.full-published-run-fixture.s1ec17.v1"
S1_EC17_FORMATION_SCOPE = "full-geometry-small-r2-r4-r8-real-fixture"
S1_EC17_FAILURE_POLICY = "retain-attempt-marker-no-automatic-retry"


def _valid_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


def _transition_coverage() -> tuple[tuple[str, str], ...]:
    return tuple(
        (
            transition,
            "substituted-small-real-fixture"
            if transition == "execute-full-r2-r4-r8-five-arm-formation"
            else "observed-fixture-schema-equivalent"
            if transition
            == "build-complete-s1ec14-payload-while-states-are-live"
            else "observed",
        )
        for transition in S1_EC16_TRANSITIONS
    )


S1_EC17_POLICY_DIGEST = _digest(
    {
        "schema_id": S1_EC17_SCHEMA_ID,
        "formation_scope": S1_EC17_FORMATION_SCOPE,
        "transition_coverage": _transition_coverage(),
        "fixture_payload_only": True,
        "full_formation_executed": False,
        "canonical_execution_permitted": False,
        "probe_execution_permitted": False,
        "claims_permitted": False,
    }
)


def _fixture_payload(
    contract: E1FullFormationPublishedRunContract,
    bundle: E1PreparedExecutionBundle,
    preflight_digest: str,
    matrix: E1SmallRefinementMatrixResult,
) -> dict[str, object]:
    state_count = sum(len(item.arms) for item in matrix.refinements)
    edge_binding_count = sum(
        len(arm.output_state.edge_bindings)
        for refinement in matrix.refinements
        for arm in refinement.arms
    )
    if state_count != 15 or edge_binding_count != 2_175:
        raise E1ConfirmationFullPublishedRunFixtureError(
            "S1-EC17 fixture does not contain 15 complete full-geometry states"
        )
    return {
        "schema_id": S1_EC17_SCHEMA_ID,
        "execution_id": contract.execution_id,
        "aggregate_policy_digest": contract.policy_digest,
        "aggregate_contract_digest": contract.digest(),
        "resource_preflight_digest": preflight_digest,
        "input_manifest_digest": _digest(bundle.input_manifest),
        "formation_scope": S1_EC17_FORMATION_SCOPE,
        "step_counts": matrix.step_counts,
        "refinements": [_refinement_payload(item) for item in matrix.refinements],
        "history_state_distances": matrix.history_state_distances,
        "r2_r4_state_residual": matrix.r2_r4_state_residual,
        "r4_r8_state_residual": matrix.r4_r8_state_residual,
        "convergence_nonincreasing": matrix.convergence_nonincreasing,
        "all_five_arm_controls_passed": matrix.all_five_arm_controls_passed,
        "prepared_inputs_preserved": matrix.prepared_inputs_preserved,
        "matrix_result_digest": matrix.result_digest,
        "state_count": state_count,
        "edge_binding_count": edge_binding_count,
        "transition_coverage": _transition_coverage(),
        "fixture_payload_only": True,
        "full_formation_executed": False,
        "canonical_execution_permitted": False,
        "probe_execution_permitted": False,
        "claims_permitted": False,
    }


def load_full_published_run_fixture_payload(
    payload: object,
) -> E1SmallRefinementMatrixResult:
    """Typed-reload all 15 fixture states from one final S1-EC17 report."""

    if not isinstance(payload, dict):
        raise E1ConfirmationFullPublishedRunFixtureError(
            "S1-EC17 fixture payload is invalid"
        )
    required = {
        "schema_id",
        "execution_id",
        "aggregate_policy_digest",
        "aggregate_contract_digest",
        "resource_preflight_digest",
        "input_manifest_digest",
        "formation_scope",
        "step_counts",
        "refinements",
        "history_state_distances",
        "r2_r4_state_residual",
        "r4_r8_state_residual",
        "convergence_nonincreasing",
        "all_five_arm_controls_passed",
        "prepared_inputs_preserved",
        "matrix_result_digest",
        "state_count",
        "edge_binding_count",
        "transition_coverage",
        "fixture_payload_only",
        "full_formation_executed",
        "canonical_execution_permitted",
        "probe_execution_permitted",
        "claims_permitted",
    }
    if (
        set(payload) != required
        or payload["schema_id"] != S1_EC17_SCHEMA_ID
        or payload["execution_id"] != S1_EC16_EXECUTION_ID
        or payload["formation_scope"] != S1_EC17_FORMATION_SCOPE
        or any(
            not _valid_digest(payload[role])
            for role in (
                "aggregate_policy_digest",
                "aggregate_contract_digest",
                "resource_preflight_digest",
                "input_manifest_digest",
                "matrix_result_digest",
            )
        )
        or payload["state_count"] != 15
        or payload["edge_binding_count"] != 2_175
        or tuple(tuple(item) for item in payload["transition_coverage"])
        != _transition_coverage()
        or payload["fixture_payload_only"] is not True
        or payload["full_formation_executed"] is not False
        or payload["canonical_execution_permitted"] is not False
        or payload["probe_execution_permitted"] is not False
        or payload["claims_permitted"] is not False
    ):
        raise E1ConfirmationFullPublishedRunFixtureError(
            "S1-EC17 fixture payload controls changed"
        )
    try:
        matrix = E1SmallRefinementMatrixResult(
            refinements=tuple(
                _load_refinement(item) for item in payload["refinements"]
            ),
            step_counts=tuple(tuple(item) for item in payload["step_counts"]),
            history_state_distances=tuple(
                (item[0], item[1]) for item in payload["history_state_distances"]
            ),
            r2_r4_state_residual=payload["r2_r4_state_residual"],
            r4_r8_state_residual=payload["r4_r8_state_residual"],
            convergence_nonincreasing=payload["convergence_nonincreasing"],
            all_five_arm_controls_passed=payload[
                "all_five_arm_controls_passed"
            ],
            prepared_inputs_preserved=payload["prepared_inputs_preserved"],
            canonical_execution_permitted=False,
            claims_permitted=False,
            result_digest=payload["matrix_result_digest"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise E1ConfirmationFullPublishedRunFixtureError(
            "S1-EC17 fixture states cannot be reconstructed"
        ) from exc
    state_count = sum(len(item.arms) for item in matrix.refinements)
    edge_binding_count = sum(
        len(arm.output_state.edge_bindings)
        for refinement in matrix.refinements
        for arm in refinement.arms
    )
    if (
        state_count != payload["state_count"]
        or edge_binding_count != payload["edge_binding_count"]
    ):
        raise E1ConfirmationFullPublishedRunFixtureError(
            "S1-EC17 typed fixture inventory changed"
        )
    return matrix


FixtureRunner = Callable[
    [object, object, object, object],
    E1SmallRefinementMatrixResult,
]


@dataclass(frozen=True, slots=True)
class E1FullPublishedRunFixtureReceipt:
    execution_id: str
    aggregate_contract_digest: str
    resource_preflight_digest: str
    payload_digest: str
    matrix_result_digest: str
    report_path: str
    report_sha256: str
    transition_coverage: tuple[tuple[str, str], ...]
    attempt_present_during_fixture_execution: bool
    final_reread_verified: bool
    typed_reload_verified: bool
    attempt_removed_after_verification: bool
    lock_released: bool
    fixture_payload_only: bool
    full_formation_executed: bool
    canonical_execution_permitted: bool
    probe_execution_permitted: bool
    claims_permitted: bool

    def __post_init__(self) -> None:
        if (
            self.execution_id != S1_EC16_EXECUTION_ID
            or any(
                not _valid_digest(value)
                for value in (
                    self.aggregate_contract_digest,
                    self.resource_preflight_digest,
                    self.payload_digest,
                    self.matrix_result_digest,
                    self.report_sha256,
                )
            )
            or self.transition_coverage != _transition_coverage()
            or self.attempt_present_during_fixture_execution is not True
            or self.final_reread_verified is not True
            or self.typed_reload_verified is not True
            or self.attempt_removed_after_verification is not True
            or self.lock_released is not True
            or self.fixture_payload_only is not True
            or self.full_formation_executed is not False
            or self.canonical_execution_permitted is not False
            or self.probe_execution_permitted is not False
            or self.claims_permitted is not False
        ):
            raise E1ConfirmationFullPublishedRunFixtureError(
                "S1-EC17 fixture receipt changed"
            )


def execute_full_published_run_fixture_once(
    contract: E1FullFormationPublishedRunContract,
    bundle: E1PreparedExecutionBundle,
    fixture_runner: FixtureRunner = run_small_real_refinement_matrix,
) -> E1FullPublishedRunFixtureReceipt:
    """Run the aggregate lifecycle with a truthful small real substitute."""

    if not isinstance(contract, E1FullFormationPublishedRunContract):
        raise E1ConfirmationFullPublishedRunFixtureError(
            "S1-EC17 requires one S1-EC16 contract"
        )
    if not isinstance(bundle, E1PreparedExecutionBundle) or not callable(
        fixture_runner
    ):
        raise E1ConfirmationFullPublishedRunFixtureError(
            "S1-EC17 requires one prepared bundle and fixture runner"
        )
    contract.__post_init__()
    bundle.require_inputs_unchanged()
    preflight = preflight_prepared_full_formation_resources(bundle)
    if (
        contract.resource_preflight_digest != preflight.result_digest
        or contract.research_descriptor_digest
        != preflight.research_descriptor_digest
        or contract.input_manifest_digest != preflight.input_manifest_digest
    ):
        raise E1ConfirmationFullPublishedRunFixtureError(
            "S1-EC17 contract and prepared inputs do not align"
        )
    report = Path(contract.report_path)
    attempt = Path(contract.attempt_path)
    lock = Path(contract.lock_path)
    _exclusive_marker(
        lock,
        {
            "execution_id": contract.execution_id,
            "contract_digest": contract.digest(),
            "fixture_payload_only": True,
        },
    )
    attempt_created = False
    try:
        _exclusive_marker(
            attempt,
            {
                "execution_id": contract.execution_id,
                "contract_digest": contract.digest(),
                "failure_policy": S1_EC17_FAILURE_POLICY,
                "fixture_payload_only": True,
            },
        )
        attempt_created = True
        in_attempt_preflight = preflight_prepared_full_formation_resources(bundle)
        if in_attempt_preflight.result_digest != preflight.result_digest:
            raise E1ConfirmationFullPublishedRunFixtureError(
                "S1-EC17 preflight changed across Attempt"
            )
        values = _typed_values_from_bundle(bundle)
        attempt_present = attempt.is_file()
        matrix = fixture_runner(
            values.av_permutation.history_ab,
            values.av_permutation.history_ba,
            values.initial_field,
            values.initial_state,
        )
        if not isinstance(matrix, E1SmallRefinementMatrixResult):
            raise E1ConfirmationFullPublishedRunFixtureError(
                "S1-EC17 fixture runner returned no small real matrix"
            )
        payload = _fixture_payload(
            contract,
            bundle,
            preflight.result_digest,
            matrix,
        )
        payload_digest = _digest(payload)
        report_payload = {
            "execution_id": contract.execution_id,
            "aggregate_contract_digest": contract.digest(),
            "payload_digest": payload_digest,
            "payload": payload,
            "fixture_payload_only": True,
            "full_formation_executed": False,
            "canonical_execution_permitted": False,
            "probe_execution_permitted": False,
            "claims_permitted": False,
        }
        report_payload_digest = _digest(report_payload)
        encoded = _atomic_publish(report, report_payload)
        report_sha256 = hashlib.sha256(encoded).hexdigest()
        reread = report.read_bytes()
        if hashlib.sha256(reread).hexdigest() != report_sha256:
            raise E1ConfirmationFullPublishedRunFixtureError(
                "S1-EC17 final report reread failed"
            )
        try:
            decoded = json.loads(reread.decode("ascii"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise E1ConfirmationFullPublishedRunFixtureError(
                "S1-EC17 final report is not canonical JSON"
            ) from exc
        if (
            _digest(decoded) != report_payload_digest
            or _digest(decoded["payload"]) != payload_digest
        ):
            raise E1ConfirmationFullPublishedRunFixtureError(
                "S1-EC17 final report payload changed"
            )
        loaded = load_full_published_run_fixture_payload(decoded["payload"])
        if loaded.result_digest != matrix.result_digest:
            raise E1ConfirmationFullPublishedRunFixtureError(
                "S1-EC17 typed reload changed the fixture matrix"
            )
        bundle.require_inputs_unchanged()
        attempt.unlink()
        return E1FullPublishedRunFixtureReceipt(
            execution_id=contract.execution_id,
            aggregate_contract_digest=contract.digest(),
            resource_preflight_digest=preflight.result_digest,
            payload_digest=payload_digest,
            matrix_result_digest=matrix.result_digest,
            report_path=str(report),
            report_sha256=report_sha256,
            transition_coverage=_transition_coverage(),
            attempt_present_during_fixture_execution=attempt_present,
            final_reread_verified=True,
            typed_reload_verified=True,
            attempt_removed_after_verification=True,
            lock_released=True,
            fixture_payload_only=True,
            full_formation_executed=False,
            canonical_execution_permitted=False,
            probe_execution_permitted=False,
            claims_permitted=False,
        )
    finally:
        lock.unlink(missing_ok=True)
        if not attempt_created:
            attempt.unlink(missing_ok=True)
