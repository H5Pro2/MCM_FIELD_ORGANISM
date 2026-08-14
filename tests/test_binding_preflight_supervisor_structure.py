"""Static-only checks for the binding preflight supervisor source."""

from __future__ import annotations

import ast
from pathlib import Path


SOURCE_PATH = Path(__file__).parents[1] / "tools/binding_preflight_supervisor.py"
SOURCE = SOURCE_PATH.read_text(encoding="utf-8")
TREE = ast.parse(SOURCE, filename=str(SOURCE_PATH))


def _calls(name: str) -> list[ast.Call]:
    return [
        node for node in ast.walk(TREE)
        if isinstance(node, ast.Call)
        and ((isinstance(node.func, ast.Attribute) and node.func.attr == name)
             or (isinstance(node.func, ast.Name) and node.func.id == name))
    ]


def _assigned_literal(name: str):
    for node in TREE.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(target, ast.Name) and target.id == name for target in targets):
                value = node.value
                if isinstance(value, ast.Constant):
                    return value.value
    raise AssertionError(f"literal assignment missing: {name}")


def _function(name: str) -> ast.FunctionDef:
    for node in TREE.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"function missing: {name}")


def _class(name: str) -> ast.ClassDef:
    for node in TREE.body:
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    raise AssertionError(f"class missing: {name}")


def _except_handler(function: ast.FunctionDef) -> ast.ExceptHandler:
    handlers = [
        node for node in ast.walk(function)
        if isinstance(node, ast.ExceptHandler)
        and node.name == "primary_error"
    ]
    assert len(handlers) == 1
    return handlers[0]


def _direct_named_call(statement: ast.stmt, name: str) -> ast.Call | None:
    value = statement.value if isinstance(statement, (ast.Expr, ast.Assign)) else None
    if (
        isinstance(value, ast.Call)
        and isinstance(value.func, ast.Name)
        and value.func.id == name
    ):
        return value
    return None


def test_source_has_no_project_or_process_helper_imports() -> None:
    imports = {
        alias.name.split(".")[0]
        for node in TREE.body
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert "subprocess" not in imports
    assert "mcm_field_organism" not in imports
    assert not any(name.startswith("mcm_") for name in imports)
    assert "os" not in imports


def test_source_has_no_automatic_entrypoint_or_shell() -> None:
    assert '__name__ == "__main__"' not in SOURCE
    assert "shell=True" not in SOURCE
    assert not _calls("system")
    assert not _calls("Popen")


def test_required_windows_api_bindings_are_present() -> None:
    required = {
        "CreatePipe", "SetHandleInformation", "InitializeProcThreadAttributeList",
        "UpdateProcThreadAttribute", "DeleteProcThreadAttributeList", "CreateProcessW",
        "CreateJobObjectW", "SetInformationJobObject", "QueryInformationJobObject",
        "AssignProcessToJobObject", "ResumeThread", "WriteFile", "ReadFile",
        "WaitForSingleObject", "GetExitCodeProcess", "TerminateJobObject", "CloseHandle",
        "TerminateProcess", "GetCurrentProcessId", "GetCurrentProcess",
        "GetProcessHandleCount", "CreateToolhelp32Snapshot", "Thread32First",
        "Thread32Next",
    }
    assert required <= {node.attr for node in ast.walk(TREE) if isinstance(node, ast.Attribute)}
    assert "CreateProcessA" not in SOURCE


def test_single_write_and_resume_paths_are_syntactically_fixed() -> None:
    assert len(_calls("WriteFile")) == 1
    assert len(_calls("ResumeThread")) == 1
    assert "FlushFileBuffers" not in SOURCE
    assert "retry" not in SOURCE.lower()


def test_contract_literals_match_document_217() -> None:
    assert _assigned_literal("PAYLOAD_SIZE") == 1806
    assert _assigned_literal("PAYLOAD_SHA256") == "d86be4be95ed54ea461aea4c538639cec179726ccca30b14dd762a605351b393"
    assert _assigned_literal("STDOUT_LIMIT") == 4096
    assert _assigned_literal("STDERR_LIMIT") == 0
    assert _assigned_literal("WALL_TIME_SECONDS") == 60.0
    assert _assigned_literal("FINALIZATION_SECONDS") == 5.0
    assert _assigned_literal("PRE_JOB_ABORT_EXIT_CODE") == 1
    assert _assigned_literal("USER_CPU_100NS") == 300_000_000
    assert _assigned_literal("PROCESS_MEMORY_LIMIT") == 1_073_741_824
    assert _assigned_literal("JOB_MEMORY_LIMIT") == 1_073_741_824
    assert _assigned_literal("ACTIVE_PROCESS_LIMIT") == 1
    assert _assigned_literal("CHILD_PROCESS_LIMIT") == 0
    assert _assigned_literal("SUCCESS_EXIT_CODE") == 0


def test_payload_identity_and_encoding_checks_are_bound() -> None:
    required = ("sha256(payload)", "decode(\"ascii\")", "decode(\"utf-8\")", "payload.endswith(b\"\\n\")", "b\"\\r\" in payload", "payload.startswith")
    assert all(fragment in SOURCE for fragment in required)
    assert "normalization detected" in SOURCE


def test_absolute_process_identity_and_creation_flags_are_bound() -> None:
    assert r'C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace' in SOURCE
    assert ".venv/Scripts/python.exe" in SOURCE
    assert "create_unicode_buffer(COMMAND_LINE)" in SOURCE
    for flag in ("CREATE_SUSPENDED", "CREATE_NO_WINDOW", "EXTENDED_STARTUPINFO_PRESENT", "CREATE_UNICODE_ENVIRONMENT"):
        assert flag in SOURCE


def test_environment_and_three_handle_allowlist_are_fixed() -> None:
    assert '"SystemRoot=C:\\\\Windows", "WINDIR=C:\\\\Windows"' in SOURCE
    assert 'wintypes.HANDLE * 3' in SOURCE
    assert "PROC_THREAD_ATTRIBUTE_HANDLE_LIST" in SOURCE
    assert "STARTF_USESTDHANDLES" in SOURCE
    assert "CreateProcessW(APPLICATION_NAME, command_buffer, None, None, True" in SOURCE


def test_all_job_limits_and_values_are_bound() -> None:
    for flag in (
        "JOB_OBJECT_LIMIT_PROCESS_TIME", "JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE",
        "JOB_OBJECT_LIMIT_ACTIVE_PROCESS", "JOB_OBJECT_LIMIT_PROCESS_MEMORY",
        "JOB_OBJECT_LIMIT_JOB_MEMORY",
    ):
        assert flag in SOURCE
    assert "_configure_job(api, job)" in SOURCE
    assert "_job_active_processes(api, job)" in SOURCE


def test_stream_exit_and_json_contract_are_bound() -> None:
    assert "STDOUT_LIMIT + 1" in SOURCE
    assert "STDERR_LIMIT + 1" in SOURCE
    create_line = _calls("CreateProcessW")[0].lineno
    started_at = next(
        node for node in ast.walk(_function("execute_once"))
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "started_at" for target in node.targets)
    )
    assert create_line < started_at.lineno
    assert "success_deadline = started_at + WALL_TIME_SECONDS" in SOURCE
    assert "_finish_readers(readers, success_deadline)" in SOURCE
    assert "exit_code.value != SUCCESS_EXIT_CODE" in SOURCE
    for key in (
        "contract_digest", "effect_measurement_allowed", "execution_locked",
        "field_execution_allowed", "hook_execution_allowed",
    ):
        assert key in SOURCE
    assert "stdout.count(b\"\\n\") != 1" in SOURCE
    assert "object_pairs_hook" in SOURCE
    assert "len(keys) != len(set(keys))" in SOURCE


def test_workspace_manifest_has_no_dynamic_exclusions_or_writes() -> None:
    assert 'relative == ".git"' in SOURCE
    assert "relative path" not in SOURCE.lower()
    assert "st_mtime_ns" in SOURCE
    assert "path.is_dir()" in SOURCE
    assert "path.is_file()" in SOURCE
    forbidden_writes = ("write_text", "write_bytes", "open(\"w", "open(\"a")
    assert not any(fragment in SOURCE for fragment in forbidden_writes)


def test_blocked_artifact_classes_are_not_excluded_from_manifest() -> None:
    blocked_artifact_classes = (
        "__pycache__", ".pyc", ".pyo", "cache", "temp", "tmp", "log",
        "dump", "database", "state", "memory",
    )
    manifest = ast.get_source_segment(SOURCE, _function("_workspace_manifest"))
    assert manifest is not None
    assert 'relative == ".git"' in manifest
    assert all(token not in manifest for token in blocked_artifact_classes)


def test_external_activity_is_fail_closed_and_result_is_internal() -> None:
    assert "_verify_external_activity_absence()" in SOURCE
    assert "has no approved verifier" in SOURCE
    assert "@dataclass(frozen=True)\nclass ExecutionResult" in SOURCE
    assert "def execute_once()" in SOURCE


def test_pre_job_assignment_failure_terminates_suspended_process() -> None:
    execute = _function("execute_once")
    terminate_process_calls = [
        node for node in ast.walk(execute)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "TerminateProcess"
    ]
    assert len(terminate_process_calls) == 1
    call = terminate_process_calls[0]
    assert isinstance(call.args[1], ast.Name)
    assert call.args[1].id == "PRE_JOB_ABORT_EXIT_CODE"
    guarded = next(
        node for node in ast.walk(execute)
        if isinstance(node, ast.If)
        and isinstance(node.test, ast.Name)
        and node.test.id == "job_assigned"
    )
    assert call.lineno > guarded.lineno
    assert _calls("ResumeThread")[0].lineno < guarded.lineno
    assert len(_calls("TerminateJobObject")) == 1


def test_technical_observation_contract_is_structurally_bound() -> None:
    thread_entry = _class("THREADENTRY32")
    thread_source = ast.get_source_segment(SOURCE, thread_entry)
    assert thread_source is not None
    for field in (
        "dwSize", "cntUsage", "th32ThreadID", "th32OwnerProcessID",
        "tpBasePri", "tpDeltaPri", "dwFlags",
    ):
        assert field in thread_source
    assert _assigned_literal("TH32CS_SNAPTHREAD") == 0x00000004
    assert _assigned_literal("ERROR_NO_MORE_FILES") == 18
    observe = ast.get_source_segment(SOURCE, _function("_observe_supervisor"))
    assert observe is not None
    assert observe.index("CloseHandle(snapshot)") < observe.index("GetProcessHandleCount")
    assert "CloseHandle(process)" not in observe
    assert "ctypes.get_last_error()" in observe
    assert "TechnicalObservations(_observe_supervisor(api), None, None)" in SOURCE
    assert "observations.before,\n            _observe_supervisor(api)," in SOURCE
    assert "observations.during,\n            _observe_supervisor(api)," in SOURCE


def test_finalization_and_manifest_paths_are_structurally_bound() -> None:
    execute = _function("execute_once")
    handler = _except_handler(execute)
    process_started = next(
        node for node in handler.body
        if isinstance(node, ast.If)
        and isinstance(node.test, ast.Name)
        and node.test.id == "process_started"
    )
    deadline_assignments = [
        node for node in ast.walk(process_started)
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name)
            and target.id == "finalization_deadline"
            for target in node.targets
        )
    ]
    assert len(deadline_assignments) == 1
    deadline = deadline_assignments[0].value
    assert isinstance(deadline, ast.BinOp) and isinstance(deadline.op, ast.Add)
    assert isinstance(deadline.left, ast.Call)
    assert isinstance(deadline.left.func, ast.Attribute)
    assert deadline.left.func.attr == "monotonic"
    assert isinstance(deadline.right, ast.Name)
    assert deadline.right.id == "FINALIZATION_SECONDS"

    handler_names = {
        node.id for node in ast.walk(handler) if isinstance(node, ast.Name)
    }
    assert "success_deadline" not in handler_names

    not_ended = next(
        node for node in process_started.body
        if isinstance(node, ast.If)
        and isinstance(node.test, ast.UnaryOp)
        and isinstance(node.test.op, ast.Not)
        and isinstance(node.test.operand, ast.Name)
        and node.test.operand.id == "process_ended"
    )
    termination_attrs = {
        node.attr for node in ast.walk(not_ended)
        if isinstance(node, ast.Attribute)
    }
    assert {"TerminateProcess", "TerminateJobObject"} <= termination_attrs
    assert "terminated process end is unconfirmed" in ast.get_source_segment(
        SOURCE, not_ended
    )

    ended = next(
        node for node in process_started.body
        if isinstance(node, ast.If)
        and isinstance(node.test, ast.Name)
        and node.test.id == "process_ended"
    )
    direct_steps = [
        (index, statement, call)
        for index, statement in enumerate(ended.body)
        if (call := _direct_named_call(statement, "_run_finalization_step"))
        is not None
    ]
    assert len(direct_steps) == 5
    step_indices = [index for index, _, _ in direct_steps]
    start = step_indices[0]
    assert step_indices == [start, start + 1, start + 2, start + 3, start + 5]
    step_statements = [statement for _, statement, _ in direct_steps]
    assert [type(statement) for statement in step_statements] == [
        ast.Expr,
        ast.Expr,
        ast.Expr,
        ast.Assign,
        ast.Expr,
    ]

    expected_steps = [
        ("pipe closure", "_close_finalization_pipes", ["ledger"]),
        (
            "reader completion",
            "_finish_readers",
            ["readers", "finalization_deadline"],
        ),
        ("process resource closure", "_close_process_resources", ["ledger"]),
        ("after observation", "_after_observations", ["api", "observations"]),
        ("after manifest", "_verify_after_manifest", ["before"]),
    ]
    steps = [call for _, _, call in direct_steps]
    for call, (label, function_name, argument_names) in zip(
        steps, expected_steps, strict=True
    ):
        assert len(call.args) == 4
        assert call.keywords == []
        assert isinstance(call.args[0], ast.Constant)
        assert call.args[0].value == label
        assert isinstance(call.args[1], ast.Name)
        assert call.args[1].id == "finalization_deadline"
        assert isinstance(call.args[1].ctx, ast.Load)
        assert isinstance(call.args[2], ast.Name)
        assert call.args[2].id == "finalization_errors"
        assert isinstance(call.args[2].ctx, ast.Load)

        callback = call.args[3]
        assert isinstance(callback, ast.Lambda)
        assert callback.args.posonlyargs == []
        assert callback.args.args == []
        assert callback.args.kwonlyargs == []
        assert callback.args.vararg is None
        assert callback.args.kwarg is None
        assert callback.args.defaults == []
        assert callback.args.kw_defaults == []
        assert isinstance(callback.body, ast.Call)
        assert isinstance(callback.body.func, ast.Name)
        assert callback.body.func.id == function_name
        assert callback.body.keywords == []
        assert all(isinstance(argument, ast.Name) for argument in callback.body.args)
        assert [argument.id for argument in callback.body.args] == argument_names
        assert all(isinstance(argument.ctx, ast.Load) for argument in callback.body.args)

    observation_step = step_statements[3]
    assert isinstance(observation_step, ast.Assign)
    assert len(observation_step.targets) == 1
    observation_target = observation_step.targets[0]
    assert isinstance(observation_target, ast.Tuple)
    assert isinstance(observation_target.ctx, ast.Store)
    assert len(observation_target.elts) == 2
    assert all(isinstance(element, ast.Name) for element in observation_target.elts)
    assert [element.id for element in observation_target.elts] == [
        "after_value",
        "after_ok",
    ]
    assert all(isinstance(element.ctx, ast.Store) for element in observation_target.elts)

    observation_transfer = ended.body[start + 4]
    assert isinstance(observation_transfer, ast.If)
    assert isinstance(observation_transfer.test, ast.BoolOp)
    assert isinstance(observation_transfer.test.op, ast.And)
    assert len(observation_transfer.test.values) == 2
    transfer_ok, transfer_value = observation_transfer.test.values
    assert isinstance(transfer_ok, ast.Name)
    assert transfer_ok.id == "after_ok"
    assert isinstance(transfer_ok.ctx, ast.Load)
    assert isinstance(transfer_value, ast.Compare)
    assert isinstance(transfer_value.left, ast.Name)
    assert transfer_value.left.id == "after_value"
    assert isinstance(transfer_value.left.ctx, ast.Load)
    assert len(transfer_value.ops) == 1
    assert isinstance(transfer_value.ops[0], ast.IsNot)
    assert len(transfer_value.comparators) == 1
    assert isinstance(transfer_value.comparators[0], ast.Constant)
    assert transfer_value.comparators[0].value is None
    assert len(observation_transfer.body) == 1
    transfer_assignment = observation_transfer.body[0]
    assert isinstance(transfer_assignment, ast.Assign)
    assert len(transfer_assignment.targets) == 1
    assert isinstance(transfer_assignment.targets[0], ast.Name)
    assert transfer_assignment.targets[0].id == "observations"
    assert isinstance(transfer_assignment.targets[0].ctx, ast.Store)
    assert isinstance(transfer_assignment.value, ast.Name)
    assert transfer_assignment.value.id == "after_value"
    assert isinstance(transfer_assignment.value.ctx, ast.Load)
    assert observation_transfer.orelse == []

    assert not any(isinstance(node, ast.Try) for node in ast.walk(ended))

    helper = _function("_run_finalization_step")
    monotonic_calls = [
        node for node in ast.walk(helper)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "monotonic"
    ]
    assert len(monotonic_calls) == 2
    assert any(isinstance(node, ast.Try) for node in helper.body)
    assert len([
        node for node in ast.walk(helper)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "append"
    ]) == 3
    step_error = ast.get_source_segment(SOURCE, _class("FinalizationStepError"))
    assert step_error is not None
    assert "self.step = step" in step_error
    assert "self.cause = cause" in step_error

    handler_raises = [
        node for node in ast.walk(handler)
        if isinstance(node, ast.Raise)
    ]
    assert any(
        isinstance(node.exc, ast.Call)
        and isinstance(node.exc.func, ast.Name)
        and node.exc.func.id == "TechnicalAbort"
        for node in handler_raises
    )
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "ExecutionResult"
        for node in ast.walk(handler)
    )
