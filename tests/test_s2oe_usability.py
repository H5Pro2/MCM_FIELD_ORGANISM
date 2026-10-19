"""New closure/UI checks only; no real media, decoder, or memory calls."""
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from tools import _s2oe_local_player as ui

OUT=ui.b.ROOT/"reports/s2oe/media-player-usability-20260912-01"


class FakeSession:
    def __init__(self,binding,code=None):
        self.binding,self.n,self.code=binding,0,code
        self.closed=False
        self.publications=0
        binding.output.mkdir()

    def next(self):
        if self.code and self.n==2:raise ui.PlayerError(self.code)
        self.n+=1
        return ui.b.canonical(dict(perception_status="RECORDED",memory_status="COMMITTED",
            context_status="NOT_REQUESTED",hypothesis=None,error_codes=[]))

    def stop(self):
        value=dict(status="RECORDING_COMPLETE" if self.n==24 else "NOT_EVALUABLE",
            failure=None if self.n==24 else dict(code="INCOMPLETE"))
        if not self.closed:
            ui.s.prior.save(self.binding.output/"record.json",value)
            self.publications+=1
            self.closed=True
        return ui.b.canonical(value)


class UsabilityTests(unittest.TestCase):
    def execute(self,name,reason=None,code=None,unknown=False):
        binding=SimpleNamespace(source=Path("neutral.mp4"),output=OUT/("fixture-"+name),inv={},
            manifest=SimpleNamespace(events=ui.p.sequence()))
        player=ui.Player(binding)
        player.used=True
        player.state["phase"]="RUNNING"
        session=FakeSession(binding,code)
        checks=[]
        def verify(path,inv):
            checks.append(str(path))
            value=ui.s.read_json(path/"record.json")
            return dict(status=value["status"],evaluation_allowed=value["status"]=="RECORDING_COMPLETE")
        def after():
            if player.state["completed"]==8:
                if reason:player.stop(reason)
                elif unknown:player.stop_event.set()
        with patch.object(player,"_open_session",return_value=session),patch.object(player,"_after_event",after),\
                patch.object(ui.verification,"verify_once",side_effect=verify),\
                patch.object(ui.m,"NativeRuntime",side_effect=AssertionError("RUNTIME_FORBIDDEN")):
            player._run()
            snapshot=player.status()
            player.stop("SERVER_SHUTDOWN")
            player._verify()
            self.assertEqual(snapshot,player.status())
        self.assertEqual(len(checks),1)
        self.assertEqual(session.publications,1)
        self.assertFalse(ui.p.MAIN_GATE)
        close=ui.s.read_json(binding.output/"player-close.json")
        self.assertLessEqual((binding.output/"player-close.json").stat().st_size,1024)
        return player,close

    def test_user_stop(self):
        player,close=self.execute("user",reason="USER_STOP")
        self.assertEqual((close["closure_cause"],close["stop_trigger"]),("USER_STOP","USER_STOP"))
        self.assertEqual((close["completed"],close["session_failure"]),(8,"INCOMPLETE"))
        self.assertEqual(player.state["last_processed"]["ordinal"],8)

    def test_server_shutdown(self):
        _,close=self.execute("server",reason="SERVER_SHUTDOWN")
        self.assertEqual(close["closure_cause"],"SERVER_SHUTDOWN")

    def test_source_end(self):
        _,close=self.execute("source",code="FRAME_COVERAGE_MISSING")
        self.assertEqual(close["closure_cause"],"SOURCE_END")
        self.assertEqual(close["error"],"FRAME_COVERAGE_MISSING")

    def test_technical_error(self):
        _,close=self.execute("technical",code="NEUTRAL_TECHNICAL_ERROR")
        self.assertEqual(close["closure_cause"],"TECHNICAL_ERROR")
        self.assertEqual(close["error"],"NEUTRAL_TECHNICAL_ERROR")

    def test_unknown_is_not_user_stop(self):
        _,close=self.execute("unknown",unknown=True)
        self.assertEqual(close["closure_cause"],"UNKNOWN")
        self.assertIsNone(close["stop_trigger"])

    def test_complete(self):
        _,close=self.execute("complete")
        self.assertEqual((close["phase"],close["closure_cause"]),("RECORDING_COMPLETE","COMPLETED"))

    def test_dom_projection(self):
        value=subprocess.run(["node","tests/s2oe_usability_dom.js"],cwd=ui.b.ROOT,
            capture_output=True,text=True,timeout=10,check=True)
        self.assertEqual(value.stdout.strip(),"DOM_OK")

    def test_invalid_stop_cause(self):
        player=ui.Player(SimpleNamespace(source=Path("neutral.mp4")))
        with self.assertRaises(ui.PlayerError) as exc:player.stop("INVENTED")
        self.assertEqual(exc.exception.code,"PLAYER_STOP_REASON_INVALID")
