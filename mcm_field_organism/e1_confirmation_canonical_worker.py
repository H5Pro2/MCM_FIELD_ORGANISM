"""Private S1-EB26 canonical worker shape with synthetic kernels only."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import tempfile

from .e1_confirmation_canonical_producer_binding import (
    E1ConfirmationCanonicalProducerBinding,
)
from .e1_confirmation_chain_contract import E1ConfirmationChainContract
from .e1_confirmation_owner_authorization import (
    E1ConfirmationOwnerAuthorization,
)
from .e1_confirmation_release_contract import E1ConfirmationReleaseContract
from .e1_confirmation_released_worker_audit import (
    E1ConfirmationReleasedWorkerAudit,
)
from .e1_confirmation_resource_guard import (
    E1ConfirmationResourceGuardBinding,
)
from .e1_confirmation_same_session_preflight import (
    prepare_e1_confirmation_same_session_preflight,
    require_fresh_e1_confirmation_preflight,
)
from .e1_refined_formation_runner import _digest


class E1ConfirmationCanonicalWorkerError(RuntimeError):
    """Raised when the S1-EB26 worker cannot preserve exactly-once rules."""


S1_EB25_AUDIT_DIGEST = (
    "90fc412b115196b85f17fda24446308dbdb2752ed920c3c990c926dc635ed57d"
)
S1_EB26_SYNTHETIC_STAGE_ORDER = (
    "formation",
    "probe_handoff",
    "probe_r2_r4_r8",
    "result_handoff",
    "result_composition",
    "report_handoff",
)
S1_EB26_SYNTHETIC_REPORT = "e1_confirmation_s1eb26_synthetic_once_v1.json"
S1_EB26_SYNTHETIC_ATTEMPT = (
    "e1_confirmation_s1eb26_synthetic_once_v1.attempt.json"
)
S1_EB26_SYNTHETIC_LOCK = "e1_confirmation_s1eb26_synthetic_once_v1.lock"


def _valid_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


SyntheticKernel = Callable[[str], str]


@dataclass(frozen=True, slots=True)
class E1ConfirmationSyntheticKernelSet:
    formation: SyntheticKernel
    probe_handoff: SyntheticKernel
    probe_r2_r4_r8: SyntheticKernel
    result_handoff: SyntheticKernel
    result_composition: SyntheticKernel
    report_handoff: SyntheticKernel

    def __post_init__(self) -> None:
        if any(
            not callable(getattr(self, role))
            for role in S1_EB26_SYNTHETIC_STAGE_ORDER
        ):
            raise E1ConfirmationCanonicalWorkerError(
                "S1-EB26 requires all synthetic kernel replacements"
            )


@dataclass(frozen=True, slots=True)
class E1ConfirmationSyntheticWorkerReceipt:
    execution_id: str
    audit_digest: str
    preflight_digest: str
    stage_digests: tuple[tuple[str, str], ...]
    report_path: str
    report_sha256: str
    attempt_removed_after_verified_publish: bool
    lock_released: bool
    synthetic_only: bool
    canonical_execution_permitted: bool
    claims_permitted: bool
    receipt_digest: str

    def __post_init__(self) -> None:
        if (
            self.execution_id != "e1.confirmation-worker.s1eb26.synthetic.once.v1"
            or self.audit_digest != S1_EB25_AUDIT_DIGEST
            or not _valid_digest(self.preflight_digest)
            or tuple(role for role, _ in self.stage_digests)
            != S1_EB26_SYNTHETIC_STAGE_ORDER
            or any(not _valid_digest(value) for _, value in self.stage_digests)
            or Path(self.report_path).name != S1_EB26_SYNTHETIC_REPORT
            or not _valid_digest(self.report_sha256)
            or self.attempt_removed_after_verified_publish is not True
            or self.lock_released is not True
            or self.synthetic_only is not True
            or self.canonical_execution_permitted is not False
            or self.claims_permitted is not False
        ):
            raise E1ConfirmationCanonicalWorkerError(
                "S1-EB26 synthetic worker receipt changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "receipt_digest"
        }
        if self.receipt_digest != _digest(payload):
            raise E1ConfirmationCanonicalWorkerError(
                "S1-EB26 receipt digest does not match its payload"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


def _validate_worker_inputs(
    binding: E1ConfirmationCanonicalProducerBinding,
    chain: E1ConfirmationChainContract,
    release: E1ConfirmationReleaseContract,
    authorization: E1ConfirmationOwnerAuthorization,
    resource_guard: E1ConfirmationResourceGuardBinding,
    audit: E1ConfirmationReleasedWorkerAudit,
) -> None:
    if not isinstance(binding, E1ConfirmationCanonicalProducerBinding) or not isinstance(
        chain, E1ConfirmationChainContract
    ) or binding.chain_contract_digest != chain.digest():
        raise E1ConfirmationCanonicalWorkerError(
            "S1-EB26 binding and chain contract do not match"
        )
    if not isinstance(release, E1ConfirmationReleaseContract) or (
        release.binding_digest != binding.digest()
        or release.chain_contract_digest != chain.digest()
    ):
        raise E1ConfirmationCanonicalWorkerError(
            "S1-EB26 release contract changed"
        )
    if not isinstance(authorization, E1ConfirmationOwnerAuthorization) or (
        authorization.release_contract_digest != release.contract_digest
    ):
        raise E1ConfirmationCanonicalWorkerError(
            "S1-EB26 authorization changed"
        )
    if not isinstance(resource_guard, E1ConfirmationResourceGuardBinding) or (
        resource_guard.authorization_digest != authorization.authorization_digest
    ):
        raise E1ConfirmationCanonicalWorkerError(
            "S1-EB26 resource guard changed"
        )
    if not isinstance(audit, E1ConfirmationReleasedWorkerAudit) or (
        audit.audit_digest != S1_EB25_AUDIT_DIGEST
        or audit.binding_digest != binding.digest()
        or audit.chain_contract_digest != chain.digest()
        or audit.release_contract_digest != release.contract_digest
        or audit.authorization_digest != authorization.authorization_digest
        or audit.resource_guard_digest != resource_guard.binding_digest
        or audit.canonical_worker_implemented is not False
        or audit.canonical_execution_permitted is not False
    ):
        raise E1ConfirmationCanonicalWorkerError(
            "S1-EB26 requires the unchanged closed S1-EB25 audit"
        )
    audit.__post_init__()


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
        raise E1ConfirmationCanonicalWorkerError(
            f"S1-EB26 marker already exists: {path.name}"
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
        prefix=target.name + ".tmp.",
        dir=target.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        if temporary.read_bytes() != encoded:
            raise E1ConfirmationCanonicalWorkerError(
                "S1-EB26 temporary report reread failed"
            )
        try:
            os.link(temporary, target)
        except FileExistsError as exc:
            raise E1ConfirmationCanonicalWorkerError(
                "S1-EB26 synthetic report already exists"
            ) from exc
        if target.read_bytes() != encoded:
            raise E1ConfirmationCanonicalWorkerError(
                "S1-EB26 published report differs"
            )
        return encoded
    finally:
        temporary.unlink(missing_ok=True)


def _execute_e1_confirmation_worker_synthetically(
    binding: E1ConfirmationCanonicalProducerBinding,
    chain: E1ConfirmationChainContract,
    release: E1ConfirmationReleaseContract,
    authorization: E1ConfirmationOwnerAuthorization,
    resource_guard: E1ConfirmationResourceGuardBinding,
    audit: E1ConfirmationReleasedWorkerAudit,
    kernels: E1ConfirmationSyntheticKernelSet,
    synthetic_directory: Path,
) -> E1ConfirmationSyntheticWorkerReceipt:
    """Exercise the exact worker shape with synthetic digest-only kernels."""

    _validate_worker_inputs(
        binding, chain, release, authorization, resource_guard, audit
    )
    if not isinstance(kernels, E1ConfirmationSyntheticKernelSet):
        raise E1ConfirmationCanonicalWorkerError(
            "S1-EB26 requires one complete synthetic kernel set"
        )
    directory = Path(synthetic_directory).resolve()
    if not directory.is_dir() or directory == Path(
        chain.report_path
    ).parent.resolve():
        raise E1ConfirmationCanonicalWorkerError(
            "S1-EB26 requires a synthetic directory outside reports"
        )
    report = directory / S1_EB26_SYNTHETIC_REPORT
    attempt = directory / S1_EB26_SYNTHETIC_ATTEMPT
    lock = directory / S1_EB26_SYNTHETIC_LOCK
    if any(path.exists() for path in (report, attempt, lock)):
        raise E1ConfirmationCanonicalWorkerError(
            "S1-EB26 synthetic one-shot path is already used"
        )

    preflight = prepare_e1_confirmation_same_session_preflight(
        binding, chain, release, authorization, resource_guard
    )
    require_fresh_e1_confirmation_preflight(preflight)
    execution_id = "e1.confirmation-worker.s1eb26.synthetic.once.v1"
    _exclusive_marker(
        lock,
        {
            "execution_id": execution_id,
            "preflight_digest": preflight.preflight_digest,
            "synthetic_only": True,
        },
    )
    attempt_created = False
    try:
        _exclusive_marker(
            attempt,
            {
                "execution_id": execution_id,
                "audit_digest": audit.audit_digest,
                "preflight_digest": preflight.preflight_digest,
                "failure_policy": "retain-attempt-marker-no-automatic-retry",
                "synthetic_only": True,
            },
        )
        attempt_created = True
        previous = preflight.preflight_digest
        stage_digests = []
        for role in S1_EB26_SYNTHETIC_STAGE_ORDER:
            produced = getattr(kernels, role)(previous)
            if not _valid_digest(produced):
                raise E1ConfirmationCanonicalWorkerError(
                    f"S1-EB26 synthetic {role} returned no SHA-256"
                )
            stage_digests.append((role, produced))
            previous = produced
        report_payload = {
            "execution_id": execution_id,
            "audit_digest": audit.audit_digest,
            "preflight_digest": preflight.preflight_digest,
            "stage_digests": tuple(stage_digests),
            "synthetic_only": True,
            "canonical_execution_permitted": False,
            "claims_permitted": False,
        }
        encoded = _atomic_publish(report, report_payload)
        if hashlib.sha256(report.read_bytes()).hexdigest() != hashlib.sha256(
            encoded
        ).hexdigest():
            raise E1ConfirmationCanonicalWorkerError(
                "S1-EB26 final report verification failed"
            )
        attempt.unlink()
        values = {
            "execution_id": execution_id,
            "audit_digest": audit.audit_digest,
            "preflight_digest": preflight.preflight_digest,
            "stage_digests": tuple(stage_digests),
            "report_path": str(report),
            "report_sha256": hashlib.sha256(encoded).hexdigest(),
            "attempt_removed_after_verified_publish": True,
            "lock_released": True,
            "synthetic_only": True,
            "canonical_execution_permitted": False,
            "claims_permitted": False,
        }
        return E1ConfirmationSyntheticWorkerReceipt(
            **values,
            receipt_digest=_digest(values),
        )
    finally:
        lock.unlink(missing_ok=True)
        if not attempt_created:
            attempt.unlink(missing_ok=True)


def execute_e1_confirmation_canonical_worker_once(
    binding: E1ConfirmationCanonicalProducerBinding,
    chain: E1ConfirmationChainContract,
    release: E1ConfirmationReleaseContract,
    authorization: E1ConfirmationOwnerAuthorization,
    resource_guard: E1ConfirmationResourceGuardBinding,
    audit: E1ConfirmationReleasedWorkerAudit,
) -> None:
    """Keep canonical execution closed until a later explicit release step."""

    _validate_worker_inputs(
        binding, chain, release, authorization, resource_guard, audit
    )
    raise E1ConfirmationCanonicalWorkerError(
        "S1-EB26 canonical worker execution remains locked"
    )
