"""Only terminal controls: synthetic immutable receipts, no memory or payloads."""
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from tools import _s2od_private_terminal_client as c


RAW = c.b.canonical(dict(perception_status="CONTACTS_ACCEPTED", memory_status="READ_ONLY",
    context_status="ABSTAIN_NO_APPLICABLE_CONTEXT", hypothesis=None, error_codes=[]))


class FakeSession:
    def __init__(self, events):
        self.events, self.seen = events, []
        self.closes = 0
        self.field = 0
        self.failure = None
        self.terminal = None

    def process(self, event):
        assert event is self.events[len(self.seen)]
        self.seen.append(event)
        self.field += 1
        if self.failure:
            raise self.failure
        return RAW

    def close(self):
        if self.terminal is None:
            self.closes += 1
            complete = len(self.seen) == len(self.events) and self.failure is None
            self.terminal = c.b.canonical(dict(status="RECORDING_COMPLETE" if complete else "NOT_EVALUABLE",
                failure=None if complete else dict(code="INCOMPLETE" if self.failure is None else self.failure.code)))
        return self.terminal


class TerminalTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.events = tuple(SimpleNamespace(ordinal=n) for n in range(1,4))
        self.fake = FakeSession(self.events)
        self.common = {"neutral":True}
        self.out = Path(self.temp.name)/"run"
        self.patches = [
            patch.object(c.s, "read_json", return_value=self.common),
            patch.object(c.s, "validate_common", return_value=SimpleNamespace(events=self.events)),
            patch.object(c, "validate_client"),
            patch.object(c.entry, "open_session", side_effect=self.open_fake),
            patch.object(c.verification, "verify_once", return_value=({"evaluation_allowed":False},{})),
            patch.object(c.b, "read_payload", side_effect=AssertionError("PAYLOAD_FORBIDDEN")),
            patch.object(c.b, "Materializer", side_effect=AssertionError("MATERIALIZER_FORBIDDEN")),
            patch.object(c.b, "CallerRuntime", side_effect=AssertionError("RUNTIME_FORBIDDEN"))]
        self.mocks = [p.start() for p in self.patches]
        self.addCleanup(self.cleanup_patches)
        self.client = self.make()

    def cleanup_patches(self):
        c.entry.MAIN_GATE = False
        for p in reversed(self.patches): p.stop()

    def make(self):
        return c.TerminalClient("neutral.json",c.s.sha(c.b.canonical(self.common)),"inventory.json",self.out)

    def open_fake(self,*args,**kwargs):
        if self.out.exists(): raise c.ClientError("SESSION_OUTPUT_CONFLICT")
        self.out.mkdir()
        return self.fake

    def opened(self):
        c.entry.MAIN_GATE = True
        self.client.command("open")

    def error(self, code, fn):
        with self.assertRaises(c.ClientError) as found: fn()
        self.assertEqual(found.exception.code,code)

    def test_01_gate(self):
        self.error("MAIN_GATE_CLOSED",lambda:self.client.command("open"))
        self.mocks[3].assert_not_called()

    def test_02_steps(self):
        self.opened()
        self.assertFalse(c.entry.MAIN_GATE)
        for n in range(1,4):
            self.assertEqual(json.loads(self.client.command("next"))["progress"],f"{n}/3")
        self.assertEqual(self.fake.seen,list(self.events))
        self.error("CLIENT_EXHAUSTED",lambda:self.client.command("next"))

    def test_03_no_automatic_step(self):
        self.opened()
        self.client.command("status")
        self.assertEqual(self.fake.seen,[])
        self.error("CLIENT_COMMAND_INVALID",lambda:self.client.command("next 2"))
        self.assertEqual(self.fake.seen,[])

    def test_04_display_immutable(self):
        before = bytes(RAW)
        self.assertEqual(c.render_step(RAW,1,3),c.render_step(RAW,1,3))
        self.assertEqual(RAW,before)
        self.assertIsNone(json.loads(c.render_step(RAW,1,3))["hypothesis"])

    def test_05_hypothesis(self):
        value = json.loads(RAW)
        value["hypothesis"]={"area":"A_RECENT","values":[0.25]}
        before = deepcopy(value)
        raw = c.b.canonical(value)
        self.assertEqual(json.loads(c.render_step(raw,1,3))["hypothesis"],value["hypothesis"])
        self.assertEqual(value,before)

    def test_06_complete(self):
        self.opened()
        for _ in self.events: self.client.command("next")
        self.mocks[4].return_value=({"evaluation_allowed":True},{})
        result=json.loads(self.client.command("close"))
        self.assertEqual(result["status"],"RECORDING_COMPLETE")
        self.assertTrue(result["evaluation_allowed"])
        self.assertEqual(self.fake.closes,1)
        self.mocks[4].assert_called_once()

    def test_07_early_close(self):
        self.opened(); self.client.command("next")
        result=json.loads(self.client.command("close"))
        self.assertEqual(result["status"],"NOT_EVALUABLE")
        self.assertEqual(result["failure"]["code"],"INCOMPLETE")
        self.assertFalse(result["evaluation_allowed"])

    def test_08_primary_failure(self):
        self.opened()
        primary=c.ClientError("SYNTHETIC_FORMATION_ERROR")
        self.fake.failure=primary
        with self.assertRaises(c.ClientError) as found: self.client.command("next")
        self.assertIs(found.exception,primary)
        self.assertEqual(self.fake.field,1)
        self.assertTrue(self.client.ended)
        self.assertEqual(self.fake.closes,1)
        self.mocks[4].assert_called_once()

    def test_09_verification_failure(self):
        self.opened(); self.fake.failure=c.ClientError("PRIMARY")
        self.mocks[4].side_effect=c.ClientError("VERIFY_FAILED")
        self.error("PRIMARY",lambda:self.client.command("next"))
        self.assertTrue(self.client.verified)
        self.error("CLIENT_NOT_OPEN",lambda:self.client.command("close"))
        self.mocks[4].assert_called_once()

    def test_10_consumed_client(self):
        self.opened(); self.client.command("abort")
        c.entry.MAIN_GATE=True
        self.error("CLIENT_ALREADY_USED",lambda:self.client.command("open"))
        self.error("CLIENT_NOT_OPEN",lambda:self.client.command("next"))
        self.assertEqual(self.fake.closes,1)

    def test_11_consumed_directory(self):
        self.opened(); self.client.command("close")
        other=self.make(); c.entry.MAIN_GATE=True
        self.error("SESSION_OUTPUT_CONFLICT",lambda:other.command("open"))
        self.assertFalse(c.entry.MAIN_GATE)

    def test_12_binding_rejection(self):
        self.mocks[1].side_effect=c.ClientError("SOURCE_CHANGED")
        self.error("SOURCE_CHANGED",self.make)
        self.mocks[3].assert_not_called()

    def test_13_pin(self):
        self.error("CLIENT_PIN_INVALID",lambda:c.TerminalClient("neutral.json","0"*64,"inv",self.out))

    def test_14_interaction(self):
        c.entry.MAIN_GATE=True
        commands=iter(("open","next","status","abort"))
        shown=[]
        self.client.interact(lambda prompt:next(commands),shown.append)
        self.assertEqual(len(self.fake.seen),1)
        self.assertEqual(self.fake.closes,1)
        self.assertFalse(c.entry.MAIN_GATE)
        self.assertIn("NOT_EVALUABLE",shown[-1])

    def test_15_display_limit(self):
        self.error("CLIENT_RESULT_INVALID",lambda:c.render_step(b"x"*16385,1,3))

    def test_16_qualification_refs(self):
        # Exercise the real client admission, not the constructor's neutral stub.
        self.patches[2].stop()
        with patch.object(c,"sources",return_value={"client.py":["a"*64,12]}):
            self.error("CLIENT_SOURCE_UNBOUND",lambda:c.validate_client({"references":[]},{}))


if __name__ == "__main__":
    unittest.main()
