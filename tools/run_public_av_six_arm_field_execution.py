from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.public_av_six_arm_field_execution import (
    execute_public_av_six_arm_field_run,
)
from mcm_field_organism.public_media_source_contract import nasa_earthrise_av_source_contract


def main() -> int:
    path = Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4")
    result = execute_public_av_six_arm_field_run(path, nasa_earthrise_av_source_contract())
    print(json.dumps({
        "runner_id": result.runner_id,
        "source_id": result.source_id,
        "clock_id": result.clock_id,
        "duration_limit_ticks": result.duration_limit_ticks,
        "arms": [
            {
                "arm_id": arm.arm_id,
                "source_event_count": arm.source_event_count,
                "completion_group_count": arm.completion_group_count,
                "mixed_completion_group_count": arm.mixed_completion_group_count,
                "proposal_step_count": arm.proposal_step_count,
                "final_completion_tick": arm.final_completion_tick,
                "layer_digest": arm.layer_digest,
                "snapshot_digest": arm.snapshot_digest,
            }
            for arm in result.arms
        ],
        "joint_reproduction_exact": result.joint_reproduction_exact,
        "permutation_activation_linf": result.permutation_activation_linf,
        "permutation_afterimage_linf": result.permutation_afterimage_linf,
        "coarse_fine_activation_linf": result.coarse_fine_activation_linf,
        "coarse_fine_afterimage_linf": result.coarse_fine_afterimage_linf,
        "auditory_only_activation_linf": result.auditory_only_activation_linf,
        "visual_only_activation_linf": result.visual_only_activation_linf,
        "raw_payload_retained": result.raw_payload_retained,
        "metadata_used_by_field": result.metadata_used_by_field,
        "memory_claim_allowed": result.memory_claim_allowed,
        "meaning_claim_allowed": result.meaning_claim_allowed,
        "organization_claim_allowed": result.organization_claim_allowed,
        "ai_claim_allowed": result.ai_claim_allowed,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
