from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from types import SimpleNamespace
import unittest

from mcm_field_organism.w7ak_cap_p0_raw_contrast_compositor import (
    W7AKResidualSample,
)
from mcm_field_organism.w7an_r124_resolution_container import (
    W7ANR124ResolutionContainer,
)
from mcm_field_organism.w7ao_resolution_comparison_contract import (
    build_w7ao_resolution_comparison_contract,
)
from mcm_field_organism.w7ap_raw_resolution_distance_compositor import (
    W7APRawResolutionDistanceError,
    compose_w7ap_raw_resolution_distances,
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _sample(tick: int, value: float) -> W7AKResidualSample:
    s_values = (value, value + 1.0)
    h_values = (value + 2.0, value + 3.0)
    payload = {
        "tick": tick,
        "s_residuals": s_values,
        "h_residuals": h_values,
    }
    return W7AKResidualSample(tick, s_values, h_values, _digest(payload))


def _container() -> W7ANR124ResolutionContainer:
    container = object.__new__(W7ANR124ResolutionContainer)
    roles = tuple(
        (path_id, checkpoint)
        for path_id in ("ab", "ag", "ba", "bg", "ua", "ub", "ug")
        for checkpoint in range(5)
    )
    resolutions = []
    for resolution_id, offset in (("r1", 0.0), ("r2", 1.0), ("r4", 1.25)):
        pairs = tuple(
            SimpleNamespace(
                path_id=path_id,
                checkpoint=checkpoint,
                plan_checkpoint_digest=f"plan-{path_id}-{checkpoint}",
                observation_ticks=(10, 20),
                residual_samples=(
                    _sample(10, offset + checkpoint),
                    _sample(20, offset + checkpoint + 0.5),
                ),
            )
            for path_id, checkpoint in roles
        )
        resolutions.append(
            SimpleNamespace(
                resolution_id=resolution_id,
                evaluated=False,
                pair_container=SimpleNamespace(pairs=pairs, evaluated=False),
            )
        )
    object.__setattr__(container, "resolutions", tuple(resolutions))
    object.__setattr__(container, "convergence_compared", False)
    object.__setattr__(container, "effect_floor_ready", False)
    object.__setattr__(
        container,
        "resolution_container_digest",
        "4f150aad9f5c3803f1432550aa4db79b40aea3f7a4975b49802694fad2fff3e5",
    )
    return container


class W7APRawResolutionDistanceCompositorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.container = _container()
        cls.contract = build_w7ao_resolution_comparison_contract()
        cls.result = compose_w7ap_raw_resolution_distances(
            cls.container,
            cls.contract,
        )

    def test_exactly_70_preregistered_role_distances_are_materialized(self):
        self.assertEqual(70, len(self.result.role_distances))
        self.assertEqual(
            ["r1-r2"] * 35 + ["r2-r4"] * 35,
            [item.comparison_id for item in self.result.role_distances],
        )

    def test_directed_residual_differences_and_metrics_are_raw(self):
        r12 = self.result.role_distances[0]
        r24 = self.result.role_distances[35]
        self.assertEqual((-1.0, -1.0), r12.distance_samples[0].s_deltas)
        self.assertEqual((-1.0, -1.0), r12.distance_samples[0].h_deltas)
        self.assertEqual(
            (1.0, 1.0, 2.0 ** 0.5 * 2.0),
            (r12.S_linf, r12.H_linf, r12.SH_l2),
        )
        self.assertEqual(0.25, r24.S_linf)
        self.assertEqual(0.25, r24.H_linf)

    def test_105_same_resolution_identity_controls_are_exact_zero(self):
        self.assertEqual(105, len(self.result.identity_distances))
        self.assertTrue(
            all(
                (item.S_linf, item.H_linf, item.SH_l2) == (0.0, 0.0, 0.0)
                for item in self.result.identity_distances
            )
        )
        self.assertTrue(self.result.identity_countercontrol_digest)
        self.assertTrue(self.result.order_countercontrol_digest)

    def test_all_decision_and_threshold_outputs_remain_locked(self):
        self.assertFalse(self.result.convergence_evaluated)
        self.assertFalse(self.result.epsilon_num_ready)
        self.assertFalse(self.result.effect_floor_ready)
        self.assertFalse(self.result.field_function_decision_allowed)
        self.assertTrue(self.result.repeat_baseline_bound_to_canonical_w7an)
        self.assertTrue(all(not item.evaluated for item in self.result.role_distances))

    def test_canonical_input_and_contract_digests_are_bound(self):
        self.assertEqual(
            self.container.resolution_container_digest,
            self.result.w7an_container_digest,
        )
        self.assertEqual(
            self.contract.contract_digest,
            self.result.w7ao_contract_digest,
        )

    def test_misaligned_role_geometry_is_rejected(self):
        container = _container()
        container.resolutions[1].pair_container.pairs[0].observation_ticks = (10,)
        with self.assertRaises(W7APRawResolutionDistanceError):
            compose_w7ap_raw_resolution_distances(container, self.contract)

    def test_tampering_is_rejected(self):
        with self.assertRaises(W7APRawResolutionDistanceError):
            replace(self.result, convergence_evaluated=True)

    def test_compositor_is_not_publicly_exported(self):
        from mcm_field_organism import current_api

        self.assertFalse(
            hasattr(current_api, "compose_w7ap_raw_resolution_distances")
        )


if __name__ == "__main__":
    unittest.main()
