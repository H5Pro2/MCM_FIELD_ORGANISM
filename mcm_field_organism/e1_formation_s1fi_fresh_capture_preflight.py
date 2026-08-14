"""S1-FI static input and resource preflight for the fresh capture run."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import ctypes
import hashlib
from pathlib import Path

from .e1_av_history_permutation import (
    E1AVHistoryPermutation,
    build_e1_av_history_permutation,
)
from .e1_completion_aligned_refinement import _source_contact_evidence
from .e1_confirmation_descriptor_refinement_planner import (
    E1ConfirmationDescriptorRefinementPlanSet,
    build_e1_confirmation_descriptor_refinement_plans,
)
from .e1_confirmation_full_formation_resource_preflight import (
    S1_EC12_EXPECTED_REFINEMENTS,
    S1_EC12_LIMITS,
)
from .e1_confirmation_research_corridor import (
    E1ConfirmationResearchCorridorDescriptor,
    build_e1_confirmation_research_corridor,
)
from .e1_formation_s1fh_fresh_capture_one_shot_contract import (
    E1FormationS1FHFreshCaptureOneShotContract,
)
from .e1_local_edge_plasticity import (
    E1_CONTRACT_ID,
    E1LocalEdgePlasticityContract,
    E1LocalEdgePlasticityState,
    build_neutral_e1_state,
    validate_e1_state_for_layer,
)
from .e1_refined_chain_canonical_producer import (
    _fresh_canonical_field,
    _initial_field_digest,
    _initial_state_digest,
)
from .e1_refined_formation_runner import _digest
from .shared_mcm_field import SharedMCMField


class E1FormationS1FIFreshCapturePreflightError(ValueError):
    """Raised when S1-FI inputs or resource evidence are malformed."""


S1_FI_PREFLIGHT_ID = "e1.formation-capture-fresh-preflight.s1fi.v1"
S1_FI_FORMATION_INPUT_ROLES = (
    "corridor",
    "av_permutation",
    "history_ab_plans",
    "history_ba_plans",
    "initial_field",
    "initial_state",
)
S1_FI_CHECK_NAMES = (
    "s1fh-contract-closed-and-bound",
    "upstream-source-exists-and-is-digest-bound",
    "six-formation-inputs-present",
    "probe-inputs-absent",
    "r2-r4-r8-history-plans-exact",
    "ab-ba-source-plan-bindings-exact",
    "initial-field-and-state-neutral",
    "field-geometry-exact",
    "fifteen-arm-fourteen-thousand-step-budget-exact",
    "fixed-resource-limits-pass",
    "free-memory-at-least-four-gib",
)


class _MemoryStatusEx(ctypes.Structure):
    _fields_ = (
        ("length", ctypes.c_ulong),
        ("memory_load", ctypes.c_ulong),
        ("total_physical", ctypes.c_ulonglong),
        ("available_physical", ctypes.c_ulonglong),
        ("total_page_file", ctypes.c_ulonglong),
        ("available_page_file", ctypes.c_ulonglong),
        ("total_virtual", ctypes.c_ulonglong),
        ("available_virtual", ctypes.c_ulonglong),
        ("available_extended_virtual", ctypes.c_ulonglong),
    )


@dataclass(frozen=True, slots=True)
class E1FormationS1FIResourceSnapshot:
    free_memory_bytes: int
    snapshot_digest: str

    def __post_init__(self) -> None:
        payload = {"free_memory_bytes": self.free_memory_bytes}
        if (
            isinstance(self.free_memory_bytes, bool)
            or not isinstance(self.free_memory_bytes, int)
            or self.free_memory_bytes < 0
            or self.snapshot_digest != _digest(payload)
        ):
            raise E1FormationS1FIFreshCapturePreflightError(
                "S1-FI resource snapshot is invalid"
            )


def read_e1_formation_s1fi_resource_snapshot(
) -> E1FormationS1FIResourceSnapshot:
    """Read available Windows memory without field or filesystem activity."""

    status = _MemoryStatusEx()
    status.length = ctypes.sizeof(status)
    try:
        succeeded = ctypes.windll.kernel32.GlobalMemoryStatusEx(  # type: ignore[attr-defined]
            ctypes.byref(status)
        )
    except (AttributeError, OSError) as exc:
        raise E1FormationS1FIFreshCapturePreflightError(
            "S1-FI cannot read the Windows memory snapshot"
        ) from exc
    if not succeeded:
        raise E1FormationS1FIFreshCapturePreflightError(
            "S1-FI Windows memory snapshot failed"
        )
    payload = {"free_memory_bytes": int(status.available_physical)}
    return E1FormationS1FIResourceSnapshot(
        **payload,
        snapshot_digest=_digest(payload),
    )


@dataclass(frozen=True, slots=True)
class E1FormationS1FIPreparedInputs:
    corridor: E1ConfirmationResearchCorridorDescriptor
    av_permutation: E1AVHistoryPermutation
    history_ab_plans: E1ConfirmationDescriptorRefinementPlanSet
    history_ba_plans: E1ConfirmationDescriptorRefinementPlanSet
    initial_field: SharedMCMField
    initial_state: E1LocalEdgePlasticityState
    input_manifest: tuple[tuple[str, str], ...]
    input_manifest_digest: str
    upstream_source_sha256: str

    def __post_init__(self) -> None:
        values = (
            self.corridor,
            self.av_permutation,
            self.history_ab_plans,
            self.history_ba_plans,
            self.initial_field,
            self.initial_state,
        )
        expected_types = (
            E1ConfirmationResearchCorridorDescriptor,
            E1AVHistoryPermutation,
            E1ConfirmationDescriptorRefinementPlanSet,
            E1ConfirmationDescriptorRefinementPlanSet,
            SharedMCMField,
            E1LocalEdgePlasticityState,
        )
        if any(not isinstance(value, kind) for value, kind in zip(values, expected_types, strict=True)):
            raise E1FormationS1FIFreshCapturePreflightError(
                "S1-FI prepared formation input type changed"
            )
        expected_manifest = (
            ("corridor", self.corridor.digest()),
            ("av_permutation", _digest(asdict(self.av_permutation))),
            ("history_ab_plans", self.history_ab_plans.digest()),
            ("history_ba_plans", self.history_ba_plans.digest()),
            ("initial_field", _initial_field_digest(self.initial_field)),
            ("initial_state", _initial_state_digest(self.initial_state)),
        )
        if (
            self.input_manifest != expected_manifest
            or tuple(role for role, _ in self.input_manifest)
            != S1_FI_FORMATION_INPUT_ROLES
            or self.input_manifest_digest != _digest(expected_manifest)
            or len(self.upstream_source_sha256) != 64
            or any(char not in "0123456789abcdef" for char in self.upstream_source_sha256)
        ):
            raise E1FormationS1FIFreshCapturePreflightError(
                "S1-FI formation input manifest changed"
            )


def prepare_e1_formation_s1fi_inputs(
    upstream_report_path: Path,
) -> E1FormationS1FIPreparedInputs:
    """Resolve formation-only AV inputs without probe data or run paths."""

    upstream = Path(upstream_report_path)
    if not upstream.is_file():
        raise E1FormationS1FIFreshCapturePreflightError(
            "S1-FI upstream AV evidence is missing"
        )
    upstream_sha256 = hashlib.sha256(upstream.read_bytes()).hexdigest()
    corridor = build_e1_confirmation_research_corridor(upstream)
    source = build_e1_av_history_permutation()
    ab_plans = build_e1_confirmation_descriptor_refinement_plans(
        corridor,
        source.history_ab,
        horizon_start_tick=0,
        horizon_end_tick=2_000_000,
        ticks_per_second=1_000_000.0,
    )
    ba_plans = build_e1_confirmation_descriptor_refinement_plans(
        corridor,
        source.history_ba,
        horizon_start_tick=0,
        horizon_end_tick=2_000_000,
        ticks_per_second=1_000_000.0,
    )
    initial_field = _fresh_canonical_field(source)
    initial_state = build_neutral_e1_state(
        initial_field.layer,
        E1LocalEdgePlasticityContract(E1_CONTRACT_ID, 1.0, 1.5, 0.25, 0.5),
    )
    manifest = (
        ("corridor", corridor.digest()),
        ("av_permutation", _digest(asdict(source))),
        ("history_ab_plans", ab_plans.digest()),
        ("history_ba_plans", ba_plans.digest()),
        ("initial_field", _initial_field_digest(initial_field)),
        ("initial_state", _initial_state_digest(initial_state)),
    )
    return E1FormationS1FIPreparedInputs(
        corridor=corridor,
        av_permutation=source,
        history_ab_plans=ab_plans,
        history_ba_plans=ba_plans,
        initial_field=initial_field,
        initial_state=initial_state,
        input_manifest=manifest,
        input_manifest_digest=_digest(manifest),
        upstream_source_sha256=upstream_sha256,
    )


@dataclass(frozen=True, slots=True)
class E1FormationS1FIFreshCapturePreflight:
    preflight_id: str
    source_s1fh_contract_digest: str
    upstream_source_sha256: str
    input_manifest: tuple[tuple[str, str], ...]
    input_manifest_digest: str
    resource_snapshot_digest: str
    refinement_step_counts: tuple[tuple[str, int, int, int], ...]
    formation_arm_count: int
    total_formation_field_steps: int
    field_node_count: int
    state_edge_count: int
    retained_binding_count: int
    free_memory_bytes: int
    minimum_free_memory_bytes: int
    checks: tuple[tuple[str, bool], ...]
    technical_preflight_passed: bool
    owner_authorization_present: bool
    execution_permitted: bool
    field_execution_performed: bool
    capture_performed: bool
    probe_execution_performed: bool
    persistence_performed: bool
    memory_claim_permitted: bool
    decision: str
    reason: str
    preflight_digest: str

    def __post_init__(self) -> None:
        passed = all(value for _, value in self.checks)
        decision = (
            "TECHNICALLY_READY_AWAITING_EXPLICIT_OWNER_AUTHORIZATION"
            if passed
            else "RESOURCE_OR_INPUT_PREFLIGHT_FAILED"
        )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "preflight_digest"
        }
        if (
            self.preflight_id != S1_FI_PREFLIGHT_ID
            or len(self.source_s1fh_contract_digest) != 64
            or len(self.upstream_source_sha256) != 64
            or tuple(role for role, _ in self.input_manifest)
            != S1_FI_FORMATION_INPUT_ROLES
            or self.input_manifest_digest != _digest(self.input_manifest)
            or len(self.resource_snapshot_digest) != 64
            or self.refinement_step_counts != S1_EC12_EXPECTED_REFINEMENTS
            or self.formation_arm_count != 15
            or self.total_formation_field_steps != 14_000
            or (self.field_node_count, self.state_edge_count) != (84, 145)
            or self.retained_binding_count != 2_175
            or self.minimum_free_memory_bytes != 4 * 1024**3
            or tuple(name for name, _ in self.checks) != S1_FI_CHECK_NAMES
            or self.technical_preflight_passed is not passed
            or self.owner_authorization_present is not False
            or self.execution_permitted is not False
            or any(
                value is not False
                for value in (
                    self.field_execution_performed,
                    self.capture_performed,
                    self.probe_execution_performed,
                    self.persistence_performed,
                    self.memory_claim_permitted,
                )
            )
            or self.decision != decision
            or not self.reason
            or self.preflight_digest != _digest(payload)
        ):
            raise E1FormationS1FIFreshCapturePreflightError(
                "S1-FI preflight changed or opened execution"
            )


def preflight_e1_formation_s1fi_fresh_capture(
    contract: E1FormationS1FHFreshCaptureOneShotContract,
    inputs: E1FormationS1FIPreparedInputs,
    resources: E1FormationS1FIResourceSnapshot,
) -> E1FormationS1FIFreshCapturePreflight:
    """Check formation-only inputs and memory without executing the field."""

    if not isinstance(contract, E1FormationS1FHFreshCaptureOneShotContract):
        raise E1FormationS1FIFreshCapturePreflightError(
            "S1-FI requires the typed S1-FH contract"
        )
    if not isinstance(inputs, E1FormationS1FIPreparedInputs) or not isinstance(
        resources, E1FormationS1FIResourceSnapshot
    ):
        raise E1FormationS1FIFreshCapturePreflightError(
            "S1-FI requires typed inputs and resource evidence"
        )
    contract.__post_init__()
    inputs.__post_init__()
    resources.__post_init__()
    ab_plans = inputs.history_ab_plans.plans
    ba_plans = inputs.history_ba_plans.plans
    refinements = tuple(
        (
            ab.refinement_id,
            ab.factor,
            len(ab.proposal_steps),
            len(ba.proposal_steps),
        )
        for ab, ba in zip(ab_plans, ba_plans, strict=True)
    )
    ab_evidence = _source_contact_evidence(
        inputs.av_permutation.history_ab, 1_000_000.0
    )
    ba_evidence = _source_contact_evidence(
        inputs.av_permutation.history_ba, 1_000_000.0
    )
    source_bindings_exact = (
        inputs.history_ab_plans.source_contact_digest == ab_evidence[0]
        and inputs.history_ba_plans.source_contact_digest == ba_evidence[0]
        and all(
            (
                item.source_contact_digest,
                item.source_signed_integral,
                item.source_absolute_integral,
                item.source_quadratic_integral,
            )
            == evidence
            for plans, evidence in (
                (ab_plans, ab_evidence),
                (ba_plans, ba_evidence),
            )
            for item in plans
        )
    )
    try:
        validate_e1_state_for_layer(inputs.initial_field.layer, inputs.initial_state)
        geometry_valid = True
    except ValueError:
        geometry_valid = False
    total_steps = sum(3 * ab + 2 * ba for _, _, ab, ba in refinements)
    field_nodes = len(inputs.initial_field.layer.neurons)
    state_edges = len(inputs.initial_state.edge_bindings)
    retained_bindings = 15 * state_edges
    limit = dict(S1_EC12_LIMITS)
    limits_pass = (
        field_nodes <= limit["maximum_field_nodes"]
        and state_edges <= limit["maximum_state_edges"]
        and max(max(ab, ba) for _, _, ab, ba in refinements)
        <= limit["maximum_single_arm_steps"]
        and total_steps <= limit["maximum_total_arm_steps"]
        and total_steps * field_nodes <= limit["maximum_node_step_units"]
        and total_steps * state_edges <= limit["maximum_edge_step_units"]
        and retained_bindings <= limit["maximum_retained_output_bindings"]
    )
    neutral = (
        inputs.initial_field.layer.tick == 0
        and inputs.initial_field.last_distribution is None
        and inputs.initial_field.substrate is None
        and all(item.binding == 0.0 for item in inputs.initial_state.edge_bindings)
    )
    checks = (
        (
            S1_FI_CHECK_NAMES[0],
            contract.execution_permitted is False
            and contract.owner_authorization_present is False,
        ),
        (S1_FI_CHECK_NAMES[1], bool(inputs.upstream_source_sha256)),
        (S1_FI_CHECK_NAMES[2], len(inputs.input_manifest) == 6),
        (
            S1_FI_CHECK_NAMES[3],
            all("probe" not in role for role, _ in inputs.input_manifest),
        ),
        (S1_FI_CHECK_NAMES[4], refinements == S1_EC12_EXPECTED_REFINEMENTS),
        (S1_FI_CHECK_NAMES[5], source_bindings_exact),
        (S1_FI_CHECK_NAMES[6], neutral),
        (S1_FI_CHECK_NAMES[7], geometry_valid and (field_nodes, state_edges) == (84, 145)),
        (S1_FI_CHECK_NAMES[8], total_steps == 14_000),
        (S1_FI_CHECK_NAMES[9], limits_pass),
        (
            S1_FI_CHECK_NAMES[10],
            resources.free_memory_bytes >= contract.minimum_free_memory_bytes,
        ),
    )
    passed = all(value for _, value in checks)
    values = {
        "preflight_id": S1_FI_PREFLIGHT_ID,
        "source_s1fh_contract_digest": contract.contract_digest,
        "upstream_source_sha256": inputs.upstream_source_sha256,
        "input_manifest": inputs.input_manifest,
        "input_manifest_digest": inputs.input_manifest_digest,
        "resource_snapshot_digest": resources.snapshot_digest,
        "refinement_step_counts": refinements,
        "formation_arm_count": 15,
        "total_formation_field_steps": total_steps,
        "field_node_count": field_nodes,
        "state_edge_count": state_edges,
        "retained_binding_count": retained_bindings,
        "free_memory_bytes": resources.free_memory_bytes,
        "minimum_free_memory_bytes": contract.minimum_free_memory_bytes,
        "checks": checks,
        "technical_preflight_passed": passed,
        "owner_authorization_present": False,
        "execution_permitted": False,
        "field_execution_performed": False,
        "capture_performed": False,
        "probe_execution_performed": False,
        "persistence_performed": False,
        "memory_claim_permitted": False,
        "decision": (
            "TECHNICALLY_READY_AWAITING_EXPLICIT_OWNER_AUTHORIZATION"
            if passed
            else "RESOURCE_OR_INPUT_PREFLIGHT_FAILED"
        ),
        "reason": (
            "formation-only-inputs-and-current-resource-snapshot-pass;"
            "owner-authorization-still-absent"
            if passed
            else "one-or-more-static-input-or-resource-gates-failed"
        ),
    }
    return E1FormationS1FIFreshCapturePreflight(
        **values,
        preflight_digest=_digest(values),
    )
