"""Closed private S2-IG runner for five real two-area context statuses."""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
import hashlib
from pathlib import Path
import re
from typing import Callable

import numpy as np

from mcm_field_organism import _tspm1_private as tspm1
from mcm_field_organism._ppb1_active_receptor_batch_binding import (
    PPB1ActiveReceptorBatchEnvelope,
    bind_ppb1_active_receptor_batch,
)
from mcm_field_organism._ppb1_receptor_profiles import (
    PPB1ModalityParameters,
    PPB1ProfileParameters,
    bind_ppb1_receptor_profile,
)
from mcm_field_organism.browser_receptor_bridge import BrowserReceptorSequenceBatch
from mcm_field_organism.browser_world_contract import BrowserWorldContract, BrowserWorldPhase
from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from mcm_field_organism.receptor_contract import CommonFieldTime, ReceptorContactFrame
from mcm_field_organism.receptor_time_model import OrganismTimedReceptorFrame, ReceptorTimeSequence
from tools import _s2fs_b4_tspm1_private_coordinator as coordinator
from tools import _s2fu_private_fixtures as p_fixtures
from tools import _s2gb_private_perceptual_context_bundle as context_bundle
from tools import _s2gi_private_two_area_context_projection as two_area
from tools import _s2gk_private_masked_visual_context_consumer as masked_contract
from tools import _s2hq_private_byte_block_conflict_fixture as q_fixtures
from tools import _s2ic_private_direct_two_area_conflict_baseline as direct_baseline
from tools import _s2ic_private_two_area_conflict_contract as signal_contract
from tools import _s2ic_private_two_area_conflict_signal as conflict_signal
from tools import _s2ig_private_append_only_recorder as recording
from tools import _s2ig_private_fixture_registry as fixtures


RUNNER_SCHEMA = "s2ig.private.runner.v1"
MAIN_EXECUTION_ENABLED = False
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_STRICT_IDENTIFIER = re.compile(r"^[a-z][a-z0-9-]{7,95}$")
_PROFILE_PARAMETERS = PPB1ProfileParameters(
    PPB1ModalityParameters(8, 0.02, 0.05, 3, 256),
    PPB1ModalityParameters(4, 0.01, 0.05, 3, 64),
)
_VISUAL_CONFIG = VisualGridConfig(120, 80, 3, 2, 30.0)
COMPACT_DUAL_PROBE_BINDING_SCHEMA = "s2it.compact-dual-probe-binding-receipt.v1"
COMPACT_SIGNAL_ARM_SCHEMA = "s2ig.signal-arm-receipt.v1"
COMPACT_DUAL_PROBE_BINDING_MAX_BYTES = 1_299
COMPACT_SIGNAL_ARM_MAX_BYTES = 1_999


class S2IGRunnerError(RuntimeError):
    """One closed runner-boundary error."""


@dataclass(frozen=True, slots=True)
class EvaluationCaseBinding:
    case_id: str
    expected_status: str
    binding_digest: str

    @classmethod
    def build(cls, case_id: str, expected_status: str) -> "EvaluationCaseBinding":
        if case_id not in fixtures.CASE_BY_ID or expected_status not in signal_contract.RESULT_STATUSES:
            raise S2IGRunnerError("evaluation case binding differs")
        payload = {
            "schema": "s2ie.evaluation-case-binding.v1",
            "case_id": case_id,
            "expected_status": expected_status,
        }
        return cls(case_id, expected_status, fixtures.canonical_digest(payload))


@dataclass(frozen=True, slots=True)
class EvaluationPlanSeal:
    plan_id: str
    case_bindings: tuple[EvaluationCaseBinding, ...]
    evaluation_source_digests: tuple[tuple[str, str], ...]
    seal_digest: str
    schema: str = "s2ie.evaluation-plan-seal.v1"


def bind_evaluation_plan(
    plan_id: str,
    case_bindings: tuple[EvaluationCaseBinding, ...],
    evaluation_source_digests: tuple[tuple[str, str], ...],
) -> EvaluationPlanSeal:
    if (
        not isinstance(plan_id, str)
        or re.fullmatch(r"[a-z][a-z0-9-]{7,95}", plan_id) is None
        or type(case_bindings) is not tuple
        or tuple(item.case_id for item in case_bindings) != tuple(f"c{index:02d}" for index in range(1, 9))
        or len({item.binding_digest for item in case_bindings}) != 8
        or type(evaluation_source_digests) is not tuple
        or not evaluation_source_digests
        or any(_DIGEST.fullmatch(digest) is None for _, digest in evaluation_source_digests)
    ):
        raise S2IGRunnerError("evaluation plan is incomplete")
    payload = {
        "schema": "s2ie.evaluation-plan-seal.v1",
        "plan_id": plan_id,
        "case_binding_digests": tuple(item.binding_digest for item in case_bindings),
        "evaluation_source_digests": evaluation_source_digests,
    }
    return EvaluationPlanSeal(
        plan_id,
        case_bindings,
        evaluation_source_digests,
        fixtures.canonical_digest(payload),
    )


@dataclass(frozen=True, slots=True)
class _BoundSource:
    role: str
    source_id: str
    visual_fixture_id: str
    auditory_fixture_id: str
    window_start: int
    window_end: int
    envelope: PPB1ActiveReceptorBatchEnvelope
    bound: coordinator.B4TSPM1BoundInput | coordinator.B4TSPM1BoundProbe
    raw_sha256: str
    source_digest: str


@dataclass(frozen=True, slots=True)
class _Recorded:
    value: object
    artifact_digest: str
    result_event_digest: str


@dataclass(frozen=True, slots=True)
class _FormationRuntimeIdentifiers:
    history_id: str
    ordinal: int
    owner_id: str
    authorization_id: str
    consumption_id: str


@dataclass(frozen=True, slots=True)
class _CaseRuntimeIdentifiers:
    case_id: str
    signal_invocation_id: str
    baseline_invocation_id: str
    dual_owner_id: str
    signal_owner_id: str
    baseline_owner_id: str


@dataclass(slots=True)
class _Runtime:
    profile: object
    tspm_config: tspm1.TSPM1ConfigBinding
    coordinator_config: coordinator.B4TSPM1CoordinatorConfig
    world: BrowserWorldContract
    receptor: LocalChannelGridReceptor
    image_serial: int = 0


@dataclass(frozen=True, slots=True)
class ContextRetrievalProbe:
    case_plan_digest: str
    probe_id: str
    source_id: str
    source_digest: str
    receptor_receipt_digest: str
    config_digest: str
    auditory_values_digest: str
    visual_values_digest: str
    av_values_digest: str
    function_probe_digest: str
    window_start_tick: int
    window_end_tick: int
    context_retrieval_probe_digest: str
    role: str = "CONTEXT_RETRIEVAL_PROBE"
    value_dimension: int = 26
    schema: str = "s2if.context-retrieval-probe.v1"


@dataclass(frozen=True, slots=True)
class MaskedSignalProbe:
    case_plan_digest: str
    probe_id: str
    source_id: str
    source_digest: str
    receptor_receipt_digest: str
    config_digest: str
    visual_values_digest: str
    visible_values_digest: str
    mask_digest: str
    masked_visual_probe_digest: str
    visible_positions: tuple[int, ...]
    masked_positions: tuple[int, ...]
    window_start_tick: int
    window_end_tick: int
    masked_signal_probe_digest: str
    role: str = "MASKED_SIGNAL_PROBE"
    value_dimension: int = 18
    schema: str = "s2if.masked-signal-probe.v1"


@dataclass(frozen=True, slots=True)
class DualProbeCaseBinding:
    case_plan_digest: str
    context_retrieval_probe_digest: str
    context_function_probe_digest: str
    masked_signal_probe_digest: str
    masked_visual_probe_digest: str
    context_source_digest: str
    signal_source_digest: str
    two_area_bundle_digest: str
    bundle_context_probe_digest: str
    signal_input_digest: str
    baseline_input_digest: str
    source_ledger_digest: str
    dual_probe_binding_digest: str
    schema: str = "s2if.dual-probe-case-binding.v1"


@dataclass(frozen=True, slots=True)
class DualProbeOwnerSnapshot:
    owner_id: str
    case_plan_digest: str
    dual_probe_binding_digest: str
    context_retrieval_probe_digest: str
    masked_signal_probe_digest: str
    two_area_bundle_digest: str
    signal_input_digest: str
    baseline_input_digest: str
    state: str
    prior_owner_digest: str | None
    signal_result_digest: str | None
    baseline_result_digest: str | None
    terminal_pair_digest: str | None
    owner_digest: str
    schema: str = "s2if.dual-probe-case-owner.v1"


@dataclass(frozen=True, slots=True)
class CompactDualProbeBindingReceiptV1:
    case_plan_digest: str
    context_retrieval_probe_digest: str
    masked_signal_probe_digest: str
    dual_probe_binding_digest: str
    signal_input_digest: str
    baseline_input_digest: str
    source_ledger_digest: str
    dual_owner_id: str
    dual_owner_prestate_digest: str
    schema: str = COMPACT_DUAL_PROBE_BINDING_SCHEMA

    def payload(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "case_plan_digest": self.case_plan_digest,
            "context_retrieval_probe_digest": self.context_retrieval_probe_digest,
            "masked_signal_probe_digest": self.masked_signal_probe_digest,
            "dual_probe_binding_digest": self.dual_probe_binding_digest,
            "signal_input_digest": self.signal_input_digest,
            "baseline_input_digest": self.baseline_input_digest,
            "source_ledger_digest": self.source_ledger_digest,
            "dual_owner_id": self.dual_owner_id,
            "dual_owner_prestate_digest": self.dual_owner_prestate_digest,
        }

    @classmethod
    def project(
        cls,
        binding: DualProbeCaseBinding,
        owner_prestate: DualProbeOwnerSnapshot,
        signal_input: signal_contract.TwoAreaConflictSignalInput,
        baseline_input: signal_contract.TwoAreaConflictSignalInput,
    ) -> "CompactDualProbeBindingReceiptV1":
        _require(type(binding) is DualProbeCaseBinding, "dual binding projection source differs")
        _require(type(owner_prestate) is DualProbeOwnerSnapshot, "dual owner projection source differs")
        _require(
            type(signal_input) is signal_contract.TwoAreaConflictSignalInput
            and type(baseline_input) is signal_contract.TwoAreaConflictSignalInput,
            "arm input projection source differs",
        )
        _require(
            owner_prestate.state == "READY"
            and owner_prestate.prior_owner_digest is None
            and owner_prestate.signal_result_digest is None
            and owner_prestate.baseline_result_digest is None
            and owner_prestate.terminal_pair_digest is None
            and owner_prestate.case_plan_digest == binding.case_plan_digest
            and owner_prestate.dual_probe_binding_digest == binding.dual_probe_binding_digest
            and owner_prestate.context_retrieval_probe_digest
            == binding.context_retrieval_probe_digest
            and owner_prestate.masked_signal_probe_digest == binding.masked_signal_probe_digest
            and owner_prestate.two_area_bundle_digest == binding.two_area_bundle_digest
            and owner_prestate.signal_input_digest == binding.signal_input_digest
            and owner_prestate.baseline_input_digest == binding.baseline_input_digest
            and signal_input.input_digest == binding.signal_input_digest
            and baseline_input.input_digest == binding.baseline_input_digest,
            "compact dual binding relation differs",
        )
        _require(
            _STRICT_IDENTIFIER.fullmatch(owner_prestate.owner_id) is not None
            and all(
                _DIGEST.fullmatch(value) is not None
                for value in (
                    binding.case_plan_digest,
                    binding.context_retrieval_probe_digest,
                    binding.masked_signal_probe_digest,
                    binding.dual_probe_binding_digest,
                    binding.signal_input_digest,
                    binding.baseline_input_digest,
                    binding.source_ledger_digest,
                    owner_prestate.owner_digest,
                )
            ),
            "compact dual binding field differs",
        )
        return cls(
            binding.case_plan_digest,
            binding.context_retrieval_probe_digest,
            binding.masked_signal_probe_digest,
            binding.dual_probe_binding_digest,
            binding.signal_input_digest,
            binding.baseline_input_digest,
            binding.source_ledger_digest,
            owner_prestate.owner_id,
            owner_prestate.owner_digest,
        )


@dataclass(frozen=True, slots=True)
class CompactSignalArmReceiptV1:
    invocation_id: str
    function_role: str
    owner_prestate_digest: str
    input_digest: str
    status: str
    probe_digest: str
    bundle_digest: str
    a_applicability_finding_digest: str
    b_applicability_finding_digest: str
    comparison_digest: str
    present_areas: tuple[str, ...]
    applicable_areas: tuple[str, ...]
    differing_masked_positions: tuple[int, ...]
    prestate_digest: str
    poststate_digest: str
    resource_ledger_digest: str
    result_digest: str
    receipt_digest: str
    owner_poststate_digest: str
    selected_area: None
    recommended_area: None
    automatic_selection: None
    visibility: str
    schema: str = COMPACT_SIGNAL_ARM_SCHEMA

    def payload(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "invocation_id": self.invocation_id,
            "function_role": self.function_role,
            "owner_prestate_digest": self.owner_prestate_digest,
            "input_digest": self.input_digest,
            "status": self.status,
            "probe_digest": self.probe_digest,
            "bundle_digest": self.bundle_digest,
            "a_applicability_finding_digest": self.a_applicability_finding_digest,
            "b_applicability_finding_digest": self.b_applicability_finding_digest,
            "comparison_digest": self.comparison_digest,
            "present_areas": self.present_areas,
            "applicable_areas": self.applicable_areas,
            "differing_masked_positions": self.differing_masked_positions,
            "prestate_digest": self.prestate_digest,
            "poststate_digest": self.poststate_digest,
            "resource_ledger_digest": self.resource_ledger_digest,
            "result_digest": self.result_digest,
            "receipt_digest": self.receipt_digest,
            "owner_poststate_digest": self.owner_poststate_digest,
            "selected_area": self.selected_area,
            "recommended_area": self.recommended_area,
            "automatic_selection": self.automatic_selection,
            "visibility": self.visibility,
        }

    @classmethod
    def project(
        cls,
        commit: signal_contract.TwoAreaConflictSignalCommit,
    ) -> "CompactSignalArmReceiptV1":
        _require(type(commit) is signal_contract.TwoAreaConflictSignalCommit, "signal commit differs")
        result = commit.result
        receipt = commit.receipt
        poststate = commit.owner_poststate
        _require(
            receipt.invocation_id == poststate.invocation_id
            and receipt.function_role == result.function_role == poststate.function_role
            and receipt.owner_prestate_digest == poststate.prior_owner_digest
            and receipt.input_digest == result.input_digest == poststate.input_digest
            and receipt.a_applicability_finding_digest
            == result.a_applicability_finding_digest
            and receipt.b_applicability_finding_digest
            == result.b_applicability_finding_digest
            and receipt.comparison_digest == result.comparison_digest
            and receipt.resource_ledger_digest == result.resource_ledger_digest
            and receipt.result_digest == result.result_digest
            and receipt.owner_poststate_digest == poststate.owner_poststate_digest
            and poststate.terminal_binding_digest == result.result_digest
            and poststate.state == "CONSUMED",
            "signal arm projection relation differs",
        )
        return cls(
            receipt.invocation_id,
            result.function_role,
            receipt.owner_prestate_digest,
            receipt.input_digest,
            result.status,
            result.probe_digest,
            result.bundle_digest,
            result.a_applicability_finding_digest,
            result.b_applicability_finding_digest,
            result.comparison_digest,
            result.present_areas,
            result.applicable_areas,
            result.differing_masked_positions,
            result.prestate_digest,
            result.poststate_digest,
            result.resource_ledger_digest,
            result.result_digest,
            receipt.receipt_digest,
            poststate.owner_poststate_digest,
            None,
            None,
            None,
            "PRIVATE_CANDIDATE_NOT_CASE_FINDING",
        )


class DualProbeCaseOwner:
    __slots__ = ("_prestate", "_poststate")

    def __init__(self, owner_id: str, binding: DualProbeCaseBinding) -> None:
        payload = {
            "schema": "s2if.dual-probe-case-owner.v1",
            "owner_id": owner_id,
            "case_plan_digest": binding.case_plan_digest,
            "dual_probe_binding_digest": binding.dual_probe_binding_digest,
            "context_retrieval_probe_digest": binding.context_retrieval_probe_digest,
            "masked_signal_probe_digest": binding.masked_signal_probe_digest,
            "two_area_bundle_digest": binding.two_area_bundle_digest,
            "signal_input_digest": binding.signal_input_digest,
            "baseline_input_digest": binding.baseline_input_digest,
            "state": "READY",
            "prior_owner_digest": None,
            "signal_result_digest": None,
            "baseline_result_digest": None,
            "terminal_pair_digest": None,
        }
        self._prestate = DualProbeOwnerSnapshot(**payload, owner_digest=fixtures.canonical_digest(payload))
        self._poststate: DualProbeOwnerSnapshot | None = None

    @property
    def prestate(self) -> DualProbeOwnerSnapshot:
        return self._prestate

    @property
    def poststate(self) -> DualProbeOwnerSnapshot | None:
        return self._poststate

    @property
    def state(self) -> str:
        return "READY" if self._poststate is None else self._poststate.state

    def commit(
        self,
        binding: DualProbeCaseBinding,
        signal_digest: str,
        baseline_digest: str,
    ) -> DualProbeOwnerSnapshot:
        _require(self._poststate is None, "dual-probe owner was already consumed")
        if (
            type(binding) is not DualProbeCaseBinding
            or binding.dual_probe_binding_digest != self._prestate.dual_probe_binding_digest
            or _DIGEST.fullmatch(signal_digest) is None
            or _DIGEST.fullmatch(baseline_digest) is None
        ):
            payload = {
                "schema": self._prestate.schema,
                "owner_id": self._prestate.owner_id,
                "case_plan_digest": self._prestate.case_plan_digest,
                "dual_probe_binding_digest": self._prestate.dual_probe_binding_digest,
                "context_retrieval_probe_digest": self._prestate.context_retrieval_probe_digest,
                "masked_signal_probe_digest": self._prestate.masked_signal_probe_digest,
                "two_area_bundle_digest": self._prestate.two_area_bundle_digest,
                "signal_input_digest": self._prestate.signal_input_digest,
                "baseline_input_digest": self._prestate.baseline_input_digest,
                "state": "FAILED",
                "prior_owner_digest": self._prestate.owner_digest,
                "signal_result_digest": None,
                "baseline_result_digest": None,
                "terminal_pair_digest": None,
            }
            self._poststate = DualProbeOwnerSnapshot(
                **payload,
                owner_digest=fixtures.canonical_digest(payload),
            )
            raise S2IGRunnerError("dual-probe owner binding differs")
        terminal = fixtures.canonical_digest(
            {"signal_result_digest": signal_digest, "baseline_result_digest": baseline_digest}
        )
        payload = {
            "schema": self._prestate.schema,
            "owner_id": self._prestate.owner_id,
            "case_plan_digest": self._prestate.case_plan_digest,
            "dual_probe_binding_digest": self._prestate.dual_probe_binding_digest,
            "context_retrieval_probe_digest": self._prestate.context_retrieval_probe_digest,
            "masked_signal_probe_digest": self._prestate.masked_signal_probe_digest,
            "two_area_bundle_digest": self._prestate.two_area_bundle_digest,
            "signal_input_digest": self._prestate.signal_input_digest,
            "baseline_input_digest": self._prestate.baseline_input_digest,
            "state": "CONSUMED",
            "prior_owner_digest": self._prestate.owner_digest,
            "signal_result_digest": signal_digest,
            "baseline_result_digest": baseline_digest,
            "terminal_pair_digest": terminal,
        }
        self._poststate = DualProbeOwnerSnapshot(**payload, owner_digest=fixtures.canonical_digest(payload))
        return self._poststate


def _canonical(value: object) -> object:
    if is_dataclass(value):
        return _canonical(asdict(value))
    if isinstance(value, dict):
        return {str(key): _canonical(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_canonical(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    return value


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2IGRunnerError(message)


def _strict_identifier(*parts: str) -> str:
    _require(
        bool(parts)
        and all(type(part) is str and re.fullmatch(r"[a-z0-9-]+", part) is not None for part in parts),
        "strict identifier component differs",
    )
    value = "-".join(parts)
    _require(_STRICT_IDENTIFIER.fullmatch(value) is not None, "strict identifier differs")
    return value


def _formation_runtime_identifiers(
    history_id: str,
    ordinal: int,
) -> _FormationRuntimeIdentifiers:
    _require(
        history_id in fixtures.HISTORY_BY_ID
        and type(ordinal) is int
        and 1 <= ordinal <= len(fixtures.HISTORY_BY_ID[history_id].steps),
        "formation identifier source differs",
    )
    stem = ("s2ig", "formation", history_id, f"{ordinal:02d}")
    return _FormationRuntimeIdentifiers(
        history_id,
        ordinal,
        _strict_identifier(*stem, "owner"),
        _strict_identifier(*stem, "authorization"),
        _strict_identifier(*stem, "consumption"),
    )


def _case_runtime_identifiers(case_id: str) -> _CaseRuntimeIdentifiers:
    _require(case_id in fixtures.CASE_BY_ID, "case identifier source differs")
    stem = ("s2ig", "case", case_id)
    return _CaseRuntimeIdentifiers(
        case_id,
        _strict_identifier(*stem, "signal", "invocation"),
        _strict_identifier(*stem, "baseline", "invocation"),
        _strict_identifier(*stem, "dual", "owner"),
        _strict_identifier(*stem, "signal", "owner"),
        _strict_identifier(*stem, "baseline", "owner"),
    )


def _validate_context_retrieval_probe(value: ContextRetrievalProbe) -> None:
    _require(type(value) is ContextRetrievalProbe, "context retrieval probe type differs")
    payload = {
        "schema": value.schema,
        "case_plan_digest": value.case_plan_digest,
        "role": value.role,
        "probe_id": value.probe_id,
        "source_id": value.source_id,
        "source_digest": value.source_digest,
        "receptor_receipt_digest": value.receptor_receipt_digest,
        "config_digest": value.config_digest,
        "auditory_values_digest": value.auditory_values_digest,
        "visual_values_digest": value.visual_values_digest,
        "av_values_digest": value.av_values_digest,
        "function_probe_digest": value.function_probe_digest,
        "value_dimension": value.value_dimension,
        "window_start_tick": value.window_start_tick,
        "window_end_tick": value.window_end_tick,
    }
    _require(
        value.schema == "s2if.context-retrieval-probe.v1"
        and value.role == "CONTEXT_RETRIEVAL_PROBE"
        and value.value_dimension == 26
        and value.window_end_tick == value.window_start_tick + 1
        and all(
            _DIGEST.fullmatch(item) is not None
            for item in (
                value.case_plan_digest,
                value.source_digest,
                value.receptor_receipt_digest,
                value.config_digest,
                value.auditory_values_digest,
                value.visual_values_digest,
                value.av_values_digest,
                value.function_probe_digest,
            )
        )
        and value.context_retrieval_probe_digest == fixtures.canonical_digest(payload),
        "context retrieval probe binding differs",
    )


def _validate_masked_signal_probe(value: MaskedSignalProbe) -> None:
    _require(type(value) is MaskedSignalProbe, "masked signal probe type differs")
    payload = {
        "schema": value.schema,
        "case_plan_digest": value.case_plan_digest,
        "role": value.role,
        "probe_id": value.probe_id,
        "source_id": value.source_id,
        "source_digest": value.source_digest,
        "receptor_receipt_digest": value.receptor_receipt_digest,
        "config_digest": value.config_digest,
        "visual_values_digest": value.visual_values_digest,
        "visible_values_digest": value.visible_values_digest,
        "mask_digest": value.mask_digest,
        "masked_visual_probe_digest": value.masked_visual_probe_digest,
        "visible_positions": value.visible_positions,
        "masked_positions": value.masked_positions,
        "value_dimension": value.value_dimension,
        "window_start_tick": value.window_start_tick,
        "window_end_tick": value.window_end_tick,
    }
    _require(
        value.schema == "s2if.masked-signal-probe.v1"
        and value.role == "MASKED_SIGNAL_PROBE"
        and value.value_dimension == 18
        and value.visible_positions == fixtures.VISIBLE_POSITIONS
        and value.masked_positions == fixtures.MASKED_POSITIONS
        and value.window_end_tick == value.window_start_tick + 1
        and all(
            _DIGEST.fullmatch(item) is not None
            for item in (
                value.case_plan_digest,
                value.source_digest,
                value.receptor_receipt_digest,
                value.config_digest,
                value.visual_values_digest,
                value.visible_values_digest,
                value.mask_digest,
                value.masked_visual_probe_digest,
            )
        )
        and value.masked_signal_probe_digest == fixtures.canonical_digest(payload),
        "masked signal probe binding differs",
    )


def bind_dual_probe_case(
    context_probe: ContextRetrievalProbe,
    signal_probe: MaskedSignalProbe,
    area_bundle: two_area.TwoAreaContextBundle,
    signal_input: signal_contract.TwoAreaConflictSignalInput,
    baseline_input: signal_contract.TwoAreaConflictSignalInput,
) -> tuple[DualProbeCaseBinding, dict[str, int]]:
    """Bind retrieval and signal provenance without equating their probes."""

    _validate_context_retrieval_probe(context_probe)
    _validate_masked_signal_probe(signal_probe)
    _require(type(area_bundle) is two_area.TwoAreaContextBundle, "two-area bundle differs")
    _require(
        type(signal_input) is signal_contract.TwoAreaConflictSignalInput
        and type(baseline_input) is signal_contract.TwoAreaConflictSignalInput,
        "signal arm input differs",
    )
    _require(
        context_probe.case_plan_digest == signal_probe.case_plan_digest
        and context_probe.config_digest == signal_probe.config_digest
        and context_probe.source_id != signal_probe.source_id
        and context_probe.source_digest != signal_probe.source_digest,
        "dual-probe case provenance differs",
    )
    _require(
        area_bundle.probe_digest == context_probe.function_probe_digest
        and signal_input.probe_digest == signal_probe.masked_visual_probe_digest
        and baseline_input.probe_digest == signal_probe.masked_visual_probe_digest
        and signal_input.bundle_digest == area_bundle.bundle_digest
        and baseline_input.bundle_digest == area_bundle.bundle_digest
        and signal_input.function_role == "SIGNAL"
        and baseline_input.function_role == "DIRECT_BASELINE",
        "dual-probe native relation differs",
    )
    source_ledger = {
        "case_plan_validation_count": 1,
        "typed_probe_validation_count": 2,
        "source_binding_validation_count": 2,
        "receptor_receipt_validation_count": 2,
        "configuration_binding_validation_count": 2,
        "context_native_probe_relation_count": 1,
        "signal_native_probe_relation_count": 1,
        "bundle_context_probe_relation_count": 1,
        "arm_input_relation_count": 2,
        "context_value_reference_count": 26,
        "signal_position_validation_count": 18,
        "digest_validation_count": 39,
        "owner_transition_count": 1,
        "new_digest_operation_count": 8,
        "storage_or_learning_call_count": 0,
    }
    source_ledger_digest = fixtures.canonical_digest(source_ledger)
    payload = {
        "schema": "s2if.dual-probe-case-binding.v1",
        "case_plan_digest": context_probe.case_plan_digest,
        "context_retrieval_probe_digest": context_probe.context_retrieval_probe_digest,
        "context_function_probe_digest": context_probe.function_probe_digest,
        "masked_signal_probe_digest": signal_probe.masked_signal_probe_digest,
        "masked_visual_probe_digest": signal_probe.masked_visual_probe_digest,
        "context_source_digest": context_probe.source_digest,
        "signal_source_digest": signal_probe.source_digest,
        "two_area_bundle_digest": area_bundle.bundle_digest,
        "bundle_context_probe_digest": area_bundle.probe_digest,
        "signal_input_digest": signal_input.input_digest,
        "baseline_input_digest": baseline_input.input_digest,
        "source_ledger_digest": source_ledger_digest,
    }
    return (
        DualProbeCaseBinding(
            **payload,
            dual_probe_binding_digest=fixtures.canonical_digest(payload),
        ),
        source_ledger,
    )


def _source_paths(workspace_root: Path) -> tuple[tuple[str, Path], ...]:
    names = (
        "_s2ig_private_fixture_registry.py",
        "_s2ig_private_runner.py",
        "_s2ig_private_append_only_recorder.py",
        "_s2fs_b4_tspm1_private_coordinator.py",
        "_s2fu_private_fixtures.py",
        "_s2hq_private_byte_block_conflict_fixture.py",
        "_s2gb_private_perceptual_context_bundle.py",
        "_s2gi_private_two_area_context_projection.py",
        "_s2gk_private_masked_visual_context_consumer.py",
        "_s2ic_private_two_area_conflict_contract.py",
        "_s2ic_private_two_area_conflict_signal.py",
        "_s2ic_private_direct_two_area_conflict_baseline.py",
    )
    return tuple((name.removesuffix(".py"), workspace_root / "tools" / name) for name in names)


def materialize_execution_plan(
    workspace_root: Path,
    run_id: str,
    owner_id: str,
) -> tuple[recording.ExecutionPlan, fixtures.RegistryBundle]:
    fixtures.validate_literal_fixtures()
    registry = fixtures.load_operation_registry()
    source_digests = tuple(
        (path.relative_to(workspace_root).as_posix(), fixtures.file_digest(path))
        for _, path in _source_paths(workspace_root)
    )
    return recording.ExecutionPlan.build(run_id, owner_id, registry, source_digests), registry


def _runtime() -> _Runtime:
    profile = bind_ppb1_receptor_profile("browser", _PROFILE_PARAMETERS)
    tspm_config = tspm1.TSPM1ConfigBinding.build(
        tspm1.TSPM1FastConfig("tspm1.fast", 3, 0.2, 0.2, 0.5, 2, 8),
        profile,
    )
    coordinator_config = coordinator.build_coordinator_config(tspm_config)
    world = BrowserWorldContract(
        contract_id="synthetic.s2ig.world.v1",
        startup_frame_count=1,
        start_lead_ns=1,
        movement_cycles=1,
        tone_frequency_hz=100.0,
        phases=(
            BrowserWorldPhase("rest.before", 10, "static", 0.0),
            BrowserWorldPhase("change", 10, "moving", 0.2),
            BrowserWorldPhase("rest.after", 10, "static", 0.0),
        ),
    )
    return _Runtime(
        profile,
        tspm_config,
        coordinator_config,
        world,
        LocalChannelGridReceptor(_VISUAL_CONFIG),
    )


def _p_fixture(identifier: str) -> p_fixtures.S2FUPatternFixture:
    key = identifier.upper()
    _require(key in p_fixtures.PATTERN_BY_ID, "unknown P fixture")
    return p_fixtures.PATTERN_BY_ID[key]


def _image_and_values(identifier: str) -> tuple[np.ndarray, tuple[float, ...]]:
    if identifier.startswith("p"):
        pattern = _p_fixture(identifier)
        cells = np.asarray(pattern.visual_cell_values, dtype=np.uint8).reshape(2, 3)
        image = np.repeat(np.repeat(cells, 40, axis=0), 40, axis=1)
        image = np.repeat(image[:, :, None], 3, axis=2)
        expected = pattern.visual_values
    elif identifier in q_fixtures.VISUAL_BY_ID:
        fixture = q_fixtures.VISUAL_BY_ID[identifier]
        cells = np.asarray(fixture.block_values, dtype=np.uint8).reshape(2, 3, 3)
        image = np.repeat(np.repeat(cells, 40, axis=0), 40, axis=1)
        expected = fixture.receptor_values
    elif identifier in fixtures.Z_VISUAL_BLOCKS:
        cells = np.asarray(fixtures.Z_VISUAL_BLOCKS[identifier], dtype=np.uint8).reshape(2, 3, 3)
        image = np.repeat(np.repeat(cells, 40, axis=0), 40, axis=1)
        expected = tuple(value / 255.0 for value in fixtures.Z_VISUAL_BLOCKS[identifier])
    else:
        raise S2IGRunnerError("unknown visual fixture")
    image.setflags(write=False)
    return image, tuple(float(value) for value in expected)


def _auditory_values(identifier: str) -> tuple[float, ...]:
    if identifier.startswith("p"):
        return tuple(float(value) for value in _p_fixture(identifier).auditory_values)
    if identifier in q_fixtures.AUDITORY_BY_ID:
        return tuple(float(value) for value in q_fixtures.AUDITORY_BY_ID[identifier].values)
    raise S2IGRunnerError("unknown auditory fixture")


def _timed(frame: ReceptorContactFrame, field_time: CommonFieldTime) -> ReceptorTimeSequence:
    return ReceptorTimeSequence(
        frame.modality_id,
        frame.geometry_id,
        field_time.clock_id,
        (OrganismTimedReceptorFrame(frame, field_time),),
    )


def _analyze(
    runtime: _Runtime,
    source_id: str,
    visual_id: str,
    auditory_id: str,
    start_tick: int,
    end_tick: int,
    role: str,
) -> _BoundSource:
    image, expected_visual = _image_and_values(visual_id)
    auditory_values = _auditory_values(auditory_id)
    raw_sha256 = hashlib.sha256(image.tobytes()).hexdigest()
    receptor_state = runtime.receptor.analyze(image, frame_index=runtime.image_serial)
    runtime.image_serial += 1
    visual_values = tuple(receptor_state.channel_values)
    _require(visual_values == expected_visual, "visual receptor values differ")
    auditory_frame = ReceptorContactFrame(
        "auditory",
        runtime.profile.auditory_config.geometry_id,
        f"{source_id}.auditory",
        "s2ig.auditory.clock",
        start_tick,
        end_tick,
        runtime.profile.auditory_config.carrier_ids,
        auditory_values,
    )
    visual_frame = ReceptorContactFrame(
        "visual",
        runtime.profile.visual_config.geometry_id,
        f"{source_id}.visual",
        "s2ig.visual.clock",
        start_tick,
        end_tick,
        runtime.profile.visual_config.carrier_ids,
        visual_values,
    )
    field_time = CommonFieldTime("s2ig.field.clock", start_tick, end_tick)
    batch = BrowserReceptorSequenceBatch(
        runtime.world.contract_id,
        runtime.world.digest(),
        (_timed(auditory_frame, field_time), _timed(visual_frame, field_time)),
    )
    _require(batch.raw_payloads_retained is False, "raw payload retention differs")
    envelope = bind_ppb1_active_receptor_batch(
        f"{source_id}.binding",
        runtime.world,
        batch,
        runtime.profile,
    )
    auditory_binding = envelope.auditory_stream.timed_frames[0]
    visual_binding = envelope.visual_stream.timed_frames[0]
    if role == "FORMATION":
        bound = coordinator.bind_coordinator_input(
            runtime.coordinator_config,
            envelope,
            auditory_binding,
            visual_binding,
        )
        bound_digest = bound.input_digest
    elif role == "READ_ONLY":
        bound = coordinator.bind_coordinator_probe(
            runtime.coordinator_config,
            envelope,
            auditory_binding,
            visual_binding,
        )
        bound_digest = bound.probe_digest
    else:
        raise S2IGRunnerError("source role differs")
    source_digest = fixtures.canonical_digest(
        {
            "schema": RUNNER_SCHEMA,
            "source_id": source_id,
            "role": role,
            "visual_fixture_id": visual_id,
            "auditory_fixture_id": auditory_id,
            "window": [start_tick, end_tick],
            "raw_sha256": raw_sha256,
            "bound_digest": bound_digest,
        }
    )
    return _BoundSource(
        role,
        source_id,
        visual_id,
        auditory_id,
        start_tick,
        end_tick,
        envelope,
        bound,
        raw_sha256,
        source_digest,
    )


def _formation(
    runtime: _Runtime,
    state: coordinator.B4TSPM1CompositeState,
    source: _BoundSource,
    history_id: str,
    ordinal: int,
) -> coordinator.B4TSPM1StepResult:
    _require(type(source.bound) is coordinator.B4TSPM1BoundInput, "formation source differs")
    identifiers = _formation_runtime_identifiers(history_id, ordinal)
    owner = coordinator.B4TSPM1CoordinatorOwner(
        identifiers.owner_id,
        identifiers.authorization_id,
        identifiers.consumption_id,
        runtime.coordinator_config.config_digest,
        state.state_digest,
        source.bound.input_digest,
    )
    return owner.consume_once(runtime.coordinator_config, state, source.bound)


def _probe(
    runtime: _Runtime,
    state: coordinator.B4TSPM1CompositeState,
    source: _BoundSource,
) -> coordinator.B4TSPM1ReadOnlyFinding:
    _require(type(source.bound) is coordinator.B4TSPM1BoundProbe, "probe source differs")
    return coordinator.probe_composite_read_only(runtime.coordinator_config, state, source.bound)


def _projection_binding(
    runtime: _Runtime,
    state: coordinator.B4TSPM1CompositeState,
    source: _BoundSource,
) -> context_bundle.PerceptualContextProjectionBinding:
    _require(type(source.bound) is coordinator.B4TSPM1BoundProbe, "projection source differs")
    return context_bundle.PerceptualContextProjectionBinding.build(
        config_digest=runtime.coordinator_config.config_digest,
        composite_state_digest=state.state_digest,
        probe_digest=source.bound.probe_digest,
        probe_values_digest=source.bound.values_digest,
        auditory_source_digest=source.bound.auditory.timed_frame_provenance_digest,
        visual_source_digest=source.bound.visual.timed_frame_provenance_digest,
        auditory_geometry_id=source.bound.auditory.timed_frame.frame.geometry_id,
        visual_geometry_id=source.bound.visual.timed_frame.frame.geometry_id,
        field_clock_id=source.bound.auditory.field_clock_id,
        window_start=source.window_start,
        window_end=source.window_end,
    )


def _record(
    recorder: recording.AppendOnlyRunRecorder,
    input_payload: dict[str, object],
    producer: Callable[[], object],
    projector: Callable[[object], dict[str, object]],
    *,
    external_parent_digest: str | None = None,
) -> _Recorded:
    row = recorder.current_row()
    recorder.start(row.operation_id, input_payload, external_parent_digest=external_parent_digest)
    value = producer()
    result_event = recorder.finish(row.operation_id, {"result": _canonical(projector(value))})
    return _Recorded(value, recorder.result_digests[row.operation_id], result_event)


def _receptor_receipt(source: object) -> dict[str, object]:
    _require(type(source) is _BoundSource, "receptor source differs")
    bound = source.bound
    return {
        "schema": "s2ig.compact-receptor-receipt.v1",
        "role": source.role,
        "source_id": source.source_id,
        "visual_fixture_id": source.visual_fixture_id,
        "auditory_fixture_id": source.auditory_fixture_id,
        "window": [source.window_start, source.window_end],
        "raw_sha256": source.raw_sha256,
        "auditory_values_digest": fixtures.canonical_digest(bound.auditory_values),
        "visual_values_digest": fixtures.canonical_digest(bound.visual_values),
        "av_values_digest": fixtures.canonical_digest(bound.av_values),
        "envelope_digest": source.envelope.envelope_digest,
        "bound_source_digest": getattr(bound, "input_digest", getattr(bound, "probe_digest", None)),
        "source_digest": source.source_digest,
        "raw_payload_retained": False,
    }


def _formation_receipt(result: object, receptor_receipt_digest: str) -> dict[str, object]:
    _require(type(result) is coordinator.B4TSPM1StepResult, "formation result differs")
    return {
        "schema": "s2ig.compact-formation-receipt.v1",
        "receptor_receipt_digest": receptor_receipt_digest,
        "prestate_digest": result.receipt.composite_prestate_digest,
        "poststate_digest": result.poststate.state_digest,
        "generation": result.poststate.generation,
        "b4_event": result.receipt.b4_event,
        "tspm_result_digest": result.receipt.tspm_result_digest,
        "step_receipt_digest": result.receipt.receipt_digest,
        "resource_ledger_digest": result.resource_ledger.ledger_digest,
        "result_digest": result.result_digest,
    }


def _finding_receipt(result: object, receptor_receipt_digest: str) -> dict[str, object]:
    _require(type(result) is coordinator.B4TSPM1ReadOnlyFinding, "read-only result differs")
    return {
        "schema": "s2ig.compact-read-only-receipt.v1",
        "receptor_receipt_digest": receptor_receipt_digest,
        "finding_digest": result.finding_digest,
        "probe_digest": result.probe_digest,
        "prestate_digest": result.prestate_digest,
        "poststate_digest": result.poststate_digest,
        "b4_status": "RECOGNIZED" if result.b4_recent.recognized else "NOT_RECOGNIZED",
        "fast_status": (
            "FUNCTIONAL_MATCH"
            if result.tspm_fast is not None and result.tspm_fast.functional_match
            else "PRESENT_NO_FUNCTIONAL_MATCH"
            if result.tspm_fast is not None
            else "ABSENT"
        ),
        "slow_statuses": tuple(item.native_status for item in result.tspm_slow),
        "slow_supports": tuple(
            None if item.selected is None else item.selected.support_count
            for item in result.tspm_slow
        ),
        "resource_ledger_digest": result.resource_ledger.ledger_digest,
    }


def _bundle_receipt(result: object, source_finding_artifact_digest: str) -> dict[str, object]:
    _require(type(result) is context_bundle.PerceptualContextBundle, "S2-GC bundle differs")
    return {
        "schema": "s2ig.compact-s2gc-receipt.v1",
        "source_finding_artifact_digest": source_finding_artifact_digest,
        "bundle_digest": result.bundle_digest,
        "binding_digest": result.binding_digest,
        "state_digest": result.composite_state_digest,
        "probe_digest": result.probe_digest,
        "role_statuses": tuple(item.status for item in result.role_findings),
        "role_finding_digests": tuple(item.finding_digest for item in result.role_findings),
        "candidate_digests": tuple(
            None if item.candidate is None else item.candidate.candidate_digest
            for item in result.role_findings
        ),
        "sequence_status": result.sequence_finding.status,
        "prestate_digest": result.prestate_digest,
        "poststate_digest": result.poststate_digest,
        "resource_ledger_digest": result.resource_ledger.ledger_digest,
    }


def _area_receipt(result: object, source_bundle_artifact_digest: str) -> dict[str, object]:
    _require(type(result) is two_area.TwoAreaContextBundle, "S2-GI bundle differs")
    return {
        "schema": "s2ig.compact-s2gi-receipt.v1",
        "source_bundle_artifact_digest": source_bundle_artifact_digest,
        "bundle_digest": result.bundle_digest,
        "source_bundle_digest": result.source_bundle_digest,
        "state_digest": result.composite_state_digest,
        "probe_digest": result.probe_digest,
        "area_finding_digests": tuple(item.finding_digest for item in result.area_findings),
        "a_recent_status": result.area_findings[0].recent_content.status,
        "a_fast_status": result.area_findings[0].fast_internal.status,
        "b_stable_status": result.area_findings[1].stable_content.status,
        "prestate_digest": result.prestate_digest,
        "poststate_digest": result.poststate_digest,
        "resource_ledger_digest": result.resource_ledger.ledger_digest,
        "automatic_selection": result.automatic_selection,
    }


def _case_plan_digest(
    case: fixtures.FunctionCaseFixture,
    runtime: _Runtime,
    registry_digest: str,
) -> str:
    return fixtures.canonical_digest(
        {
            "schema": "s2if.case-probe-plan.v1",
            "plan_id": case.case_plan_id,
            "history_id": case.history_id,
            "context_fixture_id": fixtures.HISTORY_BY_ID[case.history_id].retrieval_source.visual_id,
            "signal_fixture_id": case.signal_visual_id,
            "config_digest": runtime.coordinator_config.config_digest,
            "registry_digest": registry_digest,
            "context_role": "CONTEXT_RETRIEVAL_PROBE",
            "signal_role": "MASKED_SIGNAL_PROBE",
            "visible_positions": fixtures.VISIBLE_POSITIONS,
            "masked_positions": fixtures.MASKED_POSITIONS,
            "functional_budget_digest": fixtures.canonical_digest(fixtures.FUNCTIONAL_BUDGET),
        }
    )


def _context_probe(
    case_plan_digest: str,
    history_id: str,
    source: _BoundSource,
    receptor_receipt_digest: str,
    config_digest: str,
) -> ContextRetrievalProbe:
    _require(type(source.bound) is coordinator.B4TSPM1BoundProbe, "context probe source differs")
    payload = {
        "schema": "s2if.context-retrieval-probe.v1",
        "case_plan_digest": case_plan_digest,
        "role": "CONTEXT_RETRIEVAL_PROBE",
        "probe_id": f"s2ig.{history_id}.context-probe",
        "source_id": source.source_id,
        "source_digest": source.source_digest,
        "receptor_receipt_digest": receptor_receipt_digest,
        "config_digest": config_digest,
        "auditory_values_digest": fixtures.canonical_digest(source.bound.auditory_values),
        "visual_values_digest": fixtures.canonical_digest(source.bound.visual_values),
        "av_values_digest": fixtures.canonical_digest(source.bound.av_values),
        "function_probe_digest": source.bound.probe_digest,
        "value_dimension": 26,
        "window_start_tick": source.window_start,
        "window_end_tick": source.window_end,
    }
    return ContextRetrievalProbe(
        case_plan_digest,
        payload["probe_id"],
        source.source_id,
        source.source_digest,
        receptor_receipt_digest,
        config_digest,
        payload["auditory_values_digest"],
        payload["visual_values_digest"],
        payload["av_values_digest"],
        source.bound.probe_digest,
        source.window_start,
        source.window_end,
        fixtures.canonical_digest(payload),
    )


def _masked_signal_probe(
    case_plan_digest: str,
    case_id: str,
    source: _BoundSource,
    receptor_receipt_digest: str,
    config_digest: str,
) -> tuple[masked_contract.MaskedVisualProbe, MaskedSignalProbe]:
    _require(type(source.bound) is coordinator.B4TSPM1BoundProbe, "signal probe source differs")
    masked_values = tuple(
        value if index in fixtures.VISIBLE_POSITIONS else None
        for index, value in enumerate(source.bound.visual_values)
    )
    probe = masked_contract.MaskedVisualProbe.build(masked_values, source.source_digest)
    mask_digest = signal_contract.mask_digest_for(probe)
    payload = {
        "schema": "s2if.masked-signal-probe.v1",
        "case_plan_digest": case_plan_digest,
        "role": "MASKED_SIGNAL_PROBE",
        "probe_id": f"s2ig.{case_id}.signal-probe",
        "source_id": source.source_id,
        "source_digest": source.source_digest,
        "receptor_receipt_digest": receptor_receipt_digest,
        "config_digest": config_digest,
        "visual_values_digest": fixtures.canonical_digest(source.bound.visual_values),
        "visible_values_digest": fixtures.canonical_digest(
            tuple(source.bound.visual_values[index] for index in fixtures.VISIBLE_POSITIONS)
        ),
        "mask_digest": mask_digest,
        "masked_visual_probe_digest": probe.probe_digest,
        "visible_positions": fixtures.VISIBLE_POSITIONS,
        "masked_positions": fixtures.MASKED_POSITIONS,
        "value_dimension": 18,
        "window_start_tick": source.window_start,
        "window_end_tick": source.window_end,
    }
    wrapper = MaskedSignalProbe(
        case_plan_digest,
        payload["probe_id"],
        source.source_id,
        source.source_digest,
        receptor_receipt_digest,
        config_digest,
        payload["visual_values_digest"],
        payload["visible_values_digest"],
        mask_digest,
        probe.probe_digest,
        fixtures.VISIBLE_POSITIONS,
        fixtures.MASKED_POSITIONS,
        source.window_start,
        source.window_end,
        fixtures.canonical_digest(payload),
    )
    return probe, wrapper


def _signal_result_receipt(commit: object) -> dict[str, object]:
    _require(type(commit) is signal_contract.TwoAreaConflictSignalCommit, "signal commit differs")
    return CompactSignalArmReceiptV1.project(commit).payload()


def _execute(
    recorder: recording.AppendOnlyRunRecorder,
    runtime: _Runtime,
    evaluation_plan: EvaluationPlanSeal,
) -> None:
    states: dict[str, coordinator.B4TSPM1CompositeState] = {}
    context_sources: dict[str, _Recorded] = {}
    findings: dict[str, coordinator.B4TSPM1ReadOnlyFinding] = {}
    areas: dict[str, two_area.TwoAreaContextBundle] = {}
    history_evidence: dict[str, dict[str, object]] = {}
    history_evidence_artifacts: dict[str, str] = {}

    for history in fixtures.HISTORIES:
        recorded = _record(
            recorder,
            {"history_digest": history.history_digest},
            lambda: coordinator.initial_composite_state(runtime.coordinator_config),
            lambda result: {
                "schema": "s2ig.history-initial-receipt.v1",
                "history_digest": history.history_digest,
                "state_digest": result.state_digest,
                "generation": result.generation,
            },
        )
        _require(type(recorded.value) is coordinator.B4TSPM1CompositeState, "initial state differs")
        states[history.history_id] = recorded.value

    for history in fixtures.HISTORIES:
        state = states[history.history_id]
        for step in history.steps:
            source_id = f"s2ig.{history.history_id}.formation.{step.ordinal:02d}"
            receptor_record = _record(
                recorder,
                {"source_id": source_id, "history_id": history.history_id},
                lambda s=step, sid=source_id: _analyze(
                    runtime,
                    sid,
                    s.source.visual_id,
                    s.source.auditory_id,
                    s.window_start,
                    s.window_end,
                    "FORMATION",
                ),
                _receptor_receipt,
            )
            source = receptor_record.value
            formation_record = _record(
                recorder,
                {
                    "source_digest": source.source_digest,
                    "receptor_receipt_digest": receptor_record.artifact_digest,
                    "prestate_digest": state.state_digest,
                },
                lambda pre=state, s=source, h=history, n=step.ordinal: _formation(
                    runtime,
                    pre,
                    s,
                    h.history_id,
                    n,
                ),
                lambda result, parent=receptor_record.artifact_digest: _formation_receipt(result, parent),
            )
            _require(type(formation_record.value) is coordinator.B4TSPM1StepResult, "formation differs")
            state = formation_record.value.poststate
        states[history.history_id] = state

    for history in fixtures.HISTORIES:
        state = states[history.history_id]
        source_id = f"s2ig.{history.history_id}.context-retrieval"
        source_record = _record(
            recorder,
            {"source_id": source_id, "history_id": history.history_id},
            lambda h=history, sid=source_id: _analyze(
                runtime,
                sid,
                h.retrieval_source.visual_id,
                h.retrieval_source.auditory_id,
                h.probe_window_start,
                h.probe_window_end,
                "READ_ONLY",
            ),
            _receptor_receipt,
        )
        context_sources[history.history_id] = source_record
        finding_record = _record(
            recorder,
            {
                "source_digest": source_record.value.source_digest,
                "receptor_receipt_digest": source_record.artifact_digest,
                "state_digest": state.state_digest,
            },
            lambda source=source_record.value, pre=state: _probe(runtime, pre, source),
            lambda result, parent=source_record.artifact_digest: _finding_receipt(result, parent),
        )
        finding = finding_record.value
        findings[history.history_id] = finding
        binding = _projection_binding(runtime, state, source_record.value)
        sequence = context_bundle.ValidatedB4ShortSequenceEvidence.build(
            "NOT_REQUESTED",
            finding.b4_recent.observed_state_digest,
            finding.probe_digest,
        )
        bundle_record = _record(
            recorder,
            {"finding_digest": finding.finding_digest, "binding_digest": binding.binding_digest},
            lambda b=binding, f=finding, s=sequence: context_bundle.project_perceptual_context_bundle(b, f, s),
            lambda result, parent=finding_record.artifact_digest: _bundle_receipt(result, parent),
        )
        area_record = _record(
            recorder,
            {"source_bundle_digest": bundle_record.value.bundle_digest},
            lambda bundle=bundle_record.value: two_area.project_two_area_context(bundle),
            lambda result, parent=bundle_record.artifact_digest: _area_receipt(result, parent),
        )
        areas[history.history_id] = area_record.value
        evidence = {
            "schema": "s2ig.history-evidence.v1",
            "history_id": history.history_id,
            "history_digest": history.history_digest,
            "generation": state.generation,
            "state_digest": state.state_digest,
            "context_function_probe_digest": finding.probe_digest,
            "context_receptor_receipt_digest": source_record.artifact_digest,
            "finding_digest": finding.finding_digest,
            "s2gc_bundle_digest": bundle_record.value.bundle_digest,
            "s2gi_bundle_digest": area_record.value.bundle_digest,
            "a_recent_status": area_record.value.area_findings[0].recent_content.status,
            "b_stable_status": area_record.value.area_findings[1].stable_content.status,
            "read_only": finding.prestate_digest == finding.poststate_digest == state.state_digest,
        }
        sealed = _record(
            recorder,
            {"history_id": history.history_id, "state_digest": state.state_digest},
            lambda value=evidence: value,
            lambda value: value,
        )
        history_evidence[history.history_id] = evidence
        history_evidence_artifacts[history.history_id] = sealed.artifact_digest

    case_evidence: dict[str, dict[str, object]] = {}
    case_evidence_artifacts: dict[str, str] = {}
    for case in fixtures.FUNCTION_CASES:
        history = fixtures.HISTORY_BY_ID[case.history_id]
        area = areas[case.history_id]
        state = states[case.history_id]
        context_source_record = context_sources[case.history_id]
        case_plan_digest = _case_plan_digest(case, runtime, recorder.registry.bundle_digest)
        runtime_ids = _case_runtime_identifiers(case.case_id)
        signal_source_id = f"s2ig.{case.case_id}.masked-signal-source"
        signal_source_record = _record(
            recorder,
            {"case_plan_digest": case_plan_digest, "signal_source_id": signal_source_id},
            lambda c=case, h=history, sid=signal_source_id: _analyze(
                runtime,
                sid,
                c.signal_visual_id,
                h.retrieval_source.auditory_id,
                h.probe_window_end,
                h.probe_window_end + 1,
                "READ_ONLY",
            ),
            _receptor_receipt,
        )
        probe_record = _record(
            recorder,
            {
                "case_plan_digest": case_plan_digest,
                "signal_source_digest": signal_source_record.value.source_digest,
            },
            lambda c=case, source=signal_source_record.value, parent=signal_source_record.artifact_digest: _masked_signal_probe(
                case_plan_digest,
                c.case_id,
                source,
                parent,
                runtime.coordinator_config.config_digest,
            ),
            lambda result: {
                "schema": "s2if.masked-signal-probe-receipt.v1",
                "masked_signal_probe": _canonical(result[1]),
                "masked_visual_probe_digest": result[0].probe_digest,
            },
        )
        masked_probe, signal_wrapper = probe_record.value
        context_wrapper = _context_probe(
            case_plan_digest,
            case.history_id,
            context_source_record.value,
            context_source_record.artifact_digest,
            runtime.coordinator_config.config_digest,
        )
        _require(
            area.probe_digest == context_wrapper.function_probe_digest
            and masked_probe.probe_digest == signal_wrapper.masked_visual_probe_digest,
            "separate probe relations differ",
        )
        signal_input = signal_contract.TwoAreaConflictSignalInput.build(
            runtime_ids.signal_invocation_id,
            "SIGNAL",
            masked_probe,
            area,
        )
        baseline_input = signal_contract.TwoAreaConflictSignalInput.build(
            runtime_ids.baseline_invocation_id,
            "DIRECT_BASELINE",
            masked_probe,
            area,
        )
        dual_binding, _source_ledger = bind_dual_probe_case(
            context_wrapper,
            signal_wrapper,
            area,
            signal_input,
            baseline_input,
        )
        source_ledger_digest = dual_binding.source_ledger_digest
        dual_owner = DualProbeCaseOwner(runtime_ids.dual_owner_id, dual_binding)
        signal_owner = signal_contract.TwoAreaConflictSignalOwner(
            signal_contract.TwoAreaConflictOwnerPrestate.build(
                runtime_ids.signal_owner_id,
                signal_input,
            )
        )
        baseline_owner = signal_contract.TwoAreaConflictSignalOwner(
            signal_contract.TwoAreaConflictOwnerPrestate.build(
                runtime_ids.baseline_owner_id,
                baseline_input,
            )
        )
        dual_record = _record(
            recorder,
            {
                "case_plan_digest": case_plan_digest,
                "context_retrieval_probe_digest": context_wrapper.context_retrieval_probe_digest,
                "masked_signal_probe_digest": signal_wrapper.masked_signal_probe_digest,
            },
            lambda: (dual_binding, dual_owner.prestate, signal_input, baseline_input),
            lambda result: CompactDualProbeBindingReceiptV1.project(*result).payload(),
        )
        signal_record = _record(
            recorder,
            {"dual_probe_binding_digest": dual_binding.dual_probe_binding_digest},
            lambda: conflict_signal.form_two_area_conflict_signal(
                masked_probe,
                area,
                signal_input,
                signal_owner,
            ),
            _signal_result_receipt,
        )
        baseline_record = _record(
            recorder,
            {"dual_probe_binding_digest": dual_binding.dual_probe_binding_digest},
            lambda: direct_baseline.form_direct_two_area_conflict_baseline(
                masked_probe,
                area,
                baseline_input,
                baseline_owner,
            ),
            _signal_result_receipt,
        )
        signal_commit = signal_record.value
        baseline_commit = baseline_record.value
        owner_post = dual_owner.commit(
            dual_binding,
            signal_commit.result.result_digest,
            baseline_commit.result.result_digest,
        )
        owner_record = _record(
            recorder,
            {
                "signal_result_digest": signal_commit.result.result_digest,
                "baseline_result_digest": baseline_commit.result.result_digest,
            },
            lambda value=owner_post: value,
            lambda value: _canonical(value),
        )
        evidence = {
            "schema": "s2if.case-evidence.v1",
            "case_plan_digest": case_plan_digest,
            "context_retrieval_probe_digest": context_wrapper.context_retrieval_probe_digest,
            "context_function_probe_digest": context_wrapper.function_probe_digest,
            "masked_signal_probe_digest": signal_wrapper.masked_signal_probe_digest,
            "masked_visual_probe_digest": signal_wrapper.masked_visual_probe_digest,
            "dual_probe_binding_digest": dual_binding.dual_probe_binding_digest,
            "source_ledger_digest": source_ledger_digest,
            "owner_prestate_digest": dual_owner.prestate.owner_digest,
            "owner_poststate_digest": owner_post.owner_digest,
            "two_area_bundle_digest": area.bundle_digest,
            "bundle_context_probe_digest": area.probe_digest,
            "signal_input_digest": signal_input.input_digest,
            "signal_result_digest": signal_commit.result.result_digest,
            "signal_receipt_digest": signal_commit.receipt.receipt_digest,
            "baseline_input_digest": baseline_input.input_digest,
            "baseline_result_digest": baseline_commit.result.result_digest,
            "baseline_receipt_digest": baseline_commit.receipt.receipt_digest,
            "composite_prestate_digest": state.state_digest,
            "composite_poststate_digest": state.state_digest,
            "signal_ledger_digest": signal_commit.result.resource_ledger_digest,
            "baseline_ledger_digest": baseline_commit.result.resource_ledger_digest,
            "signal_status": signal_commit.result.status,
            "baseline_status": baseline_commit.result.status,
            "signal_equals_baseline": signal_commit.result.status == baseline_commit.result.status,
            "read_only": (
                signal_commit.result.prestate_digest
                == signal_commit.result.poststate_digest
                == baseline_commit.result.prestate_digest
                == baseline_commit.result.poststate_digest
                == state.state_digest
            ),
            "selected_area": None,
            "recommended_area": None,
            "automatic_selection": None,
            "dual_binding_artifact_digest": dual_record.artifact_digest,
            "signal_artifact_digest": signal_record.artifact_digest,
            "baseline_artifact_digest": baseline_record.artifact_digest,
            "owner_commit_artifact_digest": owner_record.artifact_digest,
        }
        sealed = _record(
            recorder,
            {"case_plan_digest": case_plan_digest, "owner_poststate_digest": owner_post.owner_digest},
            lambda value=evidence: value,
            lambda value: value,
        )
        case_evidence[case.case_id] = evidence
        case_evidence_artifacts[case.case_id] = sealed.artifact_digest

    execution_package_record = _record(
        recorder,
        {"operation_count_before_seal": 170},
        lambda: {
            "schema": "s2ie.execution-evidence-package.v1",
            "execution_plan_digest": recorder.plan.plan_digest,
            "history_evidence_artifact_digests": tuple(
                history_evidence_artifacts[item.history_id] for item in fixtures.HISTORIES
            ),
            "case_evidence_artifact_digests": tuple(
                case_evidence_artifacts[item.case_id] for item in fixtures.FUNCTION_CASES
            ),
            "event_count_before_seal": recorder.event_count,
            "last_execution_event_digest": recorder.previous_event_digest,
            "evaluation_plan_digest": None,
        },
        lambda value: value,
    )
    evaluation_binding_record = _record(
        recorder,
        {
            "execution_package_artifact_digest": execution_package_record.artifact_digest,
            "evaluation_plan_digest": evaluation_plan.seal_digest,
        },
        lambda: {
            "schema": "s2ie.evaluation-run-binding.v1",
            "execution_package_artifact_digest": execution_package_record.artifact_digest,
            "evaluation_plan_digest": evaluation_plan.seal_digest,
            "binding_digest": fixtures.canonical_digest(
                [execution_package_record.artifact_digest, evaluation_plan.seal_digest]
            ),
        },
        lambda value: value,
        external_parent_digest=evaluation_plan.seal_digest,
    )
    binding_by_case = {item.case_id: item for item in evaluation_plan.case_bindings}
    evaluations: dict[str, dict[str, object]] = {}
    for case in fixtures.FUNCTION_CASES:
        evidence = case_evidence[case.case_id]
        expected = binding_by_case[case.case_id].expected_status
        finding = {
            "schema": "s2ie.evaluation-finding.v1",
            "case_id": case.case_id,
            "evaluation_binding_digest": evaluation_binding_record.value["binding_digest"],
            "observed_status": evidence["signal_status"],
            "expected_status": expected,
            "status_matches": evidence["signal_status"] == expected,
            "signal_equals_baseline": evidence["signal_equals_baseline"],
            "read_only": evidence["read_only"],
            "method_valid": True,
        }
        recorded = _record(
            recorder,
            {"case_id": case.case_id, "evaluation_binding_digest": evaluation_binding_record.value["binding_digest"]},
            lambda value=finding: value,
            lambda value: value,
        )
        evaluations[case.case_id] = {**finding, "artifact_digest": recorded.artifact_digest}
    aggregate_record = _record(
        recorder,
        {"finding_count": 8},
        lambda: {
            "schema": "s2ie.aggregate-finding.v1",
            "finding_artifact_digests": tuple(evaluations[item.case_id]["artifact_digest"] for item in fixtures.FUNCTION_CASES),
            "all_expected": all(item["status_matches"] for item in evaluations.values()),
            "direct_comparison_explains": all(item["signal_equals_baseline"] for item in evaluations.values()),
            "all_read_only": all(item["read_only"] for item in evaluations.values()),
        },
        lambda value: value,
    )
    aggregate = aggregate_record.value
    terminal_record = _record(
        recorder,
        {"aggregate_artifact_digest": aggregate_record.artifact_digest},
        lambda: {
            "schema": "s2ie.terminal-finding.v1",
            "status": "COMPLETING",
            "functional_status": (
                "S2IE_REAL_TWO_AREA_STATUS_FUNCTION_VALID_DIRECT_COMPARISON_EXPLAINS"
                if aggregate["all_expected"]
                and aggregate["direct_comparison_explains"]
                and aggregate["all_read_only"]
                else "S2IE_REAL_TWO_AREA_STATUS_FUNCTION_FALSIFIED"
            ),
            "aggregate_artifact_digest": aggregate_record.artifact_digest,
        },
        lambda value: value,
    )
    _record(
        recorder,
        {"terminal_artifact_digest": terminal_record.artifact_digest},
        lambda: {
            "schema": "s2ie.completion-marker.v1",
            "status": "COMPLETE",
            "operation_count": fixtures.SUCCESS_OPERATION_COUNT,
            "event_count": fixtures.SUCCESS_EVENT_COUNT,
            "terminal_artifact_digest": terminal_record.artifact_digest,
        },
        lambda value: value,
    )


def run_main_once(
    output_root: Path,
    workspace_root: Path,
    run_id: str,
    owner_id: str,
    evaluation_plan: EvaluationPlanSeal,
) -> Path | recording.StartRejected:
    """Execute once only after an explicit caller opens this private gate."""

    global MAIN_EXECUTION_ENABLED
    try:
        if MAIN_EXECUTION_ENABLED is not True:
            raise S2IGRunnerError("S2-IG main execution gate is closed")
        if (
            not isinstance(output_root, Path)
            or not output_root.is_absolute()
            or not isinstance(workspace_root, Path)
            or not workspace_root.is_absolute()
            or type(evaluation_plan) is not EvaluationPlanSeal
        ):
            raise S2IGRunnerError("run boundary differs")
        plan, registry = materialize_execution_plan(workspace_root, run_id, owner_id)
        reserved = recording.AppendOnlyRunRecorder.reserve(output_root, plan, registry)
        if type(reserved) is recording.StartRejected:
            return reserved
        recorder = reserved
        try:
            _execute(recorder, _runtime(), evaluation_plan)
        except Exception as error:
            code = error.code if isinstance(error, recording.S2IGRecordingError) else "IG-E009"
            if recorder.state not in recording.TERMINAL_STATES:
                recorder.fail(code, recorder.current_row().operation_id)
            return recorder.run_directory
        _require(
            recorder.state == "COMPLETE"
            and recorder.next_operation_index == fixtures.SUCCESS_OPERATION_COUNT + 1
            and recorder.event_count == fixtures.SUCCESS_EVENT_COUNT,
            "completed run anatomy differs",
        )
        return recorder.run_directory
    finally:
        MAIN_EXECUTION_ENABLED = False


__all__: tuple[str, ...] = ()
