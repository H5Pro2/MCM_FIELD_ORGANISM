"""Atomic one-shot publication core for the future Z4-A run 197."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Callable, Iterable

from .z4a_generic_trajectory_runner import Z4ATechnicalPacket, Z4AWorldInput
from .z4a_scalar_evaluation import (
    WORLD_ORDER,
    Z4AScalarEvaluationResult,
    z4a_scalar_result_json_text,
    z4a_scalar_result_json_value,
)


class Z4AOneShotError(RuntimeError):
    """Raised when the one-shot order or publication guard is violated."""


_PREFLIGHT_CONTROL_ORDER = (
    "all_source_bindings_final",
    "all_implementation_digests_match",
    "all_world_packages_materializable",
    "browser_binding_final",
)
_RESERVED_OUTPUT = (
    Path(__file__).resolve().parents[1]
    / "reports"
    / "mcm_z4a_field_encoder_lauf_197.json"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class Z4AOneShotPreflight:
    preflight_id: str
    binding_digests: tuple[tuple[str, str], ...]
    controls: tuple[tuple[str, bool], ...]

    def __post_init__(self) -> None:
        if self.preflight_id != "z4a.run197.preflight.v1":
            raise Z4AOneShotError("one-shot preflight identity changed")
        bindings = tuple(self.binding_digests)
        controls = tuple(self.controls)
        if not bindings or any(
            not isinstance(name, str)
            or not name
            or not isinstance(digest, str)
            or len(digest) != 64
            or any(character not in "0123456789abcdef" for character in digest)
            for name, digest in bindings
        ):
            raise Z4AOneShotError("one-shot binding digests are invalid")
        if tuple(name for name, _ in controls) != _PREFLIGHT_CONTROL_ORDER or any(
            not isinstance(value, bool) for _, value in controls
        ):
            raise Z4AOneShotError("one-shot preflight controls changed")
        object.__setattr__(self, "binding_digests", bindings)
        object.__setattr__(self, "controls", controls)

    def digest(self) -> str:
        return _digest(
            {
                "preflight_id": self.preflight_id,
                "binding_digests": self.binding_digests,
                "controls": self.controls,
            }
        )


@dataclass(frozen=True, slots=True)
class Z4AOneShotReceipt:
    receipt_id: str
    output_path: str
    output_sha256: str
    preflight_digest: str
    packet_count: int
    task_count: int
    matrix_execution_calls: int
    evaluation_calls: int
    atomic_publish_complete: bool
    reserved_output_used: bool

    def __post_init__(self) -> None:
        if self.receipt_id != "z4a.run197.one-shot-receipt.v1":
            raise Z4AOneShotError("one-shot receipt identity changed")
        if self.packet_count != 4 or self.task_count != 168:
            raise Z4AOneShotError("one-shot receipt task inventory changed")
        if self.matrix_execution_calls != 1 or self.evaluation_calls != 1:
            raise Z4AOneShotError("one-shot call count changed")
        if self.atomic_publish_complete is not True:
            raise Z4AOneShotError("one-shot publication is incomplete")


_Preflight = Callable[[], Z4AOneShotPreflight]
_MaterializeWorlds = Callable[[], Iterable[Z4AWorldInput]]
_ExecuteMatrix = Callable[[tuple[Z4AWorldInput, ...]], Iterable[Z4ATechnicalPacket]]
_Evaluate = Callable[[tuple[Z4ATechnicalPacket, ...]], Z4AScalarEvaluationResult]


def _exclusive_marker(path: Path, text: str) -> None:
    try:
        with path.open("x", encoding="ascii", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise Z4AOneShotError(f"one-shot marker already exists: {path.name}") from exc


def execute_z4a_one_shot(
    output_path: str | Path,
    *,
    preflight: _Preflight,
    materialize_worlds: _MaterializeWorlds,
    execute_matrix: _ExecuteMatrix,
    evaluate: _Evaluate,
    allow_reserved_output: bool = False,
) -> Z4AOneShotReceipt:
    """Run one injected matrix call and atomically publish one validated JSON."""

    if not all(callable(item) for item in (preflight, materialize_worlds, execute_matrix, evaluate)):
        raise Z4AOneShotError("one-shot stages must be callable")
    if not isinstance(allow_reserved_output, bool):
        raise Z4AOneShotError("reserved output authorization flag must be boolean")
    target = Path(output_path).resolve()
    reserved = target == _RESERVED_OUTPUT.resolve()
    if reserved and not allow_reserved_output:
        raise Z4AOneShotError("reserved Lauf-197 output is not execution-authorized")
    if target.exists():
        raise Z4AOneShotError("one-shot output already exists")
    target.parent.mkdir(parents=True, exist_ok=True)
    lock_path = target.with_name(target.name + ".lock")
    attempt_path = target.with_name(target.name + ".attempted")
    if attempt_path.exists():
        raise Z4AOneShotError("a previous matrix attempt requires manual review")
    _exclusive_marker(lock_path, "z4a-one-shot-lock\n")
    temporary_path: Path | None = None
    matrix_started = False
    try:
        if target.exists():
            raise Z4AOneShotError("one-shot output appeared during preflight")
        preflight_result = preflight()
        if not isinstance(preflight_result, Z4AOneShotPreflight):
            raise Z4AOneShotError("preflight returned an invalid result")
        if not all(value for _, value in preflight_result.controls):
            failed = tuple(name for name, value in preflight_result.controls if not value)
            raise Z4AOneShotError(f"one-shot preflight failed: {failed}")
        worlds = tuple(materialize_worlds())
        if len(worlds) != 4 or any(not isinstance(world, Z4AWorldInput) for world in worlds):
            raise Z4AOneShotError("one-shot requires four materialized worlds")
        if tuple(world.world_id for world in worlds) != WORLD_ORDER:
            raise Z4AOneShotError("one-shot world order changed")
        _exclusive_marker(
            attempt_path,
            json.dumps(
                {
                    "attempt_id": "z4a.run197.matrix-attempt.v1",
                    "preflight_digest": preflight_result.digest(),
                },
                allow_nan=False,
                ensure_ascii=True,
                separators=(",", ":"),
                sort_keys=True,
            )
            + "\n",
        )
        matrix_started = True
        matrix_execution_calls = 1
        packets = tuple(execute_matrix(worlds))
        if len(packets) != 4 or any(
            not isinstance(packet, Z4ATechnicalPacket) for packet in packets
        ):
            raise Z4AOneShotError("matrix execution did not return four packets")
        task_count = sum(len(packet.task_inventory) for packet in packets)
        if task_count != 168:
            raise Z4AOneShotError("matrix execution task count changed")
        evaluation_calls = 1
        result = evaluate(packets)
        if not isinstance(result, Z4AScalarEvaluationResult):
            raise Z4AOneShotError("evaluation returned an invalid scalar result")
        text = z4a_scalar_result_json_text(result)
        expected_value = z4a_scalar_result_json_value(result)
        parsed = json.loads(text)
        if parsed != expected_value:
            raise Z4AOneShotError("serialized scalar result failed round-trip validation")
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=target.name + ".tmp.",
            dir=target.parent,
        )
        temporary_path = Path(temporary_name)
        with os.fdopen(descriptor, "w", encoding="ascii", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        with temporary_path.open("r", encoding="ascii") as handle:
            if json.load(handle) != expected_value:
                raise Z4AOneShotError("temporary scalar JSON failed reread validation")
        if target.exists():
            raise Z4AOneShotError("one-shot output appeared before publication")
        try:
            os.link(temporary_path, target)
        except FileExistsError as exc:
            raise Z4AOneShotError("one-shot output already exists at publication") from exc
        temporary_path.unlink()
        temporary_path = None
        with target.open("rb") as handle:
            output_bytes = handle.read()
        if json.loads(output_bytes.decode("ascii")) != expected_value:
            raise Z4AOneShotError("published scalar JSON failed final validation")
        attempt_path.unlink()
        return Z4AOneShotReceipt(
            "z4a.run197.one-shot-receipt.v1",
            str(target),
            hashlib.sha256(output_bytes).hexdigest(),
            preflight_result.digest(),
            len(packets),
            task_count,
            matrix_execution_calls,
            evaluation_calls,
            True,
            reserved,
        )
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
        if lock_path.exists():
            lock_path.unlink()
        if not matrix_started and attempt_path.exists():
            attempt_path.unlink()


def z4a_one_shot_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (Z4AOneShotPreflight, Z4AOneShotReceipt)
        for item in fields(contract)
    )
