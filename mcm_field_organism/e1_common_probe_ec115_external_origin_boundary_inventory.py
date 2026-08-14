"""S1-EC115 static inventory of possible external owner-origin boundaries."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .e1_common_probe_ec114_external_origin_attestation_contract import (
    S1_EC114_REQUIRED_EXTERNAL_EVIDENCE_SCHEMA,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeEC115ExternalOriginBoundaryInventoryError(ValueError):
    """Raised when the inventory claims an unsupported external boundary."""


S1_EC115_INVENTORY_ID = (
    "e1.common-probe-external-origin-boundary-inventory.s1ec115.v1"
)


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC115BoundaryCandidate:
    candidate_id: str
    locations: tuple[str, ...]
    boundary_kind: str
    covered_evidence_fields: tuple[str, ...]
    externally_authenticated_owner_event: bool
    eligible_for_ec114_attestation: bool
    exclusion_reason: str

    def __post_init__(self) -> None:
        if (
            not self.candidate_id
            or not self.locations
            or not self.boundary_kind
            or any(
                field not in S1_EC114_REQUIRED_EXTERNAL_EVIDENCE_SCHEMA
                for field in self.covered_evidence_fields
            )
            or len(set(self.covered_evidence_fields))
            != len(self.covered_evidence_fields)
            or self.externally_authenticated_owner_event is not False
            or self.eligible_for_ec114_attestation is not False
            or not self.exclusion_reason
        ):
            raise E1CommonProbeEC115ExternalOriginBoundaryInventoryError(
                "S1-EC115 candidate incorrectly qualifies as external origin"
            )


S1_EC115_BOUNDARY_CANDIDATES = (
    E1CommonProbeEC115BoundaryCandidate(
        candidate_id="project-codex-orchestrator-config",
        locations=(
            "../.codex-orchestrator/GEMEINSAME_ARBEITSGRENZE.md",
            "../.codex-orchestrator/project-goal.json",
            "../.codex-orchestrator/knowledge-sources.json",
            "../.codex-orchestrator/prompts/",
        ),
        boundary_kind="configuration-and-prompt-files",
        covered_evidence_fields=(),
        externally_authenticated_owner_event=False,
        eligible_for_ec114_attestation=False,
        exclusion_reason=(
            "contains project instructions and prompts but no executable host API, "
            "authenticated principal, message event, sequence, or nonce envelope"
        ),
    ),
    E1CommonProbeEC115BoundaryCandidate(
        candidate_id="legacy-boolean-owner-authorizers",
        locations=(
            "mcm_field_organism/e1_common_probe_n2_r2_diagnostic_owner_authorization.py",
            "mcm_field_organism/e1_common_probe_n2_r2_ec78_owner_authorization.py",
        ),
        boundary_kind="caller-supplied-boolean",
        covered_evidence_fields=("source_gate_digest",),
        externally_authenticated_owner_event=False,
        eligible_for_ec114_attestation=False,
        exclusion_reason=(
            "a true function argument records caller intent but proves neither "
            "external owner identity nor exact message origin"
        ),
    ),
    E1CommonProbeEC115BoundaryCandidate(
        candidate_id="ec112-ec113-synthetic-message-bridge",
        locations=(
            "mcm_field_organism/e1_common_probe_ec112_owner_message_classifier.py",
            "mcm_field_organism/e1_common_probe_ec113_synthetic_bridge_validation_receipt.py",
        ),
        boundary_kind="synthetic-structure-validation",
        covered_evidence_fields=(
            "thread_or_session_binding_digest",
            "exact_owner_message_digest",
            "source_ec113_receipt_digest",
            "source_gate_digest",
            "source_handoff_digest",
        ),
        externally_authenticated_owner_event=False,
        eligible_for_ec114_attestation=False,
        exclusion_reason=(
            "binds supplied text structure and digests but explicitly does not "
            "attest external owner origin, identity, event order, or freshness"
        ),
    ),
    E1CommonProbeEC115BoundaryCandidate(
        candidate_id="eb23-process-local-preflight",
        locations=(
            "mcm_field_organism/e1_confirmation_same_session_preflight.py",
        ),
        boundary_kind="process-local-time-and-file-binding",
        covered_evidence_fields=(),
        externally_authenticated_owner_event=False,
        eligible_for_ec114_attestation=False,
        exclusion_reason=(
            "process id, monotonic age, and file digests establish runtime "
            "freshness but no owner-message provenance"
        ),
    ),
    E1CommonProbeEC115BoundaryCandidate(
        candidate_id="shared-field-session",
        locations=("mcm_field_organism/shared_field_session.py",),
        boundary_kind="organism-field-continuity",
        covered_evidence_fields=(),
        externally_authenticated_owner_event=False,
        eligible_for_ec114_attestation=False,
        exclusion_reason=(
            "field clock and receptor continuity are unrelated to chat session "
            "identity or owner authorization"
        ),
    ),
    E1CommonProbeEC115BoundaryCandidate(
        candidate_id="browser-receptor-bridge",
        locations=("mcm_field_organism/browser_receptor_bridge.py",),
        boundary_kind="controlled-testworld-payload-reduction",
        covered_evidence_fields=(),
        externally_authenticated_owner_event=False,
        eligible_for_ec114_attestation=False,
        exclusion_reason=(
            "browser AV payload provenance is testworld input, not workflow owner "
            "identity or release provenance"
        ),
    ),
)


def _serializable_inventory_payload(
    values: dict[str, object],
) -> dict[str, object]:
    payload = dict(values)
    payload["candidates"] = tuple(
        asdict(candidate) for candidate in payload["candidates"]  # type: ignore[union-attr]
    )
    return payload


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC115ExternalOriginBoundaryInventory:
    inventory_id: str
    required_external_evidence_schema: tuple[str, ...]
    candidates: tuple[E1CommonProbeEC115BoundaryCandidate, ...]
    eligible_candidate_ids: tuple[str, ...]
    externally_authenticated_event_boundary_present: bool
    ec114_attestation_implementation_permitted: bool
    external_release_issued: bool
    owner_scope_token_creation_permitted: bool
    execution_permitted: bool
    persistence_permitted: bool
    retry_permitted: bool
    real_result_ingress_permitted: bool
    claims_permitted: bool
    decision: str
    reason: str
    inventory_digest: str

    def __post_init__(self) -> None:
        payload = _serializable_inventory_payload({
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "inventory_digest"
        })
        if (
            self.inventory_id != S1_EC115_INVENTORY_ID
            or self.required_external_evidence_schema
            != S1_EC114_REQUIRED_EXTERNAL_EVIDENCE_SCHEMA
            or self.candidates != S1_EC115_BOUNDARY_CANDIDATES
            or len({item.candidate_id for item in self.candidates})
            != len(self.candidates)
            or self.eligible_candidate_ids
            != tuple(
                item.candidate_id
                for item in self.candidates
                if item.eligible_for_ec114_attestation
            )
            or self.eligible_candidate_ids
            or any(
                value is not False
                for value in (
                    self.externally_authenticated_event_boundary_present,
                    self.ec114_attestation_implementation_permitted,
                    self.external_release_issued,
                    self.owner_scope_token_creation_permitted,
                    self.execution_permitted,
                    self.persistence_permitted,
                    self.retry_permitted,
                    self.real_result_ingress_permitted,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "NO_EXISTING_PROJECT_BOUNDARY_PROVIDES_EXTERNAL_OWNER_ORIGIN"
            or not self.reason
            or self.inventory_digest != _digest(payload)
        ):
            raise E1CommonProbeEC115ExternalOriginBoundaryInventoryError(
                "S1-EC115 inventory changed or invented an eligible boundary"
            )
        for candidate in self.candidates:
            candidate.__post_init__()


def audit_e1_common_probe_ec115_external_origin_boundary_inventory(
) -> E1CommonProbeEC115ExternalOriginBoundaryInventory:
    """Return the closed static inventory without invoking any candidate."""

    values = {
        "inventory_id": S1_EC115_INVENTORY_ID,
        "required_external_evidence_schema": (
            S1_EC114_REQUIRED_EXTERNAL_EVIDENCE_SCHEMA
        ),
        "candidates": S1_EC115_BOUNDARY_CANDIDATES,
        "eligible_candidate_ids": (),
        "externally_authenticated_event_boundary_present": False,
        "ec114_attestation_implementation_permitted": False,
        "external_release_issued": False,
        "owner_scope_token_creation_permitted": False,
        "execution_permitted": False,
        "persistence_permitted": False,
        "retry_permitted": False,
        "real_result_ingress_permitted": False,
        "claims_permitted": False,
        "decision": "NO_EXISTING_PROJECT_BOUNDARY_PROVIDES_EXTERNAL_OWNER_ORIGIN",
        "reason": (
            "the project contains prompt configuration, internal booleans, "
            "synthetic digest bindings, process freshness, and testworld or field "
            "sessions, but no authenticated host message-event envelope"
        ),
    }
    return E1CommonProbeEC115ExternalOriginBoundaryInventory(
        **values,
        inventory_digest=_digest(_serializable_inventory_payload(values)),
    )
