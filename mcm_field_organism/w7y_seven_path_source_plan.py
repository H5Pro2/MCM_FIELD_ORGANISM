"""Non-executing seven-path W7 source, checkpoint, and probe plan."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json

from .mcm_f3_controlled_history_source import (
    mcm_f3_receptor_sequences_digest,
)
from .receptor_time_model import ReceptorTimeSequence
from .w7m_capacity_function_matrix import W7MCapacityFunctionMatrixAdapter
from .w7w_symmetric_source_family import (
    W7WSourceAuthorization,
    W7WSymmetricSourceFamily,
    W7WSymmetricSourceFamilyError,
    authorize_w7w_source_segment,
    w7w_base_source_inventory_digest,
)


class W7YSevenPathSourcePlanError(ValueError):
    """Raised when the non-executing W7-Y plan leaves W7-X."""


_PLAN_ID = "w7y.seven-path-source-plan.v1"
_CLOCK_ID = "organism.mcm_f3_k2b"
_TICKS_PER_SECOND = 1_000_000.0
_PATH_IDS = ("ab", "ag", "ba", "bg", "ua", "ub", "ug")
_PREFIX_POLICY_ID = "w7x.independent-path-chains.v1"
_PROBE_COPY_POLICY_ID = "w7x.full-state-copy-per-probe.v1"
_B_AUTH_ROLE = "w7v.contact-b-prefix.combined.v1"
_A_AUTH_ROLE = "w7v.contact-a-continuation.steps.v1"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _segment_payload(
    *,
    segment_id: str,
    path_id: str,
    branch_kind: str,
    source_role: str,
    source_digest: str,
    interval: tuple[int, int],
    authorization_role_id: str | None,
) -> dict[str, object]:
    return {
        "segment_id": segment_id,
        "path_id": path_id,
        "branch_kind": branch_kind,
        "source_role": source_role,
        "source_digest": source_digest,
        "interval": interval,
        "authorization_role_id": authorization_role_id,
    }


@dataclass(frozen=True, slots=True)
class W7YSourceSegmentRef:
    """One digest-verified source reference without source processing."""

    segment_id: str
    path_id: str
    branch_kind: str
    source_role: str
    source_digest: str
    interval: tuple[int, int]
    authorization_role_id: str | None
    segment_digest: str
    sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence] = field(
        repr=False
    )

    def __post_init__(self) -> None:
        if (
            not self.segment_id
            or self.path_id not in _PATH_IDS
            or self.branch_kind not in {"main", "probe"}
            or not self.source_role
            or not self.source_digest
        ):
            raise W7YSevenPathSourcePlanError("source segment identity is invalid")
        start, end = self.interval
        if (
            isinstance(start, bool)
            or isinstance(end, bool)
            or not isinstance(start, int)
            or not isinstance(end, int)
            or end <= start
        ):
            raise W7YSevenPathSourcePlanError("source segment interval is invalid")
        sequences = tuple(self.sequences)
        if len(sequences) != 2 or len({item.modality_id for item in sequences}) != 2:
            raise W7YSevenPathSourcePlanError(
                "source segment requires two unique modalities"
            )
        if mcm_f3_receptor_sequences_digest(sequences) != self.source_digest:
            raise W7YSevenPathSourcePlanError(
                "source segment sequences differ from their digest"
            )
        observed_interval = (
            min(
                item.field_time.window_start_tick
                for sequence in sequences
                for item in sequence.frames
            ),
            max(
                item.field_time.window_end_tick
                for sequence in sequences
                for item in sequence.frames
            ),
        )
        if observed_interval != self.interval:
            raise W7YSevenPathSourcePlanError(
                "source segment sequences differ from their plan interval"
            )
        if self.source_role.startswith("additive."):
            if not self.authorization_role_id:
                raise W7YSevenPathSourcePlanError(
                    "additive segment requires one authorization role"
                )
        elif self.authorization_role_id is not None:
            raise W7YSevenPathSourcePlanError(
                "existing segment cannot carry additive authorization"
            )
        expected = _digest(
            _segment_payload(
                segment_id=self.segment_id,
                path_id=self.path_id,
                branch_kind=self.branch_kind,
                source_role=self.source_role,
                source_digest=self.source_digest,
                interval=self.interval,
                authorization_role_id=self.authorization_role_id,
            )
        )
        if self.segment_digest != expected:
            raise W7YSevenPathSourcePlanError(
                "source segment digest does not match its content"
            )
        object.__setattr__(self, "sequences", sequences)


def _uniform_payload(
    start_id: str,
    path_id: str,
    tick: int,
    matrix_digest: str,
) -> dict[str, object]:
    return {
        "start_id": start_id,
        "path_id": path_id,
        "tick": tick,
        "matrix_digest": matrix_digest,
        "has_source_sequence": False,
    }


@dataclass(frozen=True, slots=True)
class W7YUniformStartRef:
    """One source-free reference to the registered initial state at tick 4."""

    start_id: str
    path_id: str
    tick: int
    matrix_digest: str
    start_digest: str

    def __post_init__(self) -> None:
        if (
            not self.start_id
            or self.path_id not in {"ua", "ub", "ug"}
            or self.tick != 4_000_000
            or not self.matrix_digest
        ):
            raise W7YSevenPathSourcePlanError("uniform start binding is invalid")
        expected = _digest(
            _uniform_payload(
                self.start_id,
                self.path_id,
                self.tick,
                self.matrix_digest,
            )
        )
        if self.start_digest != expected:
            raise W7YSevenPathSourcePlanError(
                "uniform start digest does not match its content"
            )


def _checkpoint_payload(
    *,
    checkpoint_id: str,
    path_id: str,
    checkpoint: int,
    tick: int,
    main_predecessor_id: str,
    probe_segment_digest: str,
) -> dict[str, object]:
    return {
        "checkpoint_id": checkpoint_id,
        "path_id": path_id,
        "checkpoint": checkpoint,
        "tick": tick,
        "main_predecessor_id": main_predecessor_id,
        "probe_segment_digest": probe_segment_digest,
        "probe_copy_policy_id": _PROBE_COPY_POLICY_ID,
        "probe_returns_to_main": False,
    }


@dataclass(frozen=True, slots=True)
class W7YCheckpointPlan:
    """One passive checkpoint and its isolated probe reference."""

    checkpoint_id: str
    path_id: str
    checkpoint: int
    tick: int
    main_predecessor_id: str
    probe: W7YSourceSegmentRef
    checkpoint_digest: str

    def __post_init__(self) -> None:
        if (
            not self.checkpoint_id
            or self.path_id not in _PATH_IDS
            or self.checkpoint not in range(5)
            or self.tick != (self.checkpoint + 4) * 1_000_000
            or not self.main_predecessor_id
        ):
            raise W7YSevenPathSourcePlanError("checkpoint binding is invalid")
        if (
            not isinstance(self.probe, W7YSourceSegmentRef)
            or self.probe.path_id != self.path_id
            or self.probe.branch_kind != "probe"
            or self.probe.interval != (self.tick, self.tick + 1_000_000)
            or self.probe.source_role != f"existing.probe.{self.checkpoint}"
        ):
            raise W7YSevenPathSourcePlanError("checkpoint probe binding is invalid")
        expected = _digest(
            _checkpoint_payload(
                checkpoint_id=self.checkpoint_id,
                path_id=self.path_id,
                checkpoint=self.checkpoint,
                tick=self.tick,
                main_predecessor_id=self.main_predecessor_id,
                probe_segment_digest=self.probe.segment_digest,
            )
        )
        if self.checkpoint_digest != expected:
            raise W7YSevenPathSourcePlanError(
                "checkpoint digest does not match its content"
            )


def _path_payload(
    path_id: str,
    prefix: W7YSourceSegmentRef | None,
    uniform_start: W7YUniformStartRef | None,
    continuations: tuple[W7YSourceSegmentRef, ...],
    checkpoints: tuple[W7YCheckpointPlan, ...],
) -> dict[str, object]:
    return {
        "path_id": path_id,
        "prefix_policy_id": _PREFIX_POLICY_ID,
        "prefix_segment_digest": (
            None if prefix is None else prefix.segment_digest
        ),
        "uniform_start_digest": (
            None if uniform_start is None else uniform_start.start_digest
        ),
        "continuation_segment_digests": tuple(
            item.segment_digest for item in continuations
        ),
        "checkpoint_digests": tuple(
            item.checkpoint_digest for item in checkpoints
        ),
    }


def _expected_roles(path_id: str) -> tuple[str | None, str]:
    return {
        "ab": ("existing.a.combined", "existing.b.step"),
        "ag": ("existing.a.combined", "existing.g.step"),
        "ba": ("additive.b.combined", "additive.a.step"),
        "bg": ("additive.b.combined", "existing.g.step"),
        "ua": (None, "additive.a.step"),
        "ub": (None, "existing.b.step"),
        "ug": (None, "existing.g.step"),
    }[path_id]


@dataclass(frozen=True, slots=True)
class W7YPathPlan:
    """One complete source-only path plan with no state continuation."""

    path_id: str
    prefix: W7YSourceSegmentRef | None
    uniform_start: W7YUniformStartRef | None
    continuations: tuple[W7YSourceSegmentRef, ...]
    checkpoints: tuple[W7YCheckpointPlan, ...]
    path_plan_digest: str

    def __post_init__(self) -> None:
        if self.path_id not in _PATH_IDS:
            raise W7YSevenPathSourcePlanError("unknown seven-path plan")
        expected_prefix_role, continuation_role = _expected_roles(self.path_id)
        if expected_prefix_role is None:
            if self.prefix is not None or not isinstance(
                self.uniform_start, W7YUniformStartRef
            ):
                raise W7YSevenPathSourcePlanError(
                    "uniform path must have one source-free start"
                )
            if self.uniform_start.path_id != self.path_id:
                raise W7YSevenPathSourcePlanError(
                    "uniform start belongs to another path"
                )
            predecessor = self.uniform_start.start_id
        else:
            if self.uniform_start is not None or not isinstance(
                self.prefix, W7YSourceSegmentRef
            ):
                raise W7YSevenPathSourcePlanError(
                    "contact path must have exactly one prefix"
                )
            if (
                self.prefix.path_id != self.path_id
                or self.prefix.branch_kind != "main"
                or self.prefix.source_role != expected_prefix_role
                or self.prefix.interval != (0, 4_000_000)
                or (
                    expected_prefix_role == "additive.b.combined"
                    and self.prefix.authorization_role_id != _B_AUTH_ROLE
                )
            ):
                raise W7YSevenPathSourcePlanError("path prefix binding is invalid")
            predecessor = self.prefix.segment_id
        continuations = tuple(self.continuations)
        checkpoints = tuple(self.checkpoints)
        if len(continuations) != 4 or len(checkpoints) != 5:
            raise W7YSevenPathSourcePlanError(
                "path requires four continuations and five checkpoints"
            )
        for index, segment in enumerate(continuations):
            if (
                segment.path_id != self.path_id
                or segment.branch_kind != "main"
                or segment.source_role != f"{continuation_role}.{index}"
                or segment.interval
                != ((index + 4) * 1_000_000, (index + 5) * 1_000_000)
                or (
                    continuation_role == "additive.a.step"
                    and segment.authorization_role_id
                    != f"{_A_AUTH_ROLE}.{index}"
                )
            ):
                raise W7YSevenPathSourcePlanError(
                    "path continuation binding is invalid"
                )
        for index, checkpoint in enumerate(checkpoints):
            expected_predecessor = (
                predecessor if index == 0 else continuations[index - 1].segment_id
            )
            if (
                checkpoint.path_id != self.path_id
                or checkpoint.checkpoint != index
                or checkpoint.main_predecessor_id != expected_predecessor
            ):
                raise W7YSevenPathSourcePlanError(
                    "path checkpoint order is invalid"
                )
        expected = _digest(
            _path_payload(
                self.path_id,
                self.prefix,
                self.uniform_start,
                continuations,
                checkpoints,
            )
        )
        if self.path_plan_digest != expected:
            raise W7YSevenPathSourcePlanError(
                "path plan digest does not match its content"
            )
        object.__setattr__(self, "continuations", continuations)
        object.__setattr__(self, "checkpoints", checkpoints)


def _adapter_payload(
    *,
    matrix_digest: str,
    region_digest: str,
    base_source_inventory_digest: str,
    symmetric_inventory_digest: str,
    authorization_digest: str,
    paths: tuple[W7YPathPlan, ...],
) -> dict[str, object]:
    return {
        "plan_id": _PLAN_ID,
        "matrix_digest": matrix_digest,
        "region_digest": region_digest,
        "base_source_inventory_digest": base_source_inventory_digest,
        "symmetric_inventory_digest": symmetric_inventory_digest,
        "authorization_digest": authorization_digest,
        "clock_id": _CLOCK_ID,
        "ticks_per_second": _TICKS_PER_SECOND,
        "prefix_policy_id": _PREFIX_POLICY_ID,
        "probe_copy_policy_id": _PROBE_COPY_POLICY_ID,
        "path_plan_digests": tuple(item.path_plan_digest for item in paths),
    }


@dataclass(frozen=True, slots=True)
class W7YSevenPathSourcePlan:
    """Complete immutable W7-Y metadata plan without execution methods."""

    plan_id: str
    matrix_digest: str
    region_digest: str
    base_source_inventory_digest: str
    symmetric_inventory_digest: str
    authorization_digest: str
    clock_id: str
    ticks_per_second: float
    paths: tuple[W7YPathPlan, ...]
    seven_path_plan_digest: str

    def __post_init__(self) -> None:
        paths = tuple(self.paths)
        if (
            self.plan_id != _PLAN_ID
            or not self.matrix_digest
            or not self.region_digest
            or not self.base_source_inventory_digest
            or not self.symmetric_inventory_digest
            or not self.authorization_digest
            or self.clock_id != _CLOCK_ID
            or self.ticks_per_second != _TICKS_PER_SECOND
            or tuple(item.path_id for item in paths) != _PATH_IDS
        ):
            raise W7YSevenPathSourcePlanError("seven-path adapter binding is invalid")
        expected = _digest(
            _adapter_payload(
                matrix_digest=self.matrix_digest,
                region_digest=self.region_digest,
                base_source_inventory_digest=self.base_source_inventory_digest,
                symmetric_inventory_digest=self.symmetric_inventory_digest,
                authorization_digest=self.authorization_digest,
                paths=paths,
            )
        )
        if self.seven_path_plan_digest != expected:
            raise W7YSevenPathSourcePlanError(
                "seven-path plan digest does not match its content"
            )
        object.__setattr__(self, "paths", paths)


def _segment(
    *,
    adapter: W7MCapacityFunctionMatrixAdapter,
    authorization: W7WSourceAuthorization,
    segment_id: str,
    path_id: str,
    branch_kind: str,
    source_role: str,
    source_digest: str,
    interval: tuple[int, int],
    sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence],
    authorization_role_id: str | None = None,
) -> W7YSourceSegmentRef:
    if authorization_role_id is not None:
        try:
            authorize_w7w_source_segment(
                adapter,
                authorization,
                source_digest,
                path_id,
                interval,
            )
        except W7WSymmetricSourceFamilyError as exc:
            raise W7YSevenPathSourcePlanError(str(exc)) from exc
        roles = tuple(
            item
            for item in authorization.roles
            if item.source_digest == source_digest
        )
        if len(roles) != 1 or roles[0].role_id != authorization_role_id:
            raise W7YSevenPathSourcePlanError(
                "additive segment authorization role differs"
            )
    payload = _segment_payload(
        segment_id=segment_id,
        path_id=path_id,
        branch_kind=branch_kind,
        source_role=source_role,
        source_digest=source_digest,
        interval=interval,
        authorization_role_id=authorization_role_id,
    )
    return W7YSourceSegmentRef(
        segment_id,
        path_id,
        branch_kind,
        source_role,
        source_digest,
        interval,
        authorization_role_id,
        _digest(payload),
        sequences,
    )


def _uniform_start(
    adapter: W7MCapacityFunctionMatrixAdapter,
    path_id: str,
) -> W7YUniformStartRef:
    start_id = f"w7y.{path_id}.uniform-start"
    payload = _uniform_payload(start_id, path_id, 4_000_000, adapter.matrix_digest)
    return W7YUniformStartRef(
        start_id,
        path_id,
        4_000_000,
        adapter.matrix_digest,
        _digest(payload),
    )


def _main_sources(adapter, family, path_id):
    source = adapter.source
    if path_id in {"ab", "ag"}:
        prefix = (
            "existing.a.combined",
            source.contact_a_digest,
            source.contact_a,
            None,
        )
    elif path_id in {"ba", "bg"}:
        prefix = (
            "additive.b.combined",
            family.b_prefix_digest,
            family.b_prefix,
            _B_AUTH_ROLE,
        )
    else:
        prefix = None
    if path_id in {"ab", "ub"}:
        continuation = tuple(
            (
                f"existing.b.step.{index}",
                source.contact_b_step_digests[index],
                source.contact_b_steps[index],
                None,
            )
            for index in range(4)
        )
    elif path_id in {"ag", "bg", "ug"}:
        continuation = tuple(
            (
                f"existing.g.step.{index}",
                source.interruption_step_digests[index],
                source.interruption_steps[index],
                None,
            )
            for index in range(4)
        )
    else:
        continuation = tuple(
            (
                f"additive.a.step.{index}",
                family.a_continuation_step_digests[index],
                family.a_continuation_steps[index],
                f"{_A_AUTH_ROLE}.{index}",
            )
            for index in range(4)
        )
    return prefix, continuation


def build_w7y_seven_path_source_plan(
    adapter: W7MCapacityFunctionMatrixAdapter,
    family: W7WSymmetricSourceFamily,
    authorization: W7WSourceAuthorization,
) -> W7YSevenPathSourcePlan:
    """Build the complete source metadata plan without advancing any state."""

    if (
        not isinstance(adapter, W7MCapacityFunctionMatrixAdapter)
        or not isinstance(family, W7WSymmetricSourceFamily)
        or not isinstance(authorization, W7WSourceAuthorization)
    ):
        raise W7YSevenPathSourcePlanError(
            "W7-Y requires one adapter, source family, and authorization"
        )
    if (
        family.matrix_digest != adapter.matrix_digest
        or family.region_digest != adapter.regions.region_digest
        or family.base_source_inventory_digest
        != w7w_base_source_inventory_digest(adapter.source)
        or authorization.matrix_digest != adapter.matrix_digest
        or authorization.symmetric_inventory_digest
        != family.symmetric_inventory_digest
        or authorization.family.symmetric_inventory_digest
        != family.symmetric_inventory_digest
    ):
        raise W7YSevenPathSourcePlanError("W7-Y inventory bindings differ")
    path_plans = []
    for path_id in _PATH_IDS:
        prefix_source, continuation_sources = _main_sources(
            adapter,
            family,
            path_id,
        )
        prefix = None
        uniform_start = None
        if prefix_source is None:
            uniform_start = _uniform_start(adapter, path_id)
            predecessor = uniform_start.start_id
        else:
            role, digest, sequences, authorization_role = prefix_source
            prefix = _segment(
                adapter=adapter,
                authorization=authorization,
                segment_id=f"w7y.{path_id}.prefix",
                path_id=path_id,
                branch_kind="main",
                source_role=role,
                source_digest=digest,
                interval=(0, 4_000_000),
                sequences=sequences,
                authorization_role_id=authorization_role,
            )
            predecessor = prefix.segment_id
        continuations = tuple(
            _segment(
                adapter=adapter,
                authorization=authorization,
                segment_id=f"w7y.{path_id}.continuation.{index}",
                path_id=path_id,
                branch_kind="main",
                source_role=role,
                source_digest=digest,
                interval=(
                    (index + 4) * 1_000_000,
                    (index + 5) * 1_000_000,
                ),
                sequences=sequences,
                authorization_role_id=authorization_role,
            )
            for index, (role, digest, sequences, authorization_role) in enumerate(
                continuation_sources
            )
        )
        checkpoints = []
        for checkpoint in range(5):
            tick = (checkpoint + 4) * 1_000_000
            probe = _segment(
                adapter=adapter,
                authorization=authorization,
                segment_id=f"w7y.{path_id}.probe.{checkpoint}",
                path_id=path_id,
                branch_kind="probe",
                source_role=f"existing.probe.{checkpoint}",
                source_digest=adapter.source.probe_digests[checkpoint],
                interval=(tick, tick + 1_000_000),
                sequences=adapter.source.probes[checkpoint],
            )
            checkpoint_id = f"w7y.{path_id}.checkpoint.{checkpoint}"
            main_predecessor_id = (
                predecessor
                if checkpoint == 0
                else continuations[checkpoint - 1].segment_id
            )
            payload = _checkpoint_payload(
                checkpoint_id=checkpoint_id,
                path_id=path_id,
                checkpoint=checkpoint,
                tick=tick,
                main_predecessor_id=main_predecessor_id,
                probe_segment_digest=probe.segment_digest,
            )
            checkpoints.append(
                W7YCheckpointPlan(
                    checkpoint_id,
                    path_id,
                    checkpoint,
                    tick,
                    main_predecessor_id,
                    probe,
                    _digest(payload),
                )
            )
        checkpoints_out = tuple(checkpoints)
        path_payload = _path_payload(
            path_id,
            prefix,
            uniform_start,
            continuations,
            checkpoints_out,
        )
        path_plans.append(
            W7YPathPlan(
                path_id,
                prefix,
                uniform_start,
                continuations,
                checkpoints_out,
                _digest(path_payload),
            )
        )
    paths = tuple(path_plans)
    payload = _adapter_payload(
        matrix_digest=adapter.matrix_digest,
        region_digest=adapter.regions.region_digest,
        base_source_inventory_digest=family.base_source_inventory_digest,
        symmetric_inventory_digest=family.symmetric_inventory_digest,
        authorization_digest=authorization.authorization_digest,
        paths=paths,
    )
    return W7YSevenPathSourcePlan(
        _PLAN_ID,
        adapter.matrix_digest,
        adapter.regions.region_digest,
        family.base_source_inventory_digest,
        family.symmetric_inventory_digest,
        authorization.authorization_digest,
        _CLOCK_ID,
        _TICKS_PER_SECOND,
        paths,
        _digest(payload),
    )
