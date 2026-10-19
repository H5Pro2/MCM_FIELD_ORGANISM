"""Private one-restart decoder accounting; historical decoder defaults stay fixed."""
from dataclasses import asdict
from fractions import Fraction
import hashlib
from pathlib import Path
import subprocess
import sys

from tools import _s2oe_decoder_worker as worker
from tools import _s2oe_media_decoder as old
from tools import _media_replay_protocol as replay

VERSION = "media.restart-work.v2-batch-abort"
KEYS = ("container_read_bytes", "packets", "video_frames", "audio_frames")


class RestartError(ValueError):
    def __init__(self, code, details=None):
        self.code, self.details = code, details
        super().__init__(code)


def require(ok, code, details=None):
    if not ok:
        raise RestartError(code, details)


def limits(size):
    require(type(size) is int and size > 0, "RESTART_SOURCE_SIZE")
    return dict(container_read_bytes=24*size, packets=8192,
                video_frames=2048, audio_frames=4096)


def empty():
    return {k: 0 for k in KEYS}


class Work:
    def __init__(self, size, prior=None):
        self.limit = limits(size)
        self.prior = empty() if prior is None else dict(prior)
        require(set(self.prior) == set(KEYS) and all(type(v) is int and
                0 <= v <= self.limit[k] for k, v in self.prior.items()), "RESTART_ACCOUNT")
        self.parts = {"replay": empty(), "regular": empty()}
        self.phase = "regular"
        self.frame_evidence_complete = True

    def totals(self):
        return {k: self.prior[k] + sum(v[k] for v in self.parts.values()) for k in KEYS}

    def before(self, key, amount):
        require(key in KEYS and type(amount) is int and amount >= 0, "RESTART_WORK_FORM")
        total = self.totals()
        require(total[key] + amount <= self.limit[key], "RESTART_WORK_LIMIT",
                dict(component=key, prior=self.prior, parts=self.parts, total=total[key],
                     requested=amount, limit=self.limit[key], phase=self.phase))

    def charge(self, key, amount):
        # Actual completed work remains visible even when a decoder batch is too large.
        require(type(amount) is int and amount >= 0, "RESTART_WORK_FORM")
        self.parts[self.phase][key] += amount
        self.before(key, 0)

    def payload(self):
        return dict(version=VERSION, prior=dict(self.prior),
                    parts={k: dict(v) for k, v in self.parts.items()},
                    totals=self.totals(), limits=dict(self.limit),
                    frame_evidence_complete=self.frame_evidence_complete,
                    frame_limits="POST_BATCH_ABORT_NOT_INTERNAL_WORK_MAXIMUM")


class CountedFile:
    def __init__(self, source, counters, work):
        self.work, self.counters = work, counters
        work.before("container_read_bytes", source.size)
        self.file = Path(source.path).open("rb")
        try:
            digest, length = hashlib.sha256(), 0
            while True:
                block = self.read(min(65536, source.size-length)) if length < source.size else b""
                if not block:
                    break
                digest.update(block)
                length += len(block)
            require(length == source.size and self.file.seek(0, 2) == source.size
                    and digest.hexdigest() == source.sha256, "RESTART_SOURCE_HASH")
            self.file.seek(0)
        except BaseException:
            self.file.close()
            raise

    def read(self, n=-1):
        require(type(n) is int and 0 <= n <= 1048576, "RESTART_READ_FORM")
        self.work.before("container_read_bytes", n)
        raw = self.file.read(n)
        self.counters["container_read_bytes"] += len(raw)
        self.work.charge("container_read_bytes", len(raw))
        return raw

    def seek(self, *args):
        return self.file.seek(*args)

    def tell(self):
        return self.file.tell()

    def readable(self):
        return True

    def seekable(self):
        return True

    def close(self):
        self.file.close()


class Decoder(old.Decoder):
    def __init__(self, source, *, mode=None):
        require(mode == old.FULL_MODE, "RESTART_DECODER_MODE")
        spec = source.restart
        require(set(spec) == {"version", "prior", "next_window", "resumed"}
                and spec["version"] == VERSION and type(spec["resumed"]) is bool,
                "RESTART_DECODER_BINDING")
        n = spec["next_window"]
        require(type(n) is int and (1 <= n < 20 if spec["resumed"] else n == 0),
                "RESTART_POSITION")
        self.work = Work(source.size, spec["prior"])
        require(spec["resumed"] or self.work.prior == empty(), "RESTART_INITIAL_ACCOUNT")
        self.next_window, self.replayed = n, not spec["resumed"]
        self.replay_next = 0
        self.replay_receipt = None
        super().__init__(source, mode=mode)

    def _frames(self, container, stream, modality):
        iterator = iter(container.demux(stream))
        key = "video_frames" if modality == "video" else "audio_frames"
        while True:
            self.work.before("packets", 1)
            self.work.before(key, 1)
            self.work.before("container_read_bytes", 1)
            packet = next(iterator, None)
            if packet is None:
                return
            self.counters["packets"] += 1
            self.work.charge("packets", 1)
            require(packet.size <= 4194304, "RESTART_PACKET_SIZE")
            self.progress(modality.upper(), "packet_decode")
            try:
                frames = packet.decode()
            except BaseException:
                self.work.frame_evidence_complete = False
                raise
            self.counters[key] += len(frames)
            self.work.charge(key, len(frames))
            for frame in frames:
                require(frame.pts is not None and frame.time_base is not None, "RESTART_PTS")
                yield frame

    def begin(self, repeat):
        require(not self.closed and repeat == 1 and self.repeat == 0, "RESTART_PASS")
        self._close_pass()
        try:
            for index, kind in ((0, "video"), (1, "audio")):
                self.progress("SOURCE", kind+"_hash")
                handle = CountedFile(self.source, self.counters, self.work)
                self.handles.append(handle)
                container = self.av.open(handle, mode="r")
                self.containers.append(container)
                stream = container.streams[index]
                timebase = self.source.video_time_base if kind == "video" else self.source.audio_time_base
                require(stream.type == kind and stream.time_base == Fraction(*timebase), "RESTART_STREAM")
                if kind == "video":
                    require(stream.average_rate == Fraction(*self.source.frame_rate) and
                            (stream.codec_context.width, stream.codec_context.height) == self.source.video_size,
                            "RESTART_VIDEO_PROFILE")
                    stream.codec_context.thread_count = 1
                    self.vi = iter(self._frames(container, stream, kind))
                else:
                    require(stream.codec_context.sample_rate == 48000, "RESTART_AUDIO_PROFILE")
                    self.ai = iter(self._frames(container, stream, kind))
            self.repeat, self.window = 1, -1
            self.video_last_time = self.audio_last_end = None
            self.counters["passes"] += 1
        except BaseException:
            self._close_pass()
            raise

    def replay_one(self, window):
        require(not self.replayed and type(window) is int
                and window == self.replay_next < self.next_window, "RESTART_REPLAY_ORDER")
        self.work.phase = "replay"
        _, _, pts, next_pts = super().select(1, window)
        self.release()
        self.replay_receipt = replay.receipt(self.source, window, "replay", pts, next_pts)
        self.replay_next += 1

    def select(self, repeat, window):
        restoring = not self.replayed
        if restoring:
            require(repeat == 1 and window == self.next_window
                    and self.replay_next == self.next_window, "RESTART_REPLAY_INCOMPLETE")
            self.work.phase = "regular"
        result = super().select(repeat, window)
        if restoring:
            self.replay_receipt = replay.receipt(self.source, window, "select", result[2], result[3])
            self.replayed = True
        return result


class WorkerDecoder(worker.WorkerDecoder):
    def __init__(self, source, *, prior=None, next_window=0, resumed=False):
        self.restart = dict(version=VERSION, prior=empty() if prior is None else dict(prior),
                            next_window=next_window, resumed=resumed)
        self.work_account = None
        self.replay_client = None
        self.replay_sink = None
        self._restore_deadline = None
        super().__init__(source, diagnostic_arm="COMMIT_1024", mode=old.FULL_MODE)
        if resumed:
            self.replay_client = replay.Client(source, next_window, self.work_account)

    def _request_deadline(self):
        deadline = super()._request_deadline()
        return deadline if self._restore_deadline is None else min(deadline, self._restore_deadline)

    def _prepare_select(self, repeat, window):
        client = self.replay_client
        if client is not None and not client.complete:
            require(repeat == 1 and window == client.target, "RESTART_FIRST_SELECTION")
            require(callable(self.replay_sink), "RESTART_REPLAY_SINK_REQUIRED")
            for n in range(client.confirmed, client.target):
                self._rpc(dict(op="replay", window=n))

    def replay_summary(self):
        return None if self.replay_client is None else self.replay_client.summary()

    @staticmethod
    def _launch(command, **kwargs):
        command = [sys.executable, "-m", "tools._media_restart_work", "--worker"]
        return subprocess.Popen(command, **kwargs)

    def _rpc(self, message):
        if message.get("op") == "init":
            message = {**message, "source": {**message["source"], "restart": self.restart}}
        client = self.replay_client
        active = client is not None and not client.complete and message.get("op") in ("replay", "select")
        previous_work = self.work_account
        try:
            if active:
                self._restore_deadline = client.before(message["op"], message["window"], self._sequence+1)
            result = super()._rpc(message)
            if active:
                proof = client.accept(result)
                self.replay_sink(proof)
                self.resources["restore_progress"] = client.summary()
        except BaseException:
            if active:
                client.abort()
                self.resources["restore_progress"] = client.summary()
                self.resources["restart_work"] = previous_work
            reported = self.resources.get("original_worker_error")
            self.resources["frame_evidence_complete"] = bool(reported) and self.resources.get(
                "restart_work", {}).get("frame_evidence_complete", False)
            raise
        finally:
            self._restore_deadline = None
        value = result.get("restart_work")
        require(type(value) is dict and value["version"] == VERSION
                and value["prior"] == self.restart["prior"], "RESTART_WORK_REPLY")
        self.work_account = value
        self.resources["frame_evidence_complete"] = value["frame_evidence_complete"]
        return result


def operation(decoder, message):
    if message.get("op") != "replay":
        return None
    require(set(message) == {"op", "window", "sequence"}, "RESTART_REPLAY_REQUEST")
    decoder.replay_one(message["window"])
    return {}


def evidence(decoder):
    result = {"restart_work": decoder.work.payload()}
    if decoder.replay_receipt is not None:
        result["replay_receipt"] = decoder.replay_receipt
    return result


if __name__ == "__main__":
    require(sys.argv[1:] == ["--worker"], "RESTART_WORKER_ENTRY")
    worker.worker_main(decoder_factory=Decoder,
                       evidence_factory=evidence, operation_handler=operation)
