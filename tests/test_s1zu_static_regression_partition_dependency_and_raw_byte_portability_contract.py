from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import unittest


_ROOT = Path(__file__).parents[1]
_ARTIFACT = _ROOT / "docs" / (
    "S1ZU_STATISCHER_REGRESSIONSPARTITIONS_ABHAENGIGKEITS_UND_"
    "ROHBYTE_PORTABILITAETSVERTRAG_V1.json"
)
_BOUND = {
    "s1zt_result_artifact": _ROOT / "docs" / "S1ZT_BREITER_TECHNISCHER_REGRESSIONSTEST_ERGEBNIS_UND_URSACHENKLASSIFIKATION_V1.json",
    "s1zt_result_document": _ROOT / "docs" / "S1ZT_BREITER_TECHNISCHER_REGRESSIONSTEST_ERGEBNIS_UND_URSACHENKLASSIFIKATION.md",
    "gitattributes_before_s1zv": _ROOT / ".gitattributes",
}


def _contract() -> dict[str, object]:
    return json.loads(_ARTIFACT.read_text(encoding="utf-8"))


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


class S1ZUStaticPartitionAndPortabilityContractTests(unittest.TestCase):
    def test_contract_digest_and_bound_sources_are_exact(self) -> None:
        contract = _contract()
        self.assertEqual(_canonical_digest(contract), contract["artifact_digest"])
        for role, path in _BOUND.items():
            if role == "gitattributes_before_s1zv":
                self.assertEqual(
                    "f01f5c1ad9d089eb70e59998aa05b253b3654df829a32ac487547c7ed73e190f",
                    contract["bound_source_digests"][role],
                )
                continue
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                contract["bound_source_digests"][role],
            )

    def test_partition_counts_are_disjoint_and_complete(self) -> None:
        inventory = _contract()["partition_inventory_after_s1zu_test_added"]
        self.assertEqual(
            inventory["total_test_module_count"],
            inventory["t0_count"] + inventory["t1_count"] + inventory["t2_count"] + inventory["t3_count"] + inventory["t4_count"],
        )
        self.assertEqual(
            inventory["total_test_module_count"] + 1,
            len(list((_ROOT / "tests").glob("test_*.py"))),
        )
        self.assertEqual(6, len(_contract()["t0_active_fast_modules"]))

    def test_optional_and_historical_roles_are_explicit(self) -> None:
        contract = _contract()
        optional = contract["t1_optional_dependency_modules"]
        self.assertEqual((9, 1), (len(optional["pytest"]), len(optional["pyav"])))
        self.assertEqual(395, contract["t2_closed_history_module_counts"]["total"])
        self.assertEqual(95, contract["t3_private_engineering_module_counts"]["total"])

    def test_portability_scope_is_narrower_than_all_eol_drift(self) -> None:
        inventory = _contract()["portability_inventory"]
        self.assertEqual(2520, inventory["tracked_i_lf_w_crlf_count"])
        self.assertEqual((60, 55), (inventory["tracked_report_json_count"], inventory["report_json_w_crlf_count"]))
        self.assertFalse(inventory["global_eol_normalization_allowed"])

    def test_exact_s1zv_rules_extend_but_do_not_replace_w1f_rules(self) -> None:
        contract = _contract()
        future = contract["exact_post_s1zv_gitattributes_lines"]
        current = (_ROOT / ".gitattributes").read_text(encoding="utf-8").splitlines()
        self.assertEqual(7, len(future))
        self.assertEqual(future, current)
        self.assertEqual(
            [
                "tools/controlled_browser_payload_world/index.html text eol=lf",
                "tools/controlled_browser_payload_world/styles.css text eol=lf",
                "tools/controlled_browser_payload_world/world.js text eol=lf",
            ],
            current[:3],
        )
        self.assertEqual("reports/**/*.json text eol=lf", future[-1])
        self.assertEqual(4, contract["implementation_constraints"]["new_effective_rule_count"])
        self.assertFalse(contract["implementation_constraints"]["broad_suite_execution_allowed"])


if __name__ == "__main__":
    unittest.main()
