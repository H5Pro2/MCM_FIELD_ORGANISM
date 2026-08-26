"""Additive symmetric W7 source family without matrix or model execution."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math

from .controlled_audio_video_test_world import (
    controlled_history_holdout_world_family,
)
from .mcm_f3_controlled_history_source import (
    _combine_phase_sequences,
    mcm_f3_receptor_sequences_digest,
)
from .mcm_f3_k2b_source import MCMF3K2BSource, _phase_steps
from .receptor_time_model import ReceptorTimeSequence
from .w7m_capacity_function_matrix import W7MCapacityFunctionMatrixAdapter


class W7WSymmetricSourceFamilyError(ValueError):
    """Raised when the additive W7-W source contract is not exact."""


_FAMILY_ID = "w7v.symmetric-path-source-family.v1"
_B_PREFIX_STEPS_ID = "w7v.contact-b-prefix.steps.v1"
_B_PREFIX_ID = "w7v.contact-b-prefix.combined.v1"
_A_CONTINUATION_STEPS_ID = "w7v.contact-a-continuation.steps.v1"
_CLOCK_ID = "organism.mcm_f3_k2b"
_TICKS_PER_SECOND = 1_000_000.0
_STEP_COUNT = 4
_PATH_IDS = ("ab", "ag", "ba", "bg", "ua", "ub", "ug")


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def w7w_base_source_inventory_digest(source: MCMF3K2BSource) -> str:
    """Bind the complete existing K2-B source inventory without values."""

    if not isinstance(source, MCMF3K2BSource):
        raise W7WSymmetricSourceFamilyError(
            "base inventory requires one K2-B source"
        )
    return _digest(
        {
            "contact_a_digest": source.contact_a_digest,
            "contact_b_step_digests": source.contact_b_step_digests,
            "interruption_step_digests": source.interruption_step_digests,
            "probe_digests": source.probe_digests,
            "clock_id": source.clock_id,
            "ticks_per_second": source.ticks_per_second,
        }
    )


def _sequence_support(
    sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence],
    *,
    relative: bool,
) -> tuple[tuple[object, ...], ...]:
    ordered = tuple(sorted(tuple(sequences), key=lambda item: item.modality_id))
    if len(ordered) != 2 or len({item.modality_id for item in ordered}) != 2:
        raise W7WSymmetricSourceFamilyError(
            "source support requires two unique modalities"
        )
    origin = min(
        item.field_time.window_start_tick
        for sequence in ordered
        for item in sequence.frames
    )
    result = []
    for sequence in ordered:
        first = sequence.frames[0].frame
        carriers = tuple(first.carrier_ids)
        if any(tuple(item.frame.carrier_ids) != carriers for item in sequence.frames):
            raise W7WSymmetricSourceFamilyError(
                "source support carrier inventory changed within a sequence"
            )
        boundaries = tuple(
            (
                item.field_time.window_start_tick - (origin if relative else 0),
                item.field_time.window_end_tick - (origin if relative else 0),
            )
            for item in sequence.frames
        )
        result.append(
            (
                sequence.modality_id,
                sequence.geometry_id,
                sequence.clock_id,
                carriers,
                len(sequence.frames),
                boundaries,
            )
        )
    return tuple(result)


@dataclass(frozen=True, slots=True)
class W7WSymmetricPathSourceSpec:
    """One source-only path assignment; it does not execute the path."""

    path_id: str
    prefix_role: str
    prefix_digests: tuple[str, ...]
    continuation_role: str
    continuation_digests: tuple[str, ...]
    probe_digests: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.path_id not in _PATH_IDS:
            raise W7WSymmetricSourceFamilyError("unknown symmetric source path")
        for role in (self.prefix_role, self.continuation_role):
            if not role:
                raise W7WSymmetricSourceFamilyError("source path role is empty")
        for name in (
            "prefix_digests",
            "continuation_digests",
            "probe_digests",
        ):
            values = tuple(getattr(self, name))
            if any(not item for item in values):
                raise W7WSymmetricSourceFamilyError(
                    "source path contains an empty digest"
                )
            object.__setattr__(self, name, values)


def _path_specs(
    source: MCMF3K2BSource,
    b_prefix_digest: str,
    a_continuation_step_digests: tuple[str, ...],
) -> tuple[W7WSymmetricPathSourceSpec, ...]:
    probes = source.probe_digests
    values = (
        (
            "ab",
            "existing.a",
            (source.contact_a_digest,),
            "existing.b",
            source.contact_b_step_digests,
        ),
        (
            "ag",
            "existing.a",
            (source.contact_a_digest,),
            "existing.g",
            source.interruption_step_digests,
        ),
        (
            "ba",
            "additive.b",
            (b_prefix_digest,),
            "additive.a",
            a_continuation_step_digests,
        ),
        (
            "bg",
            "additive.b",
            (b_prefix_digest,),
            "existing.g",
            source.interruption_step_digests,
        ),
        ("ua", "uniform", (), "additive.a", a_continuation_step_digests),
        ("ub", "uniform", (), "existing.b", source.contact_b_step_digests),
        ("ug", "uniform", (), "existing.g", source.interruption_step_digests),
    )
    return tuple(
        W7WSymmetricPathSourceSpec(*item, probe_digests=probes) for item in values
    )


def _family_payload(
    *,
    matrix_digest: str,
    region_digest: str,
    base_source_inventory_digest: str,
    b_prefix_step_digests: tuple[str, ...],
    b_prefix_digest: str,
    a_continuation_step_digests: tuple[str, ...],
    prefix_support_matches: bool,
    continuation_support_matches: bool,
    paths: tuple[W7WSymmetricPathSourceSpec, ...],
) -> dict[str, object]:
    return {
        "family_id": _FAMILY_ID,
        "matrix_digest": matrix_digest,
        "region_digest": region_digest,
        "base_source_inventory_digest": base_source_inventory_digest,
        "source_roles": {
            "b_prefix_steps_id": _B_PREFIX_STEPS_ID,
            "b_prefix_id": _B_PREFIX_ID,
            "a_continuation_steps_id": _A_CONTINUATION_STEPS_ID,
        },
        "b_prefix_step_digests": b_prefix_step_digests,
        "b_prefix_digest": b_prefix_digest,
        "a_continuation_step_digests": a_continuation_step_digests,
        "clock_id": _CLOCK_ID,
        "ticks_per_second": _TICKS_PER_SECOND,
        "prefix_support_matches": prefix_support_matches,
        "continuation_support_matches": continuation_support_matches,
        "paths": [
            {
                "path_id": item.path_id,
                "prefix_role": item.prefix_role,
                "prefix_digests": item.prefix_digests,
                "continuation_role": item.continuation_role,
                "continuation_digests": item.continuation_digests,
                "probe_digests": item.probe_digests,
            }
            for item in paths
        ],
    }


@dataclass(frozen=True, slots=True)
class W7WSymmetricSourceFamily:
    """Fresh additive source material bound to the unchanged W7-M adapter."""

    family_id: str
    matrix_digest: str
    region_digest: str
    base_source_inventory_digest: str
    b_prefix_steps: tuple[tuple[ReceptorTimeSequence, ReceptorTimeSequence], ...]
    b_prefix_step_digests: tuple[str, ...]
    b_prefix: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    b_prefix_digest: str
    a_continuation_steps: tuple[
        tuple[ReceptorTimeSequence, ReceptorTimeSequence], ...
    ]
    a_continuation_step_digests: tuple[str, ...]
    clock_id: str
    ticks_per_second: float
    prefix_support_matches: bool
    continuation_support_matches: bool
    paths: tuple[W7WSymmetricPathSourceSpec, ...]
    symmetric_inventory_digest: str

    def __post_init__(self) -> None:
        if self.family_id != _FAMILY_ID:
            raise W7WSymmetricSourceFamilyError("symmetric family_id changed")
        if (
            not self.matrix_digest
            or not self.region_digest
            or not self.base_source_inventory_digest
        ):
            raise W7WSymmetricSourceFamilyError("symmetric bindings are empty")
        if self.clock_id != _CLOCK_ID or not math.isclose(
            self.ticks_per_second, _TICKS_PER_SECOND
        ):
            raise W7WSymmetricSourceFamilyError("symmetric source clock changed")
        b_steps = tuple(self.b_prefix_steps)
        a_steps = tuple(self.a_continuation_steps)
        b_digests = tuple(self.b_prefix_step_digests)
        a_digests = tuple(self.a_continuation_step_digests)
        paths = tuple(self.paths)
        if not (
            len(b_steps) == len(a_steps) == len(b_digests) == len(a_digests) == 4
        ):
            raise W7WSymmetricSourceFamilyError(
                "symmetric source family requires four steps per additive role"
            )
        if (
            tuple(mcm_f3_receptor_sequences_digest(item) for item in b_steps)
            != b_digests
        ):
            raise W7WSymmetricSourceFamilyError("B-prefix step digests differ")
        if mcm_f3_receptor_sequences_digest(self.b_prefix) != self.b_prefix_digest:
            raise W7WSymmetricSourceFamilyError("combined B-prefix digest differs")
        if (
            tuple(mcm_f3_receptor_sequences_digest(item) for item in a_steps)
            != a_digests
        ):
            raise W7WSymmetricSourceFamilyError("A-continuation step digests differ")
        if not self.prefix_support_matches or not self.continuation_support_matches:
            raise W7WSymmetricSourceFamilyError("symmetric technical support differs")
        if tuple(item.path_id for item in paths) != _PATH_IDS:
            raise W7WSymmetricSourceFamilyError("seven-path source inventory changed")
        expected = _digest(
            _family_payload(
                matrix_digest=self.matrix_digest,
                region_digest=self.region_digest,
                base_source_inventory_digest=self.base_source_inventory_digest,
                b_prefix_step_digests=b_digests,
                b_prefix_digest=self.b_prefix_digest,
                a_continuation_step_digests=a_digests,
                prefix_support_matches=self.prefix_support_matches,
                continuation_support_matches=self.continuation_support_matches,
                paths=paths,
            )
        )
        if self.symmetric_inventory_digest != expected:
            raise W7WSymmetricSourceFamilyError(
                "symmetric inventory digest does not match its content"
            )
        object.__setattr__(self, "b_prefix_steps", b_steps)
        object.__setattr__(self, "b_prefix_step_digests", b_digests)
        object.__setattr__(self, "a_continuation_steps", a_steps)
        object.__setattr__(self, "a_continuation_step_digests", a_digests)
        object.__setattr__(self, "paths", paths)


def build_w7w_symmetric_source_family(
    adapter: W7MCapacityFunctionMatrixAdapter,
) -> W7WSymmetricSourceFamily:
    """Reduce only the two additive roles and bind their technical support."""

    if not isinstance(adapter, W7MCapacityFunctionMatrixAdapter):
        raise W7WSymmetricSourceFamilyError(
            "symmetric family requires one frozen W7-M adapter"
        )
    same, changed = controlled_history_holdout_world_family()
    b_steps = _phase_steps(
        changed.phases[2],
        changed,
        world_id="w7v.contact-b-prefix",
        start_second=0,
        repetitions=_STEP_COUNT,
        snapshot_namespace="w7v.contact-b-prefix",
    )
    a_steps = _phase_steps(
        same.phases[0],
        same,
        world_id="w7v.contact-a-continuation",
        start_second=_STEP_COUNT,
        repetitions=_STEP_COUNT,
        snapshot_namespace="w7v.contact-a-continuation",
    )
    b_prefix = _combine_phase_sequences(b_steps)
    b_digests = tuple(mcm_f3_receptor_sequences_digest(item) for item in b_steps)
    a_digests = tuple(mcm_f3_receptor_sequences_digest(item) for item in a_steps)
    b_prefix_digest = mcm_f3_receptor_sequences_digest(b_prefix)
    prefix_support_matches = _sequence_support(
        adapter.source.contact_a, relative=False
    ) == _sequence_support(b_prefix, relative=False)
    continuation_support_matches = all(
        _sequence_support(existing, relative=True)
        == _sequence_support(additive, relative=True)
        for existing, additive in zip(
            adapter.source.contact_b_steps,
            a_steps,
            strict=True,
        )
    )
    existing_snapshot_ids = {
        item.frame.snapshot_id
        for sequence in adapter.source.contact_a
        for item in sequence.frames
    }
    additive_snapshot_ids = {
        item.frame.snapshot_id
        for sequence in b_prefix
        for item in sequence.frames
    }
    if existing_snapshot_ids & additive_snapshot_ids:
        raise W7WSymmetricSourceFamilyError(
            "A and B prefix snapshot identities must remain distinct"
        )
    base_digest = w7w_base_source_inventory_digest(adapter.source)
    paths = _path_specs(adapter.source, b_prefix_digest, a_digests)
    payload = _family_payload(
        matrix_digest=adapter.matrix_digest,
        region_digest=adapter.regions.region_digest,
        base_source_inventory_digest=base_digest,
        b_prefix_step_digests=b_digests,
        b_prefix_digest=b_prefix_digest,
        a_continuation_step_digests=a_digests,
        prefix_support_matches=prefix_support_matches,
        continuation_support_matches=continuation_support_matches,
        paths=paths,
    )
    return W7WSymmetricSourceFamily(
        _FAMILY_ID,
        adapter.matrix_digest,
        adapter.regions.region_digest,
        base_digest,
        b_steps,
        b_digests,
        b_prefix,
        b_prefix_digest,
        a_steps,
        a_digests,
        _CLOCK_ID,
        _TICKS_PER_SECOND,
        prefix_support_matches,
        continuation_support_matches,
        paths,
        _digest(payload),
    )


@dataclass(frozen=True, slots=True)
class W7WAuthorizedSourceRole:
    source_digest: str
    role_id: str
    allowed_path_ids: tuple[str, ...]
    interval: tuple[int, int]

    def __post_init__(self) -> None:
        paths = tuple(self.allowed_path_ids)
        if not self.source_digest or not self.role_id or not paths:
            raise W7WSymmetricSourceFamilyError("authorized source role is empty")
        if tuple(sorted(set(paths))) != paths or any(
            item not in _PATH_IDS for item in paths
        ):
            raise W7WSymmetricSourceFamilyError("authorized source paths are invalid")
        start, end = self.interval
        if (
            isinstance(start, bool)
            or isinstance(end, bool)
            or not isinstance(start, int)
            or not isinstance(end, int)
            or end <= start
        ):
            raise W7WSymmetricSourceFamilyError("authorized source interval is invalid")
        object.__setattr__(self, "allowed_path_ids", paths)


def _authorized_roles(
    family: W7WSymmetricSourceFamily,
) -> tuple[W7WAuthorizedSourceRole, ...]:
    roles = [
        W7WAuthorizedSourceRole(
            digest,
            f"{_B_PREFIX_STEPS_ID}.{index}",
            ("ba", "bg"),
            (index * 1_000_000, (index + 1) * 1_000_000),
        )
        for index, digest in enumerate(family.b_prefix_step_digests)
    ]
    roles.append(
        W7WAuthorizedSourceRole(
            family.b_prefix_digest,
            _B_PREFIX_ID,
            ("ba", "bg"),
            (0, 4_000_000),
        )
    )
    roles.extend(
        W7WAuthorizedSourceRole(
            digest,
            f"{_A_CONTINUATION_STEPS_ID}.{index}",
            ("ba", "ua"),
            ((index + 4) * 1_000_000, (index + 5) * 1_000_000),
        )
        for index, digest in enumerate(family.a_continuation_step_digests)
    )
    return tuple(roles)


@dataclass(frozen=True, slots=True)
class W7WSourceAuthorization:
    """Explicit additive authorization passed to W7-R when required."""

    matrix_digest: str
    base_source_inventory_digest: str
    symmetric_inventory_digest: str
    roles: tuple[W7WAuthorizedSourceRole, ...]
    authorization_digest: str
    family: W7WSymmetricSourceFamily

    def __post_init__(self) -> None:
        if not isinstance(self.family, W7WSymmetricSourceFamily):
            raise W7WSymmetricSourceFamilyError("authorization family is invalid")
        roles = tuple(self.roles)
        if (
            self.matrix_digest != self.family.matrix_digest
            or self.base_source_inventory_digest
            != self.family.base_source_inventory_digest
            or self.symmetric_inventory_digest
            != self.family.symmetric_inventory_digest
            or roles != _authorized_roles(self.family)
        ):
            raise W7WSymmetricSourceFamilyError("authorization bindings differ")
        expected = _digest(
            {
                "matrix_digest": self.matrix_digest,
                "base_source_inventory_digest": self.base_source_inventory_digest,
                "symmetric_inventory_digest": self.symmetric_inventory_digest,
                "roles": [
                    {
                        "source_digest": item.source_digest,
                        "role_id": item.role_id,
                        "allowed_path_ids": item.allowed_path_ids,
                        "interval": item.interval,
                    }
                    for item in roles
                ],
            }
        )
        if self.authorization_digest != expected:
            raise W7WSymmetricSourceFamilyError(
                "authorization digest does not match its content"
            )
        object.__setattr__(self, "roles", roles)


def build_w7w_source_authorization(
    adapter: W7MCapacityFunctionMatrixAdapter,
    family: W7WSymmetricSourceFamily,
) -> W7WSourceAuthorization:
    if not isinstance(adapter, W7MCapacityFunctionMatrixAdapter) or not isinstance(
        family, W7WSymmetricSourceFamily
    ):
        raise W7WSymmetricSourceFamilyError(
            "authorization requires one adapter and symmetric family"
        )
    if (
        family.matrix_digest != adapter.matrix_digest
        or family.region_digest != adapter.regions.region_digest
        or family.base_source_inventory_digest
        != w7w_base_source_inventory_digest(adapter.source)
    ):
        raise W7WSymmetricSourceFamilyError(
            "authorization family belongs to another W7-M inventory"
        )
    roles = _authorized_roles(family)
    payload = {
        "matrix_digest": adapter.matrix_digest,
        "base_source_inventory_digest": family.base_source_inventory_digest,
        "symmetric_inventory_digest": family.symmetric_inventory_digest,
        "roles": [
            {
                "source_digest": item.source_digest,
                "role_id": item.role_id,
                "allowed_path_ids": item.allowed_path_ids,
                "interval": item.interval,
            }
            for item in roles
        ],
    }
    return W7WSourceAuthorization(
        adapter.matrix_digest,
        family.base_source_inventory_digest,
        family.symmetric_inventory_digest,
        roles,
        _digest(payload),
        family,
    )


def authorize_w7w_source_segment(
    adapter: W7MCapacityFunctionMatrixAdapter,
    authorization: W7WSourceAuthorization,
    source_digest: str,
    path_id: str,
    interval: tuple[int, int],
) -> None:
    """Reject any additive source use outside its bound role."""

    if not isinstance(authorization, W7WSourceAuthorization):
        raise W7WSymmetricSourceFamilyError("additive source authorization is invalid")
    if (
        authorization.matrix_digest != adapter.matrix_digest
        or authorization.base_source_inventory_digest
        != w7w_base_source_inventory_digest(adapter.source)
    ):
        raise W7WSymmetricSourceFamilyError(
            "additive source authorization belongs to another matrix"
        )
    matches = tuple(
        item for item in authorization.roles if item.source_digest == source_digest
    )
    if len(matches) != 1:
        raise W7WSymmetricSourceFamilyError(
            "additive source digest has no unique authorized role"
        )
    role = matches[0]
    if path_id not in role.allowed_path_ids or tuple(interval) != role.interval:
        raise W7WSymmetricSourceFamilyError(
            "additive source path or interval differs from its authorized role"
        )
