"""Focused isolation/logging coverage; no historical suites or media sources."""
from dataclasses import dataclass
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch
from tools import _s2oe_decoder_worker as w


@dataclass(frozen=True)
class Source:
    path: str
    video_time_base: tuple = (1,30000)
    audio_time_base: tuple = (1,48000)
    frame_rate: tuple = (30000,1001)
    video_size: tuple = (3840,2160)


def launch(command, **kwargs):
    return subprocess.Popen([command[0], str(Path(__file__).with_name("s2oe_isolation_worker.py"))], **kwargs)


class IsolationTests(unittest.TestCase):
    def worker(self, mode, arm):
        with patch.object(w.WorkerDecoder, "_launch", staticmethod(launch)):
            worker = w.WorkerDecoder(Source(mode), diagnostic_arm=arm)
        self.addCleanup(worker.close)
        return worker

    def test_default_and_forbidden_stage(self):
        self.assertEqual(w.COMMIT_BYTES, 536870912)
        job = w.DecoderJob()
        try:
            self.assertEqual(job.snapshot()["process_commit_limit"], 536870912)
            self.assertEqual(job.snapshot()["job_commit_limit"], 536870912)
        finally:
            job.close()
        with self.assertRaises(w.WorkerError) as exc:
            w.arm_limit("COMMIT_2048")
        self.assertEqual(exc.exception.code, "DECODER_ARM_INVALID")

    def test_two_native_job_bindings(self):
        for arm, limit in (("COMMIT_512",536870912),("COMMIT_1024",1073741824)):
            with self.subTest(arm=arm):
                worker = self.worker("success", arm)
                self.assertTrue(worker.resources["job_confirmed_before_media"])
                self.assertEqual(worker.job.snapshot()["process_commit_limit"],limit)
                self.assertEqual(worker.job.snapshot()["job_commit_limit"],limit)
                pcm, rgb, _, _ = worker.select(1,0)
                self.assertEqual((pcm.nbytes,rgb.nbytes),(19200,6220800))
                del pcm, rgb
                worker.close()
                self.assertEqual(worker.resources["native_logs"][0]["message"],"bound neutral native error")
                self.assertFalse(worker.resources["native_log_overflow"])

    def test_original_native_exception_and_message(self):
        worker = self.worker("error","COMMIT_512")
        with self.assertRaises(w.WorkerError):
            worker.select(1,0)
        worker.close()
        original = worker.resources["original_worker_error"]
        self.assertEqual(original["exception_type"],"InvalidDataError")
        self.assertEqual(original["native_exception"]["strerror"],"neutral invalid data")
        self.assertEqual(worker.native_logs[0]["component"],"libav.neutral")

    def test_abrupt_exit_preserves_native_log(self):
        worker = self.worker("abrupt","COMMIT_512")
        with self.assertRaises(w.WorkerError):
            worker.select(1,0)
        worker.close()
        self.assertIsNone(worker.resources["original_worker_error"])
        self.assertEqual(worker.last_confirmed_phase["operation"],"neutral_native_error")
        self.assertEqual(len(worker.native_logs),1)

    def test_native_log_bound_is_explicit(self):
        worker = self.worker("overflow","COMMIT_512")
        with self.assertRaises(w.WorkerError) as exc:
            worker.select(1,0)
        worker.close()
        self.assertEqual(exc.exception.code,"DECODER_NATIVE_LOG_LIMIT")
        self.assertTrue(worker.resources["native_log_overflow"])
        self.assertEqual(len(worker.native_logs),32)
        self.assertLessEqual(worker.native_log_bytes,32768)

    def test_job_message_kinds_remain_distinct(self):
        job = w.DecoderJob()
        try:
            job.limit_messages.update((9,10))
            self.assertEqual(job.snapshot()["memory_limit_messages"],[9,10])
        finally:
            job.close()
