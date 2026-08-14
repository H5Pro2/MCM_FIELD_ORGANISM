"""In-memory W7-M source, region, intervention, and matrix adapter."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import math

from .audio_video_field_geometry import (
    ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    audio_video_dock_anatomies,
)
from .capacity_limited_mcm_f3_coupling import (
    MCMCapacityLimitedCouplingError,
    compute_capacity_limited_mcm_f3_coupling,
)
from .capacity_limited_mcm_f3_runtime import (
    MCMCapacityLimitedContinuationBinding,
    MCMCapacityLimitedRuntimeContract,
)
from .controlled_audio_video_test_world import (
    controlled_history_holdout_world_family,
)
from .mcm_f3_history_run import (
    MCMF3HistoryRunError,
    align_mcm_f3_fast_state,
    neutralize_mcm_f3_mass,
    transfer_mcm_f3_mass,
)
from .mcm_f3_k2b_source import MCMF3K2BSource, build_mcm_f3_k2b_source
from .mcm_f3_runtime import activate_mcm_f3_field
from .mcm_substrate_state import MCMSubstrateArmContract, MCMSubstrateState
from .receptor_time_model import ReceptorTimeSequence
from .shared_mcm_field import SharedMCMField, build_shared_mcm_field


class W7MCapacityFunctionMatrixError(ValueError):
    """Raised when the static W7-M matrix contract is incomplete."""


_MASS_ABS_TOLERANCE = 1e-12
_MATRIX_ID = "w7m.capacity-function-matrix.v1"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class W7MSourceRegions:
    """Source-only partition of field neurons into A, B, and tied regions."""

    a_neuron_ids: tuple[str, ...]
    b_neuron_ids: tuple[str, ...]
    tied_neuron_ids: tuple[str, ...]
    region_digest: str

    def __post_init__(self) -> None:
        groups = tuple(tuple(group) for group in self.groups)
        if not groups[0] or not groups[1]:
            raise W7MCapacityFunctionMatrixError(
                "W7-M source regions A and B must both be nonempty"
            )
        flattened = tuple(item for group in groups for item in group)
        if len(set(flattened)) != len(flattened):
            raise W7MCapacityFunctionMatrixError(
                "W7-M source regions must be disjoint"
            )
        if any(tuple(sorted(group)) != group for group in groups):
            raise W7MCapacityFunctionMatrixError(
                "W7-M source regions must use canonical neuron order"
            )
        expected = _digest(
            {
                "a_neuron_ids": groups[0],
                "b_neuron_ids": groups[1],
                "tied_neuron_ids": groups[2],
            }
        )
        if self.region_digest != expected:
            raise W7MCapacityFunctionMatrixError(
                "W7-M source region digest does not match its partition"
            )

    @property
    def groups(self) -> tuple[tuple[str, ...], ...]:
        return self.a_neuron_ids, self.b_neuron_ids, self.tied_neuron_ids

    @property
    def neuron_ids(self) -> tuple[str, ...]:
        return tuple(sorted(item for group in self.groups for item in group))


@dataclass(frozen=True, slots=True)
class W7MBaselineSpec:
    """One frozen matrix arm descriptor, not an executable model."""

    model_id: str
    equation_id: str
    equation_contract: str
    persistent_scalars_per_neuron: int
    parameter_bindings: tuple[tuple[str, float], ...]
    organism_runtime_allowed: bool

    def __post_init__(self) -> None:
        if not self.model_id or not self.equation_id or not self.equation_contract:
            raise W7MCapacityFunctionMatrixError(
                "W7-M baseline identities must be nonempty"
            )
        if (
            isinstance(self.persistent_scalars_per_neuron, bool)
            or not isinstance(self.persistent_scalars_per_neuron, int)
            or self.persistent_scalars_per_neuron < 0
            or self.persistent_scalars_per_neuron > 1
        ):
            raise W7MCapacityFunctionMatrixError(
                "W7-M baselines allow at most one scalar per neuron"
            )
        bindings = tuple(self.parameter_bindings)
        if tuple(sorted(bindings)) != bindings:
            raise W7MCapacityFunctionMatrixError(
                "W7-M baseline parameters must be canonical"
            )
        if len({name for name, _ in bindings}) != len(bindings):
            raise W7MCapacityFunctionMatrixError(
                "W7-M baseline parameter names must be unique"
            )
        if any(
            not name
            or isinstance(value, bool)
            or not math.isfinite(float(value))
            for name, value in bindings
        ):
            raise W7MCapacityFunctionMatrixError(
                "W7-M baseline parameters must be finite"
            )


@dataclass(frozen=True, slots=True)
class W7MPathSpec:
    """One fixed source path; phase names are not runtime inputs."""

    path_id: str
    prefix_id: str
    continuation_id: str
    checkpoint_count: int

    def __post_init__(self) -> None:
        if not self.path_id or not self.prefix_id or not self.continuation_id:
            raise W7MCapacityFunctionMatrixError(
                "W7-M path identities must be nonempty"
            )
        if (
            isinstance(self.checkpoint_count, bool)
            or not isinstance(self.checkpoint_count, int)
            or self.checkpoint_count != 5
        ):
            raise W7MCapacityFunctionMatrixError(
                "W7-M paths require exactly five checkpoints"
            )


@dataclass(frozen=True, slots=True)
class W7MRegionalCapacityLedger:
    """Observer-only regional M and free-capacity sums."""

    a_mass: float
    b_mass: float
    tied_mass: float
    a_free_capacity: float
    b_free_capacity: float
    tied_free_capacity: float
    total_mass: float
    total_free_capacity: float

    def __post_init__(self) -> None:
        if any(
            isinstance(getattr(self, role), bool)
            or not math.isfinite(float(getattr(self, role)))
            or getattr(self, role) < 0.0
            for role in self.__dataclass_fields__
        ):
            raise W7MCapacityFunctionMatrixError(
                "W7-M regional ledger values must be finite and nonnegative"
            )


@dataclass(frozen=True, slots=True)
class W7MInterventionState:
    """One observer-modified field paired with its renewed binding."""

    intervention_id: str
    field: SharedMCMField
    continuation_binding: MCMCapacityLimitedContinuationBinding

    def __post_init__(self) -> None:
        if not self.intervention_id:
            raise W7MCapacityFunctionMatrixError(
                "W7-M intervention identity must be nonempty"
            )
        if not isinstance(self.field, SharedMCMField):
            raise W7MCapacityFunctionMatrixError(
                "W7-M intervention requires one shared field"
            )
        if not isinstance(
            self.continuation_binding,
            MCMCapacityLimitedContinuationBinding,
        ):
            raise W7MCapacityFunctionMatrixError(
                "W7-M intervention requires one continuation binding"
            )
        if (
            self.continuation_binding.snapshot_digest
            != self.field.snapshot().digest()
        ):
            raise W7MCapacityFunctionMatrixError(
                "W7-M intervention binding does not match its field"
            )


@dataclass(frozen=True, slots=True)
class W7MCapacityFunctionMatrixAdapter:
    """Complete in-memory input contract without model execution."""

    matrix_id: str
    source: MCMF3K2BSource
    initial_field: SharedMCMField
    runtime_contract: MCMCapacityLimitedRuntimeContract
    regions: W7MSourceRegions
    baselines: tuple[W7MBaselineSpec, ...]
    paths: tuple[W7MPathSpec, ...]
    matrix_digest: str

    def __post_init__(self) -> None:
        if self.matrix_id != _MATRIX_ID:
            raise W7MCapacityFunctionMatrixError("W7-M matrix_id changed")
        if not isinstance(self.source, MCMF3K2BSource):
            raise W7MCapacityFunctionMatrixError("W7-M source is invalid")
        if (
            not isinstance(self.initial_field, SharedMCMField)
            or self.initial_field.substrate is None
            or self.initial_field.last_distribution is not None
        ):
            raise W7MCapacityFunctionMatrixError(
                "W7-M requires one fresh active substrate field"
            )
        if not isinstance(
            self.runtime_contract,
            MCMCapacityLimitedRuntimeContract,
        ):
            raise W7MCapacityFunctionMatrixError(
                "W7-M runtime contract is invalid"
            )
        if self.regions.neuron_ids != tuple(
            sorted(neuron.neuron_id for neuron in self.initial_field.layer.neurons)
        ):
            raise W7MCapacityFunctionMatrixError(
                "W7-M source regions must cover every field neuron"
            )
        if len({item.model_id for item in self.baselines}) != len(self.baselines):
            raise W7MCapacityFunctionMatrixError(
                "W7-M baseline identities must be unique"
            )
        if len({item.path_id for item in self.paths}) != len(self.paths):
            raise W7MCapacityFunctionMatrixError(
                "W7-M path identities must be unique"
            )
        if self.matrix_digest != _matrix_digest(self):
            raise W7MCapacityFunctionMatrixError(
                "W7-M matrix digest does not match its contract"
            )


def _source_groups(source: MCMF3K2BSource):
    return (
        (source.contact_a,),
        tuple(source.contact_b_steps),
    )


def _exposure_by_neuron(
    field: SharedMCMField,
    groups: tuple[tuple[ReceptorTimeSequence, ReceptorTimeSequence], ...],
    ticks_per_second: float,
) -> dict[str, float]:
    result = {neuron.neuron_id: 0.0 for neuron in field.layer.neurons}
    maps = {
        dock.dock_map.modality_id: dict(dock.dock_map.pairs)
        for dock in field.docks
    }
    for group in groups:
        for sequence in group:
            carrier_map = maps.get(sequence.modality_id)
            if carrier_map is None:
                raise W7MCapacityFunctionMatrixError(
                    "W7-M source modality is not present in the field"
                )
            for timed in sequence.frames:
                duration = (
                    timed.field_time.window_end_tick
                    - timed.field_time.window_start_tick
                ) / ticks_per_second
                for carrier_id, value in zip(
                    timed.frame.carrier_ids,
                    timed.frame.values,
                    strict=True,
                ):
                    result[carrier_map[carrier_id]] += abs(float(value)) * duration
    if any(not math.isfinite(value) or value < 0.0 for value in result.values()):
        raise W7MCapacityFunctionMatrixError(
            "W7-M source exposure must be finite and nonnegative"
        )
    return result


def _source_regions(
    field: SharedMCMField,
    source: MCMF3K2BSource,
) -> W7MSourceRegions:
    a_groups, b_groups = _source_groups(source)
    a_exposure = _exposure_by_neuron(field, a_groups, source.ticks_per_second)
    b_exposure = _exposure_by_neuron(field, b_groups, source.ticks_per_second)
    a_ids = tuple(
        sorted(key for key in a_exposure if a_exposure[key] > b_exposure[key])
    )
    b_ids = tuple(
        sorted(key for key in a_exposure if b_exposure[key] > a_exposure[key])
    )
    tied_ids = tuple(
        sorted(key for key in a_exposure if a_exposure[key] == b_exposure[key])
    )
    payload = {
        "a_neuron_ids": a_ids,
        "b_neuron_ids": b_ids,
        "tied_neuron_ids": tied_ids,
    }
    return W7MSourceRegions(a_ids, b_ids, tied_ids, _digest(payload))


def _baselines(site_capacity: float) -> tuple[W7MBaselineSpec, ...]:
    specs = (
        W7MBaselineSpec("cap", "w7k.capacity-limited.v1",
            "use=compute_capacity_limited_mcm_f3_coupling", 1, (
            ("eta", 1.0), ("kappa", 0.5), ("lambda_sm", 1.0),
            ("site_capacity", site_capacity),
        ), True),
        W7MBaselineSpec("p0", "mcm.fast.p0.v1",
            "state=fast_mcm_only", 0, (), True),
        W7MBaselineSpec("leak", "baseline.local-leak.v1",
            "dz_i/dt=(S_i-z_i)/tau;R_i=0", 1, (
            ("time_constant_seconds", 1.0),
        ), False),
        W7MBaselineSpec("lin", "baseline.linear-reciprocal.v1",
            "use=compute_mcm_f3_linear_coupled_baseline", 1, (
            ("eta", 1.0), ("kappa", 0.5), ("lambda_sm", 1.0),
        ), False),
        W7MBaselineSpec("f3", "baseline.k2-f3.v1",
            "use=compute_mcm_f3_coupling", 1, (
            ("eta", 1.0), ("kappa", 0.5), ("lambda_sm", 1.0),
        ), False),
        W7MBaselineSpec("const-v", "baseline.k2-f3.const-v.v1",
            "use=compute_mcm_f3_coupling;lambda_sm=V_initial", 1, (
            ("eta", 1.0), ("kappa", 0.5), ("lambda_sm", 0.5),
        ), False),
        W7MBaselineSpec("sat", "baseline.local-tanh-integrator.v1",
            "du_i/dt=(S_i-u_i)/tau;z_i=tanh(u_i);R_i=0", 1, (
            ("time_constant_seconds", 1.0),
        ), False),
        W7MBaselineSpec("mob", "baseline.source-mobility.v1",
            "q_i_to_j=lambda*M_i*(1-M_i/C_site)*(1+kappa*dS_ij)", 1, (
            ("eta", 1.0), ("initial_mobility", 0.5), ("kappa", 0.5),
            ("lambda_sm", 1.0),
            ("site_capacity", site_capacity),
        ), False),
        W7MBaselineSpec("norm", "baseline.global-l1-normalization.v1",
            "z_i=leak(S_i);observer_i=z_i/(epsilon+sum_j(abs(z_j)))", 1, (
            ("epsilon", 1e-12),
            ("time_constant_seconds", 1.0),
        ), False),
        W7MBaselineSpec("eta0", "w7k.capacity-limited.eta0.v1",
            "use=compute_capacity_limited_mcm_f3_coupling;eta=0", 1, (
            ("eta", 0.0), ("kappa", 0.5), ("lambda_sm", 1.0),
            ("site_capacity", site_capacity),
        ), False),
        W7MBaselineSpec("kappa0", "w7k.capacity-limited.kappa0.v1",
            "use=compute_capacity_limited_mcm_f3_coupling;kappa=0", 1, (
            ("eta", 1.0), ("kappa", 0.0), ("lambda_sm", 1.0),
            ("site_capacity", site_capacity),
        ), False),
        W7MBaselineSpec("sign", "w7k.capacity-limited.sign.v1",
            "use=compute_capacity_limited_mcm_f3_coupling;kappa=-0.5", 1, (
            ("eta", 1.0), ("kappa", -0.5), ("lambda_sm", 1.0),
            ("site_capacity", site_capacity),
        ), False),
    )
    return tuple(sorted(specs, key=lambda item: item.model_id))


def _paths() -> tuple[W7MPathSpec, ...]:
    return tuple(
        W7MPathSpec(*values, checkpoint_count=5)
        for values in (
            ("ab", "a", "b"),
            ("ag", "a", "gap"),
            ("ba", "b", "a"),
            ("bg", "b", "gap"),
            ("ua", "uniform", "a"),
            ("ub", "uniform", "b"),
            ("ug", "uniform", "gap"),
        )
    )


def _matrix_payload(
    matrix_id: str,
    source: MCMF3K2BSource,
    runtime_contract: MCMCapacityLimitedRuntimeContract,
    regions: W7MSourceRegions,
    baselines: tuple[W7MBaselineSpec, ...],
    paths: tuple[W7MPathSpec, ...],
) -> dict[str, object]:
    return {
        "matrix_id": matrix_id,
        "source_digests": {
            "contact_a": source.contact_a_digest,
            "contact_b_steps": source.contact_b_step_digests,
            "interruption_steps": source.interruption_step_digests,
            "probes": source.probe_digests,
        },
        "runtime_configuration_digest": runtime_contract.configuration_digest,
        "region_digest": regions.region_digest,
        "baselines": [
            {
                "model_id": item.model_id,
                "equation_id": item.equation_id,
                "equation_contract": item.equation_contract,
                "persistent_scalars_per_neuron": (
                    item.persistent_scalars_per_neuron
                ),
                "parameter_bindings": item.parameter_bindings,
                "organism_runtime_allowed": item.organism_runtime_allowed,
            }
            for item in baselines
        ],
        "paths": [
            {
                "path_id": item.path_id,
                "prefix_id": item.prefix_id,
                "continuation_id": item.continuation_id,
                "checkpoint_count": item.checkpoint_count,
            }
            for item in paths
        ],
    }


def _matrix_digest(adapter: W7MCapacityFunctionMatrixAdapter) -> str:
    return _digest(
        _matrix_payload(
            adapter.matrix_id,
            adapter.source,
            adapter.runtime_contract,
            adapter.regions,
            adapter.baselines,
            adapter.paths,
        )
    )


def build_w7m_capacity_function_matrix_adapter(
) -> W7MCapacityFunctionMatrixAdapter:
    """Build and freeze W7-M inputs without advancing any field model."""

    source = build_mcm_f3_k2b_source()
    same_world, _ = controlled_history_holdout_world_family()
    reference = tuple(sequence.frames[0].frame for sequence in source.contact_a)
    base = build_shared_mcm_field(
        reference,
        audio_video_dock_anatomies(
            auditory_carrier_count=len(reference[0].carrier_ids),
            visual_grid_columns=same_world.visual_config.grid_columns,
            visual_grid_rows=same_world.visual_config.grid_rows,
        ),
        sample_offsets=ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    )
    count = len(base.layer.neurons)
    site_capacity = 2.0 / count
    active = activate_mcm_f3_field(
        base,
        MCMSubstrateArmContract("w7m.cap", 1.0, 0.5, 1.0),
    )
    runtime_contract = MCMCapacityLimitedRuntimeContract(site_capacity)
    regions = _source_regions(base, source)
    baselines = _baselines(site_capacity)
    paths = _paths()
    matrix_digest = _digest(
        _matrix_payload(
            _MATRIX_ID,
            source,
            runtime_contract,
            regions,
            baselines,
            paths,
        )
    )
    return W7MCapacityFunctionMatrixAdapter(
        matrix_id=_MATRIX_ID,
        source=source,
        initial_field=active,
        runtime_contract=runtime_contract,
        regions=regions,
        baselines=baselines,
        paths=paths,
        matrix_digest=matrix_digest,
    )


def measure_w7m_regional_capacity(
    field: SharedMCMField,
    regions: W7MSourceRegions,
    contract: MCMCapacityLimitedRuntimeContract,
) -> W7MRegionalCapacityLedger:
    """Measure regional M and free capacity without changing field state."""

    if not isinstance(field, SharedMCMField) or field.substrate is None:
        raise W7MCapacityFunctionMatrixError(
            "W7-M regional measurement requires one substrate field"
        )
    if not isinstance(regions, W7MSourceRegions) or not isinstance(
        contract,
        MCMCapacityLimitedRuntimeContract,
    ):
        raise W7MCapacityFunctionMatrixError(
            "W7-M regional measurement contract is invalid"
        )
    mass = {item.neuron_id: item.mass for item in field.substrate.masses}
    if tuple(sorted(mass)) != regions.neuron_ids:
        raise W7MCapacityFunctionMatrixError(
            "W7-M regional measurement geometry changed"
        )
    sums = tuple(math.fsum(mass[item] for item in group) for group in regions.groups)
    free = tuple(
        len(group) * contract.site_capacity - value
        for group, value in zip(regions.groups, sums, strict=True)
    )
    if min(free) < -_MASS_ABS_TOLERANCE:
        raise W7MCapacityFunctionMatrixError(
            "W7-M regional measurement found negative free capacity"
        )
    total_mass = math.fsum(sums)
    if abs(total_mass - field.substrate.arm.initial_total_mass) > _MASS_ABS_TOLERANCE:
        raise W7MCapacityFunctionMatrixError(
            "W7-M regional measurement violated total mass"
        )
    return W7MRegionalCapacityLedger(
        a_mass=sums[0],
        b_mass=sums[1],
        tied_mass=sums[2],
        a_free_capacity=max(0.0, free[0]),
        b_free_capacity=max(0.0, free[1]),
        tied_free_capacity=max(0.0, free[2]),
        total_mass=total_mass,
        total_free_capacity=math.fsum(max(0.0, value) for value in free),
    )


def _bound_intervention(
    intervention_id: str,
    field: SharedMCMField,
    contract: MCMCapacityLimitedRuntimeContract,
) -> W7MInterventionState:
    if (
        not isinstance(field, SharedMCMField)
        or field.substrate is None
        or field.last_distribution is None
    ):
        raise W7MCapacityFunctionMatrixError(
            "W7-M intervention requires one completed field"
        )
    if not isinstance(contract, MCMCapacityLimitedRuntimeContract):
        raise W7MCapacityFunctionMatrixError(
            "W7-M intervention requires one runtime contract"
        )
    try:
        compute_capacity_limited_mcm_f3_coupling(
            field.layer,
            field.substrate,
            contract.coupling_contract,
        )
    except MCMCapacityLimitedCouplingError as exc:
        raise W7MCapacityFunctionMatrixError(str(exc)) from exc
    return W7MInterventionState(
        intervention_id,
        field,
        MCMCapacityLimitedContinuationBinding(
            field.snapshot().digest(),
            contract.configuration_digest,
        ),
    )


def align_w7m_fast_state(
    field: SharedMCMField,
    contract: MCMCapacityLimitedRuntimeContract,
) -> W7MInterventionState:
    try:
        aligned = align_mcm_f3_fast_state(field)
    except MCMF3HistoryRunError as exc:
        raise W7MCapacityFunctionMatrixError(str(exc)) from exc
    return _bound_intervention("fast-aligned", aligned, contract)


def neutralize_w7m_mass(
    field: SharedMCMField,
    contract: MCMCapacityLimitedRuntimeContract,
) -> W7MInterventionState:
    try:
        neutral = neutralize_mcm_f3_mass(field)
    except MCMF3HistoryRunError as exc:
        raise W7MCapacityFunctionMatrixError(str(exc)) from exc
    return _bound_intervention("m-neutral", neutral, contract)


def transplant_w7m_mass(
    target: SharedMCMField,
    source: SharedMCMField,
    contract: MCMCapacityLimitedRuntimeContract,
) -> W7MInterventionState:
    if (
        target.substrate is None
        or source.substrate is None
        or target.substrate.arm != source.substrate.arm
    ):
        raise W7MCapacityFunctionMatrixError(
            "W7-M M transplant requires the same model arm"
        )
    try:
        transplanted = transfer_mcm_f3_mass(target, source)
    except MCMF3HistoryRunError as exc:
        raise W7MCapacityFunctionMatrixError(str(exc)) from exc
    return _bound_intervention("m-transplant", transplanted, contract)


def _replace_arm(
    field: SharedMCMField,
    contract: MCMCapacityLimitedRuntimeContract,
    intervention_id: str,
    arm_id: str,
    *,
    kappa: float | None = None,
    eta: float | None = None,
) -> W7MInterventionState:
    if field.substrate is None:
        raise W7MCapacityFunctionMatrixError(
            "W7-M arm intervention requires one substrate field"
        )
    arm = field.substrate.arm
    replacement = MCMSubstrateArmContract(
        arm_id,
        arm.lambda_sm_per_second,
        arm.kappa if kappa is None else kappa,
        arm.eta if eta is None else eta,
        arm.initial_total_mass,
    )
    changed = replace(
        field,
        substrate=MCMSubstrateState(
            replacement,
            field.substrate.masses,
            field.substrate.edge_inventory_digest,
        ),
    )
    return _bound_intervention(intervention_id, changed, contract)


def ablate_w7m_eta(
    field: SharedMCMField,
    contract: MCMCapacityLimitedRuntimeContract,
) -> W7MInterventionState:
    return _replace_arm(
        field,
        contract,
        "eta0",
        "w7m.eta0",
        eta=0.0,
    )


def ablate_w7m_kappa(
    field: SharedMCMField,
    contract: MCMCapacityLimitedRuntimeContract,
) -> W7MInterventionState:
    return _replace_arm(
        field,
        contract,
        "kappa0",
        "w7m.kappa0",
        kappa=0.0,
    )


def invert_w7m_kappa(
    field: SharedMCMField,
    contract: MCMCapacityLimitedRuntimeContract,
) -> W7MInterventionState:
    if field.substrate is None:
        raise W7MCapacityFunctionMatrixError(
            "W7-M sign intervention requires one substrate field"
        )
    return _replace_arm(
        field,
        contract,
        "sign",
        "w7m.sign",
        kappa=-field.substrate.arm.kappa,
    )
