from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "mcm_field_organism"
ARTIFACT = (
    ROOT
    / "docs"
    / "S2BN_AVPC1_AUDIO_ONLY_IMPLEMENTIERUNGS_UND_GRENZEN_ABSCHLUSSAUDIT_V1.json"
)
BOUND = {
    "s2bm_receipt": (
        ROOT
        / "docs"
        / (
            "S2BM_AVPC1_PRIVATE_AUDIO_ONLY_QUELLE_PARTITION_PROBENHUELLE_"
            "UND_SYNTHETISCHE_VERTRAGSTESTS_V1.json"
        )
    ),
    "s2bm_document": (
        ROOT
        / "docs"
        / (
            "S2BM_AVPC1_PRIVATE_AUDIO_ONLY_QUELLE_PARTITION_PROBENHUELLE_"
            "UND_SYNTHETISCHE_VERTRAGSTESTS.md"
        )
    ),
    "s2bk_contract": (
        ROOT / "docs" / "S2BK_AVPC1_PRIVATER_AUDIO_ONLY_PROBENHUELLENVERTRAG_V1.json"
    ),
    "s2bl_preflight": (
        ROOT
        / "docs"
        / "S2BL_AVPC1_AUDIO_ONLY_PROBENHUELLE_STATISCHER_IMPLEMENTIERUNGSPREFLIGHT_V1.json"
    ),
    "private_implementation": PACKAGE / "_avpc1_audio_only_probe_envelope.py",
    "synthetic_contract_tests": (
        ROOT / "tests" / "test_s2bm_private_avpc1_audio_only_probe_envelope.py"
    ),
    "active_batch_binding": PACKAGE / "_ppb1_active_receptor_batch_binding.py",
    "ppb1_reference": PACKAGE / "_ppb1_reference.py",
    "state_lifecycle": PACKAGE / "_ppb1_s1wq_perceptual_state_lifecycle.py",
    "browser_receptor_bridge": PACKAGE / "browser_receptor_bridge.py",
    "browser_world_contract": PACKAGE / "browser_world_contract.py",
    "current_api": PACKAGE / "current_api.py",
    "package_root": PACKAGE / "__init__.py",
    "shared_field": PACKAGE / "shared_mcm_field.py",
    "root_lazy_exports": PACKAGE / "root_lazy_exports.py",
}


def _audit() -> dict[str, object]:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _canonical_digest(payload: dict[str, object]) -> str:
    value = dict(payload)
    value.pop("artifact_digest")
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


class S2BNStaticAVPC1AudioOnlyClosureAuditTests(unittest.TestCase):
    def test_audit_digest_and_bound_sources_are_exact(self) -> None:
        audit = _audit()
        self.assertEqual(_canonical_digest(audit), audit["artifact_digest"])
        for role, path in BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                audit["bound_source_digests"][role],
            )

    def test_private_source_inventory_and_forbidden_calls_are_exact(self) -> None:
        source = BOUND["private_implementation"].read_text(encoding="ascii")
        tree = ast.parse(source)
        classes = [node.name for node in tree.body if isinstance(node, ast.ClassDef)]
        functions = [
            node.name for node in tree.body if isinstance(node, ast.FunctionDef)
        ]
        self.assertEqual(4, len(classes))
        self.assertEqual(3, len([name for name in functions if name.startswith("bind_")]))
        calls = {
            node.func.id
            if isinstance(node.func, ast.Name)
            else node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, (ast.Name, ast.Attribute))
        }
        self.assertTrue(
            {
                "advance_ppb1_bank",
                "probe_s1wu_perceptual_state",
                "advance_audio_video_receptor_sequences",
                "open",
            }.isdisjoint(calls)
        )

    def test_visual_source_independence_and_time_rules_are_closed(self) -> None:
        audit = _audit()
        source = audit["source_binding_acceptance"]
        time = audit["time_acceptance"]
        self.assertFalse(source["visual_sequence_index_read_by_source_binding_logic"])
        self.assertFalse(source["parent_batch_digest_stored_in_source_binding"])
        self.assertFalse(
            source["visual_frame_value_identity_or_projection_stored_in_source_binding"]
        )
        self.assertTrue(
            time[
                "probe_source_window_end_must_be_greater_than_bank_last_source_end"
            ]
        )
        self.assertTrue(
            time[
                "probe_field_window_start_must_be_greater_than_or_equal_to_relation_max_end"
            ]
        )

    def test_partition_envelope_atomicity_and_privacy_are_complete(self) -> None:
        audit = _audit()
        self.assertEqual(
            0,
            audit["partition_acceptance"][
                "association_key_target_support_conflict_capacity_or_output_field_count"
            ],
        )
        closure = audit["envelope_digest_dependency_closure"]
        self.assertEqual(
            closure["required_role_count"],
            closure["materialized_role_count"],
        )
        self.assertEqual([], closure["missing_roles"])
        self.assertFalse(
            audit["atomicity_and_purity_acceptance"][
                "partial_output_retry_repair_or_default_path"
            ]
        )
        self.assertEqual(0, audit["privacy_acceptance"]["public_export_count"])

    def test_prior_evidence_is_reused_without_any_s2bn_execution(self) -> None:
        audit = _audit()
        evidence = audit["synthetic_evidence_reused_without_reexecution"]
        self.assertEqual(8, evidence["receipt_final_test_count"])
        self.assertEqual(8, evidence["receipt_final_passed"])
        self.assertEqual(0, evidence["s2bn_test_reexecution_count"])
        self.assertEqual(0, audit["remaining_blocker_count"])
        self.assertTrue(all(value == 0 for value in audit["execution"].values()))


if __name__ == "__main__":
    unittest.main()
