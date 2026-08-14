"""Private S1-EB30 final static go/no-go audit; starts no execution."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
from pathlib import Path

from .e1_confirmation_canonical_gate_transition_contract import (
    E1ConfirmationCanonicalGateTransitionContract,
)
from .e1_confirmation_released_worker_audit import (
    E1ConfirmationReleasedWorkerAudit,
)
from .e1_refined_formation_runner import _digest


class E1ConfirmationFinalGoNoGoAuditError(ValueError):
    """Raised when S1-EB30 cannot issue its final static decision."""


S1_EA6_SHA256 = (
    "adf8b2b6c1b9fdda48062dbb1cd9149fcde462a3dc77a348aa2dfb0cb1fcaa47"
)
S1_EB25_AUDIT_DIGEST = (
    "90fc412b115196b85f17fda24446308dbdb2752ed920c3c990c926dc635ed57d"
)
S1_EB29_CONTRACT_DIGEST = (
    "d10e89809e1e35326f6b01b0b8f7a6c15b406efb380cf1a6616df3174c4d91a2"
)
S1_EB30_IMPLEMENTATION_FILES = (
    ("release_contract", "e1_confirmation_release_contract.py"),
    ("owner_authorization", "e1_confirmation_owner_authorization.py"),
    ("resource_guard", "e1_confirmation_resource_guard.py"),
    ("same_session_preflight", "e1_confirmation_same_session_preflight.py"),
    ("guarded_worker", "e1_confirmation_one_shot_worker.py"),
    ("released_worker_audit", "e1_confirmation_released_worker_audit.py"),
    ("canonical_worker_shape", "e1_confirmation_canonical_worker.py"),
    ("canonical_function_binding", "e1_confirmation_canonical_worker_binding.py"),
    ("canonical_dataflow", "e1_confirmation_canonical_dataflow_contract.py"),
    ("gate_transitions", "e1_confirmation_canonical_gate_transition_contract.py"),
)
S1_EB30_IMPLEMENTATION_DIGESTS = (
    ("release_contract", "b5353c2e2487320db02d605dcc8dbf531a94edc98d385add2a8f16f88587766f"),
    ("owner_authorization", "1b37c7362844e04693598ed2d0e5f1ca75bdcc6ce3a4c48e61516bb41cda873a"),
    ("resource_guard", "df01fef096fb463c5297b3b99b98b9e5b4d8602343c6108f1b7833b7f94a12e4"),
    ("same_session_preflight", "aa5898f7e8b8dedb49459bd87b5c011d84a4930bfd99608b17ba699a1f087151"),
    ("guarded_worker", "eae200d33ac95ded3f0190e45f01b5dbf4acc2466498cfa043b3f8bf08d8862b"),
    ("released_worker_audit", "80c1204a452ab9e38499bd34ac26d1b9c6904181856eb13f7bc655dd3543af4d"),
    ("canonical_worker_shape", "08fba35a409368c7c174b687457f2c86df074ef33eb0dc352f1a1c0db4952d75"),
    ("canonical_function_binding", "43776f29f2250180000f4407ea8365ab192b8d8d77853ef6375dbd596967a63f"),
    ("canonical_dataflow", "b6e483e4a0aaecb0eb584318e454ade19c11b0d09e378753c0f27f7162556b78"),
    ("gate_transitions", "ae71f1cd0980d5b4d141bdb4e2ec1da5fde894527ba8fd26366270105d69b428"),
)
S1_EB30_GO_REQUIREMENTS = (
    "independent_review_freigabe_bound",
    "owner_exactly_one_run_authorization_bound",
    "23800_field_steps_bound",
    "1800_second_wall_limit_enforced",
    "4_gib_job_memory_limit_enforced",
    "same_session_preflight_proven",
    "process_tree_termination_proven",
    "exactly_once_attempt_and_no_retry_proven",
    "six_canonical_functions_bound",
    "r2_r4_r8_dataflow_and_digests_bound",
    "four_minimal_gate_transitions_bound",
    "claims_rerun_and_posthoc_tuning_closed",
    "s1_ea6_unchanged",
    "canonical_targets_free",
)
S1_EB30_ONLY_REMAINING_UNIT = (
    "implement_final_canonical_worker_exactly_from_bound_contracts",
    "launch_once_under_bound_windows_job_object",
    "create_fresh_preflight_immediately_before_lock_and_attempt",
    "execute_formation_probe_composition_and_atomic_report_once",
    "preserve_attempt_and_forbid_retry_on_started_failure",
    "report_only_preregistered_technical_decision_and_raw_evidence",
)


def _normalized_digest(name: str) -> str:
    path = Path(__file__).with_name(name)
    if not path.is_file():
        raise E1ConfirmationFinalGoNoGoAuditError(
            f"S1-EB30 implementation is missing: {name}"
        )
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def current_s1_eb30_implementation_digests() -> tuple[tuple[str, str], ...]:
    return tuple(
        (role, _normalized_digest(name))
        for role, name in S1_EB30_IMPLEMENTATION_FILES
    )


@dataclass(frozen=True, slots=True)
class E1ConfirmationFinalGoNoGoAudit:
    audit_id: str
    released_worker_audit_digest: str
    gate_transition_contract_digest: str
    implementation_digests: tuple[tuple[str, str], ...]
    go_requirements: tuple[str, ...]
    satisfied_requirements: tuple[str, ...]
    only_remaining_unit: tuple[str, ...]
    s1_ea6_sha256: str
    target_paths: tuple[str, ...]
    target_paths_free: bool
    total_field_steps: int
    max_wall_seconds: int
    max_peak_rss_bytes: int
    further_adapter_steps_permitted: bool
    canonical_worker_implemented: bool
    canonical_execution_started: bool
    canonical_persistence_started: bool
    retry_permitted: bool
    posthoc_tuning_permitted: bool
    claims_permitted: bool
    decision: str
    decision_scope: str
    audit_digest: str

    def __post_init__(self) -> None:
        if (
            self.audit_id != "e1.confirmation-final-go-no-go.s1eb30.v1"
            or self.released_worker_audit_digest != S1_EB25_AUDIT_DIGEST
            or self.gate_transition_contract_digest != S1_EB29_CONTRACT_DIGEST
            or self.implementation_digests != S1_EB30_IMPLEMENTATION_DIGESTS
            or self.implementation_digests
            != current_s1_eb30_implementation_digests()
            or self.go_requirements != S1_EB30_GO_REQUIREMENTS
            or self.satisfied_requirements != S1_EB30_GO_REQUIREMENTS
            or self.only_remaining_unit != S1_EB30_ONLY_REMAINING_UNIT
            or self.s1_ea6_sha256 != S1_EA6_SHA256
            or self.total_field_steps != 23_800
            or self.max_wall_seconds != 1_800
            or self.max_peak_rss_bytes != 4 * 1024**3
        ):
            raise E1ConfirmationFinalGoNoGoAuditError(
                "S1-EB30 final inventory changed"
            )
        targets = tuple(Path(value) for value in self.target_paths)
        if (
            len(targets) != 3
            or len(set(targets)) != 3
            or self.target_paths_free is not True
            or any(path.exists() for path in targets)
        ):
            raise E1ConfirmationFinalGoNoGoAuditError(
                "S1-EB30 canonical targets are not free"
            )
        if (
            self.further_adapter_steps_permitted is not False
            or self.canonical_worker_implemented is not False
            or self.canonical_execution_started is not False
            or self.canonical_persistence_started is not False
            or self.retry_permitted is not False
            or self.posthoc_tuning_permitted is not False
            or self.claims_permitted is not False
            or self.decision != "GO_FOR_FINAL_CANONICAL_WORKER_IMPLEMENTATION"
            or self.decision_scope != "ONE_IMPLEMENTATION_AND_EXECUTION_UNIT_ONLY"
        ):
            raise E1ConfirmationFinalGoNoGoAuditError(
                "S1-EB30 decision scope changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "audit_digest"
        }
        if self.audit_digest != _digest(payload):
            raise E1ConfirmationFinalGoNoGoAuditError(
                "S1-EB30 audit digest does not match its payload"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


def audit_e1_confirmation_final_go_no_go(
    released: E1ConfirmationReleasedWorkerAudit,
    transitions: E1ConfirmationCanonicalGateTransitionContract,
) -> E1ConfirmationFinalGoNoGoAudit:
    """Issue the final static decision without implementing or executing."""

    if not isinstance(released, E1ConfirmationReleasedWorkerAudit) or (
        released.audit_digest != S1_EB25_AUDIT_DIGEST
        or released.independent_review_complete is not True
        or released.owner_one_shot_authorized is not True
        or released.resource_enforcement_bound is not True
        or released.canonical_worker_implemented is not False
    ):
        raise E1ConfirmationFinalGoNoGoAuditError(
            "S1-EB30 released-worker audit is not ready"
        )
    released.__post_init__()
    if not isinstance(
        transitions, E1ConfirmationCanonicalGateTransitionContract
    ) or (
        transitions.contract_digest != S1_EB29_CONTRACT_DIGEST
        or transitions.gates_opened_now is not False
        or transitions.canonical_execution_permitted is not False
        or transitions.retry_permitted is not False
        or transitions.claims_permitted is not False
    ):
        raise E1ConfirmationFinalGoNoGoAuditError(
            "S1-EB30 gate-transition contract is not ready"
        )
    transitions.__post_init__()
    upstream = Path(released.target_paths[0]).parent / (
        "e1_refined_formation_transfer_s1ea_once_v1.json"
    )
    if (
        not upstream.is_file()
        or hashlib.sha256(upstream.read_bytes()).hexdigest() != S1_EA6_SHA256
    ):
        raise E1ConfirmationFinalGoNoGoAuditError(
            "S1-EB30 S1-EA6 source changed"
        )
    targets = tuple(str(Path(value).resolve()) for value in released.target_paths)
    values = {
        "audit_id": "e1.confirmation-final-go-no-go.s1eb30.v1",
        "released_worker_audit_digest": released.audit_digest,
        "gate_transition_contract_digest": transitions.contract_digest,
        "implementation_digests": current_s1_eb30_implementation_digests(),
        "go_requirements": S1_EB30_GO_REQUIREMENTS,
        "satisfied_requirements": S1_EB30_GO_REQUIREMENTS,
        "only_remaining_unit": S1_EB30_ONLY_REMAINING_UNIT,
        "s1_ea6_sha256": S1_EA6_SHA256,
        "target_paths": targets,
        "target_paths_free": all(not Path(value).exists() for value in targets),
        "total_field_steps": released.total_field_steps,
        "max_wall_seconds": released.max_wall_seconds,
        "max_peak_rss_bytes": released.max_peak_rss_bytes,
        "further_adapter_steps_permitted": False,
        "canonical_worker_implemented": False,
        "canonical_execution_started": False,
        "canonical_persistence_started": False,
        "retry_permitted": False,
        "posthoc_tuning_permitted": False,
        "claims_permitted": False,
        "decision": "GO_FOR_FINAL_CANONICAL_WORKER_IMPLEMENTATION",
        "decision_scope": "ONE_IMPLEMENTATION_AND_EXECUTION_UNIT_ONLY",
    }
    return E1ConfirmationFinalGoNoGoAudit(
        **values,
        audit_digest=_digest(values),
    )
