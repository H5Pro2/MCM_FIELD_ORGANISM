"""Single focused qualification; four neutral endpoint events, not the real task."""
from copy import deepcopy
from dataclasses import asdict, replace
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from tools import _memory_checkpoint as c

b, r = c.b, c.r
OUT = Path(os.environ["CHECKPOINT_QUAL_DIR"])
CODE = os.environ["CHECKPOINT_CODE_DIGEST"]


def fixture_manifest():
    events=[]
    for g,kind in enumerate((b.AV,b.A,b.V,b.AV)):
        pcm=None if kind==b.V else b.Payload(f"checkpoint-pcm-{g}",f"sources/neutral-checkpoint-{g}.pcm",b.digest(["pcm",g]),19200)
        rgb=None if kind==b.A else b.Payload(f"checkpoint-rgb-{g}",f"sources/neutral-checkpoint-{g}.rgb",b.digest(["rgb",g]),6220800)
        events.append(b.Event(f"checkpoint-event-{g+1}",g+1,kind,**b.expected_times(g+1,kind),pcm=pcm,rgb=rgb))
    return b.build_manifest("checkpoint-neutral-comparison",tuple(events),CODE)


def fixture():
    events, inputs = [], []
    config = r.nn.profile.build_config()
    for g, kind in enumerate((b.AV, b.A, b.V, b.AV)):
        raw = visual = None
        pcm = rgb = None
        if kind != b.V:
            pcm = b.Payload(f"checkpoint-pcm-{g}", f"sources/neutral-checkpoint-{g}.pcm", b.digest(["pcm", g]), 19200)
            raw = r.half.AuditoryReceptorState("auditory", r.half.RAW_GEOMETRY, 20*g,
                9600*g, 9600*g+4800,
                tuple(x.channel_id for x in r.half.spectral.logarithmic_bands(r.nn.LogSpectralConfig())),
                (0.25,)*48, r.half.AuditoryReceptorContact.ACTIVE_ENERGY)
        if kind != b.A:
            rgb = b.Payload(f"checkpoint-rgb-{g}", f"sources/neutral-checkpoint-{g}.rgb", b.digest(["rgb", g]), 6220800)
            p = config.profile.profile.visual_config
            values = (0.125,)*288 if kind == b.AV else (0.125,)*32+(0.0,)*256
            frame = r.nn.ReceptorContactFrame("visual", p.geometry_id, f"checkpoint-frame-{g}",
                "video.frame", 6*g+2, 6*g+3, p.carrier_ids, values)
            visual = r.nn.OrganismTimedReceptorFrame(frame, r.nn.CommonFieldTime(b.CLOCK,
                (6*g+2)*1000000000//30, 200000000*g+100000000))
        event = b.Event(f"checkpoint-event-{g+1}", g+1, kind,
            **b.expected_times(g+1, kind), pcm=pcm, rgb=rgb)
        events.append(event)
        inputs.append(b.bind_input(config=config, ordinal=g+1, event_id=event.event_id, kind=kind,
            raw_audio=raw, visual=visual, pcm_digest=pcm.sha256 if pcm else None,
            rgb_digest=rgb.sha256 if rgb else None))
    return b.build_manifest("checkpoint-neutral-comparison", tuple(events), CODE), inputs


def worker(mode):
    manifest, inputs = fixture()
    c.MAIN_GATE = True
    try:
        session = c.NeutralCheckpointSessionV1(manifest, CODE,
            checkpoint=OUT/"checkpoint.json" if mode == "restore" else None)
        if mode == "save":
            row = session.process(inputs[0])
            session.suspend(OUT/"checkpoint.json")
            result = dict(status="SUSPENDED_PREFIX", pid=os.getpid(), row=row,
                          closed=session._runtime.closed)
        else:
            restored = c.export(session._runtime, manifest, CODE,
                dict(completed_events=1, payload_read_bytes=0, mode="NEUTRAL_ENDPOINTS")) if mode == "restore" else None
            fields = []
            for item in inputs[1 if mode == "restore" else 0:]:
                session.process(item)
                fields.append(session._runtime.fb.state.field.snapshot().digest())
            record = session.close()
            proof = c.verify.verify_core(record, session._runtime.config, manifest)
            result = dict(status=record["status"], pid=os.getpid(), record=record, proof=proof,
                field_digests=fields, restored_stream=None if restored is None else restored["stream"],
                closed=session._runtime.closed)
    finally:
        c.MAIN_GATE = False
    result["gate"] = c.MAIN_GATE
    c.publish_new(OUT/(mode+".json"), result)


class CheckpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest, cls.inputs = fixture()
        common=c.common_values(cls.manifest)
        (OUT/"common.json").write_bytes(b.canonical(dict(values=common,sha256=b.digest(common))))
        cls.children = []
        for mode in ("baseline", "save", "restore"):
            # communicate/wait completes before the next fresh interpreter starts.
            child = subprocess.run([sys.executable, "-m", "tests.test_memory_checkpoint", mode],
                cwd=b.ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180, check=False)
            (OUT/(mode+".stdout")).write_bytes(child.stdout)
            (OUT/(mode+".stderr")).write_bytes(child.stderr)
            cls.children.append(dict(mode=mode, exit_code=child.returncode))
            if child.returncode != 0:
                raise AssertionError(f"Native {mode} failed; full child output retained")
        cls.base = c.read_checkpoint(OUT/"baseline.json")
        cls.save = c.read_checkpoint(OUT/"save.json")
        cls.restored = c.read_checkpoint(OUT/"restore.json")
        cls.checkpoint = c.read_checkpoint(OUT/"checkpoint.json")
        (OUT/"processes.json").write_bytes(b.canonical(cls.children))

    def code(self, expected, function):
        with self.assertRaises(c.CheckpointError) as caught:
            function()
        self.assertEqual(caught.exception.code, expected)

    def changed(self, **updates):
        value = deepcopy(self.checkpoint)
        value.update(updates)
        return c.seal({k:v for k,v in value.items() if k != "checkpoint_digest"})

    def test_01_native_technical_status(self):
        self.assertEqual(self.base["status"], "RECORDING_COMPLETE")
        self.assertEqual(self.restored["status"], "RECORDING_COMPLETE")
        self.assertTrue(self.base["proof"]["evaluation_allowed"])
        self.assertTrue(self.restored["proof"]["evaluation_allowed"])

    def test_02_real_process_end(self):
        self.assertEqual([x["exit_code"] for x in self.children], [0,0,0])
        self.assertNotEqual(self.save["pid"], self.restored["pid"])
        self.assertTrue(self.save["closed"])

    def test_03_full_continuation_equality(self):
        self.assertEqual(self.restored["status"], "RECORDING_COMPLETE")
        self.assertEqual(self.base["record"], self.restored["record"])
        self.assertEqual(self.base["field_digests"][1:], self.restored["field_digests"])

    def test_04_before_first_update(self):
        self.assertEqual(self.restored["restored_stream"], self.checkpoint["stream"])
        self.assertEqual(self.checkpoint["stream"]["next_ordinal"], 2)

    def test_05_native_roundtrip_and_no_mutation(self):
        before = b.canonical(self.checkpoint)
        stream, _ = c.validate(self.checkpoint, self.manifest, CODE)
        self.assertEqual(c.b.state_wire.encode(asdict(stream.memory_state)),
            self.checkpoint["prefix"]["states"][stream.memory_state_digest])
        self.assertEqual(stream.field_state.field.snapshot().canonical_payload(), self.checkpoint["field"])
        self.assertEqual(before, b.canonical(self.checkpoint))

    def test_06_corrupt_digest(self):
        value = deepcopy(self.checkpoint); value["chain"] = "0"*64
        self.code("CHECKPOINT_DIGEST", lambda:c.validate(value, self.manifest, CODE))

    def test_07_profile(self):
        self.code("CHECKPOINT_PROFILE", lambda:c.validate(self.changed(schema="foreign"), self.manifest, CODE))

    def test_08_code_and_manifest(self):
        self.code("CHECKPOINT_BINDING", lambda:c.validate(self.checkpoint, self.manifest, "0"*64))

    def test_09_generation(self):
        self.code("CHECKPOINT_GENERATION_BINDING", lambda:c.validate(self.changed(births=[None]*24), self.manifest, CODE))

    def test_10_missing_component(self):
        value = deepcopy(self.checkpoint); del value["field"]
        self.code("CHECKPOINT_FORM", lambda:c.validate(value, self.manifest, CODE))

    def test_11_incomplete_file(self):
        path=OUT/"truncated.json"; path.write_bytes(b'{"schema":')
        self.code("CHECKPOINT_READ_FAILED", lambda:c.read_checkpoint(path))

    def test_12_write_failure(self):
        path=OUT/"write-failure.json"
        original=Path.open
        def fail(path,*args,**kwargs):
            if path.name=="write-failure.json.pending":raise OSError("neutral write failure")
            return original(path,*args,**kwargs)
        with patch.object(Path,"open",fail):
            self.code("CHECKPOINT_WRITE_FAILED",lambda:c.publish_new(path,{"small":True}))

    def test_13_duplicate_publication(self):
        self.code("CHECKPOINT_EXISTS", lambda:c.publish_new(OUT/"checkpoint.json", self.checkpoint))

    def test_14_consumed_and_gate(self):
        c.MAIN_GATE=True
        try:
            self.code("CHECKPOINT_CONSUMED", lambda:c.NeutralCheckpointSessionV1(
                self.manifest,CODE,checkpoint=OUT/"checkpoint.json"))
        finally:
            c.MAIN_GATE=False
        self.code("CHECKPOINT_GATE_CLOSED", lambda:c.NeutralCheckpointSessionV1(self.manifest,CODE))

    def test_15_boundaries(self):
        self.assertEqual(c.checked_size("x"*(c.FIELD_CAP-2),c.FIELD_CAP,c.FIELD_CLASS), c.FIELD_CAP)
        self.code("CHECKPOINT_SIZE", lambda:c.checked_size("x"*(c.FIELD_CAP-1),c.FIELD_CAP,c.FIELD_CLASS))

    def test_16_closed_readonly_hypotheses(self):
        self.assertTrue(self.restored["closed"])
        self.assertFalse(self.restored["gate"])
        for row in self.restored["record"]["rows"][1:3]:
            self.assertEqual(row["step"]["memory_status"], "READ_ONLY_UNCHANGED")
            self.assertEqual(row["pre"]["memory_state_digest"],row["post"]["memory_state_digest"])

    def test_17_field_form(self):
        field=deepcopy(self.checkpoint["field"]);field["layer"]["neurons"].pop()
        self.code("CHECKPOINT_FIELD_FORM",lambda:c.validate_field_form(field))

    def test_18_materializer_accounting(self):
        account=dict(mode="CALLER_PAYLOADS",completed_events=1,
            counts=dict(payloads=2,audio=1,nj=1,visual=1,materialized_events=1),
            reads=dict(actual_read_bytes=6240000,read_operations=2))
        c.validate_accounting(account,self.manifest,1)
        account["reads"]["actual_read_bytes"]=0
        self.code("CHECKPOINT_ACCOUNTING",lambda:c.validate_accounting(account,self.manifest,1))

    def test_19_order_before_payload(self):
        c.MAIN_GATE=True
        session=c.NeutralCheckpointSessionV1(self.manifest,CODE,mode="CALLER_PAYLOADS")
        try:
            with patch.object(b.Materializer,"next",side_effect=AssertionError("no payload access")):
                self.code("CHECKPOINT_ORDER",lambda:session.next(self.manifest.events[1]))
            self.assertEqual(session._materializer.read_account["actual_read_bytes"],0)
            self.assertEqual(session._runtime.subject.snapshot().processed_event_count,0)
        finally:session._runtime.close();c.MAIN_GATE=False

    def test_20_read_before_analysis_failure(self):
        path=OUT/"neutral-read.pcm";path.write_bytes(bytes(19200))
        first=self.manifest.events[0]
        payload=replace(first.pcm,path=path.relative_to(b.ROOT).as_posix(),sha256=c.hashlib.sha256(bytes(19200)).hexdigest())
        manifest=b.build_manifest(self.manifest.run_id,(replace(first,pcm=payload),)+self.manifest.events[1:],CODE)
        c.MAIN_GATE=True
        session=c.NeutralCheckpointSessionV1(manifest,CODE,mode="CALLER_PAYLOADS")
        try:
            with patch.object(r.half.spectral.LogSpectralReceptor,"analyze",side_effect=b.S2OBError("NEUTRAL_ANALYSIS_FAILURE")):
                with self.assertRaises(b.S2OBError):session.next(manifest.events[0])
            self.assertEqual(session.failure["code"],"NEUTRAL_ANALYSIS_FAILURE")
            self.assertEqual(session.failure["accounting"]["reads"]["actual_read_bytes"],19200)
            self.assertTrue(session._terminal)
            saved=deepcopy(session.failure)
            self.code("CHECKPOINT_TERMINAL",session.close)
            self.assertEqual(saved,session.failure)
        finally:c.MAIN_GATE=False

    def test_21_partial_publication(self):
        path=OUT/"partial.json"
        with patch.object(c.os,"link",side_effect=OSError("neutral link failure")):
            self.code("CHECKPOINT_WRITE_FAILED",lambda:c.publish_new(path,{"small":True}))
        self.assertFalse(path.exists())
        self.assertTrue(Path(str(path)+".pending").exists())

    def test_22_reference_integrity(self):
        common=c.common_values(self.manifest)
        encoded=c.references(self.checkpoint,common)
        self.assertEqual(c.references(encoded,common,resolve=True),self.checkpoint)
        self.code("CHECKPOINT_REFERENCE",lambda:c.references(
            {"$checkpoint_common":"manifest","sha256":"0"*64},common,resolve=True))


if __name__ == "__main__":
    worker(sys.argv[1])
