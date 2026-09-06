"""Bound neutral S2-NE qualification; no corpus or main history."""

from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
import hashlib
import json
import math
import unittest

import numpy as np

from tests import test_s2kz_private_auditory_partial_cue_retrieval_336 as fixtures
from tools import _s2ne_private_auditory_transfer as ne
from tools import _s2ne_private_direct_and_verification as independent
from tools import _s2ne_private_source_binding as binding
from tools import _s2jw_profiled_memory_coordinator as coordinator
from tools import _s2lg_private_ppb_transition_evaluation as transition
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from mcm_field_organism.receptor_contract import ReceptorContactFrame, from_visual_receptor_state

QUALIFICATION_ID = "s2ne-private-memory-transfer-qualification-20260906-01"
ZERO = (0.0,) * 48
SPARSE = (0.3,) + (0.0,) * 47
METRICS = {"maximum_arm_bytes": 0, "maximum_comparisons": 0,
           "neutral_formations": 0, "neutral_audio_analyses": 0,
           "neutral_visual_analyses": 0, "ppb_transitions": []}


class S2NEQualification(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        print("S2NE_NEUTRAL_METRICS=" + json.dumps(METRICS, sort_keys=True, allow_nan=False))

    def setUp(self):
        self.config = fixtures._config()

    def run_arms(self, state, observed=(0.1,) * 24, **time):
        cue, plan = fixtures._cue(self.config, observed, **time)
        before = ne.kz.digest(fixtures.comparison._canonical(state))
        results = []
        for rule in ne.RULES:
            args = dict(rule=rule, config=self.config, state=state, cue=cue, band_plan=plan)
            primary = ne.retrieve(**args)
            baseline = independent.direct_retrieve(**args)
            self.assertTrue(independent.compare_technical(primary, baseline))
            for arm in (primary, baseline):
                self.assertEqual("VERIFIED_READ_ONLY", independent.verify_arm(
                    arm=arm, config=self.config, state=state, cue=cue, band_plan=plan))
                size = len(ne.kz.canonical_bytes(arm.canonical_payload()))
                METRICS["maximum_arm_bytes"] = max(METRICS["maximum_arm_bytes"], size)
                count = arm.evidence.resource_ledger.total_value_comparison_count
                METRICS["maximum_comparisons"] = max(METRICS["maximum_comparisons"], count)
                self.assertEqual((9, 3, 8), tuple(len(s.records) for s in arm.evidence.bank_scans))
                self.assertLess(size, 32768)
                self.assertLessEqual(count, 528)
            results.append(primary)
        self.assertEqual(before, ne.kz.digest(fixtures.comparison._canonical(state)))
        return tuple(results), cue, plan

    def test_01_unchanged_historical_reference(self):
        state = fixtures._state(self.config, b4=(fixtures.MATCH_A,), fast=(fixtures.MATCH_A,))
        (reference, _), cue, plan = self.run_arms(state)
        raw = ne.kz.form_auditory_partial_cue_retrieval_336(
            config=self.config, state=state, cue=cue, band_plan=plan)
        self.assertEqual(reference.evidence, raw)

    def test_02_inclusive_maximum_boundary(self):
        for value, expected in ((0.2, True), (math.nextafter(0.2, math.inf), False)):
            candidate = (value,) + (0.0,) * 47
            state = fixtures._state(self.config, b4=(candidate,))
            (_, alternative), _, _ = self.run_arms(state, (0.0,) * 24)
            self.assertEqual(expected, alternative.evidence.bank_scans[0].records[0].observed_match)

    def test_03_binary64_reference_is_not_statistics_mean(self):
        candidate = (0.2,) * 24 + (0.0,) * 24
        state = fixtures._state(self.config, b4=(candidate,))
        (reference, alternative), _, _ = self.run_arms(state, (0.0,) * 24)
        row = reference.evidence.bank_scans[0].records[0]
        self.assertEqual(sum((0.2,) * 24) / 24, row.observed_distance)
        self.assertGreater(row.observed_distance, 0.2)
        self.assertFalse(row.observed_match)
        self.assertTrue(alternative.evidence.bank_scans[0].records[0].observed_match)

    def test_04_slow_arithmetic_and_support_unchanged(self):
        for candidate in ((0.02,) * 24 + (0.0,) * 24, (0.48,) + (0.0,) * 47):
            for support in (2, 3):
                state = fixtures._state(self.config, slow=(candidate,), slow_supports=(support,))
                (reference, alternative), _, _ = self.run_arms(state, (0.0,) * 24)
                a, b = reference.evidence.bank_scans[2], alternative.evidence.bank_scans[2]
                self.assertEqual(a, b)
                self.assertEqual(support >= 3, a.records[0].eligible)
                if support == 3:
                    self.assertEqual(sum(candidate[:24]) / 24, a.records[0].observed_distance)

    def test_05_internal_full_candidate_equality(self):
        for fast, decision in ((fixtures.MATCH_A, "ADMIT_SINGLE_CONTEXT"),
                               (fixtures.MATCH_B, "ABSTAIN_INTERNAL_CONFLICT")):
            state = fixtures._state(self.config, b4=(fixtures.MATCH_A,), fast=(fast,))
            arms, _, _ = self.run_arms(state)
            for arm in arms:
                self.assertEqual(decision, arm.evidence.decision)
                self.assertEqual(48, arm.evidence.resource_ledger.internal_equality_comparison_count)

    def test_06_all_banks_complete_despite_ambiguity(self):
        for banks in (dict(b4=(fixtures.MATCH_A,) * 2), dict(fast=(fixtures.MATCH_A,) * 2),
                      dict(slow=(fixtures.MATCH_A,) * 2)):
            arms, _, _ = self.run_arms(fixtures._state(self.config, **banks))
            for arm in arms:
                self.assertEqual("ABSTAIN_INTERNAL_AMBIGUITY", arm.evidence.decision)
                self.assertEqual(20, arm.evidence.resource_ledger.total_slot_scan_count)

    def test_07_no_public_b_preference(self):
        state = fixtures._state(self.config, b4=(fixtures.MATCH_A,), slow=(fixtures.MATCH_A,))
        arms, _, _ = self.run_arms(state)
        for arm in arms:
            self.assertEqual("ABSTAIN_AMBIGUOUS_CONTEXT", arm.evidence.decision)
            self.assertIsNone(arm.evidence.hypothesis)

    def test_08_a_rule_only_changes_a(self):
        state = fixtures._state(self.config, b4=(SPARSE,), fast=(SPARSE,), slow=(ZERO,))
        (reference, alternative), _, _ = self.run_arms(state, (0.0,) * 24)
        self.assertEqual("ABSTAIN_AMBIGUOUS_CONTEXT", reference.evidence.decision)
        self.assertEqual("B_STABLE_AUDITORY", alternative.evidence.hypothesis.area)
        self.assertEqual(reference.evidence.bank_scans[2], alternative.evidence.bank_scans[2])

    def test_09_absence_and_incompatibility(self):
        for state, expected in ((fixtures._state(self.config), "ABSTAIN_NO_CONTEXT"),
                               (fixtures._state(self.config, fast=(fixtures.MISMATCH,)),
                                "ABSTAIN_NO_APPLICABLE_CONTEXT")):
            arms, _, _ = self.run_arms(state)
            self.assertTrue(all(a.evidence.decision == expected for a in arms))

    def test_10_native_audio_time_only(self):
        state = fixtures._state(self.config, b4=(fixtures.MATCH_A,),
                                auditory_clock_id="s2ne-native-audio", visual_clock_id="different-video")
        self.run_arms(state, clock_id="s2ne-native-audio")
        for time in (dict(clock_id="different-video"),
                     dict(clock_id="s2ne-native-audio", start=899, end=5800)):
            cue, plan = fixtures._cue(self.config, **time)
            for function in (ne.retrieve, independent.direct_retrieve):
                for rule in ne.RULES:
                    with self.assertRaises(ne.kz.S2KZError):
                        function(rule=rule, config=self.config, state=state, cue=cue, band_plan=plan)

    def test_11_cue_type_digest_and_hidden_values(self):
        cue, plan = fixtures._cue(self.config)
        state = fixtures._state(self.config)
        for bad in (replace(cue, cue_digest="0" * 64),
                    replace(cue, auditory_window_end_tick=1),
                    replace(cue, pcm_payload_digest="invalid"),
                    replace(cue, values=cue.values[:24] + (0.0,) * 24),
                    replace(cue, values=cue.values[:47]), None):
            for function in (ne.retrieve, independent.direct_retrieve):
                with self.assertRaises(ne.kz.S2KZError):
                    function(rule=ne.ALTERNATIVE, config=self.config, state=state, cue=bad, band_plan=plan)
        other = replace(cue, receptor_values_digest="6" * 64)
        other = replace(other, cue_digest=ne.kz.digest(other.payload_without_digest()))
        left = ne.retrieve(rule=ne.ALTERNATIVE, config=self.config, state=state, cue=cue, band_plan=plan)
        right = ne.retrieve(rule=ne.ALTERNATIVE, config=self.config, state=state, cue=other, band_plan=plan)
        self.assertEqual(left.evidence.bank_scans, right.evidence.bank_scans)

    def test_12_state_and_config_tampering(self):
        state = fixtures._state(self.config, b4=(fixtures.MATCH_A,))
        cue, plan = fixtures._cue(self.config)
        with self.assertRaises(coordinator.S2JWCoordinatorError):
            replace(self.config, config_digest="0" * 64)
        for config, bad in ((self.config, replace(state, state_digest="0" * 64)),
                            (None, state)):
            for function in (ne.retrieve, independent.direct_retrieve):
                with self.assertRaises(ne.kz.S2KZError):
                    function(rule=ne.ALTERNATIVE, config=config, state=bad, cue=cue, band_plan=plan)

    def test_13_verifier_rejects_rehashed_false_record(self):
        state = fixtures._state(self.config, b4=(fixtures.MATCH_A,))
        (arm, _), cue, plan = self.run_arms(state)
        scan = arm.evidence.bank_scans[0]
        row = replace(scan.records[0], slot_digest="0" * 64)
        row = replace(row, record_digest=ne.kz.digest(row.payload_without_digest()))
        changed = replace(scan, records=(row,) + scan.records[1:])
        changed = replace(changed, scan_digest=ne.kz.digest(changed.payload_without_digest()))
        result = replace(arm.evidence, bank_scans=(changed,) + arm.evidence.bank_scans[1:])
        result = replace(result, result_digest=ne.kz.digest(result.payload_without_digest()))
        bad = replace(arm, evidence=result)
        bad = replace(bad, arm_digest=ne.kz.digest(bad.payload_without_digest()))
        with self.assertRaises(ne.kz.S2KZError):
            independent.verify_arm(arm=bad, config=self.config, state=state, cue=cue, band_plan=plan)
        with self.assertRaises(ne.kz.S2KZError):
            independent.verify_arm(arm=replace(arm, sources=()), config=self.config,
                                   state=state, cue=cue, band_plan=plan)

    def test_14_valid_abstention_is_not_a_technical_failure(self):
        state = fixtures._state(self.config, b4=(fixtures.MATCH_A,) * 2)
        arms, _, _ = self.run_arms(state)
        for arm in arms:
            expected_only_in_evaluator = "ADMIT_SINGLE_CONTEXT"
            self.assertNotEqual(expected_only_in_evaluator, arm.evidence.decision)
            self.assertIsNone(arm.evidence.hypothesis)

    def test_15_immutability_and_resource_envelope(self):
        candidate = tuple(0.1234567890123456 + i * 0.00001 for i in range(48))
        state = fixtures._state(self.config, b4=(candidate,) * 9,
                                fast=(candidate,) * 3, slow=(candidate,) * 8)
        arms, _, _ = self.run_arms(state)
        for arm in arms:
            self.assertEqual(480, arm.evidence.resource_ledger.observed_comparison_count)
            self.assertLess(52 * len(ne.kz.canonical_bytes(arm.canonical_payload())), ne.MAX_RECORDING_BYTES)
            with self.assertRaises(FrozenInstanceError):
                arm.rule = "other"
        self.assertFalse(ne.MAIN_GATE)
        self.assertEqual((20, 13, 52, 1040, 24960, 2496, 27456), ne.MAIN_BUDGET)

    def test_16_binary64_ppb_expression_all_dimensions(self):
        for size in (48, 288):
            values = tuple(0.1234567890123456 for _ in range(size))
            current = values
            for _ in range(2):
                expected = tuple(float(Fraction.from_float(float(
                    Fraction.from_float(1.0 - 0.05) * Fraction.from_float(p)))
                    + Fraction.from_float(float(Fraction.from_float(0.05) * Fraction.from_float(x))))
                    for p, x in zip(current, values, strict=True))
                current = transition._matched_update(current, values)
                self.assertEqual(expected, current)
            self.assertEqual(size, len(current))

    def test_17_neutral_real_av_adapter_and_ppb_chain(self):
        state = coordinator.initial_s2jv_composite_state(self.config)
        profile = self.config.profile.profile.auditory_config
        chain = {"auditory": [], "visual": []}
        for ordinal in range(4):
            pcm = np.zeros(4800, dtype="<f4")
            ah = hashlib.sha256(pcm.tobytes()).hexdigest()
            values = LogSpectralReceptor(LogSpectralConfig()).analyze(pcm)
            METRICS["neutral_audio_analyses"] += 1
            del pcm
            auditory = ReceptorContactFrame("auditory", profile.geometry_id,
                f"s2ne-neutral-e{ordinal:02d}", "s2ne-neutral-audio-sample",
                9600 * ordinal, 9600 * ordinal + 4800, profile.carrier_ids, values)
            rgb = np.full((1080, 1920, 3), 37, dtype=np.uint8)
            vh = hashlib.sha256(rgb.tobytes()).hexdigest()
            visual_state = LocalChannelGridReceptor(VisualGridConfig()).analyze(rgb, frame_index=6 * ordinal + 2)
            METRICS["neutral_visual_analyses"] += 1
            del rgb
            visual = from_visual_receptor_state(visual_state)
            args = dict(config=self.config, auditory=auditory, visual=visual, ordinal=ordinal,
                        history_id="s2ne-neutral", event_id=f"s2ne-neutral-pair-{ordinal:02d}",
                        auditory_payload_digest=ah, visual_payload_digest=vh)
            pair = binding.bind_pair(**args)
            self.assertEqual((48, 288), (len(pair.auditory.timed_frame.frame.values),
                                       len(pair.visual.timed_frame.frame.values)))
            self.assertEqual((6 * ordinal + 2) * 1000000000 // 30, pair.plan.overlap_start_tick)
            if ordinal == 0:
                with self.assertRaises(ne.kz.S2KZError):
                    binding.bind_pair(**{**args, "ordinal": 1})
                with self.assertRaises(Exception):
                    binding.bind_pair(**{**args, "auditory_payload_digest": "bad"})
            source = coordinator.bind_s2jv_coordinator_input(config=self.config, source=pair)
            owner = coordinator.S2JVFormationOwner(f"s2ne-owner-{ordinal:02d}",
                f"s2ne-authorization-{ordinal:02d}", f"s2ne-consumption-{ordinal:02d}",
                self.config.config_digest, state.state_digest, source.input_digest)
            formed = coordinator.advance_s2jv_atomic(config=self.config, prestate=state, source=source, owner=owner)
            METRICS["neutral_formations"] += 1
            self.assertEqual(state.state_digest, formed.poststate.parent_state_digest)
            if ordinal:
                for modality in chain:
                    bank = getattr(formed.poststate.tspm_state, modality + "_ppb1_state")
                    kwargs = dict(config=self.config, prestate=state, poststate=formed.poststate,
                                  source=source, modality=modality, slot_id=bank.slots[0].slot_id)
                    receipt = binding.bind_ppb_transition(**kwargs)
                    chain[modality].append(receipt)
                    self.assertEqual(ne.kz.digest(receipt.payload_without_digest()), receipt.transition_digest)
                    with self.assertRaises(ne.kz.S2KZError):
                        binding.bind_ppb_transition(**{**kwargs, "slot_id": "foreign-slot"})
            state = formed.poststate
        for modality, receipts in chain.items():
            self.assertEqual(("CREATED", "MATCHED", "MATCHED"), tuple(r.event for r in receipts))
            self.assertEqual((1, 2, 3), tuple(r.support for r in receipts))
            bank = getattr(state.tspm_state, modality + "_ppb1_state")
            final = bank.slots[0].prototype_values
            self.assertEqual(ne.kz.digest(list(final)), receipts[-1].full_values_digest)
            masked = final[24:] if modality == "auditory" else final[32:]
            self.assertEqual(ne.kz.digest(list(masked)), receipts[-1].masked_values_digest)
            METRICS["ppb_transitions"].extend(r.payload_without_digest() for r in receipts)
        pcm = np.zeros(4800, dtype="<f4")
        ah = hashlib.sha256(pcm.tobytes()).hexdigest()
        values = LogSpectralReceptor(LogSpectralConfig()).analyze(pcm)
        METRICS["neutral_audio_analyses"] += 1
        del pcm
        plan = ne.kz.build_auditory_band_plan_48()
        cue = ne.kz.build_masked_auditory_cue_48(pcm_payload_digest=ah,
            receptor_state_digest=ne.kz.digest(dict(values=list(values), start=38400, end=43200)),
            receptor_values_digest=ne.kz.digest(list(values)), observed_values=values[:24],
            config_digest=self.config.config_digest, auditory_source_clock_id="s2ne-neutral-audio-sample",
            auditory_window_start_tick=38400, auditory_window_end_tick=43200, band_plan=plan)
        before = ne.kz.digest(fixtures.comparison._canonical(state))
        for rule in ne.RULES:
            kwargs = dict(rule=rule, config=self.config, state=state, cue=cue, band_plan=plan)
            a, b = ne.retrieve(**kwargs), independent.direct_retrieve(**kwargs)
            self.assertTrue(independent.compare_technical(a, b))
            for arm in (a, b):
                self.assertEqual("VERIFIED_READ_ONLY", independent.verify_arm(
                    arm=arm, config=self.config, state=state, cue=cue, band_plan=plan))
        self.assertEqual(before, ne.kz.digest(fixtures.comparison._canonical(state)))

    def test_18_rules_and_result_roles_are_bound(self):
        state = fixtures._state(self.config)
        arms, cue, plan = self.run_arms(state)
        for function in (ne.retrieve, independent.direct_retrieve):
            with self.assertRaises(ne.kz.S2KZError):
                function(rule="MEAN_L1_24", config=self.config, state=state, cue=cue, band_plan=plan)
        with self.assertRaises(ne.kz.S2KZError):
            independent.verify_arm(arm=replace(arms[0], implementation="DIRECT_BASELINE"),
                                   config=self.config, state=state, cue=cue, band_plan=plan)


if __name__ == "__main__":
    unittest.main()
