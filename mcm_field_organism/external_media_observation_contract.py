"""Passive contract for observing one external audiovisual media contact."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import re


class ExternalMediaObservationContractError(ValueError):
    """Raised when an external media observation opens a forbidden shortcut."""


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]*$")


@dataclass(frozen=True, slots=True)
class ExternalMediaObservationPhase:
    phase_id: str
    duration_ns: int
    media_contact: bool

    def __post_init__(self) -> None:
        if not isinstance(self.phase_id, str) or not _IDENTIFIER.fullmatch(
            self.phase_id
        ):
            raise ExternalMediaObservationContractError(
                "phase_id must be a lowercase technical identifier"
            )
        if (
            isinstance(self.duration_ns, bool)
            or not isinstance(self.duration_ns, int)
            or self.duration_ns <= 0
        ):
            raise ExternalMediaObservationContractError(
                "duration_ns must be a positive integer"
            )
        if not isinstance(self.media_contact, bool):
            raise ExternalMediaObservationContractError(
                "media_contact must be boolean"
            )


@dataclass(frozen=True, slots=True)
class ExternalMediaObservationContract:
    contract_id: str
    startup_frame_count: int
    start_lead_ns: int
    phases: tuple[ExternalMediaObservationPhase, ...]
    raw_payload_retained: bool = False
    direct_sensor_feed: bool = False
    writes_back: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.contract_id, str) or not _IDENTIFIER.fullmatch(
            self.contract_id
        ):
            raise ExternalMediaObservationContractError(
                "contract_id must be a lowercase technical identifier"
            )
        for role in ("startup_frame_count", "start_lead_ns"):
            value = getattr(self, role)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ExternalMediaObservationContractError(
                    f"{role} must be a positive integer"
                )
        phase_set = tuple(self.phases)
        if len(phase_set) != 3:
            raise ExternalMediaObservationContractError(
                "external media observation requires exactly three phases"
            )
        if any(
            not isinstance(phase, ExternalMediaObservationPhase)
            for phase in phase_set
        ):
            raise ExternalMediaObservationContractError(
                "phases must contain ExternalMediaObservationPhase values"
            )
        if len({phase.phase_id for phase in phase_set}) != len(phase_set):
            raise ExternalMediaObservationContractError(
                "phase identifiers must be unique"
            )
        if tuple(phase.media_contact for phase in phase_set) != (
            False,
            True,
            False,
        ):
            raise ExternalMediaObservationContractError(
                "media contact must remain absent-present-absent"
            )
        if self.raw_payload_retained or self.direct_sensor_feed or self.writes_back:
            raise ExternalMediaObservationContractError(
                "external media observation must remain non-retaining and passive"
            )
        object.__setattr__(self, "phases", phase_set)

    @property
    def total_duration_ns(self) -> int:
        return sum(phase.duration_ns for phase in self.phases)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "contract_id": self.contract_id,
            "startup_frame_count": self.startup_frame_count,
            "start_lead_ns": self.start_lead_ns,
            "phases": [
                {
                    "phase_id": phase.phase_id,
                    "duration_ns": phase.duration_ns,
                    "media_contact": phase.media_contact,
                }
                for phase in self.phases
            ],
            "raw_payload_retained": self.raw_payload_retained,
            "direct_sensor_feed": self.direct_sensor_feed,
            "writes_back": self.writes_back,
        }

    def digest(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def reference_external_media_observation_contract(
) -> ExternalMediaObservationContract:
    second = 1_000_000_000
    return ExternalMediaObservationContract(
        contract_id="external.media.audiovisual.v1",
        startup_frame_count=30,
        start_lead_ns=10 * second,
        phases=(
            ExternalMediaObservationPhase(
                "rest.before",
                10 * second,
                False,
            ),
            ExternalMediaObservationPhase(
                "media.contact",
                63 * second,
                True,
            ),
            ExternalMediaObservationPhase(
                "rest.after",
                20 * second,
                False,
            ),
        ),
    )


def external_media_observation_contract_public_roles() -> tuple[str, ...]:
    classes = (
        ExternalMediaObservationPhase,
        ExternalMediaObservationContract,
    )
    return tuple(item.name for cls in classes for item in fields(cls))
