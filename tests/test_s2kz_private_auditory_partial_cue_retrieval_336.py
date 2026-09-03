"""Neutral qualification of private S2-KZ auditory partial-cue retrieval."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import hashlib
import json
from pathlib import Path
import unittest

from mcm_field_organism import _ppb1_reference as ppb1
from mcm_field_organism import _tspm1_private as tspm1
from mcm_field_organism import _tspm1_s2dr_private_comparison as comparison
from tools import _s2jw_default_live_profile as profile_module
from tools import _s2jw_profiled_memory_coordinator as coordinator
from tools import _s2jw_profiled_memory_ledger as memory_ledger
from tools import _s2kz_private_auditory_partial_cue_retrieval_336 as subject
from tools import _s2kz_private_direct_auditory_slot_scan_baseline as baseline


QUALIFICATION_ID = "s2kz-auditory-partial-cue-qualification-20260904-01"
ZERO_DIGEST = "0" * 64
PARENT_DIGEST = "1" * 64
INPUT_DIGEST = "2" * 64
AUDIO_CLOCK = "audio.sample"
VIDEO_CLOCK = "video.frame"
VISUAL = (0.0,) * 288
MATCH_A = (0.10,) * 24 + (0.25,) * 24
MATCH_B = (0.10,) * 24 + (0.75,) * 24
MATCH_C = (0.10,) * 24 + (1.00,) * 24
MISMATCH = (0.90,) * 24 + (0.50,) * 24
TINY_POSITIVE = (0.10 + 1.0e-10,) * 24 + (0.60,) * 24
S2KY_RESULT = Path("reports/s2kx/s2ky-auditory-partial-cue-geometry-20260903-01/materialization.json")


def _config() -> coordinator.S2JVCoordinatorConfigV1:
    profile = profile_module.build_s2jw_default_live_profile()
    return coordinator.build_s2jv_coordinator_config(
        tspm_config=profile.tspm_config,
        b4_capacity=profile.b4_capacity,
        ledger_limits=memory_ledger.build_s2jv_ledger_limits(profile),
    )


def _ppb_state(
    config: ppb1.PPB1BankConfig,
    *,
    generation: int,
    values: tuple[tuple[float, ...], ...],
    clock_id: str,
    supports: tuple[int, ...] | None = None,
) -> ppb1.PPB1BankState:
    supports = supports or (3,) * len(values)
    occupied = tuple(
        ppb1.PPB1PrototypeSlot(
            f"{config.bank_id}.slot.{index:03d}",
            True,
            item,
            supports[index],
            min(index + 1, generation),
        )
        for index, item in enumerate(values)
    )
    free = tuple(
        ppb1.PPB1PrototypeSlot.free(f"{config.bank_id}.slot.{index:03d}")
        for index in range(len(values), config.capacity)
    )
    return ppb1.PPB1BankState(
        config.bank_id,
        config.digest(),
        generation,
        clock_id if generation else None,
        800 if generation else None,
        occupied + free,
    )


def _state(
    config: coordinator.S2JVCoordinatorConfigV1,
    *,
    b4: tuple[tuple[float, ...], ...] = (),
    fast: tuple[tuple[float, ...], ...] = (),
    slow: tuple[tuple[float, ...], ...] = (),
    slow_supports: tuple[int, ...] | None = None,
    auditory_clock_id: str = AUDIO_CLOCK,
    auditory_end_tick: int = 900,
    visual_clock_id: str = VIDEO_CLOCK,
) -> coordinator.S2JVCompositeStateV1:
    if not b4 and not fast and not slow:
        return coordinator.initial_s2jv_composite_state(config)
    generation = 9
    b4_values = b4 + (MISMATCH,) * (9 - len(b4))
    b4_state = comparison._B4State(
        generation,
        tuple(
            comparison._FIFOEntry(
                f"b4.slot.{index:03d}",
                True,
                auditory + VISUAL,
                index + 1,
            )
            for index, auditory in enumerate(b4_values)
        ),
    )
    fast_slots = tuple(
        tspm1.TSPM1FastSlot(
            f"{config.tspm_config.fast_config.fast_bank_id}.slot.{index:03d}",
            True,
            auditory,
            VISUAL,
            1,
            generation - index,
            0,
            None,
        )
        for index, auditory in enumerate(fast)
    ) + tuple(
        tspm1.TSPM1FastSlot.free(
            f"{config.tspm_config.fast_config.fast_bank_id}.slot.{index:03d}"
        )
        for index in range(len(fast), 3)
    )
    fast_state = tspm1._make_fast_state(
        config.tspm_config.fast_config,
        generation,
        auditory_clock_id,
        auditory_end_tick,
        visual_clock_id,
        900,
        fast_slots,
    )
    ppb_generation = 3 if slow else 0
    auditory_slow = _ppb_state(
        config.profile.profile.auditory_config,
        generation=ppb_generation,
        values=slow,
        clock_id=AUDIO_CLOCK,
        supports=slow_supports,
    )
    visual_slow = _ppb_state(
        config.profile.profile.visual_config,
        generation=ppb_generation,
        values=(),
        clock_id=VIDEO_CLOCK,
    )
    tspm_state = tspm1._make_composite_state(
        config.tspm_config,
        generation,
        PARENT_DIGEST,
        INPUT_DIGEST,
        fast_state,
        auditory_slow,
        visual_slow,
    )
    return coordinator._make_state(
        config,
        generation,
        PARENT_DIGEST,
        INPUT_DIGEST,
        b4_state,
        tspm_state,
    )


def _cue(
    config: coordinator.S2JVCoordinatorConfigV1,
    observed: tuple[float, ...] = (0.10,) * 24,
    *,
    clock_id: str = AUDIO_CLOCK,
    start: int = 1_000,
    end: int = 5_800,
):
    plan = subject.build_auditory_band_plan_48()
    cue = subject.build_masked_auditory_cue_48(
        pcm_payload_digest="3" * 64,
        receptor_state_digest="4" * 64,
        receptor_values_digest="5" * 64,
        config_digest=config.config_digest,
        auditory_source_clock_id=clock_id,
        auditory_window_start_tick=start,
        auditory_window_end_tick=end,
        observed_values=observed,
        band_plan=plan,
    )
    return cue, plan


def _run(config, state, cue, plan):
    primary = subject.form_auditory_partial_cue_retrieval_336(
        config=config,
        state=state,
        cue=cue,
        band_plan=plan,
    )
    direct = baseline.form_direct_auditory_slot_scan_baseline_336(
        config=config,
        state=state,
        cue=cue,
        band_plan=plan,
    )
    return primary, direct


def _semantic(result: subject.AuditoryPartialCueRetrievalResultV1):
    return (
        tuple(
            (
                scan.status,
                scan.eligible_count,
                scan.match_count,
                tuple(
                    (record.observed_distance, record.observed_match, record.observed_comparison_count)
                    for record in scan.records
                ),
            )
            for scan in result.bank_scans
        ),
        result.a_recent.status,
        result.a_recent.provenance_slot_digests,
        result.b_stable_auditory.status,
        result.b_stable_auditory.provenance_slot_digests,
        result.public_candidate_count,
        result.decision,
        None if result.hypothesis is None else result.hypothesis.area,
        None if result.hypothesis is None else result.hypothesis.proposed_values,
    )


def _real_s2ky_cue(config):
    raw = S2KY_RESULT.read_bytes()
    evidence = json.loads(raw.decode("ascii"))
    claimed = evidence.pop("result_digest")
    actual = subject.digest(evidence)
    if claimed != actual:
        raise AssertionError("S2-KY result digest differs")
    if hashlib.sha256(raw).hexdigest() != subject.S2KY_RESULT_SHA256:
        raise AssertionError("S2-KY file digest differs")
    if evidence["status"] != "S2KY_AUDIO_PARTIAL_CUE_GEOMETRY_MATERIALIZED":
        raise AssertionError("S2-KY status differs")
    measured = {item["role"]: item for item in evidence["measurements"].values()} if isinstance(evidence["measurements"], list) else evidence["measurements"]
    low = measured["CUE_LOW"]
    plan = subject.build_auditory_band_plan_48()
    cue = subject.build_masked_auditory_cue_48(
        pcm_payload_digest=low["pcm_digest"],
        receptor_state_digest=low["receptor_digest"],
        receptor_values_digest=low["values_digest"],
        config_digest=config.config_digest,
        auditory_source_clock_id=AUDIO_CLOCK,
        auditory_window_start_tick=0,
        auditory_window_end_tick=4_800,
        observed_values=tuple(low["values"][:24]),
        band_plan=plan,
    )
    return cue, plan, measured


class S2KZAuditoryPartialCueQualification(unittest.TestCase):
    def test_01_unique_a_from_equal_b4_and_fast(self) -> None:
        config = _config()
        state = _state(
            config,
            b4=(MATCH_A,),
            fast=(MATCH_A, MISMATCH, MISMATCH),
            slow=(MISMATCH,) * 8,
        )
        primary, direct = _run(config, state, *_cue(config))
        self.assertEqual(_semantic(primary), _semantic(direct))
        self.assertEqual(primary.a_recent.status, "A_RECENT_APPLICABLE")
        self.assertEqual(len(primary.a_recent.provenance_slot_digests), 2)
        self.assertEqual(primary.decision, "ADMIT_SINGLE_CONTEXT")
        self.assertEqual(primary.hypothesis.area, "A_RECENT")

    def test_02_unique_b_uses_positive_distance_not_exact_equality(self) -> None:
        config = _config()
        state = _state(config, slow=(TINY_POSITIVE,))
        primary, direct = _run(config, state, *_cue(config))
        self.assertEqual(_semantic(primary), _semantic(direct))
        distance = primary.bank_scans[2].records[0].observed_distance
        self.assertGreater(distance, 0.0)
        self.assertLessEqual(distance, 0.02)
        self.assertEqual(primary.b_stable_auditory.status, "B_STABLE_AUDITORY_APPLICABLE")
        self.assertEqual(primary.hypothesis.area, "B_STABLE_AUDITORY")

    def test_03_public_a_b_ambiguity(self) -> None:
        config = _config()
        state = _state(config, b4=(MATCH_A,), slow=(MATCH_B,))
        primary, direct = _run(config, state, *_cue(config))
        self.assertEqual(_semantic(primary), _semantic(direct))
        self.assertEqual(primary.public_candidate_count, 2)
        self.assertEqual(primary.decision, "ABSTAIN_AMBIGUOUS_CONTEXT")
        self.assertIsNone(primary.hypothesis)

    def test_04_a_bank_ambiguity_completes_all_three_scans(self) -> None:
        config = _config()
        state = _state(config, b4=(MATCH_A, MATCH_B), fast=(MISMATCH,), slow=(MATCH_C,))
        primary, direct = _run(config, state, *_cue(config))
        self.assertEqual(_semantic(primary), _semantic(direct))
        self.assertEqual(primary.bank_scans[0].match_count, 2)
        self.assertEqual(primary.a_recent.status, "A_RECENT_INTERNAL_AMBIGUITY")
        self.assertEqual(primary.bank_scans[2].match_count, 1)
        self.assertEqual(tuple(len(item.records) for item in primary.bank_scans), (9, 3, 8))

    def test_05_a_conflict_uses_complete_48_value_equality(self) -> None:
        config = _config()
        state = _state(config, b4=(MATCH_A,), fast=(MATCH_B,))
        primary, direct = _run(config, state, *_cue(config))
        self.assertEqual(_semantic(primary), _semantic(direct))
        self.assertEqual(primary.a_recent.status, "A_RECENT_INTERNAL_CONFLICT")
        self.assertEqual(primary.decision, "ABSTAIN_INTERNAL_CONFLICT")
        self.assertEqual(primary.resource_ledger.internal_equality_comparison_count, 48)

    def test_06_b_internal_ambiguity(self) -> None:
        config = _config()
        state = _state(config, slow=(MATCH_A, MATCH_B))
        primary, direct = _run(config, state, *_cue(config))
        self.assertEqual(_semantic(primary), _semantic(direct))
        self.assertEqual(primary.bank_scans[2].match_count, 2)
        self.assertEqual(primary.b_stable_auditory.status, "B_STABLE_AUDITORY_INTERNAL_AMBIGUITY")
        self.assertEqual(primary.decision, "ABSTAIN_INTERNAL_AMBIGUITY")

    def test_07_real_s2ky_pcm_receptor_cue_is_bound_without_memory_history(self) -> None:
        config = _config()
        cue, plan, measured = _real_s2ky_cue(config)
        state = _state(config)
        primary, direct = _run(config, state, cue, plan)
        self.assertEqual(_semantic(primary), _semantic(direct))
        self.assertEqual(primary.decision, "ABSTAIN_NO_CONTEXT")
        self.assertEqual(cue.pcm_payload_digest, measured["CUE_LOW"]["pcm_digest"])
        self.assertEqual(cue.receptor_values_digest, measured["CUE_LOW"]["values_digest"])

    def test_08_present_but_not_applicable(self) -> None:
        config = _config()
        state = _state(config, b4=(MATCH_A,), fast=(MATCH_A,), slow=(MATCH_B,))
        primary, direct = _run(config, state, *_cue(config, observed=(0.55,) * 24))
        self.assertEqual(_semantic(primary), _semantic(direct))
        self.assertEqual(primary.a_recent.status, "A_RECENT_NOT_APPLICABLE")
        self.assertEqual(primary.b_stable_auditory.status, "B_STABLE_AUDITORY_NOT_APPLICABLE")
        self.assertEqual(primary.decision, "ABSTAIN_NO_APPLICABLE_CONTEXT")

    def test_09_native_audio_time_is_independent_of_visual_clock(self) -> None:
        config = _config()
        state = _state(config, b4=(MATCH_A,), fast=(MATCH_A,), visual_clock_id="independent.video")
        cue, plan = _cue(config)
        primary, direct = _run(config, state, cue, plan)
        self.assertEqual(_semantic(primary), _semantic(direct))
        self.assertEqual(primary.decision, "ADMIT_SINGLE_CONTEXT")

    def test_10_wrong_native_audio_clock_fails_closed(self) -> None:
        config = _config()
        state = _state(config, b4=(MATCH_A,), fast=(MATCH_A,))
        cue, plan = _cue(config, clock_id="foreign.audio")
        for function in (subject.form_auditory_partial_cue_retrieval_336, baseline.form_direct_auditory_slot_scan_baseline_336):
            with self.subTest(function=function.__module__), self.assertRaises(subject.S2KZError):
                function(config=config, state=state, cue=cue, band_plan=plan)

    def test_11_stale_native_audio_window_fails_closed(self) -> None:
        config = _config()
        state = _state(config, b4=(MATCH_A,), fast=(MATCH_A,))
        cue, plan = _cue(config, start=899, end=900)
        for function in (subject.form_auditory_partial_cue_retrieval_336, baseline.form_direct_auditory_slot_scan_baseline_336):
            with self.subTest(function=function.__module__), self.assertRaises(subject.S2KZError):
                function(config=config, state=state, cue=cue, band_plan=plan)

    def test_12_time_and_band_plan_mutations_fail_closed(self) -> None:
        config = _config()
        state = _state(config, b4=(MATCH_A,), fast=(MATCH_A,))
        cue, plan = _cue(config)
        bad_cue = replace(cue, auditory_window_start_tick=1_001)
        bad_plan = replace(plan, observed_bands=tuple(reversed(plan.observed_bands)))
        for function in (subject.form_auditory_partial_cue_retrieval_336, baseline.form_direct_auditory_slot_scan_baseline_336):
            with self.subTest(function=function.__module__, mutation="time"), self.assertRaises(subject.S2KZError):
                function(config=config, state=state, cue=bad_cue, band_plan=plan)
            with self.subTest(function=function.__module__, mutation="plan"), self.assertRaises(subject.S2KZError):
                function(config=config, state=state, cue=cue, band_plan=bad_plan)

    def test_13_dimension_digest_and_state_mutations_fail_closed(self) -> None:
        config = _config()
        state = _state(config, b4=(MATCH_A,), fast=(MATCH_A,))
        cue, plan = _cue(config)
        bad_dimension = replace(cue, values=(0.10,) * 23 + (None,) * 25)
        bad_digest = replace(cue, observed_values_digest=ZERO_DIGEST)
        bad_state = replace(state, state_digest=ZERO_DIGEST)
        for function in (subject.form_auditory_partial_cue_retrieval_336, baseline.form_direct_auditory_slot_scan_baseline_336):
            for mutation_state, mutation_cue in ((state, bad_dimension), (state, bad_digest), (bad_state, cue)):
                with self.subTest(function=function.__module__, cue=len(mutation_cue.values)), self.assertRaises(subject.S2KZError):
                    function(config=config, state=mutation_state, cue=mutation_cue, band_plan=plan)

    def test_14_full_scan_read_only_and_worst_comparison_bound(self) -> None:
        config = _config()
        state = _state(
            config,
            b4=(MATCH_A,),
            fast=(MATCH_A, MISMATCH, MISMATCH),
            slow=(MISMATCH,) * 8,
        )
        cue, plan = _cue(config)
        before = (state.state_digest, state.b4_state, state.tspm_state, cue, plan)
        primary, direct = _run(config, state, cue, plan)
        self.assertEqual(before, (state.state_digest, state.b4_state, state.tspm_state, cue, plan))
        self.assertEqual(primary.prestate_digest, primary.poststate_digest)
        self.assertEqual(direct.prestate_digest, direct.poststate_digest)
        self.assertEqual(primary.resource_ledger.total_slot_scan_count, 20)
        self.assertEqual(primary.resource_ledger.observed_comparison_count, 480)
        self.assertEqual(primary.resource_ledger.total_value_comparison_count, 528)
        self.assertEqual(tuple(len(item.records) for item in primary.bank_scans), (9, 3, 8))

    def test_15_threshold_is_inclusive_but_a_equality_remains_exact(self) -> None:
        config = _config()
        boundary = (0.30,) * 24 + (0.25,) * 24
        state = _state(config, b4=(boundary,), fast=(boundary,))
        cue, plan = _cue(config)
        primary, direct = _run(config, state, cue, plan)
        self.assertEqual(_semantic(primary), _semantic(direct))
        self.assertTrue(primary.bank_scans[0].records[0].observed_match)
        self.assertLessEqual(primary.bank_scans[0].records[0].observed_distance, 0.2)
        self.assertEqual(primary.a_recent.status, "A_RECENT_APPLICABLE")

    def test_16_immutable_bounded_output_and_independent_baseline(self) -> None:
        config = _config()
        state = _state(config, b4=(MATCH_A,), fast=(MATCH_A,), slow=(MISMATCH,) * 8)
        primary, direct = _run(config, state, *_cue(config))
        sizes = tuple(len(subject.canonical_bytes(item.canonical_payload())) for item in (primary, direct))
        self.assertEqual(sizes, (primary.resource_ledger.serialized_output_bytes, direct.resource_ledger.serialized_output_bytes))
        self.assertLess(max(sizes), 32_768)
        baseline_source = Path(baseline.__file__).read_text(encoding="utf-8")
        self.assertNotIn("types._scan", baseline_source)
        self.assertNotIn("types._resolve", baseline_source)
        self.assertNotIn("types._decide", baseline_source)
        self.assertNotIn("ky-r", Path(subject.__file__).read_text(encoding="utf-8"))
        with self.assertRaises(FrozenInstanceError):
            primary.decision = "ABSTAIN_NO_CONTEXT"  # type: ignore[misc]
        print(f"S2KZ_QUALIFICATION_ID={QUALIFICATION_ID}")
        print(f"S2KZ_MAX_NEUTRAL_OUTPUT_BYTES={max(sizes)}")


if __name__ == "__main__":
    unittest.main()
