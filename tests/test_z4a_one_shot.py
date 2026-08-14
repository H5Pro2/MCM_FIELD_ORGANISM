from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from mcm_field_organism.z4a_generic_trajectory_runner import (
    execute_z4a_technical_packet,
)
from mcm_field_organism.z4a_one_shot import (
    Z4AOneShotError,
    Z4AOneShotPreflight,
    _RESERVED_OUTPUT,
    execute_z4a_one_shot,
    z4a_one_shot_public_roles,
)
from mcm_field_organism.z4a_scalar_evaluation import WORLD_ORDER
from mcm_field_organism.z4a_scalar_measurement_adapter import (
    evaluate_z4a_technical_packets,
)
from tests.test_z4a_generic_trajectory_runner import world


def preflight(*, fail=None):
    digest = hashlib.sha256(b"z4a.one-shot.synthetic.bindings.v1").hexdigest()
    names = (
        "all_source_bindings_final",
        "all_implementation_digests_match",
        "all_world_packages_materializable",
        "browser_binding_final",
    )
    return Z4AOneShotPreflight(
        "z4a.run197.preflight.v1",
        (("z4a.one-shot.synthetic.bindings.v1", digest),),
        tuple((name, name != fail) for name in names),
    )


class Z4AOneShotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.worlds = tuple(world(world_id) for world_id in WORLD_ORDER)

    def test_one_shot_calls_matrix_and_evaluation_once_then_publishes(self) -> None:
        calls = {"preflight": 0, "materialize": 0, "matrix": 0, "evaluate": 0}

        def checked_preflight():
            calls["preflight"] += 1
            return preflight()

        def materialize():
            calls["materialize"] += 1
            return self.worlds

        def matrix(worlds):
            calls["matrix"] += 1
            return tuple(execute_z4a_technical_packet(item) for item in worlds)

        def evaluate(packets):
            calls["evaluate"] += 1
            return evaluate_z4a_technical_packets(packets)

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "synthetic-result.json"
            receipt = execute_z4a_one_shot(
                output,
                preflight=checked_preflight,
                materialize_worlds=materialize,
                execute_matrix=matrix,
                evaluate=evaluate,
            )
            self.assertEqual(
                {"preflight": 1, "materialize": 1, "matrix": 1, "evaluate": 1},
                calls,
            )
            self.assertTrue(output.is_file())
            self.assertEqual(168, receipt.task_count)
            self.assertTrue(receipt.atomic_publish_complete)
            self.assertFalse(receipt.reserved_output_used)
            with output.open("r", encoding="ascii") as handle:
                value = json.load(handle)
            self.assertEqual("lauf-197", value["run_id"])
            self.assertFalse(value["raw_trajectories_retained"])
            self.assertFalse((Path(str(output) + ".lock")).exists())
            self.assertFalse((Path(str(output) + ".attempted")).exists())

            with self.assertRaisesRegex(Z4AOneShotError, "already exists"):
                execute_z4a_one_shot(
                    output,
                    preflight=checked_preflight,
                    materialize_worlds=materialize,
                    execute_matrix=matrix,
                    evaluate=evaluate,
                )
            self.assertEqual(1, calls["matrix"])

    def test_failed_preflight_stops_before_world_or_matrix_stage(self) -> None:
        calls = {"materialize": 0, "matrix": 0}

        def materialize():
            calls["materialize"] += 1
            return self.worlds

        def matrix(_worlds):
            calls["matrix"] += 1
            return ()

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "preflight-failure.json"
            with self.assertRaisesRegex(Z4AOneShotError, "preflight failed"):
                execute_z4a_one_shot(
                    output,
                    preflight=lambda: preflight(fail="browser_binding_final"),
                    materialize_worlds=materialize,
                    execute_matrix=matrix,
                    evaluate=evaluate_z4a_technical_packets,
                )
            self.assertEqual({"materialize": 0, "matrix": 0}, calls)
            self.assertFalse(output.exists())
            self.assertFalse(Path(str(output) + ".attempted").exists())

    def test_hard_matrix_failure_leaves_attempt_marker_and_blocks_retry(self) -> None:
        def failed_matrix(_worlds):
            raise RuntimeError("synthetic hard stop")

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "hard-failure.json"
            with self.assertRaisesRegex(RuntimeError, "synthetic hard stop"):
                execute_z4a_one_shot(
                    output,
                    preflight=preflight,
                    materialize_worlds=lambda: self.worlds,
                    execute_matrix=failed_matrix,
                    evaluate=evaluate_z4a_technical_packets,
                )
            marker = Path(str(output) + ".attempted")
            self.assertTrue(marker.is_file())
            self.assertFalse(output.exists())
            with self.assertRaisesRegex(Z4AOneShotError, "manual review"):
                execute_z4a_one_shot(
                    output,
                    preflight=preflight,
                    materialize_worlds=lambda: self.worlds,
                    execute_matrix=failed_matrix,
                    evaluate=evaluate_z4a_technical_packets,
                )

    def test_reserved_real_output_is_refused_before_preflight(self) -> None:
        calls = []
        with self.assertRaisesRegex(Z4AOneShotError, "not execution-authorized"):
            execute_z4a_one_shot(
                _RESERVED_OUTPUT,
                preflight=lambda: calls.append("preflight"),
                materialize_worlds=lambda: self.worlds,
                execute_matrix=lambda _worlds: (),
                evaluate=evaluate_z4a_technical_packets,
            )
        self.assertEqual([], calls)

    def test_public_receipt_contains_no_packet_or_trajectory_payload(self) -> None:
        roles = set(z4a_one_shot_public_roles())
        self.assertTrue(
            {
                "packets",
                "worlds",
                "trajectories",
                "field_vectors",
            }.isdisjoint(roles)
        )


if __name__ == "__main__":
    unittest.main()
