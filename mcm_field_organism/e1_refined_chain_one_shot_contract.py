"""Private S1-DW one-shot contract for the refined formation-transfer chain."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from .e1_canonical_refinement_preflight import (
    prepare_e1_canonical_refinement_preflight,
)
from .e1_refined_world_formation_contract import (
    S1_DS_DECISIONS,
    S1_DS_DECISION_RULES,
    S1_DS_METRICS,
    S1_DS_REQUIRED_CONTROLS,
    S1_DS_REFINEMENTS,
    build_e1_refined_world_formation_contract,
)


class E1RefinedChainOneShotContractError(ValueError):
    """Raised when S1-DW bindings changed or an output path was used."""


S1_DS_CONTRACT_DIGEST = (
    "de996ac492af3808499b222687ac92d6f2110eda34743cc65d623ee3d924cbd7"
)
S1_DU_PREFLIGHT_DIGEST = (
    "00b7df0cf1d98286e0f5f75d8a0b27b7176f152bc7065e0320421d521e29a032"
)
S1_DV_IMPLEMENTATION_DIGEST = (
    "df4578fbb5f9d2861a39015a378f5e72174f7035d99ed939596a7e9ed77aca9c"
)
S1_DL_TRANSFER_IMPLEMENTATION_DIGEST = (
    "86dced5ddda7634d455fcbc50aca75eb6f64ef9b04f7f690c611edb997f2bdb6"
)
S1_DW_REPORT_FIELDS = (
    "execution_id",
    "one_shot_contract_digest",
    "s1_ds_contract_digest",
    "s1_du_preflight_digest",
    "formation_implementation_digest",
    "transfer_implementation_digest",
    "source_digests",
    "probe_digest",
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
        raise E1RefinedChainOneShotContractError(
            f"S1-DW implementation is missing: {name}"
        )
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def current_s1_dv_implementation_digest() -> str:
    return _normalized_source_digest("e1_refined_formation_runner.py")


def current_s1_dl_transfer_implementation_digest() -> str:
    return _normalized_source_digest("e1_frozen_state_transfer.py")


def s1_dw_configuration_digest() -> str:
    """Bind the complete future result surface without running a role."""

    return _digest(
        {
            "clock_id": "organism.e1.av-history",
            "history_horizon_ticks": [0, 2_000_000],
            "probe_horizon_ticks": [0, 1_000_000],
            "ticks_per_second": 1_000_000.0,
            "history_support_count": 220,
            "probe_support_count": 110,
            "field_node_count": 84,
            "edge_count": 145,
            "refinements": S1_DS_REFINEMENTS,
            "formation_arms": [
                "ab",
                "ba",
                "ab_identity",
                "ab_formation_ablated",
                "ba_formation_ablated",
            ],
            "probe_arms_per_refinement": [
                "p0",
                "ab_active",
                "ba_active",
                "ab_probe_ablated",
                "ba_probe_ablated",
                "ab_fixed",
                "ba_fixed",
            ],
            "metrics": S1_DS_METRICS,
            "controls": S1_DS_REQUIRED_CONTROLS,
            "decisions": S1_DS_DECISIONS,
            "decision_rules": S1_DS_DECISION_RULES,
            "numerical_signal_margin": 8.0,
            "history_backreaction_enabled": False,
            "formed_state_frozen_during_probe": True,
            "dissipation": None,
        }
    )


@dataclass(frozen=True, slots=True)
class E1RefinedChainOneShotContract:
    execution_id: str
    upstream_report_path: str
    report_path: str
    attempt_path: str
    lock_path: str
    upstream_report_sha256: str
    s1_ds_contract_digest: str
    s1_du_preflight_digest: str
    formation_implementation_digest: str
    transfer_implementation_digest: str
    history_ab_digest: str
    history_ba_digest: str
    permutation_digest: str
    probe_digest: str
    configuration_digest: str
    refinements: tuple[tuple[str, int], ...]
    metrics: tuple[str, ...]
    required_controls: tuple[str, ...]
    technical_decisions: tuple[str, ...]
    decision_rules: tuple[str, ...]
    report_fields: tuple[str, ...]
    result_digest_method: str
    atomic_publish_method: str
    failure_policy: str
    execution_permitted: bool
    execution_started: bool
    canonical_producer_bound: bool
    canonical_executor_bound: bool
    old_history_rerun_permitted: bool
    old_transfer_rerun_permitted: bool
    memory_claim_permitted: bool
    semantic_claim_permitted: bool
    organization_claim_permitted: bool
    topology_claim_permitted: bool
    self_regulation_claim_permitted: bool
    ai_claim_permitted: bool

    def __post_init__(self) -> None:
        if self.execution_id != "e1.refined-formation-transfer.s1ea.once.v1":
            raise E1RefinedChainOneShotContractError(
                "S1-DW execution identity changed"
            )
        if (
            self.s1_ds_contract_digest != S1_DS_CONTRACT_DIGEST
            or self.s1_du_preflight_digest != S1_DU_PREFLIGHT_DIGEST
        ):
            raise E1RefinedChainOneShotContractError(
                "S1-DS or S1-DU binding changed"
            )
        if (
            self.formation_implementation_digest
            != S1_DV_IMPLEMENTATION_DIGEST
            or self.formation_implementation_digest
            != current_s1_dv_implementation_digest()
            or self.transfer_implementation_digest
            != S1_DL_TRANSFER_IMPLEMENTATION_DIGEST
            or self.transfer_implementation_digest
            != current_s1_dl_transfer_implementation_digest()
        ):
            raise E1RefinedChainOneShotContractError(
                "S1-DV formation or S1-DL transfer implementation changed"
            )
        if self.configuration_digest != s1_dw_configuration_digest():
            raise E1RefinedChainOneShotContractError(
                "S1-DW execution configuration changed"
            )
        if (
            self.refinements != S1_DS_REFINEMENTS
            or self.metrics != S1_DS_METRICS
            or self.required_controls != S1_DS_REQUIRED_CONTROLS
            or self.technical_decisions != S1_DS_DECISIONS
            or self.decision_rules != S1_DS_DECISION_RULES
            or self.report_fields != S1_DW_REPORT_FIELDS
        ):
            raise E1RefinedChainOneShotContractError(
                "S1-DW evidence or report inventory changed"
            )
        if (
            self.result_digest_method != "sha256-canonical-json-result"
            or self.atomic_publish_method != "same-directory-exclusive-link"
            or self.failure_policy
            != "retain-attempt-marker-no-automatic-retry"
        ):
            raise E1RefinedChainOneShotContractError(
                "S1-DW persistence contract changed"
            )
        if (
            self.execution_permitted is not False
            or self.execution_started is not False
            or self.canonical_producer_bound is not False
            or self.canonical_executor_bound is not False
        ):
            raise E1RefinedChainOneShotContractError(
                "S1-DW cannot release execution before producer and executor binding"
            )
        forbidden = (
            self.old_history_rerun_permitted,
            self.old_transfer_rerun_permitted,
            self.memory_claim_permitted,
            self.semantic_claim_permitted,
            self.organization_claim_permitted,
            self.topology_claim_permitted,
            self.self_regulation_claim_permitted,
            self.ai_claim_permitted,
        )
        if any(value is not False for value in forbidden):
            raise E1RefinedChainOneShotContractError(
                "S1-DW cannot release reruns or strong claims"
            )
        targets = tuple(Path(value) for value in self._target_path_values())
        if len(set(targets)) != 3 or len({path.parent for path in targets}) != 1:
            raise E1RefinedChainOneShotContractError(
                "S1-DW one-shot paths must be distinct siblings"
            )
        upstream = Path(self.upstream_report_path)
        if upstream in targets or not upstream.is_file():
            raise E1RefinedChainOneShotContractError(
                "S1-DW upstream report binding is invalid"
            )
        for role in (
            "upstream_report_sha256",
            "history_ab_digest",
            "history_ba_digest",
            "permutation_digest",
            "probe_digest",
        ):
            value = getattr(self, role)
            if len(value) != 64 or any(
                char not in "0123456789abcdef" for char in value
            ):
                raise E1RefinedChainOneShotContractError(
                    f"{role} is not SHA-256"
                )

    def _target_path_values(self) -> tuple[str, str, str]:
        return self.report_path, self.attempt_path, self.lock_path

    def digest(self) -> str:
        return _digest(
            {name: getattr(self, name) for name in self.__dataclass_fields__}
        )


def prepare_e1_refined_chain_one_shot_contract(
    report_directory: Path,
    upstream_report_path: Path,
) -> E1RefinedChainOneShotContract:
    """Register unused result paths without running formation or transfer."""

    directory = Path(report_directory).resolve()
    upstream = Path(upstream_report_path).resolve()
    if not directory.is_dir():
        raise E1RefinedChainOneShotContractError(
            "S1-DW report directory does not exist"
        )
    formation = build_e1_refined_world_formation_contract(upstream)
    preflight = prepare_e1_canonical_refinement_preflight(upstream)
    if formation.digest() != S1_DS_CONTRACT_DIGEST:
        raise E1RefinedChainOneShotContractError(
            "published S1-DS contract changed"
        )
    if preflight.digest() != S1_DU_PREFLIGHT_DIGEST:
        raise E1RefinedChainOneShotContractError(
            "published S1-DU preflight changed"
        )
    report = directory / "e1_refined_formation_transfer_s1ea_once_v1.json"
    attempt = directory / (
        "e1_refined_formation_transfer_s1ea_once_v1.attempt.json"
    )
    lock = directory / "e1_refined_formation_transfer_s1ea_once_v1.lock"
    if any(path.exists() for path in (report, attempt, lock)):
        raise E1RefinedChainOneShotContractError(
            "S1-DW one-shot path is already used"
        )
    return E1RefinedChainOneShotContract(
        execution_id="e1.refined-formation-transfer.s1ea.once.v1",
        upstream_report_path=str(upstream),
        report_path=str(report),
        attempt_path=str(attempt),
        lock_path=str(lock),
        upstream_report_sha256=hashlib.sha256(upstream.read_bytes()).hexdigest(),
        s1_ds_contract_digest=formation.digest(),
        s1_du_preflight_digest=preflight.digest(),
        formation_implementation_digest=current_s1_dv_implementation_digest(),
        transfer_implementation_digest=(
            current_s1_dl_transfer_implementation_digest()
        ),
        history_ab_digest=formation.history_ab_digest,
        history_ba_digest=formation.history_ba_digest,
        permutation_digest=formation.permutation_digest,
        probe_digest=formation.probe_digest,
        configuration_digest=s1_dw_configuration_digest(),
        refinements=S1_DS_REFINEMENTS,
        metrics=S1_DS_METRICS,
        required_controls=S1_DS_REQUIRED_CONTROLS,
        technical_decisions=S1_DS_DECISIONS,
        decision_rules=S1_DS_DECISION_RULES,
        report_fields=S1_DW_REPORT_FIELDS,
        result_digest_method="sha256-canonical-json-result",
        atomic_publish_method="same-directory-exclusive-link",
        failure_policy="retain-attempt-marker-no-automatic-retry",
        execution_permitted=False,
        execution_started=False,
        canonical_producer_bound=False,
        canonical_executor_bound=False,
        old_history_rerun_permitted=False,
        old_transfer_rerun_permitted=False,
        memory_claim_permitted=False,
        semantic_claim_permitted=False,
        organization_claim_permitted=False,
        topology_claim_permitted=False,
        self_regulation_claim_permitted=False,
        ai_claim_permitted=False,
    )
