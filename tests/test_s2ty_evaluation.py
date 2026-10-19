import unittest
import json

from tools import _s2ty_evaluation as evaluation


def envelope():
    receipts = []
    for ordinal in range(1, 27):
        action = "TRACE_FORMING"
        if ordinal == 5:
            action = {"action": "TRACE_RETAINED", "generation": 1, "evicted": None}
        elif ordinal == 10:
            action = {"action": "TRACE_CONFIRMED", "generation": 1, "evicted": None}
        elif ordinal == 17:
            action = {"action": "TRACE_RETAINED", "generation": 2, "evicted": None}
        elif ordinal == 24:
            action = {"action": "TRACE_RETAINED", "generation": 3, "evicted": 1}
        elif ordinal == 12:
            action = {"decision": "TRACE_MATCH", "matches": [[1, 1]]}
        elif ordinal == 19:
            action = {"decision": "TRACE_MATCH", "matches": [[2, 0]]}
        elif ordinal == 26:
            action = {"decision": "ABSTAIN_NO_RETAINED_TRACE", "matches": []}
        receipts.append({"ordinal": ordinal, "adapter": action, "direct": action})
    return {"status": "COMPLETE", "verification": {"status": "VERIFIED"}, "record": {"result": {"events": receipts}}}


class Tests(unittest.TestCase):
    def test_expected_transitions_and_hints_are_reported_after_verification(self):
        result = evaluation.evaluate_verified(envelope())
        self.assertTrue(result["all_expected"])
        self.assertEqual(result["hints"]["h3"]["observed"]["decision"], "ABSTAIN_NO_RETAINED_TRACE")

    def test_unverified_envelope_is_rejected_before_reading_receipts(self):
        document = envelope()
        document["verification"] = None
        with self.assertRaises(evaluation.S2TYEvaluationError) as raised:
            evaluation.evaluate_verified(document)
        self.assertEqual(raised.exception.code, "EVALUATION_NOT_VERIFIED")

    def test_functional_mismatch_is_reported_not_promoted_to_technical_failure(self):
        document = envelope()
        document["record"]["result"]["events"][11]["adapter"] = {"decision": "ABSTAIN_NO_RETAINED_TRACE", "matches": []}
        document["record"]["result"]["events"][11]["direct"] = {"decision": "ABSTAIN_NO_RETAINED_TRACE", "matches": []}
        result = evaluation.evaluate_verified(document)
        self.assertFalse(result["hints"]["h1"]["matches_expected"])

    def test_native_tuple_matches_compare_equal_to_json_lists(self):
        document = envelope()
        document["record"]["result"]["events"][11]["adapter"] = {"decision": "TRACE_MATCH", "matches": ((1, 1),)}
        document["record"]["result"]["events"][11]["direct"] = {"decision": "TRACE_MATCH", "matches": ((1, 1),)}
        self.assertTrue(evaluation.evaluate_verified(document)["hints"]["h1"]["matches_expected"])
        roundtrip = json.loads(json.dumps(document))
        self.assertTrue(evaluation.evaluate_verified(roundtrip)["hints"]["h1"]["matches_expected"])

    def test_generation_offset_order_and_multiplicity_remain_significant(self):
        for matches in (((2, 1),), ((1, 2),), ((1, 1), (1, 1))):
            with self.subTest(matches=matches):
                document = envelope()
                document["record"]["result"]["events"][11]["adapter"] = {"decision": "TRACE_MATCH", "matches": matches}
                document["record"]["result"]["events"][11]["direct"] = {"decision": "TRACE_MATCH", "matches": matches}
                self.assertFalse(evaluation.evaluate_verified(document)["hints"]["h1"]["matches_expected"])

    def test_invalid_match_structure_is_rejected(self):
        document = envelope()
        document["record"]["result"]["events"][11]["adapter"] = {"decision": "TRACE_MATCH", "matches": [[1]]}
        document["record"]["result"]["events"][11]["direct"] = {"decision": "TRACE_MATCH", "matches": [[1]]}
        with self.assertRaises(evaluation.S2TYEvaluationError) as raised:
            evaluation.evaluate_verified(document)
        self.assertEqual(raised.exception.code, "EVALUATION_MATCHES_INVALID")
