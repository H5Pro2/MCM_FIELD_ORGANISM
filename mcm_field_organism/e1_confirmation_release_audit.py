"""Private S1-EB17 static release audit; grants no execution permission."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
from pathlib import Path

from .e1_confirmation_canonical_producer_binding import (
    E1ConfirmationCanonicalProducerBinding,
)
from .e1_confirmation_chain_contract import E1ConfirmationChainContract
from .e1_refined_formation_runner import _digest


class E1ConfirmationReleaseAuditError(ValueError):
    """Raised when an S1-EB17 audit invariant changed."""


S1_EB17_IMPLEMENTATION_FILES = (
    ("s1eb9_producer_binding", "e1_confirmation_canonical_producer_binding.py"),
    ("s1eb10_formation", "e1_confirmation_canonical_formation_adapter.py"),
    ("s1eb11_probe_handoff", "e1_confirmation_canonical_probe_handoff.py"),
    ("s1eb12_probe", "e1_confirmation_canonical_probe_adapter.py"),
    ("s1eb13_result_handoff", "e1_confirmation_canonical_result_handoff.py"),
    ("s1eb14_result", "e1_confirmation_canonical_result_compositor.py"),
    ("s1eb15_report_handoff", "e1_confirmation_canonical_report_handoff.py"),
    ("s1eb16_executor", "e1_confirmation_canonical_executor.py"),
)
S1_EB17_IMPLEMENTATION_DIGESTS = (
    (
        "s1eb9_producer_binding",
        "d00d8910847fe7d40beea926dfb3a189375b279d6f6c525bee51f567fce5aaf9",
    ),
    (
        "s1eb10_formation",
        "0cdadade84639e29c8fc8affa1601c5d8ab034f5238900e461dd971914b4ffe6",
    ),
    (
        "s1eb11_probe_handoff",
        "7ba9a880ff8e1e5530cf47fa5ac11b92a1ec17e7beac48813b38d56e4fdfe1e0",
    ),
    (
        "s1eb12_probe",
        "14ca32466f45dea0aafcd9fdb6da76888e0d89c7f49256859f6abb2f907687f9",
    ),
    (
        "s1eb13_result_handoff",
        "82153cfd9de0cdeecae8cd1c852973c8b5d669aa419ad84110383634e586005c",
    ),
    (
        "s1eb14_result",
        "db3e2fe8c43154db142a5882badd801725bd7ff5aa7081da72b042c56db02b2f",
    ),
    (
        "s1eb15_report_handoff",
        "3e29fc1e968ff24700dc35cc34d2e3a0bf8545c7253c53bd65b4fb8503560faf",
    ),
    (
        "s1eb16_executor",
        "efc1819e6c96bd3a29bada4cff90f014a7f0f7a189708b8ad54f65de31c8bfb6",
    ),
)
S1_EA6_REPORT_SHA256 = (
    "adf8b2b6c1b9fdda48062dbb1cd9149fcde462a3dc77a348aa2dfb0cb1fcaa47"
)
S1_EB17_REQUIRED_RELEASE_ACTIONS = (
    "static_contract_check_of_question_controls_and_claim_boundary",
    "explicit_one_shot_authorization_for_canonical_formation_probe_and_report",
    "final_same_session_digest_and_free_target_revalidation",
    "fixed_resource_and_runtime_envelope_before_execution",
    "acknowledgement_that_failure_retains_attempt_and_forbids_automatic_retry",
)


def _normalized_source_digest(name: str) -> str:
    path = Path(__file__).with_name(name)
    if not path.is_file():
        raise E1ConfirmationReleaseAuditError(
            f"S1-EB17 implementation is missing: {name}"
        )
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def current_s1_eb17_implementation_digests() -> tuple[tuple[str, str], ...]:
    return tuple(
        (role, _normalized_source_digest(name))
        for role, name in S1_EB17_IMPLEMENTATION_FILES
    )


@dataclass(frozen=True, slots=True)
class E1ConfirmationReleaseAudit:
    audit_id: str
    binding_digest: str
    chain_contract_digest: str
    implementation_digests: tuple[tuple[str, str], ...]
    s1_ea6_report_path: str
    s1_ea6_report_sha256: str
    target_paths: tuple[str, ...]
    target_paths_free: bool
    bound_chain_roles: tuple[str, ...]
    required_release_actions: tuple[str, ...]
    audit_status: str
    technical_chain_complete: bool
    research_release_complete: bool
    execution_permitted: bool
    persistence_permitted: bool
    retry_permitted: bool
    claims_permitted: bool
    audit_digest: str

    def __post_init__(self) -> None:
        if self.audit_id != "e1.confirmation-release-audit.s1eb17.v1":
            raise E1ConfirmationReleaseAuditError(
                "S1-EB17 audit identity changed"
            )
        if (
            self.implementation_digests != S1_EB17_IMPLEMENTATION_DIGESTS
            or self.implementation_digests
            != current_s1_eb17_implementation_digests()
        ):
            raise E1ConfirmationReleaseAuditError(
                "S1-EB17 implementation inventory changed"
            )
        if (
            self.s1_ea6_report_sha256 != S1_EA6_REPORT_SHA256
            or not Path(self.s1_ea6_report_path).is_file()
        ):
            raise E1ConfirmationReleaseAuditError(
                "S1-EB17 upstream report binding changed"
            )
        targets = tuple(Path(value) for value in self.target_paths)
        if (
            len(targets) != 3
            or len(set(targets)) != 3
            or len({item.parent for item in targets}) != 1
            or self.target_paths_free is not True
            or any(item.exists() for item in targets)
        ):
            raise E1ConfirmationReleaseAuditError(
                "S1-EB17 target paths are not distinct and free"
            )
        if self.bound_chain_roles != tuple(
            role for role, _ in S1_EB17_IMPLEMENTATION_FILES
        ) or self.required_release_actions != S1_EB17_REQUIRED_RELEASE_ACTIONS:
            raise E1ConfirmationReleaseAuditError(
                "S1-EB17 role or release-action inventory changed"
            )
        if (
            self.audit_status
            != "TECHNICALLY_BOUND_AWAITING_EXPLICIT_RESEARCH_RELEASE"
            or self.technical_chain_complete is not True
            or self.research_release_complete is not False
            or any(
                value is not False
                for value in (
                    self.execution_permitted,
                    self.persistence_permitted,
                    self.retry_permitted,
                    self.claims_permitted,
                )
            )
        ):
            raise E1ConfirmationReleaseAuditError(
                "S1-EB17 cannot grant research release or execution"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "audit_digest"
        }
        if self.audit_digest != _digest(payload):
            raise E1ConfirmationReleaseAuditError(
                "S1-EB17 audit digest does not match its payload"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


def audit_e1_confirmation_release_readiness(
    binding: E1ConfirmationCanonicalProducerBinding,
    chain_contract: E1ConfirmationChainContract,
) -> E1ConfirmationReleaseAudit:
    """Audit the locked chain without building fields, running, or writing."""

    if not isinstance(binding, E1ConfirmationCanonicalProducerBinding):
        raise E1ConfirmationReleaseAuditError(
            "S1-EB17 requires the S1-EB9 producer binding"
        )
    if not isinstance(chain_contract, E1ConfirmationChainContract) or (
        binding.chain_contract_digest != chain_contract.digest()
    ):
        raise E1ConfirmationReleaseAuditError(
            "S1-EB17 requires the matching S1-EB4 chain contract"
        )
    if (
        binding.execution_permitted is not False
        or binding.persistence_permitted is not False
        or chain_contract.execution_permitted is not False
        or chain_contract.execution_started is not False
    ):
        raise E1ConfirmationReleaseAuditError(
            "S1-EB17 requires all canonical gates to remain closed"
        )
    upstream = Path(chain_contract.upstream_report_path)
    if hashlib.sha256(upstream.read_bytes()).hexdigest() != S1_EA6_REPORT_SHA256:
        raise E1ConfirmationReleaseAuditError(
            "S1-EB17 upstream report hash changed"
        )
    targets = tuple(
        str(Path(value).resolve())
        for value in chain_contract._target_path_values()
    )
    values = {
        "audit_id": "e1.confirmation-release-audit.s1eb17.v1",
        "binding_digest": binding.digest(),
        "chain_contract_digest": chain_contract.digest(),
        "implementation_digests": current_s1_eb17_implementation_digests(),
        "s1_ea6_report_path": str(upstream.resolve()),
        "s1_ea6_report_sha256": S1_EA6_REPORT_SHA256,
        "target_paths": targets,
        "target_paths_free": all(not Path(value).exists() for value in targets),
        "bound_chain_roles": tuple(
            role for role, _ in S1_EB17_IMPLEMENTATION_FILES
        ),
        "required_release_actions": S1_EB17_REQUIRED_RELEASE_ACTIONS,
        "audit_status": "TECHNICALLY_BOUND_AWAITING_EXPLICIT_RESEARCH_RELEASE",
        "technical_chain_complete": True,
        "research_release_complete": False,
        "execution_permitted": False,
        "persistence_permitted": False,
        "retry_permitted": False,
        "claims_permitted": False,
    }
    return E1ConfirmationReleaseAudit(
        **values,
        audit_digest=_digest(values),
    )
