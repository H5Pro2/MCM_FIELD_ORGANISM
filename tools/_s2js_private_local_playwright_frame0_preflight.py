"""One-shot local Z4-A2 Playwright raster preflight for S2-JR frame zero."""

from __future__ import annotations

import hashlib
import json
import os
import struct
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from mcm_field_organism.z4a_playwright_runtime_binding import (
    bind_installed_z4a_playwright_runtime,
)
from tools._s2jo_private_canonical_av_boundary import build_s2jo_visual_frame


RUN_ID = "s2jr-local-z4a2-frame0-preflight-20260902-01"
WIDTH = 1920
HEIGHT = 1080
EXPECTED_RGB_BYTES = WIDTH * HEIGHT * 3
MANIFEST_ENTRY = "chromium-headless-shell"
STATUS_EQUAL = "BROWSER_SIMULATION_FRAME0_PAYLOAD_EQUAL"
STATUS_DIFFER = "PAYLOADS_DIFFER"
STATUS_NOT_EVALUABLE = "NOT_EVALUABLE"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

_HTML = """<!doctype html>
<html><head><meta charset="utf-8"><style>
html,body{width:100%;height:100%;margin:0;padding:0;border:0;overflow:hidden;}
canvas{display:block;width:1920px;height:1080px;margin:0;padding:0;border:0;}
</style></head><body><canvas id="world" width="1920" height="1080"></canvas></body></html>"""

_RENDER_SCRIPT = """() => {
  const width = 1920;
  const height = 1080;
  const canvas = document.getElementById('world');
  const context = canvas.getContext('2d', {alpha: false});
  if (!context) throw new Error('2D_CONTEXT_UNAVAILABLE');
  const image = new ImageData(width, height);
  const data = image.data;
  for (let pixel = 0; pixel < width * height; pixel += 1) {
    const offset = pixel * 4;
    data[offset] = 16;
    data[offset + 1] = 32;
    data[offset + 2] = 48;
    data[offset + 3] = 255;
  }
  for (let y = 270; y < 405; y += 1) {
    for (let x = 0; x < 160; x += 1) {
      const offset = (y * width + x) * 4;
      data[offset] = 224;
      data[offset + 1] = 64;
      data[offset + 2] = 32;
      data[offset + 3] = 255;
    }
  }
  context.putImageData(image, 0, 0);
  return {method: 'ImageData.putImageData', frameIndex: 0, writes: 1};
}"""

_GEOMETRY_SCRIPT = """() => {
  const canvas = document.getElementById('world');
  const bodyStyle = getComputedStyle(document.body);
  const canvasStyle = getComputedStyle(canvas);
  const rect = canvas.getBoundingClientRect();
  return {
    inner_width: window.innerWidth,
    inner_height: window.innerHeight,
    device_pixel_ratio: window.devicePixelRatio,
    canvas_width: canvas.width,
    canvas_height: canvas.height,
    canvas_css_width: rect.width,
    canvas_css_height: rect.height,
    scroll_width: document.documentElement.scrollWidth,
    scroll_height: document.documentElement.scrollHeight,
    body_child_count: document.body.children.length,
    body_text: document.body.innerText,
    body_margin: bodyStyle.margin,
    body_padding: bodyStyle.padding,
    canvas_border_width: canvasStyle.borderWidth
  };
}"""


class PreflightFailure(RuntimeError):
    def __init__(self, code: str, phase: str) -> None:
        super().__init__(code)
        self.code = code
        self.phase = phase


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _atomic_json(path: Path, value: object) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("xb") as handle:
        handle.write(_canonical_bytes(value) + b"\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _phase_failure(code: str, phase: str, exc: BaseException) -> PreflightFailure:
    failure = PreflightFailure(code, phase)
    failure.__cause__ = exc
    return failure


def _validate_geometry(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError("geometry is not an object")
    expected = {
        "inner_width": WIDTH,
        "inner_height": HEIGHT,
        "device_pixel_ratio": 1,
        "canvas_width": WIDTH,
        "canvas_height": HEIGHT,
        "canvas_css_width": WIDTH,
        "canvas_css_height": HEIGHT,
        "scroll_width": WIDTH,
        "scroll_height": HEIGHT,
        "body_child_count": 1,
        "body_text": "",
        "body_margin": "0px",
        "body_padding": "0px",
        "canvas_border_width": "0px",
    }
    if any(value.get(key) != expected_value for key, expected_value in expected.items()):
        raise ValueError("browser geometry differs from the bound viewport")
    return {key: value[key] for key in expected}


def _decode_png(payload: bytes) -> tuple[bytes, dict[str, object]]:
    if len(payload) < 33 or not payload.startswith(PNG_SIGNATURE):
        raise ValueError("PNG_SIGNATURE_INVALID")
    chunk_length = struct.unpack(">I", payload[8:12])[0]
    if chunk_length != 13 or payload[12:16] != b"IHDR":
        raise ValueError("PNG_IHDR_INVALID")
    width, height, bit_depth, color_type, compression, filtering, interlace = (
        struct.unpack(">IIBBBBB", payload[16:29])
    )
    if (
        width != WIDTH
        or height != HEIGHT
        or bit_depth != 8
        or color_type not in (2, 6)
        or compression != 0
        or filtering != 0
        or interlace != 0
    ):
        raise ValueError("PNG_FORM_INVALID")
    decoded = cv2.imdecode(np.frombuffer(payload, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    if decoded is None or decoded.dtype != np.uint8:
        raise ValueError("PNG_DECODE_INVALID")
    alpha_removed = False
    if decoded.shape == (HEIGHT, WIDTH, 3):
        rgb = np.ascontiguousarray(decoded[:, :, ::-1])
    elif decoded.shape == (HEIGHT, WIDTH, 4):
        if not np.all(decoded[:, :, 3] == 255):
            raise ValueError("PNG_ALPHA_NOT_OPAQUE")
        rgb = np.ascontiguousarray(decoded[:, :, 2::-1])
        alpha_removed = True
    else:
        raise ValueError("PNG_DECODE_SHAPE_INVALID")
    rgb_bytes = rgb.tobytes(order="C")
    if len(rgb_bytes) != EXPECTED_RGB_BYTES:
        raise ValueError("RGB8_LENGTH_INVALID")
    return rgb_bytes, {
        "png_width": width,
        "png_height": height,
        "png_bit_depth": bit_depth,
        "png_color_type": color_type,
        "decoded_shape": list(decoded.shape),
        "decoded_dtype": str(decoded.dtype),
        "alpha_removed": alpha_removed,
        "alpha_rule": "REMOVE_ONLY_IF_ALL_255",
        "allowed_value_operation": "BGR_OR_BGRA_TO_RGB_CHANNEL_PERMUTATION",
        "opencv_version": cv2.__version__,
    }


def _close_lifecycle(page: Any, context: Any, browser: Any) -> dict[str, object]:
    lifecycle: dict[str, object] = {
        "page_close_attempted": False,
        "page_closed": False,
        "context_close_attempted": False,
        "context_closed": False,
        "browser_close_attempted": False,
        "browser_closed": False,
        "close_errors": [],
    }
    for name, value in (("page", page), ("context", context), ("browser", browser)):
        if value is None:
            continue
        lifecycle[f"{name}_close_attempted"] = True
        try:
            value.close()
            lifecycle[f"{name}_closed"] = True
        except Exception as exc:  # lifecycle evidence only; original phase remains bound
            lifecycle["close_errors"].append(type(exc).__name__)
    return lifecycle


def run_once(project_root: Path, evidence_root: Path, local_root: Path) -> int:
    if not project_root.is_absolute() or not evidence_root.is_absolute() or not local_root.is_absolute():
        raise ValueError("all roots must be absolute")
    evidence_dir = evidence_root / RUN_ID
    local_dir = local_root / RUN_ID
    if evidence_dir.exists() or local_dir.exists():
        raise RuntimeError("RUN_ID_ALREADY_USED")
    evidence_dir.mkdir(parents=True, exist_ok=False)
    local_dir.mkdir(parents=True, exist_ok=False)
    screenshot_path = local_dir / "browser-frame0.png"
    script_path = Path(__file__).resolve()
    runtime_source = project_root / "mcm_field_organism" / "z4a_playwright_runtime_binding.py"
    smoke_source = project_root / "mcm_field_organism" / "z4a_playwright_smoke.py"
    capture_source = project_root / "mcm_field_organism" / "z4a_playwright_capture.py"
    simulation_source = project_root / "tools" / "_s2jo_private_canonical_av_boundary.py"
    installation_root = Path(os.environ["LOCALAPPDATA"]) / "ms-playwright"
    executable = (
        installation_root
        / "chromium_headless_shell-1217"
        / "chrome-headless-shell-win64"
        / "chrome-headless-shell.exe"
    )

    runtime_binding = bind_installed_z4a_playwright_runtime(
        manifest_entry_name=MANIFEST_ENTRY,
        executable_path=executable,
        installation_root=installation_root,
    )
    source_hashes = {
        "tools/_s2js_private_local_playwright_frame0_preflight.py": _file_sha256(script_path),
        "mcm_field_organism/z4a_playwright_runtime_binding.py": _file_sha256(runtime_source),
        "mcm_field_organism/z4a_playwright_smoke.py": _file_sha256(smoke_source),
        "mcm_field_organism/z4a_playwright_capture.py": _file_sha256(capture_source),
        "tools/_s2jo_private_canonical_av_boundary.py": _file_sha256(simulation_source),
    }
    plan = {
        "schema": "s2js.local-z4a2-frame0-plan.v1",
        "run_id": RUN_ID,
        "frame_index": 0,
        "viewport": [WIDTH, HEIGHT],
        "device_scale_factor": 1,
        "page_source": "LOCAL_PAGE_SET_CONTENT",
        "render_method": "ImageData.putImageData",
        "screenshot_role": "FULL_VIEWPORT_PNG_EXACTLY_ONCE",
        "maximum_screenshot_calls": 1,
        "network_allowed": False,
        "runtime_binding": asdict(runtime_binding),
        "source_hashes": source_hashes,
        "html_sha256": _sha256(_HTML.encode("ascii")),
        "render_script_sha256": _sha256(_RENDER_SCRIPT.encode("ascii")),
        "forbidden_calls": ["receptor", "audio", "memory", "context", "field"],
    }
    _atomic_json(evidence_dir / "plan.json", plan)

    page = None
    context = None
    browser = None
    screenshot_calls = 0
    blocked_requests: list[str] = []
    geometry: dict[str, object] | None = None
    render_receipt: object = None
    observed_version = ""
    browser_started = False
    failure: PreflightFailure | None = None
    png_payload: bytes | None = None
    playwright = None
    lifecycle: dict[str, object] = _close_lifecycle(None, None, None)

    try:
        if _file_sha256(executable) != runtime_binding.executable_sha256:
            raise PreflightFailure("BROWSER_START_FAILED", "BROWSER_START")
        try:
            from playwright.sync_api import sync_playwright

            manager = sync_playwright()
            playwright = manager.start()
            try:
                browser = playwright.chromium.launch(
                    executable_path=str(executable),
                    headless=True,
                    args=[
                        "--disable-background-networking",
                        "--disable-component-update",
                        "--disable-default-apps",
                        "--disable-extensions",
                        "--disable-sync",
                        "--metrics-recording-only",
                        "--no-first-run",
                    ],
                )
                browser_started = True
                observed_version = browser.version
                if observed_version != runtime_binding.engine_version:
                    raise ValueError("observed browser version differs from binding")
            except Exception as exc:
                raise _phase_failure("BROWSER_START_FAILED", "BROWSER_START", exc)

            try:
                context = browser.new_context(
                    viewport={"width": WIDTH, "height": HEIGHT},
                    device_scale_factor=1,
                    java_script_enabled=True,
                    accept_downloads=False,
                    service_workers="block",
                )

                def block_request(route: Any, request: Any) -> None:
                    blocked_requests.append(request.url)
                    route.abort("blockedbyclient")

                context.route("**/*", block_request)
            except Exception as exc:
                raise _phase_failure("CONTEXT_CREATE_FAILED", "CONTEXT_CREATE", exc)

            try:
                page = context.new_page()
            except Exception as exc:
                raise _phase_failure("PAGE_CREATE_FAILED", "PAGE_CREATE", exc)

            try:
                page.set_content(_HTML, wait_until="load")
                geometry = _validate_geometry(page.evaluate(_GEOMETRY_SCRIPT))
                if blocked_requests:
                    raise ValueError("network request observed")
            except Exception as exc:
                raise _phase_failure("GEOMETRY_INVALID", "GEOMETRY_CHECK", exc)

            try:
                render_receipt = page.evaluate(_RENDER_SCRIPT)
                if render_receipt != {
                    "method": "ImageData.putImageData",
                    "frameIndex": 0,
                    "writes": 1,
                }:
                    raise ValueError("render receipt changed")
            except Exception as exc:
                raise _phase_failure("RENDER_FAILED", "RENDER", exc)

            try:
                screenshot_calls += 1
                png_payload = page.screenshot(
                    path=str(screenshot_path),
                    type="png",
                    full_page=False,
                    animations="disabled",
                )
                if screenshot_calls != 1 or not screenshot_path.is_file():
                    raise ValueError("screenshot cardinality changed")
            except Exception as exc:
                raise _phase_failure("SCREENSHOT_FAILED", "SCREENSHOT", exc)
        except PreflightFailure:
            raise
        except Exception as exc:
            raise _phase_failure("BROWSER_START_FAILED", "BROWSER_START", exc)
    except PreflightFailure as exc:
        failure = exc
    finally:
        lifecycle = _close_lifecycle(page, context, browser)
        if playwright is not None:
            try:
                playwright.stop()
            except Exception as exc:
                lifecycle["close_errors"].append(type(exc).__name__)
        if browser_started and (
            lifecycle["browser_closed"] is not True or lifecycle["close_errors"]
        ):
            failure = PreflightFailure("BROWSER_CLOSE_FAILED", "CLOSE")

    browser_audit = {
        "schema": "s2js.local-z4a2-browser-audit.v1",
        "run_id": RUN_ID,
        "runtime_binding_digest": _sha256(_canonical_bytes(asdict(runtime_binding))),
        "engine_version_bound": runtime_binding.engine_version,
        "engine_version_observed": observed_version,
        "browser_started": browser_started,
        "geometry": geometry,
        "render_receipt": render_receipt,
        "screenshot_count": screenshot_calls,
        "screenshot_png_path": str(screenshot_path) if screenshot_path.is_file() else None,
        "screenshot_png_size_bytes": screenshot_path.stat().st_size if screenshot_path.is_file() else 0,
        "screenshot_png_sha256": _file_sha256(screenshot_path) if screenshot_path.is_file() else None,
        "blocked_request_count": len(blocked_requests),
        "lifecycle": lifecycle,
    }
    _atomic_json(evidence_dir / "browser-audit.json", browser_audit)

    status = STATUS_NOT_EVALUABLE
    error_code: str | None = failure.code if failure is not None else None
    decode_receipt: dict[str, object] | None = None
    comparison: dict[str, object] | None = None
    if failure is None and png_payload is not None:
        try:
            actual_rgb, decode_receipt = _decode_png(png_payload)
            expected = build_s2jo_visual_frame(0)
            comparison = {
                "actual_rgb8_size_bytes": len(actual_rgb),
                "actual_rgb8_sha256": _sha256(actual_rgb),
                "simulation_rgb8_size_bytes": len(expected.pixel_bytes),
                "simulation_rgb8_sha256": expected.pixel_digest,
                "payload_bytes_equal": actual_rgb == expected.pixel_bytes,
            }
            if comparison["payload_bytes_equal"]:
                status = STATUS_EQUAL
            else:
                status = STATUS_DIFFER
                error_code = "PAYLOADS_DIFFER"
            del actual_rgb
        except Exception:
            status = STATUS_NOT_EVALUABLE
            error_code = "PNG_DECODE_FAILED"
    del png_payload

    result = {
        "schema": "s2js.local-z4a2-frame0-result.v1",
        "run_id": RUN_ID,
        "status": status,
        "error_code": error_code,
        "failure_phase": failure.phase if failure is not None else None,
        "browser_audit_digest": _sha256(_canonical_bytes(browser_audit)),
        "decode_receipt": decode_receipt,
        "comparison": comparison,
        "screenshot_count": screenshot_calls,
        "png_decoder_calls": 1 if decode_receipt is not None else 0,
        "receptor_calls": 0,
        "audio_calls": 0,
        "memory_calls": 0,
        "context_calls": 0,
        "field_calls": 0,
        "raw_payload_in_repository_result": False,
    }
    _atomic_json(evidence_dir / "result.json", result)
    exit_code = 0 if status == STATUS_EQUAL else 3
    terminal = {
        "schema": "s2js.local-z4a2-frame0-terminal.v1",
        "run_id": RUN_ID,
        "status": status,
        "exit_code": exit_code,
        "error_code": error_code,
        "result_file_sha256": _file_sha256(evidence_dir / "result.json"),
        "completed_at_utc": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
    }
    _atomic_json(evidence_dir / "terminal.json", terminal)
    marker = "COMPLETE" if status == STATUS_EQUAL else status
    (evidence_dir / marker).write_text(
        _sha256(_canonical_bytes(terminal)) + "\n", encoding="ascii", newline="\n"
    )
    print(json.dumps(terminal, sort_keys=True))
    return exit_code


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    evidence_root = project_root / "reports" / "s2jr"
    local_root = Path(os.environ["LOCALAPPDATA"]) / "MCM_FIELD_ORGANISM" / "s2jr"
    return run_once(project_root, evidence_root, local_root)


if __name__ == "__main__":
    raise SystemExit(main())
