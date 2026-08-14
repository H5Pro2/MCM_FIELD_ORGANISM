"""Device-neutral dock geometry for auditory and visual receptor fields."""

from __future__ import annotations

from .shared_mcm_field import ReceptorDockAnatomy


class FiniteAudioVideoFieldError(ValueError):
    """Raised when finite audio-video field roles are incomplete."""


ORTHOGONAL_FIELD_SAMPLE_OFFSETS = ((-1, 0), (0, -1), (0, 1), (1, 0))


def audio_video_dock_anatomies(
    *,
    auditory_carrier_count: int,
    visual_grid_columns: int,
    visual_grid_rows: int,
    visual_channel_count: int = 3,
) -> dict[str, ReceptorDockAnatomy]:
    """Place both receptor docks in one explicit two-dimensional geometry."""

    dimensions = {
        "auditory_carrier_count": auditory_carrier_count,
        "visual_grid_columns": visual_grid_columns,
        "visual_grid_rows": visual_grid_rows,
        "visual_channel_count": visual_channel_count,
    }
    if any(
        isinstance(value, bool) or not isinstance(value, int) or value <= 0
        for value in dimensions.values()
    ):
        raise FiniteAudioVideoFieldError(
            "dock anatomy dimensions must be positive integers"
        )

    visual_row_width = visual_grid_columns * visual_channel_count
    visual_count = visual_row_width * visual_grid_rows
    return {
        "auditory": ReceptorDockAnatomy(
            modality_id="auditory",
            dock_id="dock.auditory",
            positions=tuple((0, column) for column in range(auditory_carrier_count)),
        ),
        "visual": ReceptorDockAnatomy(
            modality_id="visual",
            dock_id="dock.visual",
            positions=tuple(
                (1 + index // visual_row_width, index % visual_row_width)
                for index in range(visual_count)
            ),
        ),
    }

