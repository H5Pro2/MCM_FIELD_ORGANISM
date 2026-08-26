from __future__ import annotations

import copy
import hashlib
import json
import pickle
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import numpy as np

import mcm_field_organism
from mcm_field_organism._previous_state_minimal_runner import (
    PreviousStateMinimalRunnerError,
)
from mcm_field_organism._runtime_fixation_adapters import (
    _FixationRuntimeContext,
    _boundary_digest,
    _build_fresh_context,
    _build_private_fixation_operations,
    _discard_context,
    _distribution_digest,
    _distribution_for_frame,
    _frame_for_contact,
    _generator_and_boundary_for_distribution,
    _generator_digest,
    _step_time_for_frame,
    _verify_bound_source_bytes,
)
from mcm_field_organism._runtime_fixation_structure import _FixationOperations
from mcm_field_organism.field_step_time import MCMFieldStepTime
from mcm_field_organism.receptor_contract import CommonFieldTime, ReceptorContactFrame
from mcm_field_organism.receptor_distributor import ReceptorDistribution


class RuntimeFixationAdapterTests(unittest.TestCase):
    def context(self, contact_id: str = "history.a.e1") -> _FixationRuntimeContext:
        return _FixationRuntimeContext(
            field=object(),
            distributor=Mock(),
            substrate_config=object(),
            contact_id=contact_id,
            pass_index=1,
        )

    def test_factory_binds_exactly_ten_private_roles_without_arguments(self) -> None:
        operations = _build_private_fixation_operations()
        self.assertIsInstance(operations, _FixationOperations)
        self.assertEqual(len(_FixationOperations.__dataclass_fields__), 10)
        self.assertEqual(_build_private_fixation_operations.__defaults__, None)
        expected_roles = {
            "verify_bound_source_bytes": _verify_bound_source_bytes,
            "build_fresh_context": _build_fresh_context,
            "frame_for_contact": _frame_for_contact,
            "distribution_for_frame": _distribution_for_frame,
            "distribution_digest": _distribution_digest,
            "step_time_for_frame": _step_time_for_frame,
            "generator_and_boundary": _generator_and_boundary_for_distribution,
            "generator_digest": _generator_digest,
            "boundary_digest": _boundary_digest,
            "discard_context": _discard_context,
        }
        for role, callback in expected_roles.items():
            self.assertIs(getattr(operations, role), callback)

    def test_bound_source_verification_uses_raw_bytes_and_rejects_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "source.py"
            target.write_bytes(b"fixed bytes")
            digest = hashlib.sha256(b"fixed bytes").hexdigest()
            with patch(
                "mcm_field_organism._runtime_fixation_adapters._PROJECT_ROOT",
                root,
            ):
                _verify_bound_source_bytes((("source.py", digest),))
                with self.assertRaisesRegex(
                    PreviousStateMinimalRunnerError,
                    "bound source verification failed",
                ):
                    _verify_bound_source_bytes((("source.py", "0" * 64),))

    def test_context_construction_uses_isolated_primitives(self) -> None:
        field = object()
        distributor = Mock()
        substrate = object()
        with (
            patch(
                "mcm_field_organism._runtime_fixation_adapters.build_shared_mcm_field",
                return_value=field,
            ) as build_field,
            patch(
                "mcm_field_organism._runtime_fixation_adapters.ReceptorDistributor",
                return_value=distributor,
            ),
            patch(
                "mcm_field_organism._runtime_fixation_adapters.NeutralLocalFieldSubstrateConfig",
                return_value=substrate,
            ),
        ):
            context = _build_fresh_context("history.a.e1", 1)
        self.assertIs(context.field, field)
        self.assertIs(context.distributor, distributor)
        self.assertIs(context.substrate_config, substrate)
        self.assertEqual(build_field.call_count, 1)
        self.assertEqual(distributor.attach.call_count, 1)

    def test_fourteen_context_builds_have_fresh_owned_identities(self) -> None:
        contexts = []
        with (
            patch(
                "mcm_field_organism._runtime_fixation_adapters.build_shared_mcm_field",
                side_effect=lambda **kwargs: object(),
            ),
            patch(
                "mcm_field_organism._runtime_fixation_adapters.ReceptorDistributor",
                side_effect=lambda: Mock(),
            ),
            patch(
                "mcm_field_organism._runtime_fixation_adapters.NeutralLocalFieldSubstrateConfig",
                side_effect=lambda value: object(),
            ),
        ):
            contacts = (
                "history.a.e1", "history.a.e2", "history.a.e3",
                "history.b.e1", "history.b.e2", "history.b.e3", "contact.c.e1",
            )
            contexts = [
                _build_fresh_context(contact, pass_index)
                for pass_index in (1, 2)
                for contact in contacts
            ]
        for attribute in ("field", "distributor", "substrate_config", "owner_token"):
            self.assertEqual(len({id(getattr(item, attribute)) for item in contexts}), 14)

    def test_unknown_contact_and_pass_are_rejected(self) -> None:
        for contact_id, pass_index in (("unknown", 1), ("history.a.e1", 3)):
            with self.assertRaises(PreviousStateMinimalRunnerError):
                _build_fresh_context(contact_id, pass_index)

    def test_frame_is_position_preserving(self) -> None:
        frame = _frame_for_contact("history.a.e1")
        self.assertEqual(frame.snapshot_id, "history.a.e1")
        self.assertEqual(frame.carrier_ids, ("carrier.0", "carrier.1", "carrier.2"))
        self.assertEqual(frame.values, (0.75, 0.0, 0.0))
        self.assertEqual((frame.window_start_tick, frame.window_end_tick), (0, 10))

    def test_distribution_calls_owned_distributor_once(self) -> None:
        frame = _frame_for_contact("history.a.e1")
        distribution = object()
        context = self.context()
        context.distributor.distribute.return_value = distribution
        result = _distribution_for_frame(context, frame)
        self.assertIs(result, distribution)
        self.assertEqual(context.distributor.distribute.call_count, 1)
        args = context.distributor.distribute.call_args.args
        self.assertEqual(args[0], (frame,))
        self.assertEqual(args[1].clock_id, "organism.minimal.v1")

    def test_distribution_digest_matches_canonical_distribution_payload(self) -> None:
        distribution = ReceptorDistribution(
            CommonFieldTime("organism.minimal.v1", 0, 10),
            (),
        )
        payload = {
            "contacts": [],
            "field_time": {
                "clock_id": "organism.minimal.v1",
                "window_end_tick": 10,
                "window_start_tick": 0,
            },
        }
        encoded = json.dumps(
            payload,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self.assertEqual(
            _distribution_digest(distribution),
            hashlib.sha256(encoded).hexdigest(),
        )

    def test_distribution_digest_failures_are_sanitized(self) -> None:
        secret = "synthetic-distribution-partial-value"
        distribution = ReceptorDistribution(
            CommonFieldTime("organism.minimal.v1", 0, 10),
            (),
        )
        cases = (
            (object(), None),
            (distribution, secret),
            (distribution, RuntimeError(secret)),
        )
        for value, outcome in cases:
            with self.subTest(outcome=type(outcome).__name__):
                if isinstance(outcome, BaseException):
                    digest_patch = patch.object(
                        ReceptorDistribution,
                        "digest",
                        side_effect=outcome,
                    )
                elif outcome is not None:
                    digest_patch = patch.object(
                        ReceptorDistribution,
                        "digest",
                        return_value=outcome,
                    )
                else:
                    digest_patch = patch.object(
                        ReceptorDistribution,
                        "digest",
                        wraps=ReceptorDistribution.digest,
                    )
                with digest_patch:
                    with self.assertRaises(
                        PreviousStateMinimalRunnerError
                    ) as caught:
                        _distribution_digest(value)
                self.assertNotIn(secret, str(caught.exception))

    def test_step_time_preserves_frame_interval(self) -> None:
        frame = _frame_for_contact("history.a.e2")
        step = _step_time_for_frame(frame)
        self.assertEqual((step.start_tick, step.end_tick), (10, 20))
        self.assertEqual(step.clock_id, "organism.minimal.v1")
        self.assertEqual(step.ticks_per_second, 10.0)

    def test_generator_boundary_uses_primitive_once_without_advancing(self) -> None:
        context = self.context()
        field_time = CommonFieldTime("organism.minimal.v1", 0, 10)
        distribution = ReceptorDistribution(field_time, ())
        step = MCMFieldStepTime("organism.minimal.v1", 0, 10, 10.0)
        expected = (np.eye(2), np.ones(2))
        with patch(
            "mcm_field_organism._runtime_fixation_adapters._generator_and_boundary",
            return_value=expected,
        ) as primitive:
            result = _generator_and_boundary_for_distribution(
                context, distribution, step
            )
        self.assertIs(result, expected)
        primitive.assert_called_once_with(
            context.field, distribution, context.substrate_config
        )

    def test_generator_and_boundary_digests_use_canonical_float_lists(self) -> None:
        generator = np.array([[1.0, -2.0], [3.5, 0.0]], dtype=np.float32)
        boundary = np.array([0.25, -0.5], dtype=np.float64)
        canonical = lambda value: json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        self.assertEqual(
            _generator_digest(generator),
            hashlib.sha256(canonical([[1.0, -2.0], [3.5, 0.0]])).hexdigest(),
        )
        self.assertEqual(
            _boundary_digest(boundary),
            hashlib.sha256(canonical([0.25, -0.5])).hexdigest(),
        )

    def test_invalid_array_shapes_and_nonfinite_values_are_rejected(self) -> None:
        for callback, value in (
            (_generator_digest, np.ones(2)),
            (_generator_digest, np.ones((2, 3))),
            (_boundary_digest, np.ones((1, 2))),
            (_boundary_digest, np.array([np.inf])),
        ):
            with self.assertRaises(PreviousStateMinimalRunnerError):
                callback(value)

    def test_discard_removes_references_and_rejects_reuse(self) -> None:
        context = self.context()
        with self.assertRaises(AttributeError):
            context.discarded = True
        _discard_context(context)
        self.assertTrue(context.discarded)
        self.assertIsNone(context._field)
        self.assertIsNone(context._distributor)
        self.assertIsNone(context._substrate_config)
        for accessor in (
            lambda: context.field,
            lambda: context.distributor,
            lambda: context.substrate_config,
            lambda: _discard_context(context),
        ):
            with self.assertRaises(PreviousStateMinimalRunnerError):
                accessor()

    def test_context_is_not_copyable_hashable_or_serializable(self) -> None:
        context = self.context()
        with self.assertRaises(PreviousStateMinimalRunnerError):
            copy.copy(context)
        with self.assertRaises(PreviousStateMinimalRunnerError):
            copy.deepcopy(context)
        with self.assertRaises(TypeError):
            hash(context)
        with self.assertRaises(PreviousStateMinimalRunnerError):
            pickle.dumps(context)

    def test_failures_are_sanitized(self) -> None:
        secret = "synthetic-partial-value"
        context = self.context()
        context.distributor.distribute.side_effect = RuntimeError(secret)
        with self.assertRaises(PreviousStateMinimalRunnerError) as caught:
            _distribution_for_frame(context, _frame_for_contact("history.a.e1"))
        self.assertNotIn(secret, str(caught.exception))

    def test_adapters_are_not_publicly_exported(self) -> None:
        self.assertFalse(hasattr(mcm_field_organism, "FixationRuntimeContext"))
        self.assertFalse(hasattr(mcm_field_organism, "build_private_fixation_operations"))


if __name__ == "__main__":
    unittest.main()
