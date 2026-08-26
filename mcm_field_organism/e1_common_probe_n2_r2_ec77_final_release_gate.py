"""S1-EC77 static gate before requesting a new explicit one-shot release."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re

from .e1_common_probe_n2_r2_corrected_final_preflight import (
    E1CommonProbeN2R2CorrectedFinalPreflight,
)
from .e1_common_probe_n2_r2_diagnostic_one_shot_contract import (
    E1CommonProbeN2R2DiagnosticOneShotContract,
)
from .e1_common_probe_n2_r2_ec75_synthetic_route import (
    E1CommonProbeN2R2EC75SyntheticRouteResult,
)


class E1CommonProbeN2R2EC77FinalReleaseGateError(ValueError):
    """Raised when EC77 cannot establish closed request readiness."""


S1_EC77_GATE_ID = "e1.common-probe-n2-r2-final-release-gate.s1ec77.v1"
S1_EC77_EC76_ROUTE_DIGEST = (
    "135ffafdc816a38b7064eaf5dcc74c8ce1b262eca22a253010a373139c769514"
)
S1_EC77_EC71_PREFLIGHT_DIGEST = (
    "15966ff850b5028cab9960c6fdd11914896c85e8edfa2da8c8e29092a33aa852"
)
S1_EC77_EC74_REPORT_RELATIVE_PATH = (
    "docs/S1EC74_AUTORISIERTER_DIAGNOSELAUF_HANDOFF_DIGEST_SCHEMAABWEICHUNG.md"
)
S1_EC77_EC74_REPORT_SHA256 = (
    "1644e42cdb245782c86c33622cf12a5c3ffff1b10e76d74d5f6e4f248e6792f1"
)
S1_EC77_CONSUMED_EC74_AUTHORIZATION_DIGEST = (
    "cddaffb747083b0c8d2a9307cd6a120823e7fd57401ae73843bac86c607e8b19"
)
_SHA256 = re.compile(r"[0-9a-f]{64}")


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class E1CommonProbeN2R2EC77FinalReleaseGate:
    gate_id: str
    source_ec76_route_digest: str
    source_ec72_preflight_digest: str
    source_ec73_contract_digest: str
    source_ec71_preflight_digest: str
    source_ec74_report_sha256: str
    consumed_ec74_authorization_digest: str
    registered_source_count: int
    diagnostic_gate_count: int
    maximum_total_field_steps: int
    maximum_runtime_seconds: float
    ec76_full_synthetic_route_exact: bool
    ec72_ec73_chain_current_and_closed: bool
    all_registered_sources_exact: bool
    prior_ec74_authorization_consumed: bool
    protected_artifacts_bound_by_ec72: bool
    technical_one_shot_request_ready: bool
    explicit_new_owner_authorization_required: bool
    owner_authorization_present: bool
    execution_permitted: bool
    automatic_retry_permitted: bool
    posthoc_parameter_change_permitted: bool
    persistence_permitted: bool
    research_decision_permitted: bool
    claims_permitted: bool
    status: str
    gate_digest: str

    def __post_init__(self) -> None:
        for role in (
            "source_ec76_route_digest",
            "source_ec72_preflight_digest",
            "source_ec73_contract_digest",
            "source_ec71_preflight_digest",
            "source_ec74_report_sha256",
            "consumed_ec74_authorization_digest",
            "gate_digest",
        ):
            if not _SHA256.fullmatch(getattr(self, role)):
                raise E1CommonProbeN2R2EC77FinalReleaseGateError(
                    f"S1-EC77 {role} is not SHA-256"
                )
        if (
            self.gate_id != S1_EC77_GATE_ID
            or self.source_ec76_route_digest != S1_EC77_EC76_ROUTE_DIGEST
            or self.source_ec71_preflight_digest
            != S1_EC77_EC71_PREFLIGHT_DIGEST
            or self.source_ec74_report_sha256 != S1_EC77_EC74_REPORT_SHA256
            or self.consumed_ec74_authorization_digest
            != S1_EC77_CONSUMED_EC74_AUTHORIZATION_DIGEST
            or (self.registered_source_count, self.diagnostic_gate_count) != (4, 6)
            or self.maximum_total_field_steps != 3208
            or self.maximum_runtime_seconds != 900.0
            or any(
                value is not True
                for value in (
                    self.ec76_full_synthetic_route_exact,
                    self.ec72_ec73_chain_current_and_closed,
                    self.all_registered_sources_exact,
                    self.prior_ec74_authorization_consumed,
                    self.protected_artifacts_bound_by_ec72,
                    self.technical_one_shot_request_ready,
                    self.explicit_new_owner_authorization_required,
                )
            )
            or any(
                value is not False
                for value in (
                    self.owner_authorization_present,
                    self.execution_permitted,
                    self.automatic_retry_permitted,
                    self.posthoc_parameter_change_permitted,
                    self.persistence_permitted,
                    self.research_decision_permitted,
                    self.claims_permitted,
                )
            )
            or self.status
            != "READY_TO_REQUEST_NEW_EXPLICIT_ONE_SHOT_AUTHORIZATION"
        ):
            raise E1CommonProbeN2R2EC77FinalReleaseGateError(
                "S1-EC77 gate changed or released execution"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "gate_digest"
        }
        if self.gate_digest != _digest(payload):
            raise E1CommonProbeN2R2EC77FinalReleaseGateError(
                "S1-EC77 gate digest changed"
            )


def prepare_e1_common_probe_n2_r2_ec77_final_release_gate(
    project_root: Path,
    route: E1CommonProbeN2R2EC75SyntheticRouteResult,
    preflight: E1CommonProbeN2R2CorrectedFinalPreflight,
    contract: E1CommonProbeN2R2DiagnosticOneShotContract,
) -> E1CommonProbeN2R2EC77FinalReleaseGate:
    """Prove request readiness without accepting authorization or executing."""

    if (
        not isinstance(route, E1CommonProbeN2R2EC75SyntheticRouteResult)
        or not isinstance(preflight, E1CommonProbeN2R2CorrectedFinalPreflight)
        or not isinstance(contract, E1CommonProbeN2R2DiagnosticOneShotContract)
    ):
        raise E1CommonProbeN2R2EC77FinalReleaseGateError(
            "S1-EC77 requires validated EC76, EC72, and EC73 inputs"
        )
    route.__post_init__()
    preflight.__post_init__()
    contract.__post_init__()
    report_path = Path(project_root) / S1_EC77_EC74_REPORT_RELATIVE_PATH
    if not report_path.is_file():
        raise E1CommonProbeN2R2EC77FinalReleaseGateError(
            "S1-EC77 consumed EC74 report is missing"
        )
    report_bytes = report_path.read_bytes()
    report_sha256 = hashlib.sha256(report_bytes).hexdigest()
    report_text = report_bytes.decode("utf-8")
    consumed = (
        report_sha256 == S1_EC77_EC74_REPORT_SHA256
        and S1_EC77_CONSUMED_EC74_AUTHORIZATION_DIGEST in report_text
        and "Die EC74-Freigabe ist verbraucht" in report_text
    )
    chain_closed = (
        contract.source_ec72_preflight_digest == preflight.preflight_digest
        and contract.source_ec71_preflight_digest == preflight.ec71_preflight_digest
        and contract.authorized_execution_count == 0
        and contract.execution_permitted is False
        and preflight.owner_execution_authorized is False
        and preflight.coordinator_execution_permitted is False
        and preflight.adapter_execution_permitted is False
    )
    route_exact = (
        route.result_digest == S1_EC77_EC76_ROUTE_DIGEST
        and route.actual_field_steps_executed == 0
        and route.all_six_diagnostic_gates_passed_for_all_formations
    )
    sources_exact = (
        preflight.ec71_preflight_digest == S1_EC77_EC71_PREFLIGHT_DIGEST
        and len(preflight.source_digests) == 4
        and all(expected == observed for _, expected, observed in preflight.source_digests)
    )
    if not all((route_exact, chain_closed, sources_exact, consumed)):
        raise E1CommonProbeN2R2EC77FinalReleaseGateError(
            "S1-EC77 request-readiness evidence is incomplete"
        )
    values = {
        "gate_id": S1_EC77_GATE_ID,
        "source_ec76_route_digest": route.result_digest,
        "source_ec72_preflight_digest": preflight.preflight_digest,
        "source_ec73_contract_digest": contract.contract_digest,
        "source_ec71_preflight_digest": preflight.ec71_preflight_digest,
        "source_ec74_report_sha256": report_sha256,
        "consumed_ec74_authorization_digest": (
            S1_EC77_CONSUMED_EC74_AUTHORIZATION_DIGEST
        ),
        "registered_source_count": len(preflight.source_digests),
        "diagnostic_gate_count": len(contract.diagnostic_gate_names),
        "maximum_total_field_steps": contract.maximum_total_field_steps,
        "maximum_runtime_seconds": contract.maximum_runtime_seconds,
        "ec76_full_synthetic_route_exact": route_exact,
        "ec72_ec73_chain_current_and_closed": chain_closed,
        "all_registered_sources_exact": sources_exact,
        "prior_ec74_authorization_consumed": consumed,
        "protected_artifacts_bound_by_ec72": bool(
            preflight.protected_artifact_audit_digest
        ),
        "technical_one_shot_request_ready": True,
        "explicit_new_owner_authorization_required": True,
        "owner_authorization_present": False,
        "execution_permitted": False,
        "automatic_retry_permitted": False,
        "posthoc_parameter_change_permitted": False,
        "persistence_permitted": False,
        "research_decision_permitted": False,
        "claims_permitted": False,
        "status": "READY_TO_REQUEST_NEW_EXPLICIT_ONE_SHOT_AUTHORIZATION",
    }
    return E1CommonProbeN2R2EC77FinalReleaseGate(
        **values,
        gate_digest=_digest(values),
    )
