"""Private S1-EB4 static contract for the complete confirmation chain."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

from .e1_canonical_confirmation_preflight import (
    prepare_e1_canonical_confirmation_preflight,
)
from .e1_refined_confirmation_contract import (
    S1_EB_DECISIONS,
    S1_EB_DECISION_RULES,
    S1_EB_HISTORY_STEP_COUNTS,
    S1_EB_PROBE_STEP_COUNTS,
    S1_EB_REFINEMENTS,
    build_e1_refined_confirmation_contract,
)
from .e1_refined_world_formation_contract import S1_DS_REQUIRED_CONTROLS


class E1ConfirmationChainContractError(ValueError):
    """Raised when an S1-EB4 binding or execution boundary changed."""


S1_EB_CONTRACT_DIGEST = (
    "bccf552b7ea69cc083cf65ac0a7d3faacfe7939ff8c7d13c4614f1cf42d06fb4"
)
S1_EB2_PREFLIGHT_DIGEST = (
    "e657636e86cea6eabef638597ed22e3e0bc6894bbdc9f9fb96c001d3c31a0372"
)
S1_EB_IMPLEMENTATION_DIGESTS = (
    (
        "contract",
        "d6e7501b7791c489398a12171eb9ae530f210427935a039bea8f12d9423ed5dd",
    ),
    (
        "planner",
        "cf50c5757e420a6ad8c84b248b41ccf2028c90c7a1116a8f4e3b377453215731",
    ),
    (
        "preflight",
        "ac7d0521c79eb0c2154cca4d62c2c88783cd57624d922e7835e1d76c9d2082eb",
    ),
    (
        "formation",
        "7b4fe5870bf8476b1e0367a6f8a7ad52ff026065d9945144aa3f27339663febd",
    ),
    (
        "transfer",
        "86dced5ddda7634d455fcbc50aca75eb6f64ef9b04f7f690c611edb997f2bdb6",
    ),
    (
        "probe",
        "c48ecf2322b82c7cf215eeefc4f12083fc7be9b921906d1c5b1ebccadd1516db",
    ),
)
S1_EB_IMPLEMENTATION_FILES = (
    ("contract", "e1_refined_confirmation_contract.py"),
    ("planner", "e1_confirmation_refinement_planner.py"),
    ("preflight", "e1_canonical_confirmation_preflight.py"),
    ("formation", "e1_confirmation_formation_runner.py"),
    ("transfer", "e1_frozen_state_transfer.py"),
    ("probe", "e1_refined_seven_arm_probe_runner.py"),
)
S1_EB4_FORMATION_ARMS = (
    "ab",
    "ba",
    "ab_identity",
    "ab_formation_ablated",
    "ba_formation_ablated",
)
S1_EB4_PROBE_ARMS = (
    "p0",
    "ab_active",
    "ba_active",
    "ab_probe_ablated",
    "ba_probe_ablated",
    "ab_fixed",
    "ba_fixed",
)
S1_EB4_METRICS = (
    "d_state",
    "d_total_binding",
    "d_probe_s",
    "d_probe_h",
    "state_refinement_r2_r4",
    "state_refinement_r4_r8",
    "probe_refinement_r2_r4",
    "probe_refinement_r4_r8",
    "identity_residual",
    "formation_ablation_residual",
    "probe_ablation_residual",
    "fixed_adapter_residual",
    "resource_budget_error",
)
S1_EB4_REPORT_FIELDS = (
    "execution_id",
    "confirmation_contract_digest",
    "canonical_preflight_digest",
    "implementation_digests",
    "source_digests",
    "plan_digests",
    "refinement_result_digests",
    "result_digest",
    "technical_decision",
    "metrics",
    "controls",
    "result",
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


def _normalized_source_digest(name: str) -> str:
    path = Path(__file__).with_name(name)
    if not path.is_file():
        raise E1ConfirmationChainContractError(
            f"S1-EB4 implementation is missing: {name}"
        )
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def current_s1_eb_implementation_digests() -> tuple[tuple[str, str], ...]:
    return tuple(
        (role, _normalized_source_digest(name))
        for role, name in S1_EB_IMPLEMENTATION_FILES
    )


def s1_eb4_configuration_digest() -> str:
    """Bind the future confirmation result surface without execution."""

    return _digest(
        {
            "clock_id": "organism.e1.av-history",
            "history_horizon_ticks": (0, 2_000_000),
            "probe_horizon_ticks": (0, 1_000_000),
            "ticks_per_second": 1_000_000.0,
            "history_support_count": 220,
            "probe_support_count": 110,
            "history_completion_count": 200,
            "probe_completion_count": 100,
            "field_node_count": 84,
            "edge_count": 145,
            "refinements": S1_EB_REFINEMENTS,
            "history_step_counts": S1_EB_HISTORY_STEP_COUNTS,
            "probe_step_counts": S1_EB_PROBE_STEP_COUNTS,
            "formation_arms": S1_EB4_FORMATION_ARMS,
            "probe_arms": S1_EB4_PROBE_ARMS,
            "metrics": S1_EB4_METRICS,
            "controls": S1_DS_REQUIRED_CONTROLS,
            "decisions": S1_EB_DECISIONS,
            "decision_rules": S1_EB_DECISION_RULES,
            "numerical_signal_margin": 8.0,
            "history_backreaction_enabled": False,
            "formed_state_frozen_during_probe": True,
            "posthoc_threshold_change_permitted": False,
        }
    )


@dataclass(frozen=True, slots=True)
class E1ConfirmationChainContract:
    execution_id: str
    upstream_report_path: str
    report_path: str
    attempt_path: str
    lock_path: str
    upstream_report_sha256: str
    upstream_result_sha256: str
    confirmation_contract_digest: str
    canonical_preflight_digest: str
    implementation_digests: tuple[tuple[str, str], ...]
    history_ab_digest: str
    history_ba_digest: str
    permutation_digest: str
    probe_digest: str
    ab_plan_digest: str
    ba_plan_digest: str
    probe_plan_digest: str
    configuration_digest: str
    refinements: tuple[tuple[str, int], ...]
    history_step_counts: tuple[tuple[str, int], ...]
    probe_step_counts: tuple[tuple[str, int], ...]
    formation_arms: tuple[str, ...]
    probe_arms: tuple[str, ...]
    metrics: tuple[str, ...]
    required_controls: tuple[str, ...]
    technical_decisions: tuple[str, ...]
    decision_rules: tuple[str, ...]
    report_fields: tuple[str, ...]
    result_digest_method: str
    atomic_publish_method: str
    failure_policy: str
    canonical_producer_bound: bool
    canonical_executor_bound: bool
    execution_permitted: bool
    execution_started: bool
    s1_ea6_rerun_permitted: bool
    posthoc_threshold_change_permitted: bool
    memory_claim_permitted: bool
    semantic_claim_permitted: bool
    organization_claim_permitted: bool
    topology_claim_permitted: bool
    self_regulation_claim_permitted: bool
    ai_claim_permitted: bool

    def __post_init__(self) -> None:
        if self.execution_id != "e1.refined-confirmation.s1eb.once.v1":
            raise E1ConfirmationChainContractError(
                "S1-EB4 execution identity changed"
            )
        if (
            self.confirmation_contract_digest != S1_EB_CONTRACT_DIGEST
            or self.canonical_preflight_digest != S1_EB2_PREFLIGHT_DIGEST
        ):
            raise E1ConfirmationChainContractError(
                "S1-EB or S1-EB2 binding changed"
            )
        if (
            self.implementation_digests != S1_EB_IMPLEMENTATION_DIGESTS
            or self.implementation_digests
            != current_s1_eb_implementation_digests()
        ):
            raise E1ConfirmationChainContractError(
                "S1-EB implementation binding changed"
            )
        if self.configuration_digest != s1_eb4_configuration_digest():
            raise E1ConfirmationChainContractError(
                "S1-EB4 execution configuration changed"
            )
        if (
            self.refinements != S1_EB_REFINEMENTS
            or self.history_step_counts != S1_EB_HISTORY_STEP_COUNTS
            or self.probe_step_counts != S1_EB_PROBE_STEP_COUNTS
            or self.formation_arms != S1_EB4_FORMATION_ARMS
            or self.probe_arms != S1_EB4_PROBE_ARMS
            or self.metrics != S1_EB4_METRICS
            or self.required_controls != S1_DS_REQUIRED_CONTROLS
            or self.technical_decisions != S1_EB_DECISIONS
            or self.decision_rules != S1_EB_DECISION_RULES
            or self.report_fields != S1_EB4_REPORT_FIELDS
        ):
            raise E1ConfirmationChainContractError(
                "S1-EB4 evidence or report inventory changed"
            )
        if (
            self.result_digest_method != "sha256-canonical-json-result"
            or self.atomic_publish_method != "same-directory-exclusive-link"
            or self.failure_policy != "retain-attempt-marker-no-automatic-retry"
        ):
            raise E1ConfirmationChainContractError(
                "S1-EB4 persistence contract changed"
            )
        if any(
            value is not False
            for value in (
                self.canonical_producer_bound,
                self.canonical_executor_bound,
                self.execution_permitted,
                self.execution_started,
                self.s1_ea6_rerun_permitted,
                self.posthoc_threshold_change_permitted,
                self.memory_claim_permitted,
                self.semantic_claim_permitted,
                self.organization_claim_permitted,
                self.topology_claim_permitted,
                self.self_regulation_claim_permitted,
                self.ai_claim_permitted,
            )
        ):
            raise E1ConfirmationChainContractError(
                "S1-EB4 cannot release execution, reruns, tuning, or claims"
            )
        targets = tuple(Path(value) for value in self._target_path_values())
        if (
            len(set(targets)) != 3
            or len({item.parent for item in targets}) != 1
            or any(item.exists() for item in targets)
            or Path(self.upstream_report_path) in targets
        ):
            raise E1ConfirmationChainContractError(
                "S1-EB4 one-shot paths are not distinct and free"
            )
        for role in (
            "upstream_report_sha256",
            "upstream_result_sha256",
            "history_ab_digest",
            "history_ba_digest",
            "permutation_digest",
            "probe_digest",
            "ab_plan_digest",
            "ba_plan_digest",
            "probe_plan_digest",
        ):
            value = getattr(self, role)
            if len(value) != 64 or any(
                char not in "0123456789abcdef" for char in value
            ):
                raise E1ConfirmationChainContractError(
                    f"{role} is not SHA-256"
                )

    def _target_path_values(self) -> tuple[str, str, str]:
        return self.report_path, self.attempt_path, self.lock_path

    def digest(self) -> str:
        return _digest(asdict(self))


def prepare_e1_confirmation_chain_contract(
    report_directory: Path,
    upstream_report_path: Path,
) -> E1ConfirmationChainContract:
    """Bind the complete S1-EB chain without running any chain role."""

    contract = build_e1_refined_confirmation_contract(
        report_directory, upstream_report_path
    )
    preflight = prepare_e1_canonical_confirmation_preflight(
        report_directory, upstream_report_path
    )
    preflight_digest = _digest(asdict(preflight))
    if contract.digest() != S1_EB_CONTRACT_DIGEST:
        raise E1ConfirmationChainContractError(
            "published S1-EB contract changed"
        )
    if preflight_digest != S1_EB2_PREFLIGHT_DIGEST:
        raise E1ConfirmationChainContractError(
            "published S1-EB2 preflight changed"
        )
    return E1ConfirmationChainContract(
        execution_id="e1.refined-confirmation.s1eb.once.v1",
        upstream_report_path=contract.upstream_report_path,
        report_path=contract.report_path,
        attempt_path=contract.attempt_path,
        lock_path=contract.lock_path,
        upstream_report_sha256=contract.upstream_report_sha256,
        upstream_result_sha256=contract.upstream_result_sha256,
        confirmation_contract_digest=contract.digest(),
        canonical_preflight_digest=preflight_digest,
        implementation_digests=current_s1_eb_implementation_digests(),
        history_ab_digest=preflight.history_ab_digest,
        history_ba_digest=preflight.history_ba_digest,
        permutation_digest=preflight.permutation_digest,
        probe_digest=preflight.probe_digest,
        ab_plan_digest=preflight.ab_plan_digest,
        ba_plan_digest=preflight.ba_plan_digest,
        probe_plan_digest=preflight.probe_plan_digest,
        configuration_digest=s1_eb4_configuration_digest(),
        refinements=contract.refinements,
        history_step_counts=contract.history_step_counts,
        probe_step_counts=contract.probe_step_counts,
        formation_arms=S1_EB4_FORMATION_ARMS,
        probe_arms=S1_EB4_PROBE_ARMS,
        metrics=S1_EB4_METRICS,
        required_controls=contract.required_controls,
        technical_decisions=contract.decisions,
        decision_rules=contract.decision_rules,
        report_fields=S1_EB4_REPORT_FIELDS,
        result_digest_method="sha256-canonical-json-result",
        atomic_publish_method="same-directory-exclusive-link",
        failure_policy="retain-attempt-marker-no-automatic-retry",
        canonical_producer_bound=False,
        canonical_executor_bound=False,
        execution_permitted=False,
        execution_started=False,
        s1_ea6_rerun_permitted=False,
        posthoc_threshold_change_permitted=False,
        memory_claim_permitted=False,
        semantic_claim_permitted=False,
        organization_claim_permitted=False,
        topology_claim_permitted=False,
        self_regulation_claim_permitted=False,
        ai_claim_permitted=False,
    )
