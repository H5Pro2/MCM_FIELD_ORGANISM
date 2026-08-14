"""Private adapters for a still-locked runtime fixation boundary."""

from __future__ import annotations

import hashlib
import hmac
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from ._previous_state_minimal_runner import (
    PreviousStateMinimalRunnerError,
    _INPUT_A,
    _INPUT_B,
    _INPUT_C,
)
from ._runtime_fixation_structure import _FixationOperations
from .field_step_time import MCMFieldStepTime
from .neutral_local_field_substrate import (
    NeutralLocalFieldSubstrateConfig,
    _generator_and_boundary,
)
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_distributor import (
    ReceptorDistribution,
    ReceptorDistributor,
    ReceptorDock,
)
from .shared_mcm_field import ReceptorDockAnatomy, build_shared_mcm_field


_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_CONTACTS = {
    contact.snapshot_id: contact
    for contact in (*_INPUT_A, *_INPUT_B, *_INPUT_C)
}
_CONTACT_IDS = tuple(_CONTACTS)


class _FixationRuntimeContext:
    __slots__ = (
        "_field",
        "_distributor",
        "_substrate_config",
        "contact_id",
        "pass_index",
        "owner_token",
        "_discarded",
    )

    def __init__(
        self,
        *,
        field: object,
        distributor: object,
        substrate_config: object,
        contact_id: str,
        pass_index: int,
    ) -> None:
        if contact_id not in _CONTACT_IDS or pass_index not in (1, 2):
            raise PreviousStateMinimalRunnerError("invalid fixation context identity")
        self._field = field
        self._distributor = distributor
        self._substrate_config = substrate_config
        self.contact_id = contact_id
        self.pass_index = pass_index
        self.owner_token = object()
        self._discarded = False

    @property
    def discarded(self) -> bool:
        return self._discarded

    def _require_active(self) -> None:
        if self.discarded:
            raise PreviousStateMinimalRunnerError("fixation context was discarded")

    @property
    def field(self) -> object:
        self._require_active()
        return self._field

    @property
    def distributor(self) -> object:
        self._require_active()
        return self._distributor

    @property
    def substrate_config(self) -> object:
        self._require_active()
        return self._substrate_config

    def __copy__(self) -> Any:
        raise PreviousStateMinimalRunnerError("fixation context cannot be copied")

    def __deepcopy__(self, memo: object) -> Any:
        raise PreviousStateMinimalRunnerError("fixation context cannot be copied")

    def __reduce__(self) -> Any:
        raise PreviousStateMinimalRunnerError("fixation context cannot be serialized")

    __hash__ = None


def _clean_failure(message: str) -> PreviousStateMinimalRunnerError:
    return PreviousStateMinimalRunnerError(message)


def _verify_bound_source_bytes(
    source_digests: tuple[tuple[str, str], ...],
) -> None:
    try:
        for relative_name, expected_digest in source_digests:
            relative = Path(relative_name)
            if (
                relative.is_absolute()
                or ".." in relative.parts
                or not isinstance(expected_digest, str)
                or len(expected_digest) != 64
            ):
                raise ValueError
            candidate = _PROJECT_ROOT / relative
            if candidate.is_symlink() or not candidate.is_file():
                raise ValueError
            resolved = candidate.resolve(strict=True)
            resolved.relative_to(_PROJECT_ROOT.resolve(strict=True))
            if resolved != candidate.absolute():
                raise ValueError
            actual_digest = hashlib.sha256(resolved.read_bytes()).hexdigest()
            if not hmac.compare_digest(actual_digest, expected_digest):
                raise ValueError
    except Exception:
        raise _clean_failure("bound source verification failed") from None


def _frame_for_contact(contact_id: str) -> ReceptorContactFrame:
    try:
        contact = _CONTACTS[contact_id]
        return ReceptorContactFrame(
            modality_id=contact.modality_id,
            geometry_id=contact.geometry_id,
            snapshot_id=contact.snapshot_id,
            clock_id=contact.clock_id,
            window_start_tick=contact.window_start_tick,
            window_end_tick=contact.window_end_tick,
            carrier_ids=contact.carrier_ids,
            values=contact.values,
        )
    except Exception:
        raise _clean_failure("fixation frame construction failed") from None


def _build_fresh_context(
    contact_id: str,
    pass_index: int,
) -> _FixationRuntimeContext:
    if contact_id not in _CONTACT_IDS or pass_index not in (1, 2):
        raise _clean_failure("invalid fixation context identity")
    field = distributor = substrate_config = None
    try:
        reference_frame = _frame_for_contact(_INPUT_C[0].snapshot_id)
        anatomy = ReceptorDockAnatomy(
            modality_id="synthetic",
            dock_id="dock.synthetic",
            positions=((0,), (1,), (2,)),
        )
        field = build_shared_mcm_field(
            reference_frames=(reference_frame,),
            anatomies={"synthetic": anatomy},
            sample_offsets=((-1,), (1,)),
            field_id="organism.mcm_field",
            layer_id="organism.mcm_layer",
            geometry_id="organism.shared.v1",
        )
        distributor = ReceptorDistributor()
        distributor.attach(
            ReceptorDock(
                dock_id="dock.synthetic",
                modality_id="synthetic",
                receptor_geometry_id="synthetic.line3.v1",
            )
        )
        substrate_config = NeutralLocalFieldSubstrateConfig(1.0)
        return _FixationRuntimeContext(
            field=field,
            distributor=distributor,
            substrate_config=substrate_config,
            contact_id=contact_id,
            pass_index=pass_index,
        )
    except PreviousStateMinimalRunnerError:
        raise
    except Exception:
        raise _clean_failure("fresh fixation context construction failed") from None
    finally:
        field = distributor = substrate_config = None


def _require_context(
    context: object,
    *,
    contact_id: str | None = None,
) -> _FixationRuntimeContext:
    if not isinstance(context, _FixationRuntimeContext):
        raise _clean_failure("private fixation context is required")
    context._require_active()
    if contact_id is not None and context.contact_id != contact_id:
        raise _clean_failure("fixation context contact mismatch")
    return context


def _distribution_for_frame(
    context: _FixationRuntimeContext,
    frame: ReceptorContactFrame,
) -> ReceptorDistribution:
    try:
        active = _require_context(context, contact_id=frame.snapshot_id)
        field_time = CommonFieldTime(
            "organism.minimal.v1",
            frame.window_start_tick,
            frame.window_end_tick,
        )
        return active.distributor.distribute((frame,), field_time)
    except Exception:
        raise _clean_failure("fixation distribution failed") from None


def _distribution_digest(distribution: ReceptorDistribution) -> str:
    try:
        if not isinstance(distribution, ReceptorDistribution):
            raise TypeError
        digest = distribution.digest()
        if not _is_sha256(digest):
            raise ValueError
        return digest
    except Exception:
        raise _clean_failure("fixation distribution digest failed") from None


def _step_time_for_frame(frame: ReceptorContactFrame) -> MCMFieldStepTime:
    try:
        if not isinstance(frame, ReceptorContactFrame):
            raise TypeError
        return MCMFieldStepTime(
            "organism.minimal.v1",
            frame.window_start_tick,
            frame.window_end_tick,
            10.0,
        )
    except Exception:
        raise _clean_failure("fixation step time failed") from None


def _generator_and_boundary_for_distribution(
    context: _FixationRuntimeContext,
    distribution: ReceptorDistribution,
    step_time: MCMFieldStepTime,
) -> tuple[np.ndarray, np.ndarray]:
    try:
        active = _require_context(context)
        if (
            not isinstance(distribution, ReceptorDistribution)
            or not isinstance(step_time, MCMFieldStepTime)
            or distribution.field_time.clock_id != step_time.clock_id
            or distribution.field_time.window_start_tick != step_time.start_tick
            or distribution.field_time.window_end_tick != step_time.end_tick
        ):
            raise ValueError
        return _generator_and_boundary(
            active.field,
            distribution,
            active.substrate_config,
        )
    except Exception:
        raise _clean_failure("fixation generator boundary failed") from None


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )


def _array_digest(value: object, *, dimension: int, square: bool) -> str:
    if not isinstance(value, np.ndarray) or value.ndim != dimension:
        raise _clean_failure("fixation array shape invalid")
    if not np.issubdtype(value.dtype, np.number) or np.issubdtype(
        value.dtype, np.bool_
    ):
        raise _clean_failure("fixation array values invalid")
    if square and value.shape[0] != value.shape[1]:
        raise _clean_failure("fixation array shape invalid")
    try:
        payload = value.tolist()
        flattened = value.astype(np.float64, copy=False).reshape(-1)
        if any(not math.isfinite(float(item)) for item in flattened):
            raise ValueError
        if dimension == 2:
            payload = [[float(item) for item in row] for row in payload]
        else:
            payload = [float(item) for item in payload]
        return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    except Exception:
        raise _clean_failure("fixation array digest failed") from None


def _generator_digest(generator: np.ndarray) -> str:
    return _array_digest(generator, dimension=2, square=True)


def _boundary_digest(boundary: np.ndarray) -> str:
    return _array_digest(boundary, dimension=1, square=False)


def _discard_context(context: _FixationRuntimeContext) -> None:
    active = _require_context(context)
    active._field = None
    active._distributor = None
    active._substrate_config = None
    active._discarded = True


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _build_private_fixation_operations() -> _FixationOperations:
    return _FixationOperations(
        verify_bound_source_bytes=_verify_bound_source_bytes,
        build_fresh_context=_build_fresh_context,
        frame_for_contact=_frame_for_contact,
        distribution_for_frame=_distribution_for_frame,
        distribution_digest=_distribution_digest,
        step_time_for_frame=_step_time_for_frame,
        generator_and_boundary=_generator_and_boundary_for_distribution,
        generator_digest=_generator_digest,
        boundary_digest=_boundary_digest,
        discard_context=_discard_context,
    )
