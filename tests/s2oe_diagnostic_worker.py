"""Neutral failures only; never opens the supplied source path."""
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import _s2oe_decoder_worker as w


class Fixture:
    def __init__(self, source):
        self.mode = source.path
        self.counters = dict(container_read_bytes=0, packets=0, video_frames=0,
            audio_frames=0, audio_samples=0, selected_windows=0, passes=0)

    def select(self, repeat, window):
        self.progress("VIDEO", "neutral_conversion")
        if self.mode == "abrupt":
            os._exit(17)
        if self.mode == "allocation":
            raise MemoryError()
        raise ValueError("neutral-error")

    def close(self):
        pass


if __name__ == "__main__":
    w.worker_main(Fixture)
