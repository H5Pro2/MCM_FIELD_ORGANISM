"""Private S1-DY canonical producer binding for the refined E1 chain."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from .audio_video_field_geometry import (
    ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    audio_video_dock_anatomies,
)
from .e1_av_history_permutation import build_e1_av_history_permutation
from .e1_canonical_refinement_preflight import (
    S1_DU_AB_PLAN_DIGEST,
    S1_DU_BA_PLAN_DIGEST,
    S1_DU_STEP_COUNTS,
    prepare_e1_canonical_refinement_preflight,
)
from .e1_completion_aligned_refinement import (
    build_e1_completion_aligned_refinement_plans,
)
from .e1_frozen_state_transfer_contract import (
    S1_DK_ARMS,
    _fixed_probe_sequences,
    _probe_digest,
)
from .e1_local_edge_plasticity import (
    E1_CONTRACT_ID,
    E1LocalEdgePlasticityContract,
    build_neutral_e1_state,
    validate_e1_state_for_layer,
)
from .e1_refined_chain_one_shot_contract import (
    E1RefinedChainOneShotContract,
    prepare_e1_refined_chain_one_shot_contract,
)
from .e1_refined_chain_one_shot_execution import (
    E1RefinedChainExecutionResult,
)
from .e1_refined_world_formation_contract import (
    S1_DS_FORMATION_HISTORIES,
    S1_DS_PROBE_DIGEST,
    S1_DS_REFINEMENTS,
)
from .shared_mcm_field import build_shared_mcm_field


class E1RefinedChainCanonicalProducerError(ValueError):
    """Raised when the canonical S1-DY producer binding changed."""


S1_DY_FORMATION_ARMS = (
    "ab",
    "ba",
    "ab_identity",
    "ab_formation_ablated",
    "ba_formation_ablated",
)
S1_DY_PROBE_ARMS = (
    "p0",
    "ab_active",
    "ba_active",
    "ab_probe_ablated",
    "ba_probe_ablated",
    "ab_fixed",
    "ba_fixed",
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


def _fresh_canonical_field(source):
    auditory, visual = source.history_ab
    return build_shared_mcm_field(
        (auditory.frames[0].frame, visual.frames[0].frame),
        audio_video_dock_anatomies(
            auditory_carrier_count=12,
            visual_grid_columns=6,
            visual_grid_rows=4,
            visual_channel_count=3,
        ),
        sample_offsets=ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    )


def _initial_field_digest(field) -> str:
    return _digest(
        {
            "layer": field.layer.digest(),
            "docks": tuple(
                (dock.dock_id, dock.dock_map.pairs) for dock in field.docks
            ),
            "tick": field.layer.tick,
            "distribution": field.last_distribution,
            "substrate": field.substrate,
        }
    )


def _initial_state_digest(state) -> str:
    return _digest(
        {
            "contract": (
                state.contract.contract_id,
                state.contract.node_capacity,
                state.contract.binding_rate_per_second,
                state.contract.release_rate_per_second,
                state.contract.backreaction_gain,
            ),
            "edge_inventory_digest": state.edge_inventory_digest,
            "bindings": tuple(
                (item.first_neuron_id, item.second_neuron_id, item.binding)
                for item in state.edge_bindings
            ),
        }
    )


@dataclass(frozen=True, slots=True)
class E1RefinedChainCanonicalProducerBinding:
    binding_id: str
    one_shot_contract_digest: str
    canonical_preflight_digest: str
    history_ab_digest: str
    history_ba_digest: str
    permutation_digest: str
    ab_plan_digest: str
    ba_plan_digest: str
    probe_digest: str
    geometry_digest: str
    initial_field_digest: str
    initial_state_digest: str
    source_support_count: int
    probe_support_count: int
    completion_count: int
    field_node_count: int
    edge_count: int
    refinements: tuple[tuple[str, int], ...]
    step_counts: tuple[tuple[str, int], ...]
    formation_histories: tuple[str, ...]
    formation_arms: tuple[str, ...]
    probe_arms: tuple[str, ...]
    producer_entrypoint: str
    canonical_producer_bound: bool
    execution_permitted: bool
    execution_started: bool
    memory_claim_permitted: bool
    ai_claim_permitted: bool

    def __post_init__(self) -> None:
        if self.binding_id != "e1.refined-chain-canonical-producer.s1dy.v1":
            raise E1RefinedChainCanonicalProducerError(
                "S1-DY binding identity changed"
            )
        for role in (
            "one_shot_contract_digest",
            "canonical_preflight_digest",
            "history_ab_digest",
            "history_ba_digest",
            "permutation_digest",
            "ab_plan_digest",
            "ba_plan_digest",
            "probe_digest",
            "geometry_digest",
            "initial_field_digest",
            "initial_state_digest",
        ):
            value = getattr(self, role)
            if len(value) != 64 or any(
                char not in "0123456789abcdef" for char in value
            ):
                raise E1RefinedChainCanonicalProducerError(
                    f"{role} is not SHA-256"
                )
        if (
            self.ab_plan_digest != S1_DU_AB_PLAN_DIGEST
            or self.ba_plan_digest != S1_DU_BA_PLAN_DIGEST
            or self.probe_digest != S1_DS_PROBE_DIGEST
        ):
            raise E1RefinedChainCanonicalProducerError(
                "S1-DY plan or probe binding changed"
            )
        if (
            self.source_support_count,
            self.probe_support_count,
            self.completion_count,
            self.field_node_count,
            self.edge_count,
        ) != (220, 110, 200, 84, 145):
            raise E1RefinedChainCanonicalProducerError(
                "S1-DY source or geometry inventory changed"
            )
        if (
            self.refinements != S1_DS_REFINEMENTS
            or self.step_counts != S1_DU_STEP_COUNTS
            or self.formation_histories != S1_DS_FORMATION_HISTORIES
            or self.formation_arms != S1_DY_FORMATION_ARMS
            or self.probe_arms != S1_DY_PROBE_ARMS
            or self.producer_entrypoint
            != "produce_e1_refined_chain_canonical_result"
            or self.canonical_producer_bound is not True
        ):
            raise E1RefinedChainCanonicalProducerError(
                "S1-DY producer role inventory changed"
            )
        if (
            self.execution_permitted is not False
            or self.execution_started is not False
            or self.memory_claim_permitted is not False
            or self.ai_claim_permitted is not False
        ):
            raise E1RefinedChainCanonicalProducerError(
                "S1-DY cannot release execution or strong claims"
            )

    def digest(self) -> str:
        return _digest(
            {name: getattr(self, name) for name in self.__dataclass_fields__}
        )


def prepare_e1_refined_chain_canonical_producer(
    report_directory: Path,
    upstream_report_path: Path,
) -> E1RefinedChainCanonicalProducerBinding:
    """Bind the canonical producer inputs without running formation or probe."""

    contract = prepare_e1_refined_chain_one_shot_contract(
        report_directory,
        upstream_report_path,
    )
    preflight = prepare_e1_canonical_refinement_preflight(upstream_report_path)
    source = build_e1_av_history_permutation()
    ab = build_e1_completion_aligned_refinement_plans(
        source.history_ab,
        horizon_start_tick=0,
        horizon_end_tick=2_000_000,
        ticks_per_second=1_000_000.0,
    )
    ba = build_e1_completion_aligned_refinement_plans(
        source.history_ba,
        horizon_start_tick=0,
        horizon_end_tick=2_000_000,
        ticks_per_second=1_000_000.0,
    )
    probe = _fixed_probe_sequences()
    field = _fresh_canonical_field(source)
    state = build_neutral_e1_state(
        field.layer,
        E1LocalEdgePlasticityContract(E1_CONTRACT_ID, 1.0, 1.5, 0.25, 0.5),
    )
    validate_e1_state_for_layer(field.layer, state)
    if (
        field.layer.tick != 0
        or field.last_distribution is not None
        or field.substrate is not None
        or any(item.binding != 0.0 for item in state.edge_bindings)
    ):
        raise E1RefinedChainCanonicalProducerError(
            "S1-DY initial field or E1 state is not fresh and neutral"
        )
    if _probe_digest(probe) != S1_DS_PROBE_DIGEST:
        raise E1RefinedChainCanonicalProducerError(
            "S1-DY canonical probe changed"
        )
    return E1RefinedChainCanonicalProducerBinding(
        binding_id="e1.refined-chain-canonical-producer.s1dy.v1",
        one_shot_contract_digest=contract.digest(),
        canonical_preflight_digest=preflight.digest(),
        history_ab_digest=source.history_ab_digest,
        history_ba_digest=source.history_ba_digest,
        permutation_digest=source.permutation_digest,
        ab_plan_digest=ab.digest(),
        ba_plan_digest=ba.digest(),
        probe_digest=_probe_digest(probe),
        geometry_digest=field.layer.digest(),
        initial_field_digest=_initial_field_digest(field),
        initial_state_digest=_initial_state_digest(state),
        source_support_count=sum(len(item.frames) for item in source.history_ab),
        probe_support_count=sum(len(item.frames) for item in probe),
        completion_count=len(ab.completion_ticks),
        field_node_count=len(field.layer.neurons),
        edge_count=len(state.edge_bindings),
        refinements=S1_DS_REFINEMENTS,
        step_counts=tuple(
            (item.refinement_id, len(item.proposal_steps)) for item in ab.plans
        ),
        formation_histories=S1_DS_FORMATION_HISTORIES,
        formation_arms=S1_DY_FORMATION_ARMS,
        probe_arms=S1_DY_PROBE_ARMS,
        producer_entrypoint="produce_e1_refined_chain_canonical_result",
        canonical_producer_bound=True,
        execution_permitted=False,
        execution_started=False,
        memory_claim_permitted=False,
        ai_claim_permitted=False,
    )


def produce_e1_refined_chain_canonical_result(
    binding: E1RefinedChainCanonicalProducerBinding,
    contract: E1RefinedChainOneShotContract,
) -> E1RefinedChainExecutionResult:
    """Reserved canonical entrypoint; S1-DZ must release its execution path."""

    if not isinstance(binding, E1RefinedChainCanonicalProducerBinding):
        raise E1RefinedChainCanonicalProducerError(
            "S1-DY requires its canonical producer binding"
        )
    if not isinstance(contract, E1RefinedChainOneShotContract):
        raise E1RefinedChainCanonicalProducerError(
            "S1-DY requires the bound one-shot contract"
        )
    if binding.one_shot_contract_digest != contract.digest():
        raise E1RefinedChainCanonicalProducerError(
            "S1-DY one-shot contract binding changed"
        )
    raise E1RefinedChainCanonicalProducerError(
        "S1-DY canonical execution remains locked until S1-DZ"
    )
