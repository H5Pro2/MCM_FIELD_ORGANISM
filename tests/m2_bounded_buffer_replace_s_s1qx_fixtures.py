"""Canonical in-memory fixtures for the private S1-QX M2 compositor."""

from __future__ import annotations

from dataclasses import dataclass

from mcm_field_organism.field_step_time import MCMFieldStepTime
from mcm_field_organism.m2_bounded_buffer_replace_s_compositor import (
    M2BoundedBufferConfiguration,
    M2BoundedBufferState,
    build_empty_m2_buffer,
    build_registered_m2_configuration,
)
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from mcm_field_organism.receptor_contract import (
    CommonFieldTime,
    ReceptorContactFrame,
)
from mcm_field_organism.receptor_distributor import (
    ReceptorDistribution,
    ReceptorDistributor,
    ReceptorDock,
)
from mcm_field_organism.shared_mcm_field import (
    ReceptorDockAnatomy,
    SharedMCMField,
    build_shared_mcm_field,
)
from mcm_field_organism.transient_neuron_input import (
    TransientLocalReceptorContact,
    TransientNeuronDockInput,
    TransientNeuronInputSet,
)


POSITION_IDS = ("P0", "P1", "P2", "P3", "P4")
RECORD_IDS = ("A", "B", "C", "D", "E")
REGISTERED_VALUES = (
    (0.80, -0.40, 0.20),
    (-0.60, 0.70, -0.10),
    (0.30, 0.90, -0.50),
    (-0.20, -0.80, 0.60),
    (0.95, -0.15, -0.70),
)


@dataclass(frozen=True, slots=True)
class M2BoundedBufferFixture:
    field: SharedMCMField
    distribution: ReceptorDistribution
    interval_input: MCMFieldStepTime | TransientNeuronInputSet
    substrate_config: NeutralLocalFieldSubstrateConfig
    afterimage_config: NeutralFastAfterimageConfig
    m2_configuration: M2BoundedBufferConfiguration
    m2_prestate: M2BoundedBufferState


def _reference_frame(size: int) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id="auditory",
        geometry_id="auditory.line.v1",
        snapshot_id="auditory.reference",
        clock_id="auditory.source",
        window_start_tick=0,
        window_end_tick=1,
        carrier_ids=tuple(f"auditory.carrier.{index}" for index in range(size)),
        values=(0.0,) * size,
    )


def build_field(size: int = 3) -> SharedMCMField:
    reference = _reference_frame(size)
    return build_shared_mcm_field(
        (reference,),
        {
            "auditory": ReceptorDockAnatomy(
                "auditory",
                "dock.auditory",
                tuple((index,) for index in range(size)),
            )
        },
        sample_offsets=((-1,), (1,)),
    )


def _distributor() -> ReceptorDistributor:
    distributor = ReceptorDistributor()
    distributor.attach(
        ReceptorDock("dock.auditory", "auditory", "auditory.line.v1")
    )
    return distributor


def _contact_frame(
    start_tick: int,
    end_tick: int,
    values: tuple[float, ...],
) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id="auditory",
        geometry_id="auditory.line.v1",
        snapshot_id=f"auditory.m2.{start_tick}.{end_tick}",
        clock_id="auditory.source",
        window_start_tick=start_tick,
        window_end_tick=end_tick,
        carrier_ids=tuple(
            f"auditory.carrier.{index}" for index in range(len(values))
        ),
        values=values,
    )


def build_sync_fixture(
    mode_id: str = "DELAY",
    *,
    field: SharedMCMField | None = None,
    m2_configuration: M2BoundedBufferConfiguration | None = None,
    m2_prestate: M2BoundedBufferState | None = None,
    start_tick: int = 0,
    values: tuple[float, ...] = REGISTERED_VALUES[0],
) -> M2BoundedBufferFixture:
    current_field = build_field(len(values)) if field is None else field
    end_tick = start_tick + 10
    distribution = _distributor().distribute(
        (_contact_frame(start_tick, end_tick, values),),
        CommonFieldTime("organism.test", start_tick, end_tick),
    )
    interval = MCMFieldStepTime("organism.test", start_tick, end_tick, 10.0)
    configuration = (
        build_registered_m2_configuration(mode_id)
        if m2_configuration is None
        else m2_configuration
    )
    state = (
        build_empty_m2_buffer(configuration, current_field)
        if m2_prestate is None
        else m2_prestate
    )
    return M2BoundedBufferFixture(
        current_field,
        distribution,
        interval,
        NeutralLocalFieldSubstrateConfig(1.0),
        NeutralFastAfterimageConfig(0.5),
        configuration,
        state,
    )


def build_transient_fixture(
    mode_id: str = "DELAY",
    *,
    field: SharedMCMField | None = None,
    m2_configuration: M2BoundedBufferConfiguration | None = None,
    m2_prestate: M2BoundedBufferState | None = None,
    start_tick: int = 0,
    values: tuple[float, ...] = (0.70, -0.30, 0.10),
) -> M2BoundedBufferFixture:
    current_field = build_field(len(values)) if field is None else field
    end_tick = start_tick + 10
    step = MCMFieldStepTime("organism.test", start_tick, end_tick, 10.0)
    distribution = _distributor().distribute(
        (), CommonFieldTime("organism.test", start_tick, end_tick)
    )
    dock = current_field.docks[0]
    pairs = {
        neuron_id: carrier_id
        for carrier_id, neuron_id in dock.dock_map.pairs
    }
    local_inputs = []
    for neuron, value in zip(current_field.layer.neurons, values, strict=True):
        contact = TransientLocalReceptorContact(
            snapshot_id=f"transient.m2.{start_tick}.{neuron.neuron_id}",
            source_clock_id="auditory.source",
            source_window_start_tick=start_tick,
            source_window_end_tick=start_tick + 5,
            organism_read_time=CommonFieldTime(
                "organism.test", start_tick, start_tick + 5
            ),
            value=value,
        )
        local_inputs.append(
            TransientNeuronDockInput(
                neuron.neuron_id,
                dock.dock_id,
                pairs[neuron.neuron_id],
                step,
                (contact,),
            )
        )
    interval = TransientNeuronInputSet(step, tuple(local_inputs))
    configuration = (
        build_registered_m2_configuration(mode_id)
        if m2_configuration is None
        else m2_configuration
    )
    state = (
        build_empty_m2_buffer(configuration, current_field)
        if m2_prestate is None
        else m2_prestate
    )
    return M2BoundedBufferFixture(
        current_field,
        distribution,
        interval,
        NeutralLocalFieldSubstrateConfig(1.0),
        NeutralFastAfterimageConfig(0.5),
        configuration,
        state,
    )
