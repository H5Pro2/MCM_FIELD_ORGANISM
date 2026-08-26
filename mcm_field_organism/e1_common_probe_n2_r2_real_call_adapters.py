"""S1-EC65 private call adapters from EC54 wrappers to EC64 converters."""

from __future__ import annotations

from dataclasses import dataclass
import inspect

from .e1_common_probe_n2_r2_positive_step_receipt_contract import (
    E1PositiveStepFormationReceipt,
    E1PositiveStepProbeReceipt,
)
from .e1_common_probe_n2_r2_real_output_converters import (
    convert_e1_common_probe_real_formation_output,
    convert_e1_common_probe_real_probe_output,
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


class E1CommonProbeN2R2RealCallAdapterError(ValueError):
    """Raised when EC65 call ordering or static release scope changes."""


S1_EC65_AUDIT_ID = "e1.common-probe-n2-r2-real-call-adapters.s1ec65.v1"
S1_EC65_EC64_AUDIT_DIGEST = (
    "390134f086ee6d891bf43f6997c0b84269acdbf67229bd364a435edaeee228e2"
)
S1_EC65_EC64_FIXTURE_DIGEST = (
    "dcda102b56c9e0ceddde6a6fc72418b86639f7113a8785d49e6dbc7c836e55b9"
)


def run_e1_common_probe_real_formation_receipt_adapter(
    resolved: E1CommonProbeResolvedSlot,
    initial_field: SharedMCMField,
    initial_state: E1LocalEdgePlasticityState,
) -> E1PositiveStepFormationReceipt:
    """Run one EC54 formation wrapper, then convert its output losslessly."""

    output = run_e1_common_probe_real_formation_wrapper(
        resolved, initial_field, initial_state
    )
    return convert_e1_common_probe_real_formation_output(resolved, output)


def build_e1_common_probe_real_fresh_field_adapter(
    binding: E1CommonProbeRealSlotBinding,
    initial_field: SharedMCMField,
) -> E1CommonProbeFreshField:
    """Delegate one object-separated fresh field to the EC54 wrapper."""

    return build_e1_common_probe_fresh_field(binding, initial_field)


def run_e1_common_probe_real_probe_receipt_adapter(
    resolved: E1CommonProbeResolvedSlot,
    fresh: E1CommonProbeFreshField,
    formation: E1PositiveStepFormationReceipt | None,
) -> E1PositiveStepProbeReceipt:
    """Run one EC54 probe wrapper, then convert its output losslessly."""

    frozen_state = None if formation is None else formation.output_state
    output = run_e1_common_probe_real_probe_wrapper(
        resolved, fresh, frozen_state
    )
    return convert_e1_common_probe_real_probe_output(
        resolved, output, formation
    )


@dataclass(frozen=True, slots=True)
class E1CommonProbeN2R2RealCallAdapterAudit:
    audit_id: str
    source_ec64_audit_digest: str
    source_ec64_fixture_digest: str
    adapter_names: tuple[str, ...]
    checks: tuple[tuple[str, bool], ...]
    wrapper_then_converter_order_exact: bool
    coordinator_binding_implementation_permitted: bool
    adapter_execution_permitted: bool
    persistence_permitted: bool
    research_decision_permitted: bool
    memory_claim_permitted: bool
    decision: str
    audit_digest: str

    def __post_init__(self) -> None:
        if (
            self.audit_id != S1_EC65_AUDIT_ID
            or self.source_ec64_audit_digest != S1_EC65_EC64_AUDIT_DIGEST
            or self.source_ec64_fixture_digest != S1_EC65_EC64_FIXTURE_DIGEST
            or self.adapter_names != (
                "run_e1_common_probe_real_formation_receipt_adapter",
                "build_e1_common_probe_real_fresh_field_adapter",
                "run_e1_common_probe_real_probe_receipt_adapter",
            )
            or any(value is not True for _, value in self.checks)
            or self.wrapper_then_converter_order_exact is not True
            or self.coordinator_binding_implementation_permitted is not True
            or any(value is not False for value in (
                self.adapter_execution_permitted,
                self.persistence_permitted,
                self.research_decision_permitted,
                self.memory_claim_permitted,
            ))
            or self.decision != "REAL_CALL_ADAPTERS_IMPLEMENTED_STATICALLY_NOT_RELEASED"
        ):
            raise E1CommonProbeN2R2RealCallAdapterError(
                "S1-EC65 audit changed or released adapter execution"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "audit_digest"
        }
        if self.audit_digest != _digest(payload):
            raise E1CommonProbeN2R2RealCallAdapterError(
                "S1-EC65 audit digest changed"
            )


def audit_e1_common_probe_n2_r2_real_call_adapters(
) -> E1CommonProbeN2R2RealCallAdapterAudit:
    """Audit adapter source and signatures without invoking any adapter."""

    formation_source = inspect.getsource(
        run_e1_common_probe_real_formation_receipt_adapter
    )
    fresh_source = inspect.getsource(
        build_e1_common_probe_real_fresh_field_adapter
    )
    probe_source = inspect.getsource(
        run_e1_common_probe_real_probe_receipt_adapter
    )
    formation_order = formation_source.find(
        "run_e1_common_probe_real_formation_wrapper("
    ) < formation_source.find("convert_e1_common_probe_real_formation_output(")
    probe_order = probe_source.find(
        "run_e1_common_probe_real_probe_wrapper("
    ) < probe_source.find("convert_e1_common_probe_real_probe_output(")
    checks = (
        ("formation-adapter-signature-exact", tuple(inspect.signature(run_e1_common_probe_real_formation_receipt_adapter).parameters) == ("resolved", "initial_field", "initial_state")),
        ("fresh-adapter-signature-exact", tuple(inspect.signature(build_e1_common_probe_real_fresh_field_adapter).parameters) == ("binding", "initial_field")),
        ("probe-adapter-signature-exact", tuple(inspect.signature(run_e1_common_probe_real_probe_receipt_adapter).parameters) == ("resolved", "fresh", "formation")),
        ("formation-wrapper-precedes-converter", formation_order),
        ("fresh-adapter-delegates-exactly-one-wrapper", fresh_source.count("build_e1_common_probe_fresh_field(") == 1),
        ("probe-wrapper-precedes-converter", probe_order),
        ("probe-state-comes-only-from-formation-receipt", "formation.output_state" in probe_source and "frozen_state = None if formation is None" in probe_source),
        ("all-adapters-have-no-write-path", all(token not in source for source in (formation_source, fresh_source, probe_source) for token in ("write_text", "write_bytes", "open("))),
    )
    values = {
        "audit_id": S1_EC65_AUDIT_ID,
        "source_ec64_audit_digest": S1_EC65_EC64_AUDIT_DIGEST,
        "source_ec64_fixture_digest": S1_EC65_EC64_FIXTURE_DIGEST,
        "adapter_names": (
            "run_e1_common_probe_real_formation_receipt_adapter",
            "build_e1_common_probe_real_fresh_field_adapter",
            "run_e1_common_probe_real_probe_receipt_adapter",
        ),
        "checks": checks,
        "wrapper_then_converter_order_exact": formation_order and probe_order,
        "coordinator_binding_implementation_permitted": True,
        "adapter_execution_permitted": False,
        "persistence_permitted": False,
        "research_decision_permitted": False,
        "memory_claim_permitted": False,
        "decision": "REAL_CALL_ADAPTERS_IMPLEMENTED_STATICALLY_NOT_RELEASED",
    }
    return E1CommonProbeN2R2RealCallAdapterAudit(
        **values,
        audit_digest=_digest(values),
    )
