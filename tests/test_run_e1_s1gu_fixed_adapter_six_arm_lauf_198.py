from __future__ import annotations

import ast
import inspect
import unittest

from tools.run_e1_s1gu_fixed_adapter_six_arm_lauf_198 import (
    IMPORT_PREFLIGHT_ARGUMENT,
    RUN_NUMBER,
    main,
)


class RunE1S1GUFixedAdapterSixArmLauf198Tests(unittest.TestCase):
    def test_new_run_number_is_separate_from_aborted_lauf_197(self) -> None:
        self.assertEqual(198, RUN_NUMBER)
        self.assertEqual("--import-preflight-only", IMPORT_PREFLIGHT_ARGUMENT)

    def test_runner_contains_exactly_one_s1gu_call_site(self) -> None:
        tree = ast.parse(inspect.getsource(main))
        calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "run_e1_formation_s1gu_six_arm_counting_adapter"
        ]
        self.assertEqual(1, len(calls))

    def test_runner_binds_real_transition_and_terminal_output(self) -> None:
        source = inspect.getsource(main)
        self.assertIn(
            "carrier_transition=advance_e1_formation_s1gs_real_single_batch_transition",
            source,
        )
        self.assertIn(
            "terminal_output_factory=build_e1_formation_s1hb_real_terminal_output",
            source,
        )

    def test_runner_has_no_file_writer_retry_or_memory_decision(self) -> None:
        source = inspect.getsource(main)
        for forbidden in (
            "open(",
            "write_text(",
            "write_bytes(",
            "retry",
            "memory_decision(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
