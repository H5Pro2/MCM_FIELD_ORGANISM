"""Neutral provenance tests only; never generate a PCM payload."""

import hashlib
import math
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from reports.s2nd import seal_inventory as sealer


def module(origin, location=False, filename=None):
    result = SimpleNamespace(__name__="math", __spec__=SimpleNamespace(origin=origin, has_location=location))
    if filename is not None:
        result.__file__ = filename
    return result


class S2NDModuleIdentityTests(unittest.TestCase):
    def setUp(self):
        for name in ("pcm_payload", "inventory", "panel_inventory", "evaluation_plan", "main"):
            guard = patch.object(sealer, name, side_effect=AssertionError("OUT_OF_SCOPE_CALL"))
            guard.start()
            self.addCleanup(guard.stop)

    def test_01_real_builtin_has_no_invented_file_binding(self):
        self.assertEqual("built-in", math.__spec__.origin)
        self.assertIn("math", sys.builtin_module_names)
        identity = sealer.math_identity(math, sys.builtin_module_names)
        self.assertEqual({"kind": "BUILT_IN", "module_name": "math", "spec_origin": "built-in",
                          "builtin_membership": True}, identity)
        self.assertNotIn("path", identity)
        self.assertNotIn("sha256", identity)

    def test_02_both_builtin_proofs_are_required(self):
        with self.assertRaisesRegex(ValueError, "^MATH_BUILTIN_BINDING_INVALID$"):
            sealer.math_identity(module("built-in"), ())
        for origin in (None, "", "frozen"):
            with self.subTest(origin=origin), self.assertRaises(ValueError):
                sealer.math_identity(module(origin), ("math",))
        with self.assertRaisesRegex(ValueError, "^MATH_MODULE_ORIGIN_INVALID$"):
            sealer.math_identity(SimpleNamespace(__name__="math"), ("math",))

    def test_03_file_origin_binds_actual_file_and_hash(self):
        with tempfile.TemporaryDirectory(prefix="s2nd-identity-") as directory:
            path = Path(directory) / "neutral-module.bin"
            content = b"neutral provenance fixture\x00\xff"
            path.write_bytes(content)
            identity = sealer.math_identity(module(str(path), True, str(path)), ())
            self.assertEqual({"kind": "FILE_BASED", "module_name": "math", "spec_origin": str(path),
                              "builtin_membership": False, "path": str(path.resolve()),
                              "sha256": hashlib.sha256(content).hexdigest()}, identity)
            self.assertEqual(content, path.read_bytes())

    def test_04_missing_conflicting_or_unresolved_file_origin_fails_closed(self):
        with tempfile.TemporaryDirectory(prefix="s2nd-invalid-identity-") as directory:
            one, two = Path(directory) / "one.bin", Path(directory) / "two.bin"
            one.write_bytes(b"one")
            two.write_bytes(b"two")
            variants = (
                (module(str(one), True), ()),
                (module(str(one), True, str(two)), ()),
                (module(str(one), False, str(one)), ()),
                (module(str(one), True, str(one)), ("math",)),
                (module(str(one) + ".missing", True, str(one) + ".missing"), ()),
                (module(directory, True, directory), ()),
                (module("relative.bin", True, "relative.bin"), ()),
                (module("frozen", True, str(one)), ()),
            )
            for candidate, builtin_names in variants:
                with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                    sealer.math_identity(candidate, builtin_names)

    def test_05_wrong_module_name_is_not_math_provenance(self):
        candidate = module("built-in")
        candidate.__name__ = "unrelated"
        with self.assertRaisesRegex(ValueError, "^MATH_MODULE_NAME_INVALID$"):
            sealer.math_identity(candidate, ("math", "unrelated"))


if __name__ == "__main__":
    unittest.main()
