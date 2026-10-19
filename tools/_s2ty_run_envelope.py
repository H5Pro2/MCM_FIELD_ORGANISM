"""One-shot neutral S2-TY envelope; it never materializes source payloads."""
from __future__ import annotations

import hashlib
from pathlib import Path

from tools import _s2ty_record as record
from tools import _s2ty_record_verification as success_verifier
from tools import _s2ty_failure_verification as failure_verifier
from tools import _s2ty_resource_ledger as ledger
from tools import _s2ty_source_time_binding as binding
from tools import _s2ty_audio_materialization as materialization


VERSION = "s2ty.neutral-run-envelope.v1"
CODE_FILES = (
    "_s2ty_event_control.py",
    "_s2ty_evaluation.py",
    "_s2ty_audio_materialization.py",
    "_s2ty_perception_trace_adapter.py",
    "_s2ty_record.py",
    "_s2ty_record_verification.py",
    "_s2ty_failure_verification.py",
    "_s2ty_resource_ledger.py",
    "_s2ty_source_time_binding.py",
    "_s2ty_real_source_supplier.py",
    "_s2ty_real_run_entry.py",
    "_s2tu_retained_trace.py",
    "_s2tw_exact_confirmation.py",
    "_s2tw_source_schedule.py",
    "_s2ts_temporal_trace_run.py",
    "_s2ts_temporal_trace.py",
    "_s2nj_private_auditory_output_projection.py",
    "../mcm_field_organism/log_spectral_receptor.py",
    "../mcm_field_organism/broadband_hearing_path.py",
    "_s2ty_run_envelope.py",
)
RESERVES = {"metadata": 8192, "shared": 8192, "record": 131072, "verification": 32768}


class S2TYRunError(ValueError):
    def __init__(self, code, details=None):
        self.code = code
        self.details = {} if details is None else details
        super().__init__(code)


def _need(ok, code, details=None):
    if not ok:
        raise S2TYRunError(code, details)


def code_hashes():
    root = Path(__file__).parent
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in CODE_FILES}


def neutral_inputs(manifest):
    """Create only deterministic neutral half-value fixtures, never PCM data."""
    values_by_source = {}
    rows = []
    for item in manifest["events"]:
        row = {"ordinal": item["ordinal"], "kind": item["kind"], "segment": item["segment"]}
        endpoint = item.get("endpoint")
        if endpoint is not None:
            values = values_by_source.setdefault(endpoint["source_id"], tuple((index + 1) / 1000.0 for index in range(48)))
            row["payload_sha256"] = endpoint["pcm_sha256"]
            row["profile"] = endpoint["profile"]
            row["nj_snapshot_index"] = endpoint["nj_snapshot_index"]
            row["window_start_sample"] = endpoint["window_start_sample"]
            row["window_end_sample"] = endpoint["window_end_sample"]
            row["values"] = values
        else:
            row["values"] = None
        rows.append(row)
    return rows


def _values_hex(values):
    return [value.hex() for value in values] if type(values) is tuple and all(type(value) is float for value in values) else None


def _provided(row):
    return {
        "payload_sha256": row.get("payload_sha256"), "profile": row.get("profile"),
        "nj_snapshot_index": row.get("nj_snapshot_index"), "window_start_sample": row.get("window_start_sample"),
        "window_end_sample": row.get("window_end_sample"), "values_hex": _values_hex(row.get("values")),
    }


def _event_inputs(manifest, supplied):
    _need(type(supplied) is list and len(supplied) == 26, "INPUT_COUNT_INVALID")
    events = []
    checked = 0; handoffs = []
    for item, row in zip(manifest["events"], supplied):
        ordinal = item["ordinal"]
        _need(type(row) is dict and (row.get("ordinal"), row.get("kind"), row.get("segment")) == (ordinal, item["kind"], item["segment"]), "EVENT_BINDING_INVALID", {"ordinal": ordinal})
        endpoint = item.get("endpoint")
        if endpoint is not None:
            try:
                adapter_values, direct_values, receipt = binding.handoff(
                    manifest,
                    ordinal,
                    payload_sha256=row.get("payload_sha256"),
                    profile=row.get("profile"),
                    snapshot_index=row.get("nj_snapshot_index"),
                    window_start_sample=row.get("window_start_sample"),
                    window_end_sample=row.get("window_end_sample"),
                    values=row.get("values"),
                )
            except binding.S2TYBindingError as exc:
                raise S2TYRunError(exc.code, {"last_completed_endpoint": checked, "attempted_ordinal": ordinal, "arms": {"adapter": 0, "direct": 0}, "source_failure": {"stage": "ENDPOINT", "ordinal": ordinal, "provided": _provided(row)}}) from exc
            _need(adapter_values is direct_values is row["values"] and receipt["same_instance"], "HANDOFF_IDENTITY_INVALID", {"ordinal": ordinal})
            checked += 1
            handoffs.append({"ordinal": ordinal, "source_id": endpoint["source_id"], "pcm_sha256": endpoint["pcm_sha256"], "profile": endpoint["profile"], "nj_snapshot_index": endpoint["nj_snapshot_index"], "window_start_sample": endpoint["window_start_sample"], "window_end_sample": endpoint["window_end_sample"], **receipt})
            events.append({"ordinal": ordinal, "kind": item["kind"], "segment": item["segment"], "values": adapter_values})
        else:
            events.append({"ordinal": ordinal, "kind": item["kind"], "segment": item["segment"], "values": None})
    return events, checked, handoffs


def _balance(manifest, success_bytes, failure_bytes, verification_bytes):
    actual = ledger.ledger(
        ledger.planned_shape(), source_bytes=manifest["binding_bytes"], metadata_bytes=0,
        shared_bytes=0, success_record_bytes=success_bytes, failure_record_bytes=failure_bytes,
        verification_bytes=verification_bytes,
    )
    reserved = ledger.ledger(
        ledger.planned_shape(), source_bytes=manifest["binding_bytes"], metadata_bytes=RESERVES["metadata"],
        shared_bytes=RESERVES["shared"], success_record_bytes=RESERVES["record"],
        failure_record_bytes=RESERVES["record"], verification_bytes=RESERVES["verification"],
    )
    return {"actual": actual, "reserves": RESERVES, "reserved": reserved}


def _attach_budget(envelope, *, success_bytes, failure_bytes, verification_bytes):
    """Include the entire outer envelope in the record class without recursion."""
    for _ in range(8):
        envelope["budget"] = _balance(
            envelope["source_manifest"], len(record.canonical(envelope)) if envelope.get("status") == "COMPLETE" else success_bytes,
            len(record.canonical(envelope)) if envelope.get("status") != "COMPLETE" else failure_bytes,
            verification_bytes,
        )
    return envelope


def _receipt(ordinal, measured):
    values = measured["values"]
    return {
        "ordinal": ordinal,
        "half_values_hex": [value.hex() for value in values],
        "half_values_digest": binding.digest([value.hex() for value in values]),
        **{key: value for key, value in measured.items() if key != "values"},
    }


def _materialization_failure(*, run_id, manifest, owners, expected_code_hashes, error, completed):
    counts = error["counts"]
    progress = {"completed_endpoints": completed, "attempted_ordinal": error.get("ordinal"), "arms": {"adapter": 0, "direct": 0}}
    envelope = {"version": VERSION, "run_id": run_id, "owners": owners, "source_manifest": manifest, "code_hashes": expected_code_hashes, "status": "NOT_EVALUABLE", "failure": {"code": error["code"], "phase": error["phase"], "progress": progress}, "materialization": {"counts": counts, "reached_step": error["reached_step"], "receipts": error["receipts"]}, "handoffs": [], "record": None, "verification": None}
    return _attach_budget(envelope, success_bytes=0, failure_bytes=0, verification_bytes=0)


def run_materialized_once(*, run_id, manifest, payload_supplier, owners, expected_code_hashes):
    """Materialize every bound endpoint on demand before the existing neutral chain."""
    _need(callable(payload_supplier), "PAYLOAD_SUPPLIER_INVALID")
    _need(expected_code_hashes == code_hashes(), "CODE_BINDING_INVALID")
    counters = materialization.MaterializationCounters()
    try:
        binding.validate_static(manifest)
    except binding.S2TYBindingError as exc:
        return _materialization_failure(run_id=run_id, manifest=manifest, owners=owners, expected_code_hashes=expected_code_hashes, error={"code": exc.code, "phase": "SOURCE_BINDING", "ordinal": None, "receipts": [], "counts": counters.snapshot(), "reached_step": counters.reached_step}, completed=0)
    supplied_events, receipts, completed = [], [], 0
    for item in manifest["events"]:
        endpoint = item.get("endpoint")
        if endpoint is None:
            supplied_events.append({"ordinal": item["ordinal"], "kind": item["kind"], "segment": item["segment"], "values": None})
            continue
        try:
            payload = payload_supplier(item["ordinal"], endpoint)
        except Exception as exc:
            return _materialization_failure(run_id=run_id, manifest=manifest, owners=owners, expected_code_hashes=expected_code_hashes, error={"code": type(exc).__name__, "phase": "SOURCE_BINDING", "ordinal": item["ordinal"], "receipts": receipts, "counts": counters.snapshot(), "reached_step": "NONE"}, completed=completed)
        try:
            measured = materialization.materialize(endpoint, payload, counters=counters)
            del payload
        except materialization.S2TYMaterializationError as exc:
            return _materialization_failure(run_id=run_id, manifest=manifest, owners=owners, expected_code_hashes=expected_code_hashes, error={"code": exc.code, "phase": exc.phase, "ordinal": item["ordinal"], "receipts": receipts, "counts": exc.counters, "reached_step": exc.reached_step}, completed=completed)
        completed += 1
        receipts.append(_receipt(item["ordinal"], measured))
        supplied_events.append({"ordinal": item["ordinal"], "kind": item["kind"], "segment": item["segment"], "payload_sha256": measured["pcm_sha256"], "profile": endpoint["profile"], "nj_snapshot_index": endpoint["nj_snapshot_index"], "window_start_sample": endpoint["window_start_sample"], "window_end_sample": endpoint["window_end_sample"], "values": measured["values"]})
    envelope = run_once(run_id=run_id, manifest=manifest, supplied_events=supplied_events, owners=owners, expected_code_hashes=expected_code_hashes)
    envelope["materialization"] = {"counts": counters.snapshot(), "receipts": receipts}
    return _attach_budget(envelope, success_bytes=0, failure_bytes=0, verification_bytes=len(record.canonical(envelope["verification"])) if envelope.get("verification") else 0)


def run_once(*, run_id, manifest, supplied_events, owners, expected_code_hashes):
    """Bind, preflight and execute one neutral trace; no source payload is opened."""
    _need(type(run_id) is str and run_id and type(owners) is dict and set(owners) == {"adapter", "direct"} and owners["adapter"] != owners["direct"], "RUN_BINDING_INVALID")
    _need(expected_code_hashes == code_hashes(), "CODE_BINDING_INVALID")
    try:
        binding.validate_static(manifest)
        events, checked, handoffs = _event_inputs(manifest, supplied_events)
    except (binding.S2TYBindingError, S2TYRunError) as exc:
        details = exc.details if isinstance(exc, S2TYRunError) else {"last_completed_endpoint": 0, "attempted_ordinal": None, "arms": {"adapter": 0, "direct": 0}, "source_failure": {"stage": "MANIFEST"}}
        failure = {"code": exc.code, "phase": "SOURCE_BINDING", "progress": details}
        envelope = {"version": VERSION, "run_id": run_id, "owners": owners, "source_manifest": manifest, "code_hashes": expected_code_hashes, "status": "NOT_EVALUABLE", "failure": failure, "handoffs": [], "record": None, "verification": None}
        return _attach_budget(envelope, success_bytes=0, failure_bytes=0, verification_bytes=0)

    success = record.build(events, manifest["profile"], owners)
    success_data = record.dumps(success)
    verification = success_verifier.verify(success_data) if success["status"] == "COMPLETE" else failure_verifier.verify(success_data)
    envelope = {
        "version": VERSION,
        "run_id": run_id,
        "owners": owners,
        "source_manifest": manifest,
        "code_hashes": expected_code_hashes,
        "status": success["status"],
        "preflight": {"checked_endpoints": checked},
        "handoffs": handoffs,
        "failure": success["result"]["failure"],
        "record": success,
        "verification": verification,
    }
    return _attach_budget(envelope, success_bytes=len(success_data), failure_bytes=0, verification_bytes=len(record.canonical(verification)) if verification else 0)


def _verify_inner_events(manifest, inner_record):
    decoded = record.decode_events(inner_record["inputs"])
    _need(len(decoded) == len(manifest["events"]) == 26, "INNER_EVENT_BINDING_INVALID")
    for outer, inner in zip(manifest["events"], decoded):
        _need((inner["ordinal"], inner["kind"], inner["segment"]) == (outer["ordinal"], outer["kind"], outer["segment"]), "INNER_EVENT_BINDING_INVALID")
        _need((outer.get("endpoint") is None) == (inner["values"] is None), "INNER_EVENT_BINDING_INVALID")
    return decoded


def _verify_handoffs(manifest, handoffs, inner_record):
    endpoints = [item for item in manifest["events"] if "endpoint" in item]
    _need(type(handoffs) is list and len(handoffs) == len(endpoints), "HANDOFF_RECEIPT_INVALID")
    values_by_ordinal = {item["ordinal"]: item["values"] for item in _verify_inner_events(manifest, inner_record)}
    for item, receipt in zip(endpoints, handoffs):
        endpoint, ordinal = item["endpoint"], item["ordinal"]
        _need(type(receipt) is dict and receipt.get("ordinal") == ordinal and receipt.get("same_instance") is True, "HANDOFF_RECEIPT_INVALID")
        for key in ("source_id", "pcm_sha256", "profile", "nj_snapshot_index", "window_start_sample", "window_end_sample"):
            _need(receipt.get(key) == endpoint[key], "HANDOFF_RECEIPT_INVALID")
        values = values_by_ordinal.get(ordinal)
        _need(type(values) is tuple and receipt.get("half_values_digest") == binding.digest([value.hex() for value in values]), "HANDOFF_VALUES_INVALID")


def _verify_materialization_receipt(endpoint, receipt, expected_values=None):
    _need(type(receipt) is dict and receipt.get("pcm_sha256") == endpoint["pcm_sha256"] and receipt.get("payload_bytes") == 19_200, "MATERIALIZATION_RECEIPT_INVALID")
    hex_values = receipt.get("half_values_hex")
    _need(type(hex_values) is list and len(hex_values) == 48 and all(type(value) is str for value in hex_values), "MATERIALIZATION_RECEIPT_INVALID")
    try:
        values = tuple(float.fromhex(value) for value in hex_values)
    except ValueError as exc:
        raise S2TYRunError("MATERIALIZATION_RECEIPT_INVALID") from exc
    _need(all(value.hex() == encoded and 0.0 <= value <= 1.0 for value, encoded in zip(values, hex_values)), "MATERIALIZATION_RECEIPT_INVALID")
    _need(expected_values is None or values == expected_values, "MATERIALIZATION_RECEIPT_INVALID")
    value_digest = binding.digest(hex_values)
    _need(receipt.get("half_values_digest") == value_digest, "MATERIALIZATION_RECEIPT_INVALID")
    projection = receipt.get("projection_binding")
    _need(type(projection) is dict, "MATERIALIZATION_RECEIPT_INVALID")
    payload = {**projection, "values": values}
    _need(receipt.get("projection_digest") == materialization.nj.digest(payload), "MATERIALIZATION_RECEIPT_INVALID")
    _need(
        projection.get("profile_digest") == endpoint["profile"]
        and projection.get("snapshot_index") == endpoint["nj_snapshot_index"]
        and projection.get("window_start_tick") == endpoint["window_start_sample"]
        and projection.get("window_end_tick") == endpoint["window_end_sample"]
        and projection.get("source_state_digest") == receipt.get("raw_state_digest")
        and projection.get("source_values_digest") == receipt.get("source_values_digest")
        and tuple(projection.get("subnormal_band_indices", ())) == tuple(receipt.get("subnormal_band_indices", ()))
        and tuple(projection.get("underflow_band_indices", ())) == tuple(receipt.get("underflow_band_indices", ())),
        "MATERIALIZATION_RECEIPT_INVALID",
    )
    return values


def _verify_materialization_receipts(manifest, receipts, completed, values_by_ordinal=None):
    endpoints = [item for item in manifest["events"] if "endpoint" in item]
    _need(type(receipts) is list and 0 <= completed <= len(endpoints) and len(receipts) == completed, "MATERIALIZATION_RECEIPT_INVALID")
    for item, receipt in zip(endpoints, receipts):
        ordinal = item["ordinal"]
        _need(type(receipt) is dict and receipt.get("ordinal") == ordinal, "MATERIALIZATION_RECEIPT_INVALID")
        _verify_materialization_receipt(item["endpoint"], receipt, None if values_by_ordinal is None else values_by_ordinal[ordinal])


def _verify_materialization(manifest, value, inner_record):
    endpoints = [item for item in manifest["events"] if "endpoint" in item]
    _need(type(value) is dict and value.get("counts") == {"pcm_hashes": 22, "audio_analyses": 22, "nj_projections": 22}, "MATERIALIZATION_COUNT_INVALID")
    receipts = value.get("receipts")
    values_by_ordinal = {item["ordinal"]: item["values"] for item in record.decode_events(inner_record["inputs"])}
    _verify_materialization_receipts(manifest, receipts, len(endpoints), values_by_ordinal)


def _verify_materialization_failure(manifest, envelope):
    failure, materialized = envelope["failure"], envelope.get("materialization")
    _need(type(materialized) is dict, "FAILURE_INVALID")
    progress = failure.get("progress")
    _need(envelope.get("record") is None and envelope.get("handoffs") == [] and type(progress) is dict and progress.get("arms") == {"adapter": 0, "direct": 0}, "FAILURE_INVALID")
    completed, ordinal = progress.get("completed_endpoints"), progress.get("attempted_ordinal")
    _need(type(completed) is int and (ordinal is None or type(ordinal) is int), "FAILURE_PROGRESS_INVALID")
    try:
        binding.validate_static(manifest)
    except binding.S2TYBindingError as exc:
        _need(
            completed == 0 and ordinal is None and failure.get("phase") == "SOURCE_BINDING"
            and failure.get("code") == exc.code and materialized == {
                "counts": {"pcm_hashes": 0, "audio_analyses": 0, "nj_projections": 0},
                "reached_step": "NONE",
                "receipts": [],
            },
            "FAILURE_INVALID",
        )
        return {"status": "VERIFIED_MATERIALIZATION_MANIFEST_FAILURE", "attempted": None}
    if ordinal is None:
        _need(completed == 0 and failure.get("phase") == "SOURCE_BINDING", "FAILURE_PROGRESS_INVALID")
    else:
        _need(1 <= ordinal <= 26 and sum("endpoint" in item for item in manifest["events"][:ordinal - 1]) == completed, "FAILURE_PROGRESS_INVALID")
    counts = materialized.get("counts") if type(materialized) is dict else None
    _need(type(counts) is dict and set(counts) == {"pcm_hashes", "audio_analyses", "nj_projections"} and all(type(value) is int and value >= completed for value in counts.values()), "MATERIALIZATION_COUNT_INVALID")
    _verify_materialization_receipts(manifest, materialized.get("receipts"), completed)
    reached_step = materialized.get("reached_step") if type(materialized) is dict else None
    increments = {
        "NONE": (0, 0, 0),
        "HASH": (1, 0, 0),
        "ANALYZE": (1, 1, 0),
        "NJ": (1, 1, 1),
    }
    _need(reached_step in increments and tuple(counts[key] - completed for key in ("pcm_hashes", "audio_analyses", "nj_projections")) == increments[reached_step], "MATERIALIZATION_COUNT_INVALID")
    _need(failure.get("phase") in {"SOURCE_BINDING", "PCM", "RECEPTOR", "NJ"}, "FAILURE_INVALID")
    return {"status": "VERIFIED_MATERIALIZATION_FAILURE", "attempted": ordinal}


def verify_envelope(envelope):
    _need(type(envelope) is dict and envelope.get("version") == VERSION, "ENVELOPE_INVALID")
    _need(envelope.get("code_hashes") == code_hashes(), "CODE_BINDING_INVALID")
    manifest = envelope.get("source_manifest")
    failure = envelope.get("failure")
    materialized_failure = (
        envelope.get("status") == "NOT_EVALUABLE"
        and type(failure) is dict
        and type(envelope.get("materialization")) is dict
        and envelope.get("record") is None
    )
    if materialized_failure:
        return _verify_materialization_failure(manifest, envelope)
    if envelope.get("status") == "NOT_EVALUABLE" and type(failure) is dict and failure.get("phase") == "SOURCE_BINDING":
        _need(envelope.get("record") is None, "FAILURE_INVALID")
        try:
            binding.validate_static(manifest)
        except binding.S2TYBindingError as exc:
            _need(failure.get("code") == exc.code, "FAILURE_INVALID")
            expected_progress = {"last_completed_endpoint": 0, "attempted_ordinal": None, "arms": {"adapter": 0, "direct": 0}, "source_failure": {"stage": "MANIFEST"}}
            _need(failure.get("progress") == expected_progress and envelope.get("handoffs") == [], "FAILURE_PROGRESS_INVALID")
        else:
            progress = failure.get("progress")
            proof = type(progress) is dict and type(progress.get("source_failure")) is dict and progress["source_failure"].get("stage") == "ENDPOINT"
            _need(proof and progress.get("arms") == {"adapter": 0, "direct": 0} and envelope.get("handoffs") == [], "FAILURE_PROGRESS_INVALID")
            ordinal = progress.get("attempted_ordinal")
            _need(type(ordinal) is int and 1 <= ordinal <= 26 and manifest["events"][ordinal - 1].get("endpoint") is not None, "FAILURE_PROGRESS_INVALID")
            expected_checked = sum("endpoint" in item for item in manifest["events"][:ordinal - 1])
            _need(progress.get("last_completed_endpoint") == expected_checked and progress["source_failure"].get("ordinal") == ordinal, "FAILURE_PROGRESS_INVALID")
            provided = progress["source_failure"].get("provided")
            _need(type(provided) is dict and type(provided.get("values_hex")) is list, "FAILURE_INVALID")
            try:
                values = tuple(float.fromhex(value) for value in provided["values_hex"])
                binding.handoff(manifest, ordinal, payload_sha256=provided.get("payload_sha256"), profile=provided.get("profile"), snapshot_index=provided.get("nj_snapshot_index"), window_start_sample=provided.get("window_start_sample"), window_end_sample=provided.get("window_end_sample"), values=values)
            except binding.S2TYBindingError as exc:
                _need(failure.get("code") == exc.code, "FAILURE_INVALID")
            else:
                raise S2TYRunError("FAILURE_UNCONFIRMED")
        return {"status": "VERIFIED_SOURCE_FAILURE", "attempted": failure["progress"]["attempted_ordinal"]}
    try:
        binding.validate_static(manifest)
    except binding.S2TYBindingError as exc:
        raise S2TYRunError(exc.code) from exc
    _need(type(envelope.get("owners")) is dict and set(envelope["owners"]) == {"adapter", "direct"} and envelope["owners"]["adapter"] != envelope["owners"]["direct"], "RUN_BINDING_INVALID")
    if envelope.get("status") == "COMPLETE":
        _need(envelope.get("record", {}).get("owner") == envelope["owners"] and envelope["record"].get("profile") == manifest["profile"] and envelope["record"].get("status") == envelope["record"].get("result", {}).get("status") == envelope["status"], "RUN_BINDING_INVALID")
        _verify_handoffs(manifest, envelope["handoffs"], envelope["record"])
        if "materialization" in envelope:
            _verify_materialization(manifest, envelope["materialization"], envelope["record"])
        proof = success_verifier.verify(record.dumps(envelope["record"]))
        _need(envelope.get("verification") == proof and envelope.get("preflight", {}).get("checked_endpoints") == 22, "VERIFICATION_INVALID")
        return {"status": "VERIFIED", "events": proof["events"]}
    if envelope.get("status") == "NOT_EVALUABLE":
        _need(envelope.get("record", {}).get("owner") == envelope["owners"] and envelope["record"].get("profile") == manifest["profile"] and envelope["record"].get("status") == envelope["record"].get("result", {}).get("status") == envelope["status"] and envelope.get("failure") == envelope["record"].get("result", {}).get("failure"), "RUN_BINDING_INVALID")
        _verify_handoffs(manifest, envelope["handoffs"], envelope["record"])
        if "materialization" in envelope:
            _verify_materialization(manifest, envelope["materialization"], envelope["record"])
        proof = failure_verifier.verify(record.dumps(envelope["record"]))
        _need(envelope.get("verification") == proof and envelope.get("preflight", {}).get("checked_endpoints") == 22, "VERIFICATION_INVALID")
        return {"status": "VERIFIED_CONTROL_FAILURE", "completed": proof["completed"]}
    raise S2TYRunError("STATUS_INVALID")
