"""Verify one S2-JR browser viewport PNG against S2-JO frame zero."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np

from tools._s2jo_private_canonical_av_boundary import build_s2jo_visual_frame


RUN_ID = "s2jr-frame0-browser-preflight-20260902-01"
STATUS_EQUAL = "BROWSER_SIMULATION_FRAME0_PAYLOAD_EQUAL"
STATUS_DIFFER = "PAYLOADS_DIFFER"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
EXPECTED_WIDTH = 1920
EXPECTED_HEIGHT = 1080
EXPECTED_RGB_BYTES = EXPECTED_WIDTH * EXPECTED_HEIGHT * 3


def _canonical_bytes(payload: object) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _file_sha256(path: Path) -> str:
    return _sha256(path.read_bytes())


def _atomic_json(path: Path, payload: object) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("xb") as handle:
        handle.write(_canonical_bytes(payload) + b"\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _png_identity() -> dict[str, object]:
    lines = cv2.getBuildInformation().splitlines()
    media_lines = [
        line.strip()
        for line in lines
        if line.strip().startswith(("PNG:", "ZLib:"))
    ]
    return {
        "decoder": "opencv.imdecode.IMREAD_UNCHANGED",
        "opencv_version": cv2.__version__,
        "media_build_lines": media_lines,
        "allowed_postdecode_operation": "BGR_OR_BGRA_TO_RGB_CHANNEL_PERMUTATION",
    }


def _parse_png_ihdr(payload: bytes) -> dict[str, int]:
    if len(payload) < 33 or not payload.startswith(PNG_SIGNATURE):
        raise ValueError("PNG_SIGNATURE_INVALID")
    chunk_length = struct.unpack(">I", payload[8:12])[0]
    if chunk_length != 13 or payload[12:16] != b"IHDR":
        raise ValueError("PNG_IHDR_INVALID")
    width, height, bit_depth, color_type, compression, filtering, interlace = (
        struct.unpack(">IIBBBBB", payload[16:29])
    )
    return {
        "width": width,
        "height": height,
        "bit_depth": bit_depth,
        "color_type": color_type,
        "compression": compression,
        "filtering": filtering,
        "interlace": interlace,
    }


def _decode_rgb(payload: bytes) -> tuple[bytes, dict[str, object]]:
    ihdr = _parse_png_ihdr(payload)
    if (
        ihdr["width"] != EXPECTED_WIDTH
        or ihdr["height"] != EXPECTED_HEIGHT
        or ihdr["bit_depth"] != 8
        or ihdr["color_type"] not in (2, 6)
        or ihdr["compression"] != 0
        or ihdr["filtering"] != 0
        or ihdr["interlace"] != 0
    ):
        raise ValueError("PNG_FORM_INVALID")
    encoded = np.frombuffer(payload, dtype=np.uint8)
    decoded = cv2.imdecode(encoded, cv2.IMREAD_UNCHANGED)
    if decoded is None or decoded.dtype != np.uint8:
        raise ValueError("PNG_DECODE_INVALID")
    alpha_removed = False
    if decoded.shape == (EXPECTED_HEIGHT, EXPECTED_WIDTH, 3):
        rgb = np.ascontiguousarray(decoded[:, :, ::-1])
        decoded_channels = 3
    elif decoded.shape == (EXPECTED_HEIGHT, EXPECTED_WIDTH, 4):
        alpha = decoded[:, :, 3]
        if not np.all(alpha == 255):
            raise ValueError("PNG_ALPHA_NOT_OPAQUE")
        rgb = np.ascontiguousarray(decoded[:, :, 2::-1])
        decoded_channels = 4
        alpha_removed = True
    else:
        raise ValueError("PNG_DECODE_SHAPE_INVALID")
    rgb_bytes = rgb.tobytes(order="C")
    if len(rgb_bytes) != EXPECTED_RGB_BYTES:
        raise ValueError("RGB8_LENGTH_INVALID")
    return rgb_bytes, {
        "ihdr": ihdr,
        "decoded_shape": list(decoded.shape),
        "decoded_dtype": str(decoded.dtype),
        "decoded_channels": decoded_channels,
        "alpha_removed": alpha_removed,
        "alpha_rule": "REMOVE_ONLY_IF_ALL_255",
        "value_transformations": [],
    }


def verify(png_path: Path, browser_audit_path: Path, evidence_root: Path) -> int:
    if not png_path.is_absolute() or not browser_audit_path.is_absolute():
        raise ValueError("input paths must be absolute")
    evidence_dir = evidence_root / RUN_ID
    evidence_dir.mkdir(parents=True, exist_ok=False)
    script_path = Path(__file__).resolve()
    s2jo_path = script_path.parents[1] / "tools" / "_s2jo_private_canonical_av_boundary.py"
    browser_audit = json.loads(browser_audit_path.read_text(encoding="utf-8"))
    plan = {
        "schema": "s2jr.frame0-preflight-plan.v1",
        "run_id": RUN_ID,
        "frame_index": 0,
        "viewport": [EXPECTED_WIDTH, EXPECTED_HEIGHT],
        "device_scale_factor": 1,
        "render_method": "ImageData.putImageData",
        "capture_role": "FULL_VIEWPORT_PNG_ONCE",
        "source_hashes": {
            "tools/_s2jr_private_frame0_png_verifier.py": _file_sha256(script_path),
            "tools/_s2jo_private_canonical_av_boundary.py": _file_sha256(s2jo_path),
        },
        "browser_audit_digest": _sha256(_canonical_bytes(browser_audit)),
        "forbidden_calls": ["receptor", "audio", "memory", "context", "field"],
    }
    _atomic_json(evidence_dir / "plan.json", plan)

    status = STATUS_DIFFER
    error_code = None
    try:
        png_payload = png_path.read_bytes()
        screenshot_digest = _sha256(png_payload)
        if screenshot_digest != browser_audit.get("screenshot_png_sha256"):
            raise ValueError("SCREENSHOT_DIGEST_MISMATCH")
        if browser_audit.get("screenshot_count") != 1:
            raise ValueError("SCREENSHOT_COUNT_INVALID")
        geometry = browser_audit.get("geometry")
        if not isinstance(geometry, dict) or any(
            geometry.get(key) != value
            for key, value in {
                "inner_width": EXPECTED_WIDTH,
                "inner_height": EXPECTED_HEIGHT,
                "device_pixel_ratio": 1,
                "canvas_width": EXPECTED_WIDTH,
                "canvas_height": EXPECTED_HEIGHT,
                "canvas_css_width": EXPECTED_WIDTH,
                "canvas_css_height": EXPECTED_HEIGHT,
                "scroll_width": EXPECTED_WIDTH,
                "scroll_height": EXPECTED_HEIGHT,
            }.items()
        ):
            raise ValueError("BROWSER_GEOMETRY_INVALID")
        if browser_audit.get("render_method") != "ImageData.putImageData":
            raise ValueError("RENDER_METHOD_INVALID")
        actual_rgb, decode_receipt = _decode_rgb(png_payload)
        expected = build_s2jo_visual_frame(0)
        actual_digest = _sha256(actual_rgb)
        expected_digest = expected.pixel_digest
        if actual_digest != expected_digest or actual_rgb != expected.pixel_bytes:
            raise ValueError("PIXEL_PAYLOAD_MISMATCH")
        status = STATUS_EQUAL
        result = {
            "schema": "s2jr.frame0-preflight-result.v1",
            "run_id": RUN_ID,
            "status": status,
            "frame_index": 0,
            "png_path": str(png_path),
            "png_size_bytes": len(png_payload),
            "png_sha256": screenshot_digest,
            "actual_rgb8_size_bytes": len(actual_rgb),
            "actual_rgb8_sha256": actual_digest,
            "simulation_rgb8_sha256": expected_digest,
            "payload_bytes_equal": True,
            "decode_receipt": decode_receipt,
            "browser_audit": browser_audit,
            "png_decoder_audit": _png_identity(),
            "receptor_calls": 0,
            "audio_calls": 0,
            "memory_calls": 0,
            "context_calls": 0,
            "field_calls": 0,
            "raw_payload_in_result": False,
        }
    except Exception as exc:
        error_code = str(exc) if isinstance(exc, ValueError) else type(exc).__name__
        result = {
            "schema": "s2jr.frame0-preflight-result.v1",
            "run_id": RUN_ID,
            "status": STATUS_DIFFER,
            "error_code": error_code,
            "browser_audit": browser_audit,
            "png_decoder_audit": _png_identity(),
            "receptor_calls": 0,
            "audio_calls": 0,
            "memory_calls": 0,
            "context_calls": 0,
            "field_calls": 0,
            "raw_payload_in_result": False,
        }
    _atomic_json(evidence_dir / "result.json", result)
    terminal = {
        "schema": "s2jr.frame0-preflight-terminal.v1",
        "run_id": RUN_ID,
        "status": status,
        "exit_code": 0 if status == STATUS_EQUAL else 3,
        "error_code": error_code,
        "result_file_sha256": _file_sha256(evidence_dir / "result.json"),
        "completed_at_utc": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
    }
    _atomic_json(evidence_dir / "terminal.json", terminal)
    marker = "COMPLETE" if status == STATUS_EQUAL else "PAYLOADS_DIFFER"
    (evidence_dir / marker).write_text(
        _sha256(_canonical_bytes(terminal)) + "\n",
        encoding="ascii",
        newline="\n",
    )
    print(json.dumps(terminal, sort_keys=True))
    return int(terminal["exit_code"])


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--png", required=True, type=Path)
    parser.add_argument("--browser-audit", required=True, type=Path)
    parser.add_argument("--evidence-root", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    return verify(args.png, args.browser_audit, args.evidence_root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
