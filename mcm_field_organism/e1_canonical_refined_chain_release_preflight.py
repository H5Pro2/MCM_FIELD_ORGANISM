"""Private S1-EA3 static release preflight for the canonical refined chain."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

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


class E1CanonicalRefinedChainReleasePreflightError(ValueError):
    """Raised when the S1-EA3 release surface is incomplete or changed."""


S1_EA3_WIRING_IMPLEMENTATION_DIGEST = (
    "86e415620bf036f747cc7f95fafa97ea4b0a02d5972e46d4fa4fbb581253672b"
)
S1_EA3_EXECUTOR_IMPLEMENTATION_DIGEST = (
    "a9621b561e7aa02fd18f3f43ffdd9c02c36efb4737745906a729ce8275277c7b"
)


def _normalized_source_digest(name: str) -> str:
    path = Path(__file__).with_name(name)
    if not path.is_file():
        raise E1CanonicalRefinedChainReleasePreflightError(
            f"S1-EA3 implementation is missing: {name}"
        )
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class E1CanonicalRefinedChainReleasePreflight:
    preflight_id: str
    one_shot_contract_digest: str
    canonical_binding_digest: str
    canonical_wiring_digest: str
    producer_implementation_digest: str
    executor_implementation_digest: str
    upstream_report_path: str
    upstream_report_sha256: str
    report_path: str
    attempt_path: str
    lock_path: str
    report_fields: tuple[str, ...]
    producer_entrypoint: str
    executor_core_entrypoint: str
    producer_bound: bool
    executor_core_bound: bool
    target_paths_free: bool
    canonical_executor_bound: bool
    execution_permitted: bool
    execution_started: bool
    persistence_permitted: bool
    automatic_retry_permitted: bool
    memory_claim_permitted: bool
    ai_claim_permitted: bool

    def __post_init__(self) -> None:
        if self.preflight_id != "e1.canonical-refined-chain-release.s1ea3.v1":
            raise E1CanonicalRefinedChainReleasePreflightError(
                "S1-EA3 preflight identity changed"
            )
        for role in (
            "one_shot_contract_digest",
            "canonical_binding_digest",
            "canonical_wiring_digest",
            "producer_implementation_digest",
            "executor_implementation_digest",
            "upstream_report_sha256",
        ):
            value = getattr(self, role)
            if len(value) != 64 or any(
                char not in "0123456789abcdef" for char in value
            ):
                raise E1CanonicalRefinedChainReleasePreflightError(
                    f"{role} is not SHA-256"
                )
        if (
            self.producer_implementation_digest
            != S1_EA3_WIRING_IMPLEMENTATION_DIGEST
            or self.producer_implementation_digest
            != _normalized_source_digest("e1_canonical_refined_chain_wiring.py")
            or self.executor_implementation_digest
            != S1_EA3_EXECUTOR_IMPLEMENTATION_DIGEST
            or self.executor_implementation_digest
            != _normalized_source_digest("e1_refined_chain_one_shot_execution.py")
        ):
            raise E1CanonicalRefinedChainReleasePreflightError(
                "S1-EA3 producer or executor implementation changed"
            )
        if (
            self.report_fields != S1_DW_REPORT_FIELDS
            or self.producer_entrypoint
            != "produce_e1_canonical_refined_chain_result"
            or self.executor_core_entrypoint
            != "execute_synthetic_e1_refined_chain_one_shot"
            or self.producer_bound is not True
            or self.executor_core_bound is not True
            or self.target_paths_free is not True
        ):
            raise E1CanonicalRefinedChainReleasePreflightError(
                "S1-EA3 release roles or report surface changed"
            )
        targets = tuple(Path(value) for value in (
            self.report_path, self.attempt_path, self.lock_path
        ))
        if (
            len(set(targets)) != 3
            or len({item.parent for item in targets}) != 1
            or any(item.exists() for item in targets)
        ):
            raise E1CanonicalRefinedChainReleasePreflightError(
                "S1-EA3 target paths are not distinct free siblings"
            )
        if not Path(self.upstream_report_path).is_file():
            raise E1CanonicalRefinedChainReleasePreflightError(
                "S1-EA3 upstream report is missing"
            )
        if any(
            value is not False
            for value in (
                self.canonical_executor_bound,
                self.execution_permitted,
                self.execution_started,
                self.persistence_permitted,
                self.automatic_retry_permitted,
                self.memory_claim_permitted,
                self.ai_claim_permitted,
            )
        ):
            raise E1CanonicalRefinedChainReleasePreflightError(
                "S1-EA3 cannot release the missing canonical executor"
            )

    def digest(self) -> str:
        encoded = json.dumps(
            asdict(self),
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
        return hashlib.sha256(encoded).hexdigest()


def prepare_e1_canonical_refined_chain_release_preflight(
    report_directory: Path,
    upstream_report_path: Path,
) -> E1CanonicalRefinedChainReleasePreflight:
    """Bind producer, executor core, and paths without invoking any of them."""

    contract = prepare_e1_refined_chain_one_shot_contract(
        report_directory, upstream_report_path
    )
    binding = prepare_e1_refined_chain_canonical_producer(
        report_directory, upstream_report_path
    )
    wiring = prepare_e1_canonical_refined_chain_wiring(
        report_directory, upstream_report_path
    )
    targets = tuple(Path(value) for value in (
        contract.report_path, contract.attempt_path, contract.lock_path
    ))
    return E1CanonicalRefinedChainReleasePreflight(
        preflight_id="e1.canonical-refined-chain-release.s1ea3.v1",
        one_shot_contract_digest=contract.digest(),
        canonical_binding_digest=binding.digest(),
        canonical_wiring_digest=wiring.digest(),
        producer_implementation_digest=_normalized_source_digest(
            "e1_canonical_refined_chain_wiring.py"
        ),
        executor_implementation_digest=_normalized_source_digest(
            "e1_refined_chain_one_shot_execution.py"
        ),
        upstream_report_path=contract.upstream_report_path,
        upstream_report_sha256=contract.upstream_report_sha256,
        report_path=contract.report_path,
        attempt_path=contract.attempt_path,
        lock_path=contract.lock_path,
        report_fields=contract.report_fields,
        producer_entrypoint="produce_e1_canonical_refined_chain_result",
        executor_core_entrypoint="execute_synthetic_e1_refined_chain_one_shot",
        producer_bound=True,
        executor_core_bound=True,
        target_paths_free=not any(item.exists() for item in targets),
        canonical_executor_bound=False,
        execution_permitted=False,
        execution_started=False,
        persistence_permitted=False,
        automatic_retry_permitted=False,
        memory_claim_permitted=False,
        ai_claim_permitted=False,
    )
