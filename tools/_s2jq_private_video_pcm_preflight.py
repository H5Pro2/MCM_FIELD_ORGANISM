"""Isolated S2-JQ PyAV/FFmpeg capability and bit-equality preflight."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

import av

from tools._s2jo_private_canonical_av_boundary import (
    S2JO_AUDIO_CONFIG,
    S2JO_CLOCK_ID,
    S2JO_EPISODE_ID,
    S2JO_FRAME_BYTES,
    S2JO_FRAME_COUNT,
    S2JO_HOP_BYTES,
    S2JO_HOP_COUNT,
    build_s2jo_audio_hop,
    build_s2jo_visual_frame,
)


RUN_ID = "s2jq-video-pcm-preflight-20260901-01"
SCHEMA = "s2jq.video-pcm-preflight.v1"
STATUS_AVAILABLE = "VIDEO_DECODE_PATH_AVAILABLE_BIT_EXACT"
STATUS_UNAVAILABLE = "VIDEO_DECODE_PATH_UNAVAILABLE"
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FORMAT = "rgb24"
VIDEO_CODEC = "rawvideo"
AUDIO_CODEC = "pcm_f32le"
AUDIO_FORMAT = "flt"
AUDIO_LAYOUT = "mono"
AUDIO_RATE = 48000
AUDIO_HOP_SAMPLES = 480
CONTAINER_FORMAT = "nut"
CONTAINER_LIMIT_BYTES = 67_108_864


class S2JQUnavailable(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def _canonical_bytes(payload: object) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")


def _digest_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _digest_object(payload: object) -> str:
    return _digest_bytes(_canonical_bytes(payload))


def _atomic_json(path: Path, payload: object) -> None:
    encoded = _canonical_bytes(payload) + b"\n"
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("xb") as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


class EventLog:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._index = 0
        self._previous = "0" * 64

    def append(self, stage: str, action: str, outcome: str, detail: object) -> str:
        self._index += 1
        body = {
            "schema": "s2jq.preflight-event.v1",
            "index": self._index,
            "stage": stage,
            "action": action,
            "outcome": outcome,
            "detail": detail,
            "previous_event_digest": self._previous,
        }
        event_digest = _digest_object(body)
        event = {**body, "event_digest": event_digest}
        with self._path.open("ab") as handle:
            handle.write(_canonical_bytes(event) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        self._previous = event_digest
        return event_digest

    @property
    def count(self) -> int:
        return self._index

    @property
    def terminal_digest(self) -> str:
        return self._previous


@dataclass(frozen=True)
class EncodedEpisode:
    path: Path
    size_bytes: int
    file_digest: str
    visual_payload_digests: tuple[str, ...]
    audio_payload_digests: tuple[str, ...]


@dataclass(frozen=True)
class DecodedEpisode:
    visual_payload_digests: tuple[str, ...]
    audio_payload_digests: tuple[str, ...]
    stream_inventory: dict[str, object]
    video_frame_receipts: tuple[dict[str, object], ...]
    audio_frame_receipts: tuple[dict[str, object], ...]


def _source_hash(path: Path) -> str:
    if not path.is_file():
        raise S2JQUnavailable("S2JQ_SOURCE_MISSING", f"missing source: {path.name}")
    return _digest_bytes(path.read_bytes())


def _format_fraction(value: object) -> str | None:
    if value is None:
        return None
    fraction = Fraction(value)
    return f"{fraction.numerator}/{fraction.denominator}"


def _capability_receipt() -> dict[str, object]:
    try:
        nut_output = av.ContainerFormat(CONTAINER_FORMAT, mode="w")
        nut_input = av.ContainerFormat(CONTAINER_FORMAT, mode="r")
        raw_encoder = av.Codec(VIDEO_CODEC, mode="w")
        raw_decoder = av.Codec(VIDEO_CODEC, mode="r")
        pcm_encoder = av.Codec(AUDIO_CODEC, mode="w")
        pcm_decoder = av.Codec(AUDIO_CODEC, mode="r")
    except Exception as exc:
        raise S2JQUnavailable(
            "S2JQ_CAPABILITY_ABSENT",
            f"required container or codec is unavailable: {type(exc).__name__}",
        ) from exc

    if not nut_output.is_output or not nut_input.is_input:
        raise S2JQUnavailable(
            "S2JQ_CAPABILITY_ABSENT", "NUT input/output capability is incomplete"
        )
    if not raw_encoder.is_encoder or not raw_decoder.is_decoder:
        raise S2JQUnavailable(
            "S2JQ_CAPABILITY_ABSENT", "rawvideo encode/decode capability is incomplete"
        )
    if not pcm_encoder.is_encoder or not pcm_decoder.is_decoder:
        raise S2JQUnavailable(
            "S2JQ_CAPABILITY_ABSENT", "pcm_f32le encode/decode capability is incomplete"
        )

    raw_formats = tuple(sorted(item.name for item in (raw_encoder.video_formats or [])))
    pcm_formats = tuple(sorted(item.name for item in (pcm_encoder.audio_formats or [])))
    if VIDEO_FORMAT not in raw_formats:
        raise S2JQUnavailable(
            "S2JQ_CAPABILITY_ABSENT", "rawvideo encoder does not advertise rgb24"
        )
    if AUDIO_FORMAT not in pcm_formats:
        raise S2JQUnavailable(
            "S2JQ_CAPABILITY_ABSENT", "pcm_f32le encoder does not advertise flt"
        )

    return {
        "schema": "s2jq.capability-receipt.v1",
        "container": {
            "name": CONTAINER_FORMAT,
            "input": nut_input.is_input,
            "output": nut_output.is_output,
        },
        "video": {
            "codec": VIDEO_CODEC,
            "encoder": raw_encoder.is_encoder,
            "decoder": raw_decoder.is_decoder,
            "advertised_formats": list(raw_formats),
            "required_format": VIDEO_FORMAT,
        },
        "audio": {
            "codec": AUDIO_CODEC,
            "encoder": pcm_encoder.is_encoder,
            "decoder": pcm_decoder.is_decoder,
            "advertised_formats": list(pcm_formats),
            "required_format": AUDIO_FORMAT,
            "required_layout": AUDIO_LAYOUT,
            "required_rate": AUDIO_RATE,
        },
        "pyav_version": av.__version__,
        "ffmpeg_version": av.ffmpeg_version_info,
        "library_versions": {
            key: list(value) for key, value in sorted(av.library_versions.items())
        },
        "conversion_components_used": [],
    }


def _make_video_frame(payload: bytes, pts: int) -> av.VideoFrame:
    if type(payload) is not bytes or len(payload) != S2JO_FRAME_BYTES:
        raise S2JQUnavailable("S2JQ_INVALID_FIXTURE", "visual payload is invalid")
    frame = av.VideoFrame(VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FORMAT)
    if frame.format.name != VIDEO_FORMAT or len(frame.planes) != 1:
        raise S2JQUnavailable("S2JQ_FORMAT_MISMATCH", "RGB24 frame allocation changed")
    plane = frame.planes[0]
    row_bytes = VIDEO_WIDTH * 3
    if plane.line_size < row_bytes:
        raise S2JQUnavailable("S2JQ_FORMAT_MISMATCH", "video plane stride is too small")
    if plane.line_size == row_bytes:
        packed = payload
    else:
        packed_buffer = bytearray(plane.buffer_size)
        for row in range(VIDEO_HEIGHT):
            source = row * row_bytes
            target = row * plane.line_size
            packed_buffer[target : target + row_bytes] = payload[source : source + row_bytes]
        packed = bytes(packed_buffer)
    plane.update(packed)
    frame.pts = pts
    frame.time_base = Fraction(1, 30)
    return frame


def _make_audio_frame(payload: bytes, pts: int) -> av.AudioFrame:
    if type(payload) is not bytes or len(payload) != S2JO_HOP_BYTES:
        raise S2JQUnavailable("S2JQ_INVALID_FIXTURE", "audio payload is invalid")
    frame = av.AudioFrame(
        format=AUDIO_FORMAT,
        layout=AUDIO_LAYOUT,
        samples=AUDIO_HOP_SAMPLES,
        align=1,
    )
    if (
        frame.format.name != AUDIO_FORMAT
        or frame.format.is_planar
        or frame.layout.name != AUDIO_LAYOUT
        or len(frame.planes) != 1
    ):
        raise S2JQUnavailable("S2JQ_FORMAT_MISMATCH", "PCM frame allocation changed")
    frame.planes[0].update(payload)
    frame.sample_rate = AUDIO_RATE
    frame.pts = pts
    frame.time_base = Fraction(1, AUDIO_RATE)
    return frame


def _schedule(frame_count: int, hop_count: int) -> tuple[tuple[str, int, Fraction], ...]:
    events = [("video", index, Fraction(index, 30)) for index in range(frame_count)]
    events.extend(("audio", index, Fraction(index, 100)) for index in range(hop_count))
    return tuple(sorted(events, key=lambda item: (item[2], 0 if item[0] == "video" else 1)))


def _write_episode(
    path: Path,
    frame_count: int,
    hop_count: int,
    stage: str,
    events: EventLog,
) -> EncodedEpisode:
    visual_digests: list[str] = []
    audio_digests: list[str] = []

    try:
        with av.open(str(path), mode="w", format=CONTAINER_FORMAT) as container:
            video = container.add_stream(VIDEO_CODEC, rate=Fraction(30, 1))
            video.width = VIDEO_WIDTH
            video.height = VIDEO_HEIGHT
            video.pix_fmt = VIDEO_FORMAT
            video.time_base = Fraction(1, 30)
            video.codec_context.time_base = Fraction(1, 30)

            audio = container.add_stream(AUDIO_CODEC, rate=AUDIO_RATE)
            audio.codec_context.sample_rate = AUDIO_RATE
            audio.codec_context.layout = AUDIO_LAYOUT
            audio.codec_context.format = AUDIO_FORMAT
            audio.time_base = Fraction(1, AUDIO_RATE)
            audio.codec_context.time_base = Fraction(1, AUDIO_RATE)

            for role, index, _ in _schedule(frame_count, hop_count):
                if role == "video":
                    item = build_s2jo_visual_frame(index)
                    visual_digests.append(item.pixel_digest)
                    frame = _make_video_frame(item.pixel_bytes, index)
                    packets = video.encode(frame)
                    payload_digest = item.pixel_digest
                else:
                    item = build_s2jo_audio_hop(index)
                    audio_digests.append(item.pcm_digest)
                    frame = _make_audio_frame(
                        item.pcm_bytes, index * AUDIO_HOP_SAMPLES
                    )
                    packets = audio.encode(frame)
                    payload_digest = item.pcm_digest
                for packet in packets:
                    container.mux(packet)
                events.append(
                    stage,
                    "encode_payload",
                    "OK",
                    {"role": role, "index": index, "payload_digest": payload_digest},
                )
                del item
            for packet in video.encode(None):
                container.mux(packet)
            for packet in audio.encode(None):
                container.mux(packet)
    except S2JQUnavailable:
        raise
    except Exception as exc:
        raise S2JQUnavailable(
            "S2JQ_ENCODE_FAILED", f"container encode failed: {type(exc).__name__}"
        ) from exc

    size_bytes = path.stat().st_size
    if size_bytes <= 0 or size_bytes > CONTAINER_LIMIT_BYTES:
        raise S2JQUnavailable(
            "S2JQ_CONTAINER_SIZE_INVALID", "container size is outside the bound"
        )
    file_digest = _source_hash(path)
    events.append(
        stage,
        "container_closed",
        "OK",
        {"size_bytes": size_bytes, "file_digest": file_digest},
    )
    return EncodedEpisode(
        path,
        size_bytes,
        file_digest,
        tuple(visual_digests),
        tuple(audio_digests),
    )


def _extract_rgb24(frame: av.VideoFrame) -> bytes:
    if (
        frame.format.name != VIDEO_FORMAT
        or frame.width != VIDEO_WIDTH
        or frame.height != VIDEO_HEIGHT
        or len(frame.planes) != 1
    ):
        raise S2JQUnavailable(
            "S2JQ_DECODE_FORMAT_MISMATCH", "decoded video is not direct RGB24"
        )
    plane = frame.planes[0]
    row_bytes = VIDEO_WIDTH * 3
    if plane.line_size < row_bytes:
        raise S2JQUnavailable(
            "S2JQ_DECODE_FORMAT_MISMATCH", "decoded RGB plane stride is too small"
        )
    raw = bytes(plane)
    return b"".join(
        raw[row * plane.line_size : row * plane.line_size + row_bytes]
        for row in range(VIDEO_HEIGHT)
    )


def _extract_pcm_f32le(frame: av.AudioFrame) -> bytes:
    if sys.byteorder != "little":
        raise S2JQUnavailable(
            "S2JQ_PLATFORM_ENDIANNESS", "PCM_F32LE requires a little-endian runtime"
        )
    if (
        frame.format.name != AUDIO_FORMAT
        or frame.format.is_planar
        or frame.layout.name != AUDIO_LAYOUT
        or frame.sample_rate != AUDIO_RATE
        or len(frame.planes) != 1
        or frame.samples <= 0
    ):
        raise S2JQUnavailable(
            "S2JQ_DECODE_FORMAT_MISMATCH", "decoded audio is not direct mono PCM_F32LE"
        )
    required = frame.samples * 4
    raw = bytes(frame.planes[0])
    if len(raw) < required:
        raise S2JQUnavailable(
            "S2JQ_DECODE_FORMAT_MISMATCH", "decoded PCM plane is incomplete"
        )
    return raw[:required]


def _stream_inventory(container: av.container.InputContainer) -> tuple[Any, Any, dict[str, object]]:
    streams = tuple(container.streams)
    video_streams = tuple(item for item in streams if item.type == "video")
    audio_streams = tuple(item for item in streams if item.type == "audio")
    if len(streams) != 2 or len(video_streams) != 1 or len(audio_streams) != 1:
        raise S2JQUnavailable(
            "S2JQ_STREAM_INVENTORY_MISMATCH", "container must have exactly one AV pair"
        )
    video = video_streams[0]
    audio = audio_streams[0]
    video_format = video.codec_context.format
    audio_format = audio.codec_context.format
    if (
        video.codec_context.name != VIDEO_CODEC
        or video.width != VIDEO_WIDTH
        or video.height != VIDEO_HEIGHT
        or video_format is None
        or video_format.name != VIDEO_FORMAT
    ):
        raise S2JQUnavailable(
            "S2JQ_STREAM_PROFILE_MISMATCH", "video stream profile differs"
        )
    if (
        audio.codec_context.name != AUDIO_CODEC
        or audio.sample_rate != AUDIO_RATE
        or audio.layout.name != AUDIO_LAYOUT
        or audio_format is None
        or audio_format.name != AUDIO_FORMAT
        or audio_format.is_planar
    ):
        raise S2JQUnavailable(
            "S2JQ_STREAM_PROFILE_MISMATCH", "audio stream profile differs"
        )
    inventory = {
        "container_format": container.format.name,
        "stream_count": len(streams),
        "video": {
            "index": video.index,
            "codec": video.codec_context.name,
            "format": video_format.name,
            "width": video.width,
            "height": video.height,
            "time_base": _format_fraction(video.time_base),
            "average_rate": _format_fraction(video.average_rate),
        },
        "audio": {
            "index": audio.index,
            "codec": audio.codec_context.name,
            "format": audio_format.name,
            "layout": audio.layout.name,
            "channels": len(audio.layout.channels),
            "sample_rate": audio.sample_rate,
            "time_base": _format_fraction(audio.time_base),
        },
    }
    return video, audio, inventory


def _decode_episode(
    encoded: EncodedEpisode,
    expected_frames: int,
    expected_hops: int,
    stage: str,
    events: EventLog,
) -> DecodedEpisode:
    video_digests: list[str] = []
    audio_digests: list[str] = []
    video_receipts: list[dict[str, object]] = []
    audio_receipts: list[dict[str, object]] = []
    audio_buffer = bytearray()
    decoded_audio_samples = 0

    try:
        with av.open(str(encoded.path), mode="r", format=CONTAINER_FORMAT) as container:
            video_stream, audio_stream, inventory = _stream_inventory(container)
            events.append(stage, "stream_inventory", "OK", inventory)
            for packet in container.demux(video_stream, audio_stream):
                for frame in packet.decode():
                    if isinstance(frame, av.VideoFrame):
                        index = len(video_digests)
                        if index >= expected_frames:
                            raise S2JQUnavailable(
                                "S2JQ_DECODE_COUNT_MISMATCH", "additional video frame"
                            )
                        expected_time = Fraction(index, 30)
                        actual_time = Fraction(frame.pts or 0) * Fraction(frame.time_base)
                        if frame.pts is None or actual_time != expected_time:
                            raise S2JQUnavailable(
                                "S2JQ_DECODE_TIME_MISMATCH", "video timestamp differs"
                            )
                        payload = _extract_rgb24(frame)
                        payload_digest = _digest_bytes(payload)
                        if payload_digest != encoded.visual_payload_digests[index]:
                            raise S2JQUnavailable(
                                "S2JQ_PAYLOAD_MISMATCH", "decoded visual payload differs"
                            )
                        video_digests.append(payload_digest)
                        receipt = {
                            "index": index,
                            "format": frame.format.name,
                            "pts": frame.pts,
                            "time_base": _format_fraction(frame.time_base),
                            "payload_digest": payload_digest,
                        }
                        video_receipts.append(receipt)
                        events.append(stage, "decode_video", "OK", receipt)
                    elif isinstance(frame, av.AudioFrame):
                        expected_pts = decoded_audio_samples
                        actual_position = (
                            Fraction(frame.pts or 0)
                            * Fraction(frame.time_base)
                            * AUDIO_RATE
                        )
                        if frame.pts is None or actual_position != expected_pts:
                            raise S2JQUnavailable(
                                "S2JQ_DECODE_TIME_MISMATCH", "audio timestamp differs"
                            )
                        payload = _extract_pcm_f32le(frame)
                        decoded_audio_samples += frame.samples
                        frame_receipt = {
                            "decode_frame_index": len(audio_receipts),
                            "format": frame.format.name,
                            "layout": frame.layout.name,
                            "sample_rate": frame.sample_rate,
                            "samples": frame.samples,
                            "pts": frame.pts,
                            "time_base": _format_fraction(frame.time_base),
                            "plane_digest": _digest_bytes(payload),
                        }
                        audio_receipts.append(frame_receipt)
                        events.append(stage, "decode_audio_frame", "OK", frame_receipt)
                        audio_buffer.extend(payload)
                        while len(audio_buffer) >= S2JO_HOP_BYTES:
                            index = len(audio_digests)
                            if index >= expected_hops:
                                raise S2JQUnavailable(
                                    "S2JQ_DECODE_COUNT_MISMATCH", "additional audio hop"
                                )
                            hop = bytes(audio_buffer[:S2JO_HOP_BYTES])
                            del audio_buffer[:S2JO_HOP_BYTES]
                            payload_digest = _digest_bytes(hop)
                            if payload_digest != encoded.audio_payload_digests[index]:
                                raise S2JQUnavailable(
                                    "S2JQ_PAYLOAD_MISMATCH", "decoded audio payload differs"
                                )
                            audio_digests.append(payload_digest)
                            events.append(
                                stage,
                                "accept_audio_hop",
                                "OK",
                                {"index": index, "payload_digest": payload_digest},
                            )
    except S2JQUnavailable:
        raise
    except Exception as exc:
        raise S2JQUnavailable(
            "S2JQ_DECODE_FAILED", f"container decode failed: {type(exc).__name__}"
        ) from exc

    if audio_buffer:
        raise S2JQUnavailable(
            "S2JQ_DECODE_COUNT_MISMATCH", "partial PCM hop remains after decode"
        )
    if len(video_digests) != expected_frames or len(audio_digests) != expected_hops:
        raise S2JQUnavailable(
            "S2JQ_DECODE_COUNT_MISMATCH", "decoded payload inventory differs"
        )
    return DecodedEpisode(
        tuple(video_digests),
        tuple(audio_digests),
        inventory,
        tuple(video_receipts),
        tuple(audio_receipts),
    )


def _episode_receipt(encoded: EncodedEpisode, decoded: DecodedEpisode) -> dict[str, object]:
    if decoded.visual_payload_digests != encoded.visual_payload_digests:
        raise S2JQUnavailable("S2JQ_PAYLOAD_MISMATCH", "visual digest sequence differs")
    if decoded.audio_payload_digests != encoded.audio_payload_digests:
        raise S2JQUnavailable("S2JQ_PAYLOAD_MISMATCH", "audio digest sequence differs")
    payload_bindings = [
        {"role": "VISUAL_FRAME", "index": index, "payload_digest": digest}
        for index, digest in enumerate(decoded.visual_payload_digests)
    ]
    payload_bindings.extend(
        {"role": "AUDIO_HOP", "index": index, "payload_digest": digest}
        for index, digest in enumerate(decoded.audio_payload_digests)
    )
    payload_bindings.sort(key=lambda item: (item["role"], item["index"]))
    receipt = {
        "schema": "s2jq.bit-exact-episode-receipt.v1",
        "episode_id": S2JO_EPISODE_ID,
        "clock_id": S2JO_CLOCK_ID,
        "container_path": str(encoded.path.resolve()),
        "container_size_bytes": encoded.size_bytes,
        "container_sha256": encoded.file_digest,
        "stream_inventory": decoded.stream_inventory,
        "visual_payload_count": len(decoded.visual_payload_digests),
        "audio_payload_count": len(decoded.audio_payload_digests),
        "payload_bindings": payload_bindings,
        "conversion_components_used": [],
        "raw_payload_bytes_persisted_in_evidence": 0,
    }
    return {**receipt, "receipt_digest": _digest_object(receipt)}


def _plan(repo_root: Path, fixture_root: Path) -> dict[str, object]:
    sources = (
        repo_root / "tools" / "_s2jq_private_video_pcm_preflight.py",
        repo_root / "tools" / "_s2jo_private_canonical_av_boundary.py",
        repo_root / "docs" / "S2JP_VIDEO_PCM_QUELLENAUSWAHL_UND_MATERIALISIERUNGSVERTRAG.md",
    )
    return {
        "schema": "s2jq.preflight-plan.v1",
        "run_id": RUN_ID,
        "stages": ["CAPABILITY", "FULL_FIXTURE"],
        "source_hashes": {str(path.relative_to(repo_root)): _source_hash(path) for path in sources},
        "runtime": {
            "python": sys.version,
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
            "byteorder": sys.byteorder,
            "pyav": av.__version__,
            "ffmpeg": av.ffmpeg_version_info,
        },
        "container_plan": {
            "format": CONTAINER_FORMAT,
            "video_codec": VIDEO_CODEC,
            "video_format": VIDEO_FORMAT,
            "video_shape": [VIDEO_HEIGHT, VIDEO_WIDTH, 3],
            "video_rate": "30/1",
            "audio_codec": AUDIO_CODEC,
            "audio_format": AUDIO_FORMAT,
            "audio_layout": AUDIO_LAYOUT,
            "audio_rate": AUDIO_RATE,
            "frame_count": S2JO_FRAME_COUNT,
            "hop_count": S2JO_HOP_COUNT,
            "hop_samples": AUDIO_HOP_SAMPLES,
            "container_limit_bytes": CONTAINER_LIMIT_BYTES,
        },
        "fixture_root": str(fixture_root.resolve()),
        "forbidden_calls": [
            "VideoFrame.reformat",
            "VideoFrame.to_ndarray",
            "AudioFrame.to_ndarray",
            "AudioResampler",
            "receptor",
            "memory",
            "context",
            "field",
        ],
    }


def run_preflight(evidence_root: Path, fixture_root: Path) -> int:
    repo_root = Path(__file__).resolve().parents[1]
    if not evidence_root.is_absolute() or not fixture_root.is_absolute():
        raise ValueError("output roots must be absolute Path values")
    evidence_dir = evidence_root / RUN_ID
    fixture_dir = fixture_root / RUN_ID
    evidence_dir.mkdir(parents=True, exist_ok=False)
    fixture_dir.mkdir(parents=True, exist_ok=False)
    events = EventLog(evidence_dir / "events.jsonl")
    plan = _plan(repo_root, fixture_dir)
    _atomic_json(evidence_dir / "plan.json", plan)
    events.append("PREPARE", "bind_plan", "OK", {"plan_digest": _digest_object(plan)})

    try:
        capability = _capability_receipt()
        events.append("CAPABILITY", "inspect_capabilities", "OK", capability)
        stage_one_path = fixture_dir / "capability-direct.nut"
        stage_one_encoded = _write_episode(stage_one_path, 1, 1, "CAPABILITY", events)
        stage_one_decoded = _decode_episode(
            stage_one_encoded, 1, 1, "CAPABILITY", events
        )
        stage_one_receipt = _episode_receipt(stage_one_encoded, stage_one_decoded)
        events.append("CAPABILITY", "seal_stage", "OK", stage_one_receipt)

        fixture_path = fixture_dir / "s2jo-reference-video-audio.nut"
        fixture_encoded = _write_episode(
            fixture_path,
            S2JO_FRAME_COUNT,
            S2JO_HOP_COUNT,
            "FULL_FIXTURE",
            events,
        )
        fixture_decoded = _decode_episode(
            fixture_encoded,
            S2JO_FRAME_COUNT,
            S2JO_HOP_COUNT,
            "FULL_FIXTURE",
            events,
        )
        fixture_receipt = _episode_receipt(fixture_encoded, fixture_decoded)
        events.append("FULL_FIXTURE", "seal_stage", "OK", fixture_receipt)
        result = {
            "schema": SCHEMA,
            "run_id": RUN_ID,
            "status": STATUS_AVAILABLE,
            "capability_receipt": capability,
            "stage_one_receipt": stage_one_receipt,
            "fixture_receipt": fixture_receipt,
            "video_decode_frame_receipts": list(fixture_decoded.video_frame_receipts),
            "audio_decode_frame_receipts": list(fixture_decoded.audio_frame_receipts),
            "payload_comparisons": S2JO_FRAME_COUNT + S2JO_HOP_COUNT,
            "payload_mismatches": 0,
            "receptor_calls": 0,
            "memory_calls": 0,
            "context_calls": 0,
            "field_calls": 0,
            "event_count_before_terminal": events.count,
            "terminal_event_digest_before_result": events.terminal_digest,
        }
        _atomic_json(evidence_dir / "result.json", result)
        result_digest = _source_hash(evidence_dir / "result.json")
        terminal_event = events.append(
            "TERMINAL", "publish_result", "OK", {"result_file_sha256": result_digest}
        )
        terminal = {
            "schema": "s2jq.terminal.v1",
            "run_id": RUN_ID,
            "status": STATUS_AVAILABLE,
            "exit_code": 0,
            "result_file_sha256": result_digest,
            "terminal_event_digest": terminal_event,
            "completed_at_utc": _utc_now(),
        }
        _atomic_json(evidence_dir / "terminal.json", terminal)
        (evidence_dir / "COMPLETE").write_text(
            _digest_object(terminal) + "\n", encoding="ascii", newline="\n"
        )
        print(json.dumps(terminal, sort_keys=True))
        return 0
    except Exception as exc:
        if isinstance(exc, S2JQUnavailable):
            error_code = exc.code
            message = exc.message
        else:
            error_code = "S2JQ_UNCLASSIFIED_FAILURE"
            message = type(exc).__name__
        failure_event = events.append(
            "TERMINAL",
            "stop_unavailable",
            "VIDEO_DECODE_PATH_UNAVAILABLE",
            {"error_code": error_code, "message": message},
        )
        result = {
            "schema": SCHEMA,
            "run_id": RUN_ID,
            "status": STATUS_UNAVAILABLE,
            "error_code": error_code,
            "message": message,
            "receptor_calls": 0,
            "memory_calls": 0,
            "context_calls": 0,
            "field_calls": 0,
            "event_count": events.count,
            "terminal_event_digest": failure_event,
        }
        _atomic_json(evidence_dir / "result.json", result)
        terminal = {
            "schema": "s2jq.terminal.v1",
            "run_id": RUN_ID,
            "status": STATUS_UNAVAILABLE,
            "exit_code": 2,
            "result_file_sha256": _source_hash(evidence_dir / "result.json"),
            "terminal_event_digest": failure_event,
            "completed_at_utc": _utc_now(),
        }
        _atomic_json(evidence_dir / "terminal.json", terminal)
        (evidence_dir / "UNAVAILABLE").write_text(
            _digest_object(terminal) + "\n", encoding="ascii", newline="\n"
        )
        print(json.dumps(terminal, sort_keys=True))
        return 2


def _parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-root", required=True, type=Path)
    parser.add_argument("--fixture-root", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = _parse_args(argv)
    return run_preflight(args.evidence_root, args.fixture_root)


if __name__ == "__main__":
    raise SystemExit(main())
