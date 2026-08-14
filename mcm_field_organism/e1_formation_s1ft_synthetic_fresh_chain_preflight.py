"""S1-FT synthetic preflight for the closed fresh formation-probe chain."""

from __future__ import annotations

from dataclasses import dataclass

from .e1_formation_s1fi_fresh_capture_preflight import (
    E1FormationS1FIPreparedInputs,
    S1_FI_FORMATION_INPUT_ROLES,
)
from .e1_formation_s1fp_common_probe_contract import (
    E1FormationS1FPCommonProbeContract,
    S1_FP_PROBE_ROLES,
    S1_FP_REFINEMENTS,
)
from .e1_formation_s1fr_static_resource_matrix_audit import (
    E1FormationS1FRStaticResourceMatrixAudit,
)
from .e1_formation_s1fs_fresh_chain_one_shot_contract import (
    E1FormationS1FSFreshChainOneShotContract,
    S1_FS_EXECUTION_SEQUENCE,
    S1_FS_RETURN_COMPONENTS,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1FTSyntheticFreshChainPreflightError(ValueError):
    """Raised when S1-FT receives malformed or execution-opening evidence."""


S1_FT_PREFLIGHT_ID = "e1.fresh-chain-synthetic-preflight.s1ft.v1"
S1_FT_CHAIN_MANIFEST_ROLES = (
    "formation-input-manifest",
    "probe-contract",
    "probe-source",
    "probe-slot-matrix",
    "execution-sequence",
    "atomic-return-schema",
)
S1_FT_CHECK_NAMES = (
    "s1fs-contract-closed-and-bound",
    "s1fr-budget-and-matrix-bound",
    "six-typed-formation-inputs-bound",
    "thirty-probe-slots-complete-and-unique",
    "probe-source-and-state-roles-bound",
    "execution-sequence-exact",
    "atomic-return-schema-complete",
    "forty-five-calls-and-28000-step-budget-exact",
    "synthetic-free-memory-at-least-four-gib",
    "no-observed-result-or-field-execution-present",
)


def _probe_state_role(role: str) -> str:
    if role.startswith("p0-reset-"):
        return "none"
    side = "ab" if role.endswith("-ab") else "ba"
    if "formation-ablated" in role:
        return f"formation-ablated-{side}"
    return f"active-{side}"


@dataclass(frozen=True, slots=True)
class E1FormationS1FTSyntheticResourceSnapshot:
    free_memory_bytes: int
    synthetic: bool
    measured_current_system: bool
    snapshot_digest: str

    def __post_init__(self) -> None:
        payload = {
            "free_memory_bytes": self.free_memory_bytes,
            "synthetic": self.synthetic,
            "measured_current_system": self.measured_current_system,
        }
        if (
            isinstance(self.free_memory_bytes, bool)
            or not isinstance(self.free_memory_bytes, int)
            or self.free_memory_bytes < 0
            or self.synthetic is not True
            or self.measured_current_system is not False
            or self.snapshot_digest != _digest(payload)
        ):
            raise E1FormationS1FTSyntheticFreshChainPreflightError(
                "S1-FT synthetic resource snapshot changed"
            )


def build_e1_formation_s1ft_synthetic_resource_snapshot(
    free_memory_bytes: int = 8 * 1024**3,
) -> E1FormationS1FTSyntheticResourceSnapshot:
    """Build explicit fake resource evidence without reading the host."""

    values = {
        "free_memory_bytes": free_memory_bytes,
        "synthetic": True,
        "measured_current_system": False,
    }
    return E1FormationS1FTSyntheticResourceSnapshot(
        **values,
        snapshot_digest=_digest(values),
    )


@dataclass(frozen=True, slots=True)
class E1FormationS1FTPreparedSyntheticChain:
    source_s1fs_contract_digest: str
    source_s1fr_audit_digest: str
    source_s1fp_contract_digest: str
    source_s1fi_input_manifest_digest: str
    formation_input_manifest: tuple[tuple[str, str], ...]
    probe_source_digest: str
    probe_slots: tuple[tuple[str, str, str], ...]
    execution_sequence: tuple[str, ...]
    atomic_return_components: tuple[str, ...]
    chain_manifest: tuple[tuple[str, str], ...]
    chain_manifest_digest: str

    def __post_init__(self) -> None:
        expected_slots = tuple(
            (refinement, role, _probe_state_role(role))
            for refinement in S1_FP_REFINEMENTS
            for role in S1_FP_PROBE_ROLES
        )
        expected_manifest = (
            ("formation-input-manifest", self.source_s1fi_input_manifest_digest),
            ("probe-contract", self.source_s1fp_contract_digest),
            ("probe-source", self.probe_source_digest),
            ("probe-slot-matrix", _digest(expected_slots)),
            ("execution-sequence", _digest(S1_FS_EXECUTION_SEQUENCE)),
            ("atomic-return-schema", _digest(S1_FS_RETURN_COMPONENTS)),
        )
        if (
            any(
                len(value) != 64
                for value in (
                    self.source_s1fs_contract_digest,
                    self.source_s1fr_audit_digest,
                    self.source_s1fp_contract_digest,
                    self.source_s1fi_input_manifest_digest,
                    self.probe_source_digest,
                )
            )
            or tuple(role for role, _ in self.formation_input_manifest)
            != S1_FI_FORMATION_INPUT_ROLES
            or len(self.formation_input_manifest) != 6
            or self.probe_slots != expected_slots
            or len(set((a, b) for a, b, _ in self.probe_slots)) != 30
            or self.execution_sequence != S1_FS_EXECUTION_SEQUENCE
            or self.atomic_return_components != S1_FS_RETURN_COMPONENTS
            or self.chain_manifest != expected_manifest
            or tuple(role for role, _ in self.chain_manifest)
            != S1_FT_CHAIN_MANIFEST_ROLES
            or self.chain_manifest_digest != _digest(expected_manifest)
        ):
            raise E1FormationS1FTSyntheticFreshChainPreflightError(
                "S1-FT prepared synthetic chain changed"
            )


@dataclass(frozen=True, slots=True)
class E1FormationS1FTSyntheticAtomicReturnSchema:
    components: tuple[str, ...]
    component_schema_digests: tuple[tuple[str, str], ...]
    observed_values_present: bool
    atomic_result_emitted: bool
    field_steps_executed: int
    schema_digest: str

    def __post_init__(self) -> None:
        expected = tuple(
            (component, _digest(("s1ft-schema-only", component)))
            for component in S1_FS_RETURN_COMPONENTS
        )
        payload = {
            "components": S1_FS_RETURN_COMPONENTS,
            "component_schema_digests": expected,
            "observed_values_present": False,
            "atomic_result_emitted": False,
            "field_steps_executed": 0,
        }
        if (
            self.components != S1_FS_RETURN_COMPONENTS
            or self.component_schema_digests != expected
            or self.observed_values_present is not False
            or self.atomic_result_emitted is not False
            or self.field_steps_executed != 0
            or self.schema_digest != _digest(payload)
        ):
            raise E1FormationS1FTSyntheticFreshChainPreflightError(
                "S1-FT atomic return schema contains data or changed"
            )


def prepare_e1_formation_s1ft_synthetic_objects(
    contract: E1FormationS1FSFreshChainOneShotContract,
    audit: E1FormationS1FRStaticResourceMatrixAudit,
    probe_contract: E1FormationS1FPCommonProbeContract,
    inputs: E1FormationS1FIPreparedInputs,
) -> tuple[
    E1FormationS1FTPreparedSyntheticChain,
    E1FormationS1FTSyntheticAtomicReturnSchema,
]:
    """Bind typed schema objects without resolving fields or running kernels."""

    for value, expected_type in (
        (contract, E1FormationS1FSFreshChainOneShotContract),
        (audit, E1FormationS1FRStaticResourceMatrixAudit),
        (probe_contract, E1FormationS1FPCommonProbeContract),
        (inputs, E1FormationS1FIPreparedInputs),
    ):
        if not isinstance(value, expected_type):
            raise E1FormationS1FTSyntheticFreshChainPreflightError(
                "S1-FT requires typed upstream objects"
            )
        value.__post_init__()
    if (
        contract.source_s1fr_audit_digest != audit.audit_digest
        or audit.source_contract_digest != probe_contract.contract_digest
        or contract.execution_permitted is not False
    ):
        raise E1FormationS1FTSyntheticFreshChainPreflightError(
            "S1-FT upstream digest chain changed or opened execution"
        )
    slots = tuple(
        (refinement, role, _probe_state_role(role))
        for refinement in S1_FP_REFINEMENTS
        for role in S1_FP_PROBE_ROLES
    )
    manifest = (
        ("formation-input-manifest", inputs.input_manifest_digest),
        ("probe-contract", probe_contract.contract_digest),
        ("probe-source", probe_contract.probe_source_digest),
        ("probe-slot-matrix", _digest(slots)),
        ("execution-sequence", _digest(contract.execution_sequence)),
        ("atomic-return-schema", _digest(contract.atomic_return_components)),
    )
    chain = E1FormationS1FTPreparedSyntheticChain(
        source_s1fs_contract_digest=contract.contract_digest,
        source_s1fr_audit_digest=audit.audit_digest,
        source_s1fp_contract_digest=probe_contract.contract_digest,
        source_s1fi_input_manifest_digest=inputs.input_manifest_digest,
        formation_input_manifest=inputs.input_manifest,
        probe_source_digest=probe_contract.probe_source_digest,
        probe_slots=slots,
        execution_sequence=contract.execution_sequence,
        atomic_return_components=contract.atomic_return_components,
        chain_manifest=manifest,
        chain_manifest_digest=_digest(manifest),
    )
    schema_values = {
        "components": S1_FS_RETURN_COMPONENTS,
        "component_schema_digests": tuple(
            (component, _digest(("s1ft-schema-only", component)))
            for component in S1_FS_RETURN_COMPONENTS
        ),
        "observed_values_present": False,
        "atomic_result_emitted": False,
        "field_steps_executed": 0,
    }
    schema = E1FormationS1FTSyntheticAtomicReturnSchema(
        **schema_values,
        schema_digest=_digest(schema_values),
    )
    return chain, schema


@dataclass(frozen=True, slots=True)
class E1FormationS1FTSyntheticFreshChainPreflight:
    preflight_id: str
    source_contract_digest: str
    source_audit_digest: str
    prepared_chain_digest: str
    resource_snapshot_digest: str
    atomic_return_schema_digest: str
    formation_input_count: int
    probe_slot_count: int
    planned_field_call_count: int
    planned_field_steps: int
    free_memory_bytes: int
    minimum_free_memory_bytes: int
    checks: tuple[tuple[str, bool], ...]
    synthetic_preflight_passed: bool
    real_resource_snapshot_required_later: bool
    real_runner_implemented: bool
    owner_authorization_present: bool
    execution_permitted: bool
    field_execution_performed: bool
    observed_result_present: bool
    persistence_performed: bool
    claims_permitted: bool
    decision: str
    reason: str
    preflight_digest: str

    def __post_init__(self) -> None:
        passed = all(value for _, value in self.checks)
        decision = (
            "SYNTHETIC_FRESH_CHAIN_PREFLIGHT_PASSED_REAL_RUNNER_AND_AUTHORIZATION_ABSENT"
            if passed
            else "SYNTHETIC_FRESH_CHAIN_PREFLIGHT_FAILED_CLOSED"
        )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "preflight_digest"
        }
        if (
            self.preflight_id != S1_FT_PREFLIGHT_ID
            or any(
                len(value) != 64
                for value in (
                    self.source_contract_digest,
                    self.source_audit_digest,
                    self.prepared_chain_digest,
                    self.resource_snapshot_digest,
                    self.atomic_return_schema_digest,
                )
            )
            or (self.formation_input_count, self.probe_slot_count) != (6, 30)
            or (self.planned_field_call_count, self.planned_field_steps)
            != (45, 28_000)
            or self.minimum_free_memory_bytes != 4 * 1024**3
            or tuple(name for name, _ in self.checks) != S1_FT_CHECK_NAMES
            or self.synthetic_preflight_passed is not passed
            or self.real_resource_snapshot_required_later is not True
            or any(
                value is not False
                for value in (
                    self.real_runner_implemented,
                    self.owner_authorization_present,
                    self.execution_permitted,
                    self.field_execution_performed,
                    self.observed_result_present,
                    self.persistence_performed,
                    self.claims_permitted,
                )
            )
            or self.decision != decision
            or not self.reason
            or self.preflight_digest != _digest(payload)
        ):
            raise E1FormationS1FTSyntheticFreshChainPreflightError(
                "S1-FT preflight changed or opened execution"
            )


def preflight_e1_formation_s1ft_synthetically(
    contract: E1FormationS1FSFreshChainOneShotContract,
    audit: E1FormationS1FRStaticResourceMatrixAudit,
    chain: E1FormationS1FTPreparedSyntheticChain,
    resources: E1FormationS1FTSyntheticResourceSnapshot,
    return_schema: E1FormationS1FTSyntheticAtomicReturnSchema,
) -> E1FormationS1FTSyntheticFreshChainPreflight:
    """Validate schema, order, and fake resources without any field work."""

    for value, expected_type in (
        (contract, E1FormationS1FSFreshChainOneShotContract),
        (audit, E1FormationS1FRStaticResourceMatrixAudit),
        (chain, E1FormationS1FTPreparedSyntheticChain),
        (resources, E1FormationS1FTSyntheticResourceSnapshot),
        (return_schema, E1FormationS1FTSyntheticAtomicReturnSchema),
    ):
        if not isinstance(value, expected_type):
            raise E1FormationS1FTSyntheticFreshChainPreflightError(
                "S1-FT preflight requires typed objects"
            )
        value.__post_init__()
    expected_slots = tuple(
        (refinement, role, _probe_state_role(role))
        for refinement in S1_FP_REFINEMENTS
        for role in S1_FP_PROBE_ROLES
    )
    checks = (
        (
            S1_FT_CHECK_NAMES[0],
            chain.source_s1fs_contract_digest == contract.contract_digest
            and contract.execution_permitted is False,
        ),
        (
            S1_FT_CHECK_NAMES[1],
            chain.source_s1fr_audit_digest == audit.audit_digest
            and audit.total_field_steps == 28_000,
        ),
        (
            S1_FT_CHECK_NAMES[2],
            len(chain.formation_input_manifest) == 6
            and tuple(role for role, _ in chain.formation_input_manifest)
            == S1_FI_FORMATION_INPUT_ROLES,
        ),
        (
            S1_FT_CHECK_NAMES[3],
            chain.probe_slots == expected_slots
            and len(set((a, b) for a, b, _ in chain.probe_slots)) == 30,
        ),
        (
            S1_FT_CHECK_NAMES[4],
            len(chain.probe_source_digest) == 64
            and all(role == _probe_state_role(slot) for _, slot, role in chain.probe_slots),
        ),
        (S1_FT_CHECK_NAMES[5], chain.execution_sequence == S1_FS_EXECUTION_SEQUENCE),
        (
            S1_FT_CHECK_NAMES[6],
            return_schema.components == S1_FS_RETURN_COMPONENTS
            and len(return_schema.component_schema_digests)
            == len(S1_FS_RETURN_COMPONENTS),
        ),
        (
            S1_FT_CHECK_NAMES[7],
            contract.total_field_call_count == 45
            and contract.maximum_total_field_steps == 28_000,
        ),
        (
            S1_FT_CHECK_NAMES[8],
            resources.free_memory_bytes >= contract.minimum_free_memory_bytes,
        ),
        (
            S1_FT_CHECK_NAMES[9],
            return_schema.observed_values_present is False
            and return_schema.atomic_result_emitted is False
            and return_schema.field_steps_executed == 0,
        ),
    )
    passed = all(value for _, value in checks)
    values = {
        "preflight_id": S1_FT_PREFLIGHT_ID,
        "source_contract_digest": contract.contract_digest,
        "source_audit_digest": audit.audit_digest,
        "prepared_chain_digest": chain.chain_manifest_digest,
        "resource_snapshot_digest": resources.snapshot_digest,
        "atomic_return_schema_digest": return_schema.schema_digest,
        "formation_input_count": len(chain.formation_input_manifest),
        "probe_slot_count": len(chain.probe_slots),
        "planned_field_call_count": contract.total_field_call_count,
        "planned_field_steps": contract.maximum_total_field_steps,
        "free_memory_bytes": resources.free_memory_bytes,
        "minimum_free_memory_bytes": contract.minimum_free_memory_bytes,
        "checks": checks,
        "synthetic_preflight_passed": passed,
        "real_resource_snapshot_required_later": True,
        "real_runner_implemented": False,
        "owner_authorization_present": False,
        "execution_permitted": False,
        "field_execution_performed": False,
        "observed_result_present": False,
        "persistence_performed": False,
        "claims_permitted": False,
        "decision": (
            "SYNTHETIC_FRESH_CHAIN_PREFLIGHT_PASSED_REAL_RUNNER_AND_"
            "AUTHORIZATION_ABSENT"
            if passed
            else "SYNTHETIC_FRESH_CHAIN_PREFLIGHT_FAILED_CLOSED"
        ),
        "reason": (
            "typed-inputs-slots-order-return-schema-and-synthetic-resources-pass;"
            "real-resource-snapshot-runner-and-owner-authorization-still-absent"
            if passed
            else "one-or-more-synthetic-input-resource-order-or-return-gates-failed"
        ),
    }
    return E1FormationS1FTSyntheticFreshChainPreflight(
        **values,
        preflight_digest=_digest(values),
    )
