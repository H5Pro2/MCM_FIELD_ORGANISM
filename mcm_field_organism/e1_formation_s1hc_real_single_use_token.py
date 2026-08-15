"""S1-HC process-local single-use token for one bound real batch attempt."""

from __future__ import annotations

from threading import Lock

from .e1_formation_s1gs_real_single_batch_gate_contract import (
    E1FormationS1GSRealSingleBatchGateContract,
)
from .e1_formation_s1gw_external_owner_authorization_schema import (
    E1FormationS1GWExternalOwnerAuthorization,
)
from .e1_formation_s1gx_deterministic_single_batch_target import (
    E1FormationS1GXDeterministicSingleBatchTarget,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1HCRealSingleUseTokenError(RuntimeError):
    """Raised when issuance, consumption, retirement, or replay is invalid."""


S1_HC_TOKEN_ID = "e1.real-single-batch-token.s1hc.v1"
S1_HC_OUTCOMES = ("real-attempt-success", "real-attempt-failure")
_ISSUED_AUTHORIZATION_DIGESTS: set[str] = set()
_ISSUANCE_LOCK = Lock()


class E1FormationS1HCRealSingleUseToken:
    """Noncopyable process-local capability for exactly one adapter call."""

    __slots__ = (
        "token_id",
        "authorization_digest",
        "external_origin_receipt_digest",
        "gate_digest",
        "run_id",
        "binding_digest",
        "batch_index",
        "carrier_digest",
        "maximum_adapter_calls",
        "maximum_field_steps",
        "token_digest",
        "_status",
        "_outcome",
        "_lock",
    )

    def __init__(
        self,
        authorization: E1FormationS1GWExternalOwnerAuthorization,
    ) -> None:
        if not isinstance(
            authorization,
            E1FormationS1GWExternalOwnerAuthorization,
        ):
            raise E1FormationS1HCRealSingleUseTokenError(
                "S1-HC token requires one typed owner authorization"
            )
        authorization.__post_init__()
        self.token_id = S1_HC_TOKEN_ID
        self.authorization_digest = authorization.authorization_digest
        self.external_origin_receipt_digest = (
            authorization.external_origin_receipt_digest
        )
        self.gate_digest = authorization.gate_digest
        self.run_id = authorization.run_id
        self.binding_digest = authorization.binding_digest
        self.batch_index = authorization.batch_index
        self.carrier_digest = authorization.carrier_digest
        self.maximum_adapter_calls = authorization.maximum_adapter_calls
        self.maximum_field_steps = authorization.maximum_field_steps
        self.token_digest = _digest(
            (
                self.token_id,
                self.authorization_digest,
                self.external_origin_receipt_digest,
                self.gate_digest,
                self.run_id,
                self.binding_digest,
                self.batch_index,
                self.carrier_digest,
                self.maximum_adapter_calls,
                self.maximum_field_steps,
            )
        )
        self._status = "issued"
        self._outcome: str | None = None
        self._lock = Lock()

    def __setattr__(self, name, value) -> None:
        if hasattr(self, name):
            raise E1FormationS1HCRealSingleUseTokenError(
                "S1-HC token metadata and lifecycle cannot be reassigned"
            )
        object.__setattr__(self, name, value)

    @property
    def status(self) -> str:
        with self._lock:
            return self._status

    @property
    def consumed(self) -> bool:
        return self.status == "consumed"

    @property
    def retired(self) -> bool:
        return self.status == "retired"

    @property
    def outcome(self) -> str | None:
        with self._lock:
            return self._outcome

    def consume(self) -> None:
        """Consume exactly once immediately before the future adapter call."""

        with self._lock:
            if self._status != "issued":
                raise E1FormationS1HCRealSingleUseTokenError(
                    "S1-HC token is already consumed or retired"
                )
            object.__setattr__(self, "_status", "consumed")

    def retire(self, outcome: str) -> None:
        """Retire after success or any failure; reuse remains impossible."""

        if outcome not in S1_HC_OUTCOMES:
            raise E1FormationS1HCRealSingleUseTokenError(
                "S1-HC token outcome is invalid"
            )
        with self._lock:
            if self._status == "retired":
                raise E1FormationS1HCRealSingleUseTokenError(
                    "S1-HC token is already retired"
                )
            if outcome == "real-attempt-success" and self._status != "consumed":
                raise E1FormationS1HCRealSingleUseTokenError(
                    "S1-HC success requires prior token consumption"
                )
            object.__setattr__(self, "_status", "retired")
            object.__setattr__(self, "_outcome", outcome)

    def __copy__(self):
        raise E1FormationS1HCRealSingleUseTokenError(
            "S1-HC token cannot be copied"
        )

    def __deepcopy__(self, memo):
        raise E1FormationS1HCRealSingleUseTokenError(
            "S1-HC token cannot be deep-copied"
        )

    def __reduce__(self):
        raise E1FormationS1HCRealSingleUseTokenError(
            "S1-HC token cannot be serialized"
        )


def issue_e1_formation_s1hc_real_single_use_token(
    authorization: E1FormationS1GWExternalOwnerAuthorization,
    gate: E1FormationS1GSRealSingleBatchGateContract,
    target: E1FormationS1GXDeterministicSingleBatchTarget,
) -> E1FormationS1HCRealSingleUseToken:
    """Issue once after exact authorization, gate, and target validation."""

    if (
        not isinstance(
            authorization,
            E1FormationS1GWExternalOwnerAuthorization,
        )
        or not isinstance(gate, E1FormationS1GSRealSingleBatchGateContract)
        or not isinstance(target, E1FormationS1GXDeterministicSingleBatchTarget)
    ):
        raise E1FormationS1HCRealSingleUseTokenError(
            "S1-HC requires typed authorization, gate, and target"
        )
    authorization.__post_init__()
    gate.__post_init__()
    target.__post_init__()
    if (
        authorization.run_id != target.run_id
        or authorization.gate_digest != gate.gate_digest
        or authorization.binding_digest != target.selected_binding_digest
        or authorization.batch_index != target.selected_batch_index
        or authorization.carrier_digest != target.selected_carrier_digest
        or authorization.maximum_adapter_calls
        != gate.maximum_adapter_calls
        != target.maximum_adapter_calls
        or authorization.maximum_field_steps
        != gate.maximum_field_steps
        != target.maximum_field_steps
        or authorization.single_use is not True
        or authorization.non_persistent is not True
        or authorization.retry_permitted is not False
        or authorization.reparametrization_permitted is not False
        or authorization.partial_return_permitted is not False
        or authorization.claims_permitted is not False
        or authorization.expires_after_success_or_failure is not True
    ):
        raise E1FormationS1HCRealSingleUseTokenError(
            "S1-HC authorization is not bound to the exact one-batch target"
        )
    with _ISSUANCE_LOCK:
        if authorization.authorization_digest in _ISSUED_AUTHORIZATION_DIGESTS:
            raise E1FormationS1HCRealSingleUseTokenError(
                "S1-HC authorization was already used for token issuance"
            )
        token = E1FormationS1HCRealSingleUseToken(authorization)
        _ISSUED_AUTHORIZATION_DIGESTS.add(authorization.authorization_digest)
    return token
