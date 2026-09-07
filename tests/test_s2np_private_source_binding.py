"""Neutral metadata and short non-NP generator cases only."""

from dataclasses import FrozenInstanceError, replace
import hashlib
import json
from pathlib import Path
import struct
import tempfile
from types import SimpleNamespace
import unittest

from tools import _s2np_private_source_binding as b
from tools import _s2np_private_preseal_verification as v


def plans():
    # Synthetic digests: none of the twelve NP payloads is generated here.
    sources = [b.bind_source(s, hashlib.sha256(f"neutral-{s.ordinal}".encode()).hexdigest()) for s in b.source_specs()]
    e = b.execution_plan(sources, {"neutral": True}, {}, {"neutral": True})
    return e, b.evaluation_plan(e)


def resign(value, key):
    return b.sealed({k: x for k, x in value.items() if k != key}, key)


class SourceBindingTests(unittest.TestCase):
    def test_01_literal_inventory(self):
        specs = b.source_specs()
        b.validate_specs(specs)
        self.assertEqual(len(specs), 12)
        self.assertEqual(specs[8].frequencies, (2791300, 5582600, 8373900))
        self.assertEqual(specs[4].frequencies, (319300, 638600, 957900))
        self.assertEqual(specs[-1].seed, "s2np-pcm-004")

    def test_02_identity_and_immutable_spec(self):
        s = b.source_specs()[0]
        with self.assertRaises(FrozenInstanceError):
            s.ordinal = 2
        with self.assertRaisesRegex(b.S2NPBindingError, "SOURCE_ID_INVALID"):
            replace(s, ordinal=True)
        with self.assertRaisesRegex(b.S2NPBindingError, "SOURCE_PLAN_CHANGED"):
            b.validate_specs(tuple(reversed(b.source_specs())))

    def test_03_exact_copy_bindings(self):
        specs = b.source_specs()
        for i, j in ((0, 2), (1, 6)):
            with self.subTest(pair=(i, j)):
                self.assertEqual(specs[i].recipe(), specs[j].recipe())
                self.assertNotEqual(specs[i].payload(), specs[j].payload())
                self.assertNotEqual(b.bind_source(specs[i], "a"*64)["source_digest"],
                                    b.bind_source(specs[j], "a"*64)["source_digest"])

    def test_04_time_forms(self):
        e, f = plans()
        for i, s in enumerate(e["sources"]):
            self.assertEqual((s["snapshot_index"], s["window_start_sample"], s["window_end_sample"]),
                             (10*i, 4800*i, 4800*(i+1)))
        e["sources"][0]["clock_id"] = "wrong"
        e["sources"][0] = resign(e["sources"][0], "source_digest")
        e = resign(e, "execution_digest"); f = b.evaluation_plan(e)
        with self.assertRaisesRegex(b.S2NPBindingError, "SOURCE_FORM_INVALID"):
            v.check_plans(e, f)

    def test_05_partial_order(self):
        s = b.source_specs()[0]
        with self.assertRaisesRegex(b.S2NPBindingError, "SOURCE_PLAN_CHANGED"):
            b.validate_specs((replace(s, frequencies=s.frequencies[::-1]),) + b.source_specs()[1:])
        with self.assertRaisesRegex(b.S2NPBindingError, "RECIPE_INVALID"):
            replace(s, frequencies=list(s.frequencies))

    def test_06_neutral_generator_rounding(self):
        generate, binding = b.pure_generator()
        recipe = dict(sample_count=16, sample_rate=48000, groups=[dict(seed="neutral-only",
            partials=[dict(frequency_millihz=123000, amplitude_ratio=[1, 5]),
                      dict(frequency_millihz=457000, amplitude_ratio=[1, 7])])])
        payload = generate(recipe)
        expected = bytearray()
        for j in range(16):
            total = 0.0
            for i, p in enumerate(recipe["groups"][0]["partials"]):
                u = int.from_bytes(hashlib.sha256(f"neutral-only:{i}".encode()).digest()[:4], "little")
                phase = (float(u)/4294967296.0)*b.math.tau
                angle = ((b.math.tau*(float(p["frequency_millihz"])/1000.0))*(float(j)/48000.0))+phase
                total = total + (float(p["amplitude_ratio"][0])/float(p["amplitude_ratio"][1]))*b.math.sin(angle)
            expected.extend(struct.pack("<f", total))
        self.assertEqual(payload, expected)
        self.assertEqual(len(payload), 64)
        self.assertFalse(binding["historical_entry_executed"])

    def test_07_math_builtin(self):
        module = SimpleNamespace(__name__="math", __spec__=SimpleNamespace(origin="built-in"))
        self.assertEqual(b.common.math_identity(module, ("math",))["kind"], "BUILT_IN")
        with self.assertRaisesRegex(ValueError, "MATH_BUILTIN_BINDING_INVALID"):
            b.common.math_identity(module, ())
        with self.assertRaisesRegex(ValueError, "MATH_MODULE_ORIGIN_INVALID"):
            b.common.math_identity(SimpleNamespace(__name__="math"), ("math",))

    def test_08_views(self):
        self.assertEqual([len(i) for _, i in b.VIEWS], [24, 24, 48])
        self.assertEqual(b.VIEWS[1][1], tuple(x for j in range(12) for x in (4*j, 4*j+3)))
        e, _ = plans(); e["views"][1]["indices"][0] = 1
        e = resign(e, "execution_digest")
        with self.assertRaisesRegex(b.S2NPBindingError, "VIEW_BINDING_INVALID"):
            v.check_plans(e, b.evaluation_plan(e))

    def test_09_panels_and_full_cases(self):
        e, f = plans(); v.check_plans(e, f)
        self.assertEqual(len(e["cases"]), 40)
        self.assertEqual([len(p["reference_ids"]) for p in e["panels"]], [2, 1, 1, 0])
        e["panels"][0]["reference_ids"].pop(); e = resign(e, "execution_digest")
        with self.assertRaisesRegex(b.S2NPBindingError, "PANEL_BINDING_INVALID"):
            v.check_plans(e, b.evaluation_plan(e))

    def test_10_evaluation_separation(self):
        e, f = plans()
        self.assertNotIn("target_source_id", json.dumps(e))
        self.assertEqual([r["target_source_id"] for r in f["relations"]], ["np-a01"]*4 + ["np-a02"]*4 + [None]*2)
        f["relations"][0]["target_source_id"] = "np-a02"; f = resign(f, "evaluation_digest")
        with self.assertRaisesRegex(b.S2NPBindingError, "EVALUATION_FORM_INVALID"):
            v.check_plans(e, f)

    def test_11_digest_and_root_links(self):
        e, f = plans(); f["execution_digest"] = "a"*64; f = resign(f, "evaluation_digest")
        with self.assertRaisesRegex(b.S2NPBindingError, "ROOT_LINK_INVALID"):
            v.check_plans(e, f)
        with self.assertRaisesRegex(b.S2NPBindingError, "DIGEST_INVALID"):
            b.bind_source(b.source_specs()[0], "BAD")

    def test_12_profile_metadata_only(self):
        p = b.profile_binding()
        self.assertEqual(p["half"]["factor_hex"], "0x1.0000000000000p-1")
        self.assertFalse(p["projection_executed"])
        self.assertEqual(p["half"]["raw_profile_digest"], p["raw_profile_digest"])
        e, _ = plans(); e["profiles"]["half"]["factor_hex"] = "0x1p0"; e = resign(e, "execution_digest")
        with self.assertRaisesRegex(b.S2NPBindingError, "PROFILE_BINDING_INVALID"):
            v.check_plans(e, b.evaluation_plan(e))

    def test_13_output_limit_and_write_conflict(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/"neutral.json"
            with self.assertRaisesRegex(b.S2NPBindingError, "OUTPUT_SIZE_EXCEEDED"):
                b.publish(path, {"x": "large"}, limit=1)
            self.assertFalse(path.exists())
            b.publish(path, {"x": 1})
            with self.assertRaises(FileExistsError):
                b.publish(path, {"x": 2})

    def test_14_metadata_mutation_and_budget(self):
        e, f = plans(); original = b.canonical(e)
        v.check_plans(e, f)
        self.assertEqual(original, b.canonical(e))
        self.assertLess(len(original), b.MAX_METADATA_BYTES)
        e["budgets"]["max_live_payloads"] = 2; e = resign(e, "execution_digest")
        with self.assertRaisesRegex(b.S2NPBindingError, "EXECUTION_FORM_INVALID"):
            v.check_plans(e, b.evaluation_plan(e))

    def test_15_all_collisions_preserved(self):
        sources = [dict(source_id=f"neutral-{i}", pcm_sha256="b"*64) for i in range(3)]
        self.assertEqual(b.collision_groups(sources)[0]["source_ids"], ["neutral-0", "neutral-1", "neutral-2"])
        self.assertEqual(len(sources), 3)

    def test_16_gates_and_no_forbidden_imports(self):
        import sys
        self.assertFalse(b.MAIN_GATE)
        forbidden = ("mcm_field_organism", "tools._s2nj", "tools._s2ng", "tools._s2mr")
        self.assertFalse(any(name.startswith(forbidden) for name in sys.modules))
        e, f = plans()
        for key in ("receptor_execution_authorized", "nj_execution_authorized", "comparison_execution_authorized", "system_execution_authorized"):
            self.assertFalse(e[key])
        v.check_plans(e, f)


if __name__ == "__main__":
    unittest.main()
