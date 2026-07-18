"""Local transient neuron inputs derived losslessly from dock trajectories."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math

from .field_step_time import MCMFieldStepTime
from .receptor_contract import CommonFieldTime, technical_identifier
from .shared_mcm_field import SharedFieldDock
from .transient_dock_trajectory import TransientDockTrajectory


class TransientNeuronInputError(ValueError):
    """Raised when transient dock history cannot remain local and lossless."""


def _identifier(value: object, role: str) -> str:
    try:
        return technical_identifier(value, role)
    except ValueError as exc:
        raise TransientNeuronInputError(
            f"{role} must be a technical identifier"
        ) from exc


@dataclass(frozen=True, slots=True)
class TransientLocalReceptorContact:
    """One reduced carrier value with its original technical time roles."""

    snapshot_id: str
    source_clock_id: str
    source_window_start_tick: int
    source_window_end_tick: int
    organism_read_time: CommonFieldTime
    value: float

    def __post_init__(self) -> None:
        for role in ("snapshot_id", "source_clock_id"):
            object.__setattr__(
                self,
                role,
                _identifier(getattr(self, role), role),
            )
        if (
            isinstance(self.source_window_start_tick, bool)
            or isinstance(self.source_window_end_tick, bool)
            or not isinstance(self.source_window_start_tick, int)
            or not isinstance(self.source_window_end_tick, int)
            or self.source_window_start_tick < 0
            or self.source_window_end_tick <= self.source_window_start_tick
        ):
            raise TransientNeuronInputError(
                "source ticks must form one positive ordered interval"
            )
        if not isinstance(self.organism_read_time, CommonFieldTime):
            raise TransientNeuronInputError(
                "local contact requires its measured organism read time"
            )
        value = float(self.value)
        if not math.isfinite(value) or abs(value) > 1.0:
            raise TransientNeuronInputError(
                "local receptor value must stay within the normalized domain"
            )
        object.__setattr__(self, "value", value)

    @property
    def completion_tick(self) -> int:
        return self.organism_read_time.window_end_tick


@dataclass(frozen=True, slots=True)
class TransientNeuronDockInput:
    """One neuron's complete local dock history for a proposal span."""

    neuron_id: str
    dock_id: str
    carrier_id: str
    step_time: MCMFieldStepTime
    contacts: tuple[TransientLocalReceptorContact, ...]

    def __post_init__(self) -> None:
        for role in ("neuron_id", "dock_id", "carrier_id"):
            object.__setattr__(
                self,
                role,
                _identifier(getattr(self, role), role),
            )
        if not isinstance(self.step_time, MCMFieldStepTime):
            raise TransientNeuronInputError(
                "neuron dock input requires one proposal time span"
            )
        contacts = tuple(self.contacts)
        if any(
            not isinstance(item, TransientLocalReceptorContact)
            for item in contacts
        ):
            raise TransientNeuronInputError(
                "neuron dock input requires local receptor contacts"
            )
        completion_ticks = [item.completion_tick for item in contacts]
        if completion_ticks != sorted(set(completion_ticks)):
            raise TransientNeuronInputError(
                "local receptor contacts must have unique ordered completions"
            )
        if any(
            not (
                self.step_time.start_tick
                < item.completion_tick
                <= self.step_time.end_tick
            )
            or item.organism_read_time.clock_id != self.step_time.clock_id
            for item in contacts
        ):
            raise TransientNeuronInputError(
                "local contacts must stay inside the proposal organism time"
            )
        identities = [item.snapshot_id for item in contacts]
        if len(set(identities)) != len(identities):
            raise TransientNeuronInputError(
                "local receptor snapshot identities must be unique"
            )
        object.__setattr__(self, "contacts", contacts)


@dataclass(frozen=True, slots=True)
class TransientNeuronInputSet:
    """Complete local input anatomy for one proposal, without field state."""

    step_time: MCMFieldStepTime
    neuron_inputs: tuple[TransientNeuronDockInput, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.step_time, MCMFieldStepTime):
            raise TransientNeuronInputError(
                "input set requires one proposal time span"
            )
        neuron_inputs = tuple(self.neuron_inputs)
        if not neuron_inputs or any(
            not isinstance(item, TransientNeuronDockInput)
            for item in neuron_inputs
        ):
            raise TransientNeuronInputError(
                "input set requires local neuron dock inputs"
            )
        if any(item.step_time != self.step_time for item in neuron_inputs):
            raise TransientNeuronInputError(
                "every local neuron input must share the proposal time span"
            )
        neuron_ids = [item.neuron_id for item in neuron_inputs]
        if len(set(neuron_ids)) != len(neuron_ids):
            raise TransientNeuronInputError(
                "one proposal permits one transient input per neuron"
            )
        object.__setattr__(
            self,
            "neuron_inputs",
            tuple(sorted(neuron_inputs, key=lambda item: item.neuron_id)),
        )

    @property
    def contact_count(self) -> int:
        return sum(len(item.contacts) for item in self.neuron_inputs)

    def for_neuron(self, neuron_id: str) -> TransientNeuronDockInput:
        neuron_id = _identifier(neuron_id, "neuron_id")
        for item in self.neuron_inputs:
            if item.neuron_id == neuron_id:
                return item
        raise KeyError(neuron_id)


def project_transient_docks_to_neuron_inputs(
    trajectory: TransientDockTrajectory,
    docks: tuple[SharedFieldDock, ...],
) -> TransientNeuronInputSet:
    """Expose each carrier history only to its mapped local neuron."""

    if not isinstance(trajectory, TransientDockTrajectory):
        raise TransientNeuronInputError(
            "local projection requires one transient dock trajectory"
        )
    docks_in = tuple(docks)
    if not docks_in or any(
        not isinstance(dock, SharedFieldDock) for dock in docks_in
    ):
        raise TransientNeuronInputError(
            "local projection requires shared field docks"
        )
    dock_ids = [dock.dock_id for dock in docks_in]
    if set(dock_ids) != set(trajectory.attached_dock_ids):
        raise TransientNeuronInputError(
            "shared field docks must match the transient trajectory anatomy"
        )
    if len(set(dock_ids)) != len(dock_ids):
        raise TransientNeuronInputError("shared field dock identities must be unique")

    anatomy: dict[str, tuple[str, str]] = {}
    docks_by_id = {dock.dock_id: dock for dock in docks_in}
    for dock in docks_in:
        for carrier_id, neuron_id in dock.dock_map.pairs:
            if neuron_id in anatomy:
                raise TransientNeuronInputError(
                    "one neuron cannot receive multiple receptor carriers"
                )
            anatomy[neuron_id] = (dock.dock_id, carrier_id)

    contacts_by_neuron: dict[str, list[TransientLocalReceptorContact]] = {
        neuron_id: [] for neuron_id in anatomy
    }
    for group in trajectory.completion_groups:
        for dock_frame in group.dock_frames:
            dock = docks_by_id[dock_frame.dock_id]
            frame = dock_frame.timed_frame.frame
            try:
                mapped_values = dock.dock_map.contacts_for(frame)
            except ValueError as exc:
                raise TransientNeuronInputError(
                    f"dock {dock.dock_id} rejected its transient frame: {exc}"
                ) from exc
            for neuron_id, value in mapped_values.items():
                contacts_by_neuron[neuron_id].append(
                    TransientLocalReceptorContact(
                        snapshot_id=frame.snapshot_id,
                        source_clock_id=frame.clock_id,
                        source_window_start_tick=frame.window_start_tick,
                        source_window_end_tick=frame.window_end_tick,
                        organism_read_time=dock_frame.timed_frame.field_time,
                        value=value,
                    )
                )

    return TransientNeuronInputSet(
        step_time=trajectory.step_time,
        neuron_inputs=tuple(
            TransientNeuronDockInput(
                neuron_id=neuron_id,
                dock_id=dock_id,
                carrier_id=carrier_id,
                step_time=trajectory.step_time,
                contacts=tuple(contacts_by_neuron[neuron_id]),
            )
            for neuron_id, (dock_id, carrier_id) in anatomy.items()
        ),
    )


def transient_neuron_input_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            TransientLocalReceptorContact,
            TransientNeuronDockInput,
            TransientNeuronInputSet,
        )
        for item in fields(contract)
    )
