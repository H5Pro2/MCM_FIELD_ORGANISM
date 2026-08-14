"""One-tick technical browser capability smoke for the bound Z4-A2 runtime."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from hashlib import sha256
from pathlib import Path
from typing import Any, Callable

import numpy as np

from .z4a_browser_receptor_adapter import (
    Z4ABrowserWorldContract,
    reference_z4a_browser_world_contract,
    z4a_browser_asset_digests,
)
from .z4a_playwright_runtime_binding import Z4APlaywrightRuntimeBinding


class Z4APlaywrightSmokeError(ValueError):
    """Raised when the bound browser fails the minimal one-tick capability gate."""


@dataclass(frozen=True, slots=True)
class Z4APlaywrightSmokeReceipt:
    smoke_id: str
    world_id: str
    package_version: str
    engine_version_bound: str
    engine_version_observed: str
    executable_sha256: str
    asset_digests: tuple[tuple[str, str], ...]
    rendered_tick_ns: int
    canvas_width: int
    canvas_height: int
    png_size_bytes: int
    png_sha256: str
    blocked_request_count: int
    browser_started: bool
    browser_closed: bool
    raw_png_retained: bool = False

    def __post_init__(self) -> None:
        if self.smoke_id != "z4a.playwright.one-tick.v1":
            raise Z4APlaywrightSmokeError("browser smoke identity changed")
        if self.engine_version_bound != self.engine_version_observed:
            raise Z4APlaywrightSmokeError("observed browser version differs from binding")
        if self.rendered_tick_ns != 0:
            raise Z4APlaywrightSmokeError("browser smoke may render only tick zero")
        if (self.canvas_width, self.canvas_height) != (480, 480):
            raise Z4APlaywrightSmokeError("browser canvas dimensions changed")
        if self.png_size_bytes <= 8 or len(self.png_sha256) != 64:
            raise Z4APlaywrightSmokeError("browser PNG evidence is invalid")
        if self.blocked_request_count != 0:
            raise Z4APlaywrightSmokeError("browser attempted a non-local request")
        if not self.browser_started or not self.browser_closed:
            raise Z4APlaywrightSmokeError("browser smoke lifecycle is incomplete")
        if self.raw_png_retained:
            raise Z4APlaywrightSmokeError("browser smoke cannot retain PNG bytes")


def _hash_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _decode_png_shape(png: bytes) -> tuple[int, int]:
    if not isinstance(png, bytes) or not png.startswith(b"\x89PNG\r\n\x1a\n"):
        raise Z4APlaywrightSmokeError("canvas screenshot is not a PNG")
    try:
        import cv2

        image = cv2.imdecode(np.frombuffer(png, dtype=np.uint8), cv2.IMREAD_COLOR)
    except Exception as exc:
        raise Z4APlaywrightSmokeError("canvas PNG decode failed") from exc
    if image is None or image.ndim != 3 or image.shape[2] != 3:
        raise Z4APlaywrightSmokeError("canvas PNG has no RGB image")
    return int(image.shape[1]), int(image.shape[0])


def run_z4a_playwright_smoke(
    binding: Z4APlaywrightRuntimeBinding,
    *,
    asset_directory: Path,
    contract: Z4ABrowserWorldContract | None = None,
    playwright_factory: Callable[[], Any] | None = None,
) -> Z4APlaywrightSmokeReceipt:
    """Start the bound binary once, render tick zero, and close immediately."""

    if not isinstance(binding, Z4APlaywrightRuntimeBinding):
        raise Z4APlaywrightSmokeError("smoke requires one runtime binding")
    world = contract or reference_z4a_browser_world_contract()
    if not isinstance(world, Z4ABrowserWorldContract):
        raise Z4APlaywrightSmokeError("smoke requires one bound browser world")
    executable = Path(binding.executable_real_path)
    if executable.is_symlink() or not executable.is_file():
        raise Z4APlaywrightSmokeError("bound browser binary is unavailable")
    if executable.stat().st_size != binding.executable_size_bytes:
        raise Z4APlaywrightSmokeError("bound browser binary size changed")
    if _hash_file(executable) != binding.executable_sha256:
        raise Z4APlaywrightSmokeError("bound browser binary digest changed")
    root = Path(asset_directory).resolve(strict=True)
    asset_digests = z4a_browser_asset_digests(root)
    index_url = (root / "index.html").resolve(strict=True).as_uri()

    if playwright_factory is None:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise Z4APlaywrightSmokeError("Playwright runtime is unavailable") from exc
        playwright_factory = sync_playwright

    browser = None
    context = None
    browser_started = False
    browser_closed = False
    blocked_requests: list[str] = []
    observed_version = ""
    png_size = 0
    png_digest = ""
    canvas_width = 0
    canvas_height = 0
    with playwright_factory() as playwright:
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
            context = browser.new_context(
                viewport={"width": 480, "height": 480},
                device_scale_factor=1,
                java_script_enabled=True,
                accept_downloads=False,
                service_workers="block",
            )
            page = context.new_page()

            def guard(route: Any, request: Any) -> None:
                if not request.url.startswith(root.as_uri() + "/"):
                    blocked_requests.append(request.url)
                    route.abort("blockedbyclient")
                else:
                    route.continue_()

            page.route("**/*", guard)
            page.goto(index_url, wait_until="networkidle")
            if page.url != index_url or blocked_requests:
                raise Z4APlaywrightSmokeError("browser left the local asset boundary")
            page.evaluate("worldId => window.configureWorld(worldId)", world.world_id)
            page.evaluate("tickNs => window.renderVisualAt(tickNs)", 0)
            dimensions = page.evaluate(
                "() => ({width: document.querySelector('#world').width, height: document.querySelector('#world').height})"
            )
            if not isinstance(dimensions, dict):
                raise Z4APlaywrightSmokeError("canvas dimension query failed")
            canvas_width = int(dimensions.get("width", 0))
            canvas_height = int(dimensions.get("height", 0))
            png = page.locator("canvas#world").screenshot(
                type="png",
                animations="disabled",
            )
            decoded_width, decoded_height = _decode_png_shape(png)
            if (decoded_width, decoded_height) != (canvas_width, canvas_height):
                raise Z4APlaywrightSmokeError("PNG and canvas dimensions differ")
            png_size = len(png)
            png_digest = sha256(png).hexdigest()
            del png
        finally:
            if context is not None:
                context.close()
            if browser is not None:
                browser.close()
                browser_closed = True

    return Z4APlaywrightSmokeReceipt(
        smoke_id="z4a.playwright.one-tick.v1",
        world_id=world.world_id,
        package_version=binding.package_version,
        engine_version_bound=binding.engine_version,
        engine_version_observed=observed_version,
        executable_sha256=binding.executable_sha256,
        asset_digests=asset_digests,
        rendered_tick_ns=0,
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        png_size_bytes=png_size,
        png_sha256=png_digest,
        blocked_request_count=len(blocked_requests),
        browser_started=browser_started,
        browser_closed=browser_closed,
    )


def z4a_playwright_smoke_json_value(
    receipt: Z4APlaywrightSmokeReceipt,
) -> dict[str, object]:
    if not isinstance(receipt, Z4APlaywrightSmokeReceipt):
        raise Z4APlaywrightSmokeError("JSON projection requires a smoke receipt")
    return asdict(receipt)


def z4a_playwright_smoke_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(Z4APlaywrightSmokeReceipt))
