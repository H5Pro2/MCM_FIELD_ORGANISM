"""Closed historical-input class for the immediate visual control only."""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

VERSION = "s2oe.immediate-historical-input.v1"
MAIN_GATE = False
ROOT = Path(__file__).resolve().parents[1]
PARENT = "reports/s2oe/media-memory-video-20260912-01/record.json"
HISTORICAL_LIMIT = 2097152
LIMITS = dict(metadata=65536, sources=174080, shared=262144,
              verification=262144, total=4194304)


class InputError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def need(ok, code):
    if not ok:
        raise InputError(code)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class ParentBinding:
    path: str
    byte_count: int
    sha256: str
    event_digest: str
    config_digest: str
    neutral: bool = False
    version: str = VERSION

    def validate(self):
        need(self.version == VERSION and type(self.neutral) is bool, "BINDING_VERSION_INVALID")
        need(type(self.byte_count) is int and 0 < self.byte_count <= HISTORICAL_LIMIT,
             "HISTORICAL_INPUT_LIMIT")
        for value in (self.sha256, self.event_digest, self.config_digest):
            need(type(value) is str and len(value) == 64
                 and all(c in "0123456789abcdef" for c in value), "DIGEST_FORM_INVALID")
        if not self.neutral:
            need(self.path == PARENT, "HISTORICAL_CLASS_SCOPE_INVALID")
        else:
            need(Path(self.path).name == "neutral-parent.json"
                 and Path(self.path).is_absolute(), "NEUTRAL_PARENT_INVALID")


def extract(raw, binding):
    """The entire parent is checked before any event is selected."""
    binding.validate()
    need(type(raw) is bytes and len(raw) == binding.byte_count
         and sha(raw) == binding.sha256, "PARENT_CONTENT_INVALID")
    try:
        parent = json.loads(raw)
        execution = parent["record"]["execution"]
        inputs = execution["inputs"]
        need(type(inputs) is list and len(inputs) >= 3, "EVENT_BINDING_INVALID")
        item = inputs[2]
        event = item["event"]
        need(event["event_id"] == "media-event-03" and event["ordinal"] == 3
             and event["event_type"] == "COMPLETE_AV_PERCEPTION"
             and event["event_digest"] == binding.event_digest, "EVENT_BINDING_INVALID")
        need(execution["config_digest"] == binding.config_digest, "PROFILE_BINDING_INVALID")
        receipt = execution["source_receipts"][2]
        frames = item["field"]["timed_frames"]
        need(len(frames) == 2, "VALUES_BINDING_INVALID")
        by = {f["frame"]["modality_id"]: f["frame"] for f in frames}
        need(set(by) == {"auditory", "visual"}
             and len(by["auditory"]["values"]) == 48
             and len(by["visual"]["values"]) == 288, "VALUES_BINDING_INVALID")
        need(receipt["source_digest"] == event["source_digest"]
             and receipt["nj"]["pcm_digest"] == item["operation"]["auditory_payload_digest"]
             and receipt["rgb_digest"] == item["operation"]["visual_payload_digest"],
             "SOURCE_BINDING_INVALID")
        return canonical(dict(version=VERSION, parent_sha256=binding.sha256,
            parent_bytes=binding.byte_count, index=2, input=item, source_receipt=receipt,
            config_digest=binding.config_digest))
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise InputError("PARENT_FORM_INVALID") from exc


def read_extract(binding, reads):
    binding.validate()
    path = Path(binding.path) if binding.neutral else ROOT / binding.path
    need(type(reads) is dict and set(reads) == {"bytes", "operations"}, "READ_LEDGER_INVALID")
    try:
        with path.open("rb") as handle:
            raw = handle.read(HISTORICAL_LIMIT + 1)
    except FileNotFoundError as exc:
        raise InputError("PARENT_MISSING") from exc
    reads["bytes"] += len(raw)
    reads["operations"] += 1
    return extract(raw, binding)


def verify_extract(excerpt, raw, binding):
    need(type(excerpt) is bytes and excerpt == extract(raw, binding), "EXTRACTION_RELATION_INVALID")
    return True


def balance(binding, *, metadata, sources, verification, supplement, data):
    """One physical parent; all other classes remain unmodified."""
    binding.validate()
    parts = dict(metadata=metadata, sources=sources, verification=verification,
                 supplement=supplement, data=data, historical_input=binding.byte_count)
    need(all(type(v) is int and v >= 0 for v in parts.values()), "BYTE_COUNT_INVALID")
    totals = dict(metadata=metadata, sources=sources, verification=verification,
                  shared=sources+supplement, total=sum(parts.values()))
    violations = [key for key, value in totals.items() if value > LIMITS[key]]
    return dict(version=VERSION, parts=parts, totals=totals, limits=LIMITS,
                historical_limit=HISTORICAL_LIMIT, violations=violations)


def enforce_balance(measured):
    if measured["violations"]:
        error = InputError("BUDGET_EXCEEDED")
        error.balance = measured
        raise error
