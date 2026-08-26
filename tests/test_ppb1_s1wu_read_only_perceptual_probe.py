from __future__ import annotations

from dataclasses import fields, replace
import inspect
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
import mcm_field_organism._ppb1_s1wu_read_only_perceptual_probe as s1wu
from mcm_field_organism._ppb1_reference import (
    PPB1BankConfig,
    PPB1BankState,
    PPB1PrototypeSlot,
    advance_ppb1_bank,
    initial_ppb1_bank_state,
)
from mcm_field_organism.receptor_contract import ReceptorContactFrame
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot


CARRIERS = ("c.0", "c.1")
EXPECTED_EXACT_FINDING_DIGEST = (
    "02929eab57e8ce7ec0ea6a66962138e93a75fcfec62f036f3f03a23d86ad02e4"
)


def config(*, capacity=2, stable_after=2, threshold=0.25):
    return PPB1BankConfig(
        "ppb1.s1wu.auditory",
        "auditory",
        "geometry.s1wu.auditory",
        CARRIERS,
        capacity,
        threshold,
        0.5,
        stable_after,
        10,
    )


def frame(values, *, start, end, clock="clock.s1wu.auditory"):
    return ReceptorContactFrame(
        "auditory",
        "geometry.s1wu.auditory",
        f"receptor.s1wu.{start}.{end}",
        clock,
        start,
        end,
        CARRIERS,
        values,
    )


def stabilized_state(cfg):
    first = advance_ppb1_bank(
        cfg,
        initial_ppb1_bank_state(cfg),
        frame((0.0, 0.0), start=0, end=1),
    )
    return advance_ppb1_bank(
        cfg,
        first.poststate,
        frame((0.0, 0.0), start=1, end=2),
    ).poststate


class PPB1S1WUReadOnlyPerceptualProbeTests(unittest.TestCase):
    def test_exact_later_probe_recognizes_stabilized_state(self) -> None:
        cfg = config()
        state = stabilized_state(cfg)
        finding = s1wu.probe_s1wu_perceptual_state(
            cfg,
            state,
            frame((0.0, 0.0), start=2, end=3),
            "probe.s1wu.exact",
        )
        self.assertTrue(finding.recognized)
        self.assertEqual(1, finding.eligible_slot_count)
        self.assertEqual("ppb1.s1wu.auditory.slot.000", finding.selected_slot_id)
        self.assertEqual(0.0, finding.match_distance)
        self.assertEqual(state.digest(), finding.observed_bank_state_digest)
        self.assertEqual(EXPECTED_EXACT_FINDING_DIGEST, finding.finding_digest)

    def test_nearest_distance_is_returned_when_not_recognized(self) -> None:
        cfg = config(threshold=0.1)
        state = stabilized_state(cfg)
        finding = s1wu.probe_s1wu_perceptual_state(
            cfg,
            state,
            frame((0.5, 0.5), start=2, end=3),
            "probe.s1wu.nonmatch",
        )
        self.assertFalse(finding.recognized)
        self.assertEqual("ppb1.s1wu.auditory.slot.000", finding.selected_slot_id)
        self.assertEqual(0.5, finding.match_distance)

    def test_unstabilized_and_free_slots_are_not_eligible(self) -> None:
        cfg = config(stable_after=2)
        state = advance_ppb1_bank(
            cfg,
            initial_ppb1_bank_state(cfg),
            frame((0.0, 0.0), start=0, end=1),
        ).poststate
        finding = s1wu.probe_s1wu_perceptual_state(
            cfg,
            state,
            frame((0.0, 0.0), start=1, end=2),
            "probe.s1wu.unstable",
        )
        self.assertEqual(0, finding.eligible_slot_count)
        self.assertFalse(finding.recognized)
        self.assertIsNone(finding.selected_slot_id)
        self.assertIsNone(finding.match_distance)
        self.assertIsNone(finding.selected_prototype_digest)

    def test_distance_at_threshold_recognizes_and_above_does_not(self) -> None:
        cfg = config(threshold=0.25)
        state = stabilized_state(cfg)
        at = s1wu.probe_s1wu_perceptual_state(
            cfg,
            state,
            frame((0.25, 0.25), start=2, end=3),
            "probe.s1wu.at-threshold",
        )
        above = s1wu.probe_s1wu_perceptual_state(
            cfg,
            state,
            frame((0.2501, 0.2501), start=2, end=3),
            "probe.s1wu.above-threshold",
        )
        self.assertTrue(at.recognized)
        self.assertFalse(above.recognized)

    def test_equal_distances_select_lexicographically_first_slot(self) -> None:
        cfg = config(capacity=2, threshold=1.0)
        state = PPB1BankState(
            cfg.bank_id,
            cfg.digest(),
            2,
            "clock.s1wu.auditory",
            2,
            (
                PPB1PrototypeSlot(
                    "ppb1.s1wu.auditory.slot.000", True, (-0.5, -0.5), 2, 1
                ),
                PPB1PrototypeSlot(
                    "ppb1.s1wu.auditory.slot.001", True, (0.5, 0.5), 2, 2
                ),
            ),
        )
        finding = s1wu.probe_s1wu_perceptual_state(
            cfg,
            state,
            frame((0.0, 0.0), start=2, end=3),
            "probe.s1wu.tie",
        )
        self.assertEqual(2, finding.eligible_slot_count)
        self.assertEqual("ppb1.s1wu.auditory.slot.000", finding.selected_slot_id)

    def test_probe_is_deterministic_and_does_not_change_state(self) -> None:
        cfg = config()
        state = stabilized_state(cfg)
        before = state.digest()
        probe = frame((0.1, 0.1), start=2, end=3)
        first = s1wu.probe_s1wu_perceptual_state(
            cfg, state, probe, "probe.s1wu.repeat"
        )
        second = s1wu.probe_s1wu_perceptual_state(
            cfg, state, probe, "probe.s1wu.repeat"
        )
        self.assertEqual(first, second)
        self.assertEqual(before, state.digest())
        self.assertEqual(2, state.accepted_step_count)
        self.assertEqual(2, state.slots[0].support_count)
        self.assertEqual(2, state.slots[0].last_selected_step)

    def test_wrong_or_nonlater_clock_fails_closed_without_state_change(self) -> None:
        cfg = config()
        state = stabilized_state(cfg)
        before = state.digest()
        invalid = (
            frame((0.0, 0.0), start=2, end=3, clock="clock.other"),
            frame((0.0, 0.0), start=1, end=2),
        )
        for index, probe in enumerate(invalid):
            with self.subTest(index=index):
                with self.assertRaises(s1wu.S1WUProbeError):
                    s1wu.probe_s1wu_perceptual_state(
                        cfg, state, probe, f"probe.s1wu.invalid.{index}"
                    )
                self.assertEqual(before, state.digest())

    def test_frame_and_state_anatomy_mismatch_fail_closed(self) -> None:
        cfg = config()
        state = stabilized_state(cfg)
        wrong_frame = replace(
            frame((0.0, 0.0), start=2, end=3),
            geometry_id="geometry.other",
        )
        with self.assertRaises(s1wu.S1WUProbeError):
            s1wu.probe_s1wu_perceptual_state(
                cfg, state, wrong_frame, "probe.s1wu.bad-frame"
            )
        wrong_state = replace(state, config_digest="0" * 64)
        with self.assertRaises(s1wu.S1WUProbeError):
            s1wu.probe_s1wu_perceptual_state(
                cfg,
                wrong_state,
                frame((0.0, 0.0), start=2, end=3),
                "probe.s1wu.bad-state",
            )

    def test_finding_is_digest_bound_and_tampering_fails_closed(self) -> None:
        cfg = config()
        finding = s1wu.probe_s1wu_perceptual_state(
            cfg,
            stabilized_state(cfg),
            frame((0.0, 0.0), start=2, end=3),
            "probe.s1wu.digest",
        )
        self.assertEqual(
            finding.finding_digest,
            s1wu._digest(finding.payload_without_digest()),
        )
        with self.assertRaises(s1wu.S1WUProbeError):
            replace(finding, recognized=False)
        with self.assertRaises(s1wu.S1WUProbeError):
            replace(finding, match_distance=float("nan"))

    def test_finding_has_no_poststate_or_effect_roles(self) -> None:
        names = {item.name for item in fields(s1wu.S1WUReadOnlyPerceptualFinding)}
        self.assertTrue(
            names.isdisjoint(
                {
                    "poststate",
                    "prototype_values",
                    "semantic_label",
                    "field_feedback",
                    "filesystem_operation_count",
                }
            )
        )

    def test_module_has_no_advance_file_field_semantic_or_production_path(self) -> None:
        source = inspect.getsource(s1wu)
        for forbidden in (
            "advance_ppb1_bank",
            "advance_s1wq_perceptual_state",
            "import os",
            "from pathlib",
            "open(",
            "SharedMCMField",
            "semantic_label",
            "field_feedback",
            "production",
        ):
            self.assertNotIn(forbidden, source)

    def test_probe_remains_private_and_snapshot_neutral(self) -> None:
        names = {
            "S1WUReadOnlyPerceptualFinding",
            "probe_s1wu_perceptual_state",
        }
        self.assertTrue(names.isdisjoint(mcm_field_organism.__all__))
        self.assertTrue(names.isdisjoint(ROOT_LAZY_EXPORTS))
        self.assertTrue(names.isdisjoint(current_api.__all__))
        self.assertTrue(
            names.isdisjoint({item.name for item in fields(SharedMCMFieldSnapshot)})
        )


if __name__ == "__main__":
    unittest.main()
