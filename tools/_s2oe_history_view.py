"""Pinned historical display only. No runtime, codec, receptor or scan imports."""
import hashlib
import json
from pathlib import Path

VERSION = "s2oe.historical-display.v1"
TOTAL_LIMIT = 4194304
VIEW_LIMIT = 49152
MISSING = "nicht belegt"


class DisplayError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def require(ok, code):
    if not ok:
        raise DisplayError(code)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def root(value, key):
    require(value.get(key) == sha(canonical({k: v for k, v in value.items() if k != key})),
            "DIGEST_INVALID")


def read_bound(base, ref):
    require(set(ref) == {"path", "bytes", "sha256"}, "REFERENCE_FORM_INVALID")
    path = (base / ref["path"]).resolve()
    require(path.is_relative_to(base.resolve()) and not Path(ref["path"]).is_absolute(),
            "REFERENCE_PATH_INVALID")
    try:
        require(0 <= ref["bytes"] <= TOTAL_LIMIT and path.stat().st_size == ref["bytes"],
                "REFERENCE_SIZE_INVALID")
        raw = path.read_bytes()
    except OSError as exc:
        raise DisplayError("REFERENCE_MISSING") from exc
    require(sha(raw) == ref["sha256"], "REFERENCE_HASH_INVALID")
    return raw


def checked_documents(wire, common, proof, session):
    require(wire.get("common_sha256") == session.get("common_sha256") == sha(canonical(common)),
            "COMMON_BINDING_INVALID")
    record = wire["record"]
    core = record["execution"]
    root(common, "common_digest")
    root(proof, "verification_digest")
    require(record["manifest"] == {"$oc_common": "manifest"}, "MANIFEST_REFERENCE_INVALID")
    require(record["status"] == proof["status"] == "RECORDING_COMPLETE"
            and proof["read_only"] is True and proof["evaluation_allowed"] is True,
            "HISTORICAL_COMPLETION_INVALID")
    require(proof["record_digest"] == record["record_digest"]
            and proof["native"]["record_digest"] == core["record_digest"], "PROOF_REFERENCE_INVALID")
    run = common["manifest"]["run_id"]
    require(record["run_id"] == core["run_id"] == run, "RUN_BINDING_INVALID")
    require(session["session"]["run_id"] == run, "SESSION_BINDING_INVALID")
    return record, core


def project(wire, common, proof, session):
    """Return detached display values, not native state or hypothesis completion values."""
    try:
        record, core = checked_documents(wire, common, proof, session)
        specs = common["manifest"]["events"]
        rows, inputs = core["rows"], core["inputs"]
        require(0 < len(rows) == len(inputs) == len(specs) <= 28, "EVENT_COUNT_INVALID")
        require(len(core["scans"]) <= 16, "SCAN_COUNT_INVALID")
        scans = {}
        for item in core["scans"]:
            key = (item["ordinal"], item["role"])
            require(key not in scans, "DUPLICATE_SCAN_REFERENCE")
            scans[key] = item["value"]
        transitions = {x["event"]: x["generations"] for x in proof["native"]["transitions"]}
        births = [None] * 24
        result = []
        for ordinal, (spec, row, inp) in enumerate(zip(specs, rows, inputs, strict=True), 1):
            event, step = inp["event"], row["step"]
            require(spec["ordinal"] == event["ordinal"] == ordinal
                    and spec["event_id"] == event["event_id"]
                    and step["event_digest"] == event["event_digest"], "EVENT_BINDING_INVALID")
            require(row["memory"] in core["states"]
                    and row["post"]["memory_state_digest"] == row["memory"], "STATE_REFERENCE_INVALID")
            gen = row.get("generations")
            if gen is not None:
                require(gen == transitions.get(ordinal) and gen["event"] == ordinal,
                        "GENERATION_REFERENCE_INVALID")
                require(len(gen["births"]) == len(gen["actions"]) == 24, "GENERATION_FORM_INVALID")
                for old, new, action in zip(births, gen["births"], gen["actions"], strict=True):
                    require((new == ordinal if action in ("CREATED", "REPLACED") else
                             new is None if action in ("FREE", "CLEARED") else
                             new == old if action in ("MATCHED", "UNCHANGED") else False),
                            "GENERATION_CHAIN_INVALID")
                births = list(gen["births"])
            require(row["current_births"] == births, "GENERATION_REFERENCE_INVALID")
            primary = scans.get((ordinal, "PRIMARY"))
            candidates, components, rules, areas = [], [], [], []
            if primary is not None:
                audio = "evidence" in primary
                evidence = primary["evidence"] if audio else primary
                receipt_key = "arm_digest" if audio else "result_digest"
                require(primary[receipt_key] == step["scan_receipt_digest"]
                        and evidence["state_digest"] == row["memory"]
                        and evidence["prestate_digest"] == evidence["poststate_digest"] == row["memory"]
                        and evidence["config_digest"] == core["config_digest"], "SCAN_REFERENCE_INVALID")
                require(evidence["decision"] == step["context_status"]
                        and evidence["hypothesis"] == step["hypothesis"], "DECISION_REFERENCE_INVALID")
                operation = inp["operation"]
                cue = operation["cue"] if audio else operation
                require(evidence["cue_digest"] == cue["cue_digest"], "CUE_REFERENCE_INVALID")
                positions = operation["band_plan"].get("observed_bands") if audio else cue.get("visible_positions")
                if positions is not None:
                    require(type(positions) is list and len(set(positions)) == len(positions)
                            and all(type(i) is int and 0 <= i < len(cue["values"]) for i in positions),
                            "POSITIONS_INVALID")
                    components = [dict(index=i, value=cue["values"][i]) for i in positions]
                for name in ("a_recent", "b_stable", "b_stable_auditory"):
                    if name in evidence:
                        areas.append(evidence[name]["status"])
                for bank in evidence["bank_scans"]:
                    role = bank["bank_role"]
                    offset, capacity = {"B4_RECENT": (0, 9), "TSPM_FAST": (9, 3),
                        "B_STABLE_AUDITORY": (12, 8), "B_STABLE_VISUAL": (20, 4)}[role]
                    require(len(bank["records"]) == capacity, "BANK_BINDING_INVALID")
                    for index, candidate in enumerate(bank["records"]):
                        require(candidate["bank_role"] == role
                                and candidate["slot_id"].endswith(f".{index:03d}"), "SLOT_BINDING_INVALID")
                        if candidate["observed_match"]:
                            require(births[offset + index] is not None, "GENERATION_MISSING")
                            candidates.append(dict(bank=role, slot=candidate["slot_id"],
                                slot_digest=candidate["slot_digest"], generation=births[offset + index],
                                support=candidate.get("stable_support"), historical=True))
                    threshold = next((c.get("match_threshold") for c in bank["records"]
                                      if c.get("match_threshold") is not None), None)
                    rules.append(dict(bank=role, rule=primary["rule"] if audio and offset < 12
                        else "historische Mittelwertregel" if audio else "exakte sichtbare Gleichheit",
                        threshold=threshold, schema=evidence["schema"]))
            else:
                require(step["scan_receipt_digest"] is None, "SCAN_REFERENCE_MISSING")
            media = record["media"]["receipts"][ordinal - 1]
            require(media["ordinal"] == ordinal, "MEDIA_REFERENCE_INVALID")
            result.append(dict(ordinal=ordinal, event=event["event_id"], kind=event["event_type"],
                pass_number=spec["pass_number"], window_number=spec["window_number"],
                frame_pts=media.get("frame_pts"), time_base=common["manifest"]["source"]["video_time_base"],
                runtime=[inp["field"]["start_tick"], inp["field"]["end_tick"]],
                perception=step["perception_status"], memory=step["memory_status"],
                state=row["memory"], profile=core["config_digest"], components=components,
                candidates=candidates, rules=rules, areas=areas, context=step["context_status"],
                hypothesis=step["hypothesis"] is not None, errors=step["error_codes"],
                actions=[] if gen is None else gen["actions"]))
        output = dict(version=VERSION, run_id=record["run_id"], historical=True, events=result,
                      record_digest=record["record_digest"], proof_digest=proof["verification_digest"])
        require(len(canonical(output)) <= VIEW_LIMIT, "VIEW_LIMIT")
        return json.loads(canonical(output))
    except (KeyError, IndexError, TypeError) as exc:
        raise DisplayError("EVIDENCE_FORM_INVALID") from exc


def load(base, binding):
    require(binding["version"] == VERSION, "VERSION_INVALID")
    documents = {k: json.loads(read_bound(base, ref)) for k, ref in binding["documents"].items()}
    require(set(documents) == {"wire", "common", "proof", "session"}, "DOCUMENT_SET_INVALID")
    value = project(**documents)
    require(value["run_id"] == binding["run_id"], "RUN_BINDING_INVALID")
    return value


def page(template, data):
    # Escaping '<' prevents script termination even with untrusted event labels.
    encoded = canonical(data).decode().replace("<", "\\u003c")
    result = template.replace(b"<script>",
        ("<script>window.MCM_HISTORY=" + encoded + ";</script><script>").encode(), 1)
    require(len(result) <= 65536, "HTML_LIMIT")
    return result
