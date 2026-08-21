"""S1-TN synthetic definitions. First execution is reserved for S1-TO."""

from __future__ import annotations

import ast
import copy
from dataclasses import fields, is_dataclass, replace
import hashlib
import json
import math
from pathlib import Path
import unittest

import mcm_field_organism.four_node_candidate_observation_envelope as envelope_module
from mcm_field_organism.four_node_candidate_observation_envelope import (
    ATLAS_ARTIFACT_DIGEST, ATLAS_FILE_SHA256, ATLAS_RESULT_DIGEST, AXIS_DIGEST,
    CANONICALIZATION_ID, CONTRACT_DIGEST, CONTRACT_ID, EXPOSURE_FIXTURE_DIGEST,
    FAILURE_CODES, INVALID_STATUS, NODE_ORDER, PLAN_ROLES, ROOT_FAMILIES,
    SCHEMA_ID, SOURCE_CONTRACT_ID, VALIDATION_SCHEMA_ID, VALID_STATUS,
    CandidateBalanceCheckpointRecord, CandidateEnvelopeIdentity,
    CandidateEnvelopeValidationRegistry, CandidateEnvelopeValidationResult,
    CandidateFieldCheckpointRecord, CandidateFieldProfile,
    CandidateObservationEnvelope, CandidatePlanRecord,
    CandidateStateCheckpointRecord, CandidateTransitionBalanceRecord,
    CandidateTransitionRecord, DisabledFullPathProfile, EnvelopeCompletionRecord,
    NullPathPairRecord, ReadoutAblationRecord, ReleaseLifecycleLink,
    ReuseLifecycleLink, build_candidate_envelope_validation_registry,
    validate_candidate_observation_envelope,
)


SHA = "1" * 64
BALANCE_SCHEMA_ID = "synthetic.generic.balance.v1"
BALANCE_ROLE_AXIS = ("available", "engaged", "refractory")
CHECKPOINT_AXIS = tuple(
    (position, plan_role, checkpoint_role)
    for position, plan_role in enumerate(PLAN_ROLES, 1)
    for checkpoint_role in (
        ("PRE_COMPETITION", "POST_COMPETITION", "ALIGNED_PRE_PROBE", "POST_PROBE_READOUT")
        if plan_role.startswith("C_") else
        ("ALIGNED_PRE_PROBE", "POST_PROBE_READOUT")
    )
)


def _canonical(value):
    return json.dumps(value, ensure_ascii=True, allow_nan=False, sort_keys=True,
                      separators=(",", ":")).encode("ascii")


def _digest(value):
    return hashlib.sha256(_canonical(value)).hexdigest()


def _seal(value, digest_name):
    value[digest_name] = _digest({key: item for key, item in value.items() if key != digest_name})
    return value


def _checkpoint(ordinal, position, plan_role, checkpoint_role):
    nullable = (plan_role, checkpoint_role) == ("C_GAP", "POST_COMPETITION")
    value = {
        "checkpoint_ordinal": ordinal, "plan_position": position,
        "plan_role": plan_role, "checkpoint_role": checkpoint_role,
        "checkpoint_tick": ordinal * 10, "fixture_event_digest": f"{ordinal + 10:064x}",
        "event_chain_digest": f"{ordinal + 20:064x}",
        "field_state_digest": f"{ordinal + 30:064x}", "carry_digest": f"{ordinal + 40:064x}",
        "private_state_digest": f"{ordinal + 50:064x}",
        "candidate_configuration_id": "2" * 64, "dependency_digest": f"{ordinal + 60:064x}",
        "distribution_digest_or_none": f"{ordinal + 70:064x}",
        "alignment_digest_or_none": f"{ordinal + 80:064x}",
        "receptor_contact": [None] * 4 if nullable else [float(position), 0.0, 0.0, 0.0],
        "activation": [ordinal / 1000.0, 0.0, 0.0, 0.0],
        "afterimage": [0.0, ordinal / 2000.0, 0.0, 0.0],
        "field_tick": ordinal * 10, "layer_tick": ordinal * 10,
    }
    return _seal(value, "checkpoint_digest")


def _plans(checkpoints):
    result = []
    for position, role in enumerate(PLAN_ROLES, 1):
        selected = [item for item in checkpoints if item["plan_position"] == position]
        value = {
            "plan_position": position, "plan_role": role,
            "exposure_plan_id": "synthetic-shared-exposure-plan",
            "fresh_state_id": f"synthetic-fresh-{position}",
            "candidate_configuration_id": "2" * 64,
            "checkpoint_digests": [item["checkpoint_digest"] for item in selected],
            "first_carry_digest": selected[0]["carry_digest"],
            "last_carry_digest": selected[-1]["carry_digest"],
            "terminal_event_chain_digest": selected[-1]["event_chain_digest"],
            "completion_status": "PLAN_STRUCTURALLY_COMPLETE",
        }
        result.append(_seal(value, "plan_digest"))
    return result


def _path(role, plans, checkpoints):
    value = {
        "path_role": role, "candidate_updates_enabled": False,
        "plan_records": copy.deepcopy(plans), "checkpoint_records": copy.deepcopy(checkpoints),
        "candidate_state_digests": [], "candidate_carry_digests": [],
        "terminal_event_chain_digest": checkpoints[-1]["event_chain_digest"],
    }
    return _seal(value, "path_digest")


def synthetic_envelope():
    identity = _seal({
        "schema_id": SCHEMA_ID, "contract_id": CONTRACT_ID, "contract_digest": CONTRACT_DIGEST,
        "candidate_role_id": "synthetic-candidate-role",
        "candidate_configuration_id": "2" * 64,
        "exposure_plan_id": "synthetic-shared-exposure-plan",
        "exposure_fixture_digest": EXPOSURE_FIXTURE_DIGEST,
        "manifest_digest": "3" * 64, "registration_digest": "4" * 64,
        "geometry_id": "synthetic-four-node-geometry", "node_order_id": "node-a-node-b-node-c-node-d",
        "source_inventory_digest": "5" * 64, "atlas_file_sha256": ATLAS_FILE_SHA256,
        "atlas_artifact_digest": ATLAS_ARTIFACT_DIGEST, "atlas_result_digest": ATLAS_RESULT_DIGEST,
        "axis_digest": AXIS_DIGEST, "canonicalization_id": CANONICALIZATION_ID,
        "runtime_id": "synthetic-structure-only-runtime",
    }, "identity_digest")
    checkpoints = [_checkpoint(index, *axis) for index, axis in enumerate(CHECKPOINT_AXIS, 1)]
    plans = _plans(checkpoints)
    profile = _seal({
        "checkpoint_digests": [item["checkpoint_digest"] for item in checkpoints],
        "signed_components": [number for item in checkpoints
                              for vector in (item["activation"], item["afterimage"]) for number in vector],
    }, "profile_digest")
    balances = []
    for index, checkpoint in enumerate(checkpoints, 1):
        value = {
            "checkpoint_ordinal": index, "balance_schema_id": BALANCE_SCHEMA_ID,
            "role_axis": list(BALANCE_ROLE_AXIS),
            "local_coordinates": [[1.0, 0.0, 0.0] for _ in NODE_ORDER],
            "local_totals": [1.0] * 4, "local_dissipation": [0.0] * 4,
            "global_total": 4.0, "inflow": [0.0] * 3, "outflow": [0.0] * 3,
            "transfers": [0.0] * 3, "residual": 0.0,
            "private_state_digest": checkpoint["private_state_digest"],
            "field_checkpoint_digest": checkpoint["checkpoint_digest"],
        }
        balances.append(_seal(value, "balance_checkpoint_digest"))
    states = []
    for index, (checkpoint, balance) in enumerate(zip(checkpoints, balances, strict=True), 1):
        value = {
            "checkpoint_ordinal": index, "field_checkpoint_digest": checkpoint["checkpoint_digest"],
            "private_state_digest": checkpoint["private_state_digest"],
            "candidate_configuration_id": "2" * 64, "carry_digest": checkpoint["carry_digest"],
            "event_chain_digest": checkpoint["event_chain_digest"],
            "balance_schema_id": BALANCE_SCHEMA_ID,
            "balance_checkpoint_digest": balance["balance_checkpoint_digest"],
        }
        states.append(_seal(value, "state_checkpoint_digest"))
    transitions = []
    transition_balances = []
    for ordinal in range(1, 128):
        before_index, after_index = (ordinal - 1) % 40, ordinal % 40
        plan_position = ((ordinal - 1) * 17) // 127 + 1
        value = {
            "interval_ordinal": ordinal, "plan_position": plan_position,
            "plan_role": PLAN_ROLES[plan_position - 1], "event_source_digest": f"{ordinal + 100:064x}",
            "before_state_digest": states[before_index]["state_checkpoint_digest"],
            "after_state_digest": states[after_index]["state_checkpoint_digest"],
            "before_carry_digest": states[before_index]["carry_digest"],
            "after_carry_digest": states[after_index]["carry_digest"],
            "before_balance_digest": balances[before_index]["balance_checkpoint_digest"],
            "after_balance_digest": balances[after_index]["balance_checkpoint_digest"],
            "field_progress_digest": f"{ordinal + 200:064x}", "causal_source": "FIELD_HISTORY",
            "receipt_or_diagnostic_digest": f"{ordinal + 300:064x}",
        }
        transitions.append(_seal(value, "transition_digest"))
        balance_value = {
            "interval_ordinal": ordinal,
            "before_balance_digest": balances[before_index]["balance_checkpoint_digest"],
            "after_balance_digest": balances[after_index]["balance_checkpoint_digest"],
            "transfers": [0.0] * 3, "inflows": [0.0] * 3, "outflows": [0.0] * 3,
            "dissipation": [0.0] * 3, "residual": 0.0, "causal_source": "FIELD_HISTORY",
        }
        transition_balances.append(_seal(balance_value, "transition_balance_digest"))
    readouts = [item for item in checkpoints if item["checkpoint_role"] == "POST_PROBE_READOUT"]
    ablations = []
    for checkpoint in readouts:
        value = {
            "plan_position": checkpoint["plan_position"], "plan_role": checkpoint["plan_role"],
            "exposure_plan_id": identity["exposure_plan_id"],
            "fresh_state_id": f"synthetic-fresh-{checkpoint['plan_position']}",
            "candidate_configuration_id": identity["candidate_configuration_id"],
            "history_prefix_digest": checkpoint["event_chain_digest"],
            "event_chain_digest": checkpoint["event_chain_digest"],
            "receptor_contact": checkpoint["receptor_contact"],
            "aligned_activation_before": checkpoint["activation"],
            "aligned_afterimage_before": checkpoint["afterimage"],
            "private_state_before_digest": checkpoint["private_state_digest"],
            "geometry_id": identity["geometry_id"], "readout_tick": checkpoint["checkpoint_tick"],
            "probe_digest": checkpoint["fixture_event_digest"],
            "original_readout": checkpoint["activation"] + checkpoint["afterimage"],
            "ablated_readout": checkpoint["activation"] + checkpoint["afterimage"],
            "disabled_scope": "CANDIDATE_READOUT_FEEDBACK_ONLY",
            "exclusive_disable_proof": True, "excluded_from_main_profile": True,
        }
        ablations.append(_seal(value, "ablation_digest"))
    disabled = _path("CANDIDATE_DISABLED_FULL_PATH", plans, checkpoints)
    reference = _path("INDEPENDENT_FIELD_CORE_REFERENCE", plans, checkpoints)
    pairs = []
    for index, (left, right) in enumerate(zip(disabled["checkpoint_records"], reference["checkpoint_records"], strict=True), 1):
        pairs.append(_seal({
            "checkpoint_ordinal": index, "disabled_checkpoint_digest": left["checkpoint_digest"],
            "reference_checkpoint_digest": right["checkpoint_digest"], "bit_equal": True,
        }, "pair_digest"))
    selected_ordinals = [item["checkpoint_ordinal"] for item in checkpoints if item["plan_position"] in (12, 13)]
    release = _seal({
        "early_plan_digest": plans[11]["plan_digest"], "late_plan_digest": plans[12]["plan_digest"],
        "early_checkpoint_digests": plans[11]["checkpoint_digests"],
        "late_checkpoint_digests": plans[12]["checkpoint_digests"],
        "state_checkpoint_digests": [states[index - 1]["state_checkpoint_digest"] for index in selected_ordinals],
        "balance_checkpoint_digests": [balances[index - 1]["balance_checkpoint_digest"] for index in selected_ordinals],
        "shared_provenance_digest": "6" * 64, "functional_loss_proof_digest": "7" * 64,
        "reusable_local_capacity": [1.0, 1.0, 1.0, 1.0], "reset_exclusion": True,
        "clipping_exclusion": True, "restart_exclusion": True, "recovery_toggle_exclusion": True,
    }, "release_link_digest")
    reuse = _seal({
        "released_plan_digest": plans[13]["plan_digest"], "early_plan_digest": plans[14]["plan_digest"],
        "fresh_early_plan_digest": plans[15]["plan_digest"], "fresh_late_plan_digest": plans[16]["plan_digest"],
        "release_link_digest": release["release_link_digest"],
        "pre_history_balance_digests": [balances[0]["balance_checkpoint_digest"]] * 4,
        "local_reuse_demand": [1.0] * 4,
        "readout_checkpoint_digests": [item["checkpoint_digest"] for item in readouts[13:17]],
        "role_identity_digest": "8" * 64,
    }, "reuse_link_digest")
    root = {
        "envelope_identity": identity,
        "candidate_field_profile": {"plans": plans, "field_checkpoints": checkpoints, "field_profile": profile},
        "candidate_internal_evidence": {
            "balance_schema_id": BALANCE_SCHEMA_ID, "balance_role_axis": list(BALANCE_ROLE_AXIS),
            "state_checkpoints": states, "transitions": transitions,
            "balance_checkpoints": balances, "transition_balances": transition_balances,
        },
        "candidate_controls": {
            "readout_ablations": ablations, "disabled_candidate_path": disabled,
            "independent_reference_path": reference, "null_path_pairs": pairs,
        },
        "lifecycle_links": {"release": release, "reuse": reuse},
    }
    family_digests = [_digest(root[name]) for name in ROOT_FAMILIES if name != "completion"]
    root["completion"] = _seal({
        "ordered_family_digests": family_digests, "plan_count": 17,
        "field_checkpoint_count": 40, "candidate_interval_count": 127,
        "post_probe_readout_count": 17, "null_path_pair_count": 40,
        "information_barriers_status": "INFORMATION_BARRIERS_SATISFIED",
        "envelope_digest": _digest(root),
        "completion_status": "CANDIDATE_ENVELOPE_STRUCTURALLY_COMPLETE",
        "partial_result": False,
    }, "completion_digest")
    return root


def _bytes_for(root):
    return _canonical(root)


def _mutated_result(code):
    root = synthetic_envelope()
    field = root["candidate_field_profile"]
    internal = root["candidate_internal_evidence"]
    controls = root["candidate_controls"]
    links = root["lifecycle_links"]
    if code == "ENVELOPE_CANONICAL_FORM_INVALID":
        raw = json.dumps(root, indent=2).encode("ascii")
    elif code == "ENVELOPE_ROOT_SCHEMA_INVALID":
        root["unknown"] = None; raw = _bytes_for(root)
    elif code == "ENVELOPE_IDENTITY_INVALID":
        root["envelope_identity"]["runtime_id"] = ""; _seal(root["envelope_identity"], "identity_digest"); raw = _bytes_for(root)
    elif code == "CANDIDATE_CONFIGURATION_IDENTITY_INVALID":
        root["envelope_identity"]["candidate_configuration_id"] = "bad"; _seal(root["envelope_identity"], "identity_digest"); raw = _bytes_for(root)
    elif code == "ATLAS_REFERENCE_INVALID":
        root["envelope_identity"]["atlas_result_digest"] = "0" * 64; _seal(root["envelope_identity"], "identity_digest"); raw = _bytes_for(root)
    elif code == "EXPOSURE_REFERENCE_INVALID":
        root["envelope_identity"]["axis_digest"] = "0" * 64; _seal(root["envelope_identity"], "identity_digest"); raw = _bytes_for(root)
    elif code == "PLAN_AXIS_INVALID":
        field["plans"][0], field["plans"][1] = field["plans"][1], field["plans"][0]; raw = _bytes_for(root)
    elif code == "CHECKPOINT_AXIS_INVALID":
        field["field_checkpoints"][0], field["field_checkpoints"][1] = field["field_checkpoints"][1], field["field_checkpoints"][0]; raw = _bytes_for(root)
    elif code == "FIELD_VECTOR_INVALID":
        field["field_checkpoints"][0]["activation"] = [0.0]; _seal(field["field_checkpoints"][0], "checkpoint_digest"); raw = _bytes_for(root)
    elif code == "RECEPTOR_NULLABILITY_INVALID":
        field["field_checkpoints"][0]["receptor_contact"] = [None] * 4; _seal(field["field_checkpoints"][0], "checkpoint_digest"); raw = _bytes_for(root)
    elif code == "FIELD_PROFILE_DIGEST_INVALID":
        field["field_profile"]["profile_digest"] = "0" * 64; raw = _bytes_for(root)
    elif code == "STATE_CHECKPOINT_COUNT_INVALID":
        internal["state_checkpoints"].pop(); raw = _bytes_for(root)
    elif code == "STATE_CARRY_CHAIN_INVALID":
        internal["state_checkpoints"][0]["carry_digest"] = "0" * 64; _seal(internal["state_checkpoints"][0], "state_checkpoint_digest"); raw = _bytes_for(root)
    elif code == "TRANSITION_COUNT_INVALID":
        internal["transitions"].pop(); raw = _bytes_for(root)
    elif code == "TRANSITION_CAUSAL_SOURCE_INVALID":
        internal["transitions"][0]["causal_source"] = "COMPARATOR"; _seal(internal["transitions"][0], "transition_digest"); raw = _bytes_for(root)
    elif code == "BALANCE_SCHEMA_INVALID":
        internal["balance_role_axis"] = ["available", "available"]; raw = _bytes_for(root)
    elif code == "BALANCE_CHECKPOINT_COUNT_INVALID":
        internal["balance_checkpoints"].pop(); raw = _bytes_for(root)
    elif code == "BALANCE_TRANSITION_COUNT_INVALID":
        internal["transition_balances"].pop(); raw = _bytes_for(root)
    elif code == "BALANCE_RECORD_INVALID":
        internal["balance_checkpoints"][0]["residual"] = "not-a-number"; _seal(internal["balance_checkpoints"][0], "balance_checkpoint_digest"); raw = _bytes_for(root)
    elif code == "ABLATION_COUNT_INVALID":
        controls["readout_ablations"].pop(); raw = _bytes_for(root)
    elif code == "ABLATION_PRECONDITION_MISMATCH":
        controls["readout_ablations"][0]["candidate_configuration_id"] = "0" * 64; _seal(controls["readout_ablations"][0], "ablation_digest"); raw = _bytes_for(root)
    elif code == "ABLATION_SCOPE_INVALID":
        controls["readout_ablations"][0]["disabled_scope"] = "ALL_FIELD_FEEDBACK"; _seal(controls["readout_ablations"][0], "ablation_digest"); raw = _bytes_for(root)
    elif code == "NULL_PATH_CARDINALITY_INVALID":
        controls["null_path_pairs"].pop(); raw = _bytes_for(root)
    elif code == "NULL_PATH_REFERENCE_INVALID":
        controls["null_path_pairs"][0]["reference_checkpoint_digest"] = "0" * 64; _seal(controls["null_path_pairs"][0], "pair_digest"); raw = _bytes_for(root)
    elif code == "NULL_PATH_MISMATCH":
        controls["null_path_pairs"][0]["bit_equal"] = False; _seal(controls["null_path_pairs"][0], "pair_digest"); raw = _bytes_for(root)
    elif code == "NULL_PATH_CANDIDATE_STATE_LEAK":
        controls["disabled_candidate_path"]["candidate_state_digests"] = ["0" * 64]; _seal(controls["disabled_candidate_path"], "path_digest"); raw = _bytes_for(root)
    elif code == "RELEASE_LINK_INVALID":
        links["release"]["reset_exclusion"] = False; _seal(links["release"], "release_link_digest"); raw = _bytes_for(root)
    elif code == "REUSE_LINK_WITHOUT_RELEASE":
        links["reuse"]["release_link_digest"] = "0" * 64; _seal(links["reuse"], "reuse_link_digest"); raw = _bytes_for(root)
    elif code == "REUSE_LINK_INVALID":
        links["reuse"]["local_reuse_demand"] = [-1.0] * 4; _seal(links["reuse"], "reuse_link_digest"); raw = _bytes_for(root)
    elif code == "INFORMATION_BARRIER_VIOLATION":
        root["envelope_identity"]["runtime_id"] = "baseline_result"; _seal(root["envelope_identity"], "identity_digest"); raw = _bytes_for(root)
    elif code == "ENVELOPE_COMPLETION_INVALID":
        root["completion"]["completion_status"] = "INCOMPLETE"; _seal(root["completion"], "completion_digest"); raw = _bytes_for(root)
    elif code == "PARTIAL_RESULT_FORBIDDEN":
        root["completion"]["partial_result"] = True; _seal(root["completion"], "completion_digest"); raw = _bytes_for(root)
    else:
        raise AssertionError(code)
    return validate_candidate_observation_envelope(raw, build_candidate_envelope_validation_registry())


class CandidateObservationEnvelopeTests(unittest.TestCase):
    def test_01_contract_schema_status_and_atlas_identities(self):
        self.assertEqual(hashlib.sha256(CONTRACT_ID.encode("ascii")).hexdigest(), CONTRACT_DIGEST)
        self.assertEqual((SCHEMA_ID, VALIDATION_SCHEMA_ID, SOURCE_CONTRACT_ID),
                         ("mcm.s1tk.candidate-observation-envelope.v1",
                          "mcm.s1tm.candidate-observation-envelope-validation.v1", "S1-TK"))
        self.assertTrue(all(len(item) == 64 for item in (ATLAS_FILE_SHA256, ATLAS_ARTIFACT_DIGEST, ATLAS_RESULT_DIGEST)))

    def test_02_registry_factory_is_parameterless_and_reproducible(self):
        left = build_candidate_envelope_validation_registry()
        self.assertEqual(left, build_candidate_envelope_validation_registry())
        self.assertEqual(left.registry_digest, _digest({field.name: getattr(left, field.name)
                                                       for field in fields(left) if field.name != "registry_digest"}))

    def test_03_all_and_public_functions_are_exact(self):
        functions = {name for name in envelope_module.__all__ if callable(getattr(envelope_module, name))
                     and not isinstance(getattr(envelope_module, name), type)}
        self.assertEqual(functions, {"build_candidate_envelope_validation_registry",
                                     "validate_candidate_observation_envelope"})

    def test_04_imports_are_standard_library_only(self):
        path = Path(envelope_module.__file__)
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)
                   for alias in node.names}
        imports |= {(node.module or "").split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertLessEqual(imports, {"__future__", "collections", "dataclasses", "hashlib", "json", "math", "re", "typing"})

    def test_05_public_records_are_frozen_slot_dataclasses(self):
        for name in envelope_module.__all__:
            value = getattr(envelope_module, name)
            if isinstance(value, type) and is_dataclass(value):
                self.assertTrue(value.__dataclass_params__.frozen)
                self.assertTrue(hasattr(value, "__slots__"))

    def test_06_positive_bytes_return_fully_typed_envelope(self):
        result = validate_candidate_observation_envelope(_bytes_for(synthetic_envelope()),
                                                         build_candidate_envelope_validation_registry())
        self.assertEqual((result.status, result.failure_code_or_none), (VALID_STATUS, None))
        self.assertIsInstance(result.envelope_or_none, CandidateObservationEnvelope)

    def test_07_axes_and_profile_cardinalities(self):
        result = validate_candidate_observation_envelope(_bytes_for(synthetic_envelope()),
                                                         build_candidate_envelope_validation_registry())
        value = result.envelope_or_none
        self.assertEqual((len(value.plans), len(value.field_checkpoints), len(value.transitions),
                          len(value.field_profile.signed_components)), (17, 40, 127, 320))

    def test_08_receptor_nullability_is_exact(self):
        value = validate_candidate_observation_envelope(_bytes_for(synthetic_envelope()),
                                                        build_candidate_envelope_validation_registry()).envelope_or_none
        nullable = [item for item in value.field_checkpoints if all(part is None for part in item.receptor_contact)]
        self.assertEqual([(item.plan_role, item.checkpoint_role) for item in nullable], [("C_GAP", "POST_COMPETITION")])

    def test_09_state_and_transition_references_are_complete(self):
        value = validate_candidate_observation_envelope(_bytes_for(synthetic_envelope()),
                                                        build_candidate_envelope_validation_registry()).envelope_or_none
        self.assertEqual((len(value.state_checkpoints), len(value.transitions)), (40, 127))

    def test_10_balance_references_are_complete(self):
        value = validate_candidate_observation_envelope(_bytes_for(synthetic_envelope()),
                                                        build_candidate_envelope_validation_registry()).envelope_or_none
        self.assertEqual((len(value.balance_checkpoints), len(value.transition_balances)), (40, 127))

    def test_11_all_readout_ablations_are_present(self):
        value = validate_candidate_observation_envelope(_bytes_for(synthetic_envelope()),
                                                        build_candidate_envelope_validation_registry()).envelope_or_none
        self.assertEqual(len(value.readout_ablations), 17)

    def test_12_null_paths_and_pair_proofs_are_complete(self):
        value = validate_candidate_observation_envelope(_bytes_for(synthetic_envelope()),
                                                        build_candidate_envelope_validation_registry()).envelope_or_none
        self.assertEqual((len(value.disabled_candidate_path.checkpoint_records),
                          len(value.independent_reference_path.checkpoint_records), len(value.null_path_pairs)), (40, 40, 40))

    def test_13_release_precedes_reuse(self):
        value = validate_candidate_observation_envelope(_bytes_for(synthetic_envelope()),
                                                        build_candidate_envelope_validation_registry()).envelope_or_none
        self.assertEqual(value.reuse_link.release_link_digest, value.release_link.release_link_digest)

    def test_14_record_envelope_and_result_digests_are_reproducible(self):
        raw = _bytes_for(synthetic_envelope())
        result = validate_candidate_observation_envelope(raw, build_candidate_envelope_validation_registry())
        self.assertEqual(result.input_bytes_digest, hashlib.sha256(raw).hexdigest())
        self.assertEqual(result.result_digest, _digest({"status": result.status, "failure_code_or_none": None,
                                                       "input_bytes_digest": result.input_bytes_digest,
                                                       "registry_digest": result.registry_digest}))

    def test_15_bytes_root_and_identity_mutations(self):
        for code in FAILURE_CODES[0:6]:
            with self.subTest(code=code): self.assertEqual(_mutated_result(code).failure_code_or_none, code)

    def test_16_plan_checkpoint_vector_and_receptor_mutations(self):
        for code in FAILURE_CODES[6:10]:
            with self.subTest(code=code): self.assertEqual(_mutated_result(code).failure_code_or_none, code)

    def test_17_profile_state_carry_and_transition_mutations(self):
        for code in FAILURE_CODES[10:14]:
            with self.subTest(code=code): self.assertEqual(_mutated_result(code).failure_code_or_none, code)

    def test_18_causal_source_and_balance_schema_mutations(self):
        for code in FAILURE_CODES[14:16]:
            with self.subTest(code=code): self.assertEqual(_mutated_result(code).failure_code_or_none, code)

    def test_19_balance_count_and_record_mutations(self):
        for code in FAILURE_CODES[16:19]:
            with self.subTest(code=code): self.assertEqual(_mutated_result(code).failure_code_or_none, code)

    def test_20_ablation_count_precondition_and_scope_mutations(self):
        for code in FAILURE_CODES[19:22]:
            with self.subTest(code=code): self.assertEqual(_mutated_result(code).failure_code_or_none, code)

    def test_21_null_path_count_reference_value_and_state_mutations(self):
        for code in FAILURE_CODES[22:26]:
            with self.subTest(code=code): self.assertEqual(_mutated_result(code).failure_code_or_none, code)

    def test_22_release_reuse_and_information_barrier_mutations(self):
        for code in FAILURE_CODES[26:30]:
            with self.subTest(code=code): self.assertEqual(_mutated_result(code).failure_code_or_none, code)

    def test_23_completion_partial_result_and_first_error_priority(self):
        for code in FAILURE_CODES[30:32]:
            with self.subTest(code=code): self.assertEqual(_mutated_result(code).failure_code_or_none, code)
        root = synthetic_envelope(); root["unknown"] = None; root["completion"]["partial_result"] = True
        self.assertEqual(validate_candidate_observation_envelope(_bytes_for(root),
                                                                 build_candidate_envelope_validation_registry()).failure_code_or_none,
                         "ENVELOPE_ROOT_SCHEMA_INVALID")

    def test_24_api_types_and_forbidden_surfaces(self):
        registry = build_candidate_envelope_validation_registry()
        with self.assertRaises(TypeError): validate_candidate_observation_envelope(bytearray(), registry)
        with self.assertRaises(TypeError): validate_candidate_observation_envelope(b"{}", replace(registry, axis_digest="0" * 64))
        public = set(envelope_module.__all__)
        self.assertFalse(any(any(token in name.lower() for token in (
            "file", "producer", "builder", "parse", "repair", "runner", "comparator", "serialize"
        )) for name in public))


if __name__ == "__main__":
    unittest.main()
