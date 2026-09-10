"""Finite caller session around unchanged OB materialization and processing."""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from threading import Lock
from tools import _s2ob_private_caller_binding as b
from tools import _s2ob_private_caller_verification as verifier

MAIN_GATE = False
SCHEMA = "s2oc.caller-session.v1"
QUAL_ID = "s2oc-session-qualification-20260910-01"
QUAL_DIR = b.ROOT / "reports/s2oc" / QUAL_ID
OWN = ("tools/_s2oc_private_caller_session.py", "tests/test_s2oc_private_caller_session.py",
       "reports/s2oc/qualify_once.py", "reports/s2oc/QUALIFIKATION.md")


class S2OCError(ValueError):
    def __init__(self, code, balance=None):
        self.code, self.balance = code, balance
        super().__init__(code)


def require(ok, code):
    if not ok:
        raise S2OCError(code)


def sources():
    return dict(schema=SCHEMA, ob_code_digest=b.digest(b.code_inventory()),
        files={p: [hashlib.sha256((b.ROOT/p).read_bytes()).hexdigest(), (b.ROOT/p).stat().st_size] for p in OWN})


def ob_qualification_bytes():
    names = ("preregistration.json", "result.json", "stdout.txt", "stderr.txt", "metrics.json", "state-sizes.json", "final-balance.json")
    return sum((b.QUAL_DIR/n).stat().st_size for n in names)


def package_balance(record, binding, inventory, *, proof_bytes=262144):
    refs = tuple(tuple(x) for x in record["references"])+(
        ("sources", "session-sources.json", len(b.canonical(inventory))),
        ("metadata", "session.json", len(b.canonical(binding))),
        ("metadata", "required-ob-qualification", ob_qualification_bytes()),)
    balance = b.balance(record, refs, proof_bytes=proof_bytes)
    prefix = binding.get("failed_prefix_steps", [])
    require(len(prefix) <= 28 and all(len(b.canonical(s)) <= 16384 for s in prefix), "SESSION_RESULT_LIMIT")
    prefix_bytes = sum(len(b.canonical(s)) for s in prefix)
    balance["totals"]["metadata"] -= prefix_bytes
    balance["failed_prefix_step_bytes"] = prefix_bytes
    balance["contributions"]["metadata"].append(["failed_prefix_step_classification", -prefix_bytes])
    balance["violations"] = [k.upper()+"_LIMIT" for k, n in balance["totals"].items() if n > b.LIMITS[k]]
    balance["remaining"] = {k: b.LIMITS[k]-n for k, n in balance["totals"].items()}
    if balance["violations"]:
        raise S2OCError("SESSION_PACKAGE_LIMIT", balance)
    return balance


def _qualified(inventory):
    q = json.loads((QUAL_DIR/"result.json").read_bytes())
    b.check_root(q, "result_digest")
    require(q["run_id"] == QUAL_ID and q["status"] == "QUALIFIED" and q["test_calls"] == 1
        and q["passed_tests"] == q["expected_tests"] == 24
        and q["hashes_unchanged"] is True and q["gates"] is False
        and q["session_sources_digest"] == b.digest(inventory)
        and q["source_digest"] == b.digest(dict(ob=b.code_inventory(), session=inventory)), "SESSION_NOT_QUALIFIED")
    require(set(q["files"]) == {"preregistration.json", "stdout.txt", "stderr.txt", "metrics.json"}, "SESSION_QUALIFICATION_CHANGED")
    for name, expected in q["files"].items():
        require(hashlib.sha256((QUAL_DIR/name).read_bytes()).hexdigest() == expected, "SESSION_QUALIFICATION_CHANGED")
    ledger = (QUAL_DIR/"final-balance.json").read_bytes()
    require(hashlib.sha256(ledger).hexdigest() == q["ledger_sha256"]
        and json.loads(ledger)["violations"] == [], "SESSION_QUALIFICATION_CHANGED")
    actual = sum((QUAL_DIR/name).stat().st_size for name in (*q["files"], "result.json", "final-balance.json"))
    require(q["qualification_bytes"] == actual <= 4096, "SESSION_QUALIFICATION_LIMIT")


def open_session(manifest, directory, *, mode="CALLER"):
    global MAIN_GATE
    try:
        require(MAIN_GATE and mode in ("CALLER", "NEUTRAL"), "SESSION_GATE_CLOSED")
        b.validate_manifest(manifest)
        ob = b.code_inventory()
        require(manifest.code_digest == b.digest(ob), "SESSION_CODE_INVALID")
        refs = b.qualified_references(ob) if mode == "CALLER" else (
            ("sources", b.OWN[0]+":neutral-inventory", len(b.canonical(ob))),)
        inventory = sources()
        if mode == "CALLER":
            _qualified(inventory)
        path = Path(directory)
        require(not path.exists() and path.parent.is_dir(), "SESSION_OUTPUT_CONFLICT")
        immutable = b.canonical(asdict(manifest))
        shell = dict(execution=None, manifest=json.loads(immutable), references=refs)
        package_balance(shell, dict(schema=SCHEMA, manifest_digest=manifest.manifest_digest), inventory)
        path.mkdir()
        session = Session.__new__(Session)
        session._lock = Lock()
        session._manifest = b.decode_manifest(json.loads(immutable))
        session._manifest_bytes = immutable
        session._path, session._mode, session._sources, session._refs = path, mode, inventory, refs
        session._runtime = session._materializer = None
        session._terminal = None
        session._returned = []
        session._phase = "RUNTIME_INIT"
        try:
            session._runtime = b.CallerRuntime(session._manifest)
            session._materializer = b.Materializer(session._manifest)
        except Exception as exc:
            session._fail(exc, "RUNTIME_INIT", None)
            raise S2OCError(getattr(exc, "code", "SESSION_INIT_FAILED")) from exc
        return session
    finally:
        MAIN_GATE = False


class Session:
    def __init__(self):
        raise S2OCError("USE_OPEN_SESSION")

    def _binding(self, record):
        return b.sealed(dict(schema=SCHEMA, run_id=self._manifest.run_id,
            manifest_digest=self._manifest.manifest_digest, session_sources_digest=b.digest(self._sources),
            record_digest=record["record_digest"], status=record["status"],
            returned_results=list(self._returned),
            failed_prefix_steps=[] if record["execution"] is not None else
                [row["step"] for row in self._runtime.rows[:len(self._returned)]] if self._runtime is not None else [],
            result_encoding="canonical JSON bytes of execution.rows[ordinal-1].step; no mutable references",
            main_gate=False), "session_digest")

    def _publish(self, record):
        require(self._terminal is None, "SESSION_ALREADY_PUBLISHED")
        binding = self._binding(record)
        package_balance(record, binding, self._sources)
        for name, value, limit in (("session-sources.json", self._sources, b.LIMITS["sources"]),
                                  ("session.json", binding, b.LIMITS["metadata"]),
                                  ("record.json", record, b.LIMITS["total"])):
            b.r.ng.ne.atomic_write(self._path/name, value, limit)
        self._terminal = b.canonical(record)
        return self._terminal

    def _record(self, core=None, failure=None):
        return b.sealed(dict(schema=b.SCHEMA, mode=self._mode, run_id=self._manifest.run_id,
            manifest=asdict(self._manifest), code_digest=self._manifest.code_digest, references=self._refs,
            status=core["status"] if core is not None else "NOT_EVALUABLE",
            counts=None if self._materializer is None else dict(self._materializer.counts),
            execution=core, failure=failure, evaluation=None, main_gate=False), "record_digest")

    def _fail(self, exc, phase, ordinal):
        c, m = self._runtime, self._materializer
        final = None if c is None else c.close()
        failure = dict(phase=phase, ordinal=ordinal, source_id=None if m is None else m.source_id,
            completed_events=0 if final is None else final["processed_event_count"],
            code=getattr(exc, "code", "SESSION_PROCESSING_FAILED"), error_class=type(exc).__name__,
            last_snapshot_digest=None if final is None else final["snapshot_digest"], final=final,
            balance=getattr(exc, "balance", None))
        return self._publish(self._record(failure=failure))

    def _check_progress_budget(self):
        c = self._runtime
        # Measure existing evidence only; 16 KiB covers unlisted enclosing runtime metadata.
        view = dict(states=c.states, inputs=c.packed, rows=c.rows, source_receipts=c.source,
            scans=[dict(ordinal=n, role=role, value=asdict(x)) for (n, role), x in sorted(c.scans.items())])
        shell = dict(execution=view, manifest=asdict(self._manifest), references=self._refs+(
            ("metadata", "runtime_envelope_allowance", 16384),))
        binding = dict(returned_results=self._returned, failed_prefix_steps=[])
        package_balance(shell, binding, self._sources)

    def process(self, event):
        require(self._lock.acquire(blocking=False), "SESSION_BUSY")
        try:
            require(self._terminal is None and not self._runtime.closed, "SESSION_CLOSED")
            require(b.canonical(asdict(self._manifest)) == self._manifest_bytes, "SESSION_MANIFEST_CHANGED")
            require(type(event) is b.Event, "SESSION_EVENT_INVALID")
            n = len(self._runtime.rows)
            require(type(event.ordinal) is int and event.ordinal > n, "SESSION_DUPLICATE")
            require(n < len(self._manifest.events), "SESSION_EXHAUSTED")
            require(event.ordinal == n+1, "SESSION_ORDER_INVALID")
            require(event == self._manifest.events[n], "SESSION_EVENT_BINDING_INVALID")
            require(self._materializer.counts["materialized_events"] == n, "SESSION_PROGRESS_INVALID")
            self._check_progress_budget()
            # The lock includes payload access, materialization, native processing and evidence publication.
            try:
                self._phase = "MATERIALIZATION"
                item = self._materializer.next(event)
                try:
                    self._phase = "EVENT"
                    row = self._runtime.process(item)
                    self._check_progress_budget()
                    result = b.canonical(row["step"])
                    require(len(result) <= 16384, "SESSION_RESULT_LIMIT")
                finally:
                    del item
            except Exception as exc:
                phase = self._materializer.phase if self._phase == "MATERIALIZATION" else self._phase
                if self._runtime.phase == "EVIDENCE":
                    phase = "EVIDENCE"
                self._fail(exc, phase, event.ordinal)
                raise S2OCError(getattr(exc, "code", "SESSION_PROCESSING_FAILED")) from exc
            if self._runtime.failed:
                core = self._runtime.record()
                self._publish(self._record(core, core["failure"]))
                raise S2OCError(core["failure"]["code"])
            self._returned.append(dict(ordinal=event.ordinal, sha256=hashlib.sha256(result).hexdigest(), byte_count=len(result)))
            return result
        finally:
            self._lock.release()

    def close(self):
        require(self._lock.acquire(blocking=False), "SESSION_BUSY")
        try:
            if self._terminal is not None:
                return self._terminal
            if len(self._runtime.rows) != len(self._manifest.events):
                return self._fail(S2OCError("INCOMPLETE"), "CLOSE", None)
            try:
                core = self._runtime.record()
                return self._publish(self._record(core, core["failure"]))
            except Exception as exc:
                self._fail(exc, "CLOSE", None)
                raise S2OCError(getattr(exc, "code", "SESSION_CLOSE_FAILED")) from exc
        finally:
            self._lock.release()


def verify_binding(binding, record, inventory):
    b.check_root(binding, "session_digest")
    require(binding["schema"] == SCHEMA and binding["main_gate"] is False
        and binding["run_id"] == record["run_id"] and binding["manifest_digest"] == record["manifest"]["manifest_digest"]
        and binding["record_digest"] == record["record_digest"] and binding["status"] == record["status"]
        and binding["session_sources_digest"] == b.digest(inventory), "SESSION_BINDING_INVALID")
    refs = binding["returned_results"]
    require(type(refs) is list and len(refs) <= len(record["manifest"]["events"]), "SESSION_RESULTS_INVALID")
    rows = ([dict(step=x) for x in binding["failed_prefix_steps"]] if record["execution"] is None
        else record["execution"]["rows"])
    require(record["execution"] is None or binding["failed_prefix_steps"] == [], "SESSION_RESULTS_INVALID")
    for n, ref in enumerate(refs, 1):
        require(set(ref) == {"ordinal", "sha256", "byte_count"} and ref["ordinal"] == n
            and b.r.ng.stream._valid_digest(ref["sha256"]) and type(ref["byte_count"]) is int
            and 0 < ref["byte_count"] <= 16384, "SESSION_RESULTS_INVALID")
        require(n <= len(rows), "SESSION_RESULTS_INVALID")
        raw = b.canonical(rows[n-1]["step"])
        require(len(raw) == ref["byte_count"] and hashlib.sha256(raw).hexdigest() == ref["sha256"], "SESSION_RESULTS_INVALID")
    if record["status"] == "RECORDING_COMPLETE":
        require(len(refs) == len(rows), "SESSION_RESULTS_INVALID")
    return len(refs)


def verify_session_once(directory):
    path = Path(directory)
    record = json.loads((path/"record.json").read_bytes())
    binding = json.loads((path/"session.json").read_bytes())
    inventory = json.loads((path/"session-sources.json").read_bytes())
    require(inventory == sources(), "SESSION_SOURCES_CHANGED")
    count = verify_binding(binding, record, inventory)
    proof = verifier.verify_once(path)
    result = b.sealed(dict(schema=SCHEMA, record_digest=record["record_digest"], session_digest=binding["session_digest"],
        verification_digest=proof["verification_digest"], returned_result_bindings=count,
        evaluation_allowed=proof["evaluation_allowed"], read_only=True,
        boundary="Returned bytes reconstructed from stored steps; partial error prefixes are not functional evaluation or full state-chain verification."), "session_verification_digest")
    package_balance(record, binding, inventory, proof_bytes=len(b.canonical(proof))+4+len(b.canonical(result)))
    b.r.ng.ne.atomic_write(path/"session-verification.json", result, 262144-len(b.canonical(proof))-4)
    return result
