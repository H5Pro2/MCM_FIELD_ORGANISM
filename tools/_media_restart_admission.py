"""Explicit selected-file admission; no payload I/O and no implicit gate opening."""
from dataclasses import dataclass
from pathlib import Path

from tools import _s2oe_media_binding as p
from tools._media_restart_work import require

VERSION = "media.restart-real-admission.v1"
REAL = "SELECTED_FILE_RESTART_V1"
NEUTRAL = "NEUTRAL_CONNECTION"
SOURCE = Path(r"C:\Users\TV\Downloads\17138816-uhd_3840_2160_30fps.mp4")
SHA256 = "df0986f384e156c4dfec234e94b6f6baa3d0f8a9cfd7ba81f14aadf0313450aa"
SIZE = 83498438


@dataclass(frozen=True)
class Admission:
    version: str
    run_id: str
    manifest_digest: str
    code_digest: str
    profile_digest: str
    source_path: str
    source_sha256: str
    source_size: int
    authorized: bool


def validate(manifest, mode=NEUTRAL, admission=None):
    if mode == NEUTRAL:
        require(admission is None, "RESTART_NEUTRAL_ADMISSION_MIXED")
        require(Path(manifest.source.path).resolve().is_relative_to(
            p.b.ROOT/"sources/media-restart-neutral"), "REAL_MEDIA_RESTART_BLOCKED")
        return
    require(mode == REAL, "RESTART_PLAYER_NOT_ADMITTED")
    require(type(admission) is Admission and admission.version == VERSION,
            "RESTART_REAL_ADMISSION_REQUIRED")
    require(admission.authorized is True, "RESTART_REAL_AUTHORIZATION_REQUIRED")
    p.validate(manifest)
    require(manifest.schema == p.FULL_VERSION, "RESTART_REAL_MODE")
    source = manifest.source
    require(source.path == admission.source_path == str(SOURCE)
        and Path(source.path).resolve() == SOURCE.resolve()
        and source.sha256 == admission.source_sha256 == SHA256
        and type(admission.source_size) is int
        and source.size == admission.source_size == SIZE, "RESTART_REAL_SOURCE")
    require(admission.run_id == manifest.run_id, "RESTART_REAL_RUN")
    require(admission.profile_digest == manifest.profile_digest == p.b.half.PROFILE_DIGEST,
            "RESTART_REAL_PROFILE")
    require(admission.code_digest == manifest.code_digest, "RESTART_REAL_CODE")
    require(admission.manifest_digest == manifest.manifest_digest, "RESTART_REAL_MANIFEST")
