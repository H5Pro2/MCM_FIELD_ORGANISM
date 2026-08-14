"""Static controlled browser-world contracts for the W6-D causal check."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from .browser_payload_source import BrowserPayloadSourceConfig
from .browser_world_contract import BrowserWorldContract, BrowserWorldPhase


class S1BCausalBrowserWorldError(ValueError):
    """Raised when the three causal world parts lose their fixed boundary."""


S1B_CAUSAL_BROWSER_WORLD_SET_DIGEST = (
    "66168de571819b71e68ce6605781d3d65224cc1663294924fce788ad2a821920"
)


@dataclass(frozen=True, slots=True)
class S1BCausalBrowserWorldSet:
    """Formation A, donor formation B, and one shared later probe."""

    history_a_contract: BrowserWorldContract
    history_a_source: BrowserPayloadSourceConfig
    history_b_contract: BrowserWorldContract
    history_b_source: BrowserPayloadSourceConfig
    probe_contract: BrowserWorldContract
    probe_source: BrowserPayloadSourceConfig

    def __post_init__(self) -> None:
        contracts = (
            self.history_a_contract,
            self.history_b_contract,
            self.probe_contract,
        )
        sources = (
            self.history_a_source,
            self.history_b_source,
            self.probe_source,
        )
        if any(not isinstance(item, BrowserWorldContract) for item in contracts):
            raise S1BCausalBrowserWorldError("causal world contracts are invalid")
        if any(
            not isinstance(item, BrowserPayloadSourceConfig) for item in sources
        ):
            raise S1BCausalBrowserWorldError("causal world sources are invalid")
        if len({item.contract_id for item in contracts}) != 3 or len(
            {item.source_id for item in sources}
        ) != 3:
            raise S1BCausalBrowserWorldError(
                "causal world parts require unique technical identities"
            )
        if self.history_a_contract.total_duration_ns != (
            self.history_b_contract.total_duration_ns
        ):
            raise S1BCausalBrowserWorldError(
                "causal histories require equal duration"
            )
        history_a_support = tuple(
            (phase.duration_ns, phase.visual_mode, phase.tone_gain)
            for phase in self.history_a_contract.phases
        )
        history_b_support = tuple(
            (phase.duration_ns, phase.visual_mode, phase.tone_gain)
            for phase in self.history_b_contract.phases
        )
        if history_a_support != history_b_support:
            raise S1BCausalBrowserWorldError(
                "causal histories require equal phase support"
            )
        geometry_roles = (
            "canvas_width",
            "canvas_height",
            "device_scale_factor",
            "visual_frames_per_second",
            "motion_amplitude_fraction",
            "foreground_size_fraction",
            "background_rgb",
            "foreground_rgb",
            "audio_sample_rate",
            "audio_hop_size",
            "audio_channel_count",
            "oscillator_type",
        )
        if any(
            len({getattr(source, role) for source in sources}) != 1
            for role in geometry_roles
        ):
            raise S1BCausalBrowserWorldError(
                "causal world parts require one receptor-source geometry"
            )
        if (
            self.history_a_source.motion_axis
            == self.history_b_source.motion_axis
            or self.history_a_contract.tone_frequency_hz
            == self.history_b_contract.tone_frequency_hz
        ):
            raise S1BCausalBrowserWorldError(
                "causal donor histories require two independent input differences"
            )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "history_a": {
                "world": self.history_a_contract.canonical_payload(),
                "source": self.history_a_source.canonical_payload(),
            },
            "history_b": {
                "world": self.history_b_contract.canonical_payload(),
                "source": self.history_b_source.canonical_payload(),
            },
            "probe": {
                "world": self.probe_contract.canonical_payload(),
                "source": self.probe_source.canonical_payload(),
            },
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


def _source(source_id: str, motion_axis: str) -> BrowserPayloadSourceConfig:
    return BrowserPayloadSourceConfig(
        source_id=source_id,
        canvas_width=120,
        canvas_height=80,
        device_scale_factor=1,
        visual_frames_per_second=30.0,
        motion_axis=motion_axis,
        motion_amplitude_fraction=0.2,
        foreground_size_fraction=0.2,
        background_rgb=(16, 24, 32),
        foreground_rgb=(224, 232, 240),
        audio_sample_rate=8000,
        audio_hop_size=80,
    )


def _world(contract_id: str, frequency_hz: float) -> BrowserWorldContract:
    duration = 300_000_000
    return BrowserWorldContract(
        contract_id=contract_id,
        startup_frame_count=1,
        start_lead_ns=1,
        movement_cycles=1,
        tone_frequency_hz=frequency_hz,
        phases=(
            BrowserWorldPhase("rest.before", duration, "static", 0.0),
            BrowserWorldPhase("formation", duration, "moving", 0.2),
            BrowserWorldPhase("rest.after", duration, "static", 0.0),
        ),
    )


def s1b_causal_browser_world_set() -> S1BCausalBrowserWorldSet:
    """Return the fixed, passive, unexecuted W6-D browser world contracts."""

    return S1BCausalBrowserWorldSet(
        history_a_contract=_world("browser.world.w6d.history-a.v1", 330.0),
        history_a_source=_source(
            "browser.payload.w6d.history-a.v1",
            "horizontal",
        ),
        history_b_contract=_world("browser.world.w6d.history-b.v1", 660.0),
        history_b_source=_source(
            "browser.payload.w6d.history-b.v1",
            "vertical",
        ),
        probe_contract=_world("browser.world.w6d.probe.v1", 440.0),
        probe_source=_source("browser.payload.w6d.probe.v1", "horizontal"),
    )
