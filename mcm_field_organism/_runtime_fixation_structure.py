"""Locked declarations for the runtime-value fixation preflight."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ._previous_state_minimal_runner import (
    PreviousStateMinimalRunnerError,
    _INPUT_A,
    _INPUT_B,
    _INPUT_C,
)


_CONTACT_IDS = tuple(
    contact.snapshot_id for contact in (*_INPUT_A, *_INPUT_B, *_INPUT_C)
)

_SOURCE_DIGESTS = (
    ("mcm_field_organism/receptor_contract.py", "af565ce442aa56ade4b3b5d028692cccc93b481c299f1ff2d87ba840fdb6ee71"),
    ("mcm_field_organism/receptor_distributor.py", "649bb3eb49e43f039fe525bdcbdfe5a0a1d06e67f25e5c88a10471fc546f1dad"),
    ("mcm_field_organism/shared_mcm_field.py", "2ddb013a049a13897af5e1e506a739410bf1579843799c4d6bf86d10e610a5ec"),
    ("mcm_field_organism/field_step_time.py", "2fba95b49768fcbfb01253ef20b7574a6f4df868fb51d0c0229791d0d523d3dd"),
    ("mcm_field_organism/neutral_local_field_substrate.py", "df5fb99d653963b83990315f5d3b70ff7feb00bd518a6a192a9fd06523bd4f13"),
    ("mcm_field_organism/mcm_neuron_layer.py", "ea699158096d35be62bfc308691325d4408ca491b5d456928509f52c1a554277"),
    ("mcm_field_organism/_previous_state_minimal_runner.py", "f25aa5e4f5affe9755ae5f011b029a2ad46aa5a6560532706b7db7a40d12ae72"),
    ("mcm_field_organism/previous_state_contribution_hook.py", "42f98fe9beab7f71900135524693fc7e3be898fdc16c1696057c95a0fad8a648"),
)

_STATIC_CONTRACT = (
    ("construction_digest", "1d1817784190c26d883c744b305634ee72cdabde84767bcc38aaee7c9f6a2b8e"),
    ("geometry_digest", "a9701d5524be56f21d1f8351e5c82f2e2d84d639cd08f231f09e7ea9e5391ecb"),
)

_ABORT_BOUNDARIES = (
    "static_or_source_digest_mismatch",
    "dissipation_not_none",
    "contact_contract_mismatch",
    "context_not_fresh",
    "geometry_or_construction_digest_mismatch",
    "distribution_count_mismatch",
    "generator_or_boundary_shape_invalid",
    "generator_or_boundary_nonfinite",
    "forbidden_runtime_role_requested",
    "double_derivation_mismatch",
    "partial_value_exposure",
    "incomplete_bundle_or_exception",
)

_FORBIDDEN_ROLES = (
    "effect_measurement",
    "field_advance",
    "hook_execution",
    "integration",
    "snapshot",
)

_ENTRY_KEYS = (
    "boundary_digest",
    "contact_id",
    "generator_digest",
    "receptor_distribution_digest",
)

_BUNDLE_KEYS = (
    "entries",
    "schema_version",
    "source_digests",
    "static_contract",
)

_OPERATION_ROLES = (
    "verify_bound_source_bytes",
    "build_fresh_context",
    "frame_for_contact",
    "distribution_for_frame",
    "distribution_digest",
    "step_time_for_frame",
    "generator_and_boundary",
    "generator_digest",
    "boundary_digest",
    "discard_context",
)


@dataclass(frozen=True, slots=True)
class _DigestSlots:
    contact_id: str
    receptor_distribution_digest: None = None
    generator_digest: None = None
    boundary_digest: None = None

    def __post_init__(self) -> None:
        if self.contact_id not in _CONTACT_IDS:
            raise PreviousStateMinimalRunnerError("unknown fixation contact")
        if any(
            value is not None
            for value in (
                self.receptor_distribution_digest,
                self.generator_digest,
                self.boundary_digest,
            )
        ):
            raise PreviousStateMinimalRunnerError("runtime digest slots must stay empty")


@dataclass(frozen=True, slots=True)
class _DerivationPass:
    pass_index: int
    context_tokens: tuple[object, ...]
    slots: tuple[_DigestSlots, ...]

    def __post_init__(self) -> None:
        if self.pass_index not in (1, 2):
            raise PreviousStateMinimalRunnerError("fixation requires passes one and two")
        if tuple(slot.contact_id for slot in self.slots) != _CONTACT_IDS:
            raise PreviousStateMinimalRunnerError("fixation contact order changed")
        if len(self.context_tokens) != 7 or len({id(item) for item in self.context_tokens}) != 7:
            raise PreviousStateMinimalRunnerError("every contact requires a fresh context")


@dataclass(frozen=True, slots=True)
class _BundleShape:
    schema_version: int
    top_level_keys: tuple[str, ...]
    entry_keys: tuple[str, ...]
    entry_count: int
    source_digest_count: int

    def __post_init__(self) -> None:
        if (
            self.schema_version != 1
            or self.top_level_keys != _BUNDLE_KEYS
            or self.entry_keys != _ENTRY_KEYS
            or self.entry_count != 7
            or self.source_digest_count != 8
        ):
            raise PreviousStateMinimalRunnerError("fixation bundle shape changed")


@dataclass(frozen=True, slots=True)
class _LockedFixationStructure:
    contact_ids: tuple[str, ...]
    source_digests: tuple[tuple[str, str], ...]
    static_contract: tuple[tuple[str, str], ...]
    passes: tuple[_DerivationPass, ...]
    bundle_shape: _BundleShape
    abort_boundaries: tuple[str, ...]
    forbidden_roles: tuple[str, ...]
    fixation_implementation_released: bool = False
    fixation_execution_released: bool = False
    executor_implementation_released: bool = False
    runner_execution_released: bool = False
    field_construction_released: bool = False
    receptor_distribution_released: bool = False
    integration_released: bool = False
    hook_execution_released: bool = False
    effect_evaluation_released: bool = False
    public_av_released: bool = False
    production_switch_released: bool = False
    dynamics_change_released: bool = False

    def __post_init__(self) -> None:
        if self.contact_ids != _CONTACT_IDS:
            raise PreviousStateMinimalRunnerError("fixation contacts changed")
        if self.source_digests != _SOURCE_DIGESTS:
            raise PreviousStateMinimalRunnerError("fixation source digests changed")
        if self.static_contract != _STATIC_CONTRACT:
            raise PreviousStateMinimalRunnerError("fixation static contract changed")
        if tuple(item.pass_index for item in self.passes) != (1, 2):
            raise PreviousStateMinimalRunnerError("double derivation changed")
        tokens = tuple(token for item in self.passes for token in item.context_tokens)
        if len(tokens) != 14 or len({id(token) for token in tokens}) != 14:
            raise PreviousStateMinimalRunnerError("all derivations require fresh contexts")
        if self.abort_boundaries != _ABORT_BOUNDARIES:
            raise PreviousStateMinimalRunnerError("fixation abort boundaries changed")
        if self.forbidden_roles != _FORBIDDEN_ROLES:
            raise PreviousStateMinimalRunnerError("forbidden fixation roles changed")
        release_flags = (
            self.fixation_implementation_released,
            self.fixation_execution_released,
            self.executor_implementation_released,
            self.runner_execution_released,
            self.field_construction_released,
            self.receptor_distribution_released,
            self.integration_released,
            self.hook_execution_released,
            self.effect_evaluation_released,
            self.public_av_released,
            self.production_switch_released,
            self.dynamics_change_released,
        )
        if any(release_flags):
            raise PreviousStateMinimalRunnerError("fixation structure must stay locked")


@dataclass(frozen=True, slots=True)
class _FixationOperations:
    verify_bound_source_bytes: Callable[[tuple[tuple[str, str], ...]], None]
    build_fresh_context: Callable[[str, int], object]
    frame_for_contact: Callable[[str], object]
    distribution_for_frame: Callable[[object, object], object]
    distribution_digest: Callable[[object], str]
    step_time_for_frame: Callable[[object], object]
    generator_and_boundary: Callable[[object, object, object], tuple[object, object]]
    generator_digest: Callable[[object], str]
    boundary_digest: Callable[[object], str]
    discard_context: Callable[[object], None]

    def __post_init__(self) -> None:
        values = (
            self.verify_bound_source_bytes,
            self.build_fresh_context,
            self.frame_for_contact,
            self.distribution_for_frame,
            self.distribution_digest,
            self.step_time_for_frame,
            self.generator_and_boundary,
            self.generator_digest,
            self.boundary_digest,
            self.discard_context,
        )
        if not all(callable(value) for value in values):
            raise PreviousStateMinimalRunnerError("fixation operations must be callable")


@dataclass(frozen=True, slots=True)
class _FixedDigestEntry:
    contact_id: str
    receptor_distribution_digest: str
    generator_digest: str
    boundary_digest: str

    def __post_init__(self) -> None:
        if self.contact_id not in _CONTACT_IDS:
            raise PreviousStateMinimalRunnerError("unknown fixation contact")
        if not all(
            _is_sha256(value)
            for value in (
                self.receptor_distribution_digest,
                self.generator_digest,
                self.boundary_digest,
            )
        ):
            raise PreviousStateMinimalRunnerError("invalid fixation digest")


@dataclass(frozen=True, slots=True)
class _FixedDigestBundle:
    entries: tuple[_FixedDigestEntry, ...]
    schema_version: int
    source_digests: tuple[tuple[str, str], ...]
    static_contract: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        if tuple(entry.contact_id for entry in self.entries) != _CONTACT_IDS:
            raise PreviousStateMinimalRunnerError("incomplete fixation bundle")
        if self.schema_version != 1:
            raise PreviousStateMinimalRunnerError("fixation bundle shape changed")
        if self.source_digests != _SOURCE_DIGESTS:
            raise PreviousStateMinimalRunnerError("fixation source digests changed")
        if self.static_contract != _STATIC_CONTRACT:
            raise PreviousStateMinimalRunnerError("fixation static contract changed")


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _derive_contact_with_operations(
    operations: _FixationOperations,
    contact_id: str,
    pass_index: int,
    context: object,
) -> _FixedDigestEntry:
    try:
        frame = operations.frame_for_contact(contact_id)
        distribution = operations.distribution_for_frame(context, frame)
        distribution_digest = operations.distribution_digest(distribution)
        step_time = operations.step_time_for_frame(frame)
        pair = operations.generator_and_boundary(context, distribution, step_time)
    except Exception:
        raise PreviousStateMinimalRunnerError(
            f"fixation operation failed for {contact_id} pass {pass_index}"
        ) from None

    if not isinstance(pair, tuple) or len(pair) != 2:
        raise PreviousStateMinimalRunnerError("generator boundary pair invalid")
    generator, boundary = pair
    try:
        generator_digest = operations.generator_digest(generator)
        boundary_digest = operations.boundary_digest(boundary)
    except Exception:
        raise PreviousStateMinimalRunnerError(
            f"fixation operation failed for {contact_id} pass {pass_index}"
        ) from None

    return _FixedDigestEntry(
        contact_id=contact_id,
        receptor_distribution_digest=distribution_digest,
        generator_digest=generator_digest,
        boundary_digest=boundary_digest,
    )


def _coordinate_runtime_fixation_with_operations(
    structure: _LockedFixationStructure,
    operations: _FixationOperations,
) -> _FixedDigestBundle:
    """Run only injected operations; this function has no real runtime binding."""

    if not isinstance(structure, _LockedFixationStructure):
        raise PreviousStateMinimalRunnerError("locked fixation structure is required")
    if not isinstance(operations, _FixationOperations):
        raise PreviousStateMinimalRunnerError("private fixation operations are required")

    try:
        operations.verify_bound_source_bytes(structure.source_digests)
    except Exception:
        raise PreviousStateMinimalRunnerError("bound source verification failed") from None

    seen_contexts: list[object] = []
    pass_entries: list[tuple[_FixedDigestEntry, ...]] = []
    for pass_index in (1, 2):
        current_entries: list[_FixedDigestEntry] = []
        for contact_id in structure.contact_ids:
            try:
                context = operations.build_fresh_context(contact_id, pass_index)
            except Exception:
                raise PreviousStateMinimalRunnerError(
                    f"context construction failed for {contact_id} pass {pass_index}"
                ) from None

            operation_error: PreviousStateMinimalRunnerError | None = None
            entry: _FixedDigestEntry | None = None
            if any(context is previous for previous in seen_contexts):
                operation_error = PreviousStateMinimalRunnerError(
                    f"fixation context reused for {contact_id} pass {pass_index}"
                )
            else:
                seen_contexts.append(context)
                try:
                    entry = _derive_contact_with_operations(
                        operations, contact_id, pass_index, context
                    )
                except PreviousStateMinimalRunnerError as exc:
                    operation_error = exc

            try:
                operations.discard_context(context)
            except Exception:
                raise PreviousStateMinimalRunnerError(
                    f"context discard failed for {contact_id} pass {pass_index}"
                ) from None

            if operation_error is not None:
                raise operation_error
            if entry is None:
                raise PreviousStateMinimalRunnerError("fixation entry was not formed")
            current_entries.append(entry)
        pass_entries.append(tuple(current_entries))

    if pass_entries[0] != pass_entries[1]:
        raise PreviousStateMinimalRunnerError("double derivation mismatch")

    return _FixedDigestBundle(
        entries=pass_entries[0],
        schema_version=1,
        source_digests=structure.source_digests,
        static_contract=structure.static_contract,
    )


def _derivation_pass(pass_index: int) -> _DerivationPass:
    return _DerivationPass(
        pass_index=pass_index,
        context_tokens=tuple(object() for _ in _CONTACT_IDS),
        slots=tuple(_DigestSlots(contact_id) for contact_id in _CONTACT_IDS),
    )


def build_locked_runtime_fixation_structure() -> _LockedFixationStructure:
    """Build declarations only; no runtime callable is accepted or invoked."""

    return _LockedFixationStructure(
        contact_ids=_CONTACT_IDS,
        source_digests=_SOURCE_DIGESTS,
        static_contract=_STATIC_CONTRACT,
        passes=(_derivation_pass(1), _derivation_pass(2)),
        bundle_shape=_BundleShape(1, _BUNDLE_KEYS, _ENTRY_KEYS, 7, 8),
        abort_boundaries=_ABORT_BOUNDARIES,
        forbidden_roles=_FORBIDDEN_ROLES,
    )


def execute_runtime_fixation(structure: _LockedFixationStructure) -> None:
    """Constructively retain the fixation execution lock."""

    if not isinstance(structure, _LockedFixationStructure):
        raise PreviousStateMinimalRunnerError("locked fixation structure is required")
    raise PreviousStateMinimalRunnerError("runtime fixation is not released")
