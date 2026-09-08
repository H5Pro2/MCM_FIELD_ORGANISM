"""Administrative admission only; historical tests and runtime are not run."""
from copy import deepcopy
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
from tools import _s2nr_private_qualification_binding as binding

run=binding.run
OUT=Path(os.environ["S2NR_CONNECTION_QUAL_DIR"])


class QualificationConnectionTests(unittest.TestCase):
    def setUp(self):
        self.bundle=json.loads((run.ROOT/binding.BUNDLE).read_bytes())
        self.guards=[]
        for owner,name in ((run.Materializer,"run_once"),(run,"execute_once"),(run,"load_execution"),
            (run.runtime.MaskRuntimeComparison,"__init__"),(run.source,"generators")):
            p=patch.object(owner,name,side_effect=AssertionError("runtime/materialization forbidden"))
            self.guards.append(p.start())
            self.addCleanup(p.stop)

    def tearDown(self):
        for p in self.guards:
            p.assert_not_called()
        self.assertFalse(run.MAIN_GATE or run.runtime.MAIN_GATE or run.nn.MAIN_GATE or run.ng.MAIN_GATE)

    def admission(self,bundle):
        # Synthetic receipt tests the loader boundary, not a claim of prior success.
        receipt=run.sealed(dict(status="S2NR_QUALIFICATION_CONNECTION_QUALIFIED",run_id=binding.QUAL_ID,
            passed_tests=4,expected_tests=4,exit_code=0,unittest_calls=1,
            qualification_digest=bundle["qualification_digest"],hashes_before=binding.watched(),
            hashes_after=binding.watched()),"result_digest")
        original=binding.read_json
        def read(path,limit=65536):
            if path==binding.BUNDLE:
                return deepcopy(bundle)
            if path=="reports/s2nr/"+binding.QUAL_ID+"/result.json":
                return deepcopy(receipt)
            return original(path,limit)
        with patch.object(binding,"read_json",side_effect=read):
            return binding.require_combined_qualification()

    def expect_code(self,bundle,code):
        before=run.digest(bundle)
        with self.assertRaises(run.S2NRRunError) as error:
            self.admission(bundle)
        self.assertIs(type(error.exception),run.S2NRRunError)
        self.assertEqual(code,error.exception.code)
        self.assertEqual(before,run.digest(bundle))
        run.ng.ne.atomic_write(OUT/(self._testMethodName+".json"),dict(error_class=type(error.exception).__name__,
            code=error.exception.code,input_unchanged=True,synthetic_administrative_receipt=True,
            input_digest=bundle["qualification_digest"]))

    def test_01_complete_combined_evidence_accepted(self):
        before=run.digest(self.bundle)
        self.assertEqual(self.bundle["qualification_digest"],self.admission(self.bundle))
        self.assertEqual(before,run.digest(self.bundle))
        self.assertEqual([16,11,3],[p["covered_tests"] for p in self.bundle["parts"]])
        self.assertEqual("NOT_QUALIFIED",self.bundle["parts"][1]["status"])
        self.assertTrue(self.bundle["no_new_full_test_run"])
        self.assertFalse(self.bundle["administrative_connection"]["historically_tested"])
        run.ng.ne.atomic_write(OUT/"accepted.json",dict(qualification_digest=self.bundle["qualification_digest"],
            accepted=True,input_unchanged=True,synthetic_administrative_receipt=True,
            forbidden_calls=0,gate_after=False))

    def test_02_missing_part_rejected(self):
        self.bundle["parts"].pop()
        bad=run.sealed({k:v for k,v in self.bundle.items() if k!="qualification_digest"},"qualification_digest")
        self.expect_code(bad,"QUALIFICATION_PART_MISSING")

    def test_03_incorrect_part_digest_rejected(self):
        self.bundle["parts"][1]["result_digest"]="0"*64
        bad=run.sealed({k:v for k,v in self.bundle.items() if k!="qualification_digest"},"qualification_digest")
        self.expect_code(bad,"QUALIFICATION_PART_DIGEST_INVALID")

    def test_04_unapproved_source_difference_rejected(self):
        self.bundle["current_sources"]["tools/_s2nr_private_runtime_binding.py"]="0"*64
        bad=run.sealed({k:v for k,v in self.bundle.items() if k!="qualification_digest"},"qualification_digest")
        self.expect_code(bad,"QUALIFICATION_SOURCE_MISMATCH")
