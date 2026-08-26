"""Run the bounded asynchronous audio-video partition probe."""

from __future__ import annotations

import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcm_field_organism.asynchronous_audio_video_partition_probe import (
    run_asynchronous_audio_video_partition_probe,
)


def main() -> None:
    result = run_asynchronous_audio_video_partition_probe()
    arms = tuple(
        {
            "arm_id": arm.arm_id,
            "source_id": arm.source_id,
            "partition_id": arm.partition_id,
            "sequence_order": arm.sequence_order,
            "source_event_count": arm.source_event_count,
            "completion_group_count": arm.completion_group_count,
            "mixed_completion_group_count": arm.mixed_completion_group_count,
            "final_completion_tick": arm.final_completion_tick,
            "proposal_step_count": arm.proposal_step_count,
            "field_tick": arm.field_tick,
            "activation_l2": math.sqrt(sum(value * value for value in arm.activation)),
            "afterimage_l2": math.sqrt(sum(value * value for value in arm.afterimage)),
        }
        for arm in result.arms
    )
    print(
        json.dumps(
            {
                "arms": arms,
                "coarse_fine_activation_linf": result.coarse_fine_activation_linf,
                "coarse_fine_afterimage_linf": result.coarse_fine_afterimage_linf,
                "permutation_activation_linf": result.permutation_activation_linf,
                "permutation_afterimage_linf": result.permutation_afterimage_linf,
                "reproduction_exact": result.reproduction_exact,
                "source_event_counts_equal": result.source_event_counts_equal,
                "completion_horizon_equal": result.completion_horizon_equal,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
