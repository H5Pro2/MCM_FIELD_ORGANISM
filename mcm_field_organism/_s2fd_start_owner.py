"""Private dispatch owner and independent starter; no import-time I/O.

The external reviewer's context is empty by default. Submitted JSON,
command-line flags and environment variables cannot grant execution.
"""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import PureWindowsPath
from threading import Lock
import base64
import subprocess

from ._s2fd_start_contract import (
    ATTEMPT, PARENTS, StartError, ValidatedPackage, canonical_path, checked,
    encoded, fields, file_ref, loads, owner_roles, record, require, sha,
    validate_admission, validate_start_package,
)

_TRUSTED_STARTS = ContextVar("s2fd_independent_start_admissions", default=frozenset())
_ATTEMPTS = set()
_ATTEMPT_LOCK = Lock()


@dataclass(frozen=True, slots=True)
class DispatchHandoff:
    package_digest: str
    admission_raw: bytes
    dispatch_raw: bytes
    seal_raw: bytes


def require_release(package, admission):
    key = (package.identity, admission["record_digest"],
           package.value()["metadata_admission"]["record_digest"])
    require(key in _TRUSTED_STARTS.get(), "independent execution admission absent", "BLOCKED_PREREQUISITE")


def consume_invocation(package, admission):
    require_release(package, admission)
    with _ATTEMPT_LOCK:
        require(ATTEMPT not in _ATTEMPTS, "invocation already consumed", "ALREADY_CONSUMED")
        _ATTEMPTS.add(ATTEMPT)


class SourceLease:
    """Retains native source handles, with a separate external-runtime path."""

    def __init__(self, package):
        from ._s2er_windows_files import WindowsFiles
        self.package, self.backend, self.closed = package, WindowsFiles(), False
        try:
            _, _, profile, _, _, _, _, _ = package.binding().values()
            self.backend.pin_parents(profile["parent_directories"])
            for path, expected in package.originals:
                self.read_exact({"path": path, "byte_count": len(expected), "raw_sha256": sha(expected)})
        except BaseException:
            self.close()
            raise

    def read_exact(self, ref):
        file_ref(ref)
        path = PureWindowsPath(ref["path"])
        if any(path.is_relative_to(PureWindowsPath(PARENTS[k])) for k in ("repository", "git_common")):
            _, raw = self.backend.read_source(str(path), ref["byte_count"])
        else:
            require(self.backend.kernel.GetDriveTypeW(path.anchor) == 3, "external runtime is not on a local fixed drive",
                    "BLOCKED_PREREQUISITE")
            for ancestor in (*reversed(path.parent.parents), path.parent):
                name = canonical_path(str(ancestor))
                if name not in self.backend.parents:
                    self.backend.parents[name] = self.backend._open(name, directory=True)
            self.backend.verify_parents()
            handle = self.backend._open(str(path))
            raw = self.backend.read(handle, ref["byte_count"])
        require(sha(raw) == ref["raw_sha256"], "native source/receipt bytes differ")
        return raw

    def revalidate(self):
        require(not self.closed, "source lease closed")
        self.backend.verify_parents()
        for handle in self.backend.handles:
            if not handle.directory and not handle.writable and handle.value is not None:
                require(self.backend.inspect(handle) == handle.identity, "retained source identity changed")

    def close(self):
        if not self.closed:
            self.closed = True
            self.backend.close_all()


def reserve_dispatch(package, admission_raw, lease):
    """Two exclusive owner files; no readable-file fallback or retry."""
    admission = validate_admission(package, admission_raw)
    require_release(package, admission)
    require(ATTEMPT in _ATTEMPTS, "dispatch without consumed invocation")
    roles, backend = owner_roles(), lease.backend
    for role in roles:
        try:
            backend.require_absent(role["path"])
        except Exception as error:
            if getattr(error, "code", None) == "PUBLICATION_ALREADY_CONSUMED":
                raise StartError("ALREADY_CONSUMED", "existing dispatch or seal") from error
            raise
    dispatch = record("dispatch", attempt_id=ATTEMPT, start_package_digest=package.identity,
                      start_admission_digest=admission["record_digest"], owner_role="completion_observer", state="CONSUMED")
    seal = record("dispatch-seal", attempt_id=ATTEMPT, start_package_digest=package.identity,
                  dispatch_record_digest=dispatch["record_digest"], state="DISPATCH_SEALED")
    handles = []
    try:
        for role, value in zip(roles, (dispatch, seal)):
            handle = backend.create(role["path"])
            handles.append(handle)
            raw = encoded(value)
            backend.write_complete(handle, raw)
            backend.flush(handle)
            backend.verify(handle, raw)
        for handle in handles:
            value, handle.value = handle.value, None
            backend._ok(backend.kernel.CloseHandle(value), "dispatch CloseHandle")
    except BaseException as error:
        raise StartError("COMPLETION_UNCONFIRMED", "dispatch persistence or close incomplete") from error
    return DispatchHandoff(package.identity, admission_raw, encoded(dispatch), encoded(seal))


def validate_handoff(package, handoff, lease):
    require(type(handoff) is DispatchHandoff and handoff.package_digest == package.identity, "foreign dispatch handoff")
    admission = validate_admission(package, handoff.admission_raw)
    dispatch = checked("dispatch", loads(handoff.dispatch_raw))
    seal = checked("dispatch-seal", loads(handoff.seal_raw))
    require(dispatch["start_package_digest"] == package.identity == seal["start_package_digest"] and
            dispatch["start_admission_digest"] == admission["record_digest"] and
            dispatch["owner_role"] == "completion_observer" and dispatch["state"] == "CONSUMED" and
            seal["state"] == "DISPATCH_SEALED" and seal["dispatch_record_digest"] == dispatch["record_digest"],
            "dispatch relation differs")
    for role, raw in zip(owner_roles(), (handoff.dispatch_raw, handoff.seal_raw)):
        lease.read_exact({"path": role["path"], "byte_count": len(raw), "raw_sha256": sha(raw)})
    return admission


def process_contract(package, role):
    return next(p for p in package.value()["process_contract"] if p["role"] == role)


def wire_package(package, handoff):
    return {"package": base64.b64encode(package.raw).decode("ascii"),
            "originals": [[p, base64.b64encode(raw).decode("ascii")] for p, raw in package.originals],
            "admission": base64.b64encode(handoff.admission_raw).decode("ascii"),
            "dispatch": base64.b64encode(handoff.dispatch_raw).decode("ascii"),
            "seal": base64.b64encode(handoff.seal_raw).decode("ascii")}


def unwire_package(value):
    fields(value, ("package", "originals", "admission", "dispatch", "seal"))

    def decode(text):
        require(type(text) is str, "base64 required")
        raw = base64.b64decode(text, validate=True)
        require(base64.b64encode(raw).decode("ascii") == text, "noncanonical base64")
        return raw

    require(type(value["originals"]) is list and all(type(row) is list and len(row) == 2
            for row in value["originals"]), "wire original rows differ")
    originals = {canonical_path(p): decode(raw) for p, raw in value["originals"]}
    require(len(originals) == len(value["originals"]), "duplicate wire source")
    package = validate_start_package(decode(value["package"]), originals)
    return package, DispatchHandoff(package.identity, decode(value["admission"]),
                                    decode(value["dispatch"]), decode(value["seal"]))


class ParentChannel:
    """Bounded pipe frames; OS ownership is checked by the outer observer."""

    def __init__(self, package, role, io):
        self.package, self.role, self.io = package, role, io
        self.contract = process_contract(package, role)
        self.sent = self.received = self.sent_bytes = self.received_bytes = 0

    def send(self, event, payload):
        raw = encoded({"event": event, "package_digest": self.package.identity, "payload": payload}) + b"\n"
        self.sent += 1
        self.sent_bytes += len(raw)
        require(self.sent <= self.contract["maximum_ipc_frames"] and
                self.sent_bytes <= self.contract["maximum_ipc_bytes"], "outbound IPC budget exceeded", "ABORTED_INCOMPLETE")
        self.io.write(raw)

    def receive(self):
        remaining = self.contract["maximum_ipc_bytes"] - self.received_bytes
        raw = self.io.line(remaining)
        self.received += 1
        self.received_bytes += len(raw)
        require(self.received <= self.contract["maximum_ipc_frames"] and raw.endswith(b"\n"), "IPC frame incomplete")
        value = fields(loads(raw[:-1]), ("event", "package_digest", "payload"))
        require(encoded(value) + b"\n" == raw and value["package_digest"] == self.package.identity,
                "IPC source identity differs")
        return value

    def expect(self, event):
        value = self.receive()
        require(value["event"] == event, "unexpected parent/child phase")
        return value["payload"]


class ChildOwner:
    """Exactly one Popen per role; no shell, ambient environment or retry."""

    def __init__(self, package):
        self.package, self.attempted, self.children, self.terminated = package, set(), {}, set()

    def spawn(self, role):
        require(role not in self.attempted, "child creation already attempted", "ALREADY_CONSUMED")
        self.attempted.add(role)
        plan = process_contract(self.package, role)
        child = subprocess.Popen(plan["argv"], cwd=plan["cwd"], env=plan["environment_allowlist"],
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 shell=False, close_fds=True, text=False, bufsize=0,
                                 creationflags=subprocess.CREATE_NO_WINDOW)
        self.children[role] = child
        return child

    def close(self):
        failures = []
        for role, child in self.children.items():
            try:
                if child.poll() is None and role not in self.terminated:
                    self.terminated.add(role)
                    child.kill()
                child.wait(timeout=process_contract(self.package, role)["shutdown_deadline_ms"] / 1000)
            except BaseException as error:
                failures.append(error)
            for pipe in (child.stdin, child.stdout, child.stderr):
                try:
                    if pipe is not None:
                        pipe.close()
                except BaseException as error:
                    failures.append(error)
            try:
                child._handle.Close()
            except BaseException as error:
                failures.append(error)
        require(not failures, "owned child closure incomplete", "COMPLETION_UNCONFIRMED")


def start_once(validated_package, original_dispatch_handoff, parent_channel):
    """Independent starter entry. No worker or recorder invocation here."""
    require(type(validated_package) is ValidatedPackage and type(parent_channel) is ParentChannel,
            "private starter boundary required")
    package = validated_package
    lease, children = SourceLease(package), ChildOwner(package)
    try:
        validate_handoff(package, original_dispatch_handoff, lease)
        require(parent_channel.expect("START") == {"role": "starter"}, "starter release differs")
        child = children.spawn("supervisor")
        parent_channel.send("CHILD", {"role": "supervisor", "source_role": "starter",
                                      "handle": int(child._handle), "pid": child.pid})
        require(parent_channel.expect("OWNED") == {"role": "supervisor"}, "supervisor ownership not admitted")
        from ._s2fd_completion_observer import NativePipeIO
        io = NativePipeIO.for_child(child, process_contract(package, "supervisor"))
        io.bootstrap(wire_package(package, original_dispatch_handoff))
        channel = ParentChannel(package, "supervisor", io)
        channel.send("START", {"role": "supervisor"})
        worker = channel.expect("CHILD")
        fields(worker, ("role", "source_role", "handle", "pid"))
        require(worker["role"] == "worker" and worker["source_role"] == "supervisor", "worker ownership differs")
        parent_channel.send("CHILD", worker)
        require(parent_channel.expect("OWNED") == {"role": "worker"}, "worker ownership not admitted")
        channel.send("OWNED", {"role": "worker"})
        result = channel.expect("RESULT")
        io.finish(child)
        require(child.returncode == 0, "supervisor exit differs", "ABORTED_INCOMPLETE")
        require(result["pipe_closures"] == ["worker"], "worker pipe closure missing")
        result = {**result, "pipe_closures": ["worker", "supervisor"]}
        lease.revalidate()
    finally:
        try:
            children.close()
        finally:
            lease.close()
    parent_channel.send("RESULT", result)
    return 0
