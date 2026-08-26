"""Private S1-EB14 canonical-bound result compositor; locked."""

from __future__ import annotations

from .e1_confirmation_canonical_formation_adapter import (
    E1ConfirmationCanonicalFormationProduction,
)
from .e1_confirmation_canonical_probe_handoff import (
    E1ConfirmationCanonicalProbeHandoff,
)
from .e1_confirmation_canonical_producer_binding import (
    E1ConfirmationCanonicalProducerBinding,
)
from .e1_confirmation_canonical_result_handoff import (
    E1ConfirmationCanonicalResultHandoff,
)
from .e1_confirmation_chain_composition import (
    compose_synthetic_e1_confirmation_chain,
)
from .e1_confirmation_chain_contract import E1ConfirmationChainContract
from .e1_confirmation_formation_runner import (
    E1ConfirmationFormationProduction,
)
from .e1_confirmation_result_core import E1ConfirmationChainResult
from .e1_confirmation_seven_arm_probe import E1ConfirmationProbeResult
from .e1_refined_formation_runner import _digest


class E1ConfirmationCanonicalResultCompositorError(ValueError):
    """Raised when an S1-EB14 binding, gate, or composition input changed."""


_BINDING_DIGEST = (
    "aae7f9427200c88f60155f884c3ee6a4279941c4ecf878f8490a69e19f7c2d34"
)


def _compose_bound_result_core(
    chain_contract: E1ConfirmationChainContract,
    formation: E1ConfirmationCanonicalFormationProduction,
    probes: tuple[E1ConfirmationProbeResult, ...],
) -> E1ConfirmationChainResult:
    """Exercise the existing result core through a private compatible view."""

    if not isinstance(chain_contract, E1ConfirmationChainContract):
        raise E1ConfirmationCanonicalResultCompositorError(
            "S1-EB14 requires one S1-EB4 chain contract"
        )
    if not isinstance(formation, E1ConfirmationCanonicalFormationProduction) or (
        formation.chain_contract_digest != chain_contract.digest()
    ):
        raise E1ConfirmationCanonicalResultCompositorError(
            "S1-EB14 formation does not match its chain contract"
        )
    probe_results = tuple(probes)
    if len(probe_results) != 3 or any(
        not isinstance(item, E1ConfirmationProbeResult)
        for item in probe_results
    ):
        raise E1ConfirmationCanonicalResultCompositorError(
            "S1-EB14 requires three probe results"
        )
    facade_payload = {
        "source_provenance": "synthetic-s1eb3",
        "contract_digest": chain_contract.confirmation_contract_digest,
        "ab_plan_digest": formation.ab_plan_digest,
        "ba_plan_digest": formation.ba_plan_digest,
        "initial_field_digest": formation.initial_field_digest,
        "initial_state_digest": formation.initial_state_digest,
        "result_digests": tuple(
            item.result_digest for item in formation.refinements
        ),
    }
    facade = E1ConfirmationFormationProduction(
        source_provenance="synthetic-s1eb3",
        contract_digest=chain_contract.confirmation_contract_digest,
        ab_plan_digest=formation.ab_plan_digest,
        ba_plan_digest=formation.ba_plan_digest,
        initial_field_digest=formation.initial_field_digest,
        initial_state_digest=formation.initial_state_digest,
        refinements=formation.refinements,
        production_digest=_digest(facade_payload),
    )
    try:
        return compose_synthetic_e1_confirmation_chain(
            chain_contract,
            facade,
            probe_results,
        )
    except ValueError as exc:
        raise E1ConfirmationCanonicalResultCompositorError(str(exc)) from exc


def compose_e1_confirmation_canonical_result(
    binding: E1ConfirmationCanonicalProducerBinding,
    chain_contract: E1ConfirmationChainContract,
    formation: E1ConfirmationCanonicalFormationProduction,
    probe_handoff: E1ConfirmationCanonicalProbeHandoff,
    result_handoff: E1ConfirmationCanonicalResultHandoff,
    probes: tuple[E1ConfirmationProbeResult, ...],
) -> E1ConfirmationChainResult:
    """Reserve canonical composition while the S1-EB13 gate is closed."""

    if not isinstance(binding, E1ConfirmationCanonicalProducerBinding) or (
        binding.digest() != _BINDING_DIGEST
    ):
        raise E1ConfirmationCanonicalResultCompositorError(
            "S1-EB14 requires the unchanged S1-EB9 binding"
        )
    if not isinstance(chain_contract, E1ConfirmationChainContract) or (
        chain_contract.digest() != binding.chain_contract_digest
    ):
        raise E1ConfirmationCanonicalResultCompositorError(
            "S1-EB14 requires the bound S1-EB4 chain contract"
        )
    if not isinstance(probe_handoff, E1ConfirmationCanonicalProbeHandoff) or (
        probe_handoff.binding_digest != binding.digest()
        or probe_handoff.chain_contract_digest != chain_contract.digest()
    ):
        raise E1ConfirmationCanonicalResultCompositorError(
            "S1-EB14 requires the bound S1-EB11 probe handoff"
        )
    if not isinstance(result_handoff, E1ConfirmationCanonicalResultHandoff) or (
        result_handoff.binding_digest != binding.digest()
        or result_handoff.chain_contract_digest != chain_contract.digest()
        or result_handoff.probe_handoff_digest != probe_handoff.handoff_digest
    ):
        raise E1ConfirmationCanonicalResultCompositorError(
            "S1-EB14 requires the bound S1-EB13 result handoff"
        )
    if not isinstance(formation, E1ConfirmationCanonicalFormationProduction) or (
        formation.production_digest
        != result_handoff.formation_production_digest
    ):
        raise E1ConfirmationCanonicalResultCompositorError(
            "S1-EB14 formation does not match its result handoff"
        )
    probe_results = tuple(probes)
    if tuple(
        (item.refinement_id, item.result_digest) for item in probe_results
    ) != result_handoff.probe_result_digests:
        raise E1ConfirmationCanonicalResultCompositorError(
            "S1-EB14 probes do not match their result handoff"
        )
    if result_handoff.result_composition_permitted is not True:
        raise E1ConfirmationCanonicalResultCompositorError(
            "S1-EB14 canonical result composition remains locked"
        )
    return _compose_bound_result_core(
        chain_contract,
        formation,
        probe_results,
    )
