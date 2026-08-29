"""Neutral qualification of the private S2-FU fixtures and pure evaluator.

All evidence in this module is synthetic contract evidence. It is not an
experimental result and does not call receptor, memory, coordinator, runner,
or persistence code.
"""

from __future__ import annotations

from dataclasses import replace
from fractions import Fraction
import hashlib
import json
import unittest

from tools import _s2fu_private_evaluator as evaluator
from tools import _s2fu_private_fixtures as fixtures


RUN_ID = "s2fu-fixture-evaluator-qualification-20260829-01"


def _digest(label: str) -> str:
    return hashlib.sha256(label.encode("ascii")).hexdigest()


def _payload_digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _seal(item):
    return replace(
        item,
        evidence_digest=_payload_digest(item.payload_without_digest()),
    )


def _seal_bundle(bundle: evaluator.S2FUEvidenceBundle) -> evaluator.S2FUEvidenceBundle:
    unsealed = replace(bundle, bundle_digest="")
    return replace(
        unsealed,
        bundle_digest=_payload_digest(unsealed.payload_without_digest()),
    )


def _formation_and_identity(
    expectation: fixtures.S2FUStepExpectation,
    previous_composite_digest: str,
    config_digest: str,
):
    step = expectation.step
    pattern = fixtures.PATTERN_BY_ID[expectation.pattern_id]
    exposure = fixtures.EXPOSURES[step - 1]
    b4_digest = _digest(f"b4-state-{step:02d}")
    tspm_digest = _digest(f"tspm-state-{step:02d}")
    composite_digest = _digest(f"composite-state-{step:02d}")
    formation = _seal(
        evaluator.S2FUFormationEvidence(
            step=step,
            evaluation_pattern_id=expectation.pattern_id,
            config_digest=config_digest,
            source_digest=_digest(f"source-{step:02d}"),
            input_digest=_digest(f"input-{step:02d}"),
            window_start_tick=exposure.window_start_tick,
            window_end_tick=exposure.window_end_tick,
            auditory_fixture_binding_digest=_digest(f"auditory-binding-{step:02d}"),
            visual_analysis_digest=_digest(f"visual-analysis-{step:02d}"),
            synthetic_auditory_receptor_values=tuple(
                float(value) for value in pattern.auditory_values
            ),
            visual_receptor_values=pattern.visual_values,
            composite_prestate_digest=previous_composite_digest,
            composite_poststate_digest=composite_digest,
            b4_poststate_digest=b4_digest,
            tspm_poststate_digest=tspm_digest,
            b4_event=expectation.b4_event,
            tspm_fast_event=expectation.tspm_fast_event,
            fast_loss_pattern_id=expectation.fast_loss_pattern_id,
            ppb_calls_per_modality=expectation.ppb_calls_per_modality,
            p1_slow_support=expectation.p1_slow_support,
            p2_slow_support=expectation.p2_slow_support,
            receipt_digest=_digest(f"receipt-{step:02d}"),
            result_digest=_digest(f"result-{step:02d}"),
            ledger_digest=_digest(f"ledger-step-{step:02d}"),
            operator_input_fields=fixtures.OPERATOR_INPUT_FIELDS,
            evidence_digest="",
        )
    )
    identity = _seal(
        evaluator.S2FUComponentIdentityEvidence(
            step=step,
            composite_generation=step,
            standalone_b4_generation=step,
            standalone_tspm_generation=step,
            composite_b4_state_digest=b4_digest,
            standalone_b4_state_digest=b4_digest,
            composite_tspm_state_digest=tspm_digest,
            standalone_tspm_state_digest=tspm_digest,
            evidence_digest="",
        )
    )
    return formation, identity


def _probe_source(
    probe: fixtures.S2FUProbeFixture,
    config_digest: str,
) -> evaluator.S2FUProbeSourceEvidence:
    pattern = fixtures.PATTERN_BY_ID[probe.pattern_id]
    return _seal(
        evaluator.S2FUProbeSourceEvidence(
            fixture_probe_id=probe.probe_id,
            role=probe.role,
            pattern_id=probe.pattern_id,
            config_digest=config_digest,
            source_digest=_digest(f"probe-source-{probe.probe_id}"),
            probe_digest=_digest(f"probe-input-{probe.probe_id}"),
            window_start_tick=probe.window_start_tick,
            window_end_tick=probe.window_end_tick,
            auditory_fixture_binding_digest=_digest(
                f"probe-auditory-binding-{probe.probe_id}"
            ),
            visual_analysis_digest=_digest(f"probe-visual-analysis-{probe.probe_id}"),
            synthetic_auditory_receptor_values=tuple(
                float(value) for value in pattern.auditory_values
            ),
            visual_receptor_values=pattern.visual_values,
            evidence_digest="",
        )
    )


def _view(
    target: str,
    probe: evaluator.S2FUProbeSourceEvidence,
    config_digest: str,
    final_composite_digest: str,
    final_b4_digest: str,
    final_tspm_digest: str,
) -> evaluator.S2FUViewEvidence:
    if target == "P1":
        support = 3
        stable = True
        recognized = True
    else:
        support = 1
        stable = False
        recognized = False
    return _seal(
        evaluator.S2FUViewEvidence(
            target_pattern_id=target,
            fixture_probe_id=probe.fixture_probe_id,
            config_digest=config_digest,
            probe_digest=probe.probe_digest,
            composite_state_digest=final_composite_digest,
            roles=("B4_RECENT", "TSPM_FAST", "TSPM_SLOW"),
            composite_prestate_digest=final_composite_digest,
            composite_poststate_digest=final_composite_digest,
            standalone_b4_prestate_digest=final_b4_digest,
            standalone_b4_poststate_digest=final_b4_digest,
            standalone_tspm_prestate_digest=final_tspm_digest,
            standalone_tspm_poststate_digest=final_tspm_digest,
            b4_recognized=False,
            standalone_b4_recognized=False,
            fast_recognized=False,
            standalone_fast_recognized=False,
            auditory_slow_support=support,
            auditory_slow_stable=stable,
            auditory_slow_recognized=recognized,
            standalone_auditory_slow_support=support,
            standalone_auditory_slow_stable=stable,
            standalone_auditory_slow_recognized=recognized,
            visual_slow_support=support,
            visual_slow_stable=stable,
            visual_slow_recognized=recognized,
            standalone_visual_slow_support=support,
            standalone_visual_slow_stable=stable,
            standalone_visual_slow_recognized=recognized,
            evidence_digest="",
        )
    )


def _valid_bundle() -> evaluator.S2FUEvidenceBundle:
    config_digest = _digest("s2fu-qualification-config")
    formations = []
    identities = []
    previous_composite_digest = _digest("initial-composite-state")
    for expectation in fixtures.STEP_EXPECTATIONS:
        formation, identity = _formation_and_identity(
            expectation,
            previous_composite_digest,
            config_digest,
        )
        formations.append(formation)
        identities.append(identity)
        previous_composite_digest = formation.composite_poststate_digest

    probe_sources = tuple(
        _probe_source(probe, config_digest) for probe in fixtures.PROBES
    )
    sequence = _seal(
        evaluator.S2FUSequenceEvidence(
            checkpoint_after_step=4,
            config_digest=config_digest,
            b4_state_digest=identities[3].composite_b4_state_digest,
            probe_fixture_ids=tuple(item.fixture_probe_id for item in probe_sources[:4]),
            probe_digests=tuple(item.probe_digest for item in probe_sources[:4]),
            prestate_digest=identities[3].composite_b4_state_digest,
            poststate_digest=identities[3].composite_b4_state_digest,
            ordered_recognized=True,
            order_blind_recognized=True,
            tspm_sequence_status="NOT_REPRESENTABLE_BY_CURRENT_TSPM1_STATE",
            returned_value_digests=tuple(
                _digest(f"returned-early-value-{index}") for index in range(1, 5)
            ),
            evidence_digest="",
        )
    )
    final_formation = formations[-1]
    final_identity = identities[-1]
    views = (
        _view(
            "P1",
            probe_sources[4],
            config_digest,
            final_formation.composite_poststate_digest,
            final_identity.standalone_b4_state_digest,
            final_identity.standalone_tspm_state_digest,
        ),
        _view(
            "P2",
            probe_sources[5],
            config_digest,
            final_formation.composite_poststate_digest,
            final_identity.standalone_b4_state_digest,
            final_identity.standalone_tspm_state_digest,
        ),
    )
    resource = fixtures.RESOURCES
    ledger = _seal(
        evaluator.S2FULedgerEvidence(
            resource_digest=resource.resource_digest,
            unique_receptor_analyses=resource.unique_receptor_analyses,
            composite_formations=resource.composite_formations,
            standalone_b4_formations=resource.standalone_b4_formations,
            standalone_tspm_formations=resource.standalone_tspm_formations,
            component_identity_checks=resource.component_identity_checks,
            unique_probe_inputs=len(fixtures.PROBES),
            high_level_read_only_calls=7,
            composite_formation_words=resource.composite_formation_words,
            composite_formation_distance_terms=(
                resource.composite_formation_distance_terms
            ),
            composite_control_terms=resource.composite_control_terms,
            evidence_digest="",
        )
    )
    return _seal_bundle(
        evaluator.S2FUEvidenceBundle(
            fixture_digest=fixtures.FIXTURE_DIGEST,
            config_digest=config_digest,
            source_hashes=fixtures.SOURCE_HASHES,
            formations=tuple(formations),
            component_identities=tuple(identities),
            probe_sources=probe_sources,
            sequence=sequence,
            views=views,
            ledger=ledger,
            recording_complete=True,
            bundle_digest="",
        )
    )


def _with_sequence(bundle: evaluator.S2FUEvidenceBundle, **changes):
    sequence = _seal(replace(bundle.sequence, evidence_digest="", **changes))
    return _seal_bundle(replace(bundle, sequence=sequence, bundle_digest=""))


def _with_view(bundle: evaluator.S2FUEvidenceBundle, index: int, **changes):
    views = list(bundle.views)
    views[index] = _seal(replace(views[index], evidence_digest="", **changes))
    return _seal_bundle(replace(bundle, views=tuple(views), bundle_digest=""))


def _with_formation(bundle: evaluator.S2FUEvidenceBundle, index: int, **changes):
    formations = list(bundle.formations)
    formations[index] = _seal(
        replace(formations[index], evidence_digest="", **changes)
    )
    return _seal_bundle(
        replace(bundle, formations=tuple(formations), bundle_digest="")
    )


def _with_identity(bundle: evaluator.S2FUEvidenceBundle, index: int, **changes):
    identities = list(bundle.component_identities)
    identities[index] = _seal(
        replace(identities[index], evidence_digest="", **changes)
    )
    return _seal_bundle(
        replace(bundle, component_identities=tuple(identities), bundle_digest="")
    )


class S2FUFixtureEvaluatorQualificationTests(unittest.TestCase):
    def test_01_bound_scope_has_eleven_patterns_eighteen_steps_and_six_probes(self):
        self.assertEqual("s2fu-fixture-evaluator-qualification-20260829-01", RUN_ID)
        self.assertEqual(11, len(fixtures.PATTERNS))
        self.assertEqual(tuple(range(1, 19)), tuple(item.step for item in fixtures.EXPOSURES))
        self.assertEqual(6, len(fixtures.PROBES))

    def test_02_auditory_masks_have_weight_four_and_minimum_distance_quarter(self):
        masks = tuple(pattern.auditory_values for pattern in fixtures.PATTERNS)
        self.assertTrue(all(len(mask) == 8 and sum(mask) == 4 for mask in masks))
        minimum = min(
            Fraction(sum(abs(a - b) for a, b in zip(left, right)), 8)
            for index, left in enumerate(masks)
            for right in masks[index + 1 :]
        )
        self.assertEqual(Fraction(1, 4), minimum)
        self.assertEqual(Fraction(2, 8), Fraction(fixtures.AUDITORY_MINIMUM.numerator, fixtures.AUDITORY_MINIMUM.denominator))

    def test_03_visual_histograms_and_minimum_distance_are_bound(self):
        cells = tuple(pattern.visual_cell_values for pattern in fixtures.PATTERNS)
        self.assertTrue(
            all(
                values.count(210) == 3
                and values.count(30) == 3
                and sum(values) == 720
                for values in cells
            )
        )
        minimum = min(
            Fraction(
                3 * sum(abs(a - b) for a, b in zip(left, right)),
                255 * 18,
            )
            for index, left in enumerate(cells)
            for right in cells[index + 1 :]
        )
        self.assertEqual(Fraction(180, 765), minimum)
        self.assertEqual(Fraction(180, 765), Fraction(fixtures.VISUAL_MINIMUM.numerator, fixtures.VISUAL_MINIMUM.denominator))

    def test_04_time_windows_and_evaluation_metadata_remain_separate(self):
        exposure_windows = tuple(
            (item.window_start_tick, item.window_end_tick)
            for item in fixtures.EXPOSURES
        )
        self.assertEqual(
            tuple((tick, tick + 1) for tick in range(4))
            + tuple((tick, tick + 1) for tick in range(8, 22)),
            exposure_windows,
        )
        self.assertEqual(
            ((4, 5), (5, 6), (6, 7), (7, 8), (22, 23), (23, 24)),
            tuple((item.window_start_tick, item.window_end_tick) for item in fixtures.PROBES),
        )
        self.assertTrue(
            set(fixtures.OPERATOR_INPUT_FIELDS).isdisjoint(fixtures.EVALUATION_ONLY_FIELDS)
        )

    def test_05_resource_arithmetic_is_complete(self):
        resource = fixtures.RESOURCES
        self.assertEqual(11106, resource.composite_formation_words)
        self.assertEqual(
            resource.b4_arm_words + resource.tspm_arm_words + resource.coordinator_words,
            resource.composite_formation_words,
        )
        self.assertEqual(8424, resource.composite_formation_distance_terms)
        self.assertEqual(
            resource.b4_distance_terms + resource.tspm_distance_terms,
            resource.composite_formation_distance_terms,
        )
        self.assertEqual(972, resource.composite_control_terms)
        self.assertEqual(
            resource.common_projection_terms
            + resource.coordinator_validation_terms
            + resource.coordinator_digest_operations,
            resource.composite_control_terms,
        )

    def test_06_complete_synthetic_bundle_is_functionally_confirmed(self):
        result = evaluator.evaluate_s2fu(_valid_bundle())
        self.assertEqual(evaluator.S2FU_FUNCTION_CONFIRMED, result.status)
        self.assertEqual((), result.method_issues)
        self.assertEqual((), result.functional_findings)
        self.assertTrue(result.p2_unstable_trace_present)
        self.assertIsNone(result.automatic_view_selection)

    def test_07_wrong_b4_order_is_functionally_falsified_with_valid_digests(self):
        bundle = _with_sequence(_valid_bundle(), ordered_recognized=False)
        result = evaluator.evaluate_s2fu(bundle)
        self.assertEqual(evaluator.S2FU_FUNCTION_FALSIFIED, result.status)
        self.assertEqual((), result.method_issues)
        self.assertIn("EARLY_B4_ORDER_NOT_RECOGNIZED", result.functional_findings)

    def test_08_missing_stable_p1_slow_is_functionally_falsified(self):
        bundle = _with_view(
            _valid_bundle(),
            0,
            auditory_slow_support=2,
            auditory_slow_stable=False,
            auditory_slow_recognized=False,
            standalone_auditory_slow_support=2,
            standalone_auditory_slow_stable=False,
            standalone_auditory_slow_recognized=False,
            visual_slow_support=2,
            visual_slow_stable=False,
            visual_slow_recognized=False,
            standalone_visual_slow_support=2,
            standalone_visual_slow_stable=False,
            standalone_visual_slow_recognized=False,
        )
        result = evaluator.evaluate_s2fu(bundle)
        self.assertEqual(evaluator.S2FU_FUNCTION_FALSIFIED, result.status)
        self.assertEqual((), result.method_issues)
        self.assertIn("P1_STABLE_SLOW_NOT_CONFIRMED", result.functional_findings)

    def test_09_stably_recognized_p2_is_functionally_falsified(self):
        bundle = _with_view(
            _valid_bundle(),
            1,
            auditory_slow_stable=True,
            auditory_slow_recognized=True,
            standalone_auditory_slow_stable=True,
            standalone_auditory_slow_recognized=True,
            visual_slow_stable=True,
            visual_slow_recognized=True,
            standalone_visual_slow_stable=True,
            standalone_visual_slow_recognized=True,
        )
        result = evaluator.evaluate_s2fu(bundle)
        self.assertEqual(evaluator.S2FU_FUNCTION_FALSIFIED, result.status)
        self.assertEqual((), result.method_issues)
        self.assertIn("P2_UNSTABLE_TRACE_MISMATCH", result.functional_findings)

    def test_10_tspm_sequence_claim_is_functionally_falsified(self):
        bundle = _with_sequence(
            _valid_bundle(),
            tspm_sequence_status="ORDER_RECOGNIZED",
        )
        result = evaluator.evaluate_s2fu(bundle)
        self.assertEqual(evaluator.S2FU_FUNCTION_FALSIFIED, result.status)
        self.assertEqual((), result.method_issues)
        self.assertIn("TSPM_SEQUENCE_ORDER_CLAIMED", result.functional_findings)

    def test_11_digest_source_tick_and_component_breaks_are_not_evaluable(self):
        valid = _valid_bundle()
        broken_formations = list(valid.formations)
        broken_formations[0] = replace(
            broken_formations[0], evidence_digest="0" * 64
        )
        digest_break = _seal_bundle(
            replace(valid, formations=tuple(broken_formations), bundle_digest="")
        )
        source_break = _seal_bundle(
            replace(
                valid,
                source_hashes=(("foreign/source.py", _digest("foreign-source")),),
                bundle_digest="",
            )
        )
        tick_break = _with_formation(valid, 0, window_start_tick=99, window_end_tick=100)
        component_break = _with_identity(
            valid,
            0,
            standalone_b4_state_digest=_digest("foreign-b4-state"),
        )
        for label, bundle in (
            ("digest", digest_break),
            ("source", source_break),
            ("tick", tick_break),
            ("component", component_break),
        ):
            with self.subTest(label=label):
                result = evaluator.evaluate_s2fu(bundle)
                self.assertEqual(evaluator.S2FU_NOT_EVALUABLE, result.status)
                self.assertNotEqual((), result.method_issues)

    def test_12_incomplete_ledger_and_read_only_break_are_not_evaluable(self):
        valid = _valid_bundle()
        ledger = _seal(
            replace(
                valid.ledger,
                unique_receptor_analyses=23,
                evidence_digest="",
            )
        )
        ledger_break = _seal_bundle(
            replace(valid, ledger=ledger, bundle_digest="")
        )
        read_only_break = _with_view(
            valid,
            0,
            composite_poststate_digest=_digest("mutated-composite-poststate"),
        )
        for label, bundle in (
            ("ledger", ledger_break),
            ("read-only", read_only_break),
        ):
            with self.subTest(label=label):
                result = evaluator.evaluate_s2fu(bundle)
                self.assertEqual(evaluator.S2FU_NOT_EVALUABLE, result.status)
                self.assertNotEqual((), result.method_issues)


if __name__ == "__main__":
    unittest.main()
