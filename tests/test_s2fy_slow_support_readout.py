"""Neutral S2-FY qualification tests for the slow-support readout."""

from __future__ import annotations

import unittest

from mcm_field_organism._ppb1_reference import PPB1BankState, PPB1PrototypeSlot
from tools import _s2fv_private_runner as runner


QUALIFICATION_RUN_ID = "s2fy-support-readout-qualification-20260830-01"


def _bank(config, entries: tuple[tuple[tuple[float, ...], int], ...]) -> PPB1BankState:
    accepted = max((support for _, support in entries), default=0)
    slots = []
    for index in range(config.capacity):
        slot_id = f"{config.bank_id}.slot.{index:03d}"
        if index < len(entries):
            values, support = entries[index]
            slots.append(PPB1PrototypeSlot(slot_id, True, values, support, accepted))
        else:
            slots.append(PPB1PrototypeSlot.free(slot_id))
    return PPB1BankState(
        config.bank_id,
        config.digest(),
        accepted,
        "synthetic.s2fy.clock" if accepted else None,
        accepted * 10 if accepted else None,
        tuple(slots),
    )


class S2FYSlowSupportReadoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        profile, _, _ = runner._profile_and_configs()
        cls.auditory_config = profile.auditory_config
        cls.visual_config = profile.visual_config

    def test_01_visual_averaged_prototype_reports_support_three(self) -> None:
        target = (0.2,) * 18
        averaged = (0.20000000000000004,) + target[1:]
        bank = _bank(self.visual_config, ((averaged, 3),))
        self.assertEqual(
            runner._slow_support_for_target(bank, self.visual_config, target),
            3,
        )

    def test_02_exact_prototype_reports_support_one(self) -> None:
        target = (-0.4,) * 18
        bank = _bank(self.visual_config, ((target, 1),))
        self.assertEqual(
            runner._slow_support_for_target(bank, self.visual_config, target),
            1,
        )

    def test_03_auditory_and_visual_native_thresholds_remain_distinct(self) -> None:
        auditory_target = (0.0,) * 8
        visual_target = (0.0,) * 18
        auditory_bank = _bank(self.auditory_config, (((0.015,) * 8, 1),))
        visual_bank = _bank(self.visual_config, (((0.015,) * 18, 1),))
        self.assertEqual(
            runner._slow_support_for_target(
                auditory_bank, self.auditory_config, auditory_target
            ),
            1,
        )
        self.assertEqual(
            runner._slow_support_for_target(
                visual_bank, self.visual_config, visual_target
            ),
            0,
        )

    def test_04_cross_modal_bank_config_binding_is_rejected(self) -> None:
        auditory_bank = _bank(self.auditory_config, (((0.1,) * 8, 1),))
        with self.assertRaises(runner.S2FVRunnerError):
            runner._slow_support_for_target(
                auditory_bank,
                self.visual_config,
                (0.1,) * 18,
            )

    def test_05_ambiguous_matching_slots_fail_closed(self) -> None:
        target = (0.0,) * 18
        bank = _bank(
            self.visual_config,
            (
                ((0.001,) * 18, 3),
                ((-0.001,) * 18, 1),
            ),
        )
        with self.assertRaisesRegex(
            runner.S2FVRunnerError, "slow support identity is ambiguous"
        ):
            runner._slow_support_for_target(bank, self.visual_config, target)

    def test_06_noncanonical_targets_fail_closed(self) -> None:
        target = (0.0,) * 18
        bank = _bank(self.visual_config, ((target, 1),))
        invalid_targets = ([0.0] * 18, (False,) * 18, ("0.0",) * 18)
        for invalid in invalid_targets:
            with self.subTest(target_type=type(invalid).__name__):
                with self.assertRaises(runner.S2FVRunnerError):
                    runner._slow_support_for_target(
                        bank,
                        self.visual_config,
                        invalid,  # type: ignore[arg-type]
                    )

    def test_07_outside_native_threshold_reports_no_support(self) -> None:
        target = (0.0,) * 18
        bank = _bank(self.visual_config, (((0.011,) * 18, 3),))
        self.assertEqual(
            runner._slow_support_for_target(bank, self.visual_config, target),
            0,
        )

    def test_08_readout_preserves_bank_state(self) -> None:
        target = (0.3,) * 8
        bank = _bank(self.auditory_config, (((0.30000000000000004,) * 8, 3),))
        before = bank.digest()
        self.assertEqual(
            runner._slow_support_for_target(bank, self.auditory_config, target),
            3,
        )
        self.assertEqual(bank.digest(), before)


if __name__ == "__main__":
    unittest.main()
