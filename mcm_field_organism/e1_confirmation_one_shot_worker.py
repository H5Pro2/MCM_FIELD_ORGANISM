"""Private S1-EB24 guarded one-shot worker; canonical work stays locked."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import sys
import time

from .e1_confirmation_canonical_producer_binding import (
    prepare_e1_confirmation_canonical_producer_binding,
)
from .e1_confirmation_chain_contract import (
    prepare_e1_confirmation_chain_contract,
)
from .e1_confirmation_owner_authorization import (
    E1ConfirmationOwnerAuthorization,
    bind_e1_confirmation_owner_authorization,
)
from .e1_confirmation_release_audit import (
    audit_e1_confirmation_release_readiness,
)
from .e1_confirmation_release_contract import (
    prepare_e1_confirmation_release_contract,
)
from .e1_confirmation_resource_guard import (
    E1ConfirmationResourceGuardBinding,
    run_guarded_synthetic_process,
)
from .e1_confirmation_same_session_preflight import (
    S1_EB23_MAX_AGE_NS,
    prepare_e1_confirmation_same_session_preflight,
    require_fresh_e1_confirmation_preflight,
)
from .e1_refined_formation_runner import _digest


class E1ConfirmationOneShotWorkerError(RuntimeError):
    """Raised when the S1-EB24 synthetic worker cannot fail closed."""


S1_EB22_RESOURCE_GUARD_DIGEST = (
    "03718c6111e130caebbbc9feadfa0dbe728d8c9234ad87f4133befc6b5b6cffe"
)
S1_EB24_MARKER_NAME = "e1_confirmation_s1eb24_synthetic_once_v1.lock"


def _valid_digest(value: str) -> bool:
    return len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


@dataclass(frozen=True, slots=True)
class E1ConfirmationOneShotWorkerReceipt:
    worker_id: str
    process_id: int
    preflight_digest: str
    preflight_age_at_marker_ns: int
    resource_guard_digest: str
    marker_path: str
    marker_sha256: str
    work_invocation_count: int
    synthetic_only: bool
    canonical_targets_touched: bool
    canonical_execution_permitted: bool
    claims_permitted: bool
    worker_status: str
    receipt_digest: str

    def __post_init__(self) -> None:
        if (
            self.worker_id != "e1.confirmation-worker.s1eb24.synthetic.once.v1"
            or self.process_id <= 0
            or not _valid_digest(self.preflight_digest)
            or self.preflight_age_at_marker_ns < 0
            or self.preflight_age_at_marker_ns > S1_EB23_MAX_AGE_NS
            or self.resource_guard_digest != S1_EB22_RESOURCE_GUARD_DIGEST
            or Path(self.marker_path).name != S1_EB24_MARKER_NAME
            or not _valid_digest(self.marker_sha256)
            or self.work_invocation_count != 1
            or self.synthetic_only is not True
            or self.canonical_targets_touched is not False
            or self.canonical_execution_permitted is not False
            or self.claims_permitted is not False
            or self.worker_status != "SYNTHETIC_COORDINATION_COMPLETE"
        ):
            raise E1ConfirmationOneShotWorkerError(
                "S1-EB24 worker receipt changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "receipt_digest"
        }
        if self.receipt_digest != _digest(payload):
            raise E1ConfirmationOneShotWorkerError(
                "S1-EB24 receipt digest does not match its payload"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


def _workspace_root() -> Path:
    return Path(__file__).parents[1]


def _restore_bound_resource_guard(
    authorization: E1ConfirmationOwnerAuthorization,
) -> E1ConfirmationResourceGuardBinding:
    values = {
        "binding_id": "e1.confirmation-resource-guard.s1eb22.v1",
        "authorization_digest": authorization.authorization_digest,
        "platform": "win32",
        "backend": "windows-job-object",
        "max_wall_seconds": 1_800,
        "max_peak_rss_bytes": 4 * 1024**3,
        "process_tree_kill_bound": True,
        "wall_limit_bound": True,
        "memory_limit_bound": True,
        "synthetic_success_verified": True,
        "synthetic_wall_limit_verified": True,
        "synthetic_memory_limit_verified": True,
        "canonical_execution_permitted": False,
    }
    guard = E1ConfirmationResourceGuardBinding(
        **values,
        binding_digest=_digest(values),
    )
    if guard.binding_digest != S1_EB22_RESOURCE_GUARD_DIGEST:
        raise E1ConfirmationOneShotWorkerError(
            "S1-EB24 restored resource guard changed"
        )
    return guard


def _prepare_worker_inputs():
    root = _workspace_root()
    reports = root / "reports"
    upstream = reports / "e1_refined_formation_transfer_s1ea_once_v1.json"
    binding = prepare_e1_confirmation_canonical_producer_binding(
        reports, upstream
    )
    chain = prepare_e1_confirmation_chain_contract(reports, upstream)
    audit = audit_e1_confirmation_release_readiness(binding, chain)
    release = prepare_e1_confirmation_release_contract(binding, chain, audit)
    authorization = bind_e1_confirmation_owner_authorization(release)
    guard = _restore_bound_resource_guard(authorization)
    return binding, chain, release, authorization, guard


def _exclusive_synthetic_marker(path: Path, payload: dict[str, object]) -> bytes:
    encoded = (
        json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    ).encode("ascii")
    try:
        with path.open("xb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise E1ConfirmationOneShotWorkerError(
            "S1-EB24 synthetic one-shot marker already exists"
        ) from exc
    return encoded


def _run_synthetic_worker_in_child(
    synthetic_directory: Path,
) -> E1ConfirmationOneShotWorkerReceipt:
    directory = Path(synthetic_directory).resolve()
    registered = (_workspace_root() / "reports").resolve()
    if not directory.is_dir() or directory == registered:
        raise E1ConfirmationOneShotWorkerError(
            "S1-EB24 requires a synthetic directory outside reports"
        )
    marker = directory / S1_EB24_MARKER_NAME
    if marker.exists():
        raise E1ConfirmationOneShotWorkerError(
            "S1-EB24 synthetic one-shot marker already exists"
        )

    binding, chain, release, authorization, guard = _prepare_worker_inputs()
    preflight = prepare_e1_confirmation_same_session_preflight(
        binding, chain, release, authorization, guard
    )
    require_fresh_e1_confirmation_preflight(preflight)
    marker_time_ns = time.monotonic_ns()
    age_ns = marker_time_ns - preflight.issued_monotonic_ns
    if age_ns < 0 or age_ns > preflight.max_age_ns:
        raise E1ConfirmationOneShotWorkerError(
            "S1-EB24 preflight expired before the first marker"
        )
    marker_payload = {
        "worker_id": "e1.confirmation-worker.s1eb24.synthetic.once.v1",
        "process_id": os.getpid(),
        "preflight_digest": preflight.preflight_digest,
        "marker_monotonic_ns": marker_time_ns,
        "synthetic_only": True,
        "canonical_execution_permitted": False,
    }
    encoded = _exclusive_synthetic_marker(marker, marker_payload)
    values = {
        "worker_id": "e1.confirmation-worker.s1eb24.synthetic.once.v1",
        "process_id": os.getpid(),
        "preflight_digest": preflight.preflight_digest,
        "preflight_age_at_marker_ns": age_ns,
        "resource_guard_digest": guard.binding_digest,
        "marker_path": str(marker),
        "marker_sha256": hashlib.sha256(encoded).hexdigest(),
        "work_invocation_count": 1,
        "synthetic_only": True,
        "canonical_targets_touched": False,
        "canonical_execution_permitted": False,
        "claims_permitted": False,
        "worker_status": "SYNTHETIC_COORDINATION_COMPLETE",
    }
    return E1ConfirmationOneShotWorkerReceipt(
        **values,
        receipt_digest=_digest(values),
    )


def run_guarded_synthetic_e1_confirmation_worker(
    resource_guard: E1ConfirmationResourceGuardBinding,
    synthetic_directory: Path,
) -> E1ConfirmationOneShotWorkerReceipt:
    """Run only the synthetic S1-EB24 worker under the bound Job Object."""

    if not isinstance(resource_guard, E1ConfirmationResourceGuardBinding) or (
        resource_guard.binding_digest != S1_EB22_RESOURCE_GUARD_DIGEST
        or resource_guard.canonical_execution_permitted is not False
    ):
        raise E1ConfirmationOneShotWorkerError(
            "S1-EB24 requires the unchanged closed S1-EB22 guard"
        )
    directory = Path(synthetic_directory).resolve()
    if not directory.is_dir() or directory == (
        _workspace_root() / "reports"
    ).resolve():
        raise E1ConfirmationOneShotWorkerError(
            "S1-EB24 requires a synthetic directory outside reports"
        )
    outcome = run_guarded_synthetic_process(
        (
            sys.executable,
            "-m",
            "mcm_field_organism.e1_confirmation_one_shot_worker",
            "--synthetic-directory",
            str(directory),
        ),
        _workspace_root(),
        max_wall_seconds=resource_guard.max_wall_seconds,
        max_peak_rss_bytes=resource_guard.max_peak_rss_bytes,
    )
    if outcome.status != "COMPLETED" or outcome.return_code != 0:
        detail = outcome.stderr.strip() or outcome.status
        raise E1ConfirmationOneShotWorkerError(
            f"S1-EB24 guarded synthetic worker failed: {detail}"
        )
    try:
        payload = json.loads(outcome.stdout.strip().splitlines()[-1])
        receipt = E1ConfirmationOneShotWorkerReceipt(**payload)
    except (IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise E1ConfirmationOneShotWorkerError(
            "S1-EB24 worker returned no valid receipt"
        ) from exc
    if receipt.resource_guard_digest != resource_guard.binding_digest:
        raise E1ConfirmationOneShotWorkerError(
            "S1-EB24 worker used another resource guard"
        )
    marker = Path(receipt.marker_path)
    expected_marker = directory / S1_EB24_MARKER_NAME
    if (
        marker.resolve() != expected_marker
        or not marker.is_file()
        or hashlib.sha256(marker.read_bytes()).hexdigest()
        != receipt.marker_sha256
    ):
        raise E1ConfirmationOneShotWorkerError(
            "S1-EB24 synthetic marker cannot be verified"
        )
    try:
        marker_payload = json.loads(marker.read_text(encoding="ascii"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise E1ConfirmationOneShotWorkerError(
            "S1-EB24 synthetic marker cannot be decoded"
        ) from exc
    if (
        marker_payload.get("worker_id") != receipt.worker_id
        or marker_payload.get("process_id") != receipt.process_id
        or marker_payload.get("preflight_digest") != receipt.preflight_digest
        or marker_payload.get("synthetic_only") is not True
        or marker_payload.get("canonical_execution_permitted") is not False
    ):
        raise E1ConfirmationOneShotWorkerError(
            "S1-EB24 synthetic marker does not match its receipt"
        )
    return receipt


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--synthetic-directory", required=True)
    args = parser.parse_args(argv)
    receipt = _run_synthetic_worker_in_child(Path(args.synthetic_directory))
    print(
        json.dumps(
            asdict(receipt),
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
