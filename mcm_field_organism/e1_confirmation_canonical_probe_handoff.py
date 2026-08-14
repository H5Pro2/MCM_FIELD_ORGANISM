"""Private S1-EB11 static handoff from canonical formation to probe plans."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from .e1_confirmation_canonical_formation_adapter import (
    E1ConfirmationCanonicalFormationProduction,
)
from .e1_confirmation_canonical_producer_binding import (
    E1ConfirmationCanonicalProducerBinding,
)
from .e1_confirmation_chain_contract import E1ConfirmationChainContract
from .e1_confirmation_refinement_planner import (
    build_e1_confirmation_refinement_plans,
)
from .e1_frozen_state_transfer_contract import (
    _fixed_probe_sequences,
    _probe_digest,
)
from .e1_refined_confirmation_contract import (
    S1_EB_REFINEMENTS,
    build_e1_refined_confirmation_contract,
)
from .e1_refined_formation_runner import _digest, _state_payload


class E1ConfirmationCanonicalProbeHandoffError(ValueError):
    """Raised when an S1-EB11 static transition binding changed."""


_BINDING_DIGEST = (
    "aae7f9427200c88f60155f884c3ee6a4279941c4ecf878f8490a69e19f7c2d34"
)


def _valid_digest(value: str) -> bool:
    return len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


def _state_digest(state) -> str:
    return _digest(_state_payload(state))


@dataclass(frozen=True, slots=True)
class E1ConfirmationCanonicalProbeHandoff:
    handoff_id: str
    binding_digest: str
    chain_contract_digest: str
    formation_production_digest: str
    formation_result_digests: tuple[tuple[str, str], ...]
    formation_state_digests: tuple[tuple[str, str, str], ...]
    probe_source_digest: str
    probe_plan_set_digest: str
    probe_plan_digests: tuple[tuple[str, str], ...]
    refinements: tuple[tuple[str, int], ...]
    probe_entrypoint: str
    handoff_bound: bool
    probe_execution_permitted: bool
    decision_permitted: bool
    persistence_permitted: bool
    claims_permitted: bool
    handoff_digest: str

    def __post_init__(self) -> None:
        if self.handoff_id != "e1.confirmation-probe-handoff.s1eb11.v1":
            raise E1ConfirmationCanonicalProbeHandoffError(
                "S1-EB11 handoff identity changed"
            )
        for role in (
            "binding_digest",
            "chain_contract_digest",
            "formation_production_digest",
            "probe_source_digest",
            "probe_plan_set_digest",
            "handoff_digest",
        ):
            if not _valid_digest(getattr(self, role)):
                raise E1ConfirmationCanonicalProbeHandoffError(
                    f"{role} is not SHA-256"
                )
        if self.binding_digest != _BINDING_DIGEST:
            raise E1ConfirmationCanonicalProbeHandoffError(
                "S1-EB11 canonical binding changed"
            )
        expected_ids = tuple(item[0] for item in S1_EB_REFINEMENTS)
        if (
            self.refinements != S1_EB_REFINEMENTS
            or tuple(role for role, _ in self.formation_result_digests)
            != expected_ids
            or tuple(role for role, _, _ in self.formation_state_digests)
            != expected_ids
            or tuple(role for role, _ in self.probe_plan_digests)
            != expected_ids
        ):
            raise E1ConfirmationCanonicalProbeHandoffError(
                "S1-EB11 refinement handoff inventory changed"
            )
        nested_digests = (
            *(value for _, value in self.formation_result_digests),
            *(
                value
                for _, ab_digest, ba_digest in self.formation_state_digests
                for value in (ab_digest, ba_digest)
            ),
            *(value for _, value in self.probe_plan_digests),
        )
        if any(not _valid_digest(value) for value in nested_digests):
            raise E1ConfirmationCanonicalProbeHandoffError(
                "S1-EB11 contains an invalid nested digest"
            )
        if (
            self.probe_entrypoint
            != "run_e1_confirmation_canonical_seven_arm_probe"
            or self.handoff_bound is not True
            or any(
                value is not False
                for value in (
                    self.probe_execution_permitted,
                    self.decision_permitted,
                    self.persistence_permitted,
                    self.claims_permitted,
                )
            )
        ):
            raise E1ConfirmationCanonicalProbeHandoffError(
                "S1-EB11 execution, decision, persistence, or claims opened"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "handoff_digest"
        }
        if self.handoff_digest != _digest(payload):
            raise E1ConfirmationCanonicalProbeHandoffError(
                "S1-EB11 handoff digest does not match its payload"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


def _canonical_probe_binding(chain_contract: E1ConfirmationChainContract):
    corridor = build_e1_refined_confirmation_contract(
        Path(chain_contract.report_path).parent,
        Path(chain_contract.upstream_report_path),
    )
    source = _fixed_probe_sequences()
    plans = build_e1_confirmation_refinement_plans(
        corridor,
        source,
        horizon_start_tick=0,
        horizon_end_tick=1_000_000,
        ticks_per_second=1_000_000.0,
    )
    return corridor, source, plans


def prepare_e1_confirmation_canonical_probe_handoff(
    binding: E1ConfirmationCanonicalProducerBinding,
    chain_contract: E1ConfirmationChainContract,
    formation: E1ConfirmationCanonicalFormationProduction,
) -> E1ConfirmationCanonicalProbeHandoff:
    """Bind formed states to canonical probe plans without running a probe."""

    if not isinstance(binding, E1ConfirmationCanonicalProducerBinding) or (
        binding.digest() != _BINDING_DIGEST
    ):
        raise E1ConfirmationCanonicalProbeHandoffError(
            "S1-EB11 requires the unchanged S1-EB9 binding"
        )
    if not isinstance(chain_contract, E1ConfirmationChainContract) or (
        chain_contract.digest() != binding.chain_contract_digest
    ):
        raise E1ConfirmationCanonicalProbeHandoffError(
            "S1-EB11 requires the bound S1-EB4 chain contract"
        )
    if not isinstance(formation, E1ConfirmationCanonicalFormationProduction):
        raise E1ConfirmationCanonicalProbeHandoffError(
            "S1-EB11 requires one S1-EB10 formation production"
        )
    if (
        formation.binding_digest != binding.digest()
        or formation.chain_contract_digest != chain_contract.digest()
        or formation.ab_plan_digest != binding.ab_plan_digest
        or formation.ba_plan_digest != binding.ba_plan_digest
        or formation.initial_field_digest != binding.initial_field_digest
        or formation.initial_state_digest != binding.initial_state_digest
    ):
        raise E1ConfirmationCanonicalProbeHandoffError(
            "S1-EB11 formation does not match its canonical binding"
        )
    corridor, probe_source, probe_plans = _canonical_probe_binding(
        chain_contract
    )
    if (
        corridor.digest() != chain_contract.confirmation_contract_digest
        or _probe_digest(probe_source) != binding.probe_digest
        or probe_plans.digest() != binding.probe_plan_digest
    ):
        raise E1ConfirmationCanonicalProbeHandoffError(
            "S1-EB11 canonical probe source or plans changed"
        )
    formed = tuple(formation.refinements)
    plans = tuple(probe_plans.plans)
    if tuple(
        (item.refinement_id, item.factor) for item in formed
    ) != S1_EB_REFINEMENTS or tuple(
        (item.refinement_id, item.factor) for item in plans
    ) != S1_EB_REFINEMENTS:
        raise E1ConfirmationCanonicalProbeHandoffError(
            "S1-EB11 formation and probe refinements do not align"
        )
    values = {
        "handoff_id": "e1.confirmation-probe-handoff.s1eb11.v1",
        "binding_digest": binding.digest(),
        "chain_contract_digest": chain_contract.digest(),
        "formation_production_digest": formation.production_digest,
        "formation_result_digests": tuple(
            (item.refinement_id, item.result_digest) for item in formed
        ),
        "formation_state_digests": tuple(
            (
                item.refinement_id,
                _state_digest(item.b_ab),
                _state_digest(item.b_ba),
            )
            for item in formed
        ),
        "probe_source_digest": _probe_digest(probe_source),
        "probe_plan_set_digest": probe_plans.digest(),
        "probe_plan_digests": tuple(
            (item.refinement_id, item.digest()) for item in plans
        ),
        "refinements": S1_EB_REFINEMENTS,
        "probe_entrypoint": "run_e1_confirmation_canonical_seven_arm_probe",
        "handoff_bound": True,
        "probe_execution_permitted": False,
        "decision_permitted": False,
        "persistence_permitted": False,
        "claims_permitted": False,
    }
    return E1ConfirmationCanonicalProbeHandoff(
        **values,
        handoff_digest=_digest(values),
    )
