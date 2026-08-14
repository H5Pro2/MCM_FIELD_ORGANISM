from __future__ import annotations

from dataclasses import replace
import unittest

import mcm_field_organism
from mcm_field_organism._previous_state_minimal_runner import (
    PreviousStateMinimalRunnerError,
)
from mcm_field_organism._runtime_fixation_structure import (
    _FixationOperations,
    _orchestrate_runtime_fixation_with_operations,
    build_locked_runtime_fixation_structure,
    execute_runtime_fixation,
)


class _RecordingOperations:
    def __init__(self) -> None:
        self.calls: list[tuple[object, ...]] = []
        self.contexts: list[object] = []
        self.discarded: list[object] = []
        self.reuse_context = False
        self.mismatch_second_pass = False
        self.fail_source_verification = False
        self.fail_role: str | None = None
        self.fail_with_runner_error = False
        self.fail_discard = False
        self.secret = "synthetic-partial-digest"

    def operations(self) -> _FixationOperations:
        return _FixationOperations(
            verify_bound_source_bytes=self.verify_bound_source_bytes,
            build_fresh_context=self.build_fresh_context,
            frame_for_contact=self.frame_for_contact,
            distribution_for_frame=self.distribution_for_frame,
            distribution_digest=self.distribution_digest,
            step_time_for_frame=self.step_time_for_frame,
            generator_and_boundary=self.generator_and_boundary,
            generator_digest=self.generator_digest,
            boundary_digest=self.boundary_digest,
            discard_context=self.discard_context,
        )

    def _record(self, role: str, *values: object) -> None:
        self.calls.append((role, *values))
        if self.fail_role == role:
            if self.fail_with_runner_error:
                raise PreviousStateMinimalRunnerError(self.secret)
            raise RuntimeError(self.secret)

    def verify_bound_source_bytes(self, source_digests: object) -> None:
        self._record("verify_bound_source_bytes", source_digests)
        if self.fail_source_verification:
            raise RuntimeError(self.secret)

    def build_fresh_context(self, contact_id: str, pass_index: int) -> object:
        self._record("build_fresh_context", contact_id, pass_index)
        if self.reuse_context and self.contexts:
            return self.contexts[0]
        context = {"contact_id": contact_id, "pass_index": pass_index}
        self.contexts.append(context)
        return context

    def frame_for_contact(self, contact_id: str) -> object:
        self._record("frame_for_contact", contact_id)
        return ("frame", contact_id)

    def distribution_for_frame(self, context: object, frame: object) -> object:
        self._record("distribution_for_frame", context, frame)
        return ("distribution", context, frame)

    def distribution_digest(self, distribution: object) -> str:
        self._record("distribution_digest", distribution)
        return "1" * 64

    def step_time_for_frame(self, frame: object) -> object:
        self._record("step_time_for_frame", frame)
        return ("step-time", frame)

    def generator_and_boundary(
        self, context: object, distribution: object, step_time: object
    ) -> tuple[object, object]:
        self._record("generator_and_boundary", context, distribution, step_time)
        return (("generator", context), ("boundary", context))

    def generator_digest(self, generator: object) -> str:
        self._record("generator_digest", generator)
        context = generator[1]  # type: ignore[index]
        if self.mismatch_second_pass and context["pass_index"] == 2:
            return "3" * 64
        return "2" * 64

    def boundary_digest(self, boundary: object) -> str:
        self._record("boundary_digest", boundary)
        return "3" * 64

    def discard_context(self, context: object) -> None:
        self._record("discard_context", context)
        if self.fail_discard:
            raise RuntimeError(self.secret)
        self.discarded.append(context)


class RuntimeFixationStructureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.structure = build_locked_runtime_fixation_structure()

    def test_fixed_contacts_sources_and_twenty_one_slots(self) -> None:
        self.assertEqual(
            self.structure.contact_ids,
            (
                "history.a.e1",
                "history.a.e2",
                "history.a.e3",
                "history.b.e1",
                "history.b.e2",
                "history.b.e3",
                "contact.c.e1",
            ),
        )
        self.assertEqual(len(self.structure.source_digests), 8)
        for derivation in self.structure.passes:
            self.assertEqual(len(derivation.slots), 7)
            self.assertEqual(
                sum(
                    value is None
                    for slot in derivation.slots
                    for value in (
                        slot.receptor_distribution_digest,
                        slot.generator_digest,
                        slot.boundary_digest,
                    )
                ),
                21,
            )

    def test_two_passes_use_fourteen_fresh_context_tokens(self) -> None:
        self.assertEqual(tuple(item.pass_index for item in self.structure.passes), (1, 2))
        tokens = tuple(
            token for item in self.structure.passes for token in item.context_tokens
        )
        self.assertEqual(len(tokens), 14)
        self.assertEqual(len({id(token) for token in tokens}), 14)

    def test_bundle_shape_and_abort_boundaries_are_fixed(self) -> None:
        shape = self.structure.bundle_shape
        self.assertEqual(shape.schema_version, 1)
        self.assertEqual(shape.entry_count, 7)
        self.assertEqual(shape.source_digest_count, 8)
        self.assertEqual(len(self.structure.abort_boundaries), 12)

    def test_all_release_flags_are_false(self) -> None:
        flags = tuple(
            getattr(self.structure, name)
            for name in self.structure.__dataclass_fields__
            if name.endswith("_released")
        )
        self.assertEqual(len(flags), 12)
        self.assertFalse(any(flags))

    def test_forbidden_roles_are_explicit_and_entry_point_aborts(self) -> None:
        self.assertEqual(
            self.structure.forbidden_roles,
            (
                "effect_measurement",
                "field_advance",
                "hook_execution",
                "integration",
                "snapshot",
            ),
        )
        with self.assertRaisesRegex(
            PreviousStateMinimalRunnerError, "runtime fixation is not released"
        ):
            execute_runtime_fixation(self.structure)

    def test_contact_source_slot_bundle_and_lock_mutations_are_rejected(self) -> None:
        with self.assertRaises(PreviousStateMinimalRunnerError):
            replace(self.structure, contact_ids=tuple(reversed(self.structure.contact_ids)))
        with self.assertRaises(PreviousStateMinimalRunnerError):
            replace(self.structure, source_digests=self.structure.source_digests[:-1])
        first_pass = self.structure.passes[0]
        first_slot = first_pass.slots[0]
        with self.assertRaises(PreviousStateMinimalRunnerError):
            replace(first_slot, generator_digest="0" * 64)
        with self.assertRaises(PreviousStateMinimalRunnerError):
            replace(self.structure.bundle_shape, entry_count=6)
        with self.assertRaisesRegex(
            PreviousStateMinimalRunnerError, "forbidden fixation roles changed"
        ):
            replace(self.structure, forbidden_roles=self.structure.forbidden_roles[:-1])
        with self.assertRaisesRegex(
            PreviousStateMinimalRunnerError, "fixation abort boundaries changed"
        ):
            replace(
                self.structure,
                abort_boundaries=self.structure.abort_boundaries[:-1],
            )
        with self.assertRaises(PreviousStateMinimalRunnerError):
            replace(self.structure, fixation_execution_released=True)

    def test_structure_helpers_are_not_publicly_exported(self) -> None:
        self.assertFalse(hasattr(mcm_field_organism, "build_locked_runtime_fixation_structure"))
        self.assertFalse(hasattr(mcm_field_organism, "execute_runtime_fixation"))


class RuntimeFixationOrchestrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.structure = build_locked_runtime_fixation_structure()
        self.recorder = _RecordingOperations()

    def run_orchestration(self):
        return _orchestrate_runtime_fixation_with_operations(
            self.structure, self.recorder.operations()
        )

    def test_two_passes_form_only_one_complete_immutable_bundle(self) -> None:
        bundle = self.run_orchestration()

        self.assertEqual(len(bundle.entries), 7)
        self.assertEqual(
            tuple(entry.contact_id for entry in bundle.entries),
            self.structure.contact_ids,
        )
        self.assertEqual(bundle.source_digests, self.structure.source_digests)
        self.assertEqual(bundle.static_contract, self.structure.static_contract)
        self.assertEqual(len(self.recorder.contexts), 14)
        self.assertEqual(len({id(context) for context in self.recorder.contexts}), 14)
        self.assertEqual(self.recorder.discarded, self.recorder.contexts)
        with self.assertRaises((AttributeError, TypeError)):
            bundle.entries = ()  # type: ignore[misc]

    def test_operation_order_and_counts_are_exact(self) -> None:
        self.run_orchestration()

        roles = [call[0] for call in self.recorder.calls]
        self.assertEqual(roles[0], "verify_bound_source_bytes")
        per_contact = (
            "build_fresh_context",
            "frame_for_contact",
            "distribution_for_frame",
            "distribution_digest",
            "step_time_for_frame",
            "generator_and_boundary",
            "generator_digest",
            "boundary_digest",
            "discard_context",
        )
        self.assertEqual(roles[1:], list(per_contact) * 14)

    def test_operation_surface_rejects_extra_and_noncallable_roles(self) -> None:
        kwargs = {
            name: (lambda *args: None)
            for name in _FixationOperations.__dataclass_fields__
        }
        with self.assertRaises(TypeError):
            _FixationOperations(**kwargs, integration=lambda: None)  # type: ignore[call-arg]
        kwargs["snapshot"] = None
        kwargs["discard_context"] = None
        with self.assertRaisesRegex(
            PreviousStateMinimalRunnerError, "fixation operations must be callable"
        ):
            _FixationOperations(**{key: kwargs[key] for key in _FixationOperations.__dataclass_fields__})  # type: ignore[arg-type]

    def test_context_reuse_is_rejected_after_one_discard(self) -> None:
        self.recorder.reuse_context = True
        with self.assertRaisesRegex(
            PreviousStateMinimalRunnerError, "fixation context reused"
        ):
            self.run_orchestration()
        self.assertEqual(
            sum(context is self.recorder.contexts[0] for context in self.recorder.discarded),
            2,
        )

    def test_double_derivation_mismatch_returns_no_partial_bundle(self) -> None:
        self.recorder.mismatch_second_pass = True
        with self.assertRaisesRegex(
            PreviousStateMinimalRunnerError, "double derivation mismatch"
        ) as caught:
            self.run_orchestration()
        self.assertNotIn(self.recorder.secret, str(caught.exception))
        self.assertEqual(len(self.recorder.discarded), 14)

    def test_callback_failure_is_sanitized_and_context_is_discarded(self) -> None:
        self.recorder.fail_role = "generator_digest"
        with self.assertRaises(PreviousStateMinimalRunnerError) as caught:
            self.run_orchestration()
        self.assertNotIn(self.recorder.secret, str(caught.exception))
        self.assertEqual(len(self.recorder.discarded), 1)

    def test_runner_error_from_callback_is_sanitized_and_context_is_discarded(self) -> None:
        self.recorder.fail_role = "generator_digest"
        self.recorder.fail_with_runner_error = True
        with self.assertRaises(PreviousStateMinimalRunnerError) as caught:
            bundle = self.run_orchestration()
        self.assertNotIn(self.recorder.secret, str(caught.exception))
        self.assertEqual(len(self.recorder.discarded), 1)
        self.assertNotIn("bundle", locals())

    def test_discard_failure_aborts_without_partial_values(self) -> None:
        self.recorder.fail_discard = True
        with self.assertRaisesRegex(
            PreviousStateMinimalRunnerError, "context discard failed"
        ) as caught:
            self.run_orchestration()
        self.assertNotIn(self.recorder.secret, str(caught.exception))

    def test_source_verification_failure_precedes_context_construction(self) -> None:
        self.recorder.fail_source_verification = True
        with self.assertRaisesRegex(
            PreviousStateMinimalRunnerError, "bound source verification failed"
        ) as caught:
            self.run_orchestration()
        self.assertNotIn(self.recorder.secret, str(caught.exception))
        self.assertEqual(self.recorder.contexts, [])

    def test_invalid_digest_and_generator_boundary_shape_are_rejected(self) -> None:
        self.recorder.distribution_digest = lambda distribution: "not-a-digest"  # type: ignore[method-assign]
        with self.assertRaisesRegex(
            PreviousStateMinimalRunnerError, "invalid fixation digest"
        ):
            self.run_orchestration()

        recorder = _RecordingOperations()
        recorder.generator_and_boundary = lambda *args: ("generator",)  # type: ignore[method-assign,assignment]
        with self.assertRaisesRegex(
            PreviousStateMinimalRunnerError, "generator boundary pair invalid"
        ):
            _orchestrate_runtime_fixation_with_operations(
                self.structure, recorder.operations()
            )

    def test_contact_order_partial_bundle_and_active_lock_are_rejected(self) -> None:
        with self.assertRaises(PreviousStateMinimalRunnerError):
            replace(self.structure, contact_ids=self.structure.contact_ids[:-1])
        with self.assertRaises(PreviousStateMinimalRunnerError):
            replace(self.structure, runner_execution_released=True)

    def test_standard_entry_remains_locked(self) -> None:
        with self.assertRaisesRegex(
            PreviousStateMinimalRunnerError, "runtime fixation is not released"
        ):
            execute_runtime_fixation(self.structure)


if __name__ == "__main__":
    unittest.main()
