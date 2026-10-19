"""Private S2-FQ caller. Implementation only; every entry remains blocked.

No CLI, project imports, output, persistence, recorder or child processes.
The immutable binding is descriptive, NOT a source of launch authority.
An independent pre-import source/runtime admission is still missing.
_execution_authorization() deliberately cannot grant execution. Replacing it
requires separate authorization and a fresh source digest/review, not merely
removing a guard. Actual live admission and reload-resistant consumption are
external prerequisites; the descriptive digest fields cannot supply them.

Source identity is the SHA-256 of the complete raw file, supplied by an
independent review. Embedding that digest in these same bytes would be cyclic.
The nine historical runtime pins below are minimum expectations, not evidence
of the current runtime or a complete dependency closure. Additional loaded
modules and their ancestors must be explicitly bound before any payload read.

9184 bytes bound ONLY the payload. resource_plan() separately derives source
read volume, handles, explicit native calls, validation input cardinalities and
bounded trace length. Buffer bytes are not total Python/native resident memory.
Deadlines are checked before/after synchronous calls, not hard cancellation.
Whole-runtime memory and blocking-call latency remain unproven prerequisites;
this file cannot establish S2-FC readiness or its own future process exit.

Static review must parse this file without importing/executing it. Do not read
the S2-FB payload merely to audit this source. Its expected bytes are inherited.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import PureWindowsPath
import sys
import threading
import time


CALLER_PATH = r"C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\tools\_s2fq_readonly_bootstrap_caller.py"
PAYLOAD_PATH = r"C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\docs\S2FB_STATISCHER_NATIVER_LAYOUTVERTRAG_V1.json"
PAYLOAD_BYTES = 9184
PAYLOAD_SHA256 = "3dd1bc35bf8fc8f8242475f3264484878f730a99b43494a67700b09a5c79ad58"
INTERPRETER_PATH = r"C:\Python314\python.exe"
RUNTIME_VERSION = (3, 14, 4)
CHUNK_BYTES = 65536
MAX_FILES = 128
MAX_PARENTS = 128
MAX_MODULES = 256
MAX_PATH_CHARS = 1024
MAX_FILE_BYTES = 16 * 1024 * 1024
MAX_SOURCE_BYTES = 64 * 1024 * 1024
MAX_PHASE_MS = 60000

# These are inherited expectations from S2-FC, not newly collected metadata.
RUNTIME_PINS = (
    (r"C:\Python314\python.exe", 106328, "7ca24f26d6e3f463419ee4f537ddd3acd312c38fe45e678cce08572f26a8bd1a"),
    (r"C:\Python314\python3.dll", 74072, "1dd696f02326e32e67b52c25b249b3acce3238176212d16e8fb1a050a1455ae9"),
    (r"C:\Python314\python314.dll", 6767440, "a07f7d09c3121492bb066535c6d0811df5fbc2090cbca7031a97bb47ce1480c9"),
    (r"C:\Python314\vcruntime140.dll", 120400, "052ad6a20d375957e82aa6a3c441ea548d89be0981516ca7eb306e063d5027f4"),
    (r"C:\Python314\vcruntime140_1.dll", 49776, "6a99bc0128e0c7d6cbbf615fcc26909565e17d4ca3451b97f8987f9c6acbc6c8"),
    (r"C:\Python314\DLLs\_ctypes.pyd", 142680, "79967d8614f735cc62b81649641fd8d0414ca66d3d6656fa7788334bbdbbd35b"),
    (r"C:\Python314\Lib\ctypes\__init__.py", 22814, "8c16b1320357ccfac6cc4b6d08e6d61b5dfb8bc700877b35fb711a840d65aecd"),
    (r"C:\Python314\Lib\ctypes\wintypes.py", 5963, "22948fd71cff56589e80eba0c9e41e34b21a341920e261e3bbf2839fe6c1f1fe"),
    (r"C:\Python314\include\patchlevel.h", 1822, "c6a0f36b6ef0213e2c611f0a1409f6583b3b0cfd9c0ddcea015384c37fa4ed06"),
)


class _Stop(Exception):
    def __init__(self, code: str, operation: str, native_error: int | None = None):
        self.code = code
        self.operation = operation
        self.native_error = native_error
        super().__init__(code, operation, native_error)


def _require(condition: bool, operation: str, code: str = "BINDING_REJECTED") -> None:
    if not condition:
        raise _Stop(code, operation)


def _execution_authorization() -> None:
    # No caller argument, environment variable or serialized receipt can unlock it.
    raise _Stop("BLOCKED_PREREQUISITE", "independent execution admission absent")


@dataclass(frozen=True, slots=True)
class FileIdentity:
    volume_serial: int
    file_id: bytes
    size: int
    last_write: int


@dataclass(frozen=True, slots=True)
class Artifact:
    path: str
    byte_count: int
    sha256: str
    identity: FileIdentity


@dataclass(frozen=True, slots=True)
class Parent:
    path: str
    identity: FileIdentity


@dataclass(frozen=True, slots=True)
class ProcessIdentity:
    pid: int
    creation_filetime: int
    image_path: str


@dataclass(frozen=True, slots=True)
class ModuleOrigin:
    name: str
    origin: str


@dataclass(frozen=True, slots=True)
class Binding:
    invocation_id: str
    authorization_digest: str
    preimport_provenance_digest: str
    process: ProcessIdentity
    caller: Artifact
    dependencies: tuple[Artifact, ...]
    parents: tuple[Parent, ...]
    modules: tuple[ModuleOrigin, ...]
    payload_identity: FileIdentity
    phase_ms: int
    cleanup_ms: int


@dataclass(frozen=True, slots=True)
class ResourcePlan:
    source_bytes: int
    source_read_calls: int
    payload_read_calls: int
    handles: int
    native_calls: int
    close_calls: int
    module_scans: int
    validation_input_rows: int
    byte_buffer_ceiling: int
    trace_entries: int
    hard_time_bound_proven: bool = False
    resident_memory_bound_proven: bool = False
    full_validation_work_bound_proven: bool = False


@dataclass(frozen=True, slots=True)
class Event:
    sequence: int
    phase: str
    operation: str
    resource: str
    native_error: int | None
    returned: int | None


@dataclass(slots=True)
class _OwnedHandle:
    value: int | None
    resource: str


@dataclass(frozen=True, slots=True)
class Failure:
    code: str
    operation: str
    native_error: int | None


@dataclass(frozen=True, slots=True)
class Finding:
    status: str
    invocation_id: str | None
    binding_digest: str | None
    caller_identity: ProcessIdentity | None
    payload_identity: FileIdentity | None
    payload_digest: str | None
    payload_bytes: int
    plan: ResourcePlan | None
    native_calls: int
    primary_failure: Failure | None
    cleanup_failures: tuple[Failure, ...]
    events: tuple[Event, ...]
    platform_proof: bool = False
    observer_return: bool = False


def _hex(value: str) -> None:
    _require(type(value) is str and len(value) == 64
             and all(c in "0123456789abcdef" for c in value), "sha256 shape")


def _integer(value: int, minimum: int, maximum: int, label: str) -> None:
    _require(type(value) is int and minimum <= value <= maximum, label)


def _path(value: str) -> None:
    _require(type(value) is str and 3 <= len(value) <= MAX_PATH_CHARS, "path extent")
    _require("\x00" not in value and "/" not in value, "path characters")
    path = PureWindowsPath(value)
    _require(path.is_absolute() and path.drive == "C:" and str(path) == value
             and ".." not in path.parts and ":" not in value[2:], "canonical local path")
    _require(all(not p.endswith((" ", ".")) for p in path.parts[1:]), "path suffix")


def _identity(value: FileIdentity, *, directory: bool = False) -> None:
    _require(type(value) is FileIdentity, "file identity type")
    _integer(value.volume_serial, 0, (1 << 64) - 1, "volume serial")
    _require(type(value.file_id) is bytes and len(value.file_id) == 16, "file id")
    _integer(value.size, 0, MAX_FILE_BYTES, "file size")
    _integer(value.last_write, 0, (1 << 64) - 1, "last write")
    if directory:
        _require(value.size == 0 and value.last_write == 0, "directory identity fields")


def _validate(binding: Binding) -> tuple[Artifact, ...]:
    _require(type(binding) is Binding, "binding type")
    _require(type(binding.invocation_id) is str and 1 <= len(binding.invocation_id) <= 64
             and all(c in "abcdefghijklmnopqrstuvwxyz0123456789.-" for c in binding.invocation_id),
             "invocation id")
    _hex(binding.authorization_digest)
    _hex(binding.preimport_provenance_digest)
    _require(type(binding.process) is ProcessIdentity, "process identity type")
    _integer(binding.process.pid, 1, (1 << 32) - 1, "pid")
    _integer(binding.process.creation_filetime, 1, (1 << 64) - 1, "creation time")
    _require(type(binding.process.image_path) is str
             and binding.process.image_path == INTERPRETER_PATH, "process image binding")
    _require(type(binding.dependencies) is tuple and len(binding.dependencies) < MAX_FILES,
             "dependency count")
    _require(type(binding.parents) is tuple and 0 < len(binding.parents) <= MAX_PARENTS,
             "parent count")
    _require(type(binding.modules) is tuple and 0 < len(binding.modules) <= MAX_MODULES,
             "module count")
    artifacts = (binding.caller,) + binding.dependencies
    paths = []
    for artifact in artifacts:
        _require(type(artifact) is Artifact, "artifact type")
        _path(artifact.path)
        _identity(artifact.identity)
        _hex(artifact.sha256)
        _integer(artifact.byte_count, 1, MAX_FILE_BYTES, "artifact length")
        _require(artifact.identity.size == artifact.byte_count, "artifact identity size")
        _require(artifact.path == CALLER_PATH or
                 PureWindowsPath(artifact.path).is_relative_to(PureWindowsPath(r"C:\Python314")),
                 "source outside private caller/runtime")
        _require(artifact.path != PAYLOAD_PATH, "payload cannot be bootstrap source")
        paths.append(artifact.path)
    _require(binding.caller.path == CALLER_PATH and len(set(paths)) == len(paths), "source roles")
    _require(sum(a.byte_count for a in artifacts) <= MAX_SOURCE_BYTES, "source byte ceiling")
    actual_pins = {(a.path, a.byte_count, a.sha256) for a in artifacts}
    _require(all(pin in actual_pins for pin in RUNTIME_PINS), "minimum runtime pins missing")
    required_parents = set()
    for path in paths + [PAYLOAD_PATH]:
        required_parents.update(str(p) for p in PureWindowsPath(path).parents)
    parent_paths = []
    for parent in binding.parents:
        _require(type(parent) is Parent, "parent type")
        _path(parent.path)
        _identity(parent.identity, directory=True)
        parent_paths.append(parent.path)
    expected_order = sorted(required_parents, key=lambda p: (len(PureWindowsPath(p).parts), p))
    _require(parent_paths == expected_order, "exact ancestor closure/order")
    names = []
    for module in binding.modules:
        _require(type(module) is ModuleOrigin and type(module.name) is str
                 and 0 < len(module.name) <= 128 and type(module.origin) is str, "module shape")
        _require(module.origin in ("built-in", "frozen") or module.origin in paths,
                 "unbound module origin")
        names.append(module.name)
    _require(names == sorted(set(names)), "module name order")
    _identity(binding.payload_identity)
    _require(binding.payload_identity.size == PAYLOAD_BYTES, "payload extent")
    _integer(binding.phase_ms, 1, MAX_PHASE_MS, "phase deadline")
    _integer(binding.cleanup_ms, 1, MAX_PHASE_MS, "cleanup deadline")
    return artifacts


def resource_plan(binding: Binding) -> ResourcePlan:
    """Pure derivation, not a grant or a hard CPU/RSS/latency certificate."""
    artifacts = _validate(binding)
    files, parents = len(artifacts), len(binding.parents)
    reads = sum((a.byte_count + CHUNK_BYTES - 1) // CHUNK_BYTES for a in artifacts)
    handles = parents + files + 2  # ancestors, sources, payload, real process
    # File inspect: 4 identity calls + size + position. Directory inspect: 5.
    # Each source: open, inspect, reads, inspect; all rechecked before payload.
    # Process: current PID/open plus three identity calls at three boundaries.
    calls = 11 + 16 * parents + 19 * files + reads + 20 + handles
    return ResourcePlan(sum(a.byte_count for a in artifacts), reads, 1, handles,
                        calls, handles, 2, files + parents + 3 * MAX_MODULES,
                        2 * CHUNK_BYTES + 2 * PAYLOAD_BYTES + 4 * (MAX_PATH_CHARS + 5) + 1024,
                        calls)


def _binding_digest(binding: Binding) -> str:
    # Length-delimited closed primitive fields; no repr, pickle or payload data.
    digest = hashlib.sha256()

    def put(value: str | int | bytes) -> None:
        if type(value) is str:
            tag, raw = b"s", value.encode("utf-8")
        elif type(value) is int:
            tag, raw = b"i", str(value).encode("ascii")
        else:
            tag, raw = b"b", value
        digest.update(tag + len(raw).to_bytes(8, "big") + raw)

    def identity(value: FileIdentity) -> None:
        for item in (value.volume_serial, value.file_id, value.size, value.last_write):
            put(item)

    for item in ("s2fq.binding.v1", binding.invocation_id, binding.authorization_digest,
                 binding.preimport_provenance_digest, binding.process.pid,
                 binding.process.creation_filetime, binding.process.image_path):
        put(item)
    artifacts = (binding.caller,) + binding.dependencies
    put(len(artifacts))
    for item in artifacts:
        for value in (item.path, item.byte_count, item.sha256):
            put(value)
        identity(item.identity)
    put(len(binding.parents))
    for item in binding.parents:
        put(item.path)
        identity(item.identity)
    put(len(binding.modules))
    for item in binding.modules:
        put(item.name)
        put(item.origin)
    put(PAYLOAD_PATH)
    put(PAYLOAD_SHA256)
    identity(binding.payload_identity)
    put(binding.phase_ms)
    put(binding.cleanup_ms)
    return digest.hexdigest()


class _Native:
    """Only query/open-existing/read/close; constructed behind the closed gate."""

    def __init__(self, binding: Binding, plan: ResourcePlan):
        _execution_authorization()
        import ctypes
        from ctypes import wintypes

        _require(sys.platform == "win32" and ctypes.sizeof(ctypes.c_void_p) == 8
                 and ctypes.sizeof(wintypes.WCHAR) == 2, "native ABI", "BLOCKED_PREREQUISITE")
        self.c, self.w, self.binding, self.plan = ctypes, wintypes, binding, plan
        self.events: list[Event] = []
        self.handles: list[_OwnedHandle] = []
        self.calls = 0
        self.phase = "PREPARE"
        self.payload_ready = False
        self.payload_consumed = False
        self.deadline = time.monotonic_ns() + binding.phase_ms * 1_000_000
        self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        h, d, p = wintypes.HANDLE, wintypes.DWORD, wintypes.LPVOID
        signatures = {
            "GetCurrentProcessId": ((), d),
            "OpenProcess": ((d, wintypes.BOOL, d), h),
            "GetProcessId": ((h,), d),
            "GetProcessTimes": ((h, p, p, p, p), wintypes.BOOL),
            "QueryFullProcessImageNameW": ((h, d, wintypes.LPWSTR, ctypes.POINTER(d)), wintypes.BOOL),
            "CreateFileW": ((wintypes.LPCWSTR, d, d, p, d, d, h), h),
            "GetFileInformationByHandle": ((h, p), wintypes.BOOL),
            "GetFileInformationByHandleEx": ((h, ctypes.c_int, p, d), wintypes.BOOL),
            "GetVolumeInformationByHandleW": ((h, wintypes.LPWSTR, d, p, p, p, wintypes.LPWSTR, d), wintypes.BOOL),
            "GetFinalPathNameByHandleW": ((h, wintypes.LPWSTR, d, d), d),
            "GetFileSizeEx": ((h, ctypes.POINTER(ctypes.c_longlong)), wintypes.BOOL),
            "SetFilePointerEx": ((h, ctypes.c_longlong, ctypes.POINTER(ctypes.c_longlong), d), wintypes.BOOL),
            "ReadFile": ((h, p, d, ctypes.POINTER(d), p), wintypes.BOOL),
            "CloseHandle": ((h,), wintypes.BOOL),
        }
        self.functions = {}
        for name, (args, result) in signatures.items():
            function = getattr(self.kernel, name)
            function.argtypes, function.restype = args, result
            self.functions[name] = function

    def _call(self, name: str, resource: str, *args, acquire: bool = False,
              cleanup: bool = False) -> int:
        _require(name in self.functions, "native operation not allowed")
        _require(acquire == (name in ("OpenProcess", "CreateFileW"))
                 and cleanup == (name == "CloseHandle"), "native operation role")
        if not cleanup:
            _require(time.monotonic_ns() <= self.deadline, "phase deadline", "ABORTED_INCOMPLETE")
            _require(self.calls < self.plan.native_calls - self.plan.close_calls,
                     "native operation budget", "ABORTED_INCOMPLETE")
        else:
            _require(self.calls < self.plan.native_calls, "reserved cleanup budget", "COMPLETION_UNCONFIRMED")
        self.calls += 1
        returned, error = None, None
        owned = None
        if acquire:
            _require(len(self.handles) < self.plan.handles, "owned handle ceiling")
            owned = _OwnedHandle(None, resource)
            self.handles.append(owned)
        try:
            returned = self.functions[name](*args)
            invalid = not returned or (name == "CreateFileW" and returned == self.c.c_void_p(-1).value)
            if owned is not None and not invalid:
                # The ownership slot exists before the native acquisition.
                owned.value = returned
            error = self.c.get_last_error()
            if invalid:
                code = "BLOCKED_PREREQUISITE" if self.phase == "PREPARE" else "ABORTED_INCOMPLETE"
                if cleanup:
                    code = "COMPLETION_UNCONFIRMED"
                raise _Stop(code, name, error)
            error = None
        finally:
            self.events.append(Event(self.calls, self.phase, name, resource, error, returned))
        _require(time.monotonic_ns() <= self.deadline, "native call exceeded deadline",
                 "COMPLETION_UNCONFIRMED" if cleanup else "ABORTED_INCOMPLETE")
        return returned

    def process_handle(self) -> int:
        pid = self._call("GetCurrentProcessId", "caller")
        _require(pid == self.binding.process.pid, "caller PID before process open")
        return self._call("OpenProcess", "caller", 0x1000, False, pid, acquire=True)

    def process_identity(self, handle: int) -> ProcessIdentity:
        self._owned(handle, "caller")
        pid = self._call("GetProcessId", "caller", handle)
        created, exited, kernel, user = (self.c.c_uint64() for _ in range(4))
        self._call("GetProcessTimes", "caller", handle, self.c.byref(created),
                   self.c.byref(exited), self.c.byref(kernel), self.c.byref(user))
        capacity = self.w.DWORD(MAX_PATH_CHARS + 1)
        name = self.c.create_unicode_buffer(capacity.value)
        self._call("QueryFullProcessImageNameW", "caller", handle, 0, name, self.c.byref(capacity))
        _require(0 < capacity.value <= MAX_PATH_CHARS, "process image extent")
        return ProcessIdentity(pid, created.value, name.value)

    def open_existing(self, path: str, *, directory: bool = False) -> int:
        if directory:
            permitted = any(parent.path == path for parent in self.binding.parents)
        else:
            permitted = path == PAYLOAD_PATH or any(
                artifact.path == path for artifact in (self.binding.caller,) + self.binding.dependencies)
        _require(permitted, "path outside admitted preparation roles")
        flags = 0x00200000 | (0x02000000 if directory else 0)
        # GENERIC_READ, FILE_SHARE_READ, OPEN_EXISTING; no write/delete sharing.
        return self._call("CreateFileW", path, path, 0x80000000, 1, None, 3, flags, None, acquire=True)

    def inspect(self, handle: int, path: str, *, directory: bool = False,
                position: int = 0) -> FileIdentity:
        self._owned(handle, path)
        c, w = self.c, self.w

        class FileId(c.Structure):
            _fields_ = [("serial", c.c_ulonglong), ("identifier", c.c_ubyte * 16)]

        class FileInfo(c.Structure):
            _fields_ = [("attributes", w.DWORD), ("creation", w.FILETIME), ("access", w.FILETIME),
                        ("write", w.FILETIME), ("serial", w.DWORD), ("size_high", w.DWORD),
                        ("size_low", w.DWORD), ("links", w.DWORD), ("index_high", w.DWORD),
                        ("index_low", w.DWORD)]

        _require(c.sizeof(FileId) == 24 and FileId.identifier.offset == 8
                 and c.sizeof(FileInfo) == 52, "native file layout", "BLOCKED_PREREQUISITE")
        info, file_id = FileInfo(), FileId()
        self._call("GetFileInformationByHandle", path, handle, c.byref(info))
        _require(not info.attributes & 0x400 and bool(info.attributes & 0x10) == directory,
                 "reparse/unexpected type")
        _require(directory or info.links == 1, "hardlink not admitted")
        self._call("GetFileInformationByHandleEx", path, handle, 18, c.byref(file_id), c.sizeof(file_id))
        filesystem = c.create_unicode_buffer(261)
        self._call("GetVolumeInformationByHandleW", path, handle, None, 0, None, None, None,
                   filesystem, len(filesystem))
        _require(filesystem.value == "NTFS", "filesystem", "BLOCKED_PREREQUISITE")
        name = c.create_unicode_buffer(MAX_PATH_CHARS + 5)
        count = self._call("GetFinalPathNameByHandleW", path, handle, name, len(name), 0)
        _require(count < len(name) and name.value == "\\\\?\\" + path, "exact native path")
        if directory:
            case = w.DWORD()
            self._call("GetFileInformationByHandleEx", path, handle, 23, c.byref(case), c.sizeof(case))
            _require(case.value == 0, "case-sensitive parent not admitted")
            return FileIdentity(file_id.serial, bytes(file_id.identifier), 0, 0)
        size, cursor = c.c_longlong(), c.c_longlong()
        self._call("GetFileSizeEx", path, handle, c.byref(size))
        # FILE_CURRENT with zero displacement is a position query, not a seek.
        self._call("SetFilePointerEx", path, handle, 0, c.byref(cursor), 1)
        _require(cursor.value == position, "file offset")
        stamp = (info.write.dwHighDateTime << 32) | info.write.dwLowDateTime
        return FileIdentity(file_id.serial, bytes(file_id.identifier), size.value, stamp)

    def _owned(self, handle: int, resource: str) -> None:
        _require(type(handle) is int and handle > 0
                 and any(item.value == handle and item.resource == resource for item in self.handles),
                 "foreign or closed handle")

    def read(self, handle: int, path: str, count: int) -> bytes:
        self._owned(handle, path)
        _integer(count, 1, CHUNK_BYTES, "read count")
        if path == PAYLOAD_PATH:
            _require(self.phase == "PROBE" and self.payload_ready and not self.payload_consumed
                     and count == PAYLOAD_BYTES, "payload gate or one-use mismatch", "ALREADY_CONSUMED")
            self.payload_consumed = True
        buffer, transferred = self.c.create_string_buffer(count), self.w.DWORD()
        self._call("ReadFile", path, handle, buffer, count, self.c.byref(transferred), None)
        _require(transferred.value == count, "short read", "ABORTED_INCOMPLETE")
        return buffer.raw

    def close_all(self) -> tuple[Failure, ...]:
        self.phase = "CLEANUP"
        self.deadline = time.monotonic_ns() + self.binding.cleanup_ms * 1_000_000
        errors = []
        while self.handles:
            owned = self.handles.pop()  # one close attempt, never a retry
            handle, owned.value = owned.value, None
            if handle is None:
                continue
            try:
                self._call("CloseHandle", owned.resource, handle, cleanup=True)
            except BaseException as error:
                errors.append(_failure(error, "CloseHandle"))
        return tuple(errors)


def _modules_match(binding: Binding) -> None:
    _require(len(sys.modules) <= MAX_MODULES, "loaded module ceiling", "BLOCKED_PREREQUISITE")
    expected = {m.name: m.origin for m in binding.modules}
    actual = {}
    for index, (name, module) in enumerate(sys.modules.items()):
        _require(index < MAX_MODULES, "module scan ceiling", "BLOCKED_PREREQUISITE")
        spec = getattr(module, "__spec__", None)
        origin = getattr(spec, "origin", None)
        if origin is None:
            origin = getattr(module, "__file__", None)
        _require(type(origin) is str and len(origin) <= MAX_PATH_CHARS,
                 "unknown module provenance", "BLOCKED_PREREQUISITE")
        actual[name] = origin
    _require(actual == expected, "complete loaded module closure", "BLOCKED_PREREQUISITE")


def _failure(error: BaseException, operation: str) -> Failure:
    if type(error) is _Stop:
        return Failure(error.code, error.operation, error.native_error)
    # Unknown exceptions cannot be converted to apparent native success.
    return Failure("COMPLETION_UNCONFIRMED", operation, None)


class _Owner:
    def __init__(self, binding: Binding, plan: ResourcePlan):
        _execution_authorization()
        self.binding, self.plan = binding, plan
        self.native: _Native | None = None
        self.process: ProcessIdentity | None = None
        self.process_handle: int | None = None
        self.payload: int | None = None
        self.payload_identity: FileIdentity | None = None
        self.parents: list[tuple[int, Parent]] = []
        self.sources: list[tuple[int, Artifact]] = []
        self.state = "NEW"
        self.probe_consumed = False
        self.thread = threading.get_ident()

    def prepare(self) -> None:
        _execution_authorization()
        _require(self.state == "NEW", "owner preparation reused", "ALREADY_CONSUMED")
        self.state = "PREPARING"
        _require(sys.executable == INTERPRETER_PATH and tuple(sys.version_info[:3]) == RUNTIME_VERSION
                 and sys.implementation.name == "cpython" and sys.flags.isolated
                 and sys.flags.no_site and sys.flags.dont_write_bytecode,
                 "admitted isolated runtime", "BLOCKED_PREREQUISITE")
        self.native = _Native(self.binding, self.plan)
        native = self.native
        _modules_match(self.binding)
        self.process_handle = native.process_handle()
        observed = native.process_identity(self.process_handle)
        _require(observed == self.binding.process, "initial owner identity")
        self.process = observed
        for parent in self.binding.parents:
            handle = native.open_existing(parent.path, directory=True)
            _require(native.inspect(handle, parent.path, directory=True) == parent.identity,
                     "parent identity before source open")
            self.parents.append((handle, parent))
        for artifact in (self.binding.caller,) + self.binding.dependencies:
            handle = native.open_existing(artifact.path)
            _require(native.inspect(handle, artifact.path) == artifact.identity, "source identity before read")
            digest = hashlib.sha256()
            for start in range(0, artifact.byte_count, CHUNK_BYTES):
                digest.update(native.read(handle, artifact.path, min(CHUNK_BYTES, artifact.byte_count - start)))
            _require(digest.hexdigest() == artifact.sha256, "source bytes differ")
            _require(native.inspect(handle, artifact.path, position=artifact.byte_count) == artifact.identity,
                     "source changed during binding")
            self.sources.append((handle, artifact))
        self.payload = native.open_existing(PAYLOAD_PATH)
        observed_file = native.inspect(self.payload, PAYLOAD_PATH)
        _require(observed_file == self.binding.payload_identity, "payload identity before read")
        self.payload_identity = observed_file
        self.state = "PREPARED"

    def probe_once(self) -> tuple[str, int]:
        """No open, spawn or authority acquisition; only the already owned file."""
        _execution_authorization()
        _require(self.thread == threading.get_ident() and self.state == "PREPARED"
                 and not self.probe_consumed, "probe reuse/owner mismatch", "ALREADY_CONSUMED")
        self.probe_consumed, self.state = True, "PROBING"
        native = self.native
        _require(type(native) is _Native and self.process_handle is not None
                 and self.payload is not None, "missing owned handle", "BLOCKED_PREREQUISITE")
        native.phase = "PROBE"
        _modules_match(self.binding)
        _require(native.process_identity(self.process_handle) == self.process == self.binding.process,
                 "owner changed before probe")
        for handle, parent in self.parents:
            _require(native.inspect(handle, parent.path, directory=True) == parent.identity, "parent changed")
        for handle, artifact in self.sources:
            _require(native.inspect(handle, artifact.path, position=artifact.byte_count) == artifact.identity,
                     "source changed before probe")
        _require(native.inspect(self.payload, PAYLOAD_PATH) == self.payload_identity,
                 "payload channel changed before read")
        # Identity assignments precede this sole payload read. No JSON decoding.
        native.payload_ready = True
        raw = native.read(self.payload, PAYLOAD_PATH, PAYLOAD_BYTES)
        digest = hashlib.sha256(raw).hexdigest()
        _require(digest == PAYLOAD_SHA256, "payload digest differs")
        _require(native.inspect(self.payload, PAYLOAD_PATH, position=PAYLOAD_BYTES) == self.payload_identity,
                 "payload changed after read")
        _require(native.process_identity(self.process_handle) == self.process, "owner changed after read")
        for handle, parent in self.parents:
            _require(native.inspect(handle, parent.path, directory=True) == parent.identity,
                     "parent changed after read")
        self.state = "READ_COMPLETE"
        return digest, len(raw)


_INVOCATION_LOCK = threading.Lock()
_INVOCATION_CONSUMED = False


def run_once(binding: Binding) -> Finding:
    """Defined, never invoked here. Current source always returns BLOCKED."""
    owner = None
    plan = None
    digest = None
    invocation = None
    payload_digest = None
    payload_bytes = 0
    primary = None
    cleanup = ()
    try:
        _execution_authorization()  # before argument processing and any native I/O
        global _INVOCATION_CONSUMED
        with _INVOCATION_LOCK:
            _require(not _INVOCATION_CONSUMED, "caller invocation consumed", "ALREADY_CONSUMED")
            _INVOCATION_CONSUMED = True
        plan = resource_plan(binding)
        _require(plan.hard_time_bound_proven and plan.resident_memory_bound_proven
                 and plan.full_validation_work_bound_proven,
                 "complete runtime resource admission absent", "BLOCKED_PREREQUISITE")
        digest = _binding_digest(binding)
        invocation = binding.invocation_id
        owner = _Owner(binding, plan)
        owner.prepare()
        payload_digest, payload_bytes = owner.probe_once()
    except BaseException as error:
        primary = _failure(error, "caller")
    finally:
        if owner is not None:
            owner.state = "CLEANUP"
            if owner.native is not None:
                cleanup = owner.native.close_all()
            owner.state = "CLOSED" if not cleanup else "UNKNOWN"
    native = owner.native if owner is not None else None
    status = "READ_ONLY_SCOPE_COMPLETE" if primary is None else primary.code
    if cleanup:
        status = "COMPLETION_UNCONFIRMED"
    return Finding(status, invocation, digest, owner.process if owner else None,
                   owner.payload_identity if owner else None, payload_digest, payload_bytes,
                   plan, native.calls if native else 0, primary, cleanup,
                   tuple(native.events) if native else ())
