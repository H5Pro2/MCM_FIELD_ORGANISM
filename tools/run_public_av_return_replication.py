from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.public_av_return_permutation_contract import (
    public_av_return_permutation_contract,
)
from mcm_field_organism.public_av_return_replication_entrypoint import (
    PublicAVReturnReplicationEntrypoint,
)
from mcm_field_organism.public_av_return_replication_execution import (
    bind_public_av_return_replication_executor,
)
from mcm_field_organism.public_av_return_replication_preflight import (
    audit_public_av_return_replication_preflight,
)
from mcm_field_organism.public_av_return_replication_runner import (
    wire_public_av_return_replication_runner,
)
from mcm_field_organism.public_media_source_contract import nasa_earthrise_av_source_contract


MEDIA = Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4")


def _payload(result, receipt) -> dict[str, object]:
    return {
        "execution_id": result.execution_id,
        "runner_id": result.runner_id,
        "preflight_id": result.preflight_id,
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
                "stage_two_contact_mode": arm.stage_two_contact_mode,
                "intervention_audit_id": arm.intervention_audit_id,
            }
            for arm in result.arms
        ],
        "pairwise_activation_linf": result.pairwise_activation_linf,
        "pairwise_afterimage_linf": result.pairwise_afterimage_linf,
        "layer_digest_equality": result.layer_digest_equality,
        "snapshot_digest_equality": result.snapshot_digest_equality,
        "execution_receipt": {
            "preflight_id": receipt.preflight_id,
            "runner_id": receipt.runner_id,
            "source_id": receipt.source_id,
            "release_scope": receipt.release_scope,
            "authorized_repeat_count": receipt.authorized_repeat_count,
            "execution_started": receipt.execution_started,
            "execution_completed": receipt.execution_completed,
            "memory_claim_allowed": receipt.memory_claim_allowed,
            "meaning_claim_allowed": receipt.meaning_claim_allowed,
            "organization_claim_allowed": receipt.organization_claim_allowed,
            "ai_claim_allowed": receipt.ai_claim_allowed,
        },
        "memory_threshold_defined": result.memory_threshold_defined,
        "organization_threshold_defined": result.organization_threshold_defined,
        "memory_claim_allowed": result.memory_claim_allowed,
        "meaning_claim_allowed": result.meaning_claim_allowed,
        "organization_claim_allowed": result.organization_claim_allowed,
        "ai_claim_allowed": result.ai_claim_allowed,
    }


def main() -> int:
    contract = nasa_earthrise_av_source_contract()
    permutation = public_av_return_permutation_contract()
    wiring = wire_public_av_return_replication_runner(permutation_contract=permutation)
    preflight = audit_public_av_return_replication_preflight(
        MEDIA,
        contract,
        permutation_contract=permutation,
        wiring=wiring,
    )
    if (
        not preflight.single_bounded_replication_run_release_granted
        or preflight.repeat_count_authorized != 1
        or preflight.field_run_started
    ):
        return 2
    executor = bind_public_av_return_replication_executor(preflight, permutation)
    gate = PublicAVReturnReplicationEntrypoint(executor)
    result, receipt = gate.start_once(MEDIA, contract, wiring, preflight)
    print(json.dumps(_payload(result, receipt), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
