"""Private two-history composition; no change to historical runtime defaults."""
from dataclasses import asdict, dataclass, replace
import json

from tools import _s2oe_media_session as media
from tools import _s2ob_private_caller_verification as old

p, b, r = media.p, media.b, media.r
VERSION = "experience-comparison.v1"
PROFILE = "EXPERIENCE_COMPARISON_24M_V1"
MAIN_GATE = False
LIMITS = dict(total=25165824, metadata=3145728, sources=524288,
              shared=786432, verification=262144)
EXPECTED = dict(formations=30, cues=8, contacts=11424, scans=16,
                audio=22, nj=22, visual=22)


class ComparisonError(ValueError):
    def __init__(self, code, detail=None):
        self.code, self.detail = code, detail
        super().__init__(code)


def need(ok, code, detail=None):
    if not ok:
        raise ComparisonError(code, detail)


def budget(parts):
    """One physical ledger, including temporary publication copies and reserves."""
    need(type(parts) is list, "LEDGER_FORM")
    names = set()
    totals = dict.fromkeys(LIMITS, 0)
    for row in parts:
        need(set(row) == {"path", "kind", "bytes"} and row["path"] not in names
             and row["kind"] in ("native", "metadata", "sources", "verification", "nj", "formations", "generations")
             and type(row["bytes"]) is int and row["bytes"] >= 0, "LEDGER_FORM")
        names.add(row["path"])
        n, k = row["bytes"], row["kind"]
        totals["total"] += n
        if k in totals and k != "total":
            totals[k] += n
        if k in ("sources", "nj", "formations", "generations"):
            totals["shared"] += n
    violations = [k for k in LIMITS if totals[k] > LIMITS[k]]
    result = dict(profile=PROFILE, contributions=parts, totals=totals,
                  limits=dict(LIMITS), violations=violations)
    need(not violations, "JOINT_BUDGET_LIMIT", result)
    return result


@dataclass(frozen=True)
class ArmManifest:
    run_id: str
    events: tuple
    positions: tuple
    manifest_digest: str


def arm_manifest(manifest, arm):
    p.validate(manifest)
    need(arm in ("experienced", "fresh"), "ARM_INVALID")
    positions = tuple(range(1 if arm == "experienced" else 11, 25))
    events = tuple(replace(manifest.events[g-1], ordinal=n)
                   for n, g in enumerate(positions, 1))
    run_id = manifest.run_id + "-" + arm
    b.identifier(run_id)
    root = b.digest(dict(version=VERSION, parent=manifest.manifest_digest,
                         arm=arm, positions=positions, events=[asdict(e) for e in events]))
    return ArmManifest(run_id, events, positions, root)


def local_input(item, spec, position):
    e = item.event
    need((e.ordinal, e.event_id, e.event_type) == (position, spec.event_id, spec.kind), "INPUT_POSITION_INVALID")
    # A fresh field starts at zero. Its first interval explicitly includes the
    # empty lead-in; perceptual contact times are NOT shifted or fabricated.
    field = replace(e.field_payload, start_tick=0) if spec.ordinal == 1 else e.field_payload
    event = r.ng.stream.build_perception_stream_event(event_id=e.event_id, ordinal=spec.ordinal,
        event_type=e.event_type, source_digest=e.source_digest, perception_digest=e.perception_digest,
        field_projection_digest=e.field_projection_digest, operation_projection_digest=e.operation_projection_digest,
        field_payload=field, operation_payload=e.operation_payload)
    return b.Input(event, item.nj_json)


class Arm(b.CallerRuntime):
    def __init__(self, manifest):
        self.manifest, self.config, self.run_id = manifest, r.nn.profile.build_config(), manifest.run_id
        self.inputs, self.packed, self.source = [], [], []
        self.binding = r.ng.build_binding(self.config, "ALL_BANDS_24")
        fs, ms = r.null_field(self.config), r.memory.initial_s2jv_composite_state(self.config)
        self.fb = r.ng.ObservedBranch(r.ng.field.build_s2lo_field_adapter(b.CLOCK), fs)
        self.mb, self.scans = r.MemoryBranch(self.config, self.run_id, ms), {}
        processor = r.ng.stream.RoleFreePerceptionStreamProcessor(field_adapter=self.fb, memory_adapter=self.mb,
            auditory_scan=r.ng.AudioAdapter(self.binding,self.config,False,self.scans),
            auditory_baseline=r.ng.AudioAdapter(self.binding,self.config,True,self.scans),
            visual_scan=r.ng.VisualAdapter(self.config,False,self.scans),
            visual_baseline=r.ng.VisualAdapter(self.config,True,self.scans))
        rc = r.ng.runtime.build_minimal_runtime_config(runtime_id=self.run_id,max_event_count=len(manifest.events),
            source_binding_digest=manifest.manifest_digest,component_binding_digest=self.binding.binding_digest)
        initial = r.ng.stream.initial_perception_stream_state(stream_id=self.run_id,field_state=fs,
            field_state_digest=fs.state_digest,memory_state=ms,memory_state_digest=ms.state_digest)
        self.subject = r.ng.runtime.MinimalMCMRuntime336(config=rc,processor=processor,initial_state=initial)
        self.rc, self.rows, self.states = asdict(rc), [], b.StateEvidencePool()
        self.states[ms.state_digest] = asdict(ms)
        self.initial = dict(snapshot=asdict(self.subject.snapshot()),field=r.ng.field_record(fs),memory=ms.state_digest)
        self.births = [None]*24
        self.chain = b.digest(dict(initial=ms.state_digest,config=self.config.config_digest))
        self.failed, self.phase, self.failure, self.closed = False, "INITIAL", None, False


def run_materialized(manifest, supplier, *, mode="NEUTRAL"):
    """Single sequential supplier, private native arms; no source regeneration."""
    p.validate(manifest)
    need(mode in ("NEUTRAL","MEDIA") and (mode!="MEDIA" or type(supplier) is media.Materializer),"SUPPLIER_MODE_INVALID")
    arms = {"experienced": Arm(arm_manifest(manifest,"experienced"))}
    phase, position = "INITIAL", 0
    try:
        for event in manifest.events:
            position, phase = event.ordinal, "MATERIALIZATION"
            item = supplier.next(event)
            if position == 11:
                arms["fresh"] = Arm(arm_manifest(manifest,"fresh"))
            phase = "PROCESSING"
            for name, arm in arms.items():
                spec = arm.manifest.events[len(arm.rows)]
                adapted = local_input(item,spec,position)
                arm.process(adapted)
                need(not arm.failed,"NATIVE_BRANCH_FAILURE",arm.failure)
            del item
        cores = {k:arm.record() for k,arm in arms.items()}
        materialization = None if mode=="NEUTRAL" else dict(counts=supplier.counts,receipts=supplier.receipts,
            decoder=dict(supplier.decoder.counters),resources=dict(supplier.decoder.resources))
        return b.sealed(dict(version=VERSION,profile=PROFILE,status="RECORDING_COMPLETE",mode=mode,
            manifest=asdict(manifest),arms=cores,materialization=materialization,failure=None,main_gate=False),"record_digest")
    except Exception as exc:
        final = {k:arm.close() for k,arm in arms.items()}
        return b.sealed(dict(version=VERSION,profile=PROFILE,status="NOT_EVALUABLE",
            manifest=asdict(manifest),arms={k:dict(rows=a.rows,states=a.states,inputs=a.packed,
                source_receipts=a.source,final=final[k]) for k,a in arms.items()},
            failure=dict(phase=phase,position=position,code=getattr(exc,"code",type(exc).__name__),
                detail=getattr(exc,"detail",None),progress={k:len(a.rows) for k,a in arms.items()}),
            main_gate=False),"record_digest")
    finally:
        for arm in arms.values():
            arm.close()


def provenance(core, manifest):
    """Track all observed updates, not only the generation's birth label."""
    chains = [None]*24
    snapshots = []
    for row, spec in zip(core["rows"],manifest.events,strict=True):
        gen = row["generations"]
        if gen is not None:
            for i, action in enumerate(gen["actions"]):
                link = dict(event=spec.ordinal,window=spec.window_number,pass_number=spec.pass_number,
                            transaction=gen["transaction"])
                if action in ("FREE","CLEARED"):
                    chains[i] = None
                elif action in ("CREATED","REPLACED"):
                    chains[i] = [link]
                elif action == "MATCHED":
                    need(chains[i] is not None,"PROVENANCE_CHAIN_MISSING")
                    chains[i] = chains[i] + [link]
                else:
                    need(action == "UNCHANGED","PROVENANCE_ACTION_INVALID")
        snapshots.append(json.loads(b.canonical(chains)))
    return snapshots


def origin_class(chain, window):
    if not chain:
        return "UNDETERMINED"
    values = {x["window"] for x in chain}
    return "TARGET_ONLY" if values == {window} else "MIXED" if window in values else "OTHER"


def comparison_flags(experienced, fresh):
    return dict(gain=experienced["target_admission"] and not fresh["target_admission"],
                loss=fresh["target_admission"] and not experienced["target_admission"],
                experienced_non_target=experienced["non_target_admission"],
                fresh_non_target=fresh["non_target_admission"])


def evaluate(record, proof):
    need(proof.get("evaluation_allowed") is True and proof.get("record_digest") == record["record_digest"],
         "EVALUATION_NOT_ALLOWED")
    manifest = p.decode(record["manifest"])
    result = []
    for global_n in (13,14,21,22):
        row = dict(position=global_n,window=manifest.events[global_n-1].window_number,arms={})
        for name, offset in (("experienced",0),("fresh",10)):
            core = record["arms"][name]
            n = global_n-offset
            step = core["rows"][n-1]["step"]
            scan = next(x["value"] for x in core["scans"] if x["ordinal"]==n and x["role"]=="PRIMARY")
            evidence = scan.get("evidence",scan)
            state = old.fv.old.decode_state(b.state_wire.decode(core["states"][core["rows"][n-1]["memory"]]),r.nn.profile.build_config())
            histories = provenance(core,arm_manifest(manifest,name))[n-1]
            candidates = []
            offsets = (0,9,12 if manifest.events[global_n-1].kind==b.A else 20)
            for bank,offset in zip(evidence["bank_scans"],offsets,strict=True):
                for slot_index,candidate in enumerate(bank["records"],offset):
                    if not candidate["observed_match"]:
                        continue
                    links = histories[slot_index]
                    candidates.append(dict(scan=candidate,history=links,origin=origin_class(links,row["window"]),
                        generation=core["rows"][n-1]["current_births"][slot_index]))
            h = step["hypothesis"]
            selected = [] if h is None else [x for x in candidates if x["scan"]["slot_digest"] in h["provenance_slot_digests"]]
            target = bool(selected) and all(x["origin"]=="TARGET_ONLY" for x in selected)
            row["arms"][name] = dict(decision=step["context_status"],hypothesis=h,candidates=candidates,
                target_admission=target,non_target_admission=h is not None and not target)
        row["same_public_result"] = b.canonical(row["arms"]["experienced"]["hypothesis"]) == b.canonical(row["arms"]["fresh"]["hypothesis"]) and row["arms"]["experienced"]["decision"] == row["arms"]["fresh"]["decision"]
        row.update(comparison_flags(row["arms"]["experienced"],row["arms"]["fresh"]))
        result.append(row)
    return dict(status="DIAGNOSTIC_COMPARISON",rows=result,
        boundary="Origin is experimental provenance, not semantic identity; mixed or missing origin is not a correct-target claim.")
