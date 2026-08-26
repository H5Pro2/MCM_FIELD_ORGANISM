from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import unittest
from unittest.mock import patch

from mcm_field_organism.four_node_cell_lifecycle import (
    _aligned_field,
    execute_four_node_cell,
)
from mcm_field_organism.four_node_exposure_fixture import (
    build_four_node_exposure_fixture,
)
from mcm_field_organism.four_node_fresh_factory import (
    build_four_node_role_fresh_bundle,
)
from mcm_field_organism.four_node_fresh_manifest import (
    load_four_node_fresh_manifest,
)
from mcm_field_organism.four_node_fresh_matrix_registration import (
    load_four_node_fresh_matrix_registration,
)
from mcm_field_organism.four_node_model_input_assembly import (
    FourNodeModelInputAssembly,
    assemble_four_node_model_input,
)
from mcm_field_organism.four_node_model_invocation import (
    COMPLETED,
    NOT_COMPUTABLE,
    FourNodeModelCarry,
    FourNodeModelInvocationError,
    four_node_model_field_digest,
    four_node_model_private_state_digest,
    invoke_four_node_model,
    rebind_four_node_model_carry_field,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = load_four_node_fresh_manifest(
    ROOT / "reports" / "s1rk_four_node_fresh_manifest.json"
)
REGISTRATION = load_four_node_fresh_matrix_registration(
    ROOT / "reports" / "s1sd_four_node_fresh_matrix_registration.json"
)
FIXTURE = build_four_node_exposure_fixture(REGISTRATION)
MODULE = "mcm_field_organism.four_node_cell_lifecycle"
F3_ROLES = {
    "A2_B3_LOCAL_LEAKY",
    "A2_B4_LINEAR_COUPLED",
    "A2_B5_F3_FULL",
    "A2_B6_CONST_V",
}


def _plan(position: int = 1):
    return FIXTURE.plans[position - 1]


def _first_carry(role: str = "A1_FAST_SH") -> FourNodeModelCarry:
    assembly = assemble_four_node_model_input(
        build_four_node_role_fresh_bundle(MANIFEST, role)
    )
    interval = _plan().events[0].interval_or_none
    if interval is None:
        raise AssertionError("first fixture event is not an interval")
    result = invoke_four_node_model(
        assembly,
        interval.distribution,
        interval.step_time,
        refinement=2 if role in F3_ROLES else None,
    )
    if result.next_carry_or_none is None:
        raise AssertionError(result.failure_codes)
    return result.next_carry_or_none


class FourNodeCellLifecycleTests(unittest.TestCase):
    def test_public_digest_roles_match_invocation_result(self) -> None:
        carry = _first_carry()
        self.assertEqual(
            four_node_model_field_digest(carry.field),
            four_node_model_field_digest(carry.field),
        )
        self.assertEqual(
            four_node_model_private_state_digest(carry.private_state_or_none),
            four_node_model_private_state_digest(carry.private_state_or_none),
        )

    def test_rebind_preserves_private_and_dependency_identities(self) -> None:
        carry = _first_carry("A2_B1_FIXED_ADAPTER")
        aligned = _aligned_field(carry.field, 10)
        rebound = rebind_four_node_model_carry_field(carry, aligned)
        self.assertIs(carry.private_state_or_none, rebound.private_state_or_none)
        self.assertEqual(
            (
                carry.model_role,
                carry.configuration_binding_or_none,
                carry.registered_edge_inventory_digest_or_none,
                carry.native_edge_inventory_digest_or_none,
                carry.registered_geometry_digest_or_none,
                carry.native_geometry_digest_or_none,
            ),
            (
                rebound.model_role,
                rebound.configuration_binding_or_none,
                rebound.registered_edge_inventory_digest_or_none,
                rebound.native_edge_inventory_digest_or_none,
                rebound.registered_geometry_digest_or_none,
                rebound.native_geometry_digest_or_none,
            ),
        )
        self.assertNotEqual(carry.carry_digest, rebound.carry_digest)

    def test_align_projection_is_time_free_and_constructor_valid(self) -> None:
        carry = _first_carry()
        aligned = _aligned_field(carry.field, 10)
        self.assertEqual(carry.field.layer.tick, aligned.layer.tick)
        self.assertEqual(_plan().events[0].interval_or_none.step_time.end_tick, 10)
        self.assertEqual("s1si.align.0.10", aligned.last_distribution.contacts[0].frame.snapshot_id)
        self.assertTrue(
            all(
                neuron.activation == neuron.afterimage == neuron.perception.receptor_contact == 0.0
                for neuron in aligned.layer.neurons
            )
        )

    def test_rebind_rejects_nonzero_align_projection(self) -> None:
        carry = _first_carry()
        aligned = _aligned_field(carry.field, 10)
        changed_neuron = replace(aligned.layer.neurons[0], activation=0.1)
        changed_layer = replace(
            aligned.layer,
            neurons=(changed_neuron,) + aligned.layer.neurons[1:],
        )
        changed_field = replace(aligned, layer=changed_layer)
        with self.assertRaises(FourNodeModelInvocationError):
            rebind_four_node_model_carry_field(carry, changed_field)

    def test_f_a_cell_completes_with_two_ordered_checkpoints(self) -> None:
        result = execute_four_node_cell(MANIFEST, REGISTRATION, FIXTURE, "A1_FAST_SH", 1)
        self.assertEqual(COMPLETED, result.status, result.failure_codes)
        self.assertEqual(2, len(result.ordered_checkpoint_records))
        self.assertEqual(
            ("ALIGNED_PRE_PROBE", "POST_PROBE_READOUT"),
            tuple(item.checkpoint_role for item in result.ordered_checkpoint_records),
        )
        self.assertEqual(40, result.final_carry_or_none.field.last_distribution.field_time.window_end_tick)

    def test_f3_cell_uses_refinement_two_for_every_interval(self) -> None:
        refinements: list[int | None] = []

        def wrapped(source, distribution, interval_input, *, refinement=None):
            refinements.append(refinement)
            return invoke_four_node_model(
                source, distribution, interval_input, refinement=refinement
            )

        with patch(f"{MODULE}.invoke_four_node_model", side_effect=wrapped):
            result = execute_four_node_cell(
                MANIFEST, REGISTRATION, FIXTURE, "A2_B3_LOCAL_LEAKY", 1
            )
        self.assertEqual(COMPLETED, result.status, result.failure_codes)
        self.assertEqual([2] * _plan().model_interval_count, refinements)

    def test_non_f3_cell_forbids_refinement_on_every_interval(self) -> None:
        refinements: list[int | None] = []

        def wrapped(source, distribution, interval_input, *, refinement=None):
            refinements.append(refinement)
            return invoke_four_node_model(
                source, distribution, interval_input, refinement=refinement
            )

        with patch(f"{MODULE}.invoke_four_node_model", side_effect=wrapped):
            result = execute_four_node_cell(
                MANIFEST, REGISTRATION, FIXTURE, "A1_FAST_SH", 1
            )
        self.assertEqual(COMPLETED, result.status, result.failure_codes)
        self.assertEqual([None] * _plan().model_interval_count, refinements)

    def test_align_and_checkpoints_do_not_add_model_calls(self) -> None:
        sources: list[object] = []

        def wrapped(source, distribution, interval_input, *, refinement=None):
            sources.append(source)
            return invoke_four_node_model(
                source, distribution, interval_input, refinement=refinement
            )

        with patch(f"{MODULE}.invoke_four_node_model", side_effect=wrapped):
            result = execute_four_node_cell(
                MANIFEST, REGISTRATION, FIXTURE, "A1_FAST_SH", 1
            )
        self.assertEqual(COMPLETED, result.status, result.failure_codes)
        self.assertEqual(_plan().model_interval_count, len(sources))
        self.assertIsInstance(sources[0], FourNodeModelInputAssembly)
        self.assertTrue(all(isinstance(item, FourNodeModelCarry) for item in sources[1:]))

    def test_checkpoint_records_expose_signed_four_node_vectors(self) -> None:
        result = execute_four_node_cell(MANIFEST, REGISTRATION, FIXTURE, "A1_FAST_SH", 1)
        for record in result.ordered_checkpoint_records:
            self.assertEqual(4, len(record.signed_receptor_contact_vector))
            self.assertEqual(4, len(record.signed_activation_vector))
            self.assertEqual(4, len(record.signed_afterimage_vector))
        self.assertEqual((0.0, 0.0, 0.0, 0.0), result.ordered_checkpoint_records[0].signed_activation_vector)

    def test_competition_checkpoints_precede_align_receipt(self) -> None:
        result = execute_four_node_cell(MANIFEST, REGISTRATION, FIXTURE, "A1_FAST_SH", 9)
        self.assertEqual(COMPLETED, result.status, result.failure_codes)
        records = result.ordered_checkpoint_records
        self.assertEqual(4, len(records))
        self.assertIsNone(records[0].align_receipt_digest_or_none)
        self.assertIsNone(records[1].align_receipt_digest_or_none)
        self.assertIsNotNone(records[2].align_receipt_digest_or_none)
        self.assertIsNotNone(records[3].align_receipt_digest_or_none)

    def test_failure_after_internal_checkpoint_publishes_no_partial_state(self) -> None:
        calls = 0

        def fail_fifth(source, distribution, interval_input, *, refinement=None):
            nonlocal calls
            calls += 1
            if calls == 5:
                raise RuntimeError("closed")
            return invoke_four_node_model(
                source, distribution, interval_input, refinement=refinement
            )

        with patch(f"{MODULE}.invoke_four_node_model", side_effect=fail_fifth):
            result = execute_four_node_cell(
                MANIFEST, REGISTRATION, FIXTURE, "A1_FAST_SH", 9
            )
        self.assertEqual(NOT_COMPUTABLE, result.status)
        self.assertIsNone(result.final_carry_or_none)
        self.assertEqual((), result.ordered_checkpoint_records)
        self.assertIsNone(result.terminal_event_chain_digest_or_none)

    def test_tampered_fixture_fails_before_model_invocation(self) -> None:
        tampered = replace(FIXTURE, fixture_digest="0" * 64)
        with patch(f"{MODULE}.invoke_four_node_model") as model_call:
            result = execute_four_node_cell(
                MANIFEST, REGISTRATION, tampered, "A1_FAST_SH", 1
            )
        self.assertEqual(NOT_COMPUTABLE, result.status)
        model_call.assert_not_called()

    def test_invalid_plan_position_fails_without_partial_state(self) -> None:
        result = execute_four_node_cell(
            MANIFEST, REGISTRATION, FIXTURE, "A1_FAST_SH", 0
        )
        self.assertEqual(NOT_COMPUTABLE, result.status)
        self.assertIsNone(result.cell_identity_or_none)
        self.assertIsNone(result.final_carry_or_none)
        self.assertEqual((), result.ordered_checkpoint_records)

    def test_complete_cell_result_is_deterministic(self) -> None:
        first = execute_four_node_cell(MANIFEST, REGISTRATION, FIXTURE, "A1_FAST_SH", 1)
        second = execute_four_node_cell(MANIFEST, REGISTRATION, FIXTURE, "A1_FAST_SH", 1)
        self.assertEqual(COMPLETED, first.status, first.failure_codes)
        self.assertEqual(first.cell_result_digest, second.cell_result_digest)
        self.assertEqual(
            first.terminal_event_chain_digest_or_none,
            second.terminal_event_chain_digest_or_none,
        )


if __name__ == "__main__":
    unittest.main()
