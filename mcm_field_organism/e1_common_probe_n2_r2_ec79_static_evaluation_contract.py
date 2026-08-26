"""S1-EC79 static evaluation boundary for the completed EC78 run."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path

from .e1_common_probe_acceptance_contract import (
    E1CommonProbeAcceptanceContract,
    build_e1_common_probe_acceptance_contract,
)
from .e1_common_probe_identifiability_contract import (
    S1_EC45_REQUIRED_CONTRASTS,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeN2R2EC79StaticEvaluationContractError(ValueError):
    """Raised when EC79 loses its exact evidence or evaluation boundary."""


S1_EC79_CONTRACT_ID = "e1.common-probe-n2-r2-static-evaluation.s1ec79.v1"
S1_EC79_EC78_REPORT_RELATIVE_PATH = (
    "docs/S1EC78_AUTORISIERTER_N2_R2_DIAGNOSELAUF.md"
)
S1_EC79_EC78_REPORT_SHA256 = (
    "7b6842930c9117ab259090447bf21ff1336cb6ff0c92efdad9a02cd03ff24308"
)
S1_EC79_EC78_RESULT_DIGEST = (
    "94d7b93af4a73110526de3f3a9c2481162dacccfceef2dcfc4f703f7012197c5"
)
S1_EC79_EC46_CONTRACT_DIGEST = (
    "672239cddf2a1e8a8856a5bd2570ebaf0a9bdda5f52fb45aa0306e2570dd144b"
)


@dataclass(frozen=True, slots=True)
class E1CommonProbeN2R2EC79StaticEvaluationContract:
    contract_id: str
    source_ec78_report_sha256: str
    source_ec78_result_digest: str
    source_ec46_contract_digest: str
    evidence_scope: str
    completed_formation_count: int
    completed_fresh_field_count: int
    completed_probe_count: int
    completed_field_steps: int
    available_refinement_levels: tuple[str, ...]
    required_refinement_levels: tuple[str, ...]
    metric_components: tuple[str, ...]
    structurally_available_contrasts: tuple[str, ...]
    quantitative_probe_vectors_retained: bool
    ec46_scalar_inputs_available: bool
    result_object_reconstruction_permitted: bool
    field_execution_permitted: bool
    persistence_permitted: bool
    quantitative_decision_permitted: bool
    claims_permitted: bool
    decision: str
    reason: str
    contract_digest: str

    def __post_init__(self) -> None:
        if (
            self.contract_id != S1_EC79_CONTRACT_ID
            or self.source_ec78_report_sha256 != S1_EC79_EC78_REPORT_SHA256
            or self.source_ec78_result_digest != S1_EC79_EC78_RESULT_DIGEST
            or self.source_ec46_contract_digest != S1_EC79_EC46_CONTRACT_DIGEST
            or self.evidence_scope
            != "ec78-structural-completion-only-no-retained-probe-vectors"
            or (
                self.completed_formation_count,
                self.completed_fresh_field_count,
                self.completed_probe_count,
                self.completed_field_steps,
            )
            != (4, 8, 8, 3208)
            or self.available_refinement_levels != ("r2",)
            or self.required_refinement_levels != ("r2", "r4", "r8")
            or self.metric_components != ("activation", "afterimage")
            or self.structurally_available_contrasts
            != S1_EC45_REQUIRED_CONTRASTS
            or any(
                value is not False
                for value in (
                    self.quantitative_probe_vectors_retained,
                    self.ec46_scalar_inputs_available,
                    self.result_object_reconstruction_permitted,
                    self.field_execution_permitted,
                    self.persistence_permitted,
                    self.quantitative_decision_permitted,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "EC78_TECHNICALLY_COMPLETE_QUANTITATIVE_EVALUATION_UNAVAILABLE"
            or not self.reason
        ):
            raise E1CommonProbeN2R2EC79StaticEvaluationContractError(
                "S1-EC79 changed or crossed its static evidence boundary"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "contract_digest"
        }
        if self.contract_digest != _digest(payload):
            raise E1CommonProbeN2R2EC79StaticEvaluationContractError(
                "S1-EC79 contract digest changed"
            )


def build_e1_common_probe_n2_r2_ec79_static_evaluation_contract(
    project_root: Path,
    acceptance: E1CommonProbeAcceptanceContract | None = None,
) -> E1CommonProbeN2R2EC79StaticEvaluationContract:
    """Inventory retained EC78 evidence without executing or reconstructing it."""

    root = Path(project_root)
    report = root / S1_EC79_EC78_REPORT_RELATIVE_PATH
    try:
        report_sha256 = hashlib.sha256(report.read_bytes()).hexdigest()
    except OSError as exc:
        raise E1CommonProbeN2R2EC79StaticEvaluationContractError(
            "S1-EC79 requires the exact EC78 report"
        ) from exc
    if report_sha256 != S1_EC79_EC78_REPORT_SHA256:
        raise E1CommonProbeN2R2EC79StaticEvaluationContractError(
            "S1-EC79 EC78 report changed"
        )

    source = acceptance or build_e1_common_probe_acceptance_contract()
    if not isinstance(source, E1CommonProbeAcceptanceContract):
        raise E1CommonProbeN2R2EC79StaticEvaluationContractError(
            "S1-EC79 requires the typed EC46 acceptance contract"
        )
    source.__post_init__()
    if source.contract_digest != S1_EC79_EC46_CONTRACT_DIGEST:
        raise E1CommonProbeN2R2EC79StaticEvaluationContractError(
            "S1-EC79 EC46 binding changed"
        )

    values = {
        "contract_id": S1_EC79_CONTRACT_ID,
        "source_ec78_report_sha256": report_sha256,
        "source_ec78_result_digest": S1_EC79_EC78_RESULT_DIGEST,
        "source_ec46_contract_digest": source.contract_digest,
        "evidence_scope": (
            "ec78-structural-completion-only-no-retained-probe-vectors"
        ),
        "completed_formation_count": 4,
        "completed_fresh_field_count": 8,
        "completed_probe_count": 8,
        "completed_field_steps": 3208,
        "available_refinement_levels": ("r2",),
        "required_refinement_levels": source.refinement_levels,
        "metric_components": source.metric_components,
        "structurally_available_contrasts": S1_EC45_REQUIRED_CONTRASTS,
        "quantitative_probe_vectors_retained": False,
        "ec46_scalar_inputs_available": False,
        "result_object_reconstruction_permitted": False,
        "field_execution_permitted": False,
        "persistence_permitted": False,
        "quantitative_decision_permitted": False,
        "claims_permitted": False,
        "decision": (
            "EC78_TECHNICALLY_COMPLETE_QUANTITATIVE_EVALUATION_UNAVAILABLE"
        ),
        "reason": (
            "ec78-completed-r2-route-but-retained-no-probe-vectors;"
            "ec46-also-requires-r2-r4-r8-refinement-profile"
        ),
    }
    return E1CommonProbeN2R2EC79StaticEvaluationContract(
        **values,
        contract_digest=_digest(values),
    )
