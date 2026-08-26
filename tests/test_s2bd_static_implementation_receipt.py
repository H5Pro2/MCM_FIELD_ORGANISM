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
    / (
        "S2BD_PRIVATE_QUELLGEBUNDENE_STATISCHE_PROTOTYPBASELINE_"
        "ATOMARER_COMPARATOR_UND_SYNTHETISCHE_VERTRAGSTESTS_V1.json"
    )
)
BOUND = {
    "s2bc_preflight": (
        ROOT
        / "docs"
        / (
            "S2BC_STATISCHER_QUELLGEBUNDENER_BASELINE_MATERIALISIERBARKEITS_"
            "NICHTZIRKULARITAETS_UND_INFORMATIONSFLUSS_PREFLIGHT_V1.json"
        )
    ),
    "private_static_baseline": (
        PACKAGE / "_ppb1_s2bd_active_static_prototype_baseline.py"
    ),
    "private_paired_comparator": (
        PACKAGE / "_ppb1_s2bd_paired_recognition_comparator.py"
    ),
    "synthetic_contract_tests": (
        ROOT / "tests" / "test_s2bd_private_active_static_prototype_comparator.py"
    ),
    "active_batch_binding": PACKAGE / "_ppb1_active_receptor_batch_binding.py",
    "receptor_profiles": PACKAGE / "_ppb1_receptor_profiles.py",
    "ppb1_reference": PACKAGE / "_ppb1_reference.py",
    "formation_consumer": PACKAGE / "_ppb1_active_batch_formation_consumer.py",
    "formation_probe_handoff": (
        PACKAGE / "_ppb1_active_batch_formation_probe_handoff.py"
    ),
    "current_api": PACKAGE / "current_api.py",
    "package_root": PACKAGE / "__init__.py",
    "shared_field": PACKAGE / "shared_mcm_field.py",
}


def _receipt() -> dict[str, object]:
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


class S2BDStaticImplementationReceiptTests(unittest.TestCase):
    def test_receipt_digest_and_bound_sources_are_exact(self) -> None:
        receipt = _receipt()
        self.assertEqual(_canonical_digest(receipt), receipt["artifact_digest"])
        for role, path in BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                receipt["bound_source_digests"][role],
            )

    def test_call_site_shape_and_noncircularity_are_exact(self) -> None:
        receipt = _receipt()
        tree = ast.parse(
            BOUND["private_paired_comparator"].read_text(encoding="ascii")
        )
        counts = {
            name: sum(
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == name
                for node in ast.walk(tree)
            )
            for name in (
                "probe_ppb1_active_batch_formation_result_read_only",
                "probe_s2bb_static_prototype_read_only",
                "_probe_baseline_modality",
            )
        }
        self.assertEqual(
            {
                "probe_ppb1_active_batch_formation_result_read_only": 1,
                "probe_s2bb_static_prototype_read_only": 1,
                "_probe_baseline_modality": 2,
            },
            counts,
        )
        self.assertEqual("PASS", receipt["noncircularity_result"]["status"])

    def test_tests_result_and_claim_boundary_are_narrow(self) -> None:
        receipt = _receipt()
        execution = receipt["synthetic_test_execution"]
        self.assertEqual(7, execution["final_test_count"])
        self.assertEqual(7, execution["final_passed"])
        self.assertEqual(0, execution["final_failed"])
        self.assertFalse(
            receipt["observed_comparison_result"]["functional_advantage_observed"]
        )
        self.assertFalse(
            receipt["technical_disposition"]["mcm_specific_memory_mechanism"]
        )


if __name__ == "__main__":
    unittest.main()
