"""S1-EC108 isolated synthetic r2 token and immutable return envelope."""

from __future__ import annotations

from dataclasses import dataclass, field

from .e1_common_probe_ec103_synthetic_coordinator_e2e_fixture import (
    build_e1_common_probe_ec103_synthetic_r2_result,
)
from .e1_common_probe_ec106_attestation_receipts import (
    E1CommonProbeEC106R2ProducerReceipt,
    _build_e1_common_probe_ec106_synthetic_r2_producer_receipt,
)
from .e1_common_probe_n2_r2_real_mode_coordinator import (
    E1CommonProbeN2R2RealModeCoordinatorResult,
    S1_EC67_EC59_HANDOFF_DIGEST,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeEC108R2TokenAndReturnEnvelopeError(RuntimeError):
    """Raised when the isolated token or return envelope leaves its scope."""


S1_EC108_TOKEN_ID = "e1.common-probe-r2-authorization-token.s1ec108.v1"
S1_EC108_ENVELOPE_ID = "e1.common-probe-r2-attested-return-envelope.s1ec108.v1"
S1_EC108_FIXTURE_ID = "e1.common-probe-r2-token-envelope-fixture.s1ec108.v1"
S1_EC108_SYNTHETIC_AUTHORIZATION_TEXT = (
    "S1-EC108 synthetic token fixture only; no owner execution authorization"
)


def _valid_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


class E1CommonProbeEC108R2AuthorizationToken:
    """Single-use process token; EC108 creates synthetic-scope instances only."""

    __slots__ = (
        "authorization_id",
        "authorization_digest",
        "authorization_scope",
        "source_gate_digest",
        "source_handoff_digest",
        "maximum_field_steps",
        "persistence_permitted",
        "retry_permitted",
        "_consumed",
    )

    def __init__(
        self,
        authorization_text: str,
        source_gate_digest: str,
        source_handoff_digest: str,
        *,
        authorization_scope: str,
    ) -> None:
        if (
            authorization_text != S1_EC108_SYNTHETIC_AUTHORIZATION_TEXT
            or authorization_scope != "synthetic-fixture"
            or not _valid_digest(source_gate_digest)
            or source_handoff_digest != S1_EC67_EC59_HANDOFF_DIGEST
        ):
            raise E1CommonProbeEC108R2TokenAndReturnEnvelopeError(
                "S1-EC108 permits only the closed synthetic token fixture"
            )
        self.authorization_id = S1_EC108_TOKEN_ID
        self.authorization_digest = _digest(authorization_text)
        self.authorization_scope = authorization_scope
        self.source_gate_digest = source_gate_digest
        self.source_handoff_digest = source_handoff_digest
        self.maximum_field_steps = 3208
        self.persistence_permitted = False
        self.retry_permitted = False
        self._consumed = False

    @property
    def consumed(self) -> bool:
        return self._consumed

    def consume(self) -> None:
        if self._consumed:
            raise E1CommonProbeEC108R2TokenAndReturnEnvelopeError(
                "S1-EC108 token already consumed; retry forbidden"
            )
        self._consumed = True


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC108R2AttestedCoordinatorEnvelope:
    envelope_id: str
    authorization_digest: str
    source_result_digest: str
    producer_receipt_digest: str
    result_and_receipt_returned_together: bool
    field_steps_executed: int
    persistence_performed: bool
    retry_permitted: bool
    envelope_digest: str
    token: E1CommonProbeEC108R2AuthorizationToken = field(
        repr=False, compare=False
    )
    result: E1CommonProbeN2R2RealModeCoordinatorResult = field(
        repr=False, compare=False
    )
    producer_receipt: E1CommonProbeEC106R2ProducerReceipt = field(
        repr=False, compare=False
    )

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"envelope_digest", "token", "result", "producer_receipt"}
        }
        if (
            self.envelope_id != S1_EC108_ENVELOPE_ID
            or self.token.authorization_scope != "synthetic-fixture"
            or self.token.consumed is not True
            or self.token.maximum_field_steps != 3208
            or self.token.persistence_permitted
            or self.token.retry_permitted
            or self.authorization_digest != self.token.authorization_digest
            or self.authorization_digest
            != self.producer_receipt.one_shot_authorization_digest
            or self.source_result_digest != self.result.result_digest
            or self.source_result_digest
            != self.producer_receipt.source_result_digest
            or self.producer_receipt.source_result is not self.result
            or self.producer_receipt_digest != self.producer_receipt.receipt_digest
            or self.result_and_receipt_returned_together is not True
            or self.field_steps_executed != 3208
            or self.field_steps_executed != self.result.actual_field_steps_executed
            or self.persistence_performed
            or self.retry_permitted
            or self.envelope_digest != _digest(payload)
        ):
            raise E1CommonProbeEC108R2TokenAndReturnEnvelopeError(
                "S1-EC108 attested return envelope changed or crossed scope"
            )
        self.result.__post_init__()
        self.producer_receipt.__post_init__()


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC108SyntheticLifecycleResult:
    fixture_id: str
    failure_phase: str
    token_consumed: bool
    adapter_calls: int
    envelope_returned: bool
    retry_permitted: bool
    execution_permitted: bool
    status: str
    result_digest: str
    token: E1CommonProbeEC108R2AuthorizationToken = field(
        repr=False, compare=False
    )
    envelope: E1CommonProbeEC108R2AttestedCoordinatorEnvelope | None = field(
        repr=False, compare=False
    )

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"result_digest", "token", "envelope"}
        }
        expected = {
            "before-consume": (
                False,
                False,
                "ZERO_ADAPTER_ABORT_TOKEN_FRESH_NO_ENVELOPE",
            ),
            "after-consume": (
                True,
                False,
                "TOKEN_CONSUMED_FAILURE_NO_RETRY_NO_ENVELOPE",
            ),
            "success": (
                True,
                True,
                "SYNTHETIC_TOKEN_CONSUMED_ENVELOPE_BOUND_ZERO_ADAPTERS",
            ),
        }.get(self.failure_phase)
        if (
            expected is None
            or (self.token_consumed, self.envelope_returned, self.status) != expected
            or self.token.consumed is not self.token_consumed
            or self.adapter_calls != 0
            or self.retry_permitted
            or self.execution_permitted
            or (self.envelope is not None) is not self.envelope_returned
            or self.result_digest != _digest(payload)
        ):
            raise E1CommonProbeEC108R2TokenAndReturnEnvelopeError(
                "S1-EC108 synthetic lifecycle changed"
            )
        if self.envelope is not None:
            self.envelope.__post_init__()


def _build_e1_common_probe_ec108_synthetic_token(
) -> E1CommonProbeEC108R2AuthorizationToken:
    return E1CommonProbeEC108R2AuthorizationToken(
        S1_EC108_SYNTHETIC_AUTHORIZATION_TEXT,
        _digest((S1_EC108_FIXTURE_ID, "gate")),
        S1_EC67_EC59_HANDOFF_DIGEST,
        authorization_scope="synthetic-fixture",
    )


def _build_e1_common_probe_ec108_synthetic_envelope(
    token: E1CommonProbeEC108R2AuthorizationToken,
) -> E1CommonProbeEC108R2AttestedCoordinatorEnvelope:
    if token.consumed is not True:
        raise E1CommonProbeEC108R2TokenAndReturnEnvelopeError(
            "S1-EC108 envelope requires one consumed token"
        )
    result = build_e1_common_probe_ec103_synthetic_r2_result()
    receipt = _build_e1_common_probe_ec106_synthetic_r2_producer_receipt(
        result, token.authorization_digest
    )
    values = {
        "envelope_id": S1_EC108_ENVELOPE_ID,
        "authorization_digest": token.authorization_digest,
        "source_result_digest": result.result_digest,
        "producer_receipt_digest": receipt.receipt_digest,
        "result_and_receipt_returned_together": True,
        "field_steps_executed": result.actual_field_steps_executed,
        "persistence_performed": False,
        "retry_permitted": False,
    }
    return E1CommonProbeEC108R2AttestedCoordinatorEnvelope(
        **values,
        envelope_digest=_digest(values),
        token=token,
        result=result,
        producer_receipt=receipt,
    )


def run_e1_common_probe_ec108_synthetic_lifecycle_fixture(
    failure_phase: str = "success",
) -> E1CommonProbeEC108SyntheticLifecycleResult:
    """Exercise token state and envelope binding with zero adapter calls."""

    if failure_phase not in {"before-consume", "after-consume", "success"}:
        raise E1CommonProbeEC108R2TokenAndReturnEnvelopeError(
            "S1-EC108 fixture phase changed"
        )
    token = _build_e1_common_probe_ec108_synthetic_token()
    envelope = None
    if failure_phase != "before-consume":
        token.consume()
    if failure_phase == "success":
        envelope = _build_e1_common_probe_ec108_synthetic_envelope(token)
    status = {
        "before-consume": "ZERO_ADAPTER_ABORT_TOKEN_FRESH_NO_ENVELOPE",
        "after-consume": "TOKEN_CONSUMED_FAILURE_NO_RETRY_NO_ENVELOPE",
        "success": "SYNTHETIC_TOKEN_CONSUMED_ENVELOPE_BOUND_ZERO_ADAPTERS",
    }[failure_phase]
    values = {
        "fixture_id": S1_EC108_FIXTURE_ID,
        "failure_phase": failure_phase,
        "token_consumed": token.consumed,
        "adapter_calls": 0,
        "envelope_returned": envelope is not None,
        "retry_permitted": False,
        "execution_permitted": False,
        "status": status,
    }
    return E1CommonProbeEC108SyntheticLifecycleResult(
        **values,
        result_digest=_digest(values),
        token=token,
        envelope=envelope,
    )
