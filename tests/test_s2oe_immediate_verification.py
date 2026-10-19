"""New offline verification only; prior presentation tests are not rerun."""
from copy import deepcopy
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tests.test_s2oe_immediate_visual_input import fixture
from tools import _s2oe_immediate_visual_control as c
from tools import _s2oe_immediate_visual_verification as v


class VerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.raw,cls.binding=fixture(Path(cls.temp.name)/"neutral-parent.json")
        cls.record=c.run(c.source.extract(cls.raw,cls.binding),cls.binding,run_id="neutral-verification",neutral=True)
        Path(os.environ["IMMEDIATE_QUAL_DIR"],"neutral-record.json").write_bytes(c.source.canonical(cls.record))

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def verify(self,record=None):
        with patch.object(c.nn.ng.memory,"advance_s2jv_atomic",side_effect=AssertionError("FORMATION_FORBIDDEN")),\
             patch.object(c.nn.ng.visual,"form_partial_cue_retrieval_336",side_effect=AssertionError("RETRIEVAL_FORBIDDEN")):
            return v.verify(self.record if record is None else record,self.binding,self.raw,"neutral-verification")

    def test_01_native_proof_readonly(self):
        before=c.source.canonical(self.record)
        proof=self.verify()
        self.assertEqual("EVIDENCE_VALID",proof["status"])
        self.assertTrue(proof["evaluation_allowed"])
        self.assertEqual(before,c.source.canonical(self.record))

    def test_02_parent_tampered(self):
        with self.assertRaises(c.source.InputError):
            v.verify(self.record,self.binding,self.raw+b" ","neutral-verification")

    def test_03_event_order_tampered(self):
        record=deepcopy(self.record);record["scans"].reverse()
        with self.assertRaises(c.source.InputError): self.verify(record)

    def test_04_presentation_tampered(self):
        record=deepcopy(self.record);record["presentations"][2]["visual_window"]=[14,15]
        with self.assertRaises(c.source.InputError): self.verify(record)

    def test_05_formation_link_tampered(self):
        record=deepcopy(self.record);record["formation_context"][0]="0"*64
        with self.assertRaises(c.source.InputError): self.verify(record)

    def test_06_evaluation_gate(self):
        with self.assertRaises(c.source.InputError): v.evaluate(self.record,dict(evaluation_allowed=False))
        proof=self.verify()
        evaluation=v.evaluate(self.record,proof)
        self.assertEqual(2,len(evaluation["decisions"]))
        self.assertTrue(all(x["agrees"] for x in evaluation["decisions"]))

    def test_07_entry_gate(self):
        from reports import run_immediate_visual_once as entry
        with self.assertRaises(c.source.InputError) as caught:
            entry.execute("never-opened.json")
        self.assertEqual("MAIN_GATE_CLOSED",caught.exception.code)
