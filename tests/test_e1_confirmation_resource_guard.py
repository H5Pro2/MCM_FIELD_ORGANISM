from __future__ import annotations

import inspect
from pathlib import Path
import sys
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_confirmation_owner_authorization import (
    bind_e1_confirmation_owner_authorization,
)
from mcm_field_organism.e1_confirmation_release_contract import (
    prepare_e1_confirmation_release_contract,
)
from mcm_field_organism.e1_confirmation_resource_guard import (
    E1ConfirmationResourceGuardError,
    bind_e1_confirmation_resource_guard,
    run_guarded_synthetic_process,
)
from tests.test_e1_confirmation_release_contract import _inputs


ROOT = Path.cwd()
REPORTS = Path("reports")
TARGETS = (
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.attempt.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.lock",
)


def _authorization():
    binding, chain, audit = _inputs()
    contract = prepare_e1_confirmation_release_contract(binding, chain, audit)
    return bind_e1_confirmation_owner_authorization(contract)


def _matrix():
    success = run_guarded_synthetic_process(
        (sys.executable, "-c", "print('ok')"),
        ROOT,
        max_wall_seconds=5.0,
        max_peak_rss_bytes=128 * 1024**2,
    )
    wall = run_guarded_synthetic_process(
        (sys.executable, "-c", "import time; time.sleep(2)"),
        ROOT,
        max_wall_seconds=0.1,
        max_peak_rss_bytes=128 * 1024**2,
    )
    memory = run_guarded_synthetic_process(
        (
            sys.executable,
            "-c",
            "x=bytearray(96*1024*1024); print(len(x))",
        ),
        ROOT,
        max_wall_seconds=5.0,
        max_peak_rss_bytes=48 * 1024**2,
    )
    return success, wall, memory


class E1ConfirmationResourceGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.authorization = _authorization()
        cls.success, cls.wall, cls.memory = _matrix()

    def test_synthetic_success_completes_under_limits(self) -> None:
        self.assertEqual("COMPLETED", self.success.status)
        self.assertEqual(0, self.success.return_code)
        self.assertEqual("ok", self.success.stdout.strip())

    def test_wall_limit_terminates_process_tree(self) -> None:
        self.assertEqual("WALL_LIMIT_EXCEEDED", self.wall.status)
        self.assertLess(self.wall.elapsed_seconds, 1.5)

    def test_memory_limit_terminates_or_blocks_allocation(self) -> None:
        self.assertEqual("MEMORY_LIMIT_EXCEEDED", self.memory.status)
        self.assertNotEqual(0, self.memory.return_code)

    def test_binding_requires_complete_synthetic_matrix(self) -> None:
        binding = bind_e1_confirmation_resource_guard(
            self.authorization, self.success, self.wall, self.memory
        )

        self.assertEqual(1_800, binding.max_wall_seconds)
        self.assertEqual(4 * 1024**3, binding.max_peak_rss_bytes)
        self.assertTrue(binding.process_tree_kill_bound)
        self.assertFalse(binding.canonical_execution_permitted)

    def test_incomplete_matrix_fails_closed(self) -> None:
        with self.assertRaises(E1ConfirmationResourceGuardError):
            bind_e1_confirmation_resource_guard(
                self.authorization,
                self.success,
                self.success,
                self.memory,
            )

    def test_guard_keeps_registered_paths_free(self) -> None:
        self.assertTrue(all(not path.exists() for path in TARGETS))

    def test_guard_roles_remain_private(self) -> None:
        source = inspect.getsource(bind_e1_confirmation_resource_guard)
        self.assertNotIn("execute_e1_confirmation_canonical_once", source)
        for role in (
            "E1ConfirmationResourceGuardBinding",
            "run_guarded_synthetic_process",
            "bind_e1_confirmation_resource_guard",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
