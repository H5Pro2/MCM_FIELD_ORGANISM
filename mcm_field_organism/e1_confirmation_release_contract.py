"""Private S1-EB19 immutable release contract; not an authorization."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from .e1_confirmation_canonical_producer_binding import (
    E1ConfirmationCanonicalProducerBinding,
)
from .e1_confirmation_chain_contract import E1ConfirmationChainContract
from .e1_confirmation_release_audit import E1ConfirmationReleaseAudit
from .e1_refined_formation_runner import _digest


class E1ConfirmationReleaseContractError(ValueError):
    """Raised when an S1-EB19 release boundary changed."""


S1_EB19_TOTAL_FIELD_STEPS = 23_800
S1_EB19_MAX_WALL_SECONDS = 1_800
S1_EB19_MAX_PEAK_RSS_BYTES = 4 * 1024 * 1024 * 1024
S1_EB19_RELEASE_REQUIREMENTS = (
    "static_contract_check",
    "project_owner_one_shot_authorization",
    "same_session_digest_and_target_preflight",
    "runtime_and_memory_limit_enforcement",
    "no_retry_and_no_claim_acknowledgement",
)


def _valid_digest(value: str) -> bool:
    return len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


@dataclass(frozen=True, slots=True)
class E1ConfirmationReleaseContract:
    contract_id: str
    binding_digest: str
    chain_contract_digest: str
    release_audit_digest: str
    total_field_steps: int
    max_wall_seconds: int
    max_peak_rss_bytes: int
    report_path: str
    attempt_path: str
    lock_path: str
    release_requirements: tuple[str, ...]
    static_contract_check_decision: str
    project_owner_authorization: str
    same_session_preflight_complete: bool
    resource_enforcement_bound: bool
    no_retry_after_started_failure: bool
    s1_ea6_rerun_permitted: bool
    posthoc_tuning_permitted: bool
    execution_permitted: bool
    persistence_permitted: bool
    claims_permitted: bool
    release_status: str
    contract_digest: str

    def __post_init__(self) -> None:
        if self.contract_id != "e1.confirmation-release.s1eb19.once.v1":
            raise E1ConfirmationReleaseContractError(
                "S1-EB19 contract identity changed"
            )
        for role in (
            "binding_digest",
            "chain_contract_digest",
            "release_audit_digest",
            "contract_digest",
        ):
            if not _valid_digest(getattr(self, role)):
                raise E1ConfirmationReleaseContractError(
                    f"{role} is not SHA-256"
                )
        if (
            self.total_field_steps != S1_EB19_TOTAL_FIELD_STEPS
            or self.max_wall_seconds != S1_EB19_MAX_WALL_SECONDS
            or self.max_peak_rss_bytes != S1_EB19_MAX_PEAK_RSS_BYTES
            or self.release_requirements != S1_EB19_RELEASE_REQUIREMENTS
        ):
            raise E1ConfirmationReleaseContractError(
                "S1-EB19 resource or requirement boundary changed"
            )
        targets = tuple(
            Path(value)
            for value in (self.report_path, self.attempt_path, self.lock_path)
        )
        if (
            len(set(targets)) != 3
            or len({item.parent for item in targets}) != 1
            or any(item.exists() for item in targets)
        ):
            raise E1ConfirmationReleaseContractError(
                "S1-EB19 one-shot targets are not distinct and free"
            )
        if (
            self.static_contract_check_decision != "PENDING"
            or self.project_owner_authorization != "PENDING"
            or self.same_session_preflight_complete is not False
            or self.resource_enforcement_bound is not False
            or self.no_retry_after_started_failure is not True
            or self.s1_ea6_rerun_permitted is not False
            or self.posthoc_tuning_permitted is not False
            or self.release_status
            != "DRAFT_AWAITING_AUTHORIZATION_AND_ENFORCEMENT"
            or any(
                value is not False
                for value in (
                    self.execution_permitted,
                    self.persistence_permitted,
                    self.claims_permitted,
                )
            )
        ):
            raise E1ConfirmationReleaseContractError(
                "S1-EB19 cannot grant authorization or execution"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "contract_digest"
        }
        if self.contract_digest != _digest(payload):
            raise E1ConfirmationReleaseContractError(
                "S1-EB19 digest does not match its payload"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


def prepare_e1_confirmation_release_contract(
    binding: E1ConfirmationCanonicalProducerBinding,
    chain_contract: E1ConfirmationChainContract,
    release_audit: E1ConfirmationReleaseAudit,
) -> E1ConfirmationReleaseContract:
    """Bind release limits while authorization and execution remain pending."""

    if not isinstance(binding, E1ConfirmationCanonicalProducerBinding):
        raise E1ConfirmationReleaseContractError(
            "S1-EB19 requires the S1-EB9 producer binding"
        )
    if not isinstance(chain_contract, E1ConfirmationChainContract) or (
        binding.chain_contract_digest != chain_contract.digest()
    ):
        raise E1ConfirmationReleaseContractError(
            "S1-EB19 requires the matching S1-EB4 chain contract"
        )
    if not isinstance(release_audit, E1ConfirmationReleaseAudit) or (
        release_audit.binding_digest != binding.digest()
        or release_audit.chain_contract_digest != chain_contract.digest()
        or release_audit.technical_chain_complete is not True
        or release_audit.research_release_complete is not False
    ):
        raise E1ConfirmationReleaseContractError(
            "S1-EB19 requires the closed S1-EB17 release audit"
        )
    if any(
        value is not False
        for value in (
            binding.execution_permitted,
            binding.persistence_permitted,
            chain_contract.execution_permitted,
            chain_contract.execution_started,
            release_audit.execution_permitted,
            release_audit.persistence_permitted,
        )
    ):
        raise E1ConfirmationReleaseContractError(
            "S1-EB19 requires all upstream gates to remain closed"
        )
    values = {
        "contract_id": "e1.confirmation-release.s1eb19.once.v1",
        "binding_digest": binding.digest(),
        "chain_contract_digest": chain_contract.digest(),
        "release_audit_digest": release_audit.audit_digest,
        "total_field_steps": S1_EB19_TOTAL_FIELD_STEPS,
        "max_wall_seconds": S1_EB19_MAX_WALL_SECONDS,
        "max_peak_rss_bytes": S1_EB19_MAX_PEAK_RSS_BYTES,
        "report_path": chain_contract.report_path,
        "attempt_path": chain_contract.attempt_path,
        "lock_path": chain_contract.lock_path,
        "release_requirements": S1_EB19_RELEASE_REQUIREMENTS,
        "static_contract_check_decision": "PENDING",
        "project_owner_authorization": "PENDING",
        "same_session_preflight_complete": False,
        "resource_enforcement_bound": False,
        "no_retry_after_started_failure": True,
        "s1_ea6_rerun_permitted": False,
        "posthoc_tuning_permitted": False,
        "execution_permitted": False,
        "persistence_permitted": False,
        "claims_permitted": False,
        "release_status": "DRAFT_AWAITING_AUTHORIZATION_AND_ENFORCEMENT",
    }
    return E1ConfirmationReleaseContract(
        **values,
        contract_digest=_digest(values),
    )
