"""Bound neutral child entry. Never opens the selected real media file."""
from fractions import Fraction
from pathlib import Path
import os
import sys
import time
import ctypes as ct

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import _s2oe_decoder_worker as w


class NeutralDecoder:
    def __init__(self, source):
        from tools import _s2oe_media_decoder as d
        import numpy as np
        root = Path(__file__).resolve().parents[1]/"sources/s2oe-worker-neutral"
        w.require(Path(source.path).resolve().is_relative_to(root), "REAL_MEDIA_BLOCKED")
        self.source, self.mode, self.closed = source, Path(source.path).stem, False
        self.counters = dict(container_read_bytes=0, packets=0, video_frames=0,
            audio_frames=0, audio_samples=0, selected_windows=0, passes=0)
        handle = d.CountedFile(source, self.counters)
        handle.close()
        markers = Path(os.environ["MEDIA_WORKER_QUAL_OUT"])/"access-markers"
        markers.mkdir(exist_ok=True)
        with (markers/(self.mode+".opened")).open("x",encoding="ascii") as stream:
            stream.write("AFTER_JOB_CONFIRMATION")
        self.np, self.d, self.key = np, d, None
        self.pcm = self.rgb = None

    def select(self, repeat, window):
        if self.mode == "overload":
            api = ct.WinDLL("kernel32", use_last_error=True)
            api.VirtualAlloc.argtypes = [ct.c_void_p, ct.c_size_t, ct.c_ulong, ct.c_ulong]
            api.VirtualAlloc.restype = ct.c_void_p
            pointer = api.VirtualAlloc(None, w.COMMIT_BYTES + 65536, 0x3000, 0x04)
            if pointer:
                api.VirtualFree.argtypes = [ct.c_void_p, ct.c_size_t, ct.c_ulong]
                api.VirtualFree(pointer, 0, 0x8000)
                raise w.WorkerError("OVERLOAD_WAS_NOT_DENIED")
            time.sleep(0.1)
            raise w.WorkerError("DECODER_MEMORY_ALLOCATION_FAILED")
        if self.mode == "timeout" or self.mode == "blocked" and window == 1:
            time.sleep(60)
        if self.mode == "exit" and window == 1:
            os._exit(17)
        if (repeat, window) != self.key:
            self.counters["selected_windows"] += 1
            self.counters["passes"] = repeat
            self.key = repeat, window
        if self.mode == "convert":
            av = self.d.load_av()
            frames = []
            for pts in (0, 1001, 2002):
                frame = av.VideoFrame(3840, 2160, "yuv420p")
                for plane in frame.planes:
                    plane.update(bytes(plane.buffer_size))
                frame.pts, frame.time_base = pts, Fraction(1, 30000)
                frame.colorspace, frame.color_range = 1, 1
                frames.append(frame)
            audio = []
            for i in range(5):
                frame = av.AudioFrame.from_ndarray(self.np.zeros((2, 1024), self.np.float32),
                    format="fltp", layout="stereo")
                frame.pts, frame.time_base, frame.sample_rate = i*1024, Fraction(1, 48000), 48000
                audio.append(frame)
            decoder = self.d.Decoder.__new__(self.d.Decoder)
            decoder.source, decoder.closed, decoder.repeat, decoder.window = self.source, False, 1, -1
            decoder.video_next = decoder.audio_next = decoder.rgb = decoder.pcm = None
            decoder.video_last_time = decoder.audio_last_end = None
            decoder.vi, decoder.ai = iter(frames), iter(audio)
            decoder.counters = self.counters
            result = decoder.select(1, 0)
            self.counters["video_frames"] = 3
            self.counters["audio_frames"] = 5
            return result
        if self.pcm is None:
            self.pcm = self.np.zeros(4800, dtype="<f4")
            self.rgb = self.np.full((1080, 1920, 3), 32, dtype=self.np.uint8)
        pts = ((window*15000+1500)//1001)*1001
        return self.pcm, self.rgb, pts, pts+1001

    def release(self):
        self.pcm = self.rgb = None

    def close(self):
        self.release()
        self.closed = True


if __name__ == "__main__":
    w.require(sys.argv[1:] == ["--worker"], "DECODER_ENTRY_INVALID")
    w.worker_main(NeutralDecoder)
