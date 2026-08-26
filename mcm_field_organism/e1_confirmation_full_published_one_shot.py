"""Private S1-EC19 exactly-once full formation and state publication."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import time

from .e1_confirmation_full_formation_handoff import (
    S1_EC14_EDGE_BINDING_COUNT,
    S1_EC14_STATE_COUNT,
    build_full_formation_handoff_envelope,
    load_full_formation_handoff_payload,
)
from .e1_confirmation_full_formation_lifecycle import (
    consume_prepared_full_formation,
)
from .e1_confirmation_full_formation_resource_preflight import (
    preflight_prepared_full_formation_resources,
)
from .e1_confirmation_full_published_release_audit import (
    E1FullPublishedReleaseDecision,
    E1FullPublishedResourceSnapshot,
    S1_EC18_ATTEMPT_NAME,
    S1_EC18_LOCK_NAME,
    S1_EC18_MAX_REPORT_BYTES,
    S1_EC18_MAX_RUNTIME_SECONDS,
    S1_EC18_REPORT_NAME,
    S1_EC18_RELEASE_TARGET_ID,
)
from .e1_confirmation_prepared_execution_bundle import (
    E1PreparedExecutionBundle,
    _atomic_publish,
    _exclusive_marker,
)
from .e1_refined_formation_runner import _digest


class E1ConfirmationFullPublishedOneShotError(RuntimeError):
    """Raised when the S1-EC19 full published lifecycle fails closed."""


S1_EC19_SCHEMA_ID = "e1.full-formation-published.s1ec19.once.v1"
S1_EC19_FAILURE_POLICY = "retain-attempt-marker-no-automatic-retry"
S1_EC19_FORMATION_SCOPE = "full-r2-r4-r8-five-arm-formation"


def _valid_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


@dataclass(frozen=True, slots=True)
class E1FullPublishedOneShotReceipt:
    execution_id: str
    release_policy_digest: str
    release_decision_digest: str
    resource_snapshot_digest: str
    resource_preflight_digest: str
    handoff_payload_digest: str
    formation_result_digest: str
    report_path: str
    report_sha256: str
    report_bytes: int
    runtime_seconds: float
    state_count: int
    edge_binding_count: int
    final_reread_verified: bool
    typed_reload_verified: bool
    attempt_removed_after_verification: bool
    lock_released: bool
    full_formation_executed: bool
    canonical_execution_permitted: bool
    probe_execution_permitted: bool
    claims_permitted: bool

    def __post_init__(self) -> None:
        if (
            self.execution_id != S1_EC18_RELEASE_TARGET_ID
            or any(
                not _valid_digest(value)
                for value in (
                    self.release_policy_digest,
                    self.release_decision_digest,
                    self.resource_snapshot_digest,
                    self.resource_preflight_digest,
                    self.handoff_payload_digest,
                    self.formation_result_digest,
                    self.report_sha256,
                )
            )
            or Path(self.report_path).name != S1_EC18_REPORT_NAME
            or not 0 < self.report_bytes <= S1_EC18_MAX_REPORT_BYTES
            or not 0.0 <= self.runtime_seconds <= S1_EC18_MAX_RUNTIME_SECONDS
            or self.state_count != S1_EC14_STATE_COUNT
            or self.edge_binding_count != S1_EC14_EDGE_BINDING_COUNT
            or self.final_reread_verified is not True
            or self.typed_reload_verified is not True
            or self.attempt_removed_after_verification is not True
            or self.lock_released is not True
            or self.full_formation_executed is not True
            or self.canonical_execution_permitted is not False
            or self.probe_execution_permitted is not False
            or self.claims_permitted is not False
        ):
            raise E1ConfirmationFullPublishedOneShotError(
                "S1-EC19 receipt changed"
            )


def _canonical_report_bytes(payload: dict[str, object]) -> bytes:
    return (
        json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=False,
        )
        + "\n"
    ).encode("ascii")


def execute_full_published_formation_once(
    release: E1FullPublishedReleaseDecision,
    snapshot: E1FullPublishedResourceSnapshot,
    bundle: E1PreparedExecutionBundle,
    directory: Path,
    *,
    owner_authorized: bool,
) -> E1FullPublishedOneShotReceipt:
    """Execute and publish one complete formation under the S1-EC18 gate."""

    if not isinstance(release, E1FullPublishedReleaseDecision):
        raise E1ConfirmationFullPublishedOneShotError(
            "S1-EC19 requires one typed S1-EC18 decision"
        )
    if not isinstance(snapshot, E1FullPublishedResourceSnapshot):
        raise E1ConfirmationFullPublishedOneShotError(
            "S1-EC19 requires the released resource snapshot"
        )
    if not isinstance(bundle, E1PreparedExecutionBundle):
        raise E1ConfirmationFullPublishedOneShotError(
            "S1-EC19 requires one prepared input bundle"
        )
    release.__post_init__()
    snapshot.__post_init__()
    bundle.__post_init__()
    if release.decision != "FREIGABE" or owner_authorized is not True:
        raise E1ConfirmationFullPublishedOneShotError(
            "S1-EC19 is not authorized"
        )

    root = Path(directory).resolve()
    report = root / S1_EC18_REPORT_NAME
    attempt = root / S1_EC18_ATTEMPT_NAME
    lock = root / S1_EC18_LOCK_NAME
    if (
        root != Path(snapshot.proposed_directory).resolve()
        or snapshot.digest() != release.resource_snapshot_digest
        or root == Path("reports").resolve()
        or any(
        path.exists() for path in (report, attempt, lock)
        )
    ):
        raise E1ConfirmationFullPublishedOneShotError(
            "S1-EC19 target paths are not fresh"
        )
    root.mkdir(parents=False, exist_ok=True)
    bundle.require_inputs_unchanged()
    preflight = preflight_prepared_full_formation_resources(bundle)
    if (
        preflight.result_digest != release.resource_preflight_digest
        or release.release_target_id != S1_EC18_RELEASE_TARGET_ID
    ):
        raise E1ConfirmationFullPublishedOneShotError(
            "S1-EC19 release and prepared resources do not align"
        )

    started = time.monotonic()

    def runtime_guard() -> None:
        if time.monotonic() - started > S1_EC18_MAX_RUNTIME_SECONDS:
            raise E1ConfirmationFullPublishedOneShotError(
                "S1-EC19 runtime cap exceeded"
            )

    _exclusive_marker(
        lock,
        {
            "execution_id": S1_EC18_RELEASE_TARGET_ID,
            "release_decision_digest": release.decision_digest,
        },
    )
    attempt_created = False
    try:
        _exclusive_marker(
            attempt,
            {
                "execution_id": S1_EC18_RELEASE_TARGET_ID,
                "release_decision_digest": release.decision_digest,
                "failure_policy": S1_EC19_FAILURE_POLICY,
            },
        )
        attempt_created = True
        in_attempt_preflight = preflight_prepared_full_formation_resources(bundle)
        if in_attempt_preflight.result_digest != preflight.result_digest:
            raise E1ConfirmationFullPublishedOneShotError(
                "S1-EC19 preflight changed across Attempt"
            )
        formation = consume_prepared_full_formation(
            bundle,
            preflight,
            attempt_path=attempt,
            runtime_guard=runtime_guard,
        )
        runtime_guard()
        envelope = build_full_formation_handoff_envelope(formation)
        payload = {
            "schema_id": S1_EC19_SCHEMA_ID,
            "execution_id": S1_EC18_RELEASE_TARGET_ID,
            "release_policy_digest": release.policy_digest,
            "release_decision_digest": release.decision_digest,
            "resource_snapshot_digest": release.resource_snapshot_digest,
            "resource_snapshot": asdict(snapshot),
            "resource_preflight_digest": preflight.result_digest,
            "input_bundle_digest": bundle.bundle_digest,
            "formation_scope": S1_EC19_FORMATION_SCOPE,
            "handoff_contract_digest": envelope.contract_digest,
            "handoff_payload_digest": envelope.payload_digest,
            "formation_result_digest": formation.result_digest,
            "payload": envelope.payload,
            "runtime_seconds": time.monotonic() - started,
            "state_count": envelope.state_count,
            "edge_binding_count": envelope.edge_binding_count,
            "full_formation_executed": True,
            "owner_authorized": True,
            "canonical_execution_permitted": False,
            "probe_execution_permitted": False,
            "claims_permitted": False,
        }
        encoded_before_publish = _canonical_report_bytes(payload)
        if len(encoded_before_publish) > S1_EC18_MAX_REPORT_BYTES:
            raise E1ConfirmationFullPublishedOneShotError(
                "S1-EC19 report size cap exceeded"
            )
        encoded = _atomic_publish(report, payload)
        if encoded != encoded_before_publish:
            raise E1ConfirmationFullPublishedOneShotError(
                "S1-EC19 publication encoding changed"
            )
        report_sha256 = hashlib.sha256(encoded).hexdigest()
        reread = report.read_bytes()
        if hashlib.sha256(reread).hexdigest() != report_sha256:
            raise E1ConfirmationFullPublishedOneShotError(
                "S1-EC19 final reread failed"
            )
        try:
            decoded = json.loads(reread.decode("ascii"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise E1ConfirmationFullPublishedOneShotError(
                "S1-EC19 final report is not canonical JSON"
            ) from exc
        if (
            _digest(decoded["payload"]) != envelope.payload_digest
            or decoded["formation_result_digest"] != formation.result_digest
        ):
            raise E1ConfirmationFullPublishedOneShotError(
                "S1-EC19 final payload changed"
            )
        loaded = load_full_formation_handoff_payload(decoded["payload"])
        if loaded.result_digest != formation.result_digest:
            raise E1ConfirmationFullPublishedOneShotError(
                "S1-EC19 typed reload changed the formation"
            )
        bundle.require_inputs_unchanged()
        runtime_seconds = time.monotonic() - started
        runtime_guard()
        attempt.unlink()
        return E1FullPublishedOneShotReceipt(
            execution_id=S1_EC18_RELEASE_TARGET_ID,
            release_policy_digest=release.policy_digest,
            release_decision_digest=release.decision_digest,
            resource_snapshot_digest=release.resource_snapshot_digest,
            resource_preflight_digest=preflight.result_digest,
            handoff_payload_digest=envelope.payload_digest,
            formation_result_digest=formation.result_digest,
            report_path=str(report),
            report_sha256=report_sha256,
            report_bytes=len(encoded),
            runtime_seconds=runtime_seconds,
            state_count=envelope.state_count,
            edge_binding_count=envelope.edge_binding_count,
            final_reread_verified=True,
            typed_reload_verified=True,
            attempt_removed_after_verification=True,
            lock_released=True,
            full_formation_executed=True,
            canonical_execution_permitted=False,
            probe_execution_permitted=False,
            claims_permitted=False,
        )
    finally:
        lock.unlink(missing_ok=True)
        if not attempt_created:
            attempt.unlink(missing_ok=True)
