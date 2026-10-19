"""Static NU provenance and separately named synthetic fixtures; no NU production."""
import copy
import struct

from tools import _s2uc_source_binding as science
from tools import _s2uc_run_binding as run_binding
from tools import _s2uc_evaluation as evaluation
from tools._s2uc_resource_contract_v7 import _need, _same_typed


def endpoints(manifest, scope):
    uses = [e["endpoint"] for e in manifest["events"] if "endpoint" in e]
    return {"version": "s2uc.sources.v9", "scope": scope,
            "manifest_digest": manifest["binding_digest"], "endpoint_uses": uses,
            "sources": {e["source_id"]: e for e in uses}}


def source_context():
    rows, plan = science.source.source_rows()
    manifest = science.manifest()
    # JSON normalization preserves exact public artifact types.
    import json
    return json.loads(science.canonical({
        "version": "s2uc.source-context.v9", "scope": "STRUCTURE_ONLY_NO_AUTHORIZATION",
        "source_plan_sha256": science.SOURCE_PLAN_SHA256,
        "source_execution_digest": science.SOURCE_EXECUTION_DIGEST,
        "profiles": plan["profiles"], "rows": [rows[name] for name in science.IDS.values()],
        "manifest": manifest, "adapter": endpoints(manifest, "NU_BOUND_DISABLED"),
        "targets": {f"{s}/{n}": v for (s, n), v in run_binding.TARGETS.items()},
        "expectations": {f"{s}/{n}": v for (s, n), v in evaluation.EXPECTED.items()},
        "candidate_gain_loss_status": "NOT_MEASURED", "real_execution_authorized": False}))


def validate_source_context(value):
    _need(_same_typed(value, source_context()), "V9_SOURCE_CONTEXT_INVALID")
    return copy.deepcopy(value)


def prepare_nu_supplier(value):
    """Only builds a demand supplier. Private preparation is not admission.

    The public real entry never calls this function. No cache or eager payloads.
    """
    bound = validate_source_context(value)["adapter"]["sources"]
    def supply(endpoint):
        source_id = endpoint.get("source_id")
        _need(source_id in bound and _same_typed(endpoint, bound[source_id]), "V9_NU_ENDPOINT_INVALID")
        from tools import _s2nu_private_source_binding as nu
        return nu.pcm_window(nu.WindowSpec(2, list(science.IDS.values()).index(source_id)))
    return supply


def neutral_payload(source_id):
    names = [f"neutral-v9-{i}" for i in range(5)]
    _need(source_id in names, "V9_NEUTRAL_SOURCE_REQUIRED")
    n = names.index(source_id) + 1
    # Five bounded, deterministic, nonzero synthetic waveforms; no NU generator.
    return bytearray().join(struct.pack("<f", ((i * (n * 2 + 1)) % 127 - 63) / 256.0)
                            for i in range(4800))


def neutral_manifest():
    value = copy.deepcopy(science.manifest())
    mapping = {name: f"neutral-v9-{i}" for i, name in enumerate(science.IDS.values())}
    import hashlib
    hashes = {name: hashlib.sha256(neutral_payload(name)).hexdigest() for name in mapping.values()}
    for event in value["events"]:
        if "endpoint" in event:
            endpoint = event["endpoint"]
            endpoint["source_id"] = mapping[endpoint["source_id"]]
            endpoint["pcm_sha256"] = hashes[endpoint["source_id"]]
    bare = {k: v for k, v in value.items() if k not in ("binding_digest", "binding_bytes")}
    value.update(binding_digest=science.digest(bare), binding_bytes=len(science.canonical(bare)))
    science.validate(value)
    return value
