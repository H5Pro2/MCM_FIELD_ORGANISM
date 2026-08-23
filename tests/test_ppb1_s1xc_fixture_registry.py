from __future__ import annotations

from dataclasses import fields, replace
import inspect
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
import mcm_field_organism._ppb1_s1xc_fixture_registry as s1xc
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS


EXPECTED_MATERIALIZATION_DIGEST = (
    "2f8a45b74c9bee7df5459ddae48050a45a5b5eeb8a32fad9d688a1c31bbd46be"
)


class PPB1S1XCFixtureRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.materialized = s1xc.materialize_s1xc_fixture_registry()

    def test_controlled_configs_derive_exact_12_and_72_carriers(self) -> None:
        fixtures = {item.config.modality_id: item for item in self.materialized.modalities}
        self.assertEqual(12, len(fixtures["auditory"].config.carrier_ids))
        self.assertEqual(72, len(fixtures["visual"].config.carrier_ids))
        self.assertEqual((8, 0.2, 3, 512), (
            fixtures["auditory"].config.capacity,
            fixtures["auditory"].config.match_threshold,
            fixtures["auditory"].config.stable_after,
            fixtures["auditory"].config.expire_after_steps,
        ))
        self.assertEqual((4, 0.1, 3, 128), (
            fixtures["visual"].config.capacity,
            fixtures["visual"].config.match_threshold,
            fixtures["visual"].config.stable_after,
            fixtures["visual"].config.expire_after_steps,
        ))

    def test_formation_and_candidate_prestates_are_materialized_not_advanced(self) -> None:
        for fixture in self.materialized.modalities:
            self.assertEqual([(0, 1), (1, 2), (2, 3)], [
                (frame.window_start_tick, frame.window_end_tick)
                for frame in fixture.formation_frames
            ])
            state = fixture.candidate_prestate
            self.assertEqual(3, state.accepted_step_count)
            self.assertEqual(3, state.last_source_window_end_tick)
            self.assertEqual(1, sum(slot.occupied for slot in state.slots))
            self.assertEqual(3, state.slots[0].support_count)
            self.assertTrue(all(value == 0.0 for value in state.slots[0].prototype_values))

    def test_five_later_probe_frames_per_modality_are_exact(self) -> None:
        expected = {
            "auditory": (0.0, 0.1, 0.2, 0.3, 0.6),
            "visual": (0.0, 0.05, 0.1, 0.2, 0.5),
        }
        for fixture in self.materialized.modalities:
            self.assertEqual(5, len(fixture.probe_frames))
            self.assertEqual(expected[fixture.config.modality_id], tuple(
                frame.values[0] for frame in fixture.probe_frames
            ))
            self.assertTrue(all(
                (frame.window_start_tick, frame.window_end_tick) == (4, 5)
                for frame in fixture.probe_frames
            ))

    def test_registry_has_sixty_unique_contract_ordered_cells(self) -> None:
        cells = self.materialized.cell_plans
        self.assertEqual(60, len(cells))
        self.assertEqual(60, len({cell.cell_id for cell in cells}))
        self.assertEqual("s1xa.auditory.ppb1.exact-positive", cells[0].cell_id)
        self.assertEqual(
            "s1xa.visual.last-vector-distance.distinct-negative",
            cells[-1].cell_id,
        )
        self.assertEqual(s1xc.S1XC_REGISTRY_DIGEST, self.materialized.registry_digest)
        self.assertEqual(
            EXPECTED_MATERIALIZATION_DIGEST,
            self.materialized.materialization_digest,
        )

    def test_cell_plans_bind_storage_and_expected_behavior(self) -> None:
        dimension = {"auditory": 12, "visual": 72}
        for cell in self.materialized.cell_plans:
            if cell.system_id == "no-memory":
                self.assertFalse(cell.observed_state_present)
                self.assertEqual(0, cell.stored_scalar_value_count)
                self.assertIsNone(cell.expected_distance)
                self.assertFalse(cell.expected_recognized)
            else:
                multiplier = 3 if cell.system_id == "replay" else 1
                self.assertTrue(cell.observed_state_present)
                self.assertEqual(
                    multiplier * dimension[cell.modality_id],
                    cell.stored_scalar_value_count,
                )
                self.assertIsNotNone(cell.expected_distance)
            self.assertEqual(
                cell.cell_plan_digest,
                s1xc._digest(cell.payload_without_digest()),
            )

    def test_candidate_identity_never_leaks_to_baseline_plans(self) -> None:
        for cell in self.materialized.cell_plans:
            if cell.system_id == "ppb1":
                self.assertIsNotNone(cell.state_identity_digest)
            else:
                self.assertIsNone(cell.state_identity_digest)

    def test_eight_baseline_prestates_have_bound_information_budgets(self) -> None:
        states = self.materialized.baseline_prestates
        self.assertEqual(8, len(states))
        self.assertEqual(
            {
                (modality, system)
                for modality in s1xc.S1XC_MODALITY_IDS
                for system in (
                    "replay",
                    "static-prototype",
                    "moving-state",
                    "last-vector-distance",
                )
            },
            {(state.modality_id, state.system_id) for state in states},
        )

    def test_read_only_adapters_return_positive_and_negative_findings(self) -> None:
        fixture = self.materialized.modalities[0]
        states = {
            state.system_id: state
            for state in self.materialized.baseline_prestates
            if state.modality_id == fixture.config.modality_id
        }
        for system_id in s1xc.S1XC_BASELINE_SYSTEM_IDS:
            prestate = states.get(system_id)
            exact = s1xc.probe_s1xc_baseline_read_only(
                system_id, fixture.config, prestate, fixture.probe_frames[0], "exact-positive"
            )
            distinct = s1xc.probe_s1xc_baseline_read_only(
                system_id, fixture.config, prestate, fixture.probe_frames[-1], "distinct-negative"
            )
            if system_id == "no-memory":
                self.assertFalse(exact.recognized)
                self.assertIsNone(exact.match_distance)
            else:
                self.assertTrue(exact.recognized)
                self.assertEqual(0.0, exact.match_distance)
                self.assertFalse(distinct.recognized)
                self.assertEqual(0.6, distinct.match_distance)

    def test_baseline_probe_is_deterministic_and_does_not_change_prestate(self) -> None:
        fixture = self.materialized.modalities[1]
        state = next(
            item
            for item in self.materialized.baseline_prestates
            if item.modality_id == "visual" and item.system_id == "replay"
        )
        before = state.digest()
        first = s1xc.probe_s1xc_baseline_read_only(
            "replay", fixture.config, state, fixture.probe_frames[1], "near-positive"
        )
        second = s1xc.probe_s1xc_baseline_read_only(
            "replay", fixture.config, state, fixture.probe_frames[1], "near-positive"
        )
        self.assertEqual(first, second)
        self.assertEqual(before, state.digest())

    def test_mismatched_state_window_and_no_memory_state_fail_closed(self) -> None:
        auditory, visual = self.materialized.modalities
        auditory_state = next(
            state
            for state in self.materialized.baseline_prestates
            if state.modality_id == "auditory" and state.system_id == "replay"
        )
        with self.assertRaises(s1xc.S1XCError):
            s1xc.probe_s1xc_baseline_read_only(
                "replay", visual.config, auditory_state, visual.probe_frames[0], "exact-positive"
            )
        with self.assertRaises(s1xc.S1XCError):
            s1xc.probe_s1xc_baseline_read_only(
                "no-memory",
                auditory.config,
                auditory_state,
                auditory.probe_frames[0],
                "exact-positive",
            )
        with self.assertRaises(s1xc.S1XCError):
            s1xc.probe_s1xc_baseline_read_only(
                "replay",
                auditory.config,
                auditory_state,
                auditory.formation_frames[0],
                "exact-positive",
            )

    def test_findings_are_digest_bound_and_have_no_poststate(self) -> None:
        fixture = self.materialized.modalities[0]
        finding = s1xc.probe_s1xc_baseline_read_only(
            "no-memory", fixture.config, None, fixture.probe_frames[0], "exact-positive"
        )
        self.assertEqual(finding.finding_digest, s1xc._digest(finding.payload_without_digest()))
        self.assertNotIn("poststate", {field.name for field in fields(finding)})
        with self.assertRaises(s1xc.S1XCError):
            replace(finding, recognized=True)
        with self.assertRaises(s1xc.S1XCError):
            replace(
                finding,
                system_id="replay",
                observed_prestate_digest="0" * 64,
                match_distance=float("nan"),
            )

    def test_nonfinite_or_role_invalid_baseline_state_fails_closed(self) -> None:
        fixture = self.materialized.modalities[0]
        state = next(
            item
            for item in self.materialized.baseline_prestates
            if item.modality_id == "auditory" and item.system_id == "replay"
        )
        with self.assertRaises(s1xc.S1XCError):
            replace(state, vectors=((float("nan"),) * state.dimension,) * 3)
        with self.assertRaises(s1xc.S1XCError):
            replace(state, raw_history_access_used=False)
        self.assertEqual(fixture.formation_history_digest, state.formation_history_digest)

    def test_module_is_private_and_contains_no_matrix_or_field_execution(self) -> None:
        self.assertFalse(hasattr(mcm_field_organism, "materialize_s1xc_fixture_registry"))
        self.assertFalse(hasattr(current_api, "materialize_s1xc_fixture_registry"))
        self.assertNotIn("materialize_s1xc_fixture_registry", ROOT_LAZY_EXPORTS)
        source = inspect.getsource(s1xc)
        for forbidden in (
            "advance_ppb1_bank",
            "advance_s1vn_baseline",
            "probe_s1wu_perceptual_state",
            "execute_s1vn_matrix",
            "SharedMCMField",
            "open(",
            "production",
            "semantic_label",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
