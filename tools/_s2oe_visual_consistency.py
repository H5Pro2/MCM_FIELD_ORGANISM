"""Private four-frame diagnostic access; no memory, field or audio analysis."""
from fractions import Fraction
import hashlib
import math
from pathlib import Path
import struct
import sys
import numpy as np

from tools import _s2oe_media_decoder as media
from tools import _s2oe_decoder_worker as worker
from tools import _s2oe_uhd_profile as uhd

VERSION = "s2oe.visual-consistency.v1"
POINTS = {2: (31031, 32032), 8: (121121, 122122)}
MAIN_GATE = False


def need(ok, code):
    worker.require(ok, code)


def native_binding(frame):
    # Active rows only; allocation padding is not image content.
    need(frame.format.name == "yuv420p", "NATIVE_FORMAT_UNSUPPORTED")
    planes = []
    for plane in frame.planes:
        need(0 < plane.width <= plane.line_size and plane.height > 0,
             "NATIVE_PLANE_INVALID")
        view = memoryview(plane)
        need(len(view) >= plane.line_size * plane.height, "NATIVE_PLANE_INVALID")
        h = hashlib.sha256()
        for row in range(plane.height):
            h.update(view[row*plane.line_size:row*plane.line_size+plane.width])
        planes.append(dict(width=plane.width, height=plane.height, sha256=h.hexdigest()))
    need(len(planes) == 3, "NATIVE_PLANE_INVALID")
    return dict(format=frame.format.name, width=frame.width, height=frame.height,
                colorspace=int(frame.colorspace), color_range=int(frame.color_range), planes=planes)


class VideoDecoder(media.Decoder):
    capture_native = True
    bind_native = staticmethod(native_binding)

    def _frames(self, container, stream, modality):
        frames = super()._frames(container, stream, modality)
        while True:
            need(self.counters['video_frames'] < self.frame_budget, 'GLOBAL_FRAME_LIMIT')
            try:
                frame = next(frames)
            except StopIteration:
                return
            yield frame

    def video_point(self, window, frame_budget=400):
        need(type(window) is int and window in POINTS and self.repeat == 0 and not self.closed,
             "VIDEO_POINT_INVALID")
        need(type(frame_budget) is int and 0 < frame_budget <= 400, 'FRAME_BUDGET_INVALID')
        self.frame_budget = frame_budget
        # Same file hash, stream validation, packet decoder and converter as media.Decoder.
        try:
            h = media.CountedFile(self.source, self.counters)
            self.handles.append(h)
            c = self.av.open(h, mode="r")
            self.containers.append(c)
            stream = c.streams[0]
            need(stream.type == "video" and stream.time_base == Fraction(*self.source.video_time_base),
                 "STREAM_TIME_INVALID")
            need(stream.average_rate == Fraction(*self.source.frame_rate)
                 and (stream.codec_context.width, stream.codec_context.height) == self.source.video_size,
                 "VIDEO_PROFILE_INVALID")
            stream.codec_context.thread_count = 1
            self.vi = iter(self._frames(c, stream, "video"))
            self.video_last_time = None
            self._select_video(Fraction(window, 2)+Fraction(1, 20))
            self.repeat = 1
            self.counters["passes"] = self.counters["selected_windows"] = 1
            evidence = dict(version=VERSION, window=window, pts=self.frame_pts,
                next_pts=self.next_pts, time_base=list(self.source.video_time_base),
                native=self.native, rgb_sha256=hashlib.sha256(self.rgb).hexdigest())
            return self.rgb, evidence
        except BaseException:
            self.close()
            raise


class VideoWorker(worker.WorkerDecoder):
    @staticmethod
    def _launch(args, **kwargs):
        return worker.WorkerDecoder._launch(
            [args[0], "-m", "tools._s2oe_visual_consistency", "--worker"], **kwargs)

    def video_point(self, window, frame_budget=400):
        need(type(window) is int and window in POINTS, "VIDEO_POINT_INVALID")
        need(type(frame_budget) is int and 0 < frame_budget <= 400, 'FRAME_BUDGET_INVALID')
        need(self._call_lock.acquire(blocking=False), "DECODER_BUSY")
        try:
            result = self._rpc(dict(op="video_point", window=window, frame_budget=frame_budget))["video"]
            need(result["version"] == VERSION and result["window"] == window
                 and result["time_base"] == [1, 30000], "VIDEO_BINDING_INVALID")
            # A different valid selection is diagnostic evidence, not a forced expected PTS.
            need(20*result["pts"] <= (10*window+1)*30000 < 20*result["next_pts"],
                 "FRAME_SELECTION_INVALID")
            rgb = np.frombuffer(self.slot, dtype=np.uint8, count=worker.RGB_BYTES,
                offset=worker.PCM_BYTES).reshape(1080, 1920, 3).copy()
            need(hashlib.sha256(rgb).hexdigest() == result["rgb_sha256"], "RGB_BINDING_INVALID")
            rgb.flags.writeable = False
            return rgb, result
        finally:
            self._call_lock.release()


def open_video(source, profile, run_id):
    need(MAIN_GATE, "DIAGNOSTIC_GATE_CLOSED")
    uhd.validate(profile, source, run_id)
    return VideoWorker(source, diagnostic_arm="COMMIT_1024")


def occlude(rgb):
    need(type(rgb) is np.ndarray and rgb.dtype == np.uint8 and rgb.shape == (1080,1920,3),
         "RGB_INVALID")
    frame = rgb.copy()
    cells = frame.reshape(8,135,12,160,3)
    for i in range(32,288):
        cell, channel = divmod(i,3)
        row, col = divmod(cell,12)
        cells[row,:,col,:,channel] = 0
    return frame


def bind_values(values):
    need(type(values) is tuple and len(values) == 288 and all(
        type(x) is float and math.isfinite(x) and 0 <= x <= 1 for x in values), "VALUES_INVALID")
    return tuple(x.hex() for x in values)


def compare(left, right, indices):
    a, b = bind_values(left), bind_values(right)
    need(indices in (tuple(range(288)), tuple(range(32))), "COMPARISON_SCOPE_INVALID")
    return tuple(dict(index=i, left=a[i], right=b[i], equal=struct.pack('>d',left[i]) ==
                     struct.pack('>d',right[i])) for i in indices)


def compare_frames(left, right):
    for item in (left,right):
        need(type(item) is dict and set(item) ==
             {'version','window','pts','next_pts','time_base','native','rgb_sha256'},
             'FRAME_EVIDENCE_INVALID')
        need(item['version'] == VERSION and type(item['window']) is int
             and item['window'] in POINTS and item['time_base'] == [1,30000]
             and type(item['pts']) is int and type(item['next_pts']) is int
             and 0 <= 20*item['pts'] <= (10*item['window']+1)*30000 < 20*item['next_pts'],
             'FRAME_EVIDENCE_INVALID')
    need(left['window'] == right['window'], 'POINT_MISMATCH')
    return dict(pts_equal=left['pts']==right['pts'],
        native_equal=left['native']==right['native'],
        rgb_equal=left['rgb_sha256']==right['rgb_sha256'],
        historical_pts_equal=[item['pts']==POINTS[item['window']][0] for item in (left,right)])


if __name__ == "__main__":
    need(sys.argv[1:] == ["--worker"], "DIAGNOSTIC_ENTRY_INVALID")
    worker.worker_main(VideoDecoder)
