from __future__ import annotations

import unittest

from mcm_field_organism.mcm_f3_controlled_history_source import (
    build_mcm_f3_controlled_history_inputs,
    mcm_f3_controlled_history_source_public_roles,
    mcm_f3_receptor_sequences_digest,
)


class MCMF3ControlledHistorySourceTests(unittest.TestCase):
    def test_histories_differ_and_one_fresh_probe_is_reused(self) -> None:
        inputs = build_mcm_f3_controlled_history_inputs()

        self.assertNotEqual(inputs.same_history_digest, inputs.changed_history_digest)
        self.assertEqual(
            inputs.shared_probe_digest,
            mcm_f3_receptor_sequences_digest(inputs.shared_probe),
        )
        self.assertEqual((291, 30), tuple(len(item.frames) for item in inputs.same_history))
        self.assertEqual((91, 10), tuple(len(item.frames) for item in inputs.shared_probe))
        self.assertEqual(3_090_000, inputs.shared_probe[0].frames[0].field_time.window_start_tick)
        self.assertEqual(3_000_000, inputs.shared_probe[1].frames[0].field_time.window_start_tick)
        self.assertEqual(4_000_000, inputs.shared_probe[1].frames[-1].field_time.window_end_tick)

    def test_input_adapter_has_no_claim_or_intervention_roles(self) -> None:
        roles = set(mcm_f3_controlled_history_source_public_roles())

        self.assertTrue({"memory", "meaning", "reward", "operator"}.isdisjoint(roles))


if __name__ == "__main__":
    unittest.main()
