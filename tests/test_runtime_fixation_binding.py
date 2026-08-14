from __future__ import annotations

import ast
import copy
import inspect
from pathlib import Path
import pickle
import unittest
from unittest.mock import patch

import mcm_field_organism
import mcm_field_organism._runtime_fixation_binding as binding_module
from mcm_field_organism._previous_state_minimal_runner import (
    PreviousStateMinimalRunnerError,
)
from mcm_field_organism._runtime_fixation_binding import (
    _PrivateFixationBinding,
    _build_private_fixation_binding,
)
from mcm_field_organism._runtime_fixation_structure import (
    _FixationOperations,
    _LockedFixationStructure,
)


class RuntimeFixationBindingTests(unittest.TestCase):
    def typed_doubles(self) -> tuple[_LockedFixationStructure, _FixationOperations]:
        return (
            object.__new__(_LockedFixationStructure),
            object.__new__(_FixationOperations),
        )

    def build_with_doubles(
        self,
    ) -> tuple[_PrivateFixationBinding, list[str]]:
        structure, operations = self.typed_doubles()
        calls: list[str] = []

        def build_structure() -> _LockedFixationStructure:
            calls.append("structure")
            return structure

        def build_operations() -> _FixationOperations:
            calls.append("operations")
            return operations

        with (
            patch.object(
                binding_module,
                "build_locked_runtime_fixation_structure",
                side_effect=build_structure,
            ) as structure_factory,
            patch.object(
                binding_module,
                "_build_private_fixation_operations",
                side_effect=build_operations,
            ) as operations_factory,
        ):
            binding = _build_private_fixation_binding()

        structure_factory.assert_called_once_with()
        operations_factory.assert_called_once_with()
        self.assertIs(binding.structure, structure)
        self.assertIs(binding.operations, operations)
        return binding, calls

    def test_module_defines_only_approved_private_symbols(self) -> None:
        tree = ast.parse(Path(binding_module.__file__).read_text(encoding="utf-8"))
        definitions = {
            node.name
            for node in tree.body
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        }
        self.assertEqual(
            definitions,
            {"_PrivateFixationBinding", "_build_private_fixation_binding"},
        )

    def test_factory_is_parameterless_and_calls_doubles_in_order(self) -> None:
        signature = inspect.signature(_build_private_fixation_binding)
        self.assertEqual(tuple(signature.parameters), ())
        self.assertIsNone(_build_private_fixation_binding.__defaults__)
        _, calls = self.build_with_doubles()
        self.assertEqual(calls, ["structure", "operations"])

    def test_binding_preserves_identity_and_is_immutable(self) -> None:
        binding, _ = self.build_with_doubles()
        for name, value in (("structure", object()), ("operations", object())):
            with self.assertRaises(PreviousStateMinimalRunnerError):
                setattr(binding, name, value)

    def test_binding_rejects_copy_hash_and_serialization(self) -> None:
        binding, _ = self.build_with_doubles()
        with self.assertRaises(PreviousStateMinimalRunnerError):
            copy.copy(binding)
        with self.assertRaises(PreviousStateMinimalRunnerError):
            copy.deepcopy(binding)
        with self.assertRaises(TypeError):
            hash(binding)
        with self.assertRaises(PreviousStateMinimalRunnerError):
            pickle.dumps(binding)

    def test_foreign_types_fail_without_partial_binding(self) -> None:
        structure, operations = self.typed_doubles()
        for structure_value, operations_value in (
            (object(), operations),
            (structure, object()),
        ):
            with self.subTest(
                structure_type=type(structure_value).__name__,
                operations_type=type(operations_value).__name__,
            ):
                with (
                    patch.object(
                        binding_module,
                        "build_locked_runtime_fixation_structure",
                        return_value=structure_value,
                    ),
                    patch.object(
                        binding_module,
                        "_build_private_fixation_operations",
                        return_value=operations_value,
                    ),
                ):
                    with self.assertRaisesRegex(
                        PreviousStateMinimalRunnerError,
                        "private fixation binding construction failed",
                    ):
                        _build_private_fixation_binding()

    def test_factory_failures_are_sanitized(self) -> None:
        secret = "synthetic-binding-partial-value"
        structure, operations = self.typed_doubles()
        for failing_role, exception in (
            ("structure", RuntimeError(secret)),
            ("structure", PreviousStateMinimalRunnerError(secret)),
            ("operations", RuntimeError(secret)),
            ("operations", PreviousStateMinimalRunnerError(secret)),
        ):
            with self.subTest(failing_role=failing_role, error=type(exception).__name__):
                structure_result = exception if failing_role == "structure" else structure
                operations_result = exception if failing_role == "operations" else operations
                with (
                    patch.object(
                        binding_module,
                        "build_locked_runtime_fixation_structure",
                        side_effect=structure_result
                        if isinstance(structure_result, BaseException)
                        else None,
                        return_value=None
                        if isinstance(structure_result, BaseException)
                        else structure_result,
                    ),
                    patch.object(
                        binding_module,
                        "_build_private_fixation_operations",
                        side_effect=operations_result
                        if isinstance(operations_result, BaseException)
                        else None,
                        return_value=None
                        if isinstance(operations_result, BaseException)
                        else operations_result,
                    ),
                ):
                    with self.assertRaises(PreviousStateMinimalRunnerError) as caught:
                        _build_private_fixation_binding()
                self.assertEqual(
                    str(caught.exception),
                    "private fixation binding construction failed",
                )
                self.assertNotIn(secret, str(caught.exception))

    def test_module_has_no_import_side_effect_or_forbidden_resolution(self) -> None:
        tree = ast.parse(Path(binding_module.__file__).read_text(encoding="utf-8"))
        top_level_calls = [
            node
            for statement in tree.body
            if not isinstance(
                statement,
                (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef),
            )
            for node in ast.walk(statement)
            if isinstance(node, ast.Call)
        ]
        self.assertEqual(top_level_calls, [])

        forbidden_names = {
            "_orchestrate_runtime_fixation_with_operations",
            "_derive_contact_with_operations",
            "execute_runtime_fixation",
            "importlib",
            "__import__",
            "getattr",
        }
        imported_or_called = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        } | {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertTrue(forbidden_names.isdisjoint(imported_or_called))

    def test_binding_symbols_are_not_publicly_exported(self) -> None:
        self.assertFalse(hasattr(mcm_field_organism, "PrivateFixationBinding"))
        self.assertFalse(hasattr(mcm_field_organism, "build_private_fixation_binding"))


if __name__ == "__main__":
    unittest.main()
