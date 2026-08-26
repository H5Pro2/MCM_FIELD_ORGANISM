"""Private S1-EB28 static canonical dataflow contract; no object creation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import hashlib
import inspect
from pathlib import Path

from .e1_confirmation_canonical_formation_adapter import (
    E1ConfirmationCanonicalFormationProduction,
)
from .e1_confirmation_canonical_probe_handoff import (
    E1ConfirmationCanonicalProbeHandoff,
)
from .e1_confirmation_canonical_report_handoff import (
    E1ConfirmationCanonicalReportHandoff,
)
from .e1_confirmation_canonical_result_handoff import (
    E1ConfirmationCanonicalResultHandoff,
)
from .e1_confirmation_canonical_worker_binding import (
    E1ConfirmationCanonicalWorkerBinding,
)
from .e1_confirmation_result_core import E1ConfirmationChainResult
from .e1_confirmation_seven_arm_probe import E1ConfirmationProbeResult
from .e1_refined_formation_runner import _digest


class E1ConfirmationCanonicalDataflowContractError(ValueError):
    """Raised when an S1-EB28 type, digest edge, or gate changed."""


S1_EB27_BINDING_DIGEST = (
    "088c05540d90c1a5e4a8e685310b26a6ba61fb472dceb3b5e02b521d381ba81e"
)
S1_EB27_BINDING_SHA256 = (
    "43776f29f2250180000f4407ea8365ab192b8d8d77853ef6375dbd596967a63f"
)
S1_EB28_REFINEMENTS = ("r2", "r4", "r8")
S1_EB28_TYPES = (
    E1ConfirmationCanonicalFormationProduction,
    E1ConfirmationCanonicalProbeHandoff,
    E1ConfirmationProbeResult,
    E1ConfirmationCanonicalResultHandoff,
    E1ConfirmationChainResult,
    E1ConfirmationCanonicalReportHandoff,
)
S1_EB28_TYPE_INVENTORY = (
    (
        "formation",
        "E1ConfirmationCanonicalFormationProduction",
        "production_digest",
        "refinements",
    ),
    (
        "probe_handoff",
        "E1ConfirmationCanonicalProbeHandoff",
        "handoff_digest",
        "refinements",
    ),
    (
        "probe_result",
        "E1ConfirmationProbeResult",
        "result_digest",
        "refinement_id",
    ),
    (
        "result_handoff",
        "E1ConfirmationCanonicalResultHandoff",
        "handoff_digest",
        "refinements",
    ),
    (
        "chain_result",
        "E1ConfirmationChainResult",
        "result_digest",
        "refinements",
    ),
    (
        "report_handoff",
        "E1ConfirmationCanonicalReportHandoff",
        "handoff_digest",
        "refinement_result_digests",
    ),
)
S1_EB28_DIGEST_EDGES = (
    ("formation.production_digest", "probe_handoff.formation_production_digest"),
    ("formation.refinements[*].result_digest", "probe_handoff.formation_result_digests"),
    ("formation.production_digest", "result_handoff.formation_production_digest"),
    ("probe_handoff.handoff_digest", "result_handoff.probe_handoff_digest"),
    ("probe_results[*].result_digest", "result_handoff.probe_result_digests"),
    ("probe_results[*].field_digests", "result_handoff.probe_field_digests"),
    ("result_handoff.handoff_digest", "report_handoff.result_handoff_digest"),
    ("chain_result.result_digest", "report_handoff.result_digest"),
)
S1_EB28_PARAMETER_EDGES = (
    ("formation", "probe_handoff.formation"),
    ("formation", "probe_r2_r4_r8.formation"),
    ("probe_handoff", "probe_r2_r4_r8.handoff"),
    ("formation", "result_handoff.formation"),
    ("probe_handoff", "result_handoff.probe_handoff"),
    ("probe_results", "result_handoff.probes"),
    ("formation", "result_composition.formation"),
    ("probe_handoff", "result_composition.probe_handoff"),
    ("result_handoff", "result_composition.result_handoff"),
    ("probe_results", "result_composition.probes"),
    ("result_handoff", "report_handoff.result_handoff"),
    ("chain_result", "report_handoff.result"),
)
S1_EB28_CLOSED_GATES = (
    ("probe_handoff", "probe_execution_permitted", False),
    ("probe_handoff", "decision_permitted", False),
    ("probe_handoff", "persistence_permitted", False),
    ("probe_handoff", "claims_permitted", False),
    ("result_handoff", "result_composition_permitted", False),
    ("result_handoff", "decision_permitted", False),
    ("result_handoff", "persistence_permitted", False),
    ("result_handoff", "claims_permitted", False),
    ("report_handoff", "execution_permitted", False),
    ("report_handoff", "persistence_permitted", False),
    ("report_handoff", "retry_permitted", False),
    ("report_handoff", "claims_permitted", False),
)
S1_EB28_EXTERNAL_TYPE_DIGESTS = (
    (
        "probe_result",
        "0cc32020743830b3daad48716d33ab8aedd386378f03f867e73628a65e372df1",
    ),
    (
        "chain_result",
        "614c8ee2e2a6a3e84314b073a0af0ea641e66b1ca6373f7526799fd26a2a08a6",
    ),
)


def _source_digest(type_) -> str:
    path = Path(inspect.getsourcefile(type_) or "")
    if not path.is_file():
        raise E1ConfirmationCanonicalDataflowContractError(
            "S1-EB28 cannot resolve an artifact source"
        )
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def current_s1_eb28_type_inventory():
    return tuple(
        (
            role,
            type_.__name__,
            digest_field,
            refinement_field,
        )
        for (role, _, digest_field, refinement_field), type_ in zip(
            S1_EB28_TYPE_INVENTORY, S1_EB28_TYPES, strict=True
        )
    )


def current_s1_eb28_type_fields():
    return tuple(
        (role, tuple(item.name for item in fields(type_)))
        for (role, *_), type_ in zip(
            S1_EB28_TYPE_INVENTORY, S1_EB28_TYPES, strict=True
        )
    )


def current_s1_eb28_external_type_digests():
    by_role = dict(zip((item[0] for item in S1_EB28_TYPE_INVENTORY), S1_EB28_TYPES))
    return tuple(
        (role, _source_digest(by_role[role]))
        for role, _ in S1_EB28_EXTERNAL_TYPE_DIGESTS
    )


def _all_referenced_fields_exist() -> bool:
    by_role = {
        role: {item.name for item in fields(type_)}
        for (role, *_), type_ in zip(
            S1_EB28_TYPE_INVENTORY, S1_EB28_TYPES, strict=True
        )
    }
    required = {
        "formation": {"production_digest", "refinements"},
        "probe_handoff": {
            "formation_production_digest",
            "formation_result_digests",
            "handoff_digest",
        },
        "probe_result": {"result_digest", "field_digests", "refinement_id"},
        "result_handoff": {
            "formation_production_digest",
            "probe_handoff_digest",
            "probe_result_digests",
            "probe_field_digests",
            "handoff_digest",
        },
        "chain_result": {"result_digest", "refinements"},
        "report_handoff": {
            "result_handoff_digest",
            "result_digest",
            "handoff_digest",
        },
    }
    return all(required[role] <= by_role[role] for role in required)


@dataclass(frozen=True, slots=True)
class E1ConfirmationCanonicalDataflowContract:
    contract_id: str
    function_binding_digest: str
    function_binding_sha256: str
    type_inventory: tuple[tuple[str, str, str, str], ...]
    type_fields: tuple[tuple[str, tuple[str, ...]], ...]
    external_type_digests: tuple[tuple[str, str], ...]
    parameter_edges: tuple[tuple[str, str], ...]
    digest_edges: tuple[tuple[str, str], ...]
    closed_gates: tuple[tuple[str, str, bool], ...]
    refinements: tuple[str, ...]
    probe_result_count: int
    type_fields_complete: bool
    digest_continuity_bound: bool
    closed_gates_bound: bool
    objects_constructed: bool
    canonical_calls_performed: bool
    marker_creation_permitted: bool
    canonical_execution_permitted: bool
    canonical_persistence_permitted: bool
    claims_permitted: bool
    contract_status: str
    contract_digest: str

    def __post_init__(self) -> None:
        if (
            self.contract_id != "e1.confirmation-dataflow.s1eb28.v1"
            or self.function_binding_digest != S1_EB27_BINDING_DIGEST
            or self.function_binding_sha256 != S1_EB27_BINDING_SHA256
            or self.type_inventory != S1_EB28_TYPE_INVENTORY
            or self.type_inventory != current_s1_eb28_type_inventory()
            or self.type_fields != current_s1_eb28_type_fields()
            or self.external_type_digests != S1_EB28_EXTERNAL_TYPE_DIGESTS
            or self.external_type_digests
            != current_s1_eb28_external_type_digests()
            or self.parameter_edges != S1_EB28_PARAMETER_EDGES
            or self.digest_edges != S1_EB28_DIGEST_EDGES
            or self.closed_gates != S1_EB28_CLOSED_GATES
            or self.refinements != S1_EB28_REFINEMENTS
            or self.probe_result_count != 3
            or self.type_fields_complete is not True
            or self.digest_continuity_bound is not True
            or self.closed_gates_bound is not True
            or self.objects_constructed is not False
            or self.canonical_calls_performed is not False
            or self.marker_creation_permitted is not False
            or self.canonical_execution_permitted is not False
            or self.canonical_persistence_permitted is not False
            or self.claims_permitted is not False
            or self.contract_status != "CANONICAL_DATAFLOW_BOUND_WITHOUT_OBJECTS"
        ):
            raise E1ConfirmationCanonicalDataflowContractError(
                "S1-EB28 canonical dataflow contract changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "contract_digest"
        }
        if self.contract_digest != _digest(payload):
            raise E1ConfirmationCanonicalDataflowContractError(
                "S1-EB28 contract digest does not match its payload"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


def prepare_e1_confirmation_canonical_dataflow_contract(
    binding: E1ConfirmationCanonicalWorkerBinding,
) -> E1ConfirmationCanonicalDataflowContract:
    """Bind type and digest edges without creating any canonical artifact."""

    if not isinstance(binding, E1ConfirmationCanonicalWorkerBinding) or (
        binding.binding_digest != S1_EB27_BINDING_DIGEST
        or binding.canonical_calls_performed is not False
        or binding.canonical_execution_permitted is not False
    ):
        raise E1ConfirmationCanonicalDataflowContractError(
            "S1-EB28 requires the unchanged closed S1-EB27 binding"
        )
    binding.__post_init__()
    binding_path = Path(__file__).with_name(
        "e1_confirmation_canonical_worker_binding.py"
    )
    normalized = binding_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    if hashlib.sha256(normalized.encode("utf-8")).hexdigest() != (
        S1_EB27_BINDING_SHA256
    ):
        raise E1ConfirmationCanonicalDataflowContractError(
            "S1-EB28 S1-EB27 binding implementation changed"
        )
    if not _all_referenced_fields_exist():
        raise E1ConfirmationCanonicalDataflowContractError(
            "S1-EB28 required artifact fields are incomplete"
        )
    values = {
        "contract_id": "e1.confirmation-dataflow.s1eb28.v1",
        "function_binding_digest": binding.binding_digest,
        "function_binding_sha256": S1_EB27_BINDING_SHA256,
        "type_inventory": current_s1_eb28_type_inventory(),
        "type_fields": current_s1_eb28_type_fields(),
        "external_type_digests": current_s1_eb28_external_type_digests(),
        "parameter_edges": S1_EB28_PARAMETER_EDGES,
        "digest_edges": S1_EB28_DIGEST_EDGES,
        "closed_gates": S1_EB28_CLOSED_GATES,
        "refinements": S1_EB28_REFINEMENTS,
        "probe_result_count": 3,
        "type_fields_complete": True,
        "digest_continuity_bound": True,
        "closed_gates_bound": True,
        "objects_constructed": False,
        "canonical_calls_performed": False,
        "marker_creation_permitted": False,
        "canonical_execution_permitted": False,
        "canonical_persistence_permitted": False,
        "claims_permitted": False,
        "contract_status": "CANONICAL_DATAFLOW_BOUND_WITHOUT_OBJECTS",
    }
    return E1ConfirmationCanonicalDataflowContract(
        **values,
        contract_digest=_digest(values),
    )
