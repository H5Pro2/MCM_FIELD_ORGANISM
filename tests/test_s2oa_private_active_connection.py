"""Thirty current administrative checks; no history replay or OA payloads."""
from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools import _s2oa_private_main_binding as b
from tools import _s2oa_private_main_verification as v
from reports.s2oa import prepare_active_connection as prep
from reports.s2oa import qualify_active_connection_once as driver

a,r,ids=b.active,b.r,b.ids
ROOT=b.ROOT
OUT=Path(os.environ["S2OA_ACTIVE_QUAL_DIR"])
METRICS=dict(lm_bindings=0,payloads=0,receptors=0,nj=0,memory=0,field=0,runtime=0,replays=0)


def seal(value,key):
    return {**{k:v for k,v in value.items() if k!=key},
            key:a.digest({k:v for k,v in value.items() if k!=key})}


def neutral_binding(config):
    events=b.source.events();sources=[]
    for e in events:
        for modality in ("auditory","visual"):
            t=e[modality]
            if t is None:continue
            recipe=dict(neutral=True,visible_positions=list(range(32)) if e["event_type"]==b.source.V else None)
            sources.append(seal(dict(source_id=t["source_id"],event_id=e["event_id"],event_ordinal=e["ordinal"],
                time_binding=t,recipe=recipe,recipe_digest=a.digest(recipe),payload_sha256="a"*64,
                kind="PCM" if modality=="auditory" else "RGB",byte_count=19200 if modality=="auditory" else 6220800),"source_digest"))
    ex=seal(dict(events=events,sources=sources,source_order=[s["source_id"] for s in sources],
        profiles=dict(coordinator_config_digest=config.config_digest)),"execution_digest")
    return b.BoundOA(a.canonical(ex).decode(),a.canonical(dict(execution_digest=ex["execution_digest"],event_ids=ids.build(ex))).decode())


class ActiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads((ROOT/a.MANIFEST).read_bytes())
        cls.inventory=json.loads((ROOT/a.INVENTORY).read_bytes())
        cls.hashes=b.watched()
        cls.config=r.nn.profile.build_config()
        cls.bound=neutral_binding(cls.config);cls.ex=cls.bound.execution()
        cls.mapping=cls.bound.provenance()["event_ids"]
        cls.packed=[dict(event=dict(event_id="s2oa-event-e%02d"%n,ordinal=n,event_type=e["event_type"]))
                    for n,e in enumerate(cls.ex["events"],1)]
        _,cls.preparation,cls.shape=prep.build_preparation(driver.manifest_fields())
        cls.read_bytes=Path.read_bytes;cls.is_file=Path.is_file
        for obj,name in ((b.source,"generators"),(b.source,"occlude"),(b.Materializer,"run_once"),
                         (b,"run_main_once"),(b,"OARuntime"),(r,"SingleRuntime"),
                         (r.half,"project_auditory_half_v1"),(b.LocalChannelGridReceptor,"analyze"),
                         (r.half.spectral.LogSpectralReceptor,"analyze"),
                         (r.memory,"advance_s2jv_atomic"),(r.ng.field,"build_s2lo_field_adapter")):
            guard=patch.object(obj,name,side_effect=AssertionError("FUNCTIONAL_EXECUTION_FORBIDDEN"))
            guard.start();cls.addClassCleanup(guard.stop)

    def reject(self,cls,code,fn,*args):
        with self.assertRaises(cls) as error:fn(*args)
        self.assertEqual(error.exception.code,code)
        return error.exception

    def virtual(self,*,manifest=None,mutate=None,missing=False,files=None,call=None):
        """Synthetic success only in memory; never create an active PASS file."""
        m=deepcopy(self.manifest if manifest is None else manifest)
        m=seal(m,"manifest_digest");mraw=a.canonical(m)
        blobs={n:b"" for n in ("stdout.txt","stderr.txt")}
        blobs.update({n:b"{}" for n in ("metrics.json","preflight-balance.json","final-balance.json")})
        blobs["BEFUND.md"]=b"Neutral synthetic attestation.\n"
        blobs["invoked.claim"]=b"once"
        blobs.update(files or {})
        q=dict(schema="s2oa.active-qualification.v1",run_id=m["qualification_run_id"],status="QUALIFIED",
            test_calls=1,main_gate_after=False,manifest_sha256=hashlib.sha256(mraw).hexdigest(),
            code_before=a.digest(self.hashes),code_after=a.digest(self.hashes),
            tests=[[row["id"],"PASS"] for row in self.inventory["tests"]],
            files={n:[hashlib.sha256(raw).hexdigest(),len(raw)] for n,raw in blobs.items()})
        if mutate:mutate(q)
        q=seal(q,"result_digest")
        virtual={ROOT/a.MANIFEST:mraw,ROOT/a.OUTCOME:a.canonical(q),
                 **{ROOT/a.DIRECTORY/n:raw for n,raw in blobs.items()}}
        seen=[]
        def read(path):
            seen.append(path)
            if path in virtual:return virtual[path]
            return type(self).read_bytes(path)
        def exists(path):
            if path==ROOT/a.OUTCOME:return not missing
            return path in virtual or type(self).is_file(path)
        with patch.object(Path,"read_bytes",read),patch.object(Path,"is_file",exists):
            result=(call or b.load_bound)()
        return result,seen

    def zero(self):return {k:0 for k in a.RESERVES}

    def budget_failure(self,metadata,sources,reserves,other,expected):
        # A valid baseline and exact full violation set exclude hidden gates.
        self.assertEqual(a.measure({"base":100},{"base":100},self.zero())["violations"],[])
        report=a.measure(metadata,sources,reserves,other)
        self.assertEqual([x["code"] for x in report["violations"]],expected)
        error=self.reject(a.ActiveConnectionError,expected[0],a.enforce,report)
        self.assertEqual(error.balance,report)
        self.assertEqual(report["balance"]["total_reserved_bytes"],sum(metadata.values())+sum(sources.values())+sum(reserves.values())+other)
        return report

    def test_a01(self):
        self.assertEqual(b.validate_bound(self.bound),self.ex)
        names=[ids.technical_id(self.mapping,e) for e in self.ex["events"]]
        self.assertEqual(len(set(names)),28)
        self.assertTrue(all(re.fullmatch(r"[a-z][a-z0-9-]{7,95}",name) for name in names))
        self.assertEqual([row[1] for row in self.mapping["rows"]],["e%02d"%n for n in range(1,29)])

    def test_a02(self):
        from types import SimpleNamespace as N
        for n,e in enumerate(self.ex["events"],1):
            with self.subTest(event=n):
                technical=ids.technical_id(self.mapping,e)
                self.assertEqual(len(technical),14);self.assertEqual(len("neutral-oa-%02d"%n),13)
                post=N(state_digest="p",b4_state=None,tspm_state=N(composite_state_digest="t"))
                with patch.object(r.memory,"_b4_digest",return_value="b4"):
                    context=r.formation_context(self.config,N(state_digest="old"),post,N(input_digest="input"),N(event_id=technical),"neutral-run","result")
                self.assertEqual((context[6],context[8]),(technical+"-owner",technical+"-consume"))
                self.assertEqual((len(context[6]),len(context[8])),(20,22))
        # The AV binder passes the unmodified technical ID as pair_id.
        import ast
        tree=ast.parse((ROOT/"tools/_s2oa_private_runtime_binding.py").read_text(encoding="utf-8"))
        calls=[x for x in ast.walk(tree) if isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr=="bind_pair"]
        self.assertEqual(len(calls),1)
        self.assertTrue(any(k.arg=="pair_id" and isinstance(k.value,ast.Name) and k.value.id=="event_id" for k in calls[0].keywords))
        METRICS.update(event_id_length=14,owner_id_length=20,consume_id_length=22)

    def test_a03(self):
        x=deepcopy(self.mapping);x["rows"].pop()
        self.reject(r.S2OAError,"ID_COUNT_INVALID",ids.validate,x,self.ex)

    def test_a04(self):
        x=deepcopy(self.mapping);x["rows"][0],x["rows"][1]=x["rows"][1],x["rows"][0]
        self.reject(r.S2OAError,"ID_ROW_INVALID",ids.validate,x,self.ex)

    def test_a05(self):
        x=deepcopy(self.mapping);x["rows"][1][2]=x["rows"][0][2]
        self.reject(r.S2OAError,"ID_ROW_INVALID",ids.validate,x,self.ex)

    def test_a06(self):
        x=deepcopy(self.mapping);x["execution_digest"]="f"*64
        self.reject(r.S2OAError,"ID_ROOT_INVALID",ids.validate,x,self.ex)

    def test_a07(self):
        profile=self.config.profile.profile.visual_config
        frame=r.nn.ReceptorContactFrame("visual",profile.geometry_id,"neutral.visual.2","video.frame",2,3,profile.carrier_ids,(0.0,)*288)
        timed=r.nn.OrganismTimedReceptorFrame(frame,r.nn.CommonFieldTime(r.CLOCK,66666666,100000000))
        before=a.canonical(asdict(timed))
        item=b.bind_event(self.bound,self.ex["events"][0],config=self.config,visual=timed,rgb_digest="a"*64)
        METRICS["lm_bindings"]+=1
        self.assertEqual(item.event.event_id,"s2oa-event-e01")
        self.assertEqual(item.event.event_type,"PARTIAL_VISUAL_CUE")
        packed=r.ng.pack_input(item.event,self.config)
        decoded=v.prior.ngv.decode_input(packed,self.config)
        self.assertEqual(decoded,item.event)
        v.prior.source_receipt(json.loads(item.nj_json),decoded,self.config)
        self.assertEqual(before,a.canonical(asdict(timed)))
        METRICS.update(lm_input_bytes=len(a.canonical(packed)),lm_source_bytes=len(item.nj_json))

    def test_a08(self):
        self.assertEqual(len(a.canonical(self.mapping)),1041)
        self.assertLessEqual(len(a.canonical(self.mapping)),ids.MAX_BYTES)
        self.assertEqual(ids.MAX_BYTES,2048)
        # No claim that a malformed longer ID table reaches the size gate.

    def test_a09(self):
        bound,_=self.virtual()
        self.assertIs(type(bound),b.BoundOA)
        self.assertEqual(bound.provenance()["code_digest"],a.digest(self.hashes))
        self.assertEqual(self.hashes,self.manifest["code_hashes"])

    def test_a10(self):
        self.reject(a.ActiveConnectionError,"ACTIVE_QUALIFICATION_MISSING",lambda:self.virtual(missing=True))

    def test_a11(self):
        for change,code in ((lambda q:q.update(status="NOT_QUALIFIED"),"ACTIVE_NOT_QUALIFIED"),
                            (lambda q:q["tests"].pop(),"ACTIVE_COVERAGE_INVALID")):
            with self.subTest(code=code):self.reject(a.ActiveConnectionError,code,lambda:self.virtual(mutate=change))

    def test_a12(self):
        hashes={**self.hashes,next(iter(self.hashes)):"0"*64}
        self.reject(a.ActiveConnectionError,"ACTIVE_CODE_CHANGED",lambda:self.virtual(call=lambda:a.load(ROOT,hashes)))

    def test_a13(self):
        m=deepcopy(self.manifest);m["metadata_dependencies"].pop()
        self.reject(r.S2OAError,"ACTIVE_METADATA_CLOSURE_INVALID",lambda:self.virtual(manifest=m))

    def test_a14(self):
        m=deepcopy(self.manifest);m["metadata_dependencies"][0]["sha256"]="0"*64
        self.reject(a.ActiveConnectionError,"ACTIVE_REFERENCE_INVALID",lambda:self.virtual(manifest=m))

    def test_a15(self):
        m=deepcopy(self.manifest)
        m["metadata_dependencies"][0],m["source_dependencies"][0]=m["source_dependencies"][0],m["metadata_dependencies"][0]
        self.reject(r.S2OAError,"ACTIVE_METADATA_CLOSURE_INVALID",lambda:self.virtual(manifest=m))

    def test_a16(self):
        bound,seen=self.virtual()
        required=[ROOT/ref["path"] for key in ("metadata_dependencies","source_dependencies","verification_dependencies") for ref in self.manifest[key]]
        self.assertTrue(set(required)<=set(seen))
        forbidden=("single-runtime-qualification","main-binding-qualification","event-id-qualification","compact-reference-qualification","continuous-runtime")
        self.assertFalse(any(any(marker in str(p) for marker in forbidden) and p.suffix in (".json",".txt") for p in seen))
        self.assertEqual(sum(bound.provenance()["source_items"].values()),162321)

    def test_a17(self):
        x=deepcopy(self.shape);before=a.canonical(x)
        self.assertEqual(a.canonical(b.decode_record(x)),before)
        self.assertEqual(len(x["execution"]["inputs"]),28)
        x["schema"]="s2oa.bound-main.v3"
        self.reject(r.S2OAError,"MAIN_FORM_INVALID",b.decode_record,x)

    def test_a18(self):
        with patch.object(ids,"build",side_effect=AssertionError("PRODUCER_FORBIDDEN")),patch.object(ids,"technical_id",side_effect=AssertionError("PRODUCER_FORBIDDEN")):
            self.assertEqual(v.verify_event_ids(self.mapping,self.ex,self.packed),self.mapping["id_binding_digest"])

    def test_a19(self):
        sizes=b.envelope_size(self.shape)
        self.assertEqual(sizes["breakdown"]["violations"],[])
        self.assertLessEqual(sizes["balance"]["metadata_bytes"],65536)
        self.assertEqual(sizes["breakdown"]["completion_reserved_bytes"],524292)
        METRICS.update(metadata_bytes=sizes["balance"]["metadata_bytes"],record_bytes=sizes["whole_record_bytes"])

    def test_a20(self):
        self.budget_failure({"one":65537},{},self.zero(),0,["METADATA_ITEM_LIMIT","METADATA_TOTAL_LIMIT"])

    def test_a21(self):
        self.budget_failure({"one":32768,"two":32769},{},self.zero(),0,["METADATA_TOTAL_LIMIT"])

    def test_a22(self):
        self.budget_failure({"one":100},{"one":174081},self.zero(),0,["SOURCES_ITEM_LIMIT","SOURCES_TOTAL_LIMIT"])

    def test_a23(self):
        self.budget_failure({"one":100},{"one":87040,"two":87041},self.zero(),0,["SOURCES_TOTAL_LIMIT"])

    def test_a24(self):
        self.assertEqual(174080+sum(a.RESERVES.values()),258048)
        a.enforce(a.measure({"one":100},{"one":174080},a.RESERVES))
        self.reject(r.admin.S2OAAdminError,"SHARED_LIMIT",r.admin.shared_total_check,[262144,1])

    def test_a25(self):
        for total in (4194305,4335858):
            with self.subTest(total=total):
                report=self.budget_failure({"one":100},{"one":100},self.zero(),total-200,["TOTAL_LIMIT"])
                self.assertEqual(report["balance"]["total_reserved_bytes"],total)

    def test_a26(self):
        for key,count,cap in (("nj",22,1024),("formations",20,1536),("generations",20,1536)):
            with self.subTest(category=key,boundary="aggregate"):
                reserves=self.zero();reserves[key]=a.RESERVES[key]+1
                self.budget_failure({"one":100},{"one":100},reserves,0,[key.upper()+"_RESERVE_LIMIT"])
            for mode in ("item","count"):
                with self.subTest(category=key,boundary=mode):
                    x=dict(bindings=dict(metadata_items={"one":100},source_items={"one":100}),
                        execution=dict(states={},inputs=[],scans=[],rows=[],source_receipts=[]))
                    core=x["execution"]
                    n=1 if mode=="item" else count+1
                    data="x"*(cap-1) if mode=="item" else {}
                    if key=="nj":core["source_receipts"]=[dict(nj=deepcopy(data)) for _ in range(n)]
                    else:
                        member="formation" if key=="formations" else "generations"
                        core["rows"]=[{**dict(formation=None,generations=None),member:deepcopy(data)} for _ in range(n)]
                    report=a.inspect_envelope(x)
                    self.assertEqual([z["code"] for z in report["violations"]],[key.upper()+"_"+mode.upper()+"_LIMIT"])
                    self.reject(a.ActiveConnectionError,key.upper()+"_"+mode.upper()+"_LIMIT",a.enforce,report)

    def test_a27(self):
        bound,_=self.virtual()
        self.assertEqual(bound.provenance()["metadata_items"]["qualification_reserved"],4096)
        self.assertEqual(a.inspect_envelope(self.shape)["metadata"]["report"],512)
        with self.subTest(boundary="qualification"):
            self.reject(a.ActiveConnectionError,"ACTIVE_QUALIFICATION_LIMIT",lambda:self.virtual(files={"stderr.txt":b"x"*4096}))
        with self.subTest(boundary="report"):
            self.reject(a.ActiveConnectionError,"ACTIVE_REPORT_LIMIT",lambda:self.virtual(files={"BEFUND.md":b"x"*513}))

    def test_a28(self):
        x=deepcopy(self.shape);x["bindings"]["metadata_items"]["oversized"]=65537
        report=a.inspect_envelope(x)
        self.assertEqual([z["code"] for z in report["violations"]],["METADATA_ITEM_LIMIT","METADATA_TOTAL_LIMIT"])
        self.assertIn("runtime",report["metadata"]);self.assertIn("shell",report["metadata"])
        self.assertEqual(sum(report["metadata"].values()),report["balance"]["metadata_bytes"])
        error=self.reject(a.ActiveConnectionError,"METADATA_ITEM_LIMIT",a.enforce,report)
        self.assertEqual(error.balance,report)

    def test_a29(self):
        record=self.shape;core=record["execution"];p=record["bindings"]
        lengths=[]
        for value in core["states"].values():lengths.append(len(a.canonical(value)))
        for name in ("inputs","scans"):
            lengths.extend(len(a.canonical(x)) for x in core[name])
        for row in core["rows"]:
            lengths.append(len(a.canonical({k:x for k,x in row.items() if k not in ("formation","generations")})))
            lengths.extend(len(a.canonical(row[k])) for k in ("formation","generations") if row[k] is not None)
        lengths.extend(len(a.canonical(x)) for x in core["source_receipts"] if x["nj"] is not None)
        expected=sum(p["metadata_items"].values())+len(a.canonical(record))-sum(lengths)+512
        self.assertEqual(a.inspect_envelope(record)["balance"]["metadata_bytes"],expected)
        for mode in ("omit","duplicate"):
            with self.subTest(mode=mode):
                x=deepcopy(record)
                if mode=="omit":x["bindings"]["metadata_items"].pop(next(iter(x["bindings"]["metadata_items"])))
                else:x["bindings"]["metadata_items"]["duplicate"]=1
                self.reject(r.S2OAError,"ACTIVE_ACCOUNTING_INVALID",b.envelope_size,x)

    def test_a30(self):
        with tempfile.TemporaryDirectory() as directory:
            raw=b"full-neutral-error-line\n"*300
            driver.write_raw(Path(directory)/"stderr.txt",raw)
            self.assertEqual((Path(directory)/"stderr.txt").read_bytes(),raw)
            self.assertGreater(driver.qualification_bytes(b"{}",b"{}",b"",raw),4096)
        self.assertFalse(b.MAIN_GATE);self.assertFalse(r.MAIN_GATE);self.assertFalse(b.source.MAIN_GATE)
        self.assertEqual(len(self.inventory["tests"]),30)


class Result(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.passed=[]
    def addSuccess(self,test):
        super().addSuccess(test);self.passed.append(test._testMethodName.removeprefix("test_"))


def main():
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(ActiveTests)
    result=unittest.TextTestRunner(verbosity=0,resultclass=Result).run(suite)
    METRICS.update(tests_run=result.testsRun,passed=sorted(result.passed),
                   failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped))
    driver.write_raw(OUT/"metrics.json",a.canonical(METRICS))
    return 0 if result.wasSuccessful() else 1


if __name__=="__main__":raise SystemExit(main())
