"""Small reduced-source and PPB transition bindings; no source generation or run."""

from dataclasses import dataclass

from mcm_field_organism.receptor_contract import CommonFieldTime, ReceptorContactFrame
from mcm_field_organism.receptor_time_model import OrganismTimedReceptorFrame
from tools import _s2jw_default_live_av_pairing as pairing
from tools import _s2jw_profiled_memory_coordinator as coordinator
from tools import _s2ne_private_auditory_transfer as ne


def bind_pair(*, config, auditory, visual, ordinal, history_id, event_id,
              auditory_payload_digest, visual_payload_digest):
    """Accept actual reduced frames, binding native and overlapping common time."""
    config = coordinator._validate_config(config)
    ne.check(type(ordinal) is int and ordinal >= 0)
    ne.check(type(auditory) is ReceptorContactFrame and type(visual) is ReceptorContactFrame)
    ne.check(auditory.clock_id == history_id + "-audio-sample"
             and auditory.window_start_tick == 9600 * ordinal
             and auditory.window_end_tick == 9600 * ordinal + 4800)
    ne.check(visual.clock_id == "video.frame"
             and visual.window_start_tick == 6 * ordinal + 2
             and visual.window_end_tick == 6 * ordinal + 3)
    a = OrganismTimedReceptorFrame(auditory, CommonFieldTime(
        history_id + "-pair-clock", 200000000 * ordinal, 200000000 * ordinal + 100000000))
    v = OrganismTimedReceptorFrame(visual, CommonFieldTime(
        history_id + "-pair-clock", (6 * ordinal + 2) * 1000000000 // 30,
        200000000 * ordinal + 100000000))
    plan = pairing.build_s2jv_pairing_plan(
        pair_id=event_id, source_contract_id="s2ne-private-source", profile=config.profile,
        auditory=a, visual=v, auditory_payload_digest=auditory_payload_digest,
        visual_payload_digest=visual_payload_digest)
    return pairing.bind_s2jv_default_live_pair(pairing_plan=plan, profile=config.profile,
                                              auditory=a, visual=v)


@dataclass(frozen=True, slots=True)
class PPBTransitionEvidenceV1:
    config_digest: str
    bank_config_digest: str
    prestate_digest: str
    poststate_digest: str
    generation: int
    slot_id: str
    event: str
    support: int
    input_digest: str
    pre_slot_digest: str
    post_slot_digest: str
    full_values_digest: str
    masked_values_digest: str
    transition_digest: str

    def payload_without_digest(self):
        return {name: getattr(self, name) for name in self.__dataclass_fields__
                if name != "transition_digest"}


def bind_ppb_transition(*, config, prestate, poststate, source, modality, slot_id):
    """Check the existing CREATED/MATCHED update, not a new update operation."""
    config = coordinator._validate_config(config)
    prestate = coordinator._validate_state(config, prestate)
    poststate = coordinator._validate_state(config, poststate)
    source = coordinator._validate_input(config, source)
    ne.check(poststate.parent_state_digest == prestate.state_digest
             and poststate.last_input_digest == source.input_digest)
    ne.check(modality in ("auditory", "visual"))
    bank_config = getattr(config.profile.profile, modality + "_config")
    prebank = getattr(prestate.tspm_state, modality + "_ppb1_state")
    postbank = getattr(poststate.tspm_state, modality + "_ppb1_state")
    ne.check(poststate.generation == prestate.generation + 1
             and postbank.accepted_step_count == prebank.accepted_step_count + 1)
    slots = tuple((a, b) for a, b in zip(prebank.slots, postbank.slots, strict=True)
                  if b.slot_id == slot_id)
    ne.check(len(slots) == 1)
    previous, current = slots[0]
    length = 48 if modality == "auditory" else 288
    values = coordinator._values(getattr(source, modality + "_values"), length, "PPB input")
    if previous.occupied:
        event = "MATCHED"
        expected = tuple((1.0 - bank_config.update_rate) * p + bank_config.update_rate * x
                         for p, x in zip(previous.prototype_values, values, strict=True))
        support = min(previous.support_count + 1, bank_config.stable_after)
    else:
        event, expected, support = "CREATED", values, 1
    ne.check(current.occupied and current.prototype_values == expected
             and current.support_count == support
             and current.last_selected_step == postbank.accepted_step_count)
    for a, b in zip(prebank.slots, postbank.slots, strict=True):
        if b.slot_id != slot_id:
            ne.check(a == b)
    masked = expected[24:] if modality == "auditory" else expected[32:]
    payload = dict(config_digest=config.config_digest, bank_config_digest=bank_config.digest(),
                   prestate_digest=prestate.state_digest, poststate_digest=poststate.state_digest,
                   generation=postbank.accepted_step_count, slot_id=slot_id, event=event, support=support,
                   input_digest=ne.kz.digest(list(values)),
                   pre_slot_digest=ne.kz.digest(previous.canonical_payload()),
                   post_slot_digest=ne.kz.digest(current.canonical_payload()),
                   full_values_digest=ne.kz.digest(list(expected)),
                   masked_values_digest=ne.kz.digest(list(masked)))
    return PPBTransitionEvidenceV1(**payload, transition_digest=ne.kz.digest(payload))


__all__ = ()
