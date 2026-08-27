"""Thirteen isolated file fixtures. No launcher, CLI or matrix integration."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import ctypes

from ._s2er_publication_records import PublicationError, encoded, loads, raw_digest, require
from ._s2ex_recorder_binding import ATTEMPT, CASES, checked_record, clone, record
from ._s2ex_recorder_native import open_recorded_backend, require_execution
from ._s2ex_recorder_trace import Trace, validate_trace


_CONSUMED = set()
_CONSUMPTION_LOCK = Lock()


def verify_sources(backend, references):
    for ref in references:
        _, raw = backend.read_source(ref["path"], ref["byte_count"])
        require(raw_digest(raw) == ref["raw_sha256"], "source bytes changed")


class IsolatedCase:
    def __init__(self, binding, case_id, sink):
        require_execution(binding)
        self.binding, self.case_id = binding, case_id
        self.eu, _, self.profile, self.run, _, self.refs, _, self.inventory = binding.values()
        self.trace = Trace(binding, case_id, sink)
        self.worker = open_recorded_backend(binding, self.trace, "worker")
        self.helper = open_recorded_backend(binding, self.trace, "helper")
        self.records, self.handles = {}, {}
        self.payload = ("S2EU PLATFORM FIXTURE " + case_id + "\n").encode("ascii")
        self.sentinel = ("S2EU OCCUPIED " + case_id + "\n").encode("ascii")
        self.sentinel_handle = None
        self.renamed = self.rename_attempted = False
        self.final_confirmed = self.marker_confirmed = False
        self.closed = False

    def path(self, role, case=None):
        return self.inventory.get(case or self.case_id, role).path

    def helper_action(self, name, operation):
        # The future completes only after the helper's native calls and checks.
        with ThreadPoolExecutor(max_workers=1, thread_name_prefix="s2ex-helper") as pool:
            result = pool.submit(operation).result()
        self.trace.check(name, True, "helper")
        return result

    def setup_sentinel(self, role):
        previous, self.trace.phase = self.trace.phase, "SETUP"
        try:
            def create():
                handle = self.helper.create(self.path(role))
                self.helper.write_complete(handle, self.sentinel)
                self.helper.flush(handle)
                self.helper.verify(handle, self.sentinel)
                return handle
            self.sentinel_handle = self.helper_action("helper.sentinel-ready", create)
        finally:
            self.trace.phase = previous

    def write_record(self, role):
        order = ("case_reservation", "target_reservation", "evidence", "sealed")
        count = {"case_reservation": 0, "target_reservation": 1, "evidence": 2, "sealed": 3, "marker": 4}[role]
        result_role = role in ("sealed", "marker")
        value = record("s2eu.fixture-record.v1", attempt_id=ATTEMPT, case_id=self.case_id, role=role,
                       profile_digest=self.profile["record_digest"], run_binding_digest=self.run["record_digest"],
                       prior_record_digests=[self.records[k]["record_digest"] for k in order[:count]],
                       payload_byte_count=len(self.payload) if result_role else None,
                       payload_raw_sha256=raw_digest(self.payload) if result_role else None,
                       result_identity=self.handles["staging"].identity if role == "marker" else None)
        raw = encoded(value)
        handle = self.worker.create(self.path(role))
        self.handles[role] = handle
        self.worker.write_complete(handle, raw)
        self.worker.flush(handle)
        self.worker.verify(handle, raw)
        self.records[role] = value
        return handle

    def foreign_open(self):
        def attempt():
            value = self.helper.kernel.CreateFileW(self.path("case_reservation"), 0x40000000, 7, None, 3, 0x00200000, None)
            error = ctypes.get_last_error()
            if value == ctypes.c_void_p(-1).value:
                raise PublicationError("NATIVE_PUBLICATION_ERROR", "foreign CreateFileW", native_error=error)
            # An unexpected successful open must still close its own handle once.
            result = self.helper.kernel.CloseHandle(value)
            require(bool(result), "unexpected foreign handle close failed")
            raise PublicationError("UNEXPECTED_PLATFORM_RESULT", "foreign write unexpectedly opened")
        self.helper_action("helper.foreign-open", attempt)

    def close(self):
        require(not self.closed, "case close reused")
        self.closed = True
        failures = []
        for backend in (self.worker, self.helper):
            try:
                backend.close_all()
            except BaseException as error:
                failures.append(error)
                backend.kernel.close_unrecorded_on_abort()
        if failures:
            raise failures[0]

    def postconditions(self):
        if self.sentinel_handle is not None:
            self.helper.verify(self.sentinel_handle, self.sentinel)
        if self.case_id == "p05":
            handle = self.helper._open(self.path("staging"), verification=True)
            self.helper.verify(handle, self.payload)
        verify_sources(self.helper, self.refs)
        self.trace.check("sources-unchanged", True, "helper")
        self.trace.check("case-postconditions", True, "helper")

    def cold_read(self):
        with self.trace.at_phase("E8"):
            self.worker.pin_parents(self.profile["parent_directories"])
            self.helper.pin_parents(self.profile["parent_directories"])
            self.helper.source_roots = self.worker.source_roots
            prior = []
            payload = b"S2EU PLATFORM FIXTURE p01\n"
            result = self.worker._open(self.path("final", "p01"), verification=True)
            self.worker.verify(result, payload)
            for role in ("case_reservation", "target_reservation", "evidence", "sealed", "marker"):
                handle = self.worker._open(self.path(role, "p01"), verification=True)
                value = checked_record(loads(self.worker.read(handle)))
                require(value["case_id"] == "p01" and value["role"] == role and
                        value["attempt_id"] == ATTEMPT and value["profile_digest"] == self.profile["record_digest"] and
                        value["run_binding_digest"] == self.run["record_digest"] and
                        value["prior_record_digests"] == prior, "cold fixture identity differs")
                if role in ("sealed", "marker"):
                    require(value["payload_byte_count"] == len(payload) and value["payload_raw_sha256"] == raw_digest(payload),
                            "cold payload differs")
                if role == "marker":
                    require(value["result_identity"] == result.identity, "cold result identity differs")
                prior.append(value["record_digest"])
            self.postconditions()
            self.close()

    def execute(self):
        require_execution(self.binding)
        error = None
        try:
            if self.case_id == "p13":
                self.cold_read()
                return self.trace.finish("COMPLETE_RECORDS_PRESENT_UNCONFIRMED")
            with self.trace.at_phase("E0"):
                parents = clone(self.profile["parent_directories"])
                # Helper keeps the original parents for independent postchecks.
                self.helper.pin_parents(parents)
                if self.case_id == "p02":
                    identity = parents["output"]["identity"]
                    first = identity["file_id_hex"][0]
                    identity["file_id_hex"] = ("1" if first == "0" else "0") + identity["file_id_hex"][1:]
                try:
                    self.worker.pin_parents(parents)
                except PublicationError as failure:
                    if self.case_id == "p02" and failure.code == "BLOCKED_PLATFORM_PREREQUISITE" and str(failure) == "parent native identity differs":
                        self.trace.check("expected-parent-mismatch", True)
                    raise
                verify_sources(self.worker, self.refs)
                for role in ("case_reservation", "target_reservation", "evidence", "staging", "sealed", "final", "marker"):
                    self.worker.require_absent(self.path(role))
            if self.case_id == "p03":
                self.setup_sentinel("case_reservation")
            with self.trace.at_phase("E1"):
                self.write_record("case_reservation")
                if self.case_id == "p06":
                    self.foreign_open()
            if self.case_id == "p04":
                self.setup_sentinel("target_reservation")
            with self.trace.at_phase("E2"):
                self.write_record("target_reservation")
            with self.trace.at_phase("E3"):
                self.write_record("evidence")
            with self.trace.at_phase("E4"):
                handle = self.worker.create(self.path("staging"), rename=True)
                self.handles["staging"] = handle
                self.worker.write_complete(handle, self.payload)
                self.worker.flush(handle)
                self.worker.verify(handle, self.payload)
                self.write_record("sealed")
            self.worker.require_absent(self.path("final"))
            if self.case_id == "p05":
                self.setup_sentinel("final")
            if self.case_id == "p01":
                self.helper_action("helper.before-rename", lambda: self.helper.require_absent(self.path("final")))
            with self.trace.at_phase("E5"):
                self.rename_attempted = True
                self.worker.rename_no_replace(self.handles["staging"], self.path("final"))
                self.renamed = True
            with self.trace.at_phase("E6"):
                self.worker.flush(self.handles["staging"])
                self.worker.verify_final_name(self.handles["staging"])
                self.worker.verify(self.handles["staging"], self.payload)
                self.final_confirmed = True
                if self.case_id == "p01":
                    def observe():
                        handle = self.helper._open(self.path("final"), verification=True)
                        self.helper.verify(handle, self.payload)
                        require(handle.identity == self.handles["staging"].identity, "helper final identity differs")
                    self.helper_action("helper.after-rename", observe)
            with self.trace.at_phase("E7"):
                self.write_record("marker")
                self.marker_confirmed = True
            with self.trace.at_phase("E8"):
                require(self.final_confirmed and self.marker_confirmed, "missing live barriers")
                for role, value in self.records.items():
                    self.worker.verify(self.handles[role], encoded(value))
                self.postconditions()
                self.close()
        except BaseException as failure:
            error = failure
        if error is None:
            status = "COMPLETED"
        else:
            status = "ABORTED_INCOMPLETE" if self.rename_attempted else "FAILED"
            if "case_reservation" not in self.handles and isinstance(error, PublicationError) and error.code == "BLOCKED_PLATFORM_PREREQUISITE":
                status = "BLOCKED_PLATFORM_PREREQUISITE"
            self.trace.phase = "CLEANUP"
            if not self.closed:
                try:
                    self.postconditions()
                except BaseException:
                    self.trace.broken = True
                finally:
                    self.close()
        require(not self.trace.broken, "case recording incomplete", "RECORDING_INCOMPLETE")
        return self.trace.finish(status)


def record_worker(binding, sink):
    """Called only by a separately admitted launcher after durable reservation."""
    require_execution(binding)
    identity = binding.identity()
    with _CONSUMPTION_LOCK:
        require(identity not in _CONSUMED, "isolated worker already consumed")
        _CONSUMED.add(identity)
    for case_id in CASES:
        case = IsolatedCase(binding, case_id, sink)
        raw = case.execute()
        require(validate_trace(raw, binding)["matched"], "unexpected isolated case outcome", "RECORDING_INCOMPLETE")
    return 0
