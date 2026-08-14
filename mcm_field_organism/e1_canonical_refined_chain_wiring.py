"""Private S1-EA2 canonical refined-chain wiring; execution stays locked."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

from .e1_av_history_permutation import build_e1_av_history_permutation
from .e1_canonical_refined_formation_adapter import (
    produce_e1_canonical_refined_formation,
)
from .e1_completion_aligned_refinement import (
    build_e1_completion_aligned_refinement_plans,
)
from .e1_frozen_state_transfer_contract import (
    _fixed_probe_sequences,
    _probe_digest,
)
from .e1_refined_chain_canonical_producer import (
    E1RefinedChainCanonicalProducerBinding,
    _fresh_canonical_field,
    prepare_e1_refined_chain_canonical_producer,
)
from .e1_refined_chain_one_shot_execution import E1RefinedChainExecutionResult
from .e1_refined_chain_producer_composition import (
    _compose_e1_refined_chain_result,
)
from .e1_refined_seven_arm_probe_runner import (
    run_private_e1_refined_seven_arm_probe,
)
from .e1_refined_world_formation_contract import S1_DS_PROBE_DIGEST
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)


class E1CanonicalRefinedChainWiringError(ValueError):
    """Raised when S1-EA2 canonical producer wiring changed."""


S1_EA2_PROBE_PLAN_DIGEST = (
    "0d99364043f20695ec31168cd9c7b82f8ae9df55ebb4398243024f84168d6be6"
)
S1_EA2_PROBE_STEP_COUNTS = (("r1", 100), ("r2", 200), ("r4", 400))


def _normalized_source_digest(name: str) -> str:
    path = Path(__file__).with_name(name)
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _digest(value: object) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class E1CanonicalRefinedChainWiring:
    wiring_id: str
    binding_digest: str
    formation_adapter_digest: str
    probe_runner_digest: str
    composition_digest: str
    probe_digest: str
    probe_plan_digest: str
    probe_support_count: int
    probe_completion_count: int
    probe_step_counts: tuple[tuple[str, int], ...]
    producer_entrypoint: str
    formation_bound: bool
    probe_bound: bool
    composition_bound: bool
    execution_permitted: bool
    execution_started: bool
    persistence_permitted: bool
    memory_claim_permitted: bool
    ai_claim_permitted: bool

    def __post_init__(self) -> None:
        if self.wiring_id != "e1.canonical-refined-chain-wiring.s1ea2.v1":
            raise E1CanonicalRefinedChainWiringError(
                "S1-EA2 wiring identity changed"
            )
        for role in (
            "binding_digest",
            "formation_adapter_digest",
            "probe_runner_digest",
            "composition_digest",
            "probe_digest",
            "probe_plan_digest",
        ):
            value = getattr(self, role)
            if len(value) != 64 or any(
                char not in "0123456789abcdef" for char in value
            ):
                raise E1CanonicalRefinedChainWiringError(
                    f"{role} is not SHA-256"
                )
        if (
            self.probe_digest != S1_DS_PROBE_DIGEST
            or self.probe_plan_digest != S1_EA2_PROBE_PLAN_DIGEST
            or self.probe_support_count != 110
            or self.probe_completion_count != 100
            or self.probe_step_counts != S1_EA2_PROBE_STEP_COUNTS
        ):
            raise E1CanonicalRefinedChainWiringError(
                "S1-EA2 canonical probe binding changed"
            )
        if (
            self.producer_entrypoint != "produce_e1_canonical_refined_chain_result"
            or self.formation_bound is not True
            or self.probe_bound is not True
            or self.composition_bound is not True
        ):
            raise E1CanonicalRefinedChainWiringError(
                "S1-EA2 producer roles are incomplete"
            )
        if any(
            value is not False
            for value in (
                self.execution_permitted,
                self.execution_started,
                self.persistence_permitted,
                self.memory_claim_permitted,
                self.ai_claim_permitted,
            )
        ):
            raise E1CanonicalRefinedChainWiringError(
                "S1-EA2 cannot release execution, persistence, or claims"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


def prepare_e1_canonical_refined_chain_wiring(
    report_directory: Path,
    upstream_report_path: Path,
) -> E1CanonicalRefinedChainWiring:
    """Bind the full canonical chain without calling formation or probe."""

    binding = prepare_e1_refined_chain_canonical_producer(
        report_directory, upstream_report_path
    )
    probe = _fixed_probe_sequences()
    plans = build_e1_completion_aligned_refinement_plans(
        probe,
        horizon_start_tick=0,
        horizon_end_tick=1_000_000,
        ticks_per_second=1_000_000.0,
    )
    if _probe_digest(probe) != binding.probe_digest:
        raise E1CanonicalRefinedChainWiringError(
            "S1-EA2 probe does not match S1-DY"
        )
    return E1CanonicalRefinedChainWiring(
        wiring_id="e1.canonical-refined-chain-wiring.s1ea2.v1",
        binding_digest=binding.digest(),
        formation_adapter_digest=_normalized_source_digest(
            "e1_canonical_refined_formation_adapter.py"
        ),
        probe_runner_digest=_normalized_source_digest(
            "e1_refined_seven_arm_probe_runner.py"
        ),
        composition_digest=_normalized_source_digest(
            "e1_refined_chain_producer_composition.py"
        ),
        probe_digest=_probe_digest(probe),
        probe_plan_digest=plans.digest(),
        probe_support_count=plans.source_event_count,
        probe_completion_count=len(plans.completion_ticks),
        probe_step_counts=tuple(
            (item.refinement_id, len(item.proposal_steps))
            for item in plans.plans
        ),
        producer_entrypoint="produce_e1_canonical_refined_chain_result",
        formation_bound=True,
        probe_bound=True,
        composition_bound=True,
        execution_permitted=False,
        execution_started=False,
        persistence_permitted=False,
        memory_claim_permitted=False,
        ai_claim_permitted=False,
    )


def produce_e1_canonical_refined_chain_result(
    binding: E1RefinedChainCanonicalProducerBinding,
) -> E1RefinedChainExecutionResult:
    """Run the bound chain only after a later release gate permits it."""

    if not isinstance(binding, E1RefinedChainCanonicalProducerBinding):
        raise E1CanonicalRefinedChainWiringError(
            "S1-EA2 requires the S1-DY canonical binding"
        )
    formation = produce_e1_canonical_refined_formation(binding)
    probe = _fixed_probe_sequences()
    plans = build_e1_completion_aligned_refinement_plans(
        probe,
        horizon_start_tick=0,
        horizon_end_tick=1_000_000,
        ticks_per_second=1_000_000.0,
    )
    source = build_e1_av_history_permutation()
    by_refinement = {item.refinement_id: item for item in plans.plans}

    def probe_runner(formed):
        plan = by_refinement.get(formed.refinement_id)
        if plan is None or plan.factor != formed.factor:
            raise E1CanonicalRefinedChainWiringError(
                "S1-EA2 formation and probe refinement changed"
            )
        return run_private_e1_refined_seven_arm_probe(
            formed,
            lambda: _fresh_canonical_field(source),
            probe,
            plan.proposal_steps,
            NeutralLocalFieldSubstrateConfig(1.0),
            NeutralFastAfterimageConfig(0.5),
        )

    return _compose_e1_refined_chain_result(formation, probe_runner)
