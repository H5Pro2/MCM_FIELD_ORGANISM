"""Fail-closed Windows supervisor for the preregistered binding preflight.

This module intentionally has no command-line entry point. Importing it binds
no project modules and starts no process. ABI and runtime acceptance remain
separate review gates.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import threading
import time
from typing import Callable, Final, TypeVar


WORKSPACE: Final = Path(r"C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace")
PAYLOAD_PATH: Final = WORKSPACE / "docs/forschung/215_BINDUNGS_PREFLIGHT_STDIN_NUTZLAST.txt"
APPLICATION_NAME: Final = str(WORKSPACE / ".venv/Scripts/python.exe")
COMMAND_LINE: Final = f'"{APPLICATION_NAME}" -B -I -'
PAYLOAD_SIZE: Final = 1806
PAYLOAD_SHA256: Final = "d86be4be95ed54ea461aea4c538639cec179726ccca30b14dd762a605351b393"
STDOUT_LIMIT: Final = 4096
STDERR_LIMIT: Final = 0
WALL_TIME_SECONDS: Final = 60.0
FINALIZATION_SECONDS: Final = 5.0
PRE_JOB_ABORT_EXIT_CODE: Final = 1
USER_CPU_100NS: Final = 300_000_000
PROCESS_MEMORY_LIMIT: Final = 1_073_741_824
JOB_MEMORY_LIMIT: Final = 1_073_741_824
ACTIVE_PROCESS_LIMIT: Final = 1
CHILD_PROCESS_LIMIT: Final = 0
SUCCESS_EXIT_CODE: Final = 0
ENVIRONMENT_ENTRIES: Final = ("SystemRoot=C:\\Windows", "WINDIR=C:\\Windows")
ENVIRONMENT_BLOCK: Final = "\0".join(ENVIRONMENT_ENTRIES) + "\0\0"

_T = TypeVar("_T")

CREATE_SUSPENDED = 0x00000004
CREATE_NO_WINDOW = 0x08000000
EXTENDED_STARTUPINFO_PRESENT = 0x00080000
CREATE_UNICODE_ENVIRONMENT = 0x00000400
CREATION_FLAGS = (
    CREATE_SUSPENDED
    | CREATE_NO_WINDOW
    | EXTENDED_STARTUPINFO_PRESENT
    | CREATE_UNICODE_ENVIRONMENT
)
STARTF_USESTDHANDLES = 0x00000100
HANDLE_FLAG_INHERIT = 0x00000001
PROC_THREAD_ATTRIBUTE_HANDLE_LIST = 0x00020002
INFINITE = 0xFFFFFFFF
WAIT_OBJECT_0 = 0x00000000
WAIT_TIMEOUT = 0x00000102
ERROR_BROKEN_PIPE = 109
ERROR_NO_MORE_FILES = 18
STILL_ACTIVE = 259
TH32CS_SNAPTHREAD = 0x00000004
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

JOB_OBJECT_LIMIT_PROCESS_TIME = 0x00000002
JOB_OBJECT_LIMIT_ACTIVE_PROCESS = 0x00000008
JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x00000100
JOB_OBJECT_LIMIT_JOB_MEMORY = 0x00000200
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
JOB_LIMIT_FLAGS = (
    JOB_OBJECT_LIMIT_PROCESS_TIME
    | JOB_OBJECT_LIMIT_ACTIVE_PROCESS
    | JOB_OBJECT_LIMIT_PROCESS_MEMORY
    | JOB_OBJECT_LIMIT_JOB_MEMORY
    | JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
)
JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9
JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION = 1

SIZE_T = ctypes.c_size_t
ULONG_PTR = SIZE_T
LPBYTE = ctypes.POINTER(wintypes.BYTE)
LPDWORD = ctypes.POINTER(wintypes.DWORD)
LPHANDLE = ctypes.POINTER(wintypes.HANDLE)


class ContractError(RuntimeError):
    """A fail-closed violation of the preregistered execution contract."""


class FinalizationStepError(ContractError):
    def __init__(self, step: str, cause: BaseException) -> None:
        super().__init__(f"{step}: {cause}")
        self.step = step
        self.cause = cause


class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = (
        ("nLength", wintypes.DWORD),
        ("lpSecurityDescriptor", wintypes.LPVOID),
        ("bInheritHandle", wintypes.BOOL),
    )


class STARTUPINFOW(ctypes.Structure):
    _fields_ = (
        ("cb", wintypes.DWORD),
        ("lpReserved", wintypes.LPWSTR),
        ("lpDesktop", wintypes.LPWSTR),
        ("lpTitle", wintypes.LPWSTR),
        ("dwX", wintypes.DWORD),
        ("dwY", wintypes.DWORD),
        ("dwXSize", wintypes.DWORD),
        ("dwYSize", wintypes.DWORD),
        ("dwXCountChars", wintypes.DWORD),
        ("dwYCountChars", wintypes.DWORD),
        ("dwFillAttribute", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("wShowWindow", wintypes.WORD),
        ("cbReserved2", wintypes.WORD),
        ("lpReserved2", LPBYTE),
        ("hStdInput", wintypes.HANDLE),
        ("hStdOutput", wintypes.HANDLE),
        ("hStdError", wintypes.HANDLE),
    )


class STARTUPINFOEXW(ctypes.Structure):
    _fields_ = (
        ("StartupInfo", STARTUPINFOW),
        ("lpAttributeList", wintypes.LPVOID),
    )


class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = (
        ("hProcess", wintypes.HANDLE),
        ("hThread", wintypes.HANDLE),
        ("dwProcessId", wintypes.DWORD),
        ("dwThreadId", wintypes.DWORD),
    )


class THREADENTRY32(ctypes.Structure):
    _fields_ = (
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ThreadID", wintypes.DWORD),
        ("th32OwnerProcessID", wintypes.DWORD),
        ("tpBasePri", wintypes.LONG),
        ("tpDeltaPri", wintypes.LONG),
        ("dwFlags", wintypes.DWORD),
    )


class IO_COUNTERS(ctypes.Structure):
    _fields_ = tuple((name, ctypes.c_ulonglong) for name in (
        "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
        "ReadTransferCount", "WriteTransferCount", "OtherTransferCount",
    ))


class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = (
        ("PerProcessUserTimeLimit", ctypes.c_longlong),
        ("PerJobUserTimeLimit", ctypes.c_longlong),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", SIZE_T),
        ("MaximumWorkingSetSize", SIZE_T),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ULONG_PTR),
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    )


class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = (
        ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
        ("IoInfo", IO_COUNTERS),
        ("ProcessMemoryLimit", SIZE_T),
        ("JobMemoryLimit", SIZE_T),
        ("PeakProcessMemoryUsed", SIZE_T),
        ("PeakJobMemoryUsed", SIZE_T),
    )


class JOBOBJECT_BASIC_ACCOUNTING_INFORMATION(ctypes.Structure):
    _fields_ = (
        ("TotalUserTime", ctypes.c_longlong),
        ("TotalKernelTime", ctypes.c_longlong),
        ("ThisPeriodTotalUserTime", ctypes.c_longlong),
        ("ThisPeriodTotalKernelTime", ctypes.c_longlong),
        ("TotalPageFaultCount", wintypes.DWORD),
        ("TotalProcesses", wintypes.DWORD),
        ("ActiveProcesses", wintypes.DWORD),
        ("TotalTerminatedProcesses", wintypes.DWORD),
    )


@dataclass(frozen=True)
class ManifestEntry:
    kind: str
    size: int
    digest: str
    modified_ns: int


@dataclass(frozen=True)
class ExecutionResult:
    stdout: bytes
    exit_code: int
    payload_verified: bool
    job_limits_verified: bool
    streams_verified: bool
    workspace_verified: bool
    schema_verified: bool
    observations: TechnicalObservations


@dataclass(frozen=True)
class TechnicalObservation:
    thread_count: int
    handle_count: int


@dataclass(frozen=True)
class TechnicalObservations:
    before: TechnicalObservation | None
    during: TechnicalObservation | None
    after: TechnicalObservation | None


class TechnicalAbort(ContractError):
    def __init__(
        self,
        message: str,
        observations: TechnicalObservations,
        finalization_errors: tuple[BaseException, ...],
    ) -> None:
        super().__init__(message)
        self.observations = observations
        self.finalization_errors = finalization_errors


@dataclass
class OwnedHandle:
    name: str
    value: wintypes.HANDLE
    close_at: str
    closed: bool = False


class HandleLedger:
    def __init__(self, api: "Kernel32Bindings") -> None:
        self._api = api
        self._handles: dict[str, OwnedHandle] = {}

    def own(self, name: str, value: wintypes.HANDLE, close_at: str) -> wintypes.HANDLE:
        if name in self._handles or not value:
            raise ContractError(f"invalid handle ownership: {name}")
        self._handles[name] = OwnedHandle(name, value, close_at)
        return value

    def close(self, name: str) -> None:
        item = self._handles[name]
        if item.closed:
            raise ContractError(f"handle already closed: {name}")
        if not self._api.CloseHandle(item.value):
            raise ctypes.WinError(ctypes.get_last_error())
        item.closed = True

    def value(self, name: str) -> wintypes.HANDLE:
        item = self._handles[name]
        if item.closed:
            raise ContractError(f"closed handle requested: {name}")
        return item.value

    def close_if_open(self, name: str) -> None:
        item = self._handles.get(name)
        if item is not None and not item.closed:
            self.close(name)

    def close_remaining(self) -> None:
        for item in reversed(tuple(self._handles.values())):
            if not item.closed:
                self._api.CloseHandle(item.value)
                item.closed = True


class Kernel32Bindings:
    def __init__(self) -> None:
        if not hasattr(ctypes, "WinDLL"):
            raise ContractError("Windows API is unavailable")
        dll = ctypes.WinDLL("kernel32", use_last_error=True)
        self.CreatePipe = dll.CreatePipe
        self.CreatePipe.argtypes = (LPHANDLE, LPHANDLE, ctypes.POINTER(SECURITY_ATTRIBUTES), wintypes.DWORD)
        self.CreatePipe.restype = wintypes.BOOL
        self.SetHandleInformation = dll.SetHandleInformation
        self.SetHandleInformation.argtypes = (wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD)
        self.SetHandleInformation.restype = wintypes.BOOL
        self.InitializeProcThreadAttributeList = dll.InitializeProcThreadAttributeList
        self.InitializeProcThreadAttributeList.argtypes = (wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(SIZE_T))
        self.InitializeProcThreadAttributeList.restype = wintypes.BOOL
        self.UpdateProcThreadAttribute = dll.UpdateProcThreadAttribute
        self.UpdateProcThreadAttribute.argtypes = (wintypes.LPVOID, wintypes.DWORD, SIZE_T, wintypes.LPVOID, SIZE_T, wintypes.LPVOID, ctypes.POINTER(SIZE_T))
        self.UpdateProcThreadAttribute.restype = wintypes.BOOL
        self.DeleteProcThreadAttributeList = dll.DeleteProcThreadAttributeList
        self.DeleteProcThreadAttributeList.argtypes = (wintypes.LPVOID,)
        self.DeleteProcThreadAttributeList.restype = None
        self.CreateProcessW = dll.CreateProcessW
        self.CreateProcessW.argtypes = (wintypes.LPCWSTR, wintypes.LPWSTR, ctypes.POINTER(SECURITY_ATTRIBUTES), ctypes.POINTER(SECURITY_ATTRIBUTES), wintypes.BOOL, wintypes.DWORD, wintypes.LPVOID, wintypes.LPCWSTR, ctypes.POINTER(STARTUPINFOW), ctypes.POINTER(PROCESS_INFORMATION))
        self.CreateProcessW.restype = wintypes.BOOL
        self.CreateJobObjectW = dll.CreateJobObjectW
        self.CreateJobObjectW.argtypes = (ctypes.POINTER(SECURITY_ATTRIBUTES), wintypes.LPCWSTR)
        self.CreateJobObjectW.restype = wintypes.HANDLE
        self.SetInformationJobObject = dll.SetInformationJobObject
        self.SetInformationJobObject.argtypes = (wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD)
        self.SetInformationJobObject.restype = wintypes.BOOL
        self.QueryInformationJobObject = dll.QueryInformationJobObject
        self.QueryInformationJobObject.argtypes = (wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD, LPDWORD)
        self.QueryInformationJobObject.restype = wintypes.BOOL
        self.AssignProcessToJobObject = dll.AssignProcessToJobObject
        self.AssignProcessToJobObject.argtypes = (wintypes.HANDLE, wintypes.HANDLE)
        self.AssignProcessToJobObject.restype = wintypes.BOOL
        self.ResumeThread = dll.ResumeThread
        self.ResumeThread.argtypes = (wintypes.HANDLE,)
        self.ResumeThread.restype = wintypes.DWORD
        self.WriteFile = dll.WriteFile
        self.WriteFile.argtypes = (wintypes.HANDLE, wintypes.LPCVOID, wintypes.DWORD, LPDWORD, wintypes.LPVOID)
        self.WriteFile.restype = wintypes.BOOL
        self.ReadFile = dll.ReadFile
        self.ReadFile.argtypes = (wintypes.HANDLE, wintypes.LPVOID, wintypes.DWORD, LPDWORD, wintypes.LPVOID)
        self.ReadFile.restype = wintypes.BOOL
        self.WaitForSingleObject = dll.WaitForSingleObject
        self.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
        self.WaitForSingleObject.restype = wintypes.DWORD
        self.GetExitCodeProcess = dll.GetExitCodeProcess
        self.GetExitCodeProcess.argtypes = (wintypes.HANDLE, LPDWORD)
        self.GetExitCodeProcess.restype = wintypes.BOOL
        self.TerminateJobObject = dll.TerminateJobObject
        self.TerminateJobObject.argtypes = (wintypes.HANDLE, wintypes.UINT)
        self.TerminateJobObject.restype = wintypes.BOOL
        self.TerminateProcess = dll.TerminateProcess
        self.TerminateProcess.argtypes = (wintypes.HANDLE, wintypes.UINT)
        self.TerminateProcess.restype = wintypes.BOOL
        self.CloseHandle = dll.CloseHandle
        self.CloseHandle.argtypes = (wintypes.HANDLE,)
        self.CloseHandle.restype = wintypes.BOOL
        self.GetCurrentProcessId = dll.GetCurrentProcessId
        self.GetCurrentProcessId.argtypes = ()
        self.GetCurrentProcessId.restype = wintypes.DWORD
        self.GetCurrentProcess = dll.GetCurrentProcess
        self.GetCurrentProcess.argtypes = ()
        self.GetCurrentProcess.restype = wintypes.HANDLE
        self.GetProcessHandleCount = dll.GetProcessHandleCount
        self.GetProcessHandleCount.argtypes = (wintypes.HANDLE, LPDWORD)
        self.GetProcessHandleCount.restype = wintypes.BOOL
        self.CreateToolhelp32Snapshot = dll.CreateToolhelp32Snapshot
        self.CreateToolhelp32Snapshot.argtypes = (wintypes.DWORD, wintypes.DWORD)
        self.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
        self.Thread32First = dll.Thread32First
        self.Thread32First.argtypes = (wintypes.HANDLE, ctypes.POINTER(THREADENTRY32))
        self.Thread32First.restype = wintypes.BOOL
        self.Thread32Next = dll.Thread32Next
        self.Thread32Next.argtypes = (wintypes.HANDLE, ctypes.POINTER(THREADENTRY32))
        self.Thread32Next.restype = wintypes.BOOL


def _load_and_verify_payload() -> bytes:
    payload = PAYLOAD_PATH.read_bytes()
    if len(payload) != PAYLOAD_SIZE or sha256(payload).hexdigest() != PAYLOAD_SHA256:
        raise ContractError("payload identity mismatch")
    if payload.startswith((b"\xef\xbb\xbf", b"\xff\xfe", b"\xfe\xff")):
        raise ContractError("payload BOM is forbidden")
    if b"\r" in payload or not payload.endswith(b"\n"):
        raise ContractError("payload line ending mismatch")
    try:
        ascii_text = payload.decode("ascii")
        payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContractError("payload encoding mismatch") from exc
    if ascii_text.encode("ascii") != payload:
        raise ContractError("payload normalization detected")
    return payload


def _workspace_manifest() -> dict[str, ManifestEntry]:
    result: dict[str, ManifestEntry] = {}
    stack = [WORKSPACE]
    while stack:
        directory = stack.pop()
        for path in directory.iterdir():
            relative = path.relative_to(WORKSPACE).as_posix()
            if relative == ".git":
                continue
            stat = path.stat(follow_symlinks=False)
            if path.is_symlink():
                raise ContractError(f"workspace symlink is undecidable: {relative}")
            if path.is_dir():
                result[relative] = ManifestEntry("directory", 0, "", stat.st_mtime_ns)
                stack.append(path)
            elif path.is_file():
                result[relative] = ManifestEntry(
                    "file", stat.st_size, sha256(path.read_bytes()).hexdigest(), stat.st_mtime_ns
                )
            else:
                raise ContractError(f"unsupported workspace entry: {relative}")
    return result


def _verify_external_activity_absence() -> None:
    raise ContractError(
        "absence of network, device, camera, microphone, display, clipboard, "
        "service, and other external activity has no approved verifier"
    )


def _set_non_inheritable(api: Kernel32Bindings, handle: wintypes.HANDLE) -> None:
    if not api.SetHandleInformation(handle, HANDLE_FLAG_INHERIT, 0):
        raise ctypes.WinError(ctypes.get_last_error())


def _create_pipe(api: Kernel32Bindings) -> tuple[wintypes.HANDLE, wintypes.HANDLE]:
    read_handle = wintypes.HANDLE()
    write_handle = wintypes.HANDLE()
    security = SECURITY_ATTRIBUTES(ctypes.sizeof(SECURITY_ATTRIBUTES), None, True)
    if not api.CreatePipe(ctypes.byref(read_handle), ctypes.byref(write_handle), ctypes.byref(security), 4096):
        raise ctypes.WinError(ctypes.get_last_error())
    return read_handle, write_handle


def _configure_job(api: Kernel32Bindings, job: wintypes.HANDLE) -> None:
    limits = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
    basic = limits.BasicLimitInformation
    basic.PerProcessUserTimeLimit = USER_CPU_100NS
    basic.LimitFlags = JOB_LIMIT_FLAGS
    basic.ActiveProcessLimit = ACTIVE_PROCESS_LIMIT
    limits.ProcessMemoryLimit = PROCESS_MEMORY_LIMIT
    limits.JobMemoryLimit = JOB_MEMORY_LIMIT
    if not api.SetInformationJobObject(job, JOB_OBJECT_EXTENDED_LIMIT_INFORMATION, ctypes.byref(limits), ctypes.sizeof(limits)):
        raise ctypes.WinError(ctypes.get_last_error())
    observed = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
    returned = wintypes.DWORD()
    if not api.QueryInformationJobObject(job, JOB_OBJECT_EXTENDED_LIMIT_INFORMATION, ctypes.byref(observed), ctypes.sizeof(observed), ctypes.byref(returned)):
        raise ctypes.WinError(ctypes.get_last_error())
    got = observed.BasicLimitInformation
    if (
        got.LimitFlags != JOB_LIMIT_FLAGS
        or got.PerProcessUserTimeLimit != USER_CPU_100NS
        or got.ActiveProcessLimit != ACTIVE_PROCESS_LIMIT
        or observed.ProcessMemoryLimit != PROCESS_MEMORY_LIMIT
        or observed.JobMemoryLimit != JOB_MEMORY_LIMIT
    ):
        raise ContractError("job limit readback mismatch")


def _job_active_processes(api: Kernel32Bindings, job: wintypes.HANDLE) -> int:
    accounting = JOBOBJECT_BASIC_ACCOUNTING_INFORMATION()
    if not api.QueryInformationJobObject(job, JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION, ctypes.byref(accounting), ctypes.sizeof(accounting), None):
        raise ctypes.WinError(ctypes.get_last_error())
    return int(accounting.ActiveProcesses)


def _remaining_seconds(deadline: float) -> float:
    return max(0.0, deadline - time.monotonic())


def _remaining_milliseconds(deadline: float) -> int:
    return max(0, int(_remaining_seconds(deadline) * 1000))


def _observe_supervisor(api: Kernel32Bindings) -> TechnicalObservation:
    process_id = api.GetCurrentProcessId()
    snapshot = api.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
    snapshot_value = ctypes.cast(snapshot, ctypes.c_void_p).value
    if snapshot_value == INVALID_HANDLE_VALUE:
        raise ctypes.WinError(ctypes.get_last_error())
    thread_count = 0
    try:
        entry = THREADENTRY32()
        entry.dwSize = ctypes.sizeof(THREADENTRY32)
        if not api.Thread32First(snapshot, ctypes.byref(entry)):
            raise ctypes.WinError(ctypes.get_last_error())
        while True:
            if entry.th32OwnerProcessID == process_id:
                thread_count += 1
            entry.dwSize = ctypes.sizeof(THREADENTRY32)
            if api.Thread32Next(snapshot, ctypes.byref(entry)):
                continue
            error = ctypes.get_last_error()
            if error != ERROR_NO_MORE_FILES:
                raise ctypes.WinError(error)
            break
    finally:
        if not api.CloseHandle(snapshot):
            raise ctypes.WinError(ctypes.get_last_error())

    handle_count = wintypes.DWORD()
    process = api.GetCurrentProcess()
    if not api.GetProcessHandleCount(process, ctypes.byref(handle_count)):
        raise ctypes.WinError(ctypes.get_last_error())
    return TechnicalObservation(thread_count, int(handle_count.value))


class _RawReader:
    def __init__(self, api: Kernel32Bindings, handle: wintypes.HANDLE, capacity: int, job: wintypes.HANDLE) -> None:
        self.api = api
        self.handle = handle
        self.capacity = capacity
        self.job = job
        self.data = bytearray()
        self.ready = threading.Event()
        self.eof = False
        self.error: BaseException | None = None
        self.thread = threading.Thread(target=self._run, daemon=False)
        self.started = False

    def start(self, deadline: float) -> None:
        self.started = True
        self.thread.start()
        if not self.ready.wait(_remaining_seconds(deadline)):
            raise ContractError("stream reader did not become ready")

    def _run(self) -> None:
        self.ready.set()
        try:
            while len(self.data) < self.capacity:
                chunk = (ctypes.c_ubyte * 1)()
                count = wintypes.DWORD()
                ok = self.api.ReadFile(self.handle, chunk, 1, ctypes.byref(count), None)
                if not ok:
                    error = ctypes.get_last_error()
                    if error == ERROR_BROKEN_PIPE:
                        self.eof = True
                        return
                    raise ctypes.WinError(error)
                if count.value != 1:
                    raise ContractError("ambiguous stream read")
                self.data.append(chunk[0])
            raise ContractError("stream byte limit exceeded")
        except BaseException as exc:
            self.error = exc


def _finish_readers(readers: tuple[_RawReader, ...], deadline: float) -> None:
    started_readers = tuple(reader for reader in readers if reader.started)
    for reader in started_readers:
        reader.thread.join(_remaining_seconds(deadline))
    if any(reader.thread.is_alive() for reader in started_readers):
        raise ContractError("stream EOF timeout")
    if any(reader.error or not reader.eof for reader in started_readers):
        raise ContractError("stream reader failure")


def _close_process_resources(ledger: HandleLedger) -> None:
    for name in (
        "supervisor_stdin_write",
        "child_stdin_read",
        "child_stdout_write",
        "child_stderr_write",
        "supervisor_stdout_read",
        "supervisor_stderr_read",
        "thread",
        "process",
        "job",
    ):
        ledger.close_if_open(name)


def _validate_result(stdout: bytes) -> None:
    if not stdout.endswith(b"\n") or stdout.count(b"\n") != 1:
        raise ContractError("stdout must be exactly one LF-terminated line")
    try:
        pairs = json.loads(stdout[:-1].decode("ascii"), object_pairs_hook=lambda items: items)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError("stdout schema is not ASCII JSON") from exc
    if not isinstance(pairs, list) or any(
        not isinstance(pair, tuple) or len(pair) != 2 for pair in pairs
    ):
        raise ContractError("stdout root must be a JSON object")
    keys = [key for key, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ContractError("duplicate stdout JSON key")
    value = dict(pairs)
    expected_keys = {
        "contract_digest", "effect_measurement_allowed", "execution_locked",
        "field_execution_allowed", "hook_execution_allowed",
    }
    if not isinstance(value, dict) or set(value) != expected_keys:
        raise ContractError("stdout keys mismatch")
    digest = value["contract_digest"]
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ContractError("contract digest mismatch")
    if value != {
        "contract_digest": digest,
        "effect_measurement_allowed": False,
        "execution_locked": True,
        "field_execution_allowed": False,
        "hook_execution_allowed": False,
    }:
        raise ContractError("stdout values mismatch")


def _run_finalization_step(
    name: str,
    deadline: float,
    errors: list[BaseException],
    action: Callable[[], _T],
) -> tuple[_T | None, bool]:
    if time.monotonic() >= deadline:
        errors.append(ContractError(f"{name}: deadline exhausted before step"))
        return None, False
    try:
        value = action()
    except BaseException as exc:
        errors.append(FinalizationStepError(name, exc))
        return None, False
    if time.monotonic() >= deadline:
        errors.append(ContractError(f"{name}: deadline exceeded after step"))
        return value, False
    return value, True


def _close_finalization_pipes(ledger: HandleLedger) -> None:
    for name in (
        "supervisor_stdin_write",
        "child_stdin_read",
        "child_stdout_write",
        "child_stderr_write",
    ):
        ledger.close_if_open(name)


def _after_observations(
    api: Kernel32Bindings,
    observations: TechnicalObservations,
) -> TechnicalObservations:
    return TechnicalObservations(
        observations.before,
        observations.during,
        _observe_supervisor(api),
    )


def _verify_after_manifest(before: dict[str, tuple[str, int, int]]) -> None:
    after = _workspace_manifest()
    if before != after:
        raise ContractError("workspace side effect detected")


def execute_once() -> ExecutionResult:
    """Execute the preregistered contract once; no caller is provided here."""
    payload = _load_and_verify_payload()
    before = _workspace_manifest()
    _verify_external_activity_absence()
    api = Kernel32Bindings()
    ledger = HandleLedger(api)
    attribute_buffer = None
    attribute_list = None
    job_assigned = False
    process_started = False
    process_ended = False
    readers: tuple[_RawReader, ...] = ()
    observations = TechnicalObservations(None, None, None)
    try:
        stdin_read, stdin_write = _create_pipe(api)
        ledger.own("child_stdin_read", stdin_read, "after_job_assignment")
        ledger.own("supervisor_stdin_write", stdin_write, "after_single_write")
        _set_non_inheritable(api, stdin_write)
        stdout_read, stdout_write = _create_pipe(api)
        ledger.own("supervisor_stdout_read", stdout_read, "after_eof")
        ledger.own("child_stdout_write", stdout_write, "after_job_assignment")
        _set_non_inheritable(api, stdout_read)
        stderr_read, stderr_write = _create_pipe(api)
        ledger.own("supervisor_stderr_read", stderr_read, "after_eof")
        ledger.own("child_stderr_write", stderr_write, "after_job_assignment")
        _set_non_inheritable(api, stderr_read)

        job = ledger.own("job", api.CreateJobObjectW(None, None), "final")
        _configure_job(api, job)

        child_handles = (wintypes.HANDLE * 3)(stdin_read, stdout_write, stderr_write)
        attribute_size = SIZE_T()
        api.InitializeProcThreadAttributeList(None, 1, 0, ctypes.byref(attribute_size))
        attribute_buffer = ctypes.create_string_buffer(attribute_size.value)
        attribute_list = ctypes.cast(attribute_buffer, wintypes.LPVOID)
        if not api.InitializeProcThreadAttributeList(attribute_list, 1, 0, ctypes.byref(attribute_size)):
            raise ctypes.WinError(ctypes.get_last_error())
        if not api.UpdateProcThreadAttribute(attribute_list, 0, PROC_THREAD_ATTRIBUTE_HANDLE_LIST, ctypes.cast(child_handles, wintypes.LPVOID), ctypes.sizeof(child_handles), None, None):
            raise ctypes.WinError(ctypes.get_last_error())

        startup = STARTUPINFOEXW()
        startup.StartupInfo.cb = ctypes.sizeof(STARTUPINFOEXW)
        startup.StartupInfo.dwFlags = STARTF_USESTDHANDLES
        startup.StartupInfo.hStdInput = stdin_read
        startup.StartupInfo.hStdOutput = stdout_write
        startup.StartupInfo.hStdError = stderr_write
        startup.lpAttributeList = attribute_list
        process_info = PROCESS_INFORMATION()
        command_buffer = ctypes.create_unicode_buffer(COMMAND_LINE)
        environment_buffer = ctypes.create_unicode_buffer(ENVIRONMENT_BLOCK)
        observations = TechnicalObservations(_observe_supervisor(api), None, None)
        if not api.CreateProcessW(APPLICATION_NAME, command_buffer, None, None, True, CREATION_FLAGS, ctypes.cast(environment_buffer, wintypes.LPVOID), str(WORKSPACE), ctypes.byref(startup.StartupInfo), ctypes.byref(process_info)):
            raise ctypes.WinError(ctypes.get_last_error())
        started_at = time.monotonic()
        success_deadline = started_at + WALL_TIME_SECONDS
        process_started = True
        process = ledger.own("process", process_info.hProcess, "final")
        thread = ledger.own("thread", process_info.hThread, "final")
        api.DeleteProcThreadAttributeList(attribute_list)
        attribute_list = None
        if not api.AssignProcessToJobObject(job, process):
            raise ctypes.WinError(ctypes.get_last_error())
        job_assigned = True
        _configure_job(api, job)
        if _job_active_processes(api, job) != 1:
            raise ContractError("job assignment readback mismatch")

        for child_name in ("child_stdin_read", "child_stdout_write", "child_stderr_write"):
            ledger.close(child_name)

        stdout_reader = _RawReader(api, stdout_read, STDOUT_LIMIT + 1, job)
        stderr_reader = _RawReader(api, stderr_read, STDERR_LIMIT + 1, job)
        readers = (stdout_reader, stderr_reader)
        stdout_reader.start(success_deadline)
        stderr_reader.start(success_deadline)

        written = wintypes.DWORD()
        payload_buffer = (ctypes.c_ubyte * PAYLOAD_SIZE).from_buffer_copy(payload)
        if not api.WriteFile(stdin_write, payload_buffer, PAYLOAD_SIZE, ctypes.byref(written), None) or written.value != PAYLOAD_SIZE:
            raise ContractError("single stdin write failed")
        ledger.close("supervisor_stdin_write")
        previous_suspend_count = api.ResumeThread(thread)
        if previous_suspend_count == 0xFFFFFFFF or previous_suspend_count != 1:
            raise ContractError("single thread resume failed")

        observations = TechnicalObservations(
            observations.before,
            _observe_supervisor(api),
            None,
        )
        while True:
            if time.monotonic() >= success_deadline:
                raise ContractError("wall time exceeded")
            if any(reader.error for reader in readers):
                raise ContractError("stream reader failure")
            wait_result = api.WaitForSingleObject(
                process,
                min(50, _remaining_milliseconds(success_deadline)),
            )
            if wait_result == WAIT_OBJECT_0:
                process_ended = True
                break
            if wait_result != WAIT_TIMEOUT:
                raise ContractError("ambiguous process wait result")

        _finish_readers(readers, success_deadline)
        exit_code = wintypes.DWORD(STILL_ACTIVE)
        if not api.GetExitCodeProcess(process, ctypes.byref(exit_code)) or exit_code.value == STILL_ACTIVE:
            raise ContractError("ambiguous process exit")
        if exit_code.value != SUCCESS_EXIT_CODE or len(stderr_reader.data) != 0:
            raise ContractError("process result rejected")
        if _job_active_processes(api, job) != CHILD_PROCESS_LIMIT:
            raise ContractError("job still has active processes")
        stdout = bytes(stdout_reader.data)
        _validate_result(stdout)
        _close_process_resources(ledger)
        observations = TechnicalObservations(
            observations.before,
            observations.during,
            _observe_supervisor(api),
        )
        if any(value is None for value in (
            observations.before, observations.during, observations.after
        )):
            raise ContractError("technical observations incomplete")
        after = _workspace_manifest()
        if before != after:
            raise ContractError("workspace side effect detected")
        return ExecutionResult(
            stdout, exit_code.value, True, True, True, True, True, observations
        )
    except BaseException as primary_error:
        finalization_errors: list[BaseException] = []
        if process_started:
            finalization_deadline = time.monotonic() + FINALIZATION_SECONDS
            if not process_ended:
                try:
                    if job_assigned:
                        if not api.TerminateJobObject(ledger.value("job"), 1):
                            raise ctypes.WinError(ctypes.get_last_error())
                    else:
                        if not api.TerminateProcess(
                            ledger.value("process"), PRE_JOB_ABORT_EXIT_CODE
                        ):
                            raise ctypes.WinError(ctypes.get_last_error())
                    wait_result = api.WaitForSingleObject(
                        ledger.value("process"),
                        _remaining_milliseconds(finalization_deadline),
                    )
                    exit_code = wintypes.DWORD(STILL_ACTIVE)
                    if (
                        wait_result != WAIT_OBJECT_0
                        or not api.GetExitCodeProcess(
                            ledger.value("process"), ctypes.byref(exit_code)
                        )
                        or exit_code.value == STILL_ACTIVE
                    ):
                        raise ContractError("terminated process end is unconfirmed")
                    process_ended = True
                except BaseException as exc:
                    finalization_errors.append(exc)

            if process_ended:
                _run_finalization_step(
                    "pipe closure",
                    finalization_deadline,
                    finalization_errors,
                    lambda: _close_finalization_pipes(ledger),
                )
                _run_finalization_step(
                    "reader completion",
                    finalization_deadline,
                    finalization_errors,
                    lambda: _finish_readers(readers, finalization_deadline),
                )
                _run_finalization_step(
                    "process resource closure",
                    finalization_deadline,
                    finalization_errors,
                    lambda: _close_process_resources(ledger),
                )
                after_value, after_ok = _run_finalization_step(
                    "after observation",
                    finalization_deadline,
                    finalization_errors,
                    lambda: _after_observations(api, observations),
                )
                if after_ok and after_value is not None:
                    observations = after_value
                _run_finalization_step(
                    "after manifest",
                    finalization_deadline,
                    finalization_errors,
                    lambda: _verify_after_manifest(before),
                )

        raise TechnicalAbort(
            str(primary_error), observations, tuple(finalization_errors)
        ) from primary_error
    finally:
        if attribute_list is not None:
            api.DeleteProcThreadAttributeList(attribute_list)
        ledger.close_remaining()
