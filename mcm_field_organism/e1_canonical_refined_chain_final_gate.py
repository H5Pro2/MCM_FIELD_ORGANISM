"""Private S1-EA5 final static gate before an explicit canonical one-shot."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

from .e1_canonical_refined_chain_executor_adapter import (
    prepare_e1_canonical_executor_adapter,
)
from .e1_canonical_refined_chain_release_preflight import (
    prepare_e1_canonical_refined_chain_release_preflight,
)
from .e1_canonical_refined_chain_wiring import (
    prepare_e1_canonical_refined_chain_wiring,
)
from .e1_refined_chain_canonical_producer import (
    prepare_e1_refined_chain_canonical_producer,
)
from .e1_refined_chain_one_shot_contract import (
    S1_DW_REPORT_FIELDS,
    prepare_e1_refined_chain_one_shot_contract,
)


class E1CanonicalRefinedChainFinalGateError(ValueError):
    """Raised when S1-EA5 cannot prove static one-shot readiness."""


S1_EA5_PRODUCER_IMPLEMENTATION_DIGEST = (
    "86e415620bf036f747cc7f95fafa97ea4b0a02d5972e46d4fa4fbb581253672b"
)
S1_EA5_RELEASE_IMPLEMENTATION_DIGEST = (
    "5041990a4c8598894d9674fc8277e6574eec94898dcfa5ec29985ac1c196c0c2"
)
S1_EA5_EXECUTOR_ADAPTER_IMPLEMENTATION_DIGEST = (
    "74e5ac4ee337192ecca97263bd68d7e512bfda823c924042b72a3e2d0f902508"
)


def _normalized_source_digest(name: str) -> str:
    path = Path(__file__).with_name(name)
    if not path.is_file():
        raise E1CanonicalRefinedChainFinalGateError(
            f"S1-EA5 implementation is missing: {name}"
        )
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _digest(value: object) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class E1CanonicalRefinedChainFinalGate:
    gate_id: str
    status: str
    one_shot_contract_digest: str
    canonical_binding_digest: str
    canonical_wiring_digest: str
    release_preflight_digest: str
    executor_adapter_digest: str
    producer_implementation_digest: str
    release_implementation_digest: str
    executor_adapter_implementation_digest: str
    upstream_report_sha256: str
    report_path: str
    attempt_path: str
    lock_path: str
    report_fields: tuple[str, ...]
    producer_entrypoint: str
    executor_entrypoint: str
    all_implementations_bound: bool
    all_contracts_current: bool
    target_paths_free: bool
    exactly_once_policy_bound: bool
    technical_one_shot_ready: bool
    execution_permitted: bool
    execution_started: bool
    persistence_started: bool
    automatic_retry_permitted: bool
    memory_claim_permitted: bool
    ai_claim_permitted: bool

    def __post_init__(self) -> None:
        if (
            self.gate_id != "e1.canonical-refined-chain-final-gate.s1ea5.v1"
            or self.status != "READY_FOR_EXPLICIT_ONE_SHOT_RELEASE"
        ):
            raise E1CanonicalRefinedChainFinalGateError(
                "S1-EA5 gate identity or status changed"
            )
        for role in (
            "one_shot_contract_digest",
            "canonical_binding_digest",
            "canonical_wiring_digest",
            "release_preflight_digest",
            "executor_adapter_digest",
            "producer_implementation_digest",
            "release_implementation_digest",
            "executor_adapter_implementation_digest",
            "upstream_report_sha256",
        ):
            value = getattr(self, role)
            if len(value) != 64 or any(
                char not in "0123456789abcdef" for char in value
            ):
                raise E1CanonicalRefinedChainFinalGateError(
                    f"{role} is not SHA-256"
                )
        implementations = (
            (
                self.producer_implementation_digest,
                S1_EA5_PRODUCER_IMPLEMENTATION_DIGEST,
                "e1_canonical_refined_chain_wiring.py",
            ),
            (
                self.release_implementation_digest,
                S1_EA5_RELEASE_IMPLEMENTATION_DIGEST,
                "e1_canonical_refined_chain_release_preflight.py",
            ),
            (
                self.executor_adapter_implementation_digest,
                S1_EA5_EXECUTOR_ADAPTER_IMPLEMENTATION_DIGEST,
                "e1_canonical_refined_chain_executor_adapter.py",
            ),
        )
        if any(
            observed != expected
            or observed != _normalized_source_digest(filename)
            for observed, expected, filename in implementations
        ):
            raise E1CanonicalRefinedChainFinalGateError(
                "S1-EA5 implementation binding changed"
            )
        if (
            self.report_fields != S1_DW_REPORT_FIELDS
            or self.producer_entrypoint
            != "produce_e1_canonical_refined_chain_result"
            or self.executor_entrypoint
            != "execute_e1_canonical_refined_chain_one_shot"
        ):
            raise E1CanonicalRefinedChainFinalGateError(
                "S1-EA5 callable or report surface changed"
            )
        targets = tuple(Path(value) for value in (
            self.report_path, self.attempt_path, self.lock_path
        ))
        if (
            len(set(targets)) != 3
            or len({item.parent for item in targets}) != 1
            or any(item.exists() for item in targets)
        ):
            raise E1CanonicalRefinedChainFinalGateError(
                "S1-EA5 target paths are not distinct free siblings"
            )
        if any(
            value is not True
            for value in (
                self.all_implementations_bound,
                self.all_contracts_current,
                self.target_paths_free,
                self.exactly_once_policy_bound,
                self.technical_one_shot_ready,
            )
        ):
            raise E1CanonicalRefinedChainFinalGateError(
                "S1-EA5 technical readiness is incomplete"
            )
        if any(
            value is not False
            for value in (
                self.execution_permitted,
                self.execution_started,
                self.persistence_started,
                self.automatic_retry_permitted,
                self.memory_claim_permitted,
                self.ai_claim_permitted,
            )
        ):
            raise E1CanonicalRefinedChainFinalGateError(
                "S1-EA5 cannot execute or publish the canonical run"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


def prepare_e1_canonical_refined_chain_final_gate(
    report_directory: Path,
    upstream_report_path: Path,
) -> E1CanonicalRefinedChainFinalGate:
    """Prove static readiness without calling producer or executor."""

    contract = prepare_e1_refined_chain_one_shot_contract(
        report_directory, upstream_report_path
    )
    binding = prepare_e1_refined_chain_canonical_producer(
        report_directory, upstream_report_path
    )
    wiring = prepare_e1_canonical_refined_chain_wiring(
        report_directory, upstream_report_path
    )
    release = prepare_e1_canonical_refined_chain_release_preflight(
        report_directory, upstream_report_path
    )
    adapter = prepare_e1_canonical_executor_adapter(
        report_directory, upstream_report_path
    )
    targets = tuple(Path(value) for value in (
        contract.report_path, contract.attempt_path, contract.lock_path
    ))
    return E1CanonicalRefinedChainFinalGate(
        gate_id="e1.canonical-refined-chain-final-gate.s1ea5.v1",
        status="READY_FOR_EXPLICIT_ONE_SHOT_RELEASE",
        one_shot_contract_digest=contract.digest(),
        canonical_binding_digest=binding.digest(),
        canonical_wiring_digest=wiring.digest(),
        release_preflight_digest=release.digest(),
        executor_adapter_digest=adapter.digest(),
        producer_implementation_digest=_normalized_source_digest(
            "e1_canonical_refined_chain_wiring.py"
        ),
        release_implementation_digest=_normalized_source_digest(
            "e1_canonical_refined_chain_release_preflight.py"
        ),
        executor_adapter_implementation_digest=_normalized_source_digest(
            "e1_canonical_refined_chain_executor_adapter.py"
        ),
        upstream_report_sha256=contract.upstream_report_sha256,
        report_path=contract.report_path,
        attempt_path=contract.attempt_path,
        lock_path=contract.lock_path,
        report_fields=contract.report_fields,
        producer_entrypoint="produce_e1_canonical_refined_chain_result",
        executor_entrypoint="execute_e1_canonical_refined_chain_one_shot",
        all_implementations_bound=True,
        all_contracts_current=True,
        target_paths_free=not any(item.exists() for item in targets),
        exactly_once_policy_bound=True,
        technical_one_shot_ready=True,
        execution_permitted=False,
        execution_started=False,
        persistence_started=False,
        automatic_retry_permitted=False,
        memory_claim_permitted=False,
        ai_claim_permitted=False,
    )
