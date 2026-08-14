"""Private S1-EB10 canonical-bound r2/r4/r8 formation adapter."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path

from .e1_av_history_permutation import build_e1_av_history_permutation
from .e1_confirmation_canonical_producer_binding import (
    E1ConfirmationCanonicalProducerBinding,
)
from .e1_confirmation_chain_contract import E1ConfirmationChainContract
from .e1_confirmation_formation_runner import (
    E1ConfirmationFormationResult,
    _run_arm,
)
from .e1_confirmation_refinement_planner import (
    build_e1_confirmation_refinement_plans,
)
from .e1_local_edge_plasticity import (
    E1_CONTRACT_ID,
    E1LocalEdgePlasticityContract,
    build_neutral_e1_state,
)
from .e1_refined_chain_canonical_producer import (
    _fresh_canonical_field,
    _initial_field_digest,
    _initial_state_digest,
)
from .e1_refined_confirmation_contract import (
    build_e1_refined_confirmation_contract,
)
from .e1_refined_formation_runner import _digest, _state_payload
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)


class E1ConfirmationCanonicalFormationAdapterError(ValueError):
    """Raised when an S1-EB10 binding or formation control changed."""


_REFINEMENTS = (("r2", 2), ("r4", 4), ("r8", 8))
_BINDING_DIGEST = (
    "aae7f9427200c88f60155f884c3ee6a4279941c4ecf878f8490a69e19f7c2d34"
)


def _valid_digest(value: str) -> bool:
    return len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


@dataclass(frozen=True, slots=True)
class E1ConfirmationCanonicalFormationProduction:
    source_provenance: str
    binding_digest: str
    chain_contract_digest: str
    ab_plan_digest: str
    ba_plan_digest: str
    initial_field_digest: str
    initial_state_digest: str
    refinements: tuple[E1ConfirmationFormationResult, ...]
    production_digest: str

    def __post_init__(self) -> None:
        if self.source_provenance != "canonical-s1eb9":
            raise E1ConfirmationCanonicalFormationAdapterError(
                "S1-EB10 source provenance changed"
            )
        for role in (
            "binding_digest",
            "chain_contract_digest",
            "ab_plan_digest",
            "ba_plan_digest",
            "initial_field_digest",
            "initial_state_digest",
            "production_digest",
        ):
            if not _valid_digest(getattr(self, role)):
                raise E1ConfirmationCanonicalFormationAdapterError(
                    f"{role} is not SHA-256"
                )
        if self.binding_digest != _BINDING_DIGEST:
            raise E1ConfirmationCanonicalFormationAdapterError(
                "S1-EB10 canonical binding changed"
            )
        refinements = tuple(self.refinements)
        if tuple(
            (item.refinement_id, item.factor) for item in refinements
        ) != _REFINEMENTS:
            raise E1ConfirmationCanonicalFormationAdapterError(
                "S1-EB10 requires ordered r2, r4, and r8 results"
            )
        object.__setattr__(self, "refinements", refinements)


def _canonical_inputs(
    binding: E1ConfirmationCanonicalProducerBinding,
    chain_contract: E1ConfirmationChainContract,
):
    corridor = build_e1_refined_confirmation_contract(
        Path(chain_contract.report_path).parent,
        Path(chain_contract.upstream_report_path),
    )
    source = build_e1_av_history_permutation()
    ab = build_e1_confirmation_refinement_plans(
        corridor,
        source.history_ab,
        horizon_start_tick=0,
        horizon_end_tick=2_000_000,
        ticks_per_second=1_000_000.0,
    )
    ba = build_e1_confirmation_refinement_plans(
        corridor,
        source.history_ba,
        horizon_start_tick=0,
        horizon_end_tick=2_000_000,
        ticks_per_second=1_000_000.0,
    )
    field = _fresh_canonical_field(source)
    state = build_neutral_e1_state(
        field.layer,
        E1LocalEdgePlasticityContract(
            E1_CONTRACT_ID,
            1.0,
            1.5,
            0.25,
            0.5,
        ),
    )
    observed = (
        corridor.digest(),
        source.history_ab_digest,
        source.history_ba_digest,
        source.permutation_digest,
        ab.digest(),
        ba.digest(),
        field.layer.digest(),
        _initial_field_digest(field),
        _initial_state_digest(state),
    )
    expected = (
        chain_contract.confirmation_contract_digest,
        binding.history_ab_digest,
        binding.history_ba_digest,
        binding.permutation_digest,
        binding.ab_plan_digest,
        binding.ba_plan_digest,
        binding.geometry_digest,
        binding.initial_field_digest,
        binding.initial_state_digest,
    )
    if observed != expected:
        raise E1ConfirmationCanonicalFormationAdapterError(
            "S1-EB10 canonical source, plan, geometry, field, or state changed"
        )
    return corridor, source, ab, ba, field, state


def produce_e1_confirmation_canonical_formation(
    binding: E1ConfirmationCanonicalProducerBinding,
    chain_contract: E1ConfirmationChainContract,
) -> E1ConfirmationCanonicalFormationProduction:
    """Form bound states only after a later canonical release gate permits it."""

    if not isinstance(binding, E1ConfirmationCanonicalProducerBinding) or (
        binding.digest() != _BINDING_DIGEST
    ):
        raise E1ConfirmationCanonicalFormationAdapterError(
            "S1-EB10 requires the unchanged S1-EB9 canonical binding"
        )
    if not isinstance(chain_contract, E1ConfirmationChainContract) or (
        chain_contract.digest() != binding.chain_contract_digest
    ):
        raise E1ConfirmationCanonicalFormationAdapterError(
            "S1-EB10 requires the bound S1-EB4 chain contract"
        )
    _, source, ab_plans, ba_plans, initial_field, initial_state = (
        _canonical_inputs(binding, chain_contract)
    )
    substrate = NeutralLocalFieldSubstrateConfig(1.0)
    afterimage = NeutralFastAfterimageConfig(0.5)
    initial_field_digest = _initial_field_digest(initial_field)
    initial_state_digest = _initial_state_digest(initial_state)
    results = []
    for ab_plan, ba_plan in zip(ab_plans.plans, ba_plans.plans, strict=True):
        fields = tuple(copy.deepcopy(initial_field) for _ in range(5))
        states = tuple(copy.deepcopy(initial_state) for _ in range(5))
        if len({id(item) for item in fields}) != 5 or len(
            {id(item) for item in states}
        ) != 5:
            raise E1ConfirmationCanonicalFormationAdapterError(
                "S1-EB10 arm inputs are not object-separated"
            )
        arm_specs = (
            ("ab", source.history_ab, ab_plan.proposal_steps, True),
            ("ba", source.history_ba, ba_plan.proposal_steps, True),
            ("ab_identity", source.history_ab, ab_plan.proposal_steps, True),
            (
                "ab_formation_ablated",
                source.history_ab,
                ab_plan.proposal_steps,
                False,
            ),
            (
                "ba_formation_ablated",
                source.history_ba,
                ba_plan.proposal_steps,
                False,
            ),
        )
        outputs = tuple(
            _run_arm(
                arm_id,
                ab_plan.refinement_id,
                fields[index],
                states[index],
                sequences,
                proposal_steps,
                substrate,
                afterimage,
                formation_enabled=enabled,
            )
            for index, (
                arm_id,
                sequences,
                proposal_steps,
                enabled,
            ) in enumerate(arm_specs)
        )
        output_states = tuple(item[0] for item in outputs)
        audits = tuple(item[1] for item in outputs)
        if (
            audits[0].field_digest != audits[2].field_digest
            or audits[0].field_digest != audits[3].field_digest
            or audits[1].field_digest != audits[4].field_digest
        ):
            raise E1ConfirmationCanonicalFormationAdapterError(
                "S1-EB10 history backreaction ablation failed"
            )
        payload = {
            "refinement": (ab_plan.refinement_id, ab_plan.factor),
            "states": tuple(_state_payload(item) for item in output_states),
            "audits": tuple(
                (
                    item.arm_id,
                    item.handoff_digest,
                    item.field_digest,
                    item.source_support_count,
                    item.resource_budget_error,
                )
                for item in audits
            ),
        }
        results.append(
            E1ConfirmationFormationResult(
                refinement_id=ab_plan.refinement_id,
                factor=ab_plan.factor,
                b_ab=output_states[0],
                b_ba=output_states[1],
                b_ab_identity=output_states[2],
                b_ab_formation_ablated=output_states[3],
                b_ba_formation_ablated=output_states[4],
                arm_audits=audits,
                result_digest=_digest(payload),
            )
        )
    if (
        _initial_field_digest(initial_field) != initial_field_digest
        or _initial_state_digest(initial_state) != initial_state_digest
    ):
        raise E1ConfirmationCanonicalFormationAdapterError(
            "S1-EB10 changed an initial input"
        )
    production_payload = {
        "source_provenance": "canonical-s1eb9",
        "binding_digest": binding.digest(),
        "chain_contract_digest": chain_contract.digest(),
        "ab_plan_digest": ab_plans.digest(),
        "ba_plan_digest": ba_plans.digest(),
        "initial_field_digest": initial_field_digest,
        "initial_state_digest": initial_state_digest,
        "result_digests": tuple(item.result_digest for item in results),
    }
    return E1ConfirmationCanonicalFormationProduction(
        source_provenance="canonical-s1eb9",
        binding_digest=binding.digest(),
        chain_contract_digest=chain_contract.digest(),
        ab_plan_digest=ab_plans.digest(),
        ba_plan_digest=ba_plans.digest(),
        initial_field_digest=initial_field_digest,
        initial_state_digest=initial_state_digest,
        refinements=tuple(results),
        production_digest=_digest(production_payload),
    )
