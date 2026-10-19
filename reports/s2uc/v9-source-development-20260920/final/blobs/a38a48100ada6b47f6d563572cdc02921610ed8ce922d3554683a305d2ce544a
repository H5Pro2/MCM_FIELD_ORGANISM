"""Standalone V7 accounting. No starter admission, publication or source work.

measure() audits an explicitly bounded directory containing the files being
accounted for. Assignments are caller-owned inventory, not claims from a report.
Every file in that directory must be assigned; no implicit exclusion patterns.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from types import MappingProxyType


CONTRACT_ID = "s2uc.resources.separate-code-artifacts.v7"
VERSION = "s2uc.resource-ledger.v7"
LIMITS = MappingProxyType({
    "code": 655_360, "metadata": 65_536, "static_shared": 196_608,
    "shared": 262_144, "record": 262_144, "verification": 262_144,
    "error": 16_384, "terminal": 16_384, "minimal": 16_384,
    "staging": 245_760, "total": 4_194_304,
})
RESERVES = MappingProxyType({"record": 245_760, "verification": 131_072})
CATEGORIES = ("code", "metadata", "static_shared", "record", "verification",
              "error", "terminal", "minimal", "staging")
PHASES = ("success", "failure_before_publication", "failure_after_publication")
_SHARED = ("static_shared", "error", "terminal", "minimal")
_SINGLE_FILES = ("record", "verification", "error", "terminal", "minimal", "staging")


class V7LedgerError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def _need(condition, code):
    if not condition:
        raise V7LedgerError(code)


def _total_exceeded(total, ceiling):
    """Pure arithmetic seam for isolated tests, never a public contract override."""
    return total > ceiling


def _account(phase, amounts):
    _need(phase in PHASES, "V7_PHASE_INVALID")
    _need(type(amounts) is dict and set(amounts) == set(CATEGORIES), "V7_CATEGORIES_INVALID")
    _need(all(type(n) is int and n >= 0 for n in amounts.values()), "V7_SIZE_INVALID")
    totals = {key: amounts[key] for key in ("code", "metadata", "record", "verification", "staging")}
    totals["shared"] = sum(amounts[key] for key in _SHARED)
    total = sum(totals.values())
    violations = [f"limit:{key}" for key in CATEGORIES if amounts[key] > LIMITS[key]]
    if totals["shared"] > LIMITS["shared"]:
        violations.append("limit:shared")
    violations.extend(f"reserve:{key}" for key in RESERVES if amounts[key] > RESERVES[key])
    if _total_exceeded(total, LIMITS["total"]):
        violations.append("limit:total")
    if phase == "success" and (amounts["error"] or amounts["minimal"]):
        violations.append("phase:unexpected_error_evidence")
    if phase == "failure_before_publication" and (amounts["record"] or amounts["verification"]):
        violations.append("phase:unexpected_published_record_or_verification")
    return {"categories": dict(amounts), "main_accounts": totals, "total_bytes": total,
            "violations": violations, "within_limits": not violations}


def reserve(phase, amounts):
    """Prospective allocations only; never evidence of actual file sizes."""
    return {"version": VERSION, "contract_id": CONTRACT_ID, "kind": "reservation",
            "phase": phase, "limits": dict(LIMITS), "reserves": dict(RESERVES),
            "reserved": _account(phase, amounts)}


def measure(root, assignments, *, phase):
    """Measure actual files and reject missing, unassigned or aliased paths.

    assignments: list of {path: canonical relative POSIX path, category: name}.
    This module proves completeness inside root, not project import closure.
    The latter remains the responsibility of a future V7 admission integration.
    """
    root = Path(root)
    _need(root.is_dir() and not root.is_symlink(), "V7_ROOT_INVALID")
    root = root.resolve()
    _need(type(assignments) is list, "V7_ASSIGNMENTS_INVALID")
    expected = {}
    for row in assignments:
        _need(type(row) is dict and set(row) == {"path", "category"}, "V7_ASSIGNMENTS_INVALID")
        name, category = row["path"], row["category"]
        _need(type(category) is str and category in CATEGORIES, "V7_CATEGORY_UNKNOWN")
        _need(type(name) is str and bool(name), "V7_PATH_INVALID")
        path = Path(name)
        _need(not path.is_absolute() and ".." not in path.parts and path.as_posix() == name,
              "V7_PATH_INVALID")
        _need(name not in expected, "V7_DUPLICATE_FILE")
        _need((root / path).resolve().is_relative_to(root), "V7_PATH_INVALID")
        expected[name] = category
    actual = {}
    identities = set()
    for path in root.rglob("*"):
        _need(not path.is_symlink() and not path.is_junction(), "V7_FILE_ALIAS")
        if path.is_dir():
            continue
        _need(path.is_file(), "V7_FILE_INVALID")
        stat = path.stat()
        identity = (stat.st_dev, stat.st_ino)
        _need(identity not in identities, "V7_FILE_ALIAS")
        identities.add(identity)
        actual[path.relative_to(root).as_posix()] = path
    _need(not (expected.keys() - actual.keys()), "V7_FILE_MISSING")
    _need(not (actual.keys() - expected.keys()), "V7_FILE_UNASSIGNED")
    counts = {key: list(expected.values()).count(key) for key in CATEGORIES}
    _need(all(counts[key] <= 1 for key in _SINGLE_FILES), "V7_MULTIPLE_SINGLE_ARTIFACTS")
    _need(phase in PHASES, "V7_PHASE_INVALID")
    required = {"code", "metadata", "static_shared"}
    if phase == "success":
        required |= {"record", "verification", "terminal"}
        _need(not counts["error"] and not counts["minimal"], "V7_PHASE_FILES_INVALID")
    else:
        required.add("error")
        _need(bool(counts["terminal"] or counts["minimal"]), "V7_PHASE_FILES_MISSING")
        if phase == "failure_after_publication":
            required.add("record")
        else:
            _need(not counts["record"] and not counts["verification"], "V7_PHASE_FILES_INVALID")
    _need(all(counts[key] for key in required), "V7_PHASE_FILES_MISSING")
    files = []
    amounts = dict.fromkeys(CATEGORIES, 0)
    for name, path in sorted(actual.items()):
        # Hash and count the same bytes; don't trust caller sizes or totals.
        with path.open("rb") as stream:
            digest = hashlib.sha256()
            size = 0
            while chunk := stream.read(65_536):
                digest.update(chunk)
                size += len(chunk)
        category = expected[name]
        files.append({"path": name, "category": category, "bytes": size, "sha256": digest.hexdigest()})
        amounts[category] += size
    return {"version": VERSION, "contract_id": CONTRACT_ID, "kind": "actual",
            "phase": phase, "limits": dict(LIMITS), "reserves": dict(RESERVES),
            "files": files, "actual": _account(phase, amounts)}


def _same_typed(left, right):
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return left.keys() == right.keys() and all(_same_typed(left[k], right[k]) for k in left)
    if type(left) is list:
        return len(left) == len(right) and all(_same_typed(a, b) for a, b in zip(left, right))
    return left == right


def verify(root, assignments, claimed, *, phase):
    """Recompute against disk and trusted assignments, then require all budgets."""
    measured = measure(root, assignments, phase=phase)
    _need(_same_typed(claimed, measured), "V7_LEDGER_MISMATCH")
    _need(measured["actual"]["within_limits"], "V7_BUDGET_EXCEEDED")
    return measured
