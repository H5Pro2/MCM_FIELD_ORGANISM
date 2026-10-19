"""Neutral preflight checks for the one-shot S2-TY qualification starter."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
STARTER = ROOT / "reports" / "s2ty" / "qualify_s2ty_neutral_once.py"
spec = importlib.util.spec_from_file_location("s2ty_formal_qualification_starter", STARTER)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def output_for(ids):
    lines = []
    for identifier in ids:
        method = identifier.rsplit(".", 1)[1]
        lines.append(f"{method} ({identifier}) ... ok")
    return "\n".join(lines) + f"\n\nRan {len(ids)} tests\n\nOK\n"


def observation():
    return {
        "counts": {"pcm_hashes": 22, "audio_analyses": 22, "nj_projections": 22},
        "success_branch": {"contributions": {"record": 105_817}},
        "record_reserve_bytes": 131_072,
    }


class Tests(unittest.TestCase):
    def test_static_discovery_matches_the_bound_inventory(self):
        self.assertEqual(set(module.discovered_test_ids()), set(module.TEST_IDS))

    def test_complete_bound_inventory_is_qualified(self):
        result = module.qualification_outcome(
            exit_code=0, output=output_for(module.TEST_IDS), observation=observation(), before={"x": "a"}, after={"x": "a"}
        )
        self.assertTrue(result["qualified"])
        self.assertTrue(result["test_ids_exact"])

    def test_duplicate_replaces_missing_test_id_is_not_qualified(self):
        identifiers = module.TEST_IDS[:-1] + (module.TEST_IDS[0],)
        result = module.qualification_outcome(
            exit_code=0, output=output_for(identifiers), observation=observation(), before={"x": "a"}, after={"x": "a"}
        )
        self.assertFalse(result["qualified"])
        self.assertIn("TEST_IDS_INVALID", result["reasons"])

    def test_error_output_is_not_qualified(self):
        result = module.qualification_outcome(
            exit_code=1, output="test_x (tests.example.Tests) ... ERROR\n\nRan 1 tests\n\nFAILED\n", observation=observation(), before={"x": "a"}, after={"x": "a"}
        )
        self.assertFalse(result["qualified"])
        self.assertIn("UNITTEST_EXIT_NONZERO", result["reasons"])

    def test_missing_materialization_observation_is_not_qualified(self):
        result = module.qualification_outcome(
            exit_code=0, output=output_for(module.TEST_IDS), observation=None, before={"x": "a"}, after={"x": "a"}
        )
        self.assertFalse(result["qualified"])
        self.assertIn("MATERIALIZATION_OBSERVATION_INVALID", result["reasons"])

    def test_mismatched_parenthesized_id_and_skipped_test_are_not_qualified(self):
        wrong = list(module.TEST_IDS)
        wrong[0] = wrong[0].rsplit(".", 1)[0] + ".test_other"
        output = output_for(wrong).replace(" ... ok", " ... skipped 'neutral'", 1)
        result = module.qualification_outcome(
            exit_code=0, output=output, observation=observation(), before={"x": "a"}, after={"x": "a"}
        )
        self.assertFalse(result["qualified"])
        self.assertIn("TEST_IDS_INVALID", result["reasons"])
        self.assertIn("TEST_RESULTS_INVALID", result["reasons"])
