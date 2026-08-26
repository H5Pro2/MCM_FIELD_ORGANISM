"""Private S1-EB preregistration for an independent numerical confirmation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

from .e1_canonical_refined_chain_result_audit import (
    S1_EA6_REPORT_SHA256,
    S1_EA6_RESULT_SHA256,
    audit_e1_canonical_refined_chain_result,
)
from .e1_refined_world_formation_contract import (
    S1_DS_REQUIRED_CONTROLS,
)


class E1RefinedConfirmationContractError(ValueError):
    """Raised when the S1-EB confirmation preregistration changed."""


S1_EB_REFINEMENTS = (("r2", 2), ("r4", 4), ("r8", 8))
S1_EB_HISTORY_STEP_COUNTS = (("r2", 400), ("r4", 800), ("r8", 1600))
S1_EB_PROBE_STEP_COUNTS = (("r2", 200), ("r4", 400), ("r8", 800))
S1_EB_DECISIONS = (
    "TECHNICALLY_INVALID",
    "NO_CONFIRMED_REFINED_EFFECT",
    "CONFIRMED_REFINED_WORLD_FORMATION_AND_TRANSFER_EFFECT",
    "NUMERICALLY_UNDECIDABLE",
)
S1_EB_DECISION_RULES = (
    "required-control-failure=>TECHNICALLY_INVALID",
    "all-r2-r4-r8-state-and-probe-signals-bit-zero=>NO_CONFIRMED_REFINED_EFFECT",
    "r8-state-and-both-probe-signals>8x-matching-r4-r8-residual-and-r4-r8-residual<=r2-r4-residual=>CONFIRMED_REFINED_WORLD_FORMATION_AND_TRANSFER_EFFECT",
    "otherwise=>NUMERICALLY_UNDECIDABLE",
)


def _digest(value: object) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class E1RefinedConfirmationContract:
    contract_id: str
    corridor_status: str
    upstream_report_path: str
    upstream_report_sha256: str
    upstream_result_sha256: str
    upstream_decision: str
    confirmation_question: str
    source_policy: str
    mechanism_policy: str
    threshold_policy: str
    refinements: tuple[tuple[str, int], ...]
    history_step_counts: tuple[tuple[str, int], ...]
    probe_step_counts: tuple[tuple[str, int], ...]
    required_controls: tuple[str, ...]
    decisions: tuple[str, ...]
    decision_rules: tuple[str, ...]
    numerical_signal_margin: float
    report_path: str
    attempt_path: str
    lock_path: str
    planner_implementation_permitted: bool
    runner_implementation_permitted: bool
    execution_permitted: bool
    execution_started: bool
    s1_ea6_rerun_permitted: bool
    posthoc_threshold_change_permitted: bool
    memory_claim_permitted: bool
    ai_claim_permitted: bool

    def __post_init__(self) -> None:
        if (
            self.contract_id != "e1.refined-confirmation.s1eb.v1"
            or self.corridor_status != "PREREGISTERED_NOT_IMPLEMENTED"
            or self.upstream_report_sha256 != S1_EA6_REPORT_SHA256
            or self.upstream_result_sha256 != S1_EA6_RESULT_SHA256
            or self.upstream_decision != "NUMERICALLY_UNDECIDABLE"
        ):
            raise E1RefinedConfirmationContractError(
                "S1-EB identity or upstream boundary changed"
            )
        if (
            self.confirmation_question
            != "does-r8-separate-both-probe-signals-from-the-preregistered-numerical-residual"
            or self.source_policy
            != "same-bound-canonical-av-source-new-independent-one-shot-artifact"
            or self.mechanism_policy
            != "bit-identical-e1-formation-probe-ablation-and-fixed-adapter-mechanisms"
            or self.threshold_policy != "unchanged-strict-greater-than-eight-times-fine-residual"
        ):
            raise E1RefinedConfirmationContractError(
                "S1-EB question, source, mechanism, or threshold changed"
            )
        if (
            self.refinements != S1_EB_REFINEMENTS
            or self.history_step_counts != S1_EB_HISTORY_STEP_COUNTS
            or self.probe_step_counts != S1_EB_PROBE_STEP_COUNTS
            or self.required_controls != S1_DS_REQUIRED_CONTROLS
            or self.decisions != S1_EB_DECISIONS
            or self.decision_rules != S1_EB_DECISION_RULES
            or self.numerical_signal_margin != 8.0
        ):
            raise E1RefinedConfirmationContractError(
                "S1-EB evidence or decision inventory changed"
            )
        targets = tuple(Path(value) for value in (
            self.report_path, self.attempt_path, self.lock_path
        ))
        if (
            len(set(targets)) != 3
            or len({item.parent for item in targets}) != 1
            or any(item.exists() for item in targets)
            or Path(self.upstream_report_path) in targets
        ):
            raise E1RefinedConfirmationContractError(
                "S1-EB one-shot paths are not distinct and free"
            )
        if (
            self.planner_implementation_permitted is not True
            or self.runner_implementation_permitted is not False
        ):
            raise E1RefinedConfirmationContractError(
                "S1-EB may implement only the planner next"
            )
        if any(
            value is not False
            for value in (
                self.execution_permitted,
                self.execution_started,
                self.s1_ea6_rerun_permitted,
                self.posthoc_threshold_change_permitted,
                self.memory_claim_permitted,
                self.ai_claim_permitted,
            )
        ):
            raise E1RefinedConfirmationContractError(
                "S1-EB cannot execute, rerun S1-EA6, or permit claims"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


def build_e1_refined_confirmation_contract(
    report_directory: Path,
    upstream_report_path: Path,
) -> E1RefinedConfirmationContract:
    """Preregister S1-EB without constructing a source, plan, field, or state."""

    directory = Path(report_directory).resolve()
    upstream = Path(upstream_report_path).resolve()
    if not directory.is_dir():
        raise E1RefinedConfirmationContractError(
            "S1-EB report directory does not exist"
        )
    audit = audit_e1_canonical_refined_chain_result(upstream)
    report = directory / "e1_refined_confirmation_s1eb_once_v1.json"
    attempt = directory / "e1_refined_confirmation_s1eb_once_v1.attempt.json"
    lock = directory / "e1_refined_confirmation_s1eb_once_v1.lock"
    return E1RefinedConfirmationContract(
        contract_id="e1.refined-confirmation.s1eb.v1",
        corridor_status="PREREGISTERED_NOT_IMPLEMENTED",
        upstream_report_path=str(upstream),
        upstream_report_sha256=audit.report_sha256,
        upstream_result_sha256=audit.result_sha256,
        upstream_decision=audit.technical_decision,
        confirmation_question=(
            "does-r8-separate-both-probe-signals-from-the-preregistered-numerical-residual"
        ),
        source_policy="same-bound-canonical-av-source-new-independent-one-shot-artifact",
        mechanism_policy=(
            "bit-identical-e1-formation-probe-ablation-and-fixed-adapter-mechanisms"
        ),
        threshold_policy=(
            "unchanged-strict-greater-than-eight-times-fine-residual"
        ),
        refinements=S1_EB_REFINEMENTS,
        history_step_counts=S1_EB_HISTORY_STEP_COUNTS,
        probe_step_counts=S1_EB_PROBE_STEP_COUNTS,
        required_controls=S1_DS_REQUIRED_CONTROLS,
        decisions=S1_EB_DECISIONS,
        decision_rules=S1_EB_DECISION_RULES,
        numerical_signal_margin=8.0,
        report_path=str(report),
        attempt_path=str(attempt),
        lock_path=str(lock),
        planner_implementation_permitted=True,
        runner_implementation_permitted=False,
        execution_permitted=False,
        execution_started=False,
        s1_ea6_rerun_permitted=False,
        posthoc_threshold_change_permitted=False,
        memory_claim_permitted=False,
        ai_claim_permitted=False,
    )
