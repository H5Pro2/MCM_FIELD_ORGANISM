"""Native logging and transport fixture, without media access."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import _s2oe_decoder_worker as w
from tools._s2oe_media_decoder import load_av


class NeutralDecoder:
    def __init__(self, source):
        self.av = load_av()
        self.mode = source.path
        self.counters = dict(container_read_bytes=0, packets=0, video_frames=0,
            audio_frames=0, audio_samples=0, selected_windows=0, passes=0)

    def select(self, repeat, window):
        self.progress("VIDEO", "neutral_native_error")
        for _ in range(40 if self.mode == "overflow" else 1):
            self.av.logging.log(self.av.logging.ERROR, "neutral", "bound neutral native error")
        if self.mode == "abrupt":
            import os
            os._exit(17)
        if self.mode == "error":
            raise self.av.error.InvalidDataError(1094995529, "neutral invalid data")
        import numpy as np
        self.counters["selected_windows"] = 1
        return np.zeros(4800, dtype="<f4"), np.zeros((1080,1920,3), dtype=np.uint8), 1001, 2002

    def close(self):
        pass


if __name__ == "__main__":
    w.worker_main(NeutralDecoder)
