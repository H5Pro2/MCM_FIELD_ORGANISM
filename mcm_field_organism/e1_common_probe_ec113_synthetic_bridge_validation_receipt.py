"""S1-EC113 synthetic validation receipt for complete EC112 candidates."""

from __future__ import annotations

from dataclasses import dataclass, field

from .e1_common_probe_ec112_owner_message_classifier import (
    E1CommonProbeEC112OwnerMessageClassification,
)
from .e1_common_probe_n2_r2_real_mode_coordinator import (
    S1_EC67_EC59_HANDOFF_DIGEST,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeEC113SyntheticBridgeValidationError(ValueError):
    """Raised when a candidate or receipt crosses the synthetic boundary."""


S1_EC113_RECEIPT_ID = (
    "e1.common-probe-synthetic-bridge-validation-receipt.s1ec113.v1"
)
S1_EC113_VALIDATION_SCOPE = "synthetic-candidate-structure-only"


def _valid_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC113SyntheticBridgeValidationReceipt:
    receipt_id: str
    validation_scope: str
    source_classifier_id: str
    source_classification_digest: str
    source_message_digest: str
    source_gate_digest: str
    source_handoff_digest: str
    source_session_digest: str
    maximum_field_steps: int
    candidate_structure_validated: bool
    external_owner_origin_attested: bool
    external_identity_attested: bool
    release_attestation_issued: bool
    owner_scope_token_creation_permitted: bool
    execution_permitted: bool
    persistence_permitted: bool
    retry_permitted: bool
    contractual_not_cryptographic: bool
    status: str
    receipt_digest: str
    source_classification: E1CommonProbeEC112OwnerMessageClassification = field(
        repr=False, compare=False
    )

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"receipt_digest", "source_classification"}
        }
        source = self.source_classification
        if (
            self.receipt_id != S1_EC113_RECEIPT_ID
            or self.validation_scope != S1_EC113_VALIDATION_SCOPE
            or self.source_classifier_id != source.classifier_id
            or self.source_classification_digest != source.classification_digest
            or self.source_message_digest != source.message_digest
            or self.source_gate_digest != source.gate_binding_digest
            or self.source_handoff_digest != source.handoff_binding_digest
            or self.source_session_digest != source.session_binding_digest
            or not all(
                _valid_digest(value)
                for value in (
                    self.source_classification_digest,
                    self.source_message_digest,
                    self.source_gate_digest,
                    self.source_handoff_digest,
                    self.source_session_digest,
                )
            )
            or self.source_handoff_digest != S1_EC67_EC59_HANDOFF_DIGEST
            or self.maximum_field_steps != 3208
            or self.candidate_structure_validated is not True
            or any(
                value is not False
                for value in (
                    self.external_owner_origin_attested,
                    self.external_identity_attested,
                    self.release_attestation_issued,
                    self.owner_scope_token_creation_permitted,
                    self.execution_permitted,
                    self.persistence_permitted,
                    self.retry_permitted,
                )
            )
            or self.contractual_not_cryptographic is not True
            or self.status
            != "CANDIDATE_STRUCTURE_VALIDATED_OWNER_ORIGIN_UNATTESTED_NO_RELEASE"
            or self.receipt_digest != _digest(payload)
        ):
            raise E1CommonProbeEC113SyntheticBridgeValidationError(
                "S1-EC113 receipt changed or opened owner release"
            )
        source.__post_init__()
        if (
            source.message_class != "explicit-run-release-candidate"
            or source.explicit_release_candidate_complete is not True
            or source.external_bridge_validation_required is not True
            or source.missing_release_requirements
            or source.owner_scope_token_creation_permitted is not False
            or source.execution_permitted is not False
        ):
            raise E1CommonProbeEC113SyntheticBridgeValidationError(
                "S1-EC113 requires one complete, still closed EC112 candidate"
            )


def validate_e1_common_probe_ec113_synthetic_bridge_candidate(
    classification: E1CommonProbeEC112OwnerMessageClassification,
) -> E1CommonProbeEC113SyntheticBridgeValidationReceipt:
    """Validate candidate structure without attesting owner origin or release."""

    if not isinstance(
        classification, E1CommonProbeEC112OwnerMessageClassification
    ):
        raise E1CommonProbeEC113SyntheticBridgeValidationError(
            "S1-EC113 requires one typed EC112 classification"
        )
    classification.__post_init__()
    if (
        classification.message_class != "explicit-run-release-candidate"
        or not classification.explicit_release_candidate_complete
        or not classification.external_bridge_validation_required
        or classification.missing_release_requirements
    ):
        raise E1CommonProbeEC113SyntheticBridgeValidationError(
            "S1-EC113 rejects incomplete, continuation, question, and stop messages"
        )
    values = {
        "receipt_id": S1_EC113_RECEIPT_ID,
        "validation_scope": S1_EC113_VALIDATION_SCOPE,
        "source_classifier_id": classification.classifier_id,
        "source_classification_digest": classification.classification_digest,
        "source_message_digest": classification.message_digest,
        "source_gate_digest": classification.gate_binding_digest,
        "source_handoff_digest": classification.handoff_binding_digest,
        "source_session_digest": classification.session_binding_digest,
        "maximum_field_steps": 3208,
        "candidate_structure_validated": True,
        "external_owner_origin_attested": False,
        "external_identity_attested": False,
        "release_attestation_issued": False,
        "owner_scope_token_creation_permitted": False,
        "execution_permitted": False,
        "persistence_permitted": False,
        "retry_permitted": False,
        "contractual_not_cryptographic": True,
        "status": (
            "CANDIDATE_STRUCTURE_VALIDATED_OWNER_ORIGIN_UNATTESTED_NO_RELEASE"
        ),
    }
    return E1CommonProbeEC113SyntheticBridgeValidationReceipt(
        **values,
        receipt_digest=_digest(values),
        source_classification=classification,
    )
