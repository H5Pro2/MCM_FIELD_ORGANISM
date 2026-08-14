"""Private S1-EC15 atomic publisher for a complete fixture handoff payload."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

from .e1_confirmation_full_formation_handoff import (
    E1FullFormationHandoffEnvelope,
    S1_EC14_CONTRACT_DIGEST,
    load_full_formation_handoff_payload,
)
from .e1_confirmation_prepared_execution_bundle import (
    _atomic_publish,
    _exclusive_marker,
)
from .e1_refined_formation_runner import _digest


class E1ConfirmationFullFormationHandoffPublisherError(RuntimeError):
    """Raised when the S1-EC15 fixture publication fails closed."""


S1_EC15_PUBLICATION_ID = "e1.full-formation-handoff.s1ec15.fixture.v1"
S1_EC15_REPORT = "e1_full_formation_handoff_s1ec15_fixture_once_v1.json"
S1_EC15_ATTEMPT = (
    "e1_full_formation_handoff_s1ec15_fixture_once_v1.attempt.json"
)
S1_EC15_LOCK = "e1_full_formation_handoff_s1ec15_fixture_once_v1.lock"
S1_EC15_FAILURE_POLICY = "retain-attempt-marker-no-automatic-retry"
S1_EC15_POLICY_DIGEST = _digest(
    {
        "publication_id": S1_EC15_PUBLICATION_ID,
        "report_name": S1_EC15_REPORT,
        "attempt_name": S1_EC15_ATTEMPT,
        "lock_name": S1_EC15_LOCK,
        "failure_policy": S1_EC15_FAILURE_POLICY,
        "handoff_contract_digest": S1_EC14_CONTRACT_DIGEST,
        "fixture_payload_only": True,
        "runtime_execution_permitted": False,
        "canonical_execution_permitted": False,
        "probe_execution_permitted": False,
        "claims_permitted": False,
    }
)


def _valid_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


@dataclass(frozen=True, slots=True)
class E1FullFormationHandoffPublicationContract:
    publication_id: str
    report_path: str
    attempt_path: str
    lock_path: str
    failure_policy: str
    fixture_payload_only: bool
    runtime_execution_permitted: bool
    canonical_execution_permitted: bool
    probe_execution_permitted: bool
    claims_permitted: bool

    def __post_init__(self) -> None:
        paths = tuple(
            Path(value)
            for value in (self.report_path, self.attempt_path, self.lock_path)
        )
        if (
            self.publication_id != S1_EC15_PUBLICATION_ID
            or len(set(paths)) != 3
            or len({path.parent for path in paths}) != 1
            or tuple(path.name for path in paths)
            != (S1_EC15_REPORT, S1_EC15_ATTEMPT, S1_EC15_LOCK)
            or any(path.exists() for path in paths)
            or self.failure_policy != S1_EC15_FAILURE_POLICY
            or self.fixture_payload_only is not True
            or self.runtime_execution_permitted is not False
            or self.canonical_execution_permitted is not False
            or self.probe_execution_permitted is not False
            or self.claims_permitted is not False
        ):
            raise E1ConfirmationFullFormationHandoffPublisherError(
                "S1-EC15 publication contract changed or paths are used"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


def prepare_full_formation_handoff_fixture_publication(
    directory: Path,
) -> E1FullFormationHandoffPublicationContract:
    """Bind unused fixture-only paths without creating any marker."""

    root = Path(directory).resolve()
    if not root.is_dir() or root == Path("reports").resolve():
        raise E1ConfirmationFullFormationHandoffPublisherError(
            "S1-EC15 requires an existing synthetic directory outside reports"
        )
    return E1FullFormationHandoffPublicationContract(
        publication_id=S1_EC15_PUBLICATION_ID,
        report_path=str(root / S1_EC15_REPORT),
        attempt_path=str(root / S1_EC15_ATTEMPT),
        lock_path=str(root / S1_EC15_LOCK),
        failure_policy=S1_EC15_FAILURE_POLICY,
        fixture_payload_only=True,
        runtime_execution_permitted=False,
        canonical_execution_permitted=False,
        probe_execution_permitted=False,
        claims_permitted=False,
    )


@dataclass(frozen=True, slots=True)
class E1FullFormationHandoffPublicationReceipt:
    publication_id: str
    publisher_policy_digest: str
    publication_contract_digest: str
    handoff_contract_digest: str
    payload_digest: str
    formation_result_digest: str
    report_path: str
    report_sha256: str
    final_reread_verified: bool
    typed_reload_verified: bool
    attempt_removed_after_verification: bool
    lock_released: bool
    fixture_payload_only: bool
    canonical_execution_permitted: bool
    probe_execution_permitted: bool
    claims_permitted: bool

    def __post_init__(self) -> None:
        if (
            self.publication_id != S1_EC15_PUBLICATION_ID
            or self.publisher_policy_digest != S1_EC15_POLICY_DIGEST
            or any(
                not _valid_digest(value)
                for value in (
                    self.publication_contract_digest,
                    self.handoff_contract_digest,
                    self.payload_digest,
                    self.formation_result_digest,
                    self.report_sha256,
                )
            )
            or Path(self.report_path).name != S1_EC15_REPORT
            or self.final_reread_verified is not True
            or self.typed_reload_verified is not True
            or self.attempt_removed_after_verification is not True
            or self.lock_released is not True
            or self.fixture_payload_only is not True
            or self.canonical_execution_permitted is not False
            or self.probe_execution_permitted is not False
            or self.claims_permitted is not False
        ):
            raise E1ConfirmationFullFormationHandoffPublisherError(
                "S1-EC15 publication receipt changed"
            )


def publish_full_formation_handoff_fixture_once(
    contract: E1FullFormationHandoffPublicationContract,
    envelope: E1FullFormationHandoffEnvelope,
) -> E1FullFormationHandoffPublicationReceipt:
    """Atomically publish and reload one already prepared fixture payload."""

    if not isinstance(contract, E1FullFormationHandoffPublicationContract):
        raise E1ConfirmationFullFormationHandoffPublisherError(
            "S1-EC15 requires one publication contract"
        )
    if not isinstance(envelope, E1FullFormationHandoffEnvelope):
        raise E1ConfirmationFullFormationHandoffPublisherError(
            "S1-EC15 requires one complete prepared handoff envelope"
        )
    contract.__post_init__()
    envelope.__post_init__()
    publication_contract_digest = contract.digest()
    report = Path(contract.report_path)
    attempt = Path(contract.attempt_path)
    lock = Path(contract.lock_path)
    _exclusive_marker(
        lock,
        {
            "publication_id": contract.publication_id,
            "publisher_policy_digest": S1_EC15_POLICY_DIGEST,
            "publication_contract_digest": publication_contract_digest,
            "payload_digest": envelope.payload_digest,
            "fixture_payload_only": True,
        },
    )
    attempt_created = False
    try:
        _exclusive_marker(
            attempt,
            {
                "publication_id": contract.publication_id,
                "publication_contract_digest": publication_contract_digest,
                "payload_digest": envelope.payload_digest,
                "failure_policy": S1_EC15_FAILURE_POLICY,
                "fixture_payload_only": True,
            },
        )
        attempt_created = True
        report_payload = {
            "publication_id": contract.publication_id,
            "publisher_policy_digest": S1_EC15_POLICY_DIGEST,
            "publication_contract_digest": publication_contract_digest,
            "handoff_contract_digest": envelope.contract_digest,
            "payload_digest": envelope.payload_digest,
            "payload": envelope.payload,
            "fixture_payload_only": True,
            "canonical_execution_permitted": False,
            "probe_execution_permitted": False,
            "claims_permitted": False,
        }
        report_payload_digest = _digest(report_payload)
        encoded = _atomic_publish(report, report_payload)
        report_sha256 = hashlib.sha256(encoded).hexdigest()
        reread = report.read_bytes()
        if hashlib.sha256(reread).hexdigest() != report_sha256:
            raise E1ConfirmationFullFormationHandoffPublisherError(
                "S1-EC15 final report reread failed"
            )
        try:
            decoded = json.loads(reread.decode("ascii"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise E1ConfirmationFullFormationHandoffPublisherError(
                "S1-EC15 final report is not canonical JSON"
            ) from exc
        if (
            _digest(decoded) != report_payload_digest
            or _digest(decoded["payload"]) != envelope.payload_digest
        ):
            raise E1ConfirmationFullFormationHandoffPublisherError(
                "S1-EC15 final payload digest verification failed"
            )
        loaded = load_full_formation_handoff_payload(decoded["payload"])
        formation_result_digest = decoded["payload"]["result"]["result_digest"]
        if loaded.result_digest != formation_result_digest:
            raise E1ConfirmationFullFormationHandoffPublisherError(
                "S1-EC15 typed reload changed the formation result"
            )
        attempt.unlink()
        return E1FullFormationHandoffPublicationReceipt(
            publication_id=contract.publication_id,
            publisher_policy_digest=S1_EC15_POLICY_DIGEST,
            publication_contract_digest=publication_contract_digest,
            handoff_contract_digest=envelope.contract_digest,
            payload_digest=envelope.payload_digest,
            formation_result_digest=formation_result_digest,
            report_path=str(report),
            report_sha256=report_sha256,
            final_reread_verified=True,
            typed_reload_verified=True,
            attempt_removed_after_verification=True,
            lock_released=True,
            fixture_payload_only=True,
            canonical_execution_permitted=False,
            probe_execution_permitted=False,
            claims_permitted=False,
        )
    finally:
        lock.unlink(missing_ok=True)
        if not attempt_created:
            attempt.unlink(missing_ok=True)
