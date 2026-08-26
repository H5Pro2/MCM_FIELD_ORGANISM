from __future__ import annotations

from dataclasses import fields, replace
import inspect
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
import mcm_field_organism._ppb1_s1wq_perceptual_state_lifecycle as s1wq
from mcm_field_organism._ppb1_reference import (
    PPB1BankConfig,
    PPB1ReferenceError,
    initial_ppb1_bank_state,
)
from mcm_field_organism.receptor_contract import ReceptorContactFrame
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot


ROOT = Path(__file__).resolve().parents[1]
CARRIERS = ("c.0", "c.1")
EXPECTED_FORMATION_DIGEST = (
    "b8fb740334314aa5ff2419accc24d2ab9fa73d60846a7298828a4e6e6b092371"
)


def config(*, capacity=2, stable_after=3, expire_after=4):
    return PPB1BankConfig(
        "ppb1.s1wq.auditory",
        "auditory",
        "geometry.s1wq.auditory",
        CARRIERS,
        capacity,
        0.25,
        0.5,
        stable_after,
        expire_after,
    )


def frame(values, *, step, clock="clock.s1wq.auditory"):
    return ReceptorContactFrame(
        "auditory",
        "geometry.s1wq.auditory",
        f"receptor.s1wq.{step}",
        clock,
        step - 1,
        step,
        CARRIERS,
        values,
    )


def advance(cfg, state, values, step):
    return s1wq.advance_s1wq_perceptual_state(
        cfg,
        state,
        frame(values, step=step),
    )


class PPB1S1WQPerceptualStateLifecycleTests(unittest.TestCase):
    def test_first_input_forms_one_perceptual_state(self) -> None:
        cfg = config()
        result = advance(cfg, initial_ppb1_bank_state(cfg), (0.1, 0.1), 1)
        transition = result.transition
        self.assertEqual("PERCEPTUAL_STATE_FORMED", transition.transition_role)
        self.assertEqual("CREATED", transition.reference_event)
        self.assertEqual(transition.selected_slot_id, transition.formed_slot_id)
        self.assertIsNone(transition.updated_slot_id)
        self.assertEqual((), transition.discarded_slot_ids)
        self.assertEqual(EXPECTED_FORMATION_DIGEST, transition.record_digest)

    def test_matching_input_is_valid_state_continuation_and_update(self) -> None:
        cfg = config()
        first = advance(cfg, initial_ppb1_bank_state(cfg), (0.0, 0.0), 1)
        second = advance(cfg, first.poststate, (0.2, 0.2), 2)
        self.assertEqual(
            "VALID_STATE_CONTINUATION_UPDATED",
            second.transition.transition_role,
        )
        self.assertEqual(
            second.transition.selected_slot_id,
            second.transition.updated_slot_id,
        )
        self.assertEqual((0.1, 0.1), second.reference_readout.prototype_values)

    def test_threshold_support_transition_stabilizes_once(self) -> None:
        cfg = config(stable_after=3)
        first = advance(cfg, initial_ppb1_bank_state(cfg), (0.0, 0.0), 1)
        second = advance(cfg, first.poststate, (0.0, 0.0), 2)
        third = advance(cfg, second.poststate, (0.0, 0.0), 3)
        self.assertEqual(
            "PERCEPTUAL_STATE_STABILIZED",
            third.transition.transition_role,
        )
        self.assertEqual(
            third.transition.selected_slot_id,
            third.transition.stabilized_slot_id,
        )
        self.assertTrue(third.reference_readout.stabilized)

    def test_stabilized_state_updates_without_unbounded_support(self) -> None:
        cfg = config(stable_after=2)
        first = advance(cfg, initial_ppb1_bank_state(cfg), (0.0, 0.0), 1)
        second = advance(cfg, first.poststate, (0.0, 0.0), 2)
        third = advance(cfg, second.poststate, (0.1, 0.1), 3)
        self.assertEqual(
            "STABILIZED_STATE_UPDATED",
            third.transition.transition_role,
        )
        self.assertEqual(2, third.reference_readout.support_count)
        self.assertIsNone(third.transition.stabilized_slot_id)

    def test_due_state_is_discarded_and_slot_identity_is_reused(self) -> None:
        cfg = config(capacity=2, expire_after=2)
        first = advance(cfg, initial_ppb1_bank_state(cfg), (-0.8, -0.8), 1)
        second = advance(cfg, first.poststate, (0.0, 0.0), 2)
        third = advance(cfg, second.poststate, (0.8, 0.8), 3)
        self.assertEqual(
            "PERCEPTUAL_STATE_FORMED",
            third.transition.transition_role,
        )
        self.assertIn(
            "ppb1.s1wq.auditory.slot.000",
            third.transition.discarded_slot_ids,
        )
        self.assertEqual(
            "ppb1.s1wq.auditory.slot.000",
            third.transition.formed_slot_id,
        )

    def test_full_capacity_replacement_is_explicit_discard_and_reformation(self) -> None:
        cfg = config(capacity=1, expire_after=10)
        first = advance(cfg, initial_ppb1_bank_state(cfg), (-0.8, -0.8), 1)
        second = advance(cfg, first.poststate, (0.8, 0.8), 2)
        self.assertEqual(
            "CAPACITY_STATE_DISCARDED_AND_REFORMED",
            second.transition.transition_role,
        )
        self.assertEqual(
            (second.transition.selected_slot_id,),
            second.transition.discarded_slot_ids,
        )

    def test_bank_config_and_slot_identity_remain_invariant(self) -> None:
        cfg = config()
        state = initial_ppb1_bank_state(cfg)
        identity = None
        for step, values in enumerate(
            ((-0.8, -0.8), (0.8, 0.8), (-0.7, -0.7)),
            start=1,
        ):
            result = advance(cfg, state, values, step)
            identity = identity or result.transition.state_identity_digest
            self.assertEqual(identity, result.transition.state_identity_digest)
            self.assertEqual(cfg.bank_id, result.poststate.bank_id)
            self.assertEqual(cfg.digest(), result.poststate.config_digest)
            state = result.poststate

    def test_atomic_transition_binds_pre_input_post_and_readout(self) -> None:
        cfg = config()
        prestate = initial_ppb1_bank_state(cfg)
        result = advance(cfg, prestate, (0.1, 0.1), 1)
        transition = result.transition
        self.assertEqual(prestate.digest(), transition.prestate_digest)
        self.assertEqual(result.poststate.digest(), transition.poststate_digest)
        self.assertEqual(
            result.reference_readout.digest(),
            transition.reference_readout_digest,
        )
        self.assertEqual(
            result.reference_readout.input_digest,
            transition.input_digest,
        )

    def test_exactly_one_reference_call_and_all_effect_counts_are_bounded(self) -> None:
        cfg = config()
        result = advance(cfg, initial_ppb1_bank_state(cfg), (0.0, 0.0), 1)
        transition = result.transition
        self.assertEqual(
            (1, 1),
            (
                transition.accepted_step_delta,
                transition.reference_advance_call_count,
            ),
        )
        self.assertEqual(
            (0, 0, 0, 0),
            (
                transition.partial_commit_count,
                transition.retry_count,
                transition.filesystem_operation_count,
                transition.field_feedback_count,
            ),
        )

    def test_invalid_input_fails_without_mutating_prestate_or_retry(self) -> None:
        cfg = config()
        prestate = initial_ppb1_bank_state(cfg)
        bad = frame((0.0, 0.0), step=1, clock="clock.other")
        first = advance(cfg, prestate, (0.0, 0.0), 1)
        before = first.poststate.digest()
        with self.assertRaises(PPB1ReferenceError):
            s1wq.advance_s1wq_perceptual_state(cfg, first.poststate, bad)
        self.assertEqual(before, first.poststate.digest())

    def test_identical_prestate_and_input_are_deterministic(self) -> None:
        cfg = config()
        state = initial_ppb1_bank_state(cfg)
        first = advance(cfg, state, (0.2, 0.2), 1)
        second = advance(cfg, state, (0.2, 0.2), 1)
        self.assertEqual(first, second)

    def test_transition_tampering_and_production_entry_fail_closed(self) -> None:
        cfg = config()
        result = advance(cfg, initial_ppb1_bank_state(cfg), (0.0, 0.0), 1)
        with self.assertRaises(s1wq.S1WQLifecycleError):
            replace(result.transition, retry_count=1)
        with self.assertRaises(s1wq.S1WQLifecycleError) as raised:
            s1wq.execute_s1wq_production_once()
        self.assertEqual(
            s1wq.S1WQ_PRODUCTION_EXECUTION_BLOCKED,
            raised.exception.code,
        )

    def test_module_reuses_reference_kernel_without_field_or_runtime_access(self) -> None:
        source = inspect.getsource(s1wq)
        self.assertEqual(
            s1wq.S1WQ_REFERENCE_SOURCE_DIGEST,
            __import__("hashlib").sha256(
                (ROOT / "mcm_field_organism" / "_ppb1_reference.py").read_bytes()
            ).hexdigest(),
        )
        for forbidden in (
            "import os",
            "from pathlib",
            "from tempfile",
            "SharedMCMField",
            "current_api",
            "open(",
            "write_text(",
            "write_bytes(",
            "semantic_label",
        ):
            self.assertNotIn(forbidden, source)

    def test_s1wq_remains_private_and_snapshot_neutral(self) -> None:
        names = {
            "S1WQPerceptualTransitionRecord",
            "S1WQPerceptualStateStepResult",
            "advance_s1wq_perceptual_state",
        }
        self.assertTrue(names.isdisjoint(mcm_field_organism.__all__))
        self.assertTrue(names.isdisjoint(ROOT_LAZY_EXPORTS))
        self.assertTrue(names.isdisjoint(current_api.__all__))
        self.assertTrue(
            names.isdisjoint({item.name for item in fields(SharedMCMFieldSnapshot)})
        )


if __name__ == "__main__":
    unittest.main()
