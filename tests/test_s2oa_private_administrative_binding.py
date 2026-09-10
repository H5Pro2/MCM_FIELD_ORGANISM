"""Twenty neutral administrative checks. No source payloads or historical reads."""
import copy
import importlib.abc
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


class ImportBlock(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        allowed = {"tools._s2oa_private_administrative_binding","tools._s2oa_private_administrative_verification"}
        if fullname.startswith(("mcm_field_organism", "numpy")) or (fullname.startswith("tools._") and fullname not in allowed):
            raise AssertionError("SOURCE_OR_SYSTEM_IMPORT_FORBIDDEN")


sys.meta_path.insert(0,ImportBlock())
from tools import _s2oa_private_administrative_binding as b
from tools import _s2oa_private_administrative_verification as v


def fixture():
    ex = dict(execution_digest="neutral-root", sources=[dict(source_id=f"neutral-{i:02d}",
        event_id=f"e{i%28+1:02d}",time_binding=dict(start=i*480,end=i*480+480),
        recipe=dict(kind="SYNTHETIC_METADATA_ONLY"),payload_sha256="0"*64) for i in range(48)],
        events=[dict(event_id=f"e{i+1:02d}",ordinal=i+1,start=i*480) for i in range(28)],
        profiles=dict(profile="NEUTRAL"), environment=dict(build="NEUTRAL"),
        generators=dict(executed=False), source_hashes={},contract_sha256="1"*64)
    blobs = {k:b.canonical({}) for k in b.ARCHIVE}
    blobs["execution"] = b.canonical(ex)
    blobs["evaluation"] = b.canonical(dict(cases=[dict(prediction="NEUTRAL")]))
    return blobs


class AdministrativeTests(unittest.TestCase):
    def setUp(self):
        original = Path.open
        def guarded(path,*args,**kwargs):
            resolved = path.resolve()
            if resolved.is_relative_to(b.ROOT/"reports"):
                raise AssertionError("HISTORICAL_DATA_ACCESS_FORBIDDEN")
            return original(path,*args,**kwargs)
        self.guard = patch.object(Path,"open",guarded)
        self.guard.start(); self.addCleanup(self.guard.stop)
        self.blobs = fixture()
        self.ex,self.ev = b.compact(self.blobs)

    def rejects(self, code, call):
        with self.assertRaises(b.S2OAAdminError) as caught:
            call()
        self.assertEqual(caught.exception.code,code)

    def check(self):
        v.verify_references(self.ex,self.ev,self.blobs)

    def both_budgets(self, metadata, sources, reserves=None, other=0):
        reserves = b.RESERVES if reserves is None else reserves
        self.assertEqual(b.ledger(metadata,sources,reserves,other),v.check_totals(metadata,sources,reserves,other))

    def test_01_valid_full_references(self):
        self.check()
        self.assertEqual(len(self.ex["source_refs"]),48)
        self.assertEqual(len(self.ex["event_refs"]),28)

    def test_02_missing_reference(self):
        del self.ex["source_refs"][0]["ref"]
        self.rejects("SOURCE_REFERENCE_INVALID",self.check)

    def test_03_false_digest(self):
        self.ex["source_refs"][0]["ref"]["value_digest"] = "f"*64
        self.rejects("REFERENCE_DIGEST_INVALID",self.check)

    def test_04_swapped_sources(self):
        a = self.ex["source_refs"]
        a[0],a[1] = a[1],a[0]
        self.rejects("REFERENCE_TARGET_INVALID",self.check)

    def test_05_swapped_events(self):
        a = self.ex["event_refs"]
        a[0],a[1] = a[1],a[0]
        self.rejects("REFERENCE_TARGET_INVALID",self.check)

    def test_06_profile_changed(self):
        old = json.loads(self.blobs["execution"])
        old["profiles"]["profile"] = "OTHER"
        self.blobs["execution"] = b.canonical(old)
        self.rejects("REFERENCE_DIGEST_INVALID",self.check)

    def test_07_time_changed(self):
        old = json.loads(self.blobs["execution"])
        old["sources"][0]["time_binding"]["start"] += 1
        self.blobs["execution"] = b.canonical(old)
        self.rejects("REFERENCE_DIGEST_INVALID",self.check)

    def test_08_evaluation_changed(self):
        self.blobs["evaluation"] = b.canonical(dict(cases=[dict(prediction="OTHER")]))
        self.rejects("REFERENCE_DIGEST_INVALID",self.check)

    def test_09_archive_closure(self):
        del self.blobs["preregistration"]
        self.rejects("ARCHIVE_CLOSURE_INVALID",self.check)

    def test_10_archive_hash(self):
        manifest = {k:dict(path=p,sha256=h,bytes=len(self.blobs[k])) for k,(p,h) in b.ARCHIVE.items()}
        self.rejects("ARCHIVE_HASH_INVALID",lambda:v.check_archive_manifest(manifest,self.blobs))

    def test_11_metadata_single(self):
        self.both_budgets({"a":65536},{})
        for fn in (b.ledger,v.check_totals):
            with self.subTest(fn=fn.__name__):
                self.rejects("METADATA_ITEM_LIMIT",lambda:fn({"a":65537},{},b.RESERVES))

    def test_12_metadata_joint(self):
        self.both_budgets({"a":32768,"b":32768},{})
        for fn in (b.ledger,v.check_totals):
            with self.subTest(fn=fn.__name__):
                self.rejects("METADATA_TOTAL_LIMIT",lambda:fn({"a":32768,"b":32769},{},b.RESERVES))

    def test_13_source_single(self):
        self.both_budgets({}, {"a":174080})
        for fn in (b.ledger,v.check_totals):
            with self.subTest(fn=fn.__name__):
                self.rejects("SOURCES_ITEM_LIMIT",lambda:fn({}, {"a":174081},b.RESERVES))

    def test_14_source_joint(self):
        self.both_budgets({}, {"a":87040,"b":87040})
        for fn in (b.ledger,v.check_totals):
            with self.subTest(fn=fn.__name__):
                self.rejects("SOURCES_TOTAL_LIMIT",lambda:fn({}, {"a":87040,"b":87041},b.RESERVES))

    def test_15_nj_reserve(self):
        b.reserve_items("nj",[1024]*22)
        self.rejects("RESERVE_ITEM_LIMIT",lambda:b.reserve_items("nj",[1025]))
        self.rejects("RESERVE_COUNT_LIMIT",lambda:b.reserve_items("nj",[1]*23))
        for fn in (b.ledger,v.check_totals):
            with self.subTest(fn=fn.__name__):
                self.rejects("NJ_RESERVE_LIMIT",lambda:fn({}, {},{**b.RESERVES,"nj":22529}))

    def test_16_formation_reserve(self):
        b.reserve_items("formations",[1536]*20)
        self.rejects("RESERVE_ITEM_LIMIT",lambda:b.reserve_items("formations",[1537]))
        self.rejects("RESERVE_COUNT_LIMIT",lambda:b.reserve_items("formations",[1]*21))
        for fn in (b.ledger,v.check_totals):
            with self.subTest(fn=fn.__name__):
                self.rejects("FORMATIONS_RESERVE_LIMIT",lambda:fn({}, {},{**b.RESERVES,"formations":30721}))

    def test_17_generation_reserve(self):
        b.reserve_items("generations",[1536]*20)
        self.rejects("RESERVE_ITEM_LIMIT",lambda:b.reserve_items("generations",[1537]))
        self.rejects("RESERVE_COUNT_LIMIT",lambda:b.reserve_items("generations",[1]*21))
        for fn in (b.ledger,v.check_totals):
            with self.subTest(fn=fn.__name__):
                self.rejects("GENERATIONS_RESERVE_LIMIT",lambda:fn({}, {},{**b.RESERVES,"generations":30721}))

    def test_18_shared_limit(self):
        b.shared_total_check([174080,22528,30720,30720,4096])
        self.rejects("SHARED_LIMIT",lambda:b.shared_total_check([174080,22528,30720,30720,4097]))
        self.both_budgets({}, {"all_referenced_bytes":174080})
        self.assertEqual(b.ledger({}, {"all_referenced_bytes":174080})["shared_remaining_bytes"],4096)

    def test_19_total_limit(self):
        other = 4194304-65536-174080-sum(b.RESERVES.values())
        self.both_budgets({"all":65536},{"all":174080},other=other)
        for fn in (b.ledger,v.check_totals):
            with self.subTest(fn=fn.__name__):
                self.rejects("TOTAL_LIMIT",lambda:fn({"all":65536},{"all":174080},b.RESERVES,other+1))

    def test_20_immutability_gates_and_publication(self):
        before = copy.deepcopy((self.ex,self.ev,self.blobs))
        self.check()
        self.assertEqual(before,(self.ex,self.ev,self.blobs))
        self.assertIs(b.MAIN_GATE,False)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"binding.json"
            value = dict(execution=self.ex,evaluation=self.ev)
            b.publish(path,value)
            with self.assertRaises(FileExistsError):
                b.publish(path,value)
            self.assertEqual(json.loads(path.read_bytes()),value)
        self.assertFalse(any(n.startswith("mcm_field_organism") for n in sys.modules))


if __name__ == "__main__":
    unittest.main()
