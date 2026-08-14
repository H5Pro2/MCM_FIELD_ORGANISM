"""Exactly-once browser execution for the preregistered W6-I causal check."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Callable

from .broadband_hearing_path import BroadbandHearingPath
from .browser_payload_runtime import (
    BrowserPayloadRuntimeBinding,
    browser_payload_runtime_binding_json_value,
    verify_browser_payload_runtime_binding,
)
from .browser_payload_source import (
    BrowserPayloadCapturePreflight,
    BrowserPayloadCaptureReceipt,
    browser_payload_asset_digests,
    capture_browser_payload_page,
)
from .browser_receptor_bridge import BrowserReceptorBridge
from .finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from .log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from .s1b_causal_browser_execution_contract import (
    S1BCausalBrowserExecutionContract,
)
from .s1b_causal_browser_world import (
    S1BCausalBrowserWorldSet,
    s1b_causal_browser_world_set,
)
from .s1b_causal_capture_handoff import (
    prepare_s1b_causal_capture_handoff,
    run_s1b_causal_capture_handoff,
    s1b_causal_capture_schedule,
)


class S1BCausalBrowserOneShotError(RuntimeError):
    """Raised when W6-I cannot complete under its bound one-shot contract."""


@dataclass(frozen=True, slots=True)
class S1BCausalBrowserOneShotReceipt:
    execution_id: str
    report_path: str
    report_sha256: str
    contract_digest: str
    context_count: int
    atomic_publish_complete: bool

    def __post_init__(self) -> None:
        if (
            self.execution_id != "s1b.causal.browser.w6i.once.v1"
            or len(self.report_sha256) != 64
            or len(self.contract_digest) != 64
            or self.context_count != 3
            or self.atomic_publish_complete is not True
        ):
            raise S1BCausalBrowserOneShotError("invalid W6-I execution receipt")


def _exclusive_marker(path: Path, text: str) -> None:
    try:
        with path.open("x", encoding="ascii", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise S1BCausalBrowserOneShotError(
            f"W6-I one-shot marker already exists: {path.name}"
        ) from exc


def _runtime_binding_digest(binding: BrowserPayloadRuntimeBinding) -> str:
    encoded = json.dumps(
        browser_payload_runtime_binding_json_value(binding),
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _bridge(contract: object, source: object, config: object) -> BrowserReceptorBridge:
    visual = LocalChannelGridReceptor(
        VisualGridConfig(
            source_width=source.canvas_width,
            source_height=source.canvas_height,
            grid_columns=3,
            grid_rows=2,
            frames_per_second=source.visual_frames_per_second,
        )
    )
    auditory = BroadbandHearingPath(
        LogSpectralReceptor(
            LogSpectralConfig(
                sample_rate=source.audio_sample_rate,
                window_size=800,
                hop_size=source.audio_hop_size,
                min_frequency=50.0,
                max_frequency=3000.0,
                band_count=8,
            )
        )
    )
    return BrowserReceptorBridge(contract, visual, auditory, config)


def _capture_part(
    browser: Any,
    contract: object,
    source: object,
    bridge_config: object,
    *,
    asset_directory: Path,
) -> tuple[object, BrowserPayloadCaptureReceipt, bool, bool]:
    context = None
    page = None
    page_closed = False
    context_closed = False
    try:
        context = browser.new_context(
            viewport={"width": 120, "height": 80},
            device_scale_factor=1,
            java_script_enabled=True,
            accept_downloads=False,
            service_workers="block",
            permissions=[],
        )
        page = context.new_page()
        batch, receipt = capture_browser_payload_page(
            page,
            contract,
            source,
            _bridge(contract, source, bridge_config),
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
        return batch, receipt, True, True
    finally:
        try:
            if page is not None:
                page.close()
                page_closed = True
        finally:
            if context is not None:
                context.close()
                context_closed = True
        if page is not None and not page_closed:
            raise S1BCausalBrowserOneShotError("W6-I page did not close")
        if context is not None and not context_closed:
            raise S1BCausalBrowserOneShotError("W6-I context did not close")


def _report_value(
    execution_contract: S1BCausalBrowserExecutionContract,
    handoff: object,
    result: object,
    receipts: tuple[BrowserPayloadCaptureReceipt, ...],
    *,
    pages_closed: bool,
    contexts_closed: bool,
    browser_closed: bool,
) -> dict[str, object]:
    value = {
        "execution_id": execution_contract.execution_id,
        "world_set_digest": handoff.world_set_digest,
        "runtime_binding_digest": execution_contract.runtime_binding_digest,
        "asset_digests": [list(item) for item in handoff.asset_digests],
        "history_a_batch_digest": handoff.history_a_batch_digest,
        "history_b_batch_digest": handoff.history_b_batch_digest,
        "probe_batch_digest": handoff.probe_batch_digest,
        "formation_support_count_a": result.formation_support_count_a,
        "formation_support_count_b": result.formation_support_count_b,
        "probe_support_count": result.probe_support_count,
        "l_a_linf": result.l_a_linf,
        "l_b_linf": result.l_b_linf,
        "l_ab_linf": result.l_ab_linf,
        "d_rn_s": result.d_rn_s,
        "d_rx_s": result.d_rx_s,
        "d_xn_s": result.d_xn_s,
        "d_rn_h": result.d_rn_h,
        "d_rx_h": result.d_rx_h,
        "fast_r_n_equal": result.fast_r_n_equal,
        "fast_r_x_equal": result.fast_r_x_equal,
        "null_formation_equal": result.null_formation_equal,
        "null_probe_equal": result.null_probe_equal,
        "technical_decision": result.technical_decision,
        "raw_payloads_retained": any(item.raw_payloads_retained for item in receipts),
        "audio_buffers_released": all(item.audio_buffer_released for item in receipts),
        "pages_closed": pages_closed,
        "contexts_closed": contexts_closed,
        "browser_closed": browser_closed,
    }
    if tuple(value) != execution_contract.report_fields:
        raise S1BCausalBrowserOneShotError("W6-I report field order changed")
    return value


def _atomic_publish(target: Path, value: dict[str, object]) -> bytes:
    encoded = (
        json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=False,
        )
        + "\n"
    ).encode("ascii")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=target.name + ".tmp.",
        dir=target.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        if json.loads(temporary.read_text(encoding="ascii")) != value:
            raise S1BCausalBrowserOneShotError("W6-I temporary report reread failed")
        try:
            os.link(temporary, target)
        except FileExistsError as exc:
            raise S1BCausalBrowserOneShotError("W6-I report already exists") from exc
        if target.read_bytes() != encoded:
            raise S1BCausalBrowserOneShotError("W6-I published report differs")
        return encoded
    finally:
        temporary.unlink(missing_ok=True)


def execute_s1b_causal_browser_one_shot(
    execution_contract: S1BCausalBrowserExecutionContract,
    runtime_binding: BrowserPayloadRuntimeBinding,
    *,
    asset_directory: Path,
    world_set: S1BCausalBrowserWorldSet | None = None,
    playwright_factory: Callable[[], Any] | None = None,
) -> S1BCausalBrowserOneShotReceipt:
    """Execute and atomically report the one W6-I browser attempt."""

    if (
        not isinstance(execution_contract, S1BCausalBrowserExecutionContract)
        or execution_contract.preflight_decision
        != "READY_FOR_EXPLICIT_ONE_SHOT_BROWSER_EXECUTION"
        or not execution_contract.execution_permitted
        or execution_contract.browser_started
    ):
        raise S1BCausalBrowserOneShotError("W6-I requires one READY static contract")
    verify_browser_payload_runtime_binding(runtime_binding)
    if _runtime_binding_digest(runtime_binding) != execution_contract.runtime_binding_digest:
        raise S1BCausalBrowserOneShotError("W6-I runtime differs from preflight")
    if browser_payload_asset_digests(Path(asset_directory)) != tuple(
        execution_contract.asset_digests
    ):
        raise S1BCausalBrowserOneShotError("W6-I assets differ from preflight")
    worlds = s1b_causal_browser_world_set() if world_set is None else world_set
    if worlds.digest() != execution_contract.world_set_digest:
        raise S1BCausalBrowserOneShotError("W6-I world set differs from preflight")
    target = Path(execution_contract.report_path)
    attempt = Path(execution_contract.attempt_path)
    lock = Path(execution_contract.lock_path)
    if any(path.exists() for path in (target, attempt, lock)):
        raise S1BCausalBrowserOneShotError("W6-I one-shot path is already used")
    if playwright_factory is None:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise S1BCausalBrowserOneShotError("Playwright runtime is unavailable") from exc
        playwright_factory = sync_playwright

    _exclusive_marker(lock, "s1b-w6i-one-shot-lock\n")
    browser = None
    browser_closed = False
    execution_started = False
    attempt_created = False
    try:
        _exclusive_marker(
            attempt,
            json.dumps(
                {
                    "execution_id": execution_contract.execution_id,
                    "contract_digest": execution_contract.digest(),
                },
                allow_nan=False,
                ensure_ascii=True,
                separators=(",", ":"),
                sort_keys=True,
            )
            + "\n",
        )
        attempt_created = True
        execution_started = True
        captures = []
        page_flags = []
        context_flags = []
        with playwright_factory() as playwright:
            try:
                browser = playwright.chromium.launch(
                    executable_path=runtime_binding.executable_real_path,
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
                if browser.version != runtime_binding.engine_version:
                    raise S1BCausalBrowserOneShotError(
                        "observed browser version differs from static binding"
                    )
                schedule = s1b_causal_capture_schedule(worlds)
                specifications = (
                    (worlds.history_a_contract, worlds.history_a_source, schedule.history_a_bridge_config),
                    (worlds.history_b_contract, worlds.history_b_source, schedule.history_b_bridge_config),
                    (worlds.probe_contract, worlds.probe_source, schedule.probe_bridge_config),
                )
                for contract, source, bridge_config in specifications:
                    batch, receipt, page_closed, context_closed = _capture_part(
                        browser,
                        contract,
                        source,
                        bridge_config,
                        asset_directory=asset_directory,
                    )
                    captures.append((batch, receipt))
                    page_flags.append(page_closed)
                    context_flags.append(context_closed)
            finally:
                if browser is not None:
                    browser.close()
                    browser_closed = True

        if len(captures) != 3:
            raise S1BCausalBrowserOneShotError("W6-I requires exactly three captures")
        (batch_a, receipt_a), (batch_b, receipt_b), (batch_p, receipt_p) = captures
        handoff = prepare_s1b_causal_capture_handoff(
            batch_a,
            receipt_a,
            batch_b,
            receipt_b,
            batch_p,
            receipt_p,
            world_set=worlds,
        )
        result = run_s1b_causal_capture_handoff(handoff)
        value = _report_value(
            execution_contract,
            handoff,
            result,
            (receipt_a, receipt_b, receipt_p),
            pages_closed=len(page_flags) == 3 and all(page_flags),
            contexts_closed=len(context_flags) == 3 and all(context_flags),
            browser_closed=browser_closed,
        )
        if (
            value["raw_payloads_retained"] is not False
            or value["audio_buffers_released"] is not True
            or value["pages_closed"] is not True
            or value["contexts_closed"] is not True
            or value["browser_closed"] is not True
        ):
            raise S1BCausalBrowserOneShotError("W6-I lifecycle is incomplete")
        encoded = _atomic_publish(target, value)
        attempt.unlink()
        return S1BCausalBrowserOneShotReceipt(
            execution_contract.execution_id,
            str(target),
            hashlib.sha256(encoded).hexdigest(),
            execution_contract.digest(),
            3,
            True,
        )
    finally:
        lock.unlink(missing_ok=True)
        if attempt_created and not execution_started:
            attempt.unlink(missing_ok=True)
