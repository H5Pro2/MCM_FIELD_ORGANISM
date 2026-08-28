"""Private native pipe and process observation, separate from child receipts.

Nothing is constructed or run on import. The outer caller must admit a package
independently and observe this owner's own terminal return.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
import os
import time
import base64

from ._s2fd_start_contract import (
    ATTEMPT, PARENT_ROLES, StartError, checked, digest, encoded, fields, loads,
    positive, record, require, sha, validate_admission, validate_start_package,
)
from ._s2fd_start_owner import (
    ChildOwner, ParentChannel, SourceLease, consume_invocation,
    process_contract, reserve_dispatch, wire_package,
)


class NativePipeIO:
    """Nonblocking pipes with finite byte, iteration and deadline bounds.

    No helper thread, file spool or retry of an invocation is introduced.
    Would-block polling is bounded by the admitted deadline in milliseconds.
    Unsupported nonblocking mode is a platform error, never a blocking fallback.
    """

    def __init__(self, read_fd, write_fd, error_fd, plan):
        require(os.name == "nt", "Windows pipe backend required", "BLOCKED_PREREQUISITE")
        self.read_fd, self.write_fd, self.error_fd = read_fd, write_fd, error_fd
        self.plan, self.buffer, self.eof, self.error_eof = plan, b"", False, error_fd is None
        self.read_bytes = self.write_bytes = 0
        self.remaining_polls = positive(plan["startup_deadline_ms"]) + positive(plan["completion_deadline_ms"])
        self.deadline = time.monotonic() + self.remaining_polls / 1000
        for fd in (read_fd, write_fd, error_fd):
            if fd is not None:
                os.set_blocking(fd, False)

    @classmethod
    def for_child(cls, child, plan):
        return cls(child.stdout.fileno(), child.stdin.fileno(), child.stderr.fileno(), plan)

    def _tick(self):
        require(self.remaining_polls > 0 and time.monotonic() < self.deadline,
                "IPC deadline or polling budget exhausted", "ABORTED_INCOMPLETE")
        self.remaining_polls -= 1
        time.sleep(0.001)

    def _error(self):
        if self.error_fd is not None and not self.error_eof:
            try:
                raw = os.read(self.error_fd, 1)
            except BlockingIOError:
                return
            require(not raw, "child emitted stderr", "ABORTED_INCOMPLETE")
            self.error_eof = True

    def write(self, raw):
        require(type(raw) is bytes and self.write_bytes + len(raw) <= self.plan["maximum_ipc_bytes"],
                "pipe write byte budget", "ABORTED_INCOMPLETE")
        offset = 0
        # At least one byte per successful write; all waits share _tick's cap.
        for _ in range(len(raw) + self.remaining_polls + 1):
            if offset == len(raw):
                return
            self._error()
            require(time.monotonic() < self.deadline, "pipe write deadline", "ABORTED_INCOMPLETE")
            try:
                count = os.write(self.write_fd, raw[offset:offset + 65536])
            except BlockingIOError:
                self._tick()
                continue
            require(type(count) is int and count > 0, "zero pipe write", "ABORTED_INCOMPLETE")
            offset += count
            self.write_bytes += count
        raise StartError("ABORTED_INCOMPLETE", "pipe write bound exhausted")

    def _read(self, maximum):
        self._error()
        require(time.monotonic() < self.deadline and not self.eof, "pipe EOF or deadline", "ABORTED_INCOMPLETE")
        try:
            raw = os.read(self.read_fd, min(65536, maximum))
        except BlockingIOError:
            self._tick()
            return
        if not raw:
            self.eof = True
            return
        self.read_bytes += len(raw)
        require(self.read_bytes <= self.plan["maximum_ipc_bytes"], "pipe read byte budget", "ABORTED_INCOMPLETE")
        self.buffer += raw

    def exact(self, count):
        require(type(count) is int and 0 < count <= self.plan["maximum_ipc_bytes"], "invalid pipe extent")
        for _ in range(count + self.remaining_polls + 1):
            if len(self.buffer) >= count:
                raw, self.buffer = self.buffer[:count], self.buffer[count:]
                return raw
            self._read(count - len(self.buffer))
        raise StartError("ABORTED_INCOMPLETE", "pipe extent incomplete")

    def line(self, maximum):
        positive(maximum)
        for _ in range(maximum + self.remaining_polls + 1):
            if b"\n" in self.buffer:
                line, self.buffer = self.buffer.split(b"\n", 1)
                require(len(line) + 1 <= maximum, "frame over budget")
                return line + b"\n"
            require(len(self.buffer) < maximum, "unterminated frame over budget")
            self._read(maximum - len(self.buffer))
        raise StartError("ABORTED_INCOMPLETE", "pipe frame incomplete")

    def bootstrap(self, payload):
        raw = encoded(payload)
        self.write(len(raw).to_bytes(8, "big") + raw)

    def verify_parent_origin(self):
        import msvcrt
        require(self.read_fd == 0 and self.write_fd == 1, "original caller descriptors required")
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.GetFileType.argtypes, kernel.GetFileType.restype = (wintypes.HANDLE,), wintypes.DWORD
        kernel.GetNamedPipeServerProcessId.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.ULONG))
        kernel.GetNamedPipeServerProcessId.restype = wintypes.BOOL
        handle, pid = msvcrt.get_osfhandle(self.read_fd), wintypes.ULONG()
        require(kernel.GetFileType(handle) == 3 and kernel.GetNamedPipeServerProcessId(handle, ctypes.byref(pid)) and
                pid.value == os.getppid(), "native caller pipe origin absent", "BLOCKED_PREREQUISITE")

    def finish(self, child):
        require(not self.buffer, "trailing child output")
        for _ in range(self.remaining_polls + 1):
            self._error()
            if not self.eof:
                self._read(1)
                require(not self.buffer, "extra child output")
            if self.eof and self.error_eof and child.poll() is not None:
                child.wait(timeout=max(0.001, self.deadline - time.monotonic()))
                return
            self._tick()
        raise StartError("COMPLETION_UNCONFIRMED", "process/pipe completion missing")


class ProcessEvidence:
    """Observer-owned duplicated handles, not accepted serialized handle IDs."""

    def __init__(self, package):
        self.package, self.owned, self.observations = package, {}, {}
        self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        h, d, p = wintypes.HANDLE, wintypes.DWORD, wintypes.LPVOID
        signatures = {
            "GetCurrentProcess": ((), h),
            "DuplicateHandle": ((h, h, h, ctypes.POINTER(h), d, wintypes.BOOL, d), wintypes.BOOL),
            "GetProcessId": ((h,), d),
            "GetProcessTimes": ((h, p, p, p, p), wintypes.BOOL),
            "QueryFullProcessImageNameW": ((h, d, wintypes.LPWSTR, ctypes.POINTER(d)), wintypes.BOOL),
            "WaitForSingleObject": ((h, d), d),
            "GetExitCodeProcess": ((h, ctypes.POINTER(d)), wintypes.BOOL),
            "TerminateProcess": ((h, wintypes.UINT), wintypes.BOOL),
            "CloseHandle": ((h,), wintypes.BOOL),
        }
        for name, (args, result) in signatures.items():
            function = getattr(self.kernel, name)
            function.argtypes, function.restype = args, result

    def _ok(self, result, name):
        require(bool(result), name + " failed: " + str(ctypes.get_last_error()), "COMPLETION_UNCONFIRMED")
        return result

    def _identity(self, handle, role):
        pid = self._ok(self.kernel.GetProcessId(handle), "GetProcessId")
        created, exited, kernel, user = (ctypes.c_uint64() for _ in range(4))
        self._ok(self.kernel.GetProcessTimes(handle, ctypes.byref(created), ctypes.byref(exited),
                                            ctypes.byref(kernel), ctypes.byref(user)), "GetProcessTimes")
        size = wintypes.DWORD(32768)
        name = ctypes.create_unicode_buffer(size.value)
        self._ok(self.kernel.QueryFullProcessImageNameW(handle, 0, name, ctypes.byref(size)), "process image")
        require(name.value == process_contract(self.package, role)["interpreter_file"]["path"], "process runtime differs")
        return {"pid": pid, "creation_filetime": created.value, "image_path": name.value}

    def adopt(self, role, source_role, native_value, pid):
        require(role in PARENT_ROLES and source_role == PARENT_ROLES[role] and role not in self.owned,
                "unexpected or repeated process adoption")
        positive(native_value)
        positive(pid)
        source = self.kernel.GetCurrentProcess() if source_role == "completion_observer" else self.owned[source_role]["handle"]
        handle = wintypes.HANDLE()
        self._ok(self.kernel.DuplicateHandle(source, native_value, self.kernel.GetCurrentProcess(),
                                            ctypes.byref(handle), 0, False, 2), "DuplicateHandle")
        # Register ownership before any validation that can fail.
        self.owned[role] = {"handle": handle.value, "identity": None, "terminated": False, "closed": False}
        identity = self._identity(handle.value, role)
        require(identity["pid"] == pid and all(identity != v["identity"] for k, v in self.owned.items() if k != role),
                "process identity differs or repeats")
        self.owned[role]["identity"] = identity

    def finish(self, role, pipe_eof):
        item = self.owned[role]
        plan = process_contract(self.package, role)
        require(self.kernel.WaitForSingleObject(item["handle"], plan["shutdown_deadline_ms"]) == 0,
                "process not terminal", "COMPLETION_UNCONFIRMED")
        identity = self._identity(item["handle"], role)
        require(identity == item["identity"], "process creation identity changed")
        code = wintypes.DWORD()
        self._ok(self.kernel.GetExitCodeProcess(item["handle"], ctypes.byref(code)), "GetExitCodeProcess")
        item["closed"] = True
        self._ok(self.kernel.CloseHandle(item["handle"]), "observer CloseHandle")
        observation = record("process-observation", role=role, package_digest=self.package.identity,
                             parent_role=PARENT_ROLES[role], owned_handle_generation="s2em.002." + role,
                             creation_identity=identity, exit_code=code.value,
                             pipe_eof_confirmed=pipe_eof, close_status="CONFIRMED")
        self.observations[role] = observation
        return observation

    def close(self):
        errors = []
        for role in reversed(tuple(self.owned)):
            item = self.owned[role]
            if item["closed"]:
                continue
            try:
                wait = self.kernel.WaitForSingleObject(item["handle"], 0)
                require(wait in (0, 258), "process wait error", "COMPLETION_UNCONFIRMED")
                if wait == 258 and not item["terminated"]:
                    item["terminated"] = True
                    self._ok(self.kernel.TerminateProcess(item["handle"], 1), "TerminateProcess")
                require(self.kernel.WaitForSingleObject(item["handle"],
                        process_contract(self.package, role)["shutdown_deadline_ms"]) == 0, "termination not observed")
            except BaseException as error:
                errors.append(error)
            finally:
                item["closed"] = True
                try:
                    self._ok(self.kernel.CloseHandle(item["handle"]), "observer close")
                except BaseException as error:
                    errors.append(error)
        require(not errors, "observer cleanup incomplete", "COMPLETION_UNCONFIRMED")


def validate_observed_completion(package, process_evidence, original_receipts):
    """Use only this observer's native observations plus original published bytes."""
    require(type(process_evidence) is ProcessEvidence and process_evidence.package is package,
            "observer-owned process evidence required")
    observations = process_evidence.observations
    require(set(observations) == set(PARENT_ROLES), "missing independently observed child")
    for role in PARENT_ROLES:
        row = checked("process-observation", observations[role])
        require(row["package_digest"] == package.identity and type(row["exit_code"]) is int and
                row["exit_code"] == 0 and row["pipe_eof_confirmed"] is True and row["close_status"] == "CONFIRMED",
                "child completion not confirmed", "COMPLETION_UNCONFIRMED")
    fields(original_receipts, ("live_completion", "manifest_file", "marker_file", "control_file", "raw_files"))
    binding = package.binding()
    _, _, profile, run, _, _, _, paths = binding.values()
    originals = original_receipts["raw_files"]
    from ._s2fd_start_contract import original
    from ._s2ex_recorder_trace import validate_control, validate_trace
    manifest = loads(original(original_receipts["manifest_file"], originals))
    marker = loads(original(original_receipts["marker_file"], originals))
    control = original(original_receipts["control_file"], originals)
    for key, role in (("manifest_file", "recording_manifest"), ("marker_file", "recording_marker"),
                      ("control_file", "recorder.control.spool")):
        require(original_receipts[key]["path"] == paths.get(None, role).path, "receipt path role differs")
    fields(manifest, ("schema_version", "attempt_id", "profile_digest", "run_binding_digest", "platform_report",
                      "worker_transcript", "case_traces", "worker_exit_code", "recording_status", "record_digest"))
    fields(marker, ("schema_version", "attempt_id", "manifest_raw_sha256", "manifest_record_digest",
                    "profile_digest", "run_binding_digest", "record_digest"))
    for value in (manifest, marker):
        require(value["record_digest"] == digest({k: v for k, v in value.items() if k != "record_digest"}) and
                value["attempt_id"] == ATTEMPT and value["profile_digest"] == profile["record_digest"] and
                value["run_binding_digest"] == run["record_digest"], "receipt source/digest differs")
    require(manifest["schema_version"] == "s2eu.recording-manifest.v1" and manifest["recording_status"] == "COMPLETE" and
            type(manifest["worker_exit_code"]) is int and manifest["worker_exit_code"] == 0, "manifest incomplete")
    require(marker["schema_version"] == "s2eu.recording-marker.v1" and
            marker["manifest_record_digest"] == manifest["record_digest"] and
            marker["manifest_raw_sha256"] == original_receipts["manifest_file"]["raw_sha256"], "marker differs")
    live = fields(original_receipts["live_completion"], ("binding_digest", "manifest_digest", "marker_digest", "worker_exit_code"))
    require(live == {"binding_digest": binding.identity(), "manifest_digest": manifest["record_digest"],
                     "marker_digest": marker["record_digest"], "worker_exit_code": 0}, "live completion differs")
    require(len(manifest["case_traces"]) == 13, "trace count differs")
    traces = []
    for index, ref in enumerate(manifest["case_traces"], 1):
        require(ref["path"] == paths.get(f"p{index:02d}", "trace").path, "trace order/path differs")
        trace = original(ref, originals)
        require(validate_trace(trace, binding)["matched"], "trace validation failed")
        traces.append(trace)
    require(manifest["worker_transcript"]["path"] == paths.get(None, "transcript").path and
            manifest["platform_report"]["path"] == paths.get(None, "report").path, "report/transcript role differs")
    transcript = original(manifest["worker_transcript"], originals)
    require(transcript.endswith(b"\n"), "incomplete transcript")
    streams = {"stdout": [], "stderr": []}
    for index, line in enumerate(transcript.splitlines(), 1):
        frame = fields(loads(line), ("sequence", "channel", "bytes_base64"))
        require(encoded(frame) == line and type(frame["sequence"]) is int and frame["sequence"] == index and
                frame["channel"] in streams and type(frame["bytes_base64"]) is str, "transcript frame differs")
        raw = base64.b64decode(frame["bytes_base64"], validate=True)
        require(raw and base64.b64encode(raw).decode("ascii") == frame["bytes_base64"], "transcript base64 differs")
        streams[frame["channel"]].append(raw)
    require(b"".join(streams["stdout"]) == b"".join(traces) and not streams["stderr"],
            "original worker streams differ from published traces")
    report_raw = original(manifest["platform_report"], originals)
    report = fields(loads(report_raw), ("schema_version", "platform_profile_digest", "isolated_authorization",
        "isolated_attempt_id", "publisher_sources", "recorder_sources", "platform_context", "parent_directories",
        "process_exit_code", "recording_status", "original_transcript", "cases", "record_digest"))
    require(report["schema_version"] == "s2eq.platform-report.v1" and report["record_digest"] ==
            digest({k: v for k, v in report.items() if k != "record_digest"}) and encoded(report) == report_raw,
            "report digest/schema differs")
    require(report["platform_profile_digest"] == profile["record_digest"] and report["isolated_attempt_id"] == ATTEMPT and
            report["isolated_authorization"] == package.value()["envelope_files"]["authorization_raw"] and
            report["original_transcript"] == manifest["worker_transcript"] and report["recording_status"] == "COMPLETE" and
            type(report["process_exit_code"]) is int and report["process_exit_code"] == 0, "report binding differs")
    for key in ("publisher_sources", "recorder_sources", "platform_context", "parent_directories"):
        require(report[key] == profile[key], "report provenance differs")
    require(type(report["cases"]) is list and len(report["cases"]) == 13, "report case count differs")
    for index, (row, trace, ref) in enumerate(zip(report["cases"], traces, manifest["case_traces"]), 1):
        observation = validate_trace(trace, binding)
        require(row == {"case_id": f"p{index:02d}", "raw_trace": ref, "status": "OBSERVED_COMPLETE",
                        "first_native_failure": observation["native_failure"]}, "report case projection differs")
    validate_control(control, binding)
    return tuple(observations[role] for role in PARENT_ROLES)


def observe_once(validated_package, admitted_grant, owned_parent_channel):
    """Externally admitted single invocation; never publish a success JSON file.

    The caller supplies its owned terminal-return channel and must observe our
    real exit as the explicit trust root. It is not a child-reported Boolean.
    """
    package = validate_start_package(validated_package.raw, dict(validated_package.originals))
    admission = validate_admission(package, admitted_grant)
    consume_invocation(package, admission)
    require(type(owned_parent_channel) is NativePipeIO and owned_parent_channel.read_fd == 0 and
            owned_parent_channel.write_fd == 1, "owned original caller pipe absent", "BLOCKED_PREREQUISITE")
    lease = children = evidence = None
    handoff = result = observations = None
    status, detail = "ABORTED_INCOMPLETE", "incomplete invocation"
    try:
        owned_parent_channel.verify_parent_origin()
        lease = SourceLease(package)
        handoff = reserve_dispatch(package, admitted_grant, lease)
        children, evidence = ChildOwner(package), ProcessEvidence(package)
        starter = children.spawn("starter")
        evidence.adopt("starter", "completion_observer", int(starter._handle), starter.pid)
        io = NativePipeIO.for_child(starter, process_contract(package, "starter"))
        io.bootstrap(wire_package(package, handoff))
        channel = ParentChannel(package, "starter", io)
        channel.send("START", {"role": "starter"})
        for role in ("supervisor", "worker"):
            child = channel.expect("CHILD")
            fields(child, ("role", "source_role", "handle", "pid"))
            require(child["role"] == role and child["source_role"] == PARENT_ROLES[role], "child order differs")
            evidence.adopt(role, child["source_role"], child["handle"], child["pid"])
            channel.send("OWNED", {"role": role})
        result = channel.expect("RESULT")
        fields(result, ("live_completion", "manifest_file", "marker_file", "control_file", "pipe_closures"))
        io.finish(starter)
        require(result["pipe_closures"] == ["worker", "supervisor"], "nested pipe closure receipts absent")
        for role in ("worker", "supervisor", "starter"):
            evidence.finish(role, True)
        raw_files = {}
        binding = package.binding()
        paths = binding.values()[-1]
        from ._s2fd_start_contract import file_ref

        def accept_ref(ref, path, ceiling):
            file_ref(ref)
            require(ref["path"] == path and ref["byte_count"] <= ceiling, "receipt role or extent differs")
            return ref

        for key in ("manifest_file", "marker_file", "control_file"):
            role = {"manifest_file": "recording_manifest", "marker_file": "recording_marker",
                    "control_file": "recorder.control.spool"}[key]
            ref = accept_ref(result[key], paths.get(None, role).path, binding.limits.stream_bytes)
            raw_files[ref["path"]] = lease.read_exact(ref)
        manifest = loads(raw_files[result["manifest_file"]["path"]])
        require(type(manifest["case_traces"]) is list and len(manifest["case_traces"]) == 13, "manifest trace list differs")
        remaining_refs = [accept_ref(manifest["platform_report"], paths.get(None, "report").path, binding.limits.stream_bytes),
                          accept_ref(manifest["worker_transcript"], paths.get(None, "transcript").path, binding.limits.stream_bytes)]
        remaining_refs.extend(accept_ref(ref, paths.get(f"p{index:02d}", "trace").path, binding.limits.trace_bytes)
                              for index, ref in enumerate(manifest["case_traces"], 1))
        for ref in remaining_refs:
            raw_files[ref["path"]] = lease.read_exact(ref)
        observations = validate_observed_completion(package, evidence,
                            {k: v for k, v in result.items() if k != "pipe_closures"} | {"raw_files": raw_files})
        lease.revalidate()
        status, detail = "ISOLATED_RECORDING_COMPLETE", None
    except BaseException as error:
        status = error.status if isinstance(error, StartError) else "ABORTED_INCOMPLETE"
        detail = type(error).__name__ + ": " + str(error)
    finally:
        for owner in (evidence, children, lease):
            if owner is not None:
                try:
                    owner.close()
                except BaseException as error:
                    status, detail = "COMPLETION_UNCONFIRMED", "owner closure: " + str(error)
    success = status == "ISOLATED_RECORDING_COMPLETE"
    if not success:
        missing = ["worker_exit_code", "supervisor_exit_code", "starter_exit_code", "live_completion",
                   "manifest_file", "marker_file", "control_file"]
        if not handoff:
            missing.append("dispatch_seal_digest")
        if not observations:
            missing.append("process_observations")
        detail = (detail or "completion not confirmed") + "; missing evidence: " + ", ".join(missing)
    completion = record("observed-completion", attempt_id=ATTEMPT, start_package_digest=package.identity,
        dispatch_seal_digest=loads(handoff.seal_raw)["record_digest"] if handoff else None,
        process_observations=list(observations) if observations else None,
        worker_exit_code=0 if success else None, supervisor_exit_code=0 if success else None,
        starter_exit_code=0 if success else None, live_completion=result["live_completion"] if success else None,
        manifest_file=result["manifest_file"] if success else None, marker_file=result["marker_file"] if success else None,
        control_file=result["control_file"] if success else None, control_close_observed=success,
        status=status, failure_detail=detail)
    # Return only. The caller must not turn mere receipt of this value into
    # proof of our own terminal exit; no observer-owned output path is added.
    return completion
