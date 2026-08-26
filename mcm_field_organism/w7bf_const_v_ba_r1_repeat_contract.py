"""Static W7-BF contract for AB/R1 repeat and BA/R1 counterpath."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json


class W7BFConstVBAR1RepeatContractError(ValueError):
    """Raised when the frozen repeat and counterpath boundary changes."""


_CONTRACT_ID = "w7bf.const-v-ab-repeat-ba-r1-contract.v1"
_W7BC_CONTRACT_DIGEST = (
    "973ac16436c15352132f3103e9c91887c71e388ebb3ac62f73a29e8b8643f5f9"
)
_W7BD_ADAPTER_DIGEST = (
    "496a795531ce61222fdfea7571f6c34079d5a6f1eb52b56798970a5de3e458db"
)
_W7BE_RESULT_DIGEST = (
    "88fd9722420a94f09c15fbce9e4e0b2a283a1a56422ed653e92ef2a7aeaf8708"
)
_W7Y_PLAN_DIGEST = (
    "c771a3c28c04e04a61fa24d187416ef65b17597f9af759682deb576a28c25b32"
)
_EXECUTION_ROLES = ("ab-r1-exact-repeat", "ba-r1-primary")
_PATH_BINDINGS = (("ab-r1-exact-repeat", "ab"), ("ba-r1-primary", "ba"))
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
        "required_w7bc_contract_digest": _W7BC_CONTRACT_DIGEST,
        "required_w7bd_adapter_digest": _W7BD_ADAPTER_DIGEST,
        "required_w7be_result_digest": _W7BE_RESULT_DIGEST,
        "required_w7y_plan_digest": _W7Y_PLAN_DIGEST,
        "model_id": "const-v",
        "refinement": 1,
        "execution_roles": _EXECUTION_ROLES,
        "path_bindings": _PATH_BINDINGS,
        "main_production_count_per_role": 5,
        "checkpoint_count_per_role": 5,
        "expected_sample_count_per_checkpoint": 91,
        "checkpoint_alignment_rule": "deep-copy-then-set-s-h-zero-preserve-scalar",
        "probe_returns_to_main": False,
        "repeat_comparison_surfaces": _REPEAT_SURFACES,
        "repeat_rule": "all-canonical-w7be-surfaces-must-be-exactly-equal",
        "repeat_failure_rule": "stop-before-ba-r1",
        "ba_prefix_role": "additive.b.combined",
        "ba_continuation_role": "additive.a.step",
        "ba_source_authorization_required": True,
        "ba_comparison_surface": "raw-s-h-technical-scalar-trajectories-only",
        "ba_distance_evaluation_allowed": False,
        "r1_numerical_epsilon_allowed": False,
        "cap_comparison_allowed": False,
        "profile_comparison_allowed": False,
        "accept_result_values": False,
        "execution_allowed": False,
        "field_function_decision_allowed": False,
        "memory_claim_allowed": False,
    }


@dataclass(frozen=True, slots=True)
class W7BFConstVBAR1RepeatContract:
    """Immutable rules for a later repeat and BA/R1 consumer."""

    contract_id: str
    required_w7bc_contract_digest: str
    required_w7bd_adapter_digest: str
    required_w7be_result_digest: str
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
    ba_prefix_role: str
    ba_continuation_role: str
    ba_source_authorization_required: bool
    ba_comparison_surface: str
    ba_distance_evaluation_allowed: bool
    r1_numerical_epsilon_allowed: bool
    cap_comparison_allowed: bool
    profile_comparison_allowed: bool
    accept_result_values: bool
    execution_allowed: bool
    field_function_decision_allowed: bool
    memory_claim_allowed: bool
    contract_digest: str

    def __post_init__(self) -> None:
        payload = _payload()
        observed = {key: getattr(self, key) for key in payload}
        if observed != payload or self.contract_digest != _digest(payload):
            raise W7BFConstVBAR1RepeatContractError(
                "W7-BF repeat and BA/R1 contract differs"
            )


def build_w7bf_const_v_ba_r1_repeat_contract(
) -> W7BFConstVBAR1RepeatContract:
    """Build the preregistration without accepting or producing run values."""

    payload = _payload()
    return W7BFConstVBAR1RepeatContract(
        *(payload[key] for key in payload),
        _digest(payload),
    )
