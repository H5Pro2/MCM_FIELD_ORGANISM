"""Versioned, shared OC closure accounting; no payload or runtime execution."""
from tools import _s2oc_private_session_admission as prior

b = prior.b
VERSION = "s2oc.alternative-closure.v1"
ERROR_LIMIT = 4096


class BudgetError(prior.AdmissionError):
    pass


def ledger(record, binding, references, *, attachments=(), proof_bytes=262144):
    """Physical attachments are references, never a second native allowance."""
    refs = tuple(references) + tuple(attachments)
    measured = prior.ledger(record, binding, refs, proof_bytes)
    return measured


def diagnostic(alternatives, phase, ordinal, completed):
    # Fixed-depth scalar tables. In particular, no ledger is embedded recursively.
    data = dict(version=VERSION, phase=phase, ordinal=ordinal,
                completed_events=completed, alternatives={})
    for name, measured in alternatives.items():
        parts = measured["contributions"]
        data["alternatives"][name] = dict(
            parts=dict(record=parts["record"], session=parts["session"], common=parts.get("common", 0),
                native=sum(parts["native"].values()), prefix_steps=parts["prefix_steps"],
                metadata_references=sum(n for k, p, n in parts["references"] if k == "metadata"),
                source_references=sum(n for k, p, n in parts["references"] if k == "sources"),
                report=parts["report"], verification=parts["verification"]),
            totals=dict(measured["totals"]), limits=dict(b.LIMITS),
            violations=list(measured["violations"]))
    if len(b.canonical(data)) > ERROR_LIMIT:
        raise BudgetError("BUDGET_DIAGNOSTIC_LIMIT")
    return data


def read_plan(manifest):
    files = {}
    planned = 0
    for event in manifest.events:
        for payload in (event.pcm, event.rgb):
            if payload is None:
                continue
            identity = (payload.sha256, payload.byte_count)
            if payload.path in files and files[payload.path] != identity:
                raise BudgetError("INPUT_STOCK_BINDING_INVALID")
            files[payload.path] = identity
            planned += payload.byte_count
    return dict(input_stock_bytes=sum(n for h, n in files.values()),
                planned_read_bytes=planned)

