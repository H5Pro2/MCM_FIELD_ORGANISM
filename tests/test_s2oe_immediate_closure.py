"""Only new ledger and error handoff paths; no historical suite replay."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from dataclasses import asdict
from tests.test_s2oe_immediate_visual_input import fixture
from reports import run_immediate_visual_once as entry


class ClosureTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.raw,self.parent=fixture(self.root/"neutral-parent.json")
        self.directory=self.root/"output"
        self.binding=self.root/"binding.json"
        self.value=dict(version="s2oe.immediate-run-binding.v1",status="READY_REQUIRES_AUTHORIZATION",
            files={},artifacts=[],output_directory=str(self.directory),parent=asdict(self.parent),run_id="neutral-closure")
        self.binding.write_bytes(entry.p.canonical(self.value))

    def execute(self,fault=None):
        with patch.object(entry,"MAIN_GATE",True):
            entry.execute(self.binding,neutral=True,fault=fault)

    def read(self,name): return json.loads((self.directory/name).read_bytes())

    def test_01_regular_closure(self):
        self.execute()
        self.assertEqual("CLOSED",self.read("close.json")["status"])
        self.assertEqual("EVIDENCE_VALID",self.read("verification.json")["status"])
        self.assertEqual([],self.read("balance.json")["violations"])
        expected=len(self.binding.read_bytes())+len(self.raw)+sum(f.stat().st_size for f in self.directory.iterdir())
        self.assertEqual(expected,self.read("balance.json")["totals"]["total"])
        self.assertFalse(entry.control.MAIN_GATE)

    def check_failure(self,phase,count):
        def fault(current):
            if current==phase: raise entry.p.InputError("INJECTED_PRIMARY")
        with self.assertRaises(entry.p.InputError) as caught: self.execute(fault)
        self.assertEqual("INJECTED_PRIMARY",caught.exception.code)
        f=self.read("failure.json")
        self.assertEqual((phase,count),(f["last_completed_phase"],f["completed_events"]))
        self.assertEqual("INJECTED_PRIMARY",f["code"])
        self.assertFalse(f["evaluation_allowed"])
        self.assertFalse((self.directory/"evaluation.json").exists())
        self.assertFalse((self.directory/"verification.claim").exists())
        partial=self.read("partial.json")
        self.assertEqual(0,partial["field_calls"])
        self.assertFalse(entry.control.MAIN_GATE)
        return partial

    def test_02_before_formation(self):
        partial=self.check_failure("EMPTY_CUE_COMPLETE",1)
        self.assertEqual(1,len(partial["states"]))
        self.assertIsNone(partial["formation"])

    def test_03_after_formation(self):
        partial=self.check_failure("FORMATION_COMPLETE",2)
        self.assertEqual(2,len(partial["states"]))
        state=entry.control.wire.decode(partial["states"][1])
        self.assertEqual(1,state["generation"])
        self.assertIsNotNone(partial["formation"])
        self.assertEqual([],self.read("balance.json")["violations"])

    def test_04_budget_prestart(self):
        extra=self.root/"metadata.json";extra.write_bytes(b" "*65536)
        self.value["artifacts"]=[dict(path=str(extra),kind="metadata",sha256=entry.p.sha(extra.read_bytes()))]
        self.binding.write_bytes(entry.p.canonical(self.value))
        with self.assertRaises(entry.p.InputError) as caught:self.execute()
        self.assertEqual("BUDGET_EXCEEDED",caught.exception.code)
        self.assertIn("metadata",caught.exception.balance["violations"])
        self.assertFalse(self.directory.exists())
