from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.w7m_capacity_function_matrix import (
    build_w7m_capacity_function_matrix_adapter,
)
from mcm_field_organism.w7p_measurement_compositor import (
    FIELD_MEASUREMENT_NAMES,
    OBSERVER_MEASUREMENT_NAMES,
    W7PCapacityMeasurement,
    W7PCompletedP0SSample,
    W7PFieldMeasurement,
    W7PMeasurementCompositorError,
    compose_w7p_lifecycle_profile,
    compose_w7p_observer_driver,
    compose_w7p_observer_measurement,
    select_w7p_observer_explanation,
)


class W7PMeasurementCompositorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.adapter = build_w7m_capacity_function_matrix_adapter()
        cls.specs = {item.model_id: item for item in cls.adapter.baselines}
        cls.count = len(cls.adapter.initial_field.layer.neurons)
        cls.source_digest = cls.adapter.source.contact_b_step_digests[0]

    def _driver(self):
        zeros = (0.0,) * self.count
        first = (0.25,) * self.count
        second = (-0.5,) * self.count
        return compose_w7p_observer_driver(
            self.adapter,
            self.source_digest,
            (0, 30),
            zeros,
            (
                W7PCompletedP0SSample(10, first),
                W7PCompletedP0SSample(20, second),
            ),
        )

    def test_driver_is_left_held_atomic_and_bound_to_w7m(self) -> None:
        driver = self._driver()

        self.assertEqual(self.adapter.matrix_digest, driver.matrix_digest)
        self.assertEqual(self.source_digest, driver.source_digest)
        self.assertEqual(((0, 10), (10, 20), (20, 30)), tuple(
            (item.start_tick, item.end_tick) for item in driver.segments
        ))
        self.assertEqual(0.0, driver.segments[0].s_values[0])
        self.assertEqual(0.25, driver.segments[1].s_values[0])
        self.assertEqual(-0.5, driver.segments[2].s_values[0])
        self.assertEqual((-0.5,) * self.count, driver.terminal_s_values)

    def test_driver_is_deterministic_and_inputs_remain_immutable(self) -> None:
        first = self._driver()
        second = self._driver()

        self.assertEqual(first, second)
        self.assertEqual(first.driver_digest, second.driver_digest)

    def test_driver_rejects_unbound_source_and_nonatomic_ticks(self) -> None:
        zeros = (0.0,) * self.count
        sample = W7PCompletedP0SSample(10, zeros)
        with self.assertRaisesRegex(W7PMeasurementCompositorError, "not bound"):
            compose_w7p_observer_driver(
                self.adapter, "0" * 64, (0, 20), zeros, (sample,)
            )
        with self.assertRaisesRegex(W7PMeasurementCompositorError, "atomic"):
            compose_w7p_observer_driver(
                self.adapter,
                self.source_digest,
                (0, 20),
                zeros,
                (sample, sample),
            )

    def test_all_observers_receive_the_exact_same_driver(self) -> None:
        driver = self._driver()
        results = tuple(
            compose_w7p_observer_measurement(self.specs[model_id], driver)
            for model_id in ("leak", "sat", "norm")
        )

        self.assertEqual(
            {driver.driver_digest},
            {item.driver_digest for item in results},
        )
        self.assertTrue(all(item.observer_ticks == (10, 20, 30) for item in results))
        self.assertTrue(all(len(item.observer_output_trace) == 3 for item in results))

    def test_field_and_observer_roles_cannot_be_crossed(self) -> None:
        self.assertEqual(
            (
                "probe_S_linf",
                "probe_H_linf",
                "probe_SH_trajectory_l2",
                "probe_observation_ticks",
            ),
            FIELD_MEASUREMENT_NAMES,
        )
        self.assertTrue(all(name.startswith("observer_") for name in OBSERVER_MEASUREMENT_NAMES))
        with self.assertRaisesRegex(W7PMeasurementCompositorError, "causal field"):
            W7PFieldMeasurement("leak", "ab", 0, 0.0, 0.0, 0.0, (1,))
        with self.assertRaisesRegex(W7PMeasurementCompositorError, "observer specification"):
            compose_w7p_observer_measurement(self.specs["cap"], self._driver())

    def test_only_cap_can_expose_capacity_roles(self) -> None:
        measurement = W7PCapacityMeasurement("cap", 1.0, 1.0, 0.0)
        self.assertEqual("cap", measurement.model_id)
        with self.assertRaisesRegex(W7PMeasurementCompositorError, "only CAP"):
            W7PCapacityMeasurement("mob", 1.0, 1.0, 0.0)

    def test_profiles_use_own_denominator_and_do_not_rescue_zero(self) -> None:
        resolved = compose_w7p_lifecycle_profile(
            "field",
            "cap",
            "ab",
            (2.0, 1.0),
            (1.0, 0.5),
            (0.0, 2.0),
            1e-12,
        )
        unresolved = compose_w7p_lifecycle_profile(
            "observer",
            "leak",
            "ab",
            (1e-13, 1.0),
            (0.0, 1.0),
            (0.0, 1.0),
            1e-12,
        )

        self.assertEqual("RESOLVED", resolved.resolution)
        self.assertEqual((1.0, 0.5), resolved.old_b_retention)
        self.assertEqual((0.5, 0.25), resolved.old_g_retention)
        self.assertEqual((0.0, 1.0), resolved.new_b_gain)
        self.assertEqual("NOT_RESOLVED", unresolved.resolution)
        self.assertEqual((), unresolved.old_b_retention)

    def test_profile_surface_and_model_must_agree(self) -> None:
        with self.assertRaisesRegex(W7PMeasurementCompositorError, "surface differ"):
            compose_w7p_lifecycle_profile(
                "observer", "cap", "ab", (1.0,), (1.0,), (1.0,), 0.0
            )

    def test_observer_explanation_precedence_is_fixed(self) -> None:
        self.assertEqual(
            "NOT_RESOLVED",
            select_w7p_observer_explanation(
                profile_resolved=False, matched_model_ids=("leak",)
            ),
        )
        self.assertEqual(
            "PROFILE_EXPLAINED_BY_LEAK",
            select_w7p_observer_explanation(
                profile_resolved=True,
                matched_model_ids=("norm", "sat", "leak"),
            ),
        )
        self.assertEqual(
            "PROFILE_NOT_MATCHED",
            select_w7p_observer_explanation(
                profile_resolved=True, matched_model_ids=()
            ),
        )

    def test_tampered_driver_digest_is_rejected(self) -> None:
        with self.assertRaisesRegex(W7PMeasurementCompositorError, "digest"):
            replace(self._driver(), driver_digest="changed")

    def test_module_is_not_reexported_from_current_api(self) -> None:
        from mcm_field_organism import current_api

        self.assertFalse(hasattr(current_api, "compose_w7p_observer_driver"))
        self.assertFalse(hasattr(current_api, "compose_w7p_lifecycle_profile"))


if __name__ == "__main__":
    unittest.main()
