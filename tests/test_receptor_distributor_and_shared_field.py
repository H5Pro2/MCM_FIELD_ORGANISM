from __future__ import annotations

import json
import unittest

from mcm_field_organism import (
    CommonFieldTime,
    ReceptorContactFrame,
    ReceptorDistribution,
    ReceptorDistributionError,
    ReceptorDistributor,
    ReceptorDock,
    ReceptorDockAnatomy,
    SharedMCMFieldError,
    SharedMCMFieldSnapshot,
    build_shared_mcm_field,
    receptor_projection_baseline,
    restore_shared_mcm_field,
)


FIELD_SAMPLE_OFFSETS = ((-1, 0), (0, -1), (0, 1), (1, 0))


def frame(
    modality: str,
    values: tuple[float, ...],
    *,
    geometry_id: str | None = None,
) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id=modality,
        geometry_id=geometry_id or f"{modality}.receptor.v1",
        snapshot_id=f"{modality}.snapshot.0",
        clock_id=f"{modality}.source",
        window_start_tick=0,
        window_end_tick=10,
        carrier_ids=tuple(
            f"{modality}.carrier.{index}" for index in range(len(values))
        ),
        values=values,
    )


def anatomy(modality: str, width: int) -> ReceptorDockAnatomy:
    row = {"auditory": 0, "visual": 1, "tactile": 2}[modality]
    return ReceptorDockAnatomy(
        modality_id=modality,
        dock_id=f"dock.{modality}",
        positions=tuple((row, index) for index in range(width)),
    )


class ReceptorDistributorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.audio = frame("auditory", (0.2, 0.4))
        self.video = frame("visual", (0.3, 0.7, 0.9))
        self.field_time = CommonFieldTime("organism.test", 100, 180)

    def distributor(self) -> ReceptorDistributor:
        distributor = ReceptorDistributor()
        for source in (self.audio, self.video):
            distributor.attach(
                ReceptorDock(
                    f"dock.{source.modality_id}",
                    source.modality_id,
                    source.geometry_id,
                )
            )
        return distributor

    def test_distribution_preserves_origin_geometry_and_values(self) -> None:
        result = self.distributor().distribute(
            (self.video, self.audio), self.field_time
        )
        self.assertEqual(("dock.auditory", "dock.visual"), result.dock_ids)
        self.assertEqual(("auditory", "visual"), result.modality_ids)
        contacts = {item.frame.modality_id: item.frame for item in result.contacts}
        self.assertEqual(self.audio, contacts["auditory"])
        self.assertEqual(self.video, contacts["visual"])

    def test_distributor_has_no_state_after_distribution(self) -> None:
        distributor = self.distributor()
        before = distributor.docks
        distributor.distribute((self.audio, self.video), self.field_time)
        self.assertEqual(before, distributor.docks)
        self.assertFalse(hasattr(distributor, "memory"))
        self.assertFalse(hasattr(distributor, "field_state"))

    def test_unknown_or_wrong_geometry_is_rejected(self) -> None:
        distributor = self.distributor()
        with self.assertRaisesRegex(ReceptorDistributionError, "no dock"):
            distributor.distribute(
                (frame("tactile", (0.1,)),), self.field_time
            )
        with self.assertRaisesRegex(ReceptorDistributionError, "geometry"):
            distributor.distribute(
                (frame("auditory", (0.2, 0.4), geometry_id="wrong.geometry"),),
                self.field_time,
            )


class SharedMCMFieldTests(unittest.TestCase):
    def setUp(self) -> None:
        self.audio = frame("auditory", (0.2, 0.4))
        self.video = frame("visual", (0.3, 0.7, 0.9))
        self.anatomies = {
            "auditory": anatomy("auditory", 2),
            "visual": anatomy("visual", 3),
        }
        distributor = ReceptorDistributor()
        for source in (self.audio, self.video):
            distributor.attach(
                ReceptorDock(
                    f"dock.{source.modality_id}",
                    source.modality_id,
                    source.geometry_id,
                )
            )
        self.distribution = distributor.distribute(
            (self.audio, self.video),
            CommonFieldTime("organism.test", 100, 180),
        )

    def test_one_layer_receives_all_receptor_docks_atomically(self) -> None:
        field = build_shared_mcm_field(
            (self.audio, self.video),
            self.anatomies,
            sample_offsets=FIELD_SAMPLE_OFFSETS,
        ).advance(self.distribution, receptor_projection_baseline)
        snapshot = field.snapshot()
        self.assertEqual(5, len(field.layer.neurons))
        self.assertEqual(1, field.layer.tick)
        self.assertEqual(
            self.audio.values + self.video.values,
            snapshot.activation,
        )
        self.assertEqual(
            {"organism.mcm_field"},
            {neuron.field_id for neuron in field.layer.neurons},
        )
        self.assertEqual(2, len(snapshot.dock_neuron_ids))

    def test_docks_share_one_geometry_and_can_form_local_cross_dock_samples(
        self,
    ) -> None:
        field = build_shared_mcm_field(
            (self.video, self.audio),
            self.anatomies,
            sample_offsets=FIELD_SAMPLE_OFFSETS,
        ).advance(self.distribution, receptor_projection_baseline)
        field = field.advance(
            ReceptorDistribution(
                CommonFieldTime("organism.test", 180, 260),
                self.distribution.contacts,
            ),
            receptor_projection_baseline,
        )
        auditory_id = next(
            dock.dock_map.neuron_ids[0]
            for dock in field.docks
            if dock.dock_map.modality_id == "auditory"
        )
        visual_id = next(
            dock.dock_map.neuron_ids[0]
            for dock in field.docks
            if dock.dock_map.modality_id == "visual"
        )
        sampled_ids = {
            sample.sample_id
            for sample in field.layer.neuron(auditory_id).perception.local_samples
        }
        self.assertIn(f"sample.{visual_id}", sampled_ids)
        self.assertEqual(
            {"organism.shared.v1"},
            {neuron.geometry_id for neuron in field.layer.neurons},
        )

    def test_docks_cannot_claim_the_same_shared_field_position(self) -> None:
        overlapping = dict(self.anatomies)
        overlapping["visual"] = ReceptorDockAnatomy(
            modality_id="visual",
            dock_id="dock.visual",
            positions=((0, 0), (0, 1), (0, 2)),
        )
        with self.assertRaisesRegex(
            SharedMCMFieldError,
            "overlap in shared field positions",
        ):
            build_shared_mcm_field(
                (self.audio, self.video),
                overlapping,
                sample_offsets=FIELD_SAMPLE_OFFSETS,
            )

    def test_one_modality_can_reach_the_field_while_another_is_absent(self) -> None:
        distributor = ReceptorDistributor()
        distributor.attach(
            ReceptorDock(
                "dock.auditory", "auditory", self.audio.geometry_id
            )
        )
        incomplete = distributor.distribute(
            (self.audio,), CommonFieldTime("organism.test", 100, 180)
        )
        field = build_shared_mcm_field(
            (self.audio, self.video),
            self.anatomies,
            sample_offsets=FIELD_SAMPLE_OFFSETS,
        )
        advanced = field.advance(incomplete, receptor_projection_baseline)
        snapshot = advanced.snapshot()
        self.assertEqual(self.audio.values + (0.0, 0.0, 0.0), snapshot.activation)
        visual_ids = next(
            dock.dock_map.neuron_ids
            for dock in advanced.docks
            if dock.dock_map.modality_id == "visual"
        )
        self.assertTrue(
            all(
                advanced.layer.neuron(neuron_id).perception.receptor_contact is None
                for neuron_id in visual_ids
            )
        )
        self.assertTrue(set(visual_ids).issubset(advanced.layer.docked_neuron_ids))

    def test_complete_snapshot_roundtrip_restores_the_same_runtime_state(self) -> None:
        field = build_shared_mcm_field(
            (self.audio, self.video),
            self.anatomies,
            sample_offsets=FIELD_SAMPLE_OFFSETS,
        ).advance(self.distribution, receptor_projection_baseline)

        encoded = field.snapshot().to_json()
        loaded = SharedMCMFieldSnapshot.from_json(encoded)
        restored = restore_shared_mcm_field(loaded)

        self.assertEqual(field.snapshot().digest(), restored.snapshot().digest())
        self.assertEqual(
            field.layer.digest(),
            restored.layer.digest(),
        )
        self.assertIsNot(field.layer, restored.layer)
        self.assertIsNot(field.last_distribution, restored.last_distribution)

    def test_restored_field_has_the_same_next_world_contact_result(self) -> None:
        field = build_shared_mcm_field(
            (self.audio, self.video),
            self.anatomies,
            sample_offsets=FIELD_SAMPLE_OFFSETS,
        ).advance(self.distribution, receptor_projection_baseline)
        restored = restore_shared_mcm_field(
            SharedMCMFieldSnapshot.from_json(field.snapshot().to_json())
        )
        next_distribution = ReceptorDistribution(
            CommonFieldTime("organism.test", 180, 260),
            self.distribution.contacts,
        )

        uninterrupted_next = field.advance(
            next_distribution,
            receptor_projection_baseline,
        )
        restored_next = restored.advance(
            next_distribution,
            receptor_projection_baseline,
        )

        self.assertEqual(
            uninterrupted_next.snapshot().digest(),
            restored_next.snapshot().digest(),
        )

    def test_snapshot_schema_rejects_hidden_or_invalid_state(self) -> None:
        field = build_shared_mcm_field(
            (self.audio, self.video),
            self.anatomies,
            sample_offsets=FIELD_SAMPLE_OFFSETS,
        ).advance(self.distribution, receptor_projection_baseline)
        payload = json.loads(field.snapshot().to_json())
        payload["meaning"] = "chair"
        with self.assertRaisesRegex(SharedMCMFieldError, "unknown"):
            SharedMCMFieldSnapshot.from_json(json.dumps(payload))

        payload = json.loads(field.snapshot().to_json())
        payload["layer"]["neurons"][0]["activation"] = 2.0
        with self.assertRaisesRegex(SharedMCMFieldError, "runtime contract"):
            SharedMCMFieldSnapshot.from_json(json.dumps(payload))

        payload = json.loads(field.snapshot().to_json())
        payload["last_distribution"]["contacts"][0]["values"][0] = 0.25
        with self.assertRaisesRegex(SharedMCMFieldError, "last distribution"):
            SharedMCMFieldSnapshot.from_json(json.dumps(payload))

    def test_snapshot_contains_only_current_technical_runtime_roles(self) -> None:
        field = build_shared_mcm_field(
            (self.audio, self.video),
            self.anatomies,
            sample_offsets=FIELD_SAMPLE_OFFSETS,
        ).advance(self.distribution, receptor_projection_baseline)
        encoded = field.snapshot().to_json()

        for forbidden in (
            '"meaning"',
            '"reward"',
            '"topology"',
            '"relationship"',
            '"raw_audio"',
            '"raw_image"',
        ):
            self.assertNotIn(forbidden, encoded)


if __name__ == "__main__":
    unittest.main()
