"""Administrative-only round trips and independent budget controls."""
from copy import deepcopy
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
from tools import _s2oa_private_main_binding as b
from tools import _s2oa_private_main_verification as v

c,r,ids=b.compact,b.r,b.ids
OUT=Path(os.environ["S2OA_COMPACT_QUAL_DIR"])
METRICS={}


class CompactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=b.ROOT/"reports/s2oa";old=root/b.QUAL_ID
        cls.manifest=json.loads((old/"preregistration.json").read_bytes())["hashes"]
        cls.pr=json.loads((OUT/"preregistration.json").read_bytes())
        cls.old_delta=json.loads((root/ids.QUAL_ID/"preregistration.json").read_bytes())
        cls.x=json.loads((old/"reports/s2oa/s2oa-continuous-runtime-20260910-01/record.json").read_bytes())
        admin=json.loads((b.ADMIN_DIR/"verification.json").read_bytes())
        cls.ex=dict(execution_digest=cls.x["bindings"]["execution_digest"],
            events=[dict(ordinal=n,event_id=f"e{n:02d}",event_type="PARTIAL_VISUAL_CUE") for n in range(1,29)])
        cls.mapping=ids.build(cls.ex);p=cls.x["bindings"]
        p["event_ids"]=cls.mapping;cls.x["schema"]=b.SCHEMA
        prior_bytes=admin["balance"]["metadata_bytes"]
        for role,directory in (("previous",b.OLD_QUAL),("main",old)):
            refs={n:dict(path=(directory/n).relative_to(b.ROOT).as_posix(),sha256=r.admin.filehash(directory/n),bytes=(directory/n).stat().st_size)
                for n in ("preregistration.json","result.json","stdout.txt","stderr.txt")}
            p["qualifications"][role]=refs;prior_bytes+=sum(z["bytes"] for z in refs.values())
        for role,qid in (("event_ids",ids.QUAL_ID),("correction",c.QUAL_ID)):
            names=("preregistration.json","result.json","stdout.txt","stderr.txt","metrics.json")
            if role=="correction":names=(*names,"BEFUND.md")
            p["qualifications"][role]=dict(qualification_id=qid,
                files={n:["a"*64,4096 if n=="preregistration.json" else 0] for n in names})
        p["metadata_bytes"]=prior_bytes+2*4096;p["source_bytes"]=162321
        cls.x=b.sealed({k:z for k,z in cls.x.items() if k!="record_digest"},"record_digest")
        cls.wire=c.pack(cls.x,cls.manifest)
        METRICS.update(base_reference_bytes=prior_bytes,old_id_reserve=4096,correction_reserve=4096,report_reserve=512)
        for obj,name in ((b,"run_main_once"),(b.Materializer,"run_once"),(b,"OARuntime"),(r,"SingleRuntime"),
                         (b.source,"generators"),(r.half,"project_auditory_half_v1"),(b.LocalChannelGridReceptor,"analyze"),
                         (r.half.spectral.LogSpectralReceptor,"analyze"),(v.prior,"verify")):
            pch=patch.object(obj,name,side_effect=AssertionError("REPLAY_FORBIDDEN"));pch.start();cls.addClassCleanup(pch.stop)
        read=Path.read_bytes
        def guarded(path):
            if path.is_relative_to(root) and not path.is_relative_to(OUT):raise AssertionError("CORPUS_READ_FORBIDDEN")
            return read(path)
        pch=patch.object(Path,"read_bytes",guarded);pch.start();cls.addClassCleanup(pch.stop)

    @classmethod
    def tearDownClass(cls):r.admin.publish(OUT/"metrics.json",METRICS)

    def rejected(self,code,x,manifest=None):
        with self.assertRaises(r.S2OAError) as cm:c.unpack(x,self.manifest if manifest is None else manifest)
        self.assertEqual(cm.exception.code,code)

    def reseal(self,x):return b.sealed({k:v for k,v in x.items() if k!="record_digest"},"record_digest")

    def test_01_roundtrip(self):
        old=b.canonical(self.x);wire=b.canonical(self.wire)
        expanded=c.unpack(self.wire,self.manifest)
        self.assertEqual({k:v for k,v in expanded.items() if k!="record_digest"}, {k:v for k,v in self.x.items() if k!="record_digest"})
        self.assertEqual(expanded["execution"],self.x["execution"])
        self.assertEqual(b.canonical(self.x),old);self.assertEqual(b.canonical(self.wire),wire)
        self.assertEqual(expanded["bindings"]["event_ids"]["rows"],self.mapping["rows"])
        METRICS["reconstructed_ids"]=28

    def test_02_id_single_size(self):
        self.assertLessEqual(len(b.canonical(self.mapping)),2048)
        METRICS["id_expanded_bytes"]=len(b.canonical(self.mapping))
        METRICS["id_stored_bytes"]=len(b.canonical(self.wire["bindings"]["event_ids"]))

    def test_03_lengths(self):
        for n,row in enumerate(self.mapping["rows"],1):
            with self.subTest(n=n):self.assertEqual(len(row[2]),len(f"neutral-oa-{n:02d}"))

    def test_04_metadata_item(self):
        x=deepcopy(self.wire);x["bindings"]["metadata_bytes"]=65537
        with self.assertRaises(r.admin.S2OAAdminError) as cm:b.envelope_size(x)
        self.assertEqual(cm.exception.code,"METADATA_ITEM_LIMIT")

    def test_05_source_item(self):
        x=deepcopy(self.wire);x["bindings"]["source_bytes"]=174081
        with self.assertRaises(r.admin.S2OAAdminError) as cm:b.envelope_size(x)
        self.assertEqual(cm.exception.code,"SOURCES_ITEM_LIMIT")

    def test_06_metadata_total(self):
        x=deepcopy(self.wire);x["bindings"]["metadata_bytes"]=65000
        with self.assertRaises(r.admin.S2OAAdminError) as cm:b.envelope_size(x)
        self.assertEqual(cm.exception.code,"METADATA_TOTAL_LIMIT")

    def test_07_total_limit(self):
        with self.assertRaises(r.admin.S2OAAdminError) as cm:r.admin.ledger({"q":100},{"s":162321},r.admin.RESERVES,4194304)
        self.assertEqual(cm.exception.code,"TOTAL_LIMIT")

    def test_08_complete_envelope(self):
        sizes=b.envelope_size(self.wire)
        self.assertLessEqual(sizes["balance"]["metadata_bytes"],65536)
        self.assertEqual(self.wire["bindings"]["metadata_bytes"],METRICS["base_reference_bytes"]+8192)
        q=sizes["components"];core=self.wire["execution"];balance=b.av.check_totals(
            dict(prior=self.wire["bindings"]["metadata_bytes"],runtime=q["metadata_runtime_bytes"],
                shell=len(b.canonical(self.wire))-len(b.canonical(core)),report=512),
            dict(historical=162321),q["ledger"]["reservations"],len(b.canonical(core))-q["metadata_runtime_bytes"]-sum(q["ledger"]["reservations"].values()))
        self.assertEqual(balance,sizes["balance"])
        METRICS.update(metadata_upper=balance["metadata_bytes"],metadata_remaining=balance["metadata_remaining_bytes"],
            shared_bytes=balance["shared_reserved_bytes"],total_upper=balance["total_reserved_bytes"],
            expanded_record_bytes=len(b.canonical(self.x)),compact_record_bytes=len(b.canonical(self.wire)))

    def test_09_independent_verifier(self):
        with patch.object(c,"pack",side_effect=AssertionError("ENCODER_FORBIDDEN")),patch.object(ids,"build",side_effect=AssertionError("ID_PRODUCER_FORBIDDEN")):
            expanded=c.unpack(self.wire,self.manifest)
            packed=[dict(event=dict(event_id=row[2],ordinal=row[0],event_type="PARTIAL_VISUAL_CUE")) for row in self.mapping["rows"]]
            self.assertEqual(v.verify_event_ids(expanded["bindings"]["event_ids"],self.ex,packed),self.mapping["id_binding_digest"])

    def test_10_missing_reference(self):
        x=deepcopy(self.wire);del x["bindings"]["qualifications"]["main"]["files"]["result.json"]
        self.rejected("REFERENCE_RECONSTRUCTION_INVALID",self.reseal(x))

    def test_11_wrong_reference(self):
        x=deepcopy(self.wire);x["bindings"]["event_ids"]["expanded_digest"]="f"*64
        self.rejected("ID_REFERENCE_INVALID",self.reseal(x))

    def test_12_swapped_reference(self):
        x=deepcopy(self.wire);a=x["execution"]["binding"]["component_sources"]["indices"];a[0],a[1]=a[1],a[0]
        self.rejected("COMPONENT_REFERENCE_INVALID",self.reseal(x))

    def test_13_foreign_manifest(self):
        m=deepcopy(self.manifest);m[next(iter(m))]="0"*64
        self.rejected("COMPONENT_REFERENCE_INVALID",self.wire,m)

    def test_14_failure_shape(self):
        x=deepcopy(self.x);x["execution"]=None;x["status"]="NOT_EVALUABLE"
        x["failure"]=dict(phase="BINDINGS",ordinal=None,source_id=None,completed_events=0,error_class="S2OAError",
            code="NEUTRAL_BINDING_FAILURE",last_snapshot_digest=None,final=None)
        x=self.reseal(x);wire=c.pack(x,{})
        expanded=c.unpack(wire,{})
        self.assertEqual(expanded["failure"],x["failure"]);self.assertIsNone(expanded["execution"])
        self.assertIsNone(expanded["evaluation"])

    def test_15_new_qualification_chain(self):
        previous={**self.manifest,**self.old_delta["hashes"]};now={**previous,**self.pr["hashes"]}
        b.validate_compact_manifest(self.pr,previous,now)
        self.assertEqual(c.OLD_RESULT,"9ba20ce38d5c6f19f0f4e19efe00958bfe7e5bab5584ae4098dd56322f42fce8")
        for mode in ("old","new"):
            with self.subTest(mode=mode):
                p=deepcopy(previous);n=deepcopy(now)
                if mode=="old":p[next(iter(c.REPLACED))]="0"*64;code="COMPACT_QUAL_DELTA_INVALID"
                else:n["unexpected.py"]="0"*64;code="COMPACT_QUAL_CODE_INVALID"
                with self.assertRaises(r.S2OAError) as cm:b.validate_compact_manifest(self.pr,p,n)
                self.assertEqual(cm.exception.code,code)

    def test_16_closed_gates_and_collision(self):
        self.assertFalse(b.MAIN_GATE);self.assertFalse(r.MAIN_GATE);self.assertFalse(b.source.MAIN_GATE)
        x=deepcopy(self.wire);a=x["execution"]["binding"]["component_sources"]["indices"];a[1]=a[0]
        self.rejected("COMPONENT_REFERENCE_INVALID",self.reseal(x))


if __name__=="__main__":unittest.main()
