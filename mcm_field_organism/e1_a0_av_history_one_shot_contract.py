"""Private S1-DH static one-shot contract for canonical A0 AV histories."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path


class E1A0AVHistoryOneShotContractError(ValueError):
    """Raised when the S1-DH one-shot boundary changed or was already used."""


S1_DE_HISTORY_AB_DIGEST = (
    "a48d3d1620afa82d12dda855bb2ec03de3a57e7a69488d46edba6ec99cbef6d6"
)
S1_DE_HISTORY_BA_DIGEST = (
    "bb1d887f1ff5809964ae8175c7fa661430e8fbc8502f0522a7003d6c6fc3c011"
)
S1_DE_PERMUTATION_DIGEST = (
    "ad509ef23a9394009baddc8185edc5a13f76882ee79e7c31d3b0ec111bfbcc78"
)
S1_DG_PRODUCER_IMPLEMENTATION_DIGEST = (
    "25596d8280059c53c8c48a4d511e4e1b893d5f4bb848106076f56258d5d7d43c"
)
S1_DH_ALLOWED_METRICS = ("d_state", "d_total_binding")
S1_DH_TECHNICAL_STATUSES = ("E1_A0_AV_HISTORY_STATES_PRODUCED",)
S1_DH_REPORT_FIELDS = (
    "execution_id",
    "one_shot_contract_digest",
    "history_ab_digest",
    "history_ba_digest",
    "permutation_digest",
    "producer_implementation_digest",
    "configuration_digest",
    "result_digest",
    "technical_status",
    "d_state",
    "d_total_binding",
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


def _producer_source_path() -> Path:
    return Path(__file__).with_name("e1_a0_av_history_producer.py")


def current_s1_dg_producer_implementation_digest() -> str:
    """Hash normalized producer source without importing or executing it."""

    path = _producer_source_path()
    if not path.is_file():
        raise E1A0AVHistoryOneShotContractError(
            "S1-DG producer implementation is missing"
        )
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def s1_dh_configuration_digest() -> str:
    """Return the fixed S1-DF/S1-DG execution configuration digest."""

    return _digest(
        {
            "clock_id": "organism.e1.av-history",
            "horizon_ticks": [0, 2_000_000],
            "ticks_per_second": 1_000_000.0,
            "source_supports_per_arm": 220,
            "auditory_frames_per_arm": 200,
            "visual_frames_per_arm": 20,
            "auditory_carriers": 12,
            "visual_grid": [6, 4, 3],
            "visual_carriers": 72,
            "field_nodes": 84,
            "sample_offsets": [[-1, 0], [0, -1], [0, 1], [1, 0]],
            "response_time_seconds": 1.0,
            "afterimage_time_constant_seconds": 0.5,
            "dissipation": None,
            "e1_contract": {
                "contract_id": (
                    "e1.resource-conserving-local-edge-plasticity.v1"
                ),
                "node_capacity": 1.0,
                "binding_rate_per_second": 1.5,
                "release_rate_per_second": 0.25,
                "backreaction_gain": 0.5,
            },
            "history_backreaction_enabled": False,
            "internal_arms": ["ab-p0", "ab-a0", "ba-p0", "ba-a0"],
            "returned_state_roles": ["b_ab", "b_ba"],
            "allowed_metrics": S1_DH_ALLOWED_METRICS,
            "probe_permitted": False,
        }
    )


@dataclass(frozen=True, slots=True)
class E1A0AVHistoryOneShotContract:
    """Immutable bindings for exactly one future canonical history attempt."""

    execution_id: str
    report_path: str
    attempt_path: str
    lock_path: str
    history_ab_digest: str
    history_ba_digest: str
    permutation_digest: str
    producer_implementation_digest: str
    configuration_digest: str
    report_fields: tuple[str, ...]
    allowed_metrics: tuple[str, ...]
    technical_statuses: tuple[str, ...]
    result_digest_method: str
    atomic_publish_method: str
    failure_policy: str
    execution_permitted: bool
    execution_started: bool
    probe_permitted: bool
    memory_claim_permitted: bool
    semantic_claim_permitted: bool
    organization_claim_permitted: bool
    topology_claim_permitted: bool
    self_regulation_claim_permitted: bool
    ai_claim_permitted: bool

    def __post_init__(self) -> None:
        if self.execution_id != "e1.a0-av-history.s1di.once.v1":
            raise E1A0AVHistoryOneShotContractError(
                "history execution identity changed"
            )
        expected_source = (
            S1_DE_HISTORY_AB_DIGEST,
            S1_DE_HISTORY_BA_DIGEST,
            S1_DE_PERMUTATION_DIGEST,
        )
        if (
            self.history_ab_digest,
            self.history_ba_digest,
            self.permutation_digest,
        ) != expected_source:
            raise E1A0AVHistoryOneShotContractError(
                "canonical S1-DE source binding changed"
            )
        if (
            self.producer_implementation_digest
            != S1_DG_PRODUCER_IMPLEMENTATION_DIGEST
            or self.producer_implementation_digest
            != current_s1_dg_producer_implementation_digest()
        ):
            raise E1A0AVHistoryOneShotContractError(
                "S1-DG producer implementation digest changed"
            )
        if self.configuration_digest != s1_dh_configuration_digest():
            raise E1A0AVHistoryOneShotContractError(
                "S1-DH execution configuration changed"
            )
        if self.report_fields != S1_DH_REPORT_FIELDS:
            raise E1A0AVHistoryOneShotContractError(
                "history report field order changed"
            )
        if self.allowed_metrics != S1_DH_ALLOWED_METRICS:
            raise E1A0AVHistoryOneShotContractError(
                "history metric boundary changed"
            )
        if self.technical_statuses != S1_DH_TECHNICAL_STATUSES:
            raise E1A0AVHistoryOneShotContractError(
                "history technical status changed"
            )
        if (
            self.result_digest_method != "sha256-canonical-json-result"
            or self.atomic_publish_method != "same-directory-exclusive-link"
            or self.failure_policy
            != "retain-attempt-marker-no-automatic-retry"
        ):
            raise E1A0AVHistoryOneShotContractError(
                "history persistence contract changed"
            )
        if self.execution_permitted is not True or self.execution_started is not False:
            raise E1A0AVHistoryOneShotContractError(
                "history contract must be ready but unstarted"
            )
        forbidden_release_flags = (
            self.probe_permitted,
            self.memory_claim_permitted,
            self.semantic_claim_permitted,
            self.organization_claim_permitted,
            self.topology_claim_permitted,
            self.self_regulation_claim_permitted,
            self.ai_claim_permitted,
        )
        if any(value is not False for value in forbidden_release_flags):
            raise E1A0AVHistoryOneShotContractError(
                "history registration cannot release probes or claims"
            )
        paths = tuple(Path(value) for value in self._path_values())
        if len(set(paths)) != 3 or len({path.parent for path in paths}) != 1:
            raise E1A0AVHistoryOneShotContractError(
                "history one-shot paths must be distinct siblings"
            )

    def _path_values(self) -> tuple[str, str, str]:
        return self.report_path, self.attempt_path, self.lock_path

    def digest(self) -> str:
        return _digest(
            {
                name: getattr(self, name)
                for name in self.__dataclass_fields__
            }
        )


def prepare_e1_a0_av_history_one_shot_contract(
    report_directory: Path,
) -> E1A0AVHistoryOneShotContract:
    """Bind pristine paths and digests without producing either history."""

    directory = Path(report_directory).resolve()
    if not directory.is_dir():
        raise E1A0AVHistoryOneShotContractError(
            "history report directory does not exist"
        )
    report = directory / "e1_a0_av_history_s1di_once_v1.json"
    attempt = directory / "e1_a0_av_history_s1di_once_v1.attempt.json"
    lock = directory / "e1_a0_av_history_s1di_once_v1.lock"
    if any(path.exists() for path in (report, attempt, lock)):
        raise E1A0AVHistoryOneShotContractError(
            "history one-shot path is already used"
        )
    return E1A0AVHistoryOneShotContract(
        execution_id="e1.a0-av-history.s1di.once.v1",
        report_path=str(report),
        attempt_path=str(attempt),
        lock_path=str(lock),
        history_ab_digest=S1_DE_HISTORY_AB_DIGEST,
        history_ba_digest=S1_DE_HISTORY_BA_DIGEST,
        permutation_digest=S1_DE_PERMUTATION_DIGEST,
        producer_implementation_digest=(
            current_s1_dg_producer_implementation_digest()
        ),
        configuration_digest=s1_dh_configuration_digest(),
        report_fields=S1_DH_REPORT_FIELDS,
        allowed_metrics=S1_DH_ALLOWED_METRICS,
        technical_statuses=S1_DH_TECHNICAL_STATUSES,
        result_digest_method="sha256-canonical-json-result",
        atomic_publish_method="same-directory-exclusive-link",
        failure_policy="retain-attempt-marker-no-automatic-retry",
        execution_permitted=True,
        execution_started=False,
        probe_permitted=False,
        memory_claim_permitted=False,
        semantic_claim_permitted=False,
        organization_claim_permitted=False,
        topology_claim_permitted=False,
        self_regulation_claim_permitted=False,
        ai_claim_permitted=False,
    )
