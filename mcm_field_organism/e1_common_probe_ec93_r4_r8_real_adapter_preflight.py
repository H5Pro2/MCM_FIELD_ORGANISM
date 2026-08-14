"""S1-EC93 r4/r8 real-adapter compatibility and closed run preflight."""

from __future__ import annotations

from dataclasses import dataclass
import inspect

from .e1_common_probe_ec89_r4_r8_object_handoffs import (
    E1CommonProbeEC89R4R8ObjectHandoffSet,
    E1CommonProbeEC89RefinementObjectHandoff,
)
from .e1_common_probe_ec91_refinement_receipts_converters import (
    E1CommonProbeEC91FormationReceipt,
    E1CommonProbeEC91ProbeReceipt,
    E1CommonProbeEC91SyntheticFixtureResult,
    convert_e1_common_probe_ec91_formation_output,
    convert_e1_common_probe_ec91_probe_output,
)
from .e1_common_probe_ec92_synthetic_r4_r8_coordinator import (
    E1CommonProbeEC92SyntheticCoordinatorResult,
)
from .e1_common_probe_real_binding_contract import E1CommonProbeRealSlotBinding
from .e1_common_probe_real_wrappers import (
    E1CommonProbeFreshField,
    E1CommonProbeResolvedSlot,
    build_e1_common_probe_fresh_field,
    run_e1_common_probe_real_formation_wrapper,
    run_e1_common_probe_real_probe_wrapper,
)
from .e1_local_edge_plasticity import E1LocalEdgePlasticityState
from .e1_refined_formation_runner import _digest
from .shared_mcm_field import SharedMCMField


class E1CommonProbeEC93R4R8RealAdapterPreflightError(ValueError):
    """Raised when EC93 changes adapter order or opens the real run."""


S1_EC93_PREFLIGHT_ID = "e1.common-probe-r4-r8-real-adapter-preflight.s1ec93.v1"
S1_EC93_EC89_RESULT_DIGEST = (
    "eadaee38d591f4ad36acbf00aec3681cd9da0069173a62055ca8ea70a34ffae9"
)
S1_EC93_EC91_FIXTURE_DIGEST = (
    "e194525320e5b2e73667f9cb98e5523b80171d8023fe739c3d96107cba3c0dc7"
)
S1_EC93_EC92_RESULT_DIGEST = (
    "069c94d75a4ef2d8652abe09ed396b237e728401840db5dc1a2ac744410fcc9e"
)
S1_EC93_ADAPTER_NAMES = (
    "run_e1_common_probe_ec93_formation_receipt_adapter",
    "build_e1_common_probe_ec93_fresh_field_adapter",
    "run_e1_common_probe_ec93_probe_receipt_adapter",
)
S1_EC93_CHECK_NAMES = (
    "formation-signature-carries-refinement-handoff",
    "fresh-field-signature-remains-narrow",
    "probe-signature-carries-refinement-handoff",
    "formation-wrapper-precedes-ec91-converter",
    "probe-wrapper-precedes-ec91-converter",
    "formation-refinement-is-checked-by-ec91",
    "probe-refinement-and-state-route-are-checked-by-ec91",
    "adapter-source-has-no-r2-step-literal",
    "adapter-source-has-no-write-path",
    "synthetic-r4-r8-receipts-complete",
    "synthetic-coordinator-routes-fields-scalars-complete",
)


def run_e1_common_probe_ec93_formation_receipt_adapter(
    handoff: E1CommonProbeEC89RefinementObjectHandoff,
    resolved: E1CommonProbeResolvedSlot,
    initial_field: SharedMCMField,
    initial_state: E1LocalEdgePlasticityState,
) -> E1CommonProbeEC91FormationReceipt:
    """Run one EC54 formation wrapper, then the bound EC91 converter."""

    if resolved not in handoff.formation_slots:
        raise E1CommonProbeEC93R4R8RealAdapterPreflightError(
            "S1-EC93 formation slot is outside its handoff"
        )
    output = run_e1_common_probe_real_formation_wrapper(
        resolved, initial_field, initial_state
    )
    return convert_e1_common_probe_ec91_formation_output(
        handoff, resolved, output, execution_mode="real-wrapper"
    )


def build_e1_common_probe_ec93_fresh_field_adapter(
    binding: E1CommonProbeRealSlotBinding,
    initial_field: SharedMCMField,
) -> E1CommonProbeFreshField:
    """Create one object-separated EC54 field without advancing it."""

    return build_e1_common_probe_fresh_field(binding, initial_field)


def run_e1_common_probe_ec93_probe_receipt_adapter(
    handoff: E1CommonProbeEC89RefinementObjectHandoff,
    resolved: E1CommonProbeResolvedSlot,
    fresh: E1CommonProbeFreshField,
    formation: E1CommonProbeEC91FormationReceipt | None,
) -> E1CommonProbeEC91ProbeReceipt:
    """Run one EC54 probe wrapper, then the bound EC91 converter."""

    if resolved not in handoff.resolved_slots:
        raise E1CommonProbeEC93R4R8RealAdapterPreflightError(
            "S1-EC93 probe slot is outside its handoff"
        )
    frozen_state = None if formation is None else formation.output_state
    output = run_e1_common_probe_real_probe_wrapper(resolved, fresh, frozen_state)
    return convert_e1_common_probe_ec91_probe_output(
        handoff, resolved, output, formation, execution_mode="real-wrapper"
    )


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC93R4R8RealAdapterPreflight:
    preflight_id: str
    source_ec89_result_digest: str
    source_ec91_fixture_digest: str
    source_ec92_result_digest: str
    adapter_names: tuple[str, ...]
    checks: tuple[tuple[str, bool], ...]
    refinement_ids: tuple[str, ...]
    formation_steps: int
    probe_steps: int
    maximum_total_field_steps: int
    minimum_free_memory_bytes: int
    minimum_free_disk_bytes: int
    wrapper_then_converter_order_exact: bool
    synthetic_compatibility_complete: bool
    exactly_once_required: bool
    atomic_scalar_return_required: bool
    new_owner_authorization_required: bool
    owner_authorization_present: bool
    real_execution_permitted: bool
    retry_permitted: bool
    posthoc_parameter_change_permitted: bool
    persistence_permitted: bool
    ec46_decision_permitted: bool
    claims_permitted: bool
    decision: str
    reason: str
    preflight_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "preflight_digest"
        }
        if (
            self.preflight_id != S1_EC93_PREFLIGHT_ID
            or self.source_ec89_result_digest != S1_EC93_EC89_RESULT_DIGEST
            or self.source_ec91_fixture_digest != S1_EC93_EC91_FIXTURE_DIGEST
            or self.source_ec92_result_digest != S1_EC93_EC92_RESULT_DIGEST
            or self.adapter_names != S1_EC93_ADAPTER_NAMES
            or tuple(name for name, _ in self.checks) != S1_EC93_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or self.refinement_ids != ("r4", "r8")
            or (self.formation_steps, self.probe_steps, self.maximum_total_field_steps)
            != (9648, 9600, 19248)
            or self.minimum_free_memory_bytes != 4 * 1024**3
            or self.minimum_free_disk_bytes != 1024**3
            or any(
                value is not True
                for value in (
                    self.wrapper_then_converter_order_exact,
                    self.synthetic_compatibility_complete,
                    self.exactly_once_required,
                    self.atomic_scalar_return_required,
                    self.new_owner_authorization_required,
                )
            )
            or any(
                value is not False
                for value in (
                    self.owner_authorization_present,
                    self.real_execution_permitted,
                    self.retry_permitted,
                    self.posthoc_parameter_change_permitted,
                    self.persistence_permitted,
                    self.ec46_decision_permitted,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "R4_R8_REAL_ADAPTERS_COMPATIBLE_PREFLIGHT_CLOSED_AUTHORIZATION_REQUIRED"
            or not self.reason
            or self.preflight_digest != _digest(payload)
        ):
            raise E1CommonProbeEC93R4R8RealAdapterPreflightError(
                "S1-EC93 preflight changed or opened real execution"
            )


def build_e1_common_probe_ec93_r4_r8_real_adapter_preflight(
    handoffs: E1CommonProbeEC89R4R8ObjectHandoffSet,
    fixture: E1CommonProbeEC91SyntheticFixtureResult,
    coordinator: E1CommonProbeEC92SyntheticCoordinatorResult,
) -> E1CommonProbeEC93R4R8RealAdapterPreflight:
    """Audit adapter compatibility and bind a closed exactly-once request."""

    if (
        not isinstance(handoffs, E1CommonProbeEC89R4R8ObjectHandoffSet)
        or handoffs.result_digest != S1_EC93_EC89_RESULT_DIGEST
        or not isinstance(fixture, E1CommonProbeEC91SyntheticFixtureResult)
        or fixture.result_digest != S1_EC93_EC91_FIXTURE_DIGEST
        or not isinstance(coordinator, E1CommonProbeEC92SyntheticCoordinatorResult)
        or coordinator.result_digest != S1_EC93_EC92_RESULT_DIGEST
    ):
        raise E1CommonProbeEC93R4R8RealAdapterPreflightError(
            "S1-EC93 requires exact EC89, EC91, and EC92 inputs"
        )
    handoffs.__post_init__()
    fixture.__post_init__()
    coordinator.__post_init__()

    formation_source = inspect.getsource(
        run_e1_common_probe_ec93_formation_receipt_adapter
    )
    fresh_source = inspect.getsource(
        build_e1_common_probe_ec93_fresh_field_adapter
    )
    probe_source = inspect.getsource(
        run_e1_common_probe_ec93_probe_receipt_adapter
    )
    all_source = formation_source + fresh_source + probe_source
    formation_order = formation_source.find(
        "run_e1_common_probe_real_formation_wrapper("
    ) < formation_source.find("convert_e1_common_probe_ec91_formation_output(")
    probe_order = probe_source.find(
        "run_e1_common_probe_real_probe_wrapper("
    ) < probe_source.find("convert_e1_common_probe_ec91_probe_output(")
    checks = (
        (
            S1_EC93_CHECK_NAMES[0],
            tuple(
                inspect.signature(
                    run_e1_common_probe_ec93_formation_receipt_adapter
                ).parameters
            )
            == ("handoff", "resolved", "initial_field", "initial_state"),
        ),
        (
            S1_EC93_CHECK_NAMES[1],
            tuple(
                inspect.signature(
                    build_e1_common_probe_ec93_fresh_field_adapter
                ).parameters
            )
            == ("binding", "initial_field"),
        ),
        (
            S1_EC93_CHECK_NAMES[2],
            tuple(
                inspect.signature(
                    run_e1_common_probe_ec93_probe_receipt_adapter
                ).parameters
            )
            == ("handoff", "resolved", "fresh", "formation"),
        ),
        (S1_EC93_CHECK_NAMES[3], formation_order),
        (S1_EC93_CHECK_NAMES[4], probe_order),
        (
            S1_EC93_CHECK_NAMES[5],
            "handoff, resolved, output" in formation_source
            and 'execution_mode="real-wrapper"' in formation_source,
        ),
        (
            S1_EC93_CHECK_NAMES[6],
            "handoff, resolved, output, formation" in probe_source
            and 'execution_mode="real-wrapper"' in probe_source,
        ),
        (
            S1_EC93_CHECK_NAMES[7],
            all(token not in all_source for token in ("402", "200")),
        ),
        (
            S1_EC93_CHECK_NAMES[8],
            all(token not in all_source for token in ("write_text", "write_bytes", "open(")),
        ),
        (
            S1_EC93_CHECK_NAMES[9],
            fixture.refinement_ids == ("r4", "r8")
            and all(len(items) == 4 for items in fixture.formations)
            and all(len(items) == 8 for items in fixture.probes),
        ),
        (
            S1_EC93_CHECK_NAMES[10],
            coordinator.all_routes_exact
            and coordinator.all_fresh_fields_identical_and_object_separate
            and coordinator.all_six_contrasts_exact
            and coordinator.atomic_scalar_return,
        ),
    )
    values = {
        "preflight_id": S1_EC93_PREFLIGHT_ID,
        "source_ec89_result_digest": handoffs.result_digest,
        "source_ec91_fixture_digest": fixture.result_digest,
        "source_ec92_result_digest": coordinator.result_digest,
        "adapter_names": S1_EC93_ADAPTER_NAMES,
        "checks": checks,
        "refinement_ids": handoffs.refinement_ids,
        "formation_steps": 9648,
        "probe_steps": 9600,
        "maximum_total_field_steps": handoffs.combined_maximum_total_steps,
        "minimum_free_memory_bytes": 4 * 1024**3,
        "minimum_free_disk_bytes": 1024**3,
        "wrapper_then_converter_order_exact": formation_order and probe_order,
        "synthetic_compatibility_complete": all(value for _, value in checks),
        "exactly_once_required": True,
        "atomic_scalar_return_required": True,
        "new_owner_authorization_required": True,
        "owner_authorization_present": False,
        "real_execution_permitted": False,
        "retry_permitted": False,
        "posthoc_parameter_change_permitted": False,
        "persistence_permitted": False,
        "ec46_decision_permitted": False,
        "claims_permitted": False,
        "decision": (
            "R4_R8_REAL_ADAPTERS_COMPATIBLE_PREFLIGHT_CLOSED_AUTHORIZATION_REQUIRED"
        ),
        "reason": (
            "ec54-wrapper-order-and-ec91-converters-compatible;ec92-synthetic-"
            "routes-complete;real-19248-step-run-requires-new-owner-authorization"
        ),
    }
    return E1CommonProbeEC93R4R8RealAdapterPreflight(
        **values, preflight_digest=_digest(values)
    )
