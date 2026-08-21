from __future__ import annotations

from dataclasses import fields, replace
import hashlib
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from mcm_field_organism.four_node_cell_lifecycle import (
    FourNodeCellIdentity,
    FourNodeCellLifecycleError,
    FourNodeCheckpointRecord,
    execute_four_node_cell,
    validate_four_node_cell_result,
)
from mcm_field_organism.four_node_exposure_fixture import (
    CHECKPOINT,
    build_four_node_exposure_fixture,
)
from mcm_field_organism.four_node_fresh_manifest import (
    load_four_node_fresh_manifest,
)
from mcm_field_organism.four_node_fresh_matrix_registration import (
    load_four_node_fresh_matrix_registration,
)
from mcm_field_organism.four_node_matrix_lifecycle import (
    FourNodeMatrixCellSummary,
    FourNodeMatrixResult,
    execute_four_node_matrix,
)
from mcm_field_organism.four_node_model_invocation import COMPLETED, NOT_COMPUTABLE


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = load_four_node_fresh_manifest(
    ROOT / "reports" / "s1rk_four_node_fresh_manifest.json"
)
REGISTRATION = load_four_node_fresh_matrix_registration(
    ROOT / "reports" / "s1sd_four_node_fresh_matrix_registration.json"
)
FIXTURE = build_four_node_exposure_fixture(REGISTRATION)
MODULE = "mcm_field_organism.four_node_matrix_lifecycle"
MODEL_ROLES = (
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
F3_ROLES = frozenset(MODEL_ROLES[4:8])


def _hash(value: object) -> str:
    return hashlib.sha256(repr(value).encode("utf-8")).hexdigest()


def _plan(position: int):
    return FIXTURE.plans[position - 1]


def _checkpoint_record(model_role: str, plan, event) -> FourNodeCheckpointRecord:
    digest = _hash((model_role, plan.position, event.event_digest))
    return FourNodeCheckpointRecord(
        model_role,
        plan.position,
        plan.replica_role,
        event.checkpoint_role_or_none,
        event.checkpoint_tick_or_none,
        event.event_digest,
        _hash(("event-chain", digest)),
        _hash(("field", digest)),
        _hash(("carry", digest)),
        None,
        (),
        _hash(("distribution", digest)),
        (0.0, 0.0, 0.0, 0.0),
        (0.0, 0.0, 0.0, 0.0),
        (0.0, 0.0, 0.0, 0.0),
        plan.model_interval_count,
        event.checkpoint_tick_or_none,
        None,
        digest,
    )


def _synthetic_cell(
    manifest,
    registration,
    fixture,
    model_role: str,
    plan_position: int,
):
    plan = fixture.plans[plan_position - 1]
    configuration = _hash(("configuration", model_role))
    refinement = 2 if model_role in F3_ROLES else None
    identity = FourNodeCellIdentity(
        registration.registration_digest,
        fixture.fixture_digest,
        model_role,
        plan.position,
        plan.replica_role,
        manifest.manifest_digest,
        configuration,
        refinement,
    )
    checkpoint_records = tuple(
        _checkpoint_record(model_role, plan, event)
        for event in plan.events
        if event.event_kind == CHECKPOINT
    )
    field_time = SimpleNamespace(window_end_tick=plan.terminal_tick)
    field = SimpleNamespace(last_distribution=SimpleNamespace(field_time=field_time))
    carry = SimpleNamespace(
        model_role=model_role,
        field=field,
        carry_digest=_hash(("final-carry", model_role, plan.position)),
    )
    return SimpleNamespace(
        status=COMPLETED,
        cell_identity_or_none=identity,
        matrix_registration_digest_or_none=registration.registration_digest,
        exposure_fixture_digest_or_none=fixture.fixture_digest,
        exposure_plan_digest_or_none=plan.plan_digest,
        model_configuration_digest_or_none=configuration,
        refinement_or_none=refinement,
        final_carry_or_none=carry,
        ordered_checkpoint_records=checkpoint_records,
        terminal_event_chain_digest_or_none=_hash(
            ("terminal-cell-chain", model_role, plan.position)
        ),
        failure_codes=(),
        failure_receipt_digest_or_none=None,
        cell_result_digest=_hash(("cell-result", model_role, plan.position)),
    )


def _synthetic_matrix(producer=_synthetic_cell):
    with (
        patch(f"{MODULE}.execute_four_node_cell", side_effect=producer) as cell_call,
        patch(f"{MODULE}.validate_four_node_cell_result", return_value=None),
    ):
        result = execute_four_node_matrix(MANIFEST, REGISTRATION, FIXTURE)
    return result, cell_call


class FourNodeMatrixLifecycleTests(unittest.TestCase):
    def test_public_cell_result_validator_accepts_atomic_failure(self) -> None:
        result = execute_four_node_cell(MANIFEST, REGISTRATION, FIXTURE, "A1_FAST_SH", 0)
        self.assertEqual(NOT_COMPUTABLE, result.status)
        validate_four_node_cell_result(result)

    def test_public_cell_result_validator_rejects_changed_digest(self) -> None:
        result = execute_four_node_cell(MANIFEST, REGISTRATION, FIXTURE, "A1_FAST_SH", 0)
        changed = replace(result, cell_result_digest="0" * 64)
        with self.assertRaises(FourNodeCellLifecycleError):
            validate_four_node_cell_result(changed)

    def test_synthetic_matrix_has_exact_cardinalities(self) -> None:
        result, cell_call = _synthetic_matrix()
        self.assertEqual(COMPLETED, result.status, result.failure_codes)
        self.assertEqual(238, cell_call.call_count)
        self.assertEqual(238, len(result.ordered_cell_summaries))
        self.assertEqual(560, len(result.ordered_checkpoint_records))
        self.assertEqual(14, len(result.per_role_configuration_digests))

    def test_cell_calls_are_plan_major_and_role_minor(self) -> None:
        result, cell_call = _synthetic_matrix()
        self.assertEqual(COMPLETED, result.status, result.failure_codes)
        axis = tuple((call.args[3], call.args[4]) for call in cell_call.call_args_list)
        expected = tuple(
            (role, plan.position)
            for plan in FIXTURE.plans
            for role in MODEL_ROLES
        )
        self.assertEqual(expected, axis)

    def test_first_and_last_ordinals_are_exact(self) -> None:
        result, _ = _synthetic_matrix()
        first = result.ordered_cell_summaries[0]
        last = result.ordered_cell_summaries[-1]
        self.assertEqual((1, "A0_CURRENT_CONTACT", "F_A"), (first.cell_ordinal, first.model_role, first.plan_role))
        self.assertEqual((238, "M5_DIRECT", "U_FRESH_B_LATE"), (last.cell_ordinal, last.model_role, last.plan_role))

    def test_role_configuration_digests_are_constant_and_ordered(self) -> None:
        result, _ = _synthetic_matrix()
        self.assertEqual(
            tuple((role, _hash(("configuration", role))) for role in MODEL_ROLES),
            result.per_role_configuration_digests,
        )

    def test_refinement_is_bound_only_to_four_f3_roles(self) -> None:
        result, _ = _synthetic_matrix()
        f3 = tuple(item for item in result.ordered_cell_summaries if item.model_role in F3_ROLES)
        other = tuple(item for item in result.ordered_cell_summaries if item.model_role not in F3_ROLES)
        self.assertEqual(68, len(f3))
        self.assertEqual(170, len(other))
        self.assertTrue(all(item.refinement_or_none == 2 for item in f3))
        self.assertTrue(all(item.refinement_or_none is None for item in other))

    def test_checkpoint_ledger_follows_cell_and_fixture_order(self) -> None:
        result, _ = _synthetic_matrix()
        expected = tuple(
            (role, plan.position, event.checkpoint_role_or_none)
            for plan in FIXTURE.plans
            for role in MODEL_ROLES
            for event in plan.events
            if event.event_kind == CHECKPOINT
        )
        actual = tuple(
            (item.model_role, item.plan_position, item.checkpoint_role)
            for item in result.ordered_checkpoint_records
        )
        self.assertEqual(expected, actual)

    def test_matrix_result_contains_digests_but_no_carry_objects(self) -> None:
        result, _ = _synthetic_matrix()
        summary_fields = {item.name for item in fields(FourNodeMatrixCellSummary)}
        result_fields = {item.name for item in fields(FourNodeMatrixResult)}
        self.assertIn("final_carry_digest", summary_fields)
        self.assertNotIn("final_carry_or_none", summary_fields)
        self.assertNotIn("final_carry_or_none", result_fields)
        self.assertTrue(all(item.final_carry_digest for item in result.ordered_cell_summaries))

    def test_budget_identity_is_exact(self) -> None:
        result, _ = _synthetic_matrix()
        self.assertEqual(
            (
                ("cell_count", 238),
                ("model_interval_count", 1778),
                ("align_count", 238),
                ("checkpoint_count", 560),
                ("f3_cell_count", 68),
                ("f3_model_interval_count", 508),
            ),
            result.budget_identity,
        )

    def test_synthetic_matrix_digest_chain_is_deterministic(self) -> None:
        first, _ = _synthetic_matrix()
        second, _ = _synthetic_matrix()
        self.assertEqual(first.matrix_result_digest, second.matrix_result_digest)
        self.assertEqual(
            first.terminal_matrix_chain_digest_or_none,
            second.terminal_matrix_chain_digest_or_none,
        )

    def test_first_cell_failure_stops_without_partial_publication(self) -> None:
        def producer(*args):
            result = _synthetic_cell(*args)
            result.status = NOT_COMPUTABLE
            return result

        result, cell_call = _synthetic_matrix(producer)
        self.assertEqual(NOT_COMPUTABLE, result.status)
        self.assertEqual(1, cell_call.call_count)
        self.assertEqual(1, result.failed_cell_ordinal_or_none)
        self.assertEqual((), result.ordered_cell_summaries)
        self.assertEqual((), result.ordered_checkpoint_records)

    def test_middle_cell_failure_discards_completed_prefix(self) -> None:
        calls = 0

        def producer(*args):
            nonlocal calls
            calls += 1
            result = _synthetic_cell(*args)
            if calls == 22:
                result.status = NOT_COMPUTABLE
            return result

        result, cell_call = _synthetic_matrix(producer)
        self.assertEqual(NOT_COMPUTABLE, result.status)
        self.assertEqual(22, cell_call.call_count)
        self.assertEqual(22, result.failed_cell_ordinal_or_none)
        self.assertEqual((), result.ordered_cell_summaries)
        self.assertEqual((), result.ordered_checkpoint_records)

    def test_role_configuration_change_fails_atomically(self) -> None:
        def producer(manifest, registration, fixture, role, position):
            result = _synthetic_cell(manifest, registration, fixture, role, position)
            if role == "A0_CURRENT_CONTACT" and position == 2:
                changed = _hash(("changed", role))
                result.model_configuration_digest_or_none = changed
                result.cell_identity_or_none = replace(
                    result.cell_identity_or_none,
                    model_configuration_digest=changed,
                )
            return result

        result, _ = _synthetic_matrix(producer)
        self.assertEqual(NOT_COMPUTABLE, result.status)
        self.assertEqual(15, result.failed_cell_ordinal_or_none)
        self.assertEqual((), result.ordered_cell_summaries)

    def test_duplicate_checkpoint_digest_fails_atomically(self) -> None:
        first_digest = _synthetic_cell(
            MANIFEST, REGISTRATION, FIXTURE, MODEL_ROLES[0], 1
        ).ordered_checkpoint_records[0].checkpoint_digest

        def producer(manifest, registration, fixture, role, position):
            result = _synthetic_cell(manifest, registration, fixture, role, position)
            if role == MODEL_ROLES[1] and position == 1:
                records = result.ordered_checkpoint_records
                result.ordered_checkpoint_records = (
                    replace(records[0], checkpoint_digest=first_digest),
                ) + records[1:]
            return result

        result, _ = _synthetic_matrix(producer)
        self.assertEqual(NOT_COMPUTABLE, result.status)
        self.assertEqual(2, result.failed_cell_ordinal_or_none)
        self.assertEqual((), result.ordered_checkpoint_records)

    def test_changed_fixture_stops_before_first_cell(self) -> None:
        changed = replace(FIXTURE, fixture_digest="0" * 64)
        with patch(f"{MODULE}.execute_four_node_cell") as cell_call:
            result = execute_four_node_matrix(MANIFEST, REGISTRATION, changed)
        self.assertEqual(NOT_COMPUTABLE, result.status)
        self.assertIsNone(result.failed_cell_ordinal_or_none)
        cell_call.assert_not_called()

    def test_cell_validator_failure_stops_at_current_ordinal(self) -> None:
        validations = 0

        def validate(_result):
            nonlocal validations
            validations += 1
            if validations == 3:
                raise FourNodeCellLifecycleError("closed")

        with (
            patch(f"{MODULE}.execute_four_node_cell", side_effect=_synthetic_cell) as cell_call,
            patch(f"{MODULE}.validate_four_node_cell_result", side_effect=validate),
        ):
            result = execute_four_node_matrix(MANIFEST, REGISTRATION, FIXTURE)
        self.assertEqual(NOT_COMPUTABLE, result.status)
        self.assertEqual(3, cell_call.call_count)
        self.assertEqual(3, result.failed_cell_ordinal_or_none)
        self.assertEqual((), result.ordered_cell_summaries)


if __name__ == "__main__":
    unittest.main()
