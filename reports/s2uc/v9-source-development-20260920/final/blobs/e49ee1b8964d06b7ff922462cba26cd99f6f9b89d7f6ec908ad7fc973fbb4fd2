import copy
import tempfile
import unittest
from pathlib import Path

from tools import _s2uc_resource_contract_v7 as ledger


class V7ResourceLedgerTests(unittest.TestCase):
    def amounts(self, **overrides):
        return {**dict.fromkeys(ledger.CATEGORIES, 0), **overrides}

    def fixture(self, root, sizes=None, phase="failure_after_publication"):
        sizes = sizes or {}
        categories = set(ledger.CATEGORIES)
        if phase == "success":
            categories -= {"error", "minimal"}
        elif phase == "failure_before_publication":
            categories -= {"record", "verification"}
        assignments = []
        for category in sorted(categories):
            name = category + ".bin"
            # Genuine file lengths, including boundary/overrun cases.
            with (root / name).open("wb") as stream:
                stream.truncate(sizes.get(category, 0))
            assignments.append({"path": name, "category": category})
        return assignments

    def test_contract_values_immutable_and_report_copies_independent(self):
        self.assertEqual(ledger.CONTRACT_ID, "s2uc.resources.separate-code-artifacts.v7")
        self.assertEqual(dict(ledger.LIMITS), {
            "code": 655360, "metadata": 65536, "static_shared": 196608,
            "shared": 262144, "record": 262144, "verification": 262144,
            "error": 16384, "terminal": 16384, "minimal": 16384,
            "staging": 245760, "total": 4194304})
        self.assertEqual(dict(ledger.RESERVES), {"record": 245760, "verification": 131072})
        with self.assertRaises(TypeError):
            ledger.LIMITS["total"] = 1
        with self.assertRaises(TypeError):
            ledger.RESERVES["record"] = 1
        plan = ledger.reserve("success", self.amounts())
        plan["limits"]["code"] = 1
        self.assertEqual(ledger.LIMITS["code"], 655360)

    def test_every_absolute_category_boundary_uses_actual_files(self):
        for category in ledger.CATEGORIES:
            for delta in (0, 1):
                with self.subTest(category=category, delta=delta), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    assignments = self.fixture(root, {category: ledger.LIMITS[category] + delta})
                    result = ledger.measure(root, assignments, phase="failure_after_publication")
                    self.assertEqual(result["actual"]["categories"][category], (root / (category + ".bin")).stat().st_size)
                    self.assertEqual(f"limit:{category}" in result["actual"]["violations"], delta == 1)
                    # Absolute R/V equality can already violate the stricter reserve.
                    if delta:
                        with self.assertRaisesRegex(ledger.V7LedgerError, "^V7_BUDGET_EXCEEDED$"):
                            ledger.verify(root, assignments, result, phase="failure_after_publication")

    def test_both_reserve_boundaries_are_distinct_from_absolute_limits(self):
        for category in ("record", "verification"):
            for delta in (0, 1):
                with self.subTest(category=category, delta=delta), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    assignments = self.fixture(root, {category: ledger.RESERVES[category] + delta})
                    result = ledger.measure(root, assignments, phase="failure_after_publication")
                    violations = result["actual"]["violations"]
                    self.assertEqual(f"reserve:{category}" in violations, delta == 1)
                    self.assertNotIn(f"limit:{category}", violations)
                    if not delta:
                        ledger.verify(root, assignments, result, phase="failure_after_publication")

    def test_shared_boundary_counts_subaccounts_without_double_counting(self):
        for delta in (0, 1):
            with self.subTest(delta=delta), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                sizes = {"static_shared": 196608 + delta, "error": 16384,
                         "terminal": 16384, "minimal": 32768}
                assignments = self.fixture(root, sizes)
                actual = ledger.measure(root, assignments, phase="failure_after_publication")["actual"]
                self.assertEqual(actual["main_accounts"]["shared"], 262144 + delta)
                self.assertEqual(actual["total_bytes"], 262144 + delta)
                self.assertEqual("limit:shared" in actual["violations"], delta == 1)
                self.assertIn("limit:minimal", actual["violations"])

    def test_total_boundary_on_disk_and_isolated_arithmetic(self):
        for delta in (0, 1):
            with self.subTest(delta=delta), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                assignments = self.fixture(root, {"code": 4194304 + delta})
                actual = ledger.measure(root, assignments, phase="failure_after_publication")["actual"]
                self.assertEqual("limit:total" in actual["violations"], delta == 1)
                self.assertIn("limit:code", actual["violations"])
        # Production has no adjustable limit. Exercise the same pure comparator
        # with a small ceiling so no other local cap participates in this test.
        self.assertFalse(ledger._total_exceeded(100, 100))
        self.assertTrue(ledger._total_exceeded(101, 100))
        self.assertEqual(ledger.LIMITS["total"], 4194304)

    def test_all_closure_alternatives_match_independent_sums(self):
        base = {"code": 655360, "metadata": 65536, "static_shared": 196608, "staging": 245760}
        cases = [
            ("success", {"record": 245760, "verification": 131072, "terminal": 16384}, 1556480),
            ("failure_before_publication", {"error": 16384, "terminal": 16384}, 1196032),
            ("failure_after_publication", {"record": 245760, "verification": 131072, "error": 16384, "terminal": 16384}, 1572864),
            ("failure_after_publication", {"record": 245760, "verification": 131072, "error": 16384, "terminal": 16384, "minimal": 16384}, 1589248),
        ]
        for phase, extras, total in cases:
            with self.subTest(phase=phase, minimal=extras.get("minimal", 0)), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                sizes = {**base, **extras}
                assignments = self.fixture(root, sizes, phase)
                # Remove empty, optional evidence files from the actual inventory.
                for row in assignments[:]:
                    if row["category"] in {"minimal", "verification"} and row["category"] not in extras:
                        (root / row["path"]).unlink()
                        assignments.remove(row)
                report = ledger.measure(root, assignments, phase=phase)
                self.assertEqual(report["actual"]["total_bytes"], total)
                self.assertEqual(sum(p.stat().st_size for p in root.iterdir()), total)
                self.assertEqual(report["actual"]["main_accounts"]["shared"], sum(sizes.get(k, 0) for k in ("static_shared", "error", "terminal", "minimal")))
                self.assertTrue(report["actual"]["within_limits"])
                self.assertEqual(ledger.verify(root, assignments, report, phase=phase), report)
                reserved = ledger.reserve(phase, self.amounts(**sizes))
                self.assertEqual(reserved["reserved"], report["actual"])

    def test_consistent_false_file_size_and_totals_rejected_against_disk(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            assignments = self.fixture(root, {"code": 10})
            report = ledger.measure(root, assignments, phase="failure_after_publication")
            claimed = copy.deepcopy(report)
            next(row for row in claimed["files"] if row["category"] == "code")["bytes"] = 9
            claimed["actual"]["categories"]["code"] = 9
            claimed["actual"]["main_accounts"]["code"] = 9
            claimed["actual"]["total_bytes"] = 9
            with self.assertRaisesRegex(ledger.V7LedgerError, "^V7_LEDGER_MISMATCH$"):
                ledger.verify(root, assignments, claimed, phase="failure_after_publication")

    def test_same_length_changed_file_hash_and_relabelled_category_rejected(self):
        for mutation in ("content", "category", "missing_row", "duplicate_row", "bool_size", "negative_size", "wrong_contract"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                assignments = self.fixture(root, {"code": 1})
                report = ledger.measure(root, assignments, phase="failure_after_publication")
                row = next(x for x in report["files"] if x["category"] == "code")
                if mutation == "content":
                    (root / row["path"]).write_bytes(b"x")
                elif mutation == "category":
                    row["category"] = "static_shared"
                elif mutation == "missing_row":
                    report["files"].pop()
                elif mutation == "duplicate_row":
                    report["files"].append(copy.deepcopy(row))
                elif mutation == "bool_size":
                    row["bytes"] = True
                elif mutation == "negative_size":
                    row["bytes"] = -1
                else:
                    report["contract_id"] = "s2uc.v6"
                with self.assertRaisesRegex(ledger.V7LedgerError, "^V7_LEDGER_MISMATCH$"):
                    ledger.verify(root, assignments, report, phase="failure_after_publication")

    def test_missing_and_unassigned_real_files_rejected(self):
        for mutation, error in (("missing", "V7_FILE_MISSING"), ("extra", "V7_FILE_UNASSIGNED"), ("omit", "V7_FILE_UNASSIGNED")):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                assignments = self.fixture(root)
                if mutation == "missing":
                    (root / assignments[0]["path"]).unlink()
                elif mutation == "extra":
                    (root / "unaccounted.tmp").write_bytes(b"x")
                else:
                    assignments.pop()
                with self.assertRaisesRegex(ledger.V7LedgerError, f"^{error}$"):
                    ledger.measure(root, assignments, phase="failure_after_publication")

    def test_duplicate_unknown_and_invalid_assignments_rejected(self):
        for mutation, error in (("duplicate", "V7_DUPLICATE_FILE"), ("unknown", "V7_CATEGORY_UNKNOWN"), ("escape", "V7_PATH_INVALID"), ("size", "V7_ASSIGNMENTS_INVALID")):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                assignments = self.fixture(root)
                if mutation == "duplicate":
                    assignments.append(copy.deepcopy(assignments[0]))
                elif mutation == "unknown":
                    assignments[0]["category"] = "other"
                elif mutation == "escape":
                    assignments[0]["path"] = "../outside"
                else:
                    assignments[0]["bytes"] = 0
                with self.assertRaisesRegex(ledger.V7LedgerError, f"^{error}$"):
                    ledger.measure(root, assignments, phase="failure_after_publication")

    def test_required_artifacts_and_single_staging_file_enforced(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            assignments = self.fixture(root)
            record = next(x for x in assignments if x["category"] == "record")
            assignments.remove(record)
            (root / record["path"]).unlink()
            with self.assertRaisesRegex(ledger.V7LedgerError, "^V7_PHASE_FILES_MISSING$"):
                ledger.measure(root, assignments, phase="failure_after_publication")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            assignments = self.fixture(root)
            (root / "second.tmp").write_bytes(b"x")
            assignments.append({"path": "second.tmp", "category": "staging"})
            with self.assertRaisesRegex(ledger.V7LedgerError, "^V7_MULTIPLE_SINGLE_ARTIFACTS$"):
                ledger.measure(root, assignments, phase="failure_after_publication")

    def test_invalid_reservation_sizes_and_categories_rejected(self):
        for size in (-1, True, 1.0, "1", None):
            with self.subTest(size=size), self.assertRaisesRegex(ledger.V7LedgerError, "^V7_SIZE_INVALID$"):
                ledger.reserve("success", self.amounts(code=size))
        for mutation in ("missing", "extra"):
            amounts = self.amounts()
            if mutation == "missing":
                del amounts["code"]
            else:
                amounts["other"] = 0
            with self.assertRaisesRegex(ledger.V7LedgerError, "^V7_CATEGORIES_INVALID$"):
                ledger.reserve("success", amounts)
        with self.assertRaisesRegex(ledger.V7LedgerError, "^V7_PHASE_INVALID$"):
            ledger.reserve("unknown", self.amounts())

    def test_reservation_cannot_substitute_for_measurement(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            assignments = self.fixture(root, {"record": 10})
            reserved = ledger.reserve("failure_after_publication", self.amounts(record=10))
            with self.assertRaisesRegex(ledger.V7LedgerError, "^V7_LEDGER_MISMATCH$"):
                ledger.verify(root, assignments, reserved, phase="failure_after_publication")

    def test_phase_forbids_published_files_before_publication_even_if_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            assignments = self.fixture(root)
            with self.assertRaisesRegex(ledger.V7LedgerError, "^V7_PHASE_FILES_INVALID$"):
                ledger.measure(root, assignments, phase="failure_before_publication")
            with self.assertRaisesRegex(ledger.V7LedgerError, "^V7_PHASE_FILES_INVALID$"):
                ledger.measure(root, assignments, phase="success")
