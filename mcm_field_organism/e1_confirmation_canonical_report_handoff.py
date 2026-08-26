"""Private S1-EB15 static handoff from canonical result to report surface."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from .e1_confirmation_canonical_producer_binding import (
    E1ConfirmationCanonicalProducerBinding,
)
from .e1_confirmation_canonical_result_handoff import (
    E1ConfirmationCanonicalResultHandoff,
)
from .e1_confirmation_chain_contract import (
    E1ConfirmationChainContract,
    S1_EB4_REPORT_FIELDS,
)
from .e1_confirmation_result_core import E1ConfirmationChainResult
from .e1_refined_formation_runner import _digest


class E1ConfirmationCanonicalReportHandoffError(ValueError):
    """Raised when an S1-EB15 report-surface binding changed."""


_BINDING_DIGEST = (
    "aae7f9427200c88f60155f884c3ee6a4279941c4ecf878f8490a69e19f7c2d34"
)


def _valid_digest(value: str) -> bool:
    return len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


@dataclass(frozen=True, slots=True)
class E1ConfirmationCanonicalReportHandoff:
    handoff_id: str
    binding_digest: str
    chain_contract_digest: str
    result_handoff_digest: str
    result_digest: str
    technical_decision: str
    report_fields: tuple[str, ...]
    source_digests: tuple[str, ...]
    plan_digests: tuple[str, ...]
    refinement_result_digests: tuple[tuple[str, str], ...]
    report_path: str
    attempt_path: str
    lock_path: str
    report_payload_digest: str
    executor_entrypoint: str
    report_handoff_bound: bool
    execution_permitted: bool
    persistence_permitted: bool
    retry_permitted: bool
    claims_permitted: bool
    handoff_digest: str

    def __post_init__(self) -> None:
        if self.handoff_id != "e1.confirmation-report-handoff.s1eb15.v1":
            raise E1ConfirmationCanonicalReportHandoffError(
                "S1-EB15 handoff identity changed"
            )
        for role in (
            "binding_digest",
            "chain_contract_digest",
            "result_handoff_digest",
            "result_digest",
            "report_payload_digest",
            "handoff_digest",
        ):
            if not _valid_digest(getattr(self, role)):
                raise E1ConfirmationCanonicalReportHandoffError(
                    f"{role} is not SHA-256"
                )
        if self.binding_digest != _BINDING_DIGEST:
            raise E1ConfirmationCanonicalReportHandoffError(
                "S1-EB15 canonical binding changed"
            )
        if (
            self.report_fields != S1_EB4_REPORT_FIELDS
            or len(self.source_digests) != 4
            or len(self.plan_digests) != 3
            or tuple(role for role, _ in self.refinement_result_digests)
            != ("r2", "r4", "r8")
        ):
            raise E1ConfirmationCanonicalReportHandoffError(
                "S1-EB15 report inventory changed"
            )
        nested = (
            *self.source_digests,
            *self.plan_digests,
            *(value for _, value in self.refinement_result_digests),
        )
        if any(not _valid_digest(value) for value in nested):
            raise E1ConfirmationCanonicalReportHandoffError(
                "S1-EB15 report inventory contains an invalid digest"
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
            raise E1ConfirmationCanonicalReportHandoffError(
                "S1-EB15 report targets are not distinct and free"
            )
        if (
            self.executor_entrypoint
            != "execute_e1_confirmation_canonical_once"
            or self.report_handoff_bound is not True
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
            raise E1ConfirmationCanonicalReportHandoffError(
                "S1-EB15 execution, persistence, retry, or claims opened"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "handoff_digest"
        }
        if self.handoff_digest != _digest(payload):
            raise E1ConfirmationCanonicalReportHandoffError(
                "S1-EB15 handoff digest does not match its payload"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


def prepare_e1_confirmation_canonical_report_handoff(
    binding: E1ConfirmationCanonicalProducerBinding,
    chain_contract: E1ConfirmationChainContract,
    result_handoff: E1ConfirmationCanonicalResultHandoff,
    result: E1ConfirmationChainResult,
) -> E1ConfirmationCanonicalReportHandoff:
    """Bind one result to the registered report surface without writing it."""

    if not isinstance(binding, E1ConfirmationCanonicalProducerBinding) or (
        binding.digest() != _BINDING_DIGEST
    ):
        raise E1ConfirmationCanonicalReportHandoffError(
            "S1-EB15 requires the unchanged S1-EB9 binding"
        )
    if not isinstance(chain_contract, E1ConfirmationChainContract) or (
        chain_contract.digest() != binding.chain_contract_digest
    ):
        raise E1ConfirmationCanonicalReportHandoffError(
            "S1-EB15 requires the bound S1-EB4 chain contract"
        )
    if not isinstance(result_handoff, E1ConfirmationCanonicalResultHandoff) or (
        result_handoff.binding_digest != binding.digest()
        or result_handoff.chain_contract_digest != chain_contract.digest()
    ):
        raise E1ConfirmationCanonicalReportHandoffError(
            "S1-EB15 requires the bound S1-EB13 result handoff"
        )
    if not isinstance(result, E1ConfirmationChainResult) or (
        result.contract_digest != chain_contract.digest()
    ):
        raise E1ConfirmationCanonicalReportHandoffError(
            "S1-EB15 requires one matching result"
        )
    expected_probe_fields = dict(result_handoff.probe_field_digests)
    expected_states = {
        role: (ab_digest, ba_digest)
        for role, ab_digest, ba_digest in result_handoff.frozen_state_digests
    }
    for item in result.refinements:
        states = dict(item.formation_state_digests)
        if (
            item.probe_field_digests != expected_probe_fields[item.refinement_id]
            or (states["ab"], states["ba"])
            != expected_states[item.refinement_id]
        ):
            raise E1ConfirmationCanonicalReportHandoffError(
                "S1-EB15 result does not match its probe or state handoff"
            )
    report = {
        "execution_id": chain_contract.execution_id,
        "confirmation_contract_digest": (
            chain_contract.confirmation_contract_digest
        ),
        "canonical_preflight_digest": chain_contract.canonical_preflight_digest,
        "implementation_digests": chain_contract.implementation_digests,
        "source_digests": (
            chain_contract.history_ab_digest,
            chain_contract.history_ba_digest,
            chain_contract.permutation_digest,
            chain_contract.probe_digest,
        ),
        "plan_digests": (
            chain_contract.ab_plan_digest,
            chain_contract.ba_plan_digest,
            chain_contract.probe_plan_digest,
        ),
        "refinement_result_digests": tuple(
            (item.refinement_id, item.digest())
            for item in result.refinements
        ),
        "result_digest": result.result_digest,
        "technical_decision": result.technical_decision,
        "metrics": result.metrics,
        "controls": result.controls,
        "result": asdict(result),
    }
    if tuple(report) != S1_EB4_REPORT_FIELDS:
        raise E1ConfirmationCanonicalReportHandoffError(
            "S1-EB15 report field order changed"
        )
    values = {
        "handoff_id": "e1.confirmation-report-handoff.s1eb15.v1",
        "binding_digest": binding.digest(),
        "chain_contract_digest": chain_contract.digest(),
        "result_handoff_digest": result_handoff.handoff_digest,
        "result_digest": result.result_digest,
        "technical_decision": result.technical_decision,
        "report_fields": S1_EB4_REPORT_FIELDS,
        "source_digests": report["source_digests"],
        "plan_digests": report["plan_digests"],
        "refinement_result_digests": report["refinement_result_digests"],
        "report_path": chain_contract.report_path,
        "attempt_path": chain_contract.attempt_path,
        "lock_path": chain_contract.lock_path,
        "report_payload_digest": _digest(report),
        "executor_entrypoint": "execute_e1_confirmation_canonical_once",
        "report_handoff_bound": True,
        "execution_permitted": False,
        "persistence_permitted": False,
        "retry_permitted": False,
        "claims_permitted": False,
    }
    return E1ConfirmationCanonicalReportHandoff(
        **values,
        handoff_digest=_digest(values),
    )
