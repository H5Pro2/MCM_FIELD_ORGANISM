"""Controlled time-shifted browser payload pair without research claims."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import math
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
from .browser_payload_smoke import validate_w1f_browser_payload_runtime
from .browser_payload_source import (
    BrowserPayloadCapturePreflight,
    BrowserPayloadCaptureReceipt,
    BrowserPayloadSourceConfig,
    browser_payload_asset_digests,
    capture_browser_payload_page,
)
from .browser_receptor_bridge import (
    BrowserReceptorBridge,
    BrowserReceptorSequenceBatch,
)
from .browser_world_contract import BrowserWorldContract, BrowserWorldPhase
from .finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from .log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from .neutral_local_field_substrate import NeutralLocalFieldSubstrateConfig
from .shared_mcm_field import SharedMCMFieldSnapshot


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_ENERGY_RELATIVE_TOLERANCE = 1e-12
_FIELD_NUMERICAL_TOLERANCE = 1e-12
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
_PAIR_ASSET_DIGESTS = {
    "browser.payload.timing-pair.v1": _ASSET_DIGESTS,
    "browser.payload.canonical-timing-pair.v1": _CANONICAL_ASSET_DIGESTS,
}


@dataclass(frozen=True, slots=True)
class BrowserPayloadTimingInvariantDiagnostics:
    visual_sequence_exact_match: bool
    audio_total_energy_a0: float
    audio_total_energy_c0: float
    audio_total_energy_relative_error: float
    energy_relative_tolerance: float
    auditory_state_count_a0: int
    auditory_state_count_c0: int
    visual_state_count_a0: int
    visual_state_count_c0: int
    assigned_event_count_a0: int
    assigned_event_count_c0: int
    afterimage_a0_max_abs: float
    afterimage_c0_max_abs: float
    failed_invariant_roles: tuple[str, ...]
    raw_payloads_retained: bool = False

    def __post_init__(self) -> None:
        scalar_roles = (
            "audio_total_energy_a0",
            "audio_total_energy_c0",
            "audio_total_energy_relative_error",
            "energy_relative_tolerance",
            "afterimage_a0_max_abs",
            "afterimage_c0_max_abs",
        )
        if any(
            not math.isfinite(float(getattr(self, role)))
            or float(getattr(self, role)) < 0.0
            for role in scalar_roles
        ):
            raise ValueError("timing diagnostics require finite non-negative scalars")
        counts = (
            self.auditory_state_count_a0,
            self.auditory_state_count_c0,
            self.visual_state_count_a0,
            self.visual_state_count_c0,
            self.assigned_event_count_a0,
            self.assigned_event_count_c0,
        )
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value <= 0
            for value in counts
        ):
            raise ValueError("timing diagnostics require positive inventories")
        roles = tuple(self.failed_invariant_roles)
        allowed = {
            "visual_sequence",
            "audio_total_energy",
            "auditory_inventory",
            "visual_inventory",
            "event_inventory",
            "afterimage_inactive",
        }
        if len(set(roles)) != len(roles) or not set(roles).issubset(allowed):
            raise ValueError("timing diagnostics contain invalid failure roles")
        if self.raw_payloads_retained:
            raise ValueError("timing diagnostics cannot retain raw payloads")
        object.__setattr__(self, "failed_invariant_roles", roles)


class BrowserPayloadTimingPairError(ValueError):
    """Raised when the controlled timing pair is incomplete or unfair."""

    def __init__(
        self,
        message: str,
        *,
        diagnostics: BrowserPayloadTimingInvariantDiagnostics | None = None,
    ) -> None:
        super().__init__(message)
        self.diagnostics = diagnostics


@dataclass(frozen=True, slots=True)
class BrowserPayloadTimingArmReceipt:
    condition_id: str
    world_contract_digest: str
    source_config_digest: str
    capture_receipt: BrowserPayloadCaptureReceipt
    engine_version_observed: str
    auditory_state_count: int
    visual_state_count: int
    assigned_event_count: int
    batch_digest: str
    field_snapshot_digest: str
    page_closed: bool
    context_closed: bool
    browser_closed: bool
    raw_payloads_retained: bool = False

    def __post_init__(self) -> None:
        if self.condition_id not in {"a0.coupled", "c0.audio-shifted"}:
            raise BrowserPayloadTimingPairError("timing arm identity changed")
        for role in (
            "world_contract_digest",
            "source_config_digest",
            "batch_digest",
            "field_snapshot_digest",
        ):
            if not _SHA256.fullmatch(getattr(self, role)):
                raise BrowserPayloadTimingPairError(f"{role} is invalid")
        if not isinstance(self.capture_receipt, BrowserPayloadCaptureReceipt):
            raise BrowserPayloadTimingPairError(
                "timing arm requires one capture receipt"
            )
        if self.capture_receipt.batch_digest != self.batch_digest:
            raise BrowserPayloadTimingPairError(
                "timing arm capture and batch digests differ"
            )
        if (
            self.auditory_state_count != 111
            or self.visual_state_count != 36
            or self.assigned_event_count != 147
        ):
            raise BrowserPayloadTimingPairError("timing arm inventory changed")
        if not self.engine_version_observed:
            raise BrowserPayloadTimingPairError(
                "timing arm requires an observed browser version"
            )
        if any(
            value is not True
            for value in (
                self.page_closed,
                self.context_closed,
                self.browser_closed,
            )
        ):
            raise BrowserPayloadTimingPairError(
                "timing arm lifecycle is incomplete"
            )
        if self.raw_payloads_retained:
            raise BrowserPayloadTimingPairError(
                "timing arm cannot retain raw payloads"
            )


@dataclass(frozen=True, slots=True)
class BrowserPayloadTimingPairReceipt:
    pair_id: str
    package_version: str
    engine_version_bound: str
    browser_revision: str
    asset_digests: tuple[tuple[str, str], ...]
    a0: BrowserPayloadTimingArmReceipt
    c0: BrowserPayloadTimingArmReceipt
    visual_sequence_exact_match: bool
    audio_total_energy_a0: float
    audio_total_energy_c0: float
    audio_total_energy_relative_error: float
    energy_relative_tolerance: float
    activation_final_l1: float
    activation_final_linf: float
    field_numerical_tolerance: float
    afterimage_final_linf: float
    afterimage_a0_max_abs: float
    afterimage_c0_max_abs: float
    all_input_invariants_hold: bool
    all_lifecycle_boundaries_closed: bool
    technical_decision: str
    raw_payloads_retained: bool = False

    def __post_init__(self) -> None:
        if self.pair_id not in _PAIR_ASSET_DIGESTS:
            raise BrowserPayloadTimingPairError("timing pair identity changed")
        if tuple(self.asset_digests) != _PAIR_ASSET_DIGESTS[self.pair_id]:
            raise BrowserPayloadTimingPairError("timing pair assets changed")
        if not isinstance(self.a0, BrowserPayloadTimingArmReceipt) or not isinstance(
            self.c0, BrowserPayloadTimingArmReceipt
        ):
            raise BrowserPayloadTimingPairError(
                "timing pair requires two arm receipts"
            )
        scalar_roles = (
            "audio_total_energy_a0",
            "audio_total_energy_c0",
            "audio_total_energy_relative_error",
            "energy_relative_tolerance",
            "activation_final_l1",
            "activation_final_linf",
            "field_numerical_tolerance",
            "afterimage_final_linf",
            "afterimage_a0_max_abs",
            "afterimage_c0_max_abs",
        )
        if any(
            not math.isfinite(float(getattr(self, role)))
            or float(getattr(self, role)) < 0.0
            for role in scalar_roles
        ):
            raise BrowserPayloadTimingPairError(
                "timing pair scalars must be finite and non-negative"
            )
        if self.audio_total_energy_a0 <= 0.0 or self.audio_total_energy_c0 <= 0.0:
            raise BrowserPayloadTimingPairError(
                "timing pair requires positive audio energy"
            )
        if self.visual_sequence_exact_match is not True:
            raise BrowserPayloadTimingPairError(
                "timing pair visual sequences must match exactly"
            )
        if self.all_input_invariants_hold is not True:
            raise BrowserPayloadTimingPairError(
                "timing pair input invariants failed"
            )
        if self.all_lifecycle_boundaries_closed is not True:
            raise BrowserPayloadTimingPairError(
                "timing pair lifecycle boundaries failed"
            )
        if self.afterimage_a0_max_abs != 0.0 or self.afterimage_c0_max_abs != 0.0:
            raise BrowserPayloadTimingPairError(
                "timing pair cannot activate afterimage in W1-J"
            )
        expected_decision = (
            "TECHNICAL_FIELD_INPUT_TIMING_SENSITIVITY_OBSERVED"
            if self.activation_final_linf > self.field_numerical_tolerance
            else "TECHNICAL_FINAL_FIELD_STATE_INDIFFERENT_IN_THIS_CONTRACT"
        )
        if self.technical_decision != expected_decision:
            raise BrowserPayloadTimingPairError(
                "timing pair technical decision is inconsistent"
            )
        if self.raw_payloads_retained:
            raise BrowserPayloadTimingPairError(
                "timing pair cannot retain raw payloads"
            )


@dataclass(frozen=True, slots=True)
class _TimingArmOutcome:
    receipt: BrowserPayloadTimingArmReceipt
    batch: BrowserReceptorSequenceBatch
    field_snapshot: SharedMCMFieldSnapshot


def browser_payload_timing_pair_contracts(
) -> tuple[BrowserWorldContract, BrowserWorldContract]:
    duration = 300_000_000
    shared = {
        "startup_frame_count": 1,
        "start_lead_ns": 1,
        "movement_cycles": 1,
        "tone_frequency_hz": 440.0,
    }
    a0 = BrowserWorldContract(
        contract_id="browser.world.timing.a0.v1",
        phases=(
            BrowserWorldPhase("rest.before", duration, "static", 0.0),
            BrowserWorldPhase("change", duration, "moving", 0.2),
            BrowserWorldPhase("rest.after.one", duration, "static", 0.0),
            BrowserWorldPhase("rest.after.two", duration, "static", 0.0),
        ),
        **shared,
    )
    c0 = BrowserWorldContract(
        contract_id="browser.world.timing.c0.v1",
        phases=(
            BrowserWorldPhase("rest.before", duration, "static", 0.0),
            BrowserWorldPhase("change", duration, "moving", 0.0),
            BrowserWorldPhase("rest.after.one", duration, "static", 0.2),
            BrowserWorldPhase("rest.after.two", duration, "static", 0.0),
        ),
        **shared,
    )
    return a0, c0


def browser_payload_timing_source_config(
    condition_id: str,
) -> BrowserPayloadSourceConfig:
    if condition_id not in {"a0.coupled", "c0.audio-shifted"}:
        raise BrowserPayloadTimingPairError("unknown timing condition")
    return BrowserPayloadSourceConfig(
        source_id=f"browser.payload.timing.{condition_id}.v1",
        canvas_width=120,
        canvas_height=80,
        device_scale_factor=1,
        visual_frames_per_second=30.0,
        motion_axis="horizontal",
        motion_amplitude_fraction=0.2,
        foreground_size_fraction=0.2,
        background_rgb=(16, 24, 32),
        foreground_rgb=(224, 232, 240),
        audio_sample_rate=8000,
        audio_hop_size=80,
    )


def browser_payload_timing_receptor_bridge(
    contract: BrowserWorldContract,
) -> BrowserReceptorBridge:
    visual = LocalChannelGridReceptor(
        VisualGridConfig(
            source_width=120,
            source_height=80,
            grid_columns=3,
            grid_rows=2,
            frames_per_second=30.0,
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


def browser_payload_timing_visual_signatures() -> tuple[tuple, tuple]:
    """Return render-only A0/C0 inputs, excluding audio and identities."""

    contracts = browser_payload_timing_pair_contracts()
    conditions = ("a0.coupled", "c0.audio-shifted")
    output = []
    for contract, condition_id in zip(contracts, conditions, strict=True):
        source = browser_payload_timing_source_config(condition_id)
        output.append(
            (
                contract.movement_cycles,
                tuple(
                    (phase.duration_ns, phase.visual_mode)
                    for phase in contract.phases
                ),
                source.canvas_width,
                source.canvas_height,
                source.device_scale_factor,
                source.visual_frames_per_second,
                source.motion_axis,
                source.motion_amplitude_fraction,
                source.foreground_size_fraction,
                source.background_rgb,
                source.foreground_rgb,
            )
        )
    return tuple(output)  # type: ignore[return-value]


def browser_payload_timing_audio_sample_supports(
) -> tuple[tuple[int, int], tuple[int, int]]:
    """Return the half-open active PCM sample intervals for A0 and C0."""

    phase_samples = 300_000_000 * 8000 // 1_000_000_000
    return ((phase_samples, 2 * phase_samples), (2 * phase_samples, 3 * phase_samples))


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


def _run_arm(
    binding: BrowserPayloadRuntimeBinding,
    *,
    condition_id: str,
    contract: BrowserWorldContract,
    asset_directory: Path,
    playwright_factory: Callable[[], Any],
) -> _TimingArmOutcome:
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
    snapshot = None
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
                field = advance_audio_video_receptor_sequences(
                    batch.sequences,
                    bridge.visual_receptor,
                    NeutralLocalFieldSubstrateConfig(1.0),
                    ticks_per_second=1_000_000_000.0,
                )
                assigned_event_count = field.field_run.handoff.assigned_event_count
                snapshot = field.field_run.field.snapshot()
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

    if batch is None or capture is None or snapshot is None:
        raise BrowserPayloadTimingPairError(
            "timing arm produced no complete outcome"
        )
    auditory, visual = batch.sequences
    return _TimingArmOutcome(
        BrowserPayloadTimingArmReceipt(
            condition_id=condition_id,
            world_contract_digest=contract.digest(),
            source_config_digest=source.digest(),
            capture_receipt=capture,
            engine_version_observed=observed_version,
            auditory_state_count=len(auditory.frames),
            visual_state_count=len(visual.frames),
            assigned_event_count=assigned_event_count,
            batch_digest=batch.digest(),
            field_snapshot_digest=snapshot.digest(),
            page_closed=page_closed,
            context_closed=context_closed,
            browser_closed=browser_closed,
        ),
        batch,
        snapshot,
    )


def _sequence_values(batch: BrowserReceptorSequenceBatch, index: int) -> tuple:
    return tuple(item.frame.values for item in batch.sequences[index].frames)


def _run_browser_payload_timing_pair(
    binding: BrowserPayloadRuntimeBinding,
    *,
    pair_id: str,
    expected_asset_digests: tuple[tuple[str, str], ...],
    asset_directory: Path,
    playwright_factory: Callable[[], Any],
    runtime_validator: Callable[[BrowserPayloadRuntimeBinding], None] = (
        validate_w1f_browser_payload_runtime
    ),
) -> BrowserPayloadTimingPairReceipt:
    """Run one fixed A0/C0 asset binding with an injected lifecycle."""

    try:
        verify_browser_payload_runtime_binding(binding)
    except BrowserPayloadRuntimeBindingError as exc:
        raise BrowserPayloadTimingPairError(str(exc)) from exc
    if not callable(runtime_validator) or not callable(playwright_factory):
        raise BrowserPayloadTimingPairError(
            "timing pair validators and factory must be callable"
        )
    runtime_validator(binding)
    assets = browser_payload_asset_digests(Path(asset_directory))
    if assets != expected_asset_digests:
        raise BrowserPayloadTimingPairError("timing pair assets differ from binding")

    a0_contract, c0_contract = browser_payload_timing_pair_contracts()
    a0 = _run_arm(
        binding,
        condition_id="a0.coupled",
        contract=a0_contract,
        asset_directory=asset_directory,
        playwright_factory=playwright_factory,
    )
    c0 = _run_arm(
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
        raise BrowserPayloadTimingPairError(
            "observed browser version differs from the static binding"
        )
    visual_match = _sequence_values(a0.batch, 1) == _sequence_values(c0.batch, 1)
    energy_a0 = a0.receipt.capture_receipt.audio_total_energy
    energy_c0 = c0.receipt.capture_receipt.audio_total_energy
    energy_relative_error = abs(energy_a0 - energy_c0) / max(energy_a0, energy_c0)

    if a0.field_snapshot.neuron_ids != c0.field_snapshot.neuron_ids:
        raise BrowserPayloadTimingPairError("timing pair field anatomy changed")
    activation_delta = tuple(
        abs(left - right)
        for left, right in zip(
            a0.field_snapshot.activation,
            c0.field_snapshot.activation,
            strict=True,
        )
    )
    afterimage_delta = tuple(
        abs(left - right)
        for left, right in zip(
            a0.field_snapshot.afterimage,
            c0.field_snapshot.afterimage,
            strict=True,
        )
    )
    activation_l1 = math.fsum(activation_delta)
    activation_linf = max(activation_delta, default=0.0)
    afterimage_linf = max(afterimage_delta, default=0.0)
    afterimage_a0_max = max(
        (abs(value) for value in a0.field_snapshot.afterimage),
        default=0.0,
    )
    afterimage_c0_max = max(
        (abs(value) for value in c0.field_snapshot.afterimage),
        default=0.0,
    )
    input_invariants = (
        visual_match
        and energy_relative_error <= _ENERGY_RELATIVE_TOLERANCE
        and a0.receipt.auditory_state_count == c0.receipt.auditory_state_count == 111
        and a0.receipt.visual_state_count == c0.receipt.visual_state_count == 36
        and a0.receipt.assigned_event_count == c0.receipt.assigned_event_count == 147
        and afterimage_a0_max == afterimage_c0_max == 0.0
    )
    if not input_invariants:
        failed_invariants = []
        if not visual_match:
            failed_invariants.append("visual_sequence")
        if energy_relative_error > _ENERGY_RELATIVE_TOLERANCE:
            failed_invariants.append("audio_total_energy")
        if (
            a0.receipt.auditory_state_count != 111
            or c0.receipt.auditory_state_count != 111
        ):
            failed_invariants.append("auditory_inventory")
        if (
            a0.receipt.visual_state_count != 36
            or c0.receipt.visual_state_count != 36
        ):
            failed_invariants.append("visual_inventory")
        if (
            a0.receipt.assigned_event_count != 147
            or c0.receipt.assigned_event_count != 147
        ):
            failed_invariants.append("event_inventory")
        if afterimage_a0_max != 0.0 or afterimage_c0_max != 0.0:
            failed_invariants.append("afterimage_inactive")
        diagnostics = BrowserPayloadTimingInvariantDiagnostics(
            visual_sequence_exact_match=visual_match,
            audio_total_energy_a0=energy_a0,
            audio_total_energy_c0=energy_c0,
            audio_total_energy_relative_error=energy_relative_error,
            energy_relative_tolerance=_ENERGY_RELATIVE_TOLERANCE,
            auditory_state_count_a0=a0.receipt.auditory_state_count,
            auditory_state_count_c0=c0.receipt.auditory_state_count,
            visual_state_count_a0=a0.receipt.visual_state_count,
            visual_state_count_c0=c0.receipt.visual_state_count,
            assigned_event_count_a0=a0.receipt.assigned_event_count,
            assigned_event_count_c0=c0.receipt.assigned_event_count,
            afterimage_a0_max_abs=afterimage_a0_max,
            afterimage_c0_max_abs=afterimage_c0_max,
            failed_invariant_roles=tuple(failed_invariants),
        )
        raise BrowserPayloadTimingPairError(
            "timing pair input invariants failed: "
            + ",".join(failed_invariants),
            diagnostics=diagnostics,
        )
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
    decision = (
        "TECHNICAL_FIELD_INPUT_TIMING_SENSITIVITY_OBSERVED"
        if activation_linf > _FIELD_NUMERICAL_TOLERANCE
        else "TECHNICAL_FINAL_FIELD_STATE_INDIFFERENT_IN_THIS_CONTRACT"
    )
    return BrowserPayloadTimingPairReceipt(
        pair_id=pair_id,
        package_version=binding.package_version,
        engine_version_bound=binding.engine_version,
        browser_revision=binding.browser_revision,
        asset_digests=assets,
        a0=a0.receipt,
        c0=c0.receipt,
        visual_sequence_exact_match=visual_match,
        audio_total_energy_a0=energy_a0,
        audio_total_energy_c0=energy_c0,
        audio_total_energy_relative_error=energy_relative_error,
        energy_relative_tolerance=_ENERGY_RELATIVE_TOLERANCE,
        activation_final_l1=activation_l1,
        activation_final_linf=activation_linf,
        field_numerical_tolerance=_FIELD_NUMERICAL_TOLERANCE,
        afterimage_final_linf=afterimage_linf,
        afterimage_a0_max_abs=afterimage_a0_max,
        afterimage_c0_max_abs=afterimage_c0_max,
        all_input_invariants_hold=input_invariants,
        all_lifecycle_boundaries_closed=lifecycle_closed,
        technical_decision=decision,
    )


def run_browser_payload_timing_pair(
    binding: BrowserPayloadRuntimeBinding,
    *,
    asset_directory: Path,
    playwright_factory: Callable[[], Any],
    runtime_validator: Callable[[BrowserPayloadRuntimeBinding], None] = (
        validate_w1f_browser_payload_runtime
    ),
) -> BrowserPayloadTimingPairReceipt:
    """Run the historical W1-J A0/C0 pair with an injected lifecycle."""

    return _run_browser_payload_timing_pair(
        binding,
        pair_id="browser.payload.timing-pair.v1",
        expected_asset_digests=_ASSET_DIGESTS,
        asset_directory=asset_directory,
        playwright_factory=playwright_factory,
        runtime_validator=runtime_validator,
    )


def run_browser_payload_canonical_timing_pair(
    binding: BrowserPayloadRuntimeBinding,
    *,
    asset_directory: Path,
    playwright_factory: Callable[[], Any],
    runtime_validator: Callable[[BrowserPayloadRuntimeBinding], None] = (
        validate_w1f_browser_payload_runtime
    ),
) -> BrowserPayloadTimingPairReceipt:
    """Run the canonical-segment A0/C0 pair with an injected lifecycle."""

    return _run_browser_payload_timing_pair(
        binding,
        pair_id="browser.payload.canonical-timing-pair.v1",
        expected_asset_digests=_CANONICAL_ASSET_DIGESTS,
        asset_directory=asset_directory,
        playwright_factory=playwright_factory,
        runtime_validator=runtime_validator,
    )


def browser_payload_timing_pair_json_value(
    receipt: BrowserPayloadTimingPairReceipt,
) -> dict[str, object]:
    if not isinstance(receipt, BrowserPayloadTimingPairReceipt):
        raise BrowserPayloadTimingPairError(
            "JSON projection requires a timing pair receipt"
        )
    return asdict(receipt)


def browser_payload_timing_diagnostics_json_value(
    diagnostics: BrowserPayloadTimingInvariantDiagnostics,
) -> dict[str, object]:
    if not isinstance(diagnostics, BrowserPayloadTimingInvariantDiagnostics):
        raise BrowserPayloadTimingPairError(
            "JSON projection requires timing invariant diagnostics"
        )
    return asdict(diagnostics)


def browser_payload_timing_pair_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            BrowserPayloadTimingInvariantDiagnostics,
            BrowserPayloadTimingArmReceipt,
            BrowserPayloadTimingPairReceipt,
        )
        for item in fields(contract)
    )
