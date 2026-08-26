"""Focused S1-PL acceptance for binding offer, adapter, and comparator."""

from __future__ import annotations

import ast
from dataclasses import replace
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from mcm_field_organism.g2_d3_binding_offer_baseline_adapter import (
    FAILURE_CODES as ADAPTER_FAILURE_CODES,
    adapt_g2_d3_binding_offer_to_retention_event,
    build_g2_d3_binding_offer_baseline_adapter_registry,
)
from mcm_field_organism.g2_d3_binding_offer_comparison import (
    FAILURE_CODES as COMPARISON_FAILURE_CODES,
    build_g2_d3_binding_offer_comparison_registry,
    compare_g2_d3_binding_offer_results,
)
from mcm_field_organism.g2_d3_local_binding_offer import (
    FAILURE_CODES as BINDING_FAILURE_CODES,
    NOT_COMPUTABLE,
    apply_g2_d3_local_binding_offer,
    build_g2_d3_local_binding_offer_registry,
)
from mcm_field_organism.g2_d3_matched_retention_baseline import (
    build_g2_d3_matched_retention_baseline_registry,
    evaluate_g2_d3_matched_retention_baseline,
)
from mcm_field_organism.g2_d3_schema_validator import (
    build_g2_d3_validation_registry,
    validate_g2_d3_anatomy_record,
)
from mcm_field_organism.g2_d3_two_step_composition import build_g2_d3_two_step_composition_registry
from mcm_field_organism.kfs1_schema_validator import canonical_json_bytes, sha256_hex
from tests.g2_d3_s1pb_retention_baseline_fixtures import (
    CONFIGURATION_RAW,
    INITIAL_STATE_RAW,
    XXX_FIRST,
    XXX_SECOND,
    YYY_FIRST,
    YYY_SECOND,
)
from tests.g2_d3_s1pl_binding_offer_fixtures import (
    ADAPTER_CONTRACT,
    ADAPTER_EXPECTED,
    ADAPTER_MUTATIONS,
    ALL_MUTATION_NAMES,
    BLOCKED_HELD_EXPECTED_POST,
    BLOCKED_HELD_PRE,
    CANDIDATE_EXPECTED,
    CANDIDATE_MUTATIONS,
    COMPARATOR_MUTATION_ROLES,
    EQUATION_CONTRACT,
    EVENT_PAYLOAD,
    FREE_AVAILABLE_EXPECTED_POST,
    FREE_AVAILABLE_PRE,
    PREDICTION,
)


def _rebind(raw: bytes, key: str, **changes: object) -> bytes:
    value = json.loads(raw)
    value.update(changes)
    value.pop(key, None)
    value[key] = sha256_hex(canonical_json_bytes(value))
    return canonical_json_bytes(value)


class G2D3S1PLAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.anatomy_registry = build_g2_d3_validation_registry()
        cls.binding_registry = build_g2_d3_local_binding_offer_registry()
        cls.adapter_registry = build_g2_d3_binding_offer_baseline_adapter_registry()
        cls.comparison_registry = build_g2_d3_binding_offer_comparison_registry()
        cls.baseline_registry = build_g2_d3_matched_retention_baseline_registry()
        cls.sequence_registry = build_g2_d3_two_step_composition_registry()
        cls.free_candidate = apply_g2_d3_local_binding_offer(
            FREE_AVAILABLE_PRE, EVENT_PAYLOAD, EQUATION_CONTRACT,
            cls.binding_registry, cls.anatomy_registry,
        )
        cls.blocked_candidate = apply_g2_d3_local_binding_offer(
            BLOCKED_HELD_PRE, EVENT_PAYLOAD, EQUATION_CONTRACT,
            cls.binding_registry, cls.anatomy_registry,
        )
        cls.adapter_result = adapt_g2_d3_binding_offer_to_retention_event(
            EVENT_PAYLOAD, ADAPTER_CONTRACT, cls.adapter_registry
        )
        cls.free_baseline = evaluate_g2_d3_matched_retention_baseline(
            XXX_FIRST, XXX_SECOND, INITIAL_STATE_RAW, cls.adapter_result.retention_event_raw_bytes,
            CONFIGURATION_RAW, cls.baseline_registry, cls.sequence_registry,
        )
        cls.blocked_baseline = evaluate_g2_d3_matched_retention_baseline(
            XXX_FIRST, XXX_SECOND, INITIAL_STATE_RAW, cls.adapter_result.retention_event_raw_bytes,
            CONFIGURATION_RAW, cls.baseline_registry, cls.sequence_registry,
        )

    def _compare(self, free_candidate=None, blocked_candidate=None, free_baseline=None,
                 blocked_baseline=None, prediction=PREDICTION):
        return compare_g2_d3_binding_offer_results(
            free_candidate or self.free_candidate,
            blocked_candidate or self.blocked_candidate,
            free_baseline or self.free_baseline,
            blocked_baseline or self.blocked_baseline,
            prediction,
            self.comparison_registry,
        )

    def test_01_registries_and_failure_surfaces_are_exact(self) -> None:
        self.assertEqual(18, len(BINDING_FAILURE_CODES + ADAPTER_FAILURE_CODES + COMPARISON_FAILURE_CODES))
        self.assertEqual(2, len(self.binding_registry.allowed_pre_record_digests))
        self.assertEqual(
            "0fabfc2935e47e5c5b6be99d4a31ae28e2c1d26f25cfe12892060c42ed2dbb61",
            self.comparison_registry.prediction_digest,
        )

    def test_02_positive_fixture_bytes_and_digests_are_exact(self) -> None:
        expected = (
            "320fd5409142c79b494523401e898f082592b2925b56c6910a478c35f8e546a2",
            "5c8a3dc5081755c34854ef4ab119b00731f4d60924e5becda9565d28b59135e5",
            "15d5134123f30dd45b0435cb7c7b6f151d03dd115d559253d0aec762f5e7d99d",
            "4c85ec5a607fc93c91c255f5e8b483533601d761194513296821c6f2b2089973",
        )
        self.assertEqual(expected, tuple(sha256_hex(item) for item in (
            EVENT_PAYLOAD, EQUATION_CONTRACT, ADAPTER_CONTRACT, PREDICTION
        )))

    def test_03_free_available_candidate_is_exact(self) -> None:
        self.assertEqual("valid", self.free_candidate.receipt.validation_status)
        self.assertEqual(0.375, self.free_candidate.commit_amount)
        self.assertEqual(FREE_AVAILABLE_EXPECTED_POST, self.free_candidate.poststate_raw_bytes)

    def test_04_blocked_held_candidate_is_exact(self) -> None:
        self.assertEqual("valid", self.blocked_candidate.receipt.validation_status)
        self.assertEqual(0.25, self.blocked_candidate.commit_amount)
        self.assertEqual(BLOCKED_HELD_EXPECTED_POST, self.blocked_candidate.poststate_raw_bytes)

    def test_05_both_poststates_are_conserved(self) -> None:
        for result in (self.free_candidate, self.blocked_candidate):
            value = json.loads(result.poststate_raw_bytes)
            self.assertEqual(value["capacity"], sum(value[key] for key in (
                "free", "bound_unconfigured", "bound_configured", "blocked"
            )))
            receipt = validate_g2_d3_anatomy_record(result.poststate_raw_bytes, self.anatomy_registry)
            self.assertEqual("valid", receipt.validation_status)

    def test_06_poststate_and_binding_receipt_digests_are_exact(self) -> None:
        self.assertEqual(
            ("9195946005008bf034a8625d04ddaf58826254f8a8fbd11f3b3e3433a9483d9f",
             "1f7d2b8fb9a5d7afebe1fbd60adaa915b3f46c5efe85d98c37d02389cfb64227"),
            tuple(sha256_hex(item.poststate_raw_bytes) for item in (self.free_candidate, self.blocked_candidate)),
        )
        for result in (self.free_candidate, self.blocked_candidate):
            payload = result.receipt.canonical_payload()
            digest = payload.pop("receipt_digest")
            self.assertEqual(digest, sha256_hex(canonical_json_bytes(payload)))

    def test_07_adapter_output_is_exact(self) -> None:
        self.assertEqual("valid", self.adapter_result.receipt.validation_status)
        self.assertEqual(
            "dbffc12bef77155c2271d3990ebe1b8ae4d481ce6155bf8716b1f6e19128b30f",
            sha256_hex(self.adapter_result.retention_event_raw_bytes),
        )

    def test_08_adapter_input_and_output_have_no_forbidden_information(self) -> None:
        source = json.loads(EVENT_PAYLOAD)
        output = json.loads(self.adapter_result.retention_event_raw_bytes)
        for forbidden in ("arm_id", "candidate_state", "free", "blocked", "o3"):
            self.assertNotIn(forbidden, source)
            self.assertNotIn(forbidden, output)

    def test_09_two_baseline_results_are_identical(self) -> None:
        self.assertEqual(self.free_baseline, self.blocked_baseline)
        self.assertEqual((0.5, 0.25, 0.125), self.free_baseline.checkpoint_values)

    def test_10_positive_passive_comparison_is_exact(self) -> None:
        result = self._compare()
        self.assertEqual("valid", result.receipt.validation_status)
        self.assertEqual((0.375, 0.25), result.candidate_commits)
        self.assertEqual(0.125, result.candidate_binding_contrast)
        self.assertEqual((0.25, 0.25), result.baseline_first_step_responses)
        self.assertEqual(0.0, result.baseline_replica_contrast)
        self.assertEqual("CANDIDATE_DIFFERENT_BASELINE_EQUAL", result.decision)

    def test_11_cp2_is_strictly_excluded(self) -> None:
        changed = _rebind(PREDICTION, "prediction_digest", excluded_baseline_checkpoint="included")
        result = self._compare(prediction=changed)
        self.assertEqual(("PL_CP2_EXCLUSION_FAILED",), result.receipt.failure_reasons)
        self.assertNotIn("cp2", " ".join(result.receipt.canonical_payload().keys()).lower())

    def test_12_candidate_mutations_have_single_codes(self) -> None:
        self.assertEqual(7, len(CANDIDATE_MUTATIONS))
        for name, inputs in CANDIDATE_MUTATIONS.items():
            with self.subTest(name=name):
                result = apply_g2_d3_local_binding_offer(
                    *inputs, self.binding_registry, self.anatomy_registry
                )
                self.assertEqual(CANDIDATE_EXPECTED[name], result.receipt.failure_reasons)
        original = validate_g2_d3_anatomy_record
        calls = 0
        def forced_second_failure(raw, registry):
            nonlocal calls
            calls += 1
            receipt = original(raw, registry)
            return receipt if calls == 1 else replace(
                receipt, validation_status="invalid", failure_reasons=("forced",)
            )
        with patch(
            "mcm_field_organism.g2_d3_local_binding_offer.validate_g2_d3_anatomy_record",
            side_effect=forced_second_failure,
        ):
            result = apply_g2_d3_local_binding_offer(
                FREE_AVAILABLE_PRE, EVENT_PAYLOAD, EQUATION_CONTRACT,
                self.binding_registry, self.anatomy_registry,
            )
        self.assertEqual(("PL_POSTSTATE_INVALID",), result.receipt.failure_reasons)

    def test_13_adapter_mutations_have_single_codes(self) -> None:
        self.assertEqual(3, len(ADAPTER_MUTATIONS))
        for name, inputs in ADAPTER_MUTATIONS.items():
            with self.subTest(name=name):
                result = adapt_g2_d3_binding_offer_to_retention_event(*inputs, self.adapter_registry)
                self.assertEqual(ADAPTER_EXPECTED[name], result.receipt.failure_reasons)
        with patch(
            "mcm_field_organism.g2_d3_binding_offer_baseline_adapter._RETENTION_EVENT_RAW", b"{}"
        ):
            result = adapt_g2_d3_binding_offer_to_retention_event(
                EVENT_PAYLOAD, ADAPTER_CONTRACT, self.adapter_registry
            )
        self.assertEqual(("PL_ADAPTER_OUTPUT_MISMATCH",), result.receipt.failure_reasons)

    def test_14_comparator_mutations_have_single_codes(self) -> None:
        incomplete = replace(self.free_candidate, commit_amount=NOT_COMPUTABLE)
        self.assertEqual(("PL_CANDIDATE_RESULT_INVALID",), self._compare(
            free_candidate=incomplete
        ).receipt.failure_reasons)
        bad_receipt = replace(self.free_baseline.receipt, validation_status="invalid")
        bad_baseline = replace(self.free_baseline, receipt=bad_receipt)
        self.assertEqual(("PL_BASELINE_RESULT_INVALID",), self._compare(
            free_baseline=bad_baseline
        ).receipt.failure_reasons)
        yyy = evaluate_g2_d3_matched_retention_baseline(
            YYY_FIRST, YYY_SECOND, INITIAL_STATE_RAW, self.adapter_result.retention_event_raw_bytes,
            CONFIGURATION_RAW, self.baseline_registry, self.sequence_registry,
        )
        self.assertEqual(("PL_BASELINE_PROVENANCE_MISMATCH",), self._compare(
            blocked_baseline=yyy
        ).receipt.failure_reasons)
        changed_cp1 = replace(self.free_baseline, checkpoint_values=(0.5, 0.2, 0.125))
        self.assertEqual(("PL_BASELINE_RESULT_INVALID",), self._compare(
            free_baseline=changed_cp1
        ).receipt.failure_reasons)
        cp2 = _rebind(PREDICTION, "prediction_digest", excluded_baseline_checkpoint="included")
        self.assertEqual(("PL_CP2_EXCLUSION_FAILED",), self._compare(
            prediction=cp2
        ).receipt.failure_reasons)
        decision = _rebind(PREDICTION, "prediction_digest", expected_decision="OTHER")
        self.assertEqual(("PL_PREDICTION_OR_DECISION_MISMATCH",), self._compare(
            prediction=decision
        ).receipt.failure_reasons)

    def test_15_eighteen_mutation_roles_are_complete(self) -> None:
        self.assertEqual(18, len(ALL_MUTATION_NAMES))
        self.assertEqual(18, len(set(ALL_MUTATION_NAMES)))
        self.assertEqual(6, len(COMPARATOR_MUTATION_ROLES))

    def test_16_failures_are_sorted_unique_and_deterministic(self) -> None:
        inputs = CANDIDATE_MUTATIONS["payload_edge"]
        first = apply_g2_d3_local_binding_offer(*inputs, self.binding_registry, self.anatomy_registry)
        second = apply_g2_d3_local_binding_offer(*inputs, self.binding_registry, self.anatomy_registry)
        self.assertEqual(first, second)
        self.assertEqual(tuple(sorted(set(first.receipt.failure_reasons))), first.receipt.failure_reasons)

    def test_17_inputs_and_registries_remain_unchanged(self) -> None:
        inputs = (FREE_AVAILABLE_PRE, EVENT_PAYLOAD, EQUATION_CONTRACT)
        registry = self.binding_registry
        apply_g2_d3_local_binding_offer(*inputs, registry, self.anatomy_registry)
        self.assertEqual(inputs, (FREE_AVAILABLE_PRE, EVENT_PAYLOAD, EQUATION_CONTRACT))
        self.assertEqual(registry, self.binding_registry)

    def test_18_wrong_api_types_fail_before_receipts(self) -> None:
        with self.assertRaises(TypeError):
            apply_g2_d3_local_binding_offer(
                bytearray(FREE_AVAILABLE_PRE), EVENT_PAYLOAD, EQUATION_CONTRACT,
                self.binding_registry, self.anatomy_registry,
            )
        with self.assertRaises(TypeError):
            adapt_g2_d3_binding_offer_to_retention_event(
                bytearray(EVENT_PAYLOAD), ADAPTER_CONTRACT, self.adapter_registry
            )
        with self.assertRaises(TypeError):
            compare_g2_d3_binding_offer_results(
                object(), self.blocked_candidate, self.free_baseline, self.blocked_baseline,
                PREDICTION, self.comparison_registry,
            )

    def test_19_digest_roles_are_reproducible_and_separate(self) -> None:
        result = self._compare()
        payload = result.receipt.canonical_payload()
        digest = payload.pop("receipt_digest")
        self.assertEqual(digest, sha256_hex(canonical_json_bytes(payload)))
        receipt = result.receipt.canonical_payload()
        self.assertEqual(
            receipt["free_baseline_receipt_digest"],
            receipt["blocked_baseline_receipt_digest"],
        )
        distinct_roles = (
            "prediction_input_digest", "prediction_digest",
            "free_candidate_receipt_digest", "blocked_candidate_receipt_digest",
            "free_baseline_receipt_digest", "comparison_contract_digest", "receipt_digest",
        )
        self.assertEqual(len(distinct_roles), len({receipt[key] for key in distinct_roles}))

    def test_20_import_surfaces_are_isolated(self) -> None:
        root = Path(__file__).parents[1] / "mcm_field_organism"
        for name in (
            "g2_d3_local_binding_offer.py",
            "g2_d3_binding_offer_baseline_adapter.py",
            "g2_d3_binding_offer_comparison.py",
        ):
            source = (root / name).read_text(encoding="utf-8")
            tree = ast.parse(source)
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(node.module or "")
            surface = " ".join(imports).lower()
            for forbidden in ("o3", "field", "runtime", "runner", "audio", "video", "browser", "socket"):
                self.assertNotIn(forbidden, surface)
            self.assertNotIn("open(", source.lower())


if __name__ == "__main__":
    unittest.main()
