"""Fail-closed qualification inventory for any future S2TX start."""
from __future__ import annotations
import hashlib
from pathlib import Path
REQUIRED=frozenset({"exact_confirm_recent","reverse","partial_single_value","incomplete","ambiguous","hint_readonly"})
CODE=("tools/_s2tx_recency_confirmation.py","tools/_s2tx_source_schedule.py","tools/_s2tx_run.py","tools/_s2tx_verification.py")
class S2TXQualificationError(ValueError): pass
def code_hashes(root:Path): return {name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in CODE}
def authorize(root:Path,receipt:dict):
 if set(receipt.get("test_ids",()))!=REQUIRED: raise S2TXQualificationError("QUALIFICATION_TEST_SET_INVALID")
 if receipt.get("code_hashes")!=code_hashes(root): raise S2TXQualificationError("QUALIFICATION_CODE_BINDING_INVALID")
 if receipt.get("status")!="QUALIFIED": raise S2TXQualificationError("QUALIFICATION_STATUS_INVALID")
