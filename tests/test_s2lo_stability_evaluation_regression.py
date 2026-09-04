"""Focused regression for profile-bound S2-LO PPB stability evaluation."""

from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism import _ppb1_reference as ppb1
from tools import _s2lo_private_role_free_stream_runner as runner


def _bank_with_support(config: ppb1.PPB1BankConfig, support: int) -> ppb1.PPB1BankState:
    initial = ppb1.initial_ppb1_bank_state(config)
    slots = list(initial.slots)
    slots[0] = ppb1.PPB1PrototypeSlot(
        slots[0].slot_id,
        True,
        (0.0,) * len(config.carrier_ids),
        support,
        support,
    )
    return ppb1.PPB1BankState(
        config.bank_id,
        config.digest(),
        support,
        "s2lo-regression-clock",
        support,
        tuple(slots),
    )


class S2LOStabilityEvaluationRegressionTests(unittest.TestCase):
    def test_profile_bound_support_thresholds_and_config_digest(self) -> None:
        coordinator = runner._build_config()
        for modality, config in (
            ("auditory", coordinator.tspm_config.profile.auditory_config),
            ("visual", coordinator.tspm_config.profile.visual_config),
        ):
            below = _bank_with_support(config, config.stable_after - 1)
            boundary = _bank_with_support(config, config.stable_after)
            self.assertEqual((), runner._stable_slots(coordinator, below, modality))
            self.assertEqual(1, len(runner._stable_slots(coordinator, boundary, modality)))
            with self.assertRaises(runner.S2LOError):
                runner._stable_slots(
                    coordinator,
                    replace(boundary, config_digest="0" * 64),
                    modality,
                )


if __name__ == "__main__":
    unittest.main()
