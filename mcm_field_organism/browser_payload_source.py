"""Direct local browser payload handoff into the generic receptor bridge."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any, Protocol
from urllib.parse import unquote, urlparse

from .browser_receptor_bridge import (
    BrowserReceptorBridge,
    BrowserReceptorSequenceBatch,
)
from .browser_world_contract import BrowserWorldContract
from .receptor_contract import technical_identifier


class BrowserPayloadSourceError(ValueError):
    """Raised when the local browser payload boundary is not reproducible."""


_ASSET_NAMES = frozenset(("index.html", "styles.css", "world.js"))
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _rgb(values: object, role: str) -> tuple[int, int, int]:
    try:
        result = tuple(values)  # type: ignore[arg-type]
    except TypeError as exc:
        raise BrowserPayloadSourceError(f"{role} must contain three channels") from exc
    if (
        len(result) != 3
        or any(
            isinstance(value, bool)
            or not isinstance(value, int)
            or value < 0
            or value > 255
            for value in result
        )
    ):
        raise BrowserPayloadSourceError(
            f"{role} must contain three integer channels within 0..255"
        )
    return result  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class BrowserPayloadSourceConfig:
    source_id: str
    canvas_width: int
    canvas_height: int
    device_scale_factor: int
    visual_frames_per_second: float
    motion_axis: str
    motion_amplitude_fraction: float
    foreground_size_fraction: float
    background_rgb: tuple[int, int, int]
    foreground_rgb: tuple[int, int, int]
    audio_sample_rate: int
    audio_hop_size: int
    audio_channel_count: int = 1
    oscillator_type: str = "sine"

    def __post_init__(self) -> None:
        try:
            source_id = technical_identifier(self.source_id, "source_id")
        except ValueError as exc:
            raise BrowserPayloadSourceError(str(exc)) from exc
        integer_roles = (
            ("canvas_width", self.canvas_width),
            ("canvas_height", self.canvas_height),
            ("audio_sample_rate", self.audio_sample_rate),
            ("audio_hop_size", self.audio_hop_size),
        )
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value <= 0
            for _, value in integer_roles
        ):
            raise BrowserPayloadSourceError(
                "canvas and audio dimensions must be positive integers"
            )
        if self.device_scale_factor != 1:
            raise BrowserPayloadSourceError("device_scale_factor must equal one")
        rate = float(self.visual_frames_per_second)
        amplitude = float(self.motion_amplitude_fraction)
        size = float(self.foreground_size_fraction)
        if not math.isfinite(rate) or rate <= 0.0:
            raise BrowserPayloadSourceError(
                "visual_frames_per_second must be finite and positive"
            )
        if (
            not math.isfinite(amplitude)
            or not math.isfinite(size)
            or amplitude < 0.0
            or size <= 0.0
            or amplitude + size / 2.0 > 0.5
        ):
            raise BrowserPayloadSourceError(
                "motion and foreground fractions must keep the foreground on canvas"
            )
        if self.motion_axis not in {"horizontal", "vertical"}:
            raise BrowserPayloadSourceError(
                "motion_axis must be horizontal or vertical"
            )
        if self.audio_channel_count != 1 or self.oscillator_type != "sine":
            raise BrowserPayloadSourceError(
                "browser audio source must remain monoaural sine"
            )
        object.__setattr__(self, "source_id", source_id)
        object.__setattr__(self, "visual_frames_per_second", rate)
        object.__setattr__(self, "motion_amplitude_fraction", amplitude)
        object.__setattr__(self, "foreground_size_fraction", size)
        object.__setattr__(self, "background_rgb", _rgb(self.background_rgb, "background_rgb"))
        object.__setattr__(self, "foreground_rgb", _rgb(self.foreground_rgb, "foreground_rgb"))

    def canonical_payload(self) -> dict[str, object]:
        return {
            item.name: (
                list(value)
                if item.name in {"background_rgb", "foreground_rgb"}
                else value
            )
            for item in fields(self)
            for value in (getattr(self, item.name),)
        }

    def digest(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(),
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class BrowserPayloadCapturePreflight:
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
            or isinstance(self.viewport_width, bool)
            or not isinstance(self.viewport_width, int)
            or self.viewport_width <= 0
            or isinstance(self.viewport_height, bool)
            or not isinstance(self.viewport_height, int)
            or self.viewport_height <= 0
            or self.device_scale_factor != 1
            or self.java_script_enabled is not True
        ):
            raise BrowserPayloadSourceError(
                "browser payload capture preflight is not isolated and bound"
            )


@dataclass(frozen=True, slots=True)
class BrowserPayloadCaptureReceipt:
    source_id: str
    world_contract_digest: str
    source_config_digest: str
    asset_digests: tuple[tuple[str, str], ...]
    local_request_count: int
    blocked_request_count: int
    visual_png_count: int
    audio_chunk_count: int
    rendered_audio_sample_count: int
    audio_total_energy: float
    batch_digest: str
    audio_buffer_released: bool
    raw_payloads_retained: bool = False

    def __post_init__(self) -> None:
        try:
            source_id = technical_identifier(self.source_id, "source_id")
        except ValueError as exc:
            raise BrowserPayloadSourceError(str(exc)) from exc
        digests = tuple(tuple(item) for item in self.asset_digests)
        if (
            not _SHA256.fullmatch(self.world_contract_digest)
            or not _SHA256.fullmatch(self.source_config_digest)
            or not _SHA256.fullmatch(self.batch_digest)
            or tuple(name for name, _ in digests) != tuple(sorted(_ASSET_NAMES))
            or any(not _SHA256.fullmatch(digest) for _, digest in digests)
        ):
            raise BrowserPayloadSourceError("capture receipt digests are invalid")
        counts = (
            self.local_request_count,
            self.visual_png_count,
            self.audio_chunk_count,
            self.rendered_audio_sample_count,
        )
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value <= 0
            for value in counts
        ):
            raise BrowserPayloadSourceError(
                "capture receipt requires positive technical counts"
            )
        if self.blocked_request_count != 0:
            raise BrowserPayloadSourceError(
                "capture receipt cannot contain blocked foreign requests"
            )
        energy = float(self.audio_total_energy)
        if not math.isfinite(energy) or energy <= 0.0:
            raise BrowserPayloadSourceError(
                "capture receipt requires positive finite audio energy"
            )
        if self.audio_buffer_released is not True or self.raw_payloads_retained:
            raise BrowserPayloadSourceError(
                "capture receipt must release audio and retain no raw payload"
            )
        object.__setattr__(self, "source_id", source_id)
        object.__setattr__(self, "asset_digests", digests)
        object.__setattr__(self, "audio_total_energy", energy)


class _Request(Protocol):
    @property
    def url(self) -> str: ...


class _Route(Protocol):
    def abort(self, error_code: str = "blockedbyclient") -> Any: ...

    def continue_(self) -> Any: ...


class _Locator(Protocol):
    def screenshot(self, **kwargs: object) -> bytes: ...


class BrowserPayloadPage(Protocol):
    @property
    def url(self) -> str: ...

    def route(self, url: str, handler: object) -> Any: ...

    def goto(self, url: str, **kwargs: object) -> Any: ...

    def evaluate(self, expression: str, arg: object | None = None) -> Any: ...

    def locator(self, selector: str) -> _Locator: ...


def browser_payload_asset_digests(
    asset_directory: Path,
) -> tuple[tuple[str, str], ...]:
    root = Path(asset_directory).resolve(strict=True)
    if not root.is_dir():
        raise BrowserPayloadSourceError("browser payload asset root is not a directory")
    output = []
    for name in sorted(_ASSET_NAMES):
        path = (root / name).resolve(strict=True)
        if path.parent != root or not path.is_file():
            raise BrowserPayloadSourceError("browser payload asset escaped its root")
        output.append((name, hashlib.sha256(path.read_bytes()).hexdigest()))
    return tuple(output)


def _asset_file_url(asset_directory: Path, name: str) -> str:
    path = (asset_directory / name).resolve(strict=True)
    if path.parent != asset_directory:
        raise BrowserPayloadSourceError("browser payload asset escaped its root")
    return path.as_uri()


def _local_asset_name(url: str, asset_directory: Path) -> str | None:
    parsed = urlparse(url)
    if parsed.scheme != "file" or parsed.query or parsed.fragment:
        return None
    try:
        raw_path = unquote(parsed.path)
        if re.fullmatch(r"/[A-Za-z]:/.*", raw_path):
            raw_path = raw_path[1:]
        candidate = Path(raw_path).resolve(strict=False)
    except (OSError, ValueError):
        return None
    if candidate.parent != asset_directory or candidate.name not in _ASSET_NAMES:
        return None
    return candidate.name


def _validate_source_bridge_compatibility(
    source_config: BrowserPayloadSourceConfig,
    bridge: BrowserReceptorBridge,
) -> None:
    visual = bridge.visual_receptor.config
    audio = bridge.auditory_path.receptor.config
    if (
        source_config.canvas_width != visual.source_width
        or source_config.canvas_height != visual.source_height
        or source_config.visual_frames_per_second != visual.frames_per_second
        or source_config.audio_sample_rate != audio.sample_rate
        or source_config.audio_hop_size != audio.hop_size
    ):
        raise BrowserPayloadSourceError(
            "browser source and receptor bridge configurations differ"
        )


def capture_browser_payload_page(
    page: BrowserPayloadPage,
    contract: BrowserWorldContract,
    source_config: BrowserPayloadSourceConfig,
    receptor_bridge: BrowserReceptorBridge,
    *,
    asset_directory: Path,
    preflight: BrowserPayloadCapturePreflight,
) -> tuple[BrowserReceptorSequenceBatch, BrowserPayloadCaptureReceipt]:
    """Capture one already-created local page without launching a browser."""

    if not isinstance(contract, BrowserWorldContract):
        raise BrowserPayloadSourceError("capture requires a BrowserWorldContract")
    if not isinstance(source_config, BrowserPayloadSourceConfig):
        raise BrowserPayloadSourceError(
            "capture requires a BrowserPayloadSourceConfig"
        )
    if not isinstance(receptor_bridge, BrowserReceptorBridge):
        raise BrowserPayloadSourceError("capture requires a BrowserReceptorBridge")
    if receptor_bridge.contract != contract:
        raise BrowserPayloadSourceError("world and receptor bridge contracts differ")
    if not isinstance(preflight, BrowserPayloadCapturePreflight):
        raise BrowserPayloadSourceError(
            "capture requires a BrowserPayloadCapturePreflight"
        )
    if (
        preflight.viewport_width != source_config.canvas_width
        or preflight.viewport_height != source_config.canvas_height
        or preflight.device_scale_factor != source_config.device_scale_factor
    ):
        raise BrowserPayloadSourceError("preflight and source geometry differ")
    _validate_source_bridge_compatibility(source_config, receptor_bridge)

    root = Path(asset_directory).resolve(strict=True)
    asset_digests = browser_payload_asset_digests(root)
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
        raise BrowserPayloadSourceError("browser page left the local asset origin")
    if blocked_requests:
        raise BrowserPayloadSourceError(
            "browser payload world attempted a non-local request"
        )
    if tuple(sorted(local_requests)) != tuple(sorted(_ASSET_NAMES)):
        raise BrowserPayloadSourceError(
            "browser payload world did not load the exact local asset inventory"
        )

    page.evaluate(
        "payload => window.configureWorld(payload.world, payload.source)",
        {
            "source": source_config.canonical_payload(),
            "world": contract.canonical_payload(),
        },
    )
    canvas = page.locator("canvas#world")
    for frame_index in range(receptor_bridge.expected_visual_frame_count):
        page.evaluate("index => window.renderVisualFrame(index)", frame_index)
        payload = canvas.screenshot(type="png", animations="disabled")
        receptor_bridge.push_visual_png(payload, frame_index=frame_index)

    rendered_sample_count = page.evaluate("() => window.renderAudio()")
    expected_sample_count = (
        receptor_bridge.expected_audio_chunk_count * source_config.audio_hop_size
    )
    if rendered_sample_count != expected_sample_count:
        raise BrowserPayloadSourceError("browser offline audio inventory changed")
    audio_buffer_released = False
    audio_energy_terms: list[float] = []
    try:
        for chunk_index in range(receptor_bridge.expected_audio_chunk_count):
            samples = page.evaluate(
                "index => window.readAudioChunk(index)",
                chunk_index,
            )
            try:
                samples = tuple(float(value) for value in samples)
            except (TypeError, ValueError) as exc:
                raise BrowserPayloadSourceError(
                    "browser audio chunk contains non-numeric samples"
                ) from exc
            if any(not math.isfinite(value) for value in samples):
                raise BrowserPayloadSourceError(
                    "browser audio chunk contains non-finite samples"
                )
            audio_energy_terms.extend(value * value for value in samples)
            receptor_bridge.push_audio_chunk(samples, chunk_index=chunk_index)
    finally:
        page.evaluate("() => window.releaseAudio()")
        audio_buffer_released = True

    batch = receptor_bridge.finalize()
    return batch, BrowserPayloadCaptureReceipt(
        source_id=source_config.source_id,
        world_contract_digest=contract.digest(),
        source_config_digest=source_config.digest(),
        asset_digests=asset_digests,
        local_request_count=len(local_requests),
        blocked_request_count=len(blocked_requests),
        visual_png_count=receptor_bridge.expected_visual_frame_count,
        audio_chunk_count=receptor_bridge.expected_audio_chunk_count,
        rendered_audio_sample_count=rendered_sample_count,
        audio_total_energy=math.fsum(audio_energy_terms),
        batch_digest=batch.digest(),
        audio_buffer_released=audio_buffer_released,
    )


def browser_payload_source_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for role in (
            BrowserPayloadSourceConfig,
            BrowserPayloadCapturePreflight,
            BrowserPayloadCaptureReceipt,
        )
        for item in fields(role)
    )
