"""Private S1-EC3 path-independent research corridor and run contract."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from .e1_canonical_refined_chain_result_audit import (
    S1_EA6_REPORT_SHA256,
    S1_EA6_RESULT_SHA256,
    audit_e1_canonical_refined_chain_result,
)
from .e1_confirmation_refinement_planner import S1_EB_CONTRACT_DIGEST
from .e1_refined_confirmation_contract import (
    S1_EB_DECISIONS,
    S1_EB_DECISION_RULES,
    S1_EB_HISTORY_STEP_COUNTS,
    S1_EB_PROBE_STEP_COUNTS,
    S1_EB_REFINEMENTS,
    _digest,
)
from .e1_refined_world_formation_contract import S1_DS_REQUIRED_CONTROLS


class E1ConfirmationResearchCorridorError(ValueError):
    """Raised when S1-EC3 mixes research structure with run state."""


S1_EC3_DESCRIPTOR_ID = "e1.confirmation-research-corridor.s1ec3.v1"
S1_EC3_RUN_ID = "e1.confirmation-run-contract.s1ec3.synthetic.v1"
S1_EC3_REPORT = "e1_confirmation_s1ec3_synthetic_once_v1.json"
S1_EC3_ATTEMPT = "e1_confirmation_s1ec3_synthetic_once_v1.attempt.json"
S1_EC3_LOCK = "e1_confirmation_s1ec3_synthetic_once_v1.lock"


@dataclass(frozen=True, slots=True)
class E1ConfirmationResearchCorridorDescriptor:
    descriptor_id: str
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
    legacy_planner_contract_digest: str
    memory_claim_permitted: bool
    ai_claim_permitted: bool

    def __post_init__(self) -> None:
        if (
            self.descriptor_id != S1_EC3_DESCRIPTOR_ID
            or self.upstream_report_sha256 != S1_EA6_REPORT_SHA256
            or self.upstream_result_sha256 != S1_EA6_RESULT_SHA256
            or self.upstream_decision != "NUMERICALLY_UNDECIDABLE"
            or self.legacy_planner_contract_digest != S1_EB_CONTRACT_DIGEST
        ):
            raise E1ConfirmationResearchCorridorError(
                "S1-EC3 descriptor identity or upstream boundary changed"
            )
        if (
            self.confirmation_question
            != "does-r8-separate-both-probe-signals-from-the-preregistered-numerical-residual"
            or self.source_policy
            != "same-bound-canonical-av-source-new-independent-one-shot-artifact"
            or self.mechanism_policy
            != "bit-identical-e1-formation-probe-ablation-and-fixed-adapter-mechanisms"
            or self.threshold_policy
            != "unchanged-strict-greater-than-eight-times-fine-residual"
        ):
            raise E1ConfirmationResearchCorridorError(
                "S1-EC3 question, source, mechanism, or threshold changed"
            )
        if (
            self.refinements != S1_EB_REFINEMENTS
            or self.history_step_counts != S1_EB_HISTORY_STEP_COUNTS
            or self.probe_step_counts != S1_EB_PROBE_STEP_COUNTS
            or self.required_controls != S1_DS_REQUIRED_CONTROLS
            or self.decisions != S1_EB_DECISIONS
            or self.decision_rules != S1_EB_DECISION_RULES
            or self.numerical_signal_margin != 8.0
            or self.memory_claim_permitted is not False
            or self.ai_claim_permitted is not False
        ):
            raise E1ConfirmationResearchCorridorError(
                "S1-EC3 evidence inventory or claim boundary changed"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


@dataclass(frozen=True, slots=True)
class E1ConfirmationSyntheticRunContract:
    execution_id: str
    research_descriptor_digest: str
    report_path: str
    attempt_path: str
    lock_path: str
    failure_policy: str
    synthetic_only: bool
    canonical_execution_permitted: bool
    execution_started: bool
    claims_permitted: bool

    def __post_init__(self) -> None:
        paths = tuple(
            Path(value) for value in (self.report_path, self.attempt_path, self.lock_path)
        )
        if (
            self.execution_id != S1_EC3_RUN_ID
            or len(self.research_descriptor_digest) != 64
            or any(
                char not in "0123456789abcdef"
                for char in self.research_descriptor_digest
            )
            or len(set(paths)) != 3
            or len({path.parent for path in paths}) != 1
            or tuple(path.name for path in paths)
            != (S1_EC3_REPORT, S1_EC3_ATTEMPT, S1_EC3_LOCK)
            or any(path.exists() for path in paths)
            or self.failure_policy
            != "retain-attempt-marker-no-automatic-retry"
            or self.synthetic_only is not True
            or self.canonical_execution_permitted is not False
            or self.execution_started is not False
            or self.claims_permitted is not False
        ):
            raise E1ConfirmationResearchCorridorError(
                "S1-EC3 synthetic run contract changed or paths are used"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


def build_e1_confirmation_research_corridor(
    upstream_report_path: Path,
) -> E1ConfirmationResearchCorridorDescriptor:
    """Bind research conditions without carrying any target path or run gate."""

    audit = audit_e1_canonical_refined_chain_result(
        Path(upstream_report_path).resolve()
    )
    return E1ConfirmationResearchCorridorDescriptor(
        descriptor_id=S1_EC3_DESCRIPTOR_ID,
        upstream_report_sha256=audit.report_sha256,
        upstream_result_sha256=audit.result_sha256,
        upstream_decision=audit.technical_decision,
        confirmation_question=(
            "does-r8-separate-both-probe-signals-from-the-preregistered-numerical-residual"
        ),
        source_policy=(
            "same-bound-canonical-av-source-new-independent-one-shot-artifact"
        ),
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
        legacy_planner_contract_digest=S1_EB_CONTRACT_DIGEST,
        memory_claim_permitted=False,
        ai_claim_permitted=False,
    )


def prepare_e1_confirmation_synthetic_run_contract(
    descriptor: E1ConfirmationResearchCorridorDescriptor,
    synthetic_directory: Path,
) -> E1ConfirmationSyntheticRunContract:
    """Bind separate temporary Exactly-once paths without starting a run."""

    if not isinstance(descriptor, E1ConfirmationResearchCorridorDescriptor):
        raise E1ConfirmationResearchCorridorError(
            "S1-EC3 requires one research corridor descriptor"
        )
    directory = Path(synthetic_directory).resolve()
    if not directory.is_dir() or directory == Path("reports").resolve():
        raise E1ConfirmationResearchCorridorError(
            "S1-EC3 requires an existing synthetic directory outside reports"
        )
    return E1ConfirmationSyntheticRunContract(
        execution_id=S1_EC3_RUN_ID,
        research_descriptor_digest=descriptor.digest(),
        report_path=str(directory / S1_EC3_REPORT),
        attempt_path=str(directory / S1_EC3_ATTEMPT),
        lock_path=str(directory / S1_EC3_LOCK),
        failure_policy="retain-attempt-marker-no-automatic-retry",
        synthetic_only=True,
        canonical_execution_permitted=False,
        execution_started=False,
        claims_permitted=False,
    )
