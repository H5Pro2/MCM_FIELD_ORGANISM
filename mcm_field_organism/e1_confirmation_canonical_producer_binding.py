"""Private S1-EB9 canonical producer binding without chain execution."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

from .e1_av_history_permutation import build_e1_av_history_permutation
from .e1_canonical_confirmation_preflight import (
    prepare_e1_canonical_confirmation_preflight,
)
from .e1_confirmation_chain_contract import (
    E1ConfirmationChainContract,
    prepare_e1_confirmation_chain_contract,
)
from .e1_confirmation_refinement_planner import (
    build_e1_confirmation_refinement_plans,
)
from .e1_confirmation_result_core import E1ConfirmationChainResult
from .e1_frozen_state_transfer_contract import (
    _fixed_probe_sequences,
    _probe_digest,
)
from .e1_local_edge_plasticity import (
    E1_CONTRACT_ID,
    E1LocalEdgePlasticityContract,
    build_neutral_e1_state,
    validate_e1_state_for_layer,
)
from .e1_refined_chain_canonical_producer import (
    _fresh_canonical_field,
    _initial_field_digest,
    _initial_state_digest,
)
from .e1_refined_confirmation_contract import (
    S1_EB_HISTORY_STEP_COUNTS,
    S1_EB_PROBE_STEP_COUNTS,
    S1_EB_REFINEMENTS,
    build_e1_refined_confirmation_contract,
)
from .e1_refined_world_formation_contract import S1_DS_PROBE_DIGEST


class E1ConfirmationCanonicalProducerBindingError(ValueError):
    """Raised when S1-EB9 canonical bindings or gates change."""


S1_EB4_CONTRACT_DIGEST = (
    "acf1136fa9142747729a78dda719bd36086ce2eed9e015dbfbdb58d8302fa650"
)
S1_EB2_PREFLIGHT_DIGEST = (
    "e657636e86cea6eabef638597ed22e3e0bc6894bbdc9f9fb96c001d3c31a0372"
)
S1_EB9_AB_PLAN_DIGEST = (
    "1137a456cfceef385112deb26de662294dea2a4b95a2df0d9dc73ff8620a24e5"
)
S1_EB9_BA_PLAN_DIGEST = (
    "071b4504dc11eadadeb5d5895775dd6bc076d00d937a3d62372fb958b929fc8d"
)
S1_EB9_PROBE_PLAN_DIGEST = (
    "f78b5866d2629cb781f47ad8d622bf4260a67dacc43cfb52366a33d5790ca6b4"
)
S1_EB9_IMPLEMENTATION_FILES = (
    ("formation", "e1_confirmation_formation_runner.py"),
    ("result_core", "e1_confirmation_result_core.py"),
    ("probe", "e1_confirmation_seven_arm_probe.py"),
    ("composition", "e1_confirmation_chain_composition.py"),
    ("synthetic_executor", "e1_confirmation_synthetic_executor.py"),
)
S1_EB9_IMPLEMENTATION_DIGESTS = (
    (
        "formation",
        "7b4fe5870bf8476b1e0367a6f8a7ad52ff026065d9945144aa3f27339663febd",
    ),
    (
        "result_core",
        "614c8ee2e2a6a3e84314b073a0af0ea641e66b1ca6373f7526799fd26a2a08a6",
    ),
    (
        "probe",
        "0cc32020743830b3daad48716d33ab8aedd386378f03f867e73628a65e372df1",
    ),
    (
        "composition",
        "23fff7a5097cad84745aa2697162e6ecfee147bd33baf12f15b75af41c8ae142",
    ),
    (
        "synthetic_executor",
        "d5155dbd0a5fb638b4d3dec092303324b1572b2dbb02cc7a19c990d18f1bb955",
    ),
)


def _digest(value: object) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _normalized_source_digest(name: str) -> str:
    path = Path(__file__).with_name(name)
    if not path.is_file():
        raise E1ConfirmationCanonicalProducerBindingError(
            f"S1-EB9 implementation is missing: {name}"
        )
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def current_s1_eb9_implementation_digests() -> tuple[tuple[str, str], ...]:
    return tuple(
        (role, _normalized_source_digest(name))
        for role, name in S1_EB9_IMPLEMENTATION_FILES
    )


@dataclass(frozen=True, slots=True)
class E1ConfirmationCanonicalProducerBinding:
    binding_id: str
    chain_contract_digest: str
    canonical_preflight_digest: str
    implementation_digests: tuple[tuple[str, str], ...]
    history_ab_digest: str
    history_ba_digest: str
    permutation_digest: str
    probe_digest: str
    ab_plan_digest: str
    ba_plan_digest: str
    probe_plan_digest: str
    geometry_digest: str
    initial_field_digest: str
    initial_state_digest: str
    history_support_count: int
    probe_support_count: int
    history_completion_count: int
    probe_completion_count: int
    field_node_count: int
    edge_count: int
    refinements: tuple[tuple[str, int], ...]
    history_step_counts: tuple[tuple[str, int], ...]
    probe_step_counts: tuple[tuple[str, int], ...]
    producer_entrypoint: str
    canonical_producer_bound: bool
    execution_permitted: bool
    execution_started: bool
    persistence_permitted: bool
    s1_ea6_rerun_permitted: bool
    memory_claim_permitted: bool
    semantic_claim_permitted: bool
    organization_claim_permitted: bool
    topology_claim_permitted: bool
    self_regulation_claim_permitted: bool
    ai_claim_permitted: bool

    def __post_init__(self) -> None:
        if self.binding_id != "e1.confirmation-canonical-producer.s1eb9.v1":
            raise E1ConfirmationCanonicalProducerBindingError(
                "S1-EB9 binding identity changed"
            )
        if (
            self.chain_contract_digest != S1_EB4_CONTRACT_DIGEST
            or self.canonical_preflight_digest != S1_EB2_PREFLIGHT_DIGEST
            or self.implementation_digests != S1_EB9_IMPLEMENTATION_DIGESTS
            or self.implementation_digests
            != current_s1_eb9_implementation_digests()
        ):
            raise E1ConfirmationCanonicalProducerBindingError(
                "S1-EB9 contract, preflight, or implementation binding changed"
            )
        for role in (
            "history_ab_digest",
            "history_ba_digest",
            "permutation_digest",
            "probe_digest",
            "ab_plan_digest",
            "ba_plan_digest",
            "probe_plan_digest",
            "geometry_digest",
            "initial_field_digest",
            "initial_state_digest",
        ):
            value = getattr(self, role)
            if len(value) != 64 or any(
                char not in "0123456789abcdef" for char in value
            ):
                raise E1ConfirmationCanonicalProducerBindingError(
                    f"{role} is not SHA-256"
                )
        if (
            self.probe_digest != S1_DS_PROBE_DIGEST
            or self.ab_plan_digest != S1_EB9_AB_PLAN_DIGEST
            or self.ba_plan_digest != S1_EB9_BA_PLAN_DIGEST
            or self.probe_plan_digest != S1_EB9_PROBE_PLAN_DIGEST
        ):
            raise E1ConfirmationCanonicalProducerBindingError(
                "S1-EB9 source plan binding changed"
            )
        if (
            self.history_support_count,
            self.probe_support_count,
            self.history_completion_count,
            self.probe_completion_count,
            self.field_node_count,
            self.edge_count,
        ) != (220, 110, 200, 100, 84, 145):
            raise E1ConfirmationCanonicalProducerBindingError(
                "S1-EB9 source or geometry inventory changed"
            )
        if (
            self.refinements != S1_EB_REFINEMENTS
            or self.history_step_counts != S1_EB_HISTORY_STEP_COUNTS
            or self.probe_step_counts != S1_EB_PROBE_STEP_COUNTS
            or self.producer_entrypoint
            != "produce_e1_confirmation_canonical_result"
            or self.canonical_producer_bound is not True
        ):
            raise E1ConfirmationCanonicalProducerBindingError(
                "S1-EB9 producer role inventory changed"
            )
        if any(
            value is not False
            for value in (
                self.execution_permitted,
                self.execution_started,
                self.persistence_permitted,
                self.s1_ea6_rerun_permitted,
                self.memory_claim_permitted,
                self.semantic_claim_permitted,
                self.organization_claim_permitted,
                self.topology_claim_permitted,
                self.self_regulation_claim_permitted,
                self.ai_claim_permitted,
            )
        ):
            raise E1ConfirmationCanonicalProducerBindingError(
                "S1-EB9 cannot release execution, persistence, reruns, or claims"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


def prepare_e1_confirmation_canonical_producer_binding(
    report_directory: Path,
    upstream_report_path: Path,
) -> E1ConfirmationCanonicalProducerBinding:
    """Bind canonical inputs without advancing a field or E1 state."""

    contract = prepare_e1_confirmation_chain_contract(
        report_directory,
        upstream_report_path,
    )
    preflight = prepare_e1_canonical_confirmation_preflight(
        report_directory,
        upstream_report_path,
    )
    preflight_digest = _digest(asdict(preflight))
    source = build_e1_av_history_permutation()
    probe = _fixed_probe_sequences()
    corridor = build_e1_refined_confirmation_contract(
        report_directory,
        upstream_report_path,
    )
    ab = build_e1_confirmation_refinement_plans(
        corridor,
        source.history_ab,
        horizon_start_tick=0,
        horizon_end_tick=2_000_000,
        ticks_per_second=1_000_000.0,
    )
    ba = build_e1_confirmation_refinement_plans(
        corridor,
        source.history_ba,
        horizon_start_tick=0,
        horizon_end_tick=2_000_000,
        ticks_per_second=1_000_000.0,
    )
    probe_plans = build_e1_confirmation_refinement_plans(
        corridor,
        probe,
        horizon_start_tick=0,
        horizon_end_tick=1_000_000,
        ticks_per_second=1_000_000.0,
    )
    field = _fresh_canonical_field(source)
    state = build_neutral_e1_state(
        field.layer,
        E1LocalEdgePlasticityContract(
            E1_CONTRACT_ID,
            1.0,
            1.5,
            0.25,
            0.5,
        ),
    )
    validate_e1_state_for_layer(field.layer, state)
    if (
        contract.digest() != S1_EB4_CONTRACT_DIGEST
        or preflight_digest != S1_EB2_PREFLIGHT_DIGEST
        or field.layer.tick != 0
        or field.last_distribution is not None
        or field.substrate is not None
        or any(item.binding != 0.0 for item in state.edge_bindings)
        or _probe_digest(probe) != S1_DS_PROBE_DIGEST
    ):
        raise E1ConfirmationCanonicalProducerBindingError(
            "S1-EB9 canonical preflight input changed"
        )
    return E1ConfirmationCanonicalProducerBinding(
        binding_id="e1.confirmation-canonical-producer.s1eb9.v1",
        chain_contract_digest=contract.digest(),
        canonical_preflight_digest=preflight_digest,
        implementation_digests=current_s1_eb9_implementation_digests(),
        history_ab_digest=source.history_ab_digest,
        history_ba_digest=source.history_ba_digest,
        permutation_digest=source.permutation_digest,
        probe_digest=_probe_digest(probe),
        ab_plan_digest=ab.digest(),
        ba_plan_digest=ba.digest(),
        probe_plan_digest=probe_plans.digest(),
        geometry_digest=field.layer.digest(),
        initial_field_digest=_initial_field_digest(field),
        initial_state_digest=_initial_state_digest(state),
        history_support_count=ab.source_event_count,
        probe_support_count=probe_plans.source_event_count,
        history_completion_count=len(ab.completion_ticks),
        probe_completion_count=len(probe_plans.completion_ticks),
        field_node_count=len(field.layer.neurons),
        edge_count=len(state.edge_bindings),
        refinements=S1_EB_REFINEMENTS,
        history_step_counts=tuple(
            (item.refinement_id, len(item.proposal_steps)) for item in ab.plans
        ),
        probe_step_counts=tuple(
            (item.refinement_id, len(item.proposal_steps))
            for item in probe_plans.plans
        ),
        producer_entrypoint="produce_e1_confirmation_canonical_result",
        canonical_producer_bound=True,
        execution_permitted=False,
        execution_started=False,
        persistence_permitted=False,
        s1_ea6_rerun_permitted=False,
        memory_claim_permitted=False,
        semantic_claim_permitted=False,
        organization_claim_permitted=False,
        topology_claim_permitted=False,
        self_regulation_claim_permitted=False,
        ai_claim_permitted=False,
    )


def produce_e1_confirmation_canonical_result(
    binding: E1ConfirmationCanonicalProducerBinding,
    contract: E1ConfirmationChainContract,
) -> E1ConfirmationChainResult:
    """Reserve the canonical producer entrypoint while execution is locked."""

    if not isinstance(binding, E1ConfirmationCanonicalProducerBinding) or (
        not isinstance(contract, E1ConfirmationChainContract)
        or binding.chain_contract_digest != contract.digest()
    ):
        raise E1ConfirmationCanonicalProducerBindingError(
            "S1-EB9 requires its bound producer and chain contract"
        )
    raise E1ConfirmationCanonicalProducerBindingError(
        "S1-EB9 canonical execution remains locked"
    )
