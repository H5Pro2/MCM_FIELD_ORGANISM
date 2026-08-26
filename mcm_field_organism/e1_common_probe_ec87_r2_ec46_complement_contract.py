"""S1-EC87 static EC46 placement of EC86 r2 and closed r4/r8 complement."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path

from .e1_common_probe_acceptance_contract import (
    E1CommonProbeAcceptanceContract,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeEC87R2EC46ComplementContractError(ValueError):
    """Raised when EC87 invents missing refinement evidence or permits execution."""


S1_EC87_CONTRACT_ID = "e1.common-probe-r2-ec46-complement.s1ec87.v1"
S1_EC87_EC46_CONTRACT_DIGEST = (
    "672239cddf2a1e8a8856a5bd2570ebaf0a9bdda5f52fb45aa0306e2570dd144b"
)
S1_EC87_EC86_REPORT_RELATIVE_PATH = (
    "docs/S1EC86_AUTORISIERTER_R2_MESSLAUF_MIT_ATOMARER_RUECKGABE.md"
)
S1_EC87_EC86_REPORT_SHA256 = (
    "31fdcc25c9fd2626451263bf908da8b403951ec721f862d1748b8fd478e25141"
)
S1_EC87_EC86_SCALAR_RECEIPT_DIGEST = (
    "4bad7002743248df059899a65fa9343ffbb16c3bdd0c686c8d4e5cf14053ba59"
)
S1_EC87_R2_SCALARS = (
    ("p0-reset-order", 0.0, 0.0),
    ("e1-active-order", 1.557374244509635e-06, 9.359585484425281e-07),
    ("e1-probe-feedback-ablated-order", 0.0, 0.0),
    ("e1-formation-ablated-order", 0.0, 0.0),
    (
        "ab-active-vs-probe-feedback-ablated",
        2.8709257103076702e-05,
        1.7290444112694203e-05,
    ),
    (
        "ba-active-vs-probe-feedback-ablated",
        3.0266631347586337e-05,
        1.822640266113673e-05,
    ),
)
S1_EC87_MISSING_EC46_INPUTS = (
    "r4-active-order-activation-vector",
    "r4-active-order-afterimage-vector",
    "r8-active-order-activation-vector",
    "r8-active-order-afterimage-vector",
    "coarse-r2-r4-activation-linf",
    "coarse-r2-r4-afterimage-linf",
    "fine-r4-r8-activation-linf",
    "fine-r4-r8-afterimage-linf",
    "maximum-r2-r4-r8-null-controls",
)


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC87R2EC46ComplementContract:
    contract_id: str
    source_ec46_contract_digest: str
    source_ec86_report_sha256: str
    source_ec86_scalar_receipt_digest: str
    available_refinement_levels: tuple[str, ...]
    missing_refinement_levels: tuple[str, ...]
    r2_scalars: tuple[tuple[str, float, float], ...]
    absolute_control_tolerance: float
    r2_null_controls_within_tolerance: bool
    r2_active_order_above_absolute_tolerance: bool
    missing_ec46_inputs: tuple[str, ...]
    complement_probe_roles_per_refinement: int
    complement_scalar_contrasts_per_refinement: int
    identical_probe_and_observation_space_required: bool
    fresh_field_per_probe_required: bool
    atomic_scalar_return_required: bool
    posthoc_threshold_change_permitted: bool
    field_execution_permitted: bool
    owner_authorization_present: bool
    ec46_decision_permitted: bool
    research_decision_permitted: bool
    claims_permitted: bool
    decision: str
    reason: str
    contract_digest: str

    def __post_init__(self) -> None:
        if (
            self.contract_id != S1_EC87_CONTRACT_ID
            or self.source_ec46_contract_digest != S1_EC87_EC46_CONTRACT_DIGEST
            or self.source_ec86_report_sha256 != S1_EC87_EC86_REPORT_SHA256
            or self.source_ec86_scalar_receipt_digest
            != S1_EC87_EC86_SCALAR_RECEIPT_DIGEST
            or self.available_refinement_levels != ("r2",)
            or self.missing_refinement_levels != ("r4", "r8")
            or self.r2_scalars != S1_EC87_R2_SCALARS
            or self.absolute_control_tolerance != 1e-12
            or self.r2_null_controls_within_tolerance is not True
            or self.r2_active_order_above_absolute_tolerance is not True
            or self.missing_ec46_inputs != S1_EC87_MISSING_EC46_INPUTS
            or (
                self.complement_probe_roles_per_refinement,
                self.complement_scalar_contrasts_per_refinement,
            )
            != (8, 6)
            or any(
                value is not True
                for value in (
                    self.identical_probe_and_observation_space_required,
                    self.fresh_field_per_probe_required,
                    self.atomic_scalar_return_required,
                )
            )
            or any(
                value is not False
                for value in (
                    self.posthoc_threshold_change_permitted,
                    self.field_execution_permitted,
                    self.owner_authorization_present,
                    self.ec46_decision_permitted,
                    self.research_decision_permitted,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "R2_PARTIAL_EC46_INPUT_VALID_R4_R8_COMPLEMENT_REQUIRED"
            or not self.reason
        ):
            raise E1CommonProbeEC87R2EC46ComplementContractError(
                "S1-EC87 changed, invented evidence, or released execution"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "contract_digest"
        }
        if self.contract_digest != _digest(payload):
            raise E1CommonProbeEC87R2EC46ComplementContractError(
                "S1-EC87 contract digest changed"
            )


def build_e1_common_probe_ec87_r2_ec46_complement_contract(
    project_root: Path,
    acceptance: E1CommonProbeAcceptanceContract,
) -> E1CommonProbeEC87R2EC46ComplementContract:
    """Place retained r2 scalars without calling EC46 or executing refinements."""

    if not isinstance(acceptance, E1CommonProbeAcceptanceContract):
        raise E1CommonProbeEC87R2EC46ComplementContractError(
            "S1-EC87 requires the typed EC46 contract"
        )
    acceptance.__post_init__()
    if acceptance.contract_digest != S1_EC87_EC46_CONTRACT_DIGEST:
        raise E1CommonProbeEC87R2EC46ComplementContractError(
            "S1-EC87 EC46 binding changed"
        )
    report = Path(project_root) / S1_EC87_EC86_REPORT_RELATIVE_PATH
    try:
        report_sha256 = hashlib.sha256(report.read_bytes()).hexdigest()
    except OSError as exc:
        raise E1CommonProbeEC87R2EC46ComplementContractError(
            "S1-EC87 requires the exact EC86 report"
        ) from exc
    if report_sha256 != S1_EC87_EC86_REPORT_SHA256:
        raise E1CommonProbeEC87R2EC46ComplementContractError(
            "S1-EC87 EC86 report changed"
        )

    by_name = {name: (activation, afterimage) for name, activation, afterimage in S1_EC87_R2_SCALARS}
    null_controls = tuple(by_name[name] for name in acceptance.null_controls)
    active = by_name["e1-active-order"]
    values = {
        "contract_id": S1_EC87_CONTRACT_ID,
        "source_ec46_contract_digest": acceptance.contract_digest,
        "source_ec86_report_sha256": report_sha256,
        "source_ec86_scalar_receipt_digest": S1_EC87_EC86_SCALAR_RECEIPT_DIGEST,
        "available_refinement_levels": ("r2",),
        "missing_refinement_levels": ("r4", "r8"),
        "r2_scalars": S1_EC87_R2_SCALARS,
        "absolute_control_tolerance": acceptance.absolute_control_tolerance,
        "r2_null_controls_within_tolerance": all(
            component <= acceptance.absolute_control_tolerance
            for pair in null_controls
            for component in pair
        ),
        "r2_active_order_above_absolute_tolerance": all(
            component > acceptance.absolute_control_tolerance for component in active
        ),
        "missing_ec46_inputs": S1_EC87_MISSING_EC46_INPUTS,
        "complement_probe_roles_per_refinement": 8,
        "complement_scalar_contrasts_per_refinement": 6,
        "identical_probe_and_observation_space_required": True,
        "fresh_field_per_probe_required": True,
        "atomic_scalar_return_required": True,
        "posthoc_threshold_change_permitted": False,
        "field_execution_permitted": False,
        "owner_authorization_present": False,
        "ec46_decision_permitted": False,
        "research_decision_permitted": False,
        "claims_permitted": False,
        "decision": "R2_PARTIAL_EC46_INPUT_VALID_R4_R8_COMPLEMENT_REQUIRED",
        "reason": (
            "ec86-r2-controls-and-active-order-retained;ec46-active-input-is-r8;"
            "coarse-fine-and-cross-refinement-control-maxima-unavailable"
        ),
    }
    return E1CommonProbeEC87R2EC46ComplementContract(
        **values, contract_digest=_digest(values)
    )
