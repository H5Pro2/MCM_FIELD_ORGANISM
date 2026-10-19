"""Bound synthetic packet source and real native runtime subprocess entry."""
from fractions import Fraction
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace as NS
from unittest.mock import patch

from tools import _media_restart_work as w


class Frame:
    def __init__(self, video, ordinal):
        self.video = video
        self.pts = ordinal*(1001 if video else 1024)
        self.time_base = Fraction(1, 30000 if video else 48000)
        self.width, self.height, self.colorspace, self.color_range = 3840, 2160, 1, 1
        self.sample_rate, self.samples = 48000, 1024
        self.layout, self.format = NS(name="stereo"), NS(name="fltp")

    def to_ndarray(self):
        import numpy as np
        return np.zeros((2, 1024), dtype=np.float32)

    def reformat(self, **kwargs):
        import numpy as np
        return NS(to_ndarray=lambda: np.full((1080, 1920, 3), 32, dtype=np.uint8))


class Container:
    def __init__(self, handle):
        self.handle = handle
        self.streams = [NS(type="video", time_base=Fraction(1, 30000), average_rate=Fraction(30000, 1001),
                           codec_context=NS(width=3840, height=2160, thread_count=1)),
                        NS(type="audio", time_base=Fraction(1, 48000), codec_context=NS(sample_rate=48000))]

    def demux(self, stream):
        video = stream.type == "video"
        count = 801 if video else 1255
        for n in range(count):
            self.handle.read(1)
            # Last packet models delayed EOF output, not an extra frame.
            yield NS(size=0 if n == count-1 else 1, decode=lambda n=n: [Frame(video, n)])

    def close(self):
        pass


class FakeAV:
    __version__, ffmpeg_version_info, library_versions = "neutral", "NOT_NATIVE_FFMPEG", {}
    logging = NS(ERROR=16, set_level=lambda value: None, set_skip_repeated=lambda value: None)
    open = staticmethod(lambda handle, mode: Container(handle))


class NeutralDecoder(w.Decoder):
    def __init__(self, source, *, mode=None):
        root = Path(__file__).resolve().parents[1]/"sources/media-restart-neutral"
        w.require(Path(source.path).resolve().is_relative_to(root), "NEUTRAL_SOURCE_ONLY")
        with patch.object(w.old, "load_av", return_value=FakeAV):
            super().__init__(source, mode=mode)


class NeutralWorker(w.WorkerDecoder):
    @staticmethod
    def _launch(command, **kwargs):
        return subprocess.Popen([sys.executable, "-m", "tests.media_restart_neutral", "decoder"], **kwargs)


def session_child(folder, cut, checkpoint_path):
    from tools import _media_restart_checkpoint as c
    from tools import _media_restart_evidence as evidence
    from tools import _media_restart_player as player
    root = Path(os.environ["MEDIA_RESTART_QUAL_OUT"])
    prereg = json.loads((root/"preregistration.json").read_bytes())
    manifest = c.p.decode(prereg["manifest"])
    store = evidence.Store(root, prereg["external"])
    binding = NS(manifest=manifest, source=Path(manifest.source.path), output=root/folder,
                 claim=root/(folder+".claim"), mode="NEUTRAL_CONNECTION")
    app = player.Player(binding, store, selected_checkpoint=None if checkpoint_path == "-" else root/checkpoint_path)
    def boundary():
        if cut and len(app.session.runtime.rows) == cut:
            app.stop_event.set()
    app._after_event = boundary
    with patch.object(c, "QUALIFIED", True), patch.object(w, "WorkerDecoder", NeutralWorker):
        app.start()
        app.thread.join(180)
        w.require(not app.thread.is_alive(), "NEUTRAL_SESSION_TIMEOUT")
        status = json.loads(app.status())
        w.require(status["phase"] == ("SUSPENDED" if cut else "RECORDING_COMPLETE"),
                  "NEUTRAL_NATIVE_STATUS", status)
        store.publish(root/(folder+"-process.json"), dict(pid=os.getpid(), phase=status["phase"],
            closed=app.session.closed, gate=c.MAIN_GATE, next_ordinal=status["next_ordinal"]))


if __name__ == "__main__":
    if sys.argv[1] == "decoder":
        w.worker.worker_main(decoder_factory=NeutralDecoder,
            evidence_factory=lambda d: {"restart_work": d.work.payload()})
    elif sys.argv[1] == "session":
        session_child(sys.argv[2], int(sys.argv[3]), sys.argv[4])
    else:
        raise SystemExit("Neutral entry only")
