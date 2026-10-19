"""Read-only, versioned provenance outcomes. No execution or publication callers.

Pointers address the decoded S2-UC codec tree (Frame attributes included).
Their document hashes always refer to the original, unmodified input bytes.
Synthetic fixture admission is separate and never a run authorization.
"""
import copy
import hashlib
from pathlib import Path

from tools import _s2uc_source_execution_binding as binding
from tools import _s2uc_source_binding as science
from tools import _s2uc_run_binding as targets
from tools import _s2uc_evaluation as legacy
from tools import _s2uc_record_codec as codec
from tools import _s2uc_execution_v8 as verification
from tools._s2uc_resource_contract_v7 import _same_typed

VERSION = "s2uc.provenance-outcomes.v1"
FIXTURE_VERSION = "s2uc.provenance-neutral-test-binding.v1"
OFFSETS = {("g1", 12): 1, ("g1", 24): 2, ("g1", 26): 0, ("g2", 38): 1,
           ("g3", 60): 2, ("g3", 67): 2, ("g3", 69): 0}
ARMS = ("immediate", "candidate")
FILENAMES = {"binding": "execution-binding.json", "manifest": "manifest.json",
             "record": "record.json", "verification": "verification.json", "terminal": "terminal.json"}


def _need(ok, reason):
    if not ok:
        raise ValueError(reason)


def _ref(name, data):
    return {"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def _number(value):
    _need(type(value) is int and value > 0, "PROVENANCE_GENERATION_INVALID")
    return value


def _owner(story, arm):
    return f"s2uc-{story}-" + ("tw" if arm == "immediate" else "candidate")


def _blank(refs, reason):
    rows = []
    for key, target in targets.TARGETS.items():
        rows.append({"key": f"{key[0]}/{key[1]}", "target": copy.deepcopy(target), "offset": OFFSETS[key],
                     "arms": {arm: {"classification": "NICHT_BESTIMMBAR", "correct_target_recall": None,
                                     "reason": reason} for arm in ARMS},
                     "target_recall_gain": None, "target_recall_loss": None,
                     "comparison": "NOT_DETERMINABLE", "preservation_gain": None,
                     "legacy_expectation": {"expected": list(legacy.EXPECTED[key]), "fulfilled": None}})
    return {"version": VERSION, "status": "NOT_EVALUABLE", "scope": "NEUTRAL_DEVELOPMENT_ONLY",
            "inputs": refs, "reason": reason, "hints": rows, "candidate_gains": [], "candidate_losses": [],
            "not_determinable": [r["key"] for r in rows], "coverage": {"determinate": 0, "total": 7},
            "gain_count": None, "loss_count": None, "counts_status": "NOT_DETERMINABLE",
            "real_execution_authorized": False, "mechanisms": [], "lineages": {}}


def _manifest(value):
    science.validate(value)
    bare = {k: v for k, v in value.items() if k not in ("binding_digest", "binding_bytes")}
    _need(value["binding_digest"] == science.digest(bare)
          and type(value["binding_bytes"]) is int and value["binding_bytes"] == len(science.canonical(bare)),
          "PROVENANCE_MANIFEST_DIGEST_INVALID")
    template = science.manifest()  # Reads the fixed plan; never produces NU.
    _need(value["profile"] == template["profile"] and value["limits"] == template["limits"],
          "PROVENANCE_MANIFEST_PROFILE_OR_LIMITS_INVALID")
    symbols, endpoints = {}, {}
    for event, expected in zip(value["events"], template["events"], strict=True):
        _need(_same_typed({k: v for k, v in event.items() if k != "endpoint"},
                         {k: v for k, v in expected.items() if k != "endpoint"}), "PROVENANCE_EVENT_SCHEDULE_INVALID")
        if "endpoint" not in expected:
            continue
        endpoint = event["endpoint"]
        original = expected["endpoint"]
        _need(set(endpoint) == set(original), "PROVENANCE_ENDPOINT_SCHEMA_INVALID")
        _need(_same_typed({k: v for k, v in endpoint.items() if k not in ("source_id", "pcm_sha256")},
                         {k: v for k, v in original.items() if k not in ("source_id", "pcm_sha256")}),
              "PROVENANCE_ENDPOINT_GEOMETRY_INVALID")
        source_id = endpoint["source_id"]
        _need(type(source_id) is str and bool(source_id), "PROVENANCE_SOURCE_ID_INVALID")
        symbol = original["source_id"]
        _need(symbols.setdefault(symbol, source_id) == source_id, "PROVENANCE_SOURCE_SCHEDULE_INVALID")
        _need(_same_typed(endpoints.setdefault(source_id, endpoint), endpoint), "PROVENANCE_SOURCE_BINDING_INVALID")
    _need(len(set(symbols.values())) == 5, "PROVENANCE_FIVE_SOURCE_IDENTITIES_REQUIRED")


def _gate(packet, fixture):
    _need(set(packet) == set(FILENAMES) and all(type(v) is bytes for v in packet.values()),
          "PROVENANCE_INPUT_BYTES_REQUIRED")
    caps = {"binding": binding.resources.LIMITS["metadata"], "manifest": binding.resources.LIMITS["metadata"],
            "record": binding.resources.RESERVES["record"], "verification": binding.resources.RESERVES["verification"],
            "terminal": binding.resources.LIMITS["terminal"]}
    _need(all(0 < len(data) <= caps[name] for name, data in packet.items()), "PROVENANCE_INPUT_BUDGET_INVALID")
    parsed = {k: binding.old._json(data) for k, data in packet.items()}  # Reject duplicate JSON keys, including codec.
    b, manifest, proof, terminal = (parsed[k] for k in ("binding", "manifest", "verification", "terminal"))
    _need(b["version"] == (FIXTURE_VERSION if fixture else binding.VERSION), "PROVENANCE_BINDING_VERSION_INVALID")
    auth = {"kind": "SYNTHETIC_PROVENANCE_TEST"} if fixture else {"kind": "ONE_NEUTRAL_EXECUTION", "max_uses": 1,
                                                               "payload": "SYNTHETIC_NONZERO_F32LE"}
    _need(_same_typed(b["authorization"], {**auth, "real_sources": False}), "PROVENANCE_NEUTRAL_SCOPE_REQUIRED")
    refs = {k: _ref(FILENAMES[k], v) for k, v in packet.items()}
    _need(_same_typed({k: b["artifacts"]["manifest"][k] for k in ("path", "bytes", "sha256")}, refs["manifest"]),
          "PROVENANCE_MANIFEST_REFERENCE_INVALID")
    _manifest(manifest)
    _need(terminal["version"] == "s2uc.neutral-integration.v9"
          and proof["version"] == "s2uc.verification-evaluation.v9"
          and terminal["scope"] == proof["scope"] == "NEUTRAL_DEVELOPMENT_ONLY"
          and terminal["status"] == "CLOSED_NEUTRAL_VERIFIED" and terminal["evaluation_allowed"] is True
          and terminal["primary_error"] is None and terminal["secondary_errors"] == [],
          "PROVENANCE_COMPLETE_CLOSURE_REQUIRED")
    _need(_same_typed(terminal["prestart_binding"], refs["binding"])
          and _same_typed(terminal["record"], refs["record"])
          and _same_typed(terminal["verification"], refs["verification"])
          and _same_typed(proof["record"], refs["record"]), "PROVENANCE_CLOSURE_HASH_INVALID")
    record = codec.loads(packet["record"])
    _need(record["status"] == "COMPLETE" and record["execution"]["run_id"] == b["run_id"]
          and record["execution"]["binding_sha256"] == refs["binding"]["sha256"]
          and record["execution"]["contract_id"] == b["contract_id"] == binding.resources.CONTRACT_ID,
          "PROVENANCE_EXECUTION_BINDING_INVALID")
    owners = record["owner_cleanup"]
    _need(len(owners) == 6 and {r["owner"] for r in owners} == {_owner(s, a) for s in ("g1", "g2", "g3") for a in ARMS}
          and all(r["initialized"] is True and r["closed"] is True for r in owners), "PROVENANCE_OWNER_CLOSURE_INVALID")
    technical = verification.verify_materialized(record, manifest, record["source_completion"], owners)
    _need(_same_typed(proof["technical"], technical), "PROVENANCE_TECHNICAL_PROOF_INVALID")
    return record, manifest


def _origins(story, index, manifest):
    events = {r["ordinal"]: (i, r) for i, r in enumerate(story["events"])}
    bound = {r["ordinal"]: (i, r) for i, r in enumerate(manifest["events"])}
    origins = {}
    for i, close in enumerate(story["transitions"]):
        row = events[close["ordinal"]][1]
        formation = row["segment"]
        frames = [r for r in story["events"] if r["kind"] == "FORMATION" and r["segment"] == formation]
        _need(len(frames) == 4, "PROVENANCE_FORMATION_INCOMPLETE")
        links = []
        for frame in frames:
            ordinal = frame["ordinal"]
            event_index, _ = events[ordinal]
            manifest_index, entry = bound[ordinal]
            _need(ordinal < close["ordinal"], "PROVENANCE_FORMATION_TIME_INVALID")
            links.append({"ordinal": ordinal, "event_path": f"/stories/{index}/events/{event_index}",
                          "materialization_path": f"/stories/{index}/events/{event_index}/materialization",
                          "manifest_path": f"/events/{manifest_index}/endpoint", "source_id": entry["endpoint"]["source_id"],
                          "endpoint_sha256": science.digest(entry["endpoint"])})
        origins[formation] = {"formation": formation, "frame_ordinals": [f["ordinal"] for f in frames],
                              "frames": links, "close_ordinal": close["ordinal"],
                              "close_path": f"/stories/{index}/transitions/{i}"}
    return origins, events


def _same_sources(left, right):
    return [r["endpoint_sha256"] for r in left["frames"]] == [r["endpoint_sha256"] for r in right["frames"]]


def _lineages(story, index, origins, events):
    registry, changes = {}, []
    state = {arm: {"retained": {}, "candidate": {}} for arm in ARMS}
    for ti, transition in enumerate(story["transitions"]):
        ordinal = transition["ordinal"]
        origin = origins[events[ordinal][1]["segment"]]
        path = f"/stories/{index}/transitions/{ti}"
        for arm in ARMS:
            receipt = transition[arm]
            action = receipt["action"]
            current = state[arm]
            def create(role, generation, stored, confirmed=None, promoted=None):
                generation = _number(generation)
                key = f"{story['story']}/{arm}/{role}/{generation}"
                _need(key not in registry, "PROVENANCE_GENERATION_REUSED")
                value = {"id": key, "story": story["story"], "arm": arm, "owner": _owner(story["story"], arm),
                         "role": role, "generation": generation, "stored_origin": stored,
                         "created_ordinal": ordinal, "creation_path": path + "/" + arm,
                         "ended_ordinal": None, "confirmations": [] if confirmed is None else [confirmed],
                         "promoted_from": promoted}
                registry[key] = value
                current[role][generation] = key
                return key
            def remove(role, generation, reason, replacement=None):
                generation = _number(generation)
                _need(generation in current[role], "PROVENANCE_REMOVED_GENERATION_MISSING")
                key = current[role].pop(generation)
                registry[key]["ended_ordinal"] = ordinal
                change = {"id": f"{story['story']}/{ordinal}/{arm}/{role}", "story": story["story"], "arm": arm,
                          "ordinal": ordinal, "role": role, "kind": reason, "removed": key,
                          "replacement": replacement, "transition_path": path + "/" + arm,
                          "trigger_origin": origin}
                changes.append(change)
                return key, change
            confirmation = {"ordinal": ordinal, "origin": origin, "transition_path": path + "/" + arm}
            if action == "TRACE_CONFIRMED":
                key = current["retained"][_number(receipt["generation"])]
                confirmation["same_bound_source_sequence"] = _same_sources(registry[key]["stored_origin"], origin)
                registry[key]["confirmations"].append(confirmation)
            elif arm == "immediate" and action == "TRACE_RETAINED":
                old = receipt["evicted"]
                change = remove("retained", old, "RETAINED_EVICTED")[1] if old is not None else None
                new = create("retained", receipt["generation"], origin)
                if change is not None:
                    change["replacement"] = new
            elif arm == "candidate" and action in ("TRACE_CANDIDATE_CREATED", "TRACE_CANDIDATE_REPLACED"):
                change = remove("candidate", receipt["evicted"], "CANDIDATE_REPLACED_BEFORE_PROMOTION")[1] if action.endswith("REPLACED") else None
                new = create("candidate", receipt["candidate_generation"], origin)
                if change is not None:
                    change["replacement"] = new
            elif arm == "candidate" and action == "TRACE_PROMOTED":
                candidate_id, _ = remove("candidate", receipt["candidate_generation"], "CANDIDATE_PROMOTED")
                stored = registry[candidate_id]["stored_origin"]
                _need(not set(stored["frame_ordinals"]) & set(origin["frame_ordinals"]), "PROVENANCE_CONFIRMATION_OVERLAP")
                confirmation["same_bound_source_sequence"] = _same_sources(stored, origin)
                change = remove("retained", receipt["evicted"], "RETAINED_REPLACED_BY_CONFIRMATION")[1] if receipt["evicted"] is not None else None
                new = create("retained", receipt["generation"], stored, confirmation, candidate_id)
                if change is not None:
                    change["replacement"] = new
                    change["confirmation"] = confirmation
            else:
                _need(action in ("TRACE_DISCARDED_INCOMPLETE", "TRACE_CANDIDATE_OVERLAP_NOT_CONFIRMED",
                                 "CONFIRMATION_AMBIGUOUS_EXISTING_TRACE"), "PROVENANCE_TRANSITION_ACTION_INVALID")
    return registry, changes


def _state(snapshot, arm, role, ordinal, registry, events, profile):
    raw = snapshot.get(role)
    pairs = list(raw) if arm == "immediate" and role == "retained" else ([] if raw is None else [raw])
    found = []
    for generation, frames in pairs:
        generation = _number(generation)
        keys = [key for key, entry in registry.items() if entry["arm"] == arm and entry["role"] == role
                and entry["generation"] == generation and entry["created_ordinal"] < ordinal
                and (entry["ended_ordinal"] is None or ordinal < entry["ended_ordinal"])]
        _need(len(keys) == 1, "PROVENANCE_HINT_GENERATION_INVALID")
        entry = registry[keys[0]]
        _need(entry["owner"] == snapshot["owner"] and len(frames) == 4, "PROVENANCE_OWNER_OR_FRAMES_INVALID")
        _need([f.ordinal for f in frames] == entry["stored_origin"]["frame_ordinals"], "PROVENANCE_STORED_ORIGIN_INVALID")
        for frame in frames:
            row = events[frame.ordinal][1]
            _need(frame.owner == snapshot["owner"] and frame.profile == profile and frame.segment == row["segment"]
                  and frame.values == tuple(float.fromhex(v) for v in row["values_hex"]), "PROVENANCE_FRAME_BINDING_INVALID")
        found.append(keys[0])
    active = [key for key, e in registry.items() if e["arm"] == arm and e["role"] == role
              and e["created_ordinal"] < ordinal and (e["ended_ordinal"] is None or ordinal < e["ended_ordinal"])]
    _need(set(found) == set(active) and len(found) == len(set(found)), "PROVENANCE_INVENTORY_INCOMPLETE")
    return found


def _arm_result(receipt, arm, ordinal, registry, events, manifest, hint_path, target, offset):
    before, after = receipt[arm + "_before"], receipt[arm + "_after"]
    _need(_same_typed(before, after), "PROVENANCE_HINT_NOT_READ_ONLY")
    retained = _state(before, arm, "retained", ordinal, registry, events, manifest["profile"])
    candidates = _state(before, arm, "candidate", ordinal, registry, events, manifest["profile"]) if arm == "candidate" else []
    hint_entries = [manifest["events"][ordinal - 2]["endpoint"], manifest["events"][ordinal - 1]["endpoint"]]
    hint_digests = [science.digest(e) for e in hint_entries]
    raw = receipt[arm]
    matches, addresses = [], set()
    for i, address in enumerate(raw["matches"]):
        _need(type(address) in (tuple, list) and len(address) == 2, "PROVENANCE_MATCH_ADDRESS_INVALID")
        generation, pos = address
        _number(generation)
        _need(type(pos) is int and 0 <= pos <= 2 and (generation, pos) not in addresses, "PROVENANCE_MATCH_ADDRESS_INVALID")
        addresses.add((generation, pos))
        selected = [registry[k] for k in retained if registry[k]["generation"] == generation]
        _need(len(selected) == 1, "PROVENANCE_MATCH_NOT_RETAINED")
        entry = selected[0]
        origin = entry["stored_origin"]
        pair = origin["frames"][pos:pos + 2]
        target_origin = origin["formation"] in target["formations"]
        pair_correct = pos == offset and [f["endpoint_sha256"] for f in pair] == hint_digests
        label = "ANDERE_FORMATION" if not target_origin else "ZIEL_PASSEND" if pair_correct else "FALSCHER_OFFSET_ODER_QUELLENPAAR"
        matches.append({"generation": generation, "offset": pos, "lineage": entry["id"], "stored_formation": origin["formation"],
                        "stored_frame_ordinals": origin["frame_ordinals"], "matched_frame_ordinals": [f["ordinal"] for f in pair],
                        "provenance": label, "source_pair_matches_hint": pair_correct,
                        "match_path": hint_path + f"/{arm}/matches/{i}",
                        "confirmation_origins_before_hint": [c for c in entry["confirmations"] if c["ordinal"] < ordinal]})
    decision = raw["decision"]
    _need(decision == ("TRACE_MATCH" if len(matches) == 1 else "ABSTAIN_AMBIGUOUS_RETAINED_TRACE" if matches else "ABSTAIN_NO_RETAINED_TRACE"),
          "PROVENANCE_DECISION_MATCH_COUNT_INVALID")
    classification = ("RICHTIGER_ZIELABRUF" if matches[0]["provenance"] == "ZIEL_PASSEND" else "ANDERER_ABRUF") if len(matches) == 1 else "MEHRDEUTIG" if matches else "ENTHALTUNG_OHNE_MATCH"
    target_retained = [k for k in retained if registry[k]["stored_origin"]["formation"] in target["formations"]]
    target_candidates = [k for k in candidates if registry[k]["stored_origin"]["formation"] in target["formations"]]
    return {"decision": decision, "raw_matches": copy.deepcopy(raw["matches"]), "matches": matches,
            "classification": classification, "correct_target_recall": classification == "RICHTIGER_ZIELABRUF",
            "retained_lineages": retained, "candidate_lineages": candidates, "target_retained": target_retained,
            "target_retained_present": bool(target_retained), "target_only_candidate": not target_retained and bool(target_candidates),
            "target_in_matches": any(m["provenance"] == "ZIEL_PASSEND" for m in matches),
            "abstention_context": None if matches else "EMPTY_RETAINED" if not retained else "TARGET_PRESENT_NO_MATCH" if target_retained else "OTHER_TRACES_PRESENT",
            "hint_path": hint_path, "before_path": hint_path + "/" + arm + "_before",
            "after_path": hint_path + "/" + arm + "_after"}


def _compare(rows, registry, changes):
    for i, row in enumerate(rows):
        story, ordinal = row["story"], row["ordinal"]
        left, right = (row["arms"][a]["correct_target_recall"] for a in ARMS)
        gain, loss = not left and right, left and not right
        row.update(target_recall_gain=gain, target_recall_loss=loss,
                   comparison="TARGET_RECALL_GAIN" if gain else "TARGET_RECALL_LOSS" if loss else "BOTH_CORRECT" if left else "BOTH_NO_TARGET_RECALL",
                   preservation_gain=False, preservation_evidence=[], previous_ua_correct_recall=None)
        relevant = [c for c in changes if c["story"] == story and c["ordinal"] < ordinal
                    and registry[c["removed"]]["stored_origin"]["formation"] in row["target"]["formations"]]
        row["mechanism_refs"] = [c["id"] for c in relevant if c["kind"] != "CANDIDATE_PROMOTED"]
        row["mechanism_details"] = []
        for change in relevant:
            if change["arm"] != "candidate":
                continue
            if change["kind"] == "CANDIDATE_REPLACED_BEFORE_PROMOTION":
                label = "INTERRUPTION_BEFORE_PROMOTION" if row["key"] == "g2/38" else "SINGLE_EXPERIENCE_REPLACED_BEFORE_CONFIRMATION" if row["key"] == "g1/26" else "CANDIDATE_REPLACED_BEFORE_PROMOTION"
                row["mechanism_details"].append({"kind": label, "evidence": change["id"], "previously_retained_loss": False})
            elif change["kind"] == "RETAINED_REPLACED_BY_CONFIRMATION":
                confirmed = change["confirmation"]["same_bound_source_sequence"]
                row["mechanism_details"].append({"kind": "RETAINED_REPLACED_BY_CONFIRMED_COMPETITION" if confirmed else "RETAINED_REPLACED_BY_VALUE_CONFIRMATION_ONLY",
                                                 "evidence": change["id"], "same_source_confirmation": confirmed})
        for previous in rows[:i]:
            if previous["story"] != story or previous["target"]["target"] != row["target"]["target"]:
                continue
            if previous["arms"]["candidate"]["correct_target_recall"]:
                row["previous_ua_correct_recall"] = previous["key"]
            for ua in row["arms"]["candidate"]["target_retained"]:
                if ua not in previous["arms"]["candidate"]["target_retained"]:
                    continue
                for tw in previous["arms"]["immediate"]["target_retained"]:
                    evictions = [c for c in relevant if c["removed"] == tw and c["kind"] == "RETAINED_EVICTED"
                                 and previous["ordinal"] < c["ordinal"]]
                    if gain and not row["arms"]["immediate"]["target_retained"] and evictions and registry[tw]["stored_origin"]["frame_ordinals"] == registry[ua]["stored_origin"]["frame_ordinals"]:
                        row["preservation_gain"] = True
                        row["preservation_evidence"].append({"previous_hint": previous["key"], "ua_lineage": ua,
                                                              "tw_lineage": tw, "eviction": evictions[0]["id"]})
        prior = [p for p in rows[:i] if p["key"] == row["previous_ua_correct_recall"]]
        row["loss_of_previously_demonstrated_ua_recall"] = bool(not right and prior and any(
            c["arm"] == "candidate" and c["kind"] == "RETAINED_REPLACED_BY_CONFIRMATION"
            and prior[0]["ordinal"] < c["ordinal"] < ordinal
            and c["removed"] in prior[0]["arms"]["candidate"]["target_retained"] for c in relevant))
        row["gain_subtype"] = None if not gain else "PRESERVATION_GAIN" if row["preservation_gain"] else "UNIQUE_RECALL_WITH_TW_TARGET_RETAINED" if row["arms"]["immediate"]["target_retained"] else "RECALL_GAIN_WITHOUT_PRESERVATION_PROOF"


def _evaluate_artifacts(packet, *, fixture=False):
    refs = {k: _ref(FILENAMES.get(k, k), v) for k, v in packet.items() if type(v) is bytes} if type(packet) is dict else {}
    try:
        record, manifest = _gate(packet, fixture)
        rows, registry, changes = [], {}, []
        for si, story in enumerate(record["stories"]):
            origins, events = _origins(story, si, manifest)
            local, history = _lineages(story, si, origins, events)
            registry.update(local)
            changes.extend(history)
            for hi, hint in enumerate(story["hints"]):
                ordinal = hint["ordinal"]
                key = (story["story"], ordinal)
                target, expected = targets.TARGETS[key], legacy.EXPECTED[key]
                arms = {a: _arm_result(hint, a, ordinal, local, events, manifest, f"/stories/{si}/hints/{hi}", target, OFFSETS[key]) for a in ARMS}
                actual = [arms[a]["decision"] for a in ARMS]
                rows.append({"key": f"{key[0]}/{key[1]}", "story": key[0], "ordinal": ordinal,
                             "target": copy.deepcopy(target), "offset": OFFSETS[key], "arms": arms,
                             "legacy_expectation": {"expected": list(expected), "actual": actual,
                                                    "fulfilled": actual == list(expected), "controls_provenance": False}})
        _need([(r["story"], r["ordinal"]) for r in rows] == list(targets.TARGETS), "PROVENANCE_SEVEN_HINTS_REQUIRED")
        _compare(rows, registry, changes)
        gains = [r["key"] for r in rows if r["target_recall_gain"]]
        losses = [r["key"] for r in rows if r["target_recall_loss"]]
        return {"version": VERSION, "status": "EVALUATED_NEUTRAL", "scope": "SYNTHETIC_TEST_FIXTURE" if fixture else "NEUTRAL_DEVELOPMENT_ONLY",
                "inputs": refs, "manifest_binding_digest": manifest["binding_digest"], "run_id": record["execution"]["run_id"],
                "pointer_convention": "Decoded codec record tree; Frame attributes addressable. Inputs contain original-byte hashes.",
                "hints": rows, "lineages": registry, "mechanisms": changes, "candidate_gains": gains, "candidate_losses": losses,
                "gain_count": len(gains), "loss_count": len(losses), "counts_status": "COMPLETE", "not_determinable": [],
                "coverage": {"determinate": 7, "total": 7}, "real_execution_authorized": False,
                "subtype_lists": {kind: [r["key"] + "/" + a for r in rows for a in ARMS if r["arms"][a]["classification"] == kind]
                                  for kind in ("ANDERER_ABRUF", "MEHRDEUTIG", "ENTHALTUNG_OHNE_MATCH")}}
    except Exception as exc:
        return _blank(refs, str(exc) or type(exc).__name__)


def evaluate_neutral_fixture(packet):
    """Explicit synthetic-test input; its distinct binding is rejected by starters."""
    return _evaluate_artifacts(packet, fixture=True)


def read_closed(binding_path, directory):
    """Read a current V9 neutral closure only; no writer, supplier or gate change."""
    packet = {}
    try:
        path, directory = Path(binding_path), Path(directory)
        initial = binding.validate(path)
        _need(directory.resolve().as_posix() == initial["output"], "PROVENANCE_OUTPUT_IDENTITY_INVALID")
        _need({p.name for p in directory.iterdir()} == {"record.json", "verification.json", "terminal.json"},
              "PROVENANCE_OUTPUT_NOT_SUCCESS_ONLY")
        for key, name in FILENAMES.items():
            root = path.parent if key in ("binding", "manifest") else directory
            _, packet[key], _ = binding.discovery.read_file(root, name)
        return _evaluate_artifacts(packet)
    except Exception as exc:
        return _blank({k: _ref(FILENAMES[k], v) for k, v in packet.items()}, str(exc) or type(exc).__name__)
