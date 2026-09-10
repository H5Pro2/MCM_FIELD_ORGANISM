"""OA plan identifiers and LM identifiers are different, root-bound domains."""
import re
from tools import _s2oa_private_runtime_binding as r

SCHEMA = "s2oa.event-id-binding.v1"
QUAL_ID = "s2oa-event-id-qualification-20260910-01"
MAX_BYTES = 2048
QUAL_BYTES = 4096
TEST_COUNT = 14
OLD_HASHES = {
    "tools/_s2oa_private_main_binding.py": "d261c1dcc1a9fe4b61df3fac04086141a52181cfb5cf5efe590b2648900cb13c",
    "tools/_s2oa_private_main_verification.py": "5eff0e5ad77e62bff9f0135ea9e9644e70c9da0bd1dbbcb1ddfd7b3d58f0be6f",
}
OWN = ("tools/_s2oa_private_event_ids.py", "tests/test_s2oa_private_event_ids.py",
       "reports/s2oa/qualify_event_ids_once.py", "reports/s2oa/EVENT_ID_QUALIFIKATIONSBINDUNG.md")


def build(execution):
    rows = []
    for n, event in enumerate(execution["events"], 1):
        r.require(type(event["ordinal"]) is int and event["ordinal"] == n
                  and event["event_id"] == f"e{n:02d}", "ID_PLAN_INVALID")
        rows.append([n, event["event_id"], f"s2oa-event-e{n:02d}"])
    value = r.sealed(dict(schema=SCHEMA, execution_digest=execution["execution_digest"],
        columns=["ordinal", "plan_id", "technical_id"], rows=rows), "id_binding_digest")
    validate(value, execution)
    return value


def validate(value, execution):
    r.require(type(value) is dict and set(value) == {"schema", "execution_digest", "columns", "rows", "id_binding_digest"}, "ID_FORM_INVALID")
    r.require(value["schema"] == SCHEMA and value["columns"] == ["ordinal", "plan_id", "technical_id"], "ID_FORM_INVALID")
    r.require(type(value["execution_digest"]) is str and re.fullmatch("[0-9a-f]{64}", value["execution_digest"]) is not None
              and value["execution_digest"] == execution["execution_digest"], "ID_ROOT_INVALID")
    r.require(type(value["rows"]) is list and len(value["rows"]) == len(execution["events"]) == 28, "ID_COUNT_INVALID")
    for n, (row, event) in enumerate(zip(value["rows"], execution["events"], strict=True), 1):
        r.require(type(row) is list and len(row) == 3 and type(row[0]) is int
                  and row == [n, f"e{n:02d}", f"s2oa-event-e{n:02d}"]
                  and type(event["ordinal"]) is int and event["ordinal"] == n
                  and event["event_id"] == row[1], "ID_ROW_INVALID")
    r.require(value["id_binding_digest"] == r.digest({k:v for k,v in value.items() if k != "id_binding_digest"}), "ID_DIGEST_INVALID")
    r.require(len(r.canonical(value)) <= MAX_BYTES, "ID_SIZE_INVALID")
    return value


def technical_id(value, event):
    n = event["ordinal"]
    r.require(type(n) is int and 1 <= n <= 28, "ID_EVENT_INVALID")
    row = value["rows"][n-1]
    r.require(row == [n, event["event_id"], f"s2oa-event-e{n:02d}"], "ID_EVENT_INVALID")
    return row[2]
