"""Explicit raw-frame boundary for one evolving visual MCM field shell."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from typing import Iterable

from .finite_video_path import (
    LocalChannelGridReceptor,
    VisualCaptureError,
    VisualGridConfig,
    VisualReceptorContact,
)
from .mcm_distributor import MCMFieldWindow
from .mcm_neuron_layer import MCMNeuronTransition
from .sensor_mcm_field import (
    CommonFieldTime,
    SensorMCMField,
    SensorMCMFieldError,
    build_receptor_aligned_mcm_field,
    from_visual_receptor_state,
)


class VisualMCMInterfaceError(ValueError):
    """Raised when the visual receptor-to-field boundary is violated."""


@dataclass(frozen=True, slots=True)
class VisualMCMInterfaceOutput:
    """Reduced current contact and completed visual field window only."""

    frame_index: int
    receptor_contact: VisualReceptorContact
    field_window: MCMFieldWindow

    def __post_init__(self) -> None:
        if self.field_window.modality_id != "visual":
            raise VisualMCMInterfaceError("output requires a visual MCM field window")
        if self.field_window.window_end_tick <= self.field_window.window_start_tick:
            raise VisualMCMInterfaceError("output requires a positive organism-time interval")


@dataclass(frozen=True, slots=True)
class VisualMCMInterface:
    """Immutable interface state; it never retains a source image."""

    config: VisualGridConfig
    sample_offsets: tuple[tuple[int, int, int], ...]
    dock_id: str
    layer_id: str
    field_id: str
    field_geometry_id: str
    next_frame_index: int = 0
    current_field: SensorMCMField | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.config, VisualGridConfig):
            raise VisualMCMInterfaceError("config must be a VisualGridConfig")
        if (
            isinstance(self.next_frame_index, bool)
            or not isinstance(self.next_frame_index, int)
            or self.next_frame_index < 0
        ):
            raise VisualMCMInterfaceError("next_frame_index must be non-negative")
        offsets = tuple(tuple(offset) for offset in self.sample_offsets)
        if not offsets or any(len(offset) != 3 for offset in offsets):
            raise VisualMCMInterfaceError("visual sample offsets must use three dimensions")
        if any(tuple(-value for value in offset) not in offsets for offset in offsets):
            raise VisualMCMInterfaceError("visual sample offsets must contain opposites")
        identifiers = (self.dock_id, self.layer_id, self.field_id, self.field_geometry_id)
        if any(not isinstance(value, str) or not value for value in identifiers):
            raise VisualMCMInterfaceError("visual field identifiers must be non-empty")
        if self.current_field is not None:
            if self.current_field.modality_id != "visual":
                raise VisualMCMInterfaceError("current field must remain visual")
            if self.current_field.layer.tick != self.next_frame_index:
                raise VisualMCMInterfaceError("field tick and next frame index must agree")
            if self.current_field.dock_id != self.dock_id:
                raise VisualMCMInterfaceError("current field dock cannot change")
            if self.current_field.field_id != self.field_id:
                raise VisualMCMInterfaceError("current visual field identity cannot change")
        object.__setattr__(self, "sample_offsets", offsets)

    @property
    def positions(self) -> tuple[tuple[int, int, int], ...]:
        return tuple(
            (row, column, channel)
            for row in range(self.config.grid_rows)
            for column in range(self.config.grid_columns)
            for channel in range(3)
        )

    def advance(
        self,
        frame: object,
        field_time: CommonFieldTime,
        transition: MCMNeuronTransition,
    ) -> tuple["VisualMCMInterface", VisualMCMInterfaceOutput]:
        """Consume one frame without retaining it and return the next interface state."""

        if not isinstance(field_time, CommonFieldTime):
            raise VisualMCMInterfaceError("field_time must use the common field clock")
        try:
            receptor_state = LocalChannelGridReceptor(self.config).analyze(
                frame,
                frame_index=self.next_frame_index,
            )
            receptor_frame = from_visual_receptor_state(receptor_state)
            field = self.current_field
            if field is None:
                field = build_receptor_aligned_mcm_field(
                    receptor_frame,
                    positions=self.positions,
                    sample_offsets=self.sample_offsets,
                    dock_id=self.dock_id,
                    layer_id=self.layer_id,
                    field_id=self.field_id,
                    field_geometry_id=self.field_geometry_id,
                )
            next_field = field.advance(receptor_frame, field_time, transition)
        except (VisualCaptureError, SensorMCMFieldError) as exc:
            raise VisualMCMInterfaceError("visual receptor-to-field advance failed") from exc
        output = VisualMCMInterfaceOutput(
            frame_index=self.next_frame_index,
            receptor_contact=receptor_state.contact,
            field_window=next_field.field_window(),
        )
        return (
            replace(
                self,
                next_frame_index=self.next_frame_index + 1,
                current_field=next_field,
            ),
            output,
        )


def build_visual_mcm_interface(
    config: VisualGridConfig,
    *,
    sample_offsets: Iterable[Iterable[int]] = (
        (-1, 0, 0),
        (1, 0, 0),
        (0, -1, 0),
        (0, 1, 0),
    ),
    dock_id: str = "dock.visual",
    layer_id: str = "layer.visual",
    field_id: str = "field.visual",
    field_geometry_id: str | None = None,
) -> VisualMCMInterface:
    """Build the technical visual field anatomy without consuming a frame."""

    geometry_id = field_geometry_id or (
        f"mcm.visual.grid{config.grid_columns}x{config.grid_rows}.channels3.v1"
    )
    return VisualMCMInterface(
        config=config,
        sample_offsets=tuple(tuple(offset) for offset in sample_offsets),
        dock_id=dock_id,
        layer_id=layer_id,
        field_id=field_id,
        field_geometry_id=geometry_id,
    )


def visual_mcm_interface_public_roles() -> tuple[str, ...]:
    classes = (VisualMCMInterfaceOutput, VisualMCMInterface)
    return tuple(item.name for cls in classes for item in fields(cls))
