"""One focused replay suite, not the historical qualification series."""
from copy import deepcopy
from fractions import Fraction
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

from tools import _media_restart_work as w
from tools import _media_replay_protocol as r
from tools import _media_restart_evidence as e

OUT = Path(os.environ["MEDIA_REPLAY_QUAL_OUT"])


class Replay(unittest.TestCase):
    def fixture(self, target=19):
        source = NS(path="neutral", sha256="1"*64, size=8192, video_time_base=(1, 30000),
                    audio_time_base=(1, 48000), frame_rate=(30000, 1001))
        initial = w.Work(source.size).payload()
        clock = [0.0]
        client = r.Client(source, target, initial, clock=lambda: clock[0])
        return client, clock

    def reply(self, client, n, sequence):
        account = deepcopy(client.last)
        part = "replay" if n < client.target else "regular"
        for k in w.KEYS:
            account["parts"][part][k] += 1
            account["totals"][k] += 1
        center = Fraction(28*n+1, 20)
        pts = int(center*30000)//1001*1001
        return dict(sequence=sequence, restart_work=account,
            replay_receipt=r.receipt(client.source, n, part if part == "replay" else "select", pts, pts+1001))

    def error(self, code, call):
        with self.assertRaises(r.ReplayError) as raised:
            call()
        self.assertEqual(raised.exception.code, code)

    def test_01_full_sections_and_offline(self):
        client, clock = self.fixture()
        proofs = []
        for n in range(20):
            client.before("replay" if n < 19 else "select", n, n+2)
            clock[0] += 1
            proofs.append(client.accept(self.reply(client, n, n+2)))
        self.assertTrue(r.verify(proofs, client.source, 19, client.initial["prior"], client.last, client.summary()))
        self.assertTrue(client.complete)
        self.assertEqual(client.requests, 20)

    def test_02_missing_confirmation(self):
        client, _ = self.fixture()
        client.before("replay", 0, 2)
        self.error("REPLAY_REQUEST_STATE", lambda: client.before("replay", 1, 3))

    def test_03_duplicate_confirmation(self):
        client, _ = self.fixture()
        client.before("replay", 0, 2)
        reply = self.reply(client, 0, 2)
        client.accept(reply)
        self.error("REPLAY_UNEXPECTED_CONFIRMATION", lambda: client.accept(reply))

    def test_04_regressive_or_foreign_sequence(self):
        for sequence in (1, 3):
            with self.subTest(sequence=sequence):
                client, _ = self.fixture()
                client.before("replay", 0, 2)
                self.error("REPLAY_SEQUENCE", lambda: client.accept(self.reply(client, 0, sequence)))

    def test_05_source_and_time_manipulation(self):
        for key, value in (("source", "0"*64), ("audio_start", 1), ("window", 1), ("video_time_base", [1, 30])):
            with self.subTest(key=key):
                client, _ = self.fixture()
                client.before("replay", 0, 2)
                reply = self.reply(client, 0, 2)
                reply["replay_receipt"][key] = value
                self.error("REPLAY_SOURCE_TIME_BINDING", lambda: client.accept(reply))

    def test_06_target_before_replay(self):
        client, _ = self.fixture()
        self.error("REPLAY_ORDER", lambda: client.before("select", 19, 2))
        d = w.Decoder.__new__(w.Decoder)
        d.replayed, d.next_window, d.replay_next = False, 19, 0
        with self.assertRaises(w.RestartError) as raised:
            d.select(1, 19)
        self.assertEqual(raised.exception.code, "RESTART_REPLAY_INCOMPLETE")

    def test_07_cumulative_budget_boundary(self):
        for key, cap in w.limits(8192).items():
            with self.subTest(key=key):
                client, _ = self.fixture()
                client.before("replay", 0, 2)
                reply = self.reply(client, 0, 2)
                reply["restart_work"]["parts"]["replay"][key] = cap
                reply["restart_work"]["totals"][key] = cap
                r.check_work(reply["restart_work"], client.initial["prior"], client.last, client.initial["limits"])
                reply["restart_work"]["parts"]["replay"][key] += 1
                reply["restart_work"]["totals"][key] += 1
                self.error("REPLAY_WORK_LIMIT", lambda: client.accept(reply))

    def test_08_regressive_counters(self):
        client, _ = self.fixture()
        client.before("replay", 0, 2)
        client.accept(self.reply(client, 0, 2))
        client.before("replay", 1, 3)
        reply = self.reply(client, 1, 3)
        reply["restart_work"]["parts"]["replay"]["packets"] = 0
        reply["restart_work"]["totals"]["packets"] = 0
        self.error("REPLAY_COUNTER_REGRESSION", lambda: client.accept(reply))

    def test_09_absolute_deadline_between_sections(self):
        client, clock = self.fixture()
        client.before("replay", 0, 2)
        client.accept(self.reply(client, 0, 2))
        clock[0] = 600.0
        self.error("REPLAY_TOTAL_TIMEOUT", lambda: client.before("replay", 1, 3))
        client.abort()
        self.assertFalse(client.unknown)
        self.assertEqual(client.confirmed, 1)

    def test_10_timeout_inside_section(self):
        client, clock = self.fixture()
        client.before("replay", 0, 2)
        client.accept(self.reply(client, 0, 2))
        saved = deepcopy(client.last)
        client.before("replay", 1, 3)
        clock[0] = 31
        client.abort()
        self.assertTrue(client.unknown)
        self.assertEqual(client.last, saved)
        self.assertEqual(client.confirmed, 1)

    def test_11_deadline_not_renewable(self):
        client, clock = self.fixture()
        self.assertEqual(client.before("replay", 0, 2), 30.0)
        client.accept(self.reply(client, 0, 2))
        clock[0] = 599.0
        self.assertEqual(client.before("replay", 1, 3), 600.0)
        clock[0] = 600.001
        self.error("REPLAY_TOTAL_TIMEOUT", lambda: client.accept(self.reply(client, 1, 3)))

    def test_12_native_rpc_deadline_hook(self):
        d = w.WorkerDecoder.__new__(w.WorkerDecoder)
        with patch.object(w.worker.time, "monotonic", return_value=100):
            d._restore_deadline = None
            self.assertEqual(d._request_deadline(), 130)
            d._restore_deadline = 110
            self.assertEqual(d._request_deadline(), 110)
        self.assertEqual(w.worker.REQUEST_SECONDS, 30.0)
        self.assertEqual(w.worker.STOP_SECONDS, 5.0)

    def test_13_receipt_immutable_and_message_size(self):
        client, _ = self.fixture()
        client.before("replay", 0, 2)
        reply = self.reply(client, 0, 2)
        proof = client.accept(reply)
        proof["work"]["totals"]["packets"] = 999
        reply["restart_work"]["totals"]["packets"] = 888
        self.assertEqual(client.last["totals"]["packets"], 1)
        self.assertLess(len(w.worker.encode(reply)), w.worker.MESSAGE_BYTES)

    def test_14_worker_one_window_release(self):
        d = w.Decoder.__new__(w.Decoder)
        client, _ = self.fixture()
        d.source, d.work = client.source, w.Work(8192)
        d.replayed, d.replay_next, d.next_window = False, 0, 19
        with patch.object(w.old.Decoder, "select", return_value=(None, None, 1001, 2002)) as select, \
             patch.object(w.old.Decoder, "release") as release:
            d.replay_one(0)
            select.assert_called_once_with(1, 0)
            release.assert_called_once_with()
            self.assertEqual(d.replay_next, 1)
            with self.assertRaises(w.RestartError):
                d.replay_one(0)

    def test_15_failure_account_not_reset(self):
        client, _ = self.fixture()
        client.before("replay", 0, 2)
        client.accept(self.reply(client, 0, 2))
        d = w.WorkerDecoder.__new__(w.WorkerDecoder)
        d.replay_client, d._sequence = client, 2
        d.work_account = deepcopy(client.last)
        d.resources = {"restart_work": deepcopy(client.last)}
        with patch.object(w.worker.WorkerDecoder, "_rpc", side_effect=w.worker.WorkerError("DECODER_TIMEOUT")):
            with self.assertRaises(w.worker.WorkerError):
                d._rpc(dict(op="replay", window=1))
        self.assertEqual(d.resources["restart_work"]["totals"]["packets"], 1)
        self.assertTrue(d.resources["restore_progress"]["unconfirmed_work_unknown"])
        self.assertFalse(d.resources["frame_evidence_complete"])

    def test_16_bounded_publication_and_failure_form(self):
        q = json.loads((OUT/"preregistration.json").read_bytes())
        plan = e.publication.Plan.bind(q["publication_plan"])
        plan.offer("restore20/replay-19.json", "metadata", 4096)
        with self.assertRaises(e.publication.PlanError):
            plan.offer("restore20/replay-19.json", "metadata", 4097)
        old = json.loads((e.c.b.ROOT/"reports/media-restart-real-20260913-02/restore20/failure.json").read_bytes())
        client, _ = self.fixture()
        client.before("replay", 0, 2)
        client.abort()
        old["value"]["failure"]["resources"]["restore_progress"] = client.summary()
        self.assertLessEqual(len(e.canonical(old)), e.FAILURE_BYTES)
        self.assertEqual(e.FAILURE_BYTES, 4096)

    def test_17_offline_missing_or_reordered(self):
        client, _ = self.fixture(1)
        proofs = []
        for n in range(2):
            client.before("replay" if n == 0 else "select", n, n+2)
            proofs.append(client.accept(self.reply(client, n, n+2)))
        self.error("REPLAY_PROOF_COUNT", lambda: r.verify(proofs[:1], client.source, 1,
            client.initial["prior"], client.last, client.summary()))
        self.error("REPLAY_SOURCE_TIME_BINDING", lambda: r.verify(list(reversed(proofs)), client.source, 1,
            client.initial["prior"], client.last, client.summary()))

    def test_18_available_reference_catalog(self):
        from reports import run_selected_media_restart_once as entry
        path = OUT/"neutral-catalog.json"
        path.write_bytes(e.canonical(dict(references=[dict(path="neutral", bytes=1, category="metadata", sha256="0"*64)])))
        catalog = dict(path=str(path.relative_to(entry.ROOT)), sha256=entry.identity(path)["sha256"])
        resolved = entry.reference_rows(dict(external=[], reference_catalogs=[catalog]))
        self.assertEqual(len(resolved), 2)
        self.assertEqual(resolved[1]["bytes"], path.stat().st_size)
        with self.assertRaises(w.RestartError) as caught:
            entry.reference_rows(dict(external=[], reference_catalogs=[{**catalog, "sha256": "f"*64}]))
        self.assertEqual(caught.exception.code, "REAL_BINDING_HASH")
        with self.assertRaises(FileNotFoundError):
            entry.reference_rows(dict(external=[], reference_catalogs=[{**catalog, "path": str(path.relative_to(entry.ROOT))+".missing"}]))

    def test_19_native_late_resume(self):
        for role in ("suspend19", "restore20"):
            with (OUT/(role+".stdout")).open("xb") as out, (OUT/(role+".stderr")).open("xb") as err:
                child = subprocess.run([sys.executable, "-B", "-m", "tests.media_replay_neutral", role],
                    cwd=e.c.b.ROOT, stdout=out, stderr=err, timeout=240)
            self.assertEqual(child.returncode, 0, role)
            q = json.loads((OUT/"preregistration.json").read_bytes())
            store = e.Store(OUT/"native", budget_profile=q["budget_profile"])
            proof = store.read(store.root/(role+"-process.json"))
            self.assertEqual(proof["phase"], "SUSPENDED" if role == "suspend19" else "RECORDING_COMPLETE")
            self.assertTrue(proof["closed"])
            self.assertFalse(proof["gate"])
            if role == "restore20":
                self.assertEqual(proof["confirmations"], list(range(20)))
                self.assertEqual(proof["completed"], 20)
                self.assertEqual(proof["replay_formation_calls"], 0)


if __name__ == "__main__":
    unittest.main()
