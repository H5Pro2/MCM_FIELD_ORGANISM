"""Versioned finite checkpoint boundary; historical entry points remain unchanged."""
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
from threading import Lock

from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot, restore_shared_mcm_field
from tools import _s2ob_private_caller_binding as b
from tools import _s2ob_private_caller_verification as verify
from tools import _memory_checkpoint_ledger as budgets

VERSION = "mcm.system-checkpoint.v1"
FIELD_CLASS = "FIELD_CHECKPOINT.v1"
FIELD_CAP = 524288
TOTAL_CAP = 4194304
MAIN_GATE = False
r = b.r


class CheckpointError(ValueError):
    def __init__(self, code, details=None):
        self.code, self.details = code, details
        super().__init__(code)


def require(ok, code, details=None):
    if not ok:
        raise CheckpointError(code, details)


def copy_json(value):
    return json.loads(b.canonical(value))


def seal(value):
    return b.sealed(value, "checkpoint_digest")


def checked_size(value, limit, category):
    size = len(b.canonical(value))
    require(size <= limit, "CHECKPOINT_SIZE", dict(category=category, bytes=size, limit=limit))
    return size


def common_values(manifest):
    config=r.nn.profile.build_config()
    binding=r.ng.build_binding(config,"ALL_BANDS_24")
    rc=r.ng.runtime.build_minimal_runtime_config(runtime_id=manifest.run_id,
        max_event_count=len(manifest.events),source_binding_digest=manifest.manifest_digest,
        component_binding_digest=binding.binding_digest)
    return copy_json(dict(manifest=asdict(manifest),binding=asdict(binding),runtime_config=asdict(rc)))


def references(value, common, *, resolve=False):
    if isinstance(value,list):return [references(x,common,resolve=resolve) for x in value]
    if not isinstance(value,dict):return value
    if resolve and "$checkpoint_common" in value:
        key=value["$checkpoint_common"]
        require(set(value)=={"$checkpoint_common","sha256"} and key in common
                and value["sha256"]==b.digest(common[key]),"CHECKPOINT_REFERENCE")
        return copy_json(common[key])
    if not resolve:
        for key,item in common.items():
            if value==item:return {"$checkpoint_common":key,"sha256":b.digest(item)}
    return {k:references(v,common,resolve=resolve) for k,v in value.items()}


def load_common(directory):
    try:
        raw=(Path(directory)/"common.json").read_bytes()
        require(len(raw)<=16384,"CHECKPOINT_REFERENCE")
        value=json.loads(raw)
        require(set(value)=={"values","sha256"} and b.digest(value["values"])==value["sha256"],
                "CHECKPOINT_REFERENCE")
        return value["values"]
    except OSError as exc:raise CheckpointError("CHECKPOINT_REFERENCE") from exc


def artifact_ledger(directory, *, extra=()):
    common=load_common(directory)
    result=budgets.ledger(directory,lambda raw:references(json.loads(raw),common,resolve=True),extra=extra)
    prereg=Path(directory)/"preregistration.json"
    if prereg.exists():
        binding=json.loads(prereg.read_bytes())
        for name in binding.get("charged_sources",[]):
            raw=(b.ROOT/name).read_bytes();expected=binding["inventory"]["files"][name]
            require(len(raw)==expected["bytes"] and hashlib.sha256(raw).hexdigest()==expected["sha256"],"CHECKPOINT_CODE_CHANGED")
            result["files"].append(dict(path=name,bytes=len(raw),classes={"sources":len(raw)},reference=True))
            for key in ("sources","shared","total"):result["totals"][key]+=len(raw)
        result["violations"]=[k for k,limit in budgets.LIMITS.items() if result["totals"][k]>limit]
    return result


def validate_field_form(field):
    positions=[(0,i) for i in range(48)]+[(1+i//36,i%36) for i in range(288)]
    ids=[f"organism.mcm_field.auditory.n{i}" for i in range(48)]
    ids += [f"organism.mcm_field.visual.n{i}" for i in range(288)]
    require(field.get("schema_version")==1 and set(field)=={"schema_version","layer","docks","last_distribution"},"CHECKPOINT_FIELD_FORM")
    layer=field["layer"]; neurons=layer["neurons"]
    require(layer["layer_id"]=="organism.mcm_layer" and layer["periodic_axes"]==[]
        and layer["sample_offsets"]==[[-1,0],[0,-1],[0,1],[1,0]]
        and len(neurons)==336 and set(layer["receptor_dock_ids"])==set(ids),"CHECKPOINT_FIELD_FORM")
    expected=dict(zip(ids,positions)); at={p:i for i,p in expected.items()}
    require({n["neuron_id"] for n in neurons}==set(ids),"CHECKPOINT_FIELD_FORM")
    for n in neurons:
        pos=expected[n["neuron_id"]]
        require(tuple(n["position"])==pos and n["field_id"]=="organism.mcm_field"
            and n["geometry_id"]=="organism.shared.v1" and n["modality_id"]=="organism"
            and type(n["perception"]["tick"]) is int and 1<=n["perception"]["tick"]<=28,"CHECKPOINT_FIELD_FORM")
        expected_samples={"sample."+at[(pos[0]+dr,pos[1]+dc)] for dr,dc in
            ((-1,0),(0,-1),(0,1),(1,0)) if (pos[0]+dr,pos[1]+dc) in at}
        require({s["sample_id"] for s in n["perception"]["local_samples"]}==expected_samples
            and all(s["source_field_id"]=="organism.mcm_field" for s in n["perception"]["local_samples"]),"CHECKPOINT_FIELD_FORM")
    require(len(field["docks"])==2 and field["last_distribution"]["contacts"]==[],"CHECKPOINT_FIELD_FORM")
    time=field["last_distribution"]["field_time"]
    require(time["clock_id"]==b.CLOCK and 0<=time["window_start_tick"]<time["window_end_tick"]<10000000000,"CHECKPOINT_FIELD_FORM")
    for dock in field["docks"]:
        require(len(dock["receptor_geometry_id"])<=80 and dock["receptor_geometry_id"].isascii()
            and all(len(p[0])<=80 and p[0].isascii() for p in dock["pairs"]),"CHECKPOINT_FIELD_FORM")
    checked_size(field,426580,FIELD_CLASS)


def publish_new(path, value):
    """No replacement: a complete temporary file is linked to an unused name."""
    path = Path(path)
    temporary = path.with_name(path.name + ".pending")
    common=load_common(path.parent)
    raw = b.canonical(references(value,common))
    require(len(raw) <= TOTAL_CAP, "CHECKPOINT_SIZE")
    require(not path.exists() and not temporary.exists(), "CHECKPOINT_EXISTS")
    ledger=artifact_ledger(path.parent,extra=((path.name,raw,value),(temporary.name,raw,value)))
    require(not ledger["violations"],"CHECKPOINT_BUDGET",ledger)
    try:
        with temporary.open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
        temporary.unlink()
    except OSError as exc:
        # Preserve an incomplete/complete pending file for diagnosis, never retry.
        raise CheckpointError("CHECKPOINT_WRITE_FAILED", dict(
            phase="PUBLISH", target=str(path), temporary=str(temporary),
            planned_bytes=len(raw), temporary_bytes=temporary.stat().st_size
            if temporary.exists() else 0)) from exc


def read_checkpoint(path):
    path = Path(path)
    try:
        with path.open("rb") as stream:
            raw = stream.read(TOTAL_CAP + 1)
        require(len(raw) <= TOTAL_CAP, "CHECKPOINT_SIZE")
        value = json.loads(raw)
        require(b.canonical(value) == raw, "CHECKPOINT_ENCODING")
        return references(value,load_common(path.parent),resolve=True)
    except (OSError, ValueError) as exc:
        if isinstance(exc, CheckpointError):
            raise
        raise CheckpointError("CHECKPOINT_READ_FAILED") from exc


def prefix_record(runtime):
    """Completed-prefix projection, never published as a completed full session."""
    final = asdict(runtime.subject.snapshot())
    final = b.sealed({**{k: v for k, v in final.items() if k != "snapshot_digest"},
                      "status": "CLOSED"}, "snapshot_digest")
    return b.sealed(dict(schema=b.SCHEMA, status="RECORDING_COMPLETE", run_id=runtime.run_id,
        config_digest=runtime.config.config_digest, runtime_config=runtime.rc,
        binding=asdict(runtime.binding), initial=runtime.initial, final=final,
        inputs=runtime.packed, source_receipts=runtime.source, rows=runtime.rows,
        states=runtime.states, scans=[dict(ordinal=n, role=role, value=asdict(scan))
            for (n, role), scan in sorted(runtime.scans.items())], failure=None,
        main_gate=False), "record_digest")


def export(runtime, manifest, code_digest, accounting):
    require(not runtime.closed and not runtime.failed, "CHECKPOINT_LIFECYCLE")
    n = len(runtime.rows)
    require(0 < n < len(manifest.events), "CHECKPOINT_POSITION")
    require(runtime.subject.snapshot().status == "OPEN" and runtime.phase == "EVIDENCE",
            "CHECKPOINT_BOUNDARY")
    state = runtime.subject._state
    require(n == state.processed_event_count and runtime.mb.state is state.memory_state
            and runtime.fb.state is state.field_state, "CHECKPOINT_BRANCH_BINDING")
    field = runtime.fb.state.field.snapshot().canonical_payload()
    validate_field_form(field)
    checked_size(field, FIELD_CAP, FIELD_CLASS)
    payload = dict(schema=VERSION, status="SUSPENDED_PREFIX", field_class=FIELD_CLASS,
        manifest=asdict(manifest), code_digest=code_digest, process_id=os.getpid(),
        stream={**state.payload_without_digest(), "state_digest": state.state_digest},
        field=field, field_wrapper=r.ng.field_record(runtime.fb.state),
        prefix=prefix_record(runtime), births=runtime.births, chain=runtime.chain,
        accounting=accounting, main_gate=False)
    result = copy_json(seal(payload))
    checked_size(result, TOTAL_CAP, "checkpoint_file")
    return result


def validate(value, manifest, code_digest):
    """Validate all components before a live instance is constructed."""
    try:
        require(type(value) is dict and set(value) == {"schema", "status", "field_class",
            "manifest", "code_digest", "process_id", "stream", "field", "field_wrapper",
            "prefix", "births", "chain", "accounting", "main_gate", "checkpoint_digest"},
            "CHECKPOINT_FORM")
        require(value == seal({k: v for k, v in value.items() if k != "checkpoint_digest"}),
                "CHECKPOINT_DIGEST")
        require(value["schema"] == VERSION and value["field_class"] == FIELD_CLASS
                and value["status"] == "SUSPENDED_PREFIX" and value["main_gate"] is False,
                "CHECKPOINT_PROFILE")
        b.validate_manifest(manifest)
        require(value["manifest"] == copy_json(asdict(manifest))
                and value["code_digest"] == code_digest == manifest.code_digest,
                "CHECKPOINT_BINDING")
        checked_size(value, TOTAL_CAP, "checkpoint_file")
        checked_size(value["field"], FIELD_CAP, FIELD_CLASS)
        validate_field_form(value["field"])
        config = r.nn.profile.build_config()
        prefix = value["prefix"]
        n = len(prefix["rows"])
        require(0 < n < len(manifest.events) and n == len(prefix["inputs"])
                == len(prefix["source_receipts"]), "CHECKPOINT_POSITION")
        for spec, packed, source in zip(manifest.events[:n], prefix["inputs"],
                                        prefix["source_receipts"], strict=True):
            require((packed["event"]["ordinal"], packed["event"]["event_id"],
                     packed["event"]["event_type"]) == (spec.ordinal, spec.event_id, spec.kind),
                    "CHECKPOINT_EVENT_BINDING")
            require(source["rgb_digest"] == (spec.rgb.sha256 if spec.rgb else None)
                    and (source["nj"]["pcm_digest"] if source["nj"] else None)
                    == (spec.pcm.sha256 if spec.pcm else None), "CHECKPOINT_SOURCE_BINDING")
        proof = verify.verify_core(prefix, config, manifest)
        require(proof["evaluation_allowed"] and prefix["run_id"] == manifest.run_id,
                "CHECKPOINT_PREFIX_INVALID")
        row = prefix["rows"][-1]
        memory = verify.fv.old.decode_state(b.state_wire.decode(prefix["states"][row["memory"]]), config)
        snapshot = SharedMCMFieldSnapshot.from_json(b.canonical(value["field"]))
        field = r.ng.field._field_state(restore_shared_mcm_field(snapshot),
            value["field_wrapper"]["last_end_tick"], value["field_wrapper"]["step_count"])
        require(r.ng.field_record(field) == value["field_wrapper"] == row["field"],
                "CHECKPOINT_FIELD_BINDING")
        stream = r.ng.stream.PerceptionStreamStateV1(**value["stream"],
            memory_state=memory, field_state=field)
        r.ng.stream._validate_stream_state(stream)
        require(stream.status == "OPEN" and stream.stream_id == manifest.run_id
                and stream.next_ordinal == n + 1 and stream.processed_event_count == n
                and stream.field_state_digest == field.state_digest
                and stream.memory_state_digest == memory.state_digest
                and stream.last_event_digest == prefix["inputs"][-1]["event"]["event_digest"],
                "CHECKPOINT_STREAM_BINDING")
        for key in ("field_attempt_count", "memory_formation_attempt_count", "scan_attempt_count"):
            require(getattr(stream, key) == row["post"][key], "CHECKPOINT_COUNTER_BINDING")
        require(value["births"] == row["current_births"] and value["chain"] == row["chain_digest"],
                "CHECKPOINT_GENERATION_BINDING")
        validate_accounting(value["accounting"],manifest,n)
        return stream, config
    except CheckpointError:
        raise
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        raise CheckpointError("CHECKPOINT_COMPONENT_INVALID") from exc


class ResumedRuntimeV1(r.ng.runtime.MinimalMCMRuntime336):
    """New constructor, not a relaxation of the historical fresh constructor."""
    def __init__(self, config, processor, validated_state):
        self._config = r.ng.runtime._validate_config(config)
        self._state = r.ng.stream._validate_stream_state(validated_state)
        require(type(processor) is r.ng.stream.RoleFreePerceptionStreamProcessor
                and self._state.status == "OPEN"
                and 0 < self._state.processed_event_count < config.max_event_count,
                "RESTORE_RUNTIME_BINDING")
        self._processor, self._status, self._lock = processor, "OPEN", Lock()


class RestoredCallerV1(b.CallerRuntime):
    def __init__(self, value, manifest, code_digest):
        state, config = validate(value, manifest, code_digest)
        self.expected = b.validate_manifest(manifest)
        self.manifest, self.config, self.run_id = manifest, config, manifest.run_id
        prefix = copy_json(value["prefix"])
        self.packed, self.source, self.rows = prefix["inputs"], prefix["source_receipts"], prefix["rows"]
        self.inputs = [b.Input(verify.ngv.decode_input(p, config), b.canonical(s).decode("ascii"))
                       for p, s in zip(self.packed, self.source, strict=True)]
        self.binding = r.ng.build_binding(config, "ALL_BANDS_24")
        self.fb = r.ng.ObservedBranch(r.ng.field.build_s2lo_field_adapter(b.CLOCK), state.field_state)
        self.mb = r.MemoryBranch(config, self.run_id, state.memory_state)
        self.scans = {}
        for item in prefix["scans"]:
            kind = manifest.events[item["ordinal"] - 1].kind
            decoder = verify.fv.old.decode_arm if kind == b.A else verify.ngv.decode_visual
            self.scans[item["ordinal"], item["role"]] = decoder(item["value"])
        processor = r.ng.stream.RoleFreePerceptionStreamProcessor(field_adapter=self.fb, memory_adapter=self.mb,
            auditory_scan=r.ng.AudioAdapter(self.binding, config, False, self.scans),
            auditory_baseline=r.ng.AudioAdapter(self.binding, config, True, self.scans),
            visual_scan=r.ng.VisualAdapter(config, False, self.scans),
            visual_baseline=r.ng.VisualAdapter(config, True, self.scans))
        rc = r.ng.runtime.build_minimal_runtime_config(runtime_id=self.run_id,
            max_event_count=len(manifest.events), source_binding_digest=manifest.manifest_digest,
            component_binding_digest=self.binding.binding_digest)
        self.subject = ResumedRuntimeV1(rc, processor, state)
        self.rc, self.initial = asdict(rc), prefix["initial"]
        self.states = b.StateEvidencePool()
        for key, encoded in prefix["states"].items():
            self.states[key] = b.state_wire.decode(encoded)
        self.births, self.chain = list(value["births"]), value["chain"]
        self.failed, self.closed, self.failure, self.phase = False, False, None, "EVIDENCE"


class NeutralCheckpointSessionV1:
    """Qualification-only boundary. No real caller admission is provided here."""
    def __init__(self, manifest, code_digest, *, checkpoint=None, mode="NEUTRAL_ENDPOINTS"):
        require(MAIN_GATE and code_digest == manifest.code_digest, "CHECKPOINT_GATE_CLOSED")
        self._manifest, self._code, self._lock = manifest, code_digest, Lock()
        self._terminal = False
        require(mode in ("NEUTRAL_ENDPOINTS","CALLER_PAYLOADS"),"CHECKPOINT_MODE")
        self._mode=mode;self.failure=None
        self._materializer=b.Materializer(manifest,track_reads=True)
        if checkpoint is None:
            self._runtime = b.CallerRuntime(manifest)
        else:
            value = read_checkpoint(checkpoint)
            require(value["accounting"]["mode"]==mode,"CHECKPOINT_MODE")
            require(value["process_id"] != os.getpid(), "RESTORE_REQUIRES_NEW_PROCESS")
            runtime = RestoredCallerV1(value, manifest, code_digest)
            claim = Path(str(checkpoint) + ".consumed")
            try:
                with claim.open("xb") as handle:
                    handle.write(value["checkpoint_digest"].encode("ascii"))
            except OSError as exc:
                runtime.close()
                raise CheckpointError("CHECKPOINT_CONSUMED") from exc
            self._runtime = runtime
            if mode=="CALLER_PAYLOADS":
                self._materializer.counts=dict(value["accounting"]["counts"])
                self._materializer.read_account=dict(value["accounting"]["reads"])

    def accounting(self):
        n=len(self._runtime.rows)
        if self._mode=="NEUTRAL_ENDPOINTS":
            return dict(completed_events=n,payload_read_bytes=0,mode=self._mode)
        return dict(mode=self._mode,completed_events=n,counts=dict(self._materializer.counts),
                    reads=dict(self._materializer.read_account))

    def fail(self,exc,phase):
        if self.failure is not None:return
        prior=asdict(self._runtime.subject.snapshot())
        self.failure=dict(code=getattr(exc,"code",type(exc).__name__),phase=phase,
            completed_events=len(self._runtime.rows),snapshot=prior,
            accounting=self.accounting(),details=getattr(exc,"details",None))
        try:self._runtime.close()
        except Exception as secondary:self.failure["close_error"]=type(secondary).__name__
        self._terminal=True

    def next(self,event):
        require(self._lock.acquire(blocking=False),"CHECKPOINT_BUSY")
        try:
            require(not self._terminal and self._mode=="CALLER_PAYLOADS","CHECKPOINT_TERMINAL")
            n=len(self._runtime.rows)
            require(n<len(self._manifest.events) and event==self._manifest.events[n],"CHECKPOINT_ORDER")
            try:
                item=self._materializer.next(event)
                row=self._runtime.process(item)
                require(not self._runtime.failed,"CHECKPOINT_PROCESSING_FAILED")
                return copy_json(row)
            except Exception as exc:
                self.fail(exc,self._materializer.phase if len(self._runtime.rows)==n else "EVENT")
                raise
        finally:self._lock.release()

    def process(self, item):
        require(self._lock.acquire(blocking=False), "CHECKPOINT_BUSY")
        try:
            require(not self._terminal, "CHECKPOINT_TERMINAL")
            require(self._mode=="NEUTRAL_ENDPOINTS","CHECKPOINT_MODE")
            row = self._runtime.process(item)
            require(not self._runtime.failed, "CHECKPOINT_PROCESSING_FAILED")
            return copy_json(row)
        except Exception as exc:
            if not self._terminal:
                self.fail(exc,"EVENT")
            raise
        finally:
            self._lock.release()

    def suspend(self, path):
        require(self._lock.acquire(blocking=False), "CHECKPOINT_BUSY")
        try:
            require(not self._terminal, "CHECKPOINT_TERMINAL")
            value = export(self._runtime, self._manifest, self._code,self.accounting())
            validate(value, self._manifest, self._code)
            self._runtime.close()
            self._terminal = True
            publish_new(path, value)
            return value["checkpoint_digest"]
        except Exception as exc:
            if self.failure is None:self.fail(exc,"CHECKPOINT_PUBLISH")
            raise
        finally:
            self._lock.release()

    def close(self):
        require(self._lock.acquire(blocking=False), "CHECKPOINT_BUSY")
        try:
            require(not self._terminal, "CHECKPOINT_TERMINAL")
            try:
                return copy_json(self._runtime.record())
            except Exception as exc:
                self.fail(exc,"CLOSE")
                raise
            finally:
                self._runtime.close()
                self._terminal = True
        finally:
            self._lock.release()


def validate_accounting(accounting,manifest,n):
    if accounting==dict(completed_events=n,payload_read_bytes=0,mode="NEUTRAL_ENDPOINTS"):
        return
    require(set(accounting)=={"mode","completed_events","counts","reads"}
        and accounting["mode"]=="CALLER_PAYLOADS" and accounting["completed_events"]==n,"CHECKPOINT_ACCOUNTING")
    prefix=manifest.events[:n]
    audio=sum(e.pcm is not None for e in prefix); visual=sum(e.rgb is not None for e in prefix)
    require(accounting["counts"]==dict(payloads=audio+visual,audio=audio,nj=audio,visual=visual,materialized_events=n),"CHECKPOINT_ACCOUNTING")
    total=sum(p.byte_count for e in prefix for p in (e.pcm,e.rgb) if p is not None)
    require(accounting["reads"]==dict(actual_read_bytes=total,read_operations=audio+visual),"CHECKPOINT_ACCOUNTING")
