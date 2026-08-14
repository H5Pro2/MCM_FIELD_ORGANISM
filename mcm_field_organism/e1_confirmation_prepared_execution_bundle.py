"""Private S1-EC1 prepared-input lifecycle prototype; synthetic only."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any

from .e1_confirmation_research_corridor import (
    E1ConfirmationSyntheticRunContract,
    S1_EC3_ATTEMPT,
    S1_EC3_LOCK,
    S1_EC3_REPORT,
    S1_EC3_RUN_ID,
)
from .e1_refined_formation_runner import _digest


class E1ConfirmationPreparedBundleError(RuntimeError):
    """Raised when the S1-EC1 prepared-input lifecycle fails closed."""


S1_EC1_EXECUTION_ID = "e1.confirmation-prepared-bundle.s1ec1.synthetic.v1"
S1_EC1_REPORT = "e1_confirmation_s1ec1_synthetic_once_v1.json"
S1_EC1_ATTEMPT = "e1_confirmation_s1ec1_synthetic_once_v1.attempt.json"
S1_EC1_LOCK = "e1_confirmation_s1ec1_synthetic_once_v1.lock"
S1_EC1_UNBOUND_RUN_DIGEST = _digest(
    {"execution_id": S1_EC1_EXECUTION_ID, "run_contract": "legacy-unbound"}
)


def _execution_profile(execution_id: str) -> tuple[str, str, str] | None:
    return {
        S1_EC1_EXECUTION_ID: (S1_EC1_REPORT, S1_EC1_ATTEMPT, S1_EC1_LOCK),
        S1_EC3_RUN_ID: (S1_EC3_REPORT, S1_EC3_ATTEMPT, S1_EC3_LOCK),
    }.get(execution_id)


def _valid_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


DigestReader = Callable[[Any], str]
PreparedInputResolver = Callable[[], Iterable["E1PreparedRuntimeInput"]]
PreparedBundleConsumer = Callable[["E1PreparedExecutionBundle"], str]


@dataclass(frozen=True, slots=True)
class E1PreparedRuntimeInput:
    """Bind one concrete runtime object to its pre-marker digest reader."""

    role: str
    value: Any
    prepared_digest: str
    digest_reader: DigestReader

    def __post_init__(self) -> None:
        if (
            not self.role
            or not self.role.isascii()
            or not _valid_digest(self.prepared_digest)
            or not callable(self.digest_reader)
        ):
            raise E1ConfirmationPreparedBundleError(
                "S1-EC1 prepared runtime input is invalid"
            )
        self.require_unchanged()

    def current_digest(self) -> str:
        observed = self.digest_reader(self.value)
        if not _valid_digest(observed):
            raise E1ConfirmationPreparedBundleError(
                f"S1-EC1 {self.role} digest reader returned no SHA-256"
            )
        return observed

    def require_unchanged(self) -> None:
        if self.current_digest() != self.prepared_digest:
            raise E1ConfirmationPreparedBundleError(
                f"S1-EC1 prepared input changed: {self.role}"
            )


@dataclass(frozen=True, slots=True)
class E1PreparedExecutionBundle:
    """Carry already resolved runtime objects across the attempt boundary."""

    execution_id: str
    report_path: str
    attempt_path: str
    lock_path: str
    run_contract_digest: str
    inputs: tuple[E1PreparedRuntimeInput, ...]
    input_manifest: tuple[tuple[str, str], ...]
    prepared_before_markers: bool
    synthetic_only: bool
    canonical_execution_permitted: bool
    claims_permitted: bool
    bundle_digest: str

    def __post_init__(self) -> None:
        inputs = tuple(self.inputs)
        manifest = tuple((item.role, item.prepared_digest) for item in inputs)
        paths = tuple(
            Path(value) for value in (self.report_path, self.attempt_path, self.lock_path)
        )
        profile = _execution_profile(self.execution_id)
        if (
            profile is None
            or not _valid_digest(self.run_contract_digest)
            or not inputs
            or len({item.role for item in inputs}) != len(inputs)
            or self.input_manifest != manifest
            or len(set(paths)) != 3
            or len({path.parent for path in paths}) != 1
            or tuple(path.name for path in paths) != profile
            or self.prepared_before_markers is not True
            or self.synthetic_only is not True
            or self.canonical_execution_permitted is not False
            or self.claims_permitted is not False
        ):
            raise E1ConfirmationPreparedBundleError(
                "S1-EC1 prepared execution bundle changed"
            )
        payload = {
            "execution_id": self.execution_id,
            "report_path": self.report_path,
            "attempt_path": self.attempt_path,
            "lock_path": self.lock_path,
            "run_contract_digest": self.run_contract_digest,
            "input_manifest": self.input_manifest,
            "prepared_before_markers": self.prepared_before_markers,
            "synthetic_only": self.synthetic_only,
            "canonical_execution_permitted": self.canonical_execution_permitted,
            "claims_permitted": self.claims_permitted,
        }
        if self.bundle_digest != _digest(payload):
            raise E1ConfirmationPreparedBundleError(
                "S1-EC1 bundle digest does not match its manifest"
            )
        object.__setattr__(self, "inputs", inputs)
        self.require_inputs_unchanged()

    def require_inputs_unchanged(self) -> None:
        for item in self.inputs:
            item.require_unchanged()

    def value(self, role: str) -> Any:
        for item in self.inputs:
            if item.role == role:
                return item.value
        raise E1ConfirmationPreparedBundleError(
            f"S1-EC1 prepared input is missing: {role}"
        )

    def digest(self) -> str:
        return _digest(
            {
                "execution_id": self.execution_id,
                "report_path": self.report_path,
                "attempt_path": self.attempt_path,
                "lock_path": self.lock_path,
                "run_contract_digest": self.run_contract_digest,
                "input_manifest": self.input_manifest,
                "prepared_before_markers": self.prepared_before_markers,
                "synthetic_only": self.synthetic_only,
                "canonical_execution_permitted": self.canonical_execution_permitted,
                "claims_permitted": self.claims_permitted,
                "bundle_digest": self.bundle_digest,
            }
        )


@dataclass(frozen=True, slots=True)
class E1PreparedSyntheticReceipt:
    execution_id: str
    run_contract_digest: str
    bundle_digest: str
    consumer_digest: str
    report_path: str
    report_sha256: str
    attempt_removed_after_verified_publish: bool
    lock_released: bool
    synthetic_only: bool
    canonical_execution_permitted: bool
    claims_permitted: bool

    def __post_init__(self) -> None:
        profile = _execution_profile(self.execution_id)
        if (
            profile is None
            or not _valid_digest(self.run_contract_digest)
            or not _valid_digest(self.bundle_digest)
            or not _valid_digest(self.consumer_digest)
            or Path(self.report_path).name != profile[0]
            or not _valid_digest(self.report_sha256)
            or self.attempt_removed_after_verified_publish is not True
            or self.lock_released is not True
            or self.synthetic_only is not True
            or self.canonical_execution_permitted is not False
            or self.claims_permitted is not False
        ):
            raise E1ConfirmationPreparedBundleError(
                "S1-EC1 synthetic receipt changed"
            )


def _bundle_payload(
    execution_id: str,
    paths: tuple[Path, Path, Path],
    run_contract_digest: str,
    inputs: tuple[E1PreparedRuntimeInput, ...],
) -> dict[str, object]:
    return {
        "execution_id": execution_id,
        "report_path": str(paths[0]),
        "attempt_path": str(paths[1]),
        "lock_path": str(paths[2]),
        "run_contract_digest": run_contract_digest,
        "input_manifest": tuple(
            (item.role, item.prepared_digest) for item in inputs
        ),
        "prepared_before_markers": True,
        "synthetic_only": True,
        "canonical_execution_permitted": False,
        "claims_permitted": False,
    }


def prepare_e1_confirmation_execution_bundle(
    synthetic_directory: Path,
    resolver: PreparedInputResolver,
) -> E1PreparedExecutionBundle:
    """Resolve and bind concrete inputs once while all synthetic paths are free."""

    directory = Path(synthetic_directory).resolve()
    if not directory.is_dir() or directory == Path("reports").resolve():
        raise E1ConfirmationPreparedBundleError(
            "S1-EC1 requires an existing synthetic directory outside reports"
        )
    targets = (
        directory / S1_EC1_REPORT,
        directory / S1_EC1_ATTEMPT,
        directory / S1_EC1_LOCK,
    )
    if any(path.exists() for path in targets):
        raise E1ConfirmationPreparedBundleError(
            "S1-EC1 synthetic one-shot path is already used"
        )
    if not callable(resolver):
        raise E1ConfirmationPreparedBundleError(
            "S1-EC1 requires one prepared-input resolver"
        )
    inputs = tuple(resolver())
    if not inputs or any(not isinstance(item, E1PreparedRuntimeInput) for item in inputs):
        raise E1ConfirmationPreparedBundleError(
            "S1-EC1 resolver returned invalid prepared inputs"
        )
    payload = _bundle_payload(
        S1_EC1_EXECUTION_ID,
        targets,
        S1_EC1_UNBOUND_RUN_DIGEST,
        inputs,
    )
    return E1PreparedExecutionBundle(
        **payload,
        inputs=inputs,
        bundle_digest=_digest(payload),
    )


def prepare_e1_confirmation_execution_bundle_from_run_contract(
    run_contract: E1ConfirmationSyntheticRunContract,
    resolver: PreparedInputResolver,
) -> E1PreparedExecutionBundle:
    """Bind inputs to the exact identity and paths supplied by S1-EC3."""

    if not isinstance(run_contract, E1ConfirmationSyntheticRunContract):
        raise E1ConfirmationPreparedBundleError(
            "S1-EC6 requires one S1-EC3 synthetic run contract"
        )
    run_contract.__post_init__()
    if not callable(resolver):
        raise E1ConfirmationPreparedBundleError(
            "S1-EC6 requires one prepared-input resolver"
        )
    inputs = tuple(resolver())
    if not inputs or any(not isinstance(item, E1PreparedRuntimeInput) for item in inputs):
        raise E1ConfirmationPreparedBundleError(
            "S1-EC6 resolver returned invalid prepared inputs"
        )
    paths = (
        Path(run_contract.report_path),
        Path(run_contract.attempt_path),
        Path(run_contract.lock_path),
    )
    if any(path.exists() for path in paths):
        raise E1ConfirmationPreparedBundleError(
            "S1-EC6 synthetic one-shot path is already used"
        )
    payload = _bundle_payload(
        run_contract.execution_id,
        paths,
        run_contract.digest(),
        inputs,
    )
    return E1PreparedExecutionBundle(
        **payload,
        inputs=inputs,
        bundle_digest=_digest(payload),
    )


def _exclusive_marker(path: Path, payload: dict[str, object]) -> None:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ) + "\n"
    try:
        with path.open("x", encoding="ascii", newline="\n") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise E1ConfirmationPreparedBundleError(
            f"S1-EC1 marker already exists: {path.name}"
        ) from exc


def _atomic_publish(target: Path, payload: dict[str, object]) -> bytes:
    encoded = (
        json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=False,
        )
        + "\n"
    ).encode("ascii")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=target.name + ".tmp.", dir=target.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        if temporary.read_bytes() != encoded:
            raise E1ConfirmationPreparedBundleError(
                "S1-EC1 temporary report reread failed"
            )
        try:
            os.link(temporary, target)
        except FileExistsError as exc:
            raise E1ConfirmationPreparedBundleError(
                "S1-EC1 synthetic report already exists"
            ) from exc
        if target.read_bytes() != encoded:
            raise E1ConfirmationPreparedBundleError(
                "S1-EC1 published report differs"
            )
        return encoded
    finally:
        temporary.unlink(missing_ok=True)


def execute_prepared_bundle_synthetically(
    bundle: E1PreparedExecutionBundle,
    consumer: PreparedBundleConsumer,
) -> E1PreparedSyntheticReceipt:
    """Consume only a prepared bundle after Attempt; never invoke a resolver."""

    if not isinstance(bundle, E1PreparedExecutionBundle) or not callable(consumer):
        raise E1ConfirmationPreparedBundleError(
            "S1-EC1 requires one prepared bundle and one synthetic consumer"
        )
    bundle.__post_init__()
    report = Path(bundle.report_path)
    attempt = Path(bundle.attempt_path)
    lock = Path(bundle.lock_path)
    if any(path.exists() for path in (report, attempt, lock)):
        raise E1ConfirmationPreparedBundleError(
            "S1-EC1 synthetic one-shot path is already used"
        )
    _exclusive_marker(
        lock,
        {
            "execution_id": bundle.execution_id,
            "bundle_digest": bundle.bundle_digest,
            "run_contract_digest": bundle.run_contract_digest,
            "synthetic_only": True,
        },
    )
    attempt_created = False
    try:
        _exclusive_marker(
            attempt,
            {
                "execution_id": bundle.execution_id,
                "bundle_digest": bundle.bundle_digest,
                "run_contract_digest": bundle.run_contract_digest,
                "failure_policy": "retain-attempt-marker-no-automatic-retry",
                "synthetic_only": True,
            },
        )
        attempt_created = True
        consumer_digest = consumer(bundle)
        if not _valid_digest(consumer_digest):
            raise E1ConfirmationPreparedBundleError(
                "S1-EC1 synthetic consumer returned no SHA-256"
            )
        bundle.require_inputs_unchanged()
        report_payload = {
            "execution_id": bundle.execution_id,
            "bundle_digest": bundle.bundle_digest,
            "run_contract_digest": bundle.run_contract_digest,
            "input_manifest": bundle.input_manifest,
            "consumer_digest": consumer_digest,
            "synthetic_only": True,
            "canonical_execution_permitted": False,
            "claims_permitted": False,
        }
        encoded = _atomic_publish(report, report_payload)
        report_sha256 = hashlib.sha256(encoded).hexdigest()
        if hashlib.sha256(report.read_bytes()).hexdigest() != report_sha256:
            raise E1ConfirmationPreparedBundleError(
                "S1-EC1 final report verification failed"
            )
        attempt.unlink()
        return E1PreparedSyntheticReceipt(
            execution_id=bundle.execution_id,
            run_contract_digest=bundle.run_contract_digest,
            bundle_digest=bundle.bundle_digest,
            consumer_digest=consumer_digest,
            report_path=str(report),
            report_sha256=report_sha256,
            attempt_removed_after_verified_publish=True,
            lock_released=True,
            synthetic_only=True,
            canonical_execution_permitted=False,
            claims_permitted=False,
        )
    finally:
        lock.unlink(missing_ok=True)
        if not attempt_created:
            attempt.unlink(missing_ok=True)
