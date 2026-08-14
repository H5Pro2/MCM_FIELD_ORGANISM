"""Static W7-BH contract for CONST-V AB/BA R2 repetitions."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json


class W7BHConstVR2RepeatContractError(ValueError):
    """Raised when the R2 repeat and raw D12 boundary changes."""


_CONTRACT_ID = "w7bh.const-v-ab-ba-r2-repeat-contract.v1"
_W7BF_CONTRACT_DIGEST = (
    "e7d819ad3eb236360ffda717e0abb8b250a4489b390179d893e755f3a0dc40d0"
)
_W7BG_RESULT_DIGEST = (
    "3d2abeda7658443639b327f33d79c304ffc1a6bdc8fa56016d7e42040c841927"
)
_W7BD_ADAPTER_DIGEST = (
    "496a795531ce61222fdfea7571f6c34079d5a6f1eb52b56798970a5de3e458db"
)
_W7Y_PLAN_DIGEST = (
    "c771a3c28c04e04a61fa24d187416ef65b17597f9af759682deb576a28c25b32"
)
_EXECUTION_ROLES = ("ab-r2-exact-repeat", "ba-r2-primary")
_PATH_BINDINGS = (("ab-r2-exact-repeat", "ab"), ("ba-r2-primary", "ba"))
_REPEAT_SURFACES = (
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
        "required_w7bf_contract_digest": _W7BF_CONTRACT_DIGEST,
        "required_w7bg_result_digest": _W7BG_RESULT_DIGEST,
        "required_w7bd_adapter_digest": _W7BD_ADAPTER_DIGEST,
        "required_w7y_plan_digest": _W7Y_PLAN_DIGEST,
        "model_id": "const-v",
        "refinement": 2,
        "execution_roles": _EXECUTION_ROLES,
        "path_bindings": _PATH_BINDINGS,
        "main_production_count_per_role": 5,
        "checkpoint_count_per_role": 5,
        "expected_sample_count_per_checkpoint": 91,
        "checkpoint_alignment_rule": "deep-copy-then-set-s-h-zero-preserve-scalar",
        "probe_returns_to_main": False,
        "repeat_comparison_surfaces": _REPEAT_SURFACES,
        "repeat_rule": "all-r1-canonical-surfaces-must-be-exactly-equal-with-r2",
        "repeat_failure_rule": "stop-before-ba-r2",
        "raw_d12_preparation_allowed": True,
        "raw_d12_surface": "same-role-r1-vs-r2-raw-s-h-technical-scalar-trajectories",
        "distance_evaluation_allowed": False,
        "epsilon_allowed": False,
        "effect_floor_allowed": False,
        "profile_comparison_allowed": False,
        "cap_comparison_allowed": False,
        "accept_result_values": False,
        "execution_allowed": False,
        "field_function_decision_allowed": False,
        "memory_claim_allowed": False,
    }


@dataclass(frozen=True, slots=True)
class W7BHConstVR2RepeatContract:
    """Immutable rules for later AB/BA R2 production and raw D12 preparation."""

    contract_id: str
    required_w7bf_contract_digest: str
    required_w7bg_result_digest: str
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
    raw_d12_preparation_allowed: bool
    raw_d12_surface: str
    distance_evaluation_allowed: bool
    epsilon_allowed: bool
    effect_floor_allowed: bool
    profile_comparison_allowed: bool
    cap_comparison_allowed: bool
    accept_result_values: bool
    execution_allowed: bool
    field_function_decision_allowed: bool
    memory_claim_allowed: bool
    contract_digest: str

    def __post_init__(self) -> None:
        payload = _payload()
        observed = {key: getattr(self, key) for key in payload}
        if observed != payload or self.contract_digest != _digest(payload):
            raise W7BHConstVR2RepeatContractError(
                "W7-BH R2 repeat contract differs"
            )


def build_w7bh_const_v_r2_repeat_contract() -> W7BHConstVR2RepeatContract:
    """Build the value-free R2 preregistration."""

    payload = _payload()
    return W7BHConstVR2RepeatContract(
        *(payload[key] for key in payload),
        _digest(payload),
    )
