"""Run the procedural world family through the unchanged shared MCM field."""

from __future__ import annotations

import json

from mcm_field_organism import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    controlled_reentry_world_family,
    run_controlled_test_world,
)


def main() -> None:
    summaries = []
    for world in controlled_reentry_world_family():
        result = run_controlled_test_world(
            world,
            NeutralLocalFieldSubstrateConfig(1.0),
            afterimage_config=NeutralFastAfterimageConfig(0.5),
        )
        field = result.field_run.field
        summaries.append(
            {
                "world_id": world.world_id,
                "world_digest": world.digest(),
                "duration_seconds": world.duration_seconds,
                "receptor_frame_counts": {
                    sequence.modality_id: len(sequence.frames)
                    for sequence in result.receptor_sequences
                },
                "source_support_count": result.field_run.source_support_count,
                "neuron_count": len(field.layer.neurons),
                "field_tick": field.layer.tick,
                "field_digest": field.snapshot().digest(),
                "raw_sensor_payload_retained": False,
                "memory_writeback": False,
            }
        )
    print(json.dumps({"worlds": summaries}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
