from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ERRATUM_PATH = ROOT / "docs/S1YM_LPRH1_STATISCHES_PRAEIMPLEMENTIERUNGSERRATUM_V1.json"
S1YL_PATH = ROOT / "docs/S1YL_LPRH1_STATISCHER_FINALER_BINDUNGS_UND_IMPLEMENTIERUNGSPREFLIGHT_ABSCHLUSSAUDIT_V1.json"
S1YK_PATH = ROOT / "docs/S1YK_LPRH1_STATISCHER_FINALER_IMPLEMENTIERUNGSBINDUNGSKORREKTURVERTRAG_V1.json"
S1YI_PATH = ROOT / "docs/S1YI_LPRH1_STATISCHER_KORREKTUR_UND_MATERIALISIERUNGSVERTRAG_V1.json"
EXPECTED_ERRATUM_DIGEST = "dcf4a69762a58102937ba7954f7578ee48eb4fcd1f9809a4eb72f961be4dd70c"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class LPRH1S1YMStaticPreimplementationErratumTests(unittest.TestCase):
    def test_erratum_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(load(ERRATUM_PATH), allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(EXPECTED_ERRATUM_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_parent_and_bound_files_are_exact(self) -> None:
        erratum = load(ERRATUM_PATH)
        self.assertEqual("e7dfd4d85d9428deba5d369cca652c5ccb099031f76ed733824710d2d34d98eb", erratum["parent_s1yl_canonical_audit_digest"])
        paths = {
            "s1yl_audit": "docs/S1YL_LPRH1_STATISCHER_FINALER_BINDUNGS_UND_IMPLEMENTIERUNGSPREFLIGHT_ABSCHLUSSAUDIT_V1.json",
            "s1yl_document": "docs/S1YL_LPRH1_STATISCHER_FINALER_BINDUNGS_UND_IMPLEMENTIERUNGSPREFLIGHT_ABSCHLUSSAUDIT.md",
            "s1yl_tests": "tests/test_lprh1_s1yl_static_final_preflight_closure_audit.py",
            "s1yk_contract": "docs/S1YK_LPRH1_STATISCHER_FINALER_IMPLEMENTIERUNGSBINDUNGSKORREKTURVERTRAG_V1.json",
            "s1yi_contract": "docs/S1YI_LPRH1_STATISCHER_KORREKTUR_UND_MATERIALISIERUNGSVERTRAG_V1.json",
            "package_root": "mcm_field_organism/__init__.py",
            "current_api": "mcm_field_organism/current_api.py",
            "root_lazy_exports": "mcm_field_organism/root_lazy_exports.py",
        }
        for role, relative in paths.items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(erratum["bound_file_digests"][role], actual)

    def test_schema_derives_nine_foreign_and_one_own_digest(self) -> None:
        schema = load(S1YI_PATH)["exact_type_schemas"]["LPRH1TransientLocalPrototypeContext"]
        digest_fields = [field for field in schema if field.endswith("_digest_str")]
        foreign_fields = [field for field in digest_fields if field != "context_digest_str"]
        correction = load(ERRATUM_PATH)["corrected_context_digest_binding"]
        self.assertEqual(18, len(schema))
        self.assertEqual(10, len(digest_fields))
        self.assertEqual(9, len(foreign_fields))
        self.assertEqual(foreign_fields, correction["foreign_digest_fields_in_schema_order"])
        self.assertEqual("context_digest_str", correction["own_context_digest_field"])

    def test_exact_overlooked_role_and_replacement_are_bound(self) -> None:
        erratum = load(ERRATUM_PATH)
        invariants = load(S1YK_PATH)["type_invariants"]["LPRH1TransientLocalPrototypeContext"]
        self.assertIn("ALL_EIGHT_DIGEST_ROLES_ARE_SHA256_HEX", invariants)
        self.assertEqual("selected_prototype_digest_str", erratum["discrepancy"]["overlooked_independent_context_role"])
        self.assertEqual("ALL_NINE_FOREIGN_DIGEST_ROLES_ARE_SHA256_HEX", erratum["corrected_context_digest_binding"]["replacement_invariant_literal"])

    def test_other_contract_bindings_remain_unchanged(self) -> None:
        erratum = load(ERRATUM_PATH)
        self.assertEqual(6, len(load(S1YK_PATH)["blocker_closure"]))
        self.assertEqual(28, load(S1YL_PATH)["passed_role_count"])
        self.assertTrue(erratum["scope_effect"]["all_other_s1yg_s1yi_s1yk_and_s1yl_bindings_unchanged"])
        self.assertTrue(erratum["scope_effect"]["implementation_remains_blocked_during_s1ym"])

    def test_public_surfaces_remain_without_lprh1(self) -> None:
        for relative in ("mcm_field_organism/__init__.py", "mcm_field_organism/current_api.py", "mcm_field_organism/root_lazy_exports.py"):
            source = (ROOT / relative).read_text(encoding="utf-8").lower()
            self.assertNotIn("s1ym", source)
            self.assertNotIn("lprh", source)

    def test_decision_is_narrow_and_nonexecuting(self) -> None:
        erratum = load(ERRATUM_PATH)
        self.assertEqual(14, erratum["passed_role_count"])
        self.assertEqual(0, erratum["failed_role_count"])
        self.assertEqual("PASS_LPRH1_PREIMPLEMENTATION_ERRATUM_NINE_FOREIGN_DIGEST_ROLES_BOUND_NO_IMPLEMENTATION", erratum["decision"])
        self.assertTrue(all(value == 0 for value in erratum["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
