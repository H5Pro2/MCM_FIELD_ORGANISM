"""Fixed two-pass media selection, with media time distinct from OC time."""
from dataclasses import asdict, dataclass
from fractions import Fraction
import re

from tools import _s2oc_shared_binding as shared

b = shared.b
VERSION = "s2oe.sampled-media.v2-private-budget"
TIME_VERSION = "local-media.sampled-runtime-time.v1"
MAIN_GATE = False
SESSION_LIMITS = dict(b.LIMITS, sources=180224)
QUAL_LIMITS = dict(SESSION_LIMITS, metadata=98304)


def ledger(*args, **kwargs):
    value = shared.ledger(*args, **kwargs)
    value["violations"] = [k.upper()+"_LIMIT" for k,n in value["totals"].items() if n>SESSION_LIMITS[k]]
    return value


def enforce(rows, phase, ordinal, completed):
    if any(x["violations"] for x in rows.values()):
        data = shared.budget.diagnostic(rows, phase, ordinal, completed)
        for x in data["alternatives"].values():
            x["limits"] = SESSION_LIMITS
        raise shared.budget.BudgetError("MEDIA_ENVELOPE_LIMIT", data)


class MediaError(ValueError):
    def __init__(self, code, detail=None):
        self.code, self.balance = code, detail
        super().__init__(code)


def need(ok, code):
    if not ok:
        raise MediaError(code)


@dataclass(frozen=True)
class Source:
    path: str
    sha256: str
    size: int
    video_stream: int = 0
    audio_stream: int = 1
    video_time_base: tuple = (1, 30000)
    audio_time_base: tuple = (1, 48000)
    frame_rate: tuple = (30000, 1001)
    video_size: tuple = (3840, 2160)


@dataclass(frozen=True)
class Selection:
    event_id: str
    ordinal: int
    kind: str
    pass_number: int
    window_number: int


@dataclass(frozen=True)
class Manifest:
    schema: str
    run_id: str
    profile_digest: str
    code_digest: str
    source: Source
    events: tuple
    manifest_digest: str


def sequence():
    events = []
    for repeat in (1, 2):
        for window in range(10):
            kinds = (b.A, b.V, b.AV) if repeat == 2 and window in (2, 8) else (b.AV,)
            for kind in kinds:
                n = len(events) + 1
                events.append(Selection(f"media-event-{n:02}", n, kind, repeat, window))
    return tuple(events)


def counts(events):
    f, a, v = (sum(e.kind == k for e in events) for k in (b.AV, b.A, b.V))
    return dict(events=len(events), formations=f, auditory_cues=a, visual_cues=v,
        audio=f+a, nj=f+a, visual=f+v, payloads=2*f+a+v,
        scans=2*(a+v), contacts=336*f+48*a+288*v)


def validate(m):
    need(type(m) is Manifest and m.schema == VERSION, "MEDIA_MANIFEST_INVALID")
    b.identifier(m.run_id)
    need(m.events == sequence() and all(type(e) is Selection for e in m.events), "SELECTION_INVALID")
    need(m.profile_digest == b.half.PROFILE_DIGEST, "PROFILE_INVALID")
    need(re.fullmatch("[0-9a-f]{64}", m.code_digest) is not None, "CODE_INVALID")
    src = m.source
    need(type(src) is Source and type(src.path) is str and type(src.size) is int
        and 0 < src.size <= 83498438 and re.fullmatch("[0-9a-f]{64}", src.sha256) is not None,
        "MEDIA_SOURCE_INVALID")
    need((src.video_stream, src.audio_stream, src.video_time_base, src.audio_time_base,
        src.frame_rate, src.video_size) == (0, 1, (1, 30000), (1, 48000),
        (30000, 1001), (3840, 2160)), "MEDIA_PROFILE_INVALID")
    b.check_root(asdict(m), "manifest_digest")
    need(len(b.canonical(asdict(m))) <= 4096, "MEDIA_MANIFEST_LIMIT")
    return counts(m.events)


def build(run_id, source, code_digest):
    value = dict(schema=VERSION, run_id=run_id, profile_digest=b.half.PROFILE_DIGEST,
        code_digest=code_digest, source=asdict(source), events=[asdict(e) for e in sequence()])
    m = Manifest(VERSION, run_id, b.half.PROFILE_DIGEST, code_digest, source,
        sequence(), b.digest(value))
    validate(m)
    return m


def decode(value):
    data = dict(value)
    src = dict(data["source"])
    for key in ("video_time_base", "audio_time_base", "frame_rate", "video_size"):
        src[key] = tuple(src[key])
    data["source"] = Source(**src)
    data["events"] = tuple(Selection(**e) for e in data["events"])
    m = Manifest(**data)
    validate(m)
    return m


def moment(pts, time_base):
    need(type(pts) is int and pts >= 0 and type(time_base) is tuple
        and len(time_base) == 2 and all(type(x) is int and x > 0 for x in time_base), "PTS_INVALID")
    return pts * Fraction(*time_base)


def selection_receipt(m, event, frame_pts, next_pts, pcm_hash, rgb_hash):
    need(event == m.events[event.ordinal-1], "EVENT_BINDING_INVALID")
    center = Fraction(event.window_number, 2) + Fraction(1, 20)
    if event.kind != b.A:
        need(moment(frame_pts, m.source.video_time_base) <= center
            and moment(next_pts, m.source.video_time_base) > center, "FRAME_SELECTION_INVALID")
    else:
        need(frame_pts is None and next_pts is None, "UNEXPECTED_VISUAL_BINDING")
    for h, present in ((pcm_hash, event.kind != b.V), (rgb_hash, event.kind != b.A)):
        need((type(h) is str and re.fullmatch("[0-9a-f]{64}", h) is not None)
            if present else h is None, "PAYLOAD_DIGEST_INVALID")
    # The immutable manifest supplies source, time bases, pass and runtime formula.
    value = dict(version=TIME_VERSION, manifest=m.manifest_digest, ordinal=event.ordinal,
        frame_pts=frame_pts, next_frame_pts=next_pts, pcm=pcm_hash, rgb=rgb_hash)
    need(len(b.canonical(value)) <= 512, "SELECTION_RECEIPT_LIMIT")
    return value


def runtime_times(event):
    return b.expected_times(event.ordinal, event.kind)
