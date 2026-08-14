"""Private non-executing call structure for the previous-state minimal test."""

from __future__ import annotations

from dataclasses import dataclass

from ._previous_state_minimal_runner import (
    PreviousStateMinimalRunnerError,
    _ABORT_CONDITIONS,
    _EXPECTED_ARMS,
    _INPUT_A,
    _INPUT_B,
    _INPUT_C,
    _LockedRunnerManifest,
)


@dataclass(frozen=True, slots=True)
class _ExecutorCall:
    run_id: str
    context_token: object
    role: str
    contact_id: str | None = None
    operator: str | None = None
    dissipation_config: None = None


@dataclass(frozen=True, slots=True)
class _RunStructure:
    run_id: str
    context_token: object
    calls: tuple[_ExecutorCall, ...]

    def __post_init__(self) -> None:
        if not self.calls or any(call.run_id != self.run_id for call in self.calls):
            raise PreviousStateMinimalRunnerError("run structure identity changed")
        if any(call.context_token is not self.context_token for call in self.calls):
            raise PreviousStateMinimalRunnerError("run context token changed")
        signatures = tuple(
            (call.role, call.contact_id, call.operator, call.dissipation_config)
            for call in self.calls
        )
        if signatures != _expected_call_signatures(self.run_id):
            raise PreviousStateMinimalRunnerError("fixed executor calls changed")


@dataclass(frozen=True, slots=True)
class _LockedExecutorStructure:
    runs: tuple[_RunStructure, ...]
    abort_condition_ids: tuple[str, ...]
    execution_locked: bool = True
    measurements_published: bool = False

    def __post_init__(self) -> None:
        if not self.execution_locked or self.measurements_published:
            raise PreviousStateMinimalRunnerError("executor structure must remain locked")
        if len(self.runs) != 24:
            raise PreviousStateMinimalRunnerError("executor structure requires 24 runs")
        if tuple(run.run_id for run in self.runs) != tuple(
            arm.run_id for arm in _EXPECTED_ARMS
        ):
            raise PreviousStateMinimalRunnerError("executor run order changed")
        if self.abort_condition_ids != _ABORT_CONDITIONS:
            raise PreviousStateMinimalRunnerError("executor abort conditions changed")
        tokens = tuple(run.context_token for run in self.runs)
        if len({id(token) for token in tokens}) != 24:
            raise PreviousStateMinimalRunnerError("every run requires a fresh context")


@dataclass(frozen=True, slots=True)
class _AbortStructure:
    condition_id: str
    calls_before_abort: tuple[_ExecutorCall, ...]
    further_runs_started: bool = False
    measurements_published: bool = False


_FIXED_ROLES = (
    "M0",
    "history",
    "history",
    "history",
    "M1",
    "c_distribution",
    "M2",
    "c_hook",
    "M3",
)

_ABORT_CHECKPOINTS = {
    "source_or_hook_not_frozen": 0,
    "dissipation_active_or_patch_not_isolated": 0,
    "none_identity_not_bit_equal": 72,
    "replicate_digest_mismatch": 18,
    "replicate_count_or_fresh_field_invalid": 0,
    "history_budget_duration_geometry_or_modality_mismatch": 0,
    "current_contact_c_not_byte_equal": 0,
    "generator_boundary_time_or_distribution_mismatch": 1,
    "field_dynamics_or_measurement_path_changed": 0,
    "nonfinite_or_normalized_domain_violation": 2,
    "equalized_baseline_not_equal": 144,
    "results_viewed_before_all_arms_complete": 1,
}


def _expected_call_signatures(
    run_id: str,
) -> tuple[tuple[str, str | None, str | None, None], ...]:
    try:
        arm = next(item for item in _EXPECTED_ARMS if item.run_id == run_id)
    except StopIteration as exc:
        raise PreviousStateMinimalRunnerError("unknown executor run id") from exc
    history = _INPUT_A if arm.history_id == "A" else _INPUT_B
    return (
        ("M0", None, None, None),
        *(("history", item.snapshot_id, None, None) for item in history),
        ("M1", None, None, None),
        ("c_distribution", _INPUT_C[0].snapshot_id, None, None),
        ("M2", None, None, None),
        ("c_hook", _INPUT_C[0].snapshot_id, arm.previous_state_operator, None),
        ("M3", None, None, None),
    )


def _run_calls(manifest: _LockedRunnerManifest, run_index: int) -> _RunStructure:
    arm = manifest.arms[run_index]
    history = manifest.input_a if arm.history_id == "A" else manifest.input_b
    if len(history) != 3:
        raise PreviousStateMinimalRunnerError("history requires exactly three contacts")
    token = object()
    calls = (
        _ExecutorCall(arm.run_id, token, "M0"),
        *(
            _ExecutorCall(
                arm.run_id,
                token,
                "history",
                contact_id=contact.snapshot_id,
                dissipation_config=None,
            )
            for contact in history
        ),
        _ExecutorCall(arm.run_id, token, "M1"),
        _ExecutorCall(
            arm.run_id,
            token,
            "c_distribution",
            contact_id=manifest.input_c[0].snapshot_id,
        ),
        _ExecutorCall(arm.run_id, token, "M2"),
        _ExecutorCall(
            arm.run_id,
            token,
            "c_hook",
            contact_id=manifest.input_c[0].snapshot_id,
            operator=arm.previous_state_operator,
            dissipation_config=None,
        ),
        _ExecutorCall(arm.run_id, token, "M3"),
    )
    if tuple(call.role for call in calls) != _FIXED_ROLES:
        raise PreviousStateMinimalRunnerError("executor call order changed")
    return _RunStructure(arm.run_id, token, calls)


def build_locked_executor_structure(
    manifest: _LockedRunnerManifest,
) -> _LockedExecutorStructure:
    """Build declarations only; no runtime callable is accepted or invoked."""

    if not isinstance(manifest, _LockedRunnerManifest):
        raise PreviousStateMinimalRunnerError("locked runner manifest is required")
    if not manifest.execution_locked:
        raise PreviousStateMinimalRunnerError("runner execution must remain locked")
    return _LockedExecutorStructure(
        runs=tuple(_run_calls(manifest, index) for index in range(len(manifest.arms))),
        abort_condition_ids=manifest.abort_conditions,
    )


def simulate_locked_abort(
    structure: _LockedExecutorStructure,
    condition_id: str,
) -> _AbortStructure:
    """Model an immediate pre-execution abort without invoking any call."""

    if not isinstance(structure, _LockedExecutorStructure):
        raise PreviousStateMinimalRunnerError("locked executor structure is required")
    if condition_id not in structure.abort_condition_ids:
        raise PreviousStateMinimalRunnerError("unknown abort condition")
    calls = tuple(call for run in structure.runs for call in run.calls)
    checkpoint = _ABORT_CHECKPOINTS[condition_id]
    return _AbortStructure(
        condition_id=condition_id,
        calls_before_abort=calls[:checkpoint],
    )
