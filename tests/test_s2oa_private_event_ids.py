"""Focused neutral ID tests; no payload generation or runtime processing."""
import ast
from copy import deepcopy
from dataclasses import asdict
import json
import os
from pathlib import Path
import re
import unittest
from unittest.mock import patch
from tools import _s2oa_private_main_binding as b
from tools import _s2oa_private_main_verification as v

r, ids = b.r, b.ids
OUT = Path(os.environ["S2OA_ID_QUAL_DIR"])
METRICS = {}


def fixture():
    config=r.nn.profile.build_config()
    events=b.source.events();sources=[]
    for e in events:
        for m in ("auditory","visual"):
            t=e[m]
            if t is None:continue
            recipe=dict(neutral=True,visible_positions=list(range(32)) if e["event_type"]==b.source.V else None)
            sources.append(b.sealed(dict(source_id=t["source_id"],event_id=e["event_id"],event_ordinal=e["ordinal"],
                time_binding=t,recipe=recipe,recipe_digest=b.digest(recipe),payload_sha256="a"*64,
                kind="PCM" if m=="auditory" else "RGB",byte_count=19200 if m=="auditory" else 6220800),"source_digest"))
    ex=b.sealed(dict(events=events,sources=sources,source_order=[s["source_id"] for s in sources],
        profiles=dict(coordinator_config_digest=config.config_digest)),"execution_digest")
    mapping=ids.build(ex)
    p=dict(execution_digest=ex["execution_digest"],event_ids=mapping)
    return b.BoundOA(b.canonical(ex).decode(),b.canonical(p).decode()),config


class IdTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bound,cls.config=fixture();cls.ex=cls.bound.execution();cls.mapping=cls.bound.provenance()["event_ids"]
        cls.packed=[dict(event=dict(event_id="s2oa-event-e"+str(e["ordinal"]).zfill(2),
            ordinal=e["ordinal"],event_type=e["event_type"])) for e in cls.ex["events"]]
        cls.qdir=b.ROOT/"reports/s2oa"/b.QUAL_ID
        cls.pr=json.loads((OUT/"preregistration.json").read_bytes())
        cls.oldpr=json.loads((cls.qdir/"preregistration.json").read_bytes())
        cls.shape=json.loads((cls.qdir/"reports/s2oa/s2oa-continuous-runtime-20260910-01/record.json").read_bytes())
        cls.adminproof=json.loads((b.ADMIN_DIR/"verification.json").read_bytes())
        cls.refs={}
        for role,directory in (("previous",b.OLD_QUAL),("main",cls.qdir)):
            cls.refs[role]={n:dict(path=(directory/n).relative_to(b.ROOT).as_posix(),sha256=r.admin.filehash(directory/n),
                bytes=(directory/n).stat().st_size) for n in ("preregistration.json","result.json","stdout.txt","stderr.txt")}
        for obj,name in ((b.source,"generators"),(b.source,"occlude"),(b.Materializer,"run_once"),
                         (b,"run_main_once"),(b,"OARuntime"),(r,"SingleRuntime"),
                         (r.half,"project_auditory_half_v1"),(b.LocalChannelGridReceptor,"analyze"),
                         (r.half.spectral.LogSpectralReceptor,"analyze")):
            guard=patch.object(obj,name,side_effect=AssertionError("EXECUTION_FORBIDDEN"))
            guard.start();cls.addClassCleanup(guard.stop)
        read=Path.read_bytes
        def guarded(path):
            if path.is_relative_to(b.ROOT/"reports") and not path.is_relative_to(OUT):
                raise AssertionError("CORPUS_READ_FORBIDDEN")
            return read(path)
        guard=patch.object(Path,"read_bytes",guarded);guard.start();cls.addClassCleanup(guard.stop)

    @classmethod
    def tearDownClass(cls):
        r.admin.publish(OUT/"metrics.json",METRICS)

    def reject(self,code,fn,*args):
        with self.assertRaises(r.S2OAError) as cm:fn(*args)
        self.assertEqual(cm.exception.code,code)

    def test_01_all_28(self):
        self.assertEqual(b.validate_bound(self.bound),self.ex)
        self.assertEqual(ids.validate(self.mapping,self.ex),self.mapping)
        names=[ids.technical_id(self.mapping,e) for e in self.ex["events"]]
        self.assertEqual(len(set(names)),28)
        self.assertTrue(all(re.fullmatch(r"[a-z][a-z0-9-]{7,95}",n) for n in names))
        self.assertEqual([x[1] for x in self.mapping["rows"]],[f"e{n:02d}" for n in range(1,29)])
        METRICS["id_rows"]=28

    def test_02_missing(self):
        x=deepcopy(self.mapping);x["rows"].pop()
        self.reject("ID_COUNT_INVALID",ids.validate,x,self.ex)
        p=self.bound.provenance();del p["event_ids"]
        self.reject("ID_BINDING_MISSING",b.validate_bound,b.BoundOA(self.bound.execution_json,b.canonical(p).decode()))

    def test_03_swapped(self):
        x=deepcopy(self.mapping);x["rows"][0],x["rows"][1]=x["rows"][1],x["rows"][0]
        self.reject("ID_ROW_INVALID",ids.validate,x,self.ex)

    def test_04_collision(self):
        x=deepcopy(self.mapping);x["rows"][1][2]=x["rows"][0][2]
        self.reject("ID_ROW_INVALID",ids.validate,x,self.ex)

    def test_05_foreign_root(self):
        x=deepcopy(self.mapping);x["execution_digest"]="b"*64
        self.reject("ID_ROOT_INVALID",ids.validate,x,self.ex)

    def test_06_plan_identity(self):
        for field,value in (("event_id","e02"),("ordinal",True)):
            with self.subTest(field=field):
                ex=deepcopy(self.ex);ex["events"][0][field]=value
                self.reject("ID_PLAN_INVALID",ids.build,ex)

    def test_07_shape_and_digest(self):
        for mode,code in (("extra","ID_FORM_INVALID"),("digest","ID_DIGEST_INVALID"),("bool","ID_ROW_INVALID")):
            with self.subTest(mode=mode):
                x=deepcopy(self.mapping)
                if mode=="extra":x["extra"]=None
                elif mode=="digest":x["id_binding_digest"]="0"*64
                else:x["rows"][0][0]=True
                self.reject(code,ids.validate,x,self.ex)

    def test_08_e01_visual_builder(self):
        profile=self.config.profile.profile.visual_config
        frame=r.nn.ReceptorContactFrame("visual",profile.geometry_id,"neutral.visual.2","video.frame",2,3,
            profile.carrier_ids,(0.0,)*288)
        timed=r.nn.OrganismTimedReceptorFrame(frame,r.nn.CommonFieldTime(r.CLOCK,66666666,100000000))
        before=b.canonical(asdict(timed));root=self.bound.execution_json
        item=b.bind_event(self.bound,self.ex["events"][0],config=self.config,visual=timed,rgb_digest="a"*64)
        self.assertEqual(item.event.event_id,"s2oa-event-e01")
        self.assertEqual(item.event.event_type,"PARTIAL_VISUAL_CUE")
        packed=r.ng.pack_input(item.event,self.config)
        decoded=v.prior.ngv.decode_input(packed,self.config)
        self.assertEqual(decoded,item.event)
        v.prior.source_receipt(json.loads(item.nj_json),decoded,self.config)
        self.assertEqual(b.canonical(asdict(timed)),before);self.assertEqual(self.bound.execution_json,root)
        METRICS.update(neutral_lm_inputs=1,packed_input_bytes=len(b.canonical(packed)),source_receipt_bytes=len(item.nj_json))

    def test_09_foreign_event(self):
        x=deepcopy(self.ex["events"][0]);x["event_id"]="e02"
        self.reject("ID_EVENT_INVALID",b.bind_event,self.bound,x)

    def test_10_independent_ids(self):
        with patch.object(ids,"validate",side_effect=AssertionError("PRODUCER_FORBIDDEN")),patch.object(ids,"technical_id",side_effect=AssertionError("PRODUCER_FORBIDDEN")):
            self.assertEqual(v.verify_event_ids(self.mapping,self.ex,self.packed),self.mapping["id_binding_digest"])
            for mode,code in (("missing","ID_COUNT_INVALID"),("swapped","ID_ROW_INVALID"),("collision","ID_ROW_INVALID"),("root","ID_ROOT_INVALID"),("actual","MAIN_EVENT_BINDING_INVALID")):
                with self.subTest(mode=mode):
                    x=deepcopy(self.mapping);p=deepcopy(self.packed)
                    if mode=="missing":x["rows"].pop()
                    elif mode=="swapped":x["rows"][0],x["rows"][1]=x["rows"][1],x["rows"][0]
                    elif mode=="collision":x["rows"][1][2]=x["rows"][0][2]
                    elif mode=="root":x["execution_digest"]="b"*64
                    else:p[0]["event"]["event_id"]="e01"
                    self.reject(code,v.verify_event_ids,x,self.ex,p)

    def test_11_actual_connections(self):
        tree=ast.parse((b.ROOT/"tools/_s2oa_private_main_binding.py").read_text())
        materializer=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="Materializer")
        self.assertTrue(any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=="bind_event" for n in ast.walk(materializer)))
        tree=ast.parse((b.ROOT/"tools/_s2oa_private_main_verification.py").read_text())
        verifier=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="_verify")
        self.assertTrue(any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=="verify_event_ids" for n in ast.walk(verifier)))

    def test_12_qualification_delta(self):
        previous=self.oldpr["hashes"];current={**previous,**self.pr["hashes"]}
        b.validate_id_qualification_manifest(self.pr,previous,current)
        for mode,code in (("unrelated","ID_QUAL_CODE_INVALID"),("historical","ID_QUAL_DELTA_INVALID")):
            with self.subTest(mode=mode):
                p=deepcopy(self.pr);old=deepcopy(previous);now=deepcopy(current)
                if mode=="unrelated":now["unexpected.py"]="0"*64
                else:old[next(iter(ids.OLD_HASHES))]="0"*64
                self.reject(code,b.validate_id_qualification_manifest,p,old,now)

    def test_13_complete_envelope(self):
        # Previously recorded NEUTRAL shapes only: no replay or claim of v2 digest validity.
        x=deepcopy(self.shape);p=x["bindings"]
        p["qualifications"]=deepcopy(self.refs)
        p["qualifications"]["event_ids"]=dict(qualification_id=ids.QUAL_ID,
            files={n:["a"*64,ids.QUAL_BYTES if n=="preregistration.json" else 0]
                for n in ("preregistration.json","result.json","stdout.txt","stderr.txt","metrics.json")})
        p["metadata_bytes"]=self.adminproof["balance"]["metadata_bytes"]+sum(z["bytes"] for refs in self.refs.values() for z in refs.values())+ids.QUAL_BYTES
        p["source_bytes"]=162321;p["event_ids"]=self.mapping;x["schema"]=b.SCHEMA
        sizes=b.envelope_size(x)
        self.assertLessEqual(sizes["balance"]["metadata_bytes"]+512,65536)
        self.assertLessEqual(len(b.canonical(self.mapping)),ids.MAX_BYTES)
        self.assertTrue(all(len("neutral-oa-"+str(n).zfill(2))==len(row[2]) for n,row in enumerate(self.mapping["rows"],1)))
        METRICS.update(id_binding_bytes=len(b.canonical(self.mapping)),metadata_upper=sizes["balance"]["metadata_bytes"]+512,
            total_upper=sizes["balance"]["total_reserved_bytes"]+512,whole_record_bytes=sizes["whole_record_bytes"],
            shared_bytes=sizes["balance"]["shared_reserved_bytes"],report_reserve=512,shape_only=True,new_field_memory_calls=0)
        for field,limit,code in (("metadata_bytes",65536,"METADATA_ITEM_LIMIT"),("source_bytes",174080,"SOURCES_ITEM_LIMIT")):
            # Exact established ledger codes, not generic exception acceptance.
            bad=deepcopy(x);bad["bindings"][field]=limit+1
            with self.subTest(field=field):
                with self.assertRaises(r.admin.S2OAAdminError) as cm:b.envelope_size(bad)
                self.assertEqual(cm.exception.code,code)
        bad=deepcopy(x);bad["bindings"]["metadata_bytes"]=65000
        with self.assertRaises(r.admin.S2OAAdminError) as cm:b.envelope_size(bad)
        self.assertEqual(cm.exception.code,"METADATA_TOTAL_LIMIT")

    def test_14_closed_gates(self):
        self.assertFalse(b.MAIN_GATE);self.assertFalse(r.MAIN_GATE);self.assertFalse(b.source.MAIN_GATE)
        self.assertEqual(b.SCHEMA,"s2oa.bound-main.v2")
        self.assertEqual(r.SCHEMA,"s2oa.single-runtime.v1")
        self.assertEqual(ids.OLD_HASHES,{k:self.oldpr["hashes"][k] for k in ids.OLD_HASHES})


if __name__=="__main__":unittest.main()
