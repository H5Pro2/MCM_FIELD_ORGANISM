from __future__ import annotations

from dataclasses import fields
from pathlib import Path
from types import SimpleNamespace
import unittest

import mcm_field_organism._tspm1_s2dr_private_comparison as s2dr


ROOT = Path(__file__).resolve().parents[1]
FOREIGN_DIGEST = "f" * 64


def registry():
    return s2dr.build_s2dr_registry()


def indexed_registry():
    config, fixtures, arms, plans, registry_digest = registry()
    return (
        config,
        {fixture.history_id: fixture for fixture in fixtures},
        {arm.arm_id: arm for arm in arms},
        {(plan.history_id, plan.arm_id): plan for plan in plans},
        registry_digest,
    )


def unsafe_clone(value, **changes):
    clone = object.__new__(type(value))
    for field in fields(value):
        object.__setattr__(clone, field.name, changes.get(field.name, getattr(value, field.name)))
    return clone


def owner_for(plan, *, prestate_digest=None, authorization_digest=None):
    return s2dr.S2DRCellOwner(
        f"s2dr.owner.{plan.history_id.lower()}.{plan.arm_id.lower()}",
        plan.cell_id,
        authorization_digest or plan.authorization_digest,
        f"s2dr.consume.{plan.history_id.lower()}.{plan.arm_id.lower()}",
        plan.cell_plan_digest,
        plan.config_digest,
        plan.fixture_digest,
        plan.arm_spec_digest,
        prestate_digest or plan.initial_state_digest,
    )


def valid_cell(history_id="H1", arm_id="B0"):
    config, fixtures, arms, plans, _ = indexed_registry()
    plan = plans[(history_id, arm_id)]
    owner = owner_for(plan)
    return config, fixtures[history_id], arms[arm_id], plan, owner.consume_once(
        config, fixtures[history_id], arms[arm_id], plan
    )


def assert_digest_guard(testcase, value, digest_field):
    testcase.assertEqual(getattr(value, digest_field), s2dr._digest(s2dr._record_payload(value, digest_field)))
    malformed = unsafe_clone(value, **{digest_field: FOREIGN_DIGEST})
    with testcase.assertRaises(s2dr.S2DRError):
        s2dr._validate_record(malformed, digest_field)


def rebuilt_result(result, budget):
    receipt = s2dr._built(
        s2dr.S2DRCellReceipt,
        "cell_receipt_digest",
        schema_version=result.cell_receipt.schema_version,
        cell_id=result.cell_receipt.cell_id,
        cell_plan_digest=result.cell_receipt.cell_plan_digest,
        config_digest=result.cell_receipt.config_digest,
        fixture_digest=result.cell_receipt.fixture_digest,
        arm_spec_digest=result.cell_receipt.arm_spec_digest,
        prestate_digest=result.cell_receipt.prestate_digest,
        event_digest=result.cell_receipt.event_digest,
        finding_digest=result.cell_receipt.finding_digest,
        budget_receipt_digest=budget.budget_receipt_digest,
        poststate_digest=result.cell_receipt.poststate_digest,
        owner_id=result.cell_receipt.owner_id,
        owner_terminal_state=result.cell_receipt.owner_terminal_state,
        internal_error_code=result.cell_receipt.internal_error_code,
    )
    return s2dr._built(
        s2dr.S2DRCellResult,
        "cell_result_digest",
        schema_version=result.schema_version,
        cell_id=result.cell_id,
        cell_plan_digest=result.cell_plan_digest,
        prestate_digest=result.prestate_digest,
        event_payloads=result.event_payloads,
        finding_payloads=result.finding_payloads,
        poststate_payload=result.poststate_payload,
        poststate_digest=result.poststate_digest,
        budget_receipt=budget,
        cell_receipt=receipt,
    )


def synthetic_findings(fixture, arm, vector):
    p1, p2, p3, p4, p5 = vector
    findings = []
    probe_number = 0
    for checkpoint, pairs in fixture.probe_specs:
        for pair_id in pairs:
            probe_number += 1
            recognized = False
            fast_recognized = False
            context_source = "NO_COMPLETE_CONTEXT"
            auditory_slow_status = None
            visual_slow_status = None
            auditory_proto = None
            visual_proto = None
            selected_values = None
            if fixture.history_id == "H1" and pair_id == "AX" and p1:
                recognized = fast_recognized = True
                context_source = "FAST_ASSOCIATIVE_CONTEXT"
                selected_values = ((0.0,) * 8, (0.0,) * 18)
            elif fixture.history_id == "H3" and pair_id == "AX" and p2:
                recognized = True
                context_source = "SLOW_PPB1_CONTEXT"
                auditory_slow_status = visual_slow_status = "SLOW_RECOGNIZED"
                auditory_proto = s2dr._digest(("auditory", "AX"))
                visual_proto = s2dr._digest(("visual", "AX"))
                selected_values = ((0.0,) * 8, (0.0,) * 18)
            elif fixture.history_id == "H2" and pair_id == "AX" and checkpoint == 4 and p3:
                recognized = True
                context_source = "SLOW_PPB1_CONTEXT"
                auditory_slow_status = visual_slow_status = "SLOW_RECOGNIZED"
                auditory_proto = s2dr._digest(("auditory", "AX"))
                visual_proto = s2dr._digest(("visual", "AX"))
                selected_values = ((0.0,) * 8, (0.0,) * 18)
            elif fixture.history_id == "H4" and p3:
                recognized = True
                if pair_id == "AX":
                    context_source = "SLOW_PPB1_CONTEXT"
                    auditory_slow_status = visual_slow_status = "SLOW_RECOGNIZED"
                    auditory_proto = s2dr._digest(("auditory", "AX"))
                    visual_proto = s2dr._digest(("visual", "AX"))
                    selected_values = ((0.0,) * 8, (0.0,) * 18)
                else:
                    fast_recognized = True
                    context_source = "FAST_ASSOCIATIVE_CONTEXT"
                    auditory_slow_status = visual_slow_status = "SLOW_NOT_RECOGNIZED"
                    selected_values = (
                        (s2dr.PAIR_SCALARS[pair_id][0],) * 8,
                        (s2dr.PAIR_SCALARS[pair_id][1],) * 18,
                    )
            elif fixture.history_id == "H5" and pair_id in {"AX", "P4"} and p4:
                recognized = fast_recognized = True
                context_source = "FAST_ASSOCIATIVE_CONTEXT"
                selected_values = (
                    (s2dr.PAIR_SCALARS[pair_id][0],) * 8,
                    (s2dr.PAIR_SCALARS[pair_id][1],) * 18,
                )
            elif fixture.history_id == "H7" and p5 and pair_id in {"AX", "NEAR"}:
                recognized = fast_recognized = True
                context_source = "FAST_ASSOCIATIVE_CONTEXT"
                selected_values = (
                    (s2dr.PAIR_SCALARS[pair_id][0],) * 8,
                    (s2dr.PAIR_SCALARS[pair_id][1],) * 18,
                )
            findings.append(
                s2dr._finding_payload(
                    fixture,
                    arm,
                    checkpoint,
                    pair_id,
                    recognized,
                    context_source,
                    s2dr._digest((fixture.history_id, arm.arm_id, "synthetic-state")),
                    fast_recognized=fast_recognized,
                    auditory_slow_status=auditory_slow_status,
                    visual_slow_status=visual_slow_status,
                    auditory_selected_prototype_digest=auditory_proto,
                    visual_selected_prototype_digest=visual_proto,
                    selected_values=selected_values,
                )
            )
    return tuple(findings)


def synthetic_comparison(vector_by_arm, *, error_arm=None, r0_mismatch=False):
    config, fixtures, arms, plans, registry_digest = indexed_registry()
    results = []
    ordered_plans = []
    for history_id in s2dr.HISTORY_IDS:
        for arm_id in s2dr.ARM_IDS:
            fixture = fixtures[history_id]
            arm = arms[arm_id]
            plan = plans[(history_id, arm_id)]
            ordered_plans.append(plan)
            findings = synthetic_findings(fixture, arm, vector_by_arm[arm_id])
            events = tuple(
                {"event": "FAST_UPDATED", "consolidation_status": "NOT_ELIGIBLE"}
                for _ in fixture.formation_pair_ids
            )
            formation_count = len(fixture.formation_pair_ids)
            probe_count = sum(len(pairs) for _, pairs in fixture.probe_specs)
            budget = s2dr._make_budget_receipt(
                plan,
                arm,
                (0,) * formation_count,
                (0,) * formation_count,
                (0,) * probe_count,
                (0,) * probe_count,
            )
            poststate_payload = ("synthetic-two-level", history_id)
            if r0_mismatch and arm_id == "R0" and history_id == "H1":
                poststate_payload = ("synthetic-two-level", history_id, "mismatch")
            poststate_digest = s2dr._digest(poststate_payload)
            receipt = s2dr._built(
                s2dr.S2DRCellReceipt,
                "cell_receipt_digest",
                schema_version=s2dr.S2DR_SCHEMA_VERSION,
                cell_id=plan.cell_id,
                cell_plan_digest=plan.cell_plan_digest,
                config_digest=config.config_digest,
                fixture_digest=fixture.fixture_digest,
                arm_spec_digest=arm.arm_spec_digest,
                prestate_digest=plan.initial_state_digest,
                event_digest=s2dr._digest(events),
                finding_digest=s2dr._digest(findings),
                budget_receipt_digest=budget.budget_receipt_digest,
                poststate_digest=poststate_digest,
                owner_id=f"s2dr.synthetic.owner.{history_id.lower()}.{arm_id.lower()}",
                owner_terminal_state="COMMITTED",
                internal_error_code="SYNTHETIC_ERROR" if arm_id == error_arm else None,
            )
            results.append(
                s2dr._built(
                    s2dr.S2DRCellResult,
                    "cell_result_digest",
                    schema_version=s2dr.S2DR_SCHEMA_VERSION,
                    cell_id=plan.cell_id,
                    cell_plan_digest=plan.cell_plan_digest,
                    prestate_digest=plan.initial_state_digest,
                    event_payloads=events,
                    finding_payloads=findings,
                    poststate_payload=poststate_payload,
                    poststate_digest=poststate_digest,
                    budget_receipt=budget,
                    cell_receipt=receipt,
                )
            )
    return s2dr.compare_s2dr_results(
        config,
        tuple(ordered_plans),
        tuple(results),
        registry_digest,
    )


class TSPM1S2DRPrivateComparisonContractTests(unittest.TestCase):
    def test_t01_parent_and_source_digests(self):
        config, _, _, _, _ = registry()
        self.assertIn(s2dr.S2DR_S2DS_PASS_DIGEST, config.parent_artifact_digests)
        self.assertEqual(3, len(config.source_blob_digests))

    def test_t02_two_files_no_export_or_runner(self):
        expected = {
            ROOT / "mcm_field_organism" / "_tspm1_s2dr_private_comparison.py",
            ROOT / "tests" / "test_tspm1_s2dr_private_comparison_contract.py",
        }
        self.assertTrue(all(path.is_file() for path in expected))
        self.assertFalse(hasattr(s2dr, "run_s2dr_matrix"))

    def test_t03_tspm1_name_has_no_apm1_role(self):
        source = (ROOT / "mcm_field_organism" / "_tspm1_s2dr_private_comparison.py").read_text(encoding="utf-8")
        self.assertNotIn("APM1", source)

    def test_t04_dimensions_are_8_18_26(self):
        self.assertEqual((8, 18, 26), (len(s2dr.AUDITORY_CARRIERS), len(s2dr.VISUAL_CARRIERS), len(s2dr._joint_values("AX"))))

    def test_t05_config_and_carriers_are_fixed(self):
        config, _, _, _, _ = registry()
        self.assertEqual(s2dr.AUDITORY_CARRIERS, config.auditory_carrier_ids)
        self.assertEqual(s2dr.VISUAL_CARRIERS, config.visual_carrier_ids)

    def test_t06_registry_has_56_fresh_ordered_plans(self):
        _, fixtures, arms, plans, digest = registry()
        self.assertEqual((7, 8, 56), (len(fixtures), len(arms), len(plans)))
        self.assertEqual(56, len({plan.cell_id for plan in plans}))
        self.assertRegex(digest, r"^[0-9a-f]{64}$")

    def _assert_fixture(self, history_id):
        _, fixtures, _, _, _ = indexed_registry()
        fixture = fixtures[history_id]
        self.assertEqual(s2dr.HISTORY_DEFINITIONS[history_id], (fixture.formation_pair_ids, fixture.probe_specs, fixture.ppb_budget_indices))

    def test_t07_fixture_h1(self): self._assert_fixture("H1")
    def test_t08_fixture_h2(self): self._assert_fixture("H2")
    def test_t09_fixture_h3(self): self._assert_fixture("H3")
    def test_t10_fixture_h4(self): self._assert_fixture("H4")
    def test_t11_fixture_h5(self): self._assert_fixture("H5")
    def test_t12_fixture_h6(self): self._assert_fixture("H6")
    def test_t13_fixture_h7(self): self._assert_fixture("H7")

    def _assert_initial(self, arm_id, expected_type):
        config, _, arms, _, _ = indexed_registry()
        state = s2dr.initial_s2dr_arm_state(config, arms[arm_id])
        self.assertIs(type(state), expected_type)

    def test_t14_tspm1_operator_and_initial_state(self):
        self._assert_initial("TSPM1", s2dr.tspm1.TSPM1CompositeState)

    def test_t15_b0_operator_and_initial_state(self):
        config, _, arms, _, _ = indexed_registry()
        self.assertEqual((), s2dr.initial_s2dr_arm_state(config, arms["B0"]))

    def test_t16_b1_direct_operator_and_initial_state(self):
        self._assert_initial("B1_DIRECT", s2dr._PPBPairState)

    def test_t17_b1_budget_matched_operator_and_initial_state(self):
        self._assert_initial("B1_BUDGET_MATCHED", s2dr._PPBPairState)

    def _micro_transition(self, arm_id):
        config, fixtures, arms, _, _ = indexed_registry()
        state = s2dr.initial_s2dr_arm_state(config, arms[arm_id])
        poststate, event, operations = s2dr.advance_s2dr_arm(config, fixtures["H1"], arms[arm_id], state, "AX", 1)
        self.assertIsNotNone(poststate)
        self.assertIn("event", event)
        self.assertLessEqual(operations[0], 293)

    def test_t18_b2_exact_micro_transition(self): self._micro_transition("B2")
    def test_t19_b3_exact_micro_transition(self): self._micro_transition("B3")
    def test_t20_b4_exact_micro_transition(self): self._micro_transition("B4")

    def test_t21_r0_operator_and_initial_state(self):
        self._assert_initial("R0", s2dr._GenericTwoLevelState)

    def test_t22_resource_max_is_269_words_2152_bytes(self):
        self.assertEqual((269, 2152), (max(s2dr.ARM_RESOURCE_WORDS.values()), max(s2dr.ARM_RESOURCE_WORDS.values()) * 8))

    def test_t23_eight_arm_word_counts(self):
        self.assertEqual((0, 29, 176, 255, 264, 269), tuple(sorted(set(s2dr.ARM_RESOURCE_WORDS.values()))))
        self.assertEqual(8, len(s2dr.ARM_RESOURCE_WORDS))

    def test_t24_formation_write_limit_is_293(self):
        self.assertEqual(293, s2dr.OPERATION_LIMITS["formation_write_limit"])

    def test_t25_distance_term_limits_are_234(self):
        self.assertEqual((234, 234), (s2dr.OPERATION_LIMITS["formation_distance_limit"], s2dr.OPERATION_LIMITS["probe_distance_limit"]))

    def test_t26_probe_writes_are_zero(self):
        self.assertEqual(0, s2dr.OPERATION_LIMITS["probe_write_limit"])

    def test_t27_config_record_digest(self):
        assert_digest_guard(self, registry()[0], "config_digest")

    def test_t28_fixture_record_digest(self):
        assert_digest_guard(self, registry()[1][0], "fixture_digest")

    def test_t29_arm_spec_digest(self):
        assert_digest_guard(self, registry()[2][0], "arm_spec_digest")

    def test_t30_cell_plan_digest(self):
        assert_digest_guard(self, registry()[3][0], "cell_plan_digest")

    def test_t31_budget_receipt_digest(self):
        assert_digest_guard(self, valid_cell()[4].budget_receipt, "budget_receipt_digest")

    def test_t32_cell_receipt_digest(self):
        assert_digest_guard(self, valid_cell()[4].cell_receipt, "cell_receipt_digest")

    def test_t33_cell_result_digest(self):
        assert_digest_guard(self, valid_cell()[4], "cell_result_digest")

    def test_t34_comparison_result_digest(self):
        result = s2dr._built(
            s2dr.S2DRComparisonResult,
            "comparison_result_digest",
            schema_version=s2dr.S2DR_SCHEMA_VERSION,
            registry_digest=registry()[4],
            ordered_cell_result_digests=(),
            per_arm_predicate_vectors=tuple((arm, (False,) * 5) for arm in s2dr.ARM_IDS),
            per_arm_error_counts=tuple((arm, 0) for arm in s2dr.ARM_IDS),
            strongest_simple_baseline_id="B0",
            r0_exact_equivalence=True,
            decision="TSPM1_FUNCTION_NOT_VALID",
        )
        assert_digest_guard(self, result, "comparison_result_digest")

    def test_t35_p1_p5_projection(self):
        vectors = {arm: (True,) * 5 for arm in s2dr.ARM_IDS}
        result = synthetic_comparison(vectors)
        self.assertEqual((True,) * 5, dict(result.per_arm_predicate_vectors)["TSPM1"])

    def test_t36_method_invalid_priority(self):
        vectors = {arm: (True,) * 5 for arm in s2dr.ARM_IDS}
        self.assertEqual("METHOD_INVALID", synthetic_comparison(vectors, r0_mismatch=True).decision)

    def test_t37_tspm1_invalid_priority(self):
        vectors = {arm: (True,) * 5 for arm in s2dr.ARM_IDS}
        self.assertEqual("TSPM1_FUNCTION_NOT_VALID", synthetic_comparison(vectors, error_arm="TSPM1").decision)

    def test_t38_baseline_and_tie(self):
        vectors = {arm: (True,) * 5 for arm in s2dr.ARM_IDS}
        result = synthetic_comparison(vectors)
        self.assertEqual(("FUNCTION_VALID_SIMPLE_BASELINE_EXPLAINS", "B0"), (result.decision, result.strongest_simple_baseline_id))

    def test_t39_advantage_with_r0(self):
        vectors = {arm: (False,) * 5 for arm in s2dr.ARM_IDS}
        vectors["TSPM1"] = vectors["R0"] = (True,) * 5
        self.assertEqual("TSPM1_TWO_TIMESCALE_ENGINEERING_ADVANTAGE_OVER_SIMPLE_BASELINES", synthetic_comparison(vectors).decision)

    def _assert_owner_failure(self, owner, action, inner_code):
        with self.assertRaises(s2dr.S2DRError) as caught:
            action()
        self.assertEqual(s2dr.S2DR_ATTEMPT_FAILED, caught.exception.code)
        self.assertEqual(("FAILED", inner_code, None), (owner.snapshot().status, owner.snapshot().internal_error_code, owner.snapshot().committed_result_digest))

    def test_t40_wrong_config_digest_fails_closed(self):
        config, fixtures, arms, plans, _ = indexed_registry(); plan = plans[("H1", "B0")]; owner = owner_for(plan)
        bad = unsafe_clone(config, config_digest=FOREIGN_DIGEST)
        self._assert_owner_failure(owner, lambda: owner.consume_once(bad, fixtures["H1"], arms["B0"], plan), s2dr.S2DR_DIGEST_OR_SOURCE_MISMATCH)

    def test_t41_wrong_fixture_digest_fails_closed(self):
        config, fixtures, arms, plans, _ = indexed_registry(); plan = plans[("H1", "B0")]; owner = owner_for(plan)
        bad = unsafe_clone(fixtures["H1"], fixture_digest=FOREIGN_DIGEST)
        self._assert_owner_failure(owner, lambda: owner.consume_once(config, bad, arms["B0"], plan), s2dr.S2DR_DIGEST_OR_SOURCE_MISMATCH)

    def test_t42_wrong_arm_digest_fails_closed(self):
        config, fixtures, arms, plans, _ = indexed_registry(); plan = plans[("H1", "B0")]; owner = owner_for(plan)
        bad = unsafe_clone(arms["B0"], arm_spec_digest=FOREIGN_DIGEST)
        self._assert_owner_failure(owner, lambda: owner.consume_once(config, fixtures["H1"], bad, plan), s2dr.S2DR_DIGEST_OR_SOURCE_MISMATCH)

    def test_t43_wrong_prestate_digest_fails_closed(self):
        config, fixtures, arms, plans, _ = indexed_registry(); plan = plans[("H1", "B0")]; owner = owner_for(plan, prestate_digest=FOREIGN_DIGEST)
        self._assert_owner_failure(owner, lambda: owner.consume_once(config, fixtures["H1"], arms["B0"], plan), s2dr.S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH)

    def test_t44_wrong_authorization_fails_closed(self):
        config, fixtures, arms, plans, _ = indexed_registry(); plan = plans[("H1", "B0")]
        payload = s2dr._record_payload(plan, "cell_plan_digest")
        payload["authorization_digest"] = FOREIGN_DIGEST
        bad_plan = unsafe_clone(
            plan,
            authorization_digest=FOREIGN_DIGEST,
            cell_plan_digest=s2dr._digest(payload),
        )
        owner = owner_for(plan)
        self._assert_owner_failure(owner, lambda: owner.consume_once(config, fixtures["H1"], arms["B0"], bad_plan), s2dr.S2DR_AUTHORIZATION_MISMATCH)

    def test_t45_foreign_cell_id_fails_closed(self):
        config, fixtures, arms, plans, _ = indexed_registry(); plan = plans[("H1", "B0")]; foreign = plans[("H2", "B0")]; owner = owner_for(plan)
        self._assert_owner_failure(owner, lambda: owner.consume_once(config, fixtures["H2"], arms["B0"], foreign), s2dr.S2DR_OWNER_AUTHORIZATION_MISMATCH)

    def test_t46_duplicate_cell_id_fails_closed(self):
        plan = registry()[3][0]
        fake = SimpleNamespace(cell_id=plan.cell_id, cell_plan_digest=plan.cell_plan_digest)
        with self.assertRaises(s2dr.S2DRError) as caught:
            s2dr.compare_s2dr_results(registry()[0], (plan,) * 56, (fake,) * 56, registry()[4])
        self.assertEqual(s2dr.S2DR_RESULT_RELATION_MISMATCH, caught.exception.code)

    def test_t47_stale_probe_fails_closed(self):
        config, fixtures, arms, _, _ = indexed_registry()
        with self.assertRaises(s2dr.S2DRError) as caught:
            s2dr.probe_s2dr_arm(config, fixtures["H1"], arms["B0"], (), "NEAR", 1)
        self.assertEqual(s2dr.S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, caught.exception.code)

    def test_t48_swapped_budget_receipt_fails_closed(self):
        config, fixture, arm, plan, result = valid_cell("H1", "B0")
        foreign = valid_cell("H2", "B0")[4].budget_receipt
        bad = rebuilt_result(result, foreign)
        with self.assertRaises(s2dr.S2DRError) as caught:
            s2dr.validate_s2dr_cell_result(config, fixture, arm, plan, bad)
        self.assertEqual(s2dr.S2DR_RESULT_RELATION_MISMATCH, caught.exception.code)

    def test_t49_resource_limit_exceeded_fails_closed(self):
        config, fixture, arm, plan, result = valid_cell("H1", "B0")
        values = s2dr._record_payload(result.budget_receipt, "budget_receipt_digest")
        values.update(resource_words_bound=0, resource_words_used=1, remaining_resource_words=-1)
        budget = s2dr._built(s2dr.S2DRBudgetReceipt, "budget_receipt_digest", **values)
        with self.assertRaises(s2dr.S2DRError) as caught:
            s2dr.validate_s2dr_cell_result(config, fixture, arm, plan, rebuilt_result(result, budget))
        self.assertEqual(s2dr.S2DR_RESOURCE_OR_OPERATION_LIMIT_EXCEEDED, caught.exception.code)

    def test_t50_operation_limit_exceeded_fails_closed(self):
        config, fixture, arm, plan, result = valid_cell("H1", "TSPM1")
        values = s2dr._record_payload(result.budget_receipt, "budget_receipt_digest")
        values.update(
            formation_write_bounds=((1, 293),),
            formation_write_counts=((1, 294),),
            remaining_formation_write_budget=((1, -1),),
        )
        budget = s2dr._built(s2dr.S2DRBudgetReceipt, "budget_receipt_digest", **values)
        with self.assertRaises(s2dr.S2DRError) as caught:
            s2dr.validate_s2dr_cell_result(config, fixture, arm, plan, rebuilt_result(result, budget))
        self.assertEqual(s2dr.S2DR_RESOURCE_OR_OPERATION_LIMIT_EXCEEDED, caught.exception.code)

    def test_t51_result_or_r0_relation_mismatch_fails_closed(self):
        vectors = {arm: (True,) * 5 for arm in s2dr.ARM_IDS}
        self.assertEqual("METHOD_INVALID", synthetic_comparison(vectors, r0_mismatch=True).decision)
