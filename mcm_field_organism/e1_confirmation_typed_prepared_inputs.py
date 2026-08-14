"""Private S1-EC2 typed input adapter for the S1-EC1 bundle."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path

from .e1_av_history_permutation import E1AVHistoryPermutation
from .e1_completion_aligned_refinement import _source_contact_evidence
from .e1_confirmation_prepared_execution_bundle import (
    E1PreparedExecutionBundle,
    E1PreparedRuntimeInput,
    prepare_e1_confirmation_execution_bundle,
    prepare_e1_confirmation_execution_bundle_from_run_contract,
)
from .e1_confirmation_descriptor_refinement_planner import (
    E1ConfirmationDescriptorRefinementPlanSet,
)
from .e1_confirmation_refinement_planner import (
    E1ConfirmationRefinementPlanSet,
)
from .e1_confirmation_research_corridor import (
    E1ConfirmationResearchCorridorDescriptor,
    E1ConfirmationSyntheticRunContract,
)
from .e1_frozen_state_transfer_contract import _probe_digest
from .e1_local_edge_plasticity import (
    E1LocalEdgePlasticityState,
    validate_e1_state_for_layer,
)
from .e1_refined_chain_canonical_producer import (
    _initial_field_digest,
    _initial_state_digest,
)
from .e1_refined_confirmation_contract import E1RefinedConfirmationContract
from .e1_refined_formation_runner import _digest
from .receptor_time_model import ReceptorTimeSequence
from .shared_mcm_field import SharedMCMField


class E1ConfirmationTypedPreparedInputsError(ValueError):
    """Raised when one S1-EC2 input role is absent or inconsistent."""


S1_EC2_INPUT_ROLES = (
    "corridor",
    "av_permutation",
    "history_ab_plans",
    "history_ba_plans",
    "probe_sequences",
    "probe_plans",
    "initial_field",
    "initial_state",
)


@dataclass(frozen=True, slots=True)
class E1ConfirmationTypedPreparedInputs:
    corridor: E1RefinedConfirmationContract | E1ConfirmationResearchCorridorDescriptor
    av_permutation: E1AVHistoryPermutation
    history_ab_plans: (
        E1ConfirmationRefinementPlanSet
        | E1ConfirmationDescriptorRefinementPlanSet
    )
    history_ba_plans: (
        E1ConfirmationRefinementPlanSet
        | E1ConfirmationDescriptorRefinementPlanSet
    )
    probe_sequences: tuple[ReceptorTimeSequence, ...]
    probe_plans: (
        E1ConfirmationRefinementPlanSet
        | E1ConfirmationDescriptorRefinementPlanSet
    )
    initial_field: SharedMCMField
    initial_state: E1LocalEdgePlasticityState

    def __post_init__(self) -> None:
        probe = tuple(self.probe_sequences)
        expected_types = (
            (self.av_permutation, E1AVHistoryPermutation),
            (self.initial_field, SharedMCMField),
            (self.initial_state, E1LocalEdgePlasticityState),
        )
        plan_types = (
            E1ConfirmationRefinementPlanSet,
            E1ConfirmationDescriptorRefinementPlanSet,
        )
        if (
            not isinstance(
                self.corridor,
                (
                    E1RefinedConfirmationContract,
                    E1ConfirmationResearchCorridorDescriptor,
                ),
            )
            or any(not isinstance(value, kind) for value, kind in expected_types)
            or any(
                not isinstance(value, plan_types)
                for value in (
                    self.history_ab_plans,
                    self.history_ba_plans,
                    self.probe_plans,
                )
            )
            or (
                not probe
                or any(not isinstance(item, ReceptorTimeSequence) for item in probe)
            )
        ):
            raise E1ConfirmationTypedPreparedInputsError(
                "S1-EC2 requires all eight typed input roles"
            )
        plan_sets = (
            self.history_ab_plans,
            self.history_ba_plans,
            self.probe_plans,
        )
        descriptor_bound = tuple(
            isinstance(item, E1ConfirmationDescriptorRefinementPlanSet)
            for item in plan_sets
        )
        if any(descriptor_bound) and not all(descriptor_bound):
            raise E1ConfirmationTypedPreparedInputsError(
                "S1-EC2 cannot mix legacy and descriptor-bound plans"
            )
        if all(descriptor_bound):
            if not isinstance(
                self.corridor, E1ConfirmationResearchCorridorDescriptor
            ) or any(
                item.research_descriptor_digest != self.corridor.digest()
                for item in plan_sets
            ):
                raise E1ConfirmationTypedPreparedInputsError(
                    "S1-EC2 descriptor plan binding changed"
                )
        else:
            contract_digest = (
                self.corridor.legacy_planner_contract_digest
                if isinstance(
                    self.corridor, E1ConfirmationResearchCorridorDescriptor
                )
                else self.corridor.digest()
            )
            if any(item.contract_digest != contract_digest for item in plan_sets):
                raise E1ConfirmationTypedPreparedInputsError(
                    "S1-EC2 plan contract binding changed"
                )
        self._require_source_binding(
            "history_ab",
            self.av_permutation.history_ab,
            self.history_ab_plans,
            1_000_000.0,
        )
        self._require_source_binding(
            "history_ba",
            self.av_permutation.history_ba,
            self.history_ba_plans,
            1_000_000.0,
        )
        self._require_source_binding("probe", probe, self.probe_plans, 1_000_000.0)
        refinements = tuple(self.corridor.refinements)
        if any(
            tuple((plan.refinement_id, plan.factor) for plan in item.plans)
            != refinements
            for item in plan_sets
        ):
            raise E1ConfirmationTypedPreparedInputsError(
                "S1-EC2 refinement inventory changed"
            )
        if (
            self.initial_field.layer.tick != 0
            or self.initial_field.last_distribution is not None
            or self.initial_field.substrate is not None
            or any(item.binding != 0.0 for item in self.initial_state.edge_bindings)
        ):
            raise E1ConfirmationTypedPreparedInputsError(
                "S1-EC2 requires a neutral initial field and E1 state"
            )
        try:
            validate_e1_state_for_layer(
                self.initial_field.layer,
                self.initial_state,
            )
        except ValueError as exc:
            raise E1ConfirmationTypedPreparedInputsError(
                "S1-EC2 initial field and E1 state do not share one geometry"
            ) from exc
        object.__setattr__(self, "probe_sequences", probe)

    @staticmethod
    def _require_source_binding(
        role: str,
        sequences: tuple[ReceptorTimeSequence, ...],
        plans: (
            E1ConfirmationRefinementPlanSet
            | E1ConfirmationDescriptorRefinementPlanSet
        ),
        ticks_per_second: float,
    ) -> None:
        evidence = _source_contact_evidence(tuple(sequences), ticks_per_second)
        if (
            plans.source_contact_digest != evidence[0]
            or any(
                (
                    item.source_contact_digest,
                    item.source_signed_integral,
                    item.source_absolute_integral,
                    item.source_quadratic_integral,
                )
                != evidence
                for item in plans.plans
            )
        ):
            raise E1ConfirmationTypedPreparedInputsError(
                f"S1-EC2 {role} source and plans do not match"
            )


TypedInputResolver = Callable[[], E1ConfirmationTypedPreparedInputs]


def _permutation_digest(value: E1AVHistoryPermutation) -> str:
    return _digest(asdict(value))


def _probe_sequences_digest(value: tuple[ReceptorTimeSequence, ...]) -> str:
    return _probe_digest(tuple(value))


def _method_digest(value) -> str:
    return value.digest()


def _typed_runtime_inputs(
    values: E1ConfirmationTypedPreparedInputs,
) -> tuple[E1PreparedRuntimeInput, ...]:
    bindings = (
        ("corridor", values.corridor, _method_digest),
        ("av_permutation", values.av_permutation, _permutation_digest),
        ("history_ab_plans", values.history_ab_plans, _method_digest),
        ("history_ba_plans", values.history_ba_plans, _method_digest),
        ("probe_sequences", values.probe_sequences, _probe_sequences_digest),
        ("probe_plans", values.probe_plans, _method_digest),
        ("initial_field", values.initial_field, _initial_field_digest),
        ("initial_state", values.initial_state, _initial_state_digest),
    )
    return tuple(
        E1PreparedRuntimeInput(
            role=role,
            value=value,
            prepared_digest=reader(value),
            digest_reader=reader,
        )
        for role, value, reader in bindings
    )


def prepare_e1_confirmation_typed_execution_bundle(
    synthetic_directory: Path,
    resolver: TypedInputResolver,
) -> E1PreparedExecutionBundle:
    """Resolve all typed E1 inputs once, then hand them to S1-EC1."""

    if not callable(resolver):
        raise E1ConfirmationTypedPreparedInputsError(
            "S1-EC2 requires one typed input resolver"
        )
    values = resolver()
    if not isinstance(values, E1ConfirmationTypedPreparedInputs):
        raise E1ConfirmationTypedPreparedInputsError(
            "S1-EC2 resolver returned no typed input set"
        )
    prepared = _typed_runtime_inputs(values)
    if tuple(item.role for item in prepared) != S1_EC2_INPUT_ROLES:
        raise E1ConfirmationTypedPreparedInputsError(
            "S1-EC2 prepared input order changed"
        )
    return prepare_e1_confirmation_execution_bundle(
        synthetic_directory,
        lambda: prepared,
    )


def prepare_e1_confirmation_typed_bundle_from_run_contract(
    run_contract: E1ConfirmationSyntheticRunContract,
    resolver: TypedInputResolver,
) -> E1PreparedExecutionBundle:
    """Resolve typed inputs once and bind them to the exact S1-EC3 run paths."""

    if not callable(resolver):
        raise E1ConfirmationTypedPreparedInputsError(
            "S1-EC6 requires one typed input resolver"
        )
    values = resolver()
    if not isinstance(values, E1ConfirmationTypedPreparedInputs):
        raise E1ConfirmationTypedPreparedInputsError(
            "S1-EC6 resolver returned no typed input set"
        )
    prepared = _typed_runtime_inputs(values)
    if tuple(item.role for item in prepared) != S1_EC2_INPUT_ROLES:
        raise E1ConfirmationTypedPreparedInputsError(
            "S1-EC6 prepared input order changed"
        )
    return prepare_e1_confirmation_execution_bundle_from_run_contract(
        run_contract,
        lambda: prepared,
    )
