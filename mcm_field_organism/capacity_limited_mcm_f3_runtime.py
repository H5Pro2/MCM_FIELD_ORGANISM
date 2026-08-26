"""Opt-in SharedMCMField adapter for the W7-G capacity-limited coupling."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re

import numpy as np

from .capacity_limited_mcm_f3_coupling import (
    MCMCapacityLimitedCouplingContract,
    MCMCapacityLimitedCouplingError,
    compute_capacity_limited_mcm_f3_coupling,
)
from .mcm_f3_runtime import (
    MCMF3AdvanceResult,
    MCMF3RuntimeError,
    advance_mcm_f3_shared_field,
    advance_mcm_f3_shared_field_transient,
)
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .receptor_distributor import ReceptorDistribution
from .shared_mcm_field import SharedMCMField
from .transient_neuron_input import TransientNeuronInputSet


class MCMCapacityLimitedRuntimeError(ValueError):
    """Raised when the opt-in capacity runtime leaves its bound contract."""


_METHOD_ID = "w7k.capacity-limited-shared-mcm-field.v1"
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


def _configuration_digest(equation_id: str, site_capacity: float) -> str:
    encoded = json.dumps(
        {
            "equation_id": equation_id,
            "site_capacity": site_capacity,
        },
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class MCMCapacityLimitedRuntimeContract:
    """Immutable equation configuration outside the field snapshot."""

    site_capacity: float
    equation_id: str = _METHOD_ID

    def __post_init__(self) -> None:
        if self.equation_id != _METHOD_ID:
            raise MCMCapacityLimitedRuntimeError(
                "capacity runtime equation_id is fixed"
            )
        try:
            coupling_contract = MCMCapacityLimitedCouplingContract(
                self.site_capacity
            )
        except MCMCapacityLimitedCouplingError as exc:
            raise MCMCapacityLimitedRuntimeError(str(exc)) from exc
        object.__setattr__(self, "site_capacity", coupling_contract.site_capacity)

    @property
    def configuration_digest(self) -> str:
        return _configuration_digest(self.equation_id, self.site_capacity)

    @property
    def coupling_contract(self) -> MCMCapacityLimitedCouplingContract:
        return MCMCapacityLimitedCouplingContract(self.site_capacity)


@dataclass(frozen=True, slots=True)
class MCMCapacityLimitedContinuationBinding:
    """Pair one completed field state with its external equation contract."""

    snapshot_digest: str
    configuration_digest: str

    def __post_init__(self) -> None:
        for role in ("snapshot_digest", "configuration_digest"):
            value = getattr(self, role)
            if not isinstance(value, str) or not _DIGEST.fullmatch(value):
                raise MCMCapacityLimitedRuntimeError(
                    f"{role} must be one lowercase SHA-256 digest"
                )


@dataclass(frozen=True, slots=True)
class MCMCapacityLimitedRuntimeDiagnostics:
    """Passive capacity diagnostics, never persisted as field state."""

    method_id: str
    validation_count: int
    maximum_mass: float
    minimum_free_capacity: float
    maximum_capacity_excess: float
    configuration_digest: str

    def __post_init__(self) -> None:
        if self.method_id not in {_METHOD_ID, "p0.exact"}:
            raise MCMCapacityLimitedRuntimeError(
                "unknown capacity runtime method"
            )
        if (
            isinstance(self.validation_count, bool)
            or not isinstance(self.validation_count, int)
            or self.validation_count < 1
        ):
            raise MCMCapacityLimitedRuntimeError(
                "validation_count must be a positive integer"
            )
        for role in (
            "maximum_mass",
            "minimum_free_capacity",
            "maximum_capacity_excess",
        ):
            value = getattr(self, role)
            if (
                isinstance(value, bool)
                or not math.isfinite(float(value))
                or value < 0.0
            ):
                raise MCMCapacityLimitedRuntimeError(
                    f"{role} must be finite and nonnegative"
                )
        if not isinstance(self.configuration_digest, str) or not _DIGEST.fullmatch(
            self.configuration_digest
        ):
            raise MCMCapacityLimitedRuntimeError(
                "configuration_digest must be one lowercase SHA-256 digest"
            )


@dataclass(frozen=True, slots=True)
class MCMCapacityLimitedRuntimeResult:
    """Completed base-runtime result plus external capacity evidence."""

    advance: MCMF3AdvanceResult
    capacity_diagnostics: MCMCapacityLimitedRuntimeDiagnostics
    continuation_binding: MCMCapacityLimitedContinuationBinding

    def __post_init__(self) -> None:
        if not isinstance(self.advance, MCMF3AdvanceResult):
            raise MCMCapacityLimitedRuntimeError(
                "capacity result requires one F3 advance result"
            )
        if not isinstance(
            self.capacity_diagnostics,
            MCMCapacityLimitedRuntimeDiagnostics,
        ):
            raise MCMCapacityLimitedRuntimeError(
                "capacity result requires capacity diagnostics"
            )
        if not isinstance(
            self.continuation_binding,
            MCMCapacityLimitedContinuationBinding,
        ):
            raise MCMCapacityLimitedRuntimeError(
                "capacity result requires one continuation binding"
            )
        if (
            self.capacity_diagnostics.configuration_digest
            != self.continuation_binding.configuration_digest
        ):
            raise MCMCapacityLimitedRuntimeError(
                "capacity result configuration bindings differ"
            )
        if (
            self.continuation_binding.snapshot_digest
            != self.advance.field.snapshot().digest()
        ):
            raise MCMCapacityLimitedRuntimeError(
                "capacity result snapshot binding differs from its field"
            )

    @property
    def field(self) -> SharedMCMField:
        return self.advance.field


@dataclass(slots=True)
class _CapacityAccumulator:
    validation_count: int = 0
    maximum_mass: float = 0.0
    minimum_free_capacity: float = math.inf
    maximum_capacity_excess: float = 0.0


def _validate_binding(
    field: SharedMCMField,
    contract: MCMCapacityLimitedRuntimeContract,
    continuation_binding: MCMCapacityLimitedContinuationBinding | None,
) -> None:
    if not isinstance(field, SharedMCMField) or field.substrate is None:
        raise MCMCapacityLimitedRuntimeError(
            "capacity runtime requires one substrate field"
        )
    if field.last_distribution is None:
        if continuation_binding is not None:
            raise MCMCapacityLimitedRuntimeError(
                "an initial field cannot consume a continuation binding"
            )
        return
    if continuation_binding is None:
        raise MCMCapacityLimitedRuntimeError(
            "a completed field requires its continuation binding"
        )
    if not isinstance(
        continuation_binding,
        MCMCapacityLimitedContinuationBinding,
    ):
        raise MCMCapacityLimitedRuntimeError(
            "invalid capacity continuation binding"
        )
    if continuation_binding.configuration_digest != contract.configuration_digest:
        raise MCMCapacityLimitedRuntimeError(
            "continuation configuration does not match the capacity contract"
        )
    if continuation_binding.snapshot_digest != field.snapshot().digest():
        raise MCMCapacityLimitedRuntimeError(
            "continuation snapshot does not match the supplied field"
        )


def _validate_initial_coupling(
    field: SharedMCMField,
    contract: MCMCapacityLimitedRuntimeContract,
) -> None:
    try:
        compute_capacity_limited_mcm_f3_coupling(
            field.layer,
            field.substrate,
            contract.coupling_contract,
        )
    except MCMCapacityLimitedCouplingError as exc:
        raise MCMCapacityLimitedRuntimeError(str(exc)) from exc


def _capacity_validator(
    contract: MCMCapacityLimitedRuntimeContract,
    accumulator: _CapacityAccumulator,
):
    def validate(
        activation: np.ndarray,
        afterimage: np.ndarray,
        mass: np.ndarray,
    ) -> None:
        del activation, afterimage
        maximum_mass = float(np.max(mass))
        excess = max(0.0, maximum_mass - contract.site_capacity)
        accumulator.validation_count += 1
        accumulator.maximum_mass = max(accumulator.maximum_mass, maximum_mass)
        accumulator.minimum_free_capacity = min(
            accumulator.minimum_free_capacity,
            max(0.0, contract.site_capacity - maximum_mass),
        )
        accumulator.maximum_capacity_excess = max(
            accumulator.maximum_capacity_excess,
            excess,
        )
        if excess > 0.0:
            raise MCMCapacityLimitedRuntimeError(
                "capacity runtime exceeded site_capacity"
            )

    return validate


def _coupling_calculator(contract: MCMCapacityLimitedRuntimeContract):
    def calculate(layer, substrate):
        try:
            return compute_capacity_limited_mcm_f3_coupling(
                layer,
                substrate,
                contract.coupling_contract,
            )
        except MCMCapacityLimitedCouplingError as exc:
            raise MCMCapacityLimitedRuntimeError(str(exc)) from exc

    return calculate


def _result(
    advance: MCMF3AdvanceResult,
    contract: MCMCapacityLimitedRuntimeContract,
    accumulator: _CapacityAccumulator,
) -> MCMCapacityLimitedRuntimeResult:
    diagnostics = MCMCapacityLimitedRuntimeDiagnostics(
        method_id=(
            "p0.exact"
            if advance.diagnostics.method_id == "p0.exact"
            else _METHOD_ID
        ),
        validation_count=accumulator.validation_count,
        maximum_mass=accumulator.maximum_mass,
        minimum_free_capacity=accumulator.minimum_free_capacity,
        maximum_capacity_excess=accumulator.maximum_capacity_excess,
        configuration_digest=contract.configuration_digest,
    )
    return MCMCapacityLimitedRuntimeResult(
        advance=advance,
        capacity_diagnostics=diagnostics,
        continuation_binding=MCMCapacityLimitedContinuationBinding(
            snapshot_digest=advance.field.snapshot().digest(),
            configuration_digest=contract.configuration_digest,
        ),
    )


def _prepare(
    field: SharedMCMField,
    contract: MCMCapacityLimitedRuntimeContract,
    continuation_binding: MCMCapacityLimitedContinuationBinding | None,
) -> None:
    if not isinstance(contract, MCMCapacityLimitedRuntimeContract):
        raise MCMCapacityLimitedRuntimeError(
            "capacity runtime requires one immutable runtime contract"
        )
    _validate_binding(field, contract, continuation_binding)
    _validate_initial_coupling(field, contract)


def advance_capacity_limited_mcm_f3_shared_field(
    field: SharedMCMField,
    distribution: ReceptorDistribution,
    step_time,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    contract: MCMCapacityLimitedRuntimeContract,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
    *,
    refinement: int = 1,
    continuation_binding: MCMCapacityLimitedContinuationBinding | None = None,
) -> MCMCapacityLimitedRuntimeResult:
    """Advance one continuous boundary through the opt-in capacity adapter."""

    _prepare(field, contract, continuation_binding)
    accumulator = _CapacityAccumulator()
    validator = _capacity_validator(contract, accumulator)
    if field.substrate.arm.is_null_arm:
        activation = np.asarray(
            [item.activation for item in field.layer.neurons], dtype=np.float64
        )
        afterimage = np.asarray(
            [item.afterimage for item in field.layer.neurons], dtype=np.float64
        )
        mass = np.asarray(
            [item.mass for item in field.substrate.masses], dtype=np.float64
        )
        validator(activation, afterimage, mass)
    try:
        advance = advance_mcm_f3_shared_field(
            field,
            distribution,
            step_time,
            substrate_config,
            afterimage_config,
            dissipation_config,
            refinement=refinement,
            _coupling_calculator=_coupling_calculator(contract),
            _stage_validator=validator,
        )
    except MCMF3RuntimeError as exc:
        raise MCMCapacityLimitedRuntimeError(str(exc)) from exc
    if field.substrate.arm.is_null_arm:
        mass = np.asarray(
            [item.mass for item in advance.field.substrate.masses],
            dtype=np.float64,
        )
        validator(
            np.asarray(
                [item.activation for item in advance.field.layer.neurons],
                dtype=np.float64,
            ),
            np.asarray(
                [item.afterimage for item in advance.field.layer.neurons],
                dtype=np.float64,
            ),
            mass,
        )
    return _result(advance, contract, accumulator)


def advance_capacity_limited_mcm_f3_shared_field_transient(
    field: SharedMCMField,
    distribution: ReceptorDistribution,
    transient_inputs: TransientNeuronInputSet,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    contract: MCMCapacityLimitedRuntimeContract,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
    *,
    refinement: int = 1,
    continuation_binding: MCMCapacityLimitedContinuationBinding | None = None,
    _state_observer=None,
) -> MCMCapacityLimitedRuntimeResult:
    """Advance one event-aligned boundary through the capacity adapter."""

    _prepare(field, contract, continuation_binding)
    accumulator = _CapacityAccumulator()
    validator = _capacity_validator(contract, accumulator)
    state_observer = None
    if _state_observer is not None:
        def state_observer(tick, activation, afterimage, mass):
            activation.setflags(write=False)
            afterimage.setflags(write=False)
            mass.setflags(write=False)
            return _state_observer(tick, activation, afterimage, mass)
    if field.substrate.arm.is_null_arm:
        validator(
            np.asarray(
                [item.activation for item in field.layer.neurons],
                dtype=np.float64,
            ),
            np.asarray(
                [item.afterimage for item in field.layer.neurons],
                dtype=np.float64,
            ),
            np.asarray(
                [item.mass for item in field.substrate.masses], dtype=np.float64
            ),
        )
    try:
        advance = advance_mcm_f3_shared_field_transient(
            field,
            distribution,
            transient_inputs,
            substrate_config,
            afterimage_config,
            dissipation_config,
            refinement=refinement,
            _coupling_calculator=_coupling_calculator(contract),
            _state_observer=state_observer,
            _stage_validator=validator,
        )
    except MCMF3RuntimeError as exc:
        raise MCMCapacityLimitedRuntimeError(str(exc)) from exc
    if field.substrate.arm.is_null_arm:
        validator(
            np.asarray(
                [item.activation for item in advance.field.layer.neurons],
                dtype=np.float64,
            ),
            np.asarray(
                [item.afterimage for item in advance.field.layer.neurons],
                dtype=np.float64,
            ),
            np.asarray(
                [item.mass for item in advance.field.substrate.masses],
                dtype=np.float64,
            ),
        )
    return _result(advance, contract, accumulator)
