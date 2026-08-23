from __future__ import annotations

from dataclasses import fields, replace
import inspect
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
import mcm_field_organism._ppb1_s1xz_private_temporal_update_fixture as s1xz
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BUNDLE_DIGEST = (
    "0aac41828eb64ba0f2dfc8488ba6d9c1c636998cb66023ad6bc488a0671bbadb"
)


class PPB1S1XZPrivateTemporalUpdateFixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = s1xz.build_s1xz_temporal_update_fixture()

    def test_bundle_is_deterministic_and_preflight_bound(self) -> None:
        self.assertEqual(self.fixture, s1xz.build_s1xz_temporal_update_fixture())
        self.assertEqual(EXPECTED_BUNDLE_DIGEST, self.fixture.bundle_digest)
        self.assertEqual(
            "1bf316628b75ca6ee11fb05f290713b30b758c7a35b9cb9ede19b3142c577d06",
            s1xz.S1XZ_PREFLIGHT_DIGEST,
        )

    def test_two_modality_fixtures_have_exact_existing_roles(self) -> None:
        self.assertEqual(("auditory", "visual"), tuple(item.modality_id for item in self.fixture.modalities))
        auditory, visual = self.fixture.modalities
        self.assertEqual((12, 0.25), (auditory.carrier_count, auditory.match_threshold))
        self.assertEqual((72, 0.125), (visual.carrier_count, visual.match_threshold))
        for item in self.fixture.modalities:
            self.assertEqual((2, 0.5, 3, 8), (item.capacity, item.update_rate, item.stable_after, item.expire_after_steps))

    def test_ten_plans_have_bound_modality_then_history_order(self) -> None:
        self.assertEqual(
            tuple((modality, history) for modality in s1xz.S1XZ_MODALITY_ORDER for history in s1xz.S1XZ_HISTORY_ORDER),
            tuple((item.modality_id, item.history_id) for item in self.fixture.history_plans),
        )

    def test_all_scalar_values_are_binary_exact_and_bounded(self) -> None:
        for modality in self.fixture.modalities:
            self.assertEqual(s1xz.S1XZ_VALUE_ROLES, tuple(role for role, _ in modality.named_scalar_values))
            for _, value in modality.named_scalar_values:
                numerator, denominator = value.as_integer_ratio()
                self.assertIsInstance(numerator, int)
                self.assertEqual(0, denominator & (denominator - 1))
                self.assertLessEqual(abs(value), 1.0)

    def test_h1_and_gradual_terminal_values_are_exact(self) -> None:
        auditory, visual = self.fixture.modalities
        self.assertEqual((0.09375, 0.1328125), (auditory.h1_terminal_candidate_prototype, auditory.h2_h5_terminal_candidate_prototype))
        self.assertEqual((0.046875, 0.06640625), (visual.h1_terminal_candidate_prototype, visual.h2_h5_terminal_candidate_prototype))
        for modality, target in (("auditory", 0.0546875), ("visual", 0.02734375)):
            h2 = next(item for item in self.fixture.history_plans if item.modality_id == modality and item.history_id == "H2")
            self.assertEqual(target, h2.expected_candidate_probe_distances[2])
            self.assertTrue(h2.expected_candidate_recognition[2])

    def test_h3_is_bound_only_to_separation(self) -> None:
        for modality in s1xz.S1XZ_MODALITY_ORDER:
            plan = next(item for item in self.fixture.history_plans if item.modality_id == modality and item.history_id == "H3")
            self.assertEqual("SEPARATE_ONLY", plan.target_policy)
            self.assertEqual((True, True, False), plan.expected_candidate_recognition)
            self.assertEqual((True, False, False), plan.expected_baseline_recognition)
            self.assertEqual(("CREATED", "MATCHED", "MATCHED", "CREATED", "MATCHED", "MATCHED"), plan.expected_candidate_events)

    def test_h4_binds_unique_lru_replacement_behavior(self) -> None:
        for modality in s1xz.S1XZ_MODALITY_ORDER:
            plan = next(item for item in self.fixture.history_plans if item.modality_id == modality and item.history_id == "H4")
            self.assertEqual("DETERMINISTIC_LRU_REPLACEMENT_SLOT_000", plan.target_policy)
            self.assertEqual((True, False, True, False), plan.expected_candidate_recognition)
            self.assertEqual((True, True, False, False), plan.expected_baseline_recognition)
            self.assertEqual("REPLACED", plan.expected_candidate_events[6])

    def test_h5_has_four_tick_separation_and_read_only_probe_plan(self) -> None:
        for modality in s1xz.S1XZ_MODALITY_ORDER:
            plan = next(item for item in self.fixture.history_plans if item.modality_id == modality and item.history_id == "H5")
            self.assertEqual(4, plan.separation_ticks)
            self.assertEqual(("gradual_3", "origin", "conflict_b"), plan.ordered_probe_roles)
            self.assertEqual((True, True, False), plan.expected_candidate_recognition)

    def test_exact_future_budgets_are_bound_without_retry(self) -> None:
        self.assertEqual(64, self.fixture.total_candidate_exposures)
        self.assertEqual(36, self.fixture.total_baseline_formation_exposures)
        self.assertEqual(28, self.fixture.total_baseline_frozen_handoffs)
        self.assertEqual(32, self.fixture.total_paired_probes)
        self.assertEqual(0, self.fixture.retry_count)

    def test_all_three_types_are_frozen_slotted_and_role_complete(self) -> None:
        expected = {
            s1xz.S1XZModalityFixture: 11,
            s1xz.S1XZHistoryPlan: 16,
            s1xz.S1XZTemporalUpdateFixtureBundle: 8,
        }
        for kind, count in expected.items():
            self.assertEqual(count, len(fields(kind)))
            self.assertTrue(kind.__dataclass_params__.frozen)
            self.assertIsInstance(kind.__slots__, tuple)
            self.assertEqual(count, len(kind.__slots__))

    def test_tampering_fails_closed(self) -> None:
        with self.assertRaises(s1xz.S1XZTemporalUpdateFixtureError):
            replace(self.fixture.modalities[0], match_threshold=0.5)
        with self.assertRaises(s1xz.S1XZTemporalUpdateFixtureError):
            replace(self.fixture.history_plans[0], target_policy="CHANGED")
        with self.assertRaises(s1xz.S1XZTemporalUpdateFixtureError):
            replace(self.fixture, total_paired_probes=31)

    def test_source_is_private_and_excludes_state_probe_baseline_and_runner(self) -> None:
        source = inspect.getsource(s1xz)
        for forbidden in (
            "advance_ppb1_bank",
            "initial_ppb1_bank_state",
            "advance_s1wq_perceptual_state",
            "probe_s1wu_perceptual_state",
            "ReceptorContactFrame",
            "static_prototype_baseline",
            "temporal_update_runner",
            "SharedMCMField",
            "open(",
            "write_text(",
        ):
            self.assertNotIn(forbidden, source)
        self.assertNotIn("S1XZTemporalUpdateFixtureBundle", mcm_field_organism.__all__)
        self.assertFalse(hasattr(current_api, "build_s1xz_temporal_update_fixture"))
        self.assertNotIn("build_s1xz_temporal_update_fixture", ROOT_LAZY_EXPORTS)


if __name__ == "__main__":
    unittest.main()
