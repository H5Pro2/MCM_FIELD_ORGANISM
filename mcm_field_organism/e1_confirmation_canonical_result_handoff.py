"""Private S1-EB13 static handoff from canonical probe to result core."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .e1_confirmation_canonical_formation_adapter import (
    E1ConfirmationCanonicalFormationProduction,
)
from .e1_confirmation_canonical_probe_handoff import (
    E1ConfirmationCanonicalProbeHandoff,
)
from .e1_confirmation_canonical_producer_binding import (
    E1ConfirmationCanonicalProducerBinding,
)
from .e1_confirmation_chain_contract import E1ConfirmationChainContract
from .e1_confirmation_seven_arm_probe import (
    E1ConfirmationProbeResult,
    _state_digest,
)
from .e1_refined_confirmation_contract import S1_EB_REFINEMENTS
from .e1_refined_formation_runner import _digest


class E1ConfirmationCanonicalResultHandoffError(ValueError):
    """Raised when an S1-EB13 result handoff binding changed."""


_BINDING_DIGEST = (
    "aae7f9427200c88f60155f884c3ee6a4279941c4ecf878f8490a69e19f7c2d34"
)


def _valid_digest(value: str) -> bool:
    return len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


@dataclass(frozen=True, slots=True)
class E1ConfirmationCanonicalResultHandoff:
    handoff_id: str
    binding_digest: str
    chain_contract_digest: str
    formation_production_digest: str
    probe_handoff_digest: str
    probe_result_digests: tuple[tuple[str, str], ...]
    probe_field_digests: tuple[tuple[str, tuple[tuple[str, str], ...]], ...]
    frozen_state_digests: tuple[tuple[str, str, str], ...]
    refinements: tuple[tuple[str, int], ...]
    metrics: tuple[str, ...]
    required_controls: tuple[str, ...]
    technical_decisions: tuple[str, ...]
    decision_rules: tuple[str, ...]
    result_core_entrypoint: str
    result_handoff_bound: bool
    result_composition_permitted: bool
    decision_permitted: bool
    persistence_permitted: bool
    claims_permitted: bool
    handoff_digest: str

    def __post_init__(self) -> None:
        if self.handoff_id != "e1.confirmation-result-handoff.s1eb13.v1":
            raise E1ConfirmationCanonicalResultHandoffError(
                "S1-EB13 handoff identity changed"
            )
        for role in (
            "binding_digest",
            "chain_contract_digest",
            "formation_production_digest",
            "probe_handoff_digest",
            "handoff_digest",
        ):
            if not _valid_digest(getattr(self, role)):
                raise E1ConfirmationCanonicalResultHandoffError(
                    f"{role} is not SHA-256"
                )
        if self.binding_digest != _BINDING_DIGEST:
            raise E1ConfirmationCanonicalResultHandoffError(
                "S1-EB13 canonical binding changed"
            )
        expected_ids = tuple(item[0] for item in S1_EB_REFINEMENTS)
        if (
            self.refinements != S1_EB_REFINEMENTS
            or tuple(role for role, _ in self.probe_result_digests)
            != expected_ids
            or tuple(role for role, _ in self.probe_field_digests)
            != expected_ids
            or tuple(role for role, _, _ in self.frozen_state_digests)
            != expected_ids
        ):
            raise E1ConfirmationCanonicalResultHandoffError(
                "S1-EB13 refinement result inventory changed"
            )
        nested = (
            *(value for _, value in self.probe_result_digests),
            *(
                value
                for _, fields in self.probe_field_digests
                for _, value in fields
            ),
            *(
                value
                for _, ab_digest, ba_digest in self.frozen_state_digests
                for value in (ab_digest, ba_digest)
            ),
        )
        if any(not _valid_digest(value) for value in nested):
            raise E1ConfirmationCanonicalResultHandoffError(
                "S1-EB13 contains an invalid nested digest"
            )
        if (
            self.result_core_entrypoint != "build_e1_confirmation_chain_result"
            or self.result_handoff_bound is not True
            or any(
                value is not False
                for value in (
                    self.result_composition_permitted,
                    self.decision_permitted,
                    self.persistence_permitted,
                    self.claims_permitted,
                )
            )
        ):
            raise E1ConfirmationCanonicalResultHandoffError(
                "S1-EB13 composition, decision, persistence, or claims opened"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "handoff_digest"
        }
        if self.handoff_digest != _digest(payload):
            raise E1ConfirmationCanonicalResultHandoffError(
                "S1-EB13 handoff digest does not match its payload"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


def prepare_e1_confirmation_canonical_result_handoff(
    binding: E1ConfirmationCanonicalProducerBinding,
    chain_contract: E1ConfirmationChainContract,
    formation: E1ConfirmationCanonicalFormationProduction,
    probe_handoff: E1ConfirmationCanonicalProbeHandoff,
    probes: tuple[E1ConfirmationProbeResult, ...],
) -> E1ConfirmationCanonicalResultHandoff:
    """Bind probe outputs to the result-core inventory without composing it."""

    if not isinstance(binding, E1ConfirmationCanonicalProducerBinding) or (
        binding.digest() != _BINDING_DIGEST
    ):
        raise E1ConfirmationCanonicalResultHandoffError(
            "S1-EB13 requires the unchanged S1-EB9 binding"
        )
    if not isinstance(chain_contract, E1ConfirmationChainContract) or (
        chain_contract.digest() != binding.chain_contract_digest
    ):
        raise E1ConfirmationCanonicalResultHandoffError(
            "S1-EB13 requires the bound S1-EB4 chain contract"
        )
    if not isinstance(probe_handoff, E1ConfirmationCanonicalProbeHandoff) or (
        probe_handoff.binding_digest != binding.digest()
        or probe_handoff.chain_contract_digest != chain_contract.digest()
    ):
        raise E1ConfirmationCanonicalResultHandoffError(
            "S1-EB13 requires the bound S1-EB11 probe handoff"
        )
    if not isinstance(formation, E1ConfirmationCanonicalFormationProduction) or (
        formation.production_digest
        != probe_handoff.formation_production_digest
    ):
        raise E1ConfirmationCanonicalResultHandoffError(
            "S1-EB13 formation does not match its probe handoff"
        )
    formed = tuple(formation.refinements)
    probe_results = tuple(probes)
    if tuple(
        (item.refinement_id, item.factor) for item in formed
    ) != S1_EB_REFINEMENTS or tuple(
        (item.refinement_id, item.factor) for item in probe_results
    ) != S1_EB_REFINEMENTS or any(
        not isinstance(item, E1ConfirmationProbeResult)
        for item in probe_results
    ):
        raise E1ConfirmationCanonicalResultHandoffError(
            "S1-EB13 requires ordered r2, r4, and r8 probe results"
        )
    expected_plan_digests = dict(probe_handoff.probe_plan_digests)
    for formation_item, probe in zip(formed, probe_results, strict=True):
        if (
            probe.probe_source_digest != probe_handoff.probe_source_digest
            or probe.probe_plan_digest
            != expected_plan_digests[probe.refinement_id]
            or probe.pre_probe_ab_state_digest
            != _state_digest(formation_item.b_ab)
            or probe.post_probe_ab_state_digest
            != _state_digest(formation_item.b_ab)
            or probe.pre_probe_ba_state_digest
            != _state_digest(formation_item.b_ba)
            or probe.post_probe_ba_state_digest
            != _state_digest(formation_item.b_ba)
        ):
            raise E1ConfirmationCanonicalResultHandoffError(
                "S1-EB13 probe source, plan, or frozen state binding changed"
            )
    values = {
        "handoff_id": "e1.confirmation-result-handoff.s1eb13.v1",
        "binding_digest": binding.digest(),
        "chain_contract_digest": chain_contract.digest(),
        "formation_production_digest": formation.production_digest,
        "probe_handoff_digest": probe_handoff.handoff_digest,
        "probe_result_digests": tuple(
            (item.refinement_id, item.result_digest) for item in probe_results
        ),
        "probe_field_digests": tuple(
            (item.refinement_id, item.field_digests) for item in probe_results
        ),
        "frozen_state_digests": tuple(
            (
                item.refinement_id,
                item.pre_probe_ab_state_digest,
                item.pre_probe_ba_state_digest,
            )
            for item in probe_results
        ),
        "refinements": S1_EB_REFINEMENTS,
        "metrics": chain_contract.metrics,
        "required_controls": chain_contract.required_controls,
        "technical_decisions": chain_contract.technical_decisions,
        "decision_rules": chain_contract.decision_rules,
        "result_core_entrypoint": "build_e1_confirmation_chain_result",
        "result_handoff_bound": True,
        "result_composition_permitted": False,
        "decision_permitted": False,
        "persistence_permitted": False,
        "claims_permitted": False,
    }
    return E1ConfirmationCanonicalResultHandoff(
        **values,
        handoff_digest=_digest(values),
    )
