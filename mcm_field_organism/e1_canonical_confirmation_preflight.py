"""Private S1-EB2 nonexecuting canonical r2/r4/r8 preflight."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
from pathlib import Path

from .e1_av_history_permutation import build_e1_av_history_permutation
from .e1_confirmation_refinement_planner import (
    build_e1_confirmation_refinement_plans,
)
from .e1_frozen_state_transfer_contract import (
    _fixed_probe_sequences,
    _probe_digest,
)
from .e1_refined_confirmation_contract import (
    build_e1_refined_confirmation_contract,
)
from .e1_refined_world_formation_contract import S1_DS_PROBE_DIGEST


class E1CanonicalConfirmationPreflightError(ValueError):
    """Raised when S1-EB2 canonical planning evidence changed."""


S1_EB_CONTRACT_DIGEST = (
    "bccf552b7ea69cc083cf65ac0a7d3faacfe7939ff8c7d13c4614f1cf42d06fb4"
)
S1_EB1_IMPLEMENTATION_DIGEST = (
    "cf50c5757e420a6ad8c84b248b41ccf2028c90c7a1116a8f4e3b377453215731"
)
S1_EB2_AB_PLAN_DIGEST = (
    "1137a456cfceef385112deb26de662294dea2a4b95a2df0d9dc73ff8620a24e5"
)
S1_EB2_BA_PLAN_DIGEST = (
    "071b4504dc11eadadeb5d5895775dd6bc076d00d937a3d62372fb958b929fc8d"
)
S1_EB2_PROBE_PLAN_DIGEST = (
    "f78b5866d2629cb781f47ad8d622bf4260a67dacc43cfb52366a33d5790ca6b4"
)


def _normalized_source_digest(name: str) -> str:
    path = Path(__file__).with_name(name)
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class E1CanonicalConfirmationPreflight:
    preflight_id: str
    contract_digest: str
    planner_implementation_digest: str
    history_ab_digest: str
    history_ba_digest: str
    permutation_digest: str
    probe_digest: str
    ab_plan_digest: str
    ba_plan_digest: str
    probe_plan_digest: str
    ab_source_contact_digest: str
    ba_source_contact_digest: str
    probe_source_contact_digest: str
    ab_handoff_digest: str
    ba_handoff_digest: str
    probe_handoff_digest: str
    history_source_support_count: int
    probe_source_support_count: int
    history_completion_count: int
    probe_completion_count: int
    history_step_counts: tuple[tuple[str, int], ...]
    probe_step_counts: tuple[tuple[str, int], ...]
    history_signed_integral: float
    history_absolute_integral: float
    history_quadratic_integral: float
    probe_signed_integral: float
    probe_absolute_integral: float
    probe_quadratic_integral: float
    ab_ba_inventories_equal: bool
    ab_ba_completion_ticks_equal: bool
    ab_ba_contact_integrals_equal: bool
    ordered_ab_ba_paths_different: bool
    handoffs_refinement_invariant: bool
    runner_implementation_permitted: bool
    execution_permitted: bool
    execution_started: bool
    s1_ea6_rerun_permitted: bool
    memory_claim_permitted: bool
    ai_claim_permitted: bool

    def __post_init__(self) -> None:
        if self.preflight_id != "e1.canonical-confirmation-preflight.s1eb2.v1":
            raise E1CanonicalConfirmationPreflightError(
                "S1-EB2 preflight identity changed"
            )
        if (
            self.contract_digest != S1_EB_CONTRACT_DIGEST
            or self.planner_implementation_digest != S1_EB1_IMPLEMENTATION_DIGEST
            or self.planner_implementation_digest
            != _normalized_source_digest("e1_confirmation_refinement_planner.py")
        ):
            raise E1CanonicalConfirmationPreflightError(
                "S1-EB2 contract or planner binding changed"
            )
        for role in (
            "history_ab_digest",
            "history_ba_digest",
            "permutation_digest",
            "probe_digest",
            "ab_plan_digest",
            "ba_plan_digest",
            "probe_plan_digest",
            "ab_source_contact_digest",
            "ba_source_contact_digest",
            "probe_source_contact_digest",
            "ab_handoff_digest",
            "ba_handoff_digest",
            "probe_handoff_digest",
        ):
            value = getattr(self, role)
            if len(value) != 64 or any(
                char not in "0123456789abcdef" for char in value
            ):
                raise E1CanonicalConfirmationPreflightError(
                    f"{role} is not SHA-256"
                )
        if (
            self.probe_digest != S1_DS_PROBE_DIGEST
            or self.ab_plan_digest != S1_EB2_AB_PLAN_DIGEST
            or self.ba_plan_digest != S1_EB2_BA_PLAN_DIGEST
            or self.probe_plan_digest != S1_EB2_PROBE_PLAN_DIGEST
        ):
            raise E1CanonicalConfirmationPreflightError(
                "S1-EB2 source probe or plan binding changed"
            )
        if (
            self.history_source_support_count,
            self.probe_source_support_count,
            self.history_completion_count,
            self.probe_completion_count,
        ) != (220, 110, 200, 100):
            raise E1CanonicalConfirmationPreflightError(
                "S1-EB2 support or completion inventory changed"
            )
        if self.history_step_counts != (
            ("r2", 400), ("r4", 800), ("r8", 1600)
        ) or self.probe_step_counts != (
            ("r2", 200), ("r4", 400), ("r8", 800)
        ):
            raise E1CanonicalConfirmationPreflightError(
                "S1-EB2 step inventory changed"
            )
        if (
            self.history_signed_integral,
            self.history_absolute_integral,
            self.history_quadratic_integral,
        ) != (14.328373475671894, 14.328373475671894, 3.293282702508704):
            raise E1CanonicalConfirmationPreflightError(
                "S1-EB2 history contact integral changed"
            )
        if (
            self.probe_signed_integral,
            self.probe_absolute_integral,
            self.probe_quadratic_integral,
        ) != (6.941865469153374, 6.941865469153374, 1.512406472248469):
            raise E1CanonicalConfirmationPreflightError(
                "S1-EB2 probe contact integral changed"
            )
        if any(
            value is not True
            for value in (
                self.ab_ba_inventories_equal,
                self.ab_ba_completion_ticks_equal,
                self.ab_ba_contact_integrals_equal,
                self.ordered_ab_ba_paths_different,
                self.handoffs_refinement_invariant,
                self.runner_implementation_permitted,
            )
        ):
            raise E1CanonicalConfirmationPreflightError(
                "S1-EB2 required invariant or next implementation gate failed"
            )
        if any(
            value is not False
            for value in (
                self.execution_permitted,
                self.execution_started,
                self.s1_ea6_rerun_permitted,
                self.memory_claim_permitted,
                self.ai_claim_permitted,
            )
        ):
            raise E1CanonicalConfirmationPreflightError(
                "S1-EB2 cannot execute, rerun S1-EA6, or permit claims"
            )


def prepare_e1_canonical_confirmation_preflight(
    report_directory: Path,
    upstream_report_path: Path,
) -> E1CanonicalConfirmationPreflight:
    """Plan canonical sources without constructing or advancing a field."""

    contract = build_e1_refined_confirmation_contract(
        report_directory, upstream_report_path
    )
    source = build_e1_av_history_permutation()
    probe = _fixed_probe_sequences()
    ab = build_e1_confirmation_refinement_plans(
        contract, source.history_ab,
        horizon_start_tick=0, horizon_end_tick=2_000_000,
        ticks_per_second=1_000_000.0,
    )
    ba = build_e1_confirmation_refinement_plans(
        contract, source.history_ba,
        horizon_start_tick=0, horizon_end_tick=2_000_000,
        ticks_per_second=1_000_000.0,
    )
    probe_plans = build_e1_confirmation_refinement_plans(
        contract, probe,
        horizon_start_tick=0, horizon_end_tick=1_000_000,
        ticks_per_second=1_000_000.0,
    )
    audits = source.modality_audits
    history_integrals_equal = all(
        (
            left.source_signed_integral,
            left.source_absolute_integral,
            left.source_quadratic_integral,
        ) == (
            right.source_signed_integral,
            right.source_absolute_integral,
            right.source_quadratic_integral,
        )
        for left, right in zip(ab.plans, ba.plans, strict=True)
    )
    return E1CanonicalConfirmationPreflight(
        preflight_id="e1.canonical-confirmation-preflight.s1eb2.v1",
        contract_digest=contract.digest(),
        planner_implementation_digest=_normalized_source_digest(
            "e1_confirmation_refinement_planner.py"
        ),
        history_ab_digest=source.history_ab_digest,
        history_ba_digest=source.history_ba_digest,
        permutation_digest=source.permutation_digest,
        probe_digest=_probe_digest(probe),
        ab_plan_digest=ab.digest(),
        ba_plan_digest=ba.digest(),
        probe_plan_digest=probe_plans.digest(),
        ab_source_contact_digest=ab.source_contact_digest,
        ba_source_contact_digest=ba.source_contact_digest,
        probe_source_contact_digest=probe_plans.source_contact_digest,
        ab_handoff_digest=ab.plans[0].handoff_digest,
        ba_handoff_digest=ba.plans[0].handoff_digest,
        probe_handoff_digest=probe_plans.plans[0].handoff_digest,
        history_source_support_count=ab.source_event_count,
        probe_source_support_count=probe_plans.source_event_count,
        history_completion_count=len(ab.completion_ticks),
        probe_completion_count=len(probe_plans.completion_ticks),
        history_step_counts=tuple(
            (item.refinement_id, len(item.proposal_steps)) for item in ab.plans
        ),
        probe_step_counts=tuple(
            (item.refinement_id, len(item.proposal_steps))
            for item in probe_plans.plans
        ),
        history_signed_integral=ab.plans[0].source_signed_integral,
        history_absolute_integral=ab.plans[0].source_absolute_integral,
        history_quadratic_integral=ab.plans[0].source_quadratic_integral,
        probe_signed_integral=probe_plans.plans[0].source_signed_integral,
        probe_absolute_integral=probe_plans.plans[0].source_absolute_integral,
        probe_quadratic_integral=probe_plans.plans[0].source_quadratic_integral,
        ab_ba_inventories_equal=all(
            audit.payload_inventory_digest == audit.permuted_payload_inventory_digest
            and audit.source_support_inventory_digest
            == audit.permuted_source_support_inventory_digest
            and audit.organism_slot_inventory_digest
            == audit.permuted_organism_slot_inventory_digest
            for audit in audits
        ),
        ab_ba_completion_ticks_equal=(ab.completion_ticks == ba.completion_ticks),
        ab_ba_contact_integrals_equal=history_integrals_equal,
        ordered_ab_ba_paths_different=(
            ab.source_contact_digest != ba.source_contact_digest
            and ab.plans[0].handoff_digest != ba.plans[0].handoff_digest
            and ab.digest() != ba.digest()
        ),
        handoffs_refinement_invariant=(
            len({item.handoff_digest for item in ab.plans}) == 1
            and len({item.handoff_digest for item in ba.plans}) == 1
            and len({item.handoff_digest for item in probe_plans.plans}) == 1
        ),
        runner_implementation_permitted=True,
        execution_permitted=False,
        execution_started=False,
        s1_ea6_rerun_permitted=False,
        memory_claim_permitted=False,
        ai_claim_permitted=False,
    )
