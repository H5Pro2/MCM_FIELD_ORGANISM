"""Private S1-DS static contract for refined E1 formation from AV contact."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from .e1_av_history_permutation import build_e1_av_history_permutation
from .e1_substrate_milestone_classification import (
    S1_DR_NEXT_STAGE,
    S1_DR_STATUS,
    classify_e1_substrate_milestone,
)


class E1RefinedWorldFormationContractError(ValueError):
    """Raised when the S1-DS formation-evidence boundary changes."""


S1_DR_CLASSIFICATION_DIGEST = (
    "bb8fe7f2137a931b0d0e697226154ea58013fb9b6ae2b6f3e11416b878dfb9df"
)
S1_DS_HISTORY_AB_DIGEST = (
    "a48d3d1620afa82d12dda855bb2ec03de3a57e7a69488d46edba6ec99cbef6d6"
)
S1_DS_HISTORY_BA_DIGEST = (
    "bb1d887f1ff5809964ae8175c7fa661430e8fbc8502f0522a7003d6c6fc3c011"
)
S1_DS_PERMUTATION_DIGEST = (
    "ad509ef23a9394009baddc8185edc5a13f76882ee79e7c31d3b0ec111bfbcc78"
)
S1_DS_PROBE_DIGEST = (
    "c0a9a59fb93996bdfd95247a1f6feec19723aeb36c84bd8bc8a423e677fbea7d"
)
S1_DS_REFINEMENTS = (("r1", 1), ("r2", 2), ("r4", 4))
S1_DS_FORMATION_HISTORIES = ("ab", "ba", "ab_identity")
S1_DS_FORMATION_MODES = (
    "e1_enabled_backreaction_ablated",
    "e1_formation_ablated",
)
S1_DS_METRICS = (
    "d_state",
    "d_total_binding",
    "d_probe_s",
    "d_probe_h",
    "state_refinement_r1_r2",
    "state_refinement_r2_r4",
    "probe_refinement_r1_r2",
    "probe_refinement_r2_r4",
    "identity_residual",
    "formation_ablation_residual",
    "probe_ablation_residual",
    "fixed_adapter_residual",
    "resource_budget_error",
)
S1_DS_REQUIRED_CONTROLS = (
    "all_formation_arms_start_value_identical_and_object_separate",
    "ab_ba_payload_support_slot_mass_and_energy_inventories_identical",
    "all_refinements_preserve_physical_horizon_and_integrated_input",
    "every_source_support_assigned_once_at_every_refinement",
    "ab_identity_replicates_are_bit_exact",
    "formation_ablation_remains_neutral",
    "all_probe_fields_start_value_identical_and_object_separate",
    "all_formed_states_remain_frozen_during_probe",
    "probe_ablation_equals_p0_bit_exact",
    "active_probe_equals_matching_fixed_adapter_bit_exact",
    "public_api_unchanged",
)
S1_DS_DECISIONS = (
    "TECHNICALLY_INVALID",
    "NUMERICALLY_UNDECIDABLE",
    "NO_REFINED_WORLD_FORMATION_EFFECT",
    "REFINED_WORLD_FORMATION_AND_TRANSFER_EFFECT",
)
S1_DS_DECISION_RULES = (
    "required-control-failure=>TECHNICALLY_INVALID",
    "all-r1-r2-r4-state-and-probe-signals-bit-zero=>NO_REFINED_WORLD_FORMATION_EFFECT",
    "fine-state-and-both-probe-signals>8x-matching-fine-residual-and-fine-residual<=coarse-residual=>REFINED_WORLD_FORMATION_AND_TRANSFER_EFFECT",
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


def _frame_payload(item) -> dict[str, object]:
    frame = item.frame
    return {
        "modality_id": frame.modality_id,
        "geometry_id": frame.geometry_id,
        "snapshot_id": frame.snapshot_id,
        "source_clock_id": frame.clock_id,
        "source_start_tick": frame.window_start_tick,
        "source_end_tick": frame.window_end_tick,
        "carrier_ids": list(frame.carrier_ids),
        "values": list(frame.values),
    }


def _first_block_probe_digest(sequences) -> str:
    payload = []
    for sequence in sequences:
        frames = tuple(
            item
            for item in sequence.frames
            if item.field_time.window_end_tick <= 1_000_000
        )
        payload.append(
            {
                "modality_id": sequence.modality_id,
                "geometry_id": sequence.geometry_id,
                "clock_id": sequence.clock_id,
                "frames": [
                    {
                        "frame": _frame_payload(item),
                        "field_time": [
                            item.field_time.clock_id,
                            item.field_time.window_start_tick,
                            item.field_time.window_end_tick,
                        ],
                    }
                    for item in frames
                ],
            }
        )
    return _digest(payload)


@dataclass(frozen=True, slots=True)
class E1RefinedWorldFormationContract:
    contract_id: str
    upstream_status: str
    upstream_next_stage: str
    upstream_classification_digest: str
    history_ab_digest: str
    history_ba_digest: str
    permutation_digest: str
    probe_digest: str
    clock_id: str
    history_start_tick: int
    history_split_tick: int
    history_end_tick: int
    ticks_per_second: float
    auditory_frame_count: int
    visual_frame_count: int
    source_support_count: int
    field_node_count: int
    edge_count: int
    refinements: tuple[tuple[str, int], ...]
    formation_histories: tuple[str, ...]
    formation_modes: tuple[str, ...]
    refinement_method: str
    state_distance_method: str
    field_distance_method: str
    numerical_signal_margin: float
    metrics: tuple[str, ...]
    required_controls: tuple[str, ...]
    decisions: tuple[str, ...]
    decision_rules: tuple[str, ...]
    implementation_permitted: bool
    execution_permitted: bool
    old_history_rerun_permitted: bool
    old_transfer_rerun_permitted: bool
    memory_claim_permitted: bool
    semantic_claim_permitted: bool
    organization_claim_permitted: bool
    topology_claim_permitted: bool
    self_regulation_claim_permitted: bool
    ai_claim_permitted: bool

    def __post_init__(self) -> None:
        if self.contract_id != "e1.refined-world-formation.s1ds.v1":
            raise E1RefinedWorldFormationContractError(
                "S1-DS contract identity changed"
            )
        if (
            self.upstream_status != S1_DR_STATUS
            or self.upstream_next_stage != S1_DR_NEXT_STAGE
            or self.upstream_classification_digest
            != S1_DR_CLASSIFICATION_DIGEST
        ):
            raise E1RefinedWorldFormationContractError(
                "S1-DR classification binding changed"
            )
        if (
            self.history_ab_digest,
            self.history_ba_digest,
            self.permutation_digest,
            self.probe_digest,
        ) != (
            S1_DS_HISTORY_AB_DIGEST,
            S1_DS_HISTORY_BA_DIGEST,
            S1_DS_PERMUTATION_DIGEST,
            S1_DS_PROBE_DIGEST,
        ):
            raise E1RefinedWorldFormationContractError(
                "S1-DS AV source binding changed"
            )
        if (
            self.clock_id != "organism.e1.av-history"
            or (self.history_start_tick, self.history_split_tick, self.history_end_tick)
            != (0, 1_000_000, 2_000_000)
            or self.ticks_per_second != 1_000_000.0
        ):
            raise E1RefinedWorldFormationContractError(
                "S1-DS physical history time changed"
            )
        if (
            self.auditory_frame_count,
            self.visual_frame_count,
            self.source_support_count,
            self.field_node_count,
            self.edge_count,
        ) != (200, 20, 220, 84, 145):
            raise E1RefinedWorldFormationContractError(
                "S1-DS source or geometry inventory changed"
            )
        if (
            self.refinements != S1_DS_REFINEMENTS
            or self.formation_histories != S1_DS_FORMATION_HISTORIES
            or self.formation_modes != S1_DS_FORMATION_MODES
        ):
            raise E1RefinedWorldFormationContractError(
                "S1-DS arm or refinement inventory changed"
            )
        if self.refinement_method != (
            "completion-aligned-equal-substeps-preserve-integrated-local-input"
        ):
            raise E1RefinedWorldFormationContractError(
                "S1-DS refinement method changed"
            )
        if (
            self.state_distance_method != "edge-binding-linf"
            or self.field_distance_method != "ordered-s-h-linf"
            or self.numerical_signal_margin != 8.0
        ):
            raise E1RefinedWorldFormationContractError(
                "S1-DS numerical decision boundary changed"
            )
        if (
            self.metrics != S1_DS_METRICS
            or self.required_controls != S1_DS_REQUIRED_CONTROLS
            or self.decisions != S1_DS_DECISIONS
            or self.decision_rules != S1_DS_DECISION_RULES
        ):
            raise E1RefinedWorldFormationContractError(
                "S1-DS evidence inventory changed"
            )
        if self.implementation_permitted is not True:
            raise E1RefinedWorldFormationContractError(
                "S1-DS must permit only the next implementation"
            )
        forbidden = (
            self.execution_permitted,
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
            raise E1RefinedWorldFormationContractError(
                "S1-DS cannot release an execution, rerun, or strong claim"
            )

    def digest(self) -> str:
        return _digest(
            {name: getattr(self, name) for name in self.__dataclass_fields__}
        )


def build_e1_refined_world_formation_contract(
    transfer_report_path: Path,
) -> E1RefinedWorldFormationContract:
    """Bind S1-DS from static evidence and AV sources without field execution."""

    upstream = classify_e1_substrate_milestone(transfer_report_path)
    if upstream.classification_digest != S1_DR_CLASSIFICATION_DIGEST:
        raise E1RefinedWorldFormationContractError(
            "published S1-DR classification changed"
        )
    source = build_e1_av_history_permutation()
    probe_digest = _first_block_probe_digest(source.history_ab)
    if probe_digest != S1_DS_PROBE_DIGEST:
        raise E1RefinedWorldFormationContractError(
            "S1-DS fixed AV probe digest changed"
        )
    counts = {
        item.modality_id: item.frame_count for item in source.modality_audits
    }
    return E1RefinedWorldFormationContract(
        contract_id="e1.refined-world-formation.s1ds.v1",
        upstream_status=upstream.status,
        upstream_next_stage=upstream.next_stage,
        upstream_classification_digest=upstream.classification_digest,
        history_ab_digest=source.history_ab_digest,
        history_ba_digest=source.history_ba_digest,
        permutation_digest=source.permutation_digest,
        probe_digest=probe_digest,
        clock_id="organism.e1.av-history",
        history_start_tick=0,
        history_split_tick=source.split_tick,
        history_end_tick=2_000_000,
        ticks_per_second=1_000_000.0,
        auditory_frame_count=counts["auditory"],
        visual_frame_count=counts["visual"],
        source_support_count=sum(counts.values()),
        field_node_count=84,
        edge_count=145,
        refinements=S1_DS_REFINEMENTS,
        formation_histories=S1_DS_FORMATION_HISTORIES,
        formation_modes=S1_DS_FORMATION_MODES,
        refinement_method=(
            "completion-aligned-equal-substeps-preserve-integrated-local-input"
        ),
        state_distance_method="edge-binding-linf",
        field_distance_method="ordered-s-h-linf",
        numerical_signal_margin=8.0,
        metrics=S1_DS_METRICS,
        required_controls=S1_DS_REQUIRED_CONTROLS,
        decisions=S1_DS_DECISIONS,
        decision_rules=S1_DS_DECISION_RULES,
        implementation_permitted=True,
        execution_permitted=False,
        old_history_rerun_permitted=False,
        old_transfer_rerun_permitted=False,
        memory_claim_permitted=False,
        semantic_claim_permitted=False,
        organization_claim_permitted=False,
        topology_claim_permitted=False,
        self_regulation_claim_permitted=False,
        ai_claim_permitted=False,
    )
