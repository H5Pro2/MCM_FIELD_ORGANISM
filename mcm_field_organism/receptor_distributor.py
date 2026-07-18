"""Neutral routing from completed receptor contacts into shared-field docks."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import re
from typing import Iterable

from .receptor_contract import CommonFieldTime, ReceptorContactFrame


class ReceptorDistributionError(ValueError):
    """Raised when receptor contacts cannot be routed losslessly."""


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]*$")


def _identifier(value: object, role: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise ReceptorDistributionError(
            f"{role} must be a lowercase technical identifier"
        )
    return value


@dataclass(frozen=True, slots=True)
class ReceptorDock:
    """One stable technical inlet; it contains no field state or meaning."""

    dock_id: str
    modality_id: str
    receptor_geometry_id: str

    def __post_init__(self) -> None:
        for role in ("dock_id", "modality_id", "receptor_geometry_id"):
            object.__setattr__(self, role, _identifier(getattr(self, role), role))


@dataclass(frozen=True, slots=True)
class DistributedReceptorContact:
    """One receptor frame with its preserved dock identity."""

    dock_id: str
    frame: ReceptorContactFrame

    def __post_init__(self) -> None:
        object.__setattr__(self, "dock_id", _identifier(self.dock_id, "dock_id"))
        if not isinstance(self.frame, ReceptorContactFrame):
            raise ReceptorDistributionError(
                "distributed contact requires a completed receptor frame"
            )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "dock_id": self.dock_id,
            "modality_id": self.frame.modality_id,
            "geometry_id": self.frame.geometry_id,
            "snapshot_id": self.frame.snapshot_id,
            "source_clock_id": self.frame.clock_id,
            "source_window_start_tick": self.frame.window_start_tick,
            "source_window_end_tick": self.frame.window_end_tick,
            "carrier_ids": list(self.frame.carrier_ids),
            "values": list(self.frame.values),
        }


@dataclass(frozen=True, slots=True)
class ReceptorDistribution:
    """Lossless inlet observation on the common organism clock."""

    field_time: CommonFieldTime
    contacts: tuple[DistributedReceptorContact, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.field_time, CommonFieldTime):
            raise ReceptorDistributionError(
                "distribution requires an explicit common field time"
            )
        contacts = tuple(self.contacts)
        if any(not isinstance(item, DistributedReceptorContact) for item in contacts):
            raise ReceptorDistributionError(
                "contacts must contain completed distributed receptor contacts"
            )
        dock_ids = [item.dock_id for item in contacts]
        modalities = [item.frame.modality_id for item in contacts]
        snapshots = [item.frame.snapshot_id for item in contacts]
        if len(set(dock_ids)) != len(dock_ids):
            raise ReceptorDistributionError("one distribution permits one frame per dock")
        if len(set(modalities)) != len(modalities):
            raise ReceptorDistributionError(
                "one distribution permits one frame per modality"
            )
        if len(set(snapshots)) != len(snapshots):
            raise ReceptorDistributionError("snapshot identities must be unique")
        object.__setattr__(
            self,
            "contacts",
            tuple(sorted(contacts, key=lambda item: item.dock_id)),
        )

    @property
    def dock_ids(self) -> tuple[str, ...]:
        return tuple(item.dock_id for item in self.contacts)

    @property
    def modality_ids(self) -> tuple[str, ...]:
        return tuple(item.frame.modality_id for item in self.contacts)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "field_time": {
                "clock_id": self.field_time.clock_id,
                "window_start_tick": self.field_time.window_start_tick,
                "window_end_tick": self.field_time.window_end_tick,
            },
            "contacts": [item.canonical_payload() for item in self.contacts],
        }

    def digest(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


@dataclass(slots=True)
class ReceptorDistributor:
    """Open neutral router with no memory, fusion, weights, or classification."""

    _docks: dict[str, ReceptorDock] = field(default_factory=dict, init=False, repr=False)

    @property
    def docks(self) -> tuple[ReceptorDock, ...]:
        return tuple(sorted(self._docks.values(), key=lambda item: item.dock_id))

    def attach(self, dock: ReceptorDock) -> None:
        if not isinstance(dock, ReceptorDock):
            raise ReceptorDistributionError("only receptor docks can be attached")
        if dock.dock_id in self._docks:
            raise ReceptorDistributionError(f"dock already attached: {dock.dock_id}")
        if any(item.modality_id == dock.modality_id for item in self._docks.values()):
            raise ReceptorDistributionError(
                f"modality already has a dock: {dock.modality_id}"
            )
        self._docks[dock.dock_id] = dock

    def detach(self, dock_id: str) -> ReceptorDock:
        dock_id = _identifier(dock_id, "dock_id")
        try:
            return self._docks.pop(dock_id)
        except KeyError as exc:
            raise ReceptorDistributionError(f"unknown dock: {dock_id}") from exc

    def distribute(
        self,
        frames: Iterable[ReceptorContactFrame],
        field_time: CommonFieldTime,
    ) -> ReceptorDistribution:
        frames_out = tuple(frames)
        if not frames_out:
            if not self._docks:
                raise ReceptorDistributionError(
                    "contact-free distribution requires attached receptor docks"
                )
            return ReceptorDistribution(field_time, ())
        by_modality = {dock.modality_id: dock for dock in self._docks.values()}
        if len(by_modality) != len(self._docks):
            raise ReceptorDistributionError("attached modality identities must be unique")

        contacts = []
        seen_modalities: set[str] = set()
        for frame in frames_out:
            if not isinstance(frame, ReceptorContactFrame):
                raise ReceptorDistributionError(
                    "only completed receptor frames can be distributed"
                )
            if frame.modality_id in seen_modalities:
                raise ReceptorDistributionError(
                    f"duplicate modality frame: {frame.modality_id}"
                )
            seen_modalities.add(frame.modality_id)
            dock = by_modality.get(frame.modality_id)
            if dock is None:
                raise ReceptorDistributionError(
                    f"no dock for modality: {frame.modality_id}"
                )
            if frame.geometry_id != dock.receptor_geometry_id:
                raise ReceptorDistributionError(
                    f"receptor geometry does not match dock: {dock.dock_id}"
                )
            contacts.append(DistributedReceptorContact(dock.dock_id, frame))

        return ReceptorDistribution(field_time, tuple(contacts))
