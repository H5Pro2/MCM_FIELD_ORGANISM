"""Static S1-EC26 contract for repetition-dependent E1 formation."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .e1_confirmation_prepared_execution_bundle import E1PreparedExecutionBundle
from .e1_confirmation_prepared_formation_consumer import _typed_values_from_bundle
from .e1_memory_function_gap_audit import (
    E1MemoryFunctionGapAudit,
    S1_EC25_NEXT_FUNCTION,
    S1_EC25_NEXT_STEP,
)
from .e1_refined_confirmation_contract import S1_EB_REFINEMENTS
from .e1_refined_formation_runner import _digest


class E1RepetitionFormationContractError(ValueError):
    """Raised when the S1-EC26 preregistration changes its causal question."""


S1_EC26_CONTRACT_ID = "e1.repetition-formation-contract.s1ec26.v1"
S1_EC26_INPUT_BUNDLE_DIGEST = (
    "33f2d8479a37a3697374b3f10dd4581ac41684bb3d75e86fabf33568ef77e60f"
)
S1_EC26_EPISODE_CONTACT_DIGEST = (
    "ef9e3b9c7f95320891c6900832d6f0796029efddad90f2a7e9e13fdced1f084c"
)
S1_EC26_EPISODE_EVENT_COUNT = 110
S1_EC26_EPISODE_TICKS = 1_000_000
S1_EC26_GAP_TICKS = 1_000_000
S1_EC26_HORIZON_TICKS = 15_000_000
S1_EC26_CONTACT_COUNTS = (1, 2, 4, 8)
S1_EC26_EPISODE_INTEGRALS = (
    6.941865469153374,
    6.941865469153374,
    1.512406472248469,
)
S1_EC26_REQUIRED_BASELINES = (
    "p0-neutral-field",
    "e1-formation-ablation",
    "duration-energy-and-horizon-matched-leaky",
    "duration-energy-and-horizon-matched-f3",
    "duration-energy-and-horizon-matched-const-v",
    "matching-fixed-adapter-transfer-control",
)
S1_EC26_REQUIRED_GATES = (
    "one-contact-repeated-and-continuous-arms-bit-exact",
    "same-episode-supports-and-values-replayed",
    "same-total-contact-ticks-per-count-pair",
    "same-signed-absolute-and-quadratic-integrals-per-count-pair",
    "same-fifteen-million-tick-horizon",
    "same-final-fast-field-and-identical-later-probe",
    "formation-state-swap-moves-later-effect",
    "formation-ablation-removes-later-effect",
    "observer-off-and-snapshot-restore-invariant",
    "r2-r4-r8-fine-residual-nonincreasing",
    "no-posthoc-threshold-parameter-or-arm-change",
)
S1_EC26_DECISIONS = (
    "TECHNICALLY_INVALID",
    "NO_REPETITION_DEPENDENT_FORMATION",
    "REPETITION_DEPENDENT_FORMATION_CANDIDATE",
    "NUMERICALLY_UNDECIDABLE",
)
S1_EC26_DECISION_RULES = (
    "required-gate-or-baseline-failure=>TECHNICALLY_INVALID",
    "all-n2-n4-n8-state-and-probe-contrasts-bit-zero=>NO_REPETITION_DEPENDENT_FORMATION",
    "all-n2-n4-n8-state-and-probe-contrasts>8x-matching-fine-residual-and-not-equally-explained-by-required-baselines=>REPETITION_DEPENDENT_FORMATION_CANDIDATE",
    "otherwise=>NUMERICALLY_UNDECIDABLE",
)


@dataclass(frozen=True, slots=True)
class E1RepetitionSchedule:
    contact_count: int
    repeated_start_ticks: tuple[int, ...]
    continuous_start_tick: int
    continuous_end_tick: int
    total_contact_ticks: int
    horizon_end_tick: int
    expected_event_count: int
    expected_integrals: tuple[float, float, float]

    def __post_init__(self) -> None:
        expected_starts = tuple(
            index * (S1_EC26_EPISODE_TICKS + S1_EC26_GAP_TICKS)
            for index in range(self.contact_count)
        )
        expected_integrals = tuple(
            self.contact_count * value for value in S1_EC26_EPISODE_INTEGRALS
        )
        if (
            self.contact_count not in S1_EC26_CONTACT_COUNTS
            or self.repeated_start_ticks != expected_starts
            or self.continuous_start_tick
            != (self.contact_count - 1) * S1_EC26_EPISODE_TICKS
            or self.continuous_end_tick
            != (2 * self.contact_count - 1) * S1_EC26_EPISODE_TICKS
            or self.total_contact_ticks
            != self.continuous_end_tick - self.continuous_start_tick
            or self.continuous_end_tick
            != self.repeated_start_ticks[-1] + S1_EC26_EPISODE_TICKS
            or self.horizon_end_tick != S1_EC26_HORIZON_TICKS
            or self.expected_event_count
            != self.contact_count * S1_EC26_EPISODE_EVENT_COUNT
            or self.expected_integrals != expected_integrals
            or any(
                start + S1_EC26_EPISODE_TICKS > self.horizon_end_tick
                for start in self.repeated_start_ticks
            )
        ):
            raise E1RepetitionFormationContractError(
                "S1-EC26 repetition schedule is not exposure matched"
            )


@dataclass(frozen=True, slots=True)
class E1RepetitionFormationContract:
    contract_id: str
    upstream_gap_audit_digest: str
    selected_function: str
    input_bundle_digest: str
    episode_contact_digest: str
    episode_event_count: int
    episode_ticks: int
    gap_ticks: int
    horizon_ticks: int
    refinements: tuple[tuple[str, int], ...]
    schedules: tuple[E1RepetitionSchedule, ...]
    required_baselines: tuple[str, ...]
    required_gates: tuple[str, ...]
    decisions: tuple[str, ...]
    decision_rules: tuple[str, ...]
    numerical_signal_margin: float
    planner_implementation_permitted: bool
    field_execution_permitted: bool
    result_decision_permitted: bool
    imprinting_claim_permitted: bool
    memory_claim_permitted: bool
    ai_claim_permitted: bool
    contract_digest: str

    def __post_init__(self) -> None:
        if (
            self.contract_id != S1_EC26_CONTRACT_ID
            or len(self.upstream_gap_audit_digest) != 64
            or self.selected_function != S1_EC25_NEXT_FUNCTION
            or self.input_bundle_digest != S1_EC26_INPUT_BUNDLE_DIGEST
            or self.episode_contact_digest != S1_EC26_EPISODE_CONTACT_DIGEST
            or self.episode_event_count != S1_EC26_EPISODE_EVENT_COUNT
            or self.episode_ticks != S1_EC26_EPISODE_TICKS
            or self.gap_ticks != S1_EC26_GAP_TICKS
            or self.horizon_ticks != S1_EC26_HORIZON_TICKS
            or self.refinements != S1_EB_REFINEMENTS
            or tuple(item.contact_count for item in self.schedules)
            != S1_EC26_CONTACT_COUNTS
            or self.required_baselines != S1_EC26_REQUIRED_BASELINES
            or self.required_gates != S1_EC26_REQUIRED_GATES
            or self.decisions != S1_EC26_DECISIONS
            or self.decision_rules != S1_EC26_DECISION_RULES
            or self.numerical_signal_margin != 8.0
            or self.planner_implementation_permitted is not True
            or any(
                value is not False
                for value in (
                    self.field_execution_permitted,
                    self.result_decision_permitted,
                    self.imprinting_claim_permitted,
                    self.memory_claim_permitted,
                    self.ai_claim_permitted,
                )
            )
        ):
            raise E1RepetitionFormationContractError(
                "S1-EC26 contract changed or exceeded preregistration"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "contract_digest"
        }
        payload["schedules"] = tuple(asdict(item) for item in self.schedules)
        if self.contract_digest != _digest(payload):
            raise E1RepetitionFormationContractError(
                "S1-EC26 contract digest changed"
            )


def build_e1_repetition_formation_contract(
    gap_audit: E1MemoryFunctionGapAudit,
    bundle: E1PreparedExecutionBundle,
) -> E1RepetitionFormationContract:
    """Bind schedules and decisions without constructing a field or runner."""

    if not isinstance(gap_audit, E1MemoryFunctionGapAudit):
        raise E1RepetitionFormationContractError(
            "S1-EC26 requires the S1-EC25 gap audit"
        )
    if not isinstance(bundle, E1PreparedExecutionBundle):
        raise E1RepetitionFormationContractError(
            "S1-EC26 requires the prepared canonical AV bundle"
        )
    gap_audit.__post_init__()
    bundle.__post_init__()
    values = _typed_values_from_bundle(bundle)
    probe_plans = values.probe_plans
    first = probe_plans.plans[0]
    if (
        gap_audit.next_step != S1_EC25_NEXT_STEP
        or bundle.bundle_digest != S1_EC26_INPUT_BUNDLE_DIGEST
        or probe_plans.source_contact_digest != S1_EC26_EPISODE_CONTACT_DIGEST
        or probe_plans.source_event_count != S1_EC26_EPISODE_EVENT_COUNT
        or first.horizon_start_tick != 0
        or first.horizon_end_tick != S1_EC26_EPISODE_TICKS
        or tuple(
            (
                first.source_signed_integral,
                first.source_absolute_integral,
                first.source_quadratic_integral,
            )
        )
        != S1_EC26_EPISODE_INTEGRALS
    ):
        raise E1RepetitionFormationContractError(
            "S1-EC26 canonical episode evidence changed"
        )
    schedules = tuple(
        E1RepetitionSchedule(
            contact_count=count,
            repeated_start_ticks=tuple(
                index * (S1_EC26_EPISODE_TICKS + S1_EC26_GAP_TICKS)
                for index in range(count)
            ),
            continuous_start_tick=(count - 1) * S1_EC26_EPISODE_TICKS,
            continuous_end_tick=(2 * count - 1) * S1_EC26_EPISODE_TICKS,
            total_contact_ticks=count * S1_EC26_EPISODE_TICKS,
            horizon_end_tick=S1_EC26_HORIZON_TICKS,
            expected_event_count=count * S1_EC26_EPISODE_EVENT_COUNT,
            expected_integrals=tuple(
                count * value for value in S1_EC26_EPISODE_INTEGRALS
            ),
        )
        for count in S1_EC26_CONTACT_COUNTS
    )
    payload = {
        "contract_id": S1_EC26_CONTRACT_ID,
        "upstream_gap_audit_digest": gap_audit.audit_digest,
        "selected_function": gap_audit.next_function,
        "input_bundle_digest": bundle.bundle_digest,
        "episode_contact_digest": probe_plans.source_contact_digest,
        "episode_event_count": probe_plans.source_event_count,
        "episode_ticks": S1_EC26_EPISODE_TICKS,
        "gap_ticks": S1_EC26_GAP_TICKS,
        "horizon_ticks": S1_EC26_HORIZON_TICKS,
        "refinements": S1_EB_REFINEMENTS,
        "schedules": tuple(asdict(item) for item in schedules),
        "required_baselines": S1_EC26_REQUIRED_BASELINES,
        "required_gates": S1_EC26_REQUIRED_GATES,
        "decisions": S1_EC26_DECISIONS,
        "decision_rules": S1_EC26_DECISION_RULES,
        "numerical_signal_margin": 8.0,
        "planner_implementation_permitted": True,
        "field_execution_permitted": False,
        "result_decision_permitted": False,
        "imprinting_claim_permitted": False,
        "memory_claim_permitted": False,
        "ai_claim_permitted": False,
    }
    digest = _digest(payload)
    payload["schedules"] = schedules
    return E1RepetitionFormationContract(
        **payload,
        contract_digest=digest,
    )
