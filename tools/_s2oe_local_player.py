"""Loopback-only control surface for one explicitly bound finite media session."""
from dataclasses import dataclass
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import re
import secrets
import threading
from urllib.parse import urlsplit, parse_qs

from tools import _s2oe_media_session as m
from tools import _s2oe_media_verification as verification

p,b,s=m.p,m.b,m.s
VERSION="s2oe.local-player.v2-explicit-closure"
SOURCE=Path(r"C:\Users\TV\Downloads\17138816-uhd_3840_2160_30fps.mp4")
SOURCE_SHA="df0986f384e156c4dfec234e94b6f6baa3d0f8a9cfd7ba81f14aadf0313450aa"
HTML=b.ROOT/"tools/s2oe_player.html"
PREVIEW_LIMIT=12*83498438
RESPONSE_LIMIT=16384


class PlayerError(ValueError):
    def __init__(self,code):
        self.code=code
        super().__init__(code)


def need(ok,code):
    if not ok:
        raise PlayerError(code)


def read_bound(path,digest,limit):
    path=Path(path).resolve()
    try:
        need(path.is_relative_to(b.ROOT) and path.stat().st_size<=limit,"PLAYER_FILE_INVALID")
        raw=path.read_bytes()
    except OSError as exc:
        raise PlayerError("PLAYER_FILE_UNAVAILABLE") from exc
    need(hashlib.sha256(raw).hexdigest()==digest,"PLAYER_DIGEST_INVALID")
    try:
        value=json.loads(raw)
    except ValueError as exc:
        raise PlayerError("PLAYER_JSON_INVALID") from exc
    need(type(value) is dict,"PLAYER_JSON_INVALID")
    return value


@dataclass(frozen=True)
class Binding:
    common: dict
    inv: dict
    manifest: object
    output: Path
    source: Path
    common_sha256: str
    settings_sha256: str
    claim: Path
    qualification_sha256: str


def load_binding(path,digest):
    data=read_bound(path,digest,16384)
    need(set(data)=={"version","status","common","budget","output"},"PLAYER_BINDING_INVALID")
    need(data["version"]==VERSION and data["status"]=="BOUND_AWAITING_AUTHORIZATION","PLAYER_BINDING_INVALID")
    common=read_bound(b.ROOT/data["common"]["path"],data["common"]["sha256"],16384)
    manifest=p.decode(common["manifest"])
    inv=s.inventory()
    m.check_common(manifest,common,inv)
    need(manifest.source.path==str(SOURCE) and manifest.source.sha256==SOURCE_SHA
        and manifest.source.size==83498438,"PLAYER_SOURCE_NOT_SELECTED")
    full_file=manifest.schema==p.FULL_VERSION
    result=b.ROOT/"reports/s2oe"/(m.full.QUAL_ID if full_file else m.QUAL_ID)/"result.json"
    q=s.read_json(result)
    b.check_root(q,"result_digest")
    need(q["status"]=="QUALIFIED" and q["sources"]==m.inventory(full_file),"PLAYER_NOT_QUALIFIED")
    need(s.file_reference("metadata",result) in common["references"],"PLAYER_QUALIFICATION_UNBOUND")
    output=(b.ROOT/data["output"]).resolve()
    need(output.parent==b.ROOT/"reports/s2oe" and output.name==manifest.run_id,"PLAYER_OUTPUT_INVALID")
    need(not output.exists() and not output.with_suffix(".authorization-used").exists(),"PLAYER_OUTPUT_USED")
    budget=read_bound(b.ROOT/data["budget"]["path"],data["budget"]["sha256"],32768)
    need(budget["violations"]==[] and budget["run_id"]==manifest.run_id
        and budget["limits"]==p.SESSION_LIMITS,"PLAYER_BUDGET_INVALID")
    return Binding(common,inv,manifest,output,SOURCE,data["common"]["sha256"],digest,
        output.with_suffix(".authorization-used"),s.sha(result.read_bytes()))


def projection(raw):
    need(type(raw) is bytes and len(raw)<=16384,"PLAYER_STEP_INVALID")
    value=json.loads(raw)
    need(b.canonical(value)==raw,"PLAYER_STEP_INVALID")
    return dict(perception=value["perception_status"],memory=value["memory_status"],
        context=value["context_status"],hypothesis=value["hypothesis"] is not None,
        hypothesis_digest=None if value["hypothesis"] is None else b.digest(value["hypothesis"]),
        errors=value["error_codes"])


class Player:
    def __init__(self,binding,authorization=None,authorization_sha256=None):
        self.binding=binding
        self.authorization,self.authorization_sha256=authorization,authorization_sha256
        self.lock=threading.Lock()
        self.stop_event=threading.Event()
        self.session=self.thread=None
        self.used=self.verified=False
        self.preview_bytes=0
        self.preview_signature=None
        self.state=dict(phase="READY" if authorization else "AUTHORIZATION_REQUIRED",completed=0,
            total=len(binding.manifest.events),current=None,last=None,error=None,verification=None,
            last_processed=None,closure_cause="UNKNOWN",session_failure=None,stop_trigger=None,
            source=binding.source.name,interval="vollständige Datei" if binding.manifest.schema==p.FULL_VERSION else "00:00–00:05",
            full_file=binding.manifest.schema==p.FULL_VERSION,synchronized=False)

    def _authorize(self):
        need(self.authorization is not None,"PLAYER_AUTHORIZATION_REQUIRED")
        auth=read_bound(self.authorization,self.authorization_sha256,4096)
        need(auth==dict(version=VERSION,authorized=True,single_use=True,
            run_id=self.binding.manifest.run_id,settings_sha256=self.binding.settings_sha256,
            common_sha256=self.binding.common_sha256,
            qualification_sha256=self.binding.qualification_sha256),"PLAYER_AUTHORIZATION_INVALID")
        need(not self.binding.output.exists(),"PLAYER_OUTPUT_USED")
        try:
            with self.binding.claim.open("xb") as stream:
                stream.write(b.canonical(dict(authorization_sha256=self.authorization_sha256,
                    run_id=self.binding.manifest.run_id)))
        except FileExistsError as exc:
            raise PlayerError("PLAYER_AUTHORIZATION_USED") from exc

    def start(self):
        with self.lock:
            need(not self.used,"PLAYER_ALREADY_USED")
            self._authorize()
            self.used=True
            self.state["phase"]="RUNNING"
            self.thread=threading.Thread(target=self._run,name="MCM-bound-media",daemon=False)
            self.thread.start()

    def _open_session(self):
        p.MAIN_GATE=True
        try:
            return m.start(self.binding.manifest,self.binding.common,self.binding.inv,self.binding.output)
        finally:
            p.MAIN_GATE=False

    def _after_event(self):
        """No-op observation seam for neutral client tests, not a media callback."""

    def _verify(self):
        if self.verified:
            return
        self.verified=True
        proof=verification.verify_once(self.binding.output,self.binding.inv)
        self.state["verification"]=dict(status=proof["status"],evaluation_allowed=proof["evaluation_allowed"])

    def _run(self):
        try:
            self.session=self._open_session()
            for event in self.binding.manifest.events:
                if self.stop_event.is_set():
                    break
                with self.lock:
                    self.state["current"]=dict(ordinal=event.ordinal,pass_number=event.pass_number,
                        media_start_seconds=float(p.selection_time(self.binding.manifest,event)),audio_duration_seconds=0.1,
                        frame_selection_seconds=float(p.selection_time(self.binding.manifest,event))+0.05,kind=event.kind,
                        runtime_window=p.runtime_times(event)["field_window"])
                raw=self.session.next()
                shown=projection(raw)
                with self.lock:
                    self.state.update(completed=event.ordinal,last=shown,
                        last_processed=dict(self.state["current"]))
                    if self.binding.manifest.schema==p.FULL_VERSION:
                        receipt=self.session._materializer.receipts[-1]
                        self.state["last_processed"].update(frame_pts=receipt["frame_pts"],
                            video_time_base=list(self.binding.manifest.source.video_time_base))
                        self.state["decoder"]=dict(self.session._materializer.decoder.counters)
                        generation=self.session._runtime.rows[-1]["generations"]
                        self.state["memory_changes"]=[] if generation is None else [
                            dict(slot_index=i,action=action,generation=generation["births"][i])
                            for i,action in enumerate(generation["actions"]) if action not in ("FREE","UNCHANGED")]
                self._after_event()
            if self.binding.manifest.schema==p.FULL_VERSION and not self.stop_event.is_set():
                with self.lock:
                    self.state["phase"]="DRAINING"
                self.session.drain()
                with self.lock:
                    self.state["decoder"]=dict(self.session._materializer.decoder.counters)
            result=json.loads(self.session.stop())
            with self.lock:
                self.state["phase"]=result["status"]
                failure=result.get("failure")
                self.state["session_failure"]=None if not failure else failure.get("code")
                if result["status"]=="RECORDING_COMPLETE":
                    self.state["closure_cause"]="COMPLETED"
        except Exception as exc:
            with self.lock:
                code=getattr(exc,"code",type(exc).__name__)
                self.state.update(phase="NOT_EVALUABLE",error=code)
                if self.state["closure_cause"]=="UNKNOWN":
                    self.state["closure_cause"]="SOURCE_END" if code in (
                        "FRAME_COVERAGE_MISSING","AUDIO_COVERAGE_MISSING") else "TECHNICAL_ERROR"
        finally:
            p.MAIN_GATE=False
            try:
                if self.session is not None:
                    self.session.stop()
                if (self.binding.output/"record.json").is_file():
                    self._verify()
            except Exception as exc:
                with self.lock:
                    self.state["closure_error"]=getattr(exc,"code",type(exc).__name__)
                    self.state["phase"]="NOT_EVALUABLE"
                    if self.state["closure_cause"]=="UNKNOWN":
                        self.state["closure_cause"]="TECHNICAL_ERROR"
            if self.binding.output.is_dir():
                summary=dict(version=VERSION,completed=self.state["completed"],phase=self.state["phase"],
                    error=self.state["error"],verification=self.state["verification"],
                    closure_error=self.state.get("closure_error"),preview_read_bytes=self.preview_bytes,
                    closure_cause=self.state["closure_cause"],session_failure=self.state["session_failure"],
                    stop_trigger=self.state["stop_trigger"],
                    preview_is_decoder_input=False,gates=False)
                need(len(b.canonical(summary))<=1024,"PLAYER_CLOSURE_LIMIT")
                s.prior.save(self.binding.output/"player-close.json",summary)

    def stop(self,reason="USER_STOP"):
        need(reason in ("USER_STOP","SERVER_SHUTDOWN"),"PLAYER_STOP_REASON_INVALID")
        with self.lock:
            if self.state["phase"] in ("RUNNING","DRAINING") and self.state["closure_cause"]=="UNKNOWN":
                self.state["closure_cause"]=reason
                self.state["stop_trigger"]=reason
        self.stop_event.set()
        session=self.session
        if session is not None:
            session.stop()
        if self.thread and self.thread is not threading.current_thread():
            self.thread.join(15)
            need(not self.thread.is_alive(),"PLAYER_STOP_TIMEOUT")
        return self.status()

    def status(self):
        with self.lock:
            raw=b.canonical(dict(self.state,preview_read_bytes=self.preview_bytes))
        need(len(raw)<=RESPONSE_LIMIT,"PLAYER_STATUS_LIMIT")
        return raw

    def preview(self,start,end):
        def signature(stat):
            return stat.st_dev,stat.st_ino,stat.st_size,stat.st_mtime_ns
        need(not self.used,"PLAYER_PREVIEW_CLOSED")
        with self.binding.source.open("rb") as stream:
            before=signature(os.fstat(stream.fileno()))
            need(before[2]==self.binding.manifest.source.size,"PLAYER_MEDIA_SIZE_INVALID")
            if self.preview_signature is None:
                digest=hashlib.sha256()
                while block:=stream.read(65536):
                    self.preview_bytes+=len(block)
                    need(self.preview_bytes<=PREVIEW_LIMIT,"PLAYER_PREVIEW_LIMIT")
                    digest.update(block)
                need(digest.hexdigest()==self.binding.manifest.source.sha256
                    and signature(os.fstat(stream.fileno()))==before,"PLAYER_MEDIA_HASH_INVALID")
                self.preview_signature=before
            need(before==self.preview_signature,"PLAYER_MEDIA_CHANGED")
            need(self.preview_bytes+end-start+1<=PREVIEW_LIMIT,"PLAYER_PREVIEW_LIMIT")
            stream.seek(start)
            raw=stream.read(end-start+1)
            self.preview_bytes+=len(raw)
            need(signature(os.fstat(stream.fileno()))==before,"PLAYER_MEDIA_CHANGED")
            return raw


def serve(player,port=0):
    token=secrets.token_hex(32)
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(3)

        def log_message(self,*args):
            pass

        def reply(self,code,raw,content_type="application/json"):
            self.send_response(code)
            self.send_header("Content-Type",content_type)
            self.send_header("Content-Length",str(len(raw)))
            self.send_header("Cache-Control","no-store")
            self.send_header("X-Content-Type-Options","nosniff")
            self.send_header("Content-Security-Policy","default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; media-src 'self'; connect-src 'self'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(raw)

        def allowed(self):
            origin=f"http://127.0.0.1:{self.server.server_port}"
            need(self.headers.get("Host")==f"127.0.0.1:{self.server.server_port}","PLAYER_HOST_INVALID")
            need(self.headers.get("Origin",origin)==origin,"PLAYER_ORIGIN_INVALID")
            need(len(self.path)<=2048,"PLAYER_REQUEST_LIMIT")

        def do_GET(self):
            try:
                self.allowed()
                url=urlsplit(self.path)
                if url.path=="/":
                    self.reply(200,HTML.read_bytes().replace(b"__TOKEN__",token.encode()),"text/html; charset=utf-8")
                elif url.path=="/api/status":
                    need(self.headers.get("X-MCM-Token")==token,"PLAYER_TOKEN_INVALID")
                    self.reply(200,player.status())
                elif url.path=="/media":
                    need(parse_qs(url.query)=={"token":[token]},"PLAYER_TOKEN_INVALID")
                    need(not player.used,"PLAYER_PREVIEW_CLOSED")
                    size=player.binding.source.stat().st_size
                    request=self.headers.get("Range","bytes=0-")
                    match=re.fullmatch(r"bytes=(\d+)-(\d*)",request)
                    need(match is not None,"PLAYER_RANGE_INVALID")
                    start=int(match[1]);end=min(int(match[2]) if match[2] else size-1,start+1048575,size-1)
                    need(0<=start<=end<size,"PLAYER_RANGE_INVALID")
                    raw=player.preview(start,end)
                    self.send_response(206)
                    self.send_header("Content-Type","video/mp4")
                    self.send_header("Accept-Ranges","bytes")
                    self.send_header("Content-Range",f"bytes {start}-{end}/{size}")
                    self.send_header("Content-Length",str(len(raw)))
                    self.end_headers()
                    self.wfile.write(raw)
                else:
                    self.reply(404,b'{}')
            except (PlayerError,OSError) as exc:
                self.reply(403,b.canonical(dict(error=getattr(exc,"code",type(exc).__name__))))

        def do_POST(self):
            try:
                self.allowed()
                need(self.headers.get("X-MCM-Token")==token,"PLAYER_TOKEN_INVALID")
                need(self.headers.get("Content-Length","0")=="0"
                    and self.headers.get("Transfer-Encoding") is None,"PLAYER_BODY_INVALID")
                if self.path=="/api/start":
                    player.start()
                elif self.path=="/api/stop":
                    player.stop()
                else:
                    raise PlayerError("PLAYER_COMMAND_INVALID")
                self.reply(200,player.status())
            except (PlayerError,p.MediaError) as exc:
                self.reply(409,b.canonical(dict(error=exc.code)))
    server=HTTPServer(("127.0.0.1",port),Handler)
    server.timeout=1
    return server
