"""Private S1-EB27 static binding of canonical functions to worker roles."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import inspect
from pathlib import Path

from .e1_confirmation_canonical_formation_adapter import (
    produce_e1_confirmation_canonical_formation,
)
from .e1_confirmation_canonical_probe_adapter import (
    run_e1_confirmation_canonical_seven_arm_probe,
)
from .e1_confirmation_canonical_probe_handoff import (
    prepare_e1_confirmation_canonical_probe_handoff,
)
from .e1_confirmation_canonical_report_handoff import (
    prepare_e1_confirmation_canonical_report_handoff,
)
from .e1_confirmation_canonical_result_compositor import (
    compose_e1_confirmation_canonical_result,
)
from .e1_confirmation_canonical_result_handoff import (
    prepare_e1_confirmation_canonical_result_handoff,
)
from .e1_confirmation_released_worker_audit import (
    E1ConfirmationReleasedWorkerAudit,
)
from .e1_refined_formation_runner import _digest


class E1ConfirmationCanonicalWorkerBindingError(ValueError):
    """Raised when an S1-EB27 function identity or static gate changed."""


S1_EB25_AUDIT_DIGEST = (
    "90fc412b115196b85f17fda24446308dbdb2752ed920c3c990c926dc635ed57d"
)
S1_EB26_WORKER_SHA256 = (
    "08fba35a409368c7c174b687457f2c86df074ef33eb0dc352f1a1c0db4952d75"
)
S1_EB27_REFINEMENTS = ("r2", "r4", "r8")
S1_EB27_FUNCTION_INVENTORY = (
    (
        "formation",
        "mcm_field_organism.e1_confirmation_canonical_formation_adapter",
        "produce_e1_confirmation_canonical_formation",
        ("binding", "chain_contract"),
        "E1ConfirmationCanonicalFormationProduction",
        "0cdadade84639e29c8fc8affa1601c5d8ab034f5238900e461dd971914b4ffe6",
    ),
    (
        "probe_handoff",
        "mcm_field_organism.e1_confirmation_canonical_probe_handoff",
        "prepare_e1_confirmation_canonical_probe_handoff",
        ("binding", "chain_contract", "formation"),
        "E1ConfirmationCanonicalProbeHandoff",
        "7ba9a880ff8e1e5530cf47fa5ac11b92a1ec17e7beac48813b38d56e4fdfe1e0",
    ),
    (
        "probe_r2_r4_r8",
        "mcm_field_organism.e1_confirmation_canonical_probe_adapter",
        "run_e1_confirmation_canonical_seven_arm_probe",
        ("binding", "chain_contract", "formation", "handoff"),
        "tuple[E1ConfirmationProbeResult, ...]",
        "14ca32466f45dea0aafcd9fdb6da76888e0d89c7f49256859f6abb2f907687f9",
    ),
    (
        "result_handoff",
        "mcm_field_organism.e1_confirmation_canonical_result_handoff",
        "prepare_e1_confirmation_canonical_result_handoff",
        ("binding", "chain_contract", "formation", "probe_handoff", "probes"),
        "E1ConfirmationCanonicalResultHandoff",
        "82153cfd9de0cdeecae8cd1c852973c8b5d669aa419ad84110383634e586005c",
    ),
    (
        "result_composition",
        "mcm_field_organism.e1_confirmation_canonical_result_compositor",
        "compose_e1_confirmation_canonical_result",
        (
            "binding",
            "chain_contract",
            "formation",
            "probe_handoff",
            "result_handoff",
            "probes",
        ),
        "E1ConfirmationChainResult",
        "db3e2fe8c43154db142a5882badd801725bd7ff5aa7081da72b042c56db02b2f",
    ),
    (
        "report_handoff",
        "mcm_field_organism.e1_confirmation_canonical_report_handoff",
        "prepare_e1_confirmation_canonical_report_handoff",
        ("binding", "chain_contract", "result_handoff", "result"),
        "E1ConfirmationCanonicalReportHandoff",
        "3e29fc1e968ff24700dc35cc34d2e3a0bf8545c7253c53bd65b4fb8503560faf",
    ),
)
S1_EB27_FUNCTIONS = (
    produce_e1_confirmation_canonical_formation,
    prepare_e1_confirmation_canonical_probe_handoff,
    run_e1_confirmation_canonical_seven_arm_probe,
    prepare_e1_confirmation_canonical_result_handoff,
    compose_e1_confirmation_canonical_result,
    prepare_e1_confirmation_canonical_report_handoff,
)


def _normalized_module_digest(function) -> str:
    path = Path(inspect.getsourcefile(function) or "")
    if not path.is_file():
        raise E1ConfirmationCanonicalWorkerBindingError(
            "S1-EB27 cannot resolve a canonical function source"
        )
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def current_s1_eb27_function_inventory():
    inventory = []
    for role, function in zip(
        (item[0] for item in S1_EB27_FUNCTION_INVENTORY),
        S1_EB27_FUNCTIONS,
        strict=True,
    ):
        signature = inspect.signature(function)
        annotations = inspect.get_annotations(function, eval_str=False)
        inventory.append(
            (
                role,
                function.__module__,
                function.__name__,
                tuple(signature.parameters),
                annotations.get("return", ""),
                _normalized_module_digest(function),
            )
        )
    return tuple(inventory)


@dataclass(frozen=True, slots=True)
class E1ConfirmationCanonicalWorkerBinding:
    binding_id: str
    release_audit_digest: str
    worker_implementation_sha256: str
    function_inventory: tuple[tuple[object, ...], ...]
    refinements: tuple[str, ...]
    dataflow_roles: tuple[str, ...]
    all_functions_resolved: bool
    signatures_bound: bool
    source_digests_bound: bool
    canonical_calls_performed: bool
    marker_creation_permitted: bool
    canonical_execution_permitted: bool
    canonical_persistence_permitted: bool
    claims_permitted: bool
    binding_status: str
    binding_digest: str

    def __post_init__(self) -> None:
        if (
            self.binding_id != "e1.confirmation-worker-binding.s1eb27.v1"
            or self.release_audit_digest != S1_EB25_AUDIT_DIGEST
            or self.worker_implementation_sha256 != S1_EB26_WORKER_SHA256
            or self.function_inventory != S1_EB27_FUNCTION_INVENTORY
            or self.function_inventory != current_s1_eb27_function_inventory()
            or self.refinements != S1_EB27_REFINEMENTS
            or self.dataflow_roles
            != tuple(item[0] for item in S1_EB27_FUNCTION_INVENTORY)
            or self.all_functions_resolved is not True
            or self.signatures_bound is not True
            or self.source_digests_bound is not True
            or self.canonical_calls_performed is not False
            or self.marker_creation_permitted is not False
            or self.canonical_execution_permitted is not False
            or self.canonical_persistence_permitted is not False
            or self.claims_permitted is not False
            or self.binding_status
            != "CANONICAL_FUNCTIONS_BOUND_WITHOUT_INVOCATION"
        ):
            raise E1ConfirmationCanonicalWorkerBindingError(
                "S1-EB27 canonical worker binding changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "binding_digest"
        }
        if self.binding_digest != _digest(payload):
            raise E1ConfirmationCanonicalWorkerBindingError(
                "S1-EB27 binding digest does not match its payload"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


def bind_e1_confirmation_canonical_worker_functions(
    audit: E1ConfirmationReleasedWorkerAudit,
) -> E1ConfirmationCanonicalWorkerBinding:
    """Bind function identities and signatures without invoking any function."""

    if not isinstance(audit, E1ConfirmationReleasedWorkerAudit) or (
        audit.audit_digest != S1_EB25_AUDIT_DIGEST
        or audit.canonical_worker_contract_bound is not True
        or audit.canonical_worker_implemented is not False
        or audit.canonical_execution_permitted is not False
    ):
        raise E1ConfirmationCanonicalWorkerBindingError(
            "S1-EB27 requires the unchanged closed S1-EB25 audit"
        )
    audit.__post_init__()
    worker_path = Path(__file__).with_name("e1_confirmation_canonical_worker.py")
    normalized = worker_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    worker_digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    if worker_digest != S1_EB26_WORKER_SHA256:
        raise E1ConfirmationCanonicalWorkerBindingError(
            "S1-EB27 S1-EB26 worker implementation changed"
        )
    inventory = current_s1_eb27_function_inventory()
    values = {
        "binding_id": "e1.confirmation-worker-binding.s1eb27.v1",
        "release_audit_digest": audit.audit_digest,
        "worker_implementation_sha256": worker_digest,
        "function_inventory": inventory,
        "refinements": S1_EB27_REFINEMENTS,
        "dataflow_roles": tuple(item[0] for item in inventory),
        "all_functions_resolved": True,
        "signatures_bound": True,
        "source_digests_bound": True,
        "canonical_calls_performed": False,
        "marker_creation_permitted": False,
        "canonical_execution_permitted": False,
        "canonical_persistence_permitted": False,
        "claims_permitted": False,
        "binding_status": "CANONICAL_FUNCTIONS_BOUND_WITHOUT_INVOCATION",
    }
    return E1ConfirmationCanonicalWorkerBinding(
        **values,
        binding_digest=_digest(values),
    )
