"""S1-GT synthetic-only lifecycle fixture for a process-local token."""

from __future__ import annotations

from dataclasses import dataclass
from threading import Lock

from .e1_formation_s1gs_real_single_batch_gate_contract import (
    E1FormationS1GSRealSingleBatchGateContract,
    build_e1_formation_s1gs_real_single_batch_gate_contract,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1GTSyntheticSingleUseTokenError(ValueError):
    """Raised when the synthetic token is copied, replayed, or widened."""


S1_GT_FIXTURE_ID = "e1.synthetic-token-authorization-fixture.s1gt.v1"
S1_GT_TOKEN_ID = "e1.synthetic-process-local-single-use-token.s1gt.v1"
S1_GT_RESULT_ID = "e1.synthetic-token-lifecycle-result.s1gt.v1"
S1_GT_SCOPE = "synthetic-fixture-only-no-owner-authorization"
S1_GT_OUTCOMES = ("synthetic-success", "synthetic-failure")


@dataclass(frozen=True, slots=True)
class E1FormationS1GTSyntheticAuthorizationFixture:
    fixture_id: str
    source_s1gs_gate_digest: str
    authorization_origin: str
    authorization_scope: str
    maximum_adapter_calls: int
    maximum_field_steps: int
    external_owner_authorization: bool
    real_token_creation_permitted: bool
    execution_permitted: bool
    fixture_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "fixture_digest"
        }
        if (
            self.fixture_id != S1_GT_FIXTURE_ID
            or len(self.source_s1gs_gate_digest) != 64
            or self.authorization_origin != "internal-synthetic-test-fixture"
            or self.authorization_scope != S1_GT_SCOPE
            or self.maximum_adapter_calls != 1
            or self.maximum_field_steps != 1
            or self.external_owner_authorization is not False
            or self.real_token_creation_permitted is not False
            or self.execution_permitted is not False
            or self.fixture_digest != _digest(payload)
        ):
            raise E1FormationS1GTSyntheticSingleUseTokenError(
                "S1-GT fixture was widened into owner authorization"
            )


def build_e1_formation_s1gt_synthetic_authorization_fixture(
    gate: E1FormationS1GSRealSingleBatchGateContract,
) -> E1FormationS1GTSyntheticAuthorizationFixture:
    """Build a non-owner fixture from an exactly closed S1-GS contract."""

    if not isinstance(gate, E1FormationS1GSRealSingleBatchGateContract):
        raise E1FormationS1GTSyntheticSingleUseTokenError(
            "S1-GT requires the exact closed S1-GS gate"
        )
    gate.__post_init__()
    if (
        gate.authorization_present is not False
        or gate.token_creation_permitted is not False
        or gate.execution_permitted is not False
        or gate.maximum_adapter_calls != 1
        or gate.maximum_field_steps != 1
    ):
        raise E1FormationS1GTSyntheticSingleUseTokenError(
            "S1-GT source gate is not closed at one batch and one step"
        )
    values = {
        "fixture_id": S1_GT_FIXTURE_ID,
        "source_s1gs_gate_digest": gate.gate_digest,
        "authorization_origin": "internal-synthetic-test-fixture",
        "authorization_scope": S1_GT_SCOPE,
        "maximum_adapter_calls": 1,
        "maximum_field_steps": 1,
        "external_owner_authorization": False,
        "real_token_creation_permitted": False,
        "execution_permitted": False,
    }
    return E1FormationS1GTSyntheticAuthorizationFixture(
        **values,
        fixture_digest=_digest(values),
    )


class E1FormationS1GTSyntheticSingleUseToken:
    """One noncopyable process-local token used only by synthetic tests."""

    __slots__ = (
        "token_id",
        "fixture_digest",
        "authorization_scope",
        "maximum_adapter_calls",
        "maximum_field_steps",
        "token_digest",
        "_status",
        "_outcome",
        "_lock",
    )

    def __init__(
        self,
        fixture: E1FormationS1GTSyntheticAuthorizationFixture,
    ) -> None:
        if not isinstance(fixture, E1FormationS1GTSyntheticAuthorizationFixture):
            raise E1FormationS1GTSyntheticSingleUseTokenError(
                "S1-GT token requires the exact synthetic fixture"
            )
        fixture.__post_init__()
        self.token_id = S1_GT_TOKEN_ID
        self.fixture_digest = fixture.fixture_digest
        self.authorization_scope = fixture.authorization_scope
        self.maximum_adapter_calls = fixture.maximum_adapter_calls
        self.maximum_field_steps = fixture.maximum_field_steps
        self.token_digest = _digest(
            (
                self.token_id,
                self.fixture_digest,
                self.authorization_scope,
                self.maximum_adapter_calls,
                self.maximum_field_steps,
            )
        )
        self._status = "issued"
        self._outcome: str | None = None
        self._lock = Lock()

    def __setattr__(self, name, value) -> None:
        if hasattr(self, name):
            raise E1FormationS1GTSyntheticSingleUseTokenError(
                "S1-GT token metadata and lifecycle cannot be reassigned"
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
        """Consume this synthetic object exactly once before a fake call."""

        with self._lock:
            if self._status != "issued":
                raise E1FormationS1GTSyntheticSingleUseTokenError(
                    "S1-GT token is already consumed or retired"
                )
            object.__setattr__(self, "_status", "consumed")

    def retire(self, outcome: str) -> None:
        """Retire after synthetic success or failure; no reuse is possible."""

        if outcome not in S1_GT_OUTCOMES:
            raise E1FormationS1GTSyntheticSingleUseTokenError(
                "S1-GT token outcome is not synthetic"
            )
        with self._lock:
            if self._status == "retired":
                raise E1FormationS1GTSyntheticSingleUseTokenError(
                    "S1-GT token is already retired"
                )
            if outcome == "synthetic-success" and self._status != "consumed":
                raise E1FormationS1GTSyntheticSingleUseTokenError(
                    "S1-GT success requires prior token consumption"
                )
            object.__setattr__(self, "_status", "retired")
            object.__setattr__(self, "_outcome", outcome)

    def __copy__(self):
        raise E1FormationS1GTSyntheticSingleUseTokenError(
            "S1-GT token cannot be copied"
        )

    def __deepcopy__(self, memo):
        raise E1FormationS1GTSyntheticSingleUseTokenError(
            "S1-GT token cannot be deep-copied"
        )

    def __reduce__(self):
        raise E1FormationS1GTSyntheticSingleUseTokenError(
            "S1-GT token cannot be serialized"
        )


def issue_e1_formation_s1gt_synthetic_single_use_token(
    fixture: E1FormationS1GTSyntheticAuthorizationFixture,
) -> E1FormationS1GTSyntheticSingleUseToken:
    """Issue only the synthetic fixture token, never a real gate token."""

    return E1FormationS1GTSyntheticSingleUseToken(fixture)


@dataclass(frozen=True, slots=True)
class E1FormationS1GTSyntheticTokenLifecycleResult:
    result_id: str
    source_s1gs_gate_digest: str
    fixture_digest: str
    success_token_consumed_before_retirement: bool
    success_token_retired: bool
    failure_before_consumption_retired: bool
    failure_after_consumption_retired: bool
    replay_after_consumption_rejected: bool
    replay_after_retirement_rejected: bool
    success_without_consumption_rejected: bool
    copy_rejected: bool
    deepcopy_rejected: bool
    serialization_rejected: bool
    external_owner_authorization: bool
    real_token_created: bool
    adapter_calls: int
    field_steps_executed: int
    persistence_performed: bool
    claims_permitted: bool
    decision: str
    result_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "result_digest"
        }
        if (
            self.result_id != S1_GT_RESULT_ID
            or len(self.source_s1gs_gate_digest) != 64
            or len(self.fixture_digest) != 64
            or any(
                value is not True
                for value in (
                    self.success_token_consumed_before_retirement,
                    self.success_token_retired,
                    self.failure_before_consumption_retired,
                    self.failure_after_consumption_retired,
                    self.replay_after_consumption_rejected,
                    self.replay_after_retirement_rejected,
                    self.success_without_consumption_rejected,
                    self.copy_rejected,
                    self.deepcopy_rejected,
                    self.serialization_rejected,
                )
            )
            or any(
                value is not False
                for value in (
                    self.external_owner_authorization,
                    self.real_token_created,
                    self.persistence_performed,
                    self.claims_permitted,
                )
            )
            or self.adapter_calls != 0
            or self.field_steps_executed != 0
            or self.decision
            != "SYNTHETIC_SINGLE_USE_TOKEN_LIFECYCLE_VALIDATED_REAL_GATE_CLOSED"
            or self.result_digest != _digest(payload)
        ):
            raise E1FormationS1GTSyntheticSingleUseTokenError(
                "S1-GT lifecycle result opened a real authorization path"
            )


def exercise_e1_formation_s1gt_synthetic_token_lifecycle(
) -> E1FormationS1GTSyntheticTokenLifecycleResult:
    """Exercise token states only; no adapter or field function is available."""

    import copy
    import pickle

    gate = build_e1_formation_s1gs_real_single_batch_gate_contract()
    fixture = build_e1_formation_s1gt_synthetic_authorization_fixture(gate)

    success = issue_e1_formation_s1gt_synthetic_single_use_token(fixture)
    success.consume()
    consumed_before_retirement = success.consumed
    success.retire("synthetic-success")

    failure_before = issue_e1_formation_s1gt_synthetic_single_use_token(fixture)
    failure_before.retire("synthetic-failure")

    failure_after = issue_e1_formation_s1gt_synthetic_single_use_token(fixture)
    failure_after.consume()
    try:
        failure_after.consume()
    except E1FormationS1GTSyntheticSingleUseTokenError:
        replay_after_consumption_rejected = True
    else:
        replay_after_consumption_rejected = False
    failure_after.retire("synthetic-failure")
    try:
        failure_after.consume()
    except E1FormationS1GTSyntheticSingleUseTokenError:
        replay_after_retirement_rejected = True
    else:
        replay_after_retirement_rejected = False

    premature_success = issue_e1_formation_s1gt_synthetic_single_use_token(
        fixture
    )
    try:
        premature_success.retire("synthetic-success")
    except E1FormationS1GTSyntheticSingleUseTokenError:
        success_without_consumption_rejected = True
    else:
        success_without_consumption_rejected = False
    premature_success.retire("synthetic-failure")

    protected = issue_e1_formation_s1gt_synthetic_single_use_token(fixture)
    try:
        copy.copy(protected)
    except E1FormationS1GTSyntheticSingleUseTokenError:
        copy_rejected = True
    else:
        copy_rejected = False
    try:
        copy.deepcopy(protected)
    except E1FormationS1GTSyntheticSingleUseTokenError:
        deepcopy_rejected = True
    else:
        deepcopy_rejected = False
    try:
        pickle.dumps(protected)
    except E1FormationS1GTSyntheticSingleUseTokenError:
        serialization_rejected = True
    else:
        serialization_rejected = False
    protected.retire("synthetic-failure")

    values = {
        "result_id": S1_GT_RESULT_ID,
        "source_s1gs_gate_digest": gate.gate_digest,
        "fixture_digest": fixture.fixture_digest,
        "success_token_consumed_before_retirement": consumed_before_retirement,
        "success_token_retired": success.retired,
        "failure_before_consumption_retired": failure_before.retired,
        "failure_after_consumption_retired": failure_after.retired,
        "replay_after_consumption_rejected": replay_after_consumption_rejected,
        "replay_after_retirement_rejected": replay_after_retirement_rejected,
        "success_without_consumption_rejected": (
            success_without_consumption_rejected
        ),
        "copy_rejected": copy_rejected,
        "deepcopy_rejected": deepcopy_rejected,
        "serialization_rejected": serialization_rejected,
        "external_owner_authorization": False,
        "real_token_created": False,
        "adapter_calls": 0,
        "field_steps_executed": 0,
        "persistence_performed": False,
        "claims_permitted": False,
        "decision": (
            "SYNTHETIC_SINGLE_USE_TOKEN_LIFECYCLE_VALIDATED_REAL_GATE_CLOSED"
        ),
    }
    return E1FormationS1GTSyntheticTokenLifecycleResult(
        **values,
        result_digest=_digest(values),
    )
