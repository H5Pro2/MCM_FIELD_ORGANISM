"""Isolated, single-use V8 neutral integration. No NU/default source supplier."""
import copy
import threading
from pathlib import Path

from tools import _s2uc_binding_v8 as binding
from tools import _s2uc_resources_v8 as budget
from tools import _s2uc_publication_v7 as publication
from tools import _s2uc_source_adapter as adapter
from tools import _s2uc_neutral_connection as connection
from tools import _s2uc_verification as verification
from tools import _s2nj_private_auditory_output_projection as nj
from tools._s2uc_resource_contract_v7 import _need, _same_typed

GATE = False
_USED = set()
_LOCK = threading.Lock()
_CLOSE = {"tw": connection.ub.ImmediateTwArm.close_owner,
          "candidate": connection.ub.CandidateConfirmationArm.close_owner}


class _Source(adapter.SourceAdapter):
    def __init__(self, bound, supplier):
        super().__init__(bound, supplier)
        self.digests = []
        self.last = None

    def __call__(self, endpoint):
        self.counters.reached_step = "NONE"
        result = super().__call__(endpoint)
        self.digests.append(nj.digest({"endpoint": endpoint, "result": result}))
        self.last = {"endpoint": endpoint, "values_hex": [v.hex() for v in result["values"]],
                     "materialization": {k: v for k, v in result.items() if k != "values"}}
        return result

    def snapshot(self, record=None):
        observed = sum(e["kind"] != "CLOSE" for s in (record or {}).get("stories", []) for e in s["events"])
        complete = self._index == self._successes == len(self._uses)
        if complete:
            self.complete()
        return {"status": "COMPLETE" if complete else "PARTIAL", "attempts": self._index,
                "successes": self._successes, "counters": self.counters.snapshot(),
                "reached_step": self.counters.reached_step, "receipt_digests": list(self.digests),
                "pending": self.last if self._successes == observed + 1 else None}


class _Owners:
    """Register objects before __init__; failed construction cannot hide its peer."""
    def __init__(self):
        self.items = []
        self.result = None
        self.failed = None

    def create(self, cls, profile, name):
        arm = cls.__new__(cls)
        self.items.append((name, arm))
        try:
            cls.__init__(arm, profile, name)
        except Exception:
            self.failed = name
            raise
        return arm

    def close(self):
        if self.result is not None:
            return self.result
        rows = []
        for name, arm in self.items:
            role = "tw" if name.endswith("-tw") else "candidate"
            state = getattr(arm, "store", None) if role == "tw" else arm
            initialized = state is not None and hasattr(state, "_closed")
            row = {"owner": name, "initialized": initialized, "closed": not initialized, "fallback": False}
            if name == self.failed:
                row["construction_failed"] = True
            if initialized:
                if not state._closed:
                    row["fallback"] = True
                    try:
                        _CLOSE[role](arm)
                    except Exception as exc:
                        row["error"] = publication._error(exc)
                row["closed"] = bool(state._closed)
            rows.append(row)
        self.result = rows
        return rows


def _receipt(row, endpoint, expected_digest):
    receipt = row.get("materialization")
    _need(type(receipt) is dict, "V8_MATERIALIZATION_REQUIRED")
    verification._materialization(receipt, endpoint, endpoint["profile"])
    values = tuple(float.fromhex(v) for v in row["values_hex"])
    projected = nj.HalfScaleAuditory48V1(**receipt["projection_binding"], values=values,
                                       projection_digest=receipt["projection_digest"])
    _need((projected.snapshot_index, projected.window_start_tick, projected.window_end_tick) ==
          (endpoint["nj_snapshot_index"], endpoint["window_start_sample"], endpoint["window_end_sample"]),
          "V8_PROJECTION_TIME_INVALID")
    _need(receipt["raw_state_digest"] == projected.source_state_digest
          and receipt["source_values_digest"] == projected.source_values_digest
          and _same_typed(receipt["subnormal_band_indices"], list(projected.subnormal_band_indices))
          and _same_typed(receipt["underflow_band_indices"], list(projected.underflow_band_indices)),
          "V8_RECEIPT_CROSSLINK_INVALID")
    _need(nj.digest({"endpoint": endpoint, "result": {**receipt, "values": values}}) == expected_digest,
          "V8_RECEIPT_LIVE_BINDING_INVALID")


def verify_materialized(record, manifest, source, owners):
    _need(_same_typed(record.get("source_completion"), source), "V8_SOURCE_COMPLETION_INVALID")
    _need(_same_typed(record.get("owner_cleanup"), owners) and all(r["closed"] for r in owners),
          "V8_OWNER_CLEANUP_INVALID")
    attempts, successes = source["attempts"], source["successes"]
    counters = source["counters"]
    _need(all(type(x) is int for x in (attempts, successes, *counters.values()))
          and 0 <= successes <= attempts <= 58 and attempts - successes <= 1, "V8_SOURCE_COUNTER_INVALID")
    h, a, n = (counters[k] for k in ("pcm_hashes", "audio_analyses", "nj_projections"))
    _need(successes <= n <= a <= h <= attempts, "V8_SOURCE_COUNTER_INVALID")
    complete = attempts == successes == 58
    _need(source["status"] == ("COMPLETE" if complete else "PARTIAL"), "V8_SOURCE_STATUS_INVALID")
    expected_step = "NJ" if attempts == successes and successes else "NONE"
    if attempts > successes:
        expected_step = "NJ" if n > successes else "ANALYZE" if a > successes else "HASH" if h > successes else "NONE"
    _need(source["reached_step"] == expected_step, "V8_SOURCE_PHASE_INVALID")
    uses = [e["endpoint"] for e in manifest["events"] if "endpoint" in e]
    events = [e for s in record["stories"] for e in s["events"] if e["kind"] != "CLOSE"]
    _need(len(source["receipt_digests"]) == successes and len(events) <= successes <= len(events) + 1,
          "V8_RECEIPT_COUNT_INVALID")
    for i, row in enumerate(events):
        _receipt(row, uses[i], source["receipt_digests"][i])
    if successes > len(events):
        pending = source["pending"]
        _need(type(pending) is dict and _same_typed(pending["endpoint"], uses[len(events)]), "V8_PENDING_ENDPOINT_INVALID")
        _receipt(pending, uses[len(events)], source["receipt_digests"][-1])
    else:
        _need(source["pending"] is None, "V8_PENDING_ENDPOINT_INVALID")
    if record["status"] == "COMPLETE":
        _need(complete and all(c == 58 for c in counters.values()), "V8_SOURCE_INCOMPLETE")
        return verification.verify(record, manifest, require_source_completion=True)
    _need(record["counts"]["materialization_attempts"] == attempts
          and record["counts"]["materializations"] == successes, "V8_PREFIX_SOURCE_MISMATCH")
    return verification.verify_failure(record, manifest)


class _Publication(publication._Publication):
    limits, reserves = budget.LIMITS, budget.RESERVES
    account = staticmethod(budget.account)
    version, proof_version = "s2uc.neutral-integration.v8", "s2uc.verification-evaluation.v8"

    def __init__(self, path, initial):
        self.path, self.initial = Path(path), initial
        self.directory, self.manifest = Path(initial["output"]), initial["manifest"]
        self.reset()
        self.execution = {"contract_id": budget.CONTRACT_ID, "run_id": initial["run_id"],
                          "binding_sha256": initial["binding"]["sha256"]}

    def check_record(self, record):
        _need(_same_typed(record.get("execution"), self.execution), "V8_EXECUTION_RECORD_INVALID")

    def verify_record(self, record):
        return verify_materialized(record, self.manifest, self.source_snapshot, self.owner_snapshot)


def run_neutral(binding_path, supplier, *, run_id, output_directory):
    """Explicit supplier required; fixed neutral manifest accepts only zero PCM.

    An exclusive output directory persists the consumed identity across normal
    process restarts. Manual deletion/restoration of that directory is outside
    this one-shot lifecycle; this is not a tamper-proof authorization service.
    """
    global GATE
    _need(_LOCK.acquire(blocking=False), "V8_EXECUTION_BUSY")
    try:
        _need(not GATE and run_id not in _USED, "V8_ALREADY_USED")
        initial = binding.validate(binding_path)
        _need(run_id == initial["run_id"] and Path(output_directory).resolve().as_posix() == initial["output"],
              "V8_EXECUTION_IDENTITY_INVALID")
        _need(callable(supplier), "V8_NEUTRAL_SUPPLIER_REQUIRED")
        pub = _Publication(binding_path, initial)
        _need(not pub.directory.exists() and not pub.directory.is_symlink(), "V8_OUTPUT_ALREADY_EXISTS")
        pub.directory.mkdir()  # Exclusive claim, before adapter or any supplier.
        _USED.add(run_id)
        source, owners, record = None, _Owners(), None
        GATE = True
        try:
            pub.phase = "CONNECTION"
            source = _Source(initial["sources"], supplier)
            try:
                record = connection.execute(initial["manifest"], source, owners=owners.create)
            finally:
                owner_rows = owners.close()
            if record["status"] != "COMPLETE":
                pub.primary = str(record["failure"]["code"])
            source_rows = source.snapshot(record)
            _need(record["status"] != "COMPLETE" or source_rows["status"] == "COMPLETE", "V8_SOURCE_INCOMPLETE")
            record.update(source_completion=source_rows, owner_cleanup=owner_rows, execution=pub.execution)
            pub.source_snapshot, pub.owner_snapshot = copy.deepcopy(source_rows), copy.deepcopy(owner_rows)
            pub.progress = {"connection_status": record["status"], "counts": record["counts"],
                            "source": {k: v for k, v in source_rows.items() if k not in ("receipt_digests", "pending")},
                            "owner_cleanup": owner_rows}
            pub.phase = "CODEC"
            result = publication._finish_record(pub, publication.codec.dumps(record))
        except Exception as exc:
            pub.progress = {"record_available": record is not None, "owner_cleanup": owners.close(),
                            "source": None if source is None else {"attempts": source._index, "successes": source._successes,
                                                                  "counters": source.counters.snapshot()}}
            result = pub.failure(exc)
        return {**result, "run_id": run_id, "scope": "NEUTRAL_ONLY", "source_completion":
                None if source is None else {"attempts": source._index, "successes": source._successes,
                                            "status": "COMPLETE" if source._index == source._successes == 58 else "PARTIAL",
                                            "reached_step": source.counters.reached_step,
                                            "counters": source.counters.snapshot()}, "owner_cleanup": owners.close()}
    finally:
        GATE = False
        _LOCK.release()
