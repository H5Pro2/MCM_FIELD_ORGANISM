"""Administrative OC media envelope only: no media, receptor, or runtime calls."""
from dataclasses import asdict
import json

from tools import _s2oc_shared_binding as s
from tools import _s2oc_shared_verification as v
from tools import _s2oe_media_binding as policy

b = s.b
BASE = b.ROOT / "reports/s2oc" / s.QUAL_ID
# Prospective local allocations; every file remains charged as source evidence.
SOURCE_PARTS = {
    "tools/_s2oe_media_binding.py": 8000,
    "tools/_s2oe_media_decoder.py": 8000,
    "tools/_s2oe_media_session.py": 10000,
    "tools/_s2oe_media_verification.py": 6000,
    "tests/test_s2oe_media.py": 8000,
    "reports/qualify_direct_media_once.py": 5000,
    "reports/prepare_direct_media_budget.py": 6000,
    "reports/s2oe/media-oc-qualification-20260911-02/inventory.json": 4096,
}
META_PARTS = {
    "@media-source-and-selection-binding": 4096,
    "@new-qualification-and-report": 8704,
    "@selection-receipts": 24 * 512,
    "@decoder-counter-and-closure": 2048,
    "@evaluation": 3000,
    "@dispatch": 768,
    "@final-balance": 1536,
    "@common-reference": 512,
}


def prepare():
    from tools import _s2oe_media_session as media
    inv = s.read_json(BASE / "inventory.json")
    events = []
    for n in range(1, 25):
        kind = b.A if n in (13, 21) else b.V if n in (14, 22) else b.AV
        # These stand-ins size the old core grammar, not a media admission.
        pcm = None if kind == b.V else b.Payload(
            f"media-audio-{n:02}", "unread/media-window.pcm", "0"*64, 19200)
        rgb = None if kind == b.A else b.Payload(
            f"media-visual-{n:02}", "unread/media-frame.rgb", "0"*64, 6220800)
        events.append(b.Event(f"media-event-{n:02}", n, kind,
            **b.expected_times(n, kind), pcm=pcm, rgb=rgb))
    manifest = b.build_manifest("media-envelope-preparation", tuple(events), b.digest(inv["ob"]))
    refs = [s.file_reference("sources", BASE / "inventory.json")]
    refs += [s.file_reference("sources", b.ROOT / p) for p in s.OWN]
    refs += [s.file_reference("metadata", BASE / n) for n in s.QUAL_CAPS]
    qref = next(r for r in refs if r[1].endswith("/package.json"))
    # Read current code bindings, but do not re-run an historical qualification.
    changed = [p for p, (h, size) in inv["connector"].items()
        if (b.ROOT / p).stat().st_size != size or s.sha((b.ROOT / p).read_bytes()) != h]
    if changed:
        raise RuntimeError("CURRENT_CONNECTOR_CHANGED: " + repr(changed))
    base_sources = sum(r[2] for r in refs if r[0] == "sources")
    common = s.build_common(manifest, inv, refs, qref)
    current = media.inventory()
    source_parts = {name: value[1] for name,value in current.items()}
    source_parts[f"reports/s2oe/{media.QUAL_ID}/inventory.json"] = len(b.canonical(current))
    attachments = tuple(("sources", p, n) for p, n in source_parts.items()) + tuple(
        ("metadata", p, n) for p, n in META_PARTS.items())
    positions = []
    for n in range(25):
        alternatives = {}
        for name, pair in zip(("success", "failure"), v.synthetic_forms(common, n), strict=True):
            ledger = policy.ledger(*pair, common, attachments=attachments)
            alternatives[name] = ledger
        positions.append(dict(completed=n, **alternatives))
    return dict(
        purpose="Prospective complete per-file allocations, not actual future source sizes or qualification",
        base_source_bytes=base_sources, source_parts=source_parts, metadata_parts=META_PARTS,
        counts=b.validate_manifest(manifest), limits=policy.SESSION_LIMITS,
        old_common_bytes=len(b.canonical(common)), positions=positions,
        maxima={name: {k: max(p[name]["totals"][k] for p in positions) for k in b.LIMITS}
            for name in ("success", "failure")},
        test_calls=0, media_reads=0, gates_opened=False)


if __name__ == "__main__":
    print(json.dumps(prepare(), ensure_ascii=True, sort_keys=True))
