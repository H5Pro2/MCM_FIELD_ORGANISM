from __future__ import annotations

import ast
import inspect
import unittest

from tools.run_e1_s1gu_fixed_adapter_six_arm_lauf_197 import (
    EXECUTION_PERMITTED,
    RUN_NUMBER,
    RUN_STATUS,
    main,
)


class RunE1S1GUFixedAdapterSixArmLauf197Tests(unittest.TestCase):
    def test_run_number_follows_last_executed_lauf_196(self) -> None:
        self.assertEqual(197, RUN_NUMBER)

    def test_aborted_run_is_permanently_closed_against_retry(self) -> None:
        self.assertEqual(
            "TECHNICAL_PRESTART_IMPORT_ABORT_NO_FIELD_STEPS",
            RUN_STATUS,
        )
        self.assertFalse(EXECUTION_PERMITTED)
        with self.assertRaisesRegex(RuntimeError, "cannot rerun"):
            main()

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
