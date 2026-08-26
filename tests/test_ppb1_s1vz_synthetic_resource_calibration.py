from __future__ import annotations

from dataclasses import fields, replace
import hashlib
import inspect
import json
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
import mcm_field_organism._ppb1_s1vz_synthetic_resource_calibration as s1vz
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot


ROOT = Path(__file__).resolve().parents[1]


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("ascii")).hexdigest()


def receipt(replicate: int, peak_mib: int, artifact_mib: int):
    initial = 100 * s1vz.S1VZ_MIB
    peaks = tuple(
        initial + value * s1vz.S1VZ_MIB
        for value in (
            peak_mib // 5,
            peak_mib // 4,
            peak_mib // 3,
            peak_mib // 2,
            peak_mib,
        )
    )
    return s1vz.S1VZReplicateReceipt(
        f"R{replicate}",
        (
            ("python_implementation", "CPython"),
            ("python_version", "3.test"),
            ("operating_system", "TestOS"),
            ("machine_architecture", "test64"),
            ("pointer_width_bits", "64"),
        ),
        tuple(
            (role, digest(role))
            for role in (
                "s1vq_runner",
                "s1vt_pipeline",
                "s1vw_synthetic_orchestrator",
                "s1vz_resource_calibrator",
            )
        ),
        initial,
        *peaks,
        peaks[-1] - initial,
        1024 + replicate,
        artifact_mib * s1vz.S1VZ_MIB,
        artifact_mib * s1vz.S1VZ_MIB,
        10 * s1vz.S1VZ_GIB,
        9 * s1vz.S1VZ_GIB,
        True,
        digest(f"terminal:{replicate}"),
    )


class PPB1S1VZSyntheticResourceCalibrationTests(unittest.TestCase):
    def test_memory_gate_uses_floor_margin_and_double_peak(self) -> None:
        self.assertEqual(2 * s1vz.S1VZ_GIB, s1vz.memory_gate_bytes(0))
        self.assertEqual(
            2 * s1vz.S1VZ_GIB,
            s1vz.memory_gate_bytes(700 * s1vz.S1VZ_MIB),
        )
        self.assertEqual(
            2560 * s1vz.S1VZ_MIB,
            s1vz.memory_gate_bytes(1280 * s1vz.S1VZ_MIB),
        )

    def test_disk_gate_uses_floor_margin_and_triple_artifact(self) -> None:
        self.assertEqual(s1vz.S1VZ_GIB, s1vz.disk_gate_bytes(0, 0))
        self.assertEqual(
            1500 * s1vz.S1VZ_MIB,
            s1vz.disk_gate_bytes(500 * s1vz.S1VZ_MIB, 400),
        )

    def test_aggregate_accepts_exact_three_comparable_receipts(self) -> None:
        receipts = (receipt(1, 600, 300), receipt(2, 800, 400), receipt(3, 700, 350))
        result = s1vz.aggregate_s1vz_receipts(receipts)
        self.assertEqual(800 * s1vz.S1VZ_MIB, result.observed_peak_increment_bytes)
        self.assertEqual(400 * s1vz.S1VZ_MIB, result.observed_success_artifact_bytes)
        self.assertEqual(2 * s1vz.S1VZ_GIB, result.minimum_free_memory_bytes)
        self.assertEqual(1200 * s1vz.S1VZ_MIB, result.minimum_free_disk_bytes)
        self.assertTrue(result.all_atomic_replace_checks_passed)
        self.assertFalse(result.production_execution_authorized)

    def test_aggregate_rejects_missing_or_reordered_replicates(self) -> None:
        values = (receipt(1, 600, 300), receipt(2, 800, 400), receipt(3, 700, 350))
        for invalid in (values[:2], (values[1], values[0], values[2])):
            with self.subTest(count=len(invalid)):
                with self.assertRaises(s1vz.S1VZCalibrationError):
                    s1vz.aggregate_s1vz_receipts(invalid)

    def test_aggregate_rejects_platform_or_source_drift(self) -> None:
        values = [receipt(1, 600, 300), receipt(2, 800, 400), receipt(3, 700, 350)]
        drifted_platform = replace(
            values[2],
            platform_binding=values[2].platform_binding[:-1]
            + (("pointer_width_bits", "32"),),
        )
        with self.assertRaises(s1vz.S1VZCalibrationError):
            s1vz.aggregate_s1vz_receipts(tuple(values[:2] + [drifted_platform]))

        drifted_sources = replace(
            values[2],
            source_digests=values[2].source_digests[:-1]
            + (("s1vz_resource_calibrator", digest("drift")),),
        )
        with self.assertRaises(s1vz.S1VZCalibrationError):
            s1vz.aggregate_s1vz_receipts(tuple(values[:2] + [drifted_sources]))

    def test_contract_digest_matches_canonical_json(self) -> None:
        path = (
            ROOT
            / "docs"
            / "S1VY_PPB1_PRODUKTIONS_RESSOURCENMESS_UND_GATEVERTRAG_V1.json"
        )
        payload = json.loads(path.read_text(encoding="utf-8"))
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(s1vz.S1VZ_CONTRACT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_committed_calibration_result_reconstructs_bit_equal(self) -> None:
        path = (
            ROOT
            / "docs"
            / "S1VZ_PPB1_SYNTHETISCHE_RESSOURCENKALIBRIERUNG_RESULT_V1.json"
        )
        payload = json.loads(path.read_text(encoding="utf-8"))
        expected_digest = payload.pop("calibration_digest")
        receipts = tuple(
            s1vz._receipt_from_payload(item)
            for item in payload["replicate_receipts"]
        )
        result = s1vz.aggregate_s1vz_receipts(receipts)
        self.assertEqual(payload, result.canonical_payload())
        self.assertEqual(expected_digest, result.digest())
        bound_source_digest = dict(result.source_digests)[
            "s1vz_resource_calibrator"
        ]
        self.assertEqual(
            bound_source_digest,
            hashlib.sha256(Path(s1vz.__file__).read_bytes()).hexdigest(),
        )

    def test_production_entrypoint_remains_hard_blocked(self) -> None:
        with self.assertRaises(s1vz.S1VZCalibrationError) as raised:
            s1vz.execute_s1vz_production_once()
        self.assertEqual(s1vz.S1VZ_PRODUCTION_EXECUTION_BLOCKED, raised.exception.code)

    def test_calibrator_source_has_fixed_three_workers_and_no_real_call(self) -> None:
        source = inspect.getsource(s1vz)
        self.assertIn('for replicate_id in ("R1", "R2", "R3")', source)
        self.assertNotIn("_execute_s1vq_corrected_matrix(", source)
        self.assertNotIn("execute_s1vq_corrected_matrix(", source)
        self.assertNotIn("execute_s1vw_production_once(", source)
        self.assertNotIn("data/generated/ppb1/one_shot", source)

    def test_s1vz_remains_private_and_snapshot_neutral(self) -> None:
        names = {
            "S1VZReplicateReceipt",
            "S1VZCalibrationResult",
            "run_s1vz_three_process_calibration",
        }
        self.assertTrue(names.isdisjoint(mcm_field_organism.__all__))
        self.assertTrue(names.isdisjoint(ROOT_LAZY_EXPORTS))
        self.assertTrue(names.isdisjoint(current_api.__all__))
        self.assertTrue(
            names.isdisjoint({item.name for item in fields(SharedMCMFieldSnapshot)})
        )


if __name__ == "__main__":
    unittest.main()
