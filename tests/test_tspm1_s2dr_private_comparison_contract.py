from __future__ import annotations

from dataclasses import fields
import hashlib
from pathlib import Path
from types import SimpleNamespace
import subprocess
import unittest
from unittest.mock import patch

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


# Literal unit observations, not inferred backwards from desired P1-P5 vectors.
UNIT_PROBES = (
    ("H1", 1, "AX", True, 0., 0.),
    ("H2", 1, "AX", True, 0., 0.), ("H2", 4, "AX", True, 0., 0.),
    ("H3", 12, "AX", True, 0., 0.),
    ("H4", 6, "AX", True, 0., 0.), ("H4", 6, "AY", True, 0., .6),
    ("H4", 6, "BX", True, .6, 0.),
    ("H5", 8, "AX", True, 0., 0.), ("H5", 8, "P4", True, .8, -.8),
    ("H6", 7, "AX", True, 0., 0.), ("H6", 7, "D1", True, -1., -1.),
    ("H6", 7, "D3", True, -1., 1.), ("H6", 7, "D8", True, 1., 1.),
    ("H7", 4, "AX", True, 0., 0.), ("H7", 4, "NEAR", True, 0., 0.),
    ("H7", 4, "PARTIAL_OUT", False, None, None),
    ("H7", 4, "OUTSIDE", False, None, None), ("H7", 4, "FAR", False, None, None),
)


def comparison_dtos(*, changes=None, error_arm=None, r0_change=None, writes=None):
    """Unit-only result containers. No formation, native states or cell owners."""
    config, fixtures, arms, plans, inner_digest = registry()
    registry_payload = {"evaluation_id": s2dr.S2EE_EVALUATION_ID,
                        "evaluation_contract_digest": s2dr.S2EE_CONTRACT_DIGEST,
                        "config": s2dr._canonical(config), "fixtures": s2dr._canonical(fixtures),
                        "arms": s2dr._canonical(arms), "cell_plans": s2dr._canonical(plans),
                        "inner_registry_digest": inner_digest}
    digest = s2dr._digest(registry_payload)
    results = []
    for plan in plans:
        findings = []
        for history, checkpoint, pair, recognized, audio, visual in UNIT_PROBES:
            if history != plan.history_id:
                continue
            alteration = (changes or {}).get((plan.arm_id, history, checkpoint, pair), {})
            recognized = alteration.get("recognized", recognized)
            audio, visual = alteration.get("audio", audio), alteration.get("visual", visual)
            av = ((audio,) * 8, (visual,) * 18) if recognized else (None, None)
            finding = dict(checkpoint=checkpoint, pair_id=pair, recognized=recognized,
                           context_source="TEST_ONLY", fast_recognized=recognized,
                           auditory_fast_distance=None, visual_fast_distance=None,
                           auditory_slow_status=None, visual_slow_status=None,
                           auditory_selected_slot_id="test.a.slot", visual_selected_slot_id="test.v.slot",
                           auditory_selected_prototype_digest=s2dr._digest(("test.a", audio)),
                           visual_selected_prototype_digest=s2dr._digest(("test.v", visual)),
                           auditory_slow_distance=None, visual_slow_distance=None,
                           selected_av_payload_digest=s2dr._digest(av),
                           selected_auditory_values=av[0], selected_visual_values=av[1])
            finding["observation"] = dict(checkpoint=checkpoint, probe_index=len(findings) + 1,
                                          pair_id=pair, native_recognized=recognized,
                                          selected_auditory_values=av[0], selected_visual_values=av[1])
            findings.append(finding)
        payload = {"test_only": True, "fast": {"slots": [{"slot_id": "test.fast.0"}]},
                   "auditory": {"bank_id": "test.a", "config_digest": "a" * 64,
                                "slots": [{"slot_id": "test.a.0"}]},
                   "visual": {"bank_id": "test.v", "config_digest": "b" * 64,
                              "slots": [{"slot_id": "test.v.0"}]}}
        if r0_change and plan.arm_id == "R0" and plan.history_id == "H1":
            if r0_change == "observation":
                findings[0]["observation"]["native_recognized"] = False
            elif r0_change == "slot":
                payload["fast"]["slots"][0]["slot_id"] = "test.foreign"
            else:
                payload["auditory"][r0_change] = "test.foreign"
        # Budgets here are scoring inputs, not attested operation receipts.
        count = (writes or {}).get(plan.arm_id, 0) if plan.history_id == "H1" else 0
        result = SimpleNamespace(
            cell_id=plan.cell_id, cell_plan_digest=plan.cell_plan_digest,
            poststate_payload=payload, event_payloads=({"event": "TEST_ONLY", "consolidation_status": "TEST_ONLY"},),
            finding_payloads=tuple(findings),
            budget_receipt=SimpleNamespace(formation_write_counts=((1, count),)),
            cell_receipt=SimpleNamespace(internal_error_code="TEST_ERROR" if plan.arm_id == error_arm else None),
            cell_result_digest=s2dr._digest((plan.cell_id, payload, findings, count, error_arm)))
        results.append(result)
    return config, plans, tuple(results), digest, registry_payload


def unit_attestation():
    attempt = object.__new__(s2dr._S2EFAttempt)
    attempt.status = "TEST_ONLY"
    attempt.evidence = [SimpleNamespace(record_digest=s2dr._digest(("test.evidence", n))) for n in range(56)]
    return attempt


def compare_dtos(testcase, bundle):
    config, plans, results, digest, _ = bundle
    attempt = unit_attestation()
    with testcase.assertRaises(s2dr.S2DRError):
        s2dr.compare_s2dr_results(config, plans, results, digest, attestation=attempt)
    try:
        with patch.object(s2dr._S2EFAttempt, "validate_results", autospec=True) as validation:
            try:
                return s2dr.compare_s2dr_results(config, plans, results, digest, attestation=attempt)
            finally:
                validation.assert_called_once_with(attempt, config, plans, results, digest)
    finally:
        with testcase.assertRaises(s2dr.S2DRError):
            s2dr.compare_s2dr_results(config, plans, results, digest, attestation=attempt)


class MemoryPath:
    def __init__(self, store, key):
        self.store, self.key = store, key

    def __truediv__(self, name):
        return MemoryPath(self.store, self.key + "/" + name)

    def read_bytes(self):
        self.store.events.append("read:" + self.key)
        if self.key not in self.store.data:
            raise FileNotFoundError(self.key)
        return self.store.data[self.key]


class PublicationDouble:
    """In-memory publication protocol, never a durable filesystem claim."""
    def __init__(self, mode):
        self.mode, self.data, self.events = mode, {}, []
        self.created_reservation = True
        self.paths = {key: MemoryPath(self, key) for key in ("reservation", "staging", "final")}

    def write_new(self, path, record):
        self.events.append("write:" + path.key)
        if path.key in self.data:
            raise FileExistsError(path.key)
        raw = s2dr._json_bytes(record.payload())
        partial = ((path.key == "staging" and self.mode == "stage_partial") or
                   (path.key.endswith("114.json") and self.mode == "terminal_partial"))
        self.data[path.key] = raw[:8] if partial else raw
        self.events.append("flush:" + path.key)
        if ((path.key == "staging" and self.mode == "stage_flush") or
                (path.key.endswith("114.json") and self.mode in ("terminal_full", "terminal_partial"))):
            raise OSError("injected flush failure")
        if path.read_bytes() != raw:
            raise OSError("incomplete write")

    def publish(self):
        self.events.append("publish")
        if self.mode == "rename" or "final" in self.data:
            raise FileExistsError("no replace")
        self.data["final"] = self.data.pop("staging")
        self.events.append("flush:final")
        if self.mode == "final_flush":
            raise OSError("injected final flush failure")
        if self.mode == "final_partial":
            self.data["final"] = b"{"
        if self.mode == "final_foreign":
            self.data["final"] = b'{"foreign":true}'


def publication_fixture(mode="success"):
    attempt = object.__new__(s2dr._S2EFAttempt)
    attempt.store = PublicationDouble(mode)
    attempt.status, attempt.journal, attempt.evidence = "RUNNING", [], []
    attempt._final_flush_confirmed = attempt._final_content_verified = False
    attempt._completion_proof_digest = None
    attempt.reservation = s2dr._record(
        "AttemptReservation", execution_authorization_digest="a" * 64,
        execution_plan_digest="b" * 64, study_id=s2dr.S2EE_STUDY_ID,
        execution_domain_digest="c" * 64, attempt_id="001", status="RESERVED")
    attempt.store.data["reservation/reservation.json"] = s2dr._json_bytes(attempt.reservation.payload())
    for ordinal in range(1, 113):
        entry = s2dr._record(
            "AttemptJournalEntry", reservation_digest=attempt.reservation.record_digest,
            journal_ordinal=ordinal,
            previous_journal_entry_digest_or_null=attempt.journal[-1].record_digest if attempt.journal else None,
            status="RUNNING", cell_start_digest_or_null="d" * 64,
            cell_evidence_digest_or_null="e" * 64 if ordinal % 2 == 0 else None,
            sealed_artifact_digest_or_null=None, error_or_null=None)
        attempt.journal.append(entry)
        attempt.store.data[f"reservation/journal-{ordinal:03d}.json"] = s2dr._json_bytes(entry.payload())
    payload = {"unit_only_artifact": True}
    artifact = SimpleNamespace(record_digest=s2dr._digest(payload), payload=lambda: payload)
    if mode == "destination_exists":
        attempt.store.data["final"] = s2dr._json_bytes(payload)
    return attempt, artifact


def unit_artifact_verification(attempt, path, expected):
    attempt.store.events.append("verify:" + path.key)
    s2dr._require(path.read_bytes() == s2dr._json_bytes(expected.payload()), "unit artifact differs")


class TSPM1S2DRPrivateComparisonContractTests(unittest.TestCase):
    def test_t01_parent_and_source_digests(self):
        config, _, _, _, _ = registry()
        self.assertIn(s2dr.S2DR_S2DS_PASS_DIGEST, config.parent_artifact_digests)
        paths = (
            "mcm_field_organism/__init__.py",
            "mcm_field_organism/_ppb1_active_receptor_batch_binding.py",
            "mcm_field_organism/_ppb1_receptor_profiles.py",
            "mcm_field_organism/_ppb1_reference.py",
            "mcm_field_organism/_ppb1_s1wq_perceptual_state_lifecycle.py",
            "mcm_field_organism/_ppb1_s1wu_read_only_perceptual_probe.py",
            "mcm_field_organism/_tspm1_private.py",
            "mcm_field_organism/_tspm1_s2dr_private_comparison.py",
            "mcm_field_organism/broadband_hearing_path.py",
            "mcm_field_organism/browser_receptor_bridge.py",
            "mcm_field_organism/browser_world_contract.py",
            "mcm_field_organism/carrier_baselines.py",
            "mcm_field_organism/controlled_audio_source.py",
            "mcm_field_organism/finite_video_path.py",
            "mcm_field_organism/log_spectral_receptor.py",
            "mcm_field_organism/receptor_contract.py",
            "mcm_field_organism/receptor_time_model.py",
            "mcm_field_organism/root_lazy_exports.py",
        )
        expected = tuple({"repository_relative_path": path,
                          "raw_sha256": hashlib.sha256((ROOT / path).read_bytes()).hexdigest(),
                          "git_blob": subprocess.check_output(
                              ["git", "-C", str(ROOT), "rev-parse", "HEAD:" + path], text=True).strip()}
                         for path in paths)
        self.assertEqual(tuple(sorted(paths)), paths)
        self.assertEqual(expected, s2dr._project_source_inventory())
        self.assertEqual(tuple(item["raw_sha256"] for item in expected), config.source_blob_digests)
        identity = expected[5]
        raw = (ROOT / paths[5]).read_bytes()
        codes = tuple(s2dr._source_code_objects(s2dr.probe_s1wu_perceptual_state.__code__))
        caller = next(code for code in codes if code.co_name == "<genexpr>" and code.co_firstlineno == 209)
        with self.subTest("G1"):
            for dimension in (8, 18):
                s2dr._validate_distance_source(raw, identity, identity, ["<genexpr>", 211], dimension, caller_code=caller)
                s2dr._validate_distance_source(raw, identity, identity, ["<genexpr>", 211], dimension)
        with self.subTest("G2"):
            for key, value in (("repository_relative_path", paths[3]), ("git_blob", "f" * 40)):
                with self.assertRaises(s2dr.S2DRError):
                    s2dr._validate_distance_source(raw, {**identity, key: value}, identity, ["<genexpr>", 211], 8)
        with self.subTest("G3"):
            for site, code in ((["<genexpr>", 209], caller),
                               (["<genexpr>", 211], caller.replace(co_firstlineno=210))):
                with self.assertRaises(s2dr.S2DRError):
                    s2dr._validate_distance_source(raw, identity, identity, site, 8, caller_code=code)
        with self.subTest("G4"):
            for mapping in ((), (caller, caller)):
                with patch.object(s2dr, "_source_code_objects", return_value=mapping):
                    with self.assertRaises(s2dr.S2DRError):
                        s2dr._validate_distance_source(raw, identity, identity, ["<genexpr>", 211], 8)
        with self.subTest("G5"):
            named = s2dr._per_arm_metrics.__code__
            own = next(item for item in expected if item["repository_relative_path"].endswith("_s2dr_private_comparison.py"))
            own_raw = (ROOT / own["repository_relative_path"]).read_bytes()
            s2dr._validate_distance_source(own_raw, own, own, [named.co_name, named.co_firstlineno], 8)
            for dimension in (0, 7, 26, True):
                with self.assertRaises(s2dr.S2DRError):
                    s2dr._validate_distance_source(raw, identity, identity, ["<genexpr>", 211], dimension)
            meter = s2dr._OperationMeter("B0", "unit.cell", "PROBE", 1)
            frame = SimpleNamespace(f_code=s2dr.normalized_mean_l1_distance.__code__,
                                    f_locals={"first": (0.,) * 8, "second": (0.,) * 18})
            meter._observe(frame, "call", None)
            self.assertIsInstance(meter.failure, s2dr.S2DRError)
            self.assertEqual(s2dr.S2DR_RESULT_RELATION_MISMATCH, meter.failure.code)
            self.assertEqual([], meter.distances)

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
        self.assertFalse(s2dr._EXECUTION_RELEASE_ENABLED)
        bundle = comparison_dtos()
        result = compare_dtos(self, bundle)
        assert_digest_guard(self, result, "comparison_result_digest")
        self.assertEqual(s2dr.S2EE_EVALUATION_ID, result.evaluation_id)
        self.assertEqual(s2dr._digest(bundle[4]), result.registry_digest)
        self.assertEqual(s2dr._registry_payload(registry()), bundle[4])
        self.assertEqual(8, len(result.per_arm_metrics))
        self.assertEqual(8, len(result.all_arm_ranking))
        self.assertEqual(6, len(result.simple_baseline_ranking))
        self.assertEqual(56, len(result.ordered_cell_evidence_digests))
        self.assertTrue({"evaluation_id", "per_arm_metrics", "all_arm_ranking",
                         "simple_baseline_ranking", "ordered_cell_evidence_digests"}
                        <= {field.name for field in fields(result)})
        self._publication_subcases()

    def _publication_subcases(self):
        contract = s2dr._ee_contract()
        cases = (("P1", "stage_partial", "FAILED"), ("P1", "stage_flush", "FAILED"),
                 ("P2", "rename", "FAILED"), ("P2", "destination_exists", "ABORTED_INCOMPLETE"),
                 ("P3", "final_flush", "ABORTED_INCOMPLETE"),
                 ("P4", "final_partial", "ABORTED_INCOMPLETE"),
                 ("P4", "final_foreign", "ABORTED_INCOMPLETE"),
                 ("P5", "success", "COMPLETED"),
                 ("P9", "terminal_full", "COMPLETED"),
                 ("P9", "terminal_partial", "ABORTED_INCOMPLETE"))
        with patch.object(s2dr, "_ee_contract", return_value=contract), patch.object(
                s2dr._S2EFAttempt, "_verify_artifact", new=unit_artifact_verification), patch.object(
                s2dr.os.path, "lexists", side_effect=lambda path: path.key in path.store.data):
            for case, mode, status in cases:
                with self.subTest(case=case, mode=mode):
                    attempt, artifact = publication_fixture(mode)
                    if mode == "success":
                        self.assertIs(artifact, attempt._finish_publication(artifact))
                    else:
                        with self.assertRaises((OSError, s2dr.S2DRError)) as caught:
                            attempt._finish_publication(artifact)
                        attempt._publication_failure(artifact, caught.exception)
                    self.assertEqual(status, attempt.status)
                    self.assertTrue(attempt.store.created_reservation)
                    self.assertLessEqual(attempt.store.events.count("publish"), 1)
                    self.assertLessEqual(attempt.store.events.count("flush:final"), 1)
                    self.assertLessEqual(attempt.store.events.count("flush:reservation/journal-114.json"), 1)
                    if case == "P1":
                        self.assertNotIn("publish", attempt.store.events)
                    if case in ("P1", "P2", "P3", "P4"):
                        terminal = attempt.store.data.get("reservation/journal-114.json")
                        if terminal is not None:
                            self.assertNotEqual("COMPLETED", s2dr._loads(terminal)["status"])
                    if case == "P3":
                        self.assertEqual(s2dr._json_bytes(artifact.payload()), attempt.store.data["final"])
                        self.assertFalse(attempt._final_flush_confirmed)
                    if mode == "success":
                        ordered = ("write:staging", "flush:staging", "verify:staging",
                                   "write:reservation/journal-113.json", "flush:reservation/journal-113.json",
                                   "publish", "flush:final", "verify:final",
                                   "write:reservation/journal-114.json", "flush:reservation/journal-114.json")
                        positions = [attempt.store.events.index(event) for event in ordered]
                        self.assertEqual(sorted(positions), positions)
                        with self.subTest("P6"):
                            before = dict(attempt.store.data)
                            with patch.object(s2dr._S2EFAttempt, "_verify_completion", side_effect=OSError("later read unavailable")) as late:
                                attempt._publication_failure(artifact, OSError("late"))
                                late.assert_not_called()
                            self.assertEqual("COMPLETED", attempt.status)
                            self.assertEqual(before, attempt.store.data)
            for mutation in ("missing", "corrupt", "foreign"):
                with self.subTest(case="P7" if mutation == "missing" else "P8", mutation=mutation):
                    attempt, artifact = publication_fixture()
                    attempt._finish_publication(artifact)
                    terminal_path = "reservation/journal-114.json"
                    if mutation == "missing":
                        del attempt.store.data[terminal_path]
                    elif mutation == "corrupt":
                        attempt.store.data[terminal_path] = b"{"
                    else:
                        terminal = s2dr._loads(attempt.store.data[terminal_path])
                        terminal.pop("schema_version")
                        terminal.pop("record_digest")
                        terminal["reservation_digest"] = FOREIGN_DIGEST
                        attempt.store.data[terminal_path] = s2dr._json_bytes(
                            s2dr._record("AttemptJournalEntry", **terminal).payload())
                    attempt.status = "SEALED"
                    attempt._final_flush_confirmed = attempt._final_content_verified = False
                    before = dict(attempt.store.data)
                    with self.assertRaises((OSError, ValueError, s2dr.S2DRError)):
                        attempt._verify_completion(artifact)
                    attempt._publication_failure(artifact, OSError("process lost"))
                    self.assertEqual("ABORTED_INCOMPLETE", attempt.status)
                    self.assertEqual(before, attempt.store.data)
                    self.assertEqual(1, attempt.store.events.count("publish"))
                    self.assertTrue(attempt.store.created_reservation)
            # A complete postflush terminal chain remains classifiable read-only after process loss.
            attempt, artifact = publication_fixture()
            attempt._finish_publication(artifact)
            attempt._final_flush_confirmed = attempt._final_content_verified = False
            before = dict(attempt.store.data)
            attempt._verify_completion(artifact)
            self.assertEqual(before, attempt.store.data)

    def test_t35_p1_p5_projection(self):
        result = compare_dtos(self, comparison_dtos())
        metrics = dict(result.per_arm_metrics)["TSPM1"]
        self.assertEqual((True,) * 5, metrics["predicate_vector"])
        self.assertEqual((0, 1, 0, True), (metrics["functional_error_sum"],
                         metrics["observed_capture_latency_rank"], metrics["total_formation_write_words"],
                         metrics["ax_preserved"]))
        self.assertEqual(18, len(metrics["probe_metrics"]))
        self.assertEqual(tuple(f"{h}/{step}/{pair}" for h, step, pair, *_ in UNIT_PROBES),
                         tuple(row["probe_key"] for row in metrics["probe_metrics"]))
        self.assertTrue(all(row["functional_correct"] for row in metrics["probe_metrics"]))
        changes = {(arm, h, step, pair): {"recognized": False}
                   for arm in ("TSPM1", "R0") for h, step, pair in (("H2", 1, "AX"), ("H6", 7, "D3"))}
        changed = dict(compare_dtos(self, comparison_dtos(changes=changes)).per_arm_metrics)["TSPM1"]
        self.assertEqual((True, True, True, False, True), changed["predicate_vector"])
        self.assertEqual((2, 4), (changed["functional_error_sum"], changed["observed_capture_latency_rank"]))

    def test_t36_method_invalid_priority(self):
        result = compare_dtos(self, comparison_dtos(r0_change="bank_id"))
        self.assertEqual((True,) * 5, dict(result.per_arm_predicate_vectors)["TSPM1"])
        self.assertEqual("METHOD_INVALID", result.decision)

    def test_t37_tspm1_invalid_priority(self):
        self.assertEqual("METHOD_INVALID", compare_dtos(self, comparison_dtos(error_arm="TSPM1")).decision)
        changes = {(arm, "H1", 1, "AX"): {"recognized": False} for arm in ("TSPM1", "R0")}
        result = compare_dtos(self, comparison_dtos(changes=changes))
        self.assertTrue(result.r0_exact_equivalence)
        self.assertEqual("TSPM1_FUNCTION_NOT_VALID", result.decision)

    def test_t38_baseline_and_tie(self):
        result = compare_dtos(self, comparison_dtos())
        self.assertEqual(("FUNCTION_VALID_SIMPLE_BASELINE_EXPLAINS", "B0"),
                         (result.decision, result.strongest_simple_baseline_id))
        self.assertEqual(tuple(sorted(s2dr.SIMPLE_BASELINE_ORDER)), result.simple_baseline_ranking)
        tied = {arm: dict(predicate_vector=(True,) * 5, functional_error_sum=0,
                         observed_capture_latency_rank=1, total_formation_write_words=0)
                for arm in s2dr.SIMPLE_BASELINE_ORDER}
        for field, better, worse in (("functional_error_sum", 0, 1),
                                    ("observed_capture_latency_rank", 1, 4),
                                    ("total_formation_write_words", 0, 1)):
            with self.subTest(priority=field):
                rows = {arm: dict(value) for arm, value in tied.items()}
                rows["B0"][field] = worse
                rows["B4"][field] = better
                if field == "functional_error_sum":
                    rows["B0"]["observed_capture_latency_rank"] = 1
                    rows["B4"]["observed_capture_latency_rank"] = 4
                    rows["B4"]["total_formation_write_words"] = 99
                elif field == "observed_capture_latency_rank":
                    rows["B4"]["total_formation_write_words"] = 99
                self.assertLess(s2dr._rank_key("B4", rows), s2dr._rank_key("B0", rows))
        ranked = compare_dtos(self, comparison_dtos(writes={"B0": 2}))
        self.assertEqual("B1_BUDGET_MATCHED", ranked.strongest_simple_baseline_id)
        self.assertEqual("FUNCTION_VALID_SIMPLE_BASELINE_EXPLAINS", ranked.decision)

    def test_t39_advantage_with_r0(self):
        changes = {(arm, "H1", 1, "AX"): {"recognized": False} for arm in s2dr.SIMPLE_BASELINE_ORDER}
        result = compare_dtos(self, comparison_dtos(changes=changes))
        self.assertTrue(result.r0_exact_equivalence)
        self.assertEqual((True,) * 5, dict(result.per_arm_predicate_vectors)["TSPM1"])
        self.assertTrue(all(not all(dict(result.per_arm_predicate_vectors)[arm]) for arm in s2dr.SIMPLE_BASELINE_ORDER))
        self.assertEqual("TSPM1_TWO_TIMESCALE_ENGINEERING_ADVANTAGE_OVER_SIMPLE_BASELINES", result.decision)

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
        config, plans, results, digest, payload = comparison_dtos()
        duplicate = (config, (plans[0],) * 56, (results[0],) * 56, digest, payload)
        with self.assertRaises(s2dr.S2DRError) as caught:
            s2dr.compare_s2dr_results(*duplicate[:4])
        self.assertEqual(s2dr.S2DR_AUTHORIZATION_MISMATCH, caught.exception.code)
        with self.assertRaises(s2dr.S2DRError) as caught:
            compare_dtos(self, duplicate)
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
        self.assertTrue(compare_dtos(self, comparison_dtos()).r0_exact_equivalence)
        for mutation in ("bank_id", "config_digest", "slot", "observation"):
            with self.subTest(mutation=mutation):
                result = compare_dtos(self, comparison_dtos(r0_change=mutation))
                self.assertFalse(result.r0_exact_equivalence)
                self.assertEqual("METHOD_INVALID", result.decision)
