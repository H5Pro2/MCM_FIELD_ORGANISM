"""Explicit file/run-bound private UHD profile; historical worker default unchanged."""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from tools import _s2oe_decoder_worker as worker

VERSION = "s2oe.file-bound-uhd1024.v1"
ROOT = Path(__file__).resolve().parents[1]
OWN = ("tools/_s2oe_decoder_worker.py", "tools/_s2oe_media_decoder.py",
    "tools/_s2oe_isolation_log.py", "tools/_s2oe_uhd_profile.py")
CONFIG = dict(process_commit_bytes=1073741824,job_commit_bytes=1073741824,
    active_processes=1,queue_capacity=1,slot_bytes=6240000,request_seconds=30.0,stop_seconds=5.0,
    video_threads=1,video_size=[3840,2160],rgb_size=[1920,1080],rgb_format="rgb24",
    interpolation="AREA",src_colorspace=1,dst_colorspace=1,src_range="MPEG",dst_range="JPEG",
    audio_rate=48000,audio_layout="stereo",audio_format="fltp",audio_window_samples=4800,
    native_log_level="ERROR",native_log_messages=32,native_log_bytes=32768,
    pyav="16.1.0",libraries=dict(libavutil=[60,8,100],libavcodec=[62,11,100],
        libavformat=[62,3,100],libavdevice=[62,1,100],libavfilter=[11,4,100],
        libswscale=[9,1,100],libswresample=[6,1,100]))


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def code():
    return {p:sha((ROOT/p).read_bytes()) for p in OWN}


def bind(source,run_id):
    worker.require(type(run_id) is str and 12<=len(run_id)<=100,"UHD_RUN_INVALID")
    data=dict(version=VERSION,run_id=run_id,source=asdict(source),config=CONFIG,code=code())
    data["profile_digest"]=sha(canonical(data))
    return canonical(data)


def validate(raw,source,run_id):
    worker.require(type(raw) is bytes,"UHD_BINDING_INVALID")
    data=json.loads(raw)
    worker.require(set(data)=={"version","run_id","source","config","code","profile_digest"},
        "UHD_BINDING_INVALID")
    digest=data.pop("profile_digest")
    worker.require(sha(canonical(data))==digest,"UHD_DIGEST_INVALID")
    worker.require(data["version"]==VERSION and data["config"]==CONFIG,"UHD_PROFILE_INVALID")
    worker.require(data["code"]==code(),"UHD_CODE_INVALID")
    worker.require(data["run_id"]==run_id,"UHD_RUN_INVALID")
    worker.require(canonical(data["source"])==canonical(asdict(source)),"UHD_SOURCE_INVALID")
    return digest


def open_decoder(source,raw,run_id):
    digest=validate(raw,source,run_id)
    decoder=worker.WorkerDecoder(source,diagnostic_arm="COMMIT_1024")
    try:
        worker.require(decoder.resources["process_commit_limit"]==1073741824
            and decoder.resources["job_commit_limit"]==1073741824,"UHD_ACTIVE_LIMIT_INVALID")
        decoder.resources.update(private_profile=VERSION,private_profile_digest=digest,
            private_run_id=run_id)
        return decoder
    except BaseException:
        decoder.close()
        raise
