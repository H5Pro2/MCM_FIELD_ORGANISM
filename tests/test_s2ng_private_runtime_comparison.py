"""One bounded neutral composition qualification; no MT source generation."""

import ast
from copy import deepcopy
from dataclasses import asdict, FrozenInstanceError, replace
import json
import math
import os
from pathlib import Path
import tempfile
import unittest

from tools import _s2ng_private_runtime_comparison as run
from tools import _s2ng_private_comparison_verification as verify
from tools import _s2ng_private_comparison_evaluation as evaluate
from tests import test_s2kz_private_auditory_partial_cue_retrieval_336 as neutral
from mcm_field_organism.receptor_contract import ReceptorContactFrame

QUALIFICATION_ID = "s2ng-private-runtime-composition-qualification-20260906-02"
CLOCK = "s2ng-neutral-field-clock"
METRICS = dict(main_calls=0, source_generations=0, receptor_calls=0, neutral_formations=0)


def fixture(config, *, scan_failure=False):
    """Synthetic reduced values, real immutable frame/pair/cue types."""
    def timed(modality, n, values, wrong=False):
        p = getattr(config.profile.profile, modality + "_config")
        if modality == "auditory":
            start, end, clock = n*9600, n*9600+4800, "s2ng-neutral-audio"
            first = n*200_000_000
        else:
            start, end, clock = n*6+2, n*6+3, "video.frame"
            first = start*1_000_000_000//30
        f = ReceptorContactFrame(modality, p.geometry_id, f"s2ng-neutral-{modality}-{n}",
            "foreign-audio" if wrong else clock, start, end, p.carrier_ids, values)
        return run.field.OrganismTimedReceptorFrame(f, run.field.CommonFieldTime(CLOCK, first, n*200_000_000+100_000_000))

    events, last = [], 0
    for n, kind in enumerate(("COMPLETE_AV_PERCEPTION", "PARTIAL_AUDITORY_CUE", "PARTIAL_AUDITORY_CUE", "PARTIAL_VISUAL_CUE")):
        if scan_failure and n > 1:
            break
        if n == 0:
            a, v = timed("auditory", n, (0.1,)*48), timed("visual", n, (0.25,)*288)
            plan = run.pairing.build_s2jv_pairing_plan(pair_id="s2ng-neutral-pair", source_contract_id="s2ng-neutral-source",
                profile=config.profile, auditory=a, visual=v, auditory_payload_digest="1"*64, visual_payload_digest="2"*64)
            operation = run.pairing.bind_s2jv_default_live_pair(pairing_plan=plan, profile=config.profile, auditory=a, visual=v)
            perception, frames = operation.pairing_digest, (a, v)
        elif kind == "PARTIAL_AUDITORY_CUE":
            a = timed("auditory", n, ((0.1 if n == 1 else 0.9),)*48, scan_failure)
            plan = run.audio.kz.build_auditory_band_plan_48()
            cue = run.audio.kz.build_masked_auditory_cue_48(pcm_payload_digest=str(n+2)*64,
                receptor_state_digest=run.digest(asdict(a.frame)), receptor_values_digest=run.digest(list(a.frame.values)),
                config_digest=config.config_digest, auditory_source_clock_id=a.frame.clock_id,
                auditory_window_start_tick=a.frame.window_start_tick, auditory_window_end_tick=a.frame.window_end_tick,
                observed_values=a.frame.values[:24], band_plan=plan)
            operation = run.stream.AuditoryCueOperationV1(cue, plan)
            perception, frames = cue.cue_digest, (a,)
        else:
            v = timed("visual", n, (0.25,)*32+(0.0,)*256)
            operation = run.visual.build_masked_memory_cue_336(source_digest="6"*64, config_digest=config.config_digest,
                field_clock_id=CLOCK, window_start_tick=v.field_time.window_start_tick, window_end_tick=v.field_time.window_end_tick,
                visual_source_clock_id=v.frame.clock_id, visual_window_start_tick=v.frame.window_start_tick,
                visual_window_end_tick=v.frame.window_end_tick, values=(0.25,)*32+(None,)*256)
            perception, frames = operation.cue_digest, (v,)
        end = frames[0].field_time.window_end_tick
        field_input = run.field.S2LOFieldInputV1(perception, last, end, frames)
        events.append(run.stream.build_perception_stream_event(event_id=f"s2ng-neutral-e{n+1:02d}", ordinal=n+1,
            event_type=kind, source_digest=run.digest(dict(ordinal=n+1, frames=[asdict(t) for t in frames])),
            perception_digest=perception, field_projection_digest=perception, operation_projection_digest=perception,
            field_payload=field_input, operation_payload=operation))
        last = end
    return tuple(events)


def archive(name, value):
    root = os.environ.get("S2NG_QUALIFICATION_ARTIFACTS")
    if root:
        run.ne.atomic_write(Path(root)/name, value)


class CompositionQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = run.ne.make_config()
        cls.events = fixture(cls.config)
        cls.composition = run.RuntimeComparison(config=cls.config, events=cls.events, field_clock_id=CLOCK,
            comparison_id="s2ng-neutral-composition-01")
        cls.initial_ids = [(id(b[0].state.field), id(b[1].state), id(s._processor), id(s._state))
                           for b, s in zip(cls.composition.branches, cls.composition.subjects, strict=True)]
        for _ in cls.events:
            cls.composition.process_next()
        cls.record = cls.composition.finish()
        archive("neutral-recording.json", cls.record)
        cls.proof = verify.verify_record(cls.record, config=cls.config)
        archive("neutral-verification.json", cls.proof)
        cls.expectations = (evaluate.ExpectationV1(2, "auditory", (run.digest([0.1]*48),), True, "EXACT", "LOW"),
            evaluate.ExpectationV1(3, "auditory", (), False, "UNKNOWN", "LOW"),
            evaluate.ExpectationV1(4, "visual", (run.digest([0.25]*288),), True, "EXACT", "LOW"))
        cls.evaluation = evaluate.evaluate(cls.record, cls.proof, cls.expectations)
        archive("neutral-evaluation.json", cls.evaluation)
        METRICS.update(neutral_formations=2, runtime_events=8, recording_bytes=len(run.canonical(cls.record)),
            maximum_input_bytes=max(len(run.canonical(x)) for x in cls.record["inputs"]),
            maximum_pair_bytes=max(len(run.canonical(x)) for x in cls.record["pairs"]),
            maximum_scan_bytes=max(len(run.canonical(x["value"])) for x in cls.record["scans"]),
            maximum_state_bytes=max(len(run.canonical(x)) for x in cls.record["states"].values()),
            proof=cls.proof)

    @classmethod
    def tearDownClass(cls):
        print("S2NG_NEUTRAL_METRICS=" + json.dumps(METRICS, sort_keys=True))

    def changed(self, f):
        r = deepcopy(self.record)
        f(r)
        r["record_digest"] = run.digest({k: v for k, v in r.items() if k != "record_digest"})
        return r

    def test_01_closed_main_and_fixed_binding(self):
        self.assertFalse(run.MAIN_GATE)
        with self.assertRaises(run.S2NGError):
            run.RuntimeComparison(config=self.config, events=self.events, field_clock_id=CLOCK, comparison_id="s2ng-forbidden", mode="MAIN")
        for b in self.composition.bindings:
            with self.assertRaises(FrozenInstanceError):
                b.rule = "OTHER"
            with self.assertRaises(run.S2NGError):
                run.validate_binding(replace(b, rule="OTHER"), self.config)
        self.assertEqual(run.audio.RULES, tuple(b.rule for b in self.composition.bindings))

    def test_02_instances_and_event_owners_isolated(self):
        self.assertTrue(all(a != b for a, b in zip(*self.initial_ids, strict=True)))
        a, b = self.composition.subjects
        self.assertIsNot(a, b)
        self.assertIsNot(a._processor, b._processor)
        self.assertNotEqual(a._state.state_digest, b._state.state_digest)
        text = (run.ROOT/"tools/_s2mr_private_minimal_mcm_runtime.py").read_text(encoding="utf-8")
        tree = ast.parse(text)
        method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "process_once")
        self.assertEqual(1, sum(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                               and n.func.attr == "PerceptionEventOwner" for n in ast.walk(method)))
        self.composition._isolation()

    def test_03_shared_immutable_input_exact_roundtrip(self):
        self.assertIs(self.events, self.composition.events)
        for event, p in zip(self.events, self.record["inputs"], strict=True):
            self.assertEqual(event, verify.decode_input(p, self.config))
            with self.assertRaises(FrozenInstanceError):
                event.ordinal = 99

    def test_04_native_time_and_input_integrity(self):
        e = self.events[1]
        t = e.field_payload.timed_frames[0]
        bad = replace(e, field_payload=replace(e.field_payload, timed_frames=(replace(t,
            frame=replace(t.frame, clock_id="other-clock")),)))
        with self.assertRaises(run.S2NGError):
            run.pack_input(bad, self.config)
        with self.assertRaises(run.S2NGError):
            run.pack_input(replace(e, event_digest="0"*64), self.config)

    def test_05_field_and_memory_correspond(self):
        self.assertEqual("RECORDING_COMPLETE", self.proof["status"])
        self.assertEqual(1440, self.proof["field_contacts"])
        for pair in self.record["pairs"]:
            a, b = pair["arms"]
            self.assertEqual(a["field"], b["field"])
            self.assertEqual(a["memory"], b["memory"])
            self.assertNotEqual(a["post"]["snapshot_digest"], b["post"]["snapshot_digest"])

    def test_06_read_only_cues_and_visual_unchanged(self):
        for pair in self.record["pairs"][1:]:
            for arm in pair["arms"]:
                self.assertEqual(arm["pre"]["memory_state_digest"], arm["post"]["memory_state_digest"])
                self.assertEqual("READ_ONLY_UNCHANGED", arm["step"]["memory_status"])
        values = [s["value"] for s in self.record["scans"] if s["ordinal"] == 4 and s["role"] == "PRIMARY"]
        self.assertEqual(values[0], values[1])

    def test_07_lifecycle(self):
        for end, subject in zip(self.record["final"], self.composition.subjects, strict=True):
            self.assertEqual("CLOSED", end["status"])
            self.assertEqual(end, asdict(subject.snapshot()))
            with self.assertRaises(run.runtime.S2MRRuntimeError):
                subject.process_once(self.events[-1])
            with self.assertRaises(run.runtime.S2MRRuntimeError):
                subject.close()
        with self.assertRaises(run.S2NGError):
            self.composition.process_next()

    def test_08_full_scan_receipts(self):
        self.assertEqual(12, len(self.record["scans"]))
        for s in self.record["scans"]:
            result = s["value"].get("evidence", s["value"])
            expected = (9, 3, 4) if s["ordinal"] == 4 else (9, 3, 8)
            self.assertEqual(expected, tuple(len(b["records"]) for b in result["bank_scans"]))
            self.assertLess(len(run.canonical(s["value"])), 32768)

    def test_09_missing_and_extra_receipt(self):
        for change in (lambda r: r["scans"].pop(), lambda r: r["scans"].append(deepcopy(r["scans"][0]))):
            with self.subTest(change=change):
                with self.assertRaises(run.S2NGError):
                    verify.verify_record(self.changed(change), config=self.config)

    def test_10_reordered_and_rebound_receipt(self):
        for change in (lambda r: r["pairs"].reverse(), lambda r: r["scans"][0].update(arm=1),
                       lambda r: r["scans"][0].update(ordinal=3)):
            with self.subTest(change=change):
                with self.assertRaises(run.S2NGError):
                    verify.verify_record(self.changed(change), config=self.config)

    def test_11_source_and_state_tampering(self):
        for change in (lambda r: r["sources"][0].__setitem__(1, "0"*64),
                       lambda r: r["states"][next(iter(r["states"]))].update(generation=99),
                       lambda r: r["inputs"][1]["operation"]["cue"].update(auditory_window_end_tick=1)):
            with self.subTest(change=change):
                with self.assertRaises(run.S2NGError):
                    verify.verify_record(self.changed(change), config=self.config)

    def test_12_valid_abstention_verified_but_prediction_can_fail(self):
        expected = tuple(replace(e, target_values_digests=(run.digest([0.9]*48),), expected_context=True)
                         if e.ordinal == 3 else e for e in self.expectations)
        result = evaluate.evaluate(self.record, self.proof, expected)
        row = result["rows"][1]
        self.assertTrue(row["reference_abstains"] and row["alternative_abstains"])
        self.assertFalse(row["alternative_correct"])
        self.assertEqual("RECORDING_COMPLETE", self.proof["status"])

    def test_13_scan_error_does_not_rollback_field(self):
        events = fixture(self.config, scan_failure=True)
        c = run.RuntimeComparison(config=self.config, events=events, field_clock_id=CLOCK, comparison_id="s2ng-neutral-failure")
        for _ in events:
            c.process_next()
        r = c.finish()
        METRICS["neutral_formations"] += 2
        archive("neutral-scan-failure.json", r)
        p = verify.verify_record(r, config=self.config)
        archive("neutral-scan-failure-verification.json", p)
        self.assertEqual("NOT_EVALUABLE", p["status"])
        for arm in r["pairs"][-1]["arms"]:
            self.assertEqual("FIELD_CONTACT_RECORDED", arm["step"]["perception_status"])
            self.assertEqual("SCAN_FAILED", arm["step"]["context_status"])
            self.assertEqual(2, arm["field"]["step_count"])
            self.assertEqual(arm["pre"]["memory_state_digest"], arm["post"]["memory_state_digest"])
        with self.assertRaises(run.S2NGError):
            evaluate.evaluate(r, p, ())

    def adapter_arms(self, state, cue, plan):
        results = []
        for binding in self.composition.bindings:
            store = {}
            adapter = run.AudioAdapter(binding, self.config, False, store)
            e = replace(self.events[1], operation_payload=run.stream.AuditoryCueOperationV1(cue, plan),
                        operation_projection_digest=cue.cue_digest)
            adapter(state, e)
            value = store[2, "PRIMARY"]
            run.direct.verify_arm(arm=value, config=self.config, state=state, cue=cue, band_plan=plan)
            results.append(value.evidence)
        return results

    def test_14_historical_boundary_and_unmodified_slow(self):
        value = (0.2,)*24+(0.0,)*24
        state = neutral._state(self.config, b4=(value,), slow=((0.02,)*48,))
        cue, plan = neutral._cue(self.config, (0.0,)*24)
        a, b = self.adapter_arms(state, cue, plan)
        self.assertEqual(sum((0.2,)*24)/24, a.bank_scans[0].records[0].observed_distance)
        self.assertFalse(a.bank_scans[0].records[0].observed_match)
        self.assertTrue(b.bank_scans[0].records[0].observed_match)
        self.assertEqual(a.bank_scans[2], b.bank_scans[2])
        self.assertEqual(sum((0.02,)*24)/24, b.bank_scans[2].records[0].observed_distance)

    def test_15_full_capacity_and_hidden_equality(self):
        value = neutral.MATCH_A
        state = neutral._state(self.config, b4=(value,)*9, fast=(value,)*3, slow=(value,)*8)
        cue, plan = neutral._cue(self.config)
        for result in self.adapter_arms(state, cue, plan):
            self.assertEqual(480, result.resource_ledger.observed_comparison_count)
            self.assertLessEqual(result.resource_ledger.total_value_comparison_count, 528)
            self.assertEqual("ABSTAIN_INTERNAL_AMBIGUITY", result.decision)
        changed = neutral._state(self.config, b4=(value,), fast=(neutral.MATCH_B,))
        for result in self.adapter_arms(changed, cue, plan):
            self.assertEqual("ABSTAIN_INTERNAL_CONFLICT", result.decision)

    def test_16_evaluation_gains_losses_discarded_separate(self):
        template = dict(modality="auditory", expected_context=True, variant="VARIED", competition="PRESENT",
            reference_false_admission=False, alternative_false_admission=False,
            reference_abstains=False, alternative_abstains=False, discarded_target_candidates=[])
        rows = [dict(template, ordinal=1, reference_correct=True, alternative_correct=False,
                     discarded_target_candidates=[{"slot_id": "a-slot"}]),
                dict(template, ordinal=2, reference_correct=False, alternative_correct=True),
                dict(template, ordinal=3, reference_correct=True, alternative_correct=True)]
        group = evaluate.summarize(rows)["auditory"]["ALL"]
        self.assertEqual((3, 2, 1, 1), tuple(group[k] for k in ("N", "D", "R", "L")))
        self.assertEqual([1], group["losses"])
        self.assertEqual([2], group["gains"])
        self.assertEqual(1, len(group["discarded_target_candidates"]))

    def test_17_audio_empty_denominator_not_filled_by_visual(self):
        r = deepcopy(self.evaluation["rows"])
        for row in r:
            if row["modality"] == "auditory":
                row["reference_correct"] = False
        summary = evaluate.summarize(r)
        self.assertEqual(0, summary["auditory"]["ALL"]["D"])
        self.assertEqual("ERHALTUNG_NICHT_GEPRUEFT", summary["auditory"]["ALL"]["retention_status"])
        self.assertEqual(1, summary["visual"]["ALL"]["D"])

    def test_18_evaluation_reports_target_discard(self):
        # Synthetic, already-bound neutral arm evidence; no sealed corpus.
        r = deepcopy(self.record)
        p = deepcopy(self.proof)
        for s in r["scans"]:
            if s["ordinal"] == 2 and s["role"] == "PRIMARY" and s["arm"] == 1:
                s["value"]["evidence"]["bank_scans"][0]["records"][0]["observed_match"] = False
        r["record_digest"] = run.digest({k: v for k, v in r.items() if k != "record_digest"})
        p["record_digest"] = r["record_digest"]
        p["verification_digest"] = run.digest({k: v for k, v in p.items() if k != "verification_digest"})
        result = evaluate.evaluate(r, p, self.expectations)
        self.assertEqual(1, len(result["rows"][0]["discarded_target_candidates"]))
        self.assertEqual(1, result["groups"]["auditory"]["ALL"]["R"])

    def test_19_resources_prebound(self):
        types = ("COMPLETE_AV_PERCEPTION",)*20+("PARTIAL_AUDITORY_CUE",)*4+("PARTIAL_VISUAL_CUE",)*4
        b = run.budget(types)
        self.assertEqual((16, 16, 576, 7680, 8192, 5376, 21248, 16128),
            tuple(b[k] for k in ("auditory_scans", "visual_scans", "slot_visits", "band_differences",
                "visual_comparisons", "equality_comparisons", "value_comparisons", "field_contacts")))
        self.assertEqual(4096000, run.SERIALIZATION_BOUND)
        self.assertLess(run.SERIALIZATION_BOUND, run.MAX_BYTES)
        with self.assertRaises(run.S2NGError):
            run.budget(types+("PARTIAL_AUDITORY_CUE",))

    def test_20_size_and_exclusive_atomic_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)/"recording.json"
            run.ne.atomic_write(p, self.record)
            before = p.read_bytes()
            with self.assertRaises(FileExistsError):
                run.ne.atomic_write(p, self.record)
            self.assertEqual(before, p.read_bytes())
            with self.assertRaises(run.ne.RunError):
                run.ne.atomic_write(Path(directory)/"oversize.json", {"v": "x"*run.MAX_BYTES})
        with self.assertRaises(run.S2NGError):
            verify.verify_record({"oversize": "x"*run.MAX_BYTES}, config=self.config)

    def test_21_postprocessing_is_read_only(self):
        self.assertEqual(self.record["record_digest"], self.proof["record_digest"])
        self.assertEqual(self.record["record_digest"], self.evaluation["record_digest"])
        self.assertEqual(run.digest({k: v for k, v in self.record.items() if k != "record_digest"}), self.record["record_digest"])
        with self.assertRaises(run.S2NGError):
            evaluate.evaluate(self.record, self.proof, self.expectations[:1])

    def test_22_no_historical_entry_or_rule_mutation(self):
        paths = [run.ROOT/p for p in run.SOURCE_PATHS if "/_s2ng_" in p]
        forbidden = {"analyze", "run_main_once", "materialize", "_materialize_events"}
        for path in paths:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            calls = {n.func.attr for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
            self.assertFalse(calls & forbidden)
        self.assertFalse(run.MAIN_GATE)

    def test_23_state_binding_exception_chain_and_ng_passthrough(self):
        valid = verify.verify_record(self.record, config=self.config)
        self.assertEqual("RECORDING_COMPLETE", valid["status"])
        self.assertEqual(self.proof, valid)
        bad = self.changed(lambda r: r["states"][next(iter(r["states"]))].update(generation=99))
        with self.assertRaises(run.S2NGError) as caught:
            verify.verify_record(bad, config=self.config)
        error = caught.exception
        self.assertEqual("STATE_BINDING_INVALID", error.code)
        self.assertIs(type(error.__cause__), run.memory.S2JWCoordinatorError)
        self.assertEqual("S2JW_PRESTATE_INVALID", error.__cause__.code)
        self.assertEqual("S2JW_PRESTATE_INVALID: composite state relation differs", str(error.__cause__))
        self.assertIs(error.__context__, error.__cause__)
        self.assertTrue(error.__suppress_context__)
        malformed = {**self.record, "record_digest": "0"*64}
        with self.assertRaises(run.S2NGError) as existing:
            verify.verify_record(malformed, config=self.config)
        self.assertEqual("DIGEST_INVALID", existing.exception.code)
        self.assertIsNone(existing.exception.__cause__)
        METRICS["state_binding_regression"] = dict(valid_state_accepted=True, code=error.code,
            cause_type=type(error.__cause__).__name__, cause_code=error.__cause__.code,
            cause_message=str(error.__cause__), explicit_chain=error.__suppress_context__,
            existing_ng_code=existing.exception.code, existing_ng_cause_unchanged=True)


if __name__ == "__main__":
    unittest.main()
