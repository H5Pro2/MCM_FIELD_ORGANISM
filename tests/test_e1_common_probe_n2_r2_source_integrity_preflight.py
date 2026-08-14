from __future__ import annotations

import ast
import inspect
from pathlib import Path
import shutil
import tempfile
import textwrap
import unittest

from mcm_field_organism.e1_common_probe_n2_r2_source_integrity_preflight import (
    E1CommonProbeN2R2SourceIntegrityPreflightError,
    S1_EC71_EXPECTED_SOURCE_DIGESTS,
    audit_e1_common_probe_n2_r2_source_integrity,
)


class E1CommonProbeN2R2SourceIntegrityPreflightTests(unittest.TestCase):
    def test_current_registered_sources_are_exact_but_execution_stays_blocked(self) -> None:
        result = audit_e1_common_probe_n2_r2_source_integrity()

        self.assertTrue(result.all_sources_exact)
        self.assertEqual((), result.failed_sources)
        self.assertFalse(result.real_execution_permitted)
        self.assertFalse(result.retry_permitted)
        self.assertEqual(
            "SOURCE_INTEGRITY_EXACT_REAL_EXECUTION_STILL_BLOCKED",
            result.decision,
        )
        self.assertEqual(64, len(result.preflight_digest))

    def test_one_changed_source_is_named_and_fails_closed(self) -> None:
        source_root = Path(__file__).resolve().parents[1] / "mcm_field_organism"
        with tempfile.TemporaryDirectory() as directory:
            target_root = Path(directory)
            for name, _ in S1_EC71_EXPECTED_SOURCE_DIGESTS:
                shutil.copyfile(source_root / name, target_root / name)
            changed = target_root / S1_EC71_EXPECTED_SOURCE_DIGESTS[0][0]
            changed.write_text(
                changed.read_text(encoding="utf-8") + "\n# synthetic mutation\n",
                encoding="utf-8",
            )

            result = audit_e1_common_probe_n2_r2_source_integrity(target_root)

        self.assertFalse(result.all_sources_exact)
        self.assertEqual((S1_EC71_EXPECTED_SOURCE_DIGESTS[0][0],), result.failed_sources)
        self.assertEqual("KORREKTUR_SOURCE_INTEGRITY_MISMATCH", result.decision)
        self.assertFalse(result.real_execution_permitted)
        self.assertFalse(result.retry_permitted)

    def test_missing_source_raises_before_a_preflight_can_be_issued(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(
                E1CommonProbeN2R2SourceIntegrityPreflightError,
                "source is missing",
            ):
                audit_e1_common_probe_n2_r2_source_integrity(Path(directory))

    def test_preflight_has_no_real_path_call_or_write(self) -> None:
        source = inspect.getsource(audit_e1_common_probe_n2_r2_source_integrity)
        tree = ast.parse(textwrap.dedent(source))
        called = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        for forbidden in (
            "run_e1_common_probe_n2_r2_real_mode_coordinator",
            "run_e1_common_probe_real_formation_receipt_adapter",
            "build_e1_common_probe_real_fresh_field_adapter",
            "run_e1_common_probe_real_probe_receipt_adapter",
        ):
            self.assertNotIn(forbidden, called)
        for forbidden in ("write_text", "write_bytes", "open("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
