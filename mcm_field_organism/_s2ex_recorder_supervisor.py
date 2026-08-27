"""Private recorder supervisor; accepts an already launched, admitted worker."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from threading import RLock
import ctypes
import subprocess

from ._s2er_publication_records import PublicationError, encoded, loads, raw_digest, require
from ._s2er_windows_files import WindowsFiles
from ._s2ex_recorder_binding import ATTEMPT, CASES, b64, record
from ._s2ex_recorder_fixture import verify_sources
from ._s2ex_recorder_native import open_recorded_backend, require_execution
from ._s2ex_recorder_trace import validate_control, validate_trace


def write_stream(backend, handle, raw):
    require(type(raw) is bytes and raw, "nonempty stream bytes required")
    for start in range(0, len(raw), 1048576):
        part = raw[start:start + 1048576]
        count = ctypes.c_uint32()
        buffer = ctypes.create_string_buffer(part)
        result = backend.kernel.WriteFile(handle.value, buffer, len(part), ctypes.byref(count), None)
        error = ctypes.get_last_error() if not result else None
        if not result:
            raise PublicationError("NATIVE_PUBLICATION_ERROR", "recorder WriteFile", native_error=error)
        require(count.value == len(part), "recorder short write", "RECORDING_INCOMPLETE")


class _ControlSpool:
    """Own I/O is deliberately not recursively fed into its own transcript."""

    def __init__(self, binding):
        require_execution(binding)
        _, _, profile, _, _, _, _, paths = binding.values()
        self.backend = WindowsFiles()
        self.closed = False
        try:
            self.backend.pin_parents(profile["parent_directories"])
            path = paths.get(None, "recorder.control.spool").path
            self.backend.require_absent(path)
            self.handle = self.backend.create(path)
        except BaseException:
            self.close()
            raise

    def append(self, raw):
        require(not self.closed, "control spool closed")
        write_stream(self.backend, self.handle, raw)

    def finish(self, expected):
        require(not self.closed, "control spool already finished")
        self.backend.flush(self.handle)
        self.backend.verify(self.handle, expected)
        self.close()

    def close(self):
        if not self.closed:
            self.closed = True
            self.backend.close_all()


class ControlTrace:
    def __init__(self, binding):
        _, _, profile, run, source, _, self.actors, _ = binding.values()
        self.binding = binding
        self.case_id = None
        self.spec = None
        self.phase = "SETUP"
        self.lock = RLock()
        self.parts = []
        self.bytes = self.calls = 0
        self.spool = None
        self.failed = False
        self.last = source["record_digest"]
        self.emit("CONTROL_HEADER", profile_digest=profile["record_digest"], run_binding_digest=run["record_digest"])

    def call_id(self):
        with self.lock:
            require(self.calls < self.binding.limits.calls, "control call limit", "RECORDING_INCOMPLETE")
            self.calls += 1
            return f"{ATTEMPT}.control.call.{self.calls}"

    def emit(self, event, actor="supervisor", **fields):
        with self.lock:
            require(not self.failed, "control recording terminal", "RECORDING_INCOMPLETE")
            value = record("s2ex.control-entry.v1", attempt_id=ATTEMPT, sequence=len(self.parts) + 1,
                           phase=self.phase, event=event, actor_id=self.actors[actor],
                           previous_record_digest=self.last, fields=fields)
            raw = encoded(value) + b"\n"
            require(self.bytes + len(raw) <= self.binding.limits.trace_bytes, "control byte limit", "RECORDING_INCOMPLETE")
            try:
                if self.spool is not None:
                    self.spool.append(raw)
            except BaseException:
                self.failed = True
                raise
            self.parts.append(raw)
            self.bytes += len(raw)
            self.last = value["record_digest"]

    def attach(self):
        require(self.spool is None, "control spool reused")
        self.spool = _ControlSpool(self.binding)
        self.spool.append(b"".join(self.parts))

    def finish(self):
        require(not self.failed and self.spool is not None, "control recording incomplete")
        raw = b"".join(self.parts)
        try:
            validate_control(raw, self.binding)
            self.spool.finish(raw)
        except BaseException:
            self.failed = True
            raise


@dataclass(frozen=True, slots=True)
class LiveRecordingCompletion:
    binding_digest: str
    manifest_digest: str
    marker_digest: str
    worker_exit_code: int


class RecorderSupervisor:
    def __init__(self, binding):
        require_execution(binding)
        self.binding = binding
        _, _, self.profile, self.run, self.source, self.refs, _, self.paths = binding.values()
        self.control = ControlTrace(binding)
        self.backend = open_recorded_backend(binding, self.control, "supervisor")
        self.lock = RLock()
        self.state = "FRESH"
        self.spools, self.spool_bytes, self.frozen = {}, {}, set()
        self.stdout_buffer = b""
        self.current_case = None
        self.completed_cases = []
        self.capture_bytes = 0
        self.frame_count = 0
        self.exit_code = None
        self.auth_ref = None
        self.published = []
        self.backend_closed = False

    def reserve(self, authorization_ref, preregistration_ref):
        require_execution(self.binding)
        require(self.state == "FRESH", "supervisor already consumed")
        self.state = "RESERVING"
        try:
            require(authorization_ref in self.refs and preregistration_ref in self.refs, "unbound authorization references")
            self.backend.pin_parents(self.profile["parent_directories"])
            verify_sources(self.backend, self.refs)
            for row in self.paths.by_path.values():
                if not row.role.startswith(("source.", "directory.")):
                    self.backend.require_absent(row.path)
            reservation = record("s2eu.attempt-reservation.v1", attempt_id=ATTEMPT,
                                 profile_digest=self.profile["record_digest"], run_binding_digest=self.run["record_digest"],
                                 source_manifest_digest=self.source["record_digest"], explicit_authorization=authorization_ref,
                                 preregistration_review=preregistration_ref, status="RESERVED")
            handle = self.backend.create(self.paths.get(None, "platform_reservation").path)
            raw = encoded(reservation)
            self.backend.write_complete(handle, raw)
            self.backend.flush(handle)
            self.backend.verify(handle, raw)
            self.auth_ref = loads(encoded(authorization_ref))
            self.control.attach()
            self.state = "RESERVED"
        except BaseException:
            self.abort()
            raise

    def _append(self, case, role, raw):
        key = (case, role)
        require(key not in self.frozen, "spool already frozen")
        current = self.spool_bytes.get(key, b"")
        require(len(current) + len(raw) <= self.binding.limits.stream_bytes, "spool byte limit", "RECORDING_INCOMPLETE")
        if key not in self.spools:
            self.spools[key] = self.backend.create(self.paths.get(case, role).path)
        write_stream(self.backend, self.spools[key], raw)
        self.spool_bytes[key] = current + raw

    def _stdout(self, chunk):
        self.stdout_buffer += chunk
        while b"\n" in self.stdout_buffer:
            line, self.stdout_buffer = self.stdout_buffer.split(b"\n", 1)
            value = loads(line)
            require(encoded(value) == line, "worker emitted noncanonical record", "RECORDING_INCOMPLETE")
            if self.current_case is None:
                require(len(self.completed_cases) < 13 and value.get("schema_version") == "s2eu.trace.v1" and
                        value.get("case_id") == CASES[len(self.completed_cases)], "worker case order differs")
                self.current_case = value["case_id"]
            require(value.get("case_id") == self.current_case, "interleaved worker cases")
            self._append(self.current_case, "recorder.trace.spool", line + b"\n")
            if value.get("schema_version") == "s2eu.trace-footer.v1":
                self.completed_cases.append(self.current_case)
                self.current_case = None

    def capture(self, process):
        """No process creation: the separately admitted launcher supplies Popen."""
        require_execution(self.binding)
        require(self.state == "RESERVED", "reserved supervisor required")
        self.state = "CAPTURING"
        failure = []
        killed = False

        def drain(channel, stream):
            nonlocal killed
            try:
                for _ in range(self.binding.limits.stream_bytes + 1):
                    chunk = stream.read(65536)
                    if not chunk:
                        break
                    with self.lock:
                        require(not failure, "another capture stream failed", "RECORDING_INCOMPLETE")
                        require(type(chunk) is bytes, "binary original stream required")
                        self.capture_bytes += len(chunk)
                        require(self.capture_bytes <= self.binding.limits.stream_bytes, "worker byte limit", "RECORDING_INCOMPLETE")
                        self.frame_count += 1
                        frame = encoded({"sequence": self.frame_count, "channel": channel, "bytes_base64": b64(chunk)}) + b"\n"
                        self._append(None, "recorder.transcript.spool", frame)
                        if channel == "stdout":
                            self._stdout(chunk)
            except BaseException as error:
                with self.lock:
                    failure.append(error)
                    if not killed and process.poll() is None:
                        killed = True
                        process.kill()

        try:
            require(isinstance(process, subprocess.Popen) and process.stdout is not None and
                    process.stderr is not None and not process.text_mode, "binary worker pipes required")
            with ThreadPoolExecutor(max_workers=2, thread_name_prefix="s2ex-capture") as pool:
                tasks = [pool.submit(drain, channel, stream) for channel, stream in
                         (("stdout", process.stdout), ("stderr", process.stderr))]
                for task in tasks:
                    task.result()
            self.exit_code = process.wait()
            require(not failure and self.exit_code == 0 and not self.stdout_buffer and
                    self.current_case is None and self.completed_cases == list(CASES),
                    "worker recording incomplete", "RECORDING_INCOMPLETE")
            for key, handle in self.spools.items():
                raw = self.spool_bytes[key]
                self.backend.flush(handle)
                self.backend.verify(handle, raw)
                self.frozen.add(key)
                value, handle.value = handle.value, None
                closed = self.backend.kernel.CloseHandle(value)
                close_error = ctypes.get_last_error() if not closed else None
                if not closed:
                    raise PublicationError("NATIVE_PUBLICATION_ERROR", "spool CloseHandle", native_error=close_error)
            for case in CASES:
                raw = self.spool_bytes[(case, "recorder.trace.spool")]
                require(validate_trace(raw, self.binding)["matched"], "unexpected recorded case", "RECORDING_INCOMPLETE")
            self.state = "CAPTURED"
        except BaseException:
            self.abort()
            raise

    def _publish_file(self, case, stage_role, target_role, raw):
        stage, target = self.paths.get(case, stage_role), self.paths.get(case, target_role)
        require(self.paths.edges.get(stage.path) == target.path, "publication edge differs")
        self.backend.require_absent(stage.path)
        self.backend.require_absent(target.path)
        handle = self.backend.create(stage.path, rename=True)
        self.backend.write_complete(handle, raw)
        self.backend.flush(handle)
        self.backend.verify(handle, raw)
        self.backend.rename_no_replace(handle, target.path)
        self.backend.flush(handle)
        self.backend.verify_final_name(handle)
        self.backend.verify(handle, raw)
        self.published.append((handle, raw))
        return {"path": target.path, "byte_count": len(raw), "raw_sha256": raw_digest(raw)}

    def publish(self):
        require_execution(self.binding)
        require(self.state == "CAPTURED", "no complete worker capture")
        self.state = "PUBLISHING"
        try:
            observations, trace_refs = [], []
            for case in CASES:
                raw = self.spool_bytes[(case, "recorder.trace.spool")]
                observation = validate_trace(raw, self.binding)
                require(observation["matched"], "case acceptance changed")
                ref = self._publish_file(case, "recorder.trace.stage", "trace", raw)
                trace_refs.append(ref)
                observations.append({"case_id": case, "raw_trace": ref, "status": "OBSERVED_COMPLETE",
                                     "first_native_failure": observation["native_failure"]})
            transcript_ref = self._publish_file(None, "recorder.transcript.stage", "transcript",
                                                self.spool_bytes[(None, "recorder.transcript.spool")])
            report = record("s2eq.platform-report.v1", platform_profile_digest=self.profile["record_digest"],
                            isolated_authorization=self.auth_ref, isolated_attempt_id=ATTEMPT,
                            publisher_sources=self.profile["publisher_sources"], recorder_sources=self.profile["recorder_sources"],
                            platform_context=self.profile["platform_context"], parent_directories=self.profile["parent_directories"],
                            process_exit_code=self.exit_code, recording_status="COMPLETE",
                            original_transcript=transcript_ref, cases=observations)
            report_ref = self._publish_file(None, "recorder.report.stage", "report", encoded(report))
            manifest = record("s2eu.recording-manifest.v1", attempt_id=ATTEMPT,
                              profile_digest=self.profile["record_digest"], run_binding_digest=self.run["record_digest"],
                              platform_report=report_ref, worker_transcript=transcript_ref, case_traces=trace_refs,
                              worker_exit_code=self.exit_code, recording_status="COMPLETE")
            manifest_raw = encoded(manifest)
            self._publish_file(None, "recorder.manifest.stage", "recording_manifest", manifest_raw)
            marker = record("s2eu.recording-marker.v1", attempt_id=ATTEMPT,
                            manifest_raw_sha256=raw_digest(manifest_raw), manifest_record_digest=manifest["record_digest"],
                            profile_digest=self.profile["record_digest"], run_binding_digest=self.run["record_digest"])
            marker_raw = encoded(marker)
            marker_handle = self.backend.create(self.paths.get(None, "recording_marker").path)
            self.backend.write_complete(marker_handle, marker_raw)
            self.backend.flush(marker_handle)
            self.backend.verify(marker_handle, marker_raw)
            for handle, raw in self.published:
                self.backend.verify(handle, raw)
            verify_sources(self.backend, self.refs)
            self.backend_closed = True
            self.backend.close_all()
            self.control.finish()
            self.state = "RECORDING_PUBLICATION_COMPLETE"
            return LiveRecordingCompletion(self.binding.identity(), manifest["record_digest"], marker["record_digest"], self.exit_code)
        except BaseException:
            self.abort()
            raise

    def abort(self):
        self.state = "INCOMPLETE"
        errors = []
        if not self.backend_closed:
            self.backend_closed = True
            try:
                self.backend.close_all()
            except BaseException as error:
                errors.append(error)
        errors.extend(self.backend.kernel.close_unrecorded_on_abort())
        if self.control.spool is not None:
            try:
                self.control.spool.close()
            except BaseException as error:
                errors.append(error)
        return tuple(errors)
