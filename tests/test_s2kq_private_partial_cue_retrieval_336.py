"""Neutral qualification for private S2-KQ partial-cue retrieval."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import unittest

from mcm_field_organism import _ppb1_reference as ppb1
from mcm_field_organism import _tspm1_private as tspm1
from mcm_field_organism import _tspm1_s2dr_private_comparison as comparison
from tools import _s2jw_default_live_profile as profile_module
from tools import _s2jw_profiled_memory_coordinator as coordinator
from tools import _s2jw_profiled_memory_ledger as memory_ledger
from tools import _s2kq_private_direct_slot_scan_baseline as baseline
from tools import _s2kq_private_partial_cue_retrieval_336 as subject


ZERO_DIGEST = "0" * 64
PARENT_DIGEST = "1" * 64
INPUT_DIGEST = "2" * 64
CLOCK_ID = "neutral-clock"


def _visual(visible: float, masked: float) -> tuple[float, ...]:
    return (visible,) * 32 + (masked,) * 256


MATCH_A = _visual(0.0, 0.25)
MATCH_B = _visual(0.0, 0.75)
MATCH_C = _visual(0.0, 1.0)
MISMATCH = _visual(1.0, 0.5)
AUDITORY = (0.0,) * 48


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
) -> ppb1.PPB1BankState:
    occupied = tuple(
        ppb1.PPB1PrototypeSlot(
            f"{config.bank_id}.slot.{index:03d}",
            True,
            item,
            3,
            min(index + 1, 3),
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
        CLOCK_ID if generation else None,
        800 if generation else None,
        occupied + free,
    )


def _state(
    config: coordinator.S2JVCoordinatorConfigV1,
    *,
    b4: tuple[tuple[float, ...], ...] = (),
    fast: tuple[tuple[float, ...], ...] = (),
    slow: tuple[tuple[float, ...], ...] = (),
    auditory_clock_id: str = CLOCK_ID,
    visual_clock_id: str = CLOCK_ID,
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
                AUDITORY + visual,
                index + 1,
            )
            for index, visual in enumerate(b4_values)
        ),
    )
    fast_slots = tuple(
        tspm1.TSPM1FastSlot(
            f"{config.tspm_config.fast_config.fast_bank_id}.slot.{index:03d}",
            True,
            AUDITORY,
            visual,
            1,
            generation - index,
            0,
            None,
        )
        for index, visual in enumerate(fast)
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
        900,
        visual_clock_id,
        900,
        fast_slots,
    )
    ppb_generation = 3 if slow else 0
    auditory_slow = _ppb_state(
        config.profile.profile.auditory_config,
        generation=ppb_generation,
        values=(),
    )
    visual_slow = _ppb_state(
        config.profile.profile.visual_config,
        generation=ppb_generation,
        values=slow,
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


def _cue(config: coordinator.S2JVCoordinatorConfigV1, visible: float = 0.0):
    return subject.build_masked_memory_cue_336(
        source_digest="3" * 64,
        config_digest=config.config_digest,
        field_clock_id=CLOCK_ID,
        window_start_tick=1_000,
        window_end_tick=1_100,
        visual_source_clock_id=CLOCK_ID,
        visual_window_start_tick=1_000,
        visual_window_end_tick=1_100,
        values=(visible,) * 32 + (None,) * 256,
    )


def _run(config, state, cue):
    primary = subject.form_partial_cue_retrieval_336(config=config, state=state, cue=cue)
    direct = baseline.form_direct_partial_cue_slot_scan_baseline_336(
        config=config,
        state=state,
        cue=cue,
    )
    return primary, direct


def _semantic(result: subject.PartialCueRetrievalResult336V1):
    return (
        tuple((scan.status, scan.eligible_count, scan.match_count) for scan in result.bank_scans),
        result.a_recent.status,
        result.a_recent.provenance_slot_digests,
        result.b_stable.status,
        result.b_stable.provenance_slot_digests,
        result.public_candidate_count,
        result.decision,
        None if result.hypothesis is None else result.hypothesis.area,
        None if result.hypothesis is None else result.hypothesis.proposed_values,
    )


class S2KQPrivatePartialCueRetrievalQualification(unittest.TestCase):
    def test_01_unique_a_from_equal_b4_and_fast(self) -> None:
        config = _config()
        state = _state(
            config,
            b4=(MATCH_A,),
            fast=(MATCH_A, MISMATCH, MISMATCH),
            slow=(MISMATCH, MISMATCH, MISMATCH, MISMATCH),
        )
        primary, direct = _run(config, state, _cue(config))
        self.assertEqual(_semantic(primary), _semantic(direct))
        self.assertEqual(primary.a_recent.status, "A_RECENT_APPLICABLE")
        self.assertEqual(len(primary.a_recent.provenance_slot_digests), 2)
        self.assertEqual(primary.decision, "ADMIT_SINGLE_CONTEXT")
        self.assertEqual(primary.hypothesis.area, "A_RECENT")
        self.assertEqual(primary.resource_ledger.total_value_comparison_count, 800)
        self.assertEqual(tuple(len(item.records) for item in primary.bank_scans), (9, 3, 4))

    def test_02_unique_b_stable(self) -> None:
        config = _config()
        state = _state(config, slow=(MATCH_B,))
        primary, direct = _run(config, state, _cue(config))
        self.assertEqual(_semantic(primary), _semantic(direct))
        self.assertEqual(primary.a_recent.status, "A_RECENT_NOT_APPLICABLE")
        self.assertEqual(primary.b_stable.status, "B_STABLE_APPLICABLE")
        self.assertEqual(primary.hypothesis.area, "B_STABLE")
        self.assertEqual(primary.hypothesis.proposed_values, (0.75,) * 256)

    def test_03_public_a_b_ambiguity(self) -> None:
        config = _config()
        state = _state(config, b4=(MATCH_A,), fast=(MATCH_A,), slow=(MATCH_B,))
        primary, direct = _run(config, state, _cue(config))
        self.assertEqual(_semantic(primary), _semantic(direct))
        self.assertEqual(primary.public_candidate_count, 2)
        self.assertEqual(primary.decision, "ABSTAIN_AMBIGUOUS_CONTEXT")
        self.assertIsNone(primary.hypothesis)

    def test_04_b4_bank_ambiguity_completes_all_scans(self) -> None:
        config = _config()
        state = _state(config, b4=(MATCH_A, MATCH_B), fast=(MATCH_A,), slow=(MATCH_C,))
        primary, direct = _run(config, state, _cue(config))
        self.assertEqual(_semantic(primary), _semantic(direct))
        self.assertEqual(primary.bank_scans[0].match_count, 2)
        self.assertEqual(primary.a_recent.status, "A_RECENT_INTERNAL_AMBIGUITY")
        self.assertEqual(primary.bank_scans[2].match_count, 1)
        self.assertEqual(primary.decision, "ABSTAIN_INTERNAL_AMBIGUITY")
        self.assertEqual(tuple(len(item.records) for item in primary.bank_scans), (9, 3, 4))

    def test_05_isolated_slow_bank_ambiguity(self) -> None:
        config = _config()
        state = _state(config, slow=(MATCH_A, MATCH_B))
        primary, direct = _run(config, state, _cue(config))
        self.assertEqual(_semantic(primary), _semantic(direct))
        self.assertEqual(primary.bank_scans[0].match_count, 0)
        self.assertEqual(primary.bank_scans[1].match_count, 0)
        self.assertEqual(primary.bank_scans[2].match_count, 2)
        self.assertEqual(primary.a_recent.status, "A_RECENT_NOT_APPLICABLE")
        self.assertEqual(primary.b_stable.status, "B_STABLE_INTERNAL_AMBIGUITY")
        self.assertEqual(primary.decision, "ABSTAIN_INTERNAL_AMBIGUITY")

    def test_06_unique_b4_fast_value_conflict(self) -> None:
        config = _config()
        state = _state(config, b4=(MATCH_A,), fast=(MATCH_B,))
        primary, direct = _run(config, state, _cue(config))
        self.assertEqual(_semantic(primary), _semantic(direct))
        self.assertEqual(primary.a_recent.status, "A_RECENT_INTERNAL_CONFLICT")
        self.assertEqual(primary.decision, "ABSTAIN_INTERNAL_CONFLICT")
        self.assertEqual(primary.resource_ledger.internal_equality_comparison_count, 288)

    def test_07_valid_empty_state_is_no_context(self) -> None:
        config = _config()
        state = _state(config)
        primary, direct = _run(config, state, _cue(config))
        self.assertEqual(_semantic(primary), _semantic(direct))
        self.assertEqual(primary.a_recent.status, "A_RECENT_ABSENT_VALID")
        self.assertEqual(primary.b_stable.status, "B_STABLE_ABSENT_VALID")
        self.assertEqual(primary.decision, "ABSTAIN_NO_CONTEXT")

    def test_08_present_but_visibly_incompatible(self) -> None:
        config = _config()
        state = _state(config, b4=(MATCH_A,), fast=(MATCH_A,), slow=(MATCH_B,))
        primary, direct = _run(config, state, _cue(config, visible=0.5))
        self.assertEqual(_semantic(primary), _semantic(direct))
        self.assertEqual(primary.a_recent.status, "A_RECENT_NOT_APPLICABLE")
        self.assertEqual(primary.b_stable.status, "B_STABLE_NOT_APPLICABLE")
        self.assertEqual(primary.decision, "ABSTAIN_NO_APPLICABLE_CONTEXT")

    def test_09_hypothesis_contains_only_masked_values_and_inputs_are_read_only(self) -> None:
        config = _config()
        state = _state(config, b4=(MATCH_A,), fast=(MATCH_A,))
        cue = _cue(config)
        before = (state.state_digest, state.b4_state, state.tspm_state, cue)
        primary, direct = _run(config, state, cue)
        self.assertEqual(before, (state.state_digest, state.b4_state, state.tspm_state, cue))
        self.assertEqual(primary.prestate_digest, primary.poststate_digest)
        self.assertEqual(direct.prestate_digest, direct.poststate_digest)
        self.assertEqual(primary.hypothesis.masked_positions, tuple(range(32, 288)))
        self.assertEqual(primary.hypothesis.observed_value_count, 0)
        self.assertEqual(primary.hypothesis.field_contact_count, 0)
        with self.assertRaises(FrozenInstanceError):
            primary.hypothesis.area = "B_STABLE"  # type: ignore[misc]

    def test_10_corrupt_state_and_cue_fail_closed(self) -> None:
        config = _config()
        state = _state(config, b4=(MATCH_A,), fast=(MATCH_A,))
        cue = _cue(config)
        corrupt_state = replace(state, state_digest=ZERO_DIGEST)
        corrupt_cue = replace(cue, mask_plan_digest=ZERO_DIGEST)
        for function in (
            subject.form_partial_cue_retrieval_336,
            baseline.form_direct_partial_cue_slot_scan_baseline_336,
        ):
            with self.subTest(function=function.__module__, mutation="state"):
                with self.assertRaises(subject.S2KQError):
                    function(config=config, state=corrupt_state, cue=cue)
            with self.subTest(function=function.__module__, mutation="cue"):
                with self.assertRaises(subject.S2KQError):
                    function(config=config, state=state, cue=corrupt_cue)

    def test_11_stale_source_and_dimension_fail_closed(self) -> None:
        config = _config()
        state = _state(config, b4=(MATCH_A,), fast=(MATCH_A,))
        stale = replace(_cue(config), visual_window_end_tick=900)
        malformed = replace(_cue(config), values=(0.0,) * 31 + (None,) * 257)
        for cue in (stale, malformed):
            for function in (
                subject.form_partial_cue_retrieval_336,
                baseline.form_direct_partial_cue_slot_scan_baseline_336,
            ):
                with self.subTest(cue=len(cue.values), function=function.__module__):
                    with self.assertRaises(subject.S2KQError):
                        function(config=config, state=state, cue=cue)

    def test_12_worst_materialized_output_is_bounded(self) -> None:
        config = _config()
        state = _state(
            config,
            b4=(MATCH_A,),
            fast=(MATCH_A, MISMATCH, MISMATCH),
            slow=(MISMATCH, MISMATCH, MISMATCH, MISMATCH),
        )
        primary, direct = _run(config, state, _cue(config))
        sizes = tuple(
            len(subject.canonical_bytes(item.canonical_payload()))
            for item in (primary, direct)
        )
        self.assertEqual(
            sizes,
            (
                primary.resource_ledger.serialized_output_bytes,
                direct.resource_ledger.serialized_output_bytes,
            ),
        )
        self.assertLess(max(sizes), 32_768)
        self.assertEqual(primary.resource_ledger.total_slot_scan_count, 16)
        self.assertEqual(primary.resource_ledger.total_value_comparison_count, 800)
        print(f"S2KQ_MAX_NEUTRAL_OUTPUT_BYTES={max(sizes)}")


if __name__ == "__main__":
    unittest.main()
