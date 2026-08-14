"""Isolated LEAK/SAT/NORM consumption of frozen W7-AA P0 productions."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
import hashlib
import json

from .w7aa_p0_seven_path_consumer import (
    W7AAP0CheckpointResult,
    W7AAP0PathResult,
    W7AAP0SevenPathResult,
)
from .w7m_capacity_function_matrix import W7MCapacityFunctionMatrixAdapter
from .w7p_measurement_compositor import W7PObserverDriver
from .w7r_p0_s_completion_producer import compose_w7r_observer_driver
from .w7t_observer_continuation import (
    W7TObserverCheckpoint,
    W7TObserverContinuationResult,
    W7TObserverContinuationState,
    advance_w7t_observer_continuation,
    build_initial_w7t_observer_state,
    checkpoint_w7t_observer_state,
)
from .w7w_symmetric_source_family import W7WSourceAuthorization
from .w7y_seven_path_source_plan import W7YSevenPathSourcePlan


class W7ACObserverSevenPathConsumerError(ValueError):
    """Raised when observer consumption leaves the W7-AB contract."""


_CONSUMER_ID = "w7ac.observer-seven-path-consumer.v1"
_PATH_IDS = ("ab", "ag", "ba", "bg", "ua", "ub", "ug")
_MODEL_IDS = ("leak", "sat", "norm")


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _clone_observer_state(
    state: W7TObserverContinuationState,
) -> W7TObserverContinuationState:
    if not isinstance(state, W7TObserverContinuationState):
        raise W7ACObserverSevenPathConsumerError(
            "observer probe copy requires one W7-T state"
        )
    baseline = copy.deepcopy(state.baseline_state)
    clone = W7TObserverContinuationState(
        state.matrix_digest,
        state.source_path_id,
        state.model_id,
        state.equation_id,
        state.parameter_digest,
        state.clock_id,
        state.end_tick,
        state.neuron_ids,
        baseline,
        state.predecessor_state_digest,
        state.branch_source_state_digest,
        state.processed_driver_digests,
        state.state_digest,
    )
    if (
        clone is state
        or clone.baseline_state is state.baseline_state
        or clone.state_digest != state.state_digest
        or clone.baseline_state.latent != state.baseline_state.latent
    ):
        raise W7ACObserverSevenPathConsumerError(
            "observer probe copy is not independent and digest-equal"
        )
    return clone


def _envelope_payload(
    *,
    path_id: str,
    model_id: str,
    checkpoint: int,
    source_state_digest: str,
) -> dict[str, object]:
    return {
        "path_id": path_id,
        "model_id": model_id,
        "checkpoint": checkpoint,
        "probe_branch_id": f"w7ac.{path_id}.{model_id}.probe.{checkpoint}",
        "source_state_digest": source_state_digest,
        "returns_to_main": False,
    }


@dataclass(frozen=True, slots=True)
class W7ACObserverProbeEnvelope:
    """Same-path observer copy kept outside W7-T path branching."""

    path_id: str
    model_id: str
    checkpoint: int
    source_state_digest: str
    copied_state: W7TObserverContinuationState = field(repr=False)
    envelope_digest: str

    def __post_init__(self) -> None:
        if (
            self.path_id not in _PATH_IDS
            or self.model_id not in _MODEL_IDS
            or self.checkpoint not in range(5)
            or not self.source_state_digest
            or not isinstance(self.copied_state, W7TObserverContinuationState)
            or self.copied_state.source_path_id != self.path_id
            or self.copied_state.model_id != self.model_id
            or self.copied_state.state_digest != self.source_state_digest
        ):
            raise W7ACObserverSevenPathConsumerError(
                "observer probe envelope binding is invalid"
            )
        expected = _digest(
            _envelope_payload(
                path_id=self.path_id,
                model_id=self.model_id,
                checkpoint=self.checkpoint,
                source_state_digest=self.source_state_digest,
            )
        )
        if self.envelope_digest != expected:
            raise W7ACObserverSevenPathConsumerError(
                "observer probe envelope digest differs"
            )


def _checkpoint_payload(
    *,
    p0_checkpoint_digest: str,
    path_id: str,
    model_id: str,
    checkpoint: int,
    main_state_digest: str,
    passive_checkpoint_state_digest: str,
    envelope_digest: str,
    probe_driver_digest: str,
    probe_continuation_digest: str,
) -> dict[str, object]:
    return {
        "p0_checkpoint_digest": p0_checkpoint_digest,
        "path_id": path_id,
        "model_id": model_id,
        "checkpoint": checkpoint,
        "main_state_digest": main_state_digest,
        "passive_checkpoint_state_digest": passive_checkpoint_state_digest,
        "envelope_digest": envelope_digest,
        "probe_driver_digest": probe_driver_digest,
        "probe_continuation_digest": probe_continuation_digest,
        "probe_returns_to_main": False,
    }


@dataclass(frozen=True, slots=True)
class W7ACObserverCheckpointResult:
    """One passive observer checkpoint and completed isolated probe."""

    p0_checkpoint_digest: str
    path_id: str
    model_id: str
    checkpoint: int
    main_state: W7TObserverContinuationState = field(repr=False)
    passive_checkpoint: W7TObserverCheckpoint
    probe_envelope: W7ACObserverProbeEnvelope
    probe_driver: W7PObserverDriver = field(repr=False)
    probe_continuation: W7TObserverContinuationResult = field(repr=False)
    checkpoint_result_digest: str

    def __post_init__(self) -> None:
        if (
            not self.p0_checkpoint_digest
            or self.path_id not in _PATH_IDS
            or self.model_id not in _MODEL_IDS
            or self.checkpoint not in range(5)
            or not isinstance(self.main_state, W7TObserverContinuationState)
            or not isinstance(self.passive_checkpoint, W7TObserverCheckpoint)
            or not isinstance(self.probe_envelope, W7ACObserverProbeEnvelope)
            or not isinstance(self.probe_driver, W7PObserverDriver)
            or not isinstance(
                self.probe_continuation,
                W7TObserverContinuationResult,
            )
        ):
            raise W7ACObserverSevenPathConsumerError(
                "observer checkpoint result inventory is invalid"
            )
        if (
            self.main_state.source_path_id != self.path_id
            or self.main_state.model_id != self.model_id
            or self.passive_checkpoint.source_path_id != self.path_id
            or self.passive_checkpoint.model_id != self.model_id
            or self.passive_checkpoint.checkpoint != self.checkpoint
            or self.passive_checkpoint.state_digest != self.main_state.state_digest
            or self.probe_envelope.source_state_digest
            != self.main_state.state_digest
            or self.probe_envelope.copied_state is self.main_state
            or self.probe_envelope.copied_state.baseline_state
            is self.main_state.baseline_state
            or self.probe_continuation.previous_state
            is not self.probe_envelope.copied_state
            or self.probe_continuation.driver_digest
            != self.probe_driver.driver_digest
            or self.probe_continuation.next_state is self.main_state
        ):
            raise W7ACObserverSevenPathConsumerError(
                "observer checkpoint crossed main and probe roles"
            )
        expected = _digest(
            _checkpoint_payload(
                p0_checkpoint_digest=self.p0_checkpoint_digest,
                path_id=self.path_id,
                model_id=self.model_id,
                checkpoint=self.checkpoint,
                main_state_digest=self.main_state.state_digest,
                passive_checkpoint_state_digest=(
                    self.passive_checkpoint.state_digest
                ),
                envelope_digest=self.probe_envelope.envelope_digest,
                probe_driver_digest=self.probe_driver.driver_digest,
                probe_continuation_digest=(
                    self.probe_continuation.continuation_digest
                ),
            )
        )
        if self.checkpoint_result_digest != expected:
            raise W7ACObserverSevenPathConsumerError(
                "observer checkpoint result digest differs"
            )


def _model_path_payload(
    *,
    p0_path_digest: str,
    path_id: str,
    model_id: str,
    initial_state_digest: str,
    main_driver_digests: tuple[str, ...],
    main_continuation_digests: tuple[str, ...],
    checkpoint_result_digests: tuple[str, ...],
    terminal_state_digest: str,
) -> dict[str, object]:
    return {
        "p0_path_digest": p0_path_digest,
        "path_id": path_id,
        "model_id": model_id,
        "initial_state_digest": initial_state_digest,
        "main_driver_digests": main_driver_digests,
        "main_continuation_digests": main_continuation_digests,
        "checkpoint_result_digests": checkpoint_result_digests,
        "terminal_state_digest": terminal_state_digest,
    }


@dataclass(frozen=True, slots=True)
class W7ACObserverModelPathResult:
    """One model-specific main chain and five observer probes."""

    p0_path_digest: str
    path_id: str
    model_id: str
    initial_state: W7TObserverContinuationState = field(repr=False)
    main_drivers: tuple[W7PObserverDriver, ...] = field(repr=False)
    main_continuations: tuple[W7TObserverContinuationResult, ...] = field(
        repr=False
    )
    checkpoints: tuple[W7ACObserverCheckpointResult, ...] = field(repr=False)
    terminal_state: W7TObserverContinuationState = field(repr=False)
    observer_path_consumption_digest: str

    def __post_init__(self) -> None:
        drivers = tuple(self.main_drivers)
        continuations = tuple(self.main_continuations)
        checkpoints = tuple(self.checkpoints)
        expected_count = 4 if self.path_id.startswith("u") else 5
        if (
            not self.p0_path_digest
            or self.path_id not in _PATH_IDS
            or self.model_id not in _MODEL_IDS
            or not isinstance(self.initial_state, W7TObserverContinuationState)
            or len(drivers) != expected_count
            or len(continuations) != expected_count
            or len(checkpoints) != 5
            or not isinstance(self.terminal_state, W7TObserverContinuationState)
        ):
            raise W7ACObserverSevenPathConsumerError(
                "observer model path inventory is invalid"
            )
        previous = self.initial_state
        for driver, continuation in zip(drivers, continuations, strict=True):
            if (
                continuation.previous_state is not previous
                or continuation.driver_digest != driver.driver_digest
                or continuation.next_state.model_id != self.model_id
                or continuation.next_state.source_path_id != self.path_id
            ):
                raise W7ACObserverSevenPathConsumerError(
                    "observer main chain is not contiguous"
                )
            previous = continuation.next_state
        if previous is not self.terminal_state or previous.end_tick != 8_000_000:
            raise W7ACObserverSevenPathConsumerError(
                "observer main chain does not end at tick eight"
            )
        checkpoint_states = (
            (
                (continuations[0].next_state,)
                + tuple(item.next_state for item in continuations[1:])
            )
            if expected_count == 5
            else (
                (self.initial_state,)
                + tuple(item.next_state for item in continuations)
            )
        )
        if tuple(item.main_state for item in checkpoints) != checkpoint_states:
            raise W7ACObserverSevenPathConsumerError(
                "observer checkpoints do not bind main states"
            )
        payload = _model_path_payload(
            p0_path_digest=self.p0_path_digest,
            path_id=self.path_id,
            model_id=self.model_id,
            initial_state_digest=self.initial_state.state_digest,
            main_driver_digests=tuple(item.driver_digest for item in drivers),
            main_continuation_digests=tuple(
                item.continuation_digest for item in continuations
            ),
            checkpoint_result_digests=tuple(
                item.checkpoint_result_digest for item in checkpoints
            ),
            terminal_state_digest=self.terminal_state.state_digest,
        )
        if self.observer_path_consumption_digest != _digest(payload):
            raise W7ACObserverSevenPathConsumerError(
                "observer path consumption digest differs"
            )
        object.__setattr__(self, "main_drivers", drivers)
        object.__setattr__(self, "main_continuations", continuations)
        object.__setattr__(self, "checkpoints", checkpoints)


def _countercontrol_payload(
    model_order_digests: tuple[str, ...],
    main_continuation_digest: str,
    probe_continuation_digest: str,
    p0_consumption_digest: str,
) -> dict[str, object]:
    return {
        "model_order_digests": model_order_digests,
        "main_continuation_digest": main_continuation_digest,
        "probe_continuation_digest": probe_continuation_digest,
        "p0_consumption_digest": p0_consumption_digest,
        "checkpoint_passive": True,
        "orders_match": True,
    }


@dataclass(frozen=True, slots=True)
class W7ACObserverCountercontrols:
    model_order_digests: tuple[str, ...]
    main_continuation_digest: str
    probe_continuation_digest: str
    p0_consumption_digest: str
    countercontrol_digest: str

    def __post_init__(self) -> None:
        models = tuple(self.model_order_digests)
        if (
            len(models) != 3
            or any(not item for item in models)
            or not self.main_continuation_digest
            or not self.probe_continuation_digest
            or not self.p0_consumption_digest
        ):
            raise W7ACObserverSevenPathConsumerError(
                "observer countercontrol binding is invalid"
            )
        expected = _digest(
            _countercontrol_payload(
                models,
                self.main_continuation_digest,
                self.probe_continuation_digest,
                self.p0_consumption_digest,
            )
        )
        if self.countercontrol_digest != expected:
            raise W7ACObserverSevenPathConsumerError(
                "observer countercontrol digest differs"
            )
        object.__setattr__(self, "model_order_digests", models)


def _result_payload(
    *,
    p0_consumption_digest: str,
    model_path_results: tuple[W7ACObserverModelPathResult, ...],
    countercontrol_digest: str,
) -> dict[str, object]:
    return {
        "consumer_id": _CONSUMER_ID,
        "p0_consumption_digest": p0_consumption_digest,
        "model_path_consumption_digests": tuple(
            item.observer_path_consumption_digest for item in model_path_results
        ),
        "countercontrol_digest": countercontrol_digest,
    }


@dataclass(frozen=True, slots=True)
class W7ACObserverSevenPathResult:
    """Complete external observer result without path comparison."""

    consumer_id: str
    p0_consumption_digest: str
    model_path_results: tuple[W7ACObserverModelPathResult, ...] = field(
        repr=False
    )
    countercontrols: W7ACObserverCountercontrols
    observer_seven_path_consumption_digest: str

    def __post_init__(self) -> None:
        results = tuple(self.model_path_results)
        expected_roles = tuple(
            (path_id, model_id)
            for path_id in _PATH_IDS
            for model_id in _MODEL_IDS
        )
        if (
            self.consumer_id != _CONSUMER_ID
            or not self.p0_consumption_digest
            or tuple((item.path_id, item.model_id) for item in results)
            != expected_roles
            or not isinstance(self.countercontrols, W7ACObserverCountercontrols)
            or self.countercontrols.p0_consumption_digest
            != self.p0_consumption_digest
        ):
            raise W7ACObserverSevenPathConsumerError(
                "observer seven-path result binding is invalid"
            )
        for offset in range(0, len(results), 3):
            group = results[offset : offset + 3]
            if len(
                {
                    tuple(driver.driver_digest for driver in item.main_drivers)
                    for item in group
                }
            ) != 1:
                raise W7ACObserverSevenPathConsumerError(
                    "observer models received different main driver sequences"
                )
        expected = _digest(
            _result_payload(
                p0_consumption_digest=self.p0_consumption_digest,
                model_path_results=results,
                countercontrol_digest=self.countercontrols.countercontrol_digest,
            )
        )
        if self.observer_seven_path_consumption_digest != expected:
            raise W7ACObserverSevenPathConsumerError(
                "observer seven-path consumption digest differs"
            )
        object.__setattr__(self, "model_path_results", results)


def _probe_envelope(
    state: W7TObserverContinuationState,
    checkpoint: int,
) -> W7ACObserverProbeEnvelope:
    clone = _clone_observer_state(state)
    payload = _envelope_payload(
        path_id=state.source_path_id,
        model_id=state.model_id,
        checkpoint=checkpoint,
        source_state_digest=state.state_digest,
    )
    return W7ACObserverProbeEnvelope(
        state.source_path_id,
        state.model_id,
        checkpoint,
        state.state_digest,
        clone,
        _digest(payload),
    )


def _observer_checkpoint(
    adapter: W7MCapacityFunctionMatrixAdapter,
    p0_checkpoint: W7AAP0CheckpointResult,
    checkpoint: int,
    main_state: W7TObserverContinuationState,
    probe_driver: W7PObserverDriver,
) -> W7ACObserverCheckpointResult:
    before = main_state.state_digest
    passive = checkpoint_w7t_observer_state(main_state, checkpoint)
    envelope = _probe_envelope(main_state, checkpoint)
    probe = advance_w7t_observer_continuation(
        adapter,
        envelope.copied_state,
        p0_checkpoint.probe_production,
        probe_driver,
    )
    if main_state.state_digest != before:
        raise W7ACObserverSevenPathConsumerError(
            "observer checkpoint or probe mutated the main state"
        )
    values = {
        "p0_checkpoint_digest": p0_checkpoint.checkpoint_result_digest,
        "path_id": main_state.source_path_id,
        "model_id": main_state.model_id,
        "checkpoint": checkpoint,
        "main_state": main_state,
        "passive_checkpoint": passive,
        "probe_envelope": envelope,
        "probe_driver": probe_driver,
        "probe_continuation": probe,
    }
    payload = _checkpoint_payload(
        p0_checkpoint_digest=p0_checkpoint.checkpoint_result_digest,
        path_id=main_state.source_path_id,
        model_id=main_state.model_id,
        checkpoint=checkpoint,
        main_state_digest=main_state.state_digest,
        passive_checkpoint_state_digest=passive.state_digest,
        envelope_digest=envelope.envelope_digest,
        probe_driver_digest=probe_driver.driver_digest,
        probe_continuation_digest=probe.continuation_digest,
    )
    return W7ACObserverCheckpointResult(
        **values,
        checkpoint_result_digest=_digest(payload),
    )


def _consume_model_path(
    adapter: W7MCapacityFunctionMatrixAdapter,
    p0_path: W7AAP0PathResult,
    main_drivers: tuple[W7PObserverDriver, ...],
    probe_drivers: tuple[W7PObserverDriver, ...],
    model_id: str,
) -> W7ACObserverModelPathResult:
    start_tick = 4_000_000 if p0_path.path_id.startswith("u") else 0
    initial = build_initial_w7t_observer_state(
        adapter,
        p0_path.path_id,
        model_id,
        start_tick,
    )
    current = initial
    continuations = []
    if not p0_path.path_id.startswith("u"):
        prefix = advance_w7t_observer_continuation(
            adapter,
            current,
            p0_path.main_productions[0],
            main_drivers[0],
        )
        continuations.append(prefix)
        current = prefix.next_state
        continuation_offset = 1
    else:
        continuation_offset = 0
    checkpoints = []
    for checkpoint in range(5):
        checkpoints.append(
            _observer_checkpoint(
                adapter,
                p0_path.checkpoints[checkpoint],
                checkpoint,
                current,
                probe_drivers[checkpoint],
            )
        )
        if checkpoint < 4:
            index = checkpoint + continuation_offset
            continuation = advance_w7t_observer_continuation(
                adapter,
                current,
                p0_path.main_productions[index],
                main_drivers[index],
            )
            continuations.append(continuation)
            current = continuation.next_state
    continuations_out = tuple(continuations)
    checkpoints_out = tuple(checkpoints)
    payload = _model_path_payload(
        p0_path_digest=p0_path.p0_path_consumption_digest,
        path_id=p0_path.path_id,
        model_id=model_id,
        initial_state_digest=initial.state_digest,
        main_driver_digests=tuple(item.driver_digest for item in main_drivers),
        main_continuation_digests=tuple(
            item.continuation_digest for item in continuations_out
        ),
        checkpoint_result_digests=tuple(
            item.checkpoint_result_digest for item in checkpoints_out
        ),
        terminal_state_digest=current.state_digest,
    )
    return W7ACObserverModelPathResult(
        p0_path.p0_path_consumption_digest,
        p0_path.path_id,
        model_id,
        initial,
        main_drivers,
        continuations_out,
        checkpoints_out,
        current,
        _digest(payload),
    )


def _drivers(
    adapter: W7MCapacityFunctionMatrixAdapter,
    authorization: W7WSourceAuthorization,
    p0_path: W7AAP0PathResult,
) -> tuple[tuple[W7PObserverDriver, ...], tuple[W7PObserverDriver, ...]]:
    main = tuple(
        compose_w7r_observer_driver(
            adapter,
            production,
            source_authorization=authorization,
        )
        for production in p0_path.main_productions
    )
    probes = tuple(
        compose_w7r_observer_driver(
            adapter,
            checkpoint.probe_production,
            source_authorization=authorization,
        )
        for checkpoint in p0_path.checkpoints
    )
    return main, probes


def _countercontrols(
    adapter: W7MCapacityFunctionMatrixAdapter,
    p0_result: W7AAP0SevenPathResult,
    ab_main_drivers: tuple[W7PObserverDriver, ...],
    ab_probe_drivers: tuple[W7PObserverDriver, ...],
    ab_results: tuple[W7ACObserverModelPathResult, ...],
) -> W7ACObserverCountercontrols:
    reverse = tuple(
        _consume_model_path(
            adapter,
            p0_result.path_results[0],
            ab_main_drivers,
            ab_probe_drivers,
            model_id,
        )
        for model_id in reversed(_MODEL_IDS)
    )
    actual = {item.model_id: item for item in ab_results}
    if any(
        actual[item.model_id].observer_path_consumption_digest
        != item.observer_path_consumption_digest
        for item in reverse
    ):
        raise W7ACObserverSevenPathConsumerError(
            "observer model execution order changed a result"
        )
    leak = actual["leak"]
    checkpoint = leak.checkpoints[0]
    main_state = checkpoint.main_state
    main_index = 1
    main_first = advance_w7t_observer_continuation(
        adapter,
        _clone_observer_state(main_state),
        p0_result.path_results[0].main_productions[main_index],
        ab_main_drivers[main_index],
    )
    probe_after_main = advance_w7t_observer_continuation(
        adapter,
        _clone_observer_state(main_state),
        p0_result.path_results[0].checkpoints[0].probe_production,
        ab_probe_drivers[0],
    )
    probe_first = advance_w7t_observer_continuation(
        adapter,
        _clone_observer_state(main_state),
        p0_result.path_results[0].checkpoints[0].probe_production,
        ab_probe_drivers[0],
    )
    main_after_probe = advance_w7t_observer_continuation(
        adapter,
        _clone_observer_state(main_state),
        p0_result.path_results[0].main_productions[main_index],
        ab_main_drivers[main_index],
    )
    if (
        main_first.continuation_digest != main_after_probe.continuation_digest
        or probe_first.continuation_digest
        != probe_after_main.continuation_digest
        or main_first.continuation_digest
        != leak.main_continuations[main_index].continuation_digest
        or probe_first.continuation_digest
        != checkpoint.probe_continuation.continuation_digest
    ):
        raise W7ACObserverSevenPathConsumerError(
            "observer main/probe order changed a branch result"
        )
    model_digests = tuple(
        actual[model_id].observer_path_consumption_digest
        for model_id in _MODEL_IDS
    )
    payload = _countercontrol_payload(
        model_digests,
        main_first.continuation_digest,
        probe_first.continuation_digest,
        p0_result.p0_seven_path_consumption_digest,
    )
    return W7ACObserverCountercontrols(
        model_digests,
        main_first.continuation_digest,
        probe_first.continuation_digest,
        p0_result.p0_seven_path_consumption_digest,
        _digest(payload),
    )


def consume_w7ac_observer_seven_path_result(
    adapter: W7MCapacityFunctionMatrixAdapter,
    authorization: W7WSourceAuthorization,
    plan: W7YSevenPathSourcePlan,
    p0_result: W7AAP0SevenPathResult,
) -> W7ACObserverSevenPathResult:
    """Observe W7-AA productions without modifying or comparing P0 paths."""

    if (
        not isinstance(adapter, W7MCapacityFunctionMatrixAdapter)
        or not isinstance(authorization, W7WSourceAuthorization)
        or not isinstance(plan, W7YSevenPathSourcePlan)
        or not isinstance(p0_result, W7AAP0SevenPathResult)
    ):
        raise W7ACObserverSevenPathConsumerError(
            "observer consumption requires complete W7-M/W/Y/AA bindings"
        )
    if (
        authorization.matrix_digest != adapter.matrix_digest
        or plan.matrix_digest != adapter.matrix_digest
        or plan.authorization_digest != authorization.authorization_digest
        or p0_result.plan_digest != plan.seven_path_plan_digest
    ):
        raise W7ACObserverSevenPathConsumerError(
            "observer consumption input digests differ"
        )
    p0_digest = p0_result.p0_seven_path_consumption_digest
    results = []
    driver_sets = []
    for p0_path in p0_result.path_results:
        main_drivers, probe_drivers = _drivers(
            adapter,
            authorization,
            p0_path,
        )
        driver_sets.append((main_drivers, probe_drivers))
        results.extend(
            _consume_model_path(
                adapter,
                p0_path,
                main_drivers,
                probe_drivers,
                model_id,
            )
            for model_id in _MODEL_IDS
        )
    results_out = tuple(results)
    countercontrols = _countercontrols(
        adapter,
        p0_result,
        driver_sets[0][0],
        driver_sets[0][1],
        results_out[:3],
    )
    if p0_result.p0_seven_path_consumption_digest != p0_digest:
        raise W7ACObserverSevenPathConsumerError(
            "observer consumption mutated the W7-AA result"
        )
    payload = _result_payload(
        p0_consumption_digest=p0_digest,
        model_path_results=results_out,
        countercontrol_digest=countercontrols.countercontrol_digest,
    )
    return W7ACObserverSevenPathResult(
        _CONSUMER_ID,
        p0_digest,
        results_out,
        countercontrols,
        _digest(payload),
    )
