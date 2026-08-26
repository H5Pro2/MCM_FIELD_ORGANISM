from __future__ import annotations

import ast
import inspect
from pathlib import Path
import unittest
from unittest.mock import patch

import mcm_field_organism._runtime_fixation_handoff as handoff_module
from mcm_field_organism._previous_state_minimal_runner import (
    PreviousStateMinimalRunnerError,
)
from mcm_field_organism._runtime_fixation_binding import _PrivateFixationBinding
from mcm_field_organism._runtime_fixation_handoff import (
    _execute_private_runtime_fixation,
)
from mcm_field_organism._runtime_fixation_structure import (
    _FixedDigestBundle,
    _FixationOperations,
    _LockedFixationStructure,
)


class PrivateRuntimeFixationHandoffTests(unittest.TestCase):
    @staticmethod
    def _binding() -> tuple[
        _PrivateFixationBinding,
        _LockedFixationStructure,
        _FixationOperations,
    ]:
        structure = object.__new__(_LockedFixationStructure)
        operations = object.__new__(_FixationOperations)
        binding = _PrivateFixationBinding(
            structure=structure,
            operations=operations,
        )
        return binding, structure, operations

    def test_module_defines_exactly_one_private_production_symbol(self) -> None:
        own_symbols = {
            name
            for name, value in vars(handoff_module).items()
            if getattr(value, "__module__", None) == handoff_module.__name__
            and not name.startswith("__")
        }
        self.assertEqual(own_symbols, {"_execute_private_runtime_fixation"})

    def test_signature_requires_exactly_one_binding(self) -> None:
        signature = inspect.signature(_execute_private_runtime_fixation)
        self.assertEqual(tuple(signature.parameters), ("binding",))
        parameter = signature.parameters["binding"]
        self.assertIs(parameter.default, inspect.Parameter.empty)
        self.assertEqual(parameter.kind, inspect.Parameter.POSITIONAL_OR_KEYWORD)

    def test_calls_testdouble_once_with_bound_object_identity(self) -> None:
        binding, structure, operations = self._binding()
        result = object.__new__(_FixedDigestBundle)
        calls: list[tuple[object, object]] = []

        def coordinator_double(
            received_structure: object,
            received_operations: object,
        ) -> _FixedDigestBundle:
            calls.append((received_structure, received_operations))
            return result

        with patch.object(
            handoff_module,
            "_coordinate_runtime_fixation_with_operations",
            coordinator_double,
        ):
            actual = _execute_private_runtime_fixation(binding)

        self.assertIs(actual, result)
        self.assertEqual(len(calls), 1)
        self.assertIs(calls[0][0], structure)
        self.assertIs(calls[0][1], operations)

    def test_rejects_foreign_binding_before_coordinator(self) -> None:
        calls = 0

        def forbidden_double(*args: object) -> _FixedDigestBundle:
            nonlocal calls
            calls += 1
            return object.__new__(_FixedDigestBundle)

        with patch.object(
            handoff_module,
            "_coordinate_runtime_fixation_with_operations",
            forbidden_double,
        ):
            with self.assertRaisesRegex(
                PreviousStateMinimalRunnerError,
                "^private runtime fixation execution failed$",
            ):
                _execute_private_runtime_fixation(object())  # type: ignore[arg-type]

        self.assertEqual(calls, 0)

    def test_sanitizes_coordinator_exception(self) -> None:
        binding, _, _ = self._binding()
        secret = "foreign-coordinator-secret"

        def failing_double(*args: object) -> _FixedDigestBundle:
            raise RuntimeError(secret)

        with patch.object(
            handoff_module,
            "_coordinate_runtime_fixation_with_operations",
            failing_double,
        ):
            with self.assertRaises(PreviousStateMinimalRunnerError) as caught:
                _execute_private_runtime_fixation(binding)

        self.assertEqual(
            str(caught.exception),
            "private runtime fixation execution failed",
        )
        self.assertNotIn(secret, str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)

    def test_rejects_foreign_result_without_disclosure(self) -> None:
        binding, _, _ = self._binding()
        secret = "foreign-result-secret"

        class ForeignResult:
            def __repr__(self) -> str:
                return secret

        with patch.object(
            handoff_module,
            "_coordinate_runtime_fixation_with_operations",
            return_value=ForeignResult(),
        ):
            with self.assertRaises(PreviousStateMinimalRunnerError) as caught:
                _execute_private_runtime_fixation(binding)

        self.assertEqual(
            str(caught.exception),
            "private runtime fixation execution failed",
        )
        self.assertNotIn(secret, str(caught.exception))

    def test_source_has_only_static_allowed_dependencies_and_no_top_level_call(self) -> None:
        source_path = Path(handoff_module.__file__)
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        imported_names = {
            alias.name
            for node in tree.body
            if isinstance(node, ast.ImportFrom)
            for alias in node.names
        }
        self.assertEqual(
            imported_names,
            {
                "annotations",
                "PreviousStateMinimalRunnerError",
                "_PrivateFixationBinding",
                "_FixedDigestBundle",
                "_coordinate_runtime_fixation_with_operations",
            },
        )
        self.assertFalse(
            any(isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) for node in tree.body)
        )
        forbidden_calls = {"getattr", "globals", "locals", "__import__", "eval", "exec"}
        self.assertFalse(
            any(
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id in forbidden_calls
                for node in ast.walk(tree)
            )
        )

    def test_package_does_not_export_handoff(self) -> None:
        package_init = Path(handoff_module.__file__).with_name("__init__.py")
        source = package_init.read_text(encoding="utf-8")
        self.assertNotIn("runtime_fixation_handoff", source)
        self.assertNotIn("_execute_private_runtime_fixation", source)


if __name__ == "__main__":
    unittest.main()
