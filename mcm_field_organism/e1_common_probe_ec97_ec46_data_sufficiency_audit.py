"""S1-EC97 static EC46 data-sufficiency audit after the EC96 once-run."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path

from .e1_common_probe_acceptance_contract import E1CommonProbeAcceptanceContract
from .e1_common_probe_ec87_r2_ec46_complement_contract import S1_EC87_R2_SCALARS
from .e1_refined_formation_runner import _digest


class E1CommonProbeEC97EC46DataSufficiencyAuditError(ValueError):
    """Raised when EC97 invents vectors or opens another field run."""


S1_EC97_AUDIT_ID = "e1.common-probe-ec46-data-sufficiency.s1ec97.v1"
S1_EC97_EC46_CONTRACT_DIGEST = (
    "672239cddf2a1e8a8856a5bd2570ebaf0a9bdda5f52fb45aa0306e2570dd144b"
)
S1_EC97_EC96_REPORT = (
    "docs/S1EC96_AUTORISIERTER_R4_R8_EINMALLAUF_UND_ATOMARER_ROHBEFUND.md"
)
S1_EC97_EC96_REPORT_SHA256 = (
    "f7cac823198185d68838a21366b31220aa3c204957ea8336cccc2ab77d3a6e1e"
)
S1_EC97_R4_R8_ACTIVE_SCALARS = (
    ("r4", 1.3059210545174338e-06, 7.880146558336687e-07),
    ("r8", 1.1897795942905631e-06, 7.193309551900562e-07),
)
S1_EC97_REQUIRED_VECTOR_INPUTS = (
    "r2-active-order-activation-vector",
    "r2-active-order-afterimage-vector",
    "r4-active-order-activation-vector",
    "r4-active-order-afterimage-vector",
    "r8-active-order-activation-vector",
    "r8-active-order-afterimage-vector",
)


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC97EC46DataSufficiencyAudit:
    audit_id: str
    source_ec46_contract_digest: str
    source_ec96_report_sha256: str
    available_active_scalars: tuple[tuple[str, float, float], ...]
    available_maximum_controls: tuple[tuple[str, float, float], ...]
    required_vector_inputs: tuple[str, ...]
    available_vector_inputs: tuple[str, ...]
    missing_vector_inputs: tuple[str, ...]
    exact_coarse_distance_computable: bool
    exact_fine_distance_computable: bool
    ec46_decision_computable: bool
    scalar_norm_differences_are_valid_vector_distance_substitutes: bool
    previous_authorization_consumed: bool
    rerun_permitted: bool
    field_execution_permitted: bool
    posthoc_reconstruction_permitted: bool
    persistence_performed: bool
    claims_permitted: bool
    decision: str
    reason: str
    audit_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "audit_digest"
        }
        if (
            self.audit_id != S1_EC97_AUDIT_ID
            or self.source_ec46_contract_digest != S1_EC97_EC46_CONTRACT_DIGEST
            or self.source_ec96_report_sha256 != S1_EC97_EC96_REPORT_SHA256
            or tuple(item[0] for item in self.available_active_scalars)
            != ("r2", "r4", "r8")
            or self.available_maximum_controls
            != (
                ("p0-reset-order", 0.0, 0.0),
                ("e1-probe-feedback-ablated-order", 0.0, 0.0),
                ("e1-formation-ablated-order", 0.0, 0.0),
            )
            or self.required_vector_inputs != S1_EC97_REQUIRED_VECTOR_INPUTS
            or self.available_vector_inputs != ()
            or self.missing_vector_inputs != S1_EC97_REQUIRED_VECTOR_INPUTS
            or any(
                value is not False
                for value in (
                    self.exact_coarse_distance_computable,
                    self.exact_fine_distance_computable,
                    self.ec46_decision_computable,
                    self.scalar_norm_differences_are_valid_vector_distance_substitutes,
                    self.rerun_permitted,
                    self.field_execution_permitted,
                    self.posthoc_reconstruction_permitted,
                    self.persistence_performed,
                    self.claims_permitted,
                )
            )
            or self.previous_authorization_consumed is not True
            or self.decision != "STOP_EC46_RAW_ORDER_VECTORS_NOT_RETAINED"
            or not self.reason
            or self.audit_digest != _digest(payload)
        ):
            raise E1CommonProbeEC97EC46DataSufficiencyAuditError(
                "S1-EC97 changed, invented data, or opened execution"
            )


def audit_e1_common_probe_ec97_ec46_data_sufficiency(
    project_root: Path,
    contract: E1CommonProbeAcceptanceContract,
) -> E1CommonProbeEC97EC46DataSufficiencyAudit:
    """Audit retained values without reconstructing vectors or running fields."""

    if not isinstance(contract, E1CommonProbeAcceptanceContract):
        raise E1CommonProbeEC97EC46DataSufficiencyAuditError(
            "S1-EC97 requires the typed EC46 contract"
        )
    contract.__post_init__()
    if contract.contract_digest != S1_EC97_EC46_CONTRACT_DIGEST:
        raise E1CommonProbeEC97EC46DataSufficiencyAuditError(
            "S1-EC97 EC46 binding changed"
        )
    report = Path(project_root) / S1_EC97_EC96_REPORT
    try:
        report_sha256 = hashlib.sha256(report.read_bytes()).hexdigest()
    except OSError as exc:
        raise E1CommonProbeEC97EC46DataSufficiencyAuditError(
            "S1-EC97 requires the exact EC96 report"
        ) from exc
    if report_sha256 != S1_EC97_EC96_REPORT_SHA256:
        raise E1CommonProbeEC97EC46DataSufficiencyAuditError(
            "S1-EC97 EC96 report changed"
        )

    r2_active = next(item for item in S1_EC87_R2_SCALARS if item[0] == "e1-active-order")
    active = (("r2", r2_active[1], r2_active[2]),) + S1_EC97_R4_R8_ACTIVE_SCALARS
    values = {
        "audit_id": S1_EC97_AUDIT_ID,
        "source_ec46_contract_digest": contract.contract_digest,
        "source_ec96_report_sha256": report_sha256,
        "available_active_scalars": active,
        "available_maximum_controls": (
            ("p0-reset-order", 0.0, 0.0),
            ("e1-probe-feedback-ablated-order", 0.0, 0.0),
            ("e1-formation-ablated-order", 0.0, 0.0),
        ),
        "required_vector_inputs": S1_EC97_REQUIRED_VECTOR_INPUTS,
        "available_vector_inputs": (),
        "missing_vector_inputs": S1_EC97_REQUIRED_VECTOR_INPUTS,
        "exact_coarse_distance_computable": False,
        "exact_fine_distance_computable": False,
        "ec46_decision_computable": False,
        "scalar_norm_differences_are_valid_vector_distance_substitutes": False,
        "previous_authorization_consumed": True,
        "rerun_permitted": False,
        "field_execution_permitted": False,
        "posthoc_reconstruction_permitted": False,
        "persistence_performed": False,
        "claims_permitted": False,
        "decision": "STOP_EC46_RAW_ORDER_VECTORS_NOT_RETAINED",
        "reason": (
            "ec46-coarse-fine-require-active-order-difference-vectors;ec86-and-"
            "ec96-retain-only-linf-scalars;norm-differences-do-not-identify-"
            "vector-distances;ec96-authorization-consumed"
        ),
    }
    return E1CommonProbeEC97EC46DataSufficiencyAudit(
        **values, audit_digest=_digest(values)
    )
