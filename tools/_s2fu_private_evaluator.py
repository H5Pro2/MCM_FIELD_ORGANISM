"""Pure evidence evaluator for the private S2-FU functional plan.

The evaluator accepts already produced evidence only. It imports no receptor,
memory, PPB-1, coordinator, runner, or persistence module and performs no file
operation. It never selects a preferred memory view.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re

from tools import _s2fu_private_fixtures as fixtures


S2FU_EVIDENCE_SCHEMA = "s2fu.private.evidence.v1"
S2FU_EVALUATION_SCHEMA = "s2fu.private.evaluation.v1"
S2FU_FUNCTION_CONFIRMED = "S2FU_FUNCTION_CONFIRMED"
S2FU_FUNCTION_FALSIFIED = "S2FU_FUNCTION_FALSIFIED"
S2FU_NOT_EVALUABLE = "NOT_EVALUABLE"

_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_ROLES = ("B4_RECENT", "TSPM_FAST", "TSPM_SLOW")


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


def _evidence_digest(item: object) -> str | None:
    if not hasattr(item, "payload_without_digest") or not hasattr(item, "evidence_digest"):
        return None
    try:
        return _digest(item.payload_without_digest())
    except (AttributeError, TypeError, ValueError):
        return None


@dataclass(frozen=True, slots=True)
class S2FUFormationEvidence:
    step: int
    evaluation_pattern_id: str
    config_digest: str
    source_digest: str
    input_digest: str
    window_start_tick: int
    window_end_tick: int
    auditory_fixture_binding_digest: str
    visual_analysis_digest: str
    synthetic_auditory_receptor_values: tuple[float, ...]
    visual_receptor_values: tuple[float, ...]
    composite_prestate_digest: str
    composite_poststate_digest: str
    b4_poststate_digest: str
    tspm_poststate_digest: str
    b4_event: str
    tspm_fast_event: str
    fast_loss_pattern_id: str | None
    ppb_calls_per_modality: int
    p1_slow_support: int
    p2_slow_support: int
    receipt_digest: str
    result_digest: str
    ledger_digest: str
    operator_input_fields: tuple[str, ...]
    evidence_digest: str
    schema: str = S2FU_EVIDENCE_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "step": self.step,
            "evaluation_pattern_id": self.evaluation_pattern_id,
            "config_digest": self.config_digest,
            "source_digest": self.source_digest,
            "input_digest": self.input_digest,
            "window_start_tick": self.window_start_tick,
            "window_end_tick": self.window_end_tick,
            "auditory_fixture_binding_digest": self.auditory_fixture_binding_digest,
            "visual_analysis_digest": self.visual_analysis_digest,
            "synthetic_auditory_receptor_values": list(
                self.synthetic_auditory_receptor_values
            ),
            "visual_receptor_values": list(self.visual_receptor_values),
            "composite_prestate_digest": self.composite_prestate_digest,
            "composite_poststate_digest": self.composite_poststate_digest,
            "b4_poststate_digest": self.b4_poststate_digest,
            "tspm_poststate_digest": self.tspm_poststate_digest,
            "b4_event": self.b4_event,
            "tspm_fast_event": self.tspm_fast_event,
            "fast_loss_pattern_id": self.fast_loss_pattern_id,
            "ppb_calls_per_modality": self.ppb_calls_per_modality,
            "p1_slow_support": self.p1_slow_support,
            "p2_slow_support": self.p2_slow_support,
            "receipt_digest": self.receipt_digest,
            "result_digest": self.result_digest,
            "ledger_digest": self.ledger_digest,
            "operator_input_fields": list(self.operator_input_fields),
        }


@dataclass(frozen=True, slots=True)
class S2FUComponentIdentityEvidence:
    step: int
    composite_generation: int
    standalone_b4_generation: int
    standalone_tspm_generation: int
    composite_b4_state_digest: str
    standalone_b4_state_digest: str
    composite_tspm_state_digest: str
    standalone_tspm_state_digest: str
    evidence_digest: str
    schema: str = S2FU_EVIDENCE_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "step": self.step,
            "composite_generation": self.composite_generation,
            "standalone_b4_generation": self.standalone_b4_generation,
            "standalone_tspm_generation": self.standalone_tspm_generation,
            "composite_b4_state_digest": self.composite_b4_state_digest,
            "standalone_b4_state_digest": self.standalone_b4_state_digest,
            "composite_tspm_state_digest": self.composite_tspm_state_digest,
            "standalone_tspm_state_digest": self.standalone_tspm_state_digest,
        }


@dataclass(frozen=True, slots=True)
class S2FUProbeSourceEvidence:
    fixture_probe_id: str
    role: str
    pattern_id: str
    config_digest: str
    source_digest: str
    probe_digest: str
    window_start_tick: int
    window_end_tick: int
    auditory_fixture_binding_digest: str
    visual_analysis_digest: str
    synthetic_auditory_receptor_values: tuple[float, ...]
    visual_receptor_values: tuple[float, ...]
    evidence_digest: str
    schema: str = S2FU_EVIDENCE_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "fixture_probe_id": self.fixture_probe_id,
            "role": self.role,
            "pattern_id": self.pattern_id,
            "config_digest": self.config_digest,
            "source_digest": self.source_digest,
            "probe_digest": self.probe_digest,
            "window_start_tick": self.window_start_tick,
            "window_end_tick": self.window_end_tick,
            "auditory_fixture_binding_digest": self.auditory_fixture_binding_digest,
            "visual_analysis_digest": self.visual_analysis_digest,
            "synthetic_auditory_receptor_values": list(
                self.synthetic_auditory_receptor_values
            ),
            "visual_receptor_values": list(self.visual_receptor_values),
        }


@dataclass(frozen=True, slots=True)
class S2FUSequenceEvidence:
    checkpoint_after_step: int
    config_digest: str
    b4_state_digest: str
    probe_fixture_ids: tuple[str, ...]
    probe_digests: tuple[str, ...]
    prestate_digest: str
    poststate_digest: str
    ordered_recognized: bool
    order_blind_recognized: bool
    tspm_sequence_status: str
    returned_value_digests: tuple[str, ...]
    evidence_digest: str
    schema: str = S2FU_EVIDENCE_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "checkpoint_after_step": self.checkpoint_after_step,
            "config_digest": self.config_digest,
            "b4_state_digest": self.b4_state_digest,
            "probe_fixture_ids": list(self.probe_fixture_ids),
            "probe_digests": list(self.probe_digests),
            "prestate_digest": self.prestate_digest,
            "poststate_digest": self.poststate_digest,
            "ordered_recognized": self.ordered_recognized,
            "order_blind_recognized": self.order_blind_recognized,
            "tspm_sequence_status": self.tspm_sequence_status,
            "returned_value_digests": list(self.returned_value_digests),
        }


@dataclass(frozen=True, slots=True)
class S2FUViewEvidence:
    target_pattern_id: str
    fixture_probe_id: str
    config_digest: str
    probe_digest: str
    composite_state_digest: str
    roles: tuple[str, ...]
    composite_prestate_digest: str
    composite_poststate_digest: str
    standalone_b4_prestate_digest: str
    standalone_b4_poststate_digest: str
    standalone_tspm_prestate_digest: str
    standalone_tspm_poststate_digest: str
    b4_recognized: bool
    standalone_b4_recognized: bool
    fast_recognized: bool
    standalone_fast_recognized: bool
    auditory_slow_support: int
    auditory_slow_stable: bool
    auditory_slow_recognized: bool
    standalone_auditory_slow_support: int
    standalone_auditory_slow_stable: bool
    standalone_auditory_slow_recognized: bool
    visual_slow_support: int
    visual_slow_stable: bool
    visual_slow_recognized: bool
    standalone_visual_slow_support: int
    standalone_visual_slow_stable: bool
    standalone_visual_slow_recognized: bool
    evidence_digest: str
    schema: str = S2FU_EVIDENCE_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "target_pattern_id": self.target_pattern_id,
            "fixture_probe_id": self.fixture_probe_id,
            "config_digest": self.config_digest,
            "probe_digest": self.probe_digest,
            "composite_state_digest": self.composite_state_digest,
            "roles": list(self.roles),
            "composite_prestate_digest": self.composite_prestate_digest,
            "composite_poststate_digest": self.composite_poststate_digest,
            "standalone_b4_prestate_digest": self.standalone_b4_prestate_digest,
            "standalone_b4_poststate_digest": self.standalone_b4_poststate_digest,
            "standalone_tspm_prestate_digest": self.standalone_tspm_prestate_digest,
            "standalone_tspm_poststate_digest": self.standalone_tspm_poststate_digest,
            "b4_recognized": self.b4_recognized,
            "standalone_b4_recognized": self.standalone_b4_recognized,
            "fast_recognized": self.fast_recognized,
            "standalone_fast_recognized": self.standalone_fast_recognized,
            "auditory_slow_support": self.auditory_slow_support,
            "auditory_slow_stable": self.auditory_slow_stable,
            "auditory_slow_recognized": self.auditory_slow_recognized,
            "standalone_auditory_slow_support": self.standalone_auditory_slow_support,
            "standalone_auditory_slow_stable": self.standalone_auditory_slow_stable,
            "standalone_auditory_slow_recognized": self.standalone_auditory_slow_recognized,
            "visual_slow_support": self.visual_slow_support,
            "visual_slow_stable": self.visual_slow_stable,
            "visual_slow_recognized": self.visual_slow_recognized,
            "standalone_visual_slow_support": self.standalone_visual_slow_support,
            "standalone_visual_slow_stable": self.standalone_visual_slow_stable,
            "standalone_visual_slow_recognized": self.standalone_visual_slow_recognized,
        }


@dataclass(frozen=True, slots=True)
class S2FULedgerEvidence:
    resource_digest: str
    unique_receptor_analyses: int
    composite_formations: int
    standalone_b4_formations: int
    standalone_tspm_formations: int
    component_identity_checks: int
    unique_probe_inputs: int
    high_level_read_only_calls: int
    composite_formation_words: int
    composite_formation_distance_terms: int
    composite_control_terms: int
    evidence_digest: str
    schema: str = S2FU_EVIDENCE_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "resource_digest": self.resource_digest,
            "unique_receptor_analyses": self.unique_receptor_analyses,
            "composite_formations": self.composite_formations,
            "standalone_b4_formations": self.standalone_b4_formations,
            "standalone_tspm_formations": self.standalone_tspm_formations,
            "component_identity_checks": self.component_identity_checks,
            "unique_probe_inputs": self.unique_probe_inputs,
            "high_level_read_only_calls": self.high_level_read_only_calls,
            "composite_formation_words": self.composite_formation_words,
            "composite_formation_distance_terms": self.composite_formation_distance_terms,
            "composite_control_terms": self.composite_control_terms,
        }


@dataclass(frozen=True, slots=True)
class S2FUEvidenceBundle:
    fixture_digest: str
    config_digest: str
    source_hashes: tuple[tuple[str, str], ...]
    formations: tuple[S2FUFormationEvidence, ...]
    component_identities: tuple[S2FUComponentIdentityEvidence, ...]
    probe_sources: tuple[S2FUProbeSourceEvidence, ...]
    sequence: S2FUSequenceEvidence
    views: tuple[S2FUViewEvidence, ...]
    ledger: S2FULedgerEvidence
    recording_complete: bool
    bundle_digest: str
    schema: str = S2FU_EVIDENCE_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "fixture_digest": self.fixture_digest,
            "config_digest": self.config_digest,
            "source_hashes": [list(item) for item in self.source_hashes],
            "formation_digests": [item.evidence_digest for item in self.formations],
            "component_identity_digests": [
                item.evidence_digest for item in self.component_identities
            ],
            "probe_source_digests": [item.evidence_digest for item in self.probe_sources],
            "sequence_digest": self.sequence.evidence_digest,
            "view_digests": [item.evidence_digest for item in self.views],
            "ledger_digest": self.ledger.evidence_digest,
            "recording_complete": self.recording_complete,
        }


@dataclass(frozen=True, slots=True)
class S2FUEvaluation:
    status: str
    method_issues: tuple[str, ...]
    functional_findings: tuple[str, ...]
    p2_unstable_trace_present: bool
    automatic_view_selection: None
    evaluated_bundle_digest: str | None
    evaluation_digest: str
    schema: str = S2FU_EVALUATION_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "status": self.status,
            "method_issues": list(self.method_issues),
            "functional_findings": list(self.functional_findings),
            "p2_unstable_trace_present": self.p2_unstable_trace_present,
            "automatic_view_selection": self.automatic_view_selection,
            "evaluated_bundle_digest": self.evaluated_bundle_digest,
        }


def _evaluation(
    status: str,
    method_issues: list[str],
    functional_findings: list[str],
    p2_unstable_trace_present: bool,
    bundle_digest: str | None,
) -> S2FUEvaluation:
    payload = {
        "schema": S2FU_EVALUATION_SCHEMA,
        "status": status,
        "method_issues": sorted(set(method_issues)),
        "functional_findings": sorted(set(functional_findings)),
        "p2_unstable_trace_present": p2_unstable_trace_present,
        "automatic_view_selection": None,
        "evaluated_bundle_digest": bundle_digest,
    }
    return S2FUEvaluation(
        status,
        tuple(payload["method_issues"]),
        tuple(payload["functional_findings"]),
        p2_unstable_trace_present,
        None,
        bundle_digest,
        _digest(payload),
    )


def _check_digest_shape(items: tuple[object, ...], role: str, issues: list[str]) -> None:
    for index, item in enumerate(items, start=1):
        if not _valid_digest(getattr(item, "evidence_digest", None)):
            issues.append(f"{role}_{index:02d}_DIGEST_SHAPE")
        elif _evidence_digest(item) != item.evidence_digest:
            issues.append(f"{role}_{index:02d}_DIGEST_MISMATCH")


def _exact_values(value: object, expected: tuple[float, ...]) -> bool:
    return (
        type(value) is tuple
        and len(value) == len(expected)
        and all(type(item) in (int, float) for item in value)
        and tuple(float(item) for item in value) == expected
    )


def _validate_method(bundle: S2FUEvidenceBundle) -> list[str]:
    issues: list[str] = []
    if bundle.schema != S2FU_EVIDENCE_SCHEMA:
        issues.append("BUNDLE_SCHEMA")
    if bundle.fixture_digest != fixtures.FIXTURE_DIGEST:
        issues.append("FIXTURE_DIGEST")
    if not _valid_digest(bundle.config_digest):
        issues.append("CONFIG_DIGEST")
    if bundle.source_hashes != fixtures.SOURCE_HASHES:
        issues.append("SOURCE_HASHES")
    if bundle.recording_complete is not True:
        issues.append("RECORDING_INCOMPLETE")
    if type(bundle.source_hashes) is not tuple:
        issues.append("SOURCE_HASH_COLLECTION_TYPE")
    if type(bundle.formations) is not tuple or not all(
        type(item) is S2FUFormationEvidence for item in bundle.formations
    ):
        issues.append("FORMATION_COLLECTION_TYPE")
    if type(bundle.component_identities) is not tuple or not all(
        type(item) is S2FUComponentIdentityEvidence for item in bundle.component_identities
    ):
        issues.append("COMPONENT_COLLECTION_TYPE")
    if type(bundle.probe_sources) is not tuple or not all(
        type(item) is S2FUProbeSourceEvidence for item in bundle.probe_sources
    ):
        issues.append("PROBE_SOURCE_COLLECTION_TYPE")
    if type(bundle.sequence) is not S2FUSequenceEvidence:
        issues.append("SEQUENCE_TYPE")
    if type(bundle.views) is not tuple or not all(
        type(item) is S2FUViewEvidence for item in bundle.views
    ):
        issues.append("VIEW_COLLECTION_TYPE")
    if type(bundle.ledger) is not S2FULedgerEvidence:
        issues.append("LEDGER_TYPE")
    if len(bundle.formations) != 18:
        issues.append("FORMATION_COUNT")
    if len(bundle.component_identities) != 18:
        issues.append("COMPONENT_IDENTITY_COUNT")
    if len(bundle.probe_sources) != 6:
        issues.append("PROBE_SOURCE_COUNT")
    if len(bundle.views) != 2:
        issues.append("VIEW_COUNT")

    _check_digest_shape(tuple(bundle.formations), "FORMATION", issues)
    _check_digest_shape(tuple(bundle.component_identities), "COMPONENT", issues)
    _check_digest_shape(tuple(bundle.probe_sources), "PROBE_SOURCE", issues)
    _check_digest_shape((bundle.sequence,), "SEQUENCE", issues)
    _check_digest_shape(tuple(bundle.views), "VIEW", issues)
    _check_digest_shape((bundle.ledger,), "LEDGER", issues)

    if _valid_digest(bundle.bundle_digest):
        if _digest(bundle.payload_without_digest()) != bundle.bundle_digest:
            issues.append("BUNDLE_DIGEST_MISMATCH")
    else:
        issues.append("BUNDLE_DIGEST_SHAPE")

    if len(bundle.formations) == 18:
        for expected, item in zip(fixtures.STEP_EXPECTATIONS, bundle.formations):
            if (
                item.schema != S2FU_EVIDENCE_SCHEMA
                or item.step != expected.step
                or item.config_digest != bundle.config_digest
                or item.operator_input_fields != fixtures.OPERATOR_INPUT_FIELDS
                or not all(
                    _valid_digest(value)
                    for value in (
                        item.source_digest,
                        item.input_digest,
                        item.auditory_fixture_binding_digest,
                        item.visual_analysis_digest,
                        item.composite_prestate_digest,
                        item.composite_poststate_digest,
                        item.b4_poststate_digest,
                        item.tspm_poststate_digest,
                        item.receipt_digest,
                        item.result_digest,
                        item.ledger_digest,
                    )
                )
            ):
                issues.append(f"FORMATION_{expected.step:02d}_BINDING")
            if item.evaluation_pattern_id != expected.pattern_id:
                issues.append(f"FORMATION_{expected.step:02d}_EVALUATION_METADATA")
            pattern = fixtures.PATTERN_BY_ID[expected.pattern_id]
            exposure = fixtures.EXPOSURES[expected.step - 1]
            if (
                item.window_start_tick != exposure.window_start_tick
                or item.window_end_tick != exposure.window_end_tick
                or item.auditory_fixture_binding_digest == item.visual_analysis_digest
                or not _exact_values(
                    item.synthetic_auditory_receptor_values,
                    tuple(float(value) for value in pattern.auditory_values),
                )
                or not _exact_values(item.visual_receptor_values, pattern.visual_values)
            ):
                issues.append(f"FORMATION_{expected.step:02d}_RECEPTOR_VALUES_OR_TIME")

    if len(bundle.component_identities) == 18 and len(bundle.formations) == 18:
        for step, (identity, formation) in enumerate(
            zip(bundle.component_identities, bundle.formations),
            start=1,
        ):
            if (
                identity.schema != S2FU_EVIDENCE_SCHEMA
                or identity.step != step
                or identity.composite_generation != step
                or identity.standalone_b4_generation != step
                or identity.standalone_tspm_generation != step
                or identity.composite_b4_state_digest != identity.standalone_b4_state_digest
                or identity.composite_tspm_state_digest != identity.standalone_tspm_state_digest
                or identity.composite_b4_state_digest != formation.b4_poststate_digest
                or identity.composite_tspm_state_digest != formation.tspm_poststate_digest
            ):
                issues.append(f"COMPONENT_{step:02d}_IDENTITY")

    if len(bundle.probe_sources) == 6:
        for expected, source in zip(fixtures.PROBES, bundle.probe_sources):
            pattern = fixtures.PATTERN_BY_ID[expected.pattern_id]
            if (
                type(source) is not S2FUProbeSourceEvidence
                or source.schema != S2FU_EVIDENCE_SCHEMA
                or source.fixture_probe_id != expected.probe_id
                or source.role != expected.role
                or source.pattern_id != expected.pattern_id
                or source.config_digest != bundle.config_digest
                or not _valid_digest(source.source_digest)
                or not _valid_digest(source.probe_digest)
                or source.window_start_tick != expected.window_start_tick
                or source.window_end_tick != expected.window_end_tick
                or not _valid_digest(source.auditory_fixture_binding_digest)
                or not _valid_digest(source.visual_analysis_digest)
                or source.auditory_fixture_binding_digest == source.visual_analysis_digest
                or not _exact_values(
                    source.synthetic_auditory_receptor_values,
                    tuple(float(value) for value in pattern.auditory_values),
                )
                or not _exact_values(source.visual_receptor_values, pattern.visual_values)
            ):
                issues.append(f"PROBE_SOURCE_{expected.ordinal:02d}_{expected.role}_BINDING")

    sequence = bundle.sequence
    if len(bundle.component_identities) >= 4:
        step4_b4_digest = bundle.component_identities[3].composite_b4_state_digest
    else:
        step4_b4_digest = None
    early_sources = tuple(bundle.probe_sources[:4])
    if (
        type(sequence) is not S2FUSequenceEvidence
        or sequence.schema != S2FU_EVIDENCE_SCHEMA
        or sequence.checkpoint_after_step != 4
        or sequence.config_digest != bundle.config_digest
        or sequence.b4_state_digest != step4_b4_digest
        or sequence.prestate_digest != sequence.poststate_digest
        or sequence.probe_fixture_ids != tuple(item.fixture_probe_id for item in early_sources)
        or sequence.probe_digests != tuple(item.probe_digest for item in early_sources)
        or len(sequence.probe_digests) != 4
        or not all(_valid_digest(value) for value in sequence.probe_digests)
        or len(sequence.returned_value_digests) != 4
        or not all(_valid_digest(value) for value in sequence.returned_value_digests)
    ):
        issues.append("SEQUENCE_BINDING_OR_READ_ONLY")

    final_composite_digest = (
        bundle.formations[-1].composite_poststate_digest if len(bundle.formations) == 18 else None
    )
    expected_targets = ("P1", "P2")
    final_sources = tuple(bundle.probe_sources[4:])
    if len(bundle.views) == 2:
        for expected_target, expected_source, view in zip(
            expected_targets,
            final_sources,
            bundle.views,
        ):
            digest_fields = (
                view.probe_digest,
                view.composite_state_digest,
                view.composite_prestate_digest,
                view.composite_poststate_digest,
                view.standalone_b4_prestate_digest,
                view.standalone_b4_poststate_digest,
                view.standalone_tspm_prestate_digest,
                view.standalone_tspm_poststate_digest,
            )
            if (
                view.schema != S2FU_EVIDENCE_SCHEMA
                or view.target_pattern_id != expected_target
                or view.fixture_probe_id != expected_source.fixture_probe_id
                or view.probe_digest != expected_source.probe_digest
                or view.config_digest != bundle.config_digest
                or view.roles != _ROLES
                or view.composite_state_digest != final_composite_digest
                or not all(_valid_digest(value) for value in digest_fields)
                or view.composite_prestate_digest != view.composite_poststate_digest
                or view.composite_prestate_digest != view.composite_state_digest
                or view.standalone_b4_prestate_digest != view.standalone_b4_poststate_digest
                or view.standalone_tspm_prestate_digest != view.standalone_tspm_poststate_digest
            ):
                issues.append(f"VIEW_{expected_target}_BINDING_OR_READ_ONLY")
            if (
                view.b4_recognized != view.standalone_b4_recognized
                or view.fast_recognized != view.standalone_fast_recognized
                or view.auditory_slow_support != view.standalone_auditory_slow_support
                or view.auditory_slow_stable != view.standalone_auditory_slow_stable
                or view.auditory_slow_recognized
                != view.standalone_auditory_slow_recognized
                or view.visual_slow_support != view.standalone_visual_slow_support
                or view.visual_slow_stable != view.standalone_visual_slow_stable
                or view.visual_slow_recognized != view.standalone_visual_slow_recognized
            ):
                issues.append(f"VIEW_{expected_target}_COMPONENT_REFERENCE")

    ledger = bundle.ledger
    resource = fixtures.RESOURCES
    if (
        type(ledger) is not S2FULedgerEvidence
        or ledger.schema != S2FU_EVIDENCE_SCHEMA
        or ledger.resource_digest != resource.resource_digest
        or ledger.unique_receptor_analyses != resource.unique_receptor_analyses
        or ledger.composite_formations != resource.composite_formations
        or ledger.standalone_b4_formations != resource.standalone_b4_formations
        or ledger.standalone_tspm_formations != resource.standalone_tspm_formations
        or ledger.component_identity_checks != resource.component_identity_checks
        or ledger.unique_probe_inputs != len(fixtures.PROBES)
        or ledger.high_level_read_only_calls != 7
        or ledger.composite_formation_words != resource.composite_formation_words
        or ledger.composite_formation_distance_terms
        != resource.composite_formation_distance_terms
        or ledger.composite_control_terms != resource.composite_control_terms
    ):
        issues.append("RESOURCE_LEDGER")
    return issues


def _functional_findings(bundle: S2FUEvidenceBundle) -> tuple[list[str], bool]:
    findings: list[str] = []
    for expected, item in zip(fixtures.STEP_EXPECTATIONS, bundle.formations):
        if item.b4_event != expected.b4_event:
            findings.append(f"STEP_{expected.step:02d}_B4_EVENT")
        if item.tspm_fast_event != expected.tspm_fast_event:
            findings.append(f"STEP_{expected.step:02d}_TSPM_EVENT")
        if item.fast_loss_pattern_id != expected.fast_loss_pattern_id:
            findings.append(f"STEP_{expected.step:02d}_FAST_LOSS")
        if item.ppb_calls_per_modality != expected.ppb_calls_per_modality:
            findings.append(f"STEP_{expected.step:02d}_PPB_CALLS")
        if item.p1_slow_support != expected.p1_slow_support:
            findings.append(f"STEP_{expected.step:02d}_P1_SUPPORT")
        if item.p2_slow_support != expected.p2_slow_support:
            findings.append(f"STEP_{expected.step:02d}_P2_SUPPORT")

    sequence = bundle.sequence
    if not sequence.ordered_recognized:
        findings.append("EARLY_B4_ORDER_NOT_RECOGNIZED")
    if not sequence.order_blind_recognized:
        findings.append("EARLY_B4_CONTENT_SET_NOT_RECOGNIZED")
    if sequence.tspm_sequence_status != "NOT_REPRESENTABLE_BY_CURRENT_TSPM1_STATE":
        findings.append("TSPM_SEQUENCE_ORDER_CLAIMED")

    views = {view.target_pattern_id: view for view in bundle.views}
    p1 = views["P1"]
    p2 = views["P2"]
    if p1.b4_recognized:
        findings.append("P1_REMAINS_IN_B4")
    if p1.fast_recognized:
        findings.append("P1_REMAINS_IN_FAST")
    if not (
        p1.auditory_slow_support == 3
        and p1.auditory_slow_stable
        and p1.auditory_slow_recognized
        and p1.visual_slow_support == 3
        and p1.visual_slow_stable
        and p1.visual_slow_recognized
    ):
        findings.append("P1_STABLE_SLOW_NOT_CONFIRMED")
    if p2.b4_recognized:
        findings.append("P2_REMAINS_IN_B4")
    if p2.fast_recognized:
        findings.append("P2_REMAINS_IN_FAST")
    p2_unstable_trace = (
        p2.auditory_slow_support == 1
        and not p2.auditory_slow_stable
        and not p2.auditory_slow_recognized
        and p2.visual_slow_support == 1
        and not p2.visual_slow_stable
        and not p2.visual_slow_recognized
    )
    if not p2_unstable_trace:
        findings.append("P2_UNSTABLE_TRACE_MISMATCH")
    return findings, p2_unstable_trace


def evaluate_s2fu(evidence: object) -> S2FUEvaluation:
    """Classify one immutable evidence bundle without calling project state functions."""

    if type(evidence) is not S2FUEvidenceBundle:
        return _evaluation(
            S2FU_NOT_EVALUABLE,
            ["EXACT_EVIDENCE_BUNDLE_REQUIRED"],
            [],
            False,
            None,
        )
    try:
        method_issues = _validate_method(evidence)
    except (AttributeError, IndexError, KeyError, TypeError, ValueError):
        return _evaluation(
            S2FU_NOT_EVALUABLE,
            ["MALFORMED_EVIDENCE_STRUCTURE"],
            [],
            False,
            evidence.bundle_digest if _valid_digest(evidence.bundle_digest) else None,
        )
    if method_issues:
        return _evaluation(
            S2FU_NOT_EVALUABLE,
            method_issues,
            [],
            False,
            evidence.bundle_digest if _valid_digest(evidence.bundle_digest) else None,
        )
    try:
        functional_findings, p2_trace = _functional_findings(evidence)
    except (AttributeError, IndexError, KeyError, TypeError, ValueError):
        return _evaluation(
            S2FU_NOT_EVALUABLE,
            ["MALFORMED_FUNCTIONAL_EVIDENCE"],
            [],
            False,
            evidence.bundle_digest,
        )
    status = S2FU_FUNCTION_FALSIFIED if functional_findings else S2FU_FUNCTION_CONFIRMED
    return _evaluation(
        status,
        [],
        functional_findings,
        p2_trace,
        evidence.bundle_digest,
    )
