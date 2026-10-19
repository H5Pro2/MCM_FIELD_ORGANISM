"""Independent validation of recorded S2-TY failure progress."""
from __future__ import annotations

from tools import _s2ty_record as record


class Error(ValueError):
    pass


def need(ok, code):
    if not ok:
        raise Error(code)


class Model:
    def __init__(self):
        self.forming = {}
        self.hints = {}
        self.retained = []
        self.generation = 0

    def copy(self):
        value = Model()
        value.forming = {key: list(items) for key, items in self.forming.items()}
        value.hints = {key: list(items) for key, items in self.hints.items()}
        value.retained = list(self.retained)
        value.generation = self.generation
        return value

    def snapshot(self):
        return {
            "generations": [generation for generation, _ in self.retained],
            "forming": [[segment, len(values)] for segment, values in sorted(self.forming.items())],
            "hints": [[segment, len(values)] for segment, values in sorted(self.hints.items())],
        }

    def apply(self, event):
        kind, segment = event["kind"], event["segment"]
        if kind == "FORMATION":
            values = self.forming.setdefault(segment, [])
            need(not self.hints.get(segment) and len(values) < 4, "FORMATION_INVALID")
            values.append(tuple(event["values"]))
            return "TRACE_COMPLETE" if len(values) == 4 else "TRACE_FORMING"
        if kind == "HINT":
            values = self.hints.setdefault(segment, [])
            need(len(values) < 2, "HINT_INVALID")
            values.append(tuple(event["values"]))
            if len(values) == 1:
                return None
            hint = tuple(values)
            self.hints[segment] = []
            matches = [[generation, offset] for generation, trace in self.retained for offset in range(3)
                       if trace[offset] == hint[0] and trace[offset + 1] == hint[1]]
            return {"decision": "TRACE_MATCH" if len(matches) == 1 else "ABSTAIN_AMBIGUOUS_RETAINED_TRACE" if matches else "ABSTAIN_NO_RETAINED_TRACE", "matches": matches}
        need(kind == "CLOSE" and segment in self.forming, "CLOSE_INVALID")
        trace = tuple(self.forming.pop(segment))
        self.hints.pop(segment, None)
        need(len(trace) == 4, "FORMATION_INVALID")
        equal = [item for item in self.retained if item[1] == trace]
        if len(equal) == 1:
            return {"action": "TRACE_CONFIRMED", "generation": equal[0][0], "evicted": None}
        need(not equal, "AMBIGUOUS_INVALID")
        self.generation += 1
        next_retained = [*self.retained, (self.generation, trace)]
        evicted = None if len(next_retained) <= 2 else next_retained.pop(0)[0]
        self.retained = next_retained
        return {"action": "TRACE_RETAINED", "generation": self.generation, "evicted": evicted}


def _after(model, event):
    candidate = model.copy()
    try:
        candidate.apply(event)
    except Error:
        return []
    return [candidate.snapshot()]


def verify(data):
    payload = record.loads(data)
    result = payload["result"]
    need(payload["status"] == result["status"] == "NOT_EVALUABLE", "STATUS_INVALID")
    failure = result["failure"]
    need(type(failure) is dict and type(failure.get("code")) is str and type(failure.get("phase")) is str, "FAILURE_INVALID")
    inputs = record.decode_events(payload["inputs"])
    completed = result["completed"]
    need(type(completed) is int and 0 <= completed == len(result["events"]) <= len(inputs), "COMPLETION_INVALID")
    progress = failure.get("progress")
    need(type(progress) is dict and set(progress) == {"last_completed_ordinal", "attempted_event", "arms"}, "PROGRESS_INVALID")
    expected_last = None if not completed else inputs[completed - 1]["ordinal"]
    need(progress["last_completed_ordinal"] == expected_last and failure.get("completed") == completed and result.get("attempted") == failure.get("attempted"), "PROGRESS_INVALID")
    attempted = progress["attempted_event"]
    if failure["phase"] == "OWNER_CLOSE":
        need(completed == len(inputs) and attempted is None, "OWNER_PROGRESS_INVALID")
    else:
        need(completed < len(inputs) and failure["attempted"] == inputs[completed]["ordinal"], "PROGRESS_INVALID")
        need(attempted == {"ordinal": inputs[completed]["ordinal"], "kind": inputs[completed]["kind"], "segment": inputs[completed]["segment"]}, "ATTEMPT_INVALID")
        need(not failure["code"].startswith("OWNER_CLOSE_FAILED:"), "PRIMARY_ERROR_INVALID")

    model = Model()
    for event, receipt in zip(inputs[:completed], result["events"]):
        need(receipt["ordinal"] == event["ordinal"], "RECEIPT_ORDER_INVALID")
        expected = model.apply(event)
        need(receipt["adapter"] == receipt["direct"] == expected, "RECEIPT_INVALID")
    before = model.snapshot()
    after = _after(model, inputs[completed]) if failure["phase"] != "OWNER_CLOSE" else []
    arms = progress["arms"]
    need(type(arms) is dict and set(arms) == {"adapter", "direct"}, "ARM_PROGRESS_INVALID")
    returned = {}
    for arm in ("adapter", "direct"):
        value = arms[arm]
        need(type(value) is dict and set(value) == {"returned_steps", "state", "changed_without_return"}, "ARM_PROGRESS_INVALID")
        need(type(value["returned_steps"]) is int and completed <= value["returned_steps"] <= completed + 1, "ARM_PROGRESS_INVALID")
        need(type(value["changed_without_return"]) is bool, "ARM_PROGRESS_INVALID")
        if value["returned_steps"] == completed + 1:
            need(value["state"] in after and not value["changed_without_return"], "ARM_STATE_INVALID")
        elif value["state"] == before:
            need(not value["changed_without_return"], "ARM_STATE_INVALID")
        else:
            need(value["state"] in after and value["changed_without_return"], "ARM_STATE_INVALID")
        returned[arm] = value["returned_steps"]
    need(returned["direct"] <= returned["adapter"], "ARM_ORDER_INVALID")

    closes = result["owner_closes"]
    need(type(closes) is list and len(closes) == 2 and {item.get("arm") for item in closes} == {"adapter", "direct"}, "OWNER_CLOSE_INVALID")
    close_by_arm = {item["arm"]: item for item in closes}
    for arm, state in (("adapter", arms["adapter"]["state"]), ("direct", arms["direct"]["state"])):
        close = close_by_arm[arm]
        need(close.get("before") == state["generations"] and type(close.get("closed")) is bool, "OWNER_STATE_INVALID")
        need(close["closed"] or type(close.get("error")) is str, "OWNER_CLOSE_INVALID")
    if failure["phase"] == "OWNER_CLOSE":
        need(failure["code"].startswith("OWNER_CLOSE_FAILED:"), "OWNER_ERROR_INVALID")
        need(any(not item["closed"] and type(item.get("error")) is str for item in closes), "OWNER_ERROR_INVALID")
    return {"status": "VERIFIED_FAILURE_PROGRESS", "cause_confirmed": False, "completed": completed}
