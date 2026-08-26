"""Strict Playwright-page handoff for the camera-free Z4-A2 browser worlds."""

from __future__ import annotations

from dataclasses import dataclass, fields
from pathlib import Path
import re
from typing import Any, Protocol
from urllib.parse import unquote, urlparse

from .receptor_time_alignment import ReceptorTimeSequence
from .z4a_browser_receptor_adapter import (
    Z4A_BROWSER_AUDIO_CHUNK_COUNT,
    Z4A_BROWSER_VISUAL_FRAME_COUNT,
    Z4ABrowserReceptorAdapter,
    Z4ABrowserWorldContract,
    z4a_browser_asset_digests,
)


class Z4APlaywrightCaptureError(ValueError):
    """Raised before or during a browser payload handoff contract violation."""


class _Request(Protocol):
    @property
    def url(self) -> str: ...


class _Route(Protocol):
    def abort(self, error_code: str = "blockedbyclient") -> Any: ...

    def continue_(self) -> Any: ...


class _Locator(Protocol):
    def screenshot(self, **kwargs: object) -> bytes: ...


class Z4APlaywrightPage(Protocol):
    @property
    def url(self) -> str: ...

    def route(self, url: str, handler: object) -> Any: ...

    def goto(self, url: str, **kwargs: object) -> Any: ...

    def evaluate(self, expression: str, arg: object | None = None) -> Any: ...

    def locator(self, selector: str) -> _Locator: ...


@dataclass(frozen=True, slots=True)
class Z4APlaywrightCapturePreflight:
    fresh_isolated_context: bool
    persistent_profile: bool
    extensions_enabled: bool
    viewport_width: int
    viewport_height: int
    device_scale_factor: int
    java_script_enabled: bool

    def __post_init__(self) -> None:
        if (
            self.fresh_isolated_context is not True
            or self.persistent_profile is not False
            or self.extensions_enabled is not False
            or self.viewport_width != 480
            or self.viewport_height != 480
            or self.device_scale_factor != 1
            or self.java_script_enabled is not True
        ):
            raise Z4APlaywrightCaptureError("Playwright context preflight is not bound")


@dataclass(frozen=True, slots=True)
class Z4APlaywrightCaptureReceipt:
    world_id: str
    asset_digests: tuple[tuple[str, str], ...]
    local_request_count: int
    blocked_request_count: int
    visual_png_count: int
    audio_chunk_count: int
    rendered_audio_sample_count: int
    raw_payloads_retained: bool = False

    def __post_init__(self) -> None:
        if self.blocked_request_count != 0:
            raise Z4APlaywrightCaptureError("browser world attempted a non-local request")
        if self.visual_png_count != Z4A_BROWSER_VISUAL_FRAME_COUNT:
            raise Z4APlaywrightCaptureError("visual capture inventory changed")
        if self.audio_chunk_count != Z4A_BROWSER_AUDIO_CHUNK_COUNT:
            raise Z4APlaywrightCaptureError("audio capture inventory changed")
        if self.rendered_audio_sample_count != 1_680_000:
            raise Z4APlaywrightCaptureError("offline audio sample inventory changed")
        if self.raw_payloads_retained:
            raise Z4APlaywrightCaptureError("capture receipt cannot retain raw payloads")


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_ASSET_NAMES = frozenset(("index.html", "styles.css", "world.js"))


def _asset_file_url(asset_directory: Path, name: str) -> str:
    path = (asset_directory / name).resolve(strict=True)
    if path.parent != asset_directory:
        raise Z4APlaywrightCaptureError("asset escaped the bound directory")
    return path.as_uri()


def _local_asset_name(url: str, asset_directory: Path) -> str | None:
    parsed = urlparse(url)
    if parsed.scheme != "file" or parsed.query or parsed.fragment:
        return None
    try:
        candidate = Path(unquote(parsed.path.lstrip("/"))).resolve(strict=False)
    except (OSError, ValueError):
        return None
    if candidate.parent != asset_directory or candidate.name not in _ASSET_NAMES:
        return None
    return candidate.name


def capture_z4a_playwright_page(
    page: Z4APlaywrightPage,
    contract: Z4ABrowserWorldContract,
    receptor_adapter: Z4ABrowserReceptorAdapter,
    *,
    asset_directory: Path,
    preflight: Z4APlaywrightCapturePreflight,
) -> tuple[
    tuple[ReceptorTimeSequence, ReceptorTimeSequence],
    Z4APlaywrightCaptureReceipt,
]:
    """Capture one already-created page without launching or retaining a browser."""

    if not isinstance(contract, Z4ABrowserWorldContract):
        raise Z4APlaywrightCaptureError("capture requires one bound browser contract")
    if not isinstance(receptor_adapter, Z4ABrowserReceptorAdapter):
        raise Z4APlaywrightCaptureError("capture requires the direct Z4-A2 adapter")
    if receptor_adapter.contract != contract:
        raise Z4APlaywrightCaptureError("page contract and receptor adapter differ")
    if not isinstance(preflight, Z4APlaywrightCapturePreflight):
        raise Z4APlaywrightCaptureError("capture requires a validated preflight")

    root = Path(asset_directory).resolve(strict=True)
    asset_digests = z4a_browser_asset_digests(root)
    if any(not _SHA256.fullmatch(digest) for _, digest in asset_digests):
        raise Z4APlaywrightCaptureError("asset digest is invalid")
    index_url = _asset_file_url(root, "index.html")
    local_requests: list[str] = []
    blocked_requests: list[str] = []

    def guard(route: _Route, request: _Request) -> None:
        name = _local_asset_name(request.url, root)
        if name is None:
            blocked_requests.append(request.url)
            route.abort("blockedbyclient")
            return
        local_requests.append(name)
        route.continue_()

    page.route("**/*", guard)
    page.goto(index_url, wait_until="networkidle")
    if page.url != index_url:
        raise Z4APlaywrightCaptureError("page left the bound local asset origin")
    if blocked_requests:
        raise Z4APlaywrightCaptureError("browser world attempted a non-local request")

    page.evaluate("worldId => window.configureWorld(worldId)", contract.world_id)
    canvas = page.locator("canvas#world")
    for frame_index in range(Z4A_BROWSER_VISUAL_FRAME_COUNT):
        tick_ns = frame_index * 40_000_000
        page.evaluate("tickNs => window.renderVisualAt(tickNs)", tick_ns)
        png = canvas.screenshot(type="png", animations="disabled")
        receptor_adapter.push_visual_png(png, frame_index=frame_index)

    rendered_sample_count = page.evaluate("() => window.renderAudio()")
    if rendered_sample_count != 1_680_000:
        raise Z4APlaywrightCaptureError("browser offline audio length changed")
    try:
        for chunk_index in range(Z4A_BROWSER_AUDIO_CHUNK_COUNT):
            samples = page.evaluate(
                "index => window.readAudioChunk(index)",
                chunk_index,
            )
            receptor_adapter.push_audio_chunk(samples, chunk_index=chunk_index)
    finally:
        page.evaluate("() => window.releaseAudio()")

    sequences = receptor_adapter.finalize()
    return sequences, Z4APlaywrightCaptureReceipt(
        world_id=contract.world_id,
        asset_digests=asset_digests,
        local_request_count=len(local_requests),
        blocked_request_count=len(blocked_requests),
        visual_png_count=Z4A_BROWSER_VISUAL_FRAME_COUNT,
        audio_chunk_count=Z4A_BROWSER_AUDIO_CHUNK_COUNT,
        rendered_audio_sample_count=rendered_sample_count,
    )


def z4a_playwright_capture_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (Z4APlaywrightCapturePreflight, Z4APlaywrightCaptureReceipt)
        for item in fields(cls)
    )
