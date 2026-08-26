"""Bound real-browser capability smoke for the generic browser payload path."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from pathlib import Path
import re
from typing import Any, Callable

from .audio_video_neutral_field_runtime import (
    advance_audio_video_receptor_sequences,
)
from .broadband_hearing_path import BroadbandHearingPath
from .browser_payload_runtime import (
    BrowserPayloadRuntimeBinding,
    BrowserPayloadRuntimeBindingError,
    verify_browser_payload_runtime_binding,
)
from .browser_payload_source import (
    BrowserPayloadCapturePreflight,
    BrowserPayloadCaptureReceipt,
    BrowserPayloadSourceConfig,
    browser_payload_asset_digests,
    capture_browser_payload_page,
)
from .browser_receptor_bridge import BrowserReceptorBridge
from .browser_world_contract import BrowserWorldContract, BrowserWorldPhase
from .finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from .log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from .neutral_local_field_substrate import NeutralLocalFieldSubstrateConfig


class BrowserPayloadSmokeError(ValueError):
    """Raised when the bound generic browser smoke cannot complete exactly."""


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_W1F_RUNTIME_IDENTITY = (
    "1.62.0",
    "151.0.7922.34",
    "1234",
    "6d838da3367601bc8911715ee2fd6b102c48e553933093c48904609beacdc5d2",
    "f306eed529599b1eaf2f8a85db9de2b23e1a3fe36c2b66434b7c9434fb627a99",
    "ce4635cd0e5dc0e21494542a701f347e91c1f1d821970578d97ed8df4ced50ef",
)
_W1F_ASSET_DIGESTS = (
    ("index.html", "74fc372a3eff08ac38e803689e562ce5acbb39d56d3351db475c768457e32af8"),
    ("styles.css", "f026fce8f826fb7364a11b1b05ad4acb3dd37aed7dede5453c6f82cbf497b594"),
    ("world.js", "fda8c774708af883eb97625b7064ec288c06e2819619fb2eb93e281212d32158"),
)


@dataclass(frozen=True, slots=True)
class BrowserPayloadSmokeReceipt:
    smoke_id: str
    package_version: str
    engine_version_bound: str
    engine_version_observed: str
    browser_revision: str
    requirements_sha256: str
    manifest_sha256: str
    executable_sha256: str
    world_contract_digest: str
    source_config_digest: str
    asset_digests: tuple[tuple[str, str], ...]
    capture_receipt: BrowserPayloadCaptureReceipt
    auditory_state_count: int
    visual_state_count: int
    assigned_event_count: int
    batch_digest: str
    field_snapshot_digest: str
    page_created: bool
    page_closed: bool
    context_created: bool
    context_closed: bool
    browser_started: bool
    browser_closed: bool
    raw_payloads_retained: bool = False

    def __post_init__(self) -> None:
        if self.smoke_id != "browser.payload.real-smoke.v1":
            raise BrowserPayloadSmokeError("browser smoke identity changed")
        if self.engine_version_bound != self.engine_version_observed:
            raise BrowserPayloadSmokeError(
                "observed browser version differs from the static binding"
            )
        for role in (
            "requirements_sha256",
            "manifest_sha256",
            "executable_sha256",
            "world_contract_digest",
            "source_config_digest",
            "batch_digest",
            "field_snapshot_digest",
        ):
            if not _SHA256.fullmatch(getattr(self, role)):
                raise BrowserPayloadSmokeError(f"{role} is invalid")
        if not isinstance(self.capture_receipt, BrowserPayloadCaptureReceipt):
            raise BrowserPayloadSmokeError("smoke requires one capture receipt")
        if self.asset_digests != self.capture_receipt.asset_digests:
            raise BrowserPayloadSmokeError("smoke and capture asset digests differ")
        if (
            self.auditory_state_count != 21
            or self.visual_state_count != 3
            or self.assigned_event_count != 24
        ):
            raise BrowserPayloadSmokeError("browser smoke inventory changed")
        if self.capture_receipt.batch_digest != self.batch_digest:
            raise BrowserPayloadSmokeError("capture and smoke batch digests differ")
        lifecycle = (
            self.page_created,
            self.page_closed,
            self.context_created,
            self.context_closed,
            self.browser_started,
            self.browser_closed,
        )
        if any(value is not True for value in lifecycle):
            raise BrowserPayloadSmokeError("browser smoke lifecycle is incomplete")
        if not self.capture_receipt.audio_buffer_released:
            raise BrowserPayloadSmokeError("browser audio buffer was not released")
        if self.raw_payloads_retained:
            raise BrowserPayloadSmokeError("browser smoke cannot retain raw payloads")


def browser_payload_smoke_world_contract() -> BrowserWorldContract:
    return BrowserWorldContract(
        contract_id="browser.world.payload.smoke.v1",
        startup_frame_count=1,
        start_lead_ns=1,
        movement_cycles=1,
        tone_frequency_hz=440.0,
        phases=(
            BrowserWorldPhase("rest.before", 100_000_000, "static", 0.0),
            BrowserWorldPhase("change", 100_000_000, "moving", 0.2),
            BrowserWorldPhase("rest.after", 100_000_000, "static", 0.0),
        ),
    )


def browser_payload_smoke_source_config() -> BrowserPayloadSourceConfig:
    return BrowserPayloadSourceConfig(
        source_id="browser.payload.smoke.v1",
        canvas_width=120,
        canvas_height=80,
        device_scale_factor=1,
        visual_frames_per_second=10.0,
        motion_axis="horizontal",
        motion_amplitude_fraction=0.2,
        foreground_size_fraction=0.2,
        background_rgb=(16, 24, 32),
        foreground_rgb=(224, 232, 240),
        audio_sample_rate=8000,
        audio_hop_size=80,
    )


def browser_payload_smoke_receptor_bridge() -> BrowserReceptorBridge:
    contract = browser_payload_smoke_world_contract()
    visual = LocalChannelGridReceptor(
        VisualGridConfig(
            source_width=120,
            source_height=80,
            grid_columns=3,
            grid_rows=2,
            frames_per_second=10.0,
        )
    )
    auditory = BroadbandHearingPath(
        LogSpectralReceptor(
            LogSpectralConfig(
                sample_rate=8000,
                window_size=800,
                hop_size=80,
                min_frequency=50.0,
                max_frequency=3000.0,
                band_count=8,
            )
        )
    )
    return BrowserReceptorBridge(contract, visual, auditory)


def validate_w1f_browser_payload_runtime(
    binding: BrowserPayloadRuntimeBinding,
) -> None:
    """Require the exact runtime identity bound before the real W1-H smoke."""

    identity = (
        binding.package_version,
        binding.engine_version,
        binding.browser_revision,
        binding.requirements_sha256,
        binding.manifest_sha256,
        binding.executable_sha256,
    )
    if identity != _W1F_RUNTIME_IDENTITY:
        raise BrowserPayloadSmokeError("bound runtime differs from W1-F")


def run_browser_payload_smoke(
    binding: BrowserPayloadRuntimeBinding,
    *,
    asset_directory: Path,
    playwright_factory: Callable[[], Any] | None = None,
    runtime_validator: Callable[[BrowserPayloadRuntimeBinding], None] = (
        validate_w1f_browser_payload_runtime
    ),
) -> BrowserPayloadSmokeReceipt:
    """Run one bound browser lifecycle; callers control whether it is real or fake."""

    try:
        verify_browser_payload_runtime_binding(binding)
    except BrowserPayloadRuntimeBindingError as exc:
        raise BrowserPayloadSmokeError(str(exc)) from exc
    if not callable(runtime_validator):
        raise BrowserPayloadSmokeError("runtime_validator must be callable")
    runtime_validator(binding)
    assets = browser_payload_asset_digests(Path(asset_directory))
    if assets != _W1F_ASSET_DIGESTS:
        raise BrowserPayloadSmokeError("browser payload assets differ from W1-F")
    contract = browser_payload_smoke_world_contract()
    source_config = browser_payload_smoke_source_config()
    bridge = browser_payload_smoke_receptor_bridge()
    if playwright_factory is None:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise BrowserPayloadSmokeError("Playwright runtime is unavailable") from exc
        playwright_factory = sync_playwright

    browser = None
    context = None
    page = None
    browser_started = False
    browser_closed = False
    context_created = False
    context_closed = False
    page_created = False
    page_closed = False
    observed_version = ""
    batch = None
    capture_receipt = None
    field_snapshot_digest = ""
    assigned_event_count = 0

    with playwright_factory() as playwright:
        try:
            browser = playwright.chromium.launch(
                executable_path=binding.executable_real_path,
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
                viewport={"width": 120, "height": 80},
                device_scale_factor=1,
                java_script_enabled=True,
                accept_downloads=False,
                service_workers="block",
                permissions=[],
            )
            context_created = True
            page = context.new_page()
            page_created = True
            try:
                batch, capture_receipt = capture_browser_payload_page(
                    page,
                    contract,
                    source_config,
                    bridge,
                    asset_directory=asset_directory,
                    preflight=BrowserPayloadCapturePreflight(
                        fresh_isolated_context=True,
                        persistent_profile=False,
                        extensions_enabled=False,
                        viewport_width=120,
                        viewport_height=80,
                        device_scale_factor=1,
                        java_script_enabled=True,
                    ),
                )
                field = advance_audio_video_receptor_sequences(
                    batch.sequences,
                    bridge.visual_receptor,
                    NeutralLocalFieldSubstrateConfig(1.0),
                    ticks_per_second=1_000_000_000.0,
                )
                assigned_event_count = field.field_run.handoff.assigned_event_count
                field_snapshot_digest = field.field_run.field.snapshot().digest()
            finally:
                page.close()
                page_closed = True
        finally:
            try:
                if context is not None:
                    context.close()
                    context_closed = True
            finally:
                if browser is not None:
                    browser.close()
                    browser_closed = True

    if batch is None or capture_receipt is None:
        raise BrowserPayloadSmokeError("browser smoke produced no completed capture")
    auditory, visual = batch.sequences
    return BrowserPayloadSmokeReceipt(
        smoke_id="browser.payload.real-smoke.v1",
        package_version=binding.package_version,
        engine_version_bound=binding.engine_version,
        engine_version_observed=observed_version,
        browser_revision=binding.browser_revision,
        requirements_sha256=binding.requirements_sha256,
        manifest_sha256=binding.manifest_sha256,
        executable_sha256=binding.executable_sha256,
        world_contract_digest=contract.digest(),
        source_config_digest=source_config.digest(),
        asset_digests=assets,
        capture_receipt=capture_receipt,
        auditory_state_count=len(auditory.frames),
        visual_state_count=len(visual.frames),
        assigned_event_count=assigned_event_count,
        batch_digest=batch.digest(),
        field_snapshot_digest=field_snapshot_digest,
        page_created=page_created,
        page_closed=page_closed,
        context_created=context_created,
        context_closed=context_closed,
        browser_started=browser_started,
        browser_closed=browser_closed,
    )


def browser_payload_smoke_json_value(
    receipt: BrowserPayloadSmokeReceipt,
) -> dict[str, object]:
    if not isinstance(receipt, BrowserPayloadSmokeReceipt):
        raise BrowserPayloadSmokeError("JSON projection requires a smoke receipt")
    return asdict(receipt)


def browser_payload_smoke_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(BrowserPayloadSmokeReceipt))
