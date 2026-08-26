"""Private S1-DM static one-shot contract for frozen-state AV transfer."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from .e1_frozen_state_transfer_contract import (
    S1_DK_ARMS,
    S1_DK_B_AB_DIGEST,
    S1_DK_B_BA_DIGEST,
    S1_DK_DECISIONS,
    S1_DK_METRICS,
    S1_DK_PROBE_DIGEST,
    build_e1_frozen_state_transfer_contract,
)


class E1FrozenStateTransferOneShotContractError(ValueError):
    """Raised when the S1-DM registration is changed or already used."""


S1_DK_CONTRACT_DIGEST = (
    "4574cf1caae3792a3721249dac73b4a589062051bb944fcf2f43f317b4e347f8"
)
S1_DL_IMPLEMENTATION_DIGEST = (
    "86dced5ddda7634d455fcbc50aca75eb6f64ef9b04f7f690c611edb997f2bdb6"
)
S1_DM_PARTITIONS = (
    ("coarse", (0, 1_000_000)),
    ("split", (0, 500_000, 1_000_000)),
)
S1_DM_TECHNICAL_STATUSES = S1_DK_DECISIONS
S1_DM_REPORT_FIELDS = (
    "execution_id",
    "one_shot_contract_digest",
    "s1_dk_contract_digest",
    "transfer_implementation_digest",
    "history_report_sha256",
    "history_result_sha256",
    "b_ab_digest",
    "b_ba_digest",
    "probe_digest",
    "partition_result_digests",
    "technical_status",
    "metrics",
    "controls",
    "result",
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


def _implementation_source_path() -> Path:
    return Path(__file__).with_name("e1_frozen_state_transfer.py")


def current_s1_dl_implementation_digest() -> str:
    """Hash normalized S1-DL source without importing a transfer runner."""

    path = _implementation_source_path()
    if not path.is_file():
        raise E1FrozenStateTransferOneShotContractError(
            "S1-DL transfer implementation is missing"
        )
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def s1_dm_configuration_digest() -> str:
    """Return the fixed narrow transfer execution configuration digest."""

    return _digest(
        {
            "clock_id": "organism.e1.av-history",
            "probe_horizon_ticks": [0, 1_000_000],
            "ticks_per_second": 1_000_000.0,
            "source_support_count": 110,
            "auditory_frame_count": 100,
            "visual_frame_count": 10,
            "field_node_count": 84,
            "edge_count": 145,
            "response_time_seconds": 1.0,
            "afterimage_time_constant_seconds": 0.5,
            "backreaction_gain": 0.5,
            "dissipation": None,
            "arms": S1_DK_ARMS,
            "metrics": S1_DK_METRICS,
            "partitions": S1_DM_PARTITIONS,
            "technical_statuses": S1_DM_TECHNICAL_STATUSES,
            "history_rerun_permitted": False,
            "full_s1_dc_decision_permitted": False,
        }
    )


@dataclass(frozen=True, slots=True)
class E1FrozenStateTransferOneShotContract:
    """Immutable bindings for one future canonical frozen-state transfer."""

    execution_id: str
    history_report_path: str
    report_path: str
    attempt_path: str
    lock_path: str
    s1_dk_contract_digest: str
    transfer_implementation_digest: str
    history_report_sha256: str
    history_result_sha256: str
    b_ab_digest: str
    b_ba_digest: str
    probe_digest: str
    configuration_digest: str
    partitions: tuple[tuple[str, tuple[int, ...]], ...]
    arms: tuple[str, ...]
    metrics: tuple[str, ...]
    report_fields: tuple[str, ...]
    technical_statuses: tuple[str, ...]
    result_digest_method: str
    atomic_publish_method: str
    failure_policy: str
    execution_permitted: bool
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
        if self.execution_id != "e1.frozen-state-transfer.s1dn.once.v1":
            raise E1FrozenStateTransferOneShotContractError(
                "transfer execution identity changed"
            )
        if self.s1_dk_contract_digest != S1_DK_CONTRACT_DIGEST:
            raise E1FrozenStateTransferOneShotContractError(
                "S1-DK contract binding changed"
            )
        if (
            self.transfer_implementation_digest != S1_DL_IMPLEMENTATION_DIGEST
            or self.transfer_implementation_digest
            != current_s1_dl_implementation_digest()
        ):
            raise E1FrozenStateTransferOneShotContractError(
                "S1-DL implementation digest changed"
            )
        if (self.b_ab_digest, self.b_ba_digest, self.probe_digest) != (
            S1_DK_B_AB_DIGEST,
            S1_DK_B_BA_DIGEST,
            S1_DK_PROBE_DIGEST,
        ):
            raise E1FrozenStateTransferOneShotContractError(
                "state or probe source binding changed"
            )
        if self.configuration_digest != s1_dm_configuration_digest():
            raise E1FrozenStateTransferOneShotContractError(
                "S1-DM execution configuration changed"
            )
        if (
            self.partitions != S1_DM_PARTITIONS
            or self.arms != S1_DK_ARMS
            or self.metrics != S1_DK_METRICS
        ):
            raise E1FrozenStateTransferOneShotContractError(
                "partition, arm, or metric boundary changed"
            )
        if (
            self.report_fields != S1_DM_REPORT_FIELDS
            or self.technical_statuses != S1_DM_TECHNICAL_STATUSES
        ):
            raise E1FrozenStateTransferOneShotContractError(
                "report or status boundary changed"
            )
        if (
            self.result_digest_method != "sha256-canonical-json-result"
            or self.atomic_publish_method != "same-directory-exclusive-link"
            or self.failure_policy
            != "retain-attempt-marker-no-automatic-retry"
        ):
            raise E1FrozenStateTransferOneShotContractError(
                "transfer persistence contract changed"
            )
        if self.execution_permitted is not True or self.execution_started is not False:
            raise E1FrozenStateTransferOneShotContractError(
                "transfer contract must be ready but unstarted"
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
            raise E1FrozenStateTransferOneShotContractError(
                "transfer registration cannot release history, S1-DC, or claims"
            )
        paths = tuple(Path(value) for value in self._target_path_values())
        if len(set(paths)) != 3 or len({path.parent for path in paths}) != 1:
            raise E1FrozenStateTransferOneShotContractError(
                "transfer one-shot paths must be distinct siblings"
            )
        history = Path(self.history_report_path)
        if history in paths or not history.is_file():
            raise E1FrozenStateTransferOneShotContractError(
                "published history report binding is invalid"
            )
        for role in ("history_report_sha256", "history_result_sha256"):
            value = getattr(self, role)
            if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
                raise E1FrozenStateTransferOneShotContractError(
                    f"{role} is not SHA-256"
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


def prepare_e1_frozen_state_transfer_one_shot_contract(
    report_directory: Path,
    history_report_path: Path,
) -> E1FrozenStateTransferOneShotContract:
    """Register one pristine transfer attempt without constructing its probe."""

    directory = Path(report_directory).resolve()
    history = Path(history_report_path).resolve()
    if not directory.is_dir():
        raise E1FrozenStateTransferOneShotContractError(
            "transfer report directory does not exist"
        )
    try:
        evidence = build_e1_frozen_state_transfer_contract(history)
    except (ValueError, OSError) as exc:
        raise E1FrozenStateTransferOneShotContractError(
            "published history evidence is invalid"
        ) from exc
    if evidence.digest() != S1_DK_CONTRACT_DIGEST:
        raise E1FrozenStateTransferOneShotContractError(
            "S1-DK contract digest changed"
        )
    report = directory / "e1_frozen_state_transfer_s1dn_once_v1.json"
    attempt = directory / "e1_frozen_state_transfer_s1dn_once_v1.attempt.json"
    lock = directory / "e1_frozen_state_transfer_s1dn_once_v1.lock"
    if any(path.exists() for path in (report, attempt, lock)):
        raise E1FrozenStateTransferOneShotContractError(
            "transfer one-shot path is already used"
        )
    return E1FrozenStateTransferOneShotContract(
        execution_id="e1.frozen-state-transfer.s1dn.once.v1",
        history_report_path=str(history),
        report_path=str(report),
        attempt_path=str(attempt),
        lock_path=str(lock),
        s1_dk_contract_digest=evidence.digest(),
        transfer_implementation_digest=current_s1_dl_implementation_digest(),
        history_report_sha256=evidence.history_report_sha256,
        history_result_sha256=evidence.history_result_sha256,
        b_ab_digest=evidence.b_ab_digest,
        b_ba_digest=evidence.b_ba_digest,
        probe_digest=evidence.probe_digest,
        configuration_digest=s1_dm_configuration_digest(),
        partitions=S1_DM_PARTITIONS,
        arms=S1_DK_ARMS,
        metrics=S1_DK_METRICS,
        report_fields=S1_DM_REPORT_FIELDS,
        technical_statuses=S1_DM_TECHNICAL_STATUSES,
        result_digest_method="sha256-canonical-json-result",
        atomic_publish_method="same-directory-exclusive-link",
        failure_policy="retain-attempt-marker-no-automatic-retry",
        execution_permitted=True,
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
