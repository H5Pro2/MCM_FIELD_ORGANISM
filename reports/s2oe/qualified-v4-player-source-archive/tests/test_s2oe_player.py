"""Focused new player/budget tests, not a repetition of worker qualification."""
from dataclasses import replace
import hashlib
import http.client
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
import time
import unittest
from unittest.mock import patch

from tools import _s2oe_local_player as ui
from tools import _s2oe_decoder_worker as worker

m,p,b,s=ui.m,ui.p,ui.b,ui.s
OUT=Path(os.environ["MEDIA_PLAYER_QUAL_OUT"])
INPUT=b.ROOT/"sources/s2oe-player-neutral"/m.QUAL_ID


def fixture(name):
    video=INPUT/"neutral-preview.mp4"
    manifest=p.build("player-neutral-"+name,p.Source(str(video),s.sha(video.read_bytes()),video.stat().st_size),b.digest(m.inventory()))
    return ui.Binding({}, {},manifest,OUT/("fake-"+name),video,"0"*64,"1"*64,OUT/(name+".used"),"2"*64)


def authorize(binding):
    value=dict(version=ui.VERSION,authorized=True,single_use=True,run_id=binding.manifest.run_id,
        settings_sha256=binding.settings_sha256,common_sha256=binding.common_sha256,
        qualification_sha256=binding.qualification_sha256)
    path=OUT/(binding.manifest.run_id+"-authorization.json")
    s.prior.save(path,value)
    return path,s.sha(path.read_bytes())


class FakeSession:
    def __init__(self,binding):
        self.binding,self.n=binding,0
        self.closed=False
        self.lock=threading.Lock()
        binding.output.mkdir()
    def next(self):
        self.n+=1
        return b.canonical(dict(perception_status="ACCEPTED",memory_status="READ_ONLY_UNCHANGED"
            if self.n in (13,14,21,22) else "UPDATED",context_status="ABSTAIN_NO_APPLICABLE_CONTEXT",
            hypothesis=None,error_codes=[]))
    def stop(self):
        value=dict(fixture=True,status="RECORDING_COMPLETE" if self.n==24 else "NOT_EVALUABLE")
        with self.lock:
            if not self.closed:
                s.prior.save(self.binding.output/"record.json",value)
                self.closed=True
        return b.canonical(value)


def fake_verify(path,inv):
    value=s.read_json(path/"record.json")
    return dict(status=value["status"],evaluation_allowed=value["status"]=="RECORDING_COMPLETE")


class PlayerQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import numpy as np
        from tools._s2oe_media_decoder import load_av
        av=load_av()
        INPUT.mkdir(parents=True,exist_ok=True)
        path=INPUT/"neutral-preview.mp4"
        with av.open(str(path),"w") as container:
            stream=container.add_stream("libx264",rate=10)
            stream.width,stream.height,stream.pix_fmt=320,180,"yuv420p"
            for n in range(20):
                pixels=np.full((180,320,3),(35,70,95),np.uint8)
                pixels[:,30+n*8:65+n*8]=(55,180,150)
                for packet in stream.encode(av.VideoFrame.from_ndarray(pixels,format="rgb24")):
                    container.mux(packet)
            for packet in stream.encode():
                container.mux(packet)

    def error(self,code,call):
        with self.assertRaises(ui.PlayerError) as found:
            call()
        self.assertEqual(found.exception.code,code)

    def test_01_private_metadata_limits_everywhere(self):
        self.assertEqual(p.SESSION_LIMITS["metadata"],98304)
        self.assertEqual(p.QUAL_LIMITS["metadata"],98304)
        self.assertEqual(b.LIMITS["metadata"],65536)
        from reports.qualify_media_player_once import common_fixture
        from tools._s2oc_shared_verification import synthetic_forms
        common,_=common_fixture()
        for n in (0,12,24):
            for pair in synthetic_forms(common,n):
                size=p.ledger(*pair,common)["totals"]["metadata"]
                for over in (0,1):
                    row=p.ledger(*pair,common,attachments=(("metadata","@edge",98304-size+over),))
                    if over:
                        with self.assertRaises(s.budget.BudgetError):
                            p.enforce({"edge":row},"EVIDENCE",n,n)
                    else:
                        p.enforce({"edge":row},"CLOSE",n,n)

    def test_02_authorization_required_and_single_use(self):
        bind=fixture("authorization")
        player=ui.Player(bind)
        self.error("PLAYER_AUTHORIZATION_REQUIRED",player.start)
        self.assertFalse(bind.claim.exists())
        path,digest=authorize(bind)
        player.authorization,player.authorization_sha256=path,digest
        with patch.object(player,"_open_session",return_value=FakeSession.__new__(FakeSession)):
            # Exercise the authorization claim separately, without pretending this is a runtime.
            player._authorize()
        self.error("PLAYER_AUTHORIZATION_USED",player._authorize)
        self.assertFalse(p.MAIN_GATE)

    def test_03_projection_is_independent_and_immutable(self):
        raw=b.canonical(dict(perception_status="ACCEPTED",memory_status="UNCHANGED",
            context_status="ABSTAIN_TIE",hypothesis=None,error_codes=["X"]))
        view=ui.projection(raw)
        self.assertEqual(view,dict(perception="ACCEPTED",memory="UNCHANGED",context="ABSTAIN_TIE",
            hypothesis=False,hypothesis_digest=None,errors=["X"]))
        view["errors"].append("MUTATION")
        self.assertEqual(json.loads(raw)["error_codes"],["X"])

    def test_04_complete_control_loop_and_one_verification(self):
        bind=fixture("complete");player=ui.Player(bind,*authorize(bind))
        with patch.object(player,"_open_session",side_effect=lambda:FakeSession(bind)),patch.object(
                ui.verification,"verify_once",side_effect=fake_verify) as verifier:
            player.start();player.thread.join(10)
            self.assertFalse(player.thread.is_alive())
            self.assertEqual(json.loads(player.status())["completed"],24)
            self.assertEqual(json.loads(player.status())["phase"],"RECORDING_COMPLETE")
            player.stop();player.stop()
            self.assertEqual(verifier.call_count,1)
            self.error("PLAYER_ALREADY_USED",player.start)

    def test_05_early_stop_and_primary_error(self):
        bind=fixture("early");player=ui.Player(bind,*authorize(bind))
        entered=threading.Event()
        def pause():
            entered.set();player.stop_event.wait(5)
        with patch.object(player,"_open_session",side_effect=lambda:FakeSession(bind)),patch.object(
                player,"_after_event",side_effect=pause),patch.object(ui.verification,"verify_once",side_effect=fake_verify) as verifier:
            player.start();self.assertTrue(entered.wait(5));player.stop()
            self.assertEqual(json.loads(player.status())["phase"],"NOT_EVALUABLE")
            self.assertEqual(verifier.call_count,1)
        other=fixture("error");player=ui.Player(other,*authorize(other))
        with patch.object(player,"_open_session",side_effect=ui.PlayerError("NEUTRAL_OPEN_ERROR")):
            player.start();player.thread.join(5)
        self.assertEqual(json.loads(player.status())["error"],"NEUTRAL_OPEN_ERROR")
        self.assertFalse(p.MAIN_GATE)

    def test_06_http_origin_token_and_fixed_media(self):
        player=ui.Player(fixture("http"))
        server=ui.serve(player)
        thread=threading.Thread(target=server.serve_forever);thread.start()
        try:
            connection=http.client.HTTPConnection("127.0.0.1",server.server_port,timeout=5)
            connection.request("GET","/");html=connection.getresponse().read().decode()
            token=re.search("const token='([0-9a-f]+)'",html)[1]
            connection.request("POST","/api/start",headers={"X-MCM-Token":token,"Content-Length":"0"})
            response=connection.getresponse();self.assertEqual(response.status,409);response.read()
            connection.request("GET","/api/status",headers={"X-MCM-Token":token,"Origin":"https://example.invalid"})
            response=connection.getresponse();self.assertEqual(response.status,403);response.read()
            connection.request("GET","/media?token="+token,headers={"Range":"bytes=0-31"})
            response=connection.getresponse();self.assertEqual(response.status,206);self.assertEqual(len(response.read()),32)
            connection.request("GET","/arbitrary.mp4")
            response=connection.getresponse();self.assertEqual(response.status,404);response.read()
            self.assertFalse(player.used)
        finally:
            server.shutdown();server.server_close();thread.join()

    def test_07_preview_hash_and_read_account(self):
        bind=fixture("preview")
        player=ui.Player(bind)
        raw=player.preview(0,31)
        self.assertEqual(len(raw),32)
        self.assertEqual(player.preview_bytes,bind.source.stat().st_size+32)
        wrong=replace(bind,manifest=replace(bind.manifest,source=replace(bind.manifest.source,sha256="0"*64)))
        self.error("PLAYER_MEDIA_HASH_INVALID",lambda:ui.Player(wrong).preview(0,31))

    def test_08_browser_desktop_mobile_and_neutral_video(self):
        sys.path.append(str(b.ROOT/".venv/Lib/site-packages"))
        from playwright.sync_api import sync_playwright
        player=ui.Player(fixture("browser"));server=ui.serve(player)
        thread=threading.Thread(target=server.serve_forever);thread.start()
        try:
            with sync_playwright() as api:
                browser=api.chromium.launch(headless=True)
                page=browser.new_page(viewport={"width":900,"height":680},device_scale_factor=1)
                errors=[];page.on("pageerror",lambda e:errors.append(str(e)))
                page.goto(f"http://127.0.0.1:{server.server_port}/")
                page.wait_for_function("document.getElementById('phase').textContent==='AUTHORIZATION_REQUIRED'")
                page.locator("video").evaluate("v=>v.play()")
                page.wait_for_function("document.querySelector('video').videoWidth===320")
                page.locator("video").evaluate("v=>v.pause()")
                self.assertTrue(page.get_by_role("button",name="Start",exact=True).is_disabled())
                for label,view in (("desktop",{"width":900,"height":680}),("mobile",{"width":390,"height":844})):
                    page.set_viewport_size(view)
                    self.assertTrue(page.evaluate("document.documentElement.scrollWidth<=innerWidth"))
                    page.screenshot(path=str(OUT/(label+".jpg")),full_page=True,type="jpeg",quality=40)
                self.assertEqual(errors,[])
                browser.close()
        finally:
            server.shutdown();server.server_close();thread.join()

    def test_09_native_player_stop_after_one_event(self):
        from reports.qualify_media_player_once import common_fixture
        source=b.ROOT/"sources/s2oe-worker-neutral"/m.QUAL_ID/"player-native.bin"
        source.parent.mkdir(parents=True,exist_ok=True)
        with source.open("xb") as stream:stream.write(b"N"*32)
        common,inv=common_fixture(p.Source(str(source),s.sha(source.read_bytes()),32))
        manifest=p.decode(common["manifest"])
        bind=ui.Binding(common,inv,manifest,OUT/"native-player",source,"0"*64,"1"*64,OUT/"native.used","2"*64)
        player=ui.Player(bind,*authorize(bind));entered=threading.Event()
        def open_native():
            def launch(command,**kwargs):
                return subprocess.Popen([command[0],str(b.ROOT/"tests/s2oe_neutral_worker.py"),"--worker"],**kwargs)
            p.MAIN_GATE=True
            with patch.object(worker.WorkerDecoder,"_launch",staticmethod(launch)):
                return m.start(manifest,common,inv,bind.output,neutral=True)
        def pause():
            entered.set();player.stop_event.wait(10)
        with patch.object(player,"_open_session",side_effect=open_native),patch.object(player,"_after_event",side_effect=pause):
            player.start();self.assertTrue(entered.wait(20));player.stop()
        self.assertFalse(player.thread.is_alive())
        self.assertEqual(player.state["completed"],1)
        self.assertEqual(player.state["phase"],"NOT_EVALUABLE")
        self.assertTrue(player.verified)
        self.assertFalse(player.state["verification"]["evaluation_allowed"])
        self.assertFalse(p.MAIN_GATE)

    def test_10_binding_hash_and_nonselected_source_rejected(self):
        from reports.qualify_media_player_once import common_fixture
        common,_=common_fixture()
        path=OUT/"loader-common.json";s.prior.save(path,dict(manifest=common["manifest"]))
        settings=dict(version=ui.VERSION,status="BOUND_AWAITING_AUTHORIZATION",
            common=dict(path=path.relative_to(b.ROOT).as_posix(),sha256=s.sha(path.read_bytes())),
            budget={},output="reports/s2oe/unused-player")
        target=OUT/"loader-settings.json";s.prior.save(target,settings)
        self.error("PLAYER_DIGEST_INVALID",lambda:ui.load_binding(target,"0"*64))
        # Isolate the source allowlist. Full common checking is reached in test 09.
        with patch.object(m,"check_common",return_value=None):
            self.error("PLAYER_SOURCE_NOT_SELECTED",lambda:ui.load_binding(target,s.sha(target.read_bytes())))


if __name__=="__main__":
    unittest.main()
