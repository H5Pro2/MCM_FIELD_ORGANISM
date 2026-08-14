"""Private S1-EB21 owner authorization receipt; execution stays closed."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
from pathlib import Path

from .e1_confirmation_release_contract import E1ConfirmationReleaseContract
from .e1_refined_formation_runner import _digest


class E1ConfirmationOwnerAuthorizationError(ValueError):
    """Raised when an S1-EB21 authorization boundary changed."""


S1_EB20_REVIEW_PATH = Path(__file__).parents[1] / (
    "docs/S1EB20_UNABHAENGIGE_PRUEFERENTSCHEIDUNG.md"
)
S1_EB20_REVIEW_SHA256 = (
    "0cfa8504d39787b1c5d5395dd6bf65947af28b3cca7d851e67c4a9f1819e993a"
)


def _valid_digest(value: str) -> bool:
    return len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


@dataclass(frozen=True, slots=True)
class E1ConfirmationOwnerAuthorization:
    authorization_id: str
    release_contract_digest: str
    independent_review_path: str
    independent_review_sha256: str
    independent_reviewer_decision: str
    project_owner_authorization: str
    authorized_run_count: int
    total_field_steps: int
    max_wall_seconds: int
    max_peak_rss_bytes: int
    no_retry_after_started_failure: bool
    s1_ea6_rerun_permitted: bool
    posthoc_tuning_permitted: bool
    memory_or_ai_claim_permitted: bool
    resource_enforcement_bound: bool
    same_session_preflight_complete: bool
    execution_permitted: bool
    persistence_permitted: bool
    authorization_status: str
    authorization_digest: str

    def __post_init__(self) -> None:
        for role in (
            "release_contract_digest",
            "independent_review_sha256",
            "authorization_digest",
        ):
            if not _valid_digest(getattr(self, role)):
                raise E1ConfirmationOwnerAuthorizationError(
                    f"{role} is not SHA-256"
                )
        if (
            self.authorization_id
            != "e1.confirmation-owner-authorization.s1eb21.once.v1"
            or self.independent_review_sha256 != S1_EB20_REVIEW_SHA256
            or self.independent_reviewer_decision != "FREIGABE"
            or self.project_owner_authorization != "AUTHORIZED_ONE_SHOT"
            or self.authorized_run_count != 1
            or self.total_field_steps != 23_800
            or self.max_wall_seconds != 1_800
            or self.max_peak_rss_bytes != 4 * 1024 * 1024 * 1024
            or self.no_retry_after_started_failure is not True
            or self.authorization_status
            != "OWNER_AUTHORIZED_AWAITING_ENFORCEMENT_AND_PREFLIGHT"
        ):
            raise E1ConfirmationOwnerAuthorizationError(
                "S1-EB21 authorization identity or envelope changed"
            )
        if (
            self.s1_ea6_rerun_permitted is not False
            or self.posthoc_tuning_permitted is not False
            or self.memory_or_ai_claim_permitted is not False
            or self.resource_enforcement_bound is not False
            or self.same_session_preflight_complete is not False
            or self.execution_permitted is not False
            or self.persistence_permitted is not False
        ):
            raise E1ConfirmationOwnerAuthorizationError(
                "S1-EB21 cannot bypass enforcement or preflight"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "authorization_digest"
        }
        if self.authorization_digest != _digest(payload):
            raise E1ConfirmationOwnerAuthorizationError(
                "S1-EB21 digest does not match its payload"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


def bind_e1_confirmation_owner_authorization(
    release_contract: E1ConfirmationReleaseContract,
) -> E1ConfirmationOwnerAuthorization:
    """Bind the explicit one-shot owner decision without opening execution."""

    if not isinstance(release_contract, E1ConfirmationReleaseContract):
        raise E1ConfirmationOwnerAuthorizationError(
            "S1-EB21 requires the S1-EB19 release contract"
        )
    if (
        release_contract.independent_reviewer_decision != "PENDING"
        or release_contract.project_owner_authorization != "PENDING"
        or release_contract.execution_permitted is not False
        or release_contract.persistence_permitted is not False
    ):
        raise E1ConfirmationOwnerAuthorizationError(
            "S1-EB21 requires the unchanged closed release draft"
        )
    if not S1_EB20_REVIEW_PATH.is_file() or hashlib.sha256(
        S1_EB20_REVIEW_PATH.read_bytes()
    ).hexdigest() != S1_EB20_REVIEW_SHA256:
        raise E1ConfirmationOwnerAuthorizationError(
            "S1-EB21 independent review receipt changed"
        )
    values = {
        "authorization_id": (
            "e1.confirmation-owner-authorization.s1eb21.once.v1"
        ),
        "release_contract_digest": release_contract.contract_digest,
        "independent_review_path": str(S1_EB20_REVIEW_PATH.resolve()),
        "independent_review_sha256": S1_EB20_REVIEW_SHA256,
        "independent_reviewer_decision": "FREIGABE",
        "project_owner_authorization": "AUTHORIZED_ONE_SHOT",
        "authorized_run_count": 1,
        "total_field_steps": release_contract.total_field_steps,
        "max_wall_seconds": release_contract.max_wall_seconds,
        "max_peak_rss_bytes": release_contract.max_peak_rss_bytes,
        "no_retry_after_started_failure": (
            release_contract.no_retry_after_started_failure
        ),
        "s1_ea6_rerun_permitted": False,
        "posthoc_tuning_permitted": False,
        "memory_or_ai_claim_permitted": False,
        "resource_enforcement_bound": False,
        "same_session_preflight_complete": False,
        "execution_permitted": False,
        "persistence_permitted": False,
        "authorization_status": (
            "OWNER_AUTHORIZED_AWAITING_ENFORCEMENT_AND_PREFLIGHT"
        ),
    }
    return E1ConfirmationOwnerAuthorization(
        **values,
        authorization_digest=_digest(values),
    )
