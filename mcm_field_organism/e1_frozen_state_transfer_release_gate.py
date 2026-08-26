"""Private S1-DP final static release gate for one canonical transfer."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from .e1_frozen_state_transfer_canonical_producer import (
    prepare_e1_frozen_state_transfer_canonical_plan,
)
from .e1_frozen_state_transfer_one_shot_contract import (
    S1_DK_CONTRACT_DIGEST,
    prepare_e1_frozen_state_transfer_one_shot_contract,
)


class E1FrozenStateTransferReleaseGateError(ValueError):
    """Raised when the final S1-DP release binding is no longer exact."""


S1_DM_PROJECT_CONTRACT_DIGEST = (
    "3b98967f3922f8f06fdf0576be5e09043e7f230858f2e9f45bf5e5b02dc93d9c"
)
S1_DO_PRODUCER_DIGEST = (
    "d6dea39041b8f2b967f81a5c5c248c05d67566256d798808ed014e7221af6f75"
)
S1_DN_EXECUTOR_DIGEST = (
    "de9b98a10247d346b901c93953ee962eb63328c881383c74cf7413619922915d"
)


def _digest(value: object) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _normalized_source_digest(name: str) -> str:
    path = Path(__file__).with_name(name)
    if not path.is_file():
        raise E1FrozenStateTransferReleaseGateError(
            f"release source is missing: {name}"
        )
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def current_s1_do_producer_digest() -> str:
    return _normalized_source_digest(
        "e1_frozen_state_transfer_canonical_producer.py"
    )


def current_s1_dn_executor_digest() -> str:
    return _normalized_source_digest(
        "e1_frozen_state_transfer_one_shot_execution.py"
    )


@dataclass(frozen=True, slots=True)
class E1FrozenStateTransferReleaseGate:
    release_id: str
    execution_id: str
    history_report_path: str
    report_path: str
    attempt_path: str
    lock_path: str
    one_shot_contract_digest: str
    s1_dk_contract_digest: str
    producer_digest: str
    executor_digest: str
    probe_digest: str
    geometry_digest: str
    initial_field_digest: str
    source_support_count: int
    field_node_count: int
    edge_count: int
    canonical_execution_permitted: bool
    execution_started: bool
    history_rerun_permitted: bool
    full_s1_dc_decision_permitted: bool
    memory_claim_permitted: bool
    semantic_claim_permitted: bool
    organization_claim_permitted: bool
    topology_claim_permitted: bool
    self_regulation_claim_permitted: bool
    ai_claim_permitted: bool

    def __post_init__(self) -> None:
        if (
            self.release_id != "e1.frozen-state-transfer.s1dp.release.v1"
            or self.execution_id != "e1.frozen-state-transfer.s1dn.once.v1"
        ):
            raise E1FrozenStateTransferReleaseGateError(
                "S1-DP release identity changed"
            )
        if (
            self.one_shot_contract_digest != S1_DM_PROJECT_CONTRACT_DIGEST
            or self.s1_dk_contract_digest != S1_DK_CONTRACT_DIGEST
        ):
            raise E1FrozenStateTransferReleaseGateError(
                "registered contract digest changed"
            )
        if (
            self.producer_digest != S1_DO_PRODUCER_DIGEST
            or self.producer_digest != current_s1_do_producer_digest()
            or self.executor_digest != S1_DN_EXECUTOR_DIGEST
            or self.executor_digest != current_s1_dn_executor_digest()
        ):
            raise E1FrozenStateTransferReleaseGateError(
                "producer or executor digest changed"
            )
        if (
            self.probe_digest
            != "c0a9a59fb93996bdfd95247a1f6feec19723aeb36c84bd8bc8a423e677fbea7d"
            or self.geometry_digest
            != "6cc885c3b6cb41efcdb48cea0aecb02f980f582115e505534679beb3c427b8e6"
            or self.initial_field_digest
            != "26a53d5a379ecefb7d707df0336c0f7da1b70d0cd8484e7b6221add9a65b4ce1"
        ):
            raise E1FrozenStateTransferReleaseGateError(
                "canonical source or field digest changed"
            )
        if (
            self.source_support_count != 110
            or self.field_node_count != 84
            or self.edge_count != 145
        ):
            raise E1FrozenStateTransferReleaseGateError(
                "canonical inventory changed"
            )
        if (
            self.canonical_execution_permitted is not True
            or self.execution_started is not False
        ):
            raise E1FrozenStateTransferReleaseGateError(
                "S1-DP must release one unstarted canonical attempt"
            )
        forbidden = (
            self.history_rerun_permitted,
            self.full_s1_dc_decision_permitted,
            self.memory_claim_permitted,
            self.semantic_claim_permitted,
            self.organization_claim_permitted,
            self.topology_claim_permitted,
            self.self_regulation_claim_permitted,
            self.ai_claim_permitted,
        )
        if any(value is not False for value in forbidden):
            raise E1FrozenStateTransferReleaseGateError(
                "S1-DP cannot release history, S1-DC, or claims"
            )
        targets = tuple(Path(value) for value in self._target_path_values())
        if len(set(targets)) != 3 or len({path.parent for path in targets}) != 1:
            raise E1FrozenStateTransferReleaseGateError(
                "release target paths must be distinct siblings"
            )
        if tuple(path.name for path in targets) != (
            "e1_frozen_state_transfer_s1dn_once_v1.json",
            "e1_frozen_state_transfer_s1dn_once_v1.attempt.json",
            "e1_frozen_state_transfer_s1dn_once_v1.lock",
        ) or targets[0].parent != Path(self.history_report_path).parent:
            raise E1FrozenStateTransferReleaseGateError(
                "release target path binding changed"
            )
        if any(path.exists() for path in targets):
            raise E1FrozenStateTransferReleaseGateError(
                "release target path is already used"
            )
        if not Path(self.history_report_path).is_file():
            raise E1FrozenStateTransferReleaseGateError(
                "release history evidence is missing"
            )

    def _target_path_values(self) -> tuple[str, str, str]:
        return self.report_path, self.attempt_path, self.lock_path

    def digest(self) -> str:
        return _digest(
            {
                name: getattr(self, name)
                for name in self.__dataclass_fields__
            }
        )


def validate_e1_frozen_state_transfer_release_gate(
    gate: E1FrozenStateTransferReleaseGate,
) -> None:
    """Re-evaluate source digests and unused paths without executing a role."""

    if not isinstance(gate, E1FrozenStateTransferReleaseGate):
        raise E1FrozenStateTransferReleaseGateError(
            "canonical execution requires one S1-DP gate"
        )
    gate.__post_init__()
    current = prepare_e1_frozen_state_transfer_release_gate(
        Path(gate.report_path).parent,
        Path(gate.history_report_path),
    )
    if current.digest() != gate.digest():
        raise E1FrozenStateTransferReleaseGateError(
            "S1-DP release gate changed since preparation"
        )


def prepare_e1_frozen_state_transfer_release_gate(
    report_directory: Path,
    history_report_path: Path,
) -> E1FrozenStateTransferReleaseGate:
    """Bind final canonical readiness without invoking producer or executor."""

    contract = prepare_e1_frozen_state_transfer_one_shot_contract(
        report_directory, history_report_path
    )
    if contract.digest() != S1_DM_PROJECT_CONTRACT_DIGEST:
        raise E1FrozenStateTransferReleaseGateError(
            "project one-shot contract digest changed"
        )
    plan = prepare_e1_frozen_state_transfer_canonical_plan(history_report_path)
    if plan.execution_permitted is not False:
        raise E1FrozenStateTransferReleaseGateError(
            "canonical preflight unexpectedly released execution"
        )
    return E1FrozenStateTransferReleaseGate(
        release_id="e1.frozen-state-transfer.s1dp.release.v1",
        execution_id=contract.execution_id,
        history_report_path=contract.history_report_path,
        report_path=contract.report_path,
        attempt_path=contract.attempt_path,
        lock_path=contract.lock_path,
        one_shot_contract_digest=contract.digest(),
        s1_dk_contract_digest=contract.s1_dk_contract_digest,
        producer_digest=current_s1_do_producer_digest(),
        executor_digest=current_s1_dn_executor_digest(),
        probe_digest=plan.probe_digest,
        geometry_digest=plan.geometry_digest,
        initial_field_digest=plan.initial_field_digest,
        source_support_count=plan.source_support_count,
        field_node_count=plan.field_node_count,
        edge_count=plan.edge_count,
        canonical_execution_permitted=True,
        execution_started=False,
        history_rerun_permitted=False,
        full_s1_dc_decision_permitted=False,
        memory_claim_permitted=False,
        semantic_claim_permitted=False,
        organization_claim_permitted=False,
        topology_claim_permitted=False,
        self_regulation_claim_permitted=False,
        ai_claim_permitted=False,
    )
