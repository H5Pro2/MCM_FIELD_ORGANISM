"""Private S1-WD real resource observer restricted to temporary test roots."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import struct
from tempfile import gettempdir

from . import _ppb1_s1vq_corrected_matrix as s1vq
from . import _ppb1_s1vt_result_pipeline as s1vt
from . import _ppb1_s1vw_synthetic_one_shot_handoff as s1vw
from . import _ppb1_s1vz_synthetic_resource_calibration as s1vz
from ._ppb1_s1wb_private_production_h0_types import (
    S1WAProductionResourceObservation,
    build_s1wb_injected_observation,
)


S1WD_SCHEMA_VERSION = "ppb1.s1wd.temporary-resource-observer.v1"
S1WD_INVALID_TEMPORARY_ROOT = "S1WD_INVALID_TEMPORARY_ROOT"
S1WD_INVALID_EXECUTION_ID = "S1WD_INVALID_EXECUTION_ID"
S1WD_MEMORY_OBSERVATION_FAILED = "S1WD_MEMORY_OBSERVATION_FAILED"
S1WD_ATOMIC_REPLACE_PROBE_FAILED = "S1WD_ATOMIC_REPLACE_PROBE_FAILED"
S1WD_PRODUCTION_ROOT_BLOCKED = "S1WD_PRODUCTION_ROOT_BLOCKED"
S1WD_PRODUCTION_EXECUTION_BLOCKED = "S1WD_PRODUCTION_EXECUTION_BLOCKED"

_ROOT_NAME = "s1wd-h0-observer"
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_EXECUTION_ID = re.compile(r"^s1wd\.synthetic\.[a-z0-9][a-z0-9.-]{2,80}$")


class S1WDObservationError(ValueError):
    """One fail-closed temporary observer boundary violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _canonical_bytes(payload: object) -> bytes:
    return json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _digest(payload: object) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _source_digest(module: object) -> str:
    return hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()


def _platform_binding() -> tuple[tuple[str, str], ...]:
    return (
        ("python_implementation", platform.python_implementation()),
        ("python_version", platform.python_version()),
        ("operating_system", platform.system()),
        ("machine_architecture", platform.machine()),
        ("pointer_width_bits", str(struct.calcsize("P") * 8)),
    )


def _calibrated_source_digests() -> tuple[tuple[str, str], ...]:
    return (
        ("s1vq_runner", _source_digest(s1vq)),
        ("s1vt_pipeline", _source_digest(s1vt)),
        ("s1vw_synthetic_orchestrator", _source_digest(s1vw)),
        ("s1vz_resource_calibrator", _source_digest(s1vz)),
    )


class _MemoryStatusEx(ctypes.Structure):
    _fields_ = (
        ("dwLength", wintypes.DWORD),
        ("dwMemoryLoad", wintypes.DWORD),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    )


def _windows_available_physical_memory() -> int:
    status = _MemoryStatusEx()
    status.dwLength = ctypes.sizeof(status)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.GlobalMemoryStatusEx.argtypes = (ctypes.POINTER(_MemoryStatusEx),)
    kernel32.GlobalMemoryStatusEx.restype = wintypes.BOOL
    if not kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise S1WDObservationError(
            S1WD_MEMORY_OBSERVATION_FAILED,
            "available physical memory could not be observed",
        )
    return int(status.ullAvailPhys)


def _available_physical_memory() -> int:
    if os.name == "nt":
        return _windows_available_physical_memory()
    page_size = os.sysconf("SC_PAGE_SIZE")
    available_pages = os.sysconf("SC_AVPHYS_PAGES")
    value = int(page_size) * int(available_pages)
    if value < 0:
        raise S1WDObservationError(
            S1WD_MEMORY_OBSERVATION_FAILED,
            "available physical memory is negative",
        )
    return value


def _volume_identity(path: Path) -> str:
    if os.name == "nt":
        drive = path.drive.upper().rstrip("\\/")
        if not drive:
            raise S1WDObservationError(
                S1WD_INVALID_TEMPORARY_ROOT, "temporary root has no drive"
            )
        return f"WINDOWS-{drive}"
    return f"POSIX-{path.stat().st_dev}"


def _validate_root(root: object) -> Path:
    if not isinstance(root, Path):
        raise S1WDObservationError(
            S1WD_INVALID_TEMPORARY_ROOT, "observer root must be a Path"
        )
    resolved = root.resolve()
    temporary = Path(gettempdir()).resolve()
    production = (_PROJECT_ROOT / "data/generated/ppb1/one_shot").resolve()
    if resolved == production or production in resolved.parents:
        raise S1WDObservationError(
            S1WD_PRODUCTION_ROOT_BLOCKED,
            "S1-WD cannot observe the production artifact root",
        )
    if (
        resolved.name != _ROOT_NAME
        or not resolved.is_dir()
        or temporary not in resolved.parents
    ):
        raise S1WDObservationError(
            S1WD_INVALID_TEMPORARY_ROOT,
            "observer requires a dedicated operating-system temporary root",
        )
    return resolved


def _role_paths(root: Path, execution_id: str) -> tuple[Path, ...]:
    return tuple(
        root / f"{execution_id}.{suffix}"
        for suffix in ("lock.json", "success.json", "error.json", "tmp")
    )


def _atomic_replace_probe(root: Path, execution_id: str) -> bool:
    temporary = root / f".{execution_id}.atomic-probe.tmp"
    terminal = root / f".{execution_id}.atomic-probe.ok"
    if temporary.exists() or terminal.exists():
        raise S1WDObservationError(
            S1WD_ATOMIC_REPLACE_PROBE_FAILED,
            "atomic probe paths are not free",
        )
    payload = _canonical_bytes(
        {
            "schema_version": S1WD_SCHEMA_VERSION,
            "execution_id": execution_id,
            "mode": "TEMPORARY_TEST_ONLY",
        }
    )
    try:
        with temporary.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, terminal)
        if terminal.read_bytes() != payload:
            raise S1WDObservationError(
                S1WD_ATOMIC_REPLACE_PROBE_FAILED,
                "atomic probe payload changed",
            )
        return True
    except S1WDObservationError:
        raise
    except OSError as exc:
        raise S1WDObservationError(
            S1WD_ATOMIC_REPLACE_PROBE_FAILED,
            "atomic replace probe failed",
        ) from exc
    finally:
        if temporary.exists():
            temporary.unlink()
        if terminal.exists():
            terminal.unlink()


@dataclass(frozen=True, slots=True)
class S1WDTemporaryObservationResult:
    execution_id: str
    observation: S1WAProductionResourceObservation
    atomic_probe_count: int
    probe_cleanup_passed: bool
    production_artifact_count: int
    result_digest: str

    def __post_init__(self) -> None:
        if (
            _EXECUTION_ID.fullmatch(self.execution_id) is None
            or not isinstance(
                self.observation, S1WAProductionResourceObservation
            )
            or self.atomic_probe_count != 1
            or self.probe_cleanup_passed is not True
            or self.production_artifact_count != 0
            or self.result_digest != _digest(self.payload_without_digest())
        ):
            raise S1WDObservationError(
                S1WD_INVALID_TEMPORARY_ROOT,
                "invalid temporary observation result",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": S1WD_SCHEMA_VERSION,
            "mode": "TEMPORARY_TEST_ONLY",
            "execution_id": self.execution_id,
            "observation": self.observation.canonical_payload(),
            "atomic_probe_count": self.atomic_probe_count,
            "probe_cleanup_passed": self.probe_cleanup_passed,
            "production_artifact_count": self.production_artifact_count,
        }

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "result_digest": self.result_digest,
        }


def observe_s1wd_temporary_h0(
    root: Path,
    execution_id: str,
) -> S1WDTemporaryObservationResult:
    """Observe real resources only for a dedicated temporary test root."""

    resolved = _validate_root(root)
    if not isinstance(execution_id, str) or _EXECUTION_ID.fullmatch(
        execution_id
    ) is None:
        raise S1WDObservationError(
            S1WD_INVALID_EXECUTION_ID, "invalid synthetic execution id"
        )
    role_paths = _role_paths(resolved, execution_id)
    paths_free = not any(path.exists() for path in role_paths)
    volume = _volume_identity(resolved)
    atomic_passed = _atomic_replace_probe(resolved, execution_id)
    observation = build_s1wb_injected_observation(
        _available_physical_memory(),
        shutil.disk_usage(resolved).free,
        platform_binding=_platform_binding(),
        source_digests=_calibrated_source_digests(),
        artifact_volume_identity=volume,
        temporary_volume_identity=volume,
        same_volume=True,
        atomic_replace_probe_passed=atomic_passed,
        artifact_paths_free=paths_free,
    )
    probe_paths = tuple(resolved.glob(f".{execution_id}.atomic-probe.*"))
    values = {
        "execution_id": execution_id,
        "observation": observation,
        "atomic_probe_count": 1,
        "probe_cleanup_passed": not probe_paths,
        "production_artifact_count": 0,
    }
    payload = {
        "schema_version": S1WD_SCHEMA_VERSION,
        "mode": "TEMPORARY_TEST_ONLY",
        "execution_id": execution_id,
        "observation": observation.canonical_payload(),
        "atomic_probe_count": 1,
        "probe_cleanup_passed": not probe_paths,
        "production_artifact_count": 0,
    }
    return S1WDTemporaryObservationResult(
        **values, result_digest=_digest(payload)
    )


def execute_s1wd_production_once() -> None:
    raise S1WDObservationError(
        S1WD_PRODUCTION_EXECUTION_BLOCKED,
        "S1-WD authorizes temporary resource observation only",
    )
