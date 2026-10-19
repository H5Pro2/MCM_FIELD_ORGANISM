"""Focused worker qualification; historical 14 media tests are not rerun."""
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import unittest
from unittest.mock import patch

from tools import _s2oe_media_session as m
from tools import _s2oe_decoder_worker as w
from tools import _s2oe_media_verification as verify

p, b, s = m.p, m.b, m.s
OUT = Path(os.environ["MEDIA_WORKER_QUAL_OUT"])
NEUTRAL = b.ROOT/"sources/s2oe-worker-neutral"/m.QUAL_ID


def launch(command, **kwargs):
    command = [command[0], str(b.ROOT/"tests/s2oe_neutral_worker.py"), "--worker"]
    return subprocess.Popen(command, **kwargs)


def source(name):
    NEUTRAL.mkdir(parents=True, exist_ok=True)
    file = NEUTRAL/(name+".bin")
    raw = b"NEUTRAL-WORKER-FIXTURE".ljust(32, b"\0")
    with file.open("xb") as stream:
        stream.write(raw)
    return p.Source(str(file), hashlib.sha256(raw).hexdigest(), len(raw))


def binding(src):
    from reports.qualify_media_worker_once import fixture_binding
    common, inv = fixture_binding(s.file_reference("sources", OUT/"inventory.json"), src)
    return p.decode(common["manifest"]), common, inv


def session(name):
    manifest, common, inv = binding(source(name))
    p.MAIN_GATE = True
    with patch.object(w.WorkerDecoder, "_launch", staticmethod(launch)):
        value = m.start(manifest, common, inv, OUT/("native-"+name), neutral=True)
    return value, inv


class WorkerQualification(unittest.TestCase):
    def error(self, code, function):
        with self.assertRaises(w.WorkerError) as found:
            function()
        self.assertEqual(found.exception.code, code)

    def worker(self, name):
        with patch.object(w.WorkerDecoder, "_launch", staticmethod(launch)):
            value = w.WorkerDecoder(source(name))
        self.addCleanup(value.close)
        return value

    def record_resources(self, name, worker):
        value=dict(resources=worker.resources, counters=worker.counters,
            process_returncode=worker.process.poll())
        self.assertLessEqual(len(b.canonical(value)), 1024)
        s.prior.save(OUT/(name+"-resources.json"), value)

    def test_01_fixed_profile_and_private_limits(self):
        self.assertEqual(w.COMMIT_BYTES, 536870912)
        self.assertEqual(w.SLOT_BYTES, 6240000)
        self.assertEqual((w.REQUEST_SECONDS, w.STOP_SECONDS), (30.0, 5.0))
        self.assertEqual((p.SESSION_LIMITS["sources"], p.SESSION_LIMITS["shared"]), (262144,393216))
        self.assertEqual((p.SESSION_LIMITS["metadata"], p.SESSION_LIMITS["total"]), (65536,4194304))
        self.assertEqual(b.LIMITS["sources"],174080)

    def test_02_active_job_before_neutral_source_open(self):
        value = self.worker("membership")
        self.assertTrue(value.resources["job_confirmed_before_media"])
        self.assertTrue(Path(value.process.args[1]).name == "s2oe_neutral_worker.py")
        self.assertEqual(value.job.snapshot()["job_commit_limit"], w.COMMIT_BYTES)
        self.assertEqual(value.counters["container_read_bytes"], 32)
        self.assertEqual((OUT/"access-markers/membership.opened").read_text(), "AFTER_JOB_CONFIRMATION")
        value.close()
        self.record_resources("membership", value)

    def test_03_assignment_failure_prevents_source_open(self):
        src = source("assign-denied")
        with patch.object(w.WorkerDecoder, "_launch", staticmethod(launch)), patch.object(
                w.DecoderJob, "attach", side_effect=w.WorkerError("DECODER_JOB_ASSIGN_FAILED")):
            self.error("DECODER_JOB_ASSIGN_FAILED", lambda:w.WorkerDecoder(src))
        self.assertFalse((OUT/"access-markers/assign-denied.opened").exists())

    def test_04_child_rejects_missing_job_before_media(self):
        src = source("missing-job")
        data = w.encode(dict(op="init", sequence=1, version=w.VERSION,
            job="Local\\MCMDecoderJob-does-not-exist", source={}, slot="unused"))
        proc = subprocess.run([sys.executable,str(b.ROOT/"tests/s2oe_neutral_worker.py"),"--worker"],
            input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW)
        self.assertEqual(json.loads(proc.stdout)["error"], "DECODER_JOB_OPEN_FAILED")
        self.assertFalse((OUT/"access-markers/missing-job.opened").exists())

    def test_05_os_denies_memory_overload(self):
        value = self.worker("overload")
        self.error("DECODER_MEMORY_LIMIT", lambda:value.select(1,0))
        self.assertTrue(value.resources["memory_limit_notification"])
        value.close()
        self.assertIsNotNone(value.process.poll())
        self.record_resources("overload", value)

    def test_06_actual_thirty_second_timeout(self):
        value = self.worker("timeout")
        start = time.monotonic()
        self.error("DECODER_TIMEOUT", lambda:value.select(1,0))
        self.assertGreaterEqual(time.monotonic()-start, 30)
        value.close()
        self.assertIsNotNone(value.process.poll())
        self.record_resources("timeout", value)

    def test_07_single_slot_and_immutable_transfer(self):
        value = self.worker("slot")
        pcm, rgb, pts, nxt = value.select(1,0)
        self.assertEqual((pcm.nbytes,rgb.nbytes,pts,nxt),(19200,6220800,1001,2002))
        self.assertFalse(pcm.flags.writeable or rgb.flags.writeable)
        before = (pcm.tobytes(),rgb.tobytes())
        value.release()
        value.select(1,1)
        self.assertEqual((pcm.tobytes(),rgb.tobytes()),before)
        value._call_lock.acquire()
        try:
            self.error("DECODER_BUSY", lambda:value.select(1,2))
        finally:
            value._call_lock.release()
        self.assertEqual(value._responses.maxsize,1)
        value.close()
        value.close()
        self.record_resources("slot",value)

    def test_08_native_conversion_inside_limited_worker(self):
        value = self.worker("convert")
        pcm,rgb,pts,nxt = value.select(1,0)
        self.assertEqual((pts,nxt),(1001,2002))
        self.assertEqual(pcm.tobytes(),bytes(19200))
        self.assertEqual(rgb.shape,(1080,1920,3))
        self.assertLessEqual(value.resources["peak_job_commit"],w.COMMIT_BYTES)
        value.close()
        self.record_resources("convert",value)

    def test_09_native_full_session_through_worker(self):
        value, inv = session("full")
        self.addCleanup(value.stop)
        previous = value._runtime.subject.snapshot().memory_state_digest
        for event in value._manifest.events:
            result = json.loads(value.next())
            current = value._runtime.subject.snapshot().memory_state_digest
            if event.kind != b.AV:
                self.assertEqual(current,previous)
                self.assertEqual(result["memory_status"],"READ_ONLY_UNCHANGED")
            previous = current
        record = json.loads(value.stop())
        self.assertEqual(record["status"],"RECORDING_COMPLETE")
        proof = verify.verify_once(OUT/"native-full",inv)
        self.assertTrue(proof["evaluation_allowed"])
        self.assertEqual(proof["native"]["field_contacts"],7392)
        self.assertEqual(proof["native"]["scan_receipts"],8)
        before = sorted(x.name for x in (OUT/"native-full").iterdir())
        self.assertEqual(value.stop(),b.canonical(record))
        self.assertEqual(before,sorted(x.name for x in (OUT/"native-full").iterdir()))

    def test_10_stop_blocked_worker_preserves_formation(self):
        value,inv = session("blocked")
        self.addCleanup(value.stop)
        value.next()
        previous = value._runtime.subject.snapshot()
        errors=[]
        def next_event():
            try:
                value.next()
            except Exception as exc:
                errors.append(exc)
        thread=threading.Thread(target=next_event)
        thread.start()
        limit=time.monotonic()+10
        while not value._materializer.decoder._request_lock.locked() and time.monotonic()<limit:
            time.sleep(0.01)
        self.assertTrue(value._materializer.decoder._request_lock.locked())
        record=json.loads(value.stop())
        thread.join(5)
        self.assertFalse(thread.is_alive())
        self.assertEqual(record["status"],"NOT_EVALUABLE")
        self.assertEqual(record["failure"]["code"],"DECODER_CANCELLED")
        self.assertEqual(len(errors),1)
        self.assertEqual(record["failure"]["completed_events"],1)
        self.assertEqual(record["failure"]["final"]["field_state_digest"],previous.field_state_digest)
        self.assertEqual(record["failure"]["final"]["memory_state_digest"],previous.memory_state_digest)
        common=s.load_common(OUT/"native-blocked")
        rec,bind=s.unpack(s.read_json(OUT/"native-blocked/record.json"),s.read_json(OUT/"native-blocked/session.json"),common)
        self.assertFalse(verify.verify_record(rec,bind,common,inv)["evaluation_allowed"])
        self.assertEqual(value.stop(),b.canonical(record))

    def test_11_unexpected_worker_exit_preserves_primary(self):
        value,inv=session("exit")
        self.addCleanup(value.stop)
        value.next()
        previous=value._runtime.subject.snapshot()
        self.error("DECODER_WORKER_EXIT",value.next)
        record=json.loads(value.stop())
        self.assertEqual(record["status"],"NOT_EVALUABLE")
        self.assertEqual(record["failure"]["code"],"DECODER_WORKER_EXIT")
        self.assertEqual(record["failure"]["final"]["field_state_digest"],previous.field_state_digest)
        self.assertFalse(record["media"]["resources"]["read_counters_complete"])
        common=s.load_common(OUT/"native-exit")
        rec,bind=s.unpack(s.read_json(OUT/"native-exit/record.json"),s.read_json(OUT/"native-exit/session.json"),common)
        self.assertFalse(verify.verify_record(rec,bind,common,inv)["evaluation_allowed"])

    def test_12_message_limits_and_profile_tampering(self):
        self.error("DECODER_MESSAGE_LIMIT",lambda:w.encode(dict(x="x"*4096)))
        from io import BytesIO
        self.error("DECODER_MESSAGE_INVALID",lambda:w.read_message(BytesIO(b"x"*4098)))
        manifest,common,inv=binding(source("profile"))
        common["decoder_resource_profile"]["job_commit_bytes"]+=1
        common=b.sealed({k:v for k,v in common.items() if k!="common_digest"},"common_digest")
        with self.assertRaises(p.MediaError) as exc:
            m.check_common(manifest,common,inv)
        self.assertEqual(exc.exception.code,"COMMON_BINDING_INVALID")

    def test_13_full_envelopes_and_budget_boundaries(self):
        from reports.qualify_media_worker_once import preflight, fixture_binding
        common,_=fixture_binding(s.file_reference("sources",OUT/"inventory.json"))
        upper=preflight(common)
        self.assertEqual(len(upper["positions"]),25)
        self.assertEqual(upper["violations"],[])
        from tools._s2oc_shared_verification import synthetic_forms
        pair=synthetic_forms(common,0)[1]
        for key in ("sources","shared","metadata"):
            base=p.ledger(*pair,common,attachments=())["totals"][key]
            kind="sources" if key=="shared" else key
            for delta in (0,1):
                row=p.ledger(*pair,common,attachments=((kind,"@boundary",p.SESSION_LIMITS[key]-base+delta),))
                self.assertEqual(key.upper()+"_LIMIT" in row["violations"],delta==1)
                if key=="shared":
                    # Aggregate arithmetic probe, not a feasible native ledger:
                    # the source limit is already exceeded at this shared total.
                    self.assertIn("SOURCES_LIMIT",row["violations"])

    def test_14_hash_rejection_before_neutral_analysis(self):
        src=replace(source("hash-denied"),sha256="0"*64)
        with patch.object(w.WorkerDecoder,"_launch",staticmethod(launch)):
            self.error("MEDIA_HASH_INVALID",lambda:w.WorkerDecoder(src))
        self.assertFalse((OUT/"access-markers/hash-denied.opened").exists())


if __name__=="__main__":
    unittest.main()
