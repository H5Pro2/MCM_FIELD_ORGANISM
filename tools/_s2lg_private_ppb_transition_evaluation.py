"""Pure S2-LG derivation and evaluation of the bound LC02 PPB chain."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math


S2LG_SCHEMA = "s2lg.private-ppb-transition-evaluation.v1"
UPDATE_RATE = 0.05
SLOW_THRESHOLD = 0.02
EVENT_CHAIN = ("CREATED", "MATCHED", "MATCHED")
SUPPORT_CHAIN = (1, 2, 3)
INPUT_FULL_DIGEST = "dc28fbb4ee22315131333a2c871ee82d958600d832a05c7d972db1e3acb4a023"
STEP_FULL_DIGESTS = (
    "dc28fbb4ee22315131333a2c871ee82d958600d832a05c7d972db1e3acb4a023",
    "74586d098394ad463b427f37a674073c5451edb085ba07c222f9384e60d42968",
    "24c77fb0e9c027798884e33f28b8b14f0d4fde9723142a6937ab3546b203bd3e",
)
STEP_MASKED_DIGESTS = (
    "1622004a498c487579e941a9b99193eded1a966420f916140251e21933ee1ba9",
    "1b04e6b862463cc9a7d27725a5d3783bf3e58bd40f0f7bf24297f39fee2c2b11",
    "8408f2f4452b64cd8bf53847b91de8d8a34d29f64191c344cf8684726974191e",
)
INTEGRITY_VALID = "PPB_TRANSITION_INTEGRITY_VALID"
INTEGRITY_INVALID = "PPB_TRANSITION_INTEGRITY_INVALID"
FUNCTIONAL_MATCH = "FUNCTIONAL_OBSERVED_L1_MATCH"
FUNCTIONAL_NO_MATCH = "FUNCTIONAL_OBSERVED_L1_NO_MATCH"


class S2LGError(ValueError):
    """One event, support, value, or evaluation binding differs."""


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _values(value: object, length: int, role: str) -> tuple[float, ...]:
    if (
        type(value) is not tuple
        or len(value) != length
        or any(type(item) not in (int, float) for item in value)
    ):
        raise S2LGError(f"{role} must be one exact {length}-value numeric tuple")
    result = tuple(float(item) for item in value)
    if any(not math.isfinite(item) or abs(item) > 1.0 for item in result):
        raise S2LGError(f"{role} differs from the bound receptor domain")
    return result


@dataclass(frozen=True, slots=True)
class S2LGTransitionStepV1:
    call_ordinal: int
    event: str
    support: int
    input_digest: str
    prototype_full_digest: str
    prototype_masked_digest: str
    changed_position_count_from_input: int
    maximum_absolute_difference_from_input: float
    step_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "step_digest"
        }


@dataclass(frozen=True, slots=True)
class S2LGTransitionEvaluationV1:
    event_chain: tuple[str, ...]
    support_chain: tuple[int, ...]
    ordered_chain_digest: str
    steps: tuple[S2LGTransitionStepV1, ...]
    derived_final_full_digest: str
    derived_final_masked_digest: str
    recorded_final_full_digest: str
    recorded_hypothesis_masked_digest: str
    transition_integrity_status: str
    observed_l1_distance: float
    slow_threshold: float
    functional_match_status: str
    evaluation_digest: str
    schema: str = S2LG_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "event_chain": list(self.event_chain),
            "support_chain": list(self.support_chain),
            "ordered_chain_digest": self.ordered_chain_digest,
            "step_digests": [step.step_digest for step in self.steps],
            "derived_final_full_digest": self.derived_final_full_digest,
            "derived_final_masked_digest": self.derived_final_masked_digest,
            "recorded_final_full_digest": self.recorded_final_full_digest,
            "recorded_hypothesis_masked_digest": self.recorded_hypothesis_masked_digest,
            "transition_integrity_status": self.transition_integrity_status,
            "observed_l1_distance": self.observed_l1_distance,
            "slow_threshold": self.slow_threshold,
            "functional_match_status": self.functional_match_status,
        }


def _matched_update(previous: tuple[float, ...], current: tuple[float, ...]) -> tuple[float, ...]:
    # Keep this expression identical to PPB-1; algebraic simplification changes bits.
    return tuple(
        (1.0 - UPDATE_RATE) * previous_value + UPDATE_RATE * current_value
        for previous_value, current_value in zip(previous, current, strict=True)
    )


def derive_and_evaluate_lc02(
    *,
    ppb_inputs: tuple[tuple[float, ...], ...],
    event_chain: tuple[str, ...],
    support_chain: tuple[int, ...],
    recorded_final_values: tuple[float, ...],
    recorded_hypothesis_values: tuple[float, ...],
    observed_cue_values: tuple[float, ...],
) -> S2LGTransitionEvaluationV1:
    """Derive the exact PPB chain and evaluate integrity separately from L1."""

    if type(ppb_inputs) is not tuple or len(ppb_inputs) != 3:
        raise S2LGError("exactly three PPB inputs are required")
    if type(event_chain) is not tuple or event_chain != EVENT_CHAIN:
        raise S2LGError("event chain differs from CREATED/MATCHED/MATCHED")
    if type(support_chain) is not tuple or support_chain != SUPPORT_CHAIN:
        raise S2LGError("support chain differs from 1/2/3")
    inputs = tuple(_values(item, 48, f"PPB input {index}") for index, item in enumerate(ppb_inputs))
    input_digests = tuple(_digest(list(item)) for item in inputs)
    if input_digests != (INPUT_FULL_DIGEST,) * 3 or not all(item == inputs[0] for item in inputs[1:]):
        raise S2LGError("PPB inputs are not the three bitidentical bound P vectors")
    recorded = _values(recorded_final_values, 48, "recorded final prototype")
    hypothesis = _values(recorded_hypothesis_values, 24, "recorded masked hypothesis")
    cue = _values(observed_cue_values, 24, "observed cue")

    prototypes = (inputs[0],)
    prototypes += (_matched_update(prototypes[-1], inputs[1]),)
    prototypes += (_matched_update(prototypes[-1], inputs[2]),)
    full_digests = tuple(_digest(list(item)) for item in prototypes)
    masked_digests = tuple(_digest(list(item[24:])) for item in prototypes)
    if full_digests != STEP_FULL_DIGESTS or masked_digests != STEP_MASKED_DIGESTS:
        raise S2LGError("derived transition digests differ from the static contract")

    steps: list[S2LGTransitionStepV1] = []
    for index, prototype in enumerate(prototypes):
        payload = {
            "call_ordinal": index + 1,
            "event": event_chain[index],
            "support": support_chain[index],
            "input_digest": input_digests[index],
            "prototype_full_digest": full_digests[index],
            "prototype_masked_digest": masked_digests[index],
            "changed_position_count_from_input": sum(
                left != right for left, right in zip(prototype, inputs[0], strict=True)
            ),
            "maximum_absolute_difference_from_input": max(
                abs(left - right) for left, right in zip(prototype, inputs[0], strict=True)
            ),
        }
        steps.append(S2LGTransitionStepV1(*payload.values(), _digest(payload)))

    ordered_chain_payload = {
        "event_chain": list(event_chain),
        "support_chain": list(support_chain),
        "input_digests": list(input_digests),
        "step_digests": [step.step_digest for step in steps],
    }
    final_full = _digest(list(recorded))
    final_masked = _digest(list(hypothesis))
    integrity = (
        INTEGRITY_VALID
        if recorded == prototypes[-1] and hypothesis == prototypes[-1][24:]
        else INTEGRITY_INVALID
    )
    observed_l1 = sum(abs(recorded[index] - cue[index]) for index in range(24)) / 24
    functional = FUNCTIONAL_MATCH if observed_l1 <= SLOW_THRESHOLD else FUNCTIONAL_NO_MATCH
    payload = {
        "schema": S2LG_SCHEMA,
        "event_chain": list(event_chain),
        "support_chain": list(support_chain),
        "ordered_chain_digest": _digest(ordered_chain_payload),
        "step_digests": [step.step_digest for step in steps],
        "derived_final_full_digest": full_digests[-1],
        "derived_final_masked_digest": masked_digests[-1],
        "recorded_final_full_digest": final_full,
        "recorded_hypothesis_masked_digest": final_masked,
        "transition_integrity_status": integrity,
        "observed_l1_distance": observed_l1,
        "slow_threshold": SLOW_THRESHOLD,
        "functional_match_status": functional,
    }
    return S2LGTransitionEvaluationV1(
        event_chain,
        support_chain,
        payload["ordered_chain_digest"],  # type: ignore[arg-type]
        tuple(steps),
        full_digests[-1],
        masked_digests[-1],
        final_full,
        final_masked,
        integrity,
        observed_l1,
        SLOW_THRESHOLD,
        functional,
        _digest(payload),
    )


__all__: tuple[str, ...] = ()
