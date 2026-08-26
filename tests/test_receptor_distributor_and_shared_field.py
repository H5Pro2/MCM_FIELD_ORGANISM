from __future__ import annotations

import json
import unittest

from mcm_field_organism import (
    CommonFieldTime,
    MCMFieldStepTime,
    MCMNeuronDrive,
    MCMNeuronOutput,
    MCMSubstrateArmContract,
    ReceptorContactFrame,
    ReceptorDistribution,
    ReceptorDistributionError,
    ReceptorDistributor,
    ReceptorDock,
    ReceptorDockAnatomy,
    SharedMCMFieldError,
    SharedMCMFieldSnapshot,
    TransientNeuronDockInput,
    TransientNeuronInputSet,
    attach_uniform_mcm_substrate,
    build_shared_mcm_field,
    hold_state_baseline,
    migrate_shared_mcm_field_snapshot_to_schema2,
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


def transient_input_set(field, distribution) -> TransientNeuronInputSet:
    field_time = distribution.field_time
    step_time = MCMFieldStepTime(
        clock_id=field_time.clock_id,
        start_tick=field_time.window_start_tick,
        end_tick=field_time.window_end_tick,
        ticks_per_second=1000.0,
    )
    return TransientNeuronInputSet(
        step_time=step_time,
        neuron_inputs=tuple(
            TransientNeuronDockInput(
                neuron_id=neuron_id,
                dock_id=dock.dock_id,
                carrier_id=carrier_id,
                step_time=step_time,
                contacts=(),
            )
            for dock in field.docks
            for carrier_id, neuron_id in dock.dock_map.pairs
        ),
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

    def test_contact_free_distribution_represents_absence_without_a_value(self) -> None:
        distributor = self.distributor()
        result = distributor.distribute((), self.field_time)

        self.assertEqual((), result.contacts)
        self.assertEqual((), result.dock_ids)
        self.assertEqual((), result.modality_ids)
        self.assertEqual(distributor.docks, self.distributor().docks)

        with self.assertRaisesRegex(ReceptorDistributionError, "attached"):
            ReceptorDistributor().distribute((), self.field_time)

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

    def test_contact_free_field_interval_is_absence_and_roundtrips(self) -> None:
        field = build_shared_mcm_field(
            (self.audio, self.video),
            self.anatomies,
            sample_offsets=FIELD_SAMPLE_OFFSETS,
        )
        empty = ReceptorDistribution(
            CommonFieldTime("organism.test", 100, 180),
            (),
        )
        inputs = transient_input_set(field, empty)
        observed = {}

        def observer(drive: MCMNeuronDrive) -> MCMNeuronOutput:
            observed[drive.previous.neuron_id] = (
                drive.perception.receptor_contact,
                drive.transient_receptor_input,
            )
            return MCMNeuronOutput(
                drive.previous.activation,
                drive.previous.afterimage,
            )

        advanced = field.advance(
            empty,
            observer,
            transient_neuron_inputs=inputs,
        )
        self.assertTrue(all(
            contact is None and transient is not None
            for contact, transient in observed.values()
        ))
        self.assertEqual((), advanced.last_distribution.contacts)

        restored = restore_shared_mcm_field(
            SharedMCMFieldSnapshot.from_json(advanced.snapshot().to_json())
        )
        self.assertEqual(
            advanced.snapshot().digest(),
            restored.snapshot().digest(),
        )

    def test_complete_transient_input_set_reaches_shared_layer_atomically(self) -> None:
        field = build_shared_mcm_field(
            (self.audio, self.video),
            self.anatomies,
            sample_offsets=FIELD_SAMPLE_OFFSETS,
        )
        inputs = transient_input_set(field, self.distribution)
        expected = {
            item.neuron_id: item for item in inputs.neuron_inputs
        }
        observed = {}

        def observer(drive: MCMNeuronDrive) -> MCMNeuronOutput:
            observed[drive.previous.neuron_id] = drive.transient_receptor_input
            return MCMNeuronOutput(
                drive.previous.activation,
                drive.previous.afterimage,
            )

        advanced = field.advance(
            self.distribution,
            observer,
            transient_neuron_inputs=inputs,
        )

        self.assertEqual(set(expected), set(observed))
        self.assertTrue(all(observed[key] is expected[key] for key in expected))
        self.assertNotIn("transient", advanced.snapshot().to_json())

    def test_ignored_shared_transient_input_cannot_change_field_state(self) -> None:
        field = build_shared_mcm_field(
            (self.audio, self.video),
            self.anatomies,
            sample_offsets=FIELD_SAMPLE_OFFSETS,
        )
        without = field.advance(self.distribution, hold_state_baseline)
        with_inputs = field.advance(
            self.distribution,
            hold_state_baseline,
            transient_neuron_inputs=transient_input_set(
                field,
                self.distribution,
            ),
        )
        self.assertEqual(without.snapshot().digest(), with_inputs.snapshot().digest())

    def test_shared_field_rejects_wrong_transient_anatomy_or_time(self) -> None:
        field = build_shared_mcm_field(
            (self.audio, self.video),
            self.anatomies,
            sample_offsets=FIELD_SAMPLE_OFFSETS,
        )
        valid = transient_input_set(field, self.distribution)
        first, *rest = valid.neuron_inputs
        incomplete = TransientNeuronInputSet(
            step_time=valid.step_time,
            neuron_inputs=tuple(rest),
        )
        with self.assertRaisesRegex(SharedMCMFieldError, "match every"):
            field.advance(
                self.distribution,
                hold_state_baseline,
                transient_neuron_inputs=incomplete,
            )

        wrong_anatomy = TransientNeuronInputSet(
            step_time=valid.step_time,
            neuron_inputs=(
                TransientNeuronDockInput(
                    neuron_id=first.neuron_id,
                    dock_id="dock.wrong",
                    carrier_id=first.carrier_id,
                    step_time=valid.step_time,
                    contacts=(),
                ),
                *rest,
            ),
        )
        with self.assertRaisesRegex(SharedMCMFieldError, "anatomy mismatch"):
            field.advance(
                self.distribution,
                hold_state_baseline,
                transient_neuron_inputs=wrong_anatomy,
            )

        wrong_time = MCMFieldStepTime(
            clock_id="organism.test",
            start_tick=180,
            end_tick=260,
            ticks_per_second=1000.0,
        )
        shifted = TransientNeuronInputSet(
            step_time=wrong_time,
            neuron_inputs=tuple(
                TransientNeuronDockInput(
                    neuron_id=item.neuron_id,
                    dock_id=item.dock_id,
                    carrier_id=item.carrier_id,
                    step_time=wrong_time,
                    contacts=(),
                )
                for item in valid.neuron_inputs
            ),
        )
        with self.assertRaisesRegex(SharedMCMFieldError, "time must equal"):
            field.advance(
                self.distribution,
                hold_state_baseline,
                transient_neuron_inputs=shifted,
            )

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

    def test_schema_one_digest_and_payload_remain_the_fast_field_contract(self) -> None:
        field = build_shared_mcm_field(
            (self.audio, self.video),
            self.anatomies,
            sample_offsets=FIELD_SAMPLE_OFFSETS,
        ).advance(self.distribution, receptor_projection_baseline)

        snapshot = field.snapshot()

        self.assertEqual(1, snapshot.schema_version)
        self.assertIsNone(snapshot.substrate)
        self.assertEqual(snapshot.digest(), snapshot.fast_state_projection_digest())
        self.assertEqual(
            {"schema_version", "layer", "docks", "last_distribution"},
            set(json.loads(snapshot.to_json())),
        )

    def test_explicit_schema_two_migration_preserves_fast_projection(self) -> None:
        field = build_shared_mcm_field(
            (self.audio, self.video),
            self.anatomies,
            sample_offsets=FIELD_SAMPLE_OFFSETS,
        ).advance(self.distribution, receptor_projection_baseline)
        legacy = field.snapshot()
        arm = MCMSubstrateArmContract("p0.null", 0.0, 0.25, 0.5)

        migrated = migrate_shared_mcm_field_snapshot_to_schema2(legacy, arm)
        loaded = SharedMCMFieldSnapshot.from_json(migrated.to_json())
        restored = restore_shared_mcm_field(loaded)

        self.assertEqual(2, migrated.schema_version)
        self.assertEqual(legacy.digest(), migrated.fast_state_projection_digest())
        self.assertEqual(migrated.digest(), restored.snapshot().digest())
        self.assertEqual(arm, restored.substrate.arm)
        self.assertAlmostEqual(1.0, restored.substrate.total_mass)
        self.assertEqual(
            tuple(neuron.neuron_id for neuron in field.layer.neurons),
            restored.substrate.neuron_ids,
        )
        self.assertEqual(
            {"schema_version", "layer", "docks", "last_distribution", "substrate"},
            set(json.loads(migrated.to_json())),
        )

    def test_null_substrate_keeps_the_existing_next_fast_state_exact(self) -> None:
        legacy = build_shared_mcm_field(
            (self.audio, self.video),
            self.anatomies,
            sample_offsets=FIELD_SAMPLE_OFFSETS,
        ).advance(self.distribution, receptor_projection_baseline)
        null_field = attach_uniform_mcm_substrate(
            legacy,
            MCMSubstrateArmContract("p0.null", 0.0, 0.25, 0.5),
        )
        next_distribution = ReceptorDistribution(
            CommonFieldTime("organism.test", 180, 260),
            self.distribution.contacts,
        )

        legacy_next = legacy.advance(
            next_distribution,
            receptor_projection_baseline,
        )
        null_next = null_field.advance(
            next_distribution,
            receptor_projection_baseline,
        )

        self.assertEqual(
            legacy_next.snapshot().digest(),
            null_next.snapshot().fast_state_projection_digest(),
        )
        self.assertEqual(
            null_field.substrate.digest(),
            null_next.substrate.digest(),
        )

    def test_schema_two_rejects_invalid_or_hidden_substrate_state(self) -> None:
        field = build_shared_mcm_field(
            (self.audio, self.video),
            self.anatomies,
            sample_offsets=FIELD_SAMPLE_OFFSETS,
        ).advance(self.distribution, receptor_projection_baseline)
        migrated = migrate_shared_mcm_field_snapshot_to_schema2(
            field.snapshot(),
            MCMSubstrateArmContract("p0.null", 0.0, 0.25, 0.5),
        )

        payload = json.loads(migrated.to_json())
        payload["substrate"]["masses"][0]["mass"] = -0.1
        with self.assertRaisesRegex(SharedMCMFieldError, "runtime contract"):
            SharedMCMFieldSnapshot.from_json(json.dumps(payload))

        payload = json.loads(migrated.to_json())
        payload["substrate"]["reader"] = "pattern"
        with self.assertRaisesRegex(SharedMCMFieldError, "runtime contract"):
            SharedMCMFieldSnapshot.from_json(json.dumps(payload))

        payload = json.loads(migrated.to_json())
        del payload["substrate"]
        with self.assertRaisesRegex(SharedMCMFieldError, "missing"):
            SharedMCMFieldSnapshot.from_json(json.dumps(payload))

    def test_scheme_a_rejects_active_substrate_attachment(self) -> None:
        field = build_shared_mcm_field(
            (self.audio, self.video),
            self.anatomies,
            sample_offsets=FIELD_SAMPLE_OFFSETS,
        )
        with self.assertRaisesRegex(SharedMCMFieldError, "exact null"):
            attach_uniform_mcm_substrate(
                field,
                MCMSubstrateArmContract("p1.active", 0.1, 0.25, 0.5),
            )

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
