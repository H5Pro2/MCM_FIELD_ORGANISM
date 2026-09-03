"""Twelve focused neutral contract tests for S2-KJ."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import FrozenInstanceError
import hashlib
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np

import mcm_field_organism
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
from tools import _s2kj_two_area_perceptual_context_336 as context
from tools import _s2kj_validated_perceptual_finding_336 as binder
from tools import _s2jw_default_live_av_pairing as pairing
from tools import _s2jw_profiled_memory_coordinator as coordinator
from tools import _s2jw_profiled_memory_read_only as read_only
from tools._s2jw_default_live_profile import build_s2jw_default_live_profile
from tools._s2jw_profiled_memory_ledger import build_s2jv_ledger_limits


ROOT = Path(__file__).resolve().parents[1]
QUALIFICATION_ID = "s2kj-qualification-20260903-03"


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _square_window(period: int) -> tuple[float, ...]:
    half = period // 2
    return tuple(0.5 if (index // half) % 2 == 0 else -0.5 for index in range(4800))


def _pair(
    profile,
    hearing: BroadbandHearingPath,
    *,
    period: int,
    fill: int,
    block_index: int,
    source_ordinal: int,
):
    window = _square_window(period)
    auditory_state = None
    for hop_index in range(10):
        auditory_state = hearing.push(window[hop_index * 480 : (hop_index + 1) * 480])
    assert auditory_state is not None
    assert auditory_state.snapshot_index == source_ordinal * 10
    assert auditory_state.window_start_sample == source_ordinal * 4800
    assert auditory_state.window_end_sample == (source_ordinal + 1) * 4800
    image = np.full((1080, 1920, 3), fill, dtype=np.uint8)
    visual_state = LocalChannelGridReceptor(VisualGridConfig()).analyze(
        image, frame_index=3 * block_index + 2
    )
    auditory = OrganismTimedReceptorFrame(
        from_auditory_receptor_state(auditory_state),
        CommonFieldTime(
            "s2kj-neutral-clock",
            100_000_000 * block_index + 90_000_000,
            100_000_000 * (block_index + 1),
        ),
    )
    visual = OrganismTimedReceptorFrame(
        from_visual_receptor_state(visual_state),
        CommonFieldTime(
            "s2kj-neutral-clock",
            ((3 * block_index + 2) * 1_000_000_000) // 30,
            100_000_000 * (block_index + 1),
        ),
    )
    plan = pairing.build_s2jv_pairing_plan(
        pair_id=f"s2kj-neutral-pair-{block_index:02d}",
        source_contract_id="s2kj-neutral-source",
        profile=profile,
        auditory=auditory,
        visual=visual,
        auditory_payload_digest=_sha256(np.asarray(window, dtype="<f4").tobytes()),
        visual_payload_digest=_sha256(image.tobytes(order="C")),
    )
    return pairing.bind_s2jv_default_live_pair(
        pairing_plan=plan,
        profile=profile,
        auditory=auditory,
        visual=visual,
    )


def _advance(config, state, pair, index: int):
    source = coordinator.bind_s2jv_coordinator_input(config=config, source=pair)
    owner = coordinator.S2JVFormationOwner(
        f"s2kj-owner-{index:02d}",
        f"s2kj-authorization-{index:02d}",
        f"s2kj-consumption-{index:02d}",
        config.config_digest,
        state.state_digest,
        source.input_digest,
    )
    return coordinator.advance_s2jv_atomic(
        config=config,
        prestate=state,
        source=source,
        owner=owner,
    ).poststate


def _read_and_bind(config, state, pair):
    probe = coordinator.bind_s2jv_probe(config=config, source=pair)
    finding = read_only.probe_s2jv_composite_read_only(
        config=config,
        state=state,
        probe=probe,
    )
    bound = binder.bind_validated_perceptual_finding_336(
        config=config,
        state=state,
        probe=probe,
        finding=finding,
    )
    return probe, finding, bound


class S2KJTwoAreaPerceptualContext336Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile = build_s2jw_default_live_profile()
        limits = build_s2jv_ledger_limits(cls.profile)
        cls.config = coordinator.build_s2jv_coordinator_config(
            tspm_config=cls.profile.tspm_config,
            b4_capacity=cls.profile.b4_capacity,
            ledger_limits=limits,
        )
        stable_hearing = BroadbandHearingPath(LogSpectralReceptor(LogSpectralConfig()))
        repeated = tuple(
            _pair(
                cls.profile,
                stable_hearing,
                period=960,
                fill=32,
                block_index=index,
                source_ordinal=index,
            )
            for index in range(4)
        )
        cls.h_probe_pair = _pair(
            cls.profile,
            stable_hearing,
            period=960,
            fill=32,
            block_index=4,
            source_ordinal=4,
        )
        cls.n_probe_pair = _pair(
            cls.profile,
            stable_hearing,
            period=80,
            fill=32,
            block_index=5,
            source_ordinal=5,
        )
        state = coordinator.initial_s2jv_composite_state(cls.config)
        for index, item in enumerate(repeated):
            state = _advance(cls.config, state, item, index)
        cls.stable_state = state
        cls.h_probe, cls.h_finding, cls.h_bound = _read_and_bind(
            cls.config, state, cls.h_probe_pair
        )
        cls.n_probe, cls.n_finding, cls.n_bound = _read_and_bind(
            cls.config, state, cls.n_probe_pair
        )

        empty = coordinator.initial_s2jv_composite_state(cls.config)
        cls.empty_state = empty
        cls.empty_probe, cls.empty_finding, cls.empty_bound = _read_and_bind(
            cls.config, empty, repeated[0]
        )

        divergent_hearing = BroadbandHearingPath(LogSpectralReceptor(LogSpectralConfig()))
        divergent_pairs = (
            _pair(
                cls.profile,
                divergent_hearing,
                period=960,
                fill=32,
                block_index=10,
                source_ordinal=0,
            ),
            _pair(
                cls.profile,
                divergent_hearing,
                period=960,
                fill=40,
                block_index=11,
                source_ordinal=1,
            ),
            _pair(
                cls.profile,
                divergent_hearing,
                period=960,
                fill=40,
                block_index=12,
                source_ordinal=2,
            ),
        )
        divergent = coordinator.initial_s2jv_composite_state(cls.config)
        divergent = _advance(cls.config, divergent, divergent_pairs[0], 20)
        divergent = _advance(cls.config, divergent, divergent_pairs[1], 21)
        _, _, cls.divergent_bound = _read_and_bind(
            cls.config, divergent, divergent_pairs[2]
        )

    def test_01_h_like_binding_has_both_stable_modalities(self) -> None:
        result = context.project_two_area_perceptual_context_336(self.h_bound)
        self.assertEqual("AUDITORY_AND_VISUAL_STABLE", result.b_stability_status)
        self.assertEqual((48, 288), (
            result.b_stable.auditory.candidate.dimension,
            result.b_stable.visual.candidate.dimension,
        ))
        self.assertEqual((3, 3), (
            result.b_stable.auditory.candidate.support,
            result.b_stable.visual.candidate.support,
        ))

    def test_02_n_like_binding_is_visual_stable_only(self) -> None:
        result = context.project_two_area_perceptual_context_336(self.n_bound)
        self.assertEqual("VISUAL_STABLE_ONLY", result.b_stability_status)
        self.assertEqual("NO_FUNCTIONAL_MATCH", result.b_stable.auditory.absence_reason)
        self.assertEqual("AVAILABLE", result.b_stable.visual.status)
        self.assertNotEqual("NO_CONTEXT", result.context_presence)

    def test_03_different_b4_and_fast_candidates_remain_separate(self) -> None:
        result = context.project_two_area_perceptual_context_336(self.divergent_bound)
        b4 = result.a_recent.b4_recent.candidate
        fast = result.a_recent.tspm_fast.candidate
        self.assertIsNotNone(b4)
        self.assertIsNotNone(fast)
        self.assertNotEqual(b4.visual_values, fast.visual_values)
        self.assertNotEqual(b4.candidate_digest, fast.candidate_digest)
        self.assertIsNot(result.a_recent.b4_recent, result.a_recent.tspm_fast)

    def test_04_complete_valid_absence_is_no_context(self) -> None:
        result = context.project_two_area_perceptual_context_336(self.empty_bound)
        self.assertTrue(all(item.status == "ABSENT_VALID" for item in self.empty_bound.role_findings))
        self.assertEqual("NO_CONTEXT", result.context_presence)
        self.assertEqual("NO_STABLE_CONTEXT", result.b_stability_status)

    def test_05_binder_uses_same_probe_without_a_second_memory_probe(self) -> None:
        with patch.object(read_only, "probe_s2jv_composite_read_only") as second_probe:
            rebound = binder.bind_validated_perceptual_finding_336(
                config=self.config,
                state=self.stable_state,
                probe=self.h_probe,
                finding=self.h_finding,
            )
        second_probe.assert_not_called()
        self.assertEqual(self.h_bound, rebound)
        slow_slot = next(
            slot
            for slot in self.stable_state.tspm_state.visual_ppb1_state.slots
            if slot.slot_id == rebound.role_findings[3].candidate.slot_id
        )
        self.assertEqual(slow_slot.prototype_values, rebound.role_findings[3].candidate.values)

    def test_06_projection_is_immutable_read_only_and_bounded(self) -> None:
        before = (self.h_bound.binding_digest, self.stable_state.state_digest)
        result = context.project_two_area_perceptual_context_336(self.h_bound)
        self.assertEqual(before, (self.h_bound.binding_digest, self.stable_state.state_digest))
        self.assertEqual((6, 4), (
            result.resource_ledger.logical_operation_count,
            result.resource_ledger.candidate_count,
        ))
        self.assertLessEqual(result.resource_ledger.serialized_output_bytes, 65_536)
        with self.assertRaises(FrozenInstanceError):
            result.automatic_selection = "forbidden"

    def test_07_dimension_mutation_fails_without_partial_bundle(self) -> None:
        damaged = deepcopy(self.h_bound)
        object.__setattr__(
            damaged.role_findings[0].candidate,
            "visual_values",
            damaged.role_findings[0].candidate.visual_values[:-1],
        )
        with self.assertRaises(context.S2KJContextError):
            context.project_two_area_perceptual_context_336(damaged)

    def test_08_digest_mutation_fails_without_partial_bundle(self) -> None:
        damaged = deepcopy(self.h_bound)
        object.__setattr__(damaged, "binding_digest", "0" * 64)
        with self.assertRaises(context.S2KJContextError):
            context.project_two_area_perceptual_context_336(damaged)

    def test_09_role_mutation_fails_without_partial_bundle(self) -> None:
        damaged = deepcopy(self.h_bound)
        object.__setattr__(damaged, "role_findings", tuple(reversed(damaged.role_findings)))
        with self.assertRaises(context.S2KJContextError):
            context.project_two_area_perceptual_context_336(damaged)

    def test_10_stability_mutation_fails_without_partial_bundle(self) -> None:
        damaged = deepcopy(self.h_bound)
        object.__setattr__(damaged.role_findings[2].candidate, "stable", False)
        with self.assertRaises(context.S2KJContextError):
            context.project_two_area_perceptual_context_336(damaged)

    def test_11_state_probe_and_slot_mutations_fail_closed(self) -> None:
        with self.assertRaises(binder.S2KJBindingError):
            binder.bind_validated_perceptual_finding_336(
                config=self.config,
                state=self.empty_state,
                probe=self.h_probe,
                finding=self.h_finding,
            )
        damaged = deepcopy(self.h_finding)
        object.__setattr__(damaged.b4_selected, "entry_digest", "f" * 64)
        object.__setattr__(damaged, "finding_digest", read_only._digest(damaged.payload_without_digest()))
        with self.assertRaises(binder.S2KJBindingError):
            binder.bind_validated_perceptual_finding_336(
                config=self.config,
                state=self.stable_state,
                probe=self.h_probe,
                finding=damaged,
            )

    def test_12_boundary_has_no_public_export_or_forbidden_subsystem(self) -> None:
        for name in (
            "ValidatedPerceptualFinding336V1",
            "TwoAreaPerceptualContext336",
            "bind_validated_perceptual_finding_336",
        ):
            self.assertFalse(hasattr(mcm_field_organism, name))
            self.assertFalse(hasattr(current_api, name))
            self.assertNotIn(name, ROOT_LAZY_EXPORTS)
        source = "\n".join(
            (ROOT / path).read_text(encoding="ascii")
            for path in (
                "tools/_s2kj_validated_perceptual_finding_336.py",
                "tools/_s2kj_two_area_perceptual_context_336.py",
            )
        )
        for forbidden in (
            "run_main_once",
            "BEST_MEMORY",
            "pixel_bytes",
            "pcm_bytes",
            "field_snapshot",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
