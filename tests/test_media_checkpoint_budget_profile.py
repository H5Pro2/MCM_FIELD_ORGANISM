"""Administrative budget-profile tests; no media or native processing."""
import copy
from dataclasses import FrozenInstanceError
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from reports import run_selected_media_restart_once as entry
from tools import _media_restart_evidence as e
from tools import _media_checkpoint_budget_profile as b
from tools import _media_publication_plan as p
from tools import _media_restart_reservations as r

OUT = Path(os.environ["MEDIA_BUDGET_QUAL_OUT"])
OBS = []
HISTORICAL = dict(total=4194304, metadata=131072, sources=327680, shared=393216, verification=262144)


def guard(event, args):
    if event == "open" and isinstance(args[0], (str, bytes)):
        if os.fsdecode(args[0]).lower().endswith((".mp4", ".pcm", ".rgb", ".wav", ".mp3", ".mkv")):
            raise AssertionError("MEDIA_PAYLOAD_FORBIDDEN")
    if event == "subprocess.Popen":
        raise AssertionError("CHILD_PROCESS_FORBIDDEN")


sys.addaudithook(guard)


def ledger(**amounts):
    totals = dict.fromkeys(p.CATEGORIES, 0)
    totals.update(amounts)
    totals["total"] = sum(totals.values())
    totals["shared"] = sum(totals[k] for k in ("sources", "nj", "formations", "generations"))
    return dict(files=[], totals=totals, limits=dict(b.LIMITS), budget_profile_digest=b.digest())


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(patch.stopall)
        patch.object(entry.c.media, "NativeRuntime", side_effect=AssertionError("NATIVE_FORBIDDEN")).start()
        patch.object(entry.w, "WorkerDecoder", side_effect=AssertionError("DECODER_FORBIDDEN")).start()
        self.assertFalse(entry.c.MAIN_GATE)
        self.assertFalse(entry.c.QUALIFIED)
        self.root = OUT/self._testMethodName

    @classmethod
    def tearDownClass(cls):
        with (OUT/"observations.json").open("xb") as stream:
            stream.write(e.canonical(OBS))

    def error(self, kind, code, call):
        with self.assertRaises(kind) as caught:
            call()
        self.assertEqual(caught.exception.code, code)
        return caught.exception

    def store(self):
        store = e.Store(self.root, budget_profile=b.payload())
        store.publish_profile()
        return store

    def test_01_fixed_immutable_profile(self):
        profile = b.bind(b.payload())
        self.assertEqual(profile.limits, dict(total=25165824, metadata=3145728, sources=524288, shared=786432, verification=262144))
        with self.assertRaises(FrozenInstanceError):
            profile.profile = "foreign"
        mutable = profile.limits
        mutable["metadata"] = 0
        self.assertEqual(profile.limits["metadata"], 3145728)

    def test_02_foreign_or_changed_profile(self):
        for key, value in (("version", "other"), ("profile", "other"), ("limits", HISTORICAL)):
            with self.subTest(key=key):
                bad = dict(b.payload(), **{key: value})
                self.error(b.BudgetProfileError, "MEDIA_BUDGET_PROFILE_INVALID", lambda: b.bind(bad))

    def test_03_legacy_defaults_and_bytes(self):
        store = e.Store(self.root)
        self.assertEqual(e.LIMITS, HISTORICAL)
        self.assertEqual(store.ledger()["limits"], HISTORICAL)
        self.assertNotIn("budget_profile_digest", store.ledger())
        value = dict(status="neutral", number=1)
        store.publish(self.root/"record.json", value)
        self.assertEqual((self.root/"record.json").read_bytes(), e.canonical(value))
        self.assertEqual(store.read(self.root/"record.json"), value)

    def test_04_profile_publication_and_independent_reader(self):
        store = self.store()
        value = dict(status="neutral", number=2)
        before = copy.deepcopy(value)
        store.publish(self.root/"record.json", value)
        reader = e.Store(self.root, budget_profile=b.payload())
        self.assertEqual(reader.read(self.root/"record.json"), before)
        raw = json.loads((self.root/"record.json").read_bytes())
        self.assertEqual(set(raw), {"budget_profile_digest", "value"})
        self.assertEqual(raw["budget_profile_digest"], b.digest())
        self.assertEqual(value, before)

    def test_05_missing_profile_stops_verifier(self):
        store = e.Store(self.root, budget_profile=b.payload())
        with patch.object(entry.c, "validate", side_effect=AssertionError("NATIVE_VERIFY_FORBIDDEN")) as native:
            self.error(entry.w.RestartError, "MEDIA_BUDGET_PROFILE_MISSING",
                lambda: entry.p.verify_comparison(store, None, "reference", "suspend19", "restore20"))
        native.assert_not_called()

    def test_06_manipulated_available_profile(self):
        store = self.store()
        path = self.root/"budget-profile.json"
        bad = b.payload()
        bad["limits"]["total"] += 1
        path.write_bytes(e.canonical(bad))
        self.error(entry.w.RestartError, "MEDIA_BUDGET_PROFILE_CHANGED", store.verify_budget_profile)

    def test_07_mixed_record_profiles_rejected(self):
        store = self.store()
        for i, value in enumerate((dict(status="old"), dict(budget_profile_digest="0"*64, value={} ))):
            with self.subTest(i=i):
                path = self.root/(str(i)+".json")
                path.write_bytes(e.canonical(value))
                self.error(entry.w.RestartError, "MEDIA_RECORD_PROFILE_BINDING", lambda: store.read(path))

    def test_08_metadata_exact_boundary_publication(self):
        store = self.store()
        virtual = ledger(metadata=3145728-8192-200)
        with patch.object(store, "ledger", return_value=virtual):
            store._write(self.root/"boundary", b"x"*100, "metadata")
        self.assertEqual((self.root/"boundary").stat().st_size, 100)
        OBS.append(dict(test=8, charged_metadata=3145728, accepted=True))

    def test_09_metadata_one_byte_over(self):
        store = self.store()
        virtual = ledger(metadata=3145728-8192-200+1)
        with patch.object(store, "ledger", return_value=virtual):
            error = self.error(entry.w.RestartError, "MEDIA_STORE_BUDGET",
                lambda: store._write(self.root/"over", b"x"*100, "metadata"))
        self.assertEqual(error.details["prospective"]["metadata"], 3145729)
        self.assertFalse((self.root/"over").exists())

    def test_10_global_limit_despite_valid_local_classes(self):
        # Arithmetic ledger aggregates, not a claim of a legal single state.
        value = ledger(metadata=1000000, sources=400000, nj=100000, formations=100000,
                       generations=100000, field=2000000)
        value["totals"]["native"] = 25165824-8192-200+1-value["totals"]["total"]
        value["totals"]["total"] = 25165824-8192-200+1
        result = p.transaction(value, [dict(path="temporary", category="metadata", bytes=100),
            dict(path="final", category="metadata", bytes=100)], (), (), 4096)
        self.assertEqual(result["success"]["charged"]["total"], 25165825)
        self.assertEqual(result["violations"], ["total"])

    def test_11_joint_class_and_verification_boundaries(self):
        for amount, expected in ((286432, []), (286433, ["shared"])):
            with self.subTest(amount=amount):
                result = p.transaction(ledger(sources=500000, nj=amount), [], (), (), 4096)
                self.assertEqual(result["violations"], expected)
        rows = [dict(path=str(i), category="verification", bytes=131072) for i in range(2)]
        self.assertEqual(p.transaction(ledger(), rows, (), (), 4096)["violations"], [])
        rows[1]["bytes"] += 1
        self.assertEqual(p.transaction(ledger(), rows, (), (), 4096)["violations"], ["verification"])

    def test_12_unchanged_single_publication_limits(self):
        for category, cap in b.ITEM_LIMITS.items():
            with self.subTest(category=category):
                b.check_item(category, cap)
                self.error(b.BudgetProfileError, "MEDIA_HISTORICAL_ITEM_LIMIT", lambda: b.check_item(category, cap+1))
        store = self.store()
        self.error(b.BudgetProfileError, "MEDIA_HISTORICAL_ITEM_LIMIT",
            lambda: store._write(self.root/"large", b"x"*61441, "metadata"))
        self.assertFalse((self.root/"large").exists())
        self.assertEqual(e.FAILURE_BYTES, 4096)
        self.assertEqual(e.FAILURE_RESERVE, 8192)
        self.assertEqual(e.serialization.MAX_BYTES, 4194304)

    def test_13_full_catalog_profile_preflight(self):
        catalog = json.loads((entry.ROOT/"reports/MEDIA_RESTART_SUCCESS_ENVELOPE_20260913.json").read_bytes())
        old = {row["role"]: row for row in catalog["roles"]}
        entries = []
        for role, (category, count) in p.full_layout(b.digest()).items():
            upper = len(e.canonical(b.payload())) if role == "budget-profile.json" else old[role]["upper_each"]
            entries.append(dict(id=role, category=category, count=count, lower=0, upper=upper))
        plan = p.Plan.bind(dict(version=p.VERSION, scope="FULL_RESTART", budget_profile_digest=b.digest(), positions=entries))
        groups = r.bind(catalog["joint_reservations"])
        result = plan.preflight(ledger(), groups, groups, 4096)
        self.assertEqual(len(result), 83)
        self.assertTrue(all(not row["decision"]["violations"] for row in result))
        OBS.append(dict(test=13, roles=len(entries), upper_peak=max(row["decision"]["success"]["charged"]["total"] for row in result)))

    def test_14_joint_reserves_not_multiplied(self):
        groups = r.bind([dict(name="logs", paths=["a", "b"], limit=8192, closed_by="done")])
        entries = [dict(id=name, category="metadata", count=1, lower=0, upper=8192) for name in ("a", "b")]
        plan = p.Plan.bind(dict(version=p.VERSION, scope="NEUTRAL_ADMIN", budget_profile_digest=b.digest(), positions=entries))
        result = plan.preflight(ledger(), groups, groups, 4096)
        self.assertEqual(result[0]["decision"]["success"]["charged"]["metadata"], 24576)
        self.error(p.PlanError, "PUBLICATION_LEDGER_PROFILE", lambda: plan.preflight(
            dict(ledger(), budget_profile_digest=None), groups, groups, 4096))
        self.error(b.BudgetProfileError, "MEDIA_BUDGET_LEDGER_BINDING",
            lambda: p.transaction(dict(ledger(), limits=HISTORICAL), [], (), (), 4096))

    def test_15_entry_requires_explicit_new_profile(self):
        with patch.object(entry, "bound_json", return_value={}):
            self.error(entry.w.RestartError, "REAL_BUDGET_PROFILE_REQUIRED", lambda: entry.load("x", "x", "x", "x"))
        data = dict(budget_profile=b.payload(), version=entry.VERSION, limits=HISTORICAL, stages=list(entry.STAGES))
        with patch.object(entry, "bound_json", return_value=data):
            self.error(entry.w.RestartError, "REAL_BINDING_FORM", lambda: entry.load("x", "x", "x", "x"))

    def test_16_profile_bound_error_closure(self):
        store = self.store()
        value = dict(status="NOT_EVALUABLE", code="ADMINISTRATIVE", phase="PREFLIGHT", completed=0)
        store.failure(self.root/"failure.json", value)
        self.assertEqual(store.read(self.root/"failure.json"), value)
        self.assertLessEqual((self.root/"failure.json").stat().st_size, 4096)
        original = (self.root/"failure.json").read_bytes()
        store.failure(self.root/"failure.json", value)
        self.assertEqual((self.root/"failure.json").read_bytes(), original)
