"""Finite replay confirmations; no receptor, runtime or media I/O."""
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
import math
import time

VERSION = "media.replay-confirmation.v1"
REQUEST_SECONDS = 30.0
TOTAL_SECONDS = 600.0
MAX_REQUESTS = 20
RECEIPT_BYTES = 4096
KEYS = ("container_read_bytes", "packets", "video_frames", "audio_frames")


class ReplayError(ValueError):
    def __init__(self, code, details=None):
        self.code, self.details = code, details
        super().__init__(code)


def need(ok, code):
    if not ok:
        raise ReplayError(code)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")


def binding(source):
    value = {k: getattr(source, k) for k in
             ("path", "sha256", "size", "video_time_base", "audio_time_base", "frame_rate")}
    return hashlib.sha256(canonical(value)).hexdigest()


def receipt(source, window, kind, pts, next_pts):
    return dict(version=VERSION, source=binding(source), kind=kind, window=window,
        audio_start=window*67200, audio_end=window*67200+4800,
        center=[28*window+1, 20], video_time_base=list(source.video_time_base),
        frame_pts=pts, next_frame_pts=next_pts)


def check_receipt(value, source, window, kind):
    need(type(value) is dict and type(value.get("frame_pts")) is int
         and type(value.get("next_frame_pts")) is int, "REPLAY_RECEIPT_FORM")
    expected = receipt(source, window, kind, value["frame_pts"], value["next_frame_pts"])
    need(canonical(value) == canonical(expected), "REPLAY_SOURCE_TIME_BINDING")
    tb = Fraction(*source.video_time_base)
    center = Fraction(28*window+1, 20)
    need(0 <= value["frame_pts"]*tb <= center < value["next_frame_pts"]*tb,
         "REPLAY_FRAME_BINDING")


def check_work(value, prior, previous, limits):
    need(type(value) is dict and value.get("prior") == prior and value.get("limits") == limits,
         "REPLAY_WORK_BINDING")
    need(set(value) == {"version", "prior", "parts", "totals", "limits", "frame_evidence_complete", "frame_limits"}
         and value["version"] == "media.restart-work.v2-batch-abort"
         and value["frame_limits"] == "POST_BATCH_ABORT_NOT_INTERNAL_WORK_MAXIMUM", "REPLAY_WORK_FORM")
    need(value.get("frame_evidence_complete") is True
         and set(value.get("parts", {})) == {"regular", "replay"}, "REPLAY_WORK_FORM")
    rows = (value.get("totals", {}), *value["parts"].values())
    need(all(set(r) == set(KEYS) and all(type(v) is int and v >= 0 for v in r.values())
             for r in rows), "REPLAY_WORK_FORM")
    for k in KEYS:
        need(value["totals"][k] == prior[k]+sum(r[k] for r in value["parts"].values())
             and value["totals"][k] <= limits[k], "REPLAY_WORK_LIMIT")
        need(value["totals"][k] >= previous["totals"][k]
             and all(value["parts"][part][k] >= previous["parts"][part][k]
                     for part in ("regular", "replay")), "REPLAY_COUNTER_REGRESSION")


class Client:
    def __init__(self, source, target, initial, *, clock=time.monotonic):
        need(type(target) is int and 1 <= target < MAX_REQUESTS, "REPLAY_TARGET")
        self.source, self.target, self.clock = source, target, clock
        self.initial, self.last = deepcopy(initial), deepcopy(initial)
        self.started = None
        self.requests = self.confirmed = 0
        self.complete = self.unknown = False
        self.pending = None
        self.last_sequence = None
        self.elapsed = 0.0

    def before(self, kind, window, sequence):
        need(not self.complete and not self.unknown and self.pending is None, "REPLAY_REQUEST_STATE")
        need(type(sequence) is int and (self.last_sequence is None or sequence == self.last_sequence+1),
             "REPLAY_SEQUENCE")
        need(type(window) is int and window == self.confirmed and kind == ("replay" if window < self.target else "select"),
             "REPLAY_ORDER")
        need(self.requests < MAX_REQUESTS, "REPLAY_REQUEST_LIMIT")
        now = self.clock()
        if self.started is None:
            self.started = now
        self.elapsed = now-self.started
        need(0 <= self.elapsed < TOTAL_SECONDS, "REPLAY_TOTAL_TIMEOUT")
        self.requests += 1
        self.pending = (kind, window, sequence)
        self.requested_at = self.elapsed
        self.deadline = min(now+REQUEST_SECONDS, self.started+TOTAL_SECONDS)
        return self.deadline

    def accept(self, result):
        need(self.pending is not None, "REPLAY_UNEXPECTED_CONFIRMATION")
        kind, window, sequence = self.pending
        self.elapsed = self.clock()-self.started
        need(0 <= self.elapsed <= TOTAL_SECONDS, "REPLAY_TOTAL_TIMEOUT")
        need(self.elapsed-self.requested_at <= REQUEST_SECONDS, "REPLAY_REQUEST_TIMEOUT")
        need(result.get("sequence") == sequence, "REPLAY_SEQUENCE")
        check_receipt(result.get("replay_receipt"), self.source, window, kind)
        value = result.get("restart_work")
        check_work(value, self.initial["prior"], self.last, self.initial["limits"])
        if kind == "replay":
            need(value["parts"]["regular"] == self.last["parts"]["regular"], "REPLAY_WRONG_ACCOUNT_PART")
        else:
            need(value["parts"]["replay"] == self.last["parts"]["replay"], "REPLAY_WRONG_ACCOUNT_PART")
        proof = dict(sequence=sequence, receipt=deepcopy(result["replay_receipt"]),
                     work=deepcopy(value), elapsed_seconds=self.elapsed, requested_at_seconds=self.requested_at)
        need(len(canonical(proof)) <= RECEIPT_BYTES-128, "REPLAY_RECEIPT_SIZE")
        self.last = deepcopy(value)
        self.last_sequence, self.pending = sequence, None
        self.confirmed += 1
        self.complete = kind == "select"
        return proof

    def abort(self):
        self.unknown = self.pending is not None
        if self.started is not None:
            self.elapsed = self.clock()-self.started

    def summary(self):
        return dict(version=VERSION, target=self.target, requests=self.requests,
            confirmed=self.confirmed, complete=self.complete, unconfirmed_work_unknown=self.unknown,
            elapsed_seconds=self.elapsed, total_seconds=TOTAL_SECONDS,
            request_seconds=REQUEST_SECONDS, max_requests=MAX_REQUESTS)


def verify(proofs, source, target, prior, final_work, summary):
    """Offline chain check, independently traversed; no Client or decoder call."""
    need(len(proofs) == target+1 <= MAX_REQUESTS, "REPLAY_PROOF_COUNT")
    previous = {"totals": dict(prior), "parts": {p: {k: 0 for k in KEYS} for p in ("regular", "replay")}}
    sequence, elapsed = None, 0.0
    for n, proof in enumerate(proofs):
        need(set(proof) == {"sequence", "receipt", "work", "elapsed_seconds", "requested_at_seconds"}, "REPLAY_PROOF_FORM")
        need(type(proof["sequence"]) is int and (sequence is None or proof["sequence"] == sequence+1),
             "REPLAY_SEQUENCE")
        kind = "replay" if n < target else "select"
        check_receipt(proof["receipt"], source, n, kind)
        check_work(proof["work"], prior, previous, final_work["limits"])
        part = "regular" if kind == "replay" else "replay"
        need(proof["work"]["parts"][part] == previous["parts"][part], "REPLAY_WRONG_ACCOUNT_PART")
        t = proof["elapsed_seconds"]
        start = proof["requested_at_seconds"]
        need(type(t) in (float, int) and math.isfinite(t) and elapsed <= t <= TOTAL_SECONDS,
             "REPLAY_TIME_CHAIN")
        need(type(start) in (float, int) and math.isfinite(start) and elapsed <= start <= t
             and t-start <= REQUEST_SECONDS, "REPLAY_TIME_CHAIN")
        sequence, elapsed, previous = proof["sequence"], t, proof["work"]
    need(final_work["parts"]["replay"] == previous["parts"]["replay"]
         and all(final_work["totals"][k] >= previous["totals"][k] for k in KEYS), "REPLAY_FINAL_ACCOUNT")
    need(summary == dict(version=VERSION, target=target, requests=target+1, confirmed=target+1,
        complete=True, unconfirmed_work_unknown=False, elapsed_seconds=elapsed, total_seconds=TOTAL_SECONDS,
        request_seconds=REQUEST_SECONDS, max_requests=MAX_REQUESTS), "REPLAY_SUMMARY")
    return True
