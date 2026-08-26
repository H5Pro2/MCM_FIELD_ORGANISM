"""Private S1-WB injected production-resource and H0 validation types."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re


S1WB_SCHEMA_VERSION = "ppb1.s1wb.private.injected-h0.v1"
S1WB_CONTRACT_DIGEST = (
    "e1d6c99f9141140c7db207513e725d3521065bab488d7541d4392db0b5218413"
)
S1WB_CALIBRATION_DIGEST = (
    "e8b0aa78c66ec3d9586cf89827f93463b5ce33cd9cf63e3c80ef64f099ff2928"
)
S1WB_RESOURCE_CONTRACT_DIGEST = (
    "ed2872f48ef83b26121bc68ce99ff75462cef9fc60915a7b5b073c45744992cd"
)
S1WB_PARENT_PLAN_DIGEST = (
    "35c1e589f749f1c1f1f24900f611fd43f8329d803a4b82ca94584d1925067ba3"
)
S1WB_CORRECTED_PLAN_DIGEST = (
    "f307363400ba66e53a49ec9cd21bc17973f93f240f3946eade2c6a7dbdcd1210"
)
S1WB_CASE_COUNT = 528
S1WB_MAXIMUM_CALL_COUNT = 75808
S1WB_MINIMUM_FREE_MEMORY_BYTES = 2 * 1024**3
S1WB_MINIMUM_FREE_DISK_BYTES = 1024**3
S1WB_PRODUCTION_ENTRYPOINT_ID = "ppb1.s1wa.production.once"
S1WB_PRODUCTION_AUTHORIZATION_BLOCKED = (
    "S1WB_PRODUCTION_AUTHORIZATION_BLOCKED"
)
S1WB_INVALID_INJECTED_OBSERVATION = "S1WB_INVALID_INJECTED_OBSERVATION"
S1WB_INVALID_RESOURCE_GATE = "S1WB_INVALID_RESOURCE_GATE"
S1WB_INVALID_AUTHORIZATION_CANDIDATE = (
    "S1WB_INVALID_AUTHORIZATION_CANDIDATE"
)
S1WB_DECISION = "BLOCKED_PRODUCTION_AUTHORIZATION_AND_PRODUCER_BINDING"

S1WB_PLATFORM_BINDING = (
    ("python_implementation", "CPython"),
    ("python_version", "3.14.4"),
    ("operating_system", "Windows"),
    ("machine_architecture", "AMD64"),
    ("pointer_width_bits", "64"),
)
S1WB_CALIBRATED_SOURCE_DIGESTS = (
    (
        "s1vq_runner",
        "c9485bf36e6bec241ac3e0c565e7b5d5ec7fc4041596557f2e3db26ecb757c48",
    ),
    (
        "s1vt_pipeline",
        "0aeba24aac5732f11500ec02f51aded07097c0e58c54b05a9f6978ff6980b891",
    ),
    (
        "s1vw_synthetic_orchestrator",
        "37ea1c2a76b1a987dc72a3999162cd730484a75a5a3cdf60f04d6562320322f0",
    ),
    (
        "s1vz_resource_calibrator",
        "8ef0268fe3e1c5d9eac1e85092f21854ed7a09992e79dbf9e8efd1066d5c42f5",
    ),
)
S1WB_AUTHORIZATION_TEMPLATE = (
    "Ich autorisiere genau einen realen PPB-1-Korrekturmatrixlauf mit 528 "
    "Faellen und maximal 75.808 registrierten Aufrufen fuer die "
    "Ausfuehrungs-ID {execution_id}, gebunden an den S1-WA-Vertragsdigest "
    "{contract_digest}, den S1-VZ-Kalibrierungsdigest "
    "e8b0aa78c66ec3d9586cf89827f93463b5ce33cd9cf63e3c80ef64f099ff2928 "
    "und den unmittelbar bestandenen Ressourcengatedigest "
    "{resource_gate_digest}. Die Freigabe wird vor dem ersten Aufruf "
    "dauerhaft verbraucht; ein Retry ist nicht erlaubt."
)

_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_SYNTHETIC_EXECUTION_ID = re.compile(
    r"^s1wb\.synthetic\.[a-z0-9][a-z0-9.-]{2,80}$"
)
_VOLUME_ID = re.compile(r"^[A-Z0-9][A-Z0-9_.:-]{1,80}$")


class S1WBValidationError(ValueError):
    """One fail-closed injected H0 boundary violation."""

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


def _binding_payload(binding: tuple[tuple[str, str], ...]) -> list[dict[str, str]]:
    return [{"role": role, "value": value} for role, value in binding]


def _source_payload(binding: tuple[tuple[str, str], ...]) -> list[dict[str, str]]:
    return [{"role": role, "digest": value} for role, value in binding]


@dataclass(frozen=True, slots=True)
class S1WAProductionResourceObservation:
    platform_binding: tuple[tuple[str, str], ...]
    source_digests: tuple[tuple[str, str], ...]
    available_physical_memory_bytes: int
    artifact_volume_free_bytes: int
    artifact_volume_identity: str
    temporary_volume_identity: str
    same_volume: bool
    atomic_replace_probe_passed: bool
    artifact_paths_free: bool
    observation_digest: str

    def __post_init__(self) -> None:
        if (
            tuple(role for role, _ in self.platform_binding)
            != tuple(role for role, _ in S1WB_PLATFORM_BINDING)
            or any(not value for _, value in self.platform_binding)
            or tuple(role for role, _ in self.source_digests)
            != tuple(role for role, _ in S1WB_CALIBRATED_SOURCE_DIGESTS)
            or any(_DIGEST.fullmatch(value) is None for _, value in self.source_digests)
            or any(
                isinstance(value, bool) or not isinstance(value, int) or value < 0
                for value in (
                    self.available_physical_memory_bytes,
                    self.artifact_volume_free_bytes,
                )
            )
            or _VOLUME_ID.fullmatch(self.artifact_volume_identity) is None
            or _VOLUME_ID.fullmatch(self.temporary_volume_identity) is None
            or not all(
                isinstance(value, bool)
                for value in (
                    self.same_volume,
                    self.atomic_replace_probe_passed,
                    self.artifact_paths_free,
                )
            )
            or self.observation_digest != _digest(self.payload_without_digest())
        ):
            raise S1WBValidationError(
                S1WB_INVALID_INJECTED_OBSERVATION,
                "invalid injected production resource observation",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": S1WB_SCHEMA_VERSION,
            "mode": "SYNTHETIC_INJECTED_H0_ONLY",
            "platform_binding": _binding_payload(self.platform_binding),
            "source_digests": _source_payload(self.source_digests),
            "available_physical_memory_bytes": (
                self.available_physical_memory_bytes
            ),
            "artifact_volume_free_bytes": self.artifact_volume_free_bytes,
            "artifact_volume_identity": self.artifact_volume_identity,
            "temporary_volume_identity": self.temporary_volume_identity,
            "same_volume": self.same_volume,
            "atomic_replace_probe_passed": self.atomic_replace_probe_passed,
            "artifact_paths_free": self.artifact_paths_free,
        }

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "observation_digest": self.observation_digest,
        }


def build_s1wb_injected_observation(
    available_physical_memory_bytes: int,
    artifact_volume_free_bytes: int,
    *,
    platform_binding: tuple[tuple[str, str], ...] = S1WB_PLATFORM_BINDING,
    source_digests: tuple[
        tuple[str, str], ...
    ] = S1WB_CALIBRATED_SOURCE_DIGESTS,
    artifact_volume_identity: str = "SYNTHETIC-VOLUME-C",
    temporary_volume_identity: str = "SYNTHETIC-VOLUME-C",
    same_volume: bool = True,
    atomic_replace_probe_passed: bool = True,
    artifact_paths_free: bool = True,
) -> S1WAProductionResourceObservation:
    values = {
        "platform_binding": platform_binding,
        "source_digests": source_digests,
        "available_physical_memory_bytes": available_physical_memory_bytes,
        "artifact_volume_free_bytes": artifact_volume_free_bytes,
        "artifact_volume_identity": artifact_volume_identity,
        "temporary_volume_identity": temporary_volume_identity,
        "same_volume": same_volume,
        "atomic_replace_probe_passed": atomic_replace_probe_passed,
        "artifact_paths_free": artifact_paths_free,
    }
    payload = {
        "schema_version": S1WB_SCHEMA_VERSION,
        "mode": "SYNTHETIC_INJECTED_H0_ONLY",
        "platform_binding": _binding_payload(platform_binding),
        "source_digests": _source_payload(source_digests),
        **{
            key: value
            for key, value in values.items()
            if key not in {"platform_binding", "source_digests"}
        },
    }
    return S1WAProductionResourceObservation(
        **values, observation_digest=_digest(payload)
    )


@dataclass(frozen=True, slots=True)
class S1WAProductionResourceGate:
    resource_contract_digest: str
    calibration_digest: str
    observation_digest: str
    minimum_free_memory_bytes: int
    minimum_free_disk_bytes: int
    memory_gate_passed: bool
    disk_gate_passed: bool
    platform_gate_passed: bool
    source_gate_passed: bool
    same_volume_gate_passed: bool
    atomic_replace_gate_passed: bool
    artifact_paths_gate_passed: bool
    all_resource_gates_passed: bool
    resource_gate_digest: str

    def __post_init__(self) -> None:
        gates = (
            self.memory_gate_passed,
            self.disk_gate_passed,
            self.platform_gate_passed,
            self.source_gate_passed,
            self.same_volume_gate_passed,
            self.atomic_replace_gate_passed,
            self.artifact_paths_gate_passed,
        )
        if (
            self.resource_contract_digest != S1WB_RESOURCE_CONTRACT_DIGEST
            or self.calibration_digest != S1WB_CALIBRATION_DIGEST
            or _DIGEST.fullmatch(self.observation_digest) is None
            or self.minimum_free_memory_bytes != S1WB_MINIMUM_FREE_MEMORY_BYTES
            or self.minimum_free_disk_bytes != S1WB_MINIMUM_FREE_DISK_BYTES
            or not all(isinstance(value, bool) for value in gates)
            or self.all_resource_gates_passed is not all(gates)
            or self.resource_gate_digest != _digest(self.payload_without_digest())
        ):
            raise S1WBValidationError(
                S1WB_INVALID_RESOURCE_GATE, "invalid production resource gate"
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": S1WB_SCHEMA_VERSION,
            "mode": "SYNTHETIC_INJECTED_H0_ONLY",
            "resource_contract_digest": self.resource_contract_digest,
            "calibration_digest": self.calibration_digest,
            "observation_digest": self.observation_digest,
            "minimum_free_memory_bytes": self.minimum_free_memory_bytes,
            "minimum_free_disk_bytes": self.minimum_free_disk_bytes,
            "memory_gate_passed": self.memory_gate_passed,
            "disk_gate_passed": self.disk_gate_passed,
            "platform_gate_passed": self.platform_gate_passed,
            "source_gate_passed": self.source_gate_passed,
            "same_volume_gate_passed": self.same_volume_gate_passed,
            "atomic_replace_gate_passed": self.atomic_replace_gate_passed,
            "artifact_paths_gate_passed": self.artifact_paths_gate_passed,
            "all_resource_gates_passed": self.all_resource_gates_passed,
        }

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "resource_gate_digest": self.resource_gate_digest,
        }


def evaluate_s1wb_resource_gate(
    observation: S1WAProductionResourceObservation,
) -> S1WAProductionResourceGate:
    if not isinstance(observation, S1WAProductionResourceObservation):
        raise S1WBValidationError(
            S1WB_INVALID_RESOURCE_GATE, "resource observation type is required"
        )
    values = {
        "resource_contract_digest": S1WB_RESOURCE_CONTRACT_DIGEST,
        "calibration_digest": S1WB_CALIBRATION_DIGEST,
        "observation_digest": observation.observation_digest,
        "minimum_free_memory_bytes": S1WB_MINIMUM_FREE_MEMORY_BYTES,
        "minimum_free_disk_bytes": S1WB_MINIMUM_FREE_DISK_BYTES,
        "memory_gate_passed": (
            observation.available_physical_memory_bytes
            >= S1WB_MINIMUM_FREE_MEMORY_BYTES
        ),
        "disk_gate_passed": (
            observation.artifact_volume_free_bytes
            >= S1WB_MINIMUM_FREE_DISK_BYTES
        ),
        "platform_gate_passed": (
            observation.platform_binding == S1WB_PLATFORM_BINDING
        ),
        "source_gate_passed": (
            observation.source_digests == S1WB_CALIBRATED_SOURCE_DIGESTS
        ),
        "same_volume_gate_passed": (
            observation.same_volume
            and observation.artifact_volume_identity
            == observation.temporary_volume_identity
        ),
        "atomic_replace_gate_passed": observation.atomic_replace_probe_passed,
        "artifact_paths_gate_passed": observation.artifact_paths_free,
    }
    values["all_resource_gates_passed"] = all(
        value for key, value in values.items() if key.endswith("_gate_passed")
    )
    probe = {
        "schema_version": S1WB_SCHEMA_VERSION,
        "mode": "SYNTHETIC_INJECTED_H0_ONLY",
        **values,
    }
    return S1WAProductionResourceGate(
        **values, resource_gate_digest=_digest(probe)
    )


@dataclass(frozen=True, slots=True)
class S1WBAuthorizationCandidate:
    execution_id: str
    rendered_authorization_text: str
    contract_digest: str
    calibration_digest: str
    resource_gate_digest: str
    authorization_candidate_digest: str

    def __post_init__(self) -> None:
        expected = S1WB_AUTHORIZATION_TEMPLATE.format(
            execution_id=self.execution_id,
            contract_digest=S1WB_CONTRACT_DIGEST,
            resource_gate_digest=self.resource_gate_digest,
        )
        if (
            _SYNTHETIC_EXECUTION_ID.fullmatch(self.execution_id) is None
            or self.rendered_authorization_text != expected
            or self.contract_digest != S1WB_CONTRACT_DIGEST
            or self.calibration_digest != S1WB_CALIBRATION_DIGEST
            or _DIGEST.fullmatch(self.resource_gate_digest) is None
            or self.authorization_candidate_digest
            != _digest(self.payload_without_digest())
        ):
            raise S1WBValidationError(
                S1WB_INVALID_AUTHORIZATION_CANDIDATE,
                "invalid synthetic authorization candidate",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": S1WB_SCHEMA_VERSION,
            "mode": "SYNTHETIC_CANDIDATE_NOT_AUTHORIZATION",
            "execution_id": self.execution_id,
            "rendered_authorization_text": self.rendered_authorization_text,
            "contract_digest": self.contract_digest,
            "calibration_digest": self.calibration_digest,
            "resource_gate_digest": self.resource_gate_digest,
            "case_count": S1WB_CASE_COUNT,
            "maximum_registered_call_count": S1WB_MAXIMUM_CALL_COUNT,
            "production_entrypoint_id": S1WB_PRODUCTION_ENTRYPOINT_ID,
            "retry_permitted": False,
            "authorization_instantiation_enabled": False,
        }


def build_s1wb_authorization_candidate(
    execution_id: str,
    gate: S1WAProductionResourceGate,
) -> S1WBAuthorizationCandidate:
    if (
        not isinstance(gate, S1WAProductionResourceGate)
        or not gate.all_resource_gates_passed
    ):
        raise S1WBValidationError(
            S1WB_INVALID_AUTHORIZATION_CANDIDATE,
            "a fully passed synthetic resource gate is required",
        )
    values = {
        "execution_id": execution_id,
        "rendered_authorization_text": S1WB_AUTHORIZATION_TEMPLATE.format(
            execution_id=execution_id,
            contract_digest=S1WB_CONTRACT_DIGEST,
            resource_gate_digest=gate.resource_gate_digest,
        ),
        "contract_digest": S1WB_CONTRACT_DIGEST,
        "calibration_digest": S1WB_CALIBRATION_DIGEST,
        "resource_gate_digest": gate.resource_gate_digest,
    }
    payload = {
        "schema_version": S1WB_SCHEMA_VERSION,
        "mode": "SYNTHETIC_CANDIDATE_NOT_AUTHORIZATION",
        **values,
        "case_count": S1WB_CASE_COUNT,
        "maximum_registered_call_count": S1WB_MAXIMUM_CALL_COUNT,
        "production_entrypoint_id": S1WB_PRODUCTION_ENTRYPOINT_ID,
        "retry_permitted": False,
        "authorization_instantiation_enabled": False,
    }
    return S1WBAuthorizationCandidate(
        **values, authorization_candidate_digest=_digest(payload)
    )


@dataclass(frozen=True, slots=True, init=False)
class S1WAProductionAuthorization:
    execution_id: str
    rendered_authorization_text: str
    contract_digest: str
    calibration_digest: str
    resource_gate_digest: str
    parent_plan_digest: str
    corrected_plan_digest: str
    case_count: int
    maximum_registered_call_count: int
    production_entrypoint_id: str
    retry_permitted: bool
    authorization_digest: str

    def __init__(self, *args: object, **kwargs: object) -> None:
        raise S1WBValidationError(
            S1WB_PRODUCTION_AUTHORIZATION_BLOCKED,
            "production authorization awaits a post-implementation preflight",
        )


@dataclass(frozen=True, slots=True)
class S1WBH0CandidateResult:
    execution_id: str
    observation_digest: str
    resource_gate_digest: str
    authorization_candidate_digest: str
    checks: tuple[tuple[str, bool], ...]
    decision: str
    producer_call_count: int
    production_artifact_count: int

    @property
    def ready_for_h1(self) -> bool:
        return all(passed for _, passed in self.checks)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": S1WB_SCHEMA_VERSION,
            "mode": "SYNTHETIC_INJECTED_H0_ONLY",
            "execution_id": self.execution_id,
            "observation_digest": self.observation_digest,
            "resource_gate_digest": self.resource_gate_digest,
            "authorization_candidate_digest": (
                self.authorization_candidate_digest
            ),
            "checks": [
                {"role": role, "passed": passed}
                for role, passed in self.checks
            ],
            "decision": self.decision,
            "producer_call_count": self.producer_call_count,
            "production_artifact_count": self.production_artifact_count,
            "ready_for_h1": self.ready_for_h1,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def validate_s1wb_h0_candidate(
    observation: S1WAProductionResourceObservation,
    execution_id: str,
) -> S1WBH0CandidateResult:
    gate = evaluate_s1wb_resource_gate(observation)
    candidate = build_s1wb_authorization_candidate(execution_id, gate)
    checks = (
        (
            "H0A_CONTRACT_PLAN_PLATFORM_SOURCE",
            gate.platform_gate_passed and gate.source_gate_passed,
        ),
        (
            "H0B_SAME_VOLUME_ATOMIC_REPLACE",
            gate.same_volume_gate_passed
            and gate.atomic_replace_gate_passed,
        ),
        (
            "H0C_MEMORY_DISK_RESOURCE_GATE",
            gate.memory_gate_passed and gate.disk_gate_passed,
        ),
        ("H0D_PRODUCTION_AUTHORIZATION_INSTANTIABLE", False),
        ("H0E_ARTIFACT_PATHS_FREE", gate.artifact_paths_gate_passed),
    )
    return S1WBH0CandidateResult(
        execution_id,
        observation.observation_digest,
        gate.resource_gate_digest,
        candidate.authorization_candidate_digest,
        checks,
        S1WB_DECISION,
        0,
        0,
    )


def execute_s1wb_production_once() -> None:
    raise S1WBValidationError(
        S1WB_PRODUCTION_AUTHORIZATION_BLOCKED,
        "S1-WB implements injected H0 validation only",
    )
