"""Static W7-BJ contract for CONST-V R4 and later R1/R2/R4 convergence."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json


class W7BJConstVR4ConvergenceContractError(ValueError):
    """Raised when the R4 and convergence boundary changes."""


_CONTRACT_ID = "w7bj.const-v-ab-ba-r4-convergence-contract.v1"
_W7BH_CONTRACT_DIGEST = (
    "b191a837d4a00c604dba6598c038df92c76a2e5ab9e3be5f30e288f6118c3583"
)
_W7BI_RESULT_DIGEST = (
    "b4daf8e5621369d4daa8e504910a4f84bb4fcc59c0722f769dbb20924cfcbf77"
)
_W7BD_ADAPTER_DIGEST = (
    "496a795531ce61222fdfea7571f6c34079d5a6f1eb52b56798970a5de3e458db"
)
_W7Y_PLAN_DIGEST = (
    "c771a3c28c04e04a61fa24d187416ef65b17597f9af759682deb576a28c25b32"
)
_EXECUTION_ROLES = ("ab-r4-exact-repeat", "ba-r4-primary")
_PATH_BINDINGS = (("ab-r4-exact-repeat", "ab"), ("ba-r4-primary", "ba"))
_SURFACES = (
    "initial-state",
    "five-main-productions",
    "five-checkpoint-measurements",
    "all-raw-s-h-technical-scalar-samples",
    "all-runtime-diagnostics",
    "terminal-main-state",
    "result-digest",
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _payload() -> dict[str, object]:
    return {
        "contract_id": _CONTRACT_ID,
        "required_w7bh_contract_digest": _W7BH_CONTRACT_DIGEST,
        "required_w7bi_result_digest": _W7BI_RESULT_DIGEST,
        "required_w7bd_adapter_digest": _W7BD_ADAPTER_DIGEST,
        "required_w7y_plan_digest": _W7Y_PLAN_DIGEST,
        "model_id": "const-v",
        "refinement": 4,
        "execution_roles": _EXECUTION_ROLES,
        "path_bindings": _PATH_BINDINGS,
        "main_production_count_per_role": 5,
        "checkpoint_count_per_role": 5,
        "expected_sample_count_per_checkpoint": 91,
        "checkpoint_alignment_rule": "deep-copy-then-set-s-h-zero-preserve-scalar",
        "probe_returns_to_main": False,
        "repeat_comparison_surfaces": _SURFACES,
        "repeat_rule": "all-r2-canonical-surfaces-must-be-exactly-equal-with-r4",
        "repeat_failure_rule": "stop-before-ba-r4",
        "r124_convergence_evaluation_allowed_after_r4": True,
        "convergence_components": ("s", "h"),
        "convergence_roles": 35,
        "convergence_comparison_count": 70,
        "convergence_rule": "d24-less-than-d12-or-both-exact-zero-per-role-and-component",
        "epsilon_rule": "maximum-of-all-70-r2-r4-s-h-linf-distances",
        "effect_floor_rule": "ten-times-epsilon-after-convergence-only",
        "distance_evaluation_allowed_before_r4": False,
        "accept_result_values": False,
        "execution_allowed": False,
        "field_function_decision_allowed": False,
        "memory_claim_allowed": False,
    }


@dataclass(frozen=True, slots=True)
class W7BJConstVR4ConvergenceContract:
    """Immutable R4 and post-R4 convergence rules."""

    contract_id: str
    required_w7bh_contract_digest: str
    required_w7bi_result_digest: str
    required_w7bd_adapter_digest: str
    required_w7y_plan_digest: str
    model_id: str
    refinement: int
    execution_roles: tuple[str, ...]
    path_bindings: tuple[tuple[str, str], ...]
    main_production_count_per_role: int
    checkpoint_count_per_role: int
    expected_sample_count_per_checkpoint: int
    checkpoint_alignment_rule: str
    probe_returns_to_main: bool
    repeat_comparison_surfaces: tuple[str, ...]
    repeat_rule: str
    repeat_failure_rule: str
    r124_convergence_evaluation_allowed_after_r4: bool
    convergence_components: tuple[str, ...]
    convergence_roles: int
    convergence_comparison_count: int
    convergence_rule: str
    epsilon_rule: str
    effect_floor_rule: str
    distance_evaluation_allowed_before_r4: bool
    accept_result_values: bool
    execution_allowed: bool
    field_function_decision_allowed: bool
    memory_claim_allowed: bool
    contract_digest: str

    def __post_init__(self) -> None:
        payload = _payload()
        observed = {key: getattr(self, key) for key in payload}
        if observed != payload or self.contract_digest != _digest(payload):
            raise W7BJConstVR4ConvergenceContractError(
                "W7-BJ R4 convergence contract differs"
            )


def build_w7bj_const_v_r4_convergence_contract() -> W7BJConstVR4ConvergenceContract:
    """Build the value-free R4 and convergence preregistration."""

    payload = _payload()
    return W7BJConstVR4ConvergenceContract(
        *(payload[key] for key in payload),
        _digest(payload),
    )
