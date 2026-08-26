"""Private pure S1-WU read-only probe over stabilized PPB-1 states."""

from __future__ import annotations

from dataclasses import dataclass
import re

from ._ppb1_reference import (
    PPB1BankConfig,
    PPB1BankState,
    PPB1_INVALID_INPUT,
    PPB1ReferenceError,
    _digest,
    _finite,
    _identifier,
    _input_projection,
    _validate_frame,
    _validate_state,
    normalized_mean_l1_distance,
)
from ._ppb1_s1wq_perceptual_state_lifecycle import _state_identity_payload
from .receptor_contract import ReceptorContactFrame


S1WU_SCHEMA_VERSION = "ppb1.s1wu.private.read-only-perceptual-probe.v1"
S1WU_CONTRACT_DIGEST = (
    "909d3dc3d01ec3b94b53f0c770e615364e08ecb0b91f3aaefc72daf3aa834559"
)
S1WU_PREFLIGHT_DIGEST = (
    "1e27f509ab37b785334da34ff833d4dc4184d908bbde7eea694cf29549aa43ae"
)
S1WU_INVALID_PROBE = "S1WU_INVALID_PROBE"
S1WU_INVALID_FINDING = "S1WU_INVALID_FINDING"

_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class S1WUProbeError(ValueError):
    """One fail-closed private read-only probe boundary violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


def _prototype_digest(values: tuple[float, ...]) -> str:
    return _digest({"normalized_prototype_values": list(values)})


@dataclass(frozen=True, slots=True)
class S1WUReadOnlyPerceptualFinding:
    probe_id: str
    bank_id: str
    modality_id: str
    bank_config_digest: str
    observed_bank_state_digest: str
    state_identity_digest: str
    probe_input_digest: str
    eligible_slot_count: int
    recognized: bool
    selected_slot_id: str | None
    match_distance: float | None
    selected_prototype_digest: str | None
    finding_digest: str
    schema_version: str = S1WU_SCHEMA_VERSION

    def __post_init__(self) -> None:
        try:
            _identifier(self.probe_id, "probe_id", S1WU_INVALID_FINDING)
            _identifier(self.bank_id, "bank_id", S1WU_INVALID_FINDING)
        except PPB1ReferenceError as exc:
            raise S1WUProbeError(S1WU_INVALID_FINDING, exc.detail) from exc
        if (
            self.schema_version != S1WU_SCHEMA_VERSION
            or self.modality_id not in {"auditory", "visual"}
            or not all(
                _valid_digest(value)
                for value in (
                    self.bank_config_digest,
                    self.observed_bank_state_digest,
                    self.state_identity_digest,
                    self.probe_input_digest,
                )
            )
            or isinstance(self.eligible_slot_count, bool)
            or not isinstance(self.eligible_slot_count, int)
            or self.eligible_slot_count < 0
            or not isinstance(self.recognized, bool)
        ):
            raise S1WUProbeError(
                S1WU_INVALID_FINDING,
                "finding identity, digest, count or decision is invalid",
            )
        if self.eligible_slot_count == 0:
            if (
                self.recognized
                or self.selected_slot_id is not None
                or self.match_distance is not None
                or self.selected_prototype_digest is not None
            ):
                raise S1WUProbeError(
                    S1WU_INVALID_FINDING,
                    "empty eligible inventory requires an empty negative finding",
                )
        else:
            try:
                _identifier(
                    self.selected_slot_id,
                    "selected_slot_id",
                    S1WU_INVALID_FINDING,
                )
                distance = _finite(
                    self.match_distance,
                    "match_distance",
                    S1WU_INVALID_FINDING,
                )
            except PPB1ReferenceError as exc:
                raise S1WUProbeError(S1WU_INVALID_FINDING, exc.detail) from exc
            if (
                distance < 0.0
                or distance > 2.0
                or not _valid_digest(self.selected_prototype_digest)
            ):
                raise S1WUProbeError(
                    S1WU_INVALID_FINDING,
                    "nonempty eligible inventory requires one bounded nearest result",
                )
        if self.finding_digest != _digest(self.payload_without_digest()):
            raise S1WUProbeError(
                S1WU_INVALID_FINDING,
                "finding digest does not bind the read-only result",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "contract_digest": S1WU_CONTRACT_DIGEST,
            "preflight_digest": S1WU_PREFLIGHT_DIGEST,
            "probe_id": self.probe_id,
            "bank_id": self.bank_id,
            "modality_id": self.modality_id,
            "bank_config_digest": self.bank_config_digest,
            "observed_bank_state_digest": self.observed_bank_state_digest,
            "state_identity_digest": self.state_identity_digest,
            "probe_input_digest": self.probe_input_digest,
            "eligible_slot_count": self.eligible_slot_count,
            "recognized": self.recognized,
            "selected_slot_id": self.selected_slot_id,
            "match_distance": self.match_distance,
            "selected_prototype_digest": self.selected_prototype_digest,
        }

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "finding_digest": self.finding_digest,
        }


def probe_s1wu_perceptual_state(
    config: PPB1BankConfig,
    state: PPB1BankState,
    frame: ReceptorContactFrame,
    probe_id: str,
) -> S1WUReadOnlyPerceptualFinding:
    """Compare one later reduced input without returning or changing state."""

    if not isinstance(config, PPB1BankConfig):
        raise S1WUProbeError(S1WU_INVALID_PROBE, "config is required")
    try:
        validated_state = _validate_state(config, state)
        validated_frame = _validate_frame(config, frame)
        validated_probe_id = _identifier(
            probe_id,
            "probe_id",
            PPB1_INVALID_INPUT,
        )
    except PPB1ReferenceError as exc:
        raise S1WUProbeError(S1WU_INVALID_PROBE, exc.detail) from exc

    before_digest = validated_state.digest()
    identity_digest = _digest(_state_identity_payload(validated_state))
    if (
        validated_state.source_clock_id is None
        or validated_state.last_source_window_end_tick is None
        or validated_frame.clock_id != validated_state.source_clock_id
        or validated_frame.window_end_tick
        <= validated_state.last_source_window_end_tick
    ):
        raise S1WUProbeError(
            S1WU_INVALID_PROBE,
            "probe must be causally later on the committed source clock",
        )

    eligible = tuple(
        slot
        for slot in validated_state.slots
        if (
            slot.occupied
            and slot.support_count is not None
            and slot.support_count >= config.stable_after
        )
    )
    candidates = tuple(
        (
            normalized_mean_l1_distance(
                validated_frame.values,
                slot.prototype_values,
            ),
            slot.slot_id,
            slot,
        )
        for slot in eligible
    )
    if candidates:
        distance, slot_id, selected = min(candidates)
        recognized = distance <= config.match_threshold
        prototype_digest = _prototype_digest(selected.prototype_values)
    else:
        distance = None
        slot_id = None
        recognized = False
        prototype_digest = None

    if (
        validated_state.digest() != before_digest
        or _digest(_state_identity_payload(validated_state)) != identity_digest
    ):
        raise S1WUProbeError(
            S1WU_INVALID_PROBE,
            "read-only observation changed bank state or identity",
        )
    values = {
        "probe_id": validated_probe_id,
        "bank_id": config.bank_id,
        "modality_id": config.modality_id,
        "bank_config_digest": config.digest(),
        "observed_bank_state_digest": before_digest,
        "state_identity_digest": identity_digest,
        "probe_input_digest": _digest(_input_projection(validated_frame)),
        "eligible_slot_count": len(eligible),
        "recognized": recognized,
        "selected_slot_id": slot_id,
        "match_distance": distance,
        "selected_prototype_digest": prototype_digest,
    }
    payload = {
        "schema_version": S1WU_SCHEMA_VERSION,
        "contract_digest": S1WU_CONTRACT_DIGEST,
        "preflight_digest": S1WU_PREFLIGHT_DIGEST,
        **values,
    }
    return S1WUReadOnlyPerceptualFinding(
        **values,
        finding_digest=_digest(payload),
    )
