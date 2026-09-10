"""Task assessment of verified evidence; no advances, scans or file access."""
from tools._s2ob_private_state_evidence import canonical
from hashlib import sha256


class EvaluationError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def digest(x):
    return sha256(canonical(x)).hexdigest()


def require(ok, code):
    if not ok:
        raise EvaluationError(code)


def evaluate(record, proof, plan):
    try:
        for x, k in ((record, "record_digest"), (proof, "verification_digest"),
                     (proof["core"], "verification_digest"), (plan, "evaluation_digest")):
            require(x[k] == digest({a: b for a, b in x.items() if a != k}), "DIGEST_INVALID")
        require(record["status"] == "RECORDING_COMPLETE" and proof["evaluation_allowed"] is True
                and proof["core"]["evaluation_allowed"] is True and proof["read_only"] is True
                and proof["core"]["record_digest"] == record["record_digest"], "NOT_VERIFIED")
        events = record["manifest"]["events"]
        require(record["manifest"]["manifest_digest"] == plan["manifest_digest"], "PLAN_INVALID")
        rows = record["execution"]["rows"]
        require(len(events) == len(rows) == 21, "INCOMPLETE")
        target = plan["roles"]["A"]
        origins = [set() for _ in range(24)]
        obs, decisions = {}, []
        transitions = {t["event"]: t for t in proof["core"]["core"]["transitions"]}
        for n, (event, row) in enumerate(zip(events, rows), 1):
            body = record["execution"]["states"][row["memory"]]["body"]
            ts = body["tspm_state"]
            slots = body["b4_state"]["entries"] + sum([ts[k]["slots"] for k in
                ("fast_state", "auditory_ppb1_state", "visual_ppb1_state")], [])
            g = row["generations"]
            if g is not None:
                source = event["rgb"]["path"].split("/")[-1]
                for i, action in enumerate(g["actions"]):
                    incoming = {source}
                    if i >= 12 and action in ("CREATED", "REPLACED", "MATCHED"):
                        selected = transitions[n]["fast_selected"]
                        incoming = next(origins[j] for j in range(9, 12) if slots[j]["slot_id"] == selected)
                    if action in ("FREE", "CLEARED"):
                        origins[i] = set()
                    elif action in ("CREATED", "REPLACED"):
                        origins[i] = set(incoming)
                    elif action == "MATCHED":
                        origins[i] |= incoming
            a = [i for i, s in enumerate(slots) if s["occupied"] and target in origins[i]]
            b = [[i, row["current_births"][i]] for i in a if i >= 20]
            obs[n] = dict(b4=sum(i < 9 for i in a), fast=sum(9 <= i < 12 for i in a), b=b,
                support=[slots[i]["support_count"] for i in a if i >= 9],
                visual=sum(s["occupied"] for s in slots[20:]))
            for expected in plan["decisions"]:
                if event["event_id"] != expected["event"]:
                    continue
                h = row["step"]["hypothesis"]
                status = "ADMIT_SINGLE_CONTEXT" if h else row["step"]["context_status"]
                ids = [] if not h else h["provenance_slot_digests"]
                scan = next(s["value"] for s in record["execution"]["scans"] if s["ordinal"] == n and s["role"] == "PRIMARY")
                selected = [r["slot_id"] for bank in scan["bank_scans"] for r in bank["records"] if r["slot_digest"] in ids]
                found = [i for i, s in enumerate(slots) if s["slot_id"] in selected]
                own = len(found) == len(ids) > 0 and all(slots[i]["occupied"] and row["current_births"][i] is not None
                    and origins[i] == {target} and (i < 12 if h["area"] == "A_RECENT" else i >= 20) for i in found)
                ok = status == expected["status"] and (h["area"] if h else None) == expected["area"] and (own if h else True)
                decisions.append(dict(event=n, status=status, area=h["area"] if h else None, target=own, confirmed=ok))
        o = obs
        replacement = bool(o[15]["b"]) and all(birth != 20 and rows[19]["current_births"][i] == 20 and rows[19]["generations"]["actions"][i] == "REPLACED" for i, birth in o[15]["b"])
        checks = [o[5]["support"] == [2, 3, 3], o[13]["fast"] == 0 and o[13]["b4"] == 1,
                  o[14]["fast"] == o[14]["b4"] == 0 and bool(o[14]["b"]), o[16]["visual"] == 4,
                  replacement and not o[20]["b"] and not o[21]["b"]]
        result = dict(decisions=decisions, checkpoints=[dict(event=n, confirmed=c, observed=o[n]) for n, c in zip((5, 13, 14, 16, 20), checks)],
            record_digest=record["record_digest"], verification_digest=proof["verification_digest"],
            plan_digest=plan["evaluation_digest"], status="CONFIRMED" if all(checks) and len(decisions) == 3 and all(d["confirmed"] for d in decisions) else "FALSIFIED")
        result["evaluation_digest"] = digest(result)
        require(len(canonical(result)) <= 3000, "OUTPUT_LIMIT")
        return result
    except EvaluationError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, StopIteration) as exc:
        raise EvaluationError("EVIDENCE_INVALID") from exc
