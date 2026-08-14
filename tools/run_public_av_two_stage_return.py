from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.public_av_no_input_gap_audit import audit_public_av_no_input_gap_step_time
from mcm_field_organism.public_av_two_stage_return_execution import execute_public_av_two_stage_return_run
from mcm_field_organism.public_av_two_stage_return_preflight import audit_public_av_two_stage_return_preflight
from mcm_field_organism.public_av_two_stage_return_rerun_preflight import (
    audit_public_av_two_stage_return_rerun_preflight,
)
from mcm_field_organism.public_av_two_stage_return_runner import wire_public_av_two_stage_return_runner
from mcm_field_organism.public_media_source_contract import nasa_earthrise_av_source_contract


MEDIA = Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4")


def main() -> int:
    contract = nasa_earthrise_av_source_contract()
    wiring = wire_public_av_two_stage_return_runner()
    gap_audit = audit_public_av_no_input_gap_step_time(wiring)
    preflight = audit_public_av_two_stage_return_preflight(
        MEDIA,
        contract,
        wiring=wiring,
        gap_audit=gap_audit,
    )
    if not preflight.single_bounded_run_release_granted:
        return 2
    rerun_preflight = audit_public_av_two_stage_return_rerun_preflight(
        MEDIA,
        contract,
        base_preflight=preflight,
    )
    if (
        not rerun_preflight.corrected_single_run_release_granted
        or rerun_preflight.repeat_count_authorized != 1
        or rerun_preflight.base_preflight_id != preflight.preflight_id
        or rerun_preflight.media_path != str(MEDIA)
        or rerun_preflight.source_id != contract.source_id
        or rerun_preflight.field_run_started
    ):
        return 3
    result = execute_public_av_two_stage_return_run(
        MEDIA,
        contract,
        wiring,
        gap_audit,
        preflight,
    )
    payload = {
        "runner_id": result.runner_id,
        "source_id": result.source_id,
        "clock_id": result.clock_id,
        "stage_duration_ticks": result.stage_duration_ticks,
        "resolution_duration_ticks": result.resolution_duration_ticks,
        "arms": [
            {
                "arm_id": arm.arm_id,
                "stage_one_source_event_count": arm.stage_one_source_event_count,
                "stage_two_source_event_count": arm.stage_two_source_event_count,
                "stage_one_snapshot_digest": arm.stage_one_snapshot_digest,
                "post_resolution_snapshot_digest": arm.post_resolution_snapshot_digest,
                "stage_two_snapshot_digest": arm.stage_two_snapshot_digest,
                "stage_two_layer_digest": arm.stage_two_layer_digest,
            }
            for arm in result.arms
        ],
        "stage_two_activation_linf_between_arms": result.stage_two_activation_linf_between_arms,
        "stage_two_afterimage_linf_between_arms": result.stage_two_afterimage_linf_between_arms,
        "stage_two_layer_digest_equal": result.stage_two_layer_digest_equal,
        "stage_two_snapshot_digest_equal": result.stage_two_snapshot_digest_equal,
        "raw_payload_retained": result.raw_payload_retained,
        "metadata_used_by_field": result.metadata_used_by_field,
        "memory_claim_allowed": result.memory_claim_allowed,
        "meaning_claim_allowed": result.meaning_claim_allowed,
        "organization_claim_allowed": result.organization_claim_allowed,
        "ai_claim_allowed": result.ai_claim_allowed,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
