"""Passive decomposition of one neuron's local MCM field perception."""

from __future__ import annotations

from dataclasses import dataclass

from .mcm_neuron_layer import MCMNeuronDrive


@dataclass(frozen=True, slots=True)
class MCMLocalPairDifference:
    """Signed prior-tick difference to one spatial field sample."""

    sample_id: str
    relative_position: tuple[int, ...]
    activation_difference: float
    afterimage_difference: float


@dataclass(frozen=True, slots=True)
class MCMLocalFunctionObservation:
    """Separated local inputs without an update equation or fitted coefficient."""

    neuron_id: str
    source_tick: int
    target_tick: int
    receptor_contact: float | None
    prior_activation: float
    prior_afterimage: float
    pair_differences: tuple[MCMLocalPairDifference, ...]

    @property
    def activation_pair_sum(self) -> float:
        return sum(item.activation_difference for item in self.pair_differences)

    @property
    def afterimage_pair_sum(self) -> float:
        return sum(item.afterimage_difference for item in self.pair_differences)

    @property
    def activation_pair_mean(self) -> float:
        if not self.pair_differences:
            return 0.0
        return self.activation_pair_sum / len(self.pair_differences)

    @property
    def afterimage_pair_mean(self) -> float:
        if not self.pair_differences:
            return 0.0
        return self.afterimage_pair_sum / len(self.pair_differences)


def observe_local_mcm_function(
    drive: MCMNeuronDrive,
) -> MCMLocalFunctionObservation:
    """Expose what a local rule could read, without deciding how it must react."""

    if not isinstance(drive, MCMNeuronDrive):
        raise TypeError("drive must be a causally valid MCMNeuronDrive")

    previous = drive.previous
    differences = tuple(
        MCMLocalPairDifference(
            sample_id=sample.sample_id,
            relative_position=sample.relative_position,
            activation_difference=sample.activation - previous.activation,
            afterimage_difference=sample.afterimage - previous.afterimage,
        )
        for sample in drive.perception.local_samples
    )
    return MCMLocalFunctionObservation(
        neuron_id=previous.neuron_id,
        source_tick=previous.tick,
        target_tick=drive.perception.tick,
        receptor_contact=drive.perception.receptor_contact,
        prior_activation=previous.activation,
        prior_afterimage=previous.afterimage,
        pair_differences=differences,
    )
