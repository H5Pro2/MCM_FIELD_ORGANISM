"""Fixed full-file mode profile and finite envelope, no new runtime mechanism."""
from dataclasses import asdict
import json
from tools import _s2oe_uhd_profile as old

MODE = "s2oe.full-file-sampled.v1"
VERSION = "s2oe.full-file-uhd-profile.v1"
QUAL_ID = "full-file-connection-qualification-20260912-02"
WORK = dict(video_frames=1024, audio_frames=2048, packets=4096)
CONFIG = dict(old.CONFIG, selection_step=[7,5], selection_count=20, passes=1, decoder_work=WORK)
OWN = old.OWN + ("tools/_s2oe_full_file.py", "tools/_s2oe_media_binding.py")


def code():
    return {p:old.sha((old.ROOT/p).read_bytes()) for p in OWN}


def bind(source, run_id):
    value = dict(version=VERSION, run_id=run_id, source=asdict(source), config=CONFIG, code=code())
    value["profile_digest"] = old.sha(old.canonical(value))
    return json.loads(old.canonical(value))


def resources():
    return dict(old.worker.resource_profile(), process_commit_bytes=1073741824, job_commit_bytes=1073741824)


def validate(manifest, common):
    old.worker.require(manifest.schema == MODE and common["decoder_resource_profile"] == resources()
        and common["decoder_profile"] == bind(manifest.source,manifest.run_id), "FULL_FILE_PROFILE_INVALID")
    return common["decoder_profile"]["profile_digest"]


def open_decoder(manifest, common):
    pin = validate(manifest, common)
    decoder = old.worker.WorkerDecoder(manifest.source, diagnostic_arm="COMMIT_1024", mode=MODE)
    decoder.resources.update(private_profile=VERSION, private_profile_digest=pin, private_run_id=manifest.run_id)
    return decoder


def verify_resources(manifest, common, resource):
    pin = validate(manifest, common)
    old.worker.require(resource["private_profile"] == VERSION
        and resource["private_profile_digest"] == pin and resource["private_run_id"] == manifest.run_id
        and resource["process_commit_limit"] == resource["job_commit_limit"] == 1073741824,
        "FULL_FILE_RESOURCE_INVALID")


def envelope(common, source_reserve=0, metadata_reserve=0):
    """All prefixes, alternatives, native maxima and referenced physical contents."""
    from tools import _s2oe_media_binding as p
    p.need(common["manifest"]["schema"] == MODE, "FULL_FILE_BUDGET_MODE_INVALID")
    from tools import _s2oc_shared_verification as shapes
    attachments = (("sources", "@full-file-sources", source_reserve),
                   ("metadata", "@full-file-closure", 8192 + metadata_reserve))
    positions = []
    for n in range(21):
        alternatives = {}
        for ending, (record, session) in zip(("success", "failure"), shapes.synthetic_forms(common,n), strict=True):
            # Real administrative grammar, maximum native bodies. No memory simulation.
            materialized = n if ending == "success" else min(20,n+1)
            record.pop("record_digest")
            record["mode"] = "MEDIA"
            record["media"] = dict(receipts=["x"*510 for _ in range(materialized)],
                                   decoder="x"*1022, resources="x"*1022)
            record = p.b.sealed(record,"record_digest")
            session = p.b.sealed({**{k:v for k,v in session.items() if k != "session_digest"},
                                   "record_digest":record["record_digest"]}, "session_digest")
            alternatives[ending] = p.ledger(record,session,common,attachments=attachments)
        positions.append(dict(completed=n, **alternatives))
    return dict(version=VERSION, limits=p.SESSION_LIMITS, positions=positions,
        violations=[f"{row['completed']}:{kind}:{v}" for row in positions
            for kind in ("success","failure") for v in row[kind]["violations"]])


def check_envelope(common):
    value = envelope(common)
    old.worker.require(not value["violations"], "FULL_FILE_PREFLIGHT_LIMIT")
    return value
