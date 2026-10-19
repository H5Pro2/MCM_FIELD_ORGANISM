"""Prospective V9 revision: only code changes; all artifact limits remain fixed."""
from types import MappingProxyType
from tools import _s2uc_resource_contract_v7 as v7

CONTRACT_ID = "s2uc.resources.separate-code-artifacts.v9"
VERSION = "s2uc.resource-ledger.v9"
LIMITS = MappingProxyType({**v7.LIMITS, "code": 851_968})
RESERVES = v7.RESERVES
CATEGORIES = v7.CATEGORIES


def account(phase, amounts):
    result = v7._account(phase, amounts)
    violations = [v for v in result["violations"] if v != "limit:code"]
    if amounts["code"] > LIMITS["code"]:
        violations.insert(0, "limit:code")
    return {**result, "violations": violations, "within_limits": not violations}


def reserve(phase, amounts):
    return {"version": VERSION, "contract_id": CONTRACT_ID, "kind": "reservation", "phase": phase,
            "limits": dict(LIMITS), "reserves": dict(RESERVES), "reserved": account(phase, amounts)}
