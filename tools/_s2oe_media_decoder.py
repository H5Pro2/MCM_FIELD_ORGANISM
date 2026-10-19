"""Bounded sequential PyAV selection; no receptors or memory in this module."""
from fractions import Fraction
import hashlib
from pathlib import Path
import sys
import numpy as np

from tools import _s2oe_decoder_worker as p


def load_av():
    # Keep the qualified global Python/NumPy environment; add only the existing
    # project dependency location at lowest priority for this import.
    location = str(Path(__file__).resolve().parents[1]/".venv/Lib/site-packages")
    sys.path.append(location)
    try:
        import av
    finally:
        sys.path.remove(location)
    p.need(Path(av.__file__).resolve().parent == Path(location)/"av"
        and av.__version__ == "16.1.0", "DECODER_VERSION_INVALID")
    expected = dict(libavutil=(60,8,100),libavcodec=(62,11,100),libavformat=(62,3,100),
        libavdevice=(62,1,100),libavfilter=(11,4,100),libswscale=(9,1,100),libswresample=(6,1,100))
    p.need(av.library_versions == expected, "DECODER_LIBRARIES_INVALID")
    return av


class CountedFile:
    def __init__(self, source, counters):
        self.file = Path(source.path).open("rb")
        self.counters, self.limit = counters, 12*source.size
        try:
            h = hashlib.sha256()
            size = 0
            while block := self.read(65536):
                size += len(block)
                h.update(block)
            p.need(size == source.size and h.hexdigest() == source.sha256, "MEDIA_HASH_INVALID")
            self.file.seek(0)
        except BaseException:
            self.file.close()
            raise

    def read(self, n=-1):
        p.need(type(n) is int and 0 <= n <= 1048576, "DECODER_READ_LIMIT")
        raw = self.file.read(n)
        self.counters["container_read_bytes"] += len(raw)
        p.need(self.counters["container_read_bytes"] <= self.limit, "CONTAINER_READ_LIMIT")
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


def mono(block):
    p.need(block.dtype == np.float32 and block.ndim == 2 and block.shape[0] == 2
        and 0 < block.shape[1] <= 8192 and np.isfinite(block).all(), "AUDIO_BLOCK_INVALID")
    value = (0.5 * (block[0].astype(np.float64) + block[1].astype(np.float64))).astype("<f4")
    p.need(np.isfinite(value).all() and np.max(np.abs(value)) <= 1, "PCM_DOMAIN_INVALID")
    return value


FULL_MODE = "s2oe.full-file-sampled.v1"


class Decoder:
    def __init__(self, source, *, mode=None):
        p.need(mode in (None, FULL_MODE), "DECODER_MODE_INVALID")
        self.mode, self.stream_ends = mode, None
        self.progress = lambda phase, operation: None
        av = load_av()
        self.av, self.source = av, source
        self.handles, self.containers = [], []
        self.counters = dict(container_read_bytes=0, packets=0, video_frames=0,
            audio_frames=0, audio_samples=0, selected_windows=0, passes=0)
        self.repeat, self.window = 0, -1
        self.video_next = self.audio_next = self.rgb = self.pcm = None
        self.closed = False

    def _frames(self, container, stream, modality):
        for packet in container.demux(stream):
            self.counters["packets"] += 1
            full = getattr(self, "mode", None) == FULL_MODE
            p.need(self.counters["packets"] <= (4096 if full else 2048) and packet.size <= 4194304, "PACKET_LIMIT")
            self.progress(modality.upper(), "packet_decode")
            for frame in packet.decode():
                key = "video_frames" if modality == "video" else "audio_frames"
                self.counters[key] += 1
                limit = (1024 if modality == "video" else 2048) if full else (400 if modality == "video" else 600)
                p.need(self.counters[key] <= limit, "DECODE_LIMIT")
                p.need(frame.pts is not None and frame.time_base is not None, "PTS_MISSING")
                yield frame

    def _close_pass(self):
        self.video_next = self.audio_next = self.rgb = self.pcm = None
        self.vi = self.ai = None
        failed = False
        for obj in (*self.containers, *self.handles):
            try:
                obj.close()
            except Exception:
                failed = True
        self.containers, self.handles = [], []
        p.need(not failed, "DECODER_CLOSE_FAILED")

    def begin(self, repeat):
        allowed = (1,) if getattr(self, "mode", None) == FULL_MODE else (1, 2)
        p.need(not self.closed and repeat == self.repeat + 1 and repeat in allowed, "PASS_INVALID")
        self._close_pass()
        try:
            for index, kind in ((0, "video"), (1, "audio")):
                self.progress("SOURCE", kind + "_hash")
                h = CountedFile(self.source, self.counters)
                self.handles.append(h)
                self.progress("CONTAINER", kind + "_open")
                c = self.av.open(h, mode="r")
                self.containers.append(c)
                stream = c.streams[index]
                expected = self.source.video_time_base if kind == "video" else self.source.audio_time_base
                p.need(stream.type == kind and stream.time_base == Fraction(*expected), "STREAM_TIME_INVALID")
                if kind == "video":
                    p.need(stream.average_rate == Fraction(*self.source.frame_rate)
                        and (stream.codec_context.width, stream.codec_context.height) == self.source.video_size,
                        "VIDEO_PROFILE_INVALID")
                    stream.codec_context.thread_count = 1
                    self.vi = iter(self._frames(c, stream, kind))
                else:
                    p.need(stream.codec_context.sample_rate == 48000, "AUDIO_RATE_INVALID")
                    self.ai = iter(self._frames(c, stream, kind))
            self.repeat, self.window = repeat, -1
            self.video_last_time = self.audio_last_end = None
            self.counters["passes"] += 1
        except BaseException:
            self._close_pass()
            raise

    def select(self, repeat, window):
        p.need(not self.closed, "DECODER_CLOSED")
        if repeat != self.repeat:
            self.begin(repeat)
        if window == self.window:
            p.need(self.pcm is not None and self.rgb is not None, "WINDOW_RELEASED")
            return self.pcm, self.rgb, self.frame_pts, self.next_pts
        full = getattr(self, "mode", None) == FULL_MODE
        p.need(window == self.window+1 and 0 <= window < (20 if full else 10), "WINDOW_ORDER_INVALID")
        self.pcm = self.rgb = None
        center = window * (Fraction(7, 5) if full else Fraction(1, 2)) + Fraction(1, 20)
        self._select_video(center)
        return self._select_audio(window)

    def _select_video(self, center):
        selected_native = None
        while True:
            frame = self.video_next
            if frame is None:
                self.progress("VIDEO", "next_frame")
                frame = next(self.vi, None)
            p.need(frame is not None, "FRAME_COVERAGE_MISSING")
            tb = (frame.time_base.numerator, frame.time_base.denominator)
            p.need(tb == self.source.video_time_base, "FRAME_TIME_BASE_INVALID")
            t = p.moment(frame.pts, tb)
            if t > center:
                self.video_next = frame
                self.next_pts = frame.pts
                break
            p.need(self.video_last_time is None or t > self.video_last_time, "FRAME_ORDER_INVALID")
            self.video_last_time = t
            self.video_next = None
            p.need((frame.width, frame.height) == self.source.video_size, "FRAME_SIZE_INVALID")
            # At most one retained source frame and two RGB buffers during replacement.
            p.need(frame.colorspace == 1 and frame.color_range == 1, "COLOR_PROFILE_INVALID")
            self.progress("VIDEO", "reformat_rgb")
            self.rgb = frame.reformat(width=1920, height=1080, format="rgb24", interpolation="AREA",
                src_colorspace=1, dst_colorspace=1, src_color_range="MPEG", dst_color_range="JPEG").to_ndarray()
            self.frame_pts = frame.pts
            if getattr(self, "capture_native", False):
                selected_native = frame
            del frame
        p.need(self.rgb is not None, "FRAME_SELECTION_MISSING")
        if getattr(self, "capture_native", False):
            p.need(selected_native is not None, "NATIVE_FRAME_MISSING")
            self.native = self.bind_native(selected_native)

    def _select_audio(self, window):
        start = window * (67200 if getattr(self, "mode", None) == FULL_MODE else 24000)
        end = start + 4800
        pcm = np.empty(4800, dtype="<f4")
        filled = 0
        while filled < 4800:
            frame = self.audio_next
            if frame is None:
                self.progress("AUDIO", "next_frame")
                frame = next(self.ai, None)
                p.need(frame is not None, "AUDIO_COVERAGE_MISSING")
                p.need(frame.time_base == Fraction(1, 48000) and frame.sample_rate == 48000
                    and frame.layout.name == "stereo" and frame.format.name == "fltp"
                    and 0 < frame.samples <= 8192, "AUDIO_FORMAT_INVALID")
                p.need(type(frame.pts) is int and frame.pts >= 0, "AUDIO_PTS_INVALID")
                p.need(self.audio_last_end is None or frame.pts == self.audio_last_end, "AUDIO_CONTINUITY_INVALID")
                self.audio_last_end = frame.pts + frame.samples
                self.counters["audio_samples"] += frame.samples
                self.audio_next = frame
            stop = frame.pts + frame.samples
            if stop <= start+filled:
                self.audio_next = None
                continue
            p.need(frame.pts <= start+filled, "AUDIO_GAP")
            count = min(end, stop) - (start+filled)
            self.progress("AUDIO", "mono_conversion")
            block = mono(frame.to_ndarray())
            offset = start+filled-frame.pts
            pcm[filled:filled+count] = block[offset:offset+count]
            filled += count
            del block
            if start+filled == stop:
                self.audio_next = None
        self.window, self.pcm = window, pcm
        self.counters["selected_windows"] += 1
        return self.pcm, self.rgb, self.frame_pts, self.next_pts

    def release(self):
        self.pcm = self.rgb = None

    def drain(self):
        p.need(getattr(self, "mode", None) == FULL_MODE and not self.closed
               and self.window == 19 and self.stream_ends is None, "DRAIN_ORDER_INVALID")
        self.release()
        # Remaining frames are consumed, validated and discarded, never reformatted.
        frame = self.video_next
        self.video_next = None
        last_pts = self.frame_pts
        while True:
            if frame is None:
                self.progress("DRAINING", "video_eof")
                frame = next(self.vi, None)
            if frame is None:
                break
            p.need(frame.time_base == Fraction(*self.source.video_time_base)
                and (frame.width, frame.height) == self.source.video_size
                and frame.colorspace == 1 and frame.color_range == 1, "DRAIN_VIDEO_PROFILE_INVALID")
            t = p.moment(frame.pts, self.source.video_time_base)
            p.need(self.video_last_time is None or t > self.video_last_time, "FRAME_ORDER_INVALID")
            self.video_last_time, last_pts = t, frame.pts
            frame = None
        self.audio_next = None  # Its full span was already validated and counted.
        while True:
            self.progress("DRAINING", "audio_eof")
            frame = next(self.ai, None)
            if frame is None:
                break
            p.need(frame.time_base == Fraction(1, 48000) and frame.sample_rate == 48000
                and frame.layout.name == "stereo" and frame.format.name == "fltp"
                and 0 < frame.samples <= 8192, "AUDIO_FORMAT_INVALID")
            p.need(type(frame.pts) is int and frame.pts >= 0, "AUDIO_PTS_INVALID")
            p.need(self.audio_last_end is None or frame.pts == self.audio_last_end, "AUDIO_CONTINUITY_INVALID")
            self.audio_last_end = frame.pts + frame.samples
            self.counters["audio_samples"] += frame.samples
            del frame
        self.stream_ends = dict(video_eof=True, audio_eof=True, last_video_pts=last_pts,
            audio_end_sample=self.audio_last_end, selected_windows=self.counters["selected_windows"])
        return dict(self.stream_ends)

    def close(self):
        if not self.closed:
            self.closed = True
            self._close_pass()
