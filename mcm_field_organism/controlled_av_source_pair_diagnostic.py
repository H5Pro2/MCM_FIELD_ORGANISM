"""Diagnostic A0/C0 source pair before any shared-field handoff."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from hashlib import sha256
import json
import math
from pathlib import Path
import re
from typing import Any, Callable

from .browser_payload_runtime import (
    BrowserPayloadRuntimeBinding,
    BrowserPayloadRuntimeBindingError,
    verify_browser_payload_runtime_binding,
)
from .browser_payload_smoke import validate_w1f_browser_payload_runtime
from .browser_payload_source import (
    BrowserPayloadCapturePreflight,
    BrowserPayloadCaptureReceipt,
    browser_payload_asset_digests,
    capture_browser_payload_page,
)
from .browser_payload_timing_pair import (
    browser_payload_timing_pair_contracts,
    browser_payload_timing_receptor_bridge,
    browser_payload_timing_source_config,
)
from .browser_receptor_bridge import BrowserReceptorSequenceBatch
from .browser_world_contract import BrowserWorldContract


class ControlledAVSourcePairDiagnosticError(ValueError):
    """Raised when the controlled source pair cannot be diagnosed safely."""


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_ENERGY_RELATIVE_TOLERANCE = 1e-12
_ASSET_DIGESTS = (
    ("index.html", "74fc372a3eff08ac38e803689e562ce5acbb39d56d3351db475c768457e32af8"),
    ("styles.css", "f026fce8f826fb7364a11b1b05ad4acb3dd37aed7dede5453c6f82cbf497b594"),
    ("world.js", "fda8c774708af883eb97625b7064ec288c06e2819619fb2eb93e281212d32158"),
)
_CANONICAL_ASSET_DIGESTS = (
    ("index.html", "0ceecd1e9e346ce262e8e0cb41efe52fe2f3e42e00c1d6298fdf23becc451d3b"),
    ("styles.css", "f026fce8f826fb7364a11b1b05ad4acb3dd37aed7dede5453c6f82cbf497b594"),
    ("world.js", "7e903402e16f3f11423116ab3112d452c3815fb6006ed18537963fd887c956bb"),
)
_DIAGNOSTIC_ASSETS = {
    "controlled.av.source-pair.diagnostic.v1": _ASSET_DIGESTS,
    "controlled.av.canonical-source-pair.diagnostic.v1": (
        _CANONICAL_ASSET_DIGESTS
    ),
}


@dataclass(frozen=True, slots=True)
class ControlledAVSourceDiagnosticArmReceipt:
    condition_id: str
    world_contract_digest: str
    source_config_digest: str
    capture_receipt: BrowserPayloadCaptureReceipt
    engine_version_observed: str
    auditory_state_count: int
    visual_state_count: int
    receptor_event_count: int
    auditory_sequence_digest: str
    visual_sequence_digest: str
    page_closed: bool
    context_closed: bool
    browser_closed: bool
    raw_payloads_retained: bool = False

    def __post_init__(self) -> None:
        if self.condition_id not in {"a0.coupled", "c0.audio-shifted"}:
            raise ControlledAVSourcePairDiagnosticError(
                "source diagnostic arm identity changed"
            )
        for role in (
            "world_contract_digest",
            "source_config_digest",
            "auditory_sequence_digest",
            "visual_sequence_digest",
        ):
            if not _SHA256.fullmatch(getattr(self, role)):
                raise ControlledAVSourcePairDiagnosticError(f"{role} is invalid")
        if not isinstance(self.capture_receipt, BrowserPayloadCaptureReceipt):
            raise ControlledAVSourcePairDiagnosticError(
                "source diagnostic arm requires one capture receipt"
            )
        if (
            self.auditory_state_count != 111
            or self.visual_state_count != 36
            or self.receptor_event_count != 147
        ):
            raise ControlledAVSourcePairDiagnosticError(
                "source diagnostic arm inventory changed"
            )
        if not self.engine_version_observed:
            raise ControlledAVSourcePairDiagnosticError(
                "source diagnostic arm requires an observed engine version"
            )
        if any(
            value is not True
            for value in (
                self.page_closed,
                self.context_closed,
                self.browser_closed,
            )
        ):
            raise ControlledAVSourcePairDiagnosticError(
                "source diagnostic arm lifecycle is incomplete"
            )
        if self.raw_payloads_retained:
            raise ControlledAVSourcePairDiagnosticError(
                "source diagnostic arm cannot retain raw payloads"
            )


@dataclass(frozen=True, slots=True)
class ControlledAVSourcePairDiagnosticReceipt:
    diagnostic_id: str
    package_version: str
    engine_version_bound: str
    browser_revision: str
    asset_digests: tuple[tuple[str, str], ...]
    a0: ControlledAVSourceDiagnosticArmReceipt
    c0: ControlledAVSourceDiagnosticArmReceipt
    visual_sequence_exact_match: bool
    audio_total_energy_a0: float
    audio_total_energy_c0: float
    audio_total_energy_relative_error: float
    energy_relative_tolerance: float
    failed_invariant_roles: tuple[str, ...]
    diagnostic_decision: str
    all_lifecycle_boundaries_closed: bool
    field_handoff_performed: bool = False
    raw_payloads_retained: bool = False

    def __post_init__(self) -> None:
        if self.diagnostic_id not in _DIAGNOSTIC_ASSETS:
            raise ControlledAVSourcePairDiagnosticError(
                "source pair diagnostic identity changed"
            )
        if tuple(self.asset_digests) != _DIAGNOSTIC_ASSETS[self.diagnostic_id]:
            raise ControlledAVSourcePairDiagnosticError(
                "source pair diagnostic assets changed"
            )
        if not isinstance(
            self.a0, ControlledAVSourceDiagnosticArmReceipt
        ) or not isinstance(self.c0, ControlledAVSourceDiagnosticArmReceipt):
            raise ControlledAVSourcePairDiagnosticError(
                "source pair diagnostic requires two arm receipts"
            )
        for role in (
            "audio_total_energy_a0",
            "audio_total_energy_c0",
            "audio_total_energy_relative_error",
            "energy_relative_tolerance",
        ):
            value = float(getattr(self, role))
            if not math.isfinite(value) or value < 0.0:
                raise ControlledAVSourcePairDiagnosticError(
                    "source pair diagnostic scalars are invalid"
                )
        roles = tuple(self.failed_invariant_roles)
        if not set(roles).issubset({"visual_sequence", "audio_total_energy"}):
            raise ControlledAVSourcePairDiagnosticError(
                "source pair diagnostic failure roles changed"
            )
        expected_roles = []
        if not self.visual_sequence_exact_match:
            expected_roles.append("visual_sequence")
        if self.audio_total_energy_relative_error > self.energy_relative_tolerance:
            expected_roles.append("audio_total_energy")
        if roles != tuple(expected_roles):
            raise ControlledAVSourcePairDiagnosticError(
                "source pair diagnostic roles are inconsistent"
            )
        expected_decision = (
            "SOURCE_INVARIANTS_MATCH"
            if not roles
            else "SOURCE_INVARIANTS_DIFFER"
        )
        if self.diagnostic_decision != expected_decision:
            raise ControlledAVSourcePairDiagnosticError(
                "source pair diagnostic decision is inconsistent"
            )
        if self.all_lifecycle_boundaries_closed is not True:
            raise ControlledAVSourcePairDiagnosticError(
                "source pair diagnostic lifecycle is incomplete"
            )
        if self.field_handoff_performed or self.raw_payloads_retained:
            raise ControlledAVSourcePairDiagnosticError(
                "source pair diagnostic cannot hand off to field or retain payloads"
            )
        object.__setattr__(self, "failed_invariant_roles", roles)


@dataclass(frozen=True, slots=True)
class _SourceArmOutcome:
    receipt: ControlledAVSourceDiagnosticArmReceipt
    batch: BrowserReceptorSequenceBatch


def _sequence_digest(batch: BrowserReceptorSequenceBatch, index: int) -> str:
    sequence = batch.sequences[index]
    payload = [
        {
            "start": item.field_time.window_start_tick,
            "end": item.field_time.window_end_tick,
            "values": list(item.frame.values),
        }
        for item in sequence.frames
    ]
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return sha256(encoded).hexdigest()


def _preflight() -> BrowserPayloadCapturePreflight:
    return BrowserPayloadCapturePreflight(
        fresh_isolated_context=True,
        persistent_profile=False,
        extensions_enabled=False,
        viewport_width=120,
        viewport_height=80,
        device_scale_factor=1,
        java_script_enabled=True,
    )


def _capture_arm(
    binding: BrowserPayloadRuntimeBinding,
    *,
    condition_id: str,
    contract: BrowserWorldContract,
    asset_directory: Path,
    playwright_factory: Callable[[], Any],
) -> _SourceArmOutcome:
    source = browser_payload_timing_source_config(condition_id)
    bridge = browser_payload_timing_receptor_bridge(contract)
    browser = None
    context = None
    page = None
    page_closed = False
    context_closed = False
    browser_closed = False
    observed_version = ""
    batch = None
    capture = None

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
            observed_version = browser.version
            context = browser.new_context(
                viewport={"width": 120, "height": 80},
                device_scale_factor=1,
                java_script_enabled=True,
                accept_downloads=False,
                service_workers="block",
                permissions=[],
            )
            page = context.new_page()
            try:
                batch, capture = capture_browser_payload_page(
                    page,
                    contract,
                    source,
                    bridge,
                    asset_directory=asset_directory,
                    preflight=_preflight(),
                )
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

    if batch is None or capture is None:
        raise ControlledAVSourcePairDiagnosticError(
            "source diagnostic arm produced no complete capture"
        )
    auditory, visual = batch.sequences
    return _SourceArmOutcome(
        ControlledAVSourceDiagnosticArmReceipt(
            condition_id=condition_id,
            world_contract_digest=contract.digest(),
            source_config_digest=source.digest(),
            capture_receipt=capture,
            engine_version_observed=observed_version,
            auditory_state_count=len(auditory.frames),
            visual_state_count=len(visual.frames),
            receptor_event_count=len(auditory.frames) + len(visual.frames),
            auditory_sequence_digest=_sequence_digest(batch, 0),
            visual_sequence_digest=_sequence_digest(batch, 1),
            page_closed=page_closed,
            context_closed=context_closed,
            browser_closed=browser_closed,
        ),
        batch,
    )


def _run_controlled_av_source_pair_diagnostic(
    binding: BrowserPayloadRuntimeBinding,
    *,
    diagnostic_id: str,
    expected_asset_digests: tuple[tuple[str, str], ...],
    asset_directory: Path,
    playwright_factory: Callable[[], Any],
    runtime_validator: Callable[[BrowserPayloadRuntimeBinding], None] = (
        validate_w1f_browser_payload_runtime
    ),
) -> ControlledAVSourcePairDiagnosticReceipt:
    """Capture A0/C0 and diagnose source invariants without a field handoff."""

    try:
        verify_browser_payload_runtime_binding(binding)
    except BrowserPayloadRuntimeBindingError as exc:
        raise ControlledAVSourcePairDiagnosticError(str(exc)) from exc
    if not callable(playwright_factory) or not callable(runtime_validator):
        raise ControlledAVSourcePairDiagnosticError(
            "source diagnostic factory and validator must be callable"
        )
    runtime_validator(binding)
    assets = browser_payload_asset_digests(Path(asset_directory))
    if assets != expected_asset_digests:
        raise ControlledAVSourcePairDiagnosticError(
            "source diagnostic assets differ from W1-M"
        )

    a0_contract, c0_contract = browser_payload_timing_pair_contracts()
    a0 = _capture_arm(
        binding,
        condition_id="a0.coupled",
        contract=a0_contract,
        asset_directory=asset_directory,
        playwright_factory=playwright_factory,
    )
    c0 = _capture_arm(
        binding,
        condition_id="c0.audio-shifted",
        contract=c0_contract,
        asset_directory=asset_directory,
        playwright_factory=playwright_factory,
    )
    if (
        a0.receipt.engine_version_observed != binding.engine_version
        or c0.receipt.engine_version_observed != binding.engine_version
    ):
        raise ControlledAVSourcePairDiagnosticError(
            "source diagnostic engine version differs from binding"
        )

    visual_match = (
        a0.receipt.visual_sequence_digest == c0.receipt.visual_sequence_digest
    )
    energy_a0 = a0.receipt.capture_receipt.audio_total_energy
    energy_c0 = c0.receipt.capture_receipt.audio_total_energy
    energy_error = abs(energy_a0 - energy_c0) / max(energy_a0, energy_c0)
    failed = []
    if not visual_match:
        failed.append("visual_sequence")
    if energy_error > _ENERGY_RELATIVE_TOLERANCE:
        failed.append("audio_total_energy")
    lifecycle_closed = all(
        (
            a0.receipt.page_closed,
            a0.receipt.context_closed,
            a0.receipt.browser_closed,
            c0.receipt.page_closed,
            c0.receipt.context_closed,
            c0.receipt.browser_closed,
        )
    )
    return ControlledAVSourcePairDiagnosticReceipt(
        diagnostic_id=diagnostic_id,
        package_version=binding.package_version,
        engine_version_bound=binding.engine_version,
        browser_revision=binding.browser_revision,
        asset_digests=assets,
        a0=a0.receipt,
        c0=c0.receipt,
        visual_sequence_exact_match=visual_match,
        audio_total_energy_a0=energy_a0,
        audio_total_energy_c0=energy_c0,
        audio_total_energy_relative_error=energy_error,
        energy_relative_tolerance=_ENERGY_RELATIVE_TOLERANCE,
        failed_invariant_roles=tuple(failed),
        diagnostic_decision=(
            "SOURCE_INVARIANTS_MATCH" if not failed else "SOURCE_INVARIANTS_DIFFER"
        ),
        all_lifecycle_boundaries_closed=lifecycle_closed,
    )


def run_controlled_av_source_pair_diagnostic(
    binding: BrowserPayloadRuntimeBinding,
    *,
    asset_directory: Path,
    playwright_factory: Callable[[], Any],
    runtime_validator: Callable[[BrowserPayloadRuntimeBinding], None] = (
        validate_w1f_browser_payload_runtime
    ),
) -> ControlledAVSourcePairDiagnosticReceipt:
    """Diagnose the original W1-M source pair without a field handoff."""

    return _run_controlled_av_source_pair_diagnostic(
        binding,
        diagnostic_id="controlled.av.source-pair.diagnostic.v1",
        expected_asset_digests=_ASSET_DIGESTS,
        asset_directory=asset_directory,
        playwright_factory=playwright_factory,
        runtime_validator=runtime_validator,
    )


def run_controlled_av_canonical_source_pair_diagnostic(
    binding: BrowserPayloadRuntimeBinding,
    *,
    asset_directory: Path,
    playwright_factory: Callable[[], Any],
    runtime_validator: Callable[[BrowserPayloadRuntimeBinding], None] = (
        validate_w1f_browser_payload_runtime
    ),
) -> ControlledAVSourcePairDiagnosticReceipt:
    """Diagnose the canonical-segment source pair without a field handoff."""

    return _run_controlled_av_source_pair_diagnostic(
        binding,
        diagnostic_id="controlled.av.canonical-source-pair.diagnostic.v1",
        expected_asset_digests=_CANONICAL_ASSET_DIGESTS,
        asset_directory=asset_directory,
        playwright_factory=playwright_factory,
        runtime_validator=runtime_validator,
    )


def controlled_av_source_pair_diagnostic_json_value(
    receipt: ControlledAVSourcePairDiagnosticReceipt,
) -> dict[str, object]:
    if not isinstance(receipt, ControlledAVSourcePairDiagnosticReceipt):
        raise ControlledAVSourcePairDiagnosticError(
            "JSON projection requires a source pair diagnostic receipt"
        )
    return asdict(receipt)


def controlled_av_source_pair_diagnostic_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            ControlledAVSourceDiagnosticArmReceipt,
            ControlledAVSourcePairDiagnosticReceipt,
        )
        for item in fields(contract)
    )
