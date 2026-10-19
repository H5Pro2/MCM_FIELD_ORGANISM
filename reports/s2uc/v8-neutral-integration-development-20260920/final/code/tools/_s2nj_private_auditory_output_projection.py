"""Private, single-stage output scale. No receptor/default adapter modification."""

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
import re
import sys

from mcm_field_organism.broadband_hearing_path import AuditoryReceptorContact, AuditoryReceptorState
from mcm_field_organism import log_spectral_receptor as spectral


RAW_GEOMETRY = "auditory.log48.50-18000.w4800.h480.v1"
GEOMETRY = "auditory.log48.50-18000.w4800.h480.half.v1"
PROFILE_ID = "s2nj.auditory.hann48.output-half.v1"
RECEPTOR_SHA256 = "26a6bd8f2d190db60c75ad29f275b3bd8b09b6d26d4ad54e4396176c4a36d2b0"
MAX_OUTPUT_BYTES = 16384
_HEX = re.compile(r"[0-9a-f]{64}")


class S2NJProjectionError(ValueError):
    pass


def _require(ok, code):
    if not ok:
        raise S2NJProjectionError(code)


def canonical(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                          allow_nan=False).encode("ascii")
    except (TypeError, ValueError, OverflowError) as exc:
        raise S2NJProjectionError("CANONICAL_FORM_INVALID") from exc


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def raw_profile_payload():
    return dict(schema="s2nj.bound-unscaled-auditory-profile.v1", geometry_id=RAW_GEOMETRY,
                config=dict(sample_rate=48000, window_size=4800, hop_size=480, min_frequency=50.0,
                            max_frequency=18000.0, band_count=48),
                window="numpy.hanning.symmetric", fft="numpy.fft.rfft.norm-none",
                reduction="sqrt-sum-square-weighted-amplitude", receptor_sha256=RECEPTOR_SHA256)


RAW_PROFILE_DIGEST = digest(raw_profile_payload())


def profile_payload():
    return dict(profile_id=PROFILE_ID, geometry_id=GEOMETRY, raw_profile_digest=RAW_PROFILE_DIGEST,
                factor_hex="0x1.0000000000000p-1", operation="binary64-multiply-once-after-raw-reduction",
                output_domain="finite-0-through-1-inclusive", rounding="qualified-binary64-nearest-even",
                subnormal_policy="preserve-native-rounded-result-report-underflow-no-flush-or-clamp",
                max_output_bytes=MAX_OUTPUT_BYTES)


PROFILE_DIGEST = digest(profile_payload())


def _time(snapshot, start, end):
    _require(all(type(v) is int for v in (snapshot, start, end)) and snapshot >= 0
             and start == snapshot*480 and end == start+4800, "SOURCE_TIME_INVALID")


def _carriers(carriers):
    expected = tuple(b.channel_id for b in spectral.logarithmic_bands(spectral.LogSpectralConfig()))
    _require(type(carriers) is tuple and carriers == expected, "CARRIER_BINDING_INVALID")


@dataclass(frozen=True, slots=True)
class HalfScaleAuditory48V1:
    profile_id: str
    profile_digest: str
    geometry_id: str
    source_profile_digest: str
    source_state_digest: str
    source_values_digest: str
    snapshot_index: int
    clock_id: str
    window_start_tick: int
    window_end_tick: int
    carrier_ids: tuple[str, ...]
    values: tuple[float, ...]
    subnormal_band_indices: tuple[int, ...]
    underflow_band_indices: tuple[int, ...]
    projection_digest: str

    def payload(self):
        result = asdict(self)
        del result["projection_digest"]
        return result

    def __post_init__(self):
        validate_projection(self)


def validate_projection(value):
    _require(type(value) is HalfScaleAuditory48V1, "OUTPUT_TYPE_INVALID")
    _require((value.profile_id, value.profile_digest, value.geometry_id, value.source_profile_digest) ==
             (PROFILE_ID, PROFILE_DIGEST, GEOMETRY, RAW_PROFILE_DIGEST), "OUTPUT_PROFILE_INVALID")
    _require(value.clock_id == "audio.sample", "OUTPUT_CLOCK_INVALID")
    _time(value.snapshot_index, value.window_start_tick, value.window_end_tick)
    _carriers(value.carrier_ids)
    for h in (value.source_state_digest, value.source_values_digest, value.projection_digest):
        _require(type(h) is str and _HEX.fullmatch(h) is not None, "DIGEST_FORM_INVALID")
    _require(type(value.values) is tuple and len(value.values) == 48 and
             all(type(v) is float and math.isfinite(v) and 0.0 <= v <= 1.0 for v in value.values),
             "OUTPUT_NORMALFORM_INVALID")
    for indices in (value.subnormal_band_indices, value.underflow_band_indices):
        _require(type(indices) is tuple and all(type(i) is int and 0 <= i < 48 for i in indices)
                 and tuple(sorted(set(indices))) == indices, "NUMERIC_FLAGS_INVALID")
    _require(value.subnormal_band_indices == tuple(i for i, v in enumerate(value.values)
             if 0 < v < sys.float_info.min) and all(value.values[i] == 0.0 for i in value.underflow_band_indices),
             "NUMERIC_FLAGS_INVALID")
    _require(value.projection_digest == digest(value.payload()), "PROJECTION_DIGEST_INVALID")
    _require(len(canonical(asdict(value))) <= MAX_OUTPUT_BYTES, "OUTPUT_SIZE_LIMIT")


def project_auditory_half_v1(state, *, config, source_profile_digest):
    """Return a new scale-specific value only after all 48 components validate."""
    _require(type(state) is AuditoryReceptorState, "RAW_STATE_REQUIRED")
    _require(type(config) is spectral.LogSpectralConfig and
             asdict(config) == raw_profile_payload()["config"] and source_profile_digest == RAW_PROFILE_DIGEST,
             "RAW_PROFILE_INVALID")
    _require(all(type(getattr(config, k)) is type(v) for k, v in raw_profile_payload()["config"].items()),
             "RAW_PROFILE_TYPE_INVALID")
    with Path(spectral.__file__).open("rb") as handle:
        _require(hashlib.file_digest(handle, "sha256").hexdigest() == RECEPTOR_SHA256, "RECEPTOR_CODE_CHANGED")
    _require(sys.float_info.radix == 2 and sys.float_info.mant_dig == 53 and sys.float_info.rounds == 1,
             "BINARY64_ENVIRONMENT_INVALID")
    _require(state.modality_id == "auditory" and state.geometry_id == RAW_GEOMETRY, "RAW_GEOMETRY_INVALID")
    _time(state.snapshot_index, state.window_start_sample, state.window_end_sample)
    _carriers(state.carrier_ids)
    _require(type(state.energy) is tuple and len(state.energy) == 48 and
             all(type(v) is float and math.isfinite(v) and v >= 0.0 for v in state.energy), "RAW_VALUES_INVALID")
    activity = AuditoryReceptorContact.ACTIVE_ENERGY if any(v != 0 for v in state.energy) else AuditoryReceptorContact.ACTIVE_ZERO
    _require(type(state.contact) is AuditoryReceptorContact and state.contact is activity, "RAW_ACTIVITY_INVALID")
    source_digest = state.digest()
    # Only this statement scales values; validation never rescales the output.
    values = tuple(v * 0.5 for v in state.energy)
    _require(all(math.isfinite(v) and 0.0 <= v <= 1.0 for v in values), "OUTPUT_NORMALFORM_INVALID")
    payload = dict(profile_id=PROFILE_ID, profile_digest=PROFILE_DIGEST, geometry_id=GEOMETRY,
                   source_profile_digest=RAW_PROFILE_DIGEST, source_state_digest=source_digest,
                   source_values_digest=digest(list(state.energy)), snapshot_index=state.snapshot_index,
                   clock_id="audio.sample", window_start_tick=state.window_start_sample,
                   window_end_tick=state.window_end_sample, carrier_ids=state.carrier_ids, values=values,
                   subnormal_band_indices=tuple(i for i, v in enumerate(values) if 0 < v < sys.float_info.min),
                   underflow_band_indices=tuple(i for i, (raw, v) in enumerate(zip(state.energy, values, strict=True))
                                                if raw > 0 and v == 0.0))
    _require(state.digest() == source_digest, "SOURCE_MUTATED")
    return HalfScaleAuditory48V1(**payload, projection_digest=digest(payload))
