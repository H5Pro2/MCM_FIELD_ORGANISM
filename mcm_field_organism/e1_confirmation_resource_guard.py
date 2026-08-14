"""Private S1-EB22 Windows subprocess resource guard; synthetic use only."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import asdict, dataclass
from pathlib import Path
import subprocess
import time

from .e1_confirmation_owner_authorization import (
    E1ConfirmationOwnerAuthorization,
)
from .e1_refined_formation_runner import _digest


class E1ConfirmationResourceGuardError(RuntimeError):
    """Raised when the S1-EB22 resource guard cannot fail closed."""


JOB_OBJECT_LIMIT_JOB_MEMORY = 0x00000200
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9


class _IoCounters(ctypes.Structure):
    _fields_ = [
        ("ReadOperationCount", ctypes.c_uint64),
        ("WriteOperationCount", ctypes.c_uint64),
        ("OtherOperationCount", ctypes.c_uint64),
        ("ReadTransferCount", ctypes.c_uint64),
        ("WriteTransferCount", ctypes.c_uint64),
        ("OtherTransferCount", ctypes.c_uint64),
    ]


class _BasicLimitInformation(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_int64),
        ("PerJobUserTimeLimit", ctypes.c_int64),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    ]


class _ExtendedLimitInformation(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", _BasicLimitInformation),
        ("IoInfo", _IoCounters),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


@dataclass(frozen=True, slots=True)
class E1ConfirmationResourceGuardBinding:
    binding_id: str
    authorization_digest: str
    platform: str
    backend: str
    max_wall_seconds: int
    max_peak_rss_bytes: int
    process_tree_kill_bound: bool
    wall_limit_bound: bool
    memory_limit_bound: bool
    synthetic_success_verified: bool
    synthetic_wall_limit_verified: bool
    synthetic_memory_limit_verified: bool
    canonical_execution_permitted: bool
    binding_digest: str

    def __post_init__(self) -> None:
        if (
            self.binding_id != "e1.confirmation-resource-guard.s1eb22.v1"
            or self.platform != "win32"
            or self.backend != "windows-job-object"
            or self.max_wall_seconds != 1_800
            or self.max_peak_rss_bytes != 4 * 1024**3
            or self.process_tree_kill_bound is not True
            or self.wall_limit_bound is not True
            or self.memory_limit_bound is not True
            or self.synthetic_success_verified is not True
            or self.synthetic_wall_limit_verified is not True
            or self.synthetic_memory_limit_verified is not True
            or self.canonical_execution_permitted is not False
        ):
            raise E1ConfirmationResourceGuardError(
                "S1-EB22 enforcement binding changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "binding_digest"
        }
        if self.binding_digest != _digest(payload):
            raise E1ConfirmationResourceGuardError(
                "S1-EB22 binding digest does not match its payload"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


@dataclass(frozen=True, slots=True)
class E1ConfirmationGuardedProcessResult:
    status: str
    return_code: int
    elapsed_seconds: float
    peak_job_memory_bytes: int
    stdout: str
    stderr: str

    def __post_init__(self) -> None:
        if self.status not in {
            "COMPLETED",
            "NONZERO_EXIT",
            "WALL_LIMIT_EXCEEDED",
            "MEMORY_LIMIT_EXCEEDED",
        }:
            raise E1ConfirmationResourceGuardError(
                "S1-EB22 guarded result status changed"
            )
        if self.elapsed_seconds < 0.0 or self.peak_job_memory_bytes < 0:
            raise E1ConfirmationResourceGuardError(
                "S1-EB22 guarded metrics are invalid"
            )


def _kernel32():
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateJobObjectW.restype = wintypes.HANDLE
    kernel.SetInformationJobObject.argtypes = (
        wintypes.HANDLE,
        ctypes.c_int,
        ctypes.c_void_p,
        wintypes.DWORD,
    )
    kernel.AssignProcessToJobObject.argtypes = (wintypes.HANDLE, wintypes.HANDLE)
    kernel.TerminateJobObject.argtypes = (wintypes.HANDLE, wintypes.UINT)
    kernel.QueryInformationJobObject.argtypes = (
        wintypes.HANDLE,
        ctypes.c_int,
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
    )
    return kernel


def _raise_last_error(role: str) -> None:
    raise E1ConfirmationResourceGuardError(
        f"S1-EB22 {role} failed with Win32 error {ctypes.get_last_error()}"
    )


def run_guarded_synthetic_process(
    command: tuple[str, ...],
    cwd: Path,
    *,
    max_wall_seconds: float,
    max_peak_rss_bytes: int,
) -> E1ConfirmationGuardedProcessResult:
    """Run one synthetic process tree under hard Windows resource limits."""

    if (
        not command
        or max_wall_seconds <= 0.0
        or max_peak_rss_bytes < 16 * 1024**2
        or not Path(cwd).is_dir()
    ):
        raise E1ConfirmationResourceGuardError(
            "S1-EB22 synthetic guard arguments are invalid"
        )
    kernel = _kernel32()
    job = kernel.CreateJobObjectW(None, None)
    if not job:
        _raise_last_error("CreateJobObjectW")
    process = None
    started = time.monotonic()
    peak = 0
    timed_out = False
    try:
        limits = _ExtendedLimitInformation()
        limits.BasicLimitInformation.LimitFlags = (
            JOB_OBJECT_LIMIT_JOB_MEMORY | JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        )
        limits.JobMemoryLimit = max_peak_rss_bytes
        if not kernel.SetInformationJobObject(
            job,
            JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
            ctypes.byref(limits),
            ctypes.sizeof(limits),
        ):
            _raise_last_error("SetInformationJobObject")
        process = subprocess.Popen(
            command,
            cwd=Path(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if not kernel.AssignProcessToJobObject(job, wintypes.HANDLE(process._handle)):
            process.kill()
            _raise_last_error("AssignProcessToJobObject")
        deadline = started + max_wall_seconds
        while process.poll() is None:
            if time.monotonic() >= deadline:
                timed_out = True
                kernel.TerminateJobObject(job, 124)
                break
            time.sleep(min(0.01, max_wall_seconds / 10.0))
        stdout, stderr = process.communicate(timeout=5.0)
        info = _ExtendedLimitInformation()
        returned = wintypes.DWORD()
        if kernel.QueryInformationJobObject(
            job,
            JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
            ctypes.byref(info),
            ctypes.sizeof(info),
            ctypes.byref(returned),
        ):
            peak = int(info.PeakJobMemoryUsed)
        elapsed = time.monotonic() - started
        if timed_out:
            status = "WALL_LIMIT_EXCEEDED"
        elif peak >= max_peak_rss_bytes or process.returncode in {
            -1073741801,
            -1073740791,
        }:
            status = "MEMORY_LIMIT_EXCEEDED"
        elif process.returncode == 0:
            status = "COMPLETED"
        else:
            status = "NONZERO_EXIT"
        return E1ConfirmationGuardedProcessResult(
            status=status,
            return_code=int(process.returncode),
            elapsed_seconds=elapsed,
            peak_job_memory_bytes=peak,
            stdout=stdout,
            stderr=stderr,
        )
    finally:
        if process is not None and process.poll() is None:
            kernel.TerminateJobObject(job, 125)
            process.wait(timeout=5.0)
        kernel.CloseHandle(job)


def bind_e1_confirmation_resource_guard(
    authorization: E1ConfirmationOwnerAuthorization,
    success: E1ConfirmationGuardedProcessResult,
    wall: E1ConfirmationGuardedProcessResult,
    memory: E1ConfirmationGuardedProcessResult,
) -> E1ConfirmationResourceGuardBinding:
    """Bind verified enforcement while canonical execution stays closed."""

    if not isinstance(authorization, E1ConfirmationOwnerAuthorization) or (
        authorization.project_owner_authorization != "AUTHORIZED_ONE_SHOT"
        or authorization.execution_permitted is not False
    ):
        raise E1ConfirmationResourceGuardError(
            "S1-EB22 requires the closed S1-EB21 authorization"
        )
    if (
        success.status != "COMPLETED"
        or wall.status != "WALL_LIMIT_EXCEEDED"
        or memory.status != "MEMORY_LIMIT_EXCEEDED"
    ):
        raise E1ConfirmationResourceGuardError(
            "S1-EB22 synthetic enforcement matrix is incomplete"
        )
    values = {
        "binding_id": "e1.confirmation-resource-guard.s1eb22.v1",
        "authorization_digest": authorization.authorization_digest,
        "platform": "win32",
        "backend": "windows-job-object",
        "max_wall_seconds": authorization.max_wall_seconds,
        "max_peak_rss_bytes": authorization.max_peak_rss_bytes,
        "process_tree_kill_bound": True,
        "wall_limit_bound": True,
        "memory_limit_bound": True,
        "synthetic_success_verified": True,
        "synthetic_wall_limit_verified": True,
        "synthetic_memory_limit_verified": True,
        "canonical_execution_permitted": False,
    }
    return E1ConfirmationResourceGuardBinding(
        **values,
        binding_digest=_digest(values),
    )
