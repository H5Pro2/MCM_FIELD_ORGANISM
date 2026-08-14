"""Observer-side preflight for a public audio-video container candidate."""

from __future__ import annotations

from dataclasses import dataclass, fields
import importlib.util
from pathlib import Path
import shutil

from .public_media_source_contract import (
    PublicMediaSourceAudit,
    PublicMediaSourceContract,
    audit_public_media_source,
)


class PublicAVContainerPreflightError(ValueError):
    """Raised when the public AV preflight is malformed."""


@dataclass(frozen=True, slots=True)
class PublicAVDecoderCapability:
    ffmpeg_path: str | None
    ffprobe_path: str | None
    pyav_available: bool
    soundfile_available: bool
    opencv_available: bool
    vp9_opus_container_decoder_available: bool


@dataclass(frozen=True, slots=True)
class PublicAVContainerPreflight:
    source_audit: PublicMediaSourceAudit
    decoder_capability: PublicAVDecoderCapability
    adapter_prerequisites_met: bool
    adapter_implementation_allowed: bool
    field_run_allowed: bool = False
    metadata_receptor_release_granted: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.source_audit, PublicMediaSourceAudit):
            raise PublicAVContainerPreflightError(
                "source_audit must be a public media source audit"
            )
        if not isinstance(self.decoder_capability, PublicAVDecoderCapability):
            raise PublicAVContainerPreflightError(
                "decoder_capability must be a decoder capability audit"
            )
        for role in (
            "adapter_prerequisites_met",
            "adapter_implementation_allowed",
            "field_run_allowed",
            "metadata_receptor_release_granted",
        ):
            if not isinstance(getattr(self, role), bool):
                raise PublicAVContainerPreflightError(f"{role} must be boolean")
        if self.adapter_prerequisites_met != (
            self.source_audit.accepted
            and self.decoder_capability.vp9_opus_container_decoder_available
        ):
            raise PublicAVContainerPreflightError(
                "adapter prerequisites must match source and decoder gates"
            )
        if self.adapter_implementation_allowed != self.adapter_prerequisites_met:
            raise PublicAVContainerPreflightError(
                "adapter implementation follows only completed prerequisites"
            )
        if self.field_run_allowed or self.metadata_receptor_release_granted:
            raise PublicAVContainerPreflightError(
                "preflight cannot release field runs or metadata to receptors"
            )


def _module_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def audit_public_av_decoder_capability() -> PublicAVDecoderCapability:
    """Check local decoder availability without opening or decoding media."""

    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    pyav = _module_available("av")
    soundfile = _module_available("soundfile")
    opencv = _module_available("cv2")
    return PublicAVDecoderCapability(
        ffmpeg_path=ffmpeg,
        ffprobe_path=ffprobe,
        pyav_available=pyav,
        soundfile_available=soundfile,
        opencv_available=opencv,
        vp9_opus_container_decoder_available=bool(ffmpeg and ffprobe) or pyav,
    )


def run_public_av_container_preflight(
    path: Path,
    contract: PublicMediaSourceContract,
) -> PublicAVContainerPreflight:
    """Gate a future public AV adapter; never decode or release a field run."""

    if not isinstance(path, Path):
        raise PublicAVContainerPreflightError("path must be a pathlib.Path")
    if not isinstance(contract, PublicMediaSourceContract):
        raise PublicAVContainerPreflightError(
            "contract must be a public media source contract"
        )
    source_audit = audit_public_media_source(path, contract)
    decoder_capability = audit_public_av_decoder_capability()
    prerequisites_met = (
        source_audit.accepted
        and decoder_capability.vp9_opus_container_decoder_available
    )
    return PublicAVContainerPreflight(
        source_audit=source_audit,
        decoder_capability=decoder_capability,
        adapter_prerequisites_met=prerequisites_met,
        adapter_implementation_allowed=prerequisites_met,
    )


def public_av_container_preflight_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            PublicAVDecoderCapability,
            PublicAVContainerPreflight,
        )
        for item in fields(cls)
    )
