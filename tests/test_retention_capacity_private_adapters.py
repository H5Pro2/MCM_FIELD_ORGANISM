"""Eight focused synthetic checks for the private retention adapters."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from mcm_field_organism import _tspm1_private as tspm1
from mcm_field_organism import _tspm1_s2dr_private_comparison as comparison
from mcm_field_organism._ppb1_active_receptor_batch_binding import (
    bind_ppb1_active_receptor_batch,
)
from mcm_field_organism._ppb1_receptor_profiles import (
    PPB1ModalityParameters,
    PPB1ProfileParameters,
    bind_ppb1_receptor_profile,
)
from mcm_field_organism.browser_receptor_bridge import BrowserReceptorSequenceBatch
from mcm_field_organism.browser_world_contract import BrowserWorldContract, BrowserWorldPhase
from mcm_field_organism.receptor_contract import CommonFieldTime, ReceptorContactFrame
from mcm_field_organism.receptor_time_model import OrganismTimedReceptorFrame, ReceptorTimeSequence
from tools import _retention_capacity_read_only as read_only


def _av(auditory: float, visual: float) -> tuple[float, ...]:
    return (auditory,) * 8 + (visual,) * 18


def _b4_state(accepted_count: int, indexes: tuple[int, ...], values: tuple[float, ...]):
    occupied = len(indexes)
    entries = tuple(
        comparison._FIFOEntry(
            f"b4.slot.{slot:03d}",
            slot < occupied,
            values if slot < occupied else (),
            indexes[slot] if slot < occupied else None,
        )
        for slot in range(9)
    )
    return comparison._B4State(accepted_count, entries)


def _profile():
    return bind_ppb1_receptor_profile(
        "browser",
        PPB1ProfileParameters(
            PPB1ModalityParameters(8, 0.02, 0.05, 3, 256),
            PPB1ModalityParameters(4, 0.01, 0.05, 3, 64),
        ),
    )


def _world() -> BrowserWorldContract:
    return BrowserWorldContract(
        contract_id="synthetic.retention.adapter.world.v1",
        startup_frame_count=1,
        start_lead_ns=1,
        movement_cycles=1,
        tone_frequency_hz=100.0,
        phases=(
            BrowserWorldPhase("rest.before", 10, "static", 0.0),
            BrowserWorldPhase("change", 10, "moving", 0.2),
            BrowserWorldPhase("rest.after", 10, "static", 0.0),
        ),
    )


def _sequence(config, scalars: tuple[float, ...]) -> ReceptorTimeSequence:
    timed = tuple(
        OrganismTimedReceptorFrame(
            ReceptorContactFrame(
                config.modality_id,
                config.geometry_id,
                f"synthetic.retention.{config.modality_id}.{index:03d}",
                f"synthetic.retention.{config.modality_id}.clock",
                index * 10,
                (index + 1) * 10,
                config.carrier_ids,
                tuple(scalar for _ in config.carrier_ids),
            ),
            CommonFieldTime("synthetic.retention.field.clock", index * 10, (index + 1) * 10),
        )
        for index, scalar in enumerate(scalars)
    )
    return ReceptorTimeSequence(
        config.modality_id,
        config.geometry_id,
        "synthetic.retention.field.clock",
        timed,
    )


def _state_and_probe(
    exposure_pairs: tuple[tuple[float, float], ...],
    probe_pair: tuple[float, float],
):
    profile = _profile()
    config = tspm1.TSPM1ConfigBinding.build(
        tspm1.TSPM1FastConfig("tspm1.fast", 3, 0.2, 0.2, 0.5, 2, 8),
        profile,
    )
    all_pairs = exposure_pairs + (probe_pair,)
    world = _world()
    batch = BrowserReceptorSequenceBatch(
        world.contract_id,
        world.digest(),
        (
            _sequence(profile.auditory_config, tuple(pair[0] for pair in all_pairs)),
            _sequence(profile.visual_config, tuple(pair[1] for pair in all_pairs)),
        ),
    )
    envelope = bind_ppb1_active_receptor_batch(
        "binding.retention.adapter.synthetic",
        world,
        batch,
        profile,
    )
    state = tspm1.initial_tspm1_composite_state(config)
    for index in range(len(exposure_pairs)):
        exposure = tspm1.bind_tspm1_exposure(
            config,
            envelope,
            envelope.auditory_stream.timed_frames[index],
            envelope.visual_stream.timed_frames[index],
        )
        owner = tspm1.TSPM1CoordinatorOwner(
            f"tspm1.owner.retention.{index:03d}",
            f"tspm1.authorization.retention.{index:03d}",
            f"tspm1.consumption.retention.{index:03d}",
            config.config_binding_digest,
            state.composite_state_digest,
            exposure.exposure_digest,
        )
        state = owner.consume_once(config, state, exposure).poststate
    probe_index = len(exposure_pairs)
    probe = tspm1.bind_tspm1_probe(
        config,
        envelope,
        envelope.auditory_stream.timed_frames[probe_index],
        envelope.visual_stream.timed_frames[probe_index],
    )
    return config, state, probe


class RetentionCapacityPrivateAdapterTests(unittest.TestCase):
    def test_01_values_reject_coercion_bool_and_non_tuple_containers(self) -> None:
        self.assertEqual((0.0, 1.0), read_only._values((0, 1.0), 2, "unit"))
        for invalid in (("0.0", 1.0), (False, 1.0), [0.0, 1.0], iter((0.0, 1.0))):
            with self.subTest(invalid=type(invalid).__name__):
                with self.assertRaises(read_only.RetentionReadOnlyError):
                    read_only._values(invalid, 2, "unit")

    def test_02_b4_incomplete_count_and_stale_fifo_window_fail_closed(self) -> None:
        probe = _av(0.0, 0.25)
        with self.assertRaises(read_only.RetentionReadOnlyError):
            read_only.probe_b4_content_read_only(_b4_state(1, (), probe), probe)
        with self.assertRaises(read_only.RetentionReadOnlyError):
            read_only.probe_b4_content_read_only(
                _b4_state(10, tuple(range(1, 10)), probe),
                probe,
            )

    def test_03_b4_read_only_selects_one_synthetic_current_slot(self) -> None:
        stored = _av(0.0, 0.25)
        state = _b4_state(1, (1,), stored)
        before = comparison._canonical(state)
        finding = read_only.probe_b4_content_read_only(state, stored)
        self.assertTrue(finding.recognized)
        self.assertEqual(("b4.slot.000", 1, stored), (
            finding.selected.slot_id,
            finding.selected.formation_index,
            finding.selected.values,
        ))
        self.assertEqual(finding.prestate_digest, finding.poststate_digest)
        self.assertEqual(before, comparison._canonical(state))

    def test_04_b4_complete_rolling_window_prefers_latest_equal_match(self) -> None:
        stored = _av(0.0, 0.36)
        state = _b4_state(10, tuple(range(2, 11)), stored)
        finding = read_only.probe_b4_content_read_only(state, stored)
        self.assertEqual(9, finding.occupied_slot_count)
        self.assertEqual(10, finding.selected.formation_index)
        self.assertEqual("b4.slot.008", finding.selected.slot_id)

    def test_05_tspm_fast_only_uses_one_native_probe_and_is_read_only(self) -> None:
        config, state, probe = _state_and_probe(((0.12, 0.24),), (0.12, 0.24))
        before = state.composite_state_digest
        native = tspm1.probe_tspm1_read_only
        with patch.object(tspm1, "probe_tspm1_read_only", wraps=native) as called:
            finding = read_only.probe_tspm1_content_read_only(config, state, probe)
        self.assertEqual(1, called.call_count)
        self.assertTrue(finding.native_fast_recognized)
        self.assertEqual("SLOW_UNAVAILABLE", finding.auditory_slow.native_status)
        self.assertEqual(finding.prestate_component_digests, finding.poststate_component_digests)
        self.assertEqual(before, state.composite_state_digest)

    def test_06_tspm_support_one_is_present_but_not_stable(self) -> None:
        config, state, probe = _state_and_probe(
            ((0.14, 0.28), (0.14, 0.28)),
            (0.14, 0.28),
        )
        finding = read_only.probe_tspm1_content_read_only(config, state, probe)
        self.assertEqual("SLOW_NOT_RECOGNIZED", finding.visual_slow.native_status)
        self.assertEqual(0, finding.visual_slow.eligible_slot_count)
        self.assertEqual((1, False), (
            finding.visual_slow.slots[0].support_count,
            finding.visual_slow.slots[0].stable,
        ))

    def test_07_tspm_support_three_is_stable_and_slow_readable(self) -> None:
        config, state, probe = _state_and_probe(
            ((0.16, 0.32),) * 4,
            (0.16, 0.32),
        )
        before = state.composite_state_digest
        finding = read_only.probe_tspm1_content_read_only(config, state, probe)
        self.assertEqual("SLOW_RECOGNIZED", finding.visual_slow.native_status)
        self.assertEqual((3, True), (
            finding.visual_slow.selected.support_count,
            finding.visual_slow.selected.stable,
        ))
        self.assertEqual((0.32,) * 18, finding.visual_slow.selected.prototype_values)
        self.assertEqual(before, finding.prestate_digest)
        self.assertEqual(before, finding.poststate_digest)

    def test_08_native_and_functional_slow_thresholds_remain_separate(self) -> None:
        config, state, probe = _state_and_probe(
            ((0.18, 0.40),) * 4,
            (0.18, 0.44),
        )
        finding = read_only.probe_tspm1_content_read_only(config, state, probe)
        self.assertEqual("SLOW_NOT_RECOGNIZED", finding.visual_slow.native_status)
        self.assertAlmostEqual(0.04, finding.visual_slow.selected.native_distance)
        self.assertTrue(finding.visual_slow.functional_recognized)
        self.assertTrue(finding.functional_slow_recognized)
        self.assertEqual((44, 765), (
            finding.functional_visual_threshold_numerator,
            finding.functional_visual_threshold_denominator,
        ))


if __name__ == "__main__":
    unittest.main()
