from __future__ import annotations

import copy
import hashlib
import inspect
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mcm_field_organism.e1_completion_aligned_refinement import _refined_steps
from mcm_field_organism.e1_confirmation_descriptor_input_resolver import (
    prepare_e1_confirmation_descriptor_bundle_from_run_contract,
)
from mcm_field_organism.e1_confirmation_full_formation_handoff import (
    E1ConfirmationFullFormationHandoffError,
    S1_EC14_CONTRACT_DIGEST,
    S1_EC14_EDGE_BINDING_COUNT,
    S1_EC14_PROBE_CANDIDATE_ROLES,
    S1_EC14_STATE_COUNT,
    build_full_formation_handoff_envelope,
    load_full_formation_handoff_payload,
)
from mcm_field_organism.e1_confirmation_full_formation_lifecycle import (
    E1PreparedFullFormationResult,
)
from mcm_field_organism.e1_confirmation_prepared_formation_consumer import (
    _typed_values_from_bundle,
)
from mcm_field_organism.e1_confirmation_research_corridor import (
    build_e1_confirmation_research_corridor,
    prepare_e1_confirmation_synthetic_run_contract,
)
from mcm_field_organism.e1_confirmation_small_five_arm_formation import (
    run_small_five_arm_formation_in_memory,
)
from mcm_field_organism.e1_confirmation_small_refinement_matrix import (
    _refinement_residual,
    _state_distance,
)
from mcm_field_organism.e1_refined_formation_runner import _digest
from tests.test_e1_confirmation_typed_prepared_inputs import (
    CANONICAL_TARGETS,
    UPSTREAM,
)


S1_EC13_REPORT = Path(
    "synthetic_runs/s1ec13_full_formation_once_v1/"
    "e1_confirmation_s1ec3_synthetic_once_v1.json"
)
S1_EC13_REPORT_SHA256 = (
    "15932c1f3f6b493ebc090c6e2da5612dd3bc35e6f9aa012f416ef710ee54e48a"
)


def _full_geometry_fixture_result() -> E1PreparedFullFormationResult:
    descriptor = build_e1_confirmation_research_corridor(UPSTREAM)
    with TemporaryDirectory() as directory:
        run = prepare_e1_confirmation_synthetic_run_contract(
            descriptor, Path(directory)
        )
        bundle = prepare_e1_confirmation_descriptor_bundle_from_run_contract(
            run, UPSTREAM
        )
        values = _typed_values_from_bundle(bundle)
        clock_id = values.av_permutation.history_ab[0].clock_id
        refinements = tuple(
            run_small_five_arm_formation_in_memory(
                name,
                values.av_permutation.history_ab,
                values.av_permutation.history_ba,
                _refined_steps(
                    clock_id,
                    1_000_000.0,
                    (0, 1_000_000, 2_000_000),
                    factor,
                ),
                _refined_steps(
                    clock_id,
                    1_000_000.0,
                    (0, 1_000_000, 2_000_000),
                    factor,
                ),
                values.initial_field,
                values.initial_state,
            )
            for name, factor in (("r2", 2), ("r4", 4), ("r8", 8))
        )
        history_distances = tuple(
            (
                item.refinement_id,
                _state_distance(
                    item.arms[0].output_state,
                    item.arms[1].output_state,
                ),
            )
            for item in refinements
        )
        r2_r4 = _refinement_residual(refinements[0], refinements[1])
        r4_r8 = _refinement_residual(refinements[1], refinements[2])
        values_payload = {
            "execution_id": bundle.execution_id,
            "run_contract_digest": bundle.run_contract_digest,
            "bundle_digest": bundle.bundle_digest,
            "pre_attempt_preflight_digest": "1" * 64,
            "in_attempt_preflight_digest": "1" * 64,
            "refinements": refinements,
            "refinement_step_counts": (
                ("r2", 2, 400, 400),
                ("r4", 4, 800, 800),
                ("r8", 8, 1600, 1600),
            ),
            "history_state_distances": history_distances,
            "r2_r4_state_residual": r2_r4,
            "r4_r8_state_residual": r4_r8,
            "convergence_nonincreasing": r4_r8 <= r2_r4,
            "attempt_present_during_execution": True,
            "all_five_arm_controls_passed": True,
            "prepared_inputs_preserved": True,
            "real_field_kernels_executed": True,
            "full_prepared_formation_executed": True,
            "temporary_lifecycle_only": True,
            "canonical_execution_permitted": False,
            "probe_execution_permitted": False,
            "claims_permitted": False,
        }
        digest_payload = {
            name: value
            for name, value in values_payload.items()
            if name != "refinements"
        }
        digest_payload["refinement_result_digests"] = tuple(
            item.result_digest for item in refinements
        )
        return E1PreparedFullFormationResult(
            **values_payload,
            result_digest=_digest(digest_payload),
        )


class E1ConfirmationFullFormationHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = _full_geometry_fixture_result()
        cls.envelope = build_full_formation_handoff_envelope(cls.result)

    def test_payload_contains_all_states_and_roundtrips_through_json(self) -> None:
        encoded = json.dumps(
            self.envelope.payload,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
        decoded = json.loads(encoded)
        loaded = load_full_formation_handoff_payload(decoded)

        self.assertEqual(S1_EC14_STATE_COUNT, self.envelope.state_count)
        self.assertEqual(
            S1_EC14_EDGE_BINDING_COUNT, self.envelope.edge_binding_count
        )
        self.assertEqual(self.result.result_digest, loaded.result_digest)
        self.assertEqual(
            tuple(
                arm.output_state
                for refinement in self.result.refinements
                for arm in refinement.arms
            ),
            tuple(
                arm.output_state
                for refinement in loaded.refinements
                for arm in refinement.arms
            ),
        )

    def test_payload_tampering_is_rejected(self) -> None:
        changed = copy.deepcopy(self.envelope.payload)
        binding = changed["result"]["refinements"][0]["arms"][0][
            "output_state"
        ]["edge_bindings"][0]
        binding["binding"] += 1e-9

        with self.assertRaises(E1ConfirmationFullFormationHandoffError):
            load_full_formation_handoff_payload(changed)

    def test_contract_keeps_publication_probe_and_claims_locked(self) -> None:
        self.assertEqual(S1_EC14_CONTRACT_DIGEST, self.envelope.contract_digest)
        self.assertEqual(
            S1_EC14_PROBE_CANDIDATE_ROLES,
            self.envelope.probe_candidate_roles,
        )
        self.assertFalse(self.envelope.runtime_execution_permitted)
        self.assertFalse(self.envelope.publication_permitted)
        self.assertFalse(self.envelope.probe_execution_permitted)
        self.assertFalse(self.envelope.claims_permitted)

    def test_serializer_and_loader_contain_no_execution_or_persistence(self) -> None:
        source = inspect.getsource(build_full_formation_handoff_envelope)
        source += inspect.getsource(load_full_formation_handoff_payload)

        for forbidden in (
            "_run_arm",
            "run_small_five_arm_formation_in_memory",
            "execute_prepared_bundle_synthetically",
            "_atomic_publish",
            "write_text",
            "write_bytes",
        ):
            self.assertNotIn(forbidden, source)

    def test_s1ec13_and_terminal_artifacts_remain_unchanged(self) -> None:
        self.assertEqual(
            S1_EC13_REPORT_SHA256,
            hashlib.sha256(S1_EC13_REPORT.read_bytes()).hexdigest(),
        )
        before = tuple(
            (
                path.exists(),
                hashlib.sha256(path.read_bytes()).hexdigest()
                if path.exists()
                else None,
            )
            for path in CANONICAL_TARGETS
        )
        build_full_formation_handoff_envelope(self.result)
        after = tuple(
            (
                path.exists(),
                hashlib.sha256(path.read_bytes()).hexdigest()
                if path.exists()
                else None,
            )
            for path in CANONICAL_TARGETS
        )
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
