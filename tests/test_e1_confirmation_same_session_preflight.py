from __future__ import annotations

import copy
from pathlib import Path
import unittest

from mcm_field_organism.e1_confirmation_owner_authorization import (
    bind_e1_confirmation_owner_authorization,
)
from mcm_field_organism.e1_confirmation_release_contract import (
    prepare_e1_confirmation_release_contract,
)
from mcm_field_organism.e1_confirmation_resource_guard import (
    bind_e1_confirmation_resource_guard,
)
from mcm_field_organism.e1_confirmation_same_session_preflight import (
    E1ConfirmationSameSessionPreflightError,
    prepare_e1_confirmation_same_session_preflight,
    require_fresh_e1_confirmation_preflight,
)
from tests.test_e1_confirmation_release_contract import _inputs
from tests.test_e1_confirmation_resource_guard import _matrix


TARGETS = (
    Path("reports/e1_refined_confirmation_s1eb_once_v1.json"),
    Path("reports/e1_refined_confirmation_s1eb_once_v1.attempt.json"),
    Path("reports/e1_refined_confirmation_s1eb_once_v1.lock"),
)


def _preflight():
    binding, chain, audit = _inputs()
    release = prepare_e1_confirmation_release_contract(binding, chain, audit)
    authorization = bind_e1_confirmation_owner_authorization(release)
    guard = bind_e1_confirmation_resource_guard(authorization, *_matrix())
    result = prepare_e1_confirmation_same_session_preflight(
        binding, chain, release, authorization, guard
    )
    return result


class E1ConfirmationSameSessionPreflightTests(unittest.TestCase):
    def test_preflight_opens_only_immediate_one_shot_gate(self) -> None:
        result = _preflight()

        self.assertEqual("READY_FOR_IMMEDIATE_ONE_SHOT", result.preflight_status)
        self.assertTrue(result.canonical_execution_permitted)
        self.assertTrue(result.canonical_persistence_permitted)
        self.assertFalse(result.claims_permitted)
        require_fresh_e1_confirmation_preflight(result)

    def test_preflight_binds_authorization_resources_and_step_count(self) -> None:
        result = _preflight()

        self.assertEqual(23_800, result.total_field_steps)
        self.assertEqual(1_800, result.max_wall_seconds)
        self.assertEqual(4 * 1024**3, result.max_peak_rss_bytes)
        self.assertTrue(result.one_shot_authorized)
        self.assertTrue(result.resource_enforcement_bound)
        self.assertTrue(result.no_retry_bound)

    def test_stale_preflight_fails_closed(self) -> None:
        result = copy.deepcopy(_preflight())
        object.__setattr__(
            result,
            "issued_monotonic_ns",
            result.issued_monotonic_ns - result.max_age_ns - 1,
        )

        with self.assertRaises(E1ConfirmationSameSessionPreflightError):
            require_fresh_e1_confirmation_preflight(result)

    def test_changed_process_identity_fails_closed(self) -> None:
        result = copy.deepcopy(_preflight())
        object.__setattr__(result, "process_id", result.process_id + 1)

        with self.assertRaises(E1ConfirmationSameSessionPreflightError):
            require_fresh_e1_confirmation_preflight(result)

    def test_preflight_is_ephemeral_and_targets_stay_free(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        first = _preflight()
        second = _preflight()

        self.assertNotEqual(first.preflight_digest, second.preflight_digest)
        self.assertEqual((False, False, False), before)
        self.assertEqual(before, tuple(path.exists() for path in TARGETS))

    def test_preflight_does_not_run_or_write(self) -> None:
        import inspect
        from mcm_field_organism.e1_confirmation_same_session_preflight import (
            prepare_e1_confirmation_same_session_preflight,
        )

        source = inspect.getsource(prepare_e1_confirmation_same_session_preflight)
        for forbidden in (
            "run_e1_asynchronous_field",
            "execute_e1_confirmation_canonical_once",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
