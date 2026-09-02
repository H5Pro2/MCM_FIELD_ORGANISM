"""Focused neutral qualification for the private S2-JW adapter boundary."""

from __future__ import annotations

from dataclasses import fields, replace
import hashlib
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np

import mcm_field_organism
from mcm_field_organism import _tspm1_s2dr_private_comparison as comparison
from mcm_field_organism import current_api
from mcm_field_organism.broadband_hearing_path import BroadbandHearingPath
from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from mcm_field_organism.receptor_contract import (
    CommonFieldTime,
    from_auditory_receptor_state,
    from_visual_receptor_state,
)
from mcm_field_organism.receptor_time_model import OrganismTimedReceptorFrame
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from tools import _s2jw_default_live_av_pairing as pairing
from tools import _s2jw_default_live_profile as profile_module
from tools import _s2jw_profiled_memory_coordinator as coordinator
from tools import _s2jw_profiled_memory_ledger as ledger_module
from tools import _s2jw_profiled_memory_read_only as read_only


ROOT = Path(__file__).resolve().parents[1]
CORE_HASHES = {
    "mcm_field_organism/_ppb1_reference.py": "15f1fabaa45348f067b7bf466f138d275d74f75a6e98afc05867f7b8c35d46f0",
    "mcm_field_organism/_tspm1_private.py": "321ce786c42edd217dc6dbf2210c495016b2babaa78d53449a13b0039965d516",
    "mcm_field_organism/_tspm1_s2dr_private_comparison.py": "96cdd018be34afe67de0139428fed5254cff945ba74db98163a91273f5d21b2c",
}


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _square_window(period: int) -> tuple[float, ...]:
    half = period // 2
    return tuple(0.5 if (index // half) % 2 == 0 else -0.5 for index in range(4800))


def _owner(config, state, source, suffix: str) -> coordinator.S2JVFormationOwner:
    return coordinator.S2JVFormationOwner(
        f"s2jw-owner-{suffix}",
        f"s2jw-authorization-{suffix}",
        f"s2jw-consumption-{suffix}",
        config.config_digest,
        state.state_digest,
        source.input_digest,
    )


class S2JWDefaultLiveMemoryAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile = profile_module.build_s2jw_default_live_profile()
        cls.limits = ledger_module.build_s2jv_ledger_limits(cls.profile)
        cls.config = coordinator.build_s2jv_coordinator_config(
            tspm_config=cls.profile.tspm_config,
            b4_capacity=9,
            ledger_limits=cls.limits,
        )
        visual_receptor = LocalChannelGridReceptor(VisualGridConfig())
        hearing = BroadbandHearingPath(LogSpectralReceptor(LogSpectralConfig()))
        periods = (960, 400, 960)
        fills = (0, 255, 0)
        pairs = []
        for block_index, (period, fill) in enumerate(zip(periods, fills, strict=True)):
            window = _square_window(period)
            auditory_state = None
            for hop_index in range(10):
                chunk = window[hop_index * 480 : (hop_index + 1) * 480]
                state = hearing.push(chunk)
                if hop_index == 9:
                    auditory_state = state
            assert auditory_state is not None
            image = np.full((1080, 1920, 3), fill, dtype=np.uint8)
            visual_state = visual_receptor.analyze(image, frame_index=3 * block_index + 2)
            auditory = OrganismTimedReceptorFrame(
                from_auditory_receptor_state(auditory_state),
                CommonFieldTime(
                    "s2jw-field-clock",
                    100_000_000 * block_index + 90_000_000,
                    100_000_000 * (block_index + 1),
                ),
            )
            visual = OrganismTimedReceptorFrame(
                from_visual_receptor_state(visual_state),
                CommonFieldTime(
                    "s2jw-field-clock",
                    ((3 * block_index + 2) * 1_000_000_000) // 30,
                    100_000_000 * (block_index + 1),
                ),
            )
            audio_bytes = np.asarray(window, dtype="<f4").tobytes()
            visual_bytes = image.tobytes(order="C")
            plan = pairing.build_s2jv_pairing_plan(
                pair_id=f"s2jw-pair-{block_index:02d}",
                source_contract_id="s2jw-neutral-source",
                profile=cls.profile,
                auditory=auditory,
                visual=visual,
                auditory_payload_digest=_sha256(audio_bytes),
                visual_payload_digest=_sha256(visual_bytes),
            )
            pairs.append(
                pairing.bind_s2jv_default_live_pair(
                    pairing_plan=plan,
                    profile=cls.profile,
                    auditory=auditory,
                    visual=visual,
                )
            )
        cls.pairs = tuple(pairs)

    def test_01_profile_is_exactly_default_live_and_digest_bound(self) -> None:
        self.assertEqual((48, 288, 336), (
            self.profile.auditory_dimension,
            self.profile.visual_dimension,
            self.profile.av_dimension,
        ))
        self.assertEqual("default-live", self.profile.profile.profile_id)
        self.assertEqual(profile_module.EXPECTED_PROFILE_BINDING_DIGEST, self.profile.profile.digest())
        self.assertEqual(profile_module.EXPECTED_TSPM_CONFIG_DIGEST, self.profile.tspm_config.config_binding_digest)

    def test_02_default_live_pair_uses_no_browser_relabelling(self) -> None:
        pair = self.pairs[0]
        self.assertEqual("default-live", pair.envelope.profile_id)
        self.assertNotEqual("browser", pair.envelope.profile_id)
        self.assertEqual(self.profile.profile.digest(), pair.envelope.profile_binding_digest)

    def test_03_pair_binds_one_real_336_value_overlapping_source(self) -> None:
        pair = self.pairs[0]
        self.assertEqual(48, len(pair.auditory.timed_frame.frame.values))
        self.assertEqual(288, len(pair.visual.timed_frame.frame.values))
        self.assertEqual(10_000_000, pair.plan.overlap_end_tick - pair.plan.overlap_start_tick)
        self.assertEqual(pair.plan.plan_digest, pair.plan.plan_digest)
        self.assertNotIn("pixel_bytes", {item.name for item in fields(type(pair))})
        self.assertNotIn("pcm_bytes", {item.name for item in fields(type(pair))})

    def test_04_pairing_rejects_profile_or_time_mutation(self) -> None:
        with self.assertRaises(pairing.S2JWPairingError):
            replace(self.pairs[0].plan, profile_binding_digest="0" * 64)
        with self.assertRaises(pairing.S2JWPairingError):
            replace(self.pairs[0].plan, overlap_end_tick=self.pairs[0].plan.overlap_start_tick)

    def test_05_initial_state_has_profile_derived_invariants(self) -> None:
        state = coordinator.initial_s2jv_composite_state(self.config)
        self.assertEqual((0, 0, 0), (
            state.generation,
            state.b4_state.accepted_count,
            state.tspm_state.generation,
        ))
        self.assertEqual(9, len(state.b4_state.entries))
        self.assertEqual(3, len(state.tspm_state.fast_state.slots))

    def test_06_one_real_atomic_step_publishes_both_candidates(self) -> None:
        state = coordinator.initial_s2jv_composite_state(self.config)
        source = coordinator.bind_s2jv_coordinator_input(config=self.config, source=self.pairs[0])
        result = coordinator.advance_s2jv_atomic(
            config=self.config,
            prestate=state,
            source=source,
            owner=_owner(self.config, state, source, "atomic"),
        )
        self.assertEqual((1, 1, 1), (
            result.poststate.generation,
            result.poststate.b4_state.accepted_count,
            result.poststate.tspm_state.generation,
        ))
        self.assertEqual(state.state_digest, result.poststate.parent_state_digest)
        self.assertEqual(source.input_digest, result.poststate.last_input_digest)

    def test_07_generation_equality_survives_two_neutral_steps(self) -> None:
        state = coordinator.initial_s2jv_composite_state(self.config)
        for index in range(2):
            source = coordinator.bind_s2jv_coordinator_input(config=self.config, source=self.pairs[index])
            state = coordinator.advance_s2jv_atomic(
                config=self.config,
                prestate=state,
                source=source,
                owner=_owner(self.config, state, source, f"step-{index}"),
            ).poststate
        self.assertEqual((2, 2, 2, 2), (
            state.generation,
            state.b4_state.accepted_count,
            state.tspm_state.generation,
            state.tspm_state.fast_state.accepted_exposure_count,
        ))

    def test_08_invalid_prestate_stops_before_both_arms(self) -> None:
        state = coordinator.initial_s2jv_composite_state(self.config)
        source = coordinator.bind_s2jv_coordinator_input(config=self.config, source=self.pairs[0])
        owner = _owner(self.config, state, source, "invalid")
        with patch.object(coordinator, "_advance_b4_candidate") as b4, patch.object(
            coordinator, "_advance_tspm_candidate"
        ) as tspm:
            with self.assertRaises(coordinator.S2JWCoordinatorError):
                owner.consume_once(self.config, object(), source)
        b4.assert_not_called()
        tspm.assert_not_called()
        self.assertEqual("FAILED", owner.snapshot().status)

    def test_09_tspm_failure_after_local_b4_candidate_exposes_no_partial_state(self) -> None:
        state = coordinator.initial_s2jv_composite_state(self.config)
        source = coordinator.bind_s2jv_coordinator_input(config=self.config, source=self.pairs[0])
        owner = _owner(self.config, state, source, "tspm-failure")
        native_b4 = coordinator._advance_b4_candidate
        with patch.object(coordinator, "_advance_b4_candidate", wraps=native_b4) as b4, patch.object(
            coordinator, "_advance_tspm_candidate", side_effect=RuntimeError("neutral injected failure")
        ):
            with self.assertRaises(coordinator.S2JWCoordinatorError) as caught:
                owner.consume_once(self.config, state, source)
        self.assertEqual(1, b4.call_count)
        self.assertEqual(coordinator.S2JW_TSPM_FAILED, caught.exception.code)
        self.assertEqual((0, 0, "FAILED"), (
            state.b4_state.accepted_count,
            state.tspm_state.generation,
            owner.snapshot().status,
        ))

    def test_10_owner_is_single_use(self) -> None:
        state = coordinator.initial_s2jv_composite_state(self.config)
        source = coordinator.bind_s2jv_coordinator_input(config=self.config, source=self.pairs[0])
        owner = _owner(self.config, state, source, "single-use")
        owner.consume_once(self.config, state, source)
        with self.assertRaises(coordinator.S2JWCoordinatorError) as caught:
            owner.consume_once(self.config, state, source)
        self.assertEqual(coordinator.S2JW_OWNER_TERMINAL, caught.exception.code)
        self.assertEqual("CONSUMED", owner.snapshot().status)

    def test_11_read_only_returns_separate_views_without_state_change(self) -> None:
        initial = coordinator.initial_s2jv_composite_state(self.config)
        source = coordinator.bind_s2jv_coordinator_input(config=self.config, source=self.pairs[0])
        state = _owner(self.config, initial, source, "read").consume_once(
            self.config, initial, source
        ).poststate
        probe = coordinator.bind_s2jv_probe(config=self.config, source=self.pairs[2])
        before = state.state_digest
        finding = read_only.probe_s2jv_composite_read_only(
            config=self.config,
            state=state,
            probe=probe,
        )
        self.assertEqual(
            ("B4_RECENT", "TSPM_FAST", "TSPM_SLOW_AUDITORY", "TSPM_SLOW_VISUAL"),
            finding.roles,
        )
        self.assertEqual((before, before, before), (
            finding.prestate_digest,
            finding.poststate_digest,
            state.state_digest,
        ))
        self.assertIsNotNone(finding.b4_selected)
        self.assertIsNotNone(finding.fast_selected)

    def test_12_incomplete_b4_fifo_anatomy_is_rejected(self) -> None:
        state = coordinator.initial_s2jv_composite_state(self.config)
        malformed_b4 = comparison._B4State(1, state.b4_state.entries)
        malformed = coordinator._make_state(
            self.config,
            1,
            "0" * 64,
            "1" * 64,
            malformed_b4,
            state.tspm_state,
        )
        with self.assertRaises(coordinator.S2JWCoordinatorError):
            coordinator._validate_state(self.config, malformed)

    def test_13_ledger_is_profile_derived_and_keeps_s2jv_plan_limits(self) -> None:
        self.assertEqual((3552, 9120, 5568, 44544), (
            self.limits.formation_l1_term_limit,
            self.limits.read_only_l1_term_limit,
            self.limits.maximum_state_float_words,
            self.limits.maximum_state_float64_bytes,
        ))
        self.assertEqual((15, 3, 72, 22512, 21168, 43680), (
            self.limits.plan_formation_count,
            self.limits.plan_probe_count,
            self.limits.plan_top_level_operations,
            self.limits.plan_formation_l1_terms,
            self.limits.plan_probe_l1_terms,
            self.limits.plan_total_l1_terms,
        ))

    def test_14_private_boundary_has_no_core_api_or_raw_payload_export(self) -> None:
        for path, expected in CORE_HASHES.items():
            self.assertEqual(expected, _sha256((ROOT / path).read_bytes()))
        for name in (
            "S2JVFormationOwner",
            "S2JVCompositeStateV1",
            "probe_s2jv_composite_read_only",
        ):
            self.assertFalse(hasattr(mcm_field_organism, name))
            self.assertFalse(hasattr(current_api, name))
            self.assertNotIn(name, ROOT_LAZY_EXPORTS)
        for path in (
            ROOT / "tools" / "_s2jw_profiled_memory_coordinator.py",
            ROOT / "tools" / "_s2jw_profiled_memory_read_only.py",
            ROOT / "tools" / "_s2jw_profiled_memory_ledger.py",
        ):
            source = path.read_text(encoding="ascii")
            self.assertNotIn("pixel_bytes", source)
            self.assertNotIn("pcm_bytes", source)
            self.assertNotIn("BEST_MEMORY", source)
            self.assertNotIn("run_main_once", source)


if __name__ == "__main__":
    unittest.main()
