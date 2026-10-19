"""Independent neutral checks of the new diagnostic boundary."""
from dataclasses import dataclass
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch
from tools import _s2oe_decoder_worker as w


@dataclass(frozen=True)
class Source:
    path: str
    sha256: str = "0" * 64
    size: int = 1
    video_time_base: tuple = (1, 30000)
    audio_time_base: tuple = (1, 48000)
    frame_rate: tuple = (30000, 1001)
    video_size: tuple = (3840, 2160)


def launch(command, **kwargs):
    return subprocess.Popen([command[0], str(Path(__file__).with_name(
        "s2oe_diagnostic_worker.py"))], **kwargs)


class DiagnosticTests(unittest.TestCase):
    def failure(self, mode, limit=False):
        with patch.object(w.WorkerDecoder, "_launch", staticmethod(launch)):
            worker = w.WorkerDecoder(Source(mode))
        self.addCleanup(worker.close)
        original = worker.job.snapshot
        def snapshot():
            data = original()
            if limit:
                data.update(memory_limit_notification=True, memory_limit_messages=[10])
            return data
        with patch.object(worker.job, "snapshot", snapshot):
            with self.assertRaises(w.WorkerError) as error:
                worker.select(1, 0)
            worker.close()
        self.assertTrue(worker.resources["worker_closed"])
        self.assertEqual(worker.last_confirmed_phase["operation"], "neutral_conversion")
        self.assertEqual(worker.counters["selected_windows"], 0)
        self.assertFalse(worker.resources["read_counters_complete"])
        return error.exception, worker

    def test_original_exception(self):
        exc, worker = self.failure("ordinary")
        self.assertEqual(exc.code, "DECODER_WORKER_FAILED")
        self.assertEqual(worker.resources["original_worker_error"]["exception_type"], "ValueError")
        self.assertTrue(worker.resources["original_worker_error"]["traceback"])

    def test_allocation_exception(self):
        exc, worker = self.failure("allocation")
        self.assertEqual(exc.code, "DECODER_MEMORY_ALLOCATION_FAILED")
        self.assertEqual(worker.resources["original_worker_error"]["exception_type"], "MemoryError")

    def test_limit_does_not_erase_original(self):
        exc, worker = self.failure("ordinary", limit=True)
        self.assertEqual(exc.code, "DECODER_MEMORY_LIMIT")
        self.assertEqual(worker.resources["original_worker_error"]["exception_type"], "ValueError")
        self.assertEqual(worker.resources["memory_limit_messages"], [10])

    def test_abrupt_end_retains_phase_not_exception(self):
        exc, worker = self.failure("abrupt")
        self.assertEqual(exc.code, "DECODER_WORKER_EXIT")
        self.assertIsNone(worker.resources["original_worker_error"])
        self.assertFalse(worker.resources["exact_failure_location_known"])

    def test_bounded_diagnostics_and_unchanged_limits(self):
        _, worker = self.failure("ordinary")
        self.assertEqual(w.COMMIT_BYTES, 536870912)
        self.assertEqual(w.SLOT_BYTES, 6240000)
        self.assertLess(len(w.encode(worker.resources)), w.MESSAGE_BYTES)
        self.assertNotIn("neutral-error", str(worker.resources))
        self.assertEqual(set(worker.resources["original_worker_error"]),
            {"error", "exception_type", "exception_module", "errno", "traceback"})
