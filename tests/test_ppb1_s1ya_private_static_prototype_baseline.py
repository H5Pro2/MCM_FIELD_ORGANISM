from __future__ import annotations

from dataclasses import fields, replace
import inspect
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism._ppb1_s1xz_private_temporal_update_fixture import (
    build_s1xz_temporal_update_fixture,
)
import mcm_field_organism._ppb1_s1ya_private_static_prototype_baseline as s1ya
from mcm_field_organism.receptor_contract import ReceptorContactFrame
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS


def update_frame(carry: s1ya.S1YAFrozenBaselineCarry) -> ReceptorContactFrame:
    index = carry.received_update_count
    role = carry.expected_update_roles[index]
    scalar = carry.expected_update_scalars[index]
    config = carry.config
    history_id = carry.plan_id.rsplit(".", 1)[-1]
    start = carry.last_received_window_end_tick
    return ReceptorContactFrame(
        config.modality_id,
        config.geometry_id,
        f"receptor.s1ya.{config.modality_id}.{history_id}.{role}",
        f"clock.s1ya.{config.modality_id}.{history_id}",
        start,
        start + 1,
        config.carrier_ids,
        (scalar,) * len(config.carrier_ids),
    )


class PPB1S1YAPrivateStaticPrototypeBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = build_s1xz_temporal_update_fixture()

    def formation(self, modality_id: str, history_id: str):
        modality = next(item for item in self.fixture.modalities if item.modality_id == modality_id)
        plan = next(item for item in self.fixture.history_plans if item.modality_id == modality_id and item.history_id == history_id)
        return s1ya.form_s1ya_static_baseline(modality, plan)

    def consume(self, formation):
        carry = formation.carry
        receipts = []
        while carry.received_update_count < len(carry.expected_update_roles):
            role = carry.expected_update_roles[carry.received_update_count]
            result = s1ya.receive_s1ya_frozen_exposure(carry, update_frame(carry), role)
            carry = result.carry
            receipts.append(result.receipt)
        return carry, tuple(receipts)

    def test_all_ten_formations_are_deterministic_and_fixture_bound(self) -> None:
        for plan in self.fixture.history_plans:
            first = self.formation(plan.modality_id, plan.history_id)
            second = self.formation(plan.modality_id, plan.history_id)
            self.assertEqual(first, second)
            self.assertEqual(plan.plan_digest, first.freeze_receipt.plan_digest)

    def test_exact_total_is_thirty_six_formation_transitions(self) -> None:
        formations = [self.formation(plan.modality_id, plan.history_id) for plan in self.fixture.history_plans]
        self.assertEqual(36, sum(len(item.formation_transitions) for item in formations))

    def test_freeze_receipts_bind_stable_occupied_slots(self) -> None:
        for plan in self.fixture.history_plans:
            receipt = self.formation(plan.modality_id, plan.history_id).freeze_receipt
            expected = 2 if plan.history_id == "H4" else 1
            self.assertEqual(expected, receipt.occupied_slot_count)
            self.assertEqual(expected, receipt.stabilized_slot_count)
            self.assertTrue(receipt.frozen_after_formation)

    def test_exact_total_is_twenty_eight_frozen_update_receipts(self) -> None:
        receipts = []
        for plan in self.fixture.history_plans:
            _, current = self.consume(self.formation(plan.modality_id, plan.history_id))
            receipts.extend(current)
        self.assertEqual(28, len(receipts))

    def test_every_update_preserves_bank_state_and_identity(self) -> None:
        for plan in self.fixture.history_plans:
            formation = self.formation(plan.modality_id, plan.history_id)
            final, receipts = self.consume(formation)
            self.assertEqual(formation.carry.frozen_state, final.frozen_state)
            self.assertEqual(formation.carry.frozen_state_digest, final.frozen_state_digest)
            self.assertEqual(formation.carry.state_identity_digest, final.state_identity_digest)
            self.assertTrue(all(item.state_unchanged for item in receipts))

    def test_update_receipts_are_ordered_one_tick_and_zero_effect(self) -> None:
        final, receipts = self.consume(self.formation("auditory", "H4"))
        self.assertEqual(("opposite_c",) * 3, tuple(item.expected_role for item in receipts))
        self.assertEqual((1, 2, 3), tuple(item.update_ordinal for item in receipts))
        self.assertTrue(all(item.window_end_tick == item.window_start_tick + 1 for item in receipts))
        self.assertTrue(all((item.prototype_update_count, item.expiration_count, item.replacement_count) == (0, 0, 0) for item in receipts))
        self.assertEqual(3, final.received_update_count)

    def test_h4_baseline_retains_origin_and_conflict_b(self) -> None:
        formation = self.formation("auditory", "H4")
        final, _ = self.consume(formation)
        occupied = tuple(slot for slot in final.frozen_state.slots if slot.occupied)
        self.assertEqual((0.0, 0.625), tuple(slot.prototype_values[0] for slot in occupied))
        self.assertEqual((3, 3), tuple(slot.support_count for slot in occupied))

    def test_reordered_duplicate_and_wrong_value_updates_fail_closed(self) -> None:
        carry = self.formation("visual", "H2").carry
        with self.assertRaises(s1ya.S1YAStaticPrototypeBaselineError):
            s1ya.receive_s1ya_frozen_exposure(carry, update_frame(carry), "gradual_2")
        wrong = replace(update_frame(carry), values=(0.0,) * len(carry.config.carrier_ids))
        with self.assertRaises(s1ya.S1YAStaticPrototypeBaselineError):
            s1ya.receive_s1ya_frozen_exposure(carry, wrong, "gradual_1")
        final, _ = self.consume(self.formation("visual", "H2"))
        with self.assertRaises(s1ya.S1YAStaticPrototypeBaselineError):
            s1ya.receive_s1ya_frozen_exposure(final, update_frame(carry), "gradual_1")

    def test_receipt_and_carry_tampering_fail_closed(self) -> None:
        carry = self.formation("auditory", "H1").carry
        result = s1ya.receive_s1ya_frozen_exposure(carry, update_frame(carry), "gradual_2")
        with self.assertRaises(s1ya.S1YAStaticPrototypeBaselineError):
            replace(result.receipt, prototype_update_count=1)
        with self.assertRaises(s1ya.S1YAStaticPrototypeBaselineError):
            replace(result.carry, received_update_count=0)

    def test_five_types_are_frozen_slotted_and_role_complete(self) -> None:
        expected = {
            s1ya.S1YABaselineFreezeReceipt: 10,
            s1ya.S1YAFrozenBaselineCarry: 12,
            s1ya.S1YABaselineFormationResult: 4,
            s1ya.S1YAFrozenExposureReceipt: 19,
            s1ya.S1YAFrozenExposureResult: 2,
        }
        for kind, count in expected.items():
            self.assertEqual(count, len(fields(kind)))
            self.assertTrue(kind.__dataclass_params__.frozen)
            self.assertEqual(count, len(kind.__slots__))

    def test_source_has_no_candidate_probe_runner_field_or_io_path(self) -> None:
        source = inspect.getsource(s1ya)
        for forbidden in (
            "probe_s1wu_perceptual_state",
            "temporal_update_runner",
            "candidate_state",
            "SharedMCMField",
            "open(",
            "write_text(",
            "production",
        ):
            self.assertNotIn(forbidden, source)

    def test_module_is_private_and_unexported(self) -> None:
        self.assertNotIn("S1YAFrozenBaselineCarry", mcm_field_organism.__all__)
        self.assertFalse(hasattr(current_api, "form_s1ya_static_baseline"))
        self.assertNotIn("form_s1ya_static_baseline", ROOT_LAZY_EXPORTS)


if __name__ == "__main__":
    unittest.main()
