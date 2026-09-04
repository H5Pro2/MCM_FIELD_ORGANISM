"""Private S2-LQ extension of the qualified S2-LO role-free stream shell."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from threading import Lock

import numpy as np

from mcm_field_organism.broadband_hearing_path import BroadbandHearingPath
from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from mcm_field_organism.receptor_contract import (
    CommonFieldTime,
    from_auditory_receptor_state,
    from_visual_receptor_state,
)
from mcm_field_organism.receptor_time_model import OrganismTimedReceptorFrame
from tools import _s2kq_private_partial_cue_retrieval_336 as visual_scan
from tools import _s2ks_real_partial_cue_fixtures as visual_cues
from tools import _s2kz_private_auditory_partial_cue_retrieval_336 as auditory_scan
from tools import _s2ld_auditory_partial_cue_fixtures as auditory_fixtures
from tools import _s2lm_private_role_free_stream_processor as stream
from tools import _s2lo_private_role_free_stream_runner as lo_runner
from tools import _s2jw_profiled_memory_coordinator as memory
from tools import _s2jx_default_live_memory_fixtures as visual_fixtures
from tools._s2jw_default_live_av_pairing import (
    S2JVBoundAVPairV1,
    bind_s2jv_default_live_pair,
    build_s2jv_pairing_plan,
)
from tools._s2jw_default_live_profile import S2JWDefaultLiveProfileV1


S2LQ_SCHEMA = "s2lq.role-free-multipattern-stream.v1"
S2LQ_RESULT_SCHEMA = "s2lq.role-free-multipattern-result.v1"
QUALIFICATION_ID = "s2lq-neutral-qualification-20260904-01"
AUTHORIZED_RUN_ID = "s2lq-main-not-authorized"
MAIN_EXECUTION_ENABLED = False
MAX_RESULT_BYTES = 1_048_576

MAIN_EVENT_COUNT = 29
MAIN_FORMATION_COUNT = 21
MAIN_AUDITORY_CUE_COUNT = 4
MAIN_VISUAL_CUE_COUNT = 4
MAIN_FIELD_CONTACTS = 8_400
MAIN_MEMORY_L1_TERMS = 74_592
MAIN_SCAN_COMPARISONS = 10_624
MAIN_RAW_BYTES = 156_000_000

_RUN_ID = re.compile(r"^[a-z][a-z0-9-]{7,95}$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_MAIN_LOCK = Lock()
_MAIN_USED = False

SOURCE_PATHS = (
    *lo_runner.SOURCE_PATHS,
    "tools/_s2lq_private_multipattern_stream_runner.py",
    "tools/_s2lq_private_multipattern_stream_verifier.py",
)

_FORMATION_CONTENTS = (
    "p00", "p01", "p02", "p00", "p01", "p00", "p01", "p00", "p01",
    "p02", "p02", "p03", "p04", "p05", "p06", "p07", "p08", "p09",
    "p10", "p11", "p12",
)
_CONTENT_RECIPES = {
    "p00": ("P", "X"),
    "p01": ("H", "Y"),
    "p02": ("D_FAR", "B0"),
    "p03": ("L", "S1"),
    **{f"p{index + 3:02d}": ("D_FAR", f"D{index}") for index in range(1, 10)},
}
_CUE_CONTENTS = (
    ("PARTIAL_AUDITORY_CUE", "p00"),
    ("PARTIAL_VISUAL_CUE", "p00"),
    ("PARTIAL_AUDITORY_CUE", "p01"),
    ("PARTIAL_VISUAL_CUE", "p01"),
    ("PARTIAL_AUDITORY_CUE", "p02"),
    ("PARTIAL_VISUAL_CUE", "p02"),
    ("PARTIAL_AUDITORY_CUE", "p03"),
    ("PARTIAL_VISUAL_CUE", "p03"),
)


class S2LQError(RuntimeError):
    """One bounded S2-LQ source, evaluation, or result relation is invalid."""


def _canonical_bytes(value: object, *, newline: bool = False) -> bytes:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return encoded + (b"\n" if newline else b"")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2LQError(message)


def _event_spec(
    ordinal: int,
    event_type: str,
    content_id: str,
) -> lo_runner.S2LOEventSpecV1:
    code = f"e{ordinal:02d}"
    payload = {
        "schema": S2LQ_SCHEMA,
        "event_code": code,
        "event_id": f"s2lq-event-{code}",
        "ordinal": ordinal,
        "event_type": event_type,
        "content_id": content_id,
    }
    return lo_runner.S2LOEventSpecV1(
        code,
        payload["event_id"],
        ordinal,
        event_type,
        content_id,
        _digest(payload),
        S2LQ_SCHEMA,
    )


MAIN_EVENT_SPECS = tuple(
    _event_spec(index, "COMPLETE_AV_PERCEPTION", content)
    for index, content in enumerate(_FORMATION_CONTENTS, start=1)
) + tuple(
    _event_spec(index, event_type, content)
    for index, (event_type, content) in enumerate(_CUE_CONTENTS, start=22)
)

QUALIFICATION_SOURCE_SPECS = tuple(
    _event_spec(index, "COMPLETE_AV_PERCEPTION", content)
    for index, content in enumerate(("p00", "p01", "p02", "p03"), start=1)
)


def _visual_image(recipe: str) -> np.ndarray:
    if recipe in visual_fixtures.FIXTURE_BY_LABEL:
        spec = visual_fixtures.FIXTURE_BY_LABEL[recipe]
        image = visual_fixtures._visual_image(spec.ordinal)
        _require(
            hashlib.sha256(image.tobytes(order="C")).hexdigest()
            == spec.visual_payload_digest,
            "visual fixture digest differs",
        )
        return image
    _require(recipe in {"B0", "S1"}, "visual fixture role differs")
    return visual_cues.visual_image(recipe)


class S2LQSourceStream:
    """Materialize one source at a time while retaining no raw input payload."""

    def __init__(
        self,
        profile: S2JWDefaultLiveProfileV1,
        specs: tuple[lo_runner.S2LOEventSpecV1, ...],
    ) -> None:
        _require(type(profile) is S2JWDefaultLiveProfileV1, "exact profile required")
        _require(
            type(specs) is tuple
            and specs
            and all(type(item) is lo_runner.S2LOEventSpecV1 for item in specs),
            "exact source specification tuple required",
        )
        self._profile = profile
        self._specs = specs
        self._next = 0
        self._visual = LocalChannelGridReceptor(VisualGridConfig())
        self._hearing = BroadbandHearingPath(LogSpectralReceptor(LogSpectralConfig()))

    @property
    def exhausted(self) -> bool:
        return self._next == len(self._specs)

    def _audio_state(self, recipe: str):
        window = auditory_fixtures.auditory_pcm(recipe)
        state = None
        for hop in range(10):
            state = self._hearing.push(window[hop * 480 : (hop + 1) * 480])
        _require(state is not None, "audio receptor endpoint is absent")
        return window, state

    def _field_input(
        self,
        perception_digest: str,
        ordinal: int,
        frames: tuple[OrganismTimedReceptorFrame, ...],
    ) -> lo_runner.S2LOFieldInputV1:
        start = (ordinal - 1) * 100_000_000
        end = ordinal * 100_000_000
        _require(
            frames
            and all(item.field_time.clock_id == lo_runner.FIELD_CLOCK_ID for item in frames)
            and all(item.field_time.window_end_tick == end for item in frames),
            "field time binding differs",
        )
        return lo_runner.S2LOFieldInputV1(perception_digest, start, end, frames)

    def _formation(
        self,
        spec: lo_runner.S2LOEventSpecV1,
    ) -> lo_runner.S2LOMaterializedEventV1:
        _require(spec.content_id in _CONTENT_RECIPES, "formation content differs")
        audio_recipe, visual_recipe = _CONTENT_RECIPES[spec.content_id]
        window, auditory_state = self._audio_state(audio_recipe)
        image = _visual_image(visual_recipe)
        visual_state = self._visual.analyze(image, frame_index=(spec.ordinal - 1) * 3 + 2)
        end = spec.ordinal * 100_000_000
        auditory = OrganismTimedReceptorFrame(
            from_auditory_receptor_state(auditory_state),
            CommonFieldTime(lo_runner.FIELD_CLOCK_ID, end - 10_000_000, end),
        )
        visual = OrganismTimedReceptorFrame(
            from_visual_receptor_state(visual_state),
            CommonFieldTime(
                lo_runner.FIELD_CLOCK_ID,
                (((spec.ordinal - 1) * 3 + 2) * 1_000_000_000) // 30,
                end,
            ),
        )
        audio_digest = hashlib.sha256(np.asarray(window, dtype="<f4").tobytes()).hexdigest()
        visual_digest = hashlib.sha256(image.tobytes(order="C")).hexdigest()
        plan = build_s2jv_pairing_plan(
            pair_id=f"s2lq-pair-{spec.ordinal:03d}",
            source_contract_id="s2lq-default-live-source",
            profile=self._profile,
            auditory=auditory,
            visual=visual,
            auditory_payload_digest=audio_digest,
            visual_payload_digest=visual_digest,
        )
        pair = bind_s2jv_default_live_pair(
            pairing_plan=plan,
            profile=self._profile,
            auditory=auditory,
            visual=visual,
        )
        source_payload = {
            "schema": S2LQ_SCHEMA,
            "event_spec_digest": spec.spec_digest,
            "source_id": f"s2lq-source-{spec.ordinal:03d}",
            "pairing_digest": pair.pairing_digest,
            "auditory_payload_digest": audio_digest,
            "visual_payload_digest": visual_digest,
            "auditory_values_digest": plan.auditory_values_digest,
            "visual_values_digest": plan.visual_values_digest,
        }
        source_digest = _digest(source_payload)
        return lo_runner.S2LOMaterializedEventV1(
            spec,
            source_digest,
            pair.pairing_digest,
            _digest({**source_payload, "source_digest": source_digest}),
            self._field_input(pair.pairing_digest, spec.ordinal, (auditory, visual)),
            pair,
        )

    def _auditory_cue(
        self,
        spec: lo_runner.S2LOEventSpecV1,
        config_digest: str,
        band_plan: auditory_scan.AuditoryBandPlan48V1,
    ) -> lo_runner.S2LOMaterializedEventV1:
        audio_recipe, _ = _CONTENT_RECIPES[spec.content_id]
        window, state = self._audio_state(audio_recipe)
        end = spec.ordinal * 100_000_000
        timed = OrganismTimedReceptorFrame(
            from_auditory_receptor_state(state),
            CommonFieldTime(lo_runner.FIELD_CLOCK_ID, end - 10_000_000, end),
        )
        values = tuple(state.energy)
        pcm_digest = hashlib.sha256(np.asarray(window, dtype="<f4").tobytes()).hexdigest()
        cue = auditory_scan.build_masked_auditory_cue_48(
            pcm_payload_digest=pcm_digest,
            receptor_state_digest=state.digest(),
            receptor_values_digest=visual_scan.digest(list(values)),
            config_digest=config_digest,
            auditory_source_clock_id=timed.frame.clock_id,
            auditory_window_start_tick=timed.frame.window_start_tick,
            auditory_window_end_tick=timed.frame.window_end_tick,
            observed_values=tuple(values[index] for index in auditory_scan.OBSERVED_BANDS),
            band_plan=band_plan,
        )
        source_payload = {
            "schema": S2LQ_SCHEMA,
            "event_spec_digest": spec.spec_digest,
            "source_id": f"s2lq-source-{spec.ordinal:03d}",
            "pcm_payload_digest": pcm_digest,
            "receptor_state_digest": state.digest(),
            "cue_digest": cue.cue_digest,
        }
        source_digest = _digest(source_payload)
        return lo_runner.S2LOMaterializedEventV1(
            spec,
            source_digest,
            cue.cue_digest,
            _digest({**source_payload, "source_digest": source_digest}),
            self._field_input(cue.cue_digest, spec.ordinal, (timed,)),
            stream.AuditoryCueOperationV1(cue, band_plan),
        )

    def _visual_cue(
        self,
        spec: lo_runner.S2LOEventSpecV1,
        config_digest: str,
    ) -> lo_runner.S2LOMaterializedEventV1:
        _, visual_recipe = _CONTENT_RECIPES[spec.content_id]
        image = visual_cues.occluded_visual_image(visual_recipe)
        state = self._visual.analyze(image, frame_index=(spec.ordinal - 1) * 3 + 2)
        native = from_visual_receptor_state(state)
        end = spec.ordinal * 100_000_000
        timed = OrganismTimedReceptorFrame(
            native,
            CommonFieldTime(
                lo_runner.FIELD_CLOCK_ID,
                (((spec.ordinal - 1) * 3 + 2) * 1_000_000_000) // 30,
                end,
            ),
        )
        values = tuple(state.channel_values)
        rgb_digest = hashlib.sha256(image.tobytes(order="C")).hexdigest()
        source_payload = {
            "schema": S2LQ_SCHEMA,
            "event_spec_digest": spec.spec_digest,
            "source_id": f"s2lq-source-{spec.ordinal:03d}",
            "rgb_payload_digest": rgb_digest,
            "receptor_state_digest": state.digest(),
            "receptor_values_digest": visual_scan.digest(list(values)),
        }
        source_digest = _digest(source_payload)
        cue = visual_scan.build_masked_memory_cue_336(
            source_digest=source_digest,
            config_digest=config_digest,
            field_clock_id=lo_runner.FIELD_CLOCK_ID,
            window_start_tick=timed.field_time.window_start_tick,
            window_end_tick=timed.field_time.window_end_tick,
            visual_source_clock_id=native.clock_id,
            visual_window_start_tick=native.window_start_tick,
            visual_window_end_tick=native.window_end_tick,
            values=tuple(
                values[index] if index in visual_scan.VISIBLE_POSITIONS else None
                for index in range(288)
            ),
        )
        return lo_runner.S2LOMaterializedEventV1(
            spec,
            source_digest,
            cue.cue_digest,
            _digest({**source_payload, "cue_digest": cue.cue_digest}),
            self._field_input(cue.cue_digest, spec.ordinal, (timed,)),
            cue,
        )

    def materialize_next(
        self,
        *,
        config_digest: str,
        band_plan: auditory_scan.AuditoryBandPlan48V1,
    ) -> lo_runner.S2LOMaterializedEventV1:
        _require(self._next < len(self._specs), "source stream is exhausted")
        spec = self._specs[self._next]
        if spec.event_type == "COMPLETE_AV_PERCEPTION":
            result = self._formation(spec)
        elif spec.event_type == "PARTIAL_AUDITORY_CUE":
            result = self._auditory_cue(spec, config_digest, band_plan)
        elif spec.event_type == "PARTIAL_VISUAL_CUE":
            result = self._visual_cue(spec, config_digest)
        else:
            raise S2LQError("event type differs")
        self._next += 1
        return result


def source_hashes(workspace_root: Path) -> dict[str, str]:
    _require(
        isinstance(workspace_root, Path) and workspace_root.is_absolute(),
        "absolute workspace Path required",
    )
    result = {}
    for relative in SOURCE_PATHS:
        path = workspace_root / relative
        _require(path.is_file(), f"bound source missing: {relative}")
        result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def _mean_l1(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    _require(len(left) == len(right) and left, "distance shape differs")
    return sum(abs(a - b) for a, b in zip(left, right, strict=True)) / len(left)


def _ppb_prototype(exposures: tuple[tuple[float, ...], ...]) -> tuple[float, ...]:
    _require(len(exposures) in {2, 3}, "PPB exposure chain differs")
    prototype = exposures[0]
    for current in exposures[1:]:
        prototype = tuple(
            (1.0 - 0.05) * previous + 0.05 * value
            for previous, value in zip(prototype, current, strict=True)
        )
    return prototype


def _source_geometry_preflight(
    config: memory.S2JVCoordinatorConfigV1,
) -> tuple[dict[str, object], tuple[lo_runner.S2LOMaterializedEventV1, ...]]:
    source = S2LQSourceStream(config.profile, MAIN_EVENT_SPECS)
    band_plan = auditory_scan.build_auditory_band_plan_48()
    materialized = [
        source.materialize_next(config_digest=config.config_digest, band_plan=band_plan)
        for _ in MAIN_EVENT_SPECS
    ]
    _require(source.exhausted, "source preflight did not finish")
    formation_values = []
    for item in materialized[:21]:
        pair = item.operation_payload
        _require(type(pair) is S2JVBoundAVPairV1, "formation source differs")
        formation_values.append(
            (
                tuple(pair.auditory.timed_frame.frame.values),
                tuple(pair.visual.timed_frame.frame.values),
            )
        )

    role_positions = {
        "p00": (0, 3, 5, 7),
        "p01": (1, 4, 6, 8),
        "p02": (2, 9, 10),
        "p03": (11,),
    }
    role_values = {key: formation_values[indexes[0]] for key, indexes in role_positions.items()}
    for indexes in role_positions.values():
        reference = formation_values[indexes[0]]
        _require(
            all(formation_values[index] == reference for index in indexes[1:]),
            "repeated receptor source differs",
        )
    for left_index, left in enumerate(("p00", "p01", "p02", "p03")):
        for right in ("p00", "p01", "p02", "p03")[left_index + 1 :]:
            _require(
                _mean_l1(role_values[left][0], role_values[right][0])
                > config.tspm_config.fast_config.auditory_match_threshold
                or _mean_l1(role_values[left][1], role_values[right][1])
                > config.tspm_config.fast_config.visual_match_threshold,
                "role Fast separation differs",
            )
    for left, right in (("p00", "p01"), ("p00", "p02"), ("p01", "p02")):
        auditory_distance = _mean_l1(role_values[left][0], role_values[right][0])
        visual_distance = _mean_l1(role_values[left][1], role_values[right][1])
        _require(
            auditory_distance > config.tspm_config.profile.auditory_config.match_threshold
            and visual_distance > config.tspm_config.profile.visual_config.match_threshold,
            "Slow source separation differs",
        )
    for pressure_index in range(12, 21):
        pressure = formation_values[pressure_index]
        for other_index in (*range(12), *range(12, pressure_index)):
            other = formation_values[other_index]
            separated = (
                _mean_l1(pressure[0], other[0])
                > config.tspm_config.fast_config.auditory_match_threshold
                or _mean_l1(pressure[1], other[1])
                > config.tspm_config.fast_config.visual_match_threshold
            )
            _require(separated, "Fast pressure separation differs")

    prototypes = {
        "p00": (
            _ppb_prototype(tuple(formation_values[index][0] for index in role_positions["p00"][1:])),
            _ppb_prototype(tuple(formation_values[index][1] for index in role_positions["p00"][1:])),
        ),
        "p01": (
            _ppb_prototype(tuple(formation_values[index][0] for index in role_positions["p01"][1:])),
            _ppb_prototype(tuple(formation_values[index][1] for index in role_positions["p01"][1:])),
        ),
        "p02": (
            _ppb_prototype(tuple(formation_values[index][0] for index in role_positions["p02"][1:])),
            _ppb_prototype(tuple(formation_values[index][1] for index in role_positions["p02"][1:])),
        ),
    }
    expected_matches = {
        21: ("p00",),
        22: ("p00",),
        23: ("p01",),
        24: ("p01",),
        25: (),
        26: (),
        27: ("p00",),
        28: (),
    }
    expected_pressure_match = {
        21: False,
        22: False,
        23: False,
        24: False,
        25: True,
        26: False,
        27: False,
        28: False,
    }
    measured_matches = {}
    for index, item in enumerate(materialized[21:], start=21):
        if item.spec.event_type == "PARTIAL_AUDITORY_CUE":
            operation = item.operation_payload
            _require(type(operation) is stream.AuditoryCueOperationV1, "auditory cue differs")
            cue = auditory_scan._validate_cue(operation.cue, band_plan)
            observed = tuple(float(cue.values[index]) for index in auditory_scan.OBSERVED_BANDS)
            _require(
                cue.observed_values_digest == auditory_scan.digest(list(observed)),
                "auditory observed values digest differs",
            )
            matches = tuple(
                key
                for key in ("p00", "p01")
                if _mean_l1(
                    tuple(prototypes[key][0][band] for band in auditory_scan.OBSERVED_BANDS),
                    observed,
                )
                <= config.tspm_config.profile.auditory_config.match_threshold
            )
            pressure_match = (
                _mean_l1(
                    tuple(formation_values[12][0][band] for band in auditory_scan.OBSERVED_BANDS),
                    observed,
                )
                <= config.tspm_config.fast_config.auditory_match_threshold
            )
        else:
            cue = item.operation_payload
            _require(type(cue) is visual_scan.MaskedMemoryCue336V1, "visual cue differs")
            matches = tuple(
                key
                for key in ("p00", "p01")
                if all(
                    prototypes[key][1][position] == cue.values[position]
                    for position in visual_scan.VISIBLE_POSITIONS
                )
            )
            pressure_match = any(
                all(
                    formation_values[pressure_index][1][position] == cue.values[position]
                    for position in visual_scan.VISIBLE_POSITIONS
                )
                for pressure_index in range(12, 21)
            )
        _require(matches == expected_matches[index], "partial-cue source geometry differs")
        _require(
            pressure_match is expected_pressure_match[index],
            "partial cue to pressure relation differs",
        )
        measured_matches[item.spec.event_code] = {
            "stable_content_matches": list(matches),
            "pressure_match": pressure_match,
        }

    payload = {
        "schema": S2LQ_SCHEMA,
        "source_count": len(materialized),
        "formation_count": len(formation_values),
        "cue_count": len(materialized) - len(formation_values),
        "source_receipt_digests": [item.source_receipt_digest for item in materialized],
        "prototype_digests": {
            key: [_digest(list(value[0])), _digest(list(value[1]))]
            for key, value in prototypes.items()
        },
        "measured_matches": measured_matches,
        "memory_calls": 0,
    }
    return (
        {**payload, "preflight_digest": _digest(payload)},
        tuple(materialized),
    )


def _slot_map(observation: dict[str, object], bank: str) -> dict[str, dict[str, object]]:
    slots = observation.get(bank)
    _require(type(slots) is list, "Slow inventory differs")
    result = {}
    for value in slots:
        _require(type(value) is dict and type(value.get("slot_id")) is str, "Slow slot differs")
        _require(value["slot_id"] not in result, "duplicate Slow slot")
        result[value["slot_id"]] = value
    return result


def _transition_chain(
    events: list[dict[str, object]],
    modality: str,
    event_indexes: tuple[int, ...],
) -> dict[str, object]:
    bank = f"{modality}_slow"
    slot_id = None
    prior = None
    event_codes = []
    supports = []
    prototype_digests = []
    for support, event_index in enumerate(event_indexes, start=1):
        event = events[event_index]
        observation = event["memory_observation"]
        _require(type(observation) is dict, "transition observation differs")
        source_values = tuple(observation["formation_values"][modality])
        slots = _slot_map(observation, bank)
        expected = source_values if prior is None else tuple(
            (1.0 - 0.05) * previous + 0.05 * current
            for previous, current in zip(prior, source_values, strict=True)
        )
        candidates = [
            value
            for value in slots.values()
            if value.get("support_count") == support
            and tuple(value.get("prototype_values", ())) == expected
            and value.get("prototype_digest") == _digest(list(expected))
        ]
        if slot_id is None:
            _require(len(candidates) == 1, "initial PPB transition is ambiguous")
            slot_id = candidates[0]["slot_id"]
        else:
            _require(slot_id in slots and slots[slot_id] in candidates, "PPB slot continuity differs")
        prior = expected
        event_codes.append(event["event_code"])
        supports.append(support)
        prototype_digests.append(_digest(list(expected)))
    return {
        "slot_id": slot_id,
        "event_codes": event_codes,
        "support_chain": supports,
        "prototype_digests": prototype_digests,
        "transition_integrity": True,
    }


def validate_multislot_summary(value: object) -> None:
    _require(type(value) is dict, "multislot summary differs")
    for modality in ("auditory", "visual"):
        bank = value.get(modality)
        _require(type(bank) is dict, "modality inventory differs")
        _require(
            bank.get("occupied_slot_count") == 3
            and bank.get("stable_slot_count") == 2
            and bank.get("support_by_content") == {"p00": 3, "p01": 3, "p02": 2},
            "multislot support inventory differs",
        )
        chains = bank.get("transition_chains")
        _require(type(chains) is dict and set(chains) == {"p00", "p01", "p02"}, "transition inventory differs")
        for content, supports in (("p00", [1, 2, 3]), ("p01", [1, 2, 3]), ("p02", [1, 2])):
            chain = chains[content]
            _require(
                type(chain) is dict
                and chain.get("support_chain") == supports
                and chain.get("transition_integrity") is True
                and type(chain.get("slot_id")) is str
                and len(chain.get("prototype_digests", ())) == len(supports)
                and all(_DIGEST.fullmatch(item) for item in chain["prototype_digests"]),
                "PPB transition chain differs",
            )


def _inventory_summary(events: list[dict[str, object]]) -> dict[str, object]:
    indexes = {"p00": (3, 5, 7), "p01": (4, 6, 8), "p02": (9, 10)}
    final = events[20]["memory_observation"]
    _require(type(final) is dict, "final memory observation differs")
    result = {}
    for modality in ("auditory", "visual"):
        chains = {
            content: _transition_chain(events, modality, event_indexes)
            for content, event_indexes in indexes.items()
        }
        slots = _slot_map(final, f"{modality}_slow")
        support_by_content = {
            content: slots[chain["slot_id"]]["support_count"]
            for content, chain in chains.items()
        }
        result[modality] = {
            "occupied_slot_count": len(slots),
            "stable_slot_count": sum(value["support_count"] >= 3 for value in slots.values()),
            "support_by_content": support_by_content,
            "transition_chains": chains,
            "final_slot_digests": {
                content: slots[chain["slot_id"]]["prototype_digest"]
                for content, chain in chains.items()
            },
        }
    validate_multislot_summary(result)
    return result


def _scan_equivalent(primary: dict[str, object], baseline: dict[str, object]) -> bool:
    if primary.get("decision") != baseline.get("decision"):
        return False
    left = primary.get("hypothesis")
    right = baseline.get("hypothesis")
    if left is None or right is None:
        return left is right
    return (
        type(left) is dict
        and type(right) is dict
        and left.get("area") == right.get("area")
        and left.get("masked_positions", left.get("masked_bands"))
        == right.get("masked_positions", right.get("masked_bands"))
        and left.get("proposed_values") == right.get("proposed_values")
    )


def classify_interference(
    *,
    decision: str,
    hypothesis_digest: str | None,
    expected_content_digest: str,
    own_content_stored: bool,
) -> str:
    _require(_DIGEST.fullmatch(expected_content_digest) is not None, "expected content digest differs")
    _require(not own_content_stored, "interference source was stored")
    _require(
        decision == "ADMIT_SINGLE_CONTEXT" and hypothesis_digest == expected_content_digest,
        "interference relation differs",
    )
    return "SENSOR_CONFUSION_WITH_EXISTING_STABLE_CONTENT"


def _evaluate_main(execution: dict[str, object]) -> dict[str, object]:
    events = execution.get("events")
    _require(type(events) is list and len(events) == MAIN_EVENT_COUNT, "event evidence differs")
    inventory = _inventory_summary(events)
    final = events[20]["memory_observation"]
    _require(type(final) is dict, "final memory observation differs")
    b4_indexes = [item["formation_index"] for item in final["b4"]]
    role_sources = {
        content: events[index]["memory_observation"]["formation_values"]
        for content, index in {"p00": 0, "p01": 1, "p02": 2, "p03": 11}.items()
    }
    absent_from_a = {}
    for content, source in role_sources.items():
        absent_from_a[content] = all(
            item["values_digest"] != source["av_digest"] for item in final["b4"]
        ) and all(
            item["auditory_values_digest"] != source["auditory_digest"]
            or item["visual_values_digest"] != source["visual_digest"]
            for item in final["fast"]
        )

    expected_decisions = (
        "ADMIT_SINGLE_CONTEXT", "ADMIT_SINGLE_CONTEXT",
        "ADMIT_SINGLE_CONTEXT", "ADMIT_SINGLE_CONTEXT",
        "ABSTAIN_INTERNAL_AMBIGUITY", "ABSTAIN_NO_APPLICABLE_CONTEXT",
        "ADMIT_SINGLE_CONTEXT", "ABSTAIN_NO_APPLICABLE_CONTEXT",
    )
    scan_results = []
    all_read_only = True
    all_equal = True
    for event, expected in zip(events[21:], expected_decisions, strict=True):
        primary = event["primary_scan"]
        baseline = event["baseline_scan"]
        _require(type(primary) is dict and type(baseline) is dict, "scan evidence differs")
        all_read_only = all_read_only and all(
            value == execution["counters"]["final_memory_digest"]
            for value in (
                primary["prestate_digest"], primary["poststate_digest"],
                baseline["prestate_digest"], baseline["poststate_digest"],
            )
        )
        equivalent = _scan_equivalent(primary, baseline)
        all_equal = all_equal and equivalent
        scan_results.append(
            {
                "event_code": event["event_code"],
                "decision": primary["decision"],
                "expected_decision": expected,
                "baseline_equal": equivalent,
                "hypothesis_digest": primary.get("hypothesis_digest"),
            }
        )

    a_auditory_slot = inventory["auditory"]["transition_chains"]["p00"]["slot_id"]
    final_auditory = _slot_map(final, "auditory_slow")[a_auditory_slot]
    expected_interference_digest = _digest(
        [final_auditory["prototype_values"][index] for index in auditory_scan.MASKED_BANDS]
    )
    interference_hypothesis = events[27]["primary_scan"].get("hypothesis")
    _require(type(interference_hypothesis) is dict, "interference hypothesis differs")
    interference_digest = _digest(interference_hypothesis["proposed_values"])
    interference = classify_interference(
        decision=events[27]["primary_scan"]["decision"],
        hypothesis_digest=interference_digest,
        expected_content_digest=expected_interference_digest,
        own_content_stored=not absent_from_a["p03"],
    )
    confirmed = (
        b4_indexes == list(range(13, 22))
        and all(absent_from_a.values())
        and all(item["decision"] == item["expected_decision"] for item in scan_results)
        and all_read_only
        and all_equal
        and interference == "SENSOR_CONFUSION_WITH_EXISTING_STABLE_CONTENT"
        and execution["counters"]["event_count"] == MAIN_EVENT_COUNT
        and execution["counters"]["memory_formation_attempt_count"] == MAIN_FORMATION_COUNT
        and execution["counters"]["scan_attempt_count"] == 16
    )
    payload = {
        "status": "S2LQ_MULTIPATTERN_STREAM_CONFIRMED" if confirmed else "S2LQ_MULTIPATTERN_STREAM_FALSIFIED",
        "multislot_inventory": inventory,
        "b4_formation_indexes": b4_indexes,
        "content_absent_from_a_recent": absent_from_a,
        "scan_results": scan_results,
        "interference_classification": interference,
        "memory_read_only_during_cues": all_read_only,
        "primary_baseline_equal": all_equal,
    }
    return {**payload, "evaluation_digest": _digest(payload)}


def _run_stream(
    config: memory.S2JVCoordinatorConfigV1,
    materialized_events: tuple[lo_runner.S2LOMaterializedEventV1, ...],
) -> tuple[dict[str, object], stream.PerceptionStreamStateV1]:
    _require(
        type(config) is memory.S2JVCoordinatorConfigV1
        and type(materialized_events) is tuple
        and len(materialized_events) == MAIN_EVENT_COUNT,
        "materialized stream binding differs",
    )
    first = materialized_events[0]
    initial_field = lo_runner.initial_s2lo_field_state(first.field_input)
    stored = memory.initial_s2jv_composite_state(config)
    state = stream.initial_perception_stream_state(
        stream_id="s2lq-perception-stream",
        field_state=initial_field,
        field_state_digest=initial_field.state_digest,
        memory_state=stored,
        memory_state_digest=stored.state_digest,
    )
    initial_field_observation = lo_runner._field_observation(initial_field)
    processor = lo_runner._processor(config)
    records = []
    for materialized, spec in zip(materialized_events, MAIN_EVENT_SPECS, strict=True):
        _require(materialized.spec == spec, "materialized event order differs")
        event = lo_runner.build_stream_event(materialized)
        owner = stream.PerceptionEventOwner(
            f"s2lq-event-owner-{spec.ordinal:03d}",
            state.state_digest,
            event.event_digest,
        )
        result = processor.process_once(state=state, event=event, owner=owner)
        records.append(lo_runner._event_record(materialized, event, result))
        state = result.poststate
        _require(not result.error_codes, "one stream branch failed")
    counters = {
        "event_count": state.processed_event_count,
        "field_attempt_count": state.field_attempt_count,
        "memory_formation_attempt_count": state.memory_formation_attempt_count,
        "scan_attempt_count": state.scan_attempt_count,
        "final_field_digest": state.field_state_digest,
        "final_memory_digest": state.memory_state_digest,
        "stream_status": state.status,
    }
    return {
        "initial_field_observation": initial_field_observation,
        "events": records,
        "counters": counters,
    }, state


def _neutral_multislot_summary() -> dict[str, object]:
    result = {}
    for modality in ("auditory", "visual"):
        chains = {}
        for content, supports in (("p00", [1, 2, 3]), ("p01", [1, 2, 3]), ("p02", [1, 2])):
            chains[content] = {
                "slot_id": f"neutral-{modality}-{content}",
                "event_codes": [f"n{index:02d}" for index in supports],
                "support_chain": supports,
                "prototype_digests": [_digest([modality, content, support]) for support in supports],
                "transition_integrity": True,
            }
        result[modality] = {
            "occupied_slot_count": 3,
            "stable_slot_count": 2,
            "support_by_content": {"p00": 3, "p01": 3, "p02": 2},
            "transition_chains": chains,
            "final_slot_digests": {
                content: chain["prototype_digests"][-1] for content, chain in chains.items()
            },
        }
    validate_multislot_summary(result)
    return result


def neutral_qualification_record(workspace_root: Path) -> dict[str, object]:
    config = lo_runner._build_config()
    source = S2LQSourceStream(config.profile, QUALIFICATION_SOURCE_SPECS)
    band_plan = auditory_scan.build_auditory_band_plan_48()
    bindings = []
    for _ in QUALIFICATION_SOURCE_SPECS:
        value = source.materialize_next(config_digest=config.config_digest, band_plan=band_plan)
        pair = value.operation_payload
        _require(type(pair) is S2JVBoundAVPairV1, "qualification source differs")
        binding_payload = {
            "event_spec_digest": value.spec.spec_digest,
            "source_digest": value.source_digest,
            "source_receipt_digest": value.source_receipt_digest,
            "pairing_digest": pair.pairing_digest,
            "auditory_dimension": len(pair.auditory.timed_frame.frame.values),
            "visual_dimension": len(pair.visual.timed_frame.frame.values),
        }
        bindings.append({**binding_payload, "binding_digest": _digest(binding_payload)})
    _require(source.exhausted, "qualification source did not finish")
    multislot = _neutral_multislot_summary()
    memory_digest = _digest(["neutral", "memory", "unchanged"])
    expected = _digest(["neutral", "stable", "masked"])
    interference = classify_interference(
        decision="ADMIT_SINGLE_CONTEXT",
        hypothesis_digest=expected,
        expected_content_digest=expected,
        own_content_stored=False,
    )
    payload = {
        "schema": S2LQ_RESULT_SCHEMA,
        "mode": "QUALIFICATION",
        "technical_status": "RECORDING_COMPLETE",
        "source_hashes": source_hashes(workspace_root),
        "plan": {
            "qualification_id": QUALIFICATION_ID,
            "main_execution_enabled": MAIN_EXECUTION_ENABLED,
            "authorized_run_id": AUTHORIZED_RUN_ID,
            "main_story_executed": False,
            "main_event_count": MAIN_EVENT_COUNT,
            "main_formation_count": MAIN_FORMATION_COUNT,
            "main_cue_count": MAIN_AUDITORY_CUE_COUNT + MAIN_VISUAL_CUE_COUNT,
            "raw_payload_retained": False,
        },
        "source_bindings": bindings,
        "qualification_counters": {
            "source_binding_count": len(bindings),
            "field_calls": 0,
            "memory_calls": 0,
            "scan_calls": 0,
            "main_events_processed": 0,
        },
        "multislot_inventory": multislot,
        "read_only_evidence": {
            "prestate_digest": memory_digest,
            "poststate_digest": memory_digest,
        },
        "interference_classification": interference,
        "evaluation": None,
    }
    return {**payload, "record_digest": _digest(payload)}


def _main_record(workspace_root: Path, run_id: str) -> dict[str, object]:
    config = lo_runner._build_config()
    preflight, materialized_events = _source_geometry_preflight(config)
    execution, state = _run_stream(config, materialized_events)
    _require(state.status == "OPEN", "stream did not remain open")
    evaluation = _evaluate_main(execution)
    payload = {
        "schema": S2LQ_RESULT_SCHEMA,
        "mode": "MAIN",
        "run_id": run_id,
        "technical_status": "RECORDING_COMPLETE",
        "source_hashes": source_hashes(workspace_root),
        "plan": {
            "event_spec_digests": [item.spec_digest for item in MAIN_EVENT_SPECS],
            "event_count": MAIN_EVENT_COUNT,
            "formation_count": MAIN_FORMATION_COUNT,
            "auditory_cue_count": MAIN_AUDITORY_CUE_COUNT,
            "visual_cue_count": MAIN_VISUAL_CUE_COUNT,
            "field_contacts": MAIN_FIELD_CONTACTS,
            "memory_l1_terms": MAIN_MEMORY_L1_TERMS,
            "scan_comparisons_max": MAIN_SCAN_COMPARISONS,
            "raw_bytes_max": MAIN_RAW_BYTES,
            "raw_payload_retained": False,
        },
        "source_geometry_preflight": preflight,
        "execution": execution,
        "evaluation": evaluation,
    }
    return {**payload, "record_digest": _digest(payload)}


def run_main_once(*, workspace_root: Path, output_root: Path, run_id: str) -> Path:
    global MAIN_EXECUTION_ENABLED, _MAIN_USED
    _require(MAIN_EXECUTION_ENABLED is True, "main execution gate is closed")
    _require(run_id == AUTHORIZED_RUN_ID, "run id is not authorized")
    _require(_RUN_ID.fullmatch(run_id) is not None, "run id differs")
    _require(not _MAIN_USED and _MAIN_LOCK.acquire(blocking=False), "main execution is consumed")
    _MAIN_USED = True
    try:
        record = _main_record(workspace_root, run_id)
        data = _canonical_bytes(record, newline=True)
        _require(len(data) <= MAX_RESULT_BYTES, "result exceeds bounded size")
        return lo_runner.write_result_once(output_root, run_id, record)
    finally:
        MAIN_EXECUTION_ENABLED = False
        _MAIN_LOCK.release()


assert len(MAIN_EVENT_SPECS) == MAIN_EVENT_COUNT
assert sum(item.event_type == "COMPLETE_AV_PERCEPTION" for item in MAIN_EVENT_SPECS) == 21
assert sum(item.event_type == "PARTIAL_AUDITORY_CUE" for item in MAIN_EVENT_SPECS) == 4
assert sum(item.event_type == "PARTIAL_VISUAL_CUE" for item in MAIN_EVENT_SPECS) == 4
assert len(_CONTENT_RECIPES) == 13
assert MAIN_FIELD_CONTACTS == 21 * 336 + 4 * 48 + 4 * 288
assert MAIN_MEMORY_L1_TERMS == 21 * 3_552
assert MAIN_SCAN_COMPARISONS == 8 * 528 + 8 * 800

__all__: tuple[str, ...] = ()
