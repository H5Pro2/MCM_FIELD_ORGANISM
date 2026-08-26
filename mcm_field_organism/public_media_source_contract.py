"""Observer-side integrity gate for one bounded public media source."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
from pathlib import Path
import re


class PublicMediaSourceContractError(ValueError):
    """Raised when a public media source contract is malformed."""


_HEX_SHA1 = re.compile(r"^[0-9a-f]{40}$")


@dataclass(frozen=True, slots=True)
class PublicMediaSourceContract:
    source_id: str
    expected_size_bytes: int
    expected_sha1: str

    def __post_init__(self) -> None:
        if not isinstance(self.source_id, str) or not self.source_id:
            raise PublicMediaSourceContractError("source_id must be non-empty")
        if (
            isinstance(self.expected_size_bytes, bool)
            or not isinstance(self.expected_size_bytes, int)
            or self.expected_size_bytes <= 0
        ):
            raise PublicMediaSourceContractError(
                "expected_size_bytes must be a positive integer"
            )
        digest = str(self.expected_sha1).lower()
        if not _HEX_SHA1.fullmatch(digest):
            raise PublicMediaSourceContractError(
                "expected_sha1 must contain exactly 40 lowercase hexadecimal characters"
            )
        object.__setattr__(self, "expected_sha1", digest)


@dataclass(frozen=True, slots=True)
class PublicMediaSourceAudit:
    source_id: str
    file_present: bool
    size_matches: bool
    sha1_matches: bool
    accepted: bool
    observed_size_bytes: int | None
    observed_sha1: str | None
    receptor_release_granted: bool = False


def audit_public_media_source(
    path: Path,
    contract: PublicMediaSourceContract,
) -> PublicMediaSourceAudit:
    """Read file integrity only; do not decode or release media to a receptor."""

    if not isinstance(path, Path):
        raise PublicMediaSourceContractError("path must be a pathlib.Path")
    if not isinstance(contract, PublicMediaSourceContract):
        raise PublicMediaSourceContractError(
            "contract must be a PublicMediaSourceContract"
        )
    if not path.is_file():
        return PublicMediaSourceAudit(
            source_id=contract.source_id,
            file_present=False,
            size_matches=False,
            sha1_matches=False,
            accepted=False,
            observed_size_bytes=None,
            observed_sha1=None,
        )

    observed_size = path.stat().st_size
    digest = hashlib.sha1(usedforsecurity=False)
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    observed_sha1 = digest.hexdigest()
    size_matches = observed_size == contract.expected_size_bytes
    sha1_matches = observed_sha1 == contract.expected_sha1
    return PublicMediaSourceAudit(
        source_id=contract.source_id,
        file_present=True,
        size_matches=size_matches,
        sha1_matches=sha1_matches,
        accepted=size_matches and sha1_matches,
        observed_size_bytes=observed_size,
        observed_sha1=observed_sha1,
    )


def street_traffic_source_contract() -> PublicMediaSourceContract:
    return PublicMediaSourceContract(
        source_id="public.visual.street-traffic.commons.2013-02-02",
        expected_size_bytes=26_490_572,
        expected_sha1="7f916030f14d84a65aa92077339f472897915fef",
    )


def brokindsleden_av_source_contract() -> PublicMediaSourceContract:
    return PublicMediaSourceContract(
        source_id="public.audiovisual.brokindsleden-traffic-sound.commons.2018-12-18",
        expected_size_bytes=94_052_425,
        expected_sha1="672be38ca918858ec0973b85401a832e3fc592e1",
    )


def nasa_earthrise_av_source_contract() -> PublicMediaSourceContract:
    return PublicMediaSourceContract(
        source_id="public.audiovisual.nasa-earthrise-realtime.svs.2013-12-20",
        expected_size_bytes=13_547_755,
        expected_sha1="c63198a925ad227950cca597c4a8500656bacdfc",
    )


def public_media_source_contract_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract_type in (PublicMediaSourceContract, PublicMediaSourceAudit)
        for item in fields(contract_type)
    )
