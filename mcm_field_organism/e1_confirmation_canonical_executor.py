"""Private S1-EB16 canonical exactly-once executor; execution locked."""

from __future__ import annotations

from pathlib import Path

from .e1_confirmation_canonical_producer_binding import (
    E1ConfirmationCanonicalProducerBinding,
)
from .e1_confirmation_canonical_report_handoff import (
    E1ConfirmationCanonicalReportHandoff,
)
from .e1_confirmation_chain_contract import E1ConfirmationChainContract
from .e1_confirmation_result_core import E1ConfirmationChainResult
from .e1_confirmation_synthetic_executor import (
    E1ConfirmationSyntheticReceipt,
    execute_synthetic_e1_confirmation_once,
)


class E1ConfirmationCanonicalExecutorError(RuntimeError):
    """Raised when an S1-EB16 executor binding or release gate changed."""


_BINDING_DIGEST = (
    "aae7f9427200c88f60155f884c3ee6a4279941c4ecf878f8490a69e19f7c2d34"
)


def _execute_bound_report_synthetically(
    chain_contract: E1ConfirmationChainContract,
    report_handoff: E1ConfirmationCanonicalReportHandoff,
    result: E1ConfirmationChainResult,
    synthetic_directory: Path,
) -> E1ConfirmationSyntheticReceipt:
    """Exercise the existing atomic writer outside registered targets."""

    if not isinstance(chain_contract, E1ConfirmationChainContract):
        raise E1ConfirmationCanonicalExecutorError(
            "S1-EB16 requires one S1-EB4 chain contract"
        )
    if not isinstance(report_handoff, E1ConfirmationCanonicalReportHandoff) or (
        report_handoff.chain_contract_digest != chain_contract.digest()
    ):
        raise E1ConfirmationCanonicalExecutorError(
            "S1-EB16 requires one matching S1-EB15 report handoff"
        )
    if not isinstance(result, E1ConfirmationChainResult) or (
        result.contract_digest != chain_contract.digest()
        or result.result_digest != report_handoff.result_digest
        or result.technical_decision != report_handoff.technical_decision
    ):
        raise E1ConfirmationCanonicalExecutorError(
            "S1-EB16 result does not match its report handoff"
        )
    directory = Path(synthetic_directory).resolve()
    registered = Path(chain_contract.report_path).parent.resolve()
    if directory == registered:
        raise E1ConfirmationCanonicalExecutorError(
            "S1-EB16 synthetic execution cannot use registered targets"
        )
    try:
        return execute_synthetic_e1_confirmation_once(
            chain_contract,
            lambda: result,
            directory,
        )
    except RuntimeError as exc:
        if isinstance(exc, E1ConfirmationCanonicalExecutorError):
            raise
        raise E1ConfirmationCanonicalExecutorError(str(exc)) from exc


def execute_e1_confirmation_canonical_once(
    binding: E1ConfirmationCanonicalProducerBinding,
    chain_contract: E1ConfirmationChainContract,
    report_handoff: E1ConfirmationCanonicalReportHandoff,
    result: E1ConfirmationChainResult,
) -> None:
    """Reserve canonical publication while the S1-EB15 gate is closed."""

    if not isinstance(binding, E1ConfirmationCanonicalProducerBinding) or (
        binding.digest() != _BINDING_DIGEST
    ):
        raise E1ConfirmationCanonicalExecutorError(
            "S1-EB16 requires the unchanged S1-EB9 binding"
        )
    if not isinstance(chain_contract, E1ConfirmationChainContract) or (
        chain_contract.digest() != binding.chain_contract_digest
    ):
        raise E1ConfirmationCanonicalExecutorError(
            "S1-EB16 requires the bound S1-EB4 chain contract"
        )
    if not isinstance(report_handoff, E1ConfirmationCanonicalReportHandoff) or (
        report_handoff.binding_digest != binding.digest()
        or report_handoff.chain_contract_digest != chain_contract.digest()
    ):
        raise E1ConfirmationCanonicalExecutorError(
            "S1-EB16 requires the bound S1-EB15 report handoff"
        )
    if not isinstance(result, E1ConfirmationChainResult) or (
        result.result_digest != report_handoff.result_digest
        or result.contract_digest != chain_contract.digest()
    ):
        raise E1ConfirmationCanonicalExecutorError(
            "S1-EB16 result does not match its report handoff"
        )
    if (
        report_handoff.execution_permitted is not True
        or report_handoff.persistence_permitted is not True
    ):
        raise E1ConfirmationCanonicalExecutorError(
            "S1-EB16 canonical execution and persistence remain locked"
        )
    raise E1ConfirmationCanonicalExecutorError(
        "S1-EB16 has no released canonical writer"
    )
