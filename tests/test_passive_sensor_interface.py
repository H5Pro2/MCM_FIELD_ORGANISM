from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from itertools import permutations
import math
import unittest

from mcm_field_organism import (
    CanonicalFrameSet,
    InterfaceValidationError,
    PassiveSnapshotGate,
    Presence,
    SensorFieldState,
    Validity,
    numeric_sum_baseline,
)


CARRIERS = ("carrier.0", "carrier.1")
ZERO = (0.0, 0.0)


def state(
    modality: str,
    *,
    timestamp: int = 1,
    suffix: str = "1",
    presence: Presence = Presence.ACTIVE_FIELD,
    activation: tuple[float, ...] = (0.5, -0.25),
    afterimage: tuple[float, ...] = (0.1, 0.0),
    resources: tuple[float, ...] = (1.0, 0.8),
) -> SensorFieldState:
    channel = f"{modality}.primary"
    if presence is Presence.MISSING:
        return SensorFieldState(
            modality_id=modality,
            channel_id=channel,
            snapshot_id=f"{modality}.{suffix}",
            timestamp=timestamp,
            geometry_id=None,
            carrier_ids=(),
            activation=(),
            afterimage=(),
            local_resources=(),
            presence=presence,
            validity=Validity.ABSENT,
        )
    if presence is Presence.UNAVAILABLE:
        return SensorFieldState(
            modality_id=modality,
            channel_id=channel,
            snapshot_id=f"{modality}.{suffix}",
            timestamp=timestamp,
            geometry_id=None,
            carrier_ids=(),
            activation=(),
            afterimage=(),
            local_resources=(),
            presence=presence,
            validity=Validity.UNAVAILABLE,
        )
    if presence in {Presence.NO_CONTACT, Presence.ACTIVE_ZERO}:
        activation = ZERO
    return SensorFieldState(
        modality_id=modality,
        channel_id=channel,
        snapshot_id=f"{modality}.{suffix}",
        timestamp=timestamp,
        geometry_id=f"{modality}.geometry.1",
        carrier_ids=CARRIERS,
        activation=activation,
        afterimage=afterimage,
        local_resources=resources,
        presence=presence,
        validity=Validity.VALID,
    )


def triad(*, timestamp: int = 1, suffix: str = "1") -> tuple[SensorFieldState, ...]:
    return (
        state("visual", timestamp=timestamp, suffix=f"v{suffix}"),
        state("auditory", timestamp=timestamp, suffix=f"a{suffix}"),
        state("tactile", timestamp=timestamp, suffix=f"t{suffix}"),
    )


class SensorFieldStateTests(unittest.TestCase):
    def test_state_is_immutable_and_sequences_become_tuples(self) -> None:
        item = SensorFieldState(
            modality_id="visual",
            channel_id="visual.primary",
            snapshot_id="visual.1",
            timestamp=1,
            geometry_id="visual.geometry.1",
            carrier_ids=["carrier.0", "carrier.1"],
            activation=[0.2, -0.1],
            afterimage=[0.0, 0.1],
            local_resources=[1.0, 1.0],
            presence=Presence.ACTIVE_FIELD,
            validity=Validity.VALID,
        )
        self.assertEqual((0.2, -0.1), item.activation)
        with self.assertRaises(FrozenInstanceError):
            item.timestamp = 2

    def test_mapping_requires_exactly_the_registered_roles(self) -> None:
        payload = state("visual").canonical_payload()
        rebuilt = SensorFieldState.from_mapping(payload)
        self.assertEqual(state("visual"), rebuilt)

        payload["raw_sensor"] = [1, 2, 3]
        with self.assertRaisesRegex(InterfaceValidationError, "unknown=.*raw_sensor"):
            SensorFieldState.from_mapping(payload)

    def test_all_presence_families_are_representable(self) -> None:
        families = (
            state("visual", presence=Presence.MISSING),
            state("visual", presence=Presence.UNAVAILABLE),
            state("visual", presence=Presence.NO_CONTACT, afterimage=(0.2, 0.1)),
            state("visual", presence=Presence.ACTIVE_ZERO),
            state("visual", presence=Presence.ACTIVE_FIELD),
        )
        self.assertEqual(tuple(Presence), tuple(item.presence for item in families))

    def test_no_contact_and_active_zero_remain_distinct_with_equal_vectors(self) -> None:
        no_contact = state("visual", presence=Presence.NO_CONTACT, afterimage=ZERO)
        active_zero = state("visual", presence=Presence.ACTIVE_ZERO, afterimage=ZERO)
        self.assertEqual(no_contact.activation, active_zero.activation)
        self.assertNotEqual(
            CanonicalFrameSet((no_contact,)).digest(),
            CanonicalFrameSet((active_zero,)).digest(),
        )

    def test_equal_numbers_in_different_modalities_remain_distinct(self) -> None:
        visual = state("visual")
        auditory = state("auditory")
        self.assertEqual(visual.activation, auditory.activation)
        self.assertNotEqual(
            CanonicalFrameSet((visual,)).digest(),
            CanonicalFrameSet((auditory,)).digest(),
        )

    def test_new_technical_modality_is_not_blocked_by_a_closed_enum(self) -> None:
        vestibular = state("vestibular")
        self.assertEqual("vestibular", vestibular.modality_id)

    def test_invalid_presence_vector_combinations_are_rejected(self) -> None:
        with self.assertRaisesRegex(InterfaceValidationError, "requires zero"):
            replace(
                state("visual", presence=Presence.NO_CONTACT),
                activation=(0.1, 0.0),
            )
        with self.assertRaisesRegex(InterfaceValidationError, "requires non-zero"):
            state("visual", presence=Presence.ACTIVE_FIELD, activation=ZERO)

    def test_nonfinite_and_negative_resource_values_are_rejected(self) -> None:
        with self.assertRaisesRegex(InterfaceValidationError, "finite"):
            state("visual", activation=(math.nan, 0.0))
        with self.assertRaisesRegex(InterfaceValidationError, "cannot be negative"):
            state("visual", resources=(1.0, -0.1))

    def test_geometry_lengths_and_carrier_identity_are_checked(self) -> None:
        with self.assertRaisesRegex(InterfaceValidationError, "match carrier geometry"):
            SensorFieldState(
                modality_id="visual",
                channel_id="visual.primary",
                snapshot_id="visual.1",
                timestamp=1,
                geometry_id="visual.geometry.1",
                carrier_ids=CARRIERS,
                activation=(0.2,),
                afterimage=ZERO,
                local_resources=ZERO,
                presence=Presence.ACTIVE_FIELD,
                validity=Validity.VALID,
            )


class CanonicalFrameSetTests(unittest.TestCase):
    def test_all_six_delivery_permutations_have_identical_digest(self) -> None:
        digests = {CanonicalFrameSet(order).digest() for order in permutations(triad())}
        self.assertEqual(1, len(digests))

    def test_single_pair_and_triple_states_are_accepted(self) -> None:
        visual, auditory, tactile = triad()
        self.assertEqual(1, len(CanonicalFrameSet((visual,)).states))
        self.assertEqual(2, len(CanonicalFrameSet((visual, auditory)).states))
        self.assertEqual(3, len(CanonicalFrameSet((visual, auditory, tactile)).states))

    def test_all_missing_channels_are_explicitly_represented(self) -> None:
        items = tuple(state(name, presence=Presence.MISSING) for name in ("visual", "auditory", "tactile"))
        frame = CanonicalFrameSet(items)
        self.assertEqual({"missing"}, {item["presence"] for item in frame.canonical_payload()})

    def test_mixed_timestamps_are_rejected(self) -> None:
        visual = state("visual", timestamp=1)
        auditory = state("auditory", timestamp=2)
        with self.assertRaisesRegex(InterfaceValidationError, "cannot mix timestamps"):
            CanonicalFrameSet((visual, auditory))

    def test_duplicate_channel_and_snapshot_identity_are_rejected(self) -> None:
        first = state("visual", suffix="one")
        duplicate_channel = state("visual", suffix="two")
        with self.assertRaisesRegex(InterfaceValidationError, "pairs must be unique"):
            CanonicalFrameSet((first, duplicate_channel))

        second = replace(state("auditory", suffix="one"), snapshot_id=first.snapshot_id)
        with self.assertRaisesRegex(InterfaceValidationError, "snapshot_id values must be unique"):
            CanonicalFrameSet((first, second))

    def test_canonical_payload_contains_only_registered_roles(self) -> None:
        payload = CanonicalFrameSet(triad()).canonical_payload()
        self.assertEqual(
            {
                "modality_id",
                "channel_id",
                "snapshot_id",
                "timestamp",
                "geometry_id",
                "carrier_ids",
                "activation",
                "afterimage",
                "local_resources",
                "presence",
                "validity",
            },
            set(payload[0]),
        )


class PassiveSnapshotGateTests(unittest.TestCase):
    def test_observer_is_read_only_and_does_not_change_digest(self) -> None:
        observations: list[str] = []

        def observer(frame: CanonicalFrameSet) -> None:
            observations.append(frame.digest())
            with self.assertRaises(FrozenInstanceError):
                frame.states = ()

        gate = PassiveSnapshotGate()
        accepted = gate.accept(triad(), observer=observer)
        self.assertEqual([accepted.digest()], observations)

        without_observer = PassiveSnapshotGate().accept(triad())
        self.assertEqual(without_observer.digest(), accepted.digest())

    def test_stale_equal_and_duplicate_snapshots_are_rejected_without_state_change(self) -> None:
        gate = PassiveSnapshotGate()
        gate.accept(triad(timestamp=2, suffix="first"))
        before = (gate.last_timestamp, gate.seen_snapshot_ids)

        for rejected in (
            triad(timestamp=1, suffix="stale"),
            triad(timestamp=2, suffix="equal"),
            triad(timestamp=3, suffix="first"),
        ):
            with self.assertRaises(InterfaceValidationError):
                gate.accept(rejected)
            self.assertEqual(before, (gate.last_timestamp, gate.seen_snapshot_ids))

    def test_reset_removes_only_technical_chronology(self) -> None:
        gate = PassiveSnapshotGate()
        expected = gate.accept(triad(timestamp=1, suffix="base")).digest()
        gate.accept(triad(timestamp=2, suffix="contrast"))
        gate.reset()

        self.assertIsNone(gate.last_timestamp)
        self.assertEqual(frozenset(), gate.seen_snapshot_ids)
        repeated = gate.accept(triad(timestamp=1, suffix="base"))
        self.assertEqual(expected, repeated.digest())

    def test_controlled_later_frame_is_accepted(self) -> None:
        gate = PassiveSnapshotGate()
        first = gate.accept(triad(timestamp=1, suffix="first"))
        second = gate.accept(triad(timestamp=2, suffix="second"))
        self.assertLess(first.timestamp, second.timestamp)


class BaselineTests(unittest.TestCase):
    def test_b0_and_b1_preserve_modality_distribution(self) -> None:
        items = triad()
        b0 = {item.modality_id: item.activation for item in items}
        b1 = CanonicalFrameSet(items).canonical_payload()
        self.assertEqual(set(b0), {item["modality_id"] for item in b1})

    def test_b2_has_expected_modality_collision(self) -> None:
        first = (
            state("visual", activation=(1.0, 0.0), afterimage=ZERO),
            state("auditory", activation=(0.0, 1.0), afterimage=ZERO),
        )
        second = (
            state("visual", suffix="2", activation=(0.0, 1.0), afterimage=ZERO),
            state("auditory", suffix="2", activation=(1.0, 0.0), afterimage=ZERO),
        )
        self.assertEqual(numeric_sum_baseline(first), numeric_sum_baseline(second))
        self.assertNotEqual(CanonicalFrameSet(first).digest(), CanonicalFrameSet(second).digest())

    def test_b2_rejects_incompatible_geometries(self) -> None:
        short = state("visual")
        long = SensorFieldState(
            modality_id="auditory",
            channel_id="auditory.primary",
            snapshot_id="auditory.long",
            timestamp=1,
            geometry_id="auditory.geometry.1",
            carrier_ids=("carrier.0", "carrier.1", "carrier.2"),
            activation=(0.1, 0.2, 0.3),
            afterimage=(0.0, 0.0, 0.0),
            local_resources=(1.0, 1.0, 1.0),
            presence=Presence.ACTIVE_FIELD,
            validity=Validity.VALID,
        )
        with self.assertRaisesRegex(InterfaceValidationError, "geometrically compatible"):
            numeric_sum_baseline((short, long))


if __name__ == "__main__":
    unittest.main()
