"""Private UHD session admission; no weakening of historical attestations."""
import json
from pathlib import Path
from tools import _s2oe_uhd_profile as profile

CHECK="reports/s2oe/decoder-uhd-sequence-20260911-01"
ANCHORS={"binding.json":"032b72a070caf5799bfa74425e116e51219ea22432d818bcf5ca6f1fa072fb90",
    "verification.json":"1f615f9e4e8531d133137a8fcb75496e40e5579dc6b938c52e91a9dd1e330126"}


def resources():
    return dict(profile.worker.resource_profile(),process_commit_bytes=1073741824,
        job_commit_bytes=1073741824)


def validate(manifest,common):
    profile.worker.require(common["decoder_resource_profile"]==resources(),"UHD_PROFILE_INVALID")
    return profile.validate(profile.canonical(common["decoder_profile"]),manifest.source,manifest.run_id)


def check_anchors(references):
    for name,digest in ANCHORS.items():
        path=profile.ROOT/CHECK/name
        raw=path.read_bytes()
        profile.worker.require(profile.sha(raw)==digest,"UHD_ATTESTATION_INVALID")
        profile.worker.require(["metadata",path.relative_to(profile.ROOT).as_posix(),len(raw),digest]
            in references,"UHD_ATTESTATION_MISSING")
    binding=json.loads((profile.ROOT/CHECK/"binding.json").read_text())
    proof=json.loads((profile.ROOT/CHECK/"verification.json").read_text())
    profile.worker.require(proof["status"]=="EVIDENCE_VALID"
        and proof["decoder_status"]=="DECODER_SEQUENCE_COMPLETE","UHD_NOT_READY")
    profile.worker.require(binding["profile"]["code"]==profile.code(),"UHD_SOURCE_CHANGED")


def open_decoder(manifest,common):
    validate(manifest,common)
    return profile.open_decoder(manifest.source,profile.canonical(common["decoder_profile"]),manifest.run_id)


def verify_resources(manifest,common,resource):
    digest=validate(manifest,common)
    profile.worker.require(resource["private_profile"]==profile.VERSION
        and resource["private_profile_digest"]==digest and resource["private_run_id"]==manifest.run_id
        and resource["process_commit_limit"]==1073741824
        and resource["job_commit_limit"]==1073741824,"UHD_RESOURCE_INVALID")
