"""Private S1-VZ three-process synthetic resource calibration."""

from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import shutil
import struct
import subprocess
import sys
from tempfile import TemporaryDirectory

from . import _ppb1_s1vq_corrected_matrix as s1vq
from . import _ppb1_s1vt_result_pipeline as s1vt
from . import _ppb1_s1vw_synthetic_one_shot_handoff as s1vw
from ._ppb1_s1vn_matrix import S1VNCaseReceipt, S1VNStepObservation, s1vn_config
from ._ppb1_s1vq_corrected_matrix import (
    S1VQCaseReceipt,
    S1VQIdentityObservation,
    S1VQMatrixResult,
    s1vq_corrected_matrix_plan,
)


S1VZ_SCHEMA_VERSION = "ppb1.s1vz.synthetic-resource-calibration.v1"
S1VZ_MODULE_NAME = (
    "mcm_field_organism._ppb1_s1vz_synthetic_resource_calibration"
)
S1VZ_CONTRACT_DIGEST = (
    "ed2872f48ef83b26121bc68ce99ff75462cef9fc60915a7b5b073c45744992cd"
)
S1VZ_REPLICATE_COUNT = 3
S1VZ_MIB = 1024**2
S1VZ_GIB = 1024**3
S1VZ_INVALID_CALIBRATION = "S1VZ_INVALID_CALIBRATION"
S1VZ_WORKER_FAILED = "S1VZ_WORKER_FAILED"
S1VZ_PRODUCTION_EXECUTION_BLOCKED = "S1VZ_PRODUCTION_EXECUTION_BLOCKED"

_TRACE_FAMILIES = {"B02", "B04", "B05", "B06"}
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_PLATFORM_ROLES = (
    "python_implementation",
    "python_version",
    "operating_system",
    "machine_architecture",
    "pointer_width_bits",
)
_SOURCE_ROLES = (
    "s1vq_runner",
    "s1vt_pipeline",
    "s1vw_synthetic_orchestrator",
    "s1vz_resource_calibrator",
)


class S1VZCalibrationError(ValueError):
    """One fail-closed calibration boundary violation."""

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


def _file_digest(module: object) -> str:
    return hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()


def _platform_binding() -> tuple[tuple[str, str], ...]:
    return (
        ("python_implementation", platform.python_implementation()),
        ("python_version", platform.python_version()),
        ("operating_system", platform.system()),
        ("machine_architecture", platform.machine()),
        ("pointer_width_bits", str(struct.calcsize("P") * 8)),
    )


def _source_digests() -> tuple[tuple[str, str], ...]:
    return (
        ("s1vq_runner", _file_digest(s1vq)),
        ("s1vt_pipeline", _file_digest(s1vt)),
        ("s1vw_synthetic_orchestrator", _file_digest(s1vw)),
        (
            "s1vz_resource_calibrator",
            hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        ),
    )


class _ProcessMemoryCounters(ctypes.Structure):
    _fields_ = (
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    )


def _windows_memory() -> tuple[int, int]:
    counters = _ProcessMemoryCounters()
    counters.cb = ctypes.sizeof(counters)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel32.GetCurrentProcess.argtypes = ()
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    psapi.GetProcessMemoryInfo.argtypes = (
        wintypes.HANDLE,
        ctypes.POINTER(_ProcessMemoryCounters),
        wintypes.DWORD,
    )
    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    process = kernel32.GetCurrentProcess()
    accepted = psapi.GetProcessMemoryInfo(
        process, ctypes.byref(counters), counters.cb
    )
    if not accepted:
        raise S1VZCalibrationError(
            S1VZ_INVALID_CALIBRATION, "process memory counters unavailable"
        )
    return int(counters.WorkingSetSize), int(counters.PeakWorkingSetSize)


def _posix_memory() -> tuple[int, int]:
    import resource

    peak = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    if platform.system() != "Darwin":
        peak *= 1024
    current = peak
    statm = Path("/proc/self/statm")
    if statm.is_file():
        pages = int(statm.read_text(encoding="ascii").split()[1])
        current = pages * os.sysconf("SC_PAGE_SIZE")
    return current, peak


def _process_memory() -> tuple[int, int]:
    if os.name == "nt":
        return _windows_memory()
    return _posix_memory()


def _synthetic_digest(value: str) -> str:
    return hashlib.sha256(value.encode("ascii")).hexdigest()


def _desired_identity(family: str, fixture: str, index: int) -> str:
    prefix = family.lower()
    if family in _TRACE_FAMILIES:
        return f"{prefix}.trace.000"
    if fixture in {"F01", "F02", "F08"}:
        return f"{prefix}.{fixture.lower()}.single"
    if fixture == "F03":
        return f"{prefix}.f03.{'low' if index % 2 == 0 else 'high'}"
    if fixture == "F07":
        suffix = "released" if index < 0 else str(index)
        return f"{prefix}.f07.{suffix}"
    return f"{prefix}.{fixture.lower()}.slot.{index:06d}"


def _event_is_match(fixture: str, index: int, count: int) -> bool:
    if fixture in {"F01", "F02", "F08"}:
        return index > 0
    if fixture == "F03":
        return index >= 2
    if fixture == "F04":
        return False
    if fixture == "F05":
        return index == count - 2
    return False


def _nonmatch_event(family: str) -> str:
    if family == "PPB1":
        return "CREATED"
    if family in {"B01", "B03"}:
        return "STORED"
    if family in _TRACE_FAMILIES:
        return "UPDATED"
    return "OFF"


def _active_count(family: str, fixture: str, index: int, capacity: int) -> int:
    if family == "B07":
        return 0
    if family in _TRACE_FAMILIES:
        return 1
    if fixture == "F03":
        return min(2, capacity)
    if fixture == "F06":
        return min(index + 1, capacity)
    if fixture == "F07" and index > 0:
        return min(2, capacity)
    return 1


def _constructed_receipt(path) -> S1VQCaseReceipt:
    config = s1vn_config(path.parameter_id, path.modality_id)
    events = []
    observations = []
    identities = []
    for index in range(path.expected_call_count):
        matched = _event_is_match(
            path.fixture_id, index, path.expected_call_count
        )
        event = "MATCHED" if matched else _nonmatch_event(path.family_id)
        if path.family_id == "B07":
            matched = False
            event = "OFF"
        identity_index = index
        if path.fixture_id in {"F01", "F02", "F08"}:
            identity_index = 0
        elif path.fixture_id == "F03":
            identity_index = index % 2
        elif path.fixture_id == "F05" and index == path.expected_call_count - 2:
            identity_index = 0
        assignment = _desired_identity(
            path.family_id, path.fixture_id, identity_index
        )
        selected = assignment if matched else None
        if path.family_id == "B07":
            written = None
        elif path.family_id == "B03" and matched:
            written = None
        elif path.family_id == "B01" and matched:
            written = f"b01.synthetic.{path.fixture_id.lower()}.{index:06d}"
        else:
            written = assignment
        active = _active_count(
            path.family_id, path.fixture_id, index, config.capacity
        )
        if path.family_id == "B02":
            occupied = min(index + 1, config.capacity)
            logical = (occupied + 1) * len(config.carrier_ids)
        elif path.family_id in _TRACE_FAMILIES:
            occupied = 0
            logical = len(config.carrier_ids)
        else:
            occupied = active
            logical = active * len(config.carrier_ids)
        events.append(event)
        observations.append(
            S1VNStepObservation(
                index + 1,
                event,
                0.0 if matched else None,
                logical,
                occupied,
                active if path.family_id == "PPB1" else 0,
                selected or written,
                0.0 if path.family_id == "PPB1" else None,
            )
        )
        identities.append(
            S1VQIdentityObservation(
                index + 1,
                selected,
                written,
                _synthetic_digest(f"prestate:{assignment}") if selected else None,
                active,
                _synthetic_digest(
                    f"active:{path.family_id}:{path.parameter_id}:"
                    f"{path.modality_id}:{path.fixture_id}:{index}:{active}"
                ),
            )
        )
    history_digest = _synthetic_digest(
        f"history:{path.parameter_id}:{path.modality_id}:{path.fixture_id}"
    )
    final_digest = _synthetic_digest(
        f"final:{path.family_id}:{path.parameter_id}:"
        f"{path.modality_id}:{path.fixture_id}"
    )
    base = S1VNCaseReceipt(
        path.path_id,
        path.family_id,
        path.expected_call_count,
        tuple(events),
        tuple(observations),
        history_digest,
        final_digest,
    )
    return S1VQCaseReceipt(path, base, tuple(identities))


def _constructed_legacy_result() -> S1VQMatrixResult:
    receipts = tuple(
        _constructed_receipt(path) for path in s1vq_corrected_matrix_plan()
    )
    comparisons = tuple(
        (receipt.path.path_id, receipt.repeat_comparison_digest())
        for receipt in receipts
        if receipt.path.repeat_id == "R1"
    )
    return S1VQMatrixResult(
        s1vw.S1VW_CORRECTED_PLAN_DIGEST,
        receipts,
        s1vw.S1VW_EXPECTED_CALL_COUNT,
        comparisons,
    )


@dataclass(frozen=True, slots=True)
class S1VZReplicateReceipt:
    replicate_id: str
    platform_binding: tuple[tuple[str, str], ...]
    source_digests: tuple[tuple[str, str], ...]
    process_rss_before_fixture_bytes: int
    process_peak_rss_after_fixture_bytes: int
    process_peak_rss_after_seal_bytes: int
    process_peak_rss_after_composition_bytes: int
    process_peak_rss_after_evaluation_bytes: int
    process_peak_rss_after_serialization_bytes: int
    peak_increment_over_initial_rss_bytes: int
    lock_artifact_bytes: int
    success_artifact_bytes: int
    temporary_artifact_peak_bytes: int
    artifact_volume_free_bytes_before: int
    artifact_volume_free_bytes_after: int
    same_volume_atomic_replace_passed: bool
    terminal_digest: str

    def __post_init__(self) -> None:
        numeric = (
            self.process_rss_before_fixture_bytes,
            self.process_peak_rss_after_fixture_bytes,
            self.process_peak_rss_after_seal_bytes,
            self.process_peak_rss_after_composition_bytes,
            self.process_peak_rss_after_evaluation_bytes,
            self.process_peak_rss_after_serialization_bytes,
            self.peak_increment_over_initial_rss_bytes,
            self.lock_artifact_bytes,
            self.success_artifact_bytes,
            self.temporary_artifact_peak_bytes,
            self.artifact_volume_free_bytes_before,
            self.artifact_volume_free_bytes_after,
        )
        peaks = numeric[1:6]
        if (
            self.replicate_id not in {"R1", "R2", "R3"}
            or tuple(role for role, _ in self.platform_binding)
            != _PLATFORM_ROLES
            or any(not value for _, value in self.platform_binding)
            or tuple(role for role, _ in self.source_digests) != _SOURCE_ROLES
            or any(_DIGEST.fullmatch(value) is None for _, value in self.source_digests)
            or any(
                isinstance(value, bool) or not isinstance(value, int) or value < 0
                for value in numeric
            )
            or peaks != tuple(sorted(peaks))
            or self.peak_increment_over_initial_rss_bytes
            != max(0, max(peaks) - self.process_rss_before_fixture_bytes)
            or min(
                self.lock_artifact_bytes,
                self.success_artifact_bytes,
                self.temporary_artifact_peak_bytes,
            )
            <= 0
            or self.same_volume_atomic_replace_passed is not True
            or _DIGEST.fullmatch(self.terminal_digest) is None
        ):
            raise S1VZCalibrationError(
                S1VZ_INVALID_CALIBRATION, "invalid replicate receipt"
            )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": S1VZ_SCHEMA_VERSION,
            "contract_digest": S1VZ_CONTRACT_DIGEST,
            "replicate_id": self.replicate_id,
            "platform_binding": [
                {"role": role, "value": value}
                for role, value in self.platform_binding
            ],
            "source_digests": [
                {"role": role, "digest": digest}
                for role, digest in self.source_digests
            ],
            "process_rss_before_fixture_bytes": self.process_rss_before_fixture_bytes,
            "process_peak_rss_after_fixture_bytes": (
                self.process_peak_rss_after_fixture_bytes
            ),
            "process_peak_rss_after_seal_bytes": self.process_peak_rss_after_seal_bytes,
            "process_peak_rss_after_composition_bytes": (
                self.process_peak_rss_after_composition_bytes
            ),
            "process_peak_rss_after_evaluation_bytes": (
                self.process_peak_rss_after_evaluation_bytes
            ),
            "process_peak_rss_after_serialization_bytes": (
                self.process_peak_rss_after_serialization_bytes
            ),
            "peak_increment_over_initial_rss_bytes": (
                self.peak_increment_over_initial_rss_bytes
            ),
            "lock_artifact_bytes": self.lock_artifact_bytes,
            "success_artifact_bytes": self.success_artifact_bytes,
            "temporary_artifact_peak_bytes": self.temporary_artifact_peak_bytes,
            "artifact_volume_free_bytes_before": self.artifact_volume_free_bytes_before,
            "artifact_volume_free_bytes_after": self.artifact_volume_free_bytes_after,
            "same_volume_atomic_replace_passed": self.same_volume_atomic_replace_passed,
            "terminal_digest": self.terminal_digest,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def _round_up_mib(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise S1VZCalibrationError(
            S1VZ_INVALID_CALIBRATION, "resource value must be a nonnegative integer"
        )
    return math.ceil(value / S1VZ_MIB) * S1VZ_MIB


def memory_gate_bytes(observed_peak_increment_bytes: int) -> int:
    value = max(
        2 * observed_peak_increment_bytes,
        observed_peak_increment_bytes + 512 * S1VZ_MIB,
        2 * S1VZ_GIB,
    )
    return _round_up_mib(value)


def disk_gate_bytes(
    observed_success_artifact_bytes: int,
    observed_temporary_artifact_peak_bytes: int,
) -> int:
    artifact = max(
        observed_success_artifact_bytes,
        observed_temporary_artifact_peak_bytes,
    )
    value = max(3 * artifact, artifact + 512 * S1VZ_MIB, S1VZ_GIB)
    return _round_up_mib(value)


@dataclass(frozen=True, slots=True)
class S1VZCalibrationResult:
    platform_binding: tuple[tuple[str, str], ...]
    source_digests: tuple[tuple[str, str], ...]
    replicate_receipts: tuple[S1VZReplicateReceipt, ...]
    observed_peak_increment_bytes: int
    observed_success_artifact_bytes: int
    observed_temporary_artifact_peak_bytes: int
    minimum_free_memory_bytes: int
    minimum_free_disk_bytes: int
    all_atomic_replace_checks_passed: bool
    production_execution_authorized: bool

    def __post_init__(self) -> None:
        if (
            len(self.replicate_receipts) != S1VZ_REPLICATE_COUNT
            or self.observed_peak_increment_bytes
            != max(
                item.peak_increment_over_initial_rss_bytes
                for item in self.replicate_receipts
            )
            or self.observed_success_artifact_bytes
            != max(item.success_artifact_bytes for item in self.replicate_receipts)
            or self.observed_temporary_artifact_peak_bytes
            != max(
                item.temporary_artifact_peak_bytes
                for item in self.replicate_receipts
            )
            or self.minimum_free_memory_bytes
            != memory_gate_bytes(self.observed_peak_increment_bytes)
            or self.minimum_free_disk_bytes
            != disk_gate_bytes(
                self.observed_success_artifact_bytes,
                self.observed_temporary_artifact_peak_bytes,
            )
            or self.all_atomic_replace_checks_passed is not True
            or self.production_execution_authorized is not False
        ):
            raise S1VZCalibrationError(
                S1VZ_INVALID_CALIBRATION, "invalid aggregate calibration result"
            )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": S1VZ_SCHEMA_VERSION,
            "contract_digest": S1VZ_CONTRACT_DIGEST,
            "mode": "SYNTHETIC_CALIBRATION_ONLY",
            "platform_binding": [
                {"role": role, "value": value}
                for role, value in self.platform_binding
            ],
            "source_digests": [
                {"role": role, "digest": digest}
                for role, digest in self.source_digests
            ],
            "replicate_receipts": [
                receipt.canonical_payload() for receipt in self.replicate_receipts
            ],
            "observed_peak_increment_bytes": self.observed_peak_increment_bytes,
            "observed_success_artifact_bytes": self.observed_success_artifact_bytes,
            "observed_temporary_artifact_peak_bytes": (
                self.observed_temporary_artifact_peak_bytes
            ),
            "minimum_free_memory_bytes": self.minimum_free_memory_bytes,
            "minimum_free_disk_bytes": self.minimum_free_disk_bytes,
            "all_atomic_replace_checks_passed": self.all_atomic_replace_checks_passed,
            "production_execution_authorized": self.production_execution_authorized,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def aggregate_s1vz_receipts(
    receipts: tuple[S1VZReplicateReceipt, ...],
) -> S1VZCalibrationResult:
    if (
        len(receipts) != S1VZ_REPLICATE_COUNT
        or tuple(item.replicate_id for item in receipts)
        != tuple(f"R{index}" for index in range(1, 4))
        or len({item.digest() for item in receipts}) != S1VZ_REPLICATE_COUNT
        or any(
            item.platform_binding != receipts[0].platform_binding
            for item in receipts
        )
        or any(item.source_digests != receipts[0].source_digests for item in receipts)
        or not all(item.same_volume_atomic_replace_passed for item in receipts)
    ):
        raise S1VZCalibrationError(
            S1VZ_INVALID_CALIBRATION, "three clean comparable receipts are required"
        )
    numeric_roles = (
        "process_rss_before_fixture_bytes",
        "process_peak_rss_after_fixture_bytes",
        "process_peak_rss_after_seal_bytes",
        "process_peak_rss_after_composition_bytes",
        "process_peak_rss_after_evaluation_bytes",
        "process_peak_rss_after_serialization_bytes",
        "peak_increment_over_initial_rss_bytes",
        "lock_artifact_bytes",
        "success_artifact_bytes",
        "temporary_artifact_peak_bytes",
        "artifact_volume_free_bytes_before",
        "artifact_volume_free_bytes_after",
    )
    for receipt in receipts:
        values = tuple(getattr(receipt, role) for role in numeric_roles)
        peaks = values[1:6]
        if (
            any(
                isinstance(value, bool)
                or not isinstance(value, int)
                or value < 0
                for value in values
            )
            or peaks != tuple(sorted(peaks))
            or receipt.peak_increment_over_initial_rss_bytes
            != max(0, max(peaks) - receipt.process_rss_before_fixture_bytes)
            or receipt.lock_artifact_bytes <= 0
            or receipt.success_artifact_bytes <= 0
            or receipt.temporary_artifact_peak_bytes <= 0
        ):
            raise S1VZCalibrationError(
                S1VZ_INVALID_CALIBRATION, "replicate resource ledger is invalid"
            )
    peak = max(item.peak_increment_over_initial_rss_bytes for item in receipts)
    success = max(item.success_artifact_bytes for item in receipts)
    temporary = max(item.temporary_artifact_peak_bytes for item in receipts)
    return S1VZCalibrationResult(
        receipts[0].platform_binding,
        receipts[0].source_digests,
        receipts,
        peak,
        success,
        temporary,
        memory_gate_bytes(peak),
        disk_gate_bytes(success, temporary),
        True,
        False,
    )


def _receipt_from_payload(payload: dict[str, object]) -> S1VZReplicateReceipt:
    try:
        return S1VZReplicateReceipt(
            str(payload["replicate_id"]),
            tuple(
                (str(item["role"]), str(item["value"]))
                for item in payload["platform_binding"]
            ),
            tuple(
                (str(item["role"]), str(item["digest"]))
                for item in payload["source_digests"]
            ),
            *(
                int(payload[role])
                for role in (
                    "process_rss_before_fixture_bytes",
                    "process_peak_rss_after_fixture_bytes",
                    "process_peak_rss_after_seal_bytes",
                    "process_peak_rss_after_composition_bytes",
                    "process_peak_rss_after_evaluation_bytes",
                    "process_peak_rss_after_serialization_bytes",
                    "peak_increment_over_initial_rss_bytes",
                    "lock_artifact_bytes",
                    "success_artifact_bytes",
                    "temporary_artifact_peak_bytes",
                    "artifact_volume_free_bytes_before",
                    "artifact_volume_free_bytes_after",
                )
            ),
            bool(payload["same_volume_atomic_replace_passed"]),
            str(payload["terminal_digest"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise S1VZCalibrationError(
            S1VZ_INVALID_CALIBRATION, "worker receipt payload is invalid"
        ) from exc


def _run_worker(replicate_id: str) -> S1VZReplicateReceipt:
    if replicate_id not in {"R1", "R2", "R3"}:
        raise S1VZCalibrationError(
            S1VZ_INVALID_CALIBRATION, "invalid replicate id"
        )
    initial_rss, _ = _process_memory()
    stage_peaks: dict[str, int] = {}
    artifact_sizes: dict[str, int] = {}

    with TemporaryDirectory(prefix=f"s1vz-{replicate_id.lower()}-") as temporary:
        root = Path(temporary) / "s1vw-synthetic-artifacts"
        root.mkdir()
        free_before = shutil.disk_usage(root).free

        def producer() -> S1VQMatrixResult:
            result = _constructed_legacy_result()
            stage_peaks["fixture"] = _process_memory()[1]
            return result

        def seal(receipts):
            result = s1vt.seal_s1vt_matrix_result(receipts)
            stage_peaks["seal"] = _process_memory()[1]
            return result

        def compose(matrix):
            result = s1vt.compose_s1vt_arm_records(matrix)
            stage_peaks["composition"] = _process_memory()[1]
            return result

        def evaluate(composition):
            result = s1vt.evaluate_s1vt_composition(composition)
            stage_peaks["evaluation"] = _process_memory()[1]
            return result

        def publish(target, temporary_path, counterpart, payload):
            encoded = _canonical_bytes(payload)
            artifact_sizes["temporary"] = len(encoded)
            if target.exists() or temporary_path.exists() or counterpart.exists():
                raise S1VZCalibrationError(
                    S1VZ_INVALID_CALIBRATION, "terminal paths are not free"
                )
            with temporary_path.open("xb") as handle:
                handle.write(encoded)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, target)
            artifact_sizes["success"] = target.stat().st_size
            stage_peaks["serialization"] = _process_memory()[1]

        token = s1vw.S1VWSyntheticAuthorizationToken(
            f"s1vw.synthetic.s1vz-{replicate_id.lower()}"
        )
        outcome = s1vw.run_s1vw_synthetic_once(
            token,
            producer,
            root,
            seal_adapter=seal,
            compose_adapter=compose,
            evaluate_adapter=evaluate,
            publisher=publish,
        )
        if not isinstance(outcome, s1vw.S1VWSuccessOutcome):
            raise S1VZCalibrationError(
                S1VZ_INVALID_CALIBRATION, "synthetic calibration did not succeed"
            )
        lock = next(root.glob("*.lock.json"))
        success = next(root.glob("*.success.json"))
        free_after = shutil.disk_usage(root).free
        ordered_peaks = tuple(
            stage_peaks[role]
            for role in (
                "fixture",
                "seal",
                "composition",
                "evaluation",
                "serialization",
            )
        )
        return S1VZReplicateReceipt(
            replicate_id,
            _platform_binding(),
            _source_digests(),
            initial_rss,
            *ordered_peaks,
            max(0, max(ordered_peaks) - initial_rss),
            lock.stat().st_size,
            success.stat().st_size,
            artifact_sizes["temporary"],
            free_before,
            free_after,
            success.is_file() and not any(root.glob("*.tmp")),
            outcome.terminal_digest,
        )


def run_s1vz_three_process_calibration() -> S1VZCalibrationResult:
    """Execute exactly three synthetic workers and no production path."""

    receipts = []
    for replicate_id in ("R1", "R2", "R3"):
        completed = subprocess.run(
            [sys.executable, "-m", S1VZ_MODULE_NAME, "--worker", replicate_id],
            check=False,
            capture_output=True,
            text=True,
            cwd=Path(__file__).resolve().parents[1],
        )
        if completed.returncode != 0:
            raise S1VZCalibrationError(
                S1VZ_WORKER_FAILED,
                f"{replicate_id} failed with exit code {completed.returncode}",
            )
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise S1VZCalibrationError(
                S1VZ_WORKER_FAILED, f"{replicate_id} returned invalid JSON"
            ) from exc
        receipts.append(_receipt_from_payload(payload))
    return aggregate_s1vz_receipts(tuple(receipts))


def execute_s1vz_production_once() -> None:
    raise S1VZCalibrationError(
        S1VZ_PRODUCTION_EXECUTION_BLOCKED,
        "S1-VZ authorizes synthetic calibration only",
    )


def _main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--worker", choices=("R1", "R2", "R3"))
    parser.add_argument("--calibrate", action="store_true")
    args = parser.parse_args()
    if args.worker is not None and not args.calibrate:
        print(json.dumps(_run_worker(args.worker).canonical_payload(), sort_keys=True))
        return 0
    if args.calibrate and args.worker is None:
        result = run_s1vz_three_process_calibration()
        payload = {**result.canonical_payload(), "calibration_digest": result.digest()}
        print(json.dumps(payload, sort_keys=True))
        return 0
    raise S1VZCalibrationError(
        S1VZ_INVALID_CALIBRATION, "exactly one calibration mode is required"
    )


if __name__ == "__main__":
    raise SystemExit(_main())
