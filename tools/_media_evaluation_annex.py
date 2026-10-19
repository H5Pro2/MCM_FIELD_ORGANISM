"""Administrative evaluation publication, no media or state reconstruction."""
from reports import run_selected_media_restart_once as entry
from tools import _media_restart_evidence as e
from tools import _media_checkpoint_budget_profile as profile

VERSION = "media.post-checkpoint-evaluation.v1"


def plan():
    return dict(version=e.publication.VERSION, scope="POSTCHECKPOINT_EVALUATION_V1",
        budget_profile_digest=profile.digest(), positions=[dict(id=k, category=c, count=n, lower=0,
            upper=128 if c == "native" else (61440 if k == "evaluation.json" else 8192))
            for k, (c, n) in e.publication.evaluation_layout().items()])


def shape(proof):
    entry.w.require(proof.get("status") == "RECORDING_COMPLETE" and proof.get("evaluation_allowed") is True,
                    "ANNEX_EVALUATION_BLOCKED")
    rows = proof.get("rows")
    entry.w.require(type(rows) is list and len(rows) == 20 and all(
        type(row) is dict and set(row) == {"ordinal", "equal"} and type(row["ordinal"]) is int
        and row["ordinal"] == n and type(row["equal"]) is bool for n, row in enumerate(rows, 1)),
        "ANNEX_ROWS_FORM")
    entry.w.require(all(type(proof.get(k)) is bool for k in
        ("core_equal", "selections_equal", "final_field_equal")), "ANNEX_FLAGS_FORM")


class EvaluationView:
    def __init__(self, store, accounts):
        self.root, self.store, self.accounts = store.root, store, accounts

    def read(self, path):
        role = path.relative_to(self.root).as_posix()
        entry.w.require(role in ("reference/record.json", "restore20/record.json"), "ANNEX_READ_SCOPE")
        return {"accounting": self.accounts[role.split("/")[0]]}

    def publish(self, path, value):
        entry.w.require(path == self.root/"evaluation.json", "ANNEX_WRITE_SCOPE")
        self.store.publish(path, value)


def evaluate_once(store, manifest, proof, accounts):
    shape(proof)
    entry.w.require(not (store.root/"run.claim").exists(), "ANNEX_ALREADY_USED")
    store.publish(store.root/"run.claim", dict(version=VERSION, uses=1))
    # Exact existing evaluator, restricted to the two stored accounting headers.
    return entry.evaluate(EvaluationView(store, accounts), manifest, proof)
