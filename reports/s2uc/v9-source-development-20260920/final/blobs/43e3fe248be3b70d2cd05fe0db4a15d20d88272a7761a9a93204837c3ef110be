"""S2-UC common envelope accounting; success and failure are alternatives."""
from __future__ import annotations

from tools import _s2ty_resource_ledger as base


LIMITS = {"metadata": 65_536, "shared": 262_144, "record": 262_144, "verification": 262_144, "total": 4_194_304}
RESERVES = {"metadata": 65_536, "active_bindings": 131_072, "success_record": 245_760, "failure_record": 245_760, "verification": 131_072, "terminal": 16_384}


def ledger(*, manifest_bytes: int, success_record_bytes: int, failure_record_bytes: int, verification_bytes: int,
           terminal_bytes: int, error_evidence_bytes: int = 0, active_binding_bytes: int = 0) -> dict[str, object]:
    values = (manifest_bytes, success_record_bytes, failure_record_bytes, verification_bytes, terminal_bytes, error_evidence_bytes, active_binding_bytes)
    if any(type(value) is not int or value < 0 for value in values):
        raise ValueError("LEDGER_VALUE_INVALID")
    branches = {}
    for branch, record, error_bytes in (("success", success_record_bytes, 0), ("failure", failure_record_bytes, error_evidence_bytes)):
        contributions = {"metadata": manifest_bytes, "shared": terminal_bytes + error_bytes + active_binding_bytes, "record": record, "verification": verification_bytes}
        total = sum(contributions.values())
        violations = [key for key, limit in LIMITS.items() if key != "total" and contributions[key] > limit]
        if total > LIMITS["total"]:
            violations.append("total")
        branches[branch] = {"contributions": contributions, "total_bytes": total, "violations": violations}
        record_reserve = RESERVES[f"{branch}_record"]
        reserve_violations = []
        if record > record_reserve: reserve_violations.append("record_reserve")
        if verification_bytes > RESERVES["verification"]: reserve_violations.append("verification_reserve")
        if terminal_bytes > RESERVES["terminal"]: reserve_violations.append("terminal_reserve")
        if error_bytes > RESERVES["terminal"]: reserve_violations.append("error_evidence_reserve")
        if active_binding_bytes > RESERVES["active_bindings"]: reserve_violations.append("active_binding_reserve")
        branches[branch]["reserve_violations"] = reserve_violations
    return {"limits": LIMITS, "reserves": RESERVES, "branches": branches}


def planned(manifest_bytes: int) -> dict[str, object]:
    return ledger(manifest_bytes=manifest_bytes, success_record_bytes=RESERVES["success_record"], failure_record_bytes=RESERVES["failure_record"], verification_bytes=RESERVES["verification"], terminal_bytes=RESERVES["terminal"], error_evidence_bytes=RESERVES["terminal"], active_binding_bytes=RESERVES["active_bindings"])
