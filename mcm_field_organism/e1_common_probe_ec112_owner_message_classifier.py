"""S1-EC112 pure fail-closed workflow message classifier."""

from __future__ import annotations

from dataclasses import dataclass
import re

from .e1_common_probe_ec111_external_owner_release_bridge_contract import (
    S1_EC111_CONTINUATION_EXAMPLES,
)
from .e1_common_probe_n2_r2_real_mode_coordinator import (
    S1_EC67_EC59_HANDOFF_DIGEST,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeEC112OwnerMessageClassifierError(ValueError):
    """Raised when classification input or output crosses the closed scope."""


S1_EC112_CLASSIFIER_ID = "e1.common-probe-owner-message-classifier.s1ec112.v1"
S1_EC112_MESSAGE_CLASSES = (
    "continuation-only",
    "question-or-discussion",
    "stop-or-revoke",
    "explicit-run-release-candidate",
    "ambiguous-or-incomplete",
)
S1_EC112_STOP_MESSAGES = (
    "stopp",
    "stop",
    "abbrechen",
    "nicht weiter",
)
S1_EC112_RELEASE_REQUIREMENT_IDS = (
    "run-id",
    "exactly-once",
    "step-budget",
    "nonpersistent",
    "no-retry",
    "real-execution-intent",
    "gate-binding",
    "handoff-binding",
    "session-binding",
)
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


def _normalize(message: str) -> str:
    return " ".join(message.strip().lower().split())


def _binding(normalized: str, key: str) -> str | None:
    match = re.search(rf"(?:^|\s){re.escape(key)}:([0-9a-f]{{64}})(?:\s|$)", normalized)
    return None if match is None else match.group(1)


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC112OwnerMessageClassification:
    classifier_id: str
    message_digest: str
    message_class: str
    matched_release_requirements: tuple[str, ...]
    missing_release_requirements: tuple[str, ...]
    gate_binding_digest: str | None
    handoff_binding_digest: str | None
    session_binding_digest: str | None
    continuation_work_permitted: bool
    stop_or_revoke_requested: bool
    explicit_release_candidate_complete: bool
    external_bridge_validation_required: bool
    owner_scope_token_creation_permitted: bool
    execution_permitted: bool
    persistence_permitted: bool
    retry_permitted: bool
    organism_function_rule_created: bool
    status: str
    classification_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "classification_digest"
        }
        expected_flags = {
            "continuation-only": (True, False, False, False),
            "question-or-discussion": (False, False, False, False),
            "stop-or-revoke": (False, True, False, False),
            "explicit-run-release-candidate": (False, False, True, True),
            "ambiguous-or-incomplete": (False, False, False, False),
        }.get(self.message_class)
        if (
            self.classifier_id != S1_EC112_CLASSIFIER_ID
            or self.message_class not in S1_EC112_MESSAGE_CLASSES
            or not _DIGEST.fullmatch(self.message_digest)
            or tuple(
                requirement
                for requirement in S1_EC112_RELEASE_REQUIREMENT_IDS
                if requirement in self.matched_release_requirements
            )
            != self.matched_release_requirements
            or tuple(
                requirement
                for requirement in S1_EC112_RELEASE_REQUIREMENT_IDS
                if requirement in self.missing_release_requirements
            )
            != self.missing_release_requirements
            or set(self.matched_release_requirements)
            | set(self.missing_release_requirements)
            != set(S1_EC112_RELEASE_REQUIREMENT_IDS)
            or set(self.matched_release_requirements)
            & set(self.missing_release_requirements)
            or expected_flags is None
            or (
                self.continuation_work_permitted,
                self.stop_or_revoke_requested,
                self.explicit_release_candidate_complete,
                self.external_bridge_validation_required,
            )
            != expected_flags
            or any(
                value is not False
                for value in (
                    self.owner_scope_token_creation_permitted,
                    self.execution_permitted,
                    self.persistence_permitted,
                    self.retry_permitted,
                    self.organism_function_rule_created,
                )
            )
            or not self.status
            or self.classification_digest != _digest(payload)
        ):
            raise E1CommonProbeEC112OwnerMessageClassifierError(
                "S1-EC112 classification changed or opened execution"
            )


def classify_e1_common_probe_ec112_owner_message(
    message: str,
) -> E1CommonProbeEC112OwnerMessageClassification:
    """Classify workflow intent only; never issue a release or organism rule."""

    if not isinstance(message, str) or not message.strip():
        raise E1CommonProbeEC112OwnerMessageClassifierError(
            "S1-EC112 requires one nonempty owner message"
        )
    normalized = _normalize(message)
    gate = _binding(normalized, "gate")
    handoff = _binding(normalized, "handoff")
    session = _binding(normalized, "session")
    requirements = {
        "run-id": "ec67-r2" in normalized,
        "exactly-once": "genau einen lauf" in normalized,
        "step-budget": (
            "maximal 3.208 feldschritte" in normalized
            or "maximal 3208 feldschritte" in normalized
        ),
        "nonpersistent": (
            "nicht persistent" in normalized or "nicht-persistent" in normalized
        ),
        "no-retry": "kein retry" in normalized,
        "real-execution-intent": (
            "reale ausfuehrung" in normalized
            or "reale ausführung" in normalized
        ),
        "gate-binding": gate is not None,
        "handoff-binding": handoff == S1_EC67_EC59_HANDOFF_DIGEST,
        "session-binding": session is not None,
    }
    matched = tuple(
        requirement
        for requirement in S1_EC112_RELEASE_REQUIREMENT_IDS
        if requirements[requirement]
    )
    missing = tuple(
        requirement
        for requirement in S1_EC112_RELEASE_REQUIREMENT_IDS
        if not requirements[requirement]
    )
    if normalized in S1_EC111_CONTINUATION_EXAMPLES:
        message_class = "continuation-only"
        status = "CONTINUATION_ONLY_NO_RELEASE"
    elif normalized in S1_EC112_STOP_MESSAGES:
        message_class = "stop-or-revoke"
        status = "STOP_OR_REVOKE_NO_RELEASE"
    elif not missing:
        message_class = "explicit-run-release-candidate"
        status = "COMPLETE_CANDIDATE_REQUIRES_EXTERNAL_BRIDGE_NO_TOKEN"
    elif normalized.endswith("?"):
        message_class = "question-or-discussion"
        status = "QUESTION_OR_DISCUSSION_NO_RELEASE"
    else:
        message_class = "ambiguous-or-incomplete"
        status = "AMBIGUOUS_OR_INCOMPLETE_FAIL_CLOSED"
    values = {
        "classifier_id": S1_EC112_CLASSIFIER_ID,
        "message_digest": _digest(normalized),
        "message_class": message_class,
        "matched_release_requirements": matched,
        "missing_release_requirements": missing,
        "gate_binding_digest": gate,
        "handoff_binding_digest": handoff,
        "session_binding_digest": session,
        "continuation_work_permitted": message_class == "continuation-only",
        "stop_or_revoke_requested": message_class == "stop-or-revoke",
        "explicit_release_candidate_complete": (
            message_class == "explicit-run-release-candidate"
        ),
        "external_bridge_validation_required": (
            message_class == "explicit-run-release-candidate"
        ),
        "owner_scope_token_creation_permitted": False,
        "execution_permitted": False,
        "persistence_permitted": False,
        "retry_permitted": False,
        "organism_function_rule_created": False,
        "status": status,
    }
    return E1CommonProbeEC112OwnerMessageClassification(
        **values, classification_digest=_digest(values)
    )
