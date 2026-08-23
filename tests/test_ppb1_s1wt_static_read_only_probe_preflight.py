from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT_PATH = (
    ROOT
    / "docs"
    / "S1WT_PPB1_STATISCHER_READ_ONLY_PROBE_IMPLEMENTIERUNGSPREFLIGHT_V1.json"
)
EXPECTED_PREFLIGHT_DIGEST = (
    "1e27f509ab37b785334da34ff833d4dc4184d908bbde7eea694cf29549aa43ae"
)


def load_preflight():
    return json.loads(PREFLIGHT_PATH.read_text(encoding="utf-8"))


class PPB1S1WTStaticReadOnlyProbePreflightTests(unittest.TestCase):
    def test_preflight_is_canonical_and_digest_bound(self) -> None:
        payload = load_preflight()
        observed = payload.pop("preflight_digest")
        encoded = json.dumps(
            payload,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self.assertEqual(EXPECTED_PREFLIGHT_DIGEST, observed)
        self.assertEqual(observed, hashlib.sha256(encoded).hexdigest())

    def test_scope_and_source_digests_are_exact(self) -> None:
        preflight = load_preflight()
        self.assertEqual(
            "SOURCE_AST_AND_CONTRACT_ONLY_NO_PROBE_IMPLEMENTATION_OR_EXECUTION",
            preflight["scope"],
        )
        self.assertEqual(
            {
                "contract": "51885d24c4597ab4f78c2e133d945e000931a2cbff5e2aeb2578c61a62364e0b",
                "lifecycle": "7b21391ee86ce597c9434d46fe3d76cf3d8dbe8a65f2da49555ad2b26a203954",
                "receptor": "af565ce442aa56ade4b3b5d028692cccc93b481c299f1ff2d87ba840fdb6ee71",
                "reference": "9fad3b04661fb9b8da053afd5599e3bdfe73019681ae50115263c39f3052ca9d",
            },
            preflight["source_digests"],
        )

    def test_all_fourteen_static_checks_pass(self) -> None:
        preflight = load_preflight()
        self.assertEqual(14, preflight["positive_check_count"])
        self.assertEqual(0, preflight["negative_check_count"])
        self.assertEqual(14, len(preflight["checks"]))
        self.assertTrue(all(preflight["checks"].values()))

    def test_validation_distance_digest_and_identity_roles_are_reusable(self) -> None:
        self.assertEqual(
            {
                "config_digest": "PPB1BankConfig.digest",
                "distance": "normalized_mean_l1_distance",
                "frame_validation": "_validate_frame",
                "input_digest_projection": "_input_projection_PLUS__digest",
                "state_digest": "PPB1BankState.digest",
                "state_identity_projection": "_state_identity_payload_PLUS__digest",
                "state_validation": "_validate_state",
            },
            load_preflight()["reusable_roles"],
        )

    def test_only_contract_bound_composition_roles_remain(self) -> None:
        self.assertEqual(
            {
                "causal_later_guard": (
                    "SAME_CLOCK_AND_PROBE_END_GREATER_THAN_LAST_COMMITTED_END"
                ),
                "eligible_slot_filter": (
                    "OCCUPIED_AND_SUPPORT_COUNT_AT_LEAST_STABLE_AFTER"
                ),
                "selection": "MIN_DISTANCE_THEN_LEXICOGRAPHIC_SLOT_ID",
            },
            load_preflight()["composition_only_roles"],
        )

    def test_no_execution_advance_rule_parameter_or_field_effect_occurred(self) -> None:
        preflight = load_preflight()
        for role in (
            "probe_function_execution_count",
            "state_function_execution_count",
            "advance_call_count",
            "new_match_rule_count",
            "new_parameter_count",
            "field_effect_count",
        ):
            self.assertEqual(0, preflight[role], role)

    def test_implementation_boundary_remains_private_and_read_only(self) -> None:
        self.assertEqual(
            [
                "PRIVATE_PURE_IN_MEMORY_ONLY",
                "NO_ADVANCE_CALL",
                "NO_POSTSTATE_ROLE",
                "NO_MUTATION",
                "NO_PUBLIC_EXPORT_SNAPSHOT_FIELD_OR_PRODUCTION_ENTRY",
                "NO_FILE_FIELD_SEMANTIC_OR_MEDIA_RUNTIME",
            ],
            load_preflight()["implementation_boundary"],
        )

    def test_decision_admits_only_later_private_implementation(self) -> None:
        self.assertEqual(
            "PASS_REUSE_COMPLETE_PRIVATE_PROBE_IMPLEMENTATION_ADMISSIBLE",
            load_preflight()["decision"],
        )


if __name__ == "__main__":
    unittest.main()
