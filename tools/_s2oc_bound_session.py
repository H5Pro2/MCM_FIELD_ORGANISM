"""One OC session, current shared binding, common alternative closure ledger."""
from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path
from threading import Lock

from tools import _s2oc_shared_binding as shared

b, prior, budget = shared.b, shared.prior, shared.budget
MAIN_GATE = False
ATTACHMENTS = (("metadata", "@evaluation", 3000), ("metadata", "@dispatch", 768),
               ("metadata", "@final-balance", 1536), ("metadata", "@common-reference", 512))


def alternatives(success, failure, common, *, phase, ordinal, completed):
    rows = {name: shared.ledger(*pair, common, attachments=ATTACHMENTS)
            for name, pair in (("success", success), ("failure", failure))}
    if any(row["violations"] for row in rows.values()):
        raise budget.BudgetError("COMBINED_RUNTIME_METADATA_LIMIT",
            budget.diagnostic(rows, phase, ordinal, completed))
    return rows


class Session(prior.old.Session):
    def _record(self, core=None, failure=None):
        value = super()._record(core, failure)
        del value["record_digest"]
        value["input_reads"] = dict(self._common["read_plan"], **(
            dict(actual_read_bytes=0, read_operations=0) if self._materializer is None
            else self._materializer.read_account))
        return b.sealed(value, "record_digest")

    def _forms(self):
        c = self._runtime
        final = asdict(c.subject.snapshot())
        final["status"] = "CLOSED"
        final = b.sealed({k:v for k,v in final.items() if k != "snapshot_digest"}, "snapshot_digest")
        core = b.sealed(dict(schema=b.SCHEMA, status="RECORDING_COMPLETE", run_id=c.run_id,
            config_digest=c.config.config_digest, runtime_config=c.rc, binding=asdict(c.binding),
            initial=c.initial, final=final, inputs=c.packed, source_receipts=c.source,
            rows=c.rows, states=c.states,
            scans=[dict(ordinal=n, role=role, value=asdict(x)) for (n, role), x in sorted(c.scans.items())],
            failure=None, main_gate=False), "record_digest")
        success = self._record(core)
        sb = self._binding(success)
        if len(c.rows) > len(self._returned):
            raw = b.canonical(c.rows[-1]["step"])
            sb["returned_results"].append(dict(ordinal=len(c.rows), sha256=shared.sha(raw), byte_count=len(raw)))
            sb = b.sealed({k:v for k,v in sb.items() if k != "session_digest"}, "session_digest")
        failure = self._record(failure=dict(phase="SERIALIZATION", ordinal=len(self._manifest.events),
            source_id="x"*80, completed_events=len(c.rows), code="COMBINED_RUNTIME_METADATA_LIMIT",
            error_class="BudgetError", last_snapshot_digest=final["snapshot_digest"], final=final,
            balance="x"*budget.ERROR_LIMIT))
        return (success, sb), (failure, self._binding(failure))

    def _check_progress_budget(self):
        success, failure = self._forms()
        self._last_budget = alternatives(success, failure, self._common, phase="EVIDENCE",
            ordinal=min(len(self._runtime.rows)+1,len(self._manifest.events)), completed=len(self._runtime.rows))

    def _publish(self, record):
        shared.need(self._terminal is None, "SESSION_ALREADY_PUBLISHED")
        binding = self._binding(record)
        actual = shared.ledger(record, binding, self._common, attachments=ATTACHMENTS)
        if actual["violations"]:
            raise budget.BudgetError("CLOSURE_LIMIT", budget.diagnostic({"actual":actual},
                self._phase, None, len(self._runtime.rows) if self._runtime else 0))
        wr, ws = shared.pack(record, binding, self._common)
        # The existing closed output directory is exclusively owned by this session.
        prior.save(self._path/"record.json", wr)
        prior.save(self._path/"session.json", ws)
        self._terminal = b.canonical(record)
        return self._terminal

    def process(self, event):
        try:
            return super().process(event)
        except budget.BudgetError as exc:
            if self._terminal is None:
                self.abort(exc, "EVIDENCE", getattr(event, "ordinal", None))
            raise

    def abort(self, exc, phase, ordinal):
        shared.need(self._lock.acquire(blocking=False), "SESSION_BUSY")
        try:
            if self._terminal is not None:
                return self._terminal
            return self._fail(exc, phase, ordinal)
        finally:
            self._lock.release()

    def close(self):
        if self._terminal is not None:
            return self._terminal
        try:
            self._check_progress_budget()
        except budget.BudgetError as exc:
            return self.abort(exc, "CLOSE", None)
        return super().close()


def open_session(common, inv, directory, *, neutral=False, common_path=None):
    global MAIN_GATE
    shared.need(MAIN_GATE, "MAIN_GATE_CLOSED")
    MAIN_GATE = False
    shared.need(type(neutral) is bool, "MODE_INVALID")
    manifest = shared.validate_common(common, inv, qualified=not neutral)
    path = Path(directory)
    shared.need(not path.exists() and path.parent.is_dir(), "SESSION_OUTPUT_CONFLICT")
    location=None
    if common_path is not None:
        cp=Path(common_path).resolve()
        shared.need(cp.is_relative_to(b.ROOT) and cp.suffix==".json","COMMON_LOCATION_INVALID")
        shared.need(b.canonical(shared.read_json(cp))==b.canonical(common),"COMMON_REFERENCE_INVALID")
        location=dict(path=cp.relative_to(b.ROOT).as_posix(),bytes=len(b.canonical(common)),sha256=shared.sha(b.canonical(common)))
        shared.need(len(b.canonical(location))<=512,"COMMON_LOCATION_INVALID")
    # No state or receptor is constructed before the complete structural bound.
    from tools import _s2oc_shared_verification as verification
    upper = verification.preflight(common)
    if upper["violations"]:
        raise budget.BudgetError("PREFLIGHT_LIMIT", upper["failure_diagnostic"])
    c = Session.__new__(Session)
    c._lock, c._manifest_bytes = Lock(), b.canonical(asdict(manifest))
    c._manifest, c._common = manifest, deepcopy(common)
    c._sources, c._refs = inv, shared.references(common)
    c._active_qualification = common["qualification"]
    c._path, c._mode = path, "NEUTRAL" if neutral else "CALLER"
    c._terminal, c._returned, c._phase = None, [], "RUNTIME_INIT"
    c._runtime = c._materializer = None
    path.mkdir()
    prior.save(path/("common.json" if location is None else "common-reference.json"), common if location is None else location)
    try:
        c._runtime = b.CallerRuntime(manifest)
        c._materializer = b.Materializer(manifest, track_reads=True)
        c._check_progress_budget()
    except Exception as exc:
        c._fail(exc, "RUNTIME_INIT", None)
        raise
    return c


def run_once(common, inv, directory, *, neutral=False, common_path=None):
    """File caller uses this entry; one open, no retry or functional evaluation."""
    session = open_session(common, inv, directory, neutral=neutral, common_path=common_path)
    try:
        for event in session._manifest.events:
            session.process(event)
        return session.close()
    except Exception as exc:
        if session._terminal is None:
            session.abort(exc, session._phase, len(session._runtime.rows)+1)
        raise
    finally:
        if session._terminal is None:
            session.close()
