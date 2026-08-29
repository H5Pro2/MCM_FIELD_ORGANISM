"""Neutral contract tests for the private S2-FS atomic coordinator."""

from __future__ import annotations

from dataclasses import fields
from pathlib import Path
import unittest
from unittest.mock import patch

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism import _tspm1_private as tspm1
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
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from tools import _s2fs_b4_tspm1_private_coordinator as coordinator


ROOT = Path(__file__).resolve().parents[1]


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
        contract_id="synthetic.s2fs.world.v1",
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
                f"synthetic.s2fs.{config.modality_id}.{index:03d}",
                f"synthetic.s2fs.{config.modality_id}.clock",
                index * 10,
                (index + 1) * 10,
                config.carrier_ids,
                tuple(scalar for _ in config.carrier_ids),
            ),
            CommonFieldTime("synthetic.s2fs.field.clock", index * 10, (index + 1) * 10),
        )
        for index, scalar in enumerate(scalars)
    )
    return ReceptorTimeSequence(
        config.modality_id,
        config.geometry_id,
        "synthetic.s2fs.field.clock",
        timed,
    )


def _fixture(pairs: tuple[tuple[float, float], ...] = ((0.12, 0.28), (0.14, 0.32))):
    profile = _profile()
    tspm_config = tspm1.TSPM1ConfigBinding.build(
        tspm1.TSPM1FastConfig("tspm1.fast", 3, 0.2, 0.2, 0.5, 2, 8),
        profile,
    )
    config = coordinator.build_coordinator_config(tspm_config)
    world = _world()
    batch = BrowserReceptorSequenceBatch(
        world.contract_id,
        world.digest(),
        (
            _sequence(profile.auditory_config, tuple(pair[0] for pair in pairs)),
            _sequence(profile.visual_config, tuple(pair[1] for pair in pairs)),
        ),
    )
    envelope = bind_ppb1_active_receptor_batch(
        "binding.s2fs.neutral",
        world,
        batch,
        profile,
    )
    return config, envelope


def _input(config, envelope, index: int):
    return coordinator.bind_coordinator_input(
        config,
        envelope,
        envelope.auditory_stream.timed_frames[index],
        envelope.visual_stream.timed_frames[index],
    )


def _probe(config, envelope, index: int):
    return coordinator.bind_coordinator_probe(
        config,
        envelope,
        envelope.auditory_stream.timed_frames[index],
        envelope.visual_stream.timed_frames[index],
    )


def _owner(config, state, source, suffix: str = "main"):
    return coordinator.B4TSPM1CoordinatorOwner(
        f"s2fs.owner.{suffix}",
        f"s2fs.authorization.{suffix}",
        f"s2fs.consumption.{suffix}",
        config.config_digest,
        state.state_digest,
        source.input_digest,
    )


class S2FSPrivateB4TSPM1CoordinatorTests(unittest.TestCase):
    def test_01_valid_initial_invariants(self) -> None:
        config, _ = _fixture()
        state = coordinator.initial_composite_state(config)
        self.assertEqual(0, state.generation)
        self.assertEqual(state.generation, state.b4_state.accepted_count)
        self.assertEqual(state.generation, state.tspm_state.generation)
        self.assertEqual(state.generation, state.tspm_state.fast_state.accepted_exposure_count)
        self.assertEqual(9, len(state.b4_state.entries))

    def test_02_one_common_source_binds_both_arm_projections(self) -> None:
        config, envelope = _fixture()
        source = _input(config, envelope, 0)
        self.assertIs(source.envelope, source.tspm_exposure.envelope)
        self.assertIs(source.auditory, source.tspm_exposure.auditory)
        self.assertIs(source.visual, source.tspm_exposure.visual)
        self.assertEqual(source.auditory_values + source.visual_values, source.av_values)
        self.assertEqual(26, len(source.av_values))

    def test_03_valid_atomic_double_step_publishes_one_composite(self) -> None:
        config, envelope = _fixture()
        state = coordinator.initial_composite_state(config)
        source = _input(config, envelope, 0)
        owner = _owner(config, state, source)
        result = owner.consume_once(config, state, source)
        self.assertEqual("CONSUMED", owner.snapshot().status)
        self.assertEqual(1, result.poststate.generation)
        self.assertEqual(1, result.poststate.b4_state.accepted_count)
        self.assertEqual(1, result.poststate.tspm_state.generation)
        self.assertEqual(state.state_digest, result.poststate.parent_state_digest)
        self.assertEqual(source.input_digest, result.poststate.last_input_digest)

    def test_04_generation_equality_survives_continuation(self) -> None:
        config, envelope = _fixture()
        state = coordinator.initial_composite_state(config)
        first = _input(config, envelope, 0)
        state = _owner(config, state, first, "first").consume_once(config, state, first).poststate
        second = _input(config, envelope, 1)
        state = _owner(config, state, second, "second").consume_once(config, state, second).poststate
        self.assertEqual((2, 2, 2, 2), (
            state.generation,
            state.b4_state.accepted_count,
            state.tspm_state.generation,
            state.tspm_state.fast_state.accepted_exposure_count,
        ))

    def test_05_invalid_input_stops_before_both_arm_calls(self) -> None:
        config, envelope = _fixture()
        state = coordinator.initial_composite_state(config)
        source = _input(config, envelope, 0)
        owner = _owner(config, state, source, "input-error")
        with patch.object(coordinator, "_advance_b4_candidate") as b4, patch.object(
            coordinator, "_advance_tspm_candidate"
        ) as tspm:
            with self.assertRaises(coordinator.S2FSCoordinatorError):
                owner.consume_once(config, state, object())
        b4.assert_not_called()
        tspm.assert_not_called()
        self.assertEqual("FAILED", owner.snapshot().status)

    def test_06_b4_candidate_error_stops_before_tspm(self) -> None:
        config, envelope = _fixture()
        state = coordinator.initial_composite_state(config)
        source = _input(config, envelope, 0)
        owner = _owner(config, state, source, "b4-error")
        with patch.object(
            coordinator,
            "_advance_b4_candidate",
            side_effect=RuntimeError("injected b4 candidate error"),
        ), patch.object(coordinator, "_advance_tspm_candidate") as tspm:
            with self.assertRaises(coordinator.S2FSCoordinatorError) as caught:
                owner.consume_once(config, state, source)
        self.assertEqual(coordinator.S2FS_B4_CANDIDATE_FAILED, caught.exception.code)
        tspm.assert_not_called()
        self.assertEqual("FAILED", owner.snapshot().status)
        self.assertEqual(0, state.b4_state.accepted_count)

    def test_07_tspm_error_after_local_b4_candidate_exposes_no_partial_state(self) -> None:
        config, envelope = _fixture()
        state = coordinator.initial_composite_state(config)
        source = _input(config, envelope, 0)
        owner = _owner(config, state, source, "tspm-error")
        native_b4 = coordinator._advance_b4_candidate
        with patch.object(coordinator, "_advance_b4_candidate", wraps=native_b4) as b4, patch.object(
            coordinator,
            "_advance_tspm_candidate",
            side_effect=RuntimeError("injected tspm candidate error"),
        ):
            with self.assertRaises(coordinator.S2FSCoordinatorError) as caught:
                owner.consume_once(config, state, source)
        self.assertEqual(1, b4.call_count)
        self.assertEqual(coordinator.S2FS_TSPM_CANDIDATE_FAILED, caught.exception.code)
        self.assertEqual("FAILED", owner.snapshot().status)
        self.assertEqual(0, state.b4_state.accepted_count)
        self.assertEqual(0, state.tspm_state.generation)

    def test_08_stale_source_fails_before_candidate_calls(self) -> None:
        config, envelope = _fixture()
        initial = coordinator.initial_composite_state(config)
        first = _input(config, envelope, 0)
        advanced = _owner(config, initial, first, "advance").consume_once(
            config, initial, first
        ).poststate
        stale_owner = _owner(config, advanced, first, "stale")
        with patch.object(coordinator, "_advance_b4_candidate") as b4, patch.object(
            coordinator, "_advance_tspm_candidate"
        ) as tspm:
            with self.assertRaises(coordinator.S2FSCoordinatorError):
                stale_owner.consume_once(config, advanced, first)
        b4.assert_not_called()
        tspm.assert_not_called()
        self.assertEqual("FAILED", stale_owner.snapshot().status)

    def test_09_receipt_manipulation_fails_without_composite_result(self) -> None:
        config, envelope = _fixture()
        state = coordinator.initial_composite_state(config)
        source = _input(config, envelope, 0)
        owner = _owner(config, state, source, "receipt-error")
        with patch.object(coordinator, "_make_receipt", return_value=object()):
            with self.assertRaises(coordinator.S2FSCoordinatorError) as caught:
                owner.consume_once(config, state, source)
        self.assertEqual(coordinator.S2FS_RELATION_MISMATCH, caught.exception.code)
        self.assertEqual("FAILED", owner.snapshot().status)
        self.assertEqual(0, state.generation)

    def test_10_owner_reuse_is_rejected_without_changing_terminal_success(self) -> None:
        config, envelope = _fixture()
        state = coordinator.initial_composite_state(config)
        source = _input(config, envelope, 0)
        owner = _owner(config, state, source, "reuse")
        owner.consume_once(config, state, source)
        with self.assertRaises(coordinator.S2FSCoordinatorError) as caught:
            owner.consume_once(config, state, source)
        self.assertEqual(coordinator.S2FS_OWNER_TERMINAL, caught.exception.code)
        self.assertEqual("CONSUMED", owner.snapshot().status)

    def test_11_read_only_returns_three_unprioritized_views(self) -> None:
        config, envelope = _fixture()
        state = coordinator.initial_composite_state(config)
        source = _input(config, envelope, 0)
        state = _owner(config, state, source, "read").consume_once(
            config, state, source
        ).poststate
        probe = _probe(config, envelope, 1)
        before = state.state_digest
        finding = coordinator.probe_composite_read_only(config, state, probe)
        self.assertEqual(("B4_RECENT", "TSPM_FAST", "TSPM_SLOW"), finding.roles)
        self.assertEqual(before, finding.prestate_digest)
        self.assertEqual(before, finding.poststate_digest)
        self.assertEqual(before, state.state_digest)
        names = {item.name for item in fields(type(finding))}
        self.assertNotIn("best_memory", names)
        self.assertNotIn("selected_memory", names)
        self.assertNotIn("context_source", names)

    def test_12_resource_ledger_and_private_export_boundary(self) -> None:
        config, envelope = _fixture()
        state = coordinator.initial_composite_state(config)
        source = _input(config, envelope, 0)
        result = _owner(config, state, source, "ledger").consume_once(
            config, state, source
        )
        ledger = result.resource_ledger
        self.assertEqual((26, 293, 293, 31), (
            ledger.common_projection_terms,
            ledger.b4_functional_write_words,
            ledger.tspm_functional_write_words,
            ledger.coordinator_write_words,
        ))
        self.assertEqual(617, ledger.total_functional_write_words)
        self.assertEqual(468, ledger.total_functional_distance_terms)
        self.assertEqual(54, ledger.total_control_terms)
        self.assertGreater(ledger.total_functional_write_words, 586)
        for name in (
            "B4TSPM1CoordinatorOwner",
            "B4TSPM1CompositeState",
            "probe_composite_read_only",
        ):
            self.assertFalse(hasattr(mcm_field_organism, name))
            self.assertFalse(hasattr(current_api, name))
            self.assertNotIn(name, ROOT_LAZY_EXPORTS)
        source_text = (ROOT / "tools" / "_s2fs_b4_tspm1_private_coordinator.py").read_text(
            encoding="ascii"
        )
        self.assertNotIn("BEST_MEMORY", source_text)
        self.assertNotIn("SELECTED_MEMORY", source_text)
        self.assertNotIn("run_main_once", source_text)


if __name__ == "__main__":
    unittest.main()
