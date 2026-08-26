"""Private S1-DU canonical AB/BA preflight without E1 or field execution."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from .e1_av_history_permutation import build_e1_av_history_permutation
from .e1_completion_aligned_refinement import (
    build_e1_completion_aligned_refinement_plans,
)
from .e1_refined_world_formation_contract import (
    build_e1_refined_world_formation_contract,
)


class E1CanonicalRefinementPreflightError(ValueError):
    """Raised when canonical AB/BA refinement evidence is no longer exact."""


S1_DS_CONTRACT_DIGEST = (
    "de996ac492af3808499b222687ac92d6f2110eda34743cc65d623ee3d924cbd7"
)
S1_DT_IMPLEMENTATION_DIGEST = (
    "accfe0a2ded04203785f217c6e93d3d5fbd1d46f377d4e9142b3eebd8ee59084"
)
S1_DU_AB_PLAN_DIGEST = (
    "5657cb57c136a6093275f41278a1fe261ccb6b806803bdf33086e14a697adb9b"
)
S1_DU_BA_PLAN_DIGEST = (
    "2c0406398d6bc38b508844ae8d1face022630ea2d85297f0dab994e87d2d761c"
)
S1_DU_STEP_COUNTS = (("r1", 200), ("r2", 400), ("r4", 800))


def _digest(value: object) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def current_s1_dt_implementation_digest() -> str:
    path = Path(__file__).with_name("e1_completion_aligned_refinement.py")
    if not path.is_file():
        raise E1CanonicalRefinementPreflightError(
            "S1-DT implementation is missing"
        )
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class E1CanonicalRefinementPreflight:
    preflight_id: str
    s1_ds_contract_digest: str
    s1_dt_implementation_digest: str
    ab_plan_digest: str
    ba_plan_digest: str
    ab_source_contact_digest: str
    ba_source_contact_digest: str
    completion_ticks_digest: str
    source_event_count_per_history: int
    completion_count_per_history: int
    step_counts: tuple[tuple[str, int], ...]
    source_signed_integral: float
    source_absolute_integral: float
    source_quadratic_integral: float
    payload_inventories_equal: bool
    support_inventories_equal: bool
    organism_slot_inventories_equal: bool
    completion_ticks_equal: bool
    step_grids_equal: bool
    contact_integrals_equal: bool
    ordered_contact_paths_different: bool
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
        if self.preflight_id != "e1.canonical-refinement-preflight.s1du.v1":
            raise E1CanonicalRefinementPreflightError(
                "S1-DU preflight identity changed"
            )
        if (
            self.s1_ds_contract_digest != S1_DS_CONTRACT_DIGEST
            or self.s1_dt_implementation_digest != S1_DT_IMPLEMENTATION_DIGEST
            or self.s1_dt_implementation_digest
            != current_s1_dt_implementation_digest()
        ):
            raise E1CanonicalRefinementPreflightError(
                "S1-DS contract or S1-DT implementation changed"
            )
        if (
            self.ab_plan_digest != S1_DU_AB_PLAN_DIGEST
            or self.ba_plan_digest != S1_DU_BA_PLAN_DIGEST
            or self.ab_plan_digest == self.ba_plan_digest
        ):
            raise E1CanonicalRefinementPreflightError(
                "S1-DU canonical plan binding changed"
            )
        for role in (
            "ab_source_contact_digest",
            "ba_source_contact_digest",
            "completion_ticks_digest",
        ):
            value = getattr(self, role)
            if len(value) != 64 or any(
                char not in "0123456789abcdef" for char in value
            ):
                raise E1CanonicalRefinementPreflightError(
                    f"{role} is not SHA-256"
                )
        if self.ab_source_contact_digest == self.ba_source_contact_digest:
            raise E1CanonicalRefinementPreflightError(
                "S1-DU lost the ordered AB/BA contact difference"
            )
        if (
            self.source_event_count_per_history != 220
            or self.completion_count_per_history != 200
            or self.step_counts != S1_DU_STEP_COUNTS
        ):
            raise E1CanonicalRefinementPreflightError(
                "S1-DU canonical event or step inventory changed"
            )
        expected_integrals = (
            14.328373475671894,
            14.328373475671894,
            3.293282702508704,
        )
        if (
            self.source_signed_integral,
            self.source_absolute_integral,
            self.source_quadratic_integral,
        ) != expected_integrals:
            raise E1CanonicalRefinementPreflightError(
                "S1-DU canonical contact integral changed"
            )
        required = (
            self.payload_inventories_equal,
            self.support_inventories_equal,
            self.organism_slot_inventories_equal,
            self.completion_ticks_equal,
            self.step_grids_equal,
            self.contact_integrals_equal,
            self.ordered_contact_paths_different,
            self.implementation_permitted,
        )
        if any(value is not True for value in required):
            raise E1CanonicalRefinementPreflightError(
                "S1-DU required canonical invariant failed"
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
            raise E1CanonicalRefinementPreflightError(
                "S1-DU cannot release execution, reruns, or strong claims"
            )

    def digest(self) -> str:
        return _digest(
            {name: getattr(self, name) for name in self.__dataclass_fields__}
        )


def _step_grid(plan) -> tuple[tuple[int, int], ...]:
    return tuple(
        (step.start_tick, step.end_tick)
        for refinement in plan.plans
        for step in refinement.proposal_steps
    )


def prepare_e1_canonical_refinement_preflight(
    transfer_report_path: Path,
) -> E1CanonicalRefinementPreflight:
    """Bind canonical source plans without advancing a field or E1 state."""

    contract = build_e1_refined_world_formation_contract(transfer_report_path)
    if contract.digest() != S1_DS_CONTRACT_DIGEST:
        raise E1CanonicalRefinementPreflightError(
            "published S1-DS contract changed"
        )
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
    audits = source.modality_audits
    integrals_equal = all(
        (
            left.source_signed_integral,
            left.source_absolute_integral,
            left.source_quadratic_integral,
        )
        == (
            right.source_signed_integral,
            right.source_absolute_integral,
            right.source_quadratic_integral,
        )
        for left, right in zip(ab.plans, ba.plans, strict=True)
    )
    return E1CanonicalRefinementPreflight(
        preflight_id="e1.canonical-refinement-preflight.s1du.v1",
        s1_ds_contract_digest=contract.digest(),
        s1_dt_implementation_digest=current_s1_dt_implementation_digest(),
        ab_plan_digest=ab.digest(),
        ba_plan_digest=ba.digest(),
        ab_source_contact_digest=ab.source_contact_digest,
        ba_source_contact_digest=ba.source_contact_digest,
        completion_ticks_digest=_digest(ab.completion_ticks),
        source_event_count_per_history=ab.source_event_count,
        completion_count_per_history=len(ab.completion_ticks),
        step_counts=tuple(
            (item.refinement_id, len(item.proposal_steps))
            for item in ab.plans
        ),
        source_signed_integral=ab.plans[0].source_signed_integral,
        source_absolute_integral=ab.plans[0].source_absolute_integral,
        source_quadratic_integral=ab.plans[0].source_quadratic_integral,
        payload_inventories_equal=all(
            item.payload_inventory_digest
            == item.permuted_payload_inventory_digest
            for item in audits
        ),
        support_inventories_equal=all(
            item.source_support_inventory_digest
            == item.permuted_source_support_inventory_digest
            for item in audits
        ),
        organism_slot_inventories_equal=all(
            item.organism_slot_inventory_digest
            == item.permuted_organism_slot_inventory_digest
            for item in audits
        ),
        completion_ticks_equal=(ab.completion_ticks == ba.completion_ticks),
        step_grids_equal=(_step_grid(ab) == _step_grid(ba)),
        contact_integrals_equal=integrals_equal,
        ordered_contact_paths_different=(
            ab.source_contact_digest != ba.source_contact_digest
        ),
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
