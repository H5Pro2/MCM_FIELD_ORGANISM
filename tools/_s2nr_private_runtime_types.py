"""Closed mask-aware runtime hypothesis; no field or runtime dependency."""
from dataclasses import asdict, dataclass
import math
from tools import _s2nq_private_mask_scan as scan

SCHEMA = "s2nr.mask-runtime.v2"


@dataclass(frozen=True, slots=True)
class MaskedAudioOperationV2:
    cue: scan.Cue
    perception_digest: str
    source_digest: str


@dataclass(frozen=True, slots=True)
class MaskedAudioHypothesisV2:
    band_plan: scan.BandPlan
    profile_digest: str
    config_digest: str
    cue_digest: str
    perception_digest: str
    source_digest: str
    state_digest: str
    candidate: scan.Hypothesis
    schema: str = SCHEMA

    def payload_without_digest(self):
        return asdict(self)

    @property
    def hypothesis_digest(self):
        return scan.digest(self.payload_without_digest())


def validate_hypothesis(value, *, view, profile_digest, config_digest, operation, state_digest):
    scan.require(type(value) is MaskedAudioHypothesisV2 and value.schema == SCHEMA, "HYPOTHESIS_TYPE_INVALID")
    scan.require(type(operation) is MaskedAudioOperationV2 and type(operation.cue) is scan.Cue,
                 "OPERATION_TYPE_INVALID")
    operation.cue.__post_init__()
    bp = scan.plan(view)
    scan.require(value.band_plan == operation.cue.band_plan == bp
        and value.profile_digest == operation.cue.profile_digest == profile_digest == scan.profile.half.PROFILE_DIGEST
        and value.config_digest == operation.cue.config_digest == config_digest,
        "HYPOTHESIS_PROFILE_OR_MASK_INVALID")
    scan.require(value.cue_digest == operation.cue.cue_digest
        and value.perception_digest == operation.perception_digest
        and value.source_digest == operation.source_digest and value.state_digest == state_digest
        and all(scan.hash_form(x) for x in (value.cue_digest,value.perception_digest,value.source_digest,value.state_digest)),
        "HYPOTHESIS_PARENT_INVALID")
    h=value.candidate
    scan.require(type(h) is scan.Hypothesis and h.area in ("A_RECENT","B_STABLE_AUDITORY")
        and type(h.provenance) is tuple and 1 <= len(h.provenance) <= (2 if h.area == "A_RECENT" else 1)
        and all(scan.hash_form(x) for x in h.provenance) and scan.hash_form(h.candidate_digest)
        and h.indices == bp.complement and type(h.indices) is tuple
        and type(h.values) is tuple and len(h.values) == 24
        and all(type(x) is float and math.isfinite(x) and 0 <= x <= 1 for x in h.values),
        "HYPOTHESIS_CANDIDATE_INVALID")
    return value


def wrap(result, operation):
    if result.hypothesis is None:
        return None
    value=MaskedAudioHypothesisV2(operation.cue.band_plan, operation.cue.profile_digest,
        result.config_digest,result.cue_digest,operation.perception_digest,operation.source_digest,
        result.prestate_digest,result.hypothesis)
    return validate_hypothesis(value,view=result.view,profile_digest=operation.cue.profile_digest,
        config_digest=result.config_digest,operation=operation,state_digest=result.prestate_digest)
