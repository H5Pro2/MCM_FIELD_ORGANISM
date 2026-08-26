from __future__ import annotations

from dataclasses import fields
import math
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism._ppb1_reference import (
    PPB1_CLOCK_ORDER,
    PPB1_INVALID_CONFIG,
    PPB1_INVALID_INPUT,
    PPB1_INVALID_STATE,
    PPB1BankConfig,
    PPB1BankState,
    PPB1PrototypeSlot,
    PPB1ReferenceError,
    advance_ppb1_bank,
    initial_ppb1_bank_state,
    normalized_mean_l1_distance,
)
from mcm_field_organism.receptor_contract import ReceptorContactFrame
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot


ROOT = Path(__file__).resolve().parents[1]
CARRIERS = ("c.0", "c.1", "c.2", "c.3")


def config(
    modality: str = "auditory",
    *,
    capacity: int = 2,
    expire_after_steps: int = 4,
) -> PPB1BankConfig:
    return PPB1BankConfig(
        f"ppb1.{modality}",
        modality,
        f"geometry.{modality}",
        CARRIERS,
        capacity,
        0.25,
        0.5,
        3,
        expire_after_steps,
    )


def frame(
    values: tuple[float, ...],
    *,
    modality: str = "auditory",
    geometry: str | None = None,
    carriers: tuple[str, ...] = CARRIERS,
    snapshot: str = "receptor.1",
    clock: str | None = None,
    start: int = 0,
    end: int = 1,
) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality,
        geometry or f"geometry.{modality}",
        snapshot,
        clock or f"clock.{modality}",
        start,
        end,
        carriers,
        values,
    )


def corrupt(instance: object, **changes: object) -> object:
    clone = object.__new__(type(instance))
    for item in fields(instance):
        object.__setattr__(clone, item.name, changes.get(item.name, getattr(instance, item.name)))
    return clone


def advance(
    cfg: PPB1BankConfig,
    state: PPB1BankState,
    values: tuple[float, ...],
    *,
    step: int,
):
    return advance_ppb1_bank(cfg, state, frame(values, start=step - 1, end=step))


class PPB1RegisteredThirtyPathTests(unittest.TestCase):
    def test_v01_rejects_empty_or_duplicate_carriers(self) -> None:
        with self.assertRaises(PPB1ReferenceError) as caught:
            PPB1BankConfig("ppb1.a", "auditory", "g.a", (), 2, 0.25, 0.5, 3, 4)
        self.assertEqual(PPB1_INVALID_CONFIG, caught.exception.code)
        with self.assertRaises(PPB1ReferenceError):
            PPB1BankConfig(
                "ppb1.a", "auditory", "g.a", ("c", "c"), 2, 0.25, 0.5, 3, 4
            )

    def test_v02_rejects_wrong_modality_without_touching_other_bank(self) -> None:
        cfg = config("auditory")
        state = initial_ppb1_bank_state(cfg)
        before = state.digest()
        with self.assertRaises(PPB1ReferenceError) as caught:
            advance_ppb1_bank(
                cfg,
                state,
                frame((0.0,) * 4, modality="visual"),
            )
        self.assertEqual(PPB1_INVALID_INPUT, caught.exception.code)
        self.assertEqual(before, state.digest())

    def test_v03_rejects_wrong_geometry_without_step_progress(self) -> None:
        cfg = config()
        state = initial_ppb1_bank_state(cfg)
        with self.assertRaises(PPB1ReferenceError):
            advance_ppb1_bank(cfg, state, frame((0.0,) * 4, geometry="geometry.wrong"))
        self.assertEqual(0, state.accepted_step_count)

    def test_v04_rejects_carrier_order_mismatch(self) -> None:
        cfg = config()
        state = initial_ppb1_bank_state(cfg)
        with self.assertRaises(PPB1ReferenceError):
            advance_ppb1_bank(
                cfg,
                state,
                frame((0.0,) * 4, carriers=tuple(reversed(CARRIERS))),
            )

    def test_v05_rejects_nonfinite_or_out_of_range_without_partial_commit(self) -> None:
        cfg = config()
        state = initial_ppb1_bank_state(cfg)
        valid = frame((0.0,) * 4)
        invalid = corrupt(valid, values=(0.0, math.nan, 0.0, 0.0))
        with self.assertRaises(PPB1ReferenceError):
            advance_ppb1_bank(cfg, state, invalid)  # type: ignore[arg-type]
        self.assertEqual(initial_ppb1_bank_state(cfg), state)

    def test_v06_rejects_nonadvancing_source_window(self) -> None:
        cfg = config()
        first = advance_ppb1_bank(cfg, initial_ppb1_bank_state(cfg), frame((0.0,) * 4))
        with self.assertRaises(PPB1ReferenceError) as caught:
            advance_ppb1_bank(cfg, first.poststate, frame((0.0,) * 4, start=0, end=1))
        self.assertEqual(PPB1_CLOCK_ORDER, caught.exception.code)
        self.assertEqual(1, first.poststate.accepted_step_count)

    def test_v07_rejects_bad_slot_count_or_duplicate_slot_id(self) -> None:
        cfg = config()
        state = initial_ppb1_bank_state(cfg)
        bad_count = corrupt(state, slots=state.slots[:1])
        with self.assertRaises(PPB1ReferenceError) as caught:
            advance_ppb1_bank(cfg, bad_count, frame((0.0,) * 4))  # type: ignore[arg-type]
        self.assertEqual(PPB1_INVALID_STATE, caught.exception.code)
        duplicate = corrupt(state, slots=(state.slots[0], state.slots[0]))
        with self.assertRaises(PPB1ReferenceError):
            advance_ppb1_bank(cfg, duplicate, frame((0.0,) * 4))  # type: ignore[arg-type]

    def test_v08_rejects_occupied_slot_without_valid_prototype(self) -> None:
        cfg = config()
        state = initial_ppb1_bank_state(cfg)
        bad_slot = corrupt(
            state.slots[0],
            occupied=True,
            prototype_values=(),
            support_count=1,
            last_selected_step=1,
        )
        bad_state = corrupt(
            state,
            accepted_step_count=1,
            source_clock_id="clock.auditory",
            last_source_window_end_tick=1,
            slots=(bad_slot, state.slots[1]),
        )
        with self.assertRaises(PPB1ReferenceError) as caught:
            advance_ppb1_bank(cfg, bad_state, frame((0.0,) * 4, start=1, end=2))  # type: ignore[arg-type]
        self.assertEqual(PPB1_INVALID_STATE, caught.exception.code)

    def test_v09_identical_tuples_have_zero_distance(self) -> None:
        values = (-1.0, -0.25, 0.5, 1.0)
        self.assertEqual(0.0, normalized_mean_l1_distance(values, values))

    def test_v10_distance_is_symmetric(self) -> None:
        left = (-1.0, 0.0, 0.5, 1.0)
        right = (-0.5, 0.25, 0.0, 0.75)
        self.assertEqual(
            normalized_mean_l1_distance(left, right),
            normalized_mean_l1_distance(right, left),
        )

    def test_v11_distance_is_dimension_normalized(self) -> None:
        self.assertEqual(
            normalized_mean_l1_distance((0.0, 0.0), (0.5, 0.5)),
            normalized_mean_l1_distance((0.0,) * 4, (0.5,) * 4),
        )

    def test_v12_distance_at_threshold_matches(self) -> None:
        cfg = config()
        created = advance(cfg, initial_ppb1_bank_state(cfg), (0.0,) * 4, step=1)
        matched = advance(cfg, created.poststate, (0.25,) * 4, step=2)
        self.assertEqual("MATCHED", matched.readout.event)
        self.assertEqual(0.25, matched.readout.match_distance)

    def test_v13_distance_above_threshold_does_not_match(self) -> None:
        cfg = config()
        created = advance(cfg, initial_ppb1_bank_state(cfg), (0.0,) * 4, step=1)
        second = advance(cfg, created.poststate, (0.2501,) * 4, step=2)
        self.assertEqual("CREATED", second.readout.event)

    def test_v14_exact_distance_tie_uses_smallest_slot_id(self) -> None:
        cfg = config()
        state = initial_ppb1_bank_state(cfg)
        first = advance(cfg, state, (-0.2,) * 4, step=1)
        second = advance(cfg, first.poststate, (0.2,) * 4, step=2)
        tied = advance(cfg, second.poststate, (0.0,) * 4, step=3)
        self.assertEqual("ppb1.auditory.slot.000", tied.readout.slot_id)

    def test_v15_first_input_creates_smallest_slot(self) -> None:
        cfg = config()
        result = advance(cfg, initial_ppb1_bank_state(cfg), (0.1,) * 4, step=1)
        self.assertEqual(("CREATED", "ppb1.auditory.slot.000"), (result.readout.event, result.readout.slot_id))

    def test_v16_matching_input_updates_convexly(self) -> None:
        cfg = config()
        first = advance(cfg, initial_ppb1_bank_state(cfg), (0.0,) * 4, step=1)
        second = advance(cfg, first.poststate, (0.2,) * 4, step=2)
        self.assertEqual((0.1,) * 4, second.readout.prototype_values)
        self.assertEqual(2, second.readout.support_count)

    def test_v17_third_support_stabilizes_slot(self) -> None:
        cfg = config()
        state = initial_ppb1_bank_state(cfg)
        for step in range(1, 4):
            result = advance(cfg, state, (0.0,) * 4, step=step)
            state = result.poststate
        self.assertTrue(result.readout.stabilized)
        self.assertEqual(3, result.readout.support_count)

    def test_v18_support_count_saturates(self) -> None:
        cfg = config()
        state = initial_ppb1_bank_state(cfg)
        for step in range(1, 7):
            result = advance(cfg, state, (0.0,) * 4, step=step)
            state = result.poststate
        self.assertEqual(3, result.readout.support_count)

    def test_v19_unselected_slot_is_bit_equal(self) -> None:
        cfg = config()
        first = advance(cfg, initial_ppb1_bank_state(cfg), (-0.8,) * 4, step=1)
        second = advance(cfg, first.poststate, (0.8,) * 4, step=2)
        untouched = second.poststate.slots[1]
        third = advance(cfg, second.poststate, (-0.75,) * 4, step=3)
        self.assertEqual(untouched, third.poststate.slots[1])

    def test_v20_two_unmatched_patterns_use_two_slots(self) -> None:
        cfg = config()
        first = advance(cfg, initial_ppb1_bank_state(cfg), (-0.8,) * 4, step=1)
        second = advance(cfg, first.poststate, (0.8,) * 4, step=2)
        self.assertEqual((True, True), tuple(slot.occupied for slot in second.poststate.slots))
        self.assertEqual("CREATED", second.readout.event)

    def test_v21_third_unmatched_pattern_replaces_lru(self) -> None:
        cfg = config()
        first = advance(cfg, initial_ppb1_bank_state(cfg), (-0.8,) * 4, step=1)
        second = advance(cfg, first.poststate, (0.8,) * 4, step=2)
        third = advance(cfg, second.poststate, (0.0,) * 4, step=3)
        self.assertEqual(("REPLACED", "ppb1.auditory.slot.000"), (third.readout.event, third.readout.slot_id))

    def test_v22_lru_tie_replaces_smallest_slot_id(self) -> None:
        cfg = config()
        slots = (
            PPB1PrototypeSlot("ppb1.auditory.slot.000", True, (-0.8,) * 4, 1, 1),
            PPB1PrototypeSlot("ppb1.auditory.slot.001", True, (0.8,) * 4, 1, 1),
        )
        state = PPB1BankState(cfg.bank_id, cfg.digest(), 1, "clock.auditory", 1, slots)
        result = advance(cfg, state, (0.0,) * 4, step=2)
        self.assertEqual("ppb1.auditory.slot.000", result.readout.slot_id)

    def test_v23_due_slot_is_freed_before_matching(self) -> None:
        cfg = config(expire_after_steps=2)
        first = advance(cfg, initial_ppb1_bank_state(cfg), (-0.8,) * 4, step=1)
        second = advance(cfg, first.poststate, (0.8,) * 4, step=2)
        third = advance(cfg, second.poststate, (0.75,) * 4, step=3)
        self.assertFalse(third.poststate.slots[0].occupied)

    def test_v24_due_slot_reuse_is_created_without_old_residue(self) -> None:
        cfg = config(capacity=2, expire_after_steps=2)
        first = advance(cfg, initial_ppb1_bank_state(cfg), (-0.8,) * 4, step=1)
        second = advance(cfg, first.poststate, (0.0,) * 4, step=2)
        third = advance(cfg, second.poststate, (0.8,) * 4, step=3)
        self.assertEqual("CREATED", third.readout.event)
        self.assertEqual((0.8,) * 4, third.readout.prototype_values)
        self.assertEqual(1, third.readout.support_count)

    def test_v25_audio_steps_do_not_age_visual_bank(self) -> None:
        audio_cfg = config("auditory")
        visual_cfg = config("visual")
        audio_state = initial_ppb1_bank_state(audio_cfg)
        visual_state = advance_ppb1_bank(
            visual_cfg,
            initial_ppb1_bank_state(visual_cfg),
            frame((0.4,) * 4, modality="visual"),
        ).poststate
        visual_before = visual_state.digest()
        for step in range(1, 5):
            audio_state = advance(audio_cfg, audio_state, (0.0,) * 4, step=step).poststate
        self.assertEqual(visual_before, visual_state.digest())

    def test_v26_identical_inputs_produce_bit_equal_outputs(self) -> None:
        cfg = config()
        state = initial_ppb1_bank_state(cfg)
        first = advance(cfg, state, (0.2,) * 4, step=1)
        second = advance(cfg, state, (0.2,) * 4, step=1)
        self.assertEqual(first.poststate.digest(), second.poststate.digest())
        self.assertEqual(first.readout.digest(), second.readout.digest())

    def test_v27_slot_delivery_order_is_canonical(self) -> None:
        cfg = config()
        state = initial_ppb1_bank_state(cfg)
        reversed_state = PPB1BankState(
            state.bank_id,
            state.config_digest,
            state.accepted_step_count,
            state.source_clock_id,
            state.last_source_window_end_tick,
            tuple(reversed(state.slots)),
        )
        self.assertEqual(state, reversed_state)
        self.assertEqual(
            advance(cfg, state, (0.0,) * 4, step=1),
            advance(cfg, reversed_state, (0.0,) * 4, step=1),
        )

    def test_v28_snapshot_and_ticks_do_not_enter_prototype_values(self) -> None:
        cfg = config()
        left = advance_ppb1_bank(
            cfg,
            initial_ppb1_bank_state(cfg),
            frame((0.2,) * 4, snapshot="receptor.left", start=0, end=1),
        )
        right = advance_ppb1_bank(
            cfg,
            initial_ppb1_bank_state(cfg),
            frame((0.2,) * 4, snapshot="receptor.right", start=10, end=20),
        )
        self.assertEqual(left.readout.prototype_values, right.readout.prototype_values)

    def test_v29_ppb_off_leaves_active_contract_bit_equal(self) -> None:
        before = current_api.active_field_state_contract_digest()
        cfg = config()
        advance(cfg, initial_ppb1_bank_state(cfg), (0.0,) * 4, step=1)
        self.assertEqual(before, current_api.active_field_state_contract_digest())
        source = (ROOT / "mcm_field_organism" / "_ppb1_reference.py").read_text(encoding="utf-8")
        self.assertNotIn("shared_mcm_field", source)
        self.assertNotIn("neutral_local_field_substrate", source)

    def test_v30_ppb_roles_are_absent_from_public_and_snapshot_surfaces(self) -> None:
        names = set(getattr(current_api, "__all__", ())) | set(ROOT_LAZY_EXPORTS)
        names |= {item.name for item in fields(SharedMCMFieldSnapshot)}
        self.assertFalse(any("ppb1" in name.lower() for name in names))
        self.assertFalse(
            any("ppb1" in name.lower() for name in mcm_field_organism.__all__)
        )


if __name__ == "__main__":
    unittest.main()
