"""Canonical S1-PL binding-offer fixtures and mutation roles."""

from __future__ import annotations

import json

from mcm_field_organism.kfs1_schema_validator import canonical_json_bytes, sha256_hex
from tests.g2_d3_s1pg_free_blocked_intervention_fixtures import (
    BLOCKED_HELD_POST as BLOCKED_HELD_PRE,
    FREE_AVAILABLE_POST as FREE_AVAILABLE_PRE,
)


def _bind(value: dict[str, object], key: str) -> bytes:
    item = dict(value)
    item.pop(key, None)
    item[key] = sha256_hex(canonical_json_bytes(item))
    return canonical_json_bytes(item)


EVENT_PAYLOAD = _bind({
    "schema_id": "g2_d3_fresh_binding_event_payload", "schema_version": "s1pi.v1",
    "event_identity_digest": "b1253793c16b639cabae4fd15b5911885c79ccf93ff232945813fe21ec2428e4",
    "event_id": "S1_PE_IDENTICAL_FRESH_BINDING_EVENT_V1", "event_role": "FRESH_LOCAL_BINDING_OFFER",
    "edge_id": "edge:carrier-a:carrier-b",
    "field_reference_digest": "8f189f31bd6fc92753311d3c4e4bcb29921429107728971226c48718ef410835",
    "source_role": "free", "target_role": "bound_unconfigured", "offer_amount": 0.375,
    "common_exposure_digest": "aa325bd855bf30a3691b2ba9b25f84fff0132bdf8a842255985dc009dab248e5",
}, "payload_digest")

EQUATION_CONTRACT = _bind({
    "schema_id": "g2_d3_local_binding_equation_contract", "schema_version": "s1pj.v1",
    "operator_id": "G2_D3_CONSERVATIVE_MAXIMAL_LOCAL_BINDING",
    "amount_rule_id": "MIN_OFFER_AND_PRE_FREE", "source_role": "free",
    "target_role": "bound_unconfigured",
    "unchanged_roles": ["capacity", "bound_configured", "blocked"],
    "event_payload_digest": "04135ee988060079554b117adf87099d3eeab6d9643ef3b415c05de86a9349da",
    "offer_amount": 0.375, "atomic_commit_required": True,
}, "equation_contract_digest")

ADAPTER_CONTRACT = _bind({
    "schema_id": "g2_d3_binding_offer_retention_event_adapter", "schema_version": "s1pj.v1",
    "adapter_id": "S1_PJ_BINDING_OFFER_TO_RETENTION_CONTINUATION_V1",
    "adapter_status": "BOUND_STATIC_NOT_IMPLEMENTED",
    "projection_rule_id": "EVENT_OCCURRENCE_ONLY_NO_ARM_OR_CANDIDATE_STATE",
    "source_event_payload_digest": "04135ee988060079554b117adf87099d3eeab6d9643ef3b415c05de86a9349da",
    "source_event_role": "FRESH_LOCAL_BINDING_OFFER",
    "target_event_schema_id": "g2_d3_model_neutral_continuation_event",
    "target_event_schema_version": "s1oy.v1", "target_event_class_id": "G2_D3_FRESH_CONTINUATION",
    "target_event_input_bytes_digest": "dbffc12bef77155c2271d3990ebe1b8ae4d481ce6155bf8716b1f6e19128b30f",
}, "adapter_digest")

PREDICTION = _bind({
    "schema_id": "g2_d3_binding_offer_static_prediction", "schema_version": "s1pj.v1",
    "equation_contract_digest": "ae19f42cf9b35e4bfc3429976388c75d01b2128b91b686875edfbd76e46f5ecb",
    "adapter_digest": "7a42352262636bf6dc851095814a1bc6be35c692eb21300e72a13678f4ae3c75",
    "free_available_pre_record_digest": "d9d4249f64c737b49c2b8e3816d0f9c876e0fdcea898208bf919185560c6ce4c",
    "blocked_held_pre_record_digest": "4bd692e489c6c9a217e5790abb0970d279fa367c7024b2119db6342e3f5d66e9",
    "free_available_post_record_digest": "e4f0c95e59ea37aa9db8ae25688ec5f28a700dcbaa76ba5bd2056b4eaac42804",
    "blocked_held_post_record_digest": "c3874e3b342a62c5f9366938eded9c60cb3c38356aa8be9155cd6855a126645c",
    "free_available_commit": 0.375, "blocked_held_commit": 0.25,
    "candidate_binding_contrast": 0.125, "baseline_chain_role": "OP_CHAIN_XXX",
    "baseline_first_boundary_input_digest": "c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c",
    "baseline_second_boundary_input_digest": "6d4a6a51e8c3fb81734598f23edff930f88b5f85e00b79c5d84d1da2b5b0ad9a",
    "baseline_cp0_value": 0.5, "baseline_cp1_value": 0.25, "baseline_first_step_response": 0.25,
    "baseline_replica_contrast": 0.0, "excluded_baseline_checkpoint": "cp2",
    "expected_decision": "CANDIDATE_DIFFERENT_BASELINE_EQUAL",
}, "prediction_digest")

FREE_AVAILABLE_EXPECTED_POST = (
    b'{"aggregate_projection_digest":"30fb1640be5e0bcf50f7048ddd345e5b85dd51f3d957e4141c159cc2ab2bac85",'
    b'"anatomy_record_digest":"e4f0c95e59ea37aa9db8ae25688ec5f28a700dcbaa76ba5bd2056b4eaac42804",'
    b'"blocked":0.0,"bound_configured":0.25,"bound_unconfigured":0.625,'
    b'"candidate_class_id":"G2_CONSERVATIVE_BOUND_SUBPARTITION","capacity":1.0,'
    b'"carrier_a_id":"carrier-a","carrier_b_id":"carrier-b","edge_id":"edge:carrier-a:carrier-b",'
    b'"field_reference_digest":"8f189f31bd6fc92753311d3c4e4bcb29921429107728971226c48718ef410835",'
    b'"free":0.125,"geometry_digest":"26469bd04ca523a797d18b2fb31b6b2a1ba99e4d27d4936e56a5c2fe6737e651",'
    b'"resource_account_digest":"0fc6e14290c7f3e4df23edbd02d61952a2f939def54fea4dd56cbf3186675578",'
    b'"schema_id":"g2_d3_anatomy_record","schema_version":"s1np.v1"}'
)
BLOCKED_HELD_EXPECTED_POST = (
    b'{"aggregate_projection_digest":"b4d35fdb8d8ee864092b37c8ca36157dcbc84d0939128b89a3b490e466e269f9",'
    b'"anatomy_record_digest":"c3874e3b342a62c5f9366938eded9c60cb3c38356aa8be9155cd6855a126645c",'
    b'"blocked":0.25,"bound_configured":0.25,"bound_unconfigured":0.5,'
    b'"candidate_class_id":"G2_CONSERVATIVE_BOUND_SUBPARTITION","capacity":1.0,'
    b'"carrier_a_id":"carrier-a","carrier_b_id":"carrier-b","edge_id":"edge:carrier-a:carrier-b",'
    b'"field_reference_digest":"8f189f31bd6fc92753311d3c4e4bcb29921429107728971226c48718ef410835",'
    b'"free":0.0,"geometry_digest":"26469bd04ca523a797d18b2fb31b6b2a1ba99e4d27d4936e56a5c2fe6737e651",'
    b'"resource_account_digest":"88fb527d8ec392fc9cdfaf5d28ebc7b5d0a0a20b8df1cb95a72034ce67ca252d",'
    b'"schema_id":"g2_d3_anatomy_record","schema_version":"s1np.v1"}'
)


def _mutate(raw: bytes, key: str, **changes: object) -> bytes:
    value = json.loads(raw)
    value.update(changes)
    return _bind(value, key)


bad_pre_digest = json.loads(FREE_AVAILABLE_PRE)
bad_pre_digest["anatomy_record_digest"] = "0" * 64
negative_pre = json.loads(FREE_AVAILABLE_PRE)
negative_pre.update(free=-0.125, blocked=0.625)
negative_pre = _bind(negative_pre, "anatomy_record_digest")
bad_payload_digest = json.loads(EVENT_PAYLOAD)
bad_payload_digest["payload_digest"] = "0" * 64
bad_equation_digest = json.loads(EQUATION_CONTRACT)
bad_equation_digest["equation_contract_digest"] = "0" * 64
bad_adapter_digest = json.loads(ADAPTER_CONTRACT)
bad_adapter_digest["adapter_digest"] = "0" * 64

CANDIDATE_MUTATIONS = {
    "pre_digest": (canonical_json_bytes(bad_pre_digest), EVENT_PAYLOAD, EQUATION_CONTRACT),
    "negative_pre": (negative_pre, EVENT_PAYLOAD, EQUATION_CONTRACT),
    "payload_digest": (FREE_AVAILABLE_PRE, canonical_json_bytes(bad_payload_digest), EQUATION_CONTRACT),
    "payload_version": (FREE_AVAILABLE_PRE, _mutate(EVENT_PAYLOAD, "payload_digest", schema_version="s1pi.v2"), EQUATION_CONTRACT),
    "payload_edge": (FREE_AVAILABLE_PRE, _mutate(EVENT_PAYLOAD, "payload_digest", edge_id="edge:other"), EQUATION_CONTRACT),
    "equation_digest": (FREE_AVAILABLE_PRE, EVENT_PAYLOAD, canonical_json_bytes(bad_equation_digest)),
    "equation_offer": (FREE_AVAILABLE_PRE, EVENT_PAYLOAD, _mutate(EQUATION_CONTRACT, "equation_contract_digest", offer_amount=0.25)),
}
CANDIDATE_EXPECTED = {
    "pre_digest": ("PL_PRESTATE_INVALID",), "negative_pre": ("PL_PRESTATE_INVALID",),
    "payload_digest": ("PL_EVENT_PAYLOAD_INVALID",), "payload_version": ("PL_EVENT_PAYLOAD_INVALID",),
    "payload_edge": ("PL_EVENT_STATE_IDENTITY_MISMATCH",),
    "equation_digest": ("PL_EQUATION_CONTRACT_INVALID",),
    "equation_offer": ("PL_EQUATION_CONTRACT_INVALID",),
}

arm_payload = _mutate(EVENT_PAYLOAD, "payload_digest", arm_id="FREE_AVAILABLE")
ADAPTER_MUTATIONS = {
    "adapter_digest": (EVENT_PAYLOAD, canonical_json_bytes(bad_adapter_digest)),
    "adapter_source": (EVENT_PAYLOAD, _mutate(ADAPTER_CONTRACT, "adapter_digest", source_event_payload_digest="0" * 64)),
    "adapter_arm": (arm_payload, ADAPTER_CONTRACT),
}
ADAPTER_EXPECTED = {
    "adapter_digest": ("PL_ADAPTER_CONTRACT_INVALID",),
    "adapter_source": ("PL_ADAPTER_SOURCE_INVALID",),
    "adapter_arm": ("PL_ADAPTER_FORBIDDEN_INPUT",),
}

COMPARATOR_MUTATION_ROLES = (
    "candidate_incomplete", "baseline_invalid", "baseline_provenance",
    "baseline_cp1", "cp2_inclusion", "prediction_decision",
)
ALL_MUTATION_NAMES = tuple(CANDIDATE_MUTATIONS) + (
    "post_validation", "adapter_output",
) + tuple(ADAPTER_MUTATIONS) + COMPARATOR_MUTATION_ROLES


__all__ = (
    "FREE_AVAILABLE_PRE", "BLOCKED_HELD_PRE", "EVENT_PAYLOAD", "EQUATION_CONTRACT",
    "ADAPTER_CONTRACT", "PREDICTION", "FREE_AVAILABLE_EXPECTED_POST",
    "BLOCKED_HELD_EXPECTED_POST", "CANDIDATE_MUTATIONS", "CANDIDATE_EXPECTED",
    "ADAPTER_MUTATIONS", "ADAPTER_EXPECTED", "COMPARATOR_MUTATION_ROLES",
    "ALL_MUTATION_NAMES",
)
