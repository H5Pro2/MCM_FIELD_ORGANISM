"""Bound, private execution shell for the visual SFA method experiment."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Iterable, Mapping

import numpy as np

from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from tools import _s2sfa_private_visual_method as method


SCHEMA = "s2.sfa.visual.run.v2"
MAX_RECORD_BYTES = 2 * 1024 * 1024
MAX_EVIDENCE_BYTES = 8 * 1024 * 1024
BUDGET_PROFILE = "SFA_EVIDENCE_2M_8M_V1"


class SFAVisualRunError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class SFAVisualSourceError(SFAVisualRunError):
    def __init__(self, code: str, message: str, *, receipts: tuple["SourceReceipt", ...], progress: int) -> None:
        super().__init__(code, message)
        self.receipts = receipts
        self.progress = progress


@dataclass(frozen=True, slots=True)
class LedgerEntry:
    role: str
    bytes: int


@dataclass(frozen=True, slots=True)
class SourceFrame:
    """One locally supplied RGB frame; roles are intentionally not carried here."""

    frame_id: str
    source_id: str
    recipe_digest: str
    sequence_position: int
    frame_index: int
    frame: np.ndarray


@dataclass(frozen=True, slots=True)
class SourceReceipt:
    frame_id: str
    source_id: str
    recipe_digest: str
    sequence_position: int
    frame_index: int
    shape: tuple[int, int, int]
    dtype: str
    payload_sha256: str
    status: str
    observation_digest: str | None

    def payload(self) -> dict[str, object]:
        return asdict(self)


def require_ledger(entries: tuple[LedgerEntry, ...], *, record_bytes: int, temporary_bytes: int, error_reserve_bytes: int) -> int:
    if record_bytes > MAX_RECORD_BYTES:
        raise SFAVisualRunError("RECORD_LIMIT", "record exceeds the 2 MiB limit")
    if any(not item.role or item.bytes < 0 for item in entries) or min(record_bytes, temporary_bytes, error_reserve_bytes) < 0:
        raise SFAVisualRunError("LEDGER_INVALID", "ledger contains invalid entries")
    total = sum(item.bytes for item in entries) + record_bytes + temporary_bytes + error_reserve_bytes
    if total > MAX_EVIDENCE_BYTES:
        raise SFAVisualRunError("EVIDENCE_LIMIT", f"ledger bytes {total} exceed {MAX_EVIDENCE_BYTES}")
    return total


def _canonical(value: object) -> bytes:
    return json.dumps(value, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _record_bytes(record: Mapping[str, object]) -> int:
    return len(_canonical(record))


def _require_record_budget(record: Mapping[str, object]) -> int:
    size = _record_bytes(record)
    if size > MAX_RECORD_BYTES:
        raise SFAVisualRunError("RECORD_LIMIT", f"record bytes {size} exceed {MAX_RECORD_BYTES}")
    return size


def publish_record_once(record: Mapping[str, object], output: Path, *, ledger: tuple[LedgerEntry, ...] | None, error_reserve_bytes: int | None) -> int:
    """Atomically publish one already-bound record; the temporary copy is counted."""

    if ledger is None or error_reserve_bytes is None:
        raise SFAVisualRunError("LEDGER_REQUIRED", "publisher requires the bound ledger and error reserve")
    if output.exists():
        raise SFAVisualRunError("OUTPUT_EXISTS", "result output already exists")
    payload = _canonical(record)
    if len(payload) > MAX_RECORD_BYTES:
        raise SFAVisualRunError("RECORD_LIMIT", "record exceeds atomar record limit")
    require_ledger(ledger, record_bytes=len(payload), temporary_bytes=len(payload), error_reserve_bytes=error_reserve_bytes)
    temporary = output.with_suffix(output.suffix + ".tmp")
    if temporary.exists():
        raise SFAVisualRunError("OUTPUT_EXISTS", "temporary result output already exists")
    try:
        temporary.write_bytes(payload)
        os.replace(temporary, output)
    finally:
        if temporary.exists():
            temporary.unlink()
    return len(payload)


@dataclass(frozen=True, slots=True)
class FrameSpec:
    frame_id: str
    episode: str
    ordinal: int
    time_ms: int
    background: tuple[int, int, int]
    foreground: tuple[int, int, int]
    x: int

    def payload(self) -> dict[str, object]:
        return asdict(self)


def _episode(name: str, background: tuple[int, int, int], foreground: tuple[int, int, int], positions: tuple[int, ...], ordinal: int) -> tuple[FrameSpec, ...]:
    return tuple(FrameSpec(f"{name}{index + 1}", name, ordinal + index, index * 100, background, foreground, x) for index, x in enumerate(positions))


_BACKGROUND = (24, 32, 48)
_POSITIONS = (160, 480, 800, 1120)
_REFERENCE_POSITIONS = (240, 560, 880, 1200)
_TEST_POSITIONS = (320, 640, 960, 1280)
PLAN = (
    *_episode("L1", _BACKGROUND, (224, 64, 64), _POSITIONS, 1),
    *_episode("L2", _BACKGROUND, (64, 224, 64), _POSITIONS, 5),
    *_episode("RA", _BACKGROUND, (224, 64, 64), _REFERENCE_POSITIONS, 9),
    *_episode("RB", _BACKGROUND, (64, 224, 64), _REFERENCE_POSITIONS, 13),
    *_episode("QA", _BACKGROUND, (224, 64, 64), _TEST_POSITIONS, 17),
    *_episode("QB", _BACKGROUND, (64, 224, 64), _TEST_POSITIONS, 21),
    *_episode("QAB", (96, 80, 32), (224, 64, 64), _TEST_POSITIONS, 25),
    *_episode("QC", _BACKGROUND, (64, 64, 224), _TEST_POSITIONS, 29),
)
PLAN_DIGEST = _digest([item.payload() for item in PLAN])
EVALUATION_ROLES = {"QA": "A", "QB": "B", "QAB": "A"}


def _group(values: Mapping[str, tuple[float, ...]], episode: str) -> np.ndarray:
    result = np.asarray([values[item.frame_id] for item in PLAN if item.episode == episode], dtype=np.float64)
    if result.shape != (4, 288) or not np.all(np.isfinite(result)):
        raise SFAVisualRunError("OBSERVATION_INVALID", f"{episode} must contain four finite 288-value observations")
    return result


def materialize_frame(spec: FrameSpec) -> np.ndarray:
    frame = np.empty((1080, 1920, 3), dtype=np.uint8)
    frame[:, :, :] = spec.background
    frame[405:675, spec.x : spec.x + 320, :] = spec.foreground
    return frame


def _source_receipts_digest(receipts: tuple[SourceReceipt, ...]) -> str:
    return _digest([receipt.payload() for receipt in receipts])


def _receipt_for(source: SourceFrame) -> SourceReceipt:
    frame = source.frame
    if not source.frame_id or not source.source_id or not source.recipe_digest:
        raise SFAVisualRunError("SOURCE_BINDING_INVALID", "source receipt requires frame, source and recipe bindings")
    if source.sequence_position < 1 or source.frame_index < 0:
        raise SFAVisualRunError("SOURCE_BINDING_INVALID", "source position or frame index is invalid")
    if frame.ndim != 3 or frame.shape[2] != 3 or frame.dtype != np.uint8:
        raise SFAVisualRunError("SOURCE_FORM_INVALID", "source frame must be uint8 RGB")
    return SourceReceipt(
        frame_id=source.frame_id,
        source_id=source.source_id,
        recipe_digest=source.recipe_digest,
        sequence_position=source.sequence_position,
        frame_index=source.frame_index,
        shape=tuple(int(value) for value in frame.shape),
        dtype=frame.dtype.str,
        payload_sha256=hashlib.sha256(np.ascontiguousarray(frame).tobytes()).hexdigest(),
        status="HASHED_NOT_ANALYZED",
        observation_digest=None,
    )


def observe_sources_once(sources: Iterable[SourceFrame], *, receptor: object | None = None) -> tuple[dict[str, tuple[float, ...]], tuple[SourceReceipt, ...]]:
    """Hash each supplied frame before analysis and retain a receipt without keeping RGB payloads."""

    active_receptor = LocalChannelGridReceptor(VisualGridConfig()) if receptor is None else receptor
    values: dict[str, tuple[float, ...]] = {}
    receipts: list[SourceReceipt] = []
    for source in sources:
        receipt = _receipt_for(source)
        if receipt.frame_id in values or any(item.frame_id == receipt.frame_id for item in receipts):
            raise SFAVisualRunError("SOURCE_BINDING_INVALID", "source frame IDs must be unique")
        receipts.append(receipt)
        try:
            state = active_receptor.analyze(source.frame, frame_index=source.frame_index)
            observation = tuple(float(value) for value in state.channel_values)
            if len(observation) != 288 or not np.all(np.isfinite(observation)):
                raise SFAVisualRunError("OBSERVATION_INVALID", "receptor must return 288 finite values")
            values[receipt.frame_id] = observation
            receipts[-1] = SourceReceipt(**{**receipt.payload(), "status": "ANALYZED", "observation_digest": _digest(list(observation))})
        except SFAVisualRunError as exc:
            raise SFAVisualSourceError(exc.code, str(exc), receipts=tuple(receipts), progress=len(values)) from exc
        except Exception as exc:
            raise SFAVisualSourceError("SOURCE_ANALYSIS_FAILED", str(exc), receipts=tuple(receipts), progress=len(values)) from exc
        finally:
            del source
    return values, tuple(receipts)


def _plan_sources() -> Iterable[SourceFrame]:
    for spec in PLAN:
        yield SourceFrame(
            frame_id=spec.frame_id,
            source_id=f"sfa-plan-frame-{spec.ordinal:02d}",
            recipe_digest=_digest(spec.payload()),
            sequence_position=spec.ordinal,
            frame_index=spec.ordinal,
            frame=materialize_frame(spec),
        )


def observe_plan_once() -> tuple[dict[str, tuple[float, ...]], tuple[SourceReceipt, ...]]:
    return observe_sources_once(_plan_sources())


def _decisions(frozen: method.FrozenLinearSFA, values: Mapping[str, tuple[float, ...]]) -> dict[str, object]:
    raw = {episode: frozen.transform_raw(_group(values, episode)).tolist() for episode in ("RA", "RB", "QA", "QB", "QAB", "QC")}
    feature = {episode: frozen.transform_feature(_group(values, episode)).tolist() for episode in raw}
    decisions = {}
    for episode, expected in EVALUATION_ROLES.items():
        decisions[episode] = {
            "raw": asdict(method.rank_two_references(raw[episode], raw["RA"], raw["RB"], expected_reference=expected)),
            "sfa": asdict(method.rank_two_references(feature[episode], feature["RA"], feature["RB"], expected_reference=expected)),
        }
    decisions["QC"] = {
        "raw_scores": [method.sequence_score(raw["QC"], raw[key]) for key in ("RA", "RB")],
        "sfa_scores": [method.sequence_score(feature["QC"], feature[key]) for key in ("RA", "RB")],
        "status": "OPEN_DIAGNOSTIC",
    }
    return {"raw": raw, "feature": feature, "decisions": decisions}


def _validate_source_receipts(receipts: tuple[SourceReceipt, ...], observations: Mapping[str, tuple[float, ...]], *, complete: bool) -> None:
    plan_by_id = {spec.frame_id: spec for spec in PLAN}
    receipt_ids = [receipt.frame_id for receipt in receipts]
    if len(receipt_ids) != len(set(receipt_ids)):
        raise SFAVisualRunError("SOURCE_BINDING_INVALID", "source receipt IDs must be unique")
    if any(receipt.frame_id not in plan_by_id for receipt in receipts):
        raise SFAVisualRunError("SOURCE_BINDING_INVALID", "source receipt has an unknown frame ID")
    for receipt in receipts:
        spec = plan_by_id[receipt.frame_id]
        if (receipt.sequence_position != spec.ordinal or receipt.frame_index != spec.ordinal or not receipt.source_id
                or len(receipt.recipe_digest) != 64 or receipt.shape != (1080, 1920, 3) or receipt.dtype != "|u1"
                or len(receipt.payload_sha256) != 64):
            raise SFAVisualRunError("SOURCE_BINDING_INVALID", "source receipt form or sequence binding is invalid")
        if receipt.status == "ANALYZED":
            observation = observations.get(receipt.frame_id)
            if observation is None or receipt.observation_digest != _digest(list(observation)):
                raise SFAVisualRunError("SOURCE_BINDING_INVALID", "analyzed receipt does not bind its observation")
        elif receipt.status == "HASHED_NOT_ANALYZED" and receipt.observation_digest is None:
            continue
        else:
            raise SFAVisualRunError("SOURCE_BINDING_INVALID", "source receipt status is invalid")
    if complete and (set(receipt_ids) != set(plan_by_id) or any(receipt.status != "ANALYZED" for receipt in receipts)):
        raise SFAVisualRunError("SOURCE_BINDING_INVALID", "complete record requires analyzed receipts for every plan frame")


def _source_failure_record(*, run_id: str, plan_digest: str, source_error: SFAVisualSourceError,
                           ledger: tuple[LedgerEntry, ...], error_reserve_bytes: int) -> dict[str, object]:
    _validate_source_receipts(source_error.receipts, {}, complete=False)
    payload = {
        "schema": SCHEMA,
        "run_id": run_id,
        "plan_digest": plan_digest,
        "status": "INCOMPLETE",
        "phase": "SOURCE_DELIVERY",
        "progress": source_error.progress,
        "source_receipts": [receipt.payload() for receipt in source_error.receipts],
        "source_receipts_digest": _source_receipts_digest(source_error.receipts),
        "error": {"code": source_error.code, "class": type(source_error).__name__, "message": str(source_error)},
    }
    payload["record_digest"] = _digest(payload)
    _require_record_budget(payload)
    require_ledger(ledger, record_bytes=_record_bytes(payload), temporary_bytes=_record_bytes(payload), error_reserve_bytes=error_reserve_bytes)
    return payload


def _receipts_from_record(record: Mapping[str, object]) -> tuple[SourceReceipt, ...]:
    try:
        raw_receipts = list(record["source_receipts"])
        receipts = tuple(
            SourceReceipt(
                frame_id=str(raw["frame_id"]),
                source_id=str(raw["source_id"]),
                recipe_digest=str(raw["recipe_digest"]),
                sequence_position=int(raw["sequence_position"]),
                frame_index=int(raw["frame_index"]),
                shape=tuple(int(value) for value in raw["shape"]),
                dtype=str(raw["dtype"]),
                payload_sha256=str(raw["payload_sha256"]),
                status=str(raw["status"]),
                observation_digest=None if raw["observation_digest"] is None else str(raw["observation_digest"]),
            )
            for raw in raw_receipts
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise SFAVisualRunError("SOURCE_BINDING_INVALID", "record source receipts are malformed") from exc
    if record.get("source_receipts_digest") != _source_receipts_digest(receipts):
        raise SFAVisualRunError("SOURCE_BINDING_INVALID", "record source receipt digest is invalid")
    return receipts


def run_materialized_once(*, run_id: str, plan_digest: str, observations: Mapping[str, tuple[float, ...]], authorized: bool,
                          source_receipts: tuple[SourceReceipt, ...] | None, ledger: tuple[LedgerEntry, ...] | None,
                          error_reserve_bytes: int | None) -> dict[str, object]:
    if not authorized:
        raise SFAVisualRunError("RUN_NOT_AUTHORIZED", "the one-time method run is not authorized")
    if ledger is None or error_reserve_bytes is None:
        raise SFAVisualRunError("LEDGER_REQUIRED", "entry requires the bound ledger and error reserve")
    require_ledger(ledger, record_bytes=MAX_RECORD_BYTES, temporary_bytes=MAX_RECORD_BYTES, error_reserve_bytes=error_reserve_bytes)
    if source_receipts is None:
        raise SFAVisualRunError("SOURCE_RECEIPTS_REQUIRED", "entry requires source receipts before numerical processing")
    if plan_digest != PLAN_DIGEST or set(observations) != {item.frame_id for item in PLAN}:
        raise SFAVisualRunError("BINDING_INVALID", "plan or observation binding is invalid")
    _validate_source_receipts(source_receipts, observations, complete=True)
    phase = "LEARNING"
    progress = 0
    try:
        learner = method.LinearSFALearner()
        for episode in ("L1", "L2"):
            learner.observe(_group(observations, episode))
            progress += 4
        frozen = learner.freeze()
        phase = "REFERENCE_AND_TEST"
        result = _decisions(frozen, observations)
        progress = 32
        payload = {"schema": SCHEMA, "run_id": run_id, "plan_digest": PLAN_DIGEST, "status": "RECORDING_COMPLETE", "progress": progress,
                   "source_receipts": [receipt.payload() for receipt in source_receipts],
                   "source_receipts_digest": _source_receipts_digest(source_receipts),
                   "frozen": frozen.canonical_payload(), "frozen_digest": frozen.digest,
                   "observations": {key: list(value) for key, value in observations.items()}, **result}
    except (method.SFAError, SFAVisualRunError) as exc:
        payload = {"schema": SCHEMA, "run_id": run_id, "plan_digest": PLAN_DIGEST, "status": "INCOMPLETE", "phase": phase,
                   "progress": progress, "source_receipts": [receipt.payload() for receipt in source_receipts],
                   "source_receipts_digest": _source_receipts_digest(source_receipts),
                   "error": {"code": getattr(exc, "code", "SFA_RUN_ERROR"), "class": type(exc).__name__, "message": str(exc)}}
    payload["record_digest"] = _digest(payload)
    _require_record_budget(payload)
    require_ledger(ledger, record_bytes=_record_bytes(payload), temporary_bytes=_record_bytes(payload), error_reserve_bytes=error_reserve_bytes)
    return payload


def run_plan_once(*, run_id: str, authorized: bool, ledger: tuple[LedgerEntry, ...] | None,
                  error_reserve_bytes: int | None) -> dict[str, object]:
    """Private real entry. It is intentionally not authorized by this module's callers."""

    if not authorized:
        raise SFAVisualRunError("RUN_NOT_AUTHORIZED", "the one-time method run is not authorized")
    if ledger is None or error_reserve_bytes is None:
        raise SFAVisualRunError("LEDGER_REQUIRED", "entry requires the bound ledger and error reserve")
    require_ledger(ledger, record_bytes=MAX_RECORD_BYTES, temporary_bytes=MAX_RECORD_BYTES, error_reserve_bytes=error_reserve_bytes)
    try:
        observations, receipts = observe_plan_once()
    except SFAVisualSourceError as exc:
        return _source_failure_record(run_id=run_id, plan_digest=PLAN_DIGEST, source_error=exc, ledger=ledger,
                                      error_reserve_bytes=error_reserve_bytes)
    return run_materialized_once(run_id=run_id, plan_digest=PLAN_DIGEST, observations=observations, authorized=True,
                                 source_receipts=receipts, ledger=ledger, error_reserve_bytes=error_reserve_bytes)


def verify_read_only(record: Mapping[str, object], *, ledger: tuple[LedgerEntry, ...] | None, error_reserve_bytes: int | None) -> dict[str, object]:
    if ledger is None or error_reserve_bytes is None:
        raise SFAVisualRunError("LEDGER_REQUIRED", "verification requires the bound ledger and error reserve")
    require_ledger(ledger, record_bytes=_record_bytes(record), temporary_bytes=0, error_reserve_bytes=error_reserve_bytes)
    if record.get("record_digest") != _digest({key: value for key, value in record.items() if key != "record_digest"}):
        raise SFAVisualRunError("RECORD_DIGEST_INVALID", "record digest is invalid")
    if record.get("plan_digest") != PLAN_DIGEST:
        raise SFAVisualRunError("BINDING_INVALID", "record plan digest is invalid")
    receipts = _receipts_from_record(record)
    if record.get("status") != "RECORDING_COMPLETE":
        _validate_source_receipts(receipts, {}, complete=False)
        if sum(receipt.status == "ANALYZED" for receipt in receipts) != record.get("progress"):
            raise SFAVisualRunError("SOURCE_BINDING_INVALID", "incomplete source progress does not match analyzed receipts")
        return {"verified": True, "evaluation_allowed": False, "status": "INCOMPLETE_ACCEPTED"}
    observations = {key: tuple(value) for key, value in dict(record["observations"]).items()}
    _validate_source_receipts(receipts, observations, complete=True)
    frozen = method.fit_linear_sfa((_group(observations, "L1"), _group(observations, "L2")))
    if frozen.digest != record.get("frozen_digest"):
        raise SFAVisualRunError("FROZEN_BINDING_INVALID", "independent frozen state differs")
    direct = _decisions(frozen, observations)
    if _canonical(direct["decisions"]) != _canonical(record.get("decisions")):
        raise SFAVisualRunError("SCORE_INVALID", "independent scores differ")
    return {"verified": True, "evaluation_allowed": True, "status": "RECORDING_COMPLETE"}


def evaluate_verified(record: Mapping[str, object], verification: Mapping[str, object], *, ledger: tuple[LedgerEntry, ...] | None,
                      error_reserve_bytes: int | None) -> dict[str, object]:
    if ledger is None or error_reserve_bytes is None:
        raise SFAVisualRunError("LEDGER_REQUIRED", "evaluation requires the bound ledger and error reserve")
    require_ledger(ledger, record_bytes=_record_bytes(record), temporary_bytes=0, error_reserve_bytes=error_reserve_bytes)
    if verification.get("evaluation_allowed") is not True:
        raise SFAVisualRunError("EVALUATION_BLOCKED", "evaluation requires successful verification")
    rows = []
    for episode in EVALUATION_ROLES:
        value = dict(record["decisions"])[episode]
        raw = method.RankDecision(**value["raw"])
        learned = method.RankDecision(**value["sfa"])
        rows.append((episode, raw, learned))
    summary = method.summarize_comparison(tuple(rows))
    return {"additional_correct": list(summary.additional_correct), "losses": list(summary.losses), "confusions": list(summary.confusions),
            "abstentions": list(summary.abstentions), "qc_status": dict(record["decisions"])["QC"]["status"]}
