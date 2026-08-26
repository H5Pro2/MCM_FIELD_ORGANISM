"""Isolated in-memory P0-only consumer for the frozen W7-Y source plan."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
import hashlib
import json

from .w7m_capacity_function_matrix import W7MCapacityFunctionMatrixAdapter
from .w7r_p0_s_completion_producer import (
    W7RP0SProductionResult,
    W7RP0State,
    build_initial_w7r_p0_state,
    produce_w7r_p0_s_completion_states,
)
from .w7w_symmetric_source_family import (
    W7WSourceAuthorization,
    W7WSymmetricSourceFamily,
)
from .w7y_seven_path_source_plan import (
    W7YCheckpointPlan,
    W7YPathPlan,
    W7YSevenPathSourcePlan,
    W7YSourceSegmentRef,
    build_w7y_seven_path_source_plan,
)


class W7AAP0SevenPathConsumerError(ValueError):
    """Raised when P0 plan consumption leaves the W7-Z contract."""


_CONSUMER_ID = "w7aa.p0-seven-path-consumer.v1"
_PATH_IDS = ("ab", "ag", "ba", "bg", "ua", "ub", "ug")


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _clone_p0_state(state: W7RP0State) -> W7RP0State:
    if not isinstance(state, W7RP0State):
        raise W7AAP0SevenPathConsumerError(
            "P0 checkpoint copy requires one W7-R state"
        )
    cloned_field = copy.deepcopy(state.p0_field)
    clone = W7RP0State(
        state.matrix_digest,
        state.source_path_id,
        state.clock_id,
        state.end_tick,
        state.neuron_ids,
        state.s_values,
        state.h_values,
        state.state_digest,
        cloned_field,
    )
    if (
        clone is state
        or clone.p0_field is state.p0_field
        or clone.state_digest != state.state_digest
        or clone.p0_field.layer is state.p0_field.layer
        or clone.p0_field.docks is state.p0_field.docks
        or (
            state.p0_field.last_distribution is not None
            and clone.p0_field.last_distribution
            is state.p0_field.last_distribution
        )
    ):
        raise W7AAP0SevenPathConsumerError(
            "P0 checkpoint copy is not structurally independent"
        )
    return clone


def _produce(
    adapter: W7MCapacityFunctionMatrixAdapter,
    authorization: W7WSourceAuthorization,
    segment: W7YSourceSegmentRef,
    state: W7RP0State,
) -> W7RP0SProductionResult:
    before = state.state_digest
    production = produce_w7r_p0_s_completion_states(
        adapter,
        segment.source_digest,
        segment.sequences,
        segment.interval,
        state,
        source_authorization=authorization,
    )
    if state.state_digest != before:
        raise W7AAP0SevenPathConsumerError(
            "P0 segment consumption mutated its initial state"
        )
    return production


def _checkpoint_payload(
    *,
    plan_checkpoint_digest: str,
    path_id: str,
    checkpoint: int,
    tick: int,
    main_predecessor_digest: str,
    main_state_digest: str,
    probe_initial_state_digest: str,
    probe_segment_digest: str,
    probe_production_digest: str,
    probe_end_state_digest: str,
) -> dict[str, object]:
    return {
        "plan_checkpoint_digest": plan_checkpoint_digest,
        "path_id": path_id,
        "checkpoint": checkpoint,
        "tick": tick,
        "main_predecessor_digest": main_predecessor_digest,
        "main_state_digest": main_state_digest,
        "probe_initial_state_digest": probe_initial_state_digest,
        "probe_segment_digest": probe_segment_digest,
        "probe_production_digest": probe_production_digest,
        "probe_end_state_digest": probe_end_state_digest,
        "probe_returns_to_main": False,
    }


@dataclass(frozen=True, slots=True)
class W7AAP0CheckpointResult:
    """One P0 checkpoint with an isolated completed probe branch."""

    plan_checkpoint_digest: str
    path_id: str
    checkpoint: int
    tick: int
    main_predecessor_digest: str
    main_state: W7RP0State = field(repr=False)
    probe_initial_state: W7RP0State = field(repr=False)
    probe_segment_digest: str = ""
    probe_production: W7RP0SProductionResult = field(repr=False, default=None)
    checkpoint_result_digest: str = ""

    def __post_init__(self) -> None:
        if (
            not self.plan_checkpoint_digest
            or self.path_id not in _PATH_IDS
            or self.checkpoint not in range(5)
            or self.tick != (self.checkpoint + 4) * 1_000_000
            or not self.main_predecessor_digest
            or not self.probe_segment_digest
        ):
            raise W7AAP0SevenPathConsumerError(
                "P0 checkpoint result binding is invalid"
            )
        if (
            not isinstance(self.main_state, W7RP0State)
            or not isinstance(self.probe_initial_state, W7RP0State)
            or not isinstance(self.probe_production, W7RP0SProductionResult)
        ):
            raise W7AAP0SevenPathConsumerError(
                "P0 checkpoint requires complete state and production objects"
            )
        if (
            self.main_state.source_path_id != self.path_id
            or self.probe_initial_state.source_path_id != self.path_id
            or self.main_state.end_tick != self.tick
            or self.probe_initial_state.end_tick != self.tick
            or self.main_state.state_digest
            != self.probe_initial_state.state_digest
            or self.main_state is self.probe_initial_state
            or self.main_state.p0_field is self.probe_initial_state.p0_field
        ):
            raise W7AAP0SevenPathConsumerError(
                "P0 probe did not start from an independent checkpoint copy"
            )
        if (
            self.probe_production.initial_state is not self.probe_initial_state
            or self.probe_production.source_path_id != self.path_id
            or self.probe_production.interval
            != (self.tick, self.tick + 1_000_000)
            or self.probe_production.end_state is self.main_state
        ):
            raise W7AAP0SevenPathConsumerError(
                "P0 probe production crossed checkpoint roles"
            )
        expected = _digest(
            _checkpoint_payload(
                plan_checkpoint_digest=self.plan_checkpoint_digest,
                path_id=self.path_id,
                checkpoint=self.checkpoint,
                tick=self.tick,
                main_predecessor_digest=self.main_predecessor_digest,
                main_state_digest=self.main_state.state_digest,
                probe_initial_state_digest=self.probe_initial_state.state_digest,
                probe_segment_digest=self.probe_segment_digest,
                probe_production_digest=self.probe_production.production_digest,
                probe_end_state_digest=(
                    self.probe_production.end_state.state_digest
                ),
            )
        )
        if self.checkpoint_result_digest != expected:
            raise W7AAP0SevenPathConsumerError(
                "P0 checkpoint result digest does not match its content"
            )


def _path_payload(
    *,
    path_plan_digest: str,
    path_id: str,
    initial_state_digest: str,
    main_production_digests: tuple[str, ...],
    checkpoint_result_digests: tuple[str, ...],
    probe_production_digests: tuple[str, ...],
    probe_end_state_digests: tuple[str, ...],
    terminal_main_state_digest: str,
) -> dict[str, object]:
    return {
        "path_plan_digest": path_plan_digest,
        "path_id": path_id,
        "initial_state_digest": initial_state_digest,
        "main_production_digests": main_production_digests,
        "checkpoint_result_digests": checkpoint_result_digests,
        "probe_production_digests": probe_production_digests,
        "probe_end_state_digests": probe_end_state_digests,
        "terminal_main_state_digest": terminal_main_state_digest,
    }


@dataclass(frozen=True, slots=True)
class W7AAP0PathResult:
    """One complete P0 main chain and its five isolated probes."""

    path_plan_digest: str
    path_id: str
    initial_state: W7RP0State = field(repr=False)
    main_productions: tuple[W7RP0SProductionResult, ...] = field(repr=False)
    checkpoints: tuple[W7AAP0CheckpointResult, ...] = field(repr=False)
    terminal_main_state: W7RP0State = field(repr=False)
    p0_path_consumption_digest: str

    def __post_init__(self) -> None:
        productions = tuple(self.main_productions)
        checkpoints = tuple(self.checkpoints)
        expected_count = 4 if self.path_id.startswith("u") else 5
        if (
            not self.path_plan_digest
            or self.path_id not in _PATH_IDS
            or not isinstance(self.initial_state, W7RP0State)
            or len(productions) != expected_count
            or len(checkpoints) != 5
            or not isinstance(self.terminal_main_state, W7RP0State)
        ):
            raise W7AAP0SevenPathConsumerError("P0 path result inventory is invalid")
        previous = self.initial_state
        for production in productions:
            if (
                production.source_path_id != self.path_id
                or production.initial_state is not previous
            ):
                raise W7AAP0SevenPathConsumerError(
                    "P0 main production chain is not contiguous"
                )
            previous = production.end_state
        if previous is not self.terminal_main_state or previous.end_tick != 8_000_000:
            raise W7AAP0SevenPathConsumerError(
                "P0 terminal main state is not the path endpoint"
            )
        expected_checkpoint_states = (
            (
                (productions[0].end_state,)
                + tuple(item.end_state for item in productions[1:])
            )
            if expected_count == 5
            else ((self.initial_state,) + tuple(item.end_state for item in productions))
        )
        if tuple(item.main_state for item in checkpoints) != expected_checkpoint_states:
            raise W7AAP0SevenPathConsumerError(
                "P0 checkpoints do not bind the main path states"
            )
        payload = _path_payload(
            path_plan_digest=self.path_plan_digest,
            path_id=self.path_id,
            initial_state_digest=self.initial_state.state_digest,
            main_production_digests=tuple(
                item.production_digest for item in productions
            ),
            checkpoint_result_digests=tuple(
                item.checkpoint_result_digest for item in checkpoints
            ),
            probe_production_digests=tuple(
                item.probe_production.production_digest for item in checkpoints
            ),
            probe_end_state_digests=tuple(
                item.probe_production.end_state.state_digest for item in checkpoints
            ),
            terminal_main_state_digest=self.terminal_main_state.state_digest,
        )
        if self.p0_path_consumption_digest != _digest(payload):
            raise W7AAP0SevenPathConsumerError(
                "P0 path consumption digest does not match its content"
            )
        object.__setattr__(self, "main_productions", productions)
        object.__setattr__(self, "checkpoints", checkpoints)


def _countercontrol_payload(
    path_id: str,
    checkpoint: int,
    main_production_digest: str,
    probe_production_digest: str,
) -> dict[str, object]:
    return {
        "path_id": path_id,
        "checkpoint": checkpoint,
        "main_production_digest": main_production_digest,
        "probe_production_digest": probe_production_digest,
        "orders_match": True,
    }


@dataclass(frozen=True, slots=True)
class W7AAP0OrderCountercontrol:
    path_id: str
    checkpoint: int
    main_production_digest: str
    probe_production_digest: str
    countercontrol_digest: str

    def __post_init__(self) -> None:
        if self.path_id != "ab" or self.checkpoint != 0:
            raise W7AAP0SevenPathConsumerError(
                "P0 order countercontrol role changed"
            )
        expected = _digest(
            _countercontrol_payload(
                self.path_id,
                self.checkpoint,
                self.main_production_digest,
                self.probe_production_digest,
            )
        )
        if self.countercontrol_digest != expected:
            raise W7AAP0SevenPathConsumerError(
                "P0 order countercontrol digest differs"
            )


def _result_payload(
    *,
    plan_digest: str,
    path_results: tuple[W7AAP0PathResult, ...],
    countercontrol_digest: str,
) -> dict[str, object]:
    return {
        "consumer_id": _CONSUMER_ID,
        "plan_digest": plan_digest,
        "path_consumption_digests": tuple(
            item.p0_path_consumption_digest for item in path_results
        ),
        "countercontrol_digest": countercontrol_digest,
    }


@dataclass(frozen=True, slots=True)
class W7AAP0SevenPathResult:
    """Complete P0-only result without comparisons or interpretation."""

    consumer_id: str
    plan_digest: str
    path_results: tuple[W7AAP0PathResult, ...] = field(repr=False)
    order_countercontrol: W7AAP0OrderCountercontrol
    p0_seven_path_consumption_digest: str

    def __post_init__(self) -> None:
        paths = tuple(self.path_results)
        if (
            self.consumer_id != _CONSUMER_ID
            or not self.plan_digest
            or tuple(item.path_id for item in paths) != _PATH_IDS
            or not isinstance(
                self.order_countercontrol,
                W7AAP0OrderCountercontrol,
            )
        ):
            raise W7AAP0SevenPathConsumerError(
                "P0 seven-path result binding is invalid"
            )
        expected = _digest(
            _result_payload(
                plan_digest=self.plan_digest,
                path_results=paths,
                countercontrol_digest=(
                    self.order_countercontrol.countercontrol_digest
                ),
            )
        )
        if self.p0_seven_path_consumption_digest != expected:
            raise W7AAP0SevenPathConsumerError(
                "P0 seven-path consumption digest does not match its content"
            )
        object.__setattr__(self, "path_results", paths)


def _checkpoint_result(
    adapter: W7MCapacityFunctionMatrixAdapter,
    authorization: W7WSourceAuthorization,
    checkpoint_plan: W7YCheckpointPlan,
    main_state: W7RP0State,
    main_predecessor_digest: str,
) -> W7AAP0CheckpointResult:
    before = main_state.state_digest
    probe_initial = _clone_p0_state(main_state)
    probe_production = _produce(
        adapter,
        authorization,
        checkpoint_plan.probe,
        probe_initial,
    )
    if main_state.state_digest != before:
        raise W7AAP0SevenPathConsumerError(
            "P0 probe changed the main checkpoint state"
        )
    values = {
        "plan_checkpoint_digest": checkpoint_plan.checkpoint_digest,
        "path_id": checkpoint_plan.path_id,
        "checkpoint": checkpoint_plan.checkpoint,
        "tick": checkpoint_plan.tick,
        "main_predecessor_digest": main_predecessor_digest,
        "main_state": main_state,
        "probe_initial_state": probe_initial,
        "probe_segment_digest": checkpoint_plan.probe.segment_digest,
        "probe_production": probe_production,
    }
    digest = _digest(
        _checkpoint_payload(
            plan_checkpoint_digest=checkpoint_plan.checkpoint_digest,
            path_id=checkpoint_plan.path_id,
            checkpoint=checkpoint_plan.checkpoint,
            tick=checkpoint_plan.tick,
            main_predecessor_digest=main_predecessor_digest,
            main_state_digest=main_state.state_digest,
            probe_initial_state_digest=probe_initial.state_digest,
            probe_segment_digest=checkpoint_plan.probe.segment_digest,
            probe_production_digest=probe_production.production_digest,
            probe_end_state_digest=probe_production.end_state.state_digest,
        )
    )
    return W7AAP0CheckpointResult(
        **values,
        checkpoint_result_digest=digest,
    )


def _consume_path(
    adapter: W7MCapacityFunctionMatrixAdapter,
    authorization: W7WSourceAuthorization,
    path_plan: W7YPathPlan,
) -> W7AAP0PathResult:
    start_tick = 4_000_000 if path_plan.prefix is None else 0
    initial = build_initial_w7r_p0_state(
        adapter,
        path_plan.path_id,
        start_tick,
    )
    current = initial
    productions = []
    if path_plan.prefix is not None:
        prefix_production = _produce(
            adapter,
            authorization,
            path_plan.prefix,
            current,
        )
        productions.append(prefix_production)
        current = prefix_production.end_state
        predecessor_digest = prefix_production.production_digest
    else:
        predecessor_digest = path_plan.uniform_start.start_digest
    checkpoints = []
    for checkpoint_index, checkpoint_plan in enumerate(path_plan.checkpoints):
        checkpoint = _checkpoint_result(
            adapter,
            authorization,
            checkpoint_plan,
            current,
            predecessor_digest,
        )
        checkpoints.append(checkpoint)
        if checkpoint_index < 4:
            production = _produce(
                adapter,
                authorization,
                path_plan.continuations[checkpoint_index],
                current,
            )
            productions.append(production)
            current = production.end_state
            predecessor_digest = production.production_digest
    productions_out = tuple(productions)
    checkpoints_out = tuple(checkpoints)
    payload = _path_payload(
        path_plan_digest=path_plan.path_plan_digest,
        path_id=path_plan.path_id,
        initial_state_digest=initial.state_digest,
        main_production_digests=tuple(
            item.production_digest for item in productions_out
        ),
        checkpoint_result_digests=tuple(
            item.checkpoint_result_digest for item in checkpoints_out
        ),
        probe_production_digests=tuple(
            item.probe_production.production_digest for item in checkpoints_out
        ),
        probe_end_state_digests=tuple(
            item.probe_production.end_state.state_digest for item in checkpoints_out
        ),
        terminal_main_state_digest=current.state_digest,
    )
    return W7AAP0PathResult(
        path_plan.path_plan_digest,
        path_plan.path_id,
        initial,
        productions_out,
        checkpoints_out,
        current,
        _digest(payload),
    )


def _order_countercontrol(
    adapter: W7MCapacityFunctionMatrixAdapter,
    authorization: W7WSourceAuthorization,
    path_plan: W7YPathPlan,
    path_result: W7AAP0PathResult,
) -> W7AAP0OrderCountercontrol:
    checkpoint = path_result.checkpoints[0]
    main_segment = path_plan.continuations[0]
    probe_segment = path_plan.checkpoints[0].probe

    probe_first = _produce(
        adapter,
        authorization,
        probe_segment,
        _clone_p0_state(checkpoint.main_state),
    )
    main_after_probe = _produce(
        adapter,
        authorization,
        main_segment,
        _clone_p0_state(checkpoint.main_state),
    )
    main_first = _produce(
        adapter,
        authorization,
        main_segment,
        _clone_p0_state(checkpoint.main_state),
    )
    probe_after_main = _produce(
        adapter,
        authorization,
        probe_segment,
        _clone_p0_state(checkpoint.main_state),
    )
    if (
        main_after_probe.production_digest != main_first.production_digest
        or probe_first.production_digest != probe_after_main.production_digest
        or main_first.production_digest
        != path_result.main_productions[1].production_digest
        or probe_first.production_digest
        != checkpoint.probe_production.production_digest
    ):
        raise W7AAP0SevenPathConsumerError(
            "P0 main/probe execution order changed a branch result"
        )
    payload = _countercontrol_payload(
        "ab",
        0,
        main_first.production_digest,
        probe_first.production_digest,
    )
    return W7AAP0OrderCountercontrol(
        "ab",
        0,
        main_first.production_digest,
        probe_first.production_digest,
        _digest(payload),
    )


def consume_w7aa_p0_seven_path_plan(
    adapter: W7MCapacityFunctionMatrixAdapter,
    family: W7WSymmetricSourceFamily,
    authorization: W7WSourceAuthorization,
    plan: W7YSevenPathSourcePlan,
) -> W7AAP0SevenPathResult:
    """Consume all W7-Y paths only through isolated W7-R P0 states."""

    if (
        not isinstance(adapter, W7MCapacityFunctionMatrixAdapter)
        or not isinstance(family, W7WSymmetricSourceFamily)
        or not isinstance(authorization, W7WSourceAuthorization)
        or not isinstance(plan, W7YSevenPathSourcePlan)
    ):
        raise W7AAP0SevenPathConsumerError(
            "P0 plan consumption requires complete W7-M/W/Y bindings"
        )
    expected_plan = build_w7y_seven_path_source_plan(
        adapter,
        family,
        authorization,
    )
    if (
        plan.seven_path_plan_digest != expected_plan.seven_path_plan_digest
        or plan.paths != expected_plan.paths
    ):
        raise W7AAP0SevenPathConsumerError(
            "P0 consumer received a different W7-Y plan"
        )
    paths = tuple(
        _consume_path(adapter, authorization, path_plan)
        for path_plan in plan.paths
    )
    countercontrol = _order_countercontrol(
        adapter,
        authorization,
        plan.paths[0],
        paths[0],
    )
    payload = _result_payload(
        plan_digest=plan.seven_path_plan_digest,
        path_results=paths,
        countercontrol_digest=countercontrol.countercontrol_digest,
    )
    return W7AAP0SevenPathResult(
        _CONSUMER_ID,
        plan.seven_path_plan_digest,
        paths,
        countercontrol,
        _digest(payload),
    )
