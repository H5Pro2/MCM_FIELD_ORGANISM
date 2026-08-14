"""Private S1-EC5 complete descriptor-bound input resolver."""

from __future__ import annotations

from pathlib import Path

from .e1_av_history_permutation import build_e1_av_history_permutation
from .e1_confirmation_descriptor_refinement_planner import (
    build_e1_confirmation_descriptor_refinement_plans,
)
from .e1_confirmation_prepared_execution_bundle import E1PreparedExecutionBundle
from .e1_confirmation_research_corridor import (
    E1ConfirmationSyntheticRunContract,
    build_e1_confirmation_research_corridor,
)
from .e1_confirmation_typed_prepared_inputs import (
    E1ConfirmationTypedPreparedInputs,
    prepare_e1_confirmation_typed_bundle_from_run_contract,
    prepare_e1_confirmation_typed_execution_bundle,
)
from .e1_frozen_state_transfer_contract import _fixed_probe_sequences
from .e1_local_edge_plasticity import (
    E1_CONTRACT_ID,
    E1LocalEdgePlasticityContract,
    build_neutral_e1_state,
)
from .e1_refined_chain_canonical_producer import _fresh_canonical_field


def build_e1_confirmation_descriptor_typed_inputs(
    upstream_report_path: Path,
) -> E1ConfirmationTypedPreparedInputs:
    """Resolve every E1 input from S1-EC3/4 without a one-shot path contract."""

    descriptor = build_e1_confirmation_research_corridor(upstream_report_path)
    source = build_e1_av_history_permutation()
    history_ab_plans = build_e1_confirmation_descriptor_refinement_plans(
        descriptor,
        source.history_ab,
        horizon_start_tick=0,
        horizon_end_tick=2_000_000,
        ticks_per_second=1_000_000.0,
    )
    history_ba_plans = build_e1_confirmation_descriptor_refinement_plans(
        descriptor,
        source.history_ba,
        horizon_start_tick=0,
        horizon_end_tick=2_000_000,
        ticks_per_second=1_000_000.0,
    )
    probe = _fixed_probe_sequences()
    probe_plans = build_e1_confirmation_descriptor_refinement_plans(
        descriptor,
        probe,
        horizon_start_tick=0,
        horizon_end_tick=1_000_000,
        ticks_per_second=1_000_000.0,
    )
    initial_field = _fresh_canonical_field(source)
    initial_state = build_neutral_e1_state(
        initial_field.layer,
        E1LocalEdgePlasticityContract(
            E1_CONTRACT_ID,
            1.0,
            1.5,
            0.25,
            0.5,
        ),
    )
    return E1ConfirmationTypedPreparedInputs(
        corridor=descriptor,
        av_permutation=source,
        history_ab_plans=history_ab_plans,
        history_ba_plans=history_ba_plans,
        probe_sequences=probe,
        probe_plans=probe_plans,
        initial_field=initial_field,
        initial_state=initial_state,
    )


def prepare_e1_confirmation_descriptor_execution_bundle(
    synthetic_directory: Path,
    upstream_report_path: Path,
) -> E1PreparedExecutionBundle:
    """Resolve the complete typed set once before the S1-EC1 markers."""

    return prepare_e1_confirmation_typed_execution_bundle(
        synthetic_directory,
        lambda: build_e1_confirmation_descriptor_typed_inputs(
            upstream_report_path
        ),
    )


def prepare_e1_confirmation_descriptor_bundle_from_run_contract(
    run_contract: E1ConfirmationSyntheticRunContract,
    upstream_report_path: Path,
) -> E1PreparedExecutionBundle:
    """Bind the complete descriptor input set to the exact S1-EC3 run contract."""

    return prepare_e1_confirmation_typed_bundle_from_run_contract(
        run_contract,
        lambda: build_e1_confirmation_descriptor_typed_inputs(
            upstream_report_path
        ),
    )
