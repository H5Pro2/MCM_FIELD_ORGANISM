from __future__ import annotations

from dataclasses import FrozenInstanceError
import inspect
from pathlib import Path
import unittest
from unittest.mock import patch

from mcm_field_organism import current_api
import mcm_field_organism._tspm1_private as tspm1
from mcm_field_organism._ppb1_active_receptor_batch_binding import (
    bind_ppb1_active_receptor_batch,
)
from mcm_field_organism._ppb1_receptor_profiles import (
    PPB1ModalityParameters,
    PPB1ProfileParameters,
    bind_ppb1_receptor_profile,
)
from mcm_field_organism.browser_receptor_bridge import BrowserReceptorSequenceBatch
from mcm_field_organism.browser_world_contract import (
    BrowserWorldContract,
    BrowserWorldPhase,
)
from mcm_field_organism.receptor_contract import CommonFieldTime, ReceptorContactFrame
from mcm_field_organism.receptor_time_model import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS


ROOT = Path(__file__).resolve().parents[1]


def profile():
    parameters = PPB1ProfileParameters(
        PPB1ModalityParameters(8, 0.02, 0.05, 3, 256),
        PPB1ModalityParameters(4, 0.01, 0.05, 3, 64),
    )
    return bind_ppb1_receptor_profile("browser", parameters)


def contract() -> BrowserWorldContract:
    return BrowserWorldContract(
        contract_id="synthetic.tspm1.world.v1",
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


def sequence(config, values: tuple[float, ...], *, start_index: int):
    timed = []
    for local_index, scalar in enumerate(values):
        index = start_index + local_index
        start = index * 10
        timed.append(
            OrganismTimedReceptorFrame(
                ReceptorContactFrame(
                    config.modality_id,
                    config.geometry_id,
                    f"synthetic.{config.modality_id}.{index:03d}",
                    f"source.{config.modality_id}",
                    start,
                    start + 10,
                    config.carrier_ids,
                    tuple(scalar for _ in config.carrier_ids),
                ),
                CommonFieldTime("field.synthetic", start, start + 10),
            )
        )
    return ReceptorTimeSequence(
        config.modality_id,
        config.geometry_id,
        "field.synthetic",
        tuple(timed),
    )


def envelope_for(
    bound_profile,
    pairs: tuple[tuple[float, float], ...],
    *,
    start_index: int = 0,
    suffix: str = "main",
):
    world = contract()
    auditory = sequence(
        bound_profile.auditory_config,
        tuple(pair[0] for pair in pairs),
        start_index=start_index,
    )
    visual = sequence(
        bound_profile.visual_config,
        tuple(pair[1] for pair in pairs),
        start_index=start_index,
    )
    batch = BrowserReceptorSequenceBatch(
        world.contract_id,
        world.digest(),
        (auditory, visual),
    )
    return bind_ppb1_active_receptor_batch(
        f"binding.tspm1.{suffix}",
        world,
        batch,
        bound_profile,
    )


def config_for(
    bound_profile,
    *,
    capacity: int = 3,
    threshold: float = 0.2,
    consolidate_after: int = 2,
    expire_after: int = 8,
) -> tspm1.TSPM1ConfigBinding:
    fast = tspm1.TSPM1FastConfig(
        "tspm1.fast",
        capacity,
        threshold,
        threshold,
        0.5,
        consolidate_after,
        expire_after,
    )
    return tspm1.TSPM1ConfigBinding.build(fast, bound_profile)


def exposures(config, envelope):
    return tuple(
        tspm1.bind_tspm1_exposure(config, envelope, auditory, visual)
        for auditory, visual in zip(
            envelope.auditory_stream.timed_frames,
            envelope.visual_stream.timed_frames,
            strict=True,
        )
    )


def advance(config, state, exposure, index: int):
    owner = tspm1.TSPM1CoordinatorOwner(
        f"tspm1.owner.{index:03d}",
        f"tspm1.authorization.{index:03d}",
        f"tspm1.consumption.{index:03d}",
        config.config_binding_digest,
        state.composite_state_digest,
        exposure.exposure_digest,
    )
    return owner, owner.consume_once(config, state, exposure)


class TSPM1S2DHPrivateFastCoreTests(unittest.TestCase):
    def test_source_and_probe_envelopes_bind_original_objects(self) -> None:
        bound_profile = profile()
        config = config_for(bound_profile)
        envelope = envelope_for(bound_profile, ((0.1, 0.2),), suffix="source")
        auditory = envelope.auditory_stream.timed_frames[0]
        visual = envelope.visual_stream.timed_frames[0]

        exposure = tspm1.bind_tspm1_exposure(
            config,
            envelope,
            auditory,
            visual,
        )
        probe = tspm1.bind_tspm1_probe(config, envelope, auditory, visual)

        self.assertIs(exposure.auditory, auditory)
        self.assertIs(exposure.visual, visual)
        self.assertIs(exposure.auditory.timed_frame.frame, auditory.timed_frame.frame)
        self.assertNotEqual(exposure.exposure_digest, probe.probe_digest)
        with self.assertRaises((FrozenInstanceError, AttributeError)):
            exposure.overlap_end_tick = 999  # type: ignore[misc]

    def test_foreign_timed_binding_fails_closed(self) -> None:
        bound_profile = profile()
        config = config_for(bound_profile)
        first = envelope_for(bound_profile, ((0.1, 0.1),), suffix="first")
        second = envelope_for(
            bound_profile,
            ((0.2, 0.2),),
            start_index=1,
            suffix="second",
        )
        with self.assertRaises(tspm1.TSPM1Error) as caught:
            tspm1.bind_tspm1_exposure(
                config,
                first,
                second.auditory_stream.timed_frames[0],
                first.visual_stream.timed_frames[0],
            )
        self.assertEqual(tspm1.TSPM1_SOURCE_PROVENANCE_MISMATCH, caught.exception.code)

    def test_fast_create_update_and_consolidation_are_separate(self) -> None:
        bound_profile = profile()
        config = config_for(bound_profile)
        envelope = envelope_for(
            bound_profile,
            ((0.1, 0.1), (0.1, 0.1), (0.1, 0.1), (0.1, 0.1)),
        )
        source = exposures(config, envelope)
        state = tspm1.initial_tspm1_composite_state(config)

        _, created = advance(config, state, source[0], 0)
        self.assertEqual("FAST_CREATED", created.receipt.primary_event)
        self.assertEqual("NOT_ELIGIBLE", created.receipt.consolidation_status)
        self.assertEqual(0, created.poststate.auditory_ppb1_state.accepted_step_count)

        _, first_commit = advance(config, created.poststate, source[1], 1)
        self.assertEqual("FAST_UPDATED", first_commit.receipt.primary_event)
        self.assertEqual("COMMITTED", first_commit.receipt.consolidation_status)
        self.assertFalse(first_commit.receipt.auditory_ppb1_stabilized)
        self.assertFalse(first_commit.receipt.visual_ppb1_stabilized)
        slot = next(slot for slot in first_commit.poststate.fast_state.slots if slot.occupied)
        self.assertEqual((2, 1), (slot.support_count, slot.consolidation_count))

        _, second_commit = advance(config, first_commit.poststate, source[2], 2)
        _, third_commit = advance(config, second_commit.poststate, source[3], 3)
        self.assertFalse(second_commit.receipt.auditory_ppb1_stabilized)
        self.assertTrue(third_commit.receipt.auditory_ppb1_stabilized)
        self.assertTrue(third_commit.receipt.visual_ppb1_stabilized)
        self.assertEqual(3, third_commit.poststate.auditory_ppb1_state.accepted_step_count)

    def test_partial_association_conflict_creates_without_one_sided_rewrite(self) -> None:
        bound_profile = profile()
        config = config_for(bound_profile, capacity=3)
        envelope = envelope_for(bound_profile, ((0.0, 0.0), (0.1, 0.8)))
        source = exposures(config, envelope)
        state = tspm1.initial_tspm1_composite_state(config)
        _, first = advance(config, state, source[0], 0)
        original = next(slot for slot in first.poststate.fast_state.slots if slot.occupied)

        _, conflicted = advance(config, first.poststate, source[1], 1)

        self.assertTrue(conflicted.receipt.partial_association_conflict)
        self.assertEqual("FAST_CREATED", conflicted.receipt.primary_event)
        preserved = next(
            slot
            for slot in conflicted.poststate.fast_state.slots
            if slot.slot_id == original.slot_id
        )
        self.assertEqual(original, preserved)
        self.assertEqual(2, sum(slot.occupied for slot in conflicted.poststate.fast_state.slots))

    def test_lru_replacement_uses_last_selected_step_then_slot_id(self) -> None:
        bound_profile = profile()
        config = config_for(bound_profile, capacity=2, expire_after=20)
        envelope = envelope_for(
            bound_profile,
            ((0.0, 0.0), (0.5, 0.5), (0.0, 0.0), (0.9, 0.9)),
        )
        source = exposures(config, envelope)
        state = tspm1.initial_tspm1_composite_state(config)
        results = []
        for index, item in enumerate(source):
            _, result = advance(config, state, item, index)
            results.append(result)
            state = result.poststate

        old_second = next(
            slot
            for slot in results[1].poststate.fast_state.slots
            if slot.slot_id.endswith("001")
        )
        self.assertEqual("FAST_REPLACED", results[3].receipt.primary_event)
        self.assertEqual(old_second.digest(), results[3].receipt.replaced_slot_digest)
        replacement = next(
            slot
            for slot in results[3].poststate.fast_state.slots
            if slot.slot_id.endswith("001")
        )
        self.assertEqual((0.9,), tuple(set(replacement.auditory_values)))

    def test_expiry_is_reported_as_ordered_side_axis(self) -> None:
        bound_profile = profile()
        config = config_for(bound_profile, capacity=4, threshold=0.05, expire_after=3)
        envelope = envelope_for(
            bound_profile,
            ((0.0, 0.0), (0.3, 0.3), (0.6, 0.6), (0.9, 0.9)),
        )
        source = exposures(config, envelope)
        state = tspm1.initial_tspm1_composite_state(config)
        first_slot_digest = None
        final = None
        for index, item in enumerate(source):
            _, final = advance(config, state, item, index)
            if index == 0:
                first_slot_digest = next(
                    slot.digest() for slot in final.poststate.fast_state.slots if slot.occupied
                )
            state = final.poststate
        assert final is not None
        self.assertEqual("FAST_CREATED", final.receipt.primary_event)
        self.assertIn(first_slot_digest, final.receipt.expired_slot_digests)

    def test_atomic_failure_of_second_ppb_step_publishes_nothing(self) -> None:
        bound_profile = profile()
        config = config_for(bound_profile)
        envelope = envelope_for(bound_profile, ((0.1, 0.1), (0.1, 0.1)))
        source = exposures(config, envelope)
        state = tspm1.initial_tspm1_composite_state(config)
        _, created = advance(config, state, source[0], 0)
        before = created.poststate.composite_state_digest
        owner = tspm1.TSPM1CoordinatorOwner(
            "tspm1.owner.atomic",
            "tspm1.authorization.atomic",
            "tspm1.consumption.atomic",
            config.config_binding_digest,
            created.poststate.composite_state_digest,
            source[1].exposure_digest,
        )
        real_advance = tspm1.advance_ppb1_bank
        calls = []

        def fail_visual(ppb_config, ppb_state, frame):
            calls.append(frame.modality_id)
            if frame.modality_id == "visual":
                raise RuntimeError("synthetic second PPB failure")
            return real_advance(ppb_config, ppb_state, frame)

        with patch.object(tspm1, "advance_ppb1_bank", side_effect=fail_visual):
            with self.assertRaises(tspm1.TSPM1Error) as caught:
                owner.consume_once(config, created.poststate, source[1])

        self.assertEqual(tspm1.TSPM1_ATTEMPT_FAILED, caught.exception.code)
        self.assertEqual(["auditory", "visual"], calls)
        self.assertEqual("FAILED", owner.snapshot().status)
        self.assertEqual(before, created.poststate.composite_state_digest)
        with self.assertRaises(tspm1.TSPM1Error) as retry:
            owner.consume_once(config, created.poststate, source[1])
        self.assertEqual(tspm1.TSPM1_OWNER_TERMINAL, retry.exception.code)

    def test_stale_exposure_fails_terminally(self) -> None:
        bound_profile = profile()
        config = config_for(bound_profile)
        envelope = envelope_for(bound_profile, ((0.1, 0.1),))
        exposure = exposures(config, envelope)[0]
        state = tspm1.initial_tspm1_composite_state(config)
        _, first = advance(config, state, exposure, 0)
        owner = tspm1.TSPM1CoordinatorOwner(
            "tspm1.owner.stale",
            "tspm1.authorization.stale",
            "tspm1.consumption.stale",
            config.config_binding_digest,
            first.poststate.composite_state_digest,
            exposure.exposure_digest,
        )
        with self.assertRaises(tspm1.TSPM1Error) as caught:
            owner.consume_once(config, first.poststate, exposure)
        self.assertEqual(tspm1.TSPM1_ATTEMPT_FAILED, caught.exception.code)
        self.assertEqual(
            tspm1.TSPM1_CLOCK_ORDER_OR_FIELD_OVERLAP_INVALID,
            owner.snapshot().failure_code,
        )

    def test_read_only_probe_prefers_slow_then_fast_and_changes_no_state(self) -> None:
        bound_profile = profile()
        config = config_for(bound_profile)
        envelope = envelope_for(
            bound_profile,
            (
                (0.1, 0.1),
                (0.1, 0.1),
                (0.1, 0.1),
                (0.1, 0.1),
                (0.1, 0.1),
            ),
        )
        source = exposures(config, envelope)
        state = tspm1.initial_tspm1_composite_state(config)
        _, fast_only = advance(config, state, source[0], 0)
        fast_probe = tspm1.bind_tspm1_probe(
            config,
            envelope,
            envelope.auditory_stream.timed_frames[1],
            envelope.visual_stream.timed_frames[1],
        )
        before_fast = fast_only.poststate.composite_state_digest
        fast_finding = tspm1.probe_tspm1_read_only(
            config,
            fast_only.poststate,
            fast_probe,
        )
        self.assertEqual("FAST_ASSOCIATIVE_CONTEXT", fast_finding.context_source)
        self.assertEqual("SLOW_UNAVAILABLE", fast_finding.auditory_slow_status)
        self.assertEqual(before_fast, fast_only.poststate.composite_state_digest)

        state = fast_only.poststate
        for index in range(1, 4):
            _, result = advance(config, state, source[index], index)
            state = result.poststate
        slow_probe = tspm1.bind_tspm1_probe(
            config,
            envelope,
            envelope.auditory_stream.timed_frames[4],
            envelope.visual_stream.timed_frames[4],
        )
        before_slow = state.composite_state_digest
        slow_finding = tspm1.probe_tspm1_read_only(config, state, slow_probe)
        self.assertEqual("SLOW_PPB1_CONTEXT", slow_finding.context_source)
        self.assertEqual("SLOW_RECOGNIZED", slow_finding.auditory_slow_status)
        self.assertEqual(before_slow, state.composite_state_digest)

    def test_fresh_state_probe_returns_no_complete_context(self) -> None:
        bound_profile = profile()
        config = config_for(bound_profile)
        envelope = envelope_for(bound_profile, ((0.1, 0.1),), suffix="fresh")
        state = tspm1.initial_tspm1_composite_state(config)
        probe = tspm1.bind_tspm1_probe(
            config,
            envelope,
            envelope.auditory_stream.timed_frames[0],
            envelope.visual_stream.timed_frames[0],
        )
        finding = tspm1.probe_tspm1_read_only(config, state, probe)
        self.assertEqual("NO_COMPLETE_CONTEXT", finding.context_source)
        self.assertEqual("SLOW_UNAVAILABLE", finding.auditory_slow_status)
        self.assertEqual("SLOW_UNAVAILABLE", finding.visual_slow_status)

    def test_private_boundary_and_direct_original_frame_calls(self) -> None:
        source = inspect.getsource(tspm1.TSPM1CoordinatorOwner.consume_once)
        self.assertEqual(2, source.count("advance_ppb1_bank("))
        self.assertIn("exposure.auditory.timed_frame.frame", source)
        self.assertIn("exposure.visual.timed_frame.frame", source)
        self.assertNotIn("ReceptorContactFrame(", source)

        module_source = (
            ROOT / "mcm_field_organism" / "_tspm1_private.py"
        ).read_text(encoding="ascii")
        for forbidden in ("SharedMCMField", "MCMNeuronDrive", "root_lazy_exports"):
            self.assertNotIn(forbidden, module_source)
        public_names = set(getattr(current_api, "__all__", ())) | set(ROOT_LAZY_EXPORTS)
        self.assertFalse(any("tspm" in name.lower() for name in public_names))


if __name__ == "__main__":
    unittest.main()
