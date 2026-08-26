from __future__ import annotations

import unittest

from mcm_field_organism.s1l_f3_history_function_adapter import (
    S1L_ABSOLUTE_FLOOR,
    build_s1l_source_contract,
    run_s1l_model_pair,
    run_s1l_rebind_control,
    s1l_f3_history_function_public_roles,
)


class S1LF3HistoryFunctionAdapterTests(unittest.TestCase):
    def test_history_sources_have_equal_bound_marginals(self) -> None:
        source = build_s1l_source_contract()

        self.assertNotEqual(source.history_a_digest, source.history_b_digest)
        self.assertEqual(
            source.history_a_invariants,
            source.history_b_invariants,
        )
        self.assertEqual(8, source.history_a_invariants.support_count)
        self.assertEqual(8, source.history_a_invariants.event_count)
        self.assertGreater(source.history_a_invariants.l1_amplitude, 0.0)
        self.assertGreater(source.history_a_invariants.l2_amplitude, 0.0)

    def test_model_controls_isolate_m_state_and_backreaction(self) -> None:
        f3 = run_s1l_model_pair("f3", 4)
        linear = run_s1l_model_pair("linear-coupled-field", 4)
        eta_null = run_s1l_model_pair("eta-null", 4)
        p0 = run_s1l_model_pair("p0", 4)
        neutral = run_s1l_model_pair("f3", 4, neutralized=True)

        for result in (f3, linear, eta_null, p0, neutral):
            with self.subTest(model=result.model_id, neutral=result.neutralized):
                self.assertEqual((0.0,) * 26, result.preprobe_a.activation)
                self.assertEqual((0.0,) * 26, result.preprobe_a.afterimage)
                self.assertEqual((0.0,) * 26, result.preprobe_b.activation)
                self.assertEqual((0.0,) * 26, result.preprobe_b.afterimage)
                self.assertEqual(16, result.source_event_count_per_path)
                self.assertAlmostEqual(1.0, sum(result.preprobe_a.mass), places=12)
                self.assertAlmostEqual(1.0, sum(result.preprobe_b.mass), places=12)
                self.assertGreaterEqual(min(result.preprobe_a.mass), 0.0)
                self.assertGreaterEqual(min(result.preprobe_b.mass), 0.0)
        self.assertGreater(f3.preprobe_mass_linf, 0.0)
        self.assertGreater(linear.preprobe_mass_linf, 0.0)
        self.assertGreater(eta_null.preprobe_mass_linf, 0.0)
        self.assertEqual(0.0, p0.preprobe_mass_linf)
        self.assertEqual(0.0, neutral.preprobe_mass_linf)
        self.assertGreater(f3.probe_effect_linf, S1L_ABSOLUTE_FLOOR)
        self.assertGreater(linear.probe_effect_linf, S1L_ABSOLUTE_FLOOR)
        self.assertEqual(0.0, eta_null.probe_effect_linf)
        self.assertEqual(0.0, p0.probe_effect_linf)
        self.assertEqual(0.0, neutral.probe_effect_linf)

    def test_refinements_and_repeatability_are_exposed_without_decision(self) -> None:
        results = tuple(run_s1l_model_pair("f3", value) for value in (1, 2, 4))
        repeated = run_s1l_model_pair("f3", 4)

        self.assertTrue(all(result.probe_effect_linf > 0.0 for result in results))
        self.assertEqual(
            tuple(state.digest() for state in results[-1].probe_a),
            tuple(state.digest() for state in repeated.probe_a),
        )
        self.assertEqual(
            tuple(state.digest() for state in results[-1].probe_b),
            tuple(state.digest() for state in repeated.probe_b),
        )
        self.assertFalse(results[-1].decision_allowed)
        self.assertFalse(results[-1].memory_claim_allowed)
        self.assertFalse(results[-1].learning_claim_allowed)
        self.assertFalse(results[-1].raw_payload_retained)

    def test_external_neutralization_can_bind_the_b_path_again(self) -> None:
        result = run_s1l_rebind_control(4)

        self.assertLessEqual(result.maximum_state_linf, S1L_ABSOLUTE_FLOOR)
        self.assertFalse(result.decision_allowed)
        self.assertFalse(result.raw_payload_retained)

    def test_public_roles_contain_no_result_control_or_claim_target(self) -> None:
        roles = set(s1l_f3_history_function_public_roles())
        self.assertTrue(
            {
                "label",
                "reward",
                "meaning",
                "topology",
                "observer",
                "writeback",
                "target",
                "decision",
            }.isdisjoint(roles)
        )


if __name__ == "__main__":
    unittest.main()
