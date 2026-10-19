"""One new neutral qualification; no historical tests, caller media or replay."""
from copy import deepcopy
from dataclasses import asdict
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import _s2oc_bound_session as entry
from tools import _s2oc_shared_verification as verifier
from reports.s2oc import run_bound_session_once as caller

s, b, budget = entry.shared, entry.b, entry.budget
OUT = Path(os.environ["OC_SHARED_OUT"])
INV = s.read_json(OUT/"inventory.json")
MET = dict(sessions=0, audio=0, nj=0, visual=0, core_verifications=0, failure_verifications=0)


def manifest(name="neutral-shared", kinds=(b.AV,b.A), files=None):
    events=[]
    for n,kind in enumerate(kinds,1):
        payloads={}
        for key,size in (("pcm",19200),("rgb",6220800)):
            needed=kind != (b.V if key=="pcm" else b.A)
            path,h=(files[key] if files else (f"reports/s2oc/never-read-{key}.bin","0"*64))
            payloads[key]=b.Payload(f"{name}-{key}-{n}",path,h,size) if needed else None
        events.append(b.Event(f"{name}-event-{n}",n,kind,**b.expected_times(n,kind),**payloads))
    return b.build_manifest(name,tuple(events),b.digest(INV["ob"]))


def common(m=None):
    return s.build_common(m or manifest(),INV,(s.file_reference("sources",OUT/"inventory.json"),))


def reseal(value,key):
    return b.sealed({k:v for k,v in value.items() if k!=key},key)


class SharedClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix="oc-shared-neutral-",dir=b.ROOT/"reports/s2oc")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root=Path(cls.temp.name)
        cls.files={}
        for key,raw in (("pcm",b"\0"*19200),("rgb",bytes((36,84,132))*(1920*1080))):
            p=cls.root/(key+".bin");p.write_bytes(raw)
            cls.files[key]=(p.relative_to(b.ROOT).as_posix(),s.sha(raw))
        original=Path.open
        def guarded(path,mode="r",*args,**kw):
            if "r" in mode and path.suffix in (".bin",".pcm",".rgb") and not path.resolve().is_relative_to(cls.root):
                raise AssertionError("NON_NEUTRAL_PAYLOAD_FORBIDDEN")
            return original(path,mode,*args,**kw)
        pt=patch.object(Path,"open",guarded);pt.start();cls.addClassCleanup(pt.stop)
        for obj,name,key in ((b.r.half.spectral.LogSpectralReceptor,"analyze","audio"),
                             (b.LocalChannelGridReceptor,"analyze","visual"),
                             (b.r.half,"project_auditory_half_v1","nj")):
            call=getattr(obj,name)
            def counted(*args,_call=call,_key=key,**kw):
                MET[_key]+=1
                return _call(*args,**kw)
            pt=patch.object(obj,name,counted);pt.start();cls.addClassCleanup(pt.stop)

    @classmethod
    def tearDownClass(cls):
        entry.MAIN_GATE=False
        s.prior.save(OUT/"metrics.json",dict(MET,gates=False))

    def test_01_all_22_positions_and_both_forms(self):
        c=common(manifest(kinds=tuple(b.V if n in (2,15,21) else b.AV for n in range(1,22))))
        for n in range(22):
            with self.subTest(completed=n):
                forms=verifier.synthetic_forms(c,n)
                result=entry.alternatives(*forms,c,phase="EVIDENCE",ordinal=min(n+1,21),completed=n)
                for name,pair in zip(("success","failure"),forms):
                    expected=s.ledger(*pair,c,attachments=entry.ATTACHMENTS)
                    self.assertEqual(result[name],expected)
                    self.assertFalse(expected["violations"])
                self.assertEqual(result["failure"]["contributions"]["prefix_steps"],n*16384)

    def test_02_lossless_native_binary64(self):
        c=common();record,session=verifier.synthetic_forms(c,1)[0]
        values=[-0.0,float.fromhex("0x0.0000000000001p-1022"),float.fromhex("0x1.fffffffffffffp+1023")]
        record["execution"]["states"]={"0"*64:dict(values=values,origin="unchanged",time=123)}
        record["execution"]=reseal(record["execution"],"record_digest")
        record=reseal(record,"record_digest");session["record_digest"]=record["record_digest"]
        session=reseal(session,"session_digest")
        wr,ws=s.pack(record,session,c)
        before=b.canonical((record,session,c))
        r,q=s.unpack(json.loads(b.canonical(wr)),json.loads(b.canonical(ws)),json.loads(b.canonical(c)))
        self.assertEqual(before,b.canonical((record,session,c)))
        self.assertEqual(b.canonical((r,q)),b.canonical((record,session)))
        self.assertEqual([x.hex() for x in r["execution"]["states"]["0"*64]["values"]],[x.hex() for x in values])

    def test_03_missing_common(self):
        c=common();wr,ws=s.pack(*verifier.synthetic_forms(c,0)[0],c)
        with self.assertRaises(budget.BudgetError) as ctx:s.unpack(wr,ws,None)
        self.assertEqual(ctx.exception.code,"COMMON_MISSING")

    def test_04_changed_common_pin(self):
        c=common();wr,ws=s.pack(*verifier.synthetic_forms(c,0)[0],c)
        c["read_plan"]["planned_read_bytes"]+=1;c=reseal(c,"common_digest")
        with self.assertRaises(budget.BudgetError) as ctx:s.unpack(wr,ws,c)
        self.assertEqual(ctx.exception.code,"COMMON_REFERENCE_INVALID")

    def test_05_conflicting_reference(self):
        c=common();wr,ws=s.pack(*verifier.synthetic_forms(c,0)[0],c)
        wr["record"]["manifest"]={"$oc_common":"runtime_config"}
        with self.assertRaises(budget.BudgetError) as ctx:s.unpack(wr,ws,c)
        self.assertEqual(ctx.exception.code,"ADMIN_REFERENCE_CONFLICT")

    def test_06_missing_external_content(self):
        c=common();c["references"].append(["metadata","reports/s2oc/missing-content-for-test",1,"0"*64]);c=reseal(c,"common_digest")
        with self.assertRaises(budget.BudgetError) as ctx:s.validate_common(c,INV)
        self.assertEqual(ctx.exception.code,"REFERENCE_MISSING")

    def test_07_changed_external_content(self):
        c=common();c["references"][0][3]="0"*64;c=reseal(c,"common_digest")
        with self.assertRaises(budget.BudgetError) as ctx:s.validate_common(c,INV)
        self.assertEqual(ctx.exception.code,"REFERENCE_CHANGED")

    def test_08_duplicate_reference(self):
        c=common();c["references"].append(c["references"][0][:]);c=reseal(c,"common_digest")
        with self.assertRaises(budget.BudgetError) as ctx:s.validate_common(c,INV)
        self.assertEqual(ctx.exception.code,"REFERENCE_INVALID")

    def test_09_profile_conflict(self):
        c=common();c["rule_binding"]["rule"]="HISTORICAL_SUM_L1_24";c=reseal(c,"common_digest")
        with self.assertRaises(budget.BudgetError) as ctx:s.validate_common(c,INV)
        self.assertEqual(ctx.exception.code,"COMMON_CONTENT_INVALID")

    def padded(self,extra):
        c=common();r,q=verifier.synthetic_forms(c,0)[1]
        r["budget_test_padding"]=""
        current=s.ledger(r,q,c)["totals"]["metadata"]
        r["budget_test_padding"]="x"*(65536-current+extra)
        return c,r,q

    def test_10_inclusive_budget_limit(self):
        c,r,q=self.padded(0)
        measured=s.ledger(r,q,c)
        self.assertEqual(measured["totals"]["metadata"],65536)
        self.assertFalse(measured["violations"])

    def test_11_one_byte_over_limit(self):
        c,r,q=self.padded(1)
        measured=s.ledger(r,q,c)
        self.assertEqual(measured["totals"]["metadata"],65537)
        self.assertEqual(measured["violations"],["METADATA_LIMIT"])

    def test_12_error_terms_no_recursion(self):
        c,r,q=self.padded(1)
        with self.assertRaises(budget.BudgetError) as ctx:
            entry.alternatives((r,q),(r,q),c,phase="EVIDENCE",ordinal=12,completed=11)
        d=ctx.exception.balance
        self.assertEqual((d["phase"],d["ordinal"],d["completed_events"]),("EVIDENCE",12,11))
        self.assertLessEqual(len(b.canonical(d)),4096)
        for row in d["alternatives"].values():
            self.assertGreater(row["totals"]["metadata"],row["limits"]["metadata"])
            self.assertIn("common",row["parts"])
            self.assertNotIn("balance",row)

    def test_13_physical_common_once(self):
        c=common();r,q=verifier.synthetic_forms(c,1)[0]
        wr,ws=s.pack(r,q,c);measured=s.ledger(r,q,c)
        expected=sum(len(b.canonical(x)) for x in (wr,ws,c))+sum(z[2] for z in c["references"])+512+262144
        self.assertEqual(measured["totals"]["total"],expected)

    def test_14_global_limit_independent(self):
        c=common();r,q=verifier.synthetic_forms(c,21 if len(c["manifest"]["events"])==21 else 2)[0]
        # Independent ledger summation probe, not a claimed reachable full history.
        big=(("sources","sum-only",4194304),)
        result=s.ledger(r,q,c,attachments=big)
        self.assertIn("TOTAL_LIMIT",result["violations"])
        self.assertIn("SOURCES_LIMIT",result["violations"])

    def test_15_neutral_success_and_native_verifier(self):
        m=manifest("shared-success",kinds=(b.A,b.AV),files=self.files);c=common(m)
        cp=OUT/"caller-common.json";s.prior.save(cp,c)
        entry.MAIN_GATE=True
        dispatch=caller.run(cp,s.sha(b.canonical(c)),OUT/"inventory.json",OUT/"success",neutral=True)
        MET["sessions"]+=1
        self.assertEqual(dispatch["status"],"RECORDING_COMPLETE",dispatch)
        record,_=s.unpack(s.read_json(OUT/"success/record.json"),s.read_json(OUT/"success/session.json"),c)
        self.assertEqual(record["status"],"RECORDING_COMPLETE",record["failure"])
        self.assertIsNotNone(record["execution"])
        rows=record["execution"]["rows"]
        self.assertEqual(rows[0]["pre"]["memory_state_digest"],rows[0]["post"]["memory_state_digest"])
        self.assertIsNone(rows[0]["step"]["hypothesis"])
        self.assertEqual(dispatch["status"],"RECORDING_COMPLETE")
        self.assertTrue(s.read_json(OUT/"success/verification.json")["evaluation_allowed"])
        MET["core_verifications"]+=1
        self.assertFalse(s.read_json(OUT/"success/final-balance.json")["violations"])
        self.assertFalse(entry.MAIN_GATE)

    def test_16_primary_error_after_formation(self):
        m=manifest("shared-failure",files=self.files);c=common(m)
        entry.MAIN_GATE=True;session=entry.open_session(c,INV,OUT/"failure",neutral=True);MET["sessions"]+=1
        self.addCleanup(session.close)
        initial=asdict(session._runtime.subject.snapshot())
        session.process(m.events[0]);before=asdict(session._runtime.subject.snapshot())
        self.assertEqual(before["processed_event_count"],1)
        self.assertNotEqual(initial["field_state_digest"],before["field_state_digest"])
        pairs=session._forms();rows={name:s.ledger(*pair,c) for name,pair in zip(("success","failure"),pairs)}
        rows["success"]["totals"]["metadata"]=65537;rows["success"]["violations"]=["METADATA_LIMIT"]
        error=budget.BudgetError("COMBINED_RUNTIME_METADATA_LIMIT",budget.diagnostic(rows,"EVIDENCE",2,1))
        with patch.object(session,"_check_progress_budget",side_effect=error):
            with self.assertRaises(budget.BudgetError):session.process(m.events[1])
        raw=session.close();self.assertEqual(raw,session.close());record=json.loads(raw)
        self.assertEqual(record["status"],"NOT_EVALUABLE")
        self.assertEqual(record["failure"]["code"],error.code)
        self.assertEqual(record["failure"]["phase"],"EVIDENCE")
        self.assertEqual(record["failure"]["balance"],error.balance)
        for k in ("field_state_digest","memory_state_digest"):
            self.assertEqual(before[k],record["failure"]["final"][k])
        proof,measured=verifier.verify_once(OUT/"failure",INV,qualified=False);MET["failure_verifications"]+=1
        self.assertFalse(proof["evaluation_allowed"])
        self.assertGreater(measured["contributions"]["prefix_steps"],0)

    def test_17_read_bytes_before_hash_error(self):
        p=b.Payload("neutral-bad-hash",self.files["pcm"][0],"0"*64,19200)
        counts=dict(actual_read_bytes=0,read_operations=0)
        with self.assertRaises(b.S2OBError) as ctx:b.read_payload(p,read_account=counts)
        self.assertEqual(ctx.exception.code,"PAYLOAD_HASH_INVALID")
        self.assertEqual(counts,dict(actual_read_bytes=19200,read_operations=1))

    def test_18_read_bytes_survive_analysis_error(self):
        m=manifest("neutral-analysis",kinds=(b.A,),files=self.files)
        materializer=b.Materializer(m,track_reads=True)
        with patch.object(type(materializer.audio),"analyze",side_effect=b.S2OBError("NEUTRAL_ANALYSIS_FAILURE")):
            with self.assertRaises(b.S2OBError) as ctx:materializer.next(m.events[0])
        self.assertEqual(ctx.exception.code,"NEUTRAL_ANALYSIS_FAILURE")
        self.assertEqual(materializer.read_account,dict(actual_read_bytes=19200,read_operations=1))
        self.assertEqual(materializer.counts["audio"],0)

    def test_19_planned_stock_and_actual_separate(self):
        m=manifest(files=self.files);plan=budget.read_plan(m)
        self.assertEqual(plan,dict(input_stock_bytes=6240000,planned_read_bytes=6259200))

    def test_20_renewed_code_required(self):
        c=common();bad=deepcopy(INV);bad["ob"]["files"][b.OWN[0]][0]="0"*64
        with self.assertRaises(budget.BudgetError) as ctx:s.validate_common(c,bad)
        self.assertEqual(ctx.exception.code,"COMMON_BINDING_INVALID")

    def test_21_gate_before_runtime(self):
        entry.MAIN_GATE=False
        with patch.object(b,"CallerRuntime",side_effect=AssertionError("RUNTIME_FORBIDDEN")):
            with self.assertRaises(budget.BudgetError) as ctx:entry.open_session(common(),INV,OUT/"forbidden",neutral=True)
        self.assertEqual(ctx.exception.code,"MAIN_GATE_CLOSED")

    def test_22_preflight_diagnostic(self):
        c=common();c["references"].append(["metadata","not-read",65536,"0"*64]);c=reseal(c,"common_digest")
        result=verifier.preflight(c)
        self.assertTrue(result["violations"])
        self.assertEqual(result["failure_diagnostic"]["phase"],"BINDINGS")

    def test_23_read_size_error_keeps_returned_bytes(self):
        path=self.root/"oversize.bin";path.write_bytes(b"x"*19201)
        p=b.Payload("neutral-oversize",path.relative_to(b.ROOT).as_posix(),"0"*64,19200)
        counts=dict(actual_read_bytes=0,read_operations=0)
        with self.assertRaises(b.S2OBError) as ctx:b.read_payload(p,read_account=counts)
        self.assertEqual(ctx.exception.code,"PAYLOAD_SIZE_INVALID")
        self.assertEqual(counts,dict(actual_read_bytes=19201,read_operations=1))

    def test_24_file_caller_pin_error_closes_gate(self):
        cp=self.root/"pin-common.json";s.prior.save(cp,common())
        entry.MAIN_GATE=True
        with patch.object(b,"CallerRuntime",side_effect=AssertionError("RUNTIME_FORBIDDEN")):
            with self.assertRaises(budget.BudgetError) as ctx:
                caller.run(cp,"0"*64,OUT/"inventory.json",OUT/"pin-forbidden",neutral=True)
        self.assertEqual(ctx.exception.code,"CALLER_PIN_INVALID")
        self.assertFalse(entry.MAIN_GATE)
        self.assertFalse((OUT/"pin-forbidden").exists())

    def qualification_common(self,run_id):
        root=self.root/self._testMethodName;root.mkdir()
        for name in s.qa.FILES:
            if name!="result.json":(root/name).write_bytes(b"{}")
        q=b.sealed(dict(run_id=run_id,status="QUALIFIED",test_calls=1,passed_tests=s.TEST_COUNT,expected_tests=s.TEST_COUNT,
            exit_code=0,source_digest=b.digest(INV),hashes_unchanged=True,budget_violations=[],gates=False,
            evidence={name:s.sha((root/name).read_bytes()) for name in s.qa.FILES if name!="result.json"}),"result_digest")
        s.prior.save(root/"result.json",q)
        s.qa.package.create_package(root,root/"qualification.zip",s.qa.FILES)
        measured=s.qa.measure(root/"qualification.zip",root)
        qp=root/"package.json"
        s.prior.save(qp,dict(status="QUALIFIED",sha256=measured["sha256"],violations=[]))
        qr=s.file_reference("metadata",qp)
        return s.build_common(manifest(),INV,[s.file_reference("sources",OUT/"inventory.json"),
            qr,s.file_reference("metadata",root/"qualification.zip")],qr)

    def test_25_historical_pass_not_current_admission(self):
        c=self.qualification_common("historical-qualification")
        with self.assertRaises(budget.BudgetError) as ctx:s.validate_common(c,INV,qualified=True)
        self.assertEqual(ctx.exception.code,"QUALIFICATION_INVALID")

    def test_26_qualification_leaf_content_required(self):
        c=self.qualification_common(s.QUAL_ID)
        c["references"]=[r for r in c["references"] if not r[1].endswith("qualification.zip")]
        c=reseal(c,"common_digest")
        with self.assertRaises(budget.BudgetError) as ctx:s.validate_common(c,INV,qualified=True)
        self.assertEqual(ctx.exception.code,"QUALIFICATION_EVIDENCE_INVALID")

    def test_27_native_pool_no_write_or_reconstruction(self):
        c=common();r,q=verifier.synthetic_forms(c,0)[0]
        native=asdict(b.r.memory.initial_s2jv_composite_state(b.r.nn.profile.build_config()))
        pool=b.StateEvidencePool();pool[native["state_digest"]]=native
        wire=pool[native["state_digest"]]
        self.assertEqual(b.canonical(b.state_wire.decode(wire)),b.canonical(native))
        bad=deepcopy(wire);bad["native_sha256"]="0"*64
        with self.assertRaises(b.state_wire.StateEvidenceError) as ctx:b.state_wire.decode(bad)
        self.assertEqual(ctx.exception.code,"STATE_NATIVE_DIGEST_INVALID")
        r["execution"]["states"]=pool
        r["execution"]=reseal(r["execution"],"record_digest");r=reseal(r,"record_digest")
        q["record_digest"]=r["record_digest"];q=reseal(q,"session_digest")
        before=b.canonical((r,q,c))
        with patch.object(b.StateEvidencePool,"__setitem__",side_effect=AssertionError("POOL_WRITE_FORBIDDEN")):
            with patch.object(b.state_wire,"encode",side_effect=AssertionError("ENCODE_FORBIDDEN")):
                wr,ws=s.pack(r,q,c);restored=s.unpack(wr,ws,c)
        self.assertEqual(b.canonical(restored),b.canonical((r,q)))
        self.assertEqual(before,b.canonical((r,q,c)))

    def test_28_pack_has_no_mutable_internal_alias(self):
        c=common();r,q=verifier.synthetic_forms(c,1)[0];before=b.canonical((r,q,c))
        wr,ws=s.pack(r,q,c)
        wr["record"]["execution"]["states"].clear()
        ws["session"]["returned_results"].clear()
        self.assertEqual(before,b.canonical((r,q,c)))

    def test_29_unpack_has_no_mutable_wire_alias(self):
        c=common();wr,ws=s.pack(*verifier.synthetic_forms(c,1)[0],c)
        before=b.canonical((wr,ws,c));r,q=s.unpack(wr,ws,c)
        r["execution"]["states"].clear();q["returned_results"].clear();r["manifest"]["events"].clear()
        self.assertEqual(before,b.canonical((wr,ws,c)))

    def test_30_full_log_package_integrity(self):
        root=self.root/"log-roundtrip";root.mkdir()
        raw=("Vollstaendige Fehlerdiagnostik: \u00dcberlauf\n"*200).encode("utf-8")
        (root/"stderr.txt").write_bytes(raw)
        s.qa.package.create_package(root,root/"logs.zip",["stderr.txt"])
        measured=s.qa.measure(root/"logs.zip",root)
        self.assertEqual(s.qa.old.packed_file(root/"logs.zip","stderr.txt"),raw)
        self.assertEqual(measured["expanded_total"],len(raw))
        self.assertEqual(measured["stored_total"],(root/"logs.zip").stat().st_size)
        (root/"stderr.txt").write_bytes(raw+b"changed")
        with self.assertRaises(s.qa.package.PackageError) as ctx:s.qa.measure(root/"logs.zip",root)
        self.assertEqual(str(ctx.exception),"RESTORATION_CHANGED")
