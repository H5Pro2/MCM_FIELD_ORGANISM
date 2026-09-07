"""Bound neutral composition only; no NH inputs or complete transfer story."""

from copy import deepcopy
from dataclasses import asdict, FrozenInstanceError, replace
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from mcm_field_organism.broadband_hearing_path import AuditoryReceptorState, AuditoryReceptorContact
from mcm_field_organism import _tspm1_private as core
from tools import _s2nn_private_half_runtime_binding as run

ng, half = run.ng, run.half
CLOCK = "s2nn-neutral-field-clock"
METRICS = dict(runtime_events=0, formation_attempts=0, field_contacts=0,
               valid_projection_calls=0, receptor_analyses=0, nh_calls=0)


def archive(name, value):
    data = ng.canonical(value)
    if len(data) > ng.MAX_BYTES:
        raise ValueError("NEUTRAL_ARTIFACT_LIMIT")
    with (Path(os.environ["S2NN_QUAL_DIR"])/name).open("xb") as handle:
        handle.write(data)


def raw(n):
    return AuditoryReceptorState("auditory", half.RAW_GEOMETRY, n*10, n*4800, (n+1)*4800,
        tuple(b.channel_id for b in half.spectral.logarithmic_bands(run.LogSpectralConfig())),
        (0.5,)*48, AuditoryReceptorContact.ACTIVE_ENERGY)


def visual(config, n, time, partial=False):
    p = config.profile.profile.visual_config
    values = (0.25,)*32+(0.0,)*256 if partial else (0.25,)*288
    return run.OrganismTimedReceptorFrame(run.ReceptorContactFrame("visual", p.geometry_id,
        f"s2nn-neutral-visual-{n}", "video.frame", n*3+2, n*3+3, p.carrier_ids, values), time)


def fixture(config):
    values = []
    for n, kind in enumerate(("COMPLETE_AV_PERCEPTION", "PARTIAL_AUDITORY_CUE",
                              "COMPLETE_AV_PERCEPTION", "PARTIAL_VISUAL_CUE")):
        time = run.CommonFieldTime(CLOCK, n*100_000_000+90_000_000, (n+1)*100_000_000)
        has_audio, has_visual = n != 3, n != 1
        values.append(run.bind_event(config=config, event_id=f"s2nn-neutral-event-{n+1:02d}",
            ordinal=n+1, event_type=kind, field_start_tick=n*100_000_000, common_time=time,
            raw_audio=raw(n) if has_audio else None,
            pcm_digest=half.digest(dict(neutral_audio=n)) if has_audio else None,
            visual=visual(config,n,time,n==3) if has_visual else None,
            rgb_digest=half.digest(dict(neutral_visual=n)) if has_visual else None))
    return tuple(values)


def execute(c):
    for _ in c.events:
        c.process_next()
        if c.failed:
            break
    record = c.finish()
    METRICS["runtime_events"] += len(record["pairs"])*2
    METRICS["formation_attempts"] += sum(e.event_type == "COMPLETE_AV_PERCEPTION"
        for e in c.events[:len(record["pairs"])] )*2
    METRICS["field_contacts"] += sum(len(t.frame.values) for e in c.events[:len(record["pairs"])]
                                    for t in e.field_payload.timed_frames)*2
    return record


def tearDownModule():
    archive("metrics.json", METRICS)


class HalfRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = run.profile.build_config()
        original = half.project_auditory_half_v1
        with patch.object(half, "project_auditory_half_v1", wraps=original) as counted:
            cls.inputs = fixture(cls.config)
            METRICS["valid_projection_calls"] = counted.call_count
        cls.c = run.build_comparison(inputs=cls.inputs, config=cls.config, comparison_id="s2nn-neutral-main",
                                    field_clock_id=CLOCK)
        cls.ids = [tuple(id(x) for x in (s, s._processor, s._state, b[0].state.field,
                                        b[1].state, b[1].state.b4_state, b[1].state.tspm_state))
                   for s, b in zip(cls.c.subjects, cls.c.branches, strict=True)]
        cls.record = execute(cls.c)
        archive("neutral-record.json", cls.record)
        cls.proof = run.verify_comparison(cls.record, inputs=cls.inputs, config=cls.config)
        archive("neutral-proof.json", cls.proof)

    def test_01_profile_and_rule_bindings(self):
        self.assertFalse(run.MAIN_GATE)
        self.assertFalse(ng.MAIN_GATE)
        c = self.config
        self.assertEqual((0.1,0.01,0.2,0.01), (c.tspm_config.fast_config.auditory_match_threshold,
            c.profile.profile.auditory_config.match_threshold, c.tspm_config.fast_config.visual_match_threshold,
            c.profile.profile.visual_config.match_threshold))
        self.assertEqual(core.HALF_RANK, c.tspm_config.fast_config.rank_binding)
        self.assertEqual(ng.audio.RULES, tuple(b.rule for b in self.c.bindings))
        for b in self.c.bindings:
            self.assertEqual(b.config_digest, c.config_digest)
            with self.assertRaises(FrozenInstanceError):
                b.rule = "other"
        with self.assertRaises(run.S2NNError):
            run.build_comparison(inputs=self.inputs, config=c, comparison_id="s2nn-blocked-main", field_clock_id=CLOCK, mode="MAIN")

    def test_02_single_projection_and_shared_values(self):
        self.assertEqual(3, METRICS["valid_projection_calls"])
        for value in self.inputs:
            event = value.event
            for t in event.field_payload.timed_frames:
                if t.frame.modality_id == "auditory":
                    self.assertEqual((0.25,)*48, t.frame.values)
                    self.assertEqual(value.auditory_projection.values, t.frame.values)
                    self.assertNotEqual((0.125,)*48, t.frame.values)
            if event.event_type == "COMPLETE_AV_PERCEPTION":
                bound = ng.memory.bind_s2jv_coordinator_input(config=self.config, source=event.operation_payload)
                self.assertEqual((0.25,)*48, bound.auditory_values)
                self.assertEqual((0.25,)*288, bound.visual_values)
        p = self.inputs[0].auditory_projection
        with self.assertRaises(half.S2NJProjectionError):
            run.bind_event(config=self.config, event_id="s2nn-double-half", ordinal=1,
                event_type="PARTIAL_AUDITORY_CUE", field_start_tick=0,
                common_time=run.CommonFieldTime(CLOCK,0,100_000_000), raw_audio=p, pcm_digest="1"*64)

    def test_03_mixed_profile_and_state_rejected(self):
        old = ng.ne.make_config()
        with self.assertRaises(run.S2NNError):
            run.build_comparison(inputs=self.inputs, config=old, comparison_id="s2nn-old-mixed", field_clock_id=CLOCK)
        with self.assertRaises(ng.memory.S2JWCoordinatorError):
            ng.memory._validate_state(self.config, ng.memory.initial_s2jv_composite_state(old))
        with self.assertRaises(ng.memory.S2JWCoordinatorError):
            ng.memory._validate_state(old, self.c.branches[0][1].state)

    def test_04_instances_owners_and_lifecycle(self):
        self.assertTrue(all(a != b for a,b in zip(*self.ids, strict=True)))
        self.c._isolation()
        for s in self.c.subjects:
            self.assertEqual("CLOSED", s.snapshot().status)
            self.assertEqual(4, s.snapshot().processed_event_count)
            with self.assertRaises(ng.runtime.S2MRRuntimeError):
                s.process_once(self.inputs[-1].event)
            with self.assertRaises(ng.runtime.S2MRRuntimeError):
                s.close()

    def test_05_formation_continues_across_read_only_cue(self):
        for i in range(2):
            first, cue, second, final = [p["arms"][i] for p in self.record["pairs"]]
            self.assertEqual(first["memory"], cue["memory"])
            self.assertEqual(cue["memory"], second["pre"]["memory_state_digest"])
            state = self.c.branches[i][1].state
            self.assertEqual(2, state.generation)
            self.assertEqual(2, sum(e.occupied for e in state.b4_state.entries))
            self.assertEqual(2, state.tspm_state.fast_state.slots[0].support_count)
            for modality in ("auditory", "visual"):
                slots = getattr(state.tspm_state, modality+"_ppb1_state").slots
                self.assertEqual(1, slots[0].support_count)
                self.assertEqual((0.25,)*(48 if modality == "auditory" else 288), slots[0].prototype_values)
            self.assertEqual(second["memory"], final["memory"])

    def test_06_field_contacts_new_profile_only(self):
        self.assertEqual("RECORDING_COMPLETE", self.proof["status"])
        self.assertEqual(2016, self.proof["field_contacts"])
        for n,p in enumerate(self.record["pairs"],1):
            a,b = p["arms"]
            self.assertEqual(a["field"], b["field"])
            self.assertEqual(a["memory"], b["memory"])
            self.assertEqual(n, a["field"]["step_count"])
            self.assertEqual("FIELD_CONTACT_RECORDED", a["step"]["perception_status"])
            self.assertFalse(a["step"]["error_codes"])
        self.assertNotEqual(self.record["initial"][0]["field"]["state_digest"], self.record["final"][0]["field_state_digest"])

    def test_07_both_cues_read_only_and_baselines(self):
        self.assertTrue(self.proof["baseline_equal"])
        self.assertEqual(8,len(self.record["scans"]))
        for n in (1,3):
            for a in self.record["pairs"][n]["arms"]:
                self.assertEqual(a["pre"]["memory_state_digest"],a["post"]["memory_state_digest"])
                self.assertEqual("READ_ONLY_UNCHANGED",a["step"]["memory_status"])
        self.assertEqual("CONTEXT_CANDIDATE_AVAILABLE",self.record["pairs"][1]["arms"][0]["step"]["context_status"])
        self.assertEqual("ABSTAIN_INTERNAL_AMBIGUITY",self.record["pairs"][3]["arms"][0]["step"]["context_status"])

    def test_08_visual_and_slow_unchanged_between_rule_arms(self):
        a,b = [self.c.scans[i][(4,"PRIMARY")] for i in range(2)]
        self.assertEqual(a,b)
        a,b = [self.c.scans[i][(2,"PRIMARY")].evidence for i in range(2)]
        self.assertEqual(a.bank_scans[2],b.bank_scans[2])
        self.assertEqual(0.01,a.bank_scans[2].records[0].match_threshold)

    def test_09_source_time_and_projection_tampering(self):
        value = self.inputs[0]
        for bad in (replace(value, pcm_digest="0"*64),replace(value, config_digest="0"*64)):
            with self.assertRaises(run.S2NNError):
                run.validate_input(bad,self.config)
        p = value.auditory_projection
        with self.assertRaises(half.S2NJProjectionError):
            half.validate_projection(replace(p,values=(0.125,)*48))
        with self.assertRaises(half.S2NJProjectionError):
            run.bind_event(config=self.config,event_id="s2nn-bad-audio-time",ordinal=1,
                event_type="PARTIAL_AUDITORY_CUE",field_start_tick=0,common_time=run.CommonFieldTime(CLOCK,0,100_000_000),
                raw_audio=replace(raw(0),window_end_sample=4801),pcm_digest="1"*64)

    def test_10_serialization_and_full_scans(self):
        self.assertLessEqual(len(ng.canonical(self.record)),ng.MAX_BYTES)
        for v in self.inputs:
            self.assertLessEqual(len(ng.canonical(asdict(v))),run.MAX_BOUND_INPUT_BYTES)
        for row in self.record["scans"]:
            v = row["value"].get("evidence",row["value"])
            self.assertEqual((9,3,8) if row["ordinal"] == 2 else (9,3,4),tuple(len(b["records"]) for b in v["bank_scans"]))
            self.assertLessEqual(v["resource_ledger"]["total_value_comparison_count"],528 if row["ordinal"] == 2 else 800)
            self.assertLess(len(ng.canonical(row["value"])),32768)

    def test_11_scan_failure_retains_field(self):
        values = self.inputs[:2]
        c = run.build_comparison(inputs=values,config=self.config,comparison_id="s2nn-scan-error",field_clock_id=CLOCK)
        def fail(state,event):
            raise ValueError("neutral injected scan failure")
        for s in c.subjects:
            s._processor._auditory_scan = fail
            s._processor._auditory_baseline = fail
        r = execute(c)
        archive("scan-failure.json",r)
        proof = run.verify_comparison(r,inputs=values,config=self.config)
        archive("scan-failure-proof.json",proof)
        self.assertEqual("NOT_EVALUABLE",proof["status"])
        for a in r["pairs"][-1]["arms"]:
            self.assertEqual("SCAN_FAILED",a["step"]["context_status"])
            self.assertEqual("FIELD_CONTACT_RECORDED",a["step"]["perception_status"])
            self.assertEqual(a["pre"]["memory_state_digest"],a["post"]["memory_state_digest"])

    def test_12_second_ppb_failure_is_atomic_field_survives(self):
        values = self.inputs[:3]
        c = run.build_comparison(inputs=values,config=self.config,comparison_id="s2nn-atomic-error",field_clock_id=CLOCK)
        real = core.advance_ppb1_bank
        calls = []
        def fail_visual(config,state,frame):
            calls.append(frame.modality_id)
            if frame.modality_id == "visual":
                raise RuntimeError("neutral second bank failure")
            return real(config,state,frame)
        with patch.object(core,"advance_ppb1_bank",side_effect=fail_visual):
            r = execute(c)
        archive("atomic-failure.json",r)
        proof = run.verify_comparison(r,inputs=values,config=self.config)
        archive("atomic-failure-proof.json",proof)
        self.assertEqual(["auditory","visual"]*2,calls)
        self.assertEqual("NOT_EVALUABLE",proof["status"])
        for a in r["pairs"][-1]["arms"]:
            self.assertEqual("FORMATION_FAILED",a["step"]["memory_status"])
            self.assertEqual("FIELD_CONTACT_RECORDED",a["step"]["perception_status"])
            self.assertEqual(a["pre"]["memory_state_digest"],a["post"]["memory_state_digest"])
        for _,b in c.branches:
            self.assertEqual(1,b.state.generation)
            self.assertFalse(any(s.occupied for s in b.state.tspm_state.auditory_ppb1_state.slots))

    def test_13_missing_evidence_and_old_config_rejected(self):
        bad = deepcopy(self.record)
        bad["scans"].pop()
        bad["record_digest"] = ng.digest({k:v for k,v in bad.items() if k != "record_digest"})
        with self.assertRaises(ng.S2NGError):
            run.verify_comparison(bad,inputs=self.inputs,config=self.config)
        with self.assertRaises(run.S2NNError):
            run.verify_comparison(self.record,inputs=self.inputs,config=ng.ne.make_config())

    def test_14_inputs_immutable_no_reprojection(self):
        with patch.object(half,"project_auditory_half_v1",side_effect=AssertionError("reprojection forbidden")):
            for value in self.inputs:
                self.assertIs(value,run.validate_input(value,self.config))
                with self.assertRaises(FrozenInstanceError):
                    value.config_digest = "0"*64
        self.assertEqual(half.PROFILE_DIGEST, self.inputs[0].auditory_projection.profile_digest)
