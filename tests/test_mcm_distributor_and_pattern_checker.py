from __future__ import annotations

from dataclasses import fields
from itertools import permutations
import unittest

from mcm_field_organism import (
    DistributedMCMConstellation,
    MCMDock,
    MCMDistributionError,
    MCMDistributor,
    MCMFieldWindow,
    MultimodalPatternChecker,
    TemporalRelation,
    global_sum_collision_baseline,
)


class MCMFixture(unittest.TestCase):
    clock_id = "system.monotonic"

    def dock(self, modality: str) -> MCMDock:
        return MCMDock(
            dock_id=f"dock.{modality}",
            modality_id=modality,
            geometry_id=f"mcm.{modality}.v1",
            clock_id=self.clock_id,
        )

    def state(
        self,
        modality: str,
        *,
        activation: tuple[float, ...] = (0.4, 0.2),
        afterimage: tuple[float, ...] = (0.1, 0.05),
        start: int = 100,
        end: int = 200,
        snapshot: str | None = None,
    ) -> MCMFieldWindow:
        return MCMFieldWindow(
            dock_id=f"dock.{modality}",
            modality_id=modality,
            field_id=f"field.{modality}",
            geometry_id=f"mcm.{modality}.v1",
            snapshot_id=snapshot or f"snapshot.{modality}.{start}.{end}",
            clock_id=self.clock_id,
            window_start_tick=start,
            window_end_tick=end,
            carrier_ids=(f"{modality}.carrier.0", f"{modality}.carrier.1"),
            activation=activation,
            afterimage=afterimage,
        )

    def distributor(self, *modalities: str) -> MCMDistributor:
        distributor = MCMDistributor()
        for modality in modalities:
            distributor.attach(self.dock(modality))
        return distributor


class MCMDistributorTests(MCMFixture):
    def test_docks_are_open_modules_with_stable_canonical_order(self) -> None:
        distributor = self.distributor("visual", "auditory")
        self.assertEqual(("dock.auditory", "dock.visual"), tuple(dock.dock_id for dock in distributor.docks))
        original = {dock.dock_id: dock for dock in distributor.docks}
        distributor.attach(self.dock("tactile"))
        current = {dock.dock_id: dock for dock in distributor.docks}
        self.assertEqual(original, {dock_id: current[dock_id] for dock_id in original})
        self.assertEqual(
            ("dock.auditory", "dock.tactile", "dock.visual"),
            tuple(dock.dock_id for dock in distributor.docks),
        )

    def test_duplicate_dock_or_modality_is_rejected(self) -> None:
        distributor = self.distributor("auditory")
        with self.assertRaises(MCMDistributionError):
            distributor.attach(self.dock("auditory"))
        with self.assertRaises(MCMDistributionError):
            distributor.attach(
                MCMDock("dock.other", "auditory", "mcm.auditory.v2", self.clock_id)
            )

    def test_dock_can_be_detached_without_changing_other_docks(self) -> None:
        distributor = self.distributor("auditory", "visual")
        removed = distributor.detach("dock.auditory")
        self.assertEqual("auditory", removed.modality_id)
        self.assertEqual(("dock.visual",), tuple(dock.dock_id for dock in distributor.docks))
        with self.assertRaises(MCMDistributionError):
            distributor.detach("dock.auditory")

    def test_each_sensor_mcm_can_form_a_valid_unimodal_distribution(self) -> None:
        for modality in ("auditory", "visual", "tactile"):
            with self.subTest(modality=modality):
                state = self.state(modality)
                constellation = self.distributor(modality).distribute([state])
                self.assertEqual((modality,), constellation.modality_ids)
                self.assertIs(state, constellation.states[0])

    def test_arrival_permutation_does_not_change_distribution(self) -> None:
        distributor = self.distributor("auditory", "visual", "tactile")
        states = tuple(self.state(modality) for modality in ("auditory", "visual", "tactile"))
        digests = {
            distributor.distribute(order).digest()
            for order in permutations(states)
        }
        self.assertEqual(1, len(digests))

    def test_equal_numeric_fields_remain_modally_distinct(self) -> None:
        audio = self.state("auditory", activation=(0.4, 0.2))
        visual = self.state("visual", activation=(0.4, 0.2))
        constellation = self.distributor("auditory", "visual").distribute([visual, audio])
        self.assertEqual(("auditory", "visual"), constellation.modality_ids)
        self.assertNotEqual(constellation.states[0].digest(), constellation.states[1].digest())

    def test_unknown_or_incompatible_dock_state_is_rejected(self) -> None:
        distributor = self.distributor("auditory")
        valid = self.state("auditory")
        invalid_states = (
            self.state("visual"),
            MCMFieldWindow(
                **{**valid.canonical_payload(), "modality_id": "visual"}
            ),
            MCMFieldWindow(
                **{**valid.canonical_payload(), "geometry_id": "mcm.auditory.v2"}
            ),
            MCMFieldWindow(
                **{**valid.canonical_payload(), "clock_id": "other.clock"}
            ),
        )
        for state in invalid_states:
            with self.subTest(state=state), self.assertRaises(MCMDistributionError):
                distributor.distribute([state])

    def test_duplicate_dock_field_and_snapshot_are_rejected(self) -> None:
        distributor = self.distributor("auditory", "visual")
        audio = self.state("auditory")
        visual = self.state("visual")
        duplicates = (
            (audio, self.state("auditory", snapshot="snapshot.auditory.other")),
            (audio, MCMFieldWindow(**{**visual.canonical_payload(), "field_id": audio.field_id})),
            (audio, MCMFieldWindow(**{**visual.canonical_payload(), "snapshot_id": audio.snapshot_id})),
        )
        for pair in duplicates:
            with self.assertRaises(MCMDistributionError):
                distributor.distribute(pair)

    def test_field_window_rejects_invalid_time_and_geometry(self) -> None:
        valid = self.state("auditory").canonical_payload()
        invalid = (
            {**valid, "window_end_tick": valid["window_start_tick"]},
            {**valid, "carrier_ids": []},
            {**valid, "activation": [0.1]},
            {**valid, "afterimage": [float("nan"), 0.0]},
        )
        for payload in invalid:
            with self.assertRaises(MCMDistributionError):
                MCMFieldWindow(**payload)

    def test_public_field_roles_exclude_raw_sensor_and_semantics(self) -> None:
        roles = {item.name for item in fields(MCMFieldWindow)}
        forbidden = {"samples", "audio", "image", "word", "object", "meaning", "reward"}
        self.assertTrue(forbidden.isdisjoint(roles))


class MultimodalPatternCheckerTests(MCMFixture):
    def setUp(self) -> None:
        self.distributor = self.distributor("auditory", "visual")
        self.checker = MultimodalPatternChecker()

    def test_unimodal_field_is_a_valid_single_constellation(self) -> None:
        constellation = self.distributor.distribute([self.state("auditory")])
        result = self.checker.check(constellation)
        self.assertEqual(TemporalRelation.SINGLE, result.temporal_relation)
        self.assertEqual(("auditory",), result.modality_ids)
        self.assertEqual((100, 200), (result.overlap_start_tick, result.overlap_end_tick))

    def test_overlapping_fields_report_only_the_actual_common_window(self) -> None:
        audio = self.state("auditory", start=100, end=220)
        visual = self.state("visual", start=160, end=260)
        result = self.checker.check(self.distributor.distribute([audio, visual]))
        self.assertEqual(TemporalRelation.OVERLAP, result.temporal_relation)
        self.assertEqual((160, 220), (result.overlap_start_tick, result.overlap_end_tick))

    def test_disjoint_fields_are_not_reported_as_joint_pattern(self) -> None:
        audio = self.state("auditory", start=100, end=150)
        visual = self.state("visual", start=150, end=200)
        result = self.checker.check(self.distributor.distribute([audio, visual]))
        self.assertEqual(TemporalRelation.DISJOINT, result.temporal_relation)
        self.assertIsNone(result.overlap_start_tick)
        self.assertIsNone(result.overlap_end_tick)

    def test_field_arrival_order_does_not_change_pattern_result(self) -> None:
        audio = self.state("auditory")
        visual = self.state("visual")
        first = self.checker.check(self.distributor.distribute([audio, visual]))
        second = self.checker.check(self.distributor.distribute([visual, audio]))
        self.assertEqual(first, second)

    def test_changing_only_audio_changes_only_audio_digest_and_constellation(self) -> None:
        visual = self.state("visual")
        audio_first = self.state("auditory", activation=(0.4, 0.2))
        audio_second = self.state("auditory", activation=(0.8, 0.2))
        first = self.checker.check(self.distributor.distribute([audio_first, visual]))
        second = self.checker.check(self.distributor.distribute([audio_second, visual]))
        first_parts = dict(first.modality_digests)
        second_parts = dict(second.modality_digests)
        self.assertNotEqual(first_parts["auditory"], second_parts["auditory"])
        self.assertEqual(first_parts["visual"], second_parts["visual"])
        self.assertNotEqual(first.constellation_digest, second.constellation_digest)

    def test_observer_does_not_change_pattern_result(self) -> None:
        constellation = self.distributor.distribute([self.state("auditory"), self.state("visual")])
        without = self.checker.check(constellation)
        seen = []
        with_observer = self.checker.check(constellation, observer=seen.append)
        self.assertEqual(without, with_observer)
        self.assertEqual([without], seen)

    def test_global_sum_baseline_collides_while_constellations_remain_distinct(self) -> None:
        first_states = (
            self.state("auditory", activation=(1.0, 0.0)),
            self.state("visual", activation=(0.0, 1.0)),
        )
        second_states = (
            self.state("auditory", activation=(0.0, 1.0)),
            self.state("visual", activation=(1.0, 0.0)),
        )
        self.assertEqual(global_sum_collision_baseline(first_states), global_sum_collision_baseline(second_states))
        first = self.distributor.distribute(first_states)
        second = self.distributor.distribute(second_states)
        self.assertNotEqual(first.digest(), second.digest())

    def test_pattern_result_contains_no_classification_or_similarity_roles(self) -> None:
        roles = {item.name for item in fields(type(self.checker.check(
            self.distributor.distribute([self.state("auditory")])
        )))}
        forbidden = {"label", "class_id", "similarity", "winner", "attention", "meaning"}
        self.assertTrue(forbidden.isdisjoint(roles))

    def test_constellation_constructor_canonicalizes_and_validates_clock(self) -> None:
        audio = self.state("auditory")
        visual = self.state("visual")
        constellation = DistributedMCMConstellation(self.clock_id, (visual, audio))
        self.assertEqual(("auditory", "visual"), constellation.modality_ids)
        with self.assertRaises(MCMDistributionError):
            DistributedMCMConstellation("other.clock", (audio, visual))


if __name__ == "__main__":
    unittest.main()
