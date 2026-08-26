"""OfflineAudio boundary smoke for the bound Z4-A2 browser runtime."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from hashlib import sha256
import json
import math
from pathlib import Path
from typing import Any, Callable, Iterable

from .z4a_browser_receptor_adapter import (
    Z4ABrowserWorldContract,
    reference_z4a_browser_world_contract,
    z4a_browser_asset_digests,
)
from .z4a_playwright_runtime_binding import Z4APlaywrightRuntimeBinding


class Z4APlaywrightAudioSmokeError(ValueError):
    """Raised when browser OfflineAudio violates the minimal boundary gate."""


@dataclass(frozen=True, slots=True)
class Z4APlaywrightAudioSmokeReceipt:
    smoke_id: str
    world_id: str
    engine_version_bound: str
    engine_version_observed: str
    executable_sha256: str
    asset_digests: tuple[tuple[str, str], ...]
    rendered_sample_count: int
    first_chunk_index: int
    last_chunk_index: int
    first_chunk_size: int
    last_chunk_size: int
    first_chunk_max_abs: float
    last_chunk_max_abs: float
    first_chunk_sha256: str
    last_chunk_sha256: str
    blocked_request_count: int
    audio_buffer_released: bool
    browser_started: bool
    browser_closed: bool
    raw_samples_retained: bool = False

    def __post_init__(self) -> None:
        if self.smoke_id != "z4a.playwright.offline-audio-boundary.v1":
            raise Z4APlaywrightAudioSmokeError("audio smoke identity changed")
        if self.engine_version_bound != self.engine_version_observed:
            raise Z4APlaywrightAudioSmokeError("observed browser version differs")
        if self.rendered_sample_count != 1_680_000:
            raise Z4APlaywrightAudioSmokeError("offline audio length changed")
        if (self.first_chunk_index, self.last_chunk_index) != (0, 3499):
            raise Z4APlaywrightAudioSmokeError("audio boundary indices changed")
        if (self.first_chunk_size, self.last_chunk_size) != (480, 480):
            raise Z4APlaywrightAudioSmokeError("audio boundary chunk size changed")
        for role in ("first_chunk_max_abs", "last_chunk_max_abs"):
            value = getattr(self, role)
            if not math.isfinite(value) or value < 0.0 or value > 1.0:
                raise Z4APlaywrightAudioSmokeError(f"{role} is invalid")
        for role in ("first_chunk_sha256", "last_chunk_sha256"):
            if len(getattr(self, role)) != 64:
                raise Z4APlaywrightAudioSmokeError(f"{role} is invalid")
        if self.blocked_request_count != 0:
            raise Z4APlaywrightAudioSmokeError("browser attempted a non-local request")
        if not self.audio_buffer_released:
            raise Z4APlaywrightAudioSmokeError("browser audio buffer was not released")
        if not self.browser_started or not self.browser_closed:
            raise Z4APlaywrightAudioSmokeError("browser lifecycle is incomplete")
        if self.raw_samples_retained:
            raise Z4APlaywrightAudioSmokeError("audio smoke cannot retain samples")


def _hash_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _validated_chunk(values: Iterable[float], role: str) -> tuple[float, ...]:
    try:
        chunk = tuple(float(value) for value in values)
    except (TypeError, ValueError) as exc:
        raise Z4APlaywrightAudioSmokeError(f"{role} chunk is not numeric") from exc
    if len(chunk) != 480:
        raise Z4APlaywrightAudioSmokeError(f"{role} chunk size changed")
    if any(not math.isfinite(value) or abs(value) > 1.0 for value in chunk):
        raise Z4APlaywrightAudioSmokeError(f"{role} chunk left the finite PCM domain")
    return chunk


def _chunk_digest(chunk: tuple[float, ...]) -> str:
    encoded = json.dumps(
        chunk,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("ascii")
    return sha256(encoded).hexdigest()


def run_z4a_playwright_audio_smoke(
    binding: Z4APlaywrightRuntimeBinding,
    *,
    asset_directory: Path,
    contract: Z4ABrowserWorldContract | None = None,
    playwright_factory: Callable[[], Any] | None = None,
) -> Z4APlaywrightAudioSmokeReceipt:
    """Render one browser audio buffer and inspect only its boundary chunks."""

    if not isinstance(binding, Z4APlaywrightRuntimeBinding):
        raise Z4APlaywrightAudioSmokeError("audio smoke requires a runtime binding")
    world = contract or reference_z4a_browser_world_contract()
    if not isinstance(world, Z4ABrowserWorldContract):
        raise Z4APlaywrightAudioSmokeError("audio smoke requires a bound world")
    executable = Path(binding.executable_real_path)
    if executable.is_symlink() or not executable.is_file():
        raise Z4APlaywrightAudioSmokeError("bound browser binary is unavailable")
    if executable.stat().st_size != binding.executable_size_bytes:
        raise Z4APlaywrightAudioSmokeError("bound browser binary size changed")
    if _hash_file(executable) != binding.executable_sha256:
        raise Z4APlaywrightAudioSmokeError("bound browser binary digest changed")
    root = Path(asset_directory).resolve(strict=True)
    asset_digests = z4a_browser_asset_digests(root)
    index_url = (root / "index.html").resolve(strict=True).as_uri()

    if playwright_factory is None:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise Z4APlaywrightAudioSmokeError("Playwright runtime is unavailable") from exc
        playwright_factory = sync_playwright

    browser = None
    context = None
    page = None
    browser_started = False
    browser_closed = False
    audio_rendered = False
    audio_released = False
    blocked_requests: list[str] = []
    observed_version = ""
    rendered_count = 0
    first: tuple[float, ...] = ()
    last: tuple[float, ...] = ()

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
                raise Z4APlaywrightAudioSmokeError("browser left local asset boundary")
            page.evaluate("worldId => window.configureWorld(worldId)", world.world_id)
            rendered_count = page.evaluate("() => window.renderAudio()")
            audio_rendered = True
            if rendered_count != 1_680_000:
                raise Z4APlaywrightAudioSmokeError("offline audio length changed")
            first = _validated_chunk(
                page.evaluate("index => window.readAudioChunk(index)", 0),
                "first",
            )
            last = _validated_chunk(
                page.evaluate("index => window.readAudioChunk(index)", 3499),
                "last",
            )
        finally:
            try:
                if page is not None and audio_rendered:
                    page.evaluate("() => window.releaseAudio()")
                    audio_released = True
            finally:
                try:
                    if context is not None:
                        context.close()
                finally:
                    if browser is not None:
                        browser.close()
                        browser_closed = True

    return Z4APlaywrightAudioSmokeReceipt(
        smoke_id="z4a.playwright.offline-audio-boundary.v1",
        world_id=world.world_id,
        engine_version_bound=binding.engine_version,
        engine_version_observed=observed_version,
        executable_sha256=binding.executable_sha256,
        asset_digests=asset_digests,
        rendered_sample_count=rendered_count,
        first_chunk_index=0,
        last_chunk_index=3499,
        first_chunk_size=len(first),
        last_chunk_size=len(last),
        first_chunk_max_abs=max(abs(value) for value in first),
        last_chunk_max_abs=max(abs(value) for value in last),
        first_chunk_sha256=_chunk_digest(first),
        last_chunk_sha256=_chunk_digest(last),
        blocked_request_count=len(blocked_requests),
        audio_buffer_released=audio_released,
        browser_started=browser_started,
        browser_closed=browser_closed,
    )


def z4a_playwright_audio_smoke_json_value(
    receipt: Z4APlaywrightAudioSmokeReceipt,
) -> dict[str, object]:
    if not isinstance(receipt, Z4APlaywrightAudioSmokeReceipt):
        raise Z4APlaywrightAudioSmokeError("JSON projection requires an audio receipt")
    return asdict(receipt)


def z4a_playwright_audio_smoke_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(Z4APlaywrightAudioSmokeReceipt))
