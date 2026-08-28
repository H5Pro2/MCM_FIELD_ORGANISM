"""Private S2-DR comparison implementation for the bounded TSPM-1 study."""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
import ast
import ctypes
from ctypes import wintypes
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
from threading import Lock
from types import CodeType
from typing import Any, Iterable, Mapping, Sequence

from . import _tspm1_private as tspm1
from ._ppb1_active_receptor_batch_binding import bind_ppb1_active_receptor_batch
from ._ppb1_receptor_profiles import (
    PPB1ModalityParameters,
    PPB1ProfileParameters,
    bind_ppb1_receptor_profile,
)
from ._ppb1_reference import (
    PPB1BankState,
    advance_ppb1_bank,
    initial_ppb1_bank_state,
    normalized_mean_l1_distance,
)
from ._ppb1_s1wu_read_only_perceptual_probe import (
    S1WUReadOnlyPerceptualFinding,
    probe_s1wu_perceptual_state,
)
from .browser_receptor_bridge import BrowserReceptorSequenceBatch
from .browser_world_contract import BrowserWorldContract, BrowserWorldPhase
from .receptor_contract import CommonFieldTime, ReceptorContactFrame, technical_identifier
from .receptor_time_model import OrganismTimedReceptorFrame, ReceptorTimeSequence


S2DR_SCHEMA_VERSION = "s2dr.tspm1.private-comparison.s2ef.v1"
S2EE_CONTRACT_DIGEST = "2e6c76952a7f8d8c9eb39e202c3605f525218fdaba4812bf919137305ef425ec"
S2EE_EVALUATION_ID = "S2EE_FUNCTIONAL_EVALUATION_V1"
S2EE_STUDY_ID = "s2dr.tspm1.h1-h7.56.v1"
# A later reviewed release must open this gate before a source-bound plan is built.
_EXECUTION_RELEASE_ENABLED = False
S2DR_CANDIDATE_ID = "TSPM1"
S2DR_S2DS_PASS_DIGEST = (
    "1101642ddcabe325cc76c65a0e026e185b7c8cede7ab715ac8bec16165fbf284"
)

S2DR_OWNER_BUSY = "S2DR_OWNER_BUSY"
S2DR_OWNER_TERMINAL = "S2DR_OWNER_TERMINAL"
S2DR_INVALID_TYPE_OR_SCHEMA = "S2DR_INVALID_TYPE_OR_SCHEMA"
S2DR_DIGEST_OR_SOURCE_MISMATCH = "S2DR_DIGEST_OR_SOURCE_MISMATCH"
S2DR_AUTHORIZATION_MISMATCH = "S2DR_AUTHORIZATION_MISMATCH"
S2DR_OWNER_AUTHORIZATION_MISMATCH = "S2DR_OWNER_AUTHORIZATION_MISMATCH"
S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH = "S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH"
S2DR_RESOURCE_OR_OPERATION_LIMIT_EXCEEDED = (
    "S2DR_RESOURCE_OR_OPERATION_LIMIT_EXCEEDED"
)
S2DR_RESULT_RELATION_MISMATCH = "S2DR_RESULT_RELATION_MISMATCH"
S2DR_ATOMIC_RESULT_REQUIRED = "S2DR_ATOMIC_RESULT_REQUIRED"
S2DR_ATTEMPT_FAILED = "S2DR_ATTEMPT_FAILED"

HISTORY_IDS = ("H1", "H2", "H3", "H4", "H5", "H6", "H7")
ARM_IDS = (
    "TSPM1",
    "B0",
    "B1_DIRECT",
    "B1_BUDGET_MATCHED",
    "B2",
    "B3",
    "B4",
    "R0",
)
PREDICATE_IDS = ("P1_EARLY", "P2_LATE", "P3_CONFLICT", "P4_CAPACITY", "P5_SELECTIVITY")
OUTCOMES = (
    "METHOD_INVALID",
    "TSPM1_FUNCTION_NOT_VALID",
    "FUNCTION_VALID_SIMPLE_BASELINE_EXPLAINS",
    "TSPM1_TWO_TIMESCALE_ENGINEERING_ADVANTAGE_OVER_SIMPLE_BASELINES",
)
OWNER_STATES = ("FRESH", "BUSY", "COMMITTED", "FAILED")

AUDITORY_CARRIERS = (
    "auditory.log_hz.50.000000",
    "auditory.log_hz.89.741146",
    "auditory.log_hz.161.069466",
    "auditory.log_hz.289.091169",
    "auditory.log_hz.518.867457",
    "auditory.log_hz.931.275205",
    "auditory.log_hz.1671.474085",
    "auditory.log_hz.3000.000000",
)
VISUAL_CARRIERS = tuple(
    f"visual.cell.r{row}.c{column}.channel{channel}"
    for row in range(2)
    for column in range(3)
    for channel in range(3)
)
PAIR_SCALARS = {
    "AX": (0.0, 0.0),
    "AY": (0.0, 0.6),
    "BX": (0.6, 0.0),
    "P2": (-0.8, -0.8),
    "P3": (-0.8, 0.8),
    "P4": (0.8, -0.8),
    "D1": (-1.0, -1.0),
    "D2": (-1.0, 0.0),
    "D3": (-1.0, 1.0),
    "D4": (0.0, -1.0),
    "D5": (0.0, 1.0),
    "D6": (1.0, -1.0),
    "D7": (1.0, 0.0),
    "D8": (1.0, 1.0),
    "NEAR": (0.15, 0.15),
    "PARTIAL_OUT": (0.21, 0.0),
    "OUTSIDE": (0.21, 0.21),
    "FAR": (1.0, 1.0),
}
HISTORY_DEFINITIONS = {
    "H1": (("AX",), ((1, ("AX",)),), ()),
    "H2": (("AX", "AX", "AX", "AX"), ((1, ("AX",)), (4, ("AX",))), (2, 3, 4)),
    "H3": (("AX", "AX", "AX", "AX", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"), ((12, ("AX",)),), (2, 3, 4)),
    "H4": (("AX", "AX", "AX", "AX", "AY", "BX"), ((6, ("AX", "AY", "BX")),), (2, 3, 4)),
    "H5": (("AX", "AX", "AX", "AX", "P2", "P3", "P2", "P4"), ((8, ("AX", "P4")),), (2, 3, 4, 7)),
    "H6": (("AX", "AX", "AX", "AX", "D1", "D3", "D8"), ((7, ("AX", "D1", "D3", "D8")),), (2, 3, 4)),
    "H7": (("AX", "AX", "AX", "AX"), ((4, ("AX", "NEAR", "PARTIAL_OUT", "OUTSIDE", "FAR")),), (2, 3, 4)),
}
ARM_RESOURCE_WORDS = {
    "TSPM1": 269,
    "B0": 0,
    "B1_DIRECT": 176,
    "B1_BUDGET_MATCHED": 176,
    "B2": 264,
    "B3": 29,
    "B4": 255,
    "R0": 269,
}
OPERATION_LIMITS = {
    "formation_write_limit": 293,
    "formation_distance_limit": 234,
    "probe_distance_limit": 234,
    "probe_write_limit": 0,
}
SIMPLE_BASELINE_ORDER = ("B0", "B1_DIRECT", "B1_BUDGET_MATCHED", "B2", "B3", "B4")

_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")


def _root() -> Path:
    return Path(__file__).resolve().parent.parent


def _git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(_root()), *args], text=True).strip()


def _json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _loads(raw: str | bytes) -> Any:
    return json.loads(raw, object_pairs_hook=_json_object,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def _json_bytes(value: object) -> bytes:
    return json.dumps(_canonical(value), allow_nan=False, ensure_ascii=True,
                      sort_keys=True, separators=(",", ":")).encode("ascii")


def _ee_contract() -> dict:
    path = _root() / "docs/S2EE_TSPM1_STATISCHER_KORREKTUR_UND_AUSFUEHRUNGSBINDUNGSVERTRAG_V1.json"
    contract = _loads(path.read_bytes())
    declared = contract.pop("artifact_digest")
    if declared != S2EE_CONTRACT_DIGEST or _digest(contract) != declared:
        raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, "S2-EE contract changed")
    return contract


@dataclass(frozen=True, slots=True)
class S2EFRecord:
    """Canonical value seal: callers never retain mutable record payloads."""

    kind: str
    data_json: str
    record_digest: str

    def payload(self) -> dict:
        data = _loads(self.data_json)
        required = set(_ee_contract()["source_and_receipt_contract"]["record_fields"][self.kind])
        if set(data) != required | {"schema_version"}:
            raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "record fields differ")
        if data["schema_version"] != f"s2ef.{self.kind}.v1" or _digest(data) != self.record_digest:
            raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, "record seal differs")
        return {**data, "record_digest": self.record_digest}


def _record(kind: str, **data) -> S2EFRecord:
    data = {"schema_version": f"s2ef.{kind}.v1", **data}
    record = S2EFRecord(kind, _json_bytes(data).decode("ascii"), _digest(data))
    record.payload()
    return record


def _unrecord(kind: str, data: dict) -> S2EFRecord:
    raw = dict(data)
    digest = raw.pop("record_digest")
    record = S2EFRecord(kind, _json_bytes(raw).decode("ascii"), digest)
    record.payload()
    return record


def _file_identity(path: Path) -> dict:
    relative = path.resolve().relative_to(_root()).as_posix()
    return {"repository_relative_path": relative,
            "git_blob": _git("rev-parse", f"HEAD:{relative}"),
            "raw_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def _project_source_inventory() -> tuple[dict, ...]:
    """Resolve project imports without importing modules or evaluating code."""
    package = _root() / "mcm_field_organism"
    pending = [Path(__file__).resolve(), package / "__init__.py"]
    visited = set()
    while pending:
        path = pending.pop().resolve()
        if path in visited:
            continue
        visited.add(path)
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.level:
                    base = path.parent
                    for _ in range(node.level - 1):
                        base = base.parent
                    target = base.joinpath(*(node.module or "").split("."))
                    candidates = [target.with_suffix(".py")] if node.module else []
                    candidates += [target / f"{item.name}.py" for item in node.names]
                    candidates += [target / "__init__.py"]
                elif node.module and node.module.startswith("mcm_field_organism"):
                    target = _root().joinpath(*node.module.split("."))
                    candidates = [target.with_suffix(".py"), target / "__init__.py"]
                else:
                    continue
                found = [item for item in candidates if item.is_file()]
                if not found:
                    raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, "unresolved project import")
                pending.extend(found)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("mcm_field_organism"):
                        target = _root().joinpath(*alias.name.split("."))
                        pending.append(target.with_suffix(".py") if target.with_suffix(".py").is_file()
                                       else target / "__init__.py")
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in {"__import__", "import_module", "_import_module"}:
                    # The package's lazy public exports are not used by this private path.
                    if path != package / "__init__.py":
                        raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, "dynamic project import requires audit")
    return tuple(_file_identity(path) for path in sorted(visited))


def _source_code_objects(code):
    yield code
    for constant in code.co_consts:
        if isinstance(constant, CodeType):
            yield from _source_code_objects(constant)


def _validate_distance_source(raw, identity, expected, site, dimension, *, caller_code=None):
    _require(identity == expected and hashlib.sha256(raw).hexdigest() == expected["raw_sha256"],
             "distance source bytes differ")
    _require(type(dimension) is int and dimension in (8, 18), "distance dimension differs")
    _require(len(site) == 2 and type(site[0]) is str and type(site[1]) is int,
             "distance callsite differs")
    tree = ast.parse(raw)
    if site[0] != "<genexpr>":
        _require(any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == site[0]
                     and node.lineno <= site[1] <= node.end_lineno for node in ast.walk(tree)),
                 "distance callsite is not in bound source")
        return
    _require(identity["repository_relative_path"] == "mcm_field_organism/_ppb1_s1wu_read_only_perceptual_probe.py"
             and identity["raw_sha256"] == "8739a5cf630ca8bbfb6c0c801d4d17b81dd25ae66d1bb7eef2d36bb45e17ca27",
             "unregistered generator source")
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
             and isinstance(node.func, ast.Name) and node.func.id == "normalized_mean_l1_distance"
             and (node.lineno, node.end_lineno) == (211, 214)]
    _require(len(calls) == 1 and calls[0].lineno <= site[1] <= calls[0].end_lineno,
             "unregistered generator call")
    filename = str(_root() / identity["repository_relative_path"])
    # Compile for identity inspection only; the resulting module is never executed.
    compiled = compile(raw, filename, "exec", dont_inherit=True, optimize=sys.flags.optimize)
    matches = [code for code in _source_code_objects(compiled)
               if (code.co_name, code.co_qualname, code.co_firstlineno)
               == ("<genexpr>", "probe_s1wu_perceptual_state.<locals>.<genexpr>", 209)]
    _require(len(matches) == 1, "generator code mapping is not unique")
    if caller_code is not None:
        _require(caller_code == matches[0] and Path(caller_code.co_filename).resolve() == Path(filename).resolve(),
                 "runtime generator code differs")


class _OperationMeter:
    """Thread-local Python call observation; never monkeypatches either core."""

    def __init__(self, arm_id: str, cell_id: str, phase: str, index: int):
        self.arm_id, self.cell_id, self.phase, self.index = arm_id, cell_id, phase, index
        self.distances: list[dict] = []
        self.ppb_calls: list[dict] = []
        self.identities: dict[str, dict] = {}
        self.source_inventory = {item["repository_relative_path"]: item for item in _project_source_inventory()}
        self.failure: BaseException | None = None

    def _observe(self, frame, event, value):
        try:
            if event == "call" and frame.f_code is normalized_mean_l1_distance.__code__:
                first, second = frame.f_locals["first"], frame.f_locals["second"]
                if len(first) != len(second) or len(first) not in (8, 18):
                    raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "unregistered distance dimension")
                caller = frame.f_back
                filename = caller.f_code.co_filename
                if filename not in self.identities:
                    self.identities[filename] = _file_identity(Path(filename))
                identity = self.identities[filename]
                if caller.f_code.co_name == "<genexpr>":
                    _require(caller.f_globals.get("normalized_mean_l1_distance") is normalized_mean_l1_distance,
                             "generator callee differs")
                _require(identity["repository_relative_path"] in self.source_inventory, "unregistered caller source")
                _validate_distance_source(Path(filename).read_bytes(), identity,
                                          self.source_inventory[identity["repository_relative_path"]],
                                          [caller.f_code.co_name, caller.f_lineno], len(first), caller_code=caller.f_code)
                validation = False
                cursor = caller
                while cursor is not None:
                    name = cursor.f_code.co_name
                    if name.startswith(("_validate", "validate_")) or (
                        self.arm_id == "TSPM1" and name == "_s1wu_evidence"
                    ):
                        validation = True
                    cursor = cursor.f_back
                self.distances.append({
                    "cell_id": self.cell_id, "phase": self.phase, "operation_index": self.index,
                    "ordinal": len(self.distances) + 1, "source_path": identity["repository_relative_path"],
                    "source_blob": identity["git_blob"], "callsite": [caller.f_code.co_name, caller.f_lineno],
                    "purpose": "VALIDATION" if validation else "FUNCTIONAL",
                    "operand_digests": [_digest(first), _digest(second)], "dimension": len(first),
                })
            elif event == "return" and frame.f_code is advance_ppb1_bank.__code__:
                if value is None:
                    return
                config, prestate = frame.f_locals["config"], frame.f_locals["prestate"]
                step = prestate.accepted_step_count + 1
                expired = tuple(index for index, slot in enumerate(prestate.slots)
                                if slot.occupied and step - slot.last_selected_step >= config.expire_after_steps)
                selected = next(index for index, slot in enumerate(value.poststate.slots)
                                if slot.slot_id == value.readout.slot_id)
                self.ppb_calls.append({"modality": config.modality_id, "expired": expired,
                                       "selected": selected, "event_digest": _digest(value.readout),
                                       "readout": _canonical(value.readout),
                                       "prestate": _canonical(prestate), "poststate": _canonical(value.poststate),
                                       "config": _canonical(config)})
        except BaseException as exc:
            self.failure = exc

    def __enter__(self):
        if sys.getprofile() is not None:
            raise S2DRError(S2DR_ATOMIC_RESULT_REQUIRED, "another profiler is active")
        sys.setprofile(self._observe)
        return self

    def __exit__(self, exc_type, exc, traceback):
        installed = sys.getprofile()
        sys.setprofile(None)
        if installed != self._observe or self.failure is not None:
            if isinstance(self.failure, S2DRError):
                raise self.failure
            raise S2DRError(S2DR_ATOMIC_RESULT_REQUIRED, "incomplete distance observation") from self.failure
        return False

    def seal(self, actions: list[dict], before: object, after: object,
             native_before: object, native_after: object, event: dict | None) -> dict:
        functional = sum(item["dimension"] for item in self.distances if item["purpose"] == "FUNCTIONAL")
        validation = sum(item["dimension"] for item in self.distances if item["purpose"] == "VALIDATION")
        data = {"cell_id": self.cell_id, "phase": self.phase, "operation_index": self.index,
                "distance_evidence": self.distances, "write_evidence": actions,
                "functional_terms": functional, "validation_terms": validation,
                "total_distance_terms": functional + validation,
                "functional_write_words": sum(item["width"] for item in actions),
                "ppb_call_evidence": self.ppb_calls,
                "native_prestate_payload": native_before, "native_poststate_payload": native_after,
                "native_event": event,
                "prestate_payload": before, "poststate_payload": after,
                "prestate_digest": _digest(before), "poststate_digest": _digest(after)}
        return {**data, "cost_digest": _digest(data)}


def _write_evidence(meter: _OperationMeter, prestate, poststate, event: dict) -> list[dict]:
    return _write_actions(meter.arm_id, meter.cell_id, meter.phase, meter.index,
                          _canonical(prestate), _canonical(poststate), event, meter.ppb_calls)


def _write_actions(arm_id, cell_id, phase, index, prestate, poststate, event, ppb_calls):
    actions = []
    widths = _ee_contract()["operation_contract"]["write_actions"]

    def add(action, component, position=None, digest=None):
        actions.append({"cell_id": cell_id, "phase": phase,
                        "operation_index": index, "ordinal": len(actions) + 1,
                        "action": action, "state_component": component,
                        "slot_position_or_null": position, "width": widths[action],
                        "source_event_digest": digest or _digest(event)})

    if arm_id in {"TSPM1", "R0"}:
        name = "fast_state" if arm_id == "TSPM1" else "fast"
        before, after = prestate[name], poststate[name]
        for i, slot in enumerate(before["slots"]):
            if slot["occupied"] and index - slot["last_selected_step"] >= 8:
                add("FAST_SLOT_RESET", "fast", i)
        selected = [i for i, slot in enumerate(after["slots"]) if slot["occupied"] and slot["last_selected_step"] == index]
        if len(selected) != 1:
            raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "ambiguous Fast write")
        add("FAST_SLOT_WRITE", "fast", selected[0])
        add("FAST_GLOBAL_ADVANCE", "fast")
        if event["consolidation_status"] == "COMMITTED":
            add("FAST_CONSOLIDATION_INCREMENT", "fast", selected[0])
        expected_calls = 2 if event["consolidation_status"] == "COMMITTED" else 0
    elif arm_id == "B2":
        for i, slot in enumerate(prestate["slots"]):
            if slot["occupied"] and index - slot["last_selected_step"] >= 8:
                add("B2_SLOT_RESET", "joint", i)
        selected = next(i for i, slot in enumerate(poststate["slots"]) if slot["slot_id"] == event["slot_id"])
        add("B2_SLOT_WRITE", "joint", selected)
        add("B2_GLOBAL_ADVANCE", "joint")
        expected_calls = 0
    elif arm_id == "B3":
        add("B3_UPDATE_OR_CREATE", "trace")
        expected_calls = 0
    elif arm_id == "B4":
        selected = next(i for i, entry in enumerate(poststate["entries"]) if entry["slot_id"] == event["slot_id"])
        add("B4_ENTRY_WRITE", "fifo", selected)
        add("B4_GLOBAL_ADVANCE", "fifo")
        expected_calls = 0
    else:
        expected_calls = 2 if event["event"] == "B1_PPB1_ADVANCED" else 0
    if len(ppb_calls) != expected_calls:
        raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "PPB call budget differs")
    if expected_calls and {call["modality"] for call in ppb_calls} != {"auditory", "visual"}:
        raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "asymmetric PPB calls")
    for call in ppb_calls:
        prefix = "PPB_" + call["modality"].upper()
        for i in call["expired"]:
            add(prefix + "_SLOT_RESET", call["modality"], i, call["event_digest"])
        add(prefix + "_SLOT_WRITE", call["modality"], call["selected"], call["event_digest"])
        add("PPB_BANK_GLOBAL_ADVANCE", call["modality"], digest=call["event_digest"])
    return actions


def advance_s2dr_arm(config, fixture, arm, prestate, pair_id, formation_index):
    before = _canonical(_state_payload(arm.arm_id, prestate))
    native_before = _canonical(prestate)
    with _OperationMeter(arm.arm_id, f"s2dr.cell.{fixture.history_id.lower()}.{arm.arm_id.lower()}",
                         "FORMATION", formation_index) as meter:
        poststate, event, _ = _advance_s2dr_arm_unmetered(config, fixture, arm, prestate, pair_id, formation_index)
        actions = _write_evidence(meter, prestate, poststate, event)
        after = _canonical(_state_payload(arm.arm_id, poststate))
    cost = meter.seal(actions, before, after, native_before, _canonical(poststate), event)
    return poststate, {**event, "cost_evidence": cost}, (cost["functional_write_words"], cost["total_distance_terms"])


def probe_s2dr_arm(config, fixture, arm, state, pair_id, probe_index):
    before = _canonical(_state_payload(arm.arm_id, state))
    with _OperationMeter(arm.arm_id, f"s2dr.cell.{fixture.history_id.lower()}.{arm.arm_id.lower()}",
                         "PROBE", probe_index) as meter:
        finding, _ = _probe_s2dr_arm_unmetered(config, fixture, arm, state, pair_id, probe_index)
        paths = _selected_source_paths(arm.arm_id, state, finding)
        after = _canonical(_state_payload(arm.arm_id, state))
        if before != after or meter.ppb_calls:
            raise S2DRError(S2DR_ATOMIC_RESULT_REQUIRED, "read-only operation wrote state")
    cost = meter.seal([], before, after, _canonical(state), _canonical(state), None)
    observation = {"history_id": fixture.history_id, "arm_id": arm.arm_id,
                   "checkpoint": finding["checkpoint"], "probe_index": probe_index, "pair_id": pair_id,
                   "native_recognized": finding["recognized"],
                   "selected_auditory_values": finding["selected_auditory_values"],
                   "selected_visual_values": finding["selected_visual_values"],
                   "selected_source_paths": paths, "observed_state_digest": _digest(before),
                   "native_finding_digest": _digest(finding)}
    observation["observation_digest"] = _digest(observation)
    identity = _file_identity(Path(__file__))
    checkpoint = _record("CheckpointEvidence", history_id=fixture.history_id, arm_id=arm.arm_id,
                         checkpoint=finding["checkpoint"], native_state_schema=type(state).__name__,
                         native_state_payload=_canonical(state), native_state_digest=_digest(state),
                         native_finding_payload=finding, native_finding_digest=_digest(finding),
                         extraction_source_path=identity["repository_relative_path"],
                         extraction_source_blob=identity["git_blob"])
    return {**finding, "observation": observation, "cost_evidence": cost,
            "checkpoint_evidence": checkpoint.payload()}, cost["total_distance_terms"]


def _selected_source_paths(arm_id: str, state, finding: dict) -> list[dict]:
    if not finding["recognized"]:
        if finding["selected_auditory_values"] is not None or finding["selected_visual_values"] is not None:
            raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "negative retrieval returned a payload")
        return []
    native = _canonical(state)
    if finding["context_source"] == "SLOW_PPB1_CONTEXT":
        names = ({"TSPM1": ("auditory_ppb1_state", "visual_ppb1_state"),
                  "R0": ("auditory_ppb", "visual_ppb")}.get(arm_id, ("auditory", "visual")))
        paths = []
        for modality, bank_name, dimension in zip(("auditory", "visual"), names, (8, 18), strict=True):
            slots = native[bank_name]["slots"]
            indexes = [i for i, slot in enumerate(slots) if slot["slot_id"] == finding[f"{modality}_selected_slot_id"] and slot["occupied"]]
            if len(indexes) != 1:
                raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "selected PPB source differs")
            paths.append({"path": [bank_name, "slots", indexes[0], "prototype_values"], "start": 0, "length": dimension})
    elif arm_id in {"TSPM1", "R0"}:
        name = "fast_state" if arm_id == "TSPM1" else "fast"
        indexes = [i for i, slot in enumerate(native[name]["slots"]) if slot["slot_id"] == finding["fast_slot_id"] and slot["occupied"]]
        if len(indexes) != 1:
            raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "selected Fast source differs")
        paths = [{"path": [name, "slots", indexes[0], modality + "_values"], "start": 0, "length": dim}
                 for modality, dim in (("auditory", 8), ("visual", 18))]
    else:
        if arm_id == "B3":
            base = ["values"]
        else:
            name = "slots" if arm_id == "B2" else "entries"
            indexes = [i for i, slot in enumerate(native[name]) if slot["slot_id"] == finding["fast_slot_id"] and slot["occupied"]]
            if len(indexes) != 1:
                raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "selected baseline source differs")
            base = [name, indexes[0], "values"]
        paths = [{"path": base, "start": 0, "length": 8}, {"path": base, "start": 8, "length": 18}]
    for source, modality in zip(paths, ("auditory", "visual"), strict=True):
        if _read_selected(native, source) != tuple(finding[f"selected_{modality}_values"]):
            raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "retrieved values do not match state source")
    return paths


def _read_selected(native: object, source: dict) -> tuple:
    if set(source) != {"path", "start", "length"}:
        raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "selected source shape differs")
    value = native
    for key in source["path"]:
        value = value[key]
    selected = tuple(value[source["start"]:source["start"] + source["length"]])
    if len(selected) != source["length"] or any(type(x) not in (int, float) or not math.isfinite(x) or not -1 <= x <= 1 for x in selected):
        raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "selected values are invalid")
    return selected


class S2DRError(ValueError):
    """One private fail-closed S2-DR violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _canonical(value: Any) -> Any:
    if isinstance(value, S2EFRecord):
        return value.payload()
    if is_dataclass(value):
        return {field.name: _canonical(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, Mapping):
        return {str(key): _canonical(item) for key, item in sorted(value.items())}
    if isinstance(value, (tuple, list)):
        return [_canonical(item) for item in value]
    return value


def _digest(value: Any) -> str:
    encoded = json.dumps(
        _canonical(value),
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _is_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST_RE.fullmatch(value) is not None


def _id(value: object, role: str) -> str:
    try:
        return technical_identifier(value, role)
    except ValueError as exc:
        raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, str(exc)) from exc


def _finite_tuple(values: object, length: int, role: str) -> tuple[float, ...]:
    if not isinstance(values, tuple) or len(values) != length:
        raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, f"{role} shape is invalid")
    normalized = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, f"{role} must be finite")
        normalized.append(float(value))
    return tuple(normalized)


def _record_payload(record: object, digest_field: str) -> dict[str, object]:
    return {
        field.name: _canonical(getattr(record, field.name))
        for field in fields(record)
        if field.name != digest_field
    }


def _validate_record(record: object, digest_field: str) -> None:
    digest_value = getattr(record, digest_field)
    if not _is_digest(digest_value) or digest_value != _digest(_record_payload(record, digest_field)):
        raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, f"invalid {digest_field}")


def _built(record_type, digest_field: str, **values):
    values[digest_field] = _digest(values)
    return record_type(**values)


@dataclass(frozen=True, slots=True)
class S2DRConfigRecord:
    schema_version: str
    candidate_id: str
    parent_artifact_digests: tuple[str, ...]
    source_blob_digests: tuple[str, ...]
    auditory_carrier_ids: tuple[str, ...]
    visual_carrier_ids: tuple[str, ...]
    fast_parameters: tuple[object, ...]
    auditory_ppb_parameters: tuple[object, ...]
    visual_ppb_parameters: tuple[object, ...]
    arm_resource_words: tuple[tuple[str, int], ...]
    operation_limits: tuple[tuple[str, int], ...]
    config_digest: str

    def __post_init__(self) -> None:
        if self.schema_version != S2DR_SCHEMA_VERSION or self.candidate_id != S2DR_CANDIDATE_ID:
            raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "invalid config identity")
        if self.auditory_carrier_ids != AUDITORY_CARRIERS or self.visual_carrier_ids != VISUAL_CARRIERS:
            raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, "carrier anatomy changed")
        if not all(_is_digest(value) for value in self.parent_artifact_digests + self.source_blob_digests):
            raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, "source digest is invalid")
        _validate_record(self, "config_digest")


@dataclass(frozen=True, slots=True)
class S2DRFixtureRecord:
    schema_version: str
    history_id: str
    formation_pair_ids: tuple[str, ...]
    probe_specs: tuple[tuple[int, tuple[str, ...]], ...]
    ppb_budget_indices: tuple[int, ...]
    field_clock_id: str
    interval_width: int
    source_id_format: str
    formation_frame_id_format: str
    probe_frame_id_format: str
    fixture_digest: str

    def __post_init__(self) -> None:
        if self.schema_version != S2DR_SCHEMA_VERSION or self.history_id not in HISTORY_IDS:
            raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "invalid fixture identity")
        expected = HISTORY_DEFINITIONS[self.history_id]
        if (self.formation_pair_ids, self.probe_specs, self.ppb_budget_indices) != expected:
            raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, "fixture differs from registry")
        if self.interval_width != 10 or self.field_clock_id != "field.synthetic.s2dq":
            raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, "fixture clock changed")
        _validate_record(self, "fixture_digest")


@dataclass(frozen=True, slots=True)
class S2DRArmSpec:
    schema_version: str
    arm_id: str
    operator_id: str
    state_schema_id: str
    resource_words: int
    formation_write_limit: int
    formation_distance_limit: int
    probe_distance_limit: int
    probe_write_limit: int
    initial_state_payload: object
    initial_state_digest: str
    arm_spec_digest: str

    def __post_init__(self) -> None:
        if self.schema_version != S2DR_SCHEMA_VERSION or self.arm_id not in ARM_IDS:
            raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "invalid arm identity")
        if self.resource_words != ARM_RESOURCE_WORDS[self.arm_id]:
            raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, "resource words changed")
        if (
            self.formation_write_limit,
            self.formation_distance_limit,
            self.probe_distance_limit,
            self.probe_write_limit,
        ) != (293, 234, 234, 0):
            raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, "operation limits changed")
        if self.initial_state_digest != _digest(self.initial_state_payload):
            raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, "initial state digest changed")
        _validate_record(self, "arm_spec_digest")


@dataclass(frozen=True, slots=True)
class S2DRCellPlan:
    schema_version: str
    cell_id: str
    history_id: str
    arm_id: str
    config_digest: str
    fixture_digest: str
    arm_spec_digest: str
    initial_state_digest: str
    formation_call_count: int
    probe_call_count: int
    authorization_digest: str
    cell_plan_digest: str

    def __post_init__(self) -> None:
        if self.schema_version != S2DR_SCHEMA_VERSION or self.history_id not in HISTORY_IDS or self.arm_id not in ARM_IDS:
            raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "invalid cell plan identity")
        _id(self.cell_id, "cell_id")
        if not all(_is_digest(value) for value in (self.config_digest, self.fixture_digest, self.arm_spec_digest, self.initial_state_digest, self.authorization_digest)):
            raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, "cell plan digest role invalid")
        expected = _authorization_digest(
            self.cell_id,
            self.config_digest,
            self.fixture_digest,
            self.arm_spec_digest,
            self.initial_state_digest,
        )
        if self.authorization_digest != expected:
            raise S2DRError(S2DR_AUTHORIZATION_MISMATCH, "cell authorization changed")
        _validate_record(self, "cell_plan_digest")


@dataclass(frozen=True, slots=True)
class S2DRBudgetReceipt:
    schema_version: str
    cell_id: str
    cell_plan_digest: str
    resource_words_bound: int
    resource_words_used: int
    formation_write_bounds: tuple[tuple[int, int], ...]
    formation_write_counts: tuple[tuple[int, int], ...]
    formation_distance_bounds: tuple[tuple[int, int], ...]
    formation_distance_counts: tuple[tuple[int, int], ...]
    probe_distance_bounds: tuple[tuple[int, int], ...]
    probe_distance_counts: tuple[tuple[int, int], ...]
    probe_write_bounds: tuple[tuple[int, int], ...]
    probe_write_counts: tuple[tuple[int, int], ...]
    remaining_resource_words: int
    remaining_formation_write_budget: tuple[tuple[int, int], ...]
    remaining_formation_distance_budget: tuple[tuple[int, int], ...]
    remaining_probe_distance_budget: tuple[tuple[int, int], ...]
    remaining_probe_write_budget: tuple[tuple[int, int], ...]
    budget_receipt_digest: str

    def __post_init__(self) -> None:
        if self.schema_version != S2DR_SCHEMA_VERSION:
            raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "invalid budget schema")
        _id(self.cell_id, "cell_id")
        if not _is_digest(self.cell_plan_digest):
            raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, "invalid budget plan digest")
        if any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in (self.resource_words_bound, self.resource_words_used)):
            raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "resource values must be nonnegative integers")
        if self.remaining_resource_words != self.resource_words_bound - self.resource_words_used:
            raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "resource remainder is inconsistent")
        groups = (
            (self.formation_write_bounds, self.formation_write_counts, self.remaining_formation_write_budget),
            (self.formation_distance_bounds, self.formation_distance_counts, self.remaining_formation_distance_budget),
            (self.probe_distance_bounds, self.probe_distance_counts, self.remaining_probe_distance_budget),
            (self.probe_write_bounds, self.probe_write_counts, self.remaining_probe_write_budget),
        )
        for bounds, counts, remaining in groups:
            keys = tuple(key for key, _ in bounds)
            if keys != tuple(key for key, _ in counts) or keys != tuple(key for key, _ in remaining):
                raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "budget tuple keys differ")
            if keys != tuple(sorted(keys)) or any(key < 1 for key in keys):
                raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "budget tuple keys are invalid")
            for (_, bound), (_, used), (_, rest) in zip(bounds, counts, remaining, strict=True):
                if any(isinstance(value, bool) or not isinstance(value, int) for value in (bound, used, rest)) or bound < 0 or used < 0:
                    raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "budget tuple value is invalid")
                if rest != bound - used:
                    raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "operation remainder is inconsistent")
        _validate_record(self, "budget_receipt_digest")


@dataclass(frozen=True, slots=True)
class S2DRCellReceipt:
    schema_version: str
    cell_id: str
    cell_plan_digest: str
    config_digest: str
    fixture_digest: str
    arm_spec_digest: str
    prestate_digest: str
    event_digest: str
    finding_digest: str
    budget_receipt_digest: str
    poststate_digest: str
    owner_id: str
    owner_terminal_state: str
    internal_error_code: str | None
    cell_receipt_digest: str

    def __post_init__(self) -> None:
        if self.schema_version != S2DR_SCHEMA_VERSION or self.owner_terminal_state not in OWNER_STATES:
            raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "invalid cell receipt")
        _id(self.cell_id, "cell_id")
        _id(self.owner_id, "owner_id")
        digests = (self.cell_plan_digest, self.config_digest, self.fixture_digest, self.arm_spec_digest, self.prestate_digest, self.event_digest, self.finding_digest, self.budget_receipt_digest, self.poststate_digest)
        if not all(_is_digest(value) for value in digests):
            raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, "cell receipt digest role invalid")
        _validate_record(self, "cell_receipt_digest")


@dataclass(frozen=True, slots=True)
class S2DRCellResult:
    schema_version: str
    cell_id: str
    cell_plan_digest: str
    prestate_digest: str
    event_payloads: tuple[object, ...]
    finding_payloads: tuple[object, ...]
    poststate_payload: object
    poststate_digest: str
    budget_receipt: S2DRBudgetReceipt
    cell_receipt: S2DRCellReceipt
    cell_result_digest: str

    def __post_init__(self) -> None:
        if self.schema_version != S2DR_SCHEMA_VERSION or type(self.budget_receipt) is not S2DRBudgetReceipt or type(self.cell_receipt) is not S2DRCellReceipt:
            raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "invalid cell result")
        if self.poststate_digest != _digest(self.poststate_payload):
            raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "poststate payload digest differs")
        _validate_record(self, "cell_result_digest")


@dataclass(frozen=True, slots=True)
class S2DRComparisonResult:
    schema_version: str
    registry_digest: str
    ordered_cell_result_digests: tuple[str, ...]
    per_arm_predicate_vectors: tuple[tuple[str, tuple[bool, ...]], ...]
    per_arm_error_counts: tuple[tuple[str, int], ...]
    strongest_simple_baseline_id: str | None
    r0_exact_equivalence: bool
    decision: str
    evaluation_id: str
    per_arm_metrics: tuple[tuple[str, object], ...]
    all_arm_ranking: tuple[str, ...]
    simple_baseline_ranking: tuple[str, ...]
    ordered_cell_evidence_digests: tuple[str, ...]
    comparison_result_digest: str

    def __post_init__(self) -> None:
        if self.schema_version != S2DR_SCHEMA_VERSION or self.decision not in OUTCOMES:
            raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "invalid comparison result")
        if not _is_digest(self.registry_digest) or not all(_is_digest(value) for value in self.ordered_cell_result_digests):
            raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, "comparison digest role invalid")
        _validate_record(self, "comparison_result_digest")


def _authorization_digest(
    cell_id: str,
    config_digest: str,
    fixture_digest: str,
    arm_spec_digest: str,
    initial_state_digest: str,
) -> str:
    return _digest(
        (
            "S2DR_AUTH",
            cell_id,
            config_digest,
            fixture_digest,
            arm_spec_digest,
            initial_state_digest,
        )
    )


def _initial_payload(arm_id: str) -> object:
    if arm_id in {"TSPM1", "R0"}:
        return (
            "s2dr.two-level.normalized.v1",
            0,
            tuple((False, (), (), None, None, 0) for _ in range(3)),
            "auditory.ppb.empty",
            "visual.ppb.empty",
        )
    if arm_id == "B0":
        return ("s2dr.b0.state.v1",)
    if arm_id in {"B1_DIRECT", "B1_BUDGET_MATCHED"}:
        return (f"s2dr.{arm_id.lower()}.state.v1", "auditory.ppb.empty", "visual.ppb.empty")
    if arm_id == "B2":
        return (
            "s2dr.b2.state.v1",
            0,
            None,
            None,
            tuple((f"b2.slot.{index:03d}", False, (), None, None) for index in range(9)),
        )
    if arm_id == "B3":
        return ("s2dr.b3.state.v1", False, (), None, 0)
    if arm_id == "B4":
        return (
            "s2dr.b4.state.v1",
            0,
            None,
            None,
            tuple((f"b4.slot.{index:03d}", False, (), None) for index in range(9)),
        )
    raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "unknown arm")


def _operator_id(arm_id: str) -> str:
    return {
        "TSPM1": "UNCHANGED_PRIVATE_CORE",
        "B0": "NO_FUNCTIONAL_STATE",
        "B1_DIRECT": "TWO_UNCHANGED_PPB1_BANKS_ALL_ORIGINAL_FRAMES_ONCE",
        "B1_BUDGET_MATCHED": "TWO_UNCHANGED_PPB1_BANKS_PREREGISTERED_INDICES_ONLY",
        "B2": "NINE_SLOT_JOINT_ADAPTIVE_ONLINE_PROTOTYPE_OPERATOR",
        "B3": "ONE_TRACE_ALPHA_0_5_EXPIRE_8_OPERATOR",
        "B4": "NINE_ENTRY_FIFO_OPERATOR",
        "R0": "EXACT_GENERIC_TWO_LEVEL_REDUCTION",
    }[arm_id]


def _source_blob_digests() -> tuple[str, ...]:
    return tuple(item["raw_sha256"] for item in _project_source_inventory())


def build_s2dr_registry() -> tuple[
    S2DRConfigRecord,
    tuple[S2DRFixtureRecord, ...],
    tuple[S2DRArmSpec, ...],
    tuple[S2DRCellPlan, ...],
    str,
]:
    """Build the closed 7x8 registry without creating functional states."""

    config = _built(
        S2DRConfigRecord,
        "config_digest",
        schema_version=S2DR_SCHEMA_VERSION,
        candidate_id=S2DR_CANDIDATE_ID,
        parent_artifact_digests=(
            S2EE_CONTRACT_DIGEST,
            S2DR_S2DS_PASS_DIGEST,
            "ace48bfd28e685e706d5ddf1d6647fe8e36190aa87c8fa6d80b2412c8317afed",
            "d5469f35988098020ef5ca413e641f927621dd0adb69b89914b2cbd49e9d7f18",
        ),
        source_blob_digests=_source_blob_digests(),
        auditory_carrier_ids=AUDITORY_CARRIERS,
        visual_carrier_ids=VISUAL_CARRIERS,
        fast_parameters=("tspm1.fast", 3, 0.2, 0.2, 0.5, 2, 8),
        auditory_ppb_parameters=(8, 0.02, 0.05, 3, 256),
        visual_ppb_parameters=(4, 0.01, 0.05, 3, 64),
        arm_resource_words=tuple((arm_id, ARM_RESOURCE_WORDS[arm_id]) for arm_id in ARM_IDS),
        operation_limits=tuple(OPERATION_LIMITS.items()),
    )
    fixtures = tuple(
        _built(
            S2DRFixtureRecord,
            "fixture_digest",
            schema_version=S2DR_SCHEMA_VERSION,
            history_id=history_id,
            formation_pair_ids=HISTORY_DEFINITIONS[history_id][0],
            probe_specs=HISTORY_DEFINITIONS[history_id][1],
            ppb_budget_indices=HISTORY_DEFINITIONS[history_id][2],
            field_clock_id="field.synthetic.s2dq",
            interval_width=10,
            source_id_format="s2dr.source.<modality>",
            formation_frame_id_format=f"s2dr.{history_id.lower()}.formation.<index>.<modality>",
            probe_frame_id_format=f"s2dr.{history_id.lower()}.probe.<index>.<modality>",
        )
        for history_id in HISTORY_IDS
    )
    arms = tuple(
        _built(
            S2DRArmSpec,
            "arm_spec_digest",
            schema_version=S2DR_SCHEMA_VERSION,
            arm_id=arm_id,
            operator_id=_operator_id(arm_id),
            state_schema_id=f"s2dr.{arm_id.lower()}.state.v1",
            resource_words=ARM_RESOURCE_WORDS[arm_id],
            formation_write_limit=293,
            formation_distance_limit=234,
            probe_distance_limit=234,
            probe_write_limit=0,
            initial_state_payload=_initial_payload(arm_id),
            initial_state_digest=_digest(_initial_payload(arm_id)),
        )
        for arm_id in ARM_IDS
    )
    arm_by_id = {arm.arm_id: arm for arm in arms}
    fixture_by_id = {fixture.history_id: fixture for fixture in fixtures}
    plans = []
    for history_id in HISTORY_IDS:
        fixture = fixture_by_id[history_id]
        probe_count = sum(len(pair_ids) for _, pair_ids in fixture.probe_specs)
        for arm_id in ARM_IDS:
            arm = arm_by_id[arm_id]
            cell_id = f"s2dr.cell.{history_id.lower()}.{arm_id.lower()}"
            authorization_digest = _authorization_digest(
                cell_id,
                config.config_digest,
                fixture.fixture_digest,
                arm.arm_spec_digest,
                arm.initial_state_digest,
            )
            plans.append(
                _built(
                    S2DRCellPlan,
                    "cell_plan_digest",
                    schema_version=S2DR_SCHEMA_VERSION,
                    cell_id=cell_id,
                    history_id=history_id,
                    arm_id=arm_id,
                    config_digest=config.config_digest,
                    fixture_digest=fixture.fixture_digest,
                    arm_spec_digest=arm.arm_spec_digest,
                    initial_state_digest=arm.initial_state_digest,
                    formation_call_count=len(fixture.formation_pair_ids),
                    probe_call_count=probe_count,
                    authorization_digest=authorization_digest,
                )
            )
    plans_tuple = tuple(plans)
    registry_digest = _digest(
        {
            "schema_version": S2DR_SCHEMA_VERSION,
            "config_digest": config.config_digest,
            "fixture_digests": tuple(item.fixture_digest for item in fixtures),
            "arm_spec_digests": tuple(item.arm_spec_digest for item in arms),
            "cell_plan_digests": tuple(item.cell_plan_digest for item in plans_tuple),
        }
    )
    return config, fixtures, arms, plans_tuple, registry_digest


@dataclass(frozen=True, slots=True)
class _JointSlot:
    slot_id: str
    occupied: bool
    values: tuple[float, ...]
    support: int | None
    last_selected_step: int | None


@dataclass(frozen=True, slots=True)
class _B2State:
    accepted_count: int
    slots: tuple[_JointSlot, ...]


@dataclass(frozen=True, slots=True)
class _B3State:
    occupied: bool
    values: tuple[float, ...]
    last_formation_step: int | None
    accepted_count: int


@dataclass(frozen=True, slots=True)
class _FIFOEntry:
    slot_id: str
    occupied: bool
    values: tuple[float, ...]
    formation_index: int | None


@dataclass(frozen=True, slots=True)
class _B4State:
    accepted_count: int
    entries: tuple[_FIFOEntry, ...]


@dataclass(frozen=True, slots=True)
class _PPBPairState:
    auditory: PPB1BankState
    visual: PPB1BankState


@dataclass(frozen=True, slots=True)
class _GenericFastSlot:
    slot_id: str
    occupied: bool
    auditory_values: tuple[float, ...]
    visual_values: tuple[float, ...]
    support_count: int | None
    last_selected_step: int | None
    consolidation_count: int


@dataclass(frozen=True, slots=True)
class _GenericFastState:
    accepted_count: int
    auditory_clock_id: str | None
    auditory_end_tick: int | None
    visual_clock_id: str | None
    visual_end_tick: int | None
    slots: tuple[_GenericFastSlot, ...]


@dataclass(frozen=True, slots=True)
class _GenericTwoLevelState:
    generation: int
    fast: _GenericFastState
    auditory_ppb: PPB1BankState
    visual_ppb: PPB1BankState


def _runtime_profile():
    parameters = PPB1ProfileParameters(
        PPB1ModalityParameters(8, 0.02, 0.05, 3, 256),
        PPB1ModalityParameters(4, 0.01, 0.05, 3, 64),
    )
    return bind_ppb1_receptor_profile("browser", parameters)


def _runtime_tspm_config():
    profile = _runtime_profile()
    fast = tspm1.TSPM1FastConfig("tspm1.fast", 3, 0.2, 0.2, 0.5, 2, 8)
    return profile, tspm1.TSPM1ConfigBinding.build(fast, profile)


def initial_s2dr_arm_state(config: S2DRConfigRecord, arm: S2DRArmSpec) -> object:
    if type(config) is not S2DRConfigRecord or type(arm) is not S2DRArmSpec:
        raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "exact config and arm are required")
    if arm.arm_id == "TSPM1":
        _, binding = _runtime_tspm_config()
        return tspm1.initial_tspm1_composite_state(binding)
    if arm.arm_id == "R0":
        profile = _runtime_profile()
        fast = _GenericFastState(
            0,
            None,
            None,
            None,
            None,
            tuple(
                _GenericFastSlot(
                    f"r0.fast.slot.{index:03d}", False, (), (), None, None, 0
                )
                for index in range(3)
            ),
        )
        return _GenericTwoLevelState(
            0,
            fast,
            initial_ppb1_bank_state(profile.auditory_config),
            initial_ppb1_bank_state(profile.visual_config),
        )
    if arm.arm_id == "B0":
        return ()
    if arm.arm_id in {"B1_DIRECT", "B1_BUDGET_MATCHED"}:
        profile = _runtime_profile()
        return _PPBPairState(
            initial_ppb1_bank_state(profile.auditory_config),
            initial_ppb1_bank_state(profile.visual_config),
        )
    if arm.arm_id == "B2":
        return _B2State(0, tuple(_JointSlot(f"b2.slot.{index:03d}", False, (), None, None) for index in range(9)))
    if arm.arm_id == "B3":
        return _B3State(False, (), None, 0)
    if arm.arm_id == "B4":
        return _B4State(0, tuple(_FIFOEntry(f"b4.slot.{index:03d}", False, (), None) for index in range(9)))
    raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "unknown arm")


def _ppb_projection(state: PPB1BankState) -> object:
    return (
        state.schema_version,
        state.bank_id,
        state.config_digest,
        state.accepted_step_count,
        state.source_clock_id,
        state.last_source_window_end_tick,
        tuple(
            (
                slot.slot_id,
                slot.occupied,
                tuple(slot.prototype_values),
                slot.support_count,
                slot.last_selected_step,
            )
            for slot in state.slots
        ),
    )


def _two_level_payload(
    generation: int,
    accepted_count: int,
    fast_slots: Iterable[object],
    auditory_ppb: PPB1BankState,
    visual_ppb: PPB1BankState,
    *,
    fast_slot_prefix: str,
    source_clocks: tuple[str | None, int | None, str | None, int | None],
) -> object:
    fast_slots = tuple(fast_slots)
    if tuple(slot.slot_id for slot in fast_slots) != tuple(
        f"{fast_slot_prefix}.slot.{index:03d}" for index in range(3)
    ):
        raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "fast slot identity or order differs")
    normalized_slots = []
    for slot in fast_slots:
        normalized_slots.append(
            (
                slot.occupied,
                tuple(slot.auditory_values),
                tuple(slot.visual_values),
                slot.support_count,
                slot.last_selected_step,
                slot.consolidation_count,
            )
        )
    auditory_payload = _ppb_projection(auditory_ppb)
    visual_payload = _ppb_projection(visual_ppb)
    if generation == 0:
        # Keep the registered empty descriptor only after checking its sources.
        profile = _runtime_profile()
        expected_banks = tuple(
            (
                config.schema_version,
                config.bank_id,
                config.digest(),
                0,
                None,
                None,
                tuple(
                    (f"{config.bank_id}.slot.{index:03d}", False, (), None, None)
                    for index in range(config.capacity)
                ),
            )
            for config in (profile.auditory_config, profile.visual_config)
        )
        if (
            accepted_count != 0
            or source_clocks != (None, None, None, None)
            or tuple(normalized_slots) != tuple((False, (), (), None, None, 0) for _ in range(3))
            or (auditory_payload, visual_payload) != expected_banks
        ):
            raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "initial two-level identity differs")
        return _initial_payload("R0")
    return (
        "s2dr.two-level.normalized.v1",
        generation,
        accepted_count,
        source_clocks,
        tuple(normalized_slots),
        auditory_payload,
        visual_payload,
    )


def _state_payload(arm_id: str, state: object) -> object:
    if arm_id == "TSPM1":
        if type(state) is not tspm1.TSPM1CompositeState:
            raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "TSPM-1 state required")
        return _two_level_payload(
            state.generation,
            state.fast_state.accepted_exposure_count,
            state.fast_state.slots,
            state.auditory_ppb1_state,
            state.visual_ppb1_state,
            fast_slot_prefix="tspm1.fast",
            source_clocks=(
                state.fast_state.auditory_source_clock_id,
                state.fast_state.auditory_last_end_tick,
                state.fast_state.visual_source_clock_id,
                state.fast_state.visual_last_end_tick,
            ),
        )
    if arm_id == "R0":
        if type(state) is not _GenericTwoLevelState:
            raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "R0 state required")
        return _two_level_payload(
            state.generation,
            state.fast.accepted_count,
            state.fast.slots,
            state.auditory_ppb,
            state.visual_ppb,
            fast_slot_prefix="r0.fast",
            source_clocks=(
                state.fast.auditory_clock_id,
                state.fast.auditory_end_tick,
                state.fast.visual_clock_id,
                state.fast.visual_end_tick,
            ),
        )
    if arm_id == "B0":
        if state != ():
            raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "B0 state required")
        return _initial_payload("B0")
    if arm_id in {"B1_DIRECT", "B1_BUDGET_MATCHED"}:
        if type(state) is not _PPBPairState:
            raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "PPB pair state required")
        if state.auditory.accepted_step_count == state.visual.accepted_step_count == 0:
            return _initial_payload(arm_id)
    if arm_id == "B2" and type(state) is _B2State and state.accepted_count == 0:
        return _initial_payload("B2")
    if arm_id == "B3" and type(state) is _B3State and state.accepted_count == 0:
        return _initial_payload("B3")
    if arm_id == "B4" and type(state) is _B4State and state.accepted_count == 0:
        return _initial_payload("B4")
    return _canonical(state)


def _joint_values(pair_id: str) -> tuple[float, ...]:
    try:
        auditory, visual = PAIR_SCALARS[pair_id]
    except KeyError as exc:
        raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "unknown pair") from exc
    return tuple(auditory for _ in AUDITORY_CARRIERS) + tuple(visual for _ in VISUAL_CARRIERS)


def _world() -> BrowserWorldContract:
    return BrowserWorldContract(
        contract_id="synthetic.s2dr.world.v1",
        startup_frame_count=1,
        start_lead_ns=1,
        movement_cycles=1,
        tone_frequency_hz=100.0,
        phases=(
            BrowserWorldPhase("rest.before", 10, "static", 0.0),
            BrowserWorldPhase("change", 10, "moving", 0.2),
            BrowserWorldPhase("rest.after", 10, "static", 0.0),
        ),
    )


def _sequence(modality_config, scalar: float, frame_index: int, history_id: str, role: str):
    start = (frame_index - 1) * 10
    frame = ReceptorContactFrame(
        modality_config.modality_id,
        modality_config.geometry_id,
        f"s2dr.{history_id.lower()}.{role}.{frame_index:03d}.{modality_config.modality_id}",
        f"s2dr.source.{modality_config.modality_id}",
        start,
        start + 10,
        modality_config.carrier_ids,
        tuple(scalar for _ in modality_config.carrier_ids),
    )
    timed = OrganismTimedReceptorFrame(frame, CommonFieldTime("field.synthetic.s2dq", start, start + 10))
    return ReceptorTimeSequence(modality_config.modality_id, modality_config.geometry_id, "field.synthetic.s2dq", (timed,))


def _bound_pair(history_id: str, pair_id: str, frame_index: int, role: str):
    profile = _runtime_profile()
    auditory_scalar, visual_scalar = PAIR_SCALARS[pair_id]
    auditory = _sequence(profile.auditory_config, auditory_scalar, frame_index, history_id, role)
    visual = _sequence(profile.visual_config, visual_scalar, frame_index, history_id, role)
    world = _world()
    batch = BrowserReceptorSequenceBatch(world.contract_id, world.digest(), (auditory, visual))
    envelope = bind_ppb1_active_receptor_batch(f"s2dr.binding.{history_id.lower()}.{role}.{frame_index:03d}", world, batch, profile)
    return profile, envelope, envelope.auditory_stream.timed_frames[0], envelope.visual_stream.timed_frames[0]


def _validate_operator_inputs(
    config: S2DRConfigRecord,
    fixture: S2DRFixtureRecord,
    arm: S2DRArmSpec,
) -> None:
    if type(config) is not S2DRConfigRecord or type(fixture) is not S2DRFixtureRecord or type(arm) is not S2DRArmSpec:
        raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "exact registry records are required")


def _split_distance(left: tuple[float, ...], right: tuple[float, ...]) -> tuple[float, float]:
    return (
        normalized_mean_l1_distance(left[:8], right[:8]),
        normalized_mean_l1_distance(left[8:], right[8:]),
    )


def _advance_b2(state: _B2State, values: tuple[float, ...], formation_index: int):
    if type(state) is not _B2State:
        raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "B2 state required")
    slots = []
    for slot in state.slots:
        if slot.occupied and slot.last_selected_step is not None and formation_index - slot.last_selected_step >= 8:
            slots.append(_JointSlot(slot.slot_id, False, (), None, None))
        else:
            slots.append(slot)
    matches = []
    distance_terms = 0
    for index, slot in enumerate(slots):
        if slot.occupied:
            auditory, visual = _split_distance(values, slot.values)
            distance_terms += 26
            if auditory <= 0.2 and visual <= 0.2:
                matches.append((max(auditory, visual), auditory + visual, slot.slot_id, index))
    if matches:
        _, _, _, selected_index = min(matches)
        selected = slots[selected_index]
        updated = tuple(0.5 * old + 0.5 * current for old, current in zip(selected.values, values, strict=True))
        slots[selected_index] = _JointSlot(
            selected.slot_id,
            True,
            updated,
            min(3, (selected.support or 0) + 1),
            formation_index,
        )
        event = "B2_UPDATED"
    else:
        free = [index for index, slot in enumerate(slots) if not slot.occupied]
        if free:
            selected_index = min(free, key=lambda index: slots[index].slot_id)
            event = "B2_CREATED"
        else:
            selected_index = min(
                range(len(slots)),
                key=lambda index: (slots[index].last_selected_step, slots[index].slot_id),
            )
            event = "B2_REPLACED"
        selected = slots[selected_index]
        slots[selected_index] = _JointSlot(selected.slot_id, True, values, 1, formation_index)
    poststate = _B2State(state.accepted_count + 1, tuple(slots))
    return poststate, {"event": event, "slot_id": slots[selected_index].slot_id}, (29, distance_terms)


def _advance_b3(state: _B3State, values: tuple[float, ...], formation_index: int):
    if type(state) is not _B3State:
        raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "B3 state required")
    if state.occupied:
        updated = tuple(0.5 * old + 0.5 * current for old, current in zip(state.values, values, strict=True))
        event = "B3_UPDATED"
    else:
        updated = values
        event = "B3_CREATED"
    return _B3State(True, updated, formation_index, state.accepted_count + 1), {"event": event}, (29, 26 if state.occupied else 0)


def _advance_b4(state: _B4State, values: tuple[float, ...], formation_index: int):
    if type(state) is not _B4State:
        raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "B4 state required")
    entries = list(state.entries)
    free = [index for index, entry in enumerate(entries) if not entry.occupied]
    if free:
        selected_index = min(free, key=lambda index: entries[index].slot_id)
        event = "B4_APPENDED"
    else:
        selected_index = min(
            range(len(entries)),
            key=lambda index: (entries[index].formation_index, entries[index].slot_id),
        )
        event = "B4_EVICTED_AND_APPENDED"
    selected = entries[selected_index]
    entries[selected_index] = _FIFOEntry(selected.slot_id, True, values, formation_index)
    return _B4State(state.accepted_count + 1, tuple(entries)), {"event": event, "slot_id": selected.slot_id}, (27, 0)


def _advance_r0(
    state: _GenericTwoLevelState,
    auditory_frame: ReceptorContactFrame,
    visual_frame: ReceptorContactFrame,
) -> tuple[_GenericTwoLevelState, object, tuple[int, int]]:
    if type(state) is not _GenericTwoLevelState:
        raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "generic R0 state required")
    auditory_values = tuple(auditory_frame.values)
    visual_values = tuple(visual_frame.values)
    step = state.fast.accepted_count + 1
    slots = []
    for slot in state.fast.slots:
        if (
            slot.occupied
            and slot.last_selected_step is not None
            and step - slot.last_selected_step >= 8
        ):
            slots.append(_GenericFastSlot(slot.slot_id, False, (), (), None, None, 0))
        else:
            slots.append(slot)
    matches = []
    any_auditory_match = False
    any_visual_match = False
    for index, slot in enumerate(slots):
        if not slot.occupied:
            continue
        auditory_distance = normalized_mean_l1_distance(auditory_values, slot.auditory_values)
        visual_distance = normalized_mean_l1_distance(visual_values, slot.visual_values)
        auditory_match = auditory_distance <= 0.2
        visual_match = visual_distance <= 0.2
        any_auditory_match = any_auditory_match or auditory_match
        any_visual_match = any_visual_match or visual_match
        if auditory_match and visual_match:
            matches.append(
                (
                    max(auditory_distance, visual_distance),
                    auditory_distance + visual_distance,
                    index,
                    auditory_distance,
                    visual_distance,
                )
            )
    consolidation_eligible = False
    if matches:
        _, _, selected_index, auditory_distance, visual_distance = min(matches)
        selected = slots[selected_index]
        support = min(2, (selected.support_count or 0) + 1)
        slots[selected_index] = _GenericFastSlot(
            selected.slot_id,
            True,
            tuple(0.5 * old + 0.5 * current for old, current in zip(selected.auditory_values, auditory_values, strict=True)),
            tuple(0.5 * old + 0.5 * current for old, current in zip(selected.visual_values, visual_values, strict=True)),
            support,
            step,
            selected.consolidation_count,
        )
        event = "FAST_UPDATED"
        consolidation_eligible = support >= 2
    else:
        free = [index for index, slot in enumerate(slots) if not slot.occupied]
        if free:
            selected_index = min(free)
            event = "FAST_CREATED"
        else:
            selected_index = min(
                range(len(slots)),
                key=lambda index: (slots[index].last_selected_step, index),
            )
            event = "FAST_REPLACED"
        selected = slots[selected_index]
        slots[selected_index] = _GenericFastSlot(
            selected.slot_id,
            True,
            auditory_values,
            visual_values,
            1,
            step,
            0,
        )
        auditory_distance = None
        visual_distance = None
    fast = _GenericFastState(
        step,
        auditory_frame.clock_id,
        auditory_frame.window_end_tick,
        visual_frame.clock_id,
        visual_frame.window_end_tick,
        tuple(slots),
    )
    if consolidation_eligible:
        auditory_result = advance_ppb1_bank(
            _runtime_profile().auditory_config,
            state.auditory_ppb,
            auditory_frame,
        )
        visual_result = advance_ppb1_bank(
            _runtime_profile().visual_config,
            state.visual_ppb,
            visual_frame,
        )
        selected = fast.slots[selected_index]
        updated_slots = list(fast.slots)
        updated_slots[selected_index] = _GenericFastSlot(
            selected.slot_id,
            selected.occupied,
            selected.auditory_values,
            selected.visual_values,
            selected.support_count,
            selected.last_selected_step,
            selected.consolidation_count + 1,
        )
        fast = _GenericFastState(
            fast.accepted_count,
            fast.auditory_clock_id,
            fast.auditory_end_tick,
            fast.visual_clock_id,
            fast.visual_end_tick,
            tuple(updated_slots),
        )
        auditory_ppb = auditory_result.poststate
        visual_ppb = visual_result.poststate
        consolidation_status = "COMMITTED"
    else:
        auditory_ppb = state.auditory_ppb
        visual_ppb = state.visual_ppb
        consolidation_status = "NOT_ELIGIBLE"
    poststate = _GenericTwoLevelState(
        state.generation + 1,
        fast,
        auditory_ppb,
        visual_ppb,
    )
    event_payload = {
        "event": event,
        "consolidation_status": consolidation_status,
        "generic_decision_digest": _digest(
            (
                "s2dr.r0.generic.transition.v1",
                state.generation,
                step,
                selected_index,
                auditory_distance,
                visual_distance,
                consolidation_status,
            )
        ),
    }
    return poststate, event_payload, (293, 234)


def _advance_s2dr_arm_unmetered(
    config: S2DRConfigRecord,
    fixture: S2DRFixtureRecord,
    arm: S2DRArmSpec,
    prestate: object,
    pair_id: str,
    formation_index: int,
) -> tuple[object, object, tuple[int, int]]:
    """Advance exactly one private arm by one registered formation frame."""

    _validate_operator_inputs(config, fixture, arm)
    if isinstance(formation_index, bool) or not isinstance(formation_index, int) or not 1 <= formation_index <= len(fixture.formation_pair_ids):
        raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "formation index is invalid")
    if fixture.formation_pair_ids[formation_index - 1] != pair_id:
        raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "formation pair is not registered")
    values = _joint_values(pair_id)
    if arm.arm_id == "B0":
        if prestate != ():
            raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "B0 state changed")
        return (), {"event": "B0_IGNORED", "formation_index": formation_index}, (0, 0)
    if arm.arm_id == "B2":
        return _advance_b2(prestate, values, formation_index)
    if arm.arm_id == "B3":
        return _advance_b3(prestate, values, formation_index)
    if arm.arm_id == "B4":
        return _advance_b4(prestate, values, formation_index)
    profile, envelope, auditory, visual = _bound_pair(
        fixture.history_id, pair_id, formation_index, "formation"
    )
    if arm.arm_id in {"B1_DIRECT", "B1_BUDGET_MATCHED"}:
        if type(prestate) is not _PPBPairState:
            raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "PPB pair state required")
        if arm.arm_id == "B1_BUDGET_MATCHED" and formation_index not in fixture.ppb_budget_indices:
            return prestate, {"event": "B1_BUDGET_SKIPPED", "formation_index": formation_index}, (0, 0)
        auditory_result = advance_ppb1_bank(profile.auditory_config, prestate.auditory, auditory.timed_frame.frame)
        visual_result = advance_ppb1_bank(profile.visual_config, prestate.visual, visual.timed_frame.frame)
        return (
            _PPBPairState(auditory_result.poststate, visual_result.poststate),
            {
                "event": "B1_PPB1_ADVANCED",
                "auditory_event": auditory_result.readout.event,
                "visual_event": visual_result.readout.event,
            },
            (0, 0),  # Counts are supplied only by the enclosing operation meter.
        )
    if arm.arm_id == "R0":
        return _advance_r0(
            prestate,
            auditory.timed_frame.frame,
            visual.timed_frame.frame,
        )
    _, binding = _runtime_tspm_config()
    if arm.arm_id == "TSPM1":
        if type(prestate) is not tspm1.TSPM1CompositeState:
            raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "TSPM-1 state required")
        tspm_prestate = prestate
    else:
        raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "unknown arm")
    exposure = tspm1.bind_tspm1_exposure(binding, envelope, auditory, visual)
    owner = tspm1.TSPM1CoordinatorOwner(
        f"s2dr.tspm1.owner.{fixture.history_id.lower()}.{formation_index:03d}",
        f"s2dr.tspm1.authorization.{fixture.history_id.lower()}.{formation_index:03d}",
        f"s2dr.tspm1.consume.{fixture.history_id.lower()}.{formation_index:03d}",
        binding.config_binding_digest,
        tspm_prestate.composite_state_digest,
        exposure.exposure_digest,
    )
    result = owner.consume_once(binding, tspm_prestate, exposure)
    event = {
        "event": result.receipt.primary_event,
        "consolidation_status": result.receipt.consolidation_status,
        "receipt_digest": result.receipt.receipt_digest,
    }
    return result.poststate, event, (293, 234)


def _s1wu_evidence(
    bank_config,
    bank_state: PPB1BankState,
    frame: ReceptorContactFrame,
    probe_id: str,
) -> tuple[str, S1WUReadOnlyPerceptualFinding | None, tuple[float, ...] | None]:
    if bank_state.accepted_step_count == 0:
        return "SLOW_UNAVAILABLE", None, None
    finding = probe_s1wu_perceptual_state(bank_config, bank_state, frame, probe_id)
    if type(finding) is not S1WUReadOnlyPerceptualFinding:
        raise S2DRError(S2DR_ATOMIC_RESULT_REQUIRED, "exact S1WU finding required")
    if not finding.recognized:
        return "SLOW_NOT_RECOGNIZED", finding, None
    matching = tuple(
        slot
        for slot in bank_state.slots
        if slot.slot_id == finding.selected_slot_id and slot.occupied
    )
    if len(matching) != 1:
        raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "S1WU selected slot is not unique")
    return "SLOW_RECOGNIZED", finding, tuple(matching[0].prototype_values)


def _finding_payload(
    fixture: S2DRFixtureRecord,
    arm: S2DRArmSpec,
    checkpoint: int,
    pair_id: str,
    recognized: bool,
    context_source: str,
    observed_state_digest: str,
    *,
    fast_recognized: bool | None = None,
    fast_slot_id: str | None = None,
    fast_slot_digest: str | None = None,
    auditory_fast_distance: float | None = None,
    visual_fast_distance: float | None = None,
    auditory_slow_status: str | None = None,
    visual_slow_status: str | None = None,
    auditory_slow_finding_digest: str | None = None,
    visual_slow_finding_digest: str | None = None,
    auditory_selected_slot_id: str | None = None,
    visual_selected_slot_id: str | None = None,
    auditory_selected_prototype_digest: str | None = None,
    visual_selected_prototype_digest: str | None = None,
    auditory_slow_distance: float | None = None,
    visual_slow_distance: float | None = None,
    selected_values: tuple[tuple[float, ...], tuple[float, ...]] | None = None,
) -> dict[str, object]:
    selected_digest = None
    if selected_values is not None:
        selected_digest = _digest(("S2DR_SELECTED_AV_PAYLOAD_V1", selected_values[0], selected_values[1]))
    return {
        "history_id": fixture.history_id,
        "arm_id": arm.arm_id,
        "checkpoint": checkpoint,
        "pair_id": pair_id,
        "recognized": recognized,
        "context_source": context_source,
        "fast_recognized": fast_recognized,
        "fast_slot_id": fast_slot_id,
        "fast_slot_digest": fast_slot_digest,
        "auditory_fast_distance": auditory_fast_distance,
        "visual_fast_distance": visual_fast_distance,
        "auditory_slow_status": auditory_slow_status,
        "visual_slow_status": visual_slow_status,
        "auditory_slow_finding_digest": auditory_slow_finding_digest,
        "visual_slow_finding_digest": visual_slow_finding_digest,
        "auditory_selected_slot_id": auditory_selected_slot_id,
        "visual_selected_slot_id": visual_selected_slot_id,
        "auditory_selected_prototype_digest": auditory_selected_prototype_digest,
        "visual_selected_prototype_digest": visual_selected_prototype_digest,
        "auditory_slow_distance": auditory_slow_distance,
        "visual_slow_distance": visual_slow_distance,
        "selected_av_payload_digest": selected_digest,
        "selected_auditory_values": selected_values[0] if recognized and selected_values else None,
        "selected_visual_values": selected_values[1] if recognized and selected_values else None,
        "observed_state_digest": observed_state_digest,
    }


def _probe_joint_slots(slots: Iterable[tuple[str, tuple[float, ...], int]], values: tuple[float, ...]):
    candidates = []
    for slot_id, stored, rank_step in slots:
        auditory, visual = _split_distance(values, stored)
        if auditory <= 0.2 and visual <= 0.2:
            candidates.append((max(auditory, visual), auditory + visual, -rank_step, slot_id, stored, auditory, visual))
    return min(candidates, default=None)


def _probe_s2dr_arm_unmetered(
    config: S2DRConfigRecord,
    fixture: S2DRFixtureRecord,
    arm: S2DRArmSpec,
    state: object,
    pair_id: str,
    probe_index: int,
) -> tuple[object, int]:
    """Read one registered probe without modifying the arm state."""

    _validate_operator_inputs(config, fixture, arm)
    flattened = tuple((after, pair) for after, pairs in fixture.probe_specs for pair in pairs)
    if isinstance(probe_index, bool) or not isinstance(probe_index, int) or not 1 <= probe_index <= len(flattened):
        raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "probe index is invalid")
    checkpoint, expected_pair = flattened[probe_index - 1]
    if pair_id != expected_pair:
        raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "probe pair is stale or foreign")
    state_payload = _state_payload(arm.arm_id, state)
    state_digest = _digest(state_payload)
    values = _joint_values(pair_id)
    if arm.arm_id == "B0":
        return _finding_payload(fixture, arm, checkpoint, pair_id, False, "NO_COMPLETE_CONTEXT", state_digest), 0
    if arm.arm_id == "B2":
        assert type(state) is _B2State
        occupied = ((slot.slot_id, slot.values, slot.last_selected_step or 0) for slot in state.slots if slot.occupied)
        selected = _probe_joint_slots(occupied, values)
        recognized = selected is not None
        return _finding_payload(
            fixture, arm, checkpoint, pair_id, recognized,
            "ADAPTIVE_PROTOTYPE_CONTEXT" if recognized else "NO_COMPLETE_CONTEXT",
            state_digest,
            fast_recognized=recognized,
            fast_slot_id=selected[3] if selected else None,
            auditory_fast_distance=selected[5] if selected else None,
            visual_fast_distance=selected[6] if selected else None,
            selected_values=(selected[4][:8], selected[4][8:]) if selected else None,
        ), sum(26 for slot in state.slots if slot.occupied)
    if arm.arm_id == "B3":
        assert type(state) is _B3State
        selected = None
        if state.occupied and state.last_formation_step is not None and state.accepted_count - state.last_formation_step < 8:
            auditory, visual = _split_distance(values, state.values)
            if auditory <= 0.2 and visual <= 0.2:
                selected = (auditory, visual)
        return _finding_payload(
            fixture, arm, checkpoint, pair_id, selected is not None,
            "REVERBERATION_CONTEXT" if selected else "NO_COMPLETE_CONTEXT", state_digest,
            fast_recognized=selected is not None,
            auditory_fast_distance=selected[0] if selected else None,
            visual_fast_distance=selected[1] if selected else None,
            selected_values=(state.values[:8], state.values[8:]) if selected else None,
        ), 26 if state.occupied else 0
    if arm.arm_id == "B4":
        assert type(state) is _B4State
        occupied = ((entry.slot_id, entry.values, entry.formation_index or 0) for entry in state.entries if entry.occupied)
        selected = _probe_joint_slots(occupied, values)
        return _finding_payload(
            fixture, arm, checkpoint, pair_id, selected is not None,
            "FIFO_CONTEXT" if selected else "NO_COMPLETE_CONTEXT", state_digest,
            fast_recognized=selected is not None,
            fast_slot_id=selected[3] if selected else None,
            auditory_fast_distance=selected[5] if selected else None,
            visual_fast_distance=selected[6] if selected else None,
            selected_values=(selected[4][:8], selected[4][8:]) if selected else None,
        ), sum(26 for entry in state.entries if entry.occupied)

    frame_index = len(fixture.formation_pair_ids) + probe_index
    profile, envelope, auditory, visual = _bound_pair(fixture.history_id, pair_id, frame_index, "probe")
    auditory_values = tuple(auditory.timed_frame.frame.values)
    visual_values = tuple(visual.timed_frame.frame.values)
    if arm.arm_id in {"B1_DIRECT", "B1_BUDGET_MATCHED"}:
        if type(state) is not _PPBPairState:
            raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "PPB pair state required")
        probe_token = _digest((fixture.history_id, arm.arm_id, checkpoint, pair_id, probe_index))
        auditory_status, auditory_finding, auditory_selected_values = _s1wu_evidence(
            profile.auditory_config,
            state.auditory,
            auditory.timed_frame.frame,
            f"s2dr.b1.probe.auditory.{probe_token}",
        )
        visual_status, visual_finding, visual_selected_values = _s1wu_evidence(
            profile.visual_config,
            state.visual,
            visual.timed_frame.frame,
            f"s2dr.b1.probe.visual.{probe_token}",
        )
        recognized = auditory_status == visual_status == "SLOW_RECOGNIZED"
        selected_values = (
            (auditory_selected_values, visual_selected_values)
            if recognized
            else None
        )
        return _finding_payload(
            fixture, arm, checkpoint, pair_id, recognized,
            "SLOW_PPB1_CONTEXT" if recognized else "NO_COMPLETE_CONTEXT", state_digest,
            auditory_slow_status=auditory_status,
            visual_slow_status=visual_status,
            auditory_slow_finding_digest=auditory_finding.finding_digest if auditory_finding else None,
            visual_slow_finding_digest=visual_finding.finding_digest if visual_finding else None,
            auditory_selected_slot_id=auditory_finding.selected_slot_id if auditory_finding and auditory_finding.recognized else None,
            visual_selected_slot_id=visual_finding.selected_slot_id if visual_finding and visual_finding.recognized else None,
            auditory_selected_prototype_digest=auditory_finding.selected_prototype_digest if auditory_finding and auditory_finding.recognized else None,
            visual_selected_prototype_digest=visual_finding.selected_prototype_digest if visual_finding and visual_finding.recognized else None,
            auditory_slow_distance=auditory_finding.match_distance if auditory_finding and auditory_finding.recognized else None,
            visual_slow_distance=visual_finding.match_distance if visual_finding and visual_finding.recognized else None,
            selected_values=selected_values,
        ), 8 * sum(slot.occupied for slot in state.auditory.slots) + 18 * sum(slot.occupied for slot in state.visual.slots)

    if arm.arm_id == "R0":
        if type(state) is not _GenericTwoLevelState:
            raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "generic R0 state required")
        matches = []
        for slot in state.fast.slots:
            if not slot.occupied:
                continue
            auditory_distance = normalized_mean_l1_distance(auditory_values, slot.auditory_values)
            visual_distance = normalized_mean_l1_distance(visual_values, slot.visual_values)
            if auditory_distance <= 0.2 and visual_distance <= 0.2:
                matches.append((max(auditory_distance, visual_distance), auditory_distance + visual_distance, slot.slot_id, auditory_distance, visual_distance, slot))
        if matches:
            _, _, _, auditory_fast_distance, visual_fast_distance, fast_slot = min(matches)
        else:
            fast_slot = None
            auditory_fast_distance = None
            visual_fast_distance = None
        probe_token = _digest((fixture.history_id, arm.arm_id, checkpoint, pair_id, probe_index))
        auditory_status, auditory_finding, auditory_selected_values = _s1wu_evidence(
            profile.auditory_config,
            state.auditory_ppb,
            auditory.timed_frame.frame,
            f"s2dr.r0.probe.auditory.{probe_token}",
        )
        visual_status, visual_finding, visual_selected_values = _s1wu_evidence(
            profile.visual_config,
            state.visual_ppb,
            visual.timed_frame.frame,
            f"s2dr.r0.probe.visual.{probe_token}",
        )
        both_slow = auditory_status == visual_status == "SLOW_RECOGNIZED"
        context_source = "SLOW_PPB1_CONTEXT" if both_slow else ("FAST_ASSOCIATIVE_CONTEXT" if fast_slot else "NO_COMPLETE_CONTEXT")
        selected_values = (
            (auditory_selected_values, visual_selected_values)
            if both_slow
            else ((fast_slot.auditory_values, fast_slot.visual_values) if fast_slot else None)
        )
        return _finding_payload(
            fixture,
            arm,
            checkpoint,
            pair_id,
            context_source != "NO_COMPLETE_CONTEXT",
            context_source,
            state_digest,
            fast_recognized=fast_slot is not None,
            fast_slot_id=fast_slot.slot_id if fast_slot else None,
            fast_slot_digest=_digest(_canonical(fast_slot)) if fast_slot else None,
            auditory_fast_distance=auditory_fast_distance,
            visual_fast_distance=visual_fast_distance,
            auditory_slow_status=auditory_status,
            visual_slow_status=visual_status,
            auditory_slow_finding_digest=auditory_finding.finding_digest if auditory_finding else None,
            visual_slow_finding_digest=visual_finding.finding_digest if visual_finding else None,
            auditory_selected_slot_id=auditory_finding.selected_slot_id if auditory_finding and auditory_finding.recognized else None,
            visual_selected_slot_id=visual_finding.selected_slot_id if visual_finding and visual_finding.recognized else None,
            auditory_selected_prototype_digest=auditory_finding.selected_prototype_digest if auditory_finding and auditory_finding.recognized else None,
            visual_selected_prototype_digest=visual_finding.selected_prototype_digest if visual_finding and visual_finding.recognized else None,
            auditory_slow_distance=auditory_finding.match_distance if auditory_finding and auditory_finding.recognized else None,
            visual_slow_distance=visual_finding.match_distance if visual_finding and visual_finding.recognized else None,
            selected_values=selected_values,
        ), 234

    _, binding = _runtime_tspm_config()
    if arm.arm_id == "TSPM1":
        if type(state) is not tspm1.TSPM1CompositeState:
            raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "TSPM-1 state required")
        composite = state
    else:
        raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "unknown arm")
    probe = tspm1.bind_tspm1_probe(binding, envelope, auditory, visual)
    finding = tspm1.probe_tspm1_read_only(binding, composite, probe)
    fast_values = None
    if finding.fast_recognized:
        slot = next(slot for slot in composite.fast_state.slots if slot.slot_id == finding.fast_slot_id)
        fast_values = (slot.auditory_values, slot.visual_values)
    auditory_status, auditory_s1wu, auditory_selected_values = _s1wu_evidence(
        profile.auditory_config,
        composite.auditory_ppb1_state,
        auditory.timed_frame.frame,
        f"tspm1.probe.auditory.{probe.probe_digest}",
    )
    visual_status, visual_s1wu, visual_selected_values = _s1wu_evidence(
        profile.visual_config,
        composite.visual_ppb1_state,
        visual.timed_frame.frame,
        f"tspm1.probe.visual.{probe.probe_digest}",
    )
    if (
        auditory_status != finding.auditory_slow_status
        or visual_status != finding.visual_slow_status
        or (auditory_s1wu.finding_digest if auditory_s1wu else None) != finding.auditory_s1wu_finding_digest
        or (visual_s1wu.finding_digest if visual_s1wu else None) != finding.visual_s1wu_finding_digest
    ):
        raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "TSPM slow finding is not bound to S1WU evidence")
    slow_values = None
    if auditory_status == visual_status == "SLOW_RECOGNIZED":
        slow_values = (auditory_selected_values, visual_selected_values)
    selected_values = slow_values if finding.context_source == "SLOW_PPB1_CONTEXT" else fast_values
    normalized = _finding_payload(
        fixture, arm, checkpoint, pair_id,
        finding.context_source != "NO_COMPLETE_CONTEXT",
        finding.context_source,
        state_digest,
        fast_recognized=finding.fast_recognized,
        fast_slot_id=finding.fast_slot_id,
        fast_slot_digest=finding.fast_slot_digest,
        auditory_fast_distance=finding.auditory_fast_distance,
        visual_fast_distance=finding.visual_fast_distance,
        auditory_slow_status=finding.auditory_slow_status,
        visual_slow_status=finding.visual_slow_status,
        auditory_slow_finding_digest=finding.auditory_s1wu_finding_digest,
        visual_slow_finding_digest=finding.visual_s1wu_finding_digest,
        auditory_selected_slot_id=auditory_s1wu.selected_slot_id if auditory_s1wu and auditory_s1wu.recognized else None,
        visual_selected_slot_id=visual_s1wu.selected_slot_id if visual_s1wu and visual_s1wu.recognized else None,
        auditory_selected_prototype_digest=auditory_s1wu.selected_prototype_digest if auditory_s1wu and auditory_s1wu.recognized else None,
        visual_selected_prototype_digest=visual_s1wu.selected_prototype_digest if visual_s1wu and visual_s1wu.recognized else None,
        auditory_slow_distance=auditory_s1wu.match_distance if auditory_s1wu and auditory_s1wu.recognized else None,
        visual_slow_distance=visual_s1wu.match_distance if visual_s1wu and visual_s1wu.recognized else None,
        selected_values=selected_values,
    )
    return normalized, 234


@dataclass(frozen=True, slots=True)
class S2DRCellOwnerSnapshot:
    owner_id: str
    cell_id: str
    authorization_digest: str
    consumption_id: str
    status: str
    cell_plan_digest: str
    internal_error_code: str | None
    committed_result_digest: str | None


def _budget_tuples(counts: Sequence[int], bound: int) -> tuple[
    tuple[tuple[int, int], ...],
    tuple[tuple[int, int], ...],
    tuple[tuple[int, int], ...],
]:
    bounds = tuple((index, bound) for index in range(1, len(counts) + 1))
    used = tuple((index, int(value)) for index, value in enumerate(counts, start=1))
    remaining = tuple((index, bound - int(value)) for index, value in enumerate(counts, start=1))
    return bounds, used, remaining


def _make_budget_receipt(
    plan: S2DRCellPlan,
    arm: S2DRArmSpec,
    formation_writes: Sequence[int],
    formation_distances: Sequence[int],
    probe_distances: Sequence[int],
    probe_writes: Sequence[int],
) -> S2DRBudgetReceipt:
    fw_bounds, fw_counts, fw_remaining = _budget_tuples(formation_writes, arm.formation_write_limit)
    fd_bounds, fd_counts, fd_remaining = _budget_tuples(formation_distances, arm.formation_distance_limit)
    pd_bounds, pd_counts, pd_remaining = _budget_tuples(probe_distances, arm.probe_distance_limit)
    pw_bounds, pw_counts, pw_remaining = _budget_tuples(probe_writes, arm.probe_write_limit)
    return _built(
        S2DRBudgetReceipt,
        "budget_receipt_digest",
        schema_version=S2DR_SCHEMA_VERSION,
        cell_id=plan.cell_id,
        cell_plan_digest=plan.cell_plan_digest,
        resource_words_bound=arm.resource_words,
        resource_words_used=arm.resource_words,
        formation_write_bounds=fw_bounds,
        formation_write_counts=fw_counts,
        formation_distance_bounds=fd_bounds,
        formation_distance_counts=fd_counts,
        probe_distance_bounds=pd_bounds,
        probe_distance_counts=pd_counts,
        probe_write_bounds=pw_bounds,
        probe_write_counts=pw_counts,
        remaining_resource_words=0,
        remaining_formation_write_budget=fw_remaining,
        remaining_formation_distance_budget=fd_remaining,
        remaining_probe_distance_budget=pd_remaining,
        remaining_probe_write_budget=pw_remaining,
    )


def _expected_budget_keys(plan: S2DRCellPlan) -> tuple[tuple[int, ...], tuple[int, ...]]:
    return (
        tuple(range(1, plan.formation_call_count + 1)),
        tuple(range(1, plan.probe_call_count + 1)),
    )


def _require(condition: bool, detail: str) -> None:
    if not condition:
        raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, detail)


def _validate_cost(plan, arm, cost):
    contract = _ee_contract()["operation_contract"]
    keys = {"cell_id", "phase", "operation_index", "distance_evidence", "write_evidence",
            "functional_terms", "validation_terms", "total_distance_terms", "functional_write_words",
            "ppb_call_evidence", "native_prestate_payload", "native_poststate_payload", "native_event",
            "prestate_payload", "poststate_payload", "prestate_digest", "poststate_digest", "cost_digest"}
    _require(type(cost) is dict and set(cost) == keys, "operation evidence fields differ")
    _require(cost["cost_digest"] == _digest({k: v for k, v in cost.items() if k != "cost_digest"}),
             "operation evidence changed")
    _require(cost["cell_id"] == plan.cell_id and cost["phase"] in {"FORMATION", "PROBE"},
             "operation identity differs")
    index, phase = cost["operation_index"], cost["phase"]
    count = plan.formation_call_count if phase == "FORMATION" else plan.probe_call_count
    _require(type(index) is int and 1 <= index <= count, "operation index differs")
    for key in ("functional_terms", "validation_terms", "total_distance_terms", "functional_write_words"):
        _require(type(cost[key]) is int and cost[key] >= 0, "operation count is not a nonnegative integer")
    for prefix in ("prestate", "poststate"):
        _require(cost[prefix + "_digest"] == _digest(cost[prefix + "_payload"]), "operation state seal differs")
    inventory = {item["repository_relative_path"]: item for item in _project_source_inventory()}
    for ordinal, item in enumerate(cost["distance_evidence"], 1):
        _require(set(item) == set(contract["distance_evidence_fields"]), "distance fields differ")
        _require((item["cell_id"], item["phase"], item["operation_index"], item["ordinal"])
                 == (plan.cell_id, phase, index, ordinal), "distance order differs")
        _require(type(item["dimension"]) is int and item["dimension"] in (8, 18)
                 and item["purpose"] in {"FUNCTIONAL", "VALIDATION"}, "distance role differs")
        _require(item["source_path"] in inventory
                 and item["source_blob"] == inventory[item["source_path"]]["git_blob"], "distance source differs")
        _require(len(item["operand_digests"]) == 2 and all(_is_digest(v) for v in item["operand_digests"]),
                 "distance operand seals differ")
        site = item["callsite"]
        _require(len(site) == 2 and type(site[0]) is str and type(site[1]) is int and site[1] > 0,
                 "distance callsite differs")
        identity = inventory[item["source_path"]]
        _validate_distance_source((_root() / item["source_path"]).read_bytes(), identity, identity,
                                  site, item["dimension"])
    for purpose, key in (("FUNCTIONAL", "functional_terms"), ("VALIDATION", "validation_terms")):
        _require(cost[key] == sum(item["dimension"] for item in cost["distance_evidence"]
                                  if item["purpose"] == purpose), "distance sum differs")
    _require(cost["total_distance_terms"] == cost["functional_terms"] + cost["validation_terms"],
             "total distance sum differs")
    for call in cost["ppb_call_evidence"]:
        _require(set(call) == {"modality", "expired", "selected", "event_digest", "readout", "prestate", "poststate", "config"},
                 "PPB call fields differ")
        modality = call["modality"]
        _require(modality in {"auditory", "visual"} and call["config"]["modality_id"] == modality,
                 "PPB call modality differs")
        bank_key = ({"TSPM1": modality + "_ppb1_state", "R0": modality + "_ppb"}.get(arm.arm_id, modality))
        _require(call["prestate"] == cost["native_prestate_payload"][bank_key]
                 and call["poststate"] == cost["native_poststate_payload"][bank_key], "PPB call state source differs")
        step = call["prestate"]["accepted_step_count"] + 1
        expected_expired = [i for i, slot in enumerate(call["prestate"]["slots"])
                            if slot["occupied"] and step - slot["last_selected_step"] >= call["config"]["expire_after_steps"]]
        _require(list(call["expired"]) == expected_expired and call["poststate"]["accepted_step_count"] == step,
                 "PPB expiry or step differs")
        selected = call["selected"]
        _require(type(selected) is int and 0 <= selected < len(call["poststate"]["slots"]), "PPB selected position differs")
        _require(call["poststate"]["slots"][selected]["slot_id"] == call["readout"]["slot_id"]
                 and call["poststate"]["slots"][selected]["last_selected_step"] == step
                 and call["event_digest"] == _digest(call["readout"]), "PPB write source differs")
        _require(call["readout"]["config_digest"] == _digest(call["config"])
                 == call["prestate"]["config_digest"] == call["poststate"]["config_digest"]
                 and call["readout"]["prestate_digest"] == _digest(call["prestate"])
                 and call["readout"]["poststate_digest"] == _digest(call["poststate"]), "PPB result seal differs")
    if phase == "FORMATION":
        actions = _write_actions(arm.arm_id, plan.cell_id, phase, index,
                                 cost["native_prestate_payload"], cost["native_poststate_payload"],
                                 cost["native_event"], cost["ppb_call_evidence"])
    else:
        actions = []
        _require(not cost["ppb_call_evidence"] and cost["native_event"] is None
                 and cost["native_prestate_payload"] == cost["native_poststate_payload"]
                 and cost["prestate_payload"] == cost["poststate_payload"], "probe changed state")
    _require(_canonical(actions) == _canonical(cost["write_evidence"]), "write eligibility differs")
    _require(cost["functional_write_words"] == sum(item["width"] for item in actions), "write sum differs")


def _validate_result_evidence(fixture, arm, plan, result):
    _require(len(result.event_payloads) == plan.formation_call_count, "formation coverage differs")
    checkpoints = {}
    previous_digest = plan.initial_state_digest
    previous_native = None
    budget = result.budget_receipt
    for index, event in enumerate(result.event_payloads, 1):
        cost = event["cost_evidence"]
        _validate_cost(plan, arm, cost)
        _require(cost["phase"] == "FORMATION" and cost["operation_index"] == index
                 and cost["prestate_digest"] == previous_digest, "formation chain differs")
        _require(cost["native_event"] == {k: v for k, v in event.items() if k != "cost_evidence"},
                 "formation event seal differs")
        if previous_native is not None:
            _require(previous_native == cost["native_prestate_payload"], "native state chain differs")
        _require(cost["functional_write_words"] == dict(budget.formation_write_counts)[index]
                 and cost["total_distance_terms"] == dict(budget.formation_distance_counts)[index],
                 "formation receipt counts differ")
        previous_digest = cost["poststate_digest"]
        previous_native = cost["native_poststate_payload"]
        checkpoints[index] = (previous_digest, previous_native)
    _require(previous_digest == result.poststate_digest, "final state chain differs")
    expected = [(checkpoint, pair) for checkpoint, pairs in fixture.probe_specs for pair in pairs]
    _require(len(result.finding_payloads) == len(expected) == plan.probe_call_count, "probe coverage differs")
    source = _file_identity(Path(__file__))
    observation_fields = set(_ee_contract()["functional_contract"]["observation_fields"])
    for index, (finding, (checkpoint, pair)) in enumerate(zip(result.finding_payloads, expected, strict=True), 1):
        native = {k: v for k, v in finding.items() if k not in {"observation", "cost_evidence", "checkpoint_evidence"}}
        observation, cost = finding["observation"], finding["cost_evidence"]
        _validate_cost(plan, arm, cost)
        evidence = _unrecord("CheckpointEvidence", finding["checkpoint_evidence"]).payload()
        digest, native_state = checkpoints[checkpoint]
        _require(set(observation) == observation_fields
                 and observation["observation_digest"] == _digest({k: v for k, v in observation.items() if k != "observation_digest"}),
                 "observation seal differs")
        _require((observation["history_id"], observation["arm_id"], observation["checkpoint"], observation["probe_index"], observation["pair_id"])
                 == (fixture.history_id, arm.arm_id, checkpoint, index, pair), "probe role differs")
        _require(cost["phase"] == "PROBE" and cost["operation_index"] == index
                 and cost["prestate_digest"] == digest == observation["observed_state_digest"]
                 and cost["native_prestate_payload"] == native_state == evidence["native_state_payload"], "probe checkpoint source differs")
        _require((evidence["history_id"], evidence["arm_id"], evidence["checkpoint"])
                 == (fixture.history_id, arm.arm_id, checkpoint)
                 and evidence["native_state_digest"] == _digest(native_state)
                 and evidence["native_finding_payload"] == _canonical(native)
                 and evidence["native_finding_digest"] == _digest(native) == observation["native_finding_digest"],
                 "checkpoint evidence identity differs")
        _require(evidence["extraction_source_path"] == source["repository_relative_path"]
                 and evidence["extraction_source_blob"] == source["git_blob"], "extraction source differs")
        _require(native["checkpoint"] == checkpoint and native["pair_id"] == pair
                 and native["history_id"] == fixture.history_id and native["arm_id"] == arm.arm_id
                 and native["observed_state_digest"] == digest
                 and type(native["recognized"]) is bool and native["recognized"] == observation["native_recognized"],
                 "native finding role differs")
        paths = observation["selected_source_paths"]
        _require(_canonical(paths) == _canonical(_selected_source_paths(arm.arm_id, native_state, native)),
                 "selected path is not the native selected slot")
        _require(len(paths) == (2 if native["recognized"] else 0), "selected source count differs")
        for position, modality in enumerate(("auditory", "visual")):
            value = observation[f"selected_{modality}_values"]
            _require(_canonical(value) == _canonical(native[f"selected_{modality}_values"]), "selected values changed")
            if native["recognized"]:
                _require(len(value) == (8 if position == 0 else 18)
                         and _read_selected(native_state, paths[position]) == tuple(value), "selected value provenance differs")
            else:
                _require(value is None, "negative probe contains a payload")
        _require(cost["total_distance_terms"] == dict(budget.probe_distance_counts)[index]
                 and cost["functional_write_words"] == dict(budget.probe_write_counts)[index], "probe receipt counts differ")


def validate_s2dr_cell_result(
    config: S2DRConfigRecord,
    fixture: S2DRFixtureRecord,
    arm: S2DRArmSpec,
    plan: S2DRCellPlan,
    result: S2DRCellResult | None,
    *,
    operation_cost: dict | None = None,
) -> S2DRCellResult | None:
    """Relationally validate one complete cell result and its budget."""

    _validate_operator_inputs(config, fixture, arm)
    if type(plan) is not S2DRCellPlan:
        raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "exact cell plan required")
    for record, key in ((config, "config_digest"), (fixture, "fixture_digest"),
                        (arm, "arm_spec_digest"), (plan, "cell_plan_digest")):
        _validate_record(record, key)
    _require((plan.config_digest, plan.fixture_digest, plan.arm_spec_digest, plan.initial_state_digest,
              plan.history_id, plan.arm_id)
             == (config.config_digest, fixture.fixture_digest, arm.arm_spec_digest, arm.initial_state_digest,
                 fixture.history_id, arm.arm_id), "cell plan source differs")
    if operation_cost is not None:
        if result is not None:
            raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "ambiguous budget validation mode")
        _validate_cost(plan, arm, operation_cost)
        phase = operation_cost["phase"]
        write_limit = arm.formation_write_limit if phase == "FORMATION" else arm.probe_write_limit
        distance_limit = arm.formation_distance_limit if phase == "FORMATION" else arm.probe_distance_limit
        if operation_cost["functional_write_words"] > write_limit or operation_cost["total_distance_terms"] > distance_limit:
            raise S2DRError(S2DR_RESOURCE_OR_OPERATION_LIMIT_EXCEEDED, "operation budget exceeded")
        return None
    if type(plan) is not S2DRCellPlan or type(result) is not S2DRCellResult:
        raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "exact plan and result are required")
    _validate_record(plan, "cell_plan_digest")
    _validate_record(result, "cell_result_digest")
    budget = result.budget_receipt
    receipt = result.cell_receipt
    _validate_record(budget, "budget_receipt_digest")
    _validate_record(receipt, "cell_receipt_digest")
    if result.poststate_digest != _digest(result.poststate_payload):
        raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "poststate changed after construction")
    if (
        result.cell_id != plan.cell_id
        or result.cell_plan_digest != plan.cell_plan_digest
        or budget.cell_id != plan.cell_id
        or budget.cell_plan_digest != plan.cell_plan_digest
        or receipt.cell_id != plan.cell_id
        or receipt.cell_plan_digest != plan.cell_plan_digest
        or receipt.config_digest != config.config_digest
        or receipt.fixture_digest != fixture.fixture_digest
        or receipt.arm_spec_digest != arm.arm_spec_digest
        or result.prestate_digest != plan.initial_state_digest
        or receipt.prestate_digest != result.prestate_digest
        or receipt.event_digest != _digest(result.event_payloads)
        or receipt.finding_digest != _digest(result.finding_payloads)
        or receipt.budget_receipt_digest != budget.budget_receipt_digest
        or receipt.poststate_digest != result.poststate_digest
        or receipt.owner_terminal_state != "COMMITTED"
        or receipt.internal_error_code is not None
    ):
        raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "cell result relations differ")
    formation_keys, probe_keys = _expected_budget_keys(plan)
    formation_groups = (
        (budget.formation_write_bounds, budget.formation_write_counts, budget.remaining_formation_write_budget, arm.formation_write_limit),
        (budget.formation_distance_bounds, budget.formation_distance_counts, budget.remaining_formation_distance_budget, arm.formation_distance_limit),
    )
    probe_groups = (
        (budget.probe_distance_bounds, budget.probe_distance_counts, budget.remaining_probe_distance_budget, arm.probe_distance_limit),
        (budget.probe_write_bounds, budget.probe_write_counts, budget.remaining_probe_write_budget, arm.probe_write_limit),
    )
    if budget.resource_words_bound != arm.resource_words:
        raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "resource bound source differs")
    for bounds, counts, remaining, expected_bound in formation_groups:
        if tuple(key for key, _ in bounds) != formation_keys or tuple(key for key, _ in counts) != formation_keys or tuple(key for key, _ in remaining) != formation_keys:
            raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "formation budget keys differ")
        if any(bound != expected_bound for _, bound in bounds):
            raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "formation bound source differs")
        if any(rest != bound - used for (_, bound), (_, used), (_, rest) in zip(bounds, counts, remaining, strict=True)):
            raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "formation budget arithmetic differs")
    for bounds, counts, remaining, expected_bound in probe_groups:
        if tuple(key for key, _ in bounds) != probe_keys or tuple(key for key, _ in counts) != probe_keys or tuple(key for key, _ in remaining) != probe_keys:
            raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "probe budget keys differ")
        if any(bound != expected_bound for _, bound in bounds):
            raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "probe bound source differs")
        if any(rest != bound - used for (_, bound), (_, used), (_, rest) in zip(bounds, counts, remaining, strict=True)):
            raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "probe budget arithmetic differs")
    over_limit = budget.resource_words_used > budget.resource_words_bound or budget.remaining_resource_words < 0
    for bounds, counts, remaining, _ in formation_groups + probe_groups:
        over_limit = over_limit or any(
            used > bound or rest < 0
            for (_, bound), (_, used), (_, rest) in zip(bounds, counts, remaining, strict=True)
        )
    if over_limit:
        raise S2DRError(S2DR_RESOURCE_OR_OPERATION_LIMIT_EXCEEDED, "cell budget exceeded")
    _require(budget.resource_words_used == arm.resource_words, "reserved capacity cannot be discounted")
    _validate_result_evidence(fixture, arm, plan, result)
    return result


class S2DRCellOwner:
    """Single-use fail-closed owner for one private comparison cell."""

    def __init__(
        self,
        owner_id: str,
        cell_id: str,
        authorization_digest: str,
        consumption_id: str,
        cell_plan_digest: str,
        config_digest: str,
        fixture_digest: str,
        arm_spec_digest: str,
        prestate_digest: str,
    ) -> None:
        self._owner_id = _id(owner_id, "owner_id")
        self._cell_id = _id(cell_id, "cell_id")
        self._authorization_digest = authorization_digest
        self._consumption_id = _id(consumption_id, "consumption_id")
        self._cell_plan_digest = cell_plan_digest
        self._config_digest = config_digest
        self._fixture_digest = fixture_digest
        self._arm_spec_digest = arm_spec_digest
        self._prestate_digest = prestate_digest
        if not all(_is_digest(value) for value in (authorization_digest, cell_plan_digest, config_digest, fixture_digest, arm_spec_digest, prestate_digest)):
            raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "owner digest role invalid")
        self._status = "FRESH"
        self._internal_error_code: str | None = None
        self._committed_result_digest: str | None = None
        self._lock = Lock()

    def snapshot(self) -> S2DRCellOwnerSnapshot:
        return S2DRCellOwnerSnapshot(
            self._owner_id,
            self._cell_id,
            self._authorization_digest,
            self._consumption_id,
            self._status,
            self._cell_plan_digest,
            self._internal_error_code,
            self._committed_result_digest,
        )

    def consume_once(
        self,
        config: S2DRConfigRecord,
        fixture: S2DRFixtureRecord,
        arm: S2DRArmSpec,
        plan: S2DRCellPlan,
    ) -> S2DRCellResult:
        if not self._lock.acquire(blocking=False):
            raise S2DRError(S2DR_OWNER_BUSY, "cell owner is busy")
        try:
            if self._status != "FRESH":
                raise S2DRError(S2DR_OWNER_TERMINAL, "cell owner is terminal")
            self._status = "BUSY"
            try:
                _validate_operator_inputs(config, fixture, arm)
                if type(plan) is not S2DRCellPlan:
                    raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "exact cell plan required")
                for record, digest_field in (
                    (config, "config_digest"),
                    (fixture, "fixture_digest"),
                    (arm, "arm_spec_digest"),
                    (plan, "cell_plan_digest"),
                ):
                    _validate_record(record, digest_field)
                expected_authorization = _authorization_digest(
                    plan.cell_id,
                    plan.config_digest,
                    plan.fixture_digest,
                    plan.arm_spec_digest,
                    plan.initial_state_digest,
                )
                if plan.authorization_digest != expected_authorization:
                    raise S2DRError(S2DR_AUTHORIZATION_MISMATCH, "plan authorization is invalid")
                if (
                    self._cell_id != plan.cell_id
                    or self._authorization_digest != plan.authorization_digest
                    or self._cell_plan_digest != plan.cell_plan_digest
                ):
                    raise S2DRError(S2DR_OWNER_AUTHORIZATION_MISMATCH, "owner cell authorization differs")
                if (
                    self._config_digest != plan.config_digest
                    or self._fixture_digest != plan.fixture_digest
                    or self._arm_spec_digest != plan.arm_spec_digest
                    or config.config_digest != plan.config_digest
                    or fixture.fixture_digest != plan.fixture_digest
                    or arm.arm_spec_digest != plan.arm_spec_digest
                    or fixture.history_id != plan.history_id
                    or arm.arm_id != plan.arm_id
                    or self._prestate_digest != plan.initial_state_digest
                    or arm.initial_state_digest != plan.initial_state_digest
                ):
                    raise S2DRError(S2DR_FIXTURE_ARM_OR_PRESTATE_MISMATCH, "fixture, arm, or prestate differs")
                state = initial_s2dr_arm_state(config, arm)
                events = []
                findings = []
                formation_writes = []
                formation_distances = []
                probe_distances = []
                probe_writes = []
                probe_number = 0
                probes_by_checkpoint = {after: pairs for after, pairs in fixture.probe_specs}
                for formation_index, pair_id in enumerate(fixture.formation_pair_ids, start=1):
                    state, event, operations = advance_s2dr_arm(
                        config, fixture, arm, state, pair_id, formation_index
                    )
                    validate_s2dr_cell_result(config, fixture, arm, plan, None,
                                             operation_cost=event["cost_evidence"])
                    events.append(event)
                    formation_writes.append(operations[0])
                    formation_distances.append(operations[1])
                    for probe_pair_id in probes_by_checkpoint.get(formation_index, ()):
                        probe_number += 1
                        before = _digest(_state_payload(arm.arm_id, state))
                        finding, distance_terms = probe_s2dr_arm(
                            config, fixture, arm, state, probe_pair_id, probe_number
                        )
                        validate_s2dr_cell_result(config, fixture, arm, plan, None,
                                                 operation_cost=finding["cost_evidence"])
                        after = _digest(_state_payload(arm.arm_id, state))
                        if before != after:
                            raise S2DRError(S2DR_ATOMIC_RESULT_REQUIRED, "probe changed state")
                        findings.append(finding)
                        probe_distances.append(distance_terms)
                        probe_writes.append(0)
                budget = _make_budget_receipt(
                    plan,
                    arm,
                    formation_writes,
                    formation_distances,
                    probe_distances,
                    probe_writes,
                )
                poststate_payload = _state_payload(arm.arm_id, state)
                poststate_digest = _digest(poststate_payload)
                cell_receipt = _built(
                    S2DRCellReceipt,
                    "cell_receipt_digest",
                    schema_version=S2DR_SCHEMA_VERSION,
                    cell_id=plan.cell_id,
                    cell_plan_digest=plan.cell_plan_digest,
                    config_digest=config.config_digest,
                    fixture_digest=fixture.fixture_digest,
                    arm_spec_digest=arm.arm_spec_digest,
                    prestate_digest=plan.initial_state_digest,
                    event_digest=_digest(tuple(events)),
                    finding_digest=_digest(tuple(findings)),
                    budget_receipt_digest=budget.budget_receipt_digest,
                    poststate_digest=poststate_digest,
                    owner_id=self._owner_id,
                    owner_terminal_state="COMMITTED",
                    internal_error_code=None,
                )
                result = _built(
                    S2DRCellResult,
                    "cell_result_digest",
                    schema_version=S2DR_SCHEMA_VERSION,
                    cell_id=plan.cell_id,
                    cell_plan_digest=plan.cell_plan_digest,
                    prestate_digest=plan.initial_state_digest,
                    event_payloads=tuple(events),
                    finding_payloads=tuple(findings),
                    poststate_payload=poststate_payload,
                    poststate_digest=poststate_digest,
                    budget_receipt=budget,
                    cell_receipt=cell_receipt,
                )
                validate_s2dr_cell_result(config, fixture, arm, plan, result)
                self._status = "COMMITTED"
                self._committed_result_digest = result.cell_result_digest
                return result
            except BaseException as exc:
                self._status = "FAILED"
                self._internal_error_code = getattr(exc, "code", "S2EF_UNEXPECTED_EXCEPTION")
                raise S2DRError(S2DR_ATTEMPT_FAILED, f"{self._internal_error_code}: {exc}") from exc
        finally:
            self._lock.release()


def _finding(
    results: Mapping[tuple[str, str], S2DRCellResult],
    history_id: str,
    arm_id: str,
    checkpoint: int,
    pair_id: str,
) -> Mapping[str, object] | None:
    result = results.get((history_id, arm_id))
    if result is None:
        return None
    matches = [
        item
        for item in result.finding_payloads
        if isinstance(item, Mapping)
        and item.get("checkpoint") == checkpoint
        and item.get("pair_id") == pair_id
    ]
    return matches[-1] if matches else None


def _score_functional_probe(finding: Mapping, expected: bool, target: tuple | None) -> dict:
    """Score selected values only; never select a slot or advance a state."""
    recognized = finding["recognized"]
    _require(type(recognized) is bool and type(expected) is bool, "non-boolean probe decision")
    auditory_error = visual_error = None
    terms = 0
    if recognized:
        auditory_values = _finite_tuple(tuple(finding["selected_auditory_values"]), 8, "selected auditory")
        visual_values = _finite_tuple(tuple(finding["selected_visual_values"]), 18, "selected visual")
    else:
        _require(finding["selected_auditory_values"] is None
                 and finding["selected_visual_values"] is None, "negative probe has selected values")
    if expected and recognized:
        _require(target is not None and len(target) == 2, "positive target missing")
        auditory_error = normalized_mean_l1_distance(auditory_values, (target[0],) * 8)
        visual_error = normalized_mean_l1_distance(visual_values, (target[1],) * 18)
        terms = 26
        correct = auditory_error <= 0.2 and visual_error <= 0.2
    else:
        correct = not recognized if not expected else False
    return {"expected_recognized": expected, "native_recognized": recognized,
            "auditory_target_error": auditory_error, "visual_target_error": visual_error,
            "functional_correct": correct, "evaluation_terms": terms}


def _per_arm_metrics(results: Mapping[tuple[str, str], S2DRCellResult], arm_id: str) -> dict:
    contract = _ee_contract()["functional_contract"]
    observations = {}
    rows = []
    for history, checkpoint, pair, expected, target in contract["expected_probes"]:
        finding = _finding(results, history, arm_id, checkpoint, pair)
        if finding is None:
            raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "missing functional observation")
        score = _score_functional_probe(finding, expected, PAIR_SCALARS[target] if expected else None)
        key = f"{history}/{checkpoint}/{pair}"
        observations[key] = (score["functional_correct"], finding)
        rows.append({"probe_key": key, **score})
    predicates = [all(observations[key][0] for key in contract["predicate_sources"][name])
                  for name in PREDICATE_IDS]
    previous_ok, previous = observations["H2/4/AX"]
    current_ok, current = observations["H4/6/AX"]
    preserved = previous_ok and current_ok and all(
        tuple(previous[f"selected_{modality}_values"]) == tuple(current[f"selected_{modality}_values"])
        for modality in ("auditory", "visual"))
    predicates[2] = predicates[2] and preserved
    errors = sum(not row["functional_correct"] for row in rows)
    errors += int(previous_ok and current_ok and not preserved)
    latency = next((checkpoint for checkpoint in (1, 4)
                    if observations[f"H2/{checkpoint}/AX"][0]), 5)
    writes = sum(count for history in HISTORY_IDS
                 for _, count in results[(history, arm_id)].budget_receipt.formation_write_counts)
    return {"predicate_vector": tuple(predicates), "functional_error_sum": errors,
            "observed_capture_latency_rank": latency,
            "capture_latency_status": "NOT_OBSERVED" if latency == 5 else "OBSERVED",
            "total_formation_write_words": writes, "probe_metrics": tuple(rows),
            "ax_preserved": preserved}


def _predicate_vector(results, arm_id):
    return tuple(_per_arm_metrics(results, arm_id)["predicate_vector"])


def _rank_key(arm_id: str, metrics: Mapping[str, dict]) -> tuple:
    row = metrics[arm_id]
    return (-sum(row["predicate_vector"]), row["functional_error_sum"],
            row["observed_capture_latency_rank"], row["total_formation_write_words"], arm_id)


def _decision_from_vectors(vectors, errors, r0_exact_equivalence, metrics=None):
    if (set(vectors) != set(ARM_IDS) or any(len(v) != 5 for v in vectors.values())
            or set(errors) != set(ARM_IDS) or any(errors.values()) or not r0_exact_equivalence):
        return "METHOD_INVALID", None
    if metrics is None or set(metrics) != set(ARM_IDS):
        return "METHOD_INVALID", None
    strongest = min(SIMPLE_BASELINE_ORDER, key=lambda arm: _rank_key(arm, metrics))
    if not all(vectors["TSPM1"]):
        return "TSPM1_FUNCTION_NOT_VALID", strongest
    if any(all(vectors[arm]) for arm in SIMPLE_BASELINE_ORDER):
        return "FUNCTION_VALID_SIMPLE_BASELINE_EXPLAINS", strongest
    return "TSPM1_TWO_TIMESCALE_ENGINEERING_ADVANTAGE_OVER_SIMPLE_BASELINES", strongest


def _exact_reduction_projection(result: S2DRCellResult) -> object:
    event_keys = ("event", "consolidation_status")
    finding_keys = (
        "checkpoint", "pair_id", "recognized", "context_source",
        "fast_recognized", "auditory_fast_distance", "visual_fast_distance",
        "auditory_slow_status", "visual_slow_status",
        "auditory_selected_slot_id", "visual_selected_slot_id",
        "auditory_selected_prototype_digest", "visual_selected_prototype_digest",
        "auditory_slow_distance", "visual_slow_distance", "selected_av_payload_digest",
    )
    for entries, required_keys in (
        (result.event_payloads, event_keys),
        (result.finding_payloads, finding_keys),
    ):
        if any(not isinstance(entry, Mapping) or not all(key in entry for key in required_keys) for entry in entries):
            raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "incomplete reduction projection entry")
    event_projection = tuple(
        tuple(event[key] for key in event_keys)
        for event in result.event_payloads
    )
    finding_projection = tuple(
        tuple(finding[key] for key in finding_keys)
        for finding in result.finding_payloads
    )
    return result.poststate_payload, event_projection, finding_projection


def _r0_pair_equal(left, right) -> bool:
    keys = _ee_contract()["source_and_receipt_contract"]["r0_observation_projection_fields"]
    return (_exact_reduction_projection(left) == _exact_reduction_projection(right)
            and tuple(tuple(item["observation"][key] for key in keys) for item in left.finding_payloads)
            == tuple(tuple(item["observation"][key] for key in keys) for item in right.finding_payloads))


def _engineering_groups(metrics: Mapping[str, dict]) -> tuple[dict, ...]:
    """Prefer simpler implementations only within the same functional profile."""
    groups = {}
    for arm, row in metrics.items():
        profile = (tuple((p["probe_key"], p["functional_correct"]) for p in row["probe_metrics"]),
                   row["ax_preserved"], row["observed_capture_latency_rank"])
        groups.setdefault(profile, []).append(arm)
    result = []
    for profile, arms in groups.items():
        def cost(arm):
            return (metrics[arm]["total_formation_write_words"], ARM_RESOURCE_WORDS[arm],
                    2 if arm in {"TSPM1", "R0"} else (0 if arm == "B0" else 1))
        ranked = sorted(arms, key=lambda arm: (*cost(arm), arm))
        result.append({"profile_digest": _digest(profile), "ranking": tuple(ranked),
                       "equally_preferred": tuple(a for a in ranked if cost(a) == cost(ranked[0])),
                       "costs": tuple((a, cost(a)) for a in ranked)})
    return tuple(sorted(result, key=lambda group: group["profile_digest"]))


def compare_s2dr_results(
    config: S2DRConfigRecord,
    plans: tuple[S2DRCellPlan, ...],
    results: tuple[S2DRCellResult, ...],
    registry_digest: str,
    *,
    attestation: _S2EFAttempt | None = None,
) -> S2DRComparisonResult:
    """Compare the single runner's complete, attested 56-cell result set."""

    if type(attestation) is not _S2EFAttempt:
        raise S2DRError(S2DR_AUTHORIZATION_MISMATCH, "attested S2-EE result set required")
    attestation.validate_results(config, plans, results, registry_digest)
    return _compare_s2dr_functional_results(
        config, plans, results, registry_digest,
        evidence_digests=tuple(item.record_digest for item in attestation.evidence))


def _compare_s2dr_functional_results(
    config: S2DRConfigRecord,
    plans: tuple[S2DRCellPlan, ...],
    results: tuple[S2DRCellResult, ...],
    registry_digest: str,
    *,
    evidence_digests: tuple[str, ...],
) -> S2DRComparisonResult:
    """Aggregate already admitted results; this is not an execution authorization."""
    _require(len(evidence_digests) == 56 and all(_is_digest(d) for d in evidence_digests),
             "complete evidence digest set required")
    if type(config) is not S2DRConfigRecord or not _is_digest(registry_digest):
        raise S2DRError(S2DR_INVALID_TYPE_OR_SCHEMA, "comparison source is invalid")
    if len(plans) != 56 or len(results) != 56:
        raise S2DRError(S2DR_ATOMIC_RESULT_REQUIRED, "exactly 56 plans and results are required")
    if len({plan.cell_id for plan in plans}) != 56 or len({result.cell_id for result in results}) != 56:
        raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "duplicate cell identity")
    plan_by_id = {plan.cell_id: plan for plan in plans}
    result_by_role: dict[tuple[str, str], S2DRCellResult] = {}
    for result in results:
        plan = plan_by_id.get(result.cell_id)
        if plan is None or result.cell_plan_digest != plan.cell_plan_digest:
            raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "result does not match registry plan")
        result_by_role[(plan.history_id, plan.arm_id)] = result
    if len(result_by_role) != 56:
        raise S2DRError(S2DR_RESULT_RELATION_MISMATCH, "history-arm matrix is incomplete")
    metrics = {arm_id: _per_arm_metrics(result_by_role, arm_id) for arm_id in ARM_IDS}
    vectors = {arm_id: tuple(metrics[arm_id]["predicate_vector"]) for arm_id in ARM_IDS}
    errors = {
        arm_id: sum(
            1
            for history_id in HISTORY_IDS
            if result_by_role[(history_id, arm_id)].cell_receipt.internal_error_code is not None
        )
        for arm_id in ARM_IDS
    }
    r0_exact = all(
        _r0_pair_equal(result_by_role[(history_id, "R0")], result_by_role[(history_id, "TSPM1")])
        for history_id in HISTORY_IDS
    )
    decision, strongest = _decision_from_vectors(vectors, errors, r0_exact, metrics)
    return _built(
        S2DRComparisonResult,
        "comparison_result_digest",
        schema_version=S2DR_SCHEMA_VERSION,
        registry_digest=registry_digest,
        ordered_cell_result_digests=tuple(result.cell_result_digest for result in results),
        per_arm_predicate_vectors=tuple((arm_id, vectors[arm_id]) for arm_id in ARM_IDS),
        per_arm_error_counts=tuple((arm_id, errors[arm_id]) for arm_id in ARM_IDS),
        strongest_simple_baseline_id=strongest,
        r0_exact_equivalence=r0_exact,
        decision=decision,
        evaluation_id=S2EE_EVALUATION_ID,
        per_arm_metrics=tuple((arm, metrics[arm]) for arm in ARM_IDS),
        all_arm_ranking=tuple(sorted(ARM_IDS, key=lambda arm: _rank_key(arm, metrics))),
        simple_baseline_ranking=tuple(sorted(SIMPLE_BASELINE_ORDER, key=lambda arm: _rank_key(arm, metrics))),
        ordered_cell_evidence_digests=evidence_digests,
    )


def _runtime_identity() -> dict:
    executable = Path(sys.executable).resolve()
    platform_identity = platform.platform()
    dependencies = []
    for name, module in sorted(sys.modules.copy().items()):
        filename = getattr(module, "__file__", None)
        if not filename or name.startswith("mcm_field_organism"):
            continue
        path = Path(filename).resolve()
        if not path.is_file():
            raise S2DRError(S2DR_DIGEST_OR_SOURCE_MISMATCH, "unresolved runtime dependency")
        dependencies.append({"module": name, "path": str(path),
                             "version": str(getattr(module, "__version__", "bundled-with-interpreter")),
                             "raw_sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    return {"interpreter_path": str(executable),
            "interpreter_sha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
            "python_version": sys.version, "platform": platform_identity,
            "dependencies": dependencies}


def _source_manifest() -> S2EFRecord:
    # Refuse dirty source: blob IDs and file bytes must describe the same checkout.
    _require(not _git("status", "--porcelain", "--untracked-files=all", "--", "mcm_field_organism", "docs"),
             "source tree is not committed and clean")
    contract_paths = [
        "docs/S2EE_TSPM1_STATISCHER_KORREKTUR_UND_AUSFUEHRUNGSBINDUNGSVERTRAG_V1.json",
        _ee_contract()["fixed_registry"]["fixture_contract"],
    ]
    return _record("SourceManifest", source_commit=_git("rev-parse", "HEAD"),
                   project_sources=_project_source_inventory(),
                   contract_sources=tuple(_file_identity(_root() / path) for path in contract_paths),
                   runtime_identity=_runtime_identity(), evaluation_id=S2EE_EVALUATION_ID,
                   accounting_id="S2EE_OPERATION_ACCOUNTING_V1")


def _execution_domain() -> dict:
    common = Path(_git("rev-parse", "--path-format=absolute", "--git-common-dir")).resolve()
    return {"canonical_repository_path": str(_root()), "canonical_git_common_dir": str(common),
            "host_identity": {"node": platform.node(), "system": platform.system(), "machine": platform.machine()},
            "durable_ledger_root": str(common / "mcm-execution-ledger")}


def _registry_payload(registry) -> dict:
    config, fixtures, arms, plans, inner_digest = registry
    return {"evaluation_id": S2EE_EVALUATION_ID, "evaluation_contract_digest": S2EE_CONTRACT_DIGEST,
            "config": _canonical(config), "fixtures": _canonical(fixtures), "arms": _canonical(arms),
            "cell_plans": _canonical(plans), "inner_registry_digest": inner_digest}


def _build_s2ef_execution_plan() -> tuple[S2EFRecord, S2EFRecord]:
    """Prepare immutable metadata only; this does not authorize any execution."""
    manifest = _source_manifest()
    registry = build_s2dr_registry()
    domain, contract = _execution_domain(), _ee_contract()
    payload = _registry_payload(registry)
    final = _root() / "reports/s2ee_tspm1_56_cell_comparison_v1.json"
    plan = _record("ExecutionPlan", study_id=S2EE_STUDY_ID, execution_domain=domain,
                   source_manifest_digest=manifest.record_digest, registry_payload=payload,
                   registry_digest=_digest(payload),
                   ordered_cell_plan_digests=[item.cell_plan_digest for item in registry[3]],
                   expected_probe_table_digest=_digest(contract["functional_contract"]["expected_probes"]),
                   evaluation_contract_digest=S2EE_CONTRACT_DIGEST,
                   resource_and_operation_contract_digest=_digest(contract["operation_contract"]),
                   publication_paths={"final": str(final),
                                      "staging": str(final.parent / ".s2ee_tspm1_56_cell_comparison.attempt-001.staging"),
                                      "reservation": str(Path(domain["durable_ledger_root"]) / S2EE_STUDY_ID)})
    return manifest, plan


def _validate_execution_sources(manifest: S2EFRecord, plan: S2EFRecord) -> tuple:
    _require(type(manifest) is S2EFRecord and manifest.kind == "SourceManifest"
             and type(plan) is S2EFRecord and plan.kind == "ExecutionPlan", "execution source types differ")
    manifest.payload()
    expected_manifest, expected_plan = _build_s2ef_execution_plan()
    _require(manifest == expected_manifest and plan == expected_plan, "execution source, registry or domain changed")
    registry = build_s2dr_registry()
    _require(plan.payload()["registry_payload"] == _registry_payload(registry), "execution registry changed")
    return registry


class _DurableStudyStore:
    """Local NTFS only; volume flush privilege is required, never elevated here."""

    def __init__(self, plan: S2EFRecord):
        self.plan = plan
        self.created_reservation = False
        data = plan.payload()
        _require(os.name == "nt", "no audited durability backend for this platform")
        self.paths = {key: Path(value) for key, value in data["publication_paths"].items()}
        self.ledger_root = Path(data["execution_domain"]["durable_ledger_root"])
        self.authorization_path = self.ledger_root / (S2EE_STUDY_ID + ".authorization.json")
        self._kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel = self._kernel
        kernel.CreateFileW.argtypes = (wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                      wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE)
        kernel.CreateFileW.restype = wintypes.HANDLE
        kernel.FlushFileBuffers.argtypes = (wintypes.HANDLE,)
        kernel.FlushFileBuffers.restype = wintypes.BOOL
        kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
        kernel.CloseHandle.restype = wintypes.BOOL
        kernel.MoveFileExW.argtypes = (wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD)
        kernel.MoveFileExW.restype = wintypes.BOOL
        kernel.GetDriveTypeW.argtypes = (wintypes.LPCWSTR,)
        kernel.GetDriveTypeW.restype = wintypes.UINT
        kernel.GetVolumeInformationW.argtypes = (wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD,
                                                ctypes.POINTER(wintypes.DWORD), ctypes.POINTER(wintypes.DWORD),
                                                ctypes.POINTER(wintypes.DWORD), wintypes.LPWSTR, wintypes.DWORD)
        kernel.GetVolumeInformationW.restype = wintypes.BOOL
        self.handle = None
        self.check_paths()
        drive = self.paths["final"].anchor
        _require(kernel.GetDriveTypeW(drive) == 3, "durable ledger requires a local fixed volume")
        filesystem = ctypes.create_unicode_buffer(32)
        if not kernel.GetVolumeInformationW(drive, None, 0, None, None, None, filesystem, len(filesystem)):
            raise ctypes.WinError(ctypes.get_last_error())
        _require(filesystem.value == "NTFS", "durability backend is restricted to NTFS")
        handle = kernel.CreateFileW("\\\\.\\" + drive[:2], 0xC0000000, 3, None, 3, 0, None)
        if handle == ctypes.c_void_p(-1).value:
            raise S2DRError(S2DR_ATOMIC_RESULT_REQUIRED, "durable volume flush unavailable; no reservation or execution")
        self.handle = handle
        try:
            self.flush()
        except BaseException:
            self.close()
            raise

    def check_paths(self):
        data = self.plan.payload()
        _require(data["execution_domain"] == _execution_domain(), "execution domain changed")
        roots = (_root(), Path(data["execution_domain"]["canonical_git_common_dir"]))
        _require(self.paths["final"].parent == self.paths["staging"].parent
                 and self.paths["reservation"] == self.ledger_root / S2EE_STUDY_ID, "publication paths differ")
        for path in (*self.paths.values(), self.authorization_path, self.ledger_root, *roots):
            _require(path.is_absolute() and path.drive == self.paths["final"].drive
                     and str(path) == str(path.resolve()), "noncanonical or cross-volume path")
            for ancestor in (path, *path.parents):
                if os.path.lexists(ancestor):
                    _require(not ancestor.is_symlink()
                             and not (getattr(ancestor.lstat(), "st_file_attributes", 0) & 0x400),
                             "reparse point in execution path")
        _require(self.paths["final"].is_relative_to(roots[0])
                 and self.paths["reservation"].is_relative_to(roots[1]), "path escaped execution domain")

    def flush(self):
        if not self._kernel.FlushFileBuffers(self.handle):
            raise ctypes.WinError(ctypes.get_last_error())

    def close(self):
        if self.handle is not None:
            self._kernel.CloseHandle(self.handle)
            self.handle = None

    def write_new(self, path: Path, record: S2EFRecord):
        self.check_paths()
        _require(path.parent == self.paths["reservation"] or path == self.paths["staging"],
                 "unbound record destination")
        raw = _json_bytes(record.payload())
        with path.open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        self.flush()
        _require(path.read_bytes() == raw, "durable record reread differs")

    def reserve(self, reservation: S2EFRecord):
        self.check_paths()
        _require(not os.path.lexists(self.paths["final"]) and not os.path.lexists(self.paths["staging"]),
                 "publication entry already exists")
        self.ledger_root.mkdir(exist_ok=True)
        self.paths["final"].parent.mkdir(exist_ok=True)
        self.flush()
        # No reclaim even for an empty marker: mkdir is the irreversible consumption.
        self.paths["reservation"].mkdir(exist_ok=False)
        self.created_reservation = True
        self.flush()
        self.write_new(self.paths["reservation"] / "reservation.json", reservation)

    def publish(self):
        self.check_paths()
        # MOVEFILE_WRITE_THROUGH, without REPLACE_EXISTING or COPY_ALLOWED.
        if not self._kernel.MoveFileExW(str(self.paths["staging"]), str(self.paths["final"]), 0x8):
            raise ctypes.WinError(ctypes.get_last_error())
        self.flush()


class _S2EFAttempt:
    """A private, durable, serial attempt; no release is installed in S2-EF."""

    def __init__(self, manifest: S2EFRecord, plan: S2EFRecord, authorization: S2EFRecord):
        if not _EXECUTION_RELEASE_ENABLED:
            raise S2DRError(S2DR_AUTHORIZATION_MISMATCH, "56-cell matrix remains locked")
        self.registry = _validate_execution_sources(manifest, plan)
        _require(type(authorization) is S2EFRecord and authorization.kind == "ExecutionAuthorization",
                 "explicit execution authorization required")
        auth, data = authorization.payload(), plan.payload()
        _require(auth["execution_plan_digest"] == plan.record_digest and auth["study_id"] == S2EE_STUDY_ID
                 and auth["execution_domain_digest"] == _digest(data["execution_domain"])
                 and type(auth["authorized_attempt_count"]) is int and auth["authorized_attempt_count"] == 1
                 and _is_digest(auth["user_authorization_text_digest"]), "execution authorization differs")
        authorization_path = Path(data["execution_domain"]["durable_ledger_root"]) / (S2EE_STUDY_ID + ".authorization.json")
        _require(authorization_path.read_bytes() == _json_bytes(authorization.payload()),
                 "separately supplied immutable execution authorization differs")
        self.manifest, self.plan, self.authorization = manifest, plan, authorization
        self.reservation = _record("AttemptReservation", execution_authorization_digest=authorization.record_digest,
                                   execution_plan_digest=plan.record_digest, study_id=S2EE_STUDY_ID,
                                   execution_domain_digest=_digest(data["execution_domain"]), attempt_id="001", status="RESERVED")
        self.store = _DurableStudyStore(plan)
        self.evidence: list[S2EFRecord] = []
        self.starts: list[S2EFRecord] = []
        self.results: list[S2DRCellResult] = []
        self.owners: list[S2DRCellOwner] = []
        self.journal: list[S2EFRecord] = []
        self._lock = Lock()
        self.status = "FRESH"
        self._final_flush_confirmed = False
        self._final_content_verified = False
        self._completion_proof_digest = None

    def _journal(self, status, *, start=None, evidence=None, artifact=None, error=None):
        entry = _record("AttemptJournalEntry", reservation_digest=self.reservation.record_digest,
                        journal_ordinal=len(self.journal) + 1,
                        previous_journal_entry_digest_or_null=self.journal[-1].record_digest if self.journal else None,
                        status=status, cell_start_digest_or_null=start, cell_evidence_digest_or_null=evidence,
                        sealed_artifact_digest_or_null=artifact, error_or_null=error)
        self.store.write_new(self.store.paths["reservation"] / f"journal-{len(self.journal) + 1:03d}.json", entry)
        self.journal.append(entry)

    def _cell_evidence(self, start, owner, result):
        return _record("CellEvidence", cell_start_digest=start.record_digest,
                       core_cell_result=_canonical(result), core_cell_result_digest=result.cell_result_digest,
                       owner_terminal_snapshot=_canonical(owner.snapshot()),
                       checkpoint_evidence=[f["checkpoint_evidence"] for f in result.finding_payloads],
                       observations=[f["observation"] for f in result.finding_payloads],
                       cost_evidence={"formation": [e["cost_evidence"] for e in result.event_payloads],
                                      "probe": [f["cost_evidence"] for f in result.finding_payloads]},
                       source_manifest_digest=self.manifest.record_digest)

    def validate_results(self, config, plans, results, registry_digest):
        _require(self.status == "RUNNING" and len(self.evidence) == len(self.starts) == len(self.owners) == len(self.results) == 56,
                 "attempt is incomplete or terminal")
        _validate_execution_sources(self.manifest, self.plan)
        self.store.check_paths()
        _require(self.store.authorization_path.read_bytes() == _json_bytes(self.authorization.payload()),
                 "execution authorization changed")
        _require(config == self.registry[0] and plans == self.registry[3]
                 and registry_digest == self.plan.payload()["registry_digest"]
                 and len(results) == 56 and all(a is b for a, b in zip(results, self.results, strict=True)),
                 "comparator does not own these results")
        reservation_path = self.store.paths["reservation"] / "reservation.json"
        _require(reservation_path.read_bytes() == _json_bytes(self.reservation.payload()), "durable reservation changed")
        _require(len(self.journal) == 112, "durable cell journal is incomplete")
        for index, entry in enumerate(self.journal, 1):
            _require((self.store.paths["reservation"] / f"journal-{index:03d}.json").read_bytes() == _json_bytes(entry.payload()),
                     "durable journal changed")
        fixtures = {f.history_id: f for f in self.registry[1]}
        arms = {a.arm_id: a for a in self.registry[2]}
        expected_roles = [(h, a) for h in HISTORY_IDS for a in ARM_IDS]
        for index, (plan, result, start, evidence, owner, role) in enumerate(
                zip(plans, results, self.starts, self.evidence, self.owners, expected_roles, strict=True), 1):
            start_data, snapshot = start.payload(), owner.snapshot()
            suffix = f"{self.reservation.record_digest}.{index:03d}"
            _require((plan.history_id, plan.arm_id) == role
                     and start_data == _record("CellStart", reservation_digest=self.reservation.record_digest,
                                               ordinal=index, cell_id=plan.cell_id, cell_plan_digest=plan.cell_plan_digest,
                                               owner_id="s2ee.owner." + suffix, consumption_id="s2ee.consume." + suffix,
                                               expected_initial_state_digest=plan.initial_state_digest).payload(), "cell start source differs")
            _require(snapshot.status == "COMMITTED" and snapshot.owner_id == "s2ee.owner." + suffix
                     and snapshot.consumption_id == "s2ee.consume." + suffix and snapshot.cell_id == plan.cell_id
                     and snapshot.authorization_digest == plan.authorization_digest
                     and snapshot.cell_plan_digest == plan.cell_plan_digest and snapshot.internal_error_code is None
                     and snapshot.committed_result_digest == result.cell_result_digest
                     and result.cell_receipt.owner_id == snapshot.owner_id, "owner result binding differs")
            validate_s2dr_cell_result(config, fixtures[plan.history_id], arms[plan.arm_id], plan, result)
            _require(evidence == self._cell_evidence(start, owner, result), "cell evidence changed")
            _require((self.store.paths["reservation"] / f"cell-start-{index:03d}.json").read_bytes() == _json_bytes(start.payload())
                     and (self.store.paths["reservation"] / f"cell-evidence-{index:03d}.json").read_bytes() == _json_bytes(evidence.payload()),
                     "persisted cell evidence differs")
            before, after = self.journal[2 * (index - 1)].payload(), self.journal[2 * (index - 1) + 1].payload()
            _require(before["cell_start_digest_or_null"] == start.record_digest
                     and before["cell_evidence_digest_or_null"] is None
                     and after["cell_start_digest_or_null"] == start.record_digest
                     and after["cell_evidence_digest_or_null"] == evidence.record_digest, "journal source order differs")

    def run_once(self) -> S2EFRecord:
        if not self._lock.acquire(blocking=False):
            raise S2DRError(S2DR_OWNER_BUSY, "attempt is busy")
        if self.status != "FRESH":
            self._lock.release()
            raise S2DRError(S2DR_OWNER_TERMINAL, "attempt cannot be repeated")
        artifact = None
        try:
            self.status = "RESERVED"
            _validate_execution_sources(self.manifest, self.plan)
            _require(_EXECUTION_RELEASE_ENABLED and self.store.authorization_path.read_bytes() == _json_bytes(self.authorization.payload()),
                     "execution release changed")
            self.store.reserve(self.reservation)
            self.status = "RUNNING"
            config, fixtures, arms, plans, _ = self.registry
            fixture_map, arm_map = {f.history_id: f for f in fixtures}, {a.arm_id: a for a in arms}
            for ordinal, plan in enumerate(plans, 1):
                suffix = f"{self.reservation.record_digest}.{ordinal:03d}"
                start = _record("CellStart", reservation_digest=self.reservation.record_digest, ordinal=ordinal,
                                cell_id=plan.cell_id, cell_plan_digest=plan.cell_plan_digest,
                                owner_id="s2ee.owner." + suffix, consumption_id="s2ee.consume." + suffix,
                                expected_initial_state_digest=plan.initial_state_digest)
                self.store.write_new(self.store.paths["reservation"] / f"cell-start-{ordinal:03d}.json", start)
                self._journal("RUNNING", start=start.record_digest)
                self.starts.append(start)
                owner = S2DRCellOwner("s2ee.owner." + suffix, plan.cell_id, plan.authorization_digest,
                                      "s2ee.consume." + suffix, plan.cell_plan_digest, plan.config_digest,
                                      plan.fixture_digest, plan.arm_spec_digest, plan.initial_state_digest)
                self.owners.append(owner)
                result = owner.consume_once(config, fixture_map[plan.history_id], arm_map[plan.arm_id], plan)
                self.results.append(result)
                evidence = self._cell_evidence(start, owner, result)
                self.store.write_new(self.store.paths["reservation"] / f"cell-evidence-{ordinal:03d}.json", evidence)
                self._journal("RUNNING", start=start.record_digest, evidence=evidence.record_digest)
                self.evidence.append(evidence)
            comparison = compare_s2dr_results(config, plans, tuple(self.results),
                                               self.plan.payload()["registry_digest"], attestation=self)
            _require(comparison.decision != "METHOD_INVALID", "method-invalid comparison cannot be published")
            payload = _record("ComparisonPayload", evaluation_id=S2EE_EVALUATION_ID,
                              registry_digest=comparison.registry_digest,
                              ordered_cell_evidence_digests=comparison.ordered_cell_evidence_digests,
                              per_arm_metrics=comparison.per_arm_metrics, all_arm_ranking=comparison.all_arm_ranking,
                              simple_baseline_ranking=comparison.simple_baseline_ranking,
                              strongest_simple_baseline_id=comparison.strongest_simple_baseline_id,
                              r0_exact_equivalence=comparison.r0_exact_equivalence, decision=comparison.decision,
                              structural_representation_status="NOT_ASSESSED_BY_BOUND_FIXTURES")
            self.validate_results(config, plans, tuple(self.results), comparison.registry_digest)
            artifact = _record("MatrixArtifact", execution_plan_digest=self.plan.record_digest,
                               execution_authorization_digest=self.authorization.record_digest,
                               reservation_digest=self.reservation.record_digest, status="COMPLETED",
                               ordered_cell_evidence=[item.payload() for item in self.evidence],
                               ordered_cell_evidence_digests=[item.record_digest for item in self.evidence],
                               comparison_payload=payload.payload(), comparison_digest=payload.record_digest,
                               technical_errors=dict(comparison.per_arm_error_counts),
                               source_final_check={"unchanged": True, "source_manifest": self.manifest.payload(),
                                                   "execution_plan": self.plan.payload(), "authorization": self.authorization.payload(),
                                                   "reservation": self.reservation.payload(), "cell_starts": [item.payload() for item in self.starts]},
                               structural_representation_status="NOT_ASSESSED_BY_BOUND_FIXTURES")
            return self._finish_publication(artifact)
        except BaseException as exc:
            self._publication_failure(artifact, exc)
            raise
        finally:
            try:
                self.store.close()
            finally:
                self._lock.release()

    def _finish_publication(self, artifact):
        _require(self.status == "RUNNING" and len(self.journal) == 112
                 and not self._final_flush_confirmed and not self._final_content_verified,
                 "publication is not fresh")
        self.store.write_new(self.store.paths["staging"], artifact)
        self._verify_artifact(self.store.paths["staging"], artifact)
        self._journal("SEALED", artifact=artifact.record_digest)
        self.status = "SEALED"
        self.store.publish()
        self._final_flush_confirmed = True
        self._verify_artifact(self.store.paths["final"], artifact)
        self._final_content_verified = True
        self._journal("COMPLETED", artifact=artifact.record_digest)
        self._verify_completion(artifact)
        self._completion_proof_digest = artifact.record_digest
        self.status = "COMPLETED"
        return artifact

    def _verify_completion(self, artifact):
        """Read-only proof, also usable with trusted context after process loss."""
        self._verify_artifact(self.store.paths["final"], artifact)
        directory = self.store.paths["reservation"]
        _require((directory / "reservation.json").read_bytes() == _json_bytes(self.reservation.payload()),
                 "completion reservation differs")
        _require(len(self.journal) in (113, 114), "completion journal prefix incomplete")
        previous = None
        for ordinal in range(1, 115):
            raw = (directory / f"journal-{ordinal:03d}.json").read_bytes()
            entry = _unrecord("AttemptJournalEntry", _loads(raw))
            data = entry.payload()
            _require(raw == _json_bytes(data) and data["reservation_digest"] == self.reservation.record_digest
                     and data["journal_ordinal"] == ordinal
                     and data["previous_journal_entry_digest_or_null"] == previous,
                     "completion journal chain differs")
            if ordinal <= 112:
                _require(entry == self.journal[ordinal - 1] and data["status"] == "RUNNING",
                         "completion cell journal differs")
            else:
                expected = _record("AttemptJournalEntry", reservation_digest=self.reservation.record_digest,
                                   journal_ordinal=ordinal, previous_journal_entry_digest_or_null=previous,
                                   status="SEALED" if ordinal == 113 else "COMPLETED",
                                   cell_start_digest_or_null=None, cell_evidence_digest_or_null=None,
                                   sealed_artifact_digest_or_null=artifact.record_digest, error_or_null=None)
                _require(entry == expected, "completion terminal proof differs")
                if ordinal <= len(self.journal):
                    _require(entry == self.journal[ordinal - 1], "completion in-memory journal differs")
            previous = entry.record_digest

    def _publication_failure(self, artifact, exc):
        # A visible final file is not proof that publish's volume flush returned.
        if artifact is not None and self._final_flush_confirmed and self._final_content_verified:
            if self.status == "COMPLETED" and self._completion_proof_digest == artifact.record_digest:
                return
            try:
                self._verify_completion(artifact)
                self._completion_proof_digest = artifact.record_digest
                self.status = "COMPLETED"
                return
            except BaseException:
                pass
        try:
            visible = os.path.lexists(self.store.paths["final"])
        except BaseException:
            visible = True
        self.status = "ABORTED_INCOMPLETE" if visible else "FAILED"
        if not visible and self.store.created_reservation:
            try:
                self._journal("FAILED", error={"decision": "METHOD_INVALID", "last_completed_ordinal": len(self.evidence),
                                                "code": getattr(exc, "code", S2DR_ATTEMPT_FAILED), "exception_type": type(exc).__name__})
            except BaseException:
                pass

    def _verify_artifact(self, path: Path, expected: S2EFRecord):
        raw = path.read_bytes()
        record = _unrecord("MatrixArtifact", _loads(raw))
        _require(raw == _json_bytes(record.payload()) and record == expected, "published artifact identity differs")
        data = record.payload()
        _require(data["status"] == "COMPLETED" and data["execution_plan_digest"] == self.plan.record_digest
                 and data["execution_authorization_digest"] == self.authorization.record_digest
                 and data["reservation_digest"] == self.reservation.record_digest
                 and len(data["ordered_cell_evidence"]) == 56 and not any(data["technical_errors"].values()),
                 "published artifact is incomplete")
        comparison = _unrecord("ComparisonPayload", data["comparison_payload"])
        _require(comparison.record_digest == data["comparison_digest"]
                 and comparison.payload()["decision"] != "METHOD_INVALID", "published comparison differs")
        for index, entry in enumerate(data["ordered_cell_evidence"]):
            evidence = _unrecord("CellEvidence", entry)
            _require(evidence == self.evidence[index]
                     and evidence.record_digest == data["ordered_cell_evidence_digests"][index], "published cell seal differs")
            core = entry["core_cell_result"]
            for digest_key, value in (("cell_result_digest", core), ("cell_receipt_digest", core["cell_receipt"]),
                                      ("budget_receipt_digest", core["budget_receipt"])):
                _require(value[digest_key] == _digest({k: v for k, v in value.items() if k != digest_key}),
                         "published inner seal differs")
            for checkpoint in entry["checkpoint_evidence"]:
                _unrecord("CheckpointEvidence", checkpoint)
