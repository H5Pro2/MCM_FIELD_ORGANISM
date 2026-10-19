import unittest
from pathlib import Path
from tools import _s2tx_qualification_gate as gate

ROOT=Path(__file__).resolve().parents[1]
class GateTests(unittest.TestCase):
 def valid(self): return dict(status="QUALIFIED",test_ids=sorted(gate.REQUIRED),code_hashes=gate.code_hashes(ROOT))
 def test_complete_receipt_is_accepted(self): gate.authorize(ROOT,self.valid())
 def test_partial_ids_fail_closed(self):
  r=self.valid();r["test_ids"]=r["test_ids"][:-1]
  with self.assertRaisesRegex(gate.S2TXQualificationError,"QUALIFICATION_TEST_SET_INVALID"): gate.authorize(ROOT,r)
 def test_failed_status_fails_closed(self):
  r=self.valid();r["status"]="FAILED"
  with self.assertRaisesRegex(gate.S2TXQualificationError,"QUALIFICATION_STATUS_INVALID"): gate.authorize(ROOT,r)
 def test_code_hash_difference_fails_closed(self):
  r=self.valid();r["code_hashes"][next(iter(r["code_hashes"]))]="0"*64
  with self.assertRaisesRegex(gate.S2TXQualificationError,"QUALIFICATION_CODE_BINDING_INVALID"): gate.authorize(ROOT,r)
