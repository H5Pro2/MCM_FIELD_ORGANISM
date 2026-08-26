"""Private S1-WJ injected root-mirror and resource adapters."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from tempfile import gettempdir

from ._ppb1_s1wb_private_production_h0_types import (
    S1WAProductionResourceGate,
    S1WAProductionResourceObservation,
    S1WB_CALIBRATED_SOURCE_DIGESTS,
    S1WB_PLATFORM_BINDING,
    build_s1wb_injected_observation,
    evaluate_s1wb_resource_gate,
)
from ._ppb1_s1wh_private_injected_coordinator_shell import (
    S1WHInjectedStageAdapter,
)


S1WJ_SCHEMA_VERSION = "ppb1.s1wj.private.injected-root-resource.v1"
S1WJ_CONTRACT_DIGEST = (
    "c220857ae7974ed4ad7aa60676dc66c67574cd3dc94cf879b26cf220ade3e84b"
)
S1WJ_PRODUCTION_RELATIVE_ROOT = "data/generated/ppb1/one_shot"
S1WJ_MIRROR_ROOT_NAME = "s1wj-production-root-mirror"
S1WJ_MODE = "INJECTED_TEMPORARY_MIRROR_ONLY"
S1WJ_INVALID_MIRROR_ROOT = "S1WJ_INVALID_MIRROR_ROOT"
S1WJ_PRODUCTION_ROOT_BLOCKED = "S1WJ_PRODUCTION_ROOT_BLOCKED"
S1WJ_INVALID_INJECTED_RESOURCE = "S1WJ_INVALID_INJECTED_RESOURCE"
S1WJ_PRODUCTION_EXECUTION_BLOCKED = "S1WJ_PRODUCTION_EXECUTION_BLOCKED"

_PROJECT_ROOT = Path(__file__).absolute().parents[1]
_PRODUCTION_ROOT = _PROJECT_ROOT / S1WJ_PRODUCTION_RELATIVE_ROOT
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_VOLUME = re.compile(r"^[A-Z0-9][A-Z0-9_.:-]{1,80}$")


class S1WJAdapterError(ValueError):
    """One fail-closed S1-WJ injected adapter boundary violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _canonical_bytes(payload: object) -> bytes:
    return json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _digest(payload: object) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


@dataclass(frozen=True, slots=True)
class S1WJRootMirrorReceipt:
    declared_production_relative_root: str
    mirror_root_digest: str
    artifact_volume_identity: str
    temporary_volume_identity: str
    same_volume: bool
    mirror_only: bool
    production_root_accessed: bool
    filesystem_write_count: int
    production_artifact_count: int
    receipt_digest: str

    def __post_init__(self) -> None:
        if (
            self.declared_production_relative_root
            != S1WJ_PRODUCTION_RELATIVE_ROOT
            or not _valid_digest(self.mirror_root_digest)
            or _VOLUME.fullmatch(self.artifact_volume_identity) is None
            or _VOLUME.fullmatch(self.temporary_volume_identity) is None
            or self.same_volume is not (
                self.artifact_volume_identity == self.temporary_volume_identity
            )
            or self.mirror_only is not True
            or self.production_root_accessed is not False
            or self.filesystem_write_count != 0
            or self.production_artifact_count != 0
            or self.receipt_digest != _digest(self.payload_without_digest())
        ):
            raise S1WJAdapterError(
                S1WJ_INVALID_MIRROR_ROOT,
                "invalid injected root mirror receipt",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": S1WJ_SCHEMA_VERSION,
            "mode": S1WJ_MODE,
            "contract_digest": S1WJ_CONTRACT_DIGEST,
            "declared_production_relative_root": (
                self.declared_production_relative_root
            ),
            "mirror_root_digest": self.mirror_root_digest,
            "artifact_volume_identity": self.artifact_volume_identity,
            "temporary_volume_identity": self.temporary_volume_identity,
            "same_volume": self.same_volume,
            "mirror_only": self.mirror_only,
            "production_root_accessed": self.production_root_accessed,
            "filesystem_write_count": self.filesystem_write_count,
            "production_artifact_count": self.production_artifact_count,
        }

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "receipt_digest": self.receipt_digest,
        }


@dataclass(frozen=True, slots=True)
class S1WJInjectedResourceReceipt:
    root_receipt_digest: str
    observation: S1WAProductionResourceObservation
    gate: S1WAProductionResourceGate
    injected_value_count: int
    operating_system_probe_count: int
    filesystem_write_count: int
    production_root_access_count: int
    production_artifact_count: int
    receipt_digest: str

    def __post_init__(self) -> None:
        if (
            not _valid_digest(self.root_receipt_digest)
            or not isinstance(self.observation, S1WAProductionResourceObservation)
            or not isinstance(self.gate, S1WAProductionResourceGate)
            or self.gate.observation_digest != self.observation.observation_digest
            or self.injected_value_count != 4
            or any(
                value != 0
                for value in (
                    self.operating_system_probe_count,
                    self.filesystem_write_count,
                    self.production_root_access_count,
                    self.production_artifact_count,
                )
            )
            or self.receipt_digest != _digest(self.payload_without_digest())
        ):
            raise S1WJAdapterError(
                S1WJ_INVALID_INJECTED_RESOURCE,
                "invalid injected resource receipt",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": S1WJ_SCHEMA_VERSION,
            "mode": S1WJ_MODE,
            "contract_digest": S1WJ_CONTRACT_DIGEST,
            "root_receipt_digest": self.root_receipt_digest,
            "observation": self.observation.canonical_payload(),
            "gate": self.gate.canonical_payload(),
            "injected_value_count": self.injected_value_count,
            "operating_system_probe_count": self.operating_system_probe_count,
            "filesystem_write_count": self.filesystem_write_count,
            "production_root_access_count": self.production_root_access_count,
            "production_artifact_count": self.production_artifact_count,
        }

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "receipt_digest": self.receipt_digest,
        }


def resolve_s1wj_injected_root_mirror(
    mirror_root: Path,
    artifact_volume_identity: str,
    temporary_volume_identity: str,
) -> S1WJRootMirrorReceipt:
    """Validate only a dedicated OS-temp mirror, never the production root."""

    if not isinstance(mirror_root, Path):
        raise S1WJAdapterError(
            S1WJ_INVALID_MIRROR_ROOT,
            "mirror root must be a Path",
        )
    lexical = mirror_root.absolute()
    if lexical == _PRODUCTION_ROOT or _PRODUCTION_ROOT in lexical.parents:
        raise S1WJAdapterError(
            S1WJ_PRODUCTION_ROOT_BLOCKED,
            "S1-WJ cannot access the production artifact root",
        )
    resolved = mirror_root.resolve()
    temporary = Path(gettempdir()).resolve()
    if (
        resolved.name != S1WJ_MIRROR_ROOT_NAME
        or not resolved.is_dir()
        or temporary not in resolved.parents
        or _VOLUME.fullmatch(artifact_volume_identity) is None
        or _VOLUME.fullmatch(temporary_volume_identity) is None
    ):
        raise S1WJAdapterError(
            S1WJ_INVALID_MIRROR_ROOT,
            "S1-WJ requires a dedicated injected OS-temp mirror",
        )
    values = {
        "declared_production_relative_root": S1WJ_PRODUCTION_RELATIVE_ROOT,
        "mirror_root_digest": _digest(
            {
                "mode": S1WJ_MODE,
                "resolved_mirror_root": resolved.as_posix(),
            }
        ),
        "artifact_volume_identity": artifact_volume_identity,
        "temporary_volume_identity": temporary_volume_identity,
        "same_volume": artifact_volume_identity == temporary_volume_identity,
        "mirror_only": True,
        "production_root_accessed": False,
        "filesystem_write_count": 0,
        "production_artifact_count": 0,
    }
    payload = {
        "schema_version": S1WJ_SCHEMA_VERSION,
        "mode": S1WJ_MODE,
        "contract_digest": S1WJ_CONTRACT_DIGEST,
        **values,
    }
    return S1WJRootMirrorReceipt(
        **values,
        receipt_digest=_digest(payload),
    )


def observe_s1wj_injected_resources(
    root_receipt: S1WJRootMirrorReceipt,
    available_physical_memory_bytes: int,
    artifact_volume_free_bytes: int,
    atomic_replace_probe_passed: bool,
    artifact_paths_free: bool,
    *,
    platform_binding: tuple[tuple[str, str], ...] = S1WB_PLATFORM_BINDING,
    source_digests: tuple[
        tuple[str, str], ...
    ] = S1WB_CALIBRATED_SOURCE_DIGESTS,
) -> S1WJInjectedResourceReceipt:
    """Evaluate injected values only; perform no operating-system probe."""

    if not isinstance(root_receipt, S1WJRootMirrorReceipt):
        raise S1WJAdapterError(
            S1WJ_INVALID_INJECTED_RESOURCE,
            "resource adapter requires a root mirror receipt",
        )
    observation = build_s1wb_injected_observation(
        available_physical_memory_bytes,
        artifact_volume_free_bytes,
        platform_binding=platform_binding,
        source_digests=source_digests,
        artifact_volume_identity=root_receipt.artifact_volume_identity,
        temporary_volume_identity=root_receipt.temporary_volume_identity,
        same_volume=root_receipt.same_volume,
        atomic_replace_probe_passed=atomic_replace_probe_passed,
        artifact_paths_free=artifact_paths_free,
    )
    gate = evaluate_s1wb_resource_gate(observation)
    values = {
        "root_receipt_digest": root_receipt.receipt_digest,
        "observation": observation,
        "gate": gate,
        "injected_value_count": 4,
        "operating_system_probe_count": 0,
        "filesystem_write_count": 0,
        "production_root_access_count": 0,
        "production_artifact_count": 0,
    }
    payload = {
        "schema_version": S1WJ_SCHEMA_VERSION,
        "mode": S1WJ_MODE,
        "contract_digest": S1WJ_CONTRACT_DIGEST,
        "root_receipt_digest": root_receipt.receipt_digest,
        "observation": observation.canonical_payload(),
        "gate": gate.canonical_payload(),
        "injected_value_count": 4,
        "operating_system_probe_count": 0,
        "filesystem_write_count": 0,
        "production_root_access_count": 0,
        "production_artifact_count": 0,
    }
    return S1WJInjectedResourceReceipt(
        **values,
        receipt_digest=_digest(payload),
    )


def build_s1wj_h0b_adapter(
    receipt: S1WJRootMirrorReceipt,
) -> S1WHInjectedStageAdapter:
    if not isinstance(receipt, S1WJRootMirrorReceipt):
        raise S1WJAdapterError(
            S1WJ_INVALID_MIRROR_ROOT,
            "H0B adapter requires a root mirror receipt",
        )
    return S1WHInjectedStageAdapter(
        "s1wh.injected.root",
        "H0B",
        passed=receipt.same_volume,
        detail_role=f"S1WJ_ROOT_{receipt.receipt_digest}",
    )


def build_s1wj_h0c_adapter(
    receipt: S1WJInjectedResourceReceipt,
) -> S1WHInjectedStageAdapter:
    if not isinstance(receipt, S1WJInjectedResourceReceipt):
        raise S1WJAdapterError(
            S1WJ_INVALID_INJECTED_RESOURCE,
            "H0C adapter requires an injected resource receipt",
        )
    return S1WHInjectedStageAdapter(
        "s1wh.injected.resource",
        "H0C",
        passed=receipt.gate.all_resource_gates_passed,
        detail_role=f"S1WJ_RESOURCE_{receipt.receipt_digest}",
    )


def execute_s1wj_production_once() -> None:
    raise S1WJAdapterError(
        S1WJ_PRODUCTION_EXECUTION_BLOCKED,
        "S1-WJ authorizes injected temporary mirror adapters only",
    )
