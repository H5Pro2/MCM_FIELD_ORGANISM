"""S1-EC80 in-memory r2 contrast and scalar receipt contract."""

from __future__ import annotations

from dataclasses import dataclass
import math

from .e1_common_probe_identifiability_contract import (
    S1_EC45_PROBE_ROLES,
    S1_EC45_REQUIRED_CONTRASTS,
)
from .e1_common_probe_n2_r2_ec79_static_evaluation_contract import (
    E1CommonProbeN2R2EC79StaticEvaluationContract,
)
from .e1_common_probe_n2_r2_positive_step_receipt_contract import (
    E1PositiveStepProbeReceipt,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeR2EC80ScalarContractError(ValueError):
    """Raised when EC80 receives an incomplete or changed r2 receipt set."""


S1_EC80_CONTRACT_ID = "e1.common-probe-r2-scalars.s1ec80.v1"
S1_EC80_EC79_CONTRACT_DIGEST = (
    "c8dcddaa12420bef5af40e98fc831372ee94465ca8e721520aa7d489ce760c49"
)
S1_EC80_CONTRAST_ROLE_PAIRS = (
    ("p0-reset-order", "p0-reset-ab", "p0-reset-ba"),
    ("e1-active-order", "e1-active-ab", "e1-active-ba"),
    (
        "e1-probe-feedback-ablated-order",
        "e1-probe-feedback-ablated-ab",
        "e1-probe-feedback-ablated-ba",
    ),
    (
        "e1-formation-ablated-order",
        "e1-formation-ablated-ab",
        "e1-formation-ablated-ba",
    ),
    (
        "ab-active-vs-probe-feedback-ablated",
        "e1-active-ab",
        "e1-probe-feedback-ablated-ab",
    ),
    (
        "ba-active-vs-probe-feedback-ablated",
        "e1-active-ba",
        "e1-probe-feedback-ablated-ba",
    ),
)


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


def _linf_difference(
    left: tuple[float, ...], right: tuple[float, ...]
) -> float:
    if not left or len(left) != len(right):
        raise E1CommonProbeR2EC80ScalarContractError(
            "S1-EC80 requires equal nonempty probe vectors"
        )
    value = max(abs(a - b) for a, b in zip(left, right, strict=True))
    if not math.isfinite(value):
        raise E1CommonProbeR2EC80ScalarContractError(
            "S1-EC80 requires finite probe contrasts"
        )
    return value


@dataclass(frozen=True, slots=True)
class E1CommonProbeR2EC80ScalarReceipt:
    contract_id: str
    source_ec79_contract_digest: str
    source_result_digest: str
    source_probe_receipt_digests: tuple[str, ...]
    refinement_id: str
    roles: tuple[str, ...]
    metric_components: tuple[str, ...]
    contrast_scalars: tuple[tuple[str, float, float], ...]
    probe_count: int
    all_roles_exact_once: bool
    raw_probe_vectors_persisted: bool
    field_execution_performed: bool
    ec46_decision_permitted: bool
    research_decision_permitted: bool
    claims_permitted: bool
    decision: str
    receipt_digest: str

    def __post_init__(self) -> None:
        scalar_names = tuple(item[0] for item in self.contrast_scalars)
        scalar_values = tuple(
            value for _, activation, afterimage in self.contrast_scalars
            for value in (activation, afterimage)
        )
        if (
            self.contract_id != S1_EC80_CONTRACT_ID
            or self.source_ec79_contract_digest != S1_EC80_EC79_CONTRACT_DIGEST
            or not _valid_digest(self.source_result_digest)
            or len(self.source_probe_receipt_digests) != 8
            or not all(_valid_digest(item) for item in self.source_probe_receipt_digests)
            or self.refinement_id != "r2"
            or self.roles != S1_EC45_PROBE_ROLES
            or self.metric_components != ("activation", "afterimage")
            or scalar_names != S1_EC45_REQUIRED_CONTRASTS
            or not all(math.isfinite(value) and value >= 0.0 for value in scalar_values)
            or self.probe_count != 8
            or self.all_roles_exact_once is not True
            or any(
                value is not False
                for value in (
                    self.raw_probe_vectors_persisted,
                    self.field_execution_performed,
                    self.ec46_decision_permitted,
                    self.research_decision_permitted,
                    self.claims_permitted,
                )
            )
            or self.decision != "R2_SCALARS_COMPUTED_EC46_DECISION_BLOCKED"
        ):
            raise E1CommonProbeR2EC80ScalarContractError(
                "S1-EC80 scalar receipt changed or crossed its scope"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "receipt_digest"
        }
        if self.receipt_digest != _digest(payload):
            raise E1CommonProbeR2EC80ScalarContractError(
                "S1-EC80 scalar receipt digest changed"
            )


def build_e1_common_probe_r2_ec80_scalar_receipt(
    boundary: E1CommonProbeN2R2EC79StaticEvaluationContract,
    probes: tuple[E1PositiveStepProbeReceipt, ...],
    *,
    source_result_digest: str,
) -> E1CommonProbeR2EC80ScalarReceipt:
    """Reduce eight existing r2 receipts without running a field or deciding EC46."""

    if not isinstance(boundary, E1CommonProbeN2R2EC79StaticEvaluationContract):
        raise E1CommonProbeR2EC80ScalarContractError(
            "S1-EC80 requires the typed EC79 boundary"
        )
    boundary.__post_init__()
    if boundary.contract_digest != S1_EC80_EC79_CONTRACT_DIGEST:
        raise E1CommonProbeR2EC80ScalarContractError(
            "S1-EC80 EC79 binding changed"
        )
    receipts = tuple(probes)
    if (
        tuple(item.role_id for item in receipts if isinstance(item, E1PositiveStepProbeReceipt))
        != S1_EC45_PROBE_ROLES
        or len(receipts) != 8
        or not _valid_digest(source_result_digest)
    ):
        raise E1CommonProbeR2EC80ScalarContractError(
            "S1-EC80 requires all eight ordered r2 probe receipts"
        )
    for item in receipts:
        item.__post_init__()

    by_role = {item.role_id: item for item in receipts}
    contrast_scalars = tuple(
        (
            name,
            _linf_difference(by_role[left].activation, by_role[right].activation),
            _linf_difference(by_role[left].afterimage, by_role[right].afterimage),
        )
        for name, left, right in S1_EC80_CONTRAST_ROLE_PAIRS
    )
    values = {
        "contract_id": S1_EC80_CONTRACT_ID,
        "source_ec79_contract_digest": boundary.contract_digest,
        "source_result_digest": source_result_digest,
        "source_probe_receipt_digests": tuple(item.receipt_digest for item in receipts),
        "refinement_id": "r2",
        "roles": tuple(item.role_id for item in receipts),
        "metric_components": ("activation", "afterimage"),
        "contrast_scalars": contrast_scalars,
        "probe_count": len(receipts),
        "all_roles_exact_once": len(by_role) == 8,
        "raw_probe_vectors_persisted": False,
        "field_execution_performed": False,
        "ec46_decision_permitted": False,
        "research_decision_permitted": False,
        "claims_permitted": False,
        "decision": "R2_SCALARS_COMPUTED_EC46_DECISION_BLOCKED",
    }
    return E1CommonProbeR2EC80ScalarReceipt(
        **values,
        receipt_digest=_digest(values),
    )
