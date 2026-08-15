"""Private S1-EB25 static released-worker audit; no execution is opened."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
from pathlib import Path

from .e1_confirmation_canonical_producer_binding import (
    E1ConfirmationCanonicalProducerBinding,
)
from .e1_confirmation_chain_contract import E1ConfirmationChainContract
from .e1_confirmation_owner_authorization import (
    E1ConfirmationOwnerAuthorization,
)
from .e1_confirmation_release_audit import (
    S1_EB17_IMPLEMENTATION_DIGESTS,
    current_s1_eb17_implementation_digests,
)
from .e1_confirmation_release_contract import E1ConfirmationReleaseContract
from .e1_confirmation_resource_guard import (
    E1ConfirmationResourceGuardBinding,
)
from .e1_refined_formation_runner import _digest


class E1ConfirmationReleasedWorkerAuditError(ValueError):
    """Raised when an S1-EB25 release-chain invariant changed."""


S1_EA6_SHA256 = (
    "adf8b2b6c1b9fdda48062dbb1cd9149fcde462a3dc77a348aa2dfb0cb1fcaa47"
)
S1_EB22_RESOURCE_GUARD_DIGEST = (
    "03718c6111e130caebbbc9feadfa0dbe728d8c9234ad87f4133befc6b5b6cffe"
)
S1_EB25_RELEASE_FILES = (
    ("s1eb19_release_contract", "e1_confirmation_release_contract.py"),
    ("s1eb21_owner_authorization", "e1_confirmation_owner_authorization.py"),
    ("s1eb22_resource_guard", "e1_confirmation_resource_guard.py"),
    ("s1eb23_same_session_preflight", "e1_confirmation_same_session_preflight.py"),
    ("s1eb24_one_shot_worker", "e1_confirmation_one_shot_worker.py"),
)
S1_EB25_RELEASE_DIGESTS = (
    ("s1eb19_release_contract", "07f57b93bd559876941d77f96a9556b5389804ce59baa2117501a0247b9c7015"),
    ("s1eb21_owner_authorization", "32512caf4df83e0af61f421c88a594aff454a60369c6efcf0617b2be9e642a09"),
    ("s1eb22_resource_guard", "df01fef096fb463c5297b3b99b98b9e5b4d8602343c6108f1b7833b7f94a12e4"),
    ("s1eb23_same_session_preflight", "485516db6a213740da34da5d6185ae7d103ccd5a35e5754e95b68374ae8cd020"),
    ("s1eb24_one_shot_worker", "bd287e55649eb3d0e8a7182416112d939c65e2d953bb183a94068d803765bab3"),
)
S1_EB25_DECISION_RECEIPTS = (
    (
        "static_contract_check",
        "docs/S1EB20_STATISCHE_RELEASEVERTRAGSPRUEFUNG.md",
        "e3b8dafbb1078c43fbc7e700cac730a3668337f7d99654f175702d3670ef5804",
    ),
    (
        "owner_authorization",
        "docs/S1EB21_PROJEKTEIGNER_EINMALLAUF_AUTORISIERUNG.md",
        "f23f7a0088c00ab3241949865d6d74ad6cdfee605c893461ffd6e6da23465956",
    ),
)
S1_EB25_CANONICAL_WORKER_ORDER = (
    "prepare_e1_confirmation_same_session_preflight",
    "require_fresh_e1_confirmation_preflight",
    "create_exclusive_lock_marker",
    "create_exclusive_attempt_marker",
    "produce_e1_confirmation_canonical_formation",
    "prepare_e1_confirmation_canonical_probe_handoff",
    "run_e1_confirmation_canonical_seven_arm_probe_r2_r4_r8",
    "prepare_e1_confirmation_canonical_result_handoff",
    "compose_e1_confirmation_canonical_result",
    "prepare_e1_confirmation_canonical_report_handoff",
    "atomically_publish_and_verify_canonical_report",
    "remove_attempt_only_after_verified_publish",
    "release_lock",
)


def _normalized_source_digest(name: str) -> str:
    path = Path(__file__).with_name(name)
    if not path.is_file():
        raise E1ConfirmationReleasedWorkerAuditError(
            f"S1-EB25 implementation is missing: {name}"
        )
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def current_s1_eb25_release_digests() -> tuple[tuple[str, str], ...]:
    return tuple(
        (role, _normalized_source_digest(name))
        for role, name in S1_EB25_RELEASE_FILES
    )


def current_s1_eb25_decision_receipts() -> tuple[tuple[str, str, str], ...]:
    root = Path(__file__).parents[1]
    result = []
    for role, relative, _ in S1_EB25_DECISION_RECEIPTS:
        path = root / relative
        if not path.is_file():
            raise E1ConfirmationReleasedWorkerAuditError(
                f"S1-EB25 decision receipt is missing: {relative}"
            )
        result.append((role, relative, hashlib.sha256(path.read_bytes()).hexdigest()))
    return tuple(result)


@dataclass(frozen=True, slots=True)
class E1ConfirmationReleasedWorkerAudit:
    audit_id: str
    binding_digest: str
    chain_contract_digest: str
    release_contract_digest: str
    authorization_digest: str
    resource_guard_digest: str
    canonical_implementation_digests: tuple[tuple[str, str], ...]
    release_implementation_digests: tuple[tuple[str, str], ...]
    decision_receipts: tuple[tuple[str, str, str], ...]
    s1_ea6_sha256: str
    target_paths: tuple[str, ...]
    target_paths_free: bool
    canonical_worker_order: tuple[str, ...]
    total_field_steps: int
    max_wall_seconds: int
    max_peak_rss_bytes: int
    static_contract_check_complete: bool
    owner_one_shot_authorized: bool
    resource_enforcement_bound: bool
    same_session_preflight_proven_synthetically: bool
    guarded_worker_proven_synthetically: bool
    canonical_worker_contract_bound: bool
    canonical_worker_implemented: bool
    canonical_execution_permitted: bool
    canonical_persistence_permitted: bool
    retry_permitted: bool
    claims_permitted: bool
    audit_status: str
    audit_digest: str

    def __post_init__(self) -> None:
        if (
            self.audit_id != "e1.confirmation-released-worker-audit.s1eb25.v1"
            or self.canonical_implementation_digests
            != S1_EB17_IMPLEMENTATION_DIGESTS
            or self.canonical_implementation_digests
            != current_s1_eb17_implementation_digests()
            or self.release_implementation_digests != S1_EB25_RELEASE_DIGESTS
            or self.release_implementation_digests
            != current_s1_eb25_release_digests()
            or self.decision_receipts != S1_EB25_DECISION_RECEIPTS
            or self.decision_receipts != current_s1_eb25_decision_receipts()
            or self.s1_ea6_sha256 != S1_EA6_SHA256
            or self.canonical_worker_order != S1_EB25_CANONICAL_WORKER_ORDER
            or self.total_field_steps != 23_800
            or self.max_wall_seconds != 1_800
            or self.max_peak_rss_bytes != 4 * 1024**3
        ):
            raise E1ConfirmationReleasedWorkerAuditError(
                "S1-EB25 bound release inventory changed"
            )
        targets = tuple(Path(value) for value in self.target_paths)
        if (
            len(targets) != 3
            or len(set(targets)) != 3
            or len({item.parent for item in targets}) != 1
            or self.target_paths_free is not True
            or any(item.exists() for item in targets)
        ):
            raise E1ConfirmationReleasedWorkerAuditError(
                "S1-EB25 canonical targets are not distinct and free"
            )
        if (
            self.static_contract_check_complete is not True
            or self.owner_one_shot_authorized is not True
            or self.resource_enforcement_bound is not True
            or self.same_session_preflight_proven_synthetically is not True
            or self.guarded_worker_proven_synthetically is not True
            or self.canonical_worker_contract_bound is not True
            or self.canonical_worker_implemented is not False
            or self.canonical_execution_permitted is not False
            or self.canonical_persistence_permitted is not False
            or self.retry_permitted is not False
            or self.claims_permitted is not False
            or self.audit_status
            != "RELEASE_CHAIN_BOUND_CANONICAL_WORKER_NOT_IMPLEMENTED"
        ):
            raise E1ConfirmationReleasedWorkerAuditError(
                "S1-EB25 cannot implement or execute the canonical worker"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "audit_digest"
        }
        if self.audit_digest != _digest(payload):
            raise E1ConfirmationReleasedWorkerAuditError(
                "S1-EB25 audit digest does not match its payload"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


def audit_e1_confirmation_released_worker_contract(
    binding: E1ConfirmationCanonicalProducerBinding,
    chain: E1ConfirmationChainContract,
    release: E1ConfirmationReleaseContract,
    authorization: E1ConfirmationOwnerAuthorization,
    resource_guard: E1ConfirmationResourceGuardBinding,
) -> E1ConfirmationReleasedWorkerAudit:
    """Bind the released worker order without running or writing anything."""

    if not isinstance(binding, E1ConfirmationCanonicalProducerBinding) or not isinstance(
        chain, E1ConfirmationChainContract
    ) or binding.chain_contract_digest != chain.digest():
        raise E1ConfirmationReleasedWorkerAuditError(
            "S1-EB25 binding and chain contract do not match"
        )
    if not isinstance(release, E1ConfirmationReleaseContract) or (
        release.binding_digest != binding.digest()
        or release.chain_contract_digest != chain.digest()
    ):
        raise E1ConfirmationReleasedWorkerAuditError(
            "S1-EB25 release contract changed"
        )
    if not isinstance(authorization, E1ConfirmationOwnerAuthorization) or (
        authorization.release_contract_digest != release.contract_digest
        or authorization.project_owner_authorization != "AUTHORIZED_ONE_SHOT"
    ):
        raise E1ConfirmationReleasedWorkerAuditError(
            "S1-EB25 owner authorization changed"
        )
    if not isinstance(resource_guard, E1ConfirmationResourceGuardBinding) or (
        resource_guard.authorization_digest != authorization.authorization_digest
        or resource_guard.binding_digest != S1_EB22_RESOURCE_GUARD_DIGEST
    ):
        raise E1ConfirmationReleasedWorkerAuditError(
            "S1-EB25 resource guard changed"
        )
    if any(
        value is not False
        for value in (
            binding.execution_permitted,
            binding.persistence_permitted,
            chain.execution_permitted,
            chain.execution_started,
            release.execution_permitted,
            release.persistence_permitted,
            authorization.execution_permitted,
            authorization.persistence_permitted,
            resource_guard.canonical_execution_permitted,
        )
    ):
        raise E1ConfirmationReleasedWorkerAuditError(
            "S1-EB25 requires all canonical gates to remain closed"
        )
    upstream = Path(chain.upstream_report_path)
    if hashlib.sha256(upstream.read_bytes()).hexdigest() != S1_EA6_SHA256:
        raise E1ConfirmationReleasedWorkerAuditError(
            "S1-EB25 S1-EA6 hash changed"
        )
    targets = tuple(str(Path(value).resolve()) for value in chain._target_path_values())
    values = {
        "audit_id": "e1.confirmation-released-worker-audit.s1eb25.v1",
        "binding_digest": binding.digest(),
        "chain_contract_digest": chain.digest(),
        "release_contract_digest": release.contract_digest,
        "authorization_digest": authorization.authorization_digest,
        "resource_guard_digest": resource_guard.binding_digest,
        "canonical_implementation_digests": current_s1_eb17_implementation_digests(),
        "release_implementation_digests": current_s1_eb25_release_digests(),
        "decision_receipts": current_s1_eb25_decision_receipts(),
        "s1_ea6_sha256": S1_EA6_SHA256,
        "target_paths": targets,
        "target_paths_free": all(not Path(value).exists() for value in targets),
        "canonical_worker_order": S1_EB25_CANONICAL_WORKER_ORDER,
        "total_field_steps": release.total_field_steps,
        "max_wall_seconds": release.max_wall_seconds,
        "max_peak_rss_bytes": release.max_peak_rss_bytes,
        "static_contract_check_complete": True,
        "owner_one_shot_authorized": True,
        "resource_enforcement_bound": True,
        "same_session_preflight_proven_synthetically": True,
        "guarded_worker_proven_synthetically": True,
        "canonical_worker_contract_bound": True,
        "canonical_worker_implemented": False,
        "canonical_execution_permitted": False,
        "canonical_persistence_permitted": False,
        "retry_permitted": False,
        "claims_permitted": False,
        "audit_status": "RELEASE_CHAIN_BOUND_CANONICAL_WORKER_NOT_IMPLEMENTED",
    }
    return E1ConfirmationReleasedWorkerAudit(
        **values,
        audit_digest=_digest(values),
    )
