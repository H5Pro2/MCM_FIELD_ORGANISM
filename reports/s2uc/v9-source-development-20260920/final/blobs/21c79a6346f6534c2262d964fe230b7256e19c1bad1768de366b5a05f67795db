"""Isolated neutral-record publication, never source production or starter admission.

Single writer owns a freshly created directory. One fixed staging name, atomic
rename on the same filesystem, no crash/power-loss recovery claim. Verification
and evaluation are candidate evidence until a successful terminal closes it.
"""
from __future__ import annotations

import os
from pathlib import Path

from tools import _s2uc_prestart_v7 as prestart
from tools import _s2uc_inventory_v7 as inventory
from tools import _s2uc_resource_contract_v7 as ledger
from tools import _s2uc_record_codec as codec
from tools import _s2uc_verification as verification
from tools import _s2uc_evaluation as evaluation

VERSION = "s2uc.neutral-publication.v7"
STAGING = "publication.tmp"


def _error(exc):
    return str(getattr(exc, "code", None) or str(exc) or type(exc).__name__)


def _read(path):
    return path.read_bytes()


def _write(path, data):
    with path.open("xb") as stream:
        if stream.write(data) != len(data):
            raise OSError("V7_SHORT_WRITE")
        stream.flush()
        os.fsync(stream.fileno())


class _Publication:
    limits, reserves = ledger.LIMITS, ledger.RESERVES
    account = staticmethod(ledger._account)
    version, proof_version = VERSION, "s2uc.verification-evaluation.v7"
    def __init__(self, binding_path, directory):
        self.path = Path(binding_path)
        self.directory = Path(directory)
        self.initial = prestart.validate(self.path)
        value = prestart._json(self.path.read_bytes())
        ledger._need(value["evidence_kind"] == "synthetic-development", "V7_NEUTRAL_SCOPE_REQUIRED")
        self.manifest = prestart._json((self.path.parent / "manifest.json").read_bytes())
        self.reset()

    def reset(self):
        self.primary = None
        self.issues = []
        self.phase = "RECORD_PREFLIGHT"
        self.candidate = None
        self.cleanup_observations = []

    def check_record(self, record):
        ledger._need(record.get("version") == "s2uc.neutral-connection.v1" and "source_completion" not in record
                     and all("materialization" not in e for s in record["stories"] for e in s["events"]),
                     "V7_NEUTRAL_RECORD_REQUIRED")

    def verify_record(self, record):
        return verification.verify(record, self.manifest) if self.primary is None else verification.verify_failure(record, self.manifest)

    def snapshot(self):
        """Measure all present bytes. Unknown/unreadable entries prevent success."""
        amounts = dict.fromkeys(ledger.CATEGORIES, 0)
        inputs, results, problems = [], [], []
        identities = set()
        unchanged = True
        expected = [(inventory.ROOT, r, "code") for r in self.initial["inventory"]["files"]]
        expected += [(inventory.ROOT if r["namespace"] == "project" else self.path.parent, r, r["category"])
                     for r in self.initial["prestart_artifacts"].values()]
        expected.append((self.path.parent, self.initial["binding"], "metadata"))
        for root, ref, category in expected:
            try:
                actual, _, identity = inventory.read_file(root, ref["path"])
                unchanged &= all(actual[key] == ref[key] for key in ("path", "bytes", "sha256"))
                ledger._need(identity not in identities, "V7_FILE_ALIAS")
                identities.add(identity)
                amounts[category] += actual["bytes"]
                inputs.append({**actual, "category": category, "root": str(root)})
            except Exception as exc:
                unchanged = False
                problems.append({"path": ref["path"], "error": _error(exc)})
        unknown_bytes = 0
        for path in sorted(self.directory.rglob("*")):
            name = path.relative_to(self.directory).as_posix()
            category = prestart.RESULT_FILES.get(name)
            if path.is_dir() and not path.is_symlink() and not path.is_junction():
                problems.append({"path": name, "error": "V7_UNREGISTERED_DIRECTORY"})
                continue
            try:
                ref, _, identity = inventory.read_file(self.directory, name)
                ledger._need(identity not in identities, "V7_FILE_ALIAS")
                identities.add(identity)
            except Exception as exc:
                # Retain a measurable file size even if its contents cannot be read.
                size = path.stat().st_size if path.is_file() else None
                ref = {"path": name, "bytes": size, "sha256": None}
                problems.append({"path": name, "error": _error(exc)})
            results.append({**ref, "category": category})
            if category is None:
                unknown_bytes += ref["bytes"] or 0
                problems.append({"path": name, "error": "V7_UNREGISTERED_RESULT"})
            else:
                amounts[category] += ref["bytes"] or 0
        phase = "failure_after_publication" if any(r["path"] == "record.json" for r in results) else "failure_before_publication"
        actual = self.account(phase, amounts)
        return {"version": self.version, "prestart_binding": self.initial["binding"],
                "prestart_unchanged": bool(unchanged), "inputs": inputs, "result_inventory": results,
                "actual": actual, "reservations": self.initial["budget"]["reservations"],
                "unclassified_bytes": unknown_bytes, "observed_total_bytes": actual["total_bytes"] + unknown_bytes,
                "accounting_complete": unchanged and not problems, "inspection_errors": problems}

    def atomic(self, name, data):
        category = prestart.RESULT_FILES[name]
        limit = min(self.limits[category], self.reserves.get(category, self.limits[category]))
        ledger._need(len(data) <= limit and len(data) <= self.limits["staging"], "V7_PUBLICATION_BUDGET_EXCEEDED")
        target, stage = self.directory / name, self.directory / STAGING
        ledger._need(not stage.exists() and not stage.is_symlink(), "V7_STAGING_PRESENT")
        ledger._need(not target.exists() and not target.is_symlink(), "V7_RESULT_ALREADY_EXISTS")
        measured = self.snapshot()
        ledger._need(measured["accounting_complete"], "V7_PRESTART_OR_RESULT_CHANGED")
        amounts = measured["actual"]["categories"]
        # Transient coexistence is counted before writing, not only after rename.
        for addition in ("staging", category):
            projected = {**amounts, addition: amounts[addition] + len(data)}
            phase = "failure_after_publication" if projected["record"] else "failure_before_publication"
            ledger._need(self.account(phase, projected)["within_limits"], "V7_PUBLICATION_BUDGET_EXCEEDED")
        _write(stage, data)
        # Recheck after writing; short/corrupt writes must never be published.
        ledger._need(_read(stage) == data, "V7_STAGING_BYTES_CHANGED")
        os.replace(stage, target)
        ledger._need(_read(target) == data, "V7_PUBLISHED_BYTES_CHANGED")

    def cleanup(self):
        try:
            stage = self.directory / STAGING
            if stage.exists() or stage.is_symlink():
                ref, _, _ = inventory.read_file(self.directory, STAGING)
                self.cleanup_observations.append(ref)
                stage.unlink()
        except Exception as exc:
            self.issues.append({"phase": "STAGING_CLEANUP", "error": _error(exc)})

    def references(self):
        return {r["path"]: {k: r[k] for k in ("path", "bytes", "sha256")}
                for r in self.snapshot()["result_inventory"]}

    def receipt(self, status):
        refs = self.references()
        return {"version": self.version, "status": status, "scope": "NEUTRAL_DEVELOPMENT_ONLY",
                "prestart_binding": self.initial["binding"], "primary_error": self.primary,
                "phase": self.phase, "candidate_record": self.candidate, "progress": getattr(self, "progress", None),
                "record": refs.get("record.json"), "verification": refs.get("verification.json"),
                "evaluation_allowed": self.primary is None,
                "authority": "invalidated by any error, minimal, staging or integrity failure",
                "secondary_errors": list(self.issues)}

    def failure(self, exc=None):
        if exc is not None:
            self.primary = self.primary or _error(exc)
            self.issues.append({"phase": self.phase, "error": _error(exc)})
        self.cleanup()
        def attempt(name, status):
            try:
                self.atomic(name, prestart.canonical(self.receipt(status)))
                return True
            except Exception as error:
                self.issues.append({"phase": name, "error": _error(error)})
                self.cleanup()
                return False
        attempt("error.json", "NOT_EVALUABLE")
        if not attempt("terminal.json", "NOT_EVALUABLE"):
            attempt("terminal-minimal.json", "NOT_EVALUABLE")
        return self.finish()

    def finish(self):
        measured = self.snapshot()
        names = {r["path"] for r in measured["result_inventory"]}
        refs = self.references()
        success = False
        try:
            terminal = prestart._json(_read(self.directory / "terminal.json"))
            proof = prestart._json(_read(self.directory / "verification.json"))
            success = (self.primary is None and measured["accounting_complete"] and measured["actual"]["within_limits"]
                       and names == {"record.json", "verification.json", "terminal.json"}
                       and terminal["status"] == "CLOSED_NEUTRAL_VERIFIED"
                       and terminal["record"] == refs["record.json"]
                       and terminal["verification"] == refs["verification.json"]
                       and proof["record"] == refs["record.json"])
        except Exception:
            pass
        missing = []
        if not success:
            for options in (("error.json",), ("terminal.json", "terminal-minimal.json")):
                valid = False
                for name in options:
                    try:
                        value = prestart._json(_read(self.directory / name))
                        valid |= value.get("status") == "NOT_EVALUABLE" and value.get("primary_error") == self.primary
                    except Exception:
                        pass
                if not valid:
                    missing.append(" or ".join(options))
        return {**measured, "status": "CLOSED_NEUTRAL_VERIFIED" if success else "NOT_EVALUABLE",
                "primary_error": self.primary, "secondary_errors": self.issues,
                "staging_cleanup_observations": self.cleanup_observations,
                "missing_durable_evidence": missing, "evaluation_allowed": success,
                "evaluation": proof.get("evaluation") if success else None}


def audit(binding_path, directory):
    """Read-only byte inventory; no caller-provided categories or source supplier."""
    publication = _Publication(binding_path, directory)
    ledger._need(publication.directory.is_dir(), "V7_OUTPUT_MISSING")
    return publication.snapshot()


def publish_neutral(record_bytes, binding_path, directory):
    """Accept already serialized neutral connection bytes, never a callable source."""
    directory = Path(directory)
    ledger._need(not directory.exists() and not directory.is_symlink(), "V7_OUTPUT_ALREADY_EXISTS")
    ledger._need(type(record_bytes) is bytes, "V7_RECORD_BYTES_REQUIRED")
    publication = _Publication(binding_path, directory)
    ledger._need(not directory.resolve().is_relative_to(Path(binding_path).parent.resolve()), "V7_OUTPUT_INSIDE_PRESTART")
    directory.mkdir()  # Exclusive creation; an existing folder is never modified.
    return _finish_record(publication, record_bytes)


def _finish_record(publication, record_bytes):
    directory = publication.directory
    try:
        publication.candidate = {"bytes": len(record_bytes), "sha256": inventory.sha(record_bytes)}
        ledger._need(len(record_bytes) <= publication.reserves["record"], "V7_RECORD_BUDGET_EXCEEDED")
        record = codec.loads(record_bytes)
        publication.check_record(record)
        if record.get("status") != "COMPLETE":
            publication.primary = str((record.get("failure") or {}).get("code") or "V7_INPUT_NOT_COMPLETE")
        publication.phase = "RECORD_PUBLICATION"
        publication.atomic("record.json", record_bytes)
        publication.phase = "RECORD_RELOAD"
        data = _read(directory / "record.json")
        ledger._need(data == record_bytes, "V7_RECORD_RELOAD_CHANGED")
        reloaded = codec.loads(data)
        ledger._need(publication.snapshot()["accounting_complete"], "V7_PRESTART_OR_RESULT_CHANGED")
        publication.phase = "TECHNICAL_VERIFICATION"
        technical = publication.verify_record(reloaded)
        if publication.primary is None:
            ledger._need(_read(directory / "record.json") == record_bytes, "V7_VERIFIED_RECORD_CHANGED")
            publication.phase = "EVALUATION"
            functional = evaluation.evaluate(reloaded)
        else:
            functional = None
        publication.phase = "VERIFICATION_PUBLICATION"
        proof = {"version": publication.proof_version, "scope": "NEUTRAL_DEVELOPMENT_ONLY",
                 "record": {"path": "record.json", **publication.candidate}, "technical": technical,
                 "evaluation": functional, "authority": "candidate until successful terminal; errors invalidate use"}
        proof_bytes = prestart.canonical(proof)
        publication.atomic("verification.json", proof_bytes)
        if publication.primary is not None:
            return publication.failure()
        publication.phase = "TERMINAL_PUBLICATION"
        terminal = publication.receipt("CLOSED_NEUTRAL_VERIFIED")
        terminal.update(record=proof["record"], verification={"path": "verification.json",
                        "bytes": len(proof_bytes), "sha256": inventory.sha(proof_bytes)})
        publication.atomic("terminal.json", prestart.canonical(terminal))
        result = publication.finish()
        ledger._need(result["evaluation_allowed"], "V7_FINAL_INTEGRITY_FAILED")
        return result
    except Exception as exc:
        return publication.failure(exc)
