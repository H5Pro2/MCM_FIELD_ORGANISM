"""Gated file entry for a later separately authorized S2-UC source run."""
from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path

from tools import _s2uc_neutral_connection as connection
from tools import _s2uc_record_codec as codec
from tools import _s2uc_verification as verification
from tools import _s2uc_evaluation as evaluation
from tools import _s2uc_resource_ledger as ledger
from tools import _s2uc_source_binding as binding
from tools import _s2uc_run_binding as run_binding


MAIN_GATE = False
USED = False


class S2UCRecordBudgetError(ValueError):
    def __init__(self, code: str, candidate: dict[str, object]) -> None:
        self.code, self.candidate = code, candidate
        super().__init__(code)

_ACTIVE = ("_s2uc_source_binding.py", "_s2uc_neutral_connection.py", "_s2uc_record_codec.py", "_s2uc_verification.py", "_s2uc_evaluation.py", "_s2uc_resource_ledger.py", "_s2uc_run_entry.py", "_s2uc_run_binding.py", "_s2uc_source_adapter.py", "s2uc_run_bound_once.py", "_s2ub_candidate_confirmation.py", "_s2ub_candidate_verification.py", "_s2tw_exact_confirmation.py", "_s2tu_retained_trace.py", "_s2ty_audio_materialization.py", "_s2nj_private_auditory_output_projection.py")

def _active_bindings():
    root = Path(__file__).parent
    rows = []
    for name in _ACTIVE:
        data = (root / name).read_bytes()
        rows.append({"name": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    return {"files": rows, "bytes": sum(row["bytes"] for row in rows)}

def _publish(path: Path, value: bytes):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(value)
    os.replace(temporary, path)

def _json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _candidate(record_bytes: bytes) -> dict[str, object]:
    return {"bytes": len(record_bytes), "sha256": hashlib.sha256(record_bytes).hexdigest(), "codec_version": codec.VERSION}


def _error_evidence(*, primary: str, phase: str, progress, candidate: dict[str, object] | None) -> bytes:
    """A bounded diagnostic receipt that never embeds a candidate record."""
    value = {"status": "CLOSED_WITH_ERROR_EVIDENCE", "primary_error": primary, "phase": phase,
             "progress": progress, "candidate_record": candidate, "evaluation_allowed": False}
    encoded = _json(value)
    if len(encoded) > ledger.RESERVES["terminal"]:
        raise ValueError("ERROR_EVIDENCE_BUDGET_INVALID")
    return encoded

def _published_references(directory: Path):
    rows = []
    for path in sorted(directory.glob("*.json")):
        data = path.read_bytes()
        rows.append({"name": path.name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    return rows

def _minimal_terminal(*, directory, primary, progress, reason, manifest_bytes, active, error_evidence_bytes=0):
    references = _published_references(directory)
    value = {"status": "CLOSED_WITH_MINIMAL_ERROR_EVIDENCE", "primary_error": primary, "progress": progress,
             "incomplete_evidence_reason": reason, "published_references": references,
             "missing": ["full_terminal_budget"], "evaluation_allowed": False}
    encoded = _json(value)
    record_bytes = next((row["bytes"] for row in references if row["name"] == "record.json"), 0)
    budget = ledger.ledger(manifest_bytes=manifest_bytes, success_record_bytes=record_bytes, failure_record_bytes=record_bytes,
                           verification_bytes=0, terminal_bytes=len(encoded), error_evidence_bytes=error_evidence_bytes,
                           active_binding_bytes=active["bytes"])
    valid = len(encoded) <= ledger.RESERVES["terminal"] and not (budget["branches"]["failure"]["violations"] or budget["branches"]["failure"]["reserve_violations"])
    return encoded, value, budget, valid

def _terminal_with_budget(*, status, record_bytes, technical, functional, active, manifest_bytes, primary_error=None, progress=None,
                          error_evidence_bytes=0):
    """Resolve terminal size and its own ledger entry to a stable serialized form."""
    terminal_bytes = 0
    for _ in range(8):
        budget = ledger.ledger(manifest_bytes=manifest_bytes, success_record_bytes=len(record_bytes), failure_record_bytes=len(record_bytes),
                               verification_bytes=len(_json({"technical": technical, "evaluation": functional})), terminal_bytes=terminal_bytes,
                               error_evidence_bytes=error_evidence_bytes, active_binding_bytes=active["bytes"])
        value = {"status": status, "record_sha256": None if record_bytes is None else hashlib.sha256(record_bytes).hexdigest(),
                 "technical": technical, "evaluation_allowed": functional is not None, "evaluation": functional,
                 "active_bindings": active, "budget": budget, "primary_error": primary_error, "progress": progress}
        encoded = _json(value)
        if len(encoded) == terminal_bytes:
            return encoded, value, budget
        terminal_bytes = len(encoded)
    raise ValueError("TERMINAL_BUDGET_UNSTABLE")


def run_once(manifest: dict[str, object], materialize, output_directory, completion=None) -> dict[str, object]:
    """Execute only after a future caller binds sources and opens this gate once."""
    global MAIN_GATE, USED
    if not MAIN_GATE or USED:
        raise ValueError("RUN_NOT_AUTHORIZED")
    directory = Path(output_directory)
    record = None
    candidate = None
    created = False
    manifest_bytes = 0
    active = {"files": [], "bytes": 0}
    phase = "PRESTART"
    try:
        if directory.exists():
            raise ValueError("OUTPUT_DIRECTORY_ALREADY_EXISTS")
        directory.mkdir(parents=True)
        created = True
        binding.validate(manifest)
        manifest_bytes = manifest["binding_bytes"]
        active = _active_bindings()
        budget = ledger.planned(manifest_bytes)
        if active["bytes"] > ledger.RESERVES["active_bindings"]:
            raise ValueError("ACTIVE_BINDING_RESERVE_INVALID")
        if any(branch["violations"] for branch in budget["branches"].values()):
            raise ValueError("BUDGET_PRECONDITION_INVALID")
        USED = True
        phase = "CONNECTION"
        connection_record = connection.execute(manifest, materialize)
        record = connection_record
        if completion is not None:
            connection_record["source_completion"] = completion()
        phase = "RECORD_PREFLIGHT"
        record_bytes = codec.dumps(connection_record)
        candidate = _candidate(record_bytes)
        if len(record_bytes) > ledger.RESERVES["success_record"] or len(record_bytes) > ledger.LIMITS["record"]:
            raise S2UCRecordBudgetError("RECORD_BUDGET_INVALID", candidate)
        frame_count = 2 * sum("endpoint" in event for event in manifest["events"])
        metadata_ceiling = codec.conservative_metadata_ceiling(record_limit=ledger.RESERVES["success_record"], frame_count=frame_count)
        candidate["record_metadata_bytes"] = codec.record_metadata_bytes(record_bytes)
        candidate["record_metadata_ceiling"] = metadata_ceiling
        record_budget = ledger.ledger(manifest_bytes=manifest_bytes, success_record_bytes=len(record_bytes),
                                      failure_record_bytes=0, verification_bytes=ledger.RESERVES["verification"], terminal_bytes=0,
                                      active_binding_bytes=active["bytes"])
        if (record_budget["branches"]["success"]["violations"]
                or record_budget["branches"]["success"]["reserve_violations"]):
            raise S2UCRecordBudgetError("RECORD_BUDGET_INVALID", candidate)
        phase = "RECORD_PUBLICATION"
        _publish(directory / "record.json", record_bytes)
        phase = "VERIFICATION"
        reloaded = codec.loads((directory / "record.json").read_bytes())
        if reloaded["status"] == "COMPLETE":
            technical = verification.verify(reloaded, manifest, require_source_completion=completion is not None)
            functional = evaluation.evaluate(reloaded)
            evaluation_allowed = True
        else:
            technical = verification.verify_failure(reloaded, manifest)
            functional = None
            evaluation_allowed = False
        terminal_bytes, terminal, actual_budget = _terminal_with_budget(status="CLOSED", record_bytes=record_bytes, technical=technical,
                                                                          functional=functional, active=active, manifest_bytes=manifest_bytes)
        if actual_budget["branches"]["success"]["violations"] or actual_budget["branches"]["success"]["reserve_violations"]:
            raise ValueError("ACTUAL_BUDGET_INVALID")
        _publish(directory / "terminal.json", terminal_bytes)
        return {"budget": budget, "actual_budget": actual_budget, "record_bytes": record_bytes, "output_directory": str(directory),
                "technical_verification": technical, "evaluation_allowed": evaluation_allowed, "evaluation": functional}
    except Exception as exc:
        primary = getattr(exc, "code", str(exc) or type(exc).__name__)
        if isinstance(exc, S2UCRecordBudgetError):
            candidate = exc.candidate
        progress = None
        if record is not None:
            progress = record.get("failure") or {"connection_status": record.get("status"), "stories": [row.get("story") for row in record.get("stories", [])],
                                                   "completed_events": sum(row.get("completed", 0) for row in record.get("stories", [])), "phase": "POST_CONNECTION"}
        terminal = {"status": "CLOSED_AFTER_FAILURE", "primary_error": primary, "progress": progress,
                    "evaluation_allowed": False, "record_present": record is not None}
        error_evidence = {"published": False}
        error_evidence_bytes = 0
        if created:
            try:
                encoded = _error_evidence(primary=primary, phase=phase, progress=progress, candidate=candidate)
                _publish(directory / "error.json", encoded)
                error_evidence = {"published": True, "bytes": len(encoded), "sha256": hashlib.sha256(encoded).hexdigest()}
                error_evidence_bytes = len(encoded)
            except Exception as evidence_error:
                error_evidence = {"published": False, "error": str(evidence_error) or type(evidence_error).__name__}
            try:
                existing = (directory / "record.json").read_bytes() if (directory / "record.json").is_file() else b""
                terminal_bytes, terminal, failure_budget = _terminal_with_budget(status="CLOSED_AFTER_FAILURE", record_bytes=existing, technical=None,
                                                                      functional=None, active=active, manifest_bytes=manifest_bytes,
                                                                      primary_error=primary, progress=progress, error_evidence_bytes=error_evidence_bytes)
                if failure_budget["branches"]["failure"]["violations"] or failure_budget["branches"]["failure"]["reserve_violations"]:
                    raise ValueError("FAILURE_TERMINAL_BUDGET_INVALID")
                _publish(directory / "terminal.json", terminal_bytes)
            except Exception as publication_error:
                terminal["terminal_publication_error"] = str(publication_error) or type(publication_error).__name__
                try:
                    minimal_bytes, minimal, minimal_budget, valid = _minimal_terminal(directory=directory, primary=primary, progress=progress,
                                                                                       reason=terminal["terminal_publication_error"], manifest_bytes=manifest_bytes,
                                                                                       active=active, error_evidence_bytes=error_evidence_bytes)
                    if not valid:
                        raise ValueError("MINIMAL_TERMINAL_BUDGET_INVALID")
                    _publish(directory / "terminal-minimal.json", minimal_bytes)
                    terminal["minimal_terminal"] = {"published": True, "bytes": len(minimal_bytes), "budget": minimal_budget}
                except Exception as minimal_error:
                    terminal["minimal_terminal"] = {"published": False, "error": str(minimal_error) or type(minimal_error).__name__,
                                                    "permanent_terminal_evidence": "ABSENT"}
        return {"status": "NOT_EVALUABLE", "primary_error": primary, "evaluation_allowed": False,
                "evaluation": None, "output_directory": str(directory), "terminal": terminal, "error_evidence": error_evidence}
    finally:
        MAIN_GATE = False

def run_bound_once(bound: dict[str, object], manifest: dict[str, object], materialize, output_directory, completion=None) -> dict[str, object]:
    """Future real entry: validate static source/task binding before any payload access."""
    run_binding.validate(bound)
    if manifest.get("binding_digest") != bound.get("manifest_digest") or str(output_directory) != bound.get("output"):
        raise ValueError("RUN_BOUNDARY_INVALID")
    return run_once(manifest, materialize, output_directory, completion)
