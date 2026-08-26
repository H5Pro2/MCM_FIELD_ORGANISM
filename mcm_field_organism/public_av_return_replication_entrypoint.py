"""One-shot execution gate for the preflight-approved AV return replication."""

from __future__ import annotations

from dataclasses import dataclass, fields
from pathlib import Path
from typing import Callable, Generic, TypeVar

from .public_av_return_replication_preflight import PublicAVReturnReplicationPreflight
from .public_av_return_replication_runner import PublicAVReturnReplicationRunnerWiring
from .public_media_source_contract import PublicMediaSourceContract


class PublicAVReturnReplicationEntrypointError(ValueError):
    """Raised before execution when the one-shot release gate is invalid."""


ResultT = TypeVar("ResultT")


@dataclass(frozen=True, slots=True)
class PublicAVReturnReplicationExecutionReceipt:
    preflight_id: str
    runner_id: str
    source_id: str
    release_scope: str
    authorized_repeat_count: int
    execution_started: bool
    execution_completed: bool
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        if self.authorized_repeat_count != 1:
            raise PublicAVReturnReplicationEntrypointError("receipt requires one authorized execution")
        if not self.execution_started or not self.execution_completed:
            raise PublicAVReturnReplicationEntrypointError("receipt requires a completed executor call")
        if any((
            self.memory_claim_allowed,
            self.meaning_claim_allowed,
            self.organization_claim_allowed,
            self.ai_claim_allowed,
        )):
            raise PublicAVReturnReplicationEntrypointError("execution receipt cannot release claims")


class PublicAVReturnReplicationEntrypoint(Generic[ResultT]):
    """Consume one positive preflight and invoke one supplied replication executor."""

    __slots__ = ("_consumed", "_executor")

    def __init__(self, executor: Callable[[Path, PublicMediaSourceContract, PublicAVReturnReplicationRunnerWiring], ResultT]):
        if not callable(executor):
            raise PublicAVReturnReplicationEntrypointError("replication executor must be callable")
        self._executor = executor
        self._consumed = False

    @property
    def consumed(self) -> bool:
        return self._consumed

    def start_once(
        self,
        path: Path,
        contract: PublicMediaSourceContract,
        wiring: PublicAVReturnReplicationRunnerWiring,
        preflight: PublicAVReturnReplicationPreflight,
    ) -> tuple[ResultT, PublicAVReturnReplicationExecutionReceipt]:
        if self._consumed:
            raise PublicAVReturnReplicationEntrypointError("replication release was already consumed")
        _validate_release(path, contract, wiring, preflight)

        # Consume before delegation so an executor failure cannot silently authorize a retry.
        self._consumed = True
        result = self._executor(path, contract, wiring)
        receipt = PublicAVReturnReplicationExecutionReceipt(
            preflight_id=preflight.preflight_id,
            runner_id=wiring.runner_id,
            source_id=preflight.source_id,
            release_scope=preflight.release_scope,
            authorized_repeat_count=preflight.repeat_count_authorized,
            execution_started=True,
            execution_completed=True,
        )
        return result, receipt


def _validate_release(
    path: Path,
    contract: PublicMediaSourceContract,
    wiring: PublicAVReturnReplicationRunnerWiring,
    preflight: PublicAVReturnReplicationPreflight,
) -> None:
    if not isinstance(path, Path):
        raise PublicAVReturnReplicationEntrypointError("path must be a pathlib.Path")
    if not isinstance(contract, PublicMediaSourceContract):
        raise PublicAVReturnReplicationEntrypointError("source contract is required")
    if not isinstance(wiring, PublicAVReturnReplicationRunnerWiring):
        raise PublicAVReturnReplicationEntrypointError("runner wiring is required")
    if not isinstance(preflight, PublicAVReturnReplicationPreflight):
        raise PublicAVReturnReplicationEntrypointError("positive replication preflight is required")
    if not preflight.single_bounded_replication_run_release_granted:
        raise PublicAVReturnReplicationEntrypointError("single bounded replication is not released")
    if preflight.repeat_count_authorized != 1 or preflight.field_run_started:
        raise PublicAVReturnReplicationEntrypointError("preflight is not an unused one-shot release")
    if preflight.media_path != str(path):
        raise PublicAVReturnReplicationEntrypointError("preflight path differs")
    if contract.source_id != preflight.source_id or wiring.source_id != preflight.source_id:
        raise PublicAVReturnReplicationEntrypointError("source identity differs")
    if not preflight.preregistration_id_matches or wiring.preregistration_id == "":
        raise PublicAVReturnReplicationEntrypointError("preregistration identity differs")
    if not preflight.compatibility_audit_id_matches or not preflight.permutation_contract_id_matches:
        raise PublicAVReturnReplicationEntrypointError("runner contract identity differs")
    if not preflight.permutation_contract_digest_matches:
        raise PublicAVReturnReplicationEntrypointError("permutation contract digest differs")
    if not preflight.arm_ids_complete or not preflight.all_arms_wired or len(wiring.arms) != 6:
        raise PublicAVReturnReplicationEntrypointError("six complete arms are required")
    if not preflight.fixed_field_parameters_match_preregistration:
        raise PublicAVReturnReplicationEntrypointError("field parameters differ")
    if not preflight.runner_run_lock_engaged or not preflight.compatibility_run_lock_engaged:
        raise PublicAVReturnReplicationEntrypointError("underlying run locks must remain engaged")
    if preflight.release_scope != "one_public_av_six_arm_return_replication_0p5s_plus_0p1s_gap":
        raise PublicAVReturnReplicationEntrypointError("release scope differs")


def public_av_return_replication_entrypoint_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(PublicAVReturnReplicationExecutionReceipt))
