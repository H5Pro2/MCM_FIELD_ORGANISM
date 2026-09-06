"""Ten neutral metadata tests. Never generate any S2-NF PCM source."""

import copy
from dataclasses import FrozenInstanceError, replace
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from tools import _s2nf_private_source_binding as b
from tools import _s2nf_private_preseal_verification as v


class SourceBindingTests(unittest.TestCase):
    def setUp(self):
        self.guard = patch.object(b.harmonic, "pcm_payload", side_effect=AssertionError("PCM_FORBIDDEN"))
        self.guard.start()
        self.addCleanup(self.guard.stop)
        self.specs = b.source_specs()

    def plans(self):
        rows = [b.bind_payload(s, s.historical_pcm_sha256 or "a" * 64) for s in self.specs]
        execution = b.execution_plan(rows, {"neutral_identity": True}, {})
        return execution, b.evaluation_plan(execution)

    def test_01_builtin_math_requires_two_independent_bindings(self):
        module = SimpleNamespace(__name__="math", __spec__=SimpleNamespace(origin="built-in"))
        actual = b.harmonic.math_identity(module, ("math",))
        self.assertEqual(actual, dict(kind="BUILT_IN", module_name="math", spec_origin="built-in", builtin_membership=True))
        with self.assertRaises(ValueError):
            b.harmonic.math_identity(module, ())
        with self.assertRaises(ValueError):
            b.harmonic.math_identity(SimpleNamespace(__name__="math"), ("math",))

    def test_02_file_math_binds_actual_file(self):
        with tempfile.TemporaryDirectory(prefix="s2nf-neutral-math-") as temp:
            path = Path(temp) / "neutral-module.bin"
            path.write_bytes(b"neutral module identity; no PCM")
            module = SimpleNamespace(__name__="math", __file__=str(path),
                __spec__=SimpleNamespace(origin=str(path), has_location=True))
            self.assertEqual(b.harmonic.math_identity(module, ())["sha256"], b.filehash(path))
            module.__spec__.origin = str(path.with_name("foreign.bin"))
            with self.assertRaises(ValueError):
                b.harmonic.math_identity(module, ())

    def test_03_source_identity_and_immutable_specs(self):
        self.assertEqual(tuple(s.source_id for s in self.specs), tuple(f"nf-a{i:02d}" for i in range(1, 8)))
        with self.assertRaises(FrozenInstanceError):
            self.specs[0].ordinal = 2
        with self.assertRaises(ValueError):
            replace(self.specs[0], source_id="nf-a03")
        with self.assertRaises(ValueError):
            b.validate_specs(list(self.specs))
        metadata = self.specs[0].payload()
        metadata["recipe"]["partials"].reverse()
        self.assertNotEqual(metadata["recipe"], self.specs[0].payload()["recipe"])

    def test_04_partial_append_order_and_phase_seed(self):
        base, extra = [json.loads(s.recipe_json) for s in (self.specs[0], self.specs[6])]
        self.assertEqual(extra["seed"], base["seed"])
        self.assertEqual(extra["partials"][:3], base["partials"])
        self.assertEqual(extra["partials"][3], dict(frequency_millihz=120000, amplitude_ratio=[3, 10]))
        extra["partials"].reverse()
        changed = replace(self.specs[6], recipe_json=b.canonical(extra).decode("ascii"))
        with self.assertRaises(ValueError):
            b.validate_specs(self.specs[:6] + (changed,))

    def test_05_exact_copies_keep_distinct_time_and_identity(self):
        left, right = self.specs[0], self.specs[2]
        self.assertEqual(left.recipe_json, right.recipe_json)
        self.assertEqual(left.historical_pcm_sha256, right.historical_pcm_sha256)
        self.assertNotEqual(left.source_id, right.source_id)
        self.assertEqual((left.payload()["window_start_sample"], right.payload()["window_start_sample"]), (0, 9600))
        self.assertNotEqual(b.bind_payload(left, left.historical_pcm_sha256)["source_digest"],
                            b.bind_payload(right, right.historical_pcm_sha256)["source_digest"])

    def test_06_payload_hash_and_size_fail_closed(self):
        with self.assertRaises(ValueError):
            b.bind_payload(self.specs[0], "a" * 64)
        with self.assertRaises(ValueError):
            b.bind_payload(self.specs[6], "invalid")
        with self.assertRaises(ValueError):
            b.bind_payload(self.specs[6], "a" * 64, 0)

    def test_07_literal_events_time_and_profile(self):
        events = b.events()
        self.assertEqual(len(events), 13)
        self.assertEqual(sum(e["kind"] == "FORMATION" for e in events), 3)
        self.assertEqual(events[7]["audio_source_id"], "nf-a02")
        self.assertEqual(events[7]["audio_start_tick"], 0)
        for history in ("s2nf-h01", "s2nf-h02"):
            rows = [e for e in events if e["history_id"] == history]
            self.assertTrue(all(a["audio_end_tick"] < c["audio_start_tick"] for a, c in zip(rows, rows[1:])))
        self.assertEqual(tuple(dict(b.PROFILE).values()), (48000, 4800, 480, 50.0, 18000.0, 48))

    def test_08_plan_roles_and_independent_metadata_verification(self):
        execution, evaluation = self.plans()
        before = b.digest([execution, evaluation])
        v.check_plans(execution, evaluation)
        self.assertEqual(b.digest([execution, evaluation]), before)
        self.assertNotIn("target_present", b.canonical(execution).decode("ascii"))
        self.assertEqual(sum(c["retention_eligible"] for c in evaluation["cases"]), 5)
        self.assertEqual(evaluation["zero_denominator"], "ERHALTUNG_NICHT_GEPRUEFT")

    def test_09_mutated_roots_fail_even_with_recomputed_selfdigests(self):
        execution, evaluation = self.plans()
        for field in ("events", "sources", "budgets", "extra"):
            changed = copy.deepcopy(execution)
            if field in ("events", "sources"):
                changed[field].reverse()
            elif field == "budgets":
                changed[field]["source_windows"] = 8
            else:
                changed["target_present"] = True
            changed.pop("execution_digest")
            changed = b.sealed(changed, "execution_digest")
            counterpart = copy.deepcopy(evaluation)
            counterpart.pop("evaluation_digest")
            counterpart["execution_digest"] = changed["execution_digest"]
            counterpart = b.sealed(counterpart, "evaluation_digest")
            with self.assertRaises(ValueError):
                v.check_plans(changed, counterpart)

    def test_10_pure_generator_selection_and_no_forbidden_imports(self):
        function, identity = b.chirp_functions()
        self.assertEqual(function.__name__, "_materialize_pcm")
        self.assertEqual(identity["selected_definitions"], ["S2LBMaterializationError", "_f32", "_materialize_pcm"])
        self.assertFalse(identity["module_entry_executed"])
        self.assertFalse(identity["function_bodies_modified"])
        self.assertFalse(any(n.startswith("mcm_field_organism") for n in sys.modules))
        self.assertNotIn("tools._s2lb_d_far_pcm_materialization", sys.modules)


if __name__ == "__main__":
    unittest.main()
