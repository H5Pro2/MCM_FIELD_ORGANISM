"""Private S1-EB23 ephemeral preflight for immediate one-shot consumption."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import os
from pathlib import Path
import time

from .e1_confirmation_canonical_producer_binding import (
    E1ConfirmationCanonicalProducerBinding,
)
from .e1_confirmation_chain_contract import E1ConfirmationChainContract
from .e1_confirmation_owner_authorization import (
    E1ConfirmationOwnerAuthorization,
)
from .e1_confirmation_release_contract import E1ConfirmationReleaseContract
from .e1_confirmation_resource_guard import (
    E1ConfirmationResourceGuardBinding,
)
from .e1_refined_formation_runner import _digest


class E1ConfirmationSameSessionPreflightError(ValueError):
    """Raised when S1-EB23 is stale or any release input changed."""


S1_EB23_MAX_AGE_NS = 5_000_000_000
S1_EA6_SHA256 = (
    "adf8b2b6c1b9fdda48062dbb1cd9149fcde462a3dc77a348aa2dfb0cb1fcaa47"
)
S1_EB23_BOUND_FILES = (
    ("release_review", "docs/S1EB20_UNABHAENGIGE_PRUEFERENTSCHEIDUNG.md"),
    ("owner_authorization", "docs/S1EB21_PROJEKTEIGNER_EINMALLAUF_AUTORISIERUNG.md"),
    ("resource_guard", "mcm_field_organism/e1_confirmation_resource_guard.py"),
    ("canonical_formation", "mcm_field_organism/e1_confirmation_canonical_formation_adapter.py"),
    ("canonical_probe", "mcm_field_organism/e1_confirmation_canonical_probe_adapter.py"),
    ("canonical_result", "mcm_field_organism/e1_confirmation_canonical_result_compositor.py"),
    ("canonical_report", "mcm_field_organism/e1_confirmation_canonical_report_handoff.py"),
    ("canonical_executor", "mcm_field_organism/e1_confirmation_canonical_executor.py"),
)
S1_EB23_BOUND_DIGESTS = (
    ("release_review", "0cfa8504d39787b1c5d5395dd6bf65947af28b3cca7d851e67c4a9f1819e993a"),
    ("owner_authorization", "e9f3882319855d54d8432e20683f17c9258a47be32bb23a845f956b80e9ba569"),
    ("resource_guard", "df01fef096fb463c5297b3b99b98b9e5b4d8602343c6108f1b7833b7f94a12e4"),
    ("canonical_formation", "0cdadade84639e29c8fc8affa1601c5d8ab034f5238900e461dd971914b4ffe6"),
    ("canonical_probe", "14ca32466f45dea0aafcd9fdb6da76888e0d89c7f49256859f6abb2f907687f9"),
    ("canonical_result", "db3e2fe8c43154db142a5882badd801725bd7ff5aa7081da72b042c56db02b2f"),
    ("canonical_report", "3e29fc1e968ff24700dc35cc34d2e3a0bf8545c7253c53bd65b4fb8503560faf"),
    ("canonical_executor", "efc1819e6c96bd3a29bada4cff90f014a7f0f7a189708b8ad54f65de31c8bfb6"),
)


def _workspace_root() -> Path:
    return Path(__file__).parents[1]


def current_s1_eb23_bound_digests() -> tuple[tuple[str, str], ...]:
    root = _workspace_root()
    result = []
    for role, relative in S1_EB23_BOUND_FILES:
        path = root / relative
        if not path.is_file():
            raise E1ConfirmationSameSessionPreflightError(
                f"S1-EB23 bound file is missing: {relative}"
            )
        if path.suffix == ".py":
            normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
            encoded = normalized.encode("utf-8")
        else:
            encoded = path.read_bytes()
        result.append((role, hashlib.sha256(encoded).hexdigest()))
    return tuple(result)


@dataclass(frozen=True, slots=True)
class E1ConfirmationSameSessionPreflight:
    preflight_id: str
    process_id: int
    issued_monotonic_ns: int
    max_age_ns: int
    binding_digest: str
    chain_contract_digest: str
    release_contract_digest: str
    authorization_digest: str
    resource_guard_digest: str
    bound_file_digests: tuple[tuple[str, str], ...]
    s1_ea6_sha256: str
    target_paths: tuple[str, ...]
    targets_free: bool
    total_field_steps: int
    max_wall_seconds: int
    max_peak_rss_bytes: int
    one_shot_authorized: bool
    resource_enforcement_bound: bool
    no_retry_bound: bool
    canonical_execution_permitted: bool
    canonical_persistence_permitted: bool
    claims_permitted: bool
    preflight_status: str
    preflight_digest: str

    def __post_init__(self) -> None:
        if (
            self.preflight_id != "e1.confirmation-preflight.s1eb23.once.v1"
            or self.process_id != os.getpid()
            or self.issued_monotonic_ns <= 0
            or self.max_age_ns != S1_EB23_MAX_AGE_NS
            or self.bound_file_digests != S1_EB23_BOUND_DIGESTS
            or self.bound_file_digests != current_s1_eb23_bound_digests()
            or self.s1_ea6_sha256 != S1_EA6_SHA256
            or self.targets_free is not True
            or self.total_field_steps != 23_800
            or self.max_wall_seconds != 1_800
            or self.max_peak_rss_bytes != 4 * 1024**3
            or self.one_shot_authorized is not True
            or self.resource_enforcement_bound is not True
            or self.no_retry_bound is not True
            or self.canonical_execution_permitted is not True
            or self.canonical_persistence_permitted is not True
            or self.claims_permitted is not False
            or self.preflight_status != "READY_FOR_IMMEDIATE_ONE_SHOT"
        ):
            raise E1ConfirmationSameSessionPreflightError(
                "S1-EB23 release preflight changed"
            )
        targets = tuple(Path(value) for value in self.target_paths)
        if len(targets) != 3 or len(set(targets)) != 3 or any(
            item.exists() for item in targets
        ):
            raise E1ConfirmationSameSessionPreflightError(
                "S1-EB23 targets are not distinct and free"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "preflight_digest"
        }
        if self.preflight_digest != _digest(payload):
            raise E1ConfirmationSameSessionPreflightError(
                "S1-EB23 digest does not match its payload"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


def prepare_e1_confirmation_same_session_preflight(
    binding: E1ConfirmationCanonicalProducerBinding,
    chain: E1ConfirmationChainContract,
    release: E1ConfirmationReleaseContract,
    authorization: E1ConfirmationOwnerAuthorization,
    resource_guard: E1ConfirmationResourceGuardBinding,
) -> E1ConfirmationSameSessionPreflight:
    """Create one process-local, five-second release gate without running."""

    if not isinstance(binding, E1ConfirmationCanonicalProducerBinding) or not isinstance(
        chain, E1ConfirmationChainContract
    ) or binding.chain_contract_digest != chain.digest():
        raise E1ConfirmationSameSessionPreflightError(
            "S1-EB23 binding and chain contract do not match"
        )
    if not isinstance(release, E1ConfirmationReleaseContract) or (
        release.binding_digest != binding.digest()
        or release.chain_contract_digest != chain.digest()
    ):
        raise E1ConfirmationSameSessionPreflightError(
            "S1-EB23 release contract changed"
        )
    if not isinstance(authorization, E1ConfirmationOwnerAuthorization) or (
        authorization.release_contract_digest != release.contract_digest
        or authorization.project_owner_authorization != "AUTHORIZED_ONE_SHOT"
    ):
        raise E1ConfirmationSameSessionPreflightError(
            "S1-EB23 owner authorization changed"
        )
    if not isinstance(resource_guard, E1ConfirmationResourceGuardBinding) or (
        resource_guard.authorization_digest != authorization.authorization_digest
        or resource_guard.max_wall_seconds != release.max_wall_seconds
        or resource_guard.max_peak_rss_bytes != release.max_peak_rss_bytes
    ):
        raise E1ConfirmationSameSessionPreflightError(
            "S1-EB23 resource enforcement changed"
        )
    upstream = Path(chain.upstream_report_path)
    if hashlib.sha256(upstream.read_bytes()).hexdigest() != S1_EA6_SHA256:
        raise E1ConfirmationSameSessionPreflightError(
            "S1-EB23 S1-EA6 hash changed"
        )
    targets = tuple(str(Path(value).resolve()) for value in chain._target_path_values())
    values = {
        "preflight_id": "e1.confirmation-preflight.s1eb23.once.v1",
        "process_id": os.getpid(),
        "issued_monotonic_ns": time.monotonic_ns(),
        "max_age_ns": S1_EB23_MAX_AGE_NS,
        "binding_digest": binding.digest(),
        "chain_contract_digest": chain.digest(),
        "release_contract_digest": release.contract_digest,
        "authorization_digest": authorization.authorization_digest,
        "resource_guard_digest": resource_guard.binding_digest,
        "bound_file_digests": current_s1_eb23_bound_digests(),
        "s1_ea6_sha256": S1_EA6_SHA256,
        "target_paths": targets,
        "targets_free": all(not Path(value).exists() for value in targets),
        "total_field_steps": release.total_field_steps,
        "max_wall_seconds": release.max_wall_seconds,
        "max_peak_rss_bytes": release.max_peak_rss_bytes,
        "one_shot_authorized": True,
        "resource_enforcement_bound": True,
        "no_retry_bound": True,
        "canonical_execution_permitted": True,
        "canonical_persistence_permitted": True,
        "claims_permitted": False,
        "preflight_status": "READY_FOR_IMMEDIATE_ONE_SHOT",
    }
    return E1ConfirmationSameSessionPreflight(
        **values,
        preflight_digest=_digest(values),
    )


def require_fresh_e1_confirmation_preflight(
    preflight: E1ConfirmationSameSessionPreflight,
) -> None:
    """Fail unless the gate is current, same-process, intact, and unconsumed."""

    if not isinstance(preflight, E1ConfirmationSameSessionPreflight):
        raise E1ConfirmationSameSessionPreflightError(
            "S1-EB23 requires one preflight receipt"
        )
    preflight.__post_init__()
    age = time.monotonic_ns() - preflight.issued_monotonic_ns
    if age < 0 or age > preflight.max_age_ns:
        raise E1ConfirmationSameSessionPreflightError(
            "S1-EB23 preflight is stale"
        )
